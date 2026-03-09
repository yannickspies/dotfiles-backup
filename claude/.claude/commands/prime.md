---
allowed-tools: Bash, Read, Glob
description: Load context for a new agent session by analyzing codebase structure, documentation and README
---

# Prime

Analyze the project structure and report your understanding.

## Execute
- `find . -maxdepth 3 -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.nx/*' -not -path '*/dist/*' | sort | head -120`

## Read (if they exist)
- README.md
- CLAUDE.md
- The top-level project config file (e.g. the manifest that defines dependencies, scripts, and metadata)

## Report
- Project purpose and tech stack
- Key directories and their roles
- Entry points and build/run commands
