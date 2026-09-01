---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git commit:*)
argument-hint: [files to stage; empty = the files this task touched]
description: Commit only the files that belong to the current task, with a conventional-commit message
---

## Context
- Working tree: !`git status --short`
- Tracked changes: !`git diff HEAD --stat`
- Recent commits for style: !`git log --oneline -5`
- Files named by the user: $ARGUMENTS

## Task

Commit ONLY the files that belong to the current task.

1. If the user named files above, stage exactly those.
2. Otherwise stage the files this session changed for the task at hand. List them
   back in one line before committing.
3. If the tree holds modified or untracked files you did not touch, leave them alone
   and say so in one line. Never `git add -A`, `git add .`, or `git commit -a`.
4. One commit per task. Message format:
   - Subject: `<type>: <summary>` — imperative, lowercase, no period, at most 72 chars.
     Types: feat, fix, refactor, docs, test, chore, perf, ci. Add a scope when it
     helps: `feat(api): …`.
   - Body (optional): what changed and why, not how. Lines at most 100 chars.
5. Finish with `git log -1 --stat` so the result is visible.
