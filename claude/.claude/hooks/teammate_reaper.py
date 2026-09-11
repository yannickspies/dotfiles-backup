#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Stop hook: close tmux panes of teammates that finished long ago.

A teammate (an `Agent` call with a `name:` under `teammateMode: auto`) never
exits on its own. It reports back, then idles at a prompt with its MCP servers
until the lead sends a `shutdown_request`. When the lead forgets, the pane and
its ~400 MB stay until the session ends. This hook is the safety net.

On every Stop of the lead it reads the team config for this session
(`~/.claude/teams/session-<id8>/config.json`) and, for each tmux teammate,
kills the pane when all of these hold:

  * the pane is alive and its claude process can be found,
  * that process runs no Bash tool right now (no `shell-snapshots` child),
  * its inbox holds no undelivered message,
  * its transcript was last written more than IDLE_SECONDS ago.

A teammate whose transcript cannot be located is never touched.

Because Stop only fires when the lead ends a turn, the hook also leaves one
detached checker per team running (`--daemon <team>`) that repeats the sweep
every CHECK_SECONDS until the team config disappears or no tmux teammate is
left. The daemon is found again via its command line; nothing is written.

Exit code is always 0. Nothing here ever blocks the lead.

Manual use:  teammate_reaper.py --team session-abcd1234 [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

IDLE_SECONDS = 10 * 60
CHECK_SECONDS = 60
DAEMON_MAX_SECONDS = 12 * 60 * 60
TRANSCRIPT_HEAD_BYTES = 256 * 1024
TRANSCRIPT_MAX_AGE_DAYS = 3
CLAUDE_HOME = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
BUSY_MARKER = "shell-snapshots"


@dataclass(frozen=True)
class Member:
    name: str
    agent_id: str
    pane: str
    cwd: str


@dataclass(frozen=True)
class Verdict:
    member: Member
    kill: bool
    reason: str


@dataclass(frozen=True)
class ProcessTable:
    """Snapshot of `ps -eo pid,ppid,args`."""

    rows: tuple[tuple[int, int, str], ...]

    @classmethod
    def capture(cls) -> "ProcessTable":
        out = run(["ps", "-eo", "pid,ppid,args"])
        return cls.parse(out or "")

    @classmethod
    def parse(cls, text: str) -> "ProcessTable":
        rows = []
        for line in text.splitlines()[1:]:
            parts = line.split(None, 2)
            if len(parts) < 3:
                continue
            try:
                rows.append((int(parts[0]), int(parts[1]), parts[2]))
            except ValueError:
                continue
        return cls(tuple(rows))

    def find(self, needle: str) -> tuple[int, ...]:
        return tuple(pid for pid, _, args in self.rows if needle in args)

    def descendants(self, root: int) -> tuple[int, ...]:
        found: list[int] = []
        frontier = [root]
        while frontier:
            parent = frontier.pop()
            for pid, ppid, _ in self.rows:
                if ppid == parent and pid not in found:
                    found.append(pid)
                    frontier.append(pid)
        return tuple(found)

    def is_running_shell(self, root: int) -> bool:
        kids = set(self.descendants(root))
        return any(pid in kids and BUSY_MARKER in args for pid, _, args in self.rows)


def run(cmd: list[str]) -> str | None:
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def slug(cwd: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", cwd)


def team_dir(team: str) -> Path:
    return CLAUDE_HOME / "teams" / team


def load_members(team: str) -> tuple[Member, ...]:
    try:
        config = json.loads((team_dir(team) / "config.json").read_text())
    except (OSError, ValueError):
        return ()
    members = []
    for raw in config.get("members", []):
        if raw.get("backendType") != "tmux" or not raw.get("tmuxPaneId"):
            continue
        members.append(
            Member(
                name=str(raw.get("name", "")),
                agent_id=str(raw.get("agentId", "")),
                pane=str(raw["tmuxPaneId"]),
                cwd=str(raw.get("cwd", "")),
            )
        )
    return tuple(members)


def pane_alive(pane: str) -> bool:
    out = run(["tmux", "display-message", "-p", "-t", pane, "#{pane_id}"])
    return bool(out and out.strip() == pane)


def inbox_pending(team: str, name: str) -> bool:
    path = team_dir(team) / "inboxes" / f"{name}.json"
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return False
    return bool(data)


def find_transcript(projects_dir: Path, member: Member, team: str) -> Path | None:
    folder = projects_dir / slug(member.cwd)
    if not folder.is_dir():
        return None
    name_tag = f'"agentName":"{member.name}"'
    team_tag = f'"teamName":"{team}"'
    cutoff = time.time() - TRANSCRIPT_MAX_AGE_DAYS * 86400
    best: Path | None = None
    for path in folder.glob("*.jsonl"):
        try:
            mtime = path.stat().st_mtime
            if mtime < cutoff:
                continue
            with path.open("rb") as fh:
                head = fh.read(TRANSCRIPT_HEAD_BYTES).decode("utf-8", "replace")
        except OSError:
            continue
        if name_tag in head and team_tag in head:
            if best is None or mtime > best.stat().st_mtime:
                best = path
    return best


def assess(
    member: Member,
    team: str,
    procs: ProcessTable,
    projects_dir: Path,
    now: float,
    is_pane_alive=pane_alive,
    has_pending=inbox_pending,
) -> Verdict:
    if not is_pane_alive(member.pane):
        return Verdict(member, False, "pane gone")
    pids = procs.find(f"--agent-id {member.agent_id}")
    if not pids:
        return Verdict(member, False, "process not found")
    if any(procs.is_running_shell(pid) for pid in pids):
        return Verdict(member, False, "running a shell")
    if has_pending(team, member.name):
        return Verdict(member, False, "inbox pending")
    transcript = find_transcript(projects_dir, member, team)
    if transcript is None:
        return Verdict(member, False, "transcript not found")
    idle = now - transcript.stat().st_mtime
    if idle < IDLE_SECONDS:
        return Verdict(member, False, f"idle {int(idle)}s")
    return Verdict(member, True, f"idle {int(idle // 60)}m")


def sweep(team: str, dry_run: bool) -> tuple[Verdict, ...]:
    members = load_members(team)
    if not members:
        return ()
    procs = ProcessTable.capture()
    projects_dir = CLAUDE_HOME / "projects"
    verdicts = tuple(assess(m, team, procs, projects_dir, time.time()) for m in members)
    for v in verdicts:
        if v.kill and not dry_run:
            run(["tmux", "kill-pane", "-t", v.member.pane])
    return verdicts


def daemon_running(team: str, procs: ProcessTable) -> bool:
    needle = f"teammate_reaper.py --daemon {team}"
    return any(needle in args and pid != os.getpid() for pid, _, args in procs.rows)


def spawn_daemon(team: str) -> None:
    try:
        subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), "--daemon", team],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        pass


