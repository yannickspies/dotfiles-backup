# Dotfiles Audit & Findings Report

> **Deliverable type:** Findings report (per your choice: "just the report").
> This is a prioritized map of what to clean up, fix, and — where you want it —
> expand. Nothing here has been changed. You can act on sections yourself, or
> hand me any P0/P1 block later and say "do this section."
>
> Suggested home once approved: move this to `docs/dotfiles-audit.md` (it's
> currently a plan-mode scratch file).

## Context

You asked for a high-IQ pass over the dotfiles to find where to **improve, clean
up, or expand**. The repo has grown organically — a large ECC (everything-claude-code)
import in May, a removed TTS/voice subsystem, a fish setup with heavy plugin
vendoring, and two parallel Neovim configs. The audit ran three parallel explorers
(shell/core, Claude config, neovim) plus direct git/settings recon.

**The through-line:** the biggest issues aren't missing features — they're
**dead code that memory says was removed but still ships**, **configs that
silently fail** (statusline, qwen naming, gitsigns keymaps), and **runtime
artifacts committed to git**. Cleaning these is low-risk and high-value.

### Your decisions (baked into recommendations below)
- **Neovim:** you've moved to agentic engineering and rarely use nvim → **keep it
  light, remove unused code**, retire the abandoned second config. No expansion.
