# ECC Integration Plan

This spec captures the integration of
[`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code)
(ECC) into Yannick's dotfiles. Executed 2026-05-14 across 8 commits
(`dba3dac` → `a58f7e7`).

## Final tallies
- **23 agents** cherry-picked
- **74 skills** cherry-picked (2 from plan unavailable upstream: `long-context-retrieval`, `logging-patterns`)
- **3 rule packs** (common, typescript, python)
- **3 custom items removed** (learning-coach, cleancode-auditor, simplify-fixer)
- **1 hook removed** (learning_trigger.py) + **1 command removed** (learn.md)
- **2 dead settings keys removed** (voice, voiceEnabled)
- **1 file untracked** (cache/changelog.md)

## Future updates (followup)

A `/update-ecc` skill is planned to re-cherry-pick from upstream periodically.
For now, manual re-runs of the cp sequence in `~/.claude/plans/first-commit-or-stash-glistening-hejlsberg.md`
will work.

---

## Strategic decisions

| Decision | Choice | Rationale |
|---|---|---|
| Install method | **Manual cherry-pick** into dotfiles | Version-controlled, stow-portable, no plugin auto-update opacity, focused config |
| Learning system | **Remove entirely** | Half-broken, overwhelming, not in use; can rebuild later |
| Rules languages | **`common/` + `typescript/` + `python/`** | Languages Yannick actually works in |
| Voice settings | **Remove** dead `voice`/`voiceEnabled` keys | TTS removed 2026-03-05 (per memory) |
| `cache/changelog.md` | **`git rm --cached`** (already gitignored) | Auto-regenerated 1870-line file shouldn't be tracked |

---

## Phase 0 — Preserve existing work (one commit)

**Commit**: `add auditor agents and recap/board-status commands`

Stage:
- `claude/.claude/agents/cleancode-auditor.md` (new)
- `claude/.claude/agents/component-harvest-auditor.md` (new)
- `claude/.claude/agents/monorepo-health-auditor.md` (new)
- `claude/.claude/agents/simplify-fixer.md` (new)
- `claude/.claude/commands/board-status.md` (new)
- `claude/.claude/commands/recap.md` (new)
- `claude/.claude/settings.json` (modifications kept; voice cleanup is Phase 2)

Do not stage:
- `claude/.claude/agents/learning-coach.md` (deleted Phase 1)
- `claude/.claude/cache/changelog.md` (untracked Phase 2)

---

## Phase 1 — Remove learning system (one commit)

**Commit**: `remove learning curriculum system`

Files to delete from dotfiles:
- `claude/.claude/agents/learning-coach.md`
- `claude/.claude/commands/learn.md`
- `claude/.claude/hooks/learning_trigger.py`

Edit `claude/.claude/settings.json` → remove `learning_trigger.py` entry from `Stop` hooks array.

Runtime data (outside dotfiles, separate `rm`, not in commit):
- `~/.claude/learning/` (~26 KB: `taxonomy.json`, `progress.json`, `lessons/`, `archive/`, `queue/`, `ingest.py`)
- If lessons are worth preserving, archive before deleting.

The `ai_docs/*.md` files that mention "learning" in passing are unrelated docs — leave alone.

---

## Phase 2 — Hygiene (one commit)

**Commit**: `clean up dead voice settings and untrack runtime changelog`

1. Remove from `settings.json`:
   ```json
   "voice": {"enabled": true, "mode": "hold"},
   "voiceEnabled": true,
   ```

2. Untrack changelog:
   ```bash
   git rm --cached claude/.claude/cache/changelog.md
   ```
   No `.gitignore` edit — `cache/` is already ignored, the file just predates the ignore rule.

---

## Phase 3 — Adopt ECC rules system (one commit)

**Commit**: `add ECC rules (common, typescript, python)`

```bash
git clone --depth 1 https://github.com/affaan-m/everything-claude-code /tmp/ecc
mkdir -p ~/dotfiles/claude/.claude/rules/ecc
cp -r /tmp/ecc/rules/common      ~/dotfiles/claude/.claude/rules/ecc/
cp -r /tmp/ecc/rules/typescript  ~/dotfiles/claude/.claude/rules/ecc/
cp -r /tmp/ecc/rules/python      ~/dotfiles/claude/.claude/rules/ecc/
rm -rf /tmp/ecc
```

Verify each `rules/ecc/{common,typescript,python}/*.md` is human-readable and on-point.

Expected under `common/`:
`coding-style.md`, `git-workflow.md`, `testing.md`, `performance.md`,
`security.md`, `patterns.md`, `hooks.md`, `agents.md`.

Claude Code auto-loads `~/.claude/rules/**/*.md` — no `settings.json` changes needed.

---

## Critical files modified

- `claude/.claude/agents/` — delete `learning-coach.md`; add 4 auditors
- `claude/.claude/commands/` — delete `learn.md`; add `board-status.md`, `recap.md`
- `claude/.claude/hooks/` — delete `learning_trigger.py`
- `claude/.claude/settings.json` — remove learning_trigger Stop entry; remove voice keys
- `claude/.claude/cache/changelog.md` — `git rm --cached` only (file stays on disk)
- `claude/.claude/rules/ecc/{common,typescript,python}/` — new, copied from ECC

---

## Verification (after all 4 commits)

Open a fresh Claude Code session in `~/dotfiles`:
1. `SessionStart` hook fires cleanly.
2. `Stop` hook fires cleanly (no missing `learning_trigger.py` error).
3. `/help` no longer lists `/learn`.
4. `git status` is clean.
5. Spot-check Claude picks up at least one rule from `~/.claude/rules/ecc/common/coding-style.md`.
6. Auditor agents still launchable via `Agent` tool.

---

## Deferred to follow-up spec(s)

- ECC agent cherry-picks (60 available) → next planning round
- ECC skill cherry-picks (228 available) → next planning round
- ECC command cherry-picks (75 available)
- `continuous-learning-v2` (instinct system) — revisit when a learning replacement is wanted
- Cleanup of unused `status_line_v{1,2,4}.py` variants (only v3 is wired)
- ECC `hooks.json` (Node.js) — explicitly keeping Python `uv run` hook stack
