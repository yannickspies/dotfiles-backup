# `ccw` — Claude Code Worktrees

Run several **long-lived Claude Code CLI sessions in parallel**, each in its own
isolated git worktree — no branch collisions, no stash chaos, one shared `.git`.
A fish port of the idea behind [`craigsc/cmux`](https://github.com/craigsc/cmux)
("tmux for Claude Code"), adapted to WSL2/fish. Lives in the `fish` stow package
(`fish/.config/fish/functions/ccw.fish` + completions), autoloaded — no config edit.

> **Why not the cmux from the video?** That one (`manaflow-ai/cmux`) is a macOS-only
> desktop app and won't run on WSL2. `ccw` is the cross-platform, self-contained
> equivalent for the one capability the in-session tools can't give you: *multiple
> independent human-driven sessions at once.*

## Commands

| Command | Does |
|---|---|
| `ccw new <branch>` | Create `.worktrees/<branch>/`, `cd` in, launch `claude`. Reuses the branch if it already exists, else creates it. |
| `ccw ls` | List all worktrees (`git worktree list`). |
| `ccw cd <branch>` | Jump into an existing worktree. |
| `ccw merge [branch]` | Merge a worktree's branch into the **primary** working tree's branch (`--no-ff`). Defaults to the current branch. |
| `ccw rm [branch]` | Remove a worktree and prune. Defaults to the one you're standing in (and `cd`s you back to the primary tree first). |

Worktrees always live under `<repo-root>/.worktrees/<sanitized-branch>/`
(`feature/foo` → `feature-foo`). Tab-completion is wired for every subcommand.

**Add `.worktrees/` to each repo's `.gitignore`** so the worktree dirs never get
committed:

```gitignore
.worktrees/
```

## Which parallelism tool for which job?

Three different shapes of "run agents in parallel" — they don't compete, they layer:

| Tool | Sessions | Visibility | Use when |
|---|---|---|---|
| **`Workflow`** (`/orchestrate`) | 1 session, many *background* agents | progress tree, no mid-step glance | decomposable fan-out where you only need the result |
| **agent-teams** (`/fleet`) | 1 session, visible *teammates* in tmux panes | live pane per teammate, steer via `SendMessage` | ambiguous / high-blast-radius work you want to watch |
| **`ccw`** | **many** independent CLI sessions, one per worktree | full terminal each; you drive them | you personally want to hack on 2–3 branches at once, or babysit long autonomous runs side by side |

Rule of thumb: `Workflow`/`/fleet` parallelize *within* one Claude session; `ccw`
parallelizes *across* sessions that you own. See
`rules/ecc/common/agent-fleet.md` for the in-session surfaces.

## Typical flow

```fish
ccw new spike/new-parser   # branch off, opens claude in .worktrees/spike-new-parser
# ...work in that session; open another terminal tab:
ccw new fix/flaky-test     # a second isolated claude session, zero interference
ccw ls                     # see both
ccw merge spike/new-parser # fold the good one back into your primary branch
ccw rm spike/new-parser    # tidy up
```

Pair it with tmux (`prefix c` for a new window per session) to keep several `ccw`
sessions organized in one terminal — the poor-man's cmux, fully on WSL2.
