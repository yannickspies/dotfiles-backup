#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""PreToolUse guard for the Bash tool: block deletions aimed outside the project.

Only three commands are inspected: `rm`, `find` with `-delete` or `-exec rm`,
and `rsync` with `--delete`. Every target path is resolved against the
command's (virtual) working directory, following `cd` inside the command.
A target is blocked when it is `/`, the home directory, an ancestor of the
project directory, or any absolute path outside the project directory,
`/tmp`, or `~/.claude/projects`. Everything else is left to the auto-mode
classifier.

Exit 2 with a one-line `BLOCKED:` reason on stderr blocks the call. Exit 0
allows it. Any unexpected error allows the call and prints a warning. The
script never writes a file.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from dataclasses import dataclass, field

MAX_DEPTH = 3
SHELLS = {"bash", "sh", "zsh", "dash"}
INSPECTED = {"rm", "find", "rsync"}

ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
SEP_RE = re.compile(r"^[;&|\n]+$")
REDIR_RE = re.compile(r"^\d*[<>&]+\d*$")
GLOB_RE = re.compile(r"[*?\[]")
VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

SUDO_ARG_OPTS = {"-u", "-g", "-h", "-p", "-U", "-r", "-t", "-C", "-D", "--user", "--group"}
ENV_ARG_OPTS = {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"}
FIND_START_OPTS = {"-H", "-L", "-P"}
RSYNC_ARG_OPTS = {
    "-e", "--rsh", "--exclude", "--include", "--filter", "--exclude-from",
    "--include-from", "--files-from", "--rsync-path", "--link-dest",
    "--backup-dir", "--compare-dest", "--copy-dest", "--log-file",
    "--partial-dir", "--temp-dir", "-T", "--password-file", "-B",
    "--block-size", "--bwlimit", "--timeout", "--contimeout", "--port",
    "--sockopts", "--suffix", "--chmod", "--chown", "--max-size",
    "--min-size", "--max-delete", "--out-format", "--log-file-format",
    "--iconv", "--address", "--modify-window", "--checksum-choice",
    "--compress-choice", "--compress-level", "--skip-compress", "--usermap",
    "--groupmap", "--copy-as", "--write-batch", "--only-write-batch",
    "--read-batch", "--protocol", "--remote-option", "-M", "--outbuf",
    "--info", "--debug", "--stderr", "-f",
}
FALLBACK_DANGEROUS = {
    "/", "/*", "~", "~/", "~/*", "$HOME", "${HOME}", "$HOME/", "$HOME/*",
    "${HOME}/", "${HOME}/*",
}


@dataclass(frozen=True)
class Ctx:
    cwd: str
    project_dir: str
    home: str
    tmp_roots: tuple[str, ...] = ("/tmp",)
    env: dict[str, str] = field(default_factory=dict)

    @property
    def zones(self) -> tuple[str, ...]:
        zones = [norm(z) for z in self.tmp_roots]
        zones.append(norm(os.path.join(self.home, ".claude", "projects")))
        if norm(self.project_dir) != norm(self.home):
            zones.insert(0, norm(self.project_dir))
        return tuple(zones)


def norm(path: str) -> str:
    path = os.path.normpath(path)
    while path.startswith("//"):
        path = path[1:]
    return path


def build_ctx(hook_input: dict) -> Ctx:
    cwd = hook_input.get("cwd") or os.getcwd()
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or cwd
    home = os.path.expanduser("~")
    env = dict(os.environ)
    env.setdefault("HOME", home)
    env["CLAUDE_PROJECT_DIR"] = project_dir
    tmp_roots: tuple[str, ...] = ("/tmp",)
    tmpdir = os.environ.get("TMPDIR")
    if tmpdir and norm(tmpdir) != "/tmp":
        tmp_roots += (tmpdir,)
    return Ctx(cwd=cwd, project_dir=project_dir, home=home, tmp_roots=tmp_roots, env=env)


def strip_heredocs(command: str) -> str:
    """Remove heredoc bodies so quoted text inside them is never inspected."""
    out: list[str] = []
    pos = 0
    while True:
        match = HEREDOC_RE.search(command, pos)
        if not match:
            out.append(command[pos:])
            break
        word = match.group(2)
        newline = command.find("\n", match.end())
        if newline == -1:
            out.append(command[pos:])
            break
        out.append(command[pos : newline + 1])
        lines = command[newline + 1 :].split("\n")
        end = next((i for i, line in enumerate(lines) if line.strip("\t ") == word), None)
        if end is None:
            break
        pos = newline + 1 + sum(len(line) + 1 for line in lines[: end + 1])
    return "".join(out)


def tokenize(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|<>()\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def split_simple_commands(tokens: list[str]) -> list[list[str]]:
    commands: list[list[str]] = []
    current: list[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if SEP_RE.match(token) or token in ("(", ")"):
            if current:
                commands.append(current)
                current = []
            if token in ("(", ")"):
                commands.append([token])
            i += 1
            continue
        if REDIR_RE.match(token):
            i += 1
            if i < len(tokens) and not SEP_RE.match(tokens[i]) and tokens[i] not in ("(", ")"):
                i += 1
            continue
        current.append(token)
        i += 1
    if current:
        commands.append(current)
    return commands


def _basename(token: str) -> str:
    return os.path.basename(token.lstrip("\\"))


def strip_wrappers(argv: list[str]) -> list[str]:
    while argv:
        head = argv[0]
        if ASSIGN_RE.match(head):
            argv = argv[1:]
            continue
        base = _basename(head)
        if base in ("sudo", "doas"):
            argv = argv[1:]
            while argv and argv[0].startswith("-"):
                opt = argv.pop(0)
                if opt == "--":
                    break
                if opt in SUDO_ARG_OPTS and argv:
                    argv = argv[1:]
            continue
        if base == "env":
            argv = argv[1:]
            while argv:
                if ASSIGN_RE.match(argv[0]) or argv[0] in ("-i", "--ignore-environment", "-0", "--null"):
                    argv = argv[1:]
                    continue
                if argv[0] in ENV_ARG_OPTS and len(argv) > 1:
                    argv = argv[2:]
                    continue
                if argv[0] == "--":
                    argv = argv[1:]
                break
            continue
        if base in ("command", "builtin", "nice", "nohup", "time", "exec"):
            argv = argv[1:]
            while argv and argv[0].startswith("-"):
                opt = argv.pop(0)
                if opt in ("-n", "--adjustment") and argv:
                    argv = argv[1:]
            continue
        break
    if argv:
        argv = [_basename(argv[0])] + argv[1:]
    return argv


def expand_vars(text: str, env: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(1) or match.group(2)
        return env[name] if name in env else match.group(0)

    return VAR_RE.sub(repl, text)


def expand_path(token: str, vcwd: str | None, ctx: Ctx) -> tuple[str | None, bool]:
    """Resolve a path token. Returns (absolute path or None, is_glob)."""
    path = token
    if path == "~" or path.startswith("~/"):
        path = ctx.home + path[1:]
    elif path.startswith("~"):
        return None, False
    env = dict(ctx.env)
    if vcwd:
        env["PWD"] = vcwd
    path = expand_vars(path, env)
    is_glob = GLOB_RE.search(path) is not None
    if "$" in path or "`" in path:
        return None, is_glob
    if not os.path.isabs(path):
        if not vcwd:
            return None, is_glob
        path = os.path.join(vcwd, path)
    parts = path.split("/")
    for index, part in enumerate(parts):
        if GLOB_RE.search(part):
            path = "/".join(parts[:index]) or "/"
            break
    return norm(path), is_glob


def classify(resolved: str | None, mode: str, ctx: Ctx) -> str | None:
    """Return a block reason, or None when the path may be deleted."""
    if resolved is None:
        return "cannot be resolved statically"
    path = norm(resolved)
    if path == "/":
        return "is the root filesystem"
    home = norm(ctx.home)
    if path == home:
        return "is the home dir"
    project = norm(ctx.project_dir)
    if project != home and project != path and project.startswith(path + "/"):
        return "is a parent of the project dir"
    for zone in ctx.zones:
        if path == zone:
            return None if mode == "container" else f"is the whole of {zone}"
        if path.startswith(zone + "/"):
            return None
    if path.startswith(home + "/"):
        return "is in the home dir, outside the project"
    return "is outside the project dir, /tmp and ~/.claude/projects"


def rm_targets(argv: list[str]) -> list[tuple[str, str]]:
    targets: list[tuple[str, str]] = []
    after_dashdash = False
    for token in argv[1:]:
        if after_dashdash:
            targets.append((token, "strict"))
        elif token == "--":
            after_dashdash = True
        elif token.startswith("-") and len(token) > 1:
            continue
        else:
            targets.append((token, "strict"))
    return targets


def find_targets(argv: list[str]) -> list[tuple[str, str]]:
    args = argv[1:]
    dangerous = False
    for index, arg in enumerate(args):
        if arg == "-delete":
            dangerous = True
        if arg in ("-exec", "-execdir", "-ok", "-okdir") and index + 1 < len(args):
            if _basename(args[index + 1]) == "rm":
                dangerous = True
    if not dangerous:
        return []
    starts: list[str] = []
    for arg in args:
        if arg in FIND_START_OPTS or arg.startswith("-O") or arg.startswith("-D"):
            continue
        if arg.startswith("-") or arg in ("!", "("):
            break
        starts.append(arg)
    return [(start, "container") for start in starts or ["."]]


def rsync_targets(argv: list[str]) -> list[tuple[str, str]]:
    args = argv[1:]
    if not any(arg.startswith("--delete") or arg == "--del" for arg in args):
        return []
    positionals: list[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            positionals.extend(args[index + 1 :])
            break
        if arg.startswith("-"):
            index += 2 if arg in RSYNC_ARG_OPTS else 1
            continue
        positionals.append(arg)
        index += 1
    return [
        (path, "container")
        for path in positionals
        if not path.startswith("rsync://") and not re.match(r"^[^/]+:", path)
    ]


def track_cd(argv: list[str], vcwd: str | None, ctx: Ctx) -> str | None:
    if argv[0] == "popd":
        return None
    operands = [arg for arg in argv[1:] if not (arg.startswith("-") and len(arg) > 1)]
    if not operands or operands[0] == "~":
        return ctx.home
    if operands[0] == "-":
        return None
    resolved, is_glob = expand_path(operands[0], vcwd, ctx)
    return None if resolved is None or is_glob else resolved


def fallback_regex(command: str) -> str | None:
    """Coarse check when the command cannot be tokenized (unbalanced quotes)."""
    words = command.split()
    for index, word in enumerate(words):
        if _basename(word.strip("\"'")) != "rm":
            continue
        for follower in words[index + 1 :]:
            if SEP_RE.match(follower) or follower in ("&&", "||"):
                break
            if follower.strip("\"'") in FALLBACK_DANGEROUS:
                return f"rm target '{follower}' is a protected root (command has unbalanced quotes)"
    return None


def evaluate(command: str, ctx: Ctx, depth: int = 0, start_cwd: str | None = None) -> str | None:
    """Return the first block reason found in `command`, or None."""
    if depth > MAX_DEPTH:
        return None
    try:
        tokens = tokenize(strip_heredocs(command))
    except ValueError:
        return fallback_regex(command)
    vcwd: str | None = start_cwd if start_cwd is not None else ctx.cwd
    stack: list[str | None] = []
    for argv in split_simple_commands(tokens):
        if argv == ["("]:
            stack.append(vcwd)
            continue
        if argv == [")"]:
            vcwd = stack.pop() if stack else vcwd
            continue
        argv = strip_wrappers(argv)
        if not argv:
            continue
        name = argv[0]
        if name in ("cd", "pushd", "popd"):
            vcwd = track_cd(argv, vcwd, ctx)
            continue
        if name in SHELLS:
            for index, arg in enumerate(argv[1:], 1):
                if arg == "-c" and index + 1 < len(argv):
                    reason = evaluate(argv[index + 1], ctx, depth + 1, start_cwd=vcwd or "")
                    if reason:
                        return reason
                    break
            continue
        if name == "eval":
            reason = evaluate(" ".join(argv[1:]), ctx, depth + 1, start_cwd=vcwd or "")
            if reason:
                return reason
            continue
        if name not in INSPECTED:
            continue
        if name == "rm":
            targets = rm_targets(argv)
        elif name == "find":
            targets = find_targets(argv)
        else:
            targets = rsync_targets(argv)
        for token, mode in targets:
            resolved, is_glob = expand_path(token, vcwd, ctx)
            reason = classify(resolved, "container" if is_glob else mode, ctx)
            if reason:
                shown = resolved if resolved else "?"
                return f"{name} target '{token}' -> {shown} {reason}"
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") != "Bash":
            sys.exit(0)
        command = (data.get("tool_input") or {}).get("command") or ""
        reason = evaluate(command, build_ctx(data))
        if reason:
            print(f"BLOCKED: {reason}", file=sys.stderr)
            sys.exit(2)
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - never block on our own bug
        print(f"pre_tool_use: warning: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
