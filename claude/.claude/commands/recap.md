---
allowed-tools: Bash(git log:*), Bash(git status:*), Bash(git diff:*), Read, Glob, Grep
description: Quick recap of where you left off — recent changes, uncommitted work, and open items
---

## Context
- Recent commits (last 15): !`git log --oneline -15`
- Current working tree: !`git status --short`

## Task

First, use `Glob` to find the MEMORY.md file for this project under `~/.claude/projects/`. Then `Read` it.

Then give me a **short, scannable recap** to get back up to speed. Structure it as:

### Last session
- Summarize what the recent commits accomplished (group related commits, don't just list them)
- Mention the last ~1-2 sessions worth of work, not ancient history

### Uncommitted work
- If there are unstaged/untracked changes, summarize what they are and whether they look like work-in-progress or leftover artifacts
- If clean, just say "Clean working tree"

### Open items
- Check the memory file for any "pending", "TODO", "still needs", "should extract", or similar language that indicates unfinished work
- List these as actionable bullet points
- If none found, say "Nothing flagged in memory"

### Suggested next steps
- Based on the above, suggest 1-3 concrete things to pick up

**Keep the whole response under 40 lines.** Be concise. No filler. Use bullet points.
