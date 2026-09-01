#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Status line: session title, model, context %, EUR cost, rate-limit windows.

Reads the JSON Claude Code passes to the statusLine command on stdin
(https://code.claude.com/docs/en/statusline) and prints one line. Every
field is optional: a missing field drops its segment. Any error prints a
placeholder so the status bar never breaks. Writes nothing.

The EUR rate comes from ~/.claude-cost-tracker/config.json (`eur_per_usd`),
falling back to 0.92.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude-cost-tracker" / "config.json"
DEFAULT_EUR_PER_USD = 0.92
SEPARATOR = " · "


def eur_rate() -> float:
    try:
        return float(json.loads(CONFIG_PATH.read_text())["eur_per_usd"])
    except (OSError, ValueError, KeyError, TypeError):
        return DEFAULT_EUR_PER_USD


def get(data: dict, *keys: str):
    node = data
    for key in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def build_line(data: dict) -> str:
    segments: list[str] = []

    name = get(data, "session_name") or (get(data, "session_id") or "")[:8]
    if name:
        segments.append(str(name))

    model = get(data, "model", "display_name")
    if model:
        segments.append(str(model))

    used = get(data, "context_window", "used_percentage")
    if isinstance(used, (int, float)):
        segments.append(f"ctx {used:.0f}%")

    cost = get(data, "cost", "total_cost_usd")
    if isinstance(cost, (int, float)):
        segments.append(f"€{cost * eur_rate():.2f}")

    for label, window in (("5h", "five_hour"), ("7d", "seven_day"), ("spend", "spend_limit")):
        pct = get(data, "rate_limits", window, "used_percentage")
        if isinstance(pct, (int, float)):
            segments.append(f"{label} {pct:.0f}%")

    return SEPARATOR.join(segments) if segments else "💭 no session data"


def main() -> None:
    try:
        print(build_line(json.load(sys.stdin)))
    except Exception:  # noqa: BLE001 - the status bar must never crash
        print("💭 status line unavailable")


if __name__ == "__main__":
    main()
