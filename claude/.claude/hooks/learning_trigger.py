#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Learning trigger hook — runs on Stop to nudge toward unlearned topics.

Logic:
1. Increment sessions_since_learning counter
2. Gate: skip if < 3 sessions since last learning OR random > 30%
3. Match touched files against taxonomy file_patterns
4. Find unlearned topic matching session work
5. Print nudge as passive terminal text
"""

import json
import os
import sys
import random
import subprocess
from pathlib import Path
from datetime import datetime
from fnmatch import fnmatch


LEARNING_DIR = Path.home() / ".claude" / "learning"
PROGRESS_FILE = LEARNING_DIR / "progress.json"
TAXONOMY_FILE = LEARNING_DIR / "taxonomy.json"


def load_json(path: Path) -> dict | None:
    """Load a JSON file, returning None on any error."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def save_json(path: Path, data: dict) -> None:
    """Save data as formatted JSON."""
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def get_recently_touched_files() -> list[str]:
    """Get files touched in recent git commits (last 10 commits)."""
    try:
        result = subprocess.run(
            ["git", "log", "--name-only", "-10", "--pretty=format:"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
            return list(set(files))
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    return []


def match_files_to_topics(
    files: list[str], taxonomy: dict, progress: dict
) -> list[dict]:
    """Find unlearned topics whose file_patterns match touched files."""
    matches = []
    topics = taxonomy.get("topics", [])
    topic_progress = progress.get("topics", {})

    for topic in topics:
        topic_id = topic["id"]
        status = topic_progress.get(topic_id, {}).get("status", "pending")

        # Only consider pending topics
        if status != "pending":
            continue

        # Check if any touched file matches any of the topic's file_patterns
        patterns = topic.get("file_patterns", [])
        match_count = 0
        for f in files:
            for pattern in patterns:
                if fnmatch(f, pattern):
                    match_count += 1
                    break

        if match_count > 0:
            matches.append(
                {
                    "topic": topic,
                    "match_count": match_count,
                }
            )

    # Sort by match count (most relevant first)
    matches.sort(key=lambda m: m["match_count"], reverse=True)
    return matches


def check_prerequisites_met(topic: dict, progress: dict) -> bool:
    """Check if all prerequisites for a topic are completed."""
    topic_progress = progress.get("topics", {})
    for prereq_id in topic.get("prerequisites", []):
        prereq_status = topic_progress.get(prereq_id, {}).get("status", "pending")
        if prereq_status != "completed":
            return False
    return True


def main():
    try:
        # Read stdin (hook input) — we don't use it but must consume it
        try:
            json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            pass

        # Load data files
        progress = load_json(PROGRESS_FILE)
        taxonomy = load_json(TAXONOMY_FILE)

        if not progress or not taxonomy:
            sys.exit(0)

        # Step 1: Increment sessions_since_learning
        sessions = progress.get("sessions_since_learning", 0) + 1
        progress["sessions_since_learning"] = sessions
        save_json(PROGRESS_FILE, progress)

        # Step 2: Gate check — skip if too soon or random chance
        if sessions < 3:
            sys.exit(0)

        if random.random() > 0.30:
            sys.exit(0)

        # Step 3: Get recently touched files
        files = get_recently_touched_files()
        if not files:
            sys.exit(0)

        # Step 4: Match files to unlearned topics
        matches = match_files_to_topics(files, taxonomy, progress)

        # Filter to topics with prerequisites met
        eligible = [
            m
            for m in matches
            if check_prerequisites_met(m["topic"], progress)
        ]

        if not eligible:
            sys.exit(0)

        # Step 5: Print nudge for the best match
        best = eligible[0]["topic"]
        topic_name = best["name"]
        topic_id = best["id"]

        # Print to stderr so it appears in the terminal without affecting hook output
        print(
            f"\n  You've been working with files related to \"{topic_name}\"."
            f"\n  Run /learn {topic_id} to explore this topic deeper.\n",
            file=sys.stderr,
        )

        sys.exit(0)

    except Exception:
        # Never block the session — fail silently
        sys.exit(0)


if __name__ == "__main__":
    main()
