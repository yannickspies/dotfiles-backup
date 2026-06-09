#!/usr/bin/env python3
"""Surface project-level Claude Code config that runs code on session start.

Called by the `claude-scan` fish function. Scans a repo for `.claude/settings*.json`
and `.mcp.json` — the files an untrusted repo can ship to auto-execute hooks or
launch MCP server processes the moment you start Claude Code in that folder.

Exit codes:
  0  no project-level hooks / MCP servers found (safe to launch)
  1  hooks or MCP servers exist (review before launching; pauses `claude-scan && claude`)
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
                    risky = bool(RISKY.search(cmd)) or not is_user_owned(cmd)
                    findings.append((rel, event, cmd, risky))

        for name, srv in (data.get("mcpServers") or {}).items():
            cmd = " ".join([srv.get("command", "")] + srv.get("args", []))
            findings.append((rel, f"mcpServer:{name}", cmd, True))

    label = os.path.basename(os.path.normpath(root)) or root

    if not findings:
        print(f"{GREEN}✓ no project-level hooks or MCP servers in {label}{RESET}")
        print("  (safe to launch Claude Code here)")
        return 0

    print(f"{BOLD}claude-scan: {root}{RESET}")
    print(f"{YELLOW}⚠ this repo ships config that runs code on session start — review first:{RESET}\n")

    risky_count = 0
    for rel, event, cmd, risky in findings:
        if risky:
            risky_count += 1
        mark = f"{RED}⚑{RESET}" if risky else f"{GREEN}·{RESET}"
        tag = f"[{event}]" if event else "[parse]"
        print(f"  {mark} {rel} {tag}")
        print(f"      {cmd}")

    print()
    if risky_count:
        print(f"{RED}{risky_count} command(s) flagged: not user-owned (~/.claude) or matched a risky pattern.{RESET}")
        print(f"{RED}Do NOT run `claude` here until you've read each ⚑ line above.{RESET}")
    else:
        print(f"{GREEN}All hook commands point to your own ~/.claude scripts.{RESET}")
    return 1  # nonzero whenever config exists, so the chained launch pauses for a look


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
