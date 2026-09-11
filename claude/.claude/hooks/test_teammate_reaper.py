"""Tests for teammate_reaper.py. Run from hooks/:

PYTHONDONTWRITEBYTECODE=1 uv run --python 3.12 --with pytest pytest -q -p no:cacheprovider test_teammate_reaper.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

import teammate_reaper as tr

TEAM = "session-abcd1234"
CWD = "/home/someone/projects/app"
MEMBER = tr.Member(name="lane-a", agent_id=f"lane-a@{TEAM}", pane="%7", cwd=CWD)

PS = """  PID  PPID COMMAND
  100     1 fish -c cd /x && env CLAUDECODE=1 /bin/claude --agent-id lane-a@session-abcd1234 --agent-name lane-a
  101   100 /bin/claude --agent-id lane-a@session-abcd1234 --agent-name lane-a
  102   101 npm exec firecrawl-mcp
  200     1 /bin/claude --agent-id lane-b@session-abcd1234
  201   200 /bin/bash -c source /home/someone/.claude/shell-snapshots/snapshot-bash-1.sh
"""


def write_transcript(projects: Path, member: tr.Member, team: str, age_seconds: float) -> Path:
    folder = projects / tr.slug(member.cwd)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "11111111-2222-3333-4444-555555555555.jsonl"
    line = json.dumps({"agentName": member.name, "teamName": team, "sessionId": "1111"}, separators=(",", ":"))
    path.write_text(line + "\n")
    stamp = time.time() - age_seconds
    os.utime(path, (stamp, stamp))
    return path


def test_slug_replaces_every_non_alphanumeric():
    assert tr.slug("/home/me/.claude/x") == "-home-me--claude-x"


def test_process_table_finds_agent_and_descendants():
    procs = tr.ProcessTable.parse(PS)
    assert procs.find("--agent-id lane-a@session-abcd1234") == (100, 101)
    assert set(procs.descendants(100)) == {101, 102}
    assert procs.is_running_shell(101) is False
    assert procs.is_running_shell(200) is True


def test_idle_teammate_is_killed(tmp_path: Path):
    write_transcript(tmp_path, MEMBER, TEAM, age_seconds=tr.IDLE_SECONDS + 60)
    verdict = tr.assess(
        MEMBER, TEAM, tr.ProcessTable.parse(PS), tmp_path, time.time(),
        is_pane_alive=lambda _p: True, has_pending=lambda _t, _n: False,
    )
    assert verdict.kill is True
    assert verdict.reason.startswith("idle ")


def test_recently_active_teammate_is_kept(tmp_path: Path):
    write_transcript(tmp_path, MEMBER, TEAM, age_seconds=30)
    verdict = tr.assess(
        MEMBER, TEAM, tr.ProcessTable.parse(PS), tmp_path, time.time(),
        is_pane_alive=lambda _p: True, has_pending=lambda _t, _n: False,
    )
    assert verdict.kill is False


def test_teammate_running_a_shell_is_kept(tmp_path: Path):
    busy = tr.Member(name="lane-b", agent_id=f"lane-b@{TEAM}", pane="%8", cwd=CWD)
    write_transcript(tmp_path, busy, TEAM, age_seconds=tr.IDLE_SECONDS * 5)
    verdict = tr.assess(
        busy, TEAM, tr.ProcessTable.parse(PS), tmp_path, time.time(),
        is_pane_alive=lambda _p: True, has_pending=lambda _t, _n: False,
    )
    assert verdict == tr.Verdict(busy, False, "running a shell")


def test_pending_inbox_is_kept(tmp_path: Path):
    write_transcript(tmp_path, MEMBER, TEAM, age_seconds=tr.IDLE_SECONDS * 5)
    verdict = tr.assess(
        MEMBER, TEAM, tr.ProcessTable.parse(PS), tmp_path, time.time(),
        is_pane_alive=lambda _p: True, has_pending=lambda _t, _n: True,
    )
    assert verdict.reason == "inbox pending"


@pytest.mark.parametrize("alive, found", [(False, True), (True, False)])
def test_missing_pane_or_transcript_is_never_killed(tmp_path: Path, alive: bool, found: bool):
    if found:
        write_transcript(tmp_path, MEMBER, TEAM, age_seconds=tr.IDLE_SECONDS * 5)
    verdict = tr.assess(
        MEMBER, TEAM, tr.ProcessTable.parse(PS), tmp_path, time.time(),
        is_pane_alive=lambda _p: alive, has_pending=lambda _t, _n: False,
    )
    assert verdict.kill is False


def test_transcript_from_another_team_is_ignored(tmp_path: Path):
    write_transcript(tmp_path, MEMBER, "session-other000", age_seconds=tr.IDLE_SECONDS * 5)
    assert tr.find_transcript(tmp_path, MEMBER, TEAM) is None


def test_daemon_detection_ignores_self():
    procs = tr.ProcessTable.parse(
        "PID PPID COMMAND\n"
        f"{os.getpid()} 1 python teammate_reaper.py --daemon {TEAM}\n"
        f"999 1 python teammate_reaper.py --daemon {TEAM}\n"
    )
    assert tr.daemon_running(TEAM, procs) is True
    own_only = tr.ProcessTable.parse(f"PID PPID COMMAND\n{os.getpid()} 1 python teammate_reaper.py --daemon {TEAM}\n")
    assert tr.daemon_running(TEAM, own_only) is False


def test_load_members_keeps_only_tmux_members(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(tr, "CLAUDE_HOME", tmp_path)
    folder = tmp_path / "teams" / TEAM
    folder.mkdir(parents=True)
    (folder / "config.json").write_text(json.dumps({"members": [
        {"name": "team-lead", "agentId": f"team-lead@{TEAM}", "backendType": "in-process", "tmuxPaneId": "leader"},
        {"name": "lane-a", "agentId": f"lane-a@{TEAM}", "backendType": "tmux", "tmuxPaneId": "%7", "cwd": CWD},
    ]}))
    assert tr.load_members(TEAM) == (MEMBER,)
