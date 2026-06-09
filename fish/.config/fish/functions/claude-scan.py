#!/usr/bin/env python3
"""Surface project-level Claude Code config that runs code on session start.

Called by the `claude-scan` fish function. Scans a repo for `.claude/settings*.json`
and `.mcp.json` — the files an untrusted repo can ship to auto-execute hooks or
launch MCP server processes the moment you start Claude Code in that folder.

Vetted MCP servers / hook commands can be allowlisted in
`~/.claude/claude-scan-trusted.txt` (one substring pattern per line, `#` comments)
so they show `·` instead of `⚑`. Pin versions in the allowlist entry
(e.g. `foo-mcp@1.2.3`) so a later version bump re-trips the flag for review.

Exit codes:
  0  no risky findings (no config at all, or every command is trusted/user-owned)
  1  at least one risky finding (review before launching; pauses `claude-scan && claude`)
  2  bad usage
"""
import json
import sys
import glob
import os
import re

RISKY = re.compile(
    r"curl|wget|/dev/tcp|base64|eval|\bnc\b|bash\s+-i|python\s+-c|"
    r"\|\s*(sh|bash)|>\s*/dev|chmod|\.ssh|\.env\b|aws|token|secret|key",
    re.I,
)

GREEN, RED, YELLOW, RESET, BOLD = (
    "\033[32m",
    "\033[31m",
    "\033[33m",
    "\033[0m",
    "\033[1m",
)


TRUSTED_FILE = os.path.expanduser("~/.claude/claude-scan-trusted.txt")


def load_trusted() -> list[str]:
    """Read user-vetted command substrings from ~/.claude/claude-scan-trusted.txt."""
    try:
        with open(TRUSTED_FILE) as f:
            lines = (ln.split("#", 1)[0].strip() for ln in f)
            return [ln for ln in lines if ln]
    except FileNotFoundError:
        return []


def is_trusted(cmd: str, trusted: list[str]) -> bool:
    """True if the command matches a user-vetted allowlist entry (substring)."""
    return any(t in cmd for t in trusted)


def is_user_owned(cmd: str) -> bool:
    """A hook command is trusted only if it runs a script under the user's own ~/.claude."""
    if "~/.claude" in cmd or "$HOME/.claude" in cmd:
        return True
    return "/.claude/" in cmd and "hooks" in cmd


def collect_targets(root: str) -> list[str]:
    targets: list[str] = []
    for pat in (
        ".claude/settings.json",
        ".claude/settings.local.json",
        ".mcp.json",
        ".claude/*.mcp.json",
    ):
        targets += glob.glob(os.path.join(root, pat))
    return sorted(set(targets))


def scan(root: str) -> int:
    findings: list[tuple[str, str | None, str, bool]] = []
    trusted = load_trusted()

    for path in collect_targets(root):
        rel = os.path.relpath(path, root)
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception as e:  # noqa: BLE001 — report, don't crash
            findings.append((rel, None, f"could not parse ({e})", True))
            continue

        for event, groups in (data.get("hooks") or {}).items():
            for group in groups if isinstance(groups, list) else []:
                for hook in group.get("hooks", []):
                    cmd = hook.get("command", "")
                    if not cmd:
                        continue
                    risky = not is_trusted(cmd, trusted) and (
                        bool(RISKY.search(cmd)) or not is_user_owned(cmd)
                    )
                    findings.append((rel, event, cmd, risky))

        for name, srv in (data.get("mcpServers") or {}).items():
            cmd = " ".join([srv.get("command", "")] + srv.get("args", []))
            # Every MCP server launches a process on session start; only ones the
            # user has explicitly vetted in the allowlist are treated as safe.
            findings.append((rel, f"mcpServer:{name}", cmd, not is_trusted(cmd, trusted)))

    label = os.path.basename(os.path.normpath(root)) or root

    if not findings:
        print(f"{GREEN}✓ no project-level hooks or MCP servers in {label}{RESET}")
        print("  (safe to launch Claude Code here)")
        return 0

    risky_count = sum(1 for *_, risky in findings if risky)

    print(f"{BOLD}claude-scan: {root}{RESET}")
    if risky_count:
        print(f"{YELLOW}⚠ this repo ships config that runs code on session start — review first:{RESET}\n")
    else:
        print(f"{GREEN}✓ config present, but every command is vetted (allowlist or ~/.claude):{RESET}\n")

    for rel, event, cmd, risky in findings:
        mark = f"{RED}⚑{RESET}" if risky else f"{GREEN}·{RESET}"
        tag = f"[{event}]" if event else "[parse]"
        print(f"  {mark} {rel} {tag}")
        print(f"      {cmd}")

    print()
    if risky_count:
        print(f"{RED}{risky_count} command(s) flagged: not user-owned (~/.claude), not allowlisted, or matched a risky pattern.{RESET}")
        print(f"{RED}Do NOT run `claude` here until you've read each ⚑ line above.{RESET}")
        return 1  # nonzero so a chained `claude-scan && claude` pauses for a look
    print(f"{GREEN}All commands are vetted (user-owned or allowlisted) — safe to launch.{RESET}")
    return 0  # everything reviewed; let the chained launch proceed


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: claude-scan.py <dir>", file=sys.stderr)
        return 2
    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f"claude-scan: not a directory: {root}", file=sys.stderr)
        return 2
    return scan(root)


if __name__ == "__main__":
    sys.exit(main())
