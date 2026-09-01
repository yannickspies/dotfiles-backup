# Harness review, 2026-09-01

> Status: every item below was executed on 2026-09-01 (dotfiles `f32abb2..6e7e93c`, monorepo `0c69d720`). Repo stays public by decision; the InShared agents were deleted instead. Statusline went native (`session_name` + cost + rate limits); no Ollama.

The harness spends its safety budget on a regex that blocks `rm -rf dist` while pre-approving `git reset --hard`. Its eight hooks only duplicate the transcript. Its rule files contradict the feedback memories. Those three families cause most of the variance between models, because a model facing conflicting instructions picks a side by temperament.

Scope is the dotfiles `.claude/` tree plus the monorepo's `.claude/`, `.mcp.json` and project memory. Method: read every config file. Ran the rm-guard against 14 probe commands. Checked every tool and server name an agent references against this build (Claude Code 2.1.257). Re-checked the open items from `dotfiles-audit.md`. That audit's shell, tmux and Neovim parts are not repeated here.

## Fable is the default model again, re-added inside a wezterm commit

`settings.json` sets `"model": "fable"` and `"effortLevel": "xhigh"`. Commit `e503cd9` (2026-08-17) removed the Fable default on purpose. Commit `daa1ce4` (2026-08-30, "feat(windows): revive wezterm as nightly trial") put it back. Nothing else changed. The plan memory still says Fable is deliberate paid spend. `performance.md` still says to invoke it deliberately via `/orchestrate --fable` and not for routine turns. `orchestrate.md` still quotes a billing window that ended 2026-07-12.

Either the default is intended, and three documents need to say so, or it is not, and the key goes. This is the one decision the review cannot make.

## The rm-guard blocks text, not deletion, and the allowlist covers what it misses

`pre_tool_use.py` lower-cases the command and searches for `rm` followed by a recursive flag and any slash, dot or star. Probe results:

| Command | Guard says | Deletes anything? |
|---|---|---|
| `rm -rf dist` | blocked | yes, one build dir |
| `git rm -r --cached tasks/` | blocked | no, index only |
| `echo "rm -rf /" > notes.txt` | blocked | no |
| `grep -n "rm -rf" hooks/pre_tool_use.py` | blocked | no |
| `find / -delete` | allowed | everything |
| `git clean -fdx` | allowed | every untracked file |
| `git reset --hard origin/main` | allowed | all local work |
| `python3 -c "shutil.rmtree('dist')"` | allowed | yes |
| `rsync -a --delete empty/ dist/` | allowed | yes |

The guard blocked this review's own read-only probe because the command line contained the string `rm -rf /` inside quotes. The project memory records the workaround ("use `find -delete`"), so the harness now trains every model to route around its one guard.

The monorepo's `.claude/settings.local.json` makes it worse. It holds about 200 allow rules. Inference: under `defaultMode: auto`, an explicit allow rule skips the classifier, so these are the only commands that never get judged at all.

| Allow rule | What it pre-approves |
|---|---|
| `Bash(git:*)`, `Bash(git clean:*)` | force-push, hard reset, clean of untracked files |
| `Bash(python3:*)`, `Bash(node:*)`, `Bash(find:*)` | any deletion the rm-guard cannot see |
| `Bash(railway ssh *)`, `Bash(railway run *)` | shell on production services |
| `Bash(psql:*)`, `Bash(sudo -u postgres psql:*)` | any SQL against any reachable database |
| `Bash(curl:*)` | outbound upload of anything |
| `Bash(done)`, `Bash(break)`, `Bash(and echo *)`, `Bash(cp klein-package.webp starter-package.webp)` | one-off junk that can never match again |
| `Read(//home/yannickspies/apps/chores/**)` | a path that does not exist |
| Stripe webhook update with a specific live endpoint id | one historical command |

Fix: the guard checks the resolved target path, not the text. Block deletion whose target is `/`, `~`, `$HOME`, a `..` walk, or an absolute path outside the repo. Match only `Bash`. Cut the allowlist to read-only and build commands (`nx`, `pnpm`, `git status/log/diff`, `grep`, `ls`) and let auto mode classify everything else.

## All eight hooks only log, and they log every tool result to plaintext

None of the hooks is invoked with the flag that makes it do its job. `user_prompt_submit.py` runs with `--log-only`; `stop.py`, `subagent_stop.py`, `notification.py`, `session_start.py` and `pre_compact.py` run with no flags, so their text-to-speech (TTS), context-loading and backup branches are dead code. What remains is eight Python processes per lifecycle event that append the full hook payload to a JSON array and rewrite the whole file. Sizes in megabytes (MB):

