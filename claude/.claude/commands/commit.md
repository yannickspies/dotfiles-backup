---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git commit:*)
description: Create a concise git commit with staged and unstaged changes
---

## Context
- Current git status: !`git status --short`
- Changes to commit: !`git diff HEAD`
- Recent commits for style reference: !`git log --oneline -5`

## Task
Create a single git commit with ALL changes (both staged and unstaged).

Requirements:
- Write a concise, descriptive commit message (max 50 chars for subject line)
- Focus on WHAT changed and WHY, not HOW
- Use imperative mood ("fix" not "fixed" or "fixes")
- Stage all modified files and commit them

Commit message format:
- Subject line: brief summary (imperative, lowercase, no period)
- If needed, blank line then 1-2 lines of context