#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Windows toast when Claude Code finishes work or needs you.

Wired to `UserPromptSubmit`, `Stop`, `SubagentStop` and `Notification`.
`UserPromptSubmit` only records the turn start time. The others send a
Windows toast via powershell.exe, using the `reminder` scenario so the card
gets through Do Not Disturb (priority-only) and stays until dismissed.

`Stop` only toasts when the turn ran longer than MIN_TURN_SECONDS, so short
chat replies stay quiet. Any error is swallowed: a notification must never
break the session.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from xml.sax.saxutils import escape

MIN_TURN_SECONDS = 30
STAMP_DIR = Path("/tmp/claude-notify")
APP_ID = "Microsoft.WSL"

NOTIFICATION_TEXT = {
    "agent_completed": "Background agent finished",
    "agent_needs_input": "Background agent needs input",
    "permission_prompt": "Permission needed",
    "elicitation_dialog": "A tool is asking you something",
    "idle_prompt": "Waiting for input",
}


def stamp_path(session_id: str) -> Path:
    return STAMP_DIR / f"{session_id}.start"


def record_start(session_id: str) -> None:
    STAMP_DIR.mkdir(parents=True, exist_ok=True)
    stamp_path(session_id).write_text(str(time.time()))


def turn_seconds(session_id: str) -> float | None:
    try:
        return time.time() - float(stamp_path(session_id).read_text())
    except (OSError, ValueError):
        return None


def message_for(event: dict) -> str | None:
    name = event.get("hook_event_name")
    if name == "Stop":
        elapsed = turn_seconds(event.get("session_id", ""))
        if elapsed is not None and elapsed < MIN_TURN_SECONDS:
            return None
        return "Done" if elapsed is None else f"Done after {int(elapsed)}s"
    if name == "SubagentStop":
        agent = event.get("agent_type") or "subagent"
        return f"Agent finished: {agent}"
    if name == "Notification":
        kind = event.get("notification_type", "")
        text = NOTIFICATION_TEXT.get(kind)
        if text is None:
            return event.get("message") or f"Notification: {kind}"
        return text
    return None


def send_toast(title: str, body: str) -> None:
    xml = (
        '<toast scenario="reminder"><visual><binding template="ToastGeneric">'
        f"<text>{escape(title)}</text><text>{escape(body)}</text>"
        "</binding></visual>"
        '<actions><action content="OK" arguments="ok"/></actions></toast>'
    )
    script = (
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
        "ContentType = WindowsRuntime] | Out-Null; "
        "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, "
        "ContentType = WindowsRuntime] | Out-Null; "
        "$x = [Windows.Data.Xml.Dom.XmlDocument]::new(); "
        f"$x.LoadXml('{xml.replace(chr(39), chr(39) * 2)}'); "
        f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{APP_ID}')"
        ".Show([Windows.UI.Notifications.ToastNotification]::new($x))"
    )
    subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        cwd="/tmp",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def main() -> None:
    event = json.load(sys.stdin)
    if event.get("hook_event_name") == "UserPromptSubmit":
        record_start(event.get("session_id", ""))
        return
    body = message_for(event)
    if body is None:
        return
    project = Path(event.get("cwd") or ".").name or "Claude Code"
    send_toast(f"Claude Code · {project}", body)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"notify hook: {exc}", file=sys.stderr)
    sys.exit(0)