| File | Size |
|---|---|
| `logs/post_tool_use.json` | 2.7 MB |
| `logs/status_line.json` | 2.6 MB |
| `logs/pre_tool_use.json` | 0.5 MB |
| `logs/` total | 6.4 MB |

Claude Code already keeps the full transcript in `~/.claude/projects/<slug>/*.jsonl`. The hook logs are a second copy with no rotation and no redaction, so any `railway variables`, `stripe` or `.env` output lands on disk in plaintext. Checked today: the only credentials present are localhost Postgres URLs. The risk is the mechanism, not a leak found.

The log path is `Path.cwd() / 'logs'`, so sessions started or `cd`'d inside a subdirectory spray `logs/` folders: `rules/yspies/common/logs`, `agents/logs`, `output-styles/logs`, `skills/logs` inside the dotfiles, and `~/.claude/.claude/data/sessions` at home. The memory documents the cleanup command instead of the one-line fix (`$CLAUDE_PROJECT_DIR`).

Fix: delete the seven logging hooks and the `utils/` tree. Keep one `PreToolUse` hook matched on `Bash` with the path-based guard above. The `statusLine` entry stays.

## The public dotfiles repo carries employer-internal agents

`gh repo view` reports the visibility of `yannickspies/dotfiles-backup` as public. Tracked in it: `agents/funnel-expert.md`, `agents/i18n-sync.md`, `agents/wuc-migrator.md`, `agents/myzone-redesign-specialist.md` and `commands/pr-status.md`. They describe InShared's funnel architecture, the MyZone redesign rules from epic OPPO-15409, the POEditor translation flow and third-party integrations by name.

They also load into every personal session: the four agents have no `model` or `tools` frontmatter and their descriptions sit in the system prompt of a monorepo session that has no `apps/inshared-*` to point them at.

Fix: move them to the work repo's `.claude/agents/` and remove them from history, or make the repo private. Decision is the owner's.

## Agents name tools and servers this build does not have

| Reference | Where | Reality |
|---|---|---|
| `TaskCreate`, `TaskList`, `TaskUpdate` | 14 mentions across agents, `agent-fleet.md`, `/fleet` | not found by ToolSearch in this session |
| `TodoWrite` | `hooks.md`, 4 mentions | not found |
| `MultiEdit` | `meta-agent`, both auditors | not found |
| `mcp__context7__*` | `docs-lookup`, `development-workflow.md` | no context7 server in `~/.claude.json` or `.mcp.json` |
| Vercel `agent-browser` "preferred" | `e2e-runner` | not installed |
| `knip`, `ts-prune`, `depcheck` | `refactor-cleaner` | not installed |

The earlier audit fixed the Context7 tool name inside `docs-lookup` without noticing the server was never configured. `meta-agent` declares `Write` and `MultiEdit` but neither `Read` nor `Edit`, so it cannot open an existing agent to model a new one on. An agent with a phantom tool silently runs with fewer tools than its charter says.

## The imported rule pack contradicts the feedback memories, so each model picks a side

The everything-claude-code (ECC) rule pack under `rules/ecc/common/` and the feedback memories are both loaded every session. Where they disagree, the model resolves it by temperament, which is most of the difference between models on this harness.

| ECC rule says | Feedback memory says |
|---|---|
| `development-workflow.md`: write a product requirements doc (PRD), architecture, system design, tech doc and task list before coding | short docs, don't pre-decide; minimal-first |
| `development-workflow.md`: run `gh search repos` before writing anything new | no equivalent; never done in practice |
| `testing.md`: 80% coverage, unit + integration + e2e all required, test-driven development (TDD) mandatory | deliver only what was asked; no widening into tests or docs |
| `agents.md`: spawn `code-reviewer` after every edit, `tdd-guide` for every bug fix, no prompt needed | no unwanted scope |
| `hooks.md`: never use dangerously-skip-permissions; configure `allowedTools` in `~/.claude.json` | `settings.json` sets `skipDangerousModePermissionPrompt: true`; that `allowedTools` is empty |
| `code-review.md`: block on missing 80% coverage | same as above |

`hooks.md` also says the Stop hook fires "when session ends" (it fires when Claude finishes a reply) and recommends `TodoWrite`. `performance.md` quotes a 31,999-token thinking reserve and an Option+T toggle that are unverified.

Fix: delete `development-workflow.md`, `testing.md`, `code-review.md`, `hooks.md`, `patterns.md` and `security.md` from `rules/ecc/common/`, or cut each to the five lines that are enforced. Keep `epistemics.md`, `writing.md`, `agent-fleet.md` and `performance.md` after the tool-name fixes. Every session loads this much before the first message, roughly 21k tokens in total:

