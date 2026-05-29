#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Status line wrapper.

Combines the existing v3 status line (agent/model/recent prompts) with
ccusage's live cost readout, converting USD amounts to EUR using the rate
from ~/.claude-cost-tracker/config.json. Fail-soft: any error in one source
falls back to the other; if both fail, prints a small placeholder so the
status bar never crashes.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude-cost-tracker" / "config.json"

DEFAULTS: dict = {
    "eur_per_usd": 0.92,
    "ccusage_cmd": ["npx", "-y", "ccusage@latest", "statusline"],
    "base_status_cmd": [
        "uv",
        "run",
        str(Path.home() / ".claude" / "status_lines" / "status_line_v3.py"),
    ],
}

USD_RE = re.compile(r"\$(-?\d+(?:\.\d+)?)")


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return {**DEFAULTS, **json.loads(CONFIG_PATH.read_text())}
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULTS


def run_capture(cmd: list[str], stdin_data: str, timeout: float = 5.0) -> str:
    try:
        result = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def usd_to_eur(text: str, rate: float) -> str:
    def repl(match: re.Match) -> str:
        return f"€{float(match.group(1)) * rate:.2f}"

    return USD_RE.sub(repl, text)


# Strips ` / <amount> block (<time> left)` from the 💰 cost segment.
BLOCK_RE = re.compile(r"\s*/\s*[€$][\d.\-]+\s*block\s*\([^)]*\)")


def clean_cost_line(text: str) -> str:
    """Trim ccusage output to the segments we care about.

    Keeps model (🤖), session/today costs (💰), and context window (🧠).
    Drops the per-block cost (redundant with the daily total) and the
    hourly burn rate (🔥), which aren't actionable.
    """
    kept: list[str] = []
    for segment in (s.strip() for s in text.split("|")):
        if segment.startswith("🔥"):
            continue  # burn rate — not useful
        if segment.startswith("💰"):
            segment = BLOCK_RE.sub("", segment)  # drop redundant block total
        kept.append(segment)
    return " | ".join(kept)


def main() -> None:
    cfg = load_config()
    stdin_data = sys.stdin.read()

    base_line = run_capture(list(cfg["base_status_cmd"]), stdin_data)
    cost_line = run_capture(list(cfg["ccusage_cmd"]), stdin_data, timeout=8.0)

    if cost_line:
        cost_line = usd_to_eur(cost_line, float(cfg["eur_per_usd"]))
        cost_line = clean_cost_line(cost_line)

    parts = [p for p in (base_line, cost_line) if p]
    print(" | ".join(parts) if parts else "💭 status line unavailable")


if __name__ == "__main__":
    main()