- **TTS/voice:** **fully excise.**
- **qwen2.5:3b naming + rich statusline:** **revive it** (it's currently dead).

### Severity legend
| Tag | Meaning |
|-----|---------|
| **P0** | Broken / dead / actively misleading — fix or delete |
| **P1** | Hygiene & correctness — clear win, low risk |
| **P2** | Modernization / expansion — optional, higher effort |

---

## Part 1 — Claude config (`claude/.claude/`) — largest surface

### P0 — Dead code & broken references

| Item | Evidence | Action |
|------|----------|--------|
| **TTS/voice residue (fully excise)** | `hooks/utils/tts/` (elevenlabs/openai/pyttsx3 + committed `__pycache__/*.pyc`); `output-styles/tts-summary.md`; `agents/work-completion-summary.md` (dead `mcp__ElevenLabs__*` tools, hardcodes user "Dan"); dead `get_tts_script_path()`/`announce_*()` in `stop.py`, `subagent_stop.py`, `notification.py`, `session_start.py`; `settings.json` `voice`+`voiceEnabled` keys; `.env.sample` TTS block; empty `data/tts_queue/` | Delete all. The `docs/ecc-integration-plan.md` already records `voice` keys as "removed" — they crept back. |
| **qwen naming + rich statusline are DEAD** | `settings.json` runs `user_prompt_submit.py --log-only`; session files are only written under `--store-last-prompt`/`--name-agent`, so `status_line_v3.get_session_data()` always errors → base line renders `""`. Only the EUR cost segment shows. The whole `hooks/utils/llm/` (anth/oai/ollama) tree is unreachable as a result. | **Revive:** change the UserPromptSubmit hook to `--store-last-prompt --name-agent` (keep logging). This lights up qwen agent-naming + the agent-name/recent-prompts statusline. |
| **`docs-lookup` agent has a wrong tool name** | Declares `mcp__context7__query-docs` (lines 4,29,33,42,67); real Context7 tool is `get-library-docs`. Agent silently fails to fetch docs. | Fix tool name → `mcp__context7__get-library-docs` (verify against installed Context7 server first). |
| **Rules reference non-existent agents** | `rules/ecc/common/code-review.md` "Agent Usage" table lists `go-reviewer` and `rust-reviewer` — neither exists in `agents/`. | Remove those rows (or create the agents — but you have no Go/Rust surface). |
| **`pre_tool_use.py` rm-guard over-blocks** | `dangerous_paths` includes bare `*` and `.`, so ordinary `rm -rf ./build` or `rm -rf node_modules/*` get **blocked** (exit 2). | Tighten the guard to genuinely dangerous roots (`/`, `~`, `$HOME`, bare `rm -rf *` at cwd) rather than any wildcard/dot. |
| **Misplaced skill (not discoverable)** | `skills/pr-summary-dutch.md` sits directly under `skills/` instead of `skills/pr-summary-dutch/SKILL.md`; CC discovers via `<dir>/SKILL.md`. | Move to `skills/pr-summary-dutch/SKILL.md`. |
| **Ollama model mismatch (3 places)** | `.env` → `qwen2.5:3b` (wins at runtime); `hooks/utils/llm/ollama.py:39` default → `gpt-oss:20b`; `.env.sample:18` → `llama3.2:latest`. | Align `ollama.py` default and `.env.sample` to `qwen2.5:3b`. |

### P1 — Hygiene & staleness

| Item | Evidence | Action |
|------|----------|--------|
| **113 runtime files tracked in git** | `tasks/` (49), `paste-cache/` (48), `telemetry/` (6), `teams/` (10) are committed. `.claude/.gitignore` already ignores the first three — they were committed *before* the rule, so git still tracks them. `teams/` isn't ignored at all. | `git rm -r --cached` those four dirs; add `teams/` to `.claude/.gitignore`. |
| **3 of 4 statusline scripts dead** | Only `status_line_v3.py` is referenced by `cost_statusline.py`. `status_line.py`, `_v2.py`, `_v4.py` unused (v4 is *newer* than v3 — abandoned upgrade). | Keep v3, delete the other three (or promote v4 deliberately). |
| **`agents.md` rule table stale** | Lists 9 agents; you have 27. Disagrees with `code-review.md`'s roster. | Regenerate the table from the actual `agents/` dir. |
| **`hooks.md` rule outdated** | Documents only PreToolUse/PostToolUse/Stop; live system runs 8 events. Points to `~/.claude.json allowedTools` for permissions, but you configure via `settings.json permissions`. | Rewrite to match the 8 wired events + real scripts. |
| **README severely stale** | Says "3 sub-agents", "10 commands"; omits `skills/` and `rules/` entirely; still credits the upstream `disler` scaffold. | Refresh counts (27 agents, 20 commands, 75 skills, rule packs). |
| **Time-bomb billing note** | `performance.md` Fable billing pinned to "through 2026-07-12" — now past. | Soften to "check current Fable billing terms" instead of a hard date. |
| **`hello-world-agent.md`** | Upstream tutorial cruft (greets on "hi claude"). | Delete. |
| **Dead learning hook** | `skills/continuous-learning-v2/hooks/observe.sh` isn't wired into `settings.json` — inert unless installed. | Wire it in or note it as opt-in in the skill. |
| **Settings keys to verify** | `permissions.defaultMode: "auto"` may be non-canonical (CC modes are `default`/`acceptEdits`/`plan`/`bypassPermissions`); `enabledPlugins` assumes the marketplace is installed. | Verify against current CC schema; correct `defaultMode` if invalid. |

### P2 — Consolidation (optional; you ship the tools to do it)

- **Overlap sprawl:** the same domain is covered 3–4× across skills/agents/commands/rules — git (`skills/git-workflow` + `rules/git-workflow.md` + `/commit` + `/git_status`), security (3 skills + agent + rule), testing (3 skills + 3 agents + rule), cleanup (`code-simplifier` agent + `/cleancode` + `simplify` skill). Big context-budget surface. Run the shipped **`context-budget`** and **`skill-stocktake`** skills to prune.
- **6 near-duplicate `board-status` commands** → one parameterized command taking a board name.
- **Overlapping architect agents** (`architect` vs `code-architect`) — merge charters.
- **Monorepo-coupled agents** (`monorepo-health-auditor`, `component-harvest-auditor`) reference a `@yspies/ui`/`primeng`/`CLAUDE.md` that isn't in dotfiles — dead weight outside that repo; keep only if you still work in it.

### P2 — Worthwhile additions
- **PostToolUse auto-formatter:** `hooks.md` promises "auto-format" but `post_tool_use.py` only logs. The shipped **`plankton-code-quality`** skill does exactly this — wire it in.
- **`common/mcp.md` rule** documenting expected MCP servers (trello, context7, firecrawl, browser-tools) — several agents/commands depend on them silently.

---

## Part 2 — Shell & core tooling (fish, tmux, git)

### P0 — Portability breakage
| Item | Evidence | Action |
|------|----------|--------|
| **Unguarded uv source** | `conf.d/uv.env.fish` → `source "$HOME/.local/bin/env.fish"` with no `test -e`; errors on any machine without uv. | Guard with `test -e`. |
| **Hardcoded CHROME_BIN** | `config.fish:2` sets `/usr/bin/chromium-browser` unconditionally; path usually absent on WSL. | Make conditional or remove. |

### P1 — Hygiene
| Item | Evidence | Action |
|------|----------|--------|
| **~140 of 149 fish function files are vendored** | `fish_plugins` declares plugins, but every fisher-installed file (`_pure_*`, `_nvm_*`, `_autopair_*`, `__z*`, `nvm.fish`, `fisher.fish`, catppuccin themes) **and** ~130 generated eza `l*` alias functions are also committed. On a fresh clone, `stow` + `fisher install` → guaranteed drift. Only ~5 files are hand-written (`ccw`, `claude`, `claude-scan`, `eza_git`, `fish_greeting`). | Stop committing fisher-generated files + the eza alias explosion; keep `fish_plugins` + hand-written functions, let fisher regenerate. Removes ~140 files. |
| **Duplicated theme copies** | `themes/` vs `themes/static/` | Drop one. |
| **Dead greeting** | `fish_greeting.fish` only calls `_pure_check_for_new_release`, which `pure.fish` disables → no-op. | Delete. |
| **`logs/` = 5.3 MB untracked cruft** | Gitignored runtime hook logs piling up in repo root. | Periodic cleanup; consider redirecting hook logs out of the repo tree. |
| **Retired file in tree** | `windows/wezterm/wezterm.lua.retired` | Delete (git history preserves it). |
| **Git email mismatch** | Tracked-nowhere `~/.gitconfig` uses `yannickspies@gmail.com`; session context shows `yannickspies91@gmail.com`. | Confirm which is intended. |

### P1 — Reproducibility (the single biggest gap)
- **No bootstrap script and no root README.** Fresh-machine setup (stow invocation, `fisher install`, TPM clone + `prefix+I`, tool installs: eza/fzf/win32yank/uv/node, theme selection) is entirely tribal knowledge. **Add `install.sh` + root `README.md`.** This is the highest-leverage single addition for the whole repo.
- **No tracked gitconfig / gitignore_global.** Git config lives only in unmanaged `~/.gitconfig` (2 lines) + `~/.config/git/ignore` (1 line). Given how worktree-heavy your workflow is (`ccw`), a managed gitconfig (aliases, `pull.rebase`, `push.autoSetupRemote`, `rerere`, `init.defaultBranch`, delta pager) is a big low-effort win.

### P2 — Modernization (optional)
- `jethrokuan/z` (legacy) → **zoxide** (`zi` interactive, DB-backed).
- Add **fzf + fzf.fish** (Ctrl-R history / Ctrl-T file) — currently absent.
- `nvm use lts` runs on *every* interactive shell (`config.fish:11`), redundant with `conf.d/nvm.fish` — measurable per-pane cost. Consider **mise** to replace `nvm.fish` and manage node/python via `.tool-versions`.
- **atuin** (searchable history), **direnv** (per-project env).
- Bridge fish's own `fish_clipboard_copy`/`paste` to `win32yank.exe` (only tmux copy-mode is wired today).
- tmux: move `~/.tmux.conf` → XDG `~/.config/tmux/tmux.conf`; pin `tpm`/`tmux-sensible` versions; bootstrap TPM in the install script.

---

## Part 3 — Neovim (keep light, remove unused — per your directive)

Since you've largely moved off nvim, the recommendation is **trim, not expand.**

### P0 — Retire the abandoned second config
- **Two unrelated nvim configs exist.** Active: **kickstart.nvim** at `dotfiles/nvim/.config/nvim` (symlinked to `~/.config/nvim`, last touched 2026-06). Abandoned: **LazyVim** at `wsl-dotfiles/nvim` (not wired to anything, last touched 2025-07). → **Delete/archive `wsl-dotfiles/nvim`.** You're maintaining two configs and using neither much.

### P1 — Strip dead code from the active kickstart config
- Delete unloaded files: `lua/kickstart/plugins/debug.lua`, `lint.lua`, `indent_line.lua`, the kickstart `gitsigns.lua` (commented out at `init.lua:771-776`), and the empty `lua/custom/plugins/init.lua` stub.
- Strip kickstart boilerplate: the ASCII/`:Tutor` header (`init.lua:1-85`) and the scattered "MOVED TO:" breadcrumb comments (~lines 288, 312, 328, 337, 755-787).
- **Dead config blocks:** `snacks.lua:37-49` `notifier_opts` is not a valid snacks key (silently ignored); `friendly-snippets` is commented out (`init.lua:673-678`) so LuaSnip has no snippet library loaded.

### P1 — Two live bugs (fix only if you still open nvim occasionally)
- **`<leader>sn` double-bound:** `telescope.lua:91` ("Search Neovim files") vs `snacks.lua:53` ("notification history") — snacks wins, telescope one is dead.
- **Misleading which-key group:** `which-key.lua:48-52` labels `<leader>h` as "Git Hunk", but `<leader>h*` is actually **Harpoon**; the git-hunk maps live only in the *unloaded* gitsigns file, so there are currently **no active gitsigns keymaps** at all.
- **Treesitter on experimental `main` branch** (`custom/plugins/treesitter.lua`) with no `vim.treesitter.start()` call and `lazy-lock.json` still pinned to `master` — highlighting may not actually be active. Git history shows repeated "fix treesitter" commits. Simplest fix for a light config: move back to `master` with classic `highlight = { enable = true }`.

> Explicitly **not recommended** given your directive: the snacks-picker/LSP-extras/AI-plugin expansions the explorer surfaced. Keep it minimal.

---

## Part 4 — Repo-wide git hygiene

- **`git rm -r --cached`** the 113 tracked runtime files (Part 1 P1) — biggest single de-noise.
- Add to ignore: `claude/.claude/teams/`, any `__pycache__/`, `*.pyc`.
- `docs/ecc-integration-plan.md` is a completed one-time migration record — consider moving to an `docs/archive/` folder so it's not mistaken for live guidance.

---

## Recommended execution order (if/when you act)

1. **TTS excision** (Part 1 P0) — self-contained, matches documented removal.
2. **Revive qwen/statusline** (Part 1 P0) — one hook-flag change, unlocks a dead feature.
3. **`git rm --cached` runtime files** (Part 4) — biggest de-noise, zero behavior change.
4. **Fix broken agent/rule references** (Part 1 P0: docs-lookup, code-review roster, rm-guard, pr-summary-dutch, ollama model).
5. **Add `install.sh` + root README + managed gitconfig** (Part 2 P1) — closes the reproducibility gap.
6. **De-vendor fish** (Part 2 P1) — removes ~140 files; do after the bootstrap script exists so a fresh clone still works.
7. **Neovim trim + retire second config** (Part 3).
8. **P2 consolidation/modernization** — as appetite allows.

## Verification (for whichever items get executed)
- **TTS/qwen/statusline:** after changes, start a fresh CC session and confirm the statusline shows an agent name + recent prompts + EUR cost (not just cost); confirm no hook errors in `logs/`. `grep -ri 'tts\|voice\|elevenlabs' claude/` should return nothing but false positives.
- **Runtime untracking:** `git status` clean after `git rm --cached`; the dirs still exist on disk and regenerate.
- **Fish de-vendor:** on a throwaway checkout, run the new `install.sh` (stow + `fisher install`) and confirm prompt/aliases/nvm all come back.
- **Hooks:** `uv run claude/.claude/hooks/<each>.py < /dev/null` should exit cleanly with TTS code removed.
- **Neovim (if kept):** `:checkhealth`, `:Lazy sync`, confirm treesitter highlighting via `:Inspect`, and that `<leader>sn` / gitsigns keymaps resolve.