| Always-loaded file | Size |
|---|---|
| `CLAUDE.md` (monorepo) | 24.7 KB |
| `MEMORY.md` | 16.2 KB |
| `writing.md` | 9.3 KB |
| ECC common rules, 12 files | about 25 KB |
| Output style | 8 KB |

## The output style fights the platform's own writing guidance

`plain-english.md` puts the conclusion last and bans a closing recap. The harness text every model also receives says "lead with the answer or outcome" and "close with a short recap". The style never says it overrides those, so a model that weights platform text higher answers twice. One line at the top of the style fixes it: "This overrides the harness defaults to lead with the answer and close with a recap."

## `/commit` stages everything, which is the failure the worktree memory exists for

`commit.md`: "Create a single git commit with ALL changes (both staged and unstaged)". `feedback_use_worktrees` records two entanglements caused by exactly that and ends with "stage only the files for the task at hand". The command also asks for a 50-character subject with no type prefix, while `git-workflow.md` wants conventional commits and the repo's commitlint enforces a 100-column body. Fix: `/commit` names the files it stages and uses `<type>: <subject>`.

## Skills: 72 disabled directories shipped, 5 overrides pointing at nothing, 13 still referenced

`skillOverrides` turns off 74 names. An agent told to use a disabled skill gets nothing.

| Problem | Names |
|---|---|
| Override with no directory on disk | `angular-developer`, `autonomous-loops`, `pr-summary-dutch`, `rules-distill`, `strategic-compact` |
| Disabled but still named by an agent or rule | `tdd-workflow`, `security-review`, `git-workflow`, `e2e-testing`, `coding-standards`, `backend-patterns`, `frontend-patterns`, `python-patterns`, `python-testing`, `design-system`, `brand-voice`, `content-engine`, `crosspost` |
| Bare file instead of `<dir>/SKILL.md`, so undiscoverable | `skills/read-lighthouse-json.md` |

Fix: delete the 72 directories (git keeps them), drop the overrides block, fix the 13 references, move the Lighthouse skill into a directory.

## Status line runs an unpinned npm package on every refresh

`cost_statusline.py` shells out to `npx -y ccusage@latest statusline` each time the status line redraws. The package is unpinned and `ccusage` is already installed under nvm. The base line it wraps (`status_line_v3.py`) reads session files that only `user_prompt_submit.py --store-last-prompt` writes, and that flag is not passed, so the base segment has been empty since at least the earlier audit. Fix: call the installed binary or pin a version; either pass the flag or drop v3.

## Memory carries a status claim, 14 dead links and a wrong fact about the hook

`MEMORY.md` says "SpiesLabs portfolio — not deployed yet", a status claim the memory rules ban. The gotcha line "pre-tool hook blocks reading `.env`" is wrong: the hook has no `.env` logic. Inference: that block comes from Claude Code itself. Fourteen `[[links]]` resolve to nothing:

| Cause | Links |
|---|---|
| Slug mismatch between `-` and `_` | `luisterlink-is-live`, `use-worktrees`, `tone-luisterlink-outreach`, `trello-board-per-project` |
| Note never written | `fable-orchestration-setup`, `theme-scope-system`, `project_growth_mindset_app`, `project_storybook_theme` |
| Other | six more, all in `reference_*` and `project_*` files |

## Still open from the 2026-08 audit

| Item | State |
|---|---|
| TTS residue: `hooks/utils/tts/`, `__pycache__`, `.env.sample` TTS keys | still present |
| rm-guard over-blocks | still present, now shown to be bypassable too |
| Setup readme says 3 agents, 10 commands, credits the upstream scaffold | still stale |
| Statusline base segment dead | still dead |
| Fable billing date in `orchestrate.md` | still 2026-07-12 |
| Ollama model default mismatch | not re-checked |
| `hello-world-agent.md`, tracked runtime files, `docs-lookup` tool name, `agents.md` table | done |

## Two decisions first, then eight mechanical fixes

| # | Action | Needs a decision |
|---|---|---|
| 1 | Fable default: keep and document, or remove the key | yes |
| 2 | InShared agents out of the public repo | yes |
| 3 | Replace eight hooks with one path-based Bash guard; delete `logs/` folders | no |
| 4 | Prune `.claude/settings.local.json` to read-only and build rules | no |
| 5 | Delete or cut the six ECC common rules; add the override line to the output style | no |
| 6 | Delete 72 skill dirs and the overrides block; fix 13 references | no |
| 7 | Fix phantom tool names; remove Context7, agent-browser and knip claims or install them | no |
| 8 | `/commit` stages named files with a conventional type | no |
| 9 | Pin or localize `ccusage`; fix or drop `status_line_v3` | no |
| 10 | Memory: fix 14 links, drop the status line, correct the `.env` claim | no |
