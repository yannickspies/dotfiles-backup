# Claude Code config

Stow package for `~/.claude`. `cd ~/dotfiles && stow claude` symlinks everything
below into place. Needs `uv` on PATH: the hook and the status line are single-file
`uv run --script` programs with no dependencies.

## What is here

| Path | What it is |
|---|---|
| `settings.json` | Auto-mode permissions, one hook, the status line, the output style. No `model` key on purpose: Fable is reached with `/model fable` or `/orchestrate --fable`, never as the session default. |
| `hooks/pre_tool_use.py` | The only hook. Blocks `rm`, `find -delete` and `rsync --delete` whose target resolves outside the project dir, `/tmp` or `~/.claude/projects`. Text that merely mentions a command is never inspected. Tests in `hooks/test_pre_tool_use.py`. |
| `hooks/statusline.py` | Session title, model, context %, EUR cost and rate-limit windows, read from the JSON Claude Code passes to the status line. EUR rate lives in `~/.claude-cost-tracker/config.json`. |
| `agents/` | 26 sub-agents: reviewers, planner, architect, monorepo auditors, growth strategist. Listed in `rules/ecc/common/agents.md`. |
| `commands/` | 19 slash commands: `/commit`, `/recap`, `/orchestrate`, `/fleet`, `/board-status*`, `/prime`, `/fix-build`, and friends. |
| `skills/` | deep-research, market-research, mcp-server-patterns, read-lighthouse-json. |
| `rules/ecc/` | Rule packs from everything-claude-code: `common/` loads every session; `typescript/` and `python/` are path-scoped. |
| `rules/yspies/` | Writing rules for documents. |
| `output-styles/` | `plain-english.md` is active. The rest are unused alternatives. |
| `scripts/`, `ai_docs/`, `themes/` | Helpers used by skills, reference docs, the terminal theme. |

## Conventions

- Hooks write nothing. Transcripts live where Claude Code puts them, under `~/.claude/projects/`.
- Secrets never live here. `.gitignore` covers `.credentials.json`.
- Test the hook from `hooks/`:
  `PYTHONDONTWRITEBYTECODE=1 uv run --python 3.12 --with pytest pytest -q -p no:cacheprovider test_pre_tool_use.py`
- Lint a document with the monorepo's linter: `node scripts/lint-doc.mjs <file>`.
- Runtime state (`projects/`, `sessions/`, `tasks/`, caches) is gitignored and
  machine-local; a fresh machine needs only the stow step above.
