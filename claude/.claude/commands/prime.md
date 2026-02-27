---
allowed-tools: Bash, Read, Glob
description: Load context for a new agent session by analyzing codebase structure, documentation and README
---

# Prime

Analyze the project structure and report your understanding.

## Execute
- `git ls-files`

## Read (if they exist)
- README.md
- CLAUDE.md
- The top-level project config file (e.g. the manifest that defines dependencies, scripts, and metadata)

## Report
- Project purpose and tech stack
- Key directories and their roles
- Entry points and build/run commands