def daemon(team: str) -> None:
    deadline = time.time() + DAEMON_MAX_SECONDS
    while time.time() < deadline:
        time.sleep(CHECK_SECONDS)
        if not (team_dir(team) / "config.json").exists():
            return
        verdicts = sweep(team, dry_run=False)
        alive = [v for v in verdicts if v.reason != "pane gone" and not v.kill]
        if not alive:
            return


def report(verdicts: tuple[Verdict, ...], dry_run: bool) -> None:
    for v in verdicts:
        if v.kill:
            verb = "would close" if dry_run else "closed"
            print(f"teammate_reaper: {verb} pane {v.member.pane} ({v.member.name}, {v.reason})")
        elif dry_run:
            print(f"teammate_reaper: keep {v.member.pane} ({v.member.name}, {v.reason})")


def team_from_stdin() -> str | None:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return None
    session_id = str(payload.get("session_id", ""))
    return f"session-{session_id[:8]}" if len(session_id) >= 8 else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--team")
    parser.add_argument("--daemon", metavar="TEAM")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.daemon:
        daemon(args.daemon)
        return 0

    team = args.team or team_from_stdin()
    if not team or not (team_dir(team) / "config.json").exists():
        return 0

    verdicts = sweep(team, args.dry_run)
    report(verdicts, args.dry_run)

    still_open = [v for v in verdicts if not v.kill and v.reason != "pane gone"]
    if still_open and not args.dry_run and not daemon_running(team, ProcessTable.capture()):
        spawn_daemon(team)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - a hook must never block the lead
        print(f"teammate_reaper: skipped ({exc})", file=sys.stderr)
        sys.exit(0)
