# Performance Optimization

## Model Selection Strategy (manager-model pattern)

Spend intelligence on the **orchestrator**, keep **workers** cheap and parallel.
Orchestration decisions compound; worker output does not — a small early error in
planning/delegation propagates through the whole run, so the frontier model leads
and cheap workers execute.

**Fable 5** (frontier orchestrator — draws usage faster than Opus, ~2x):
- Lead the high-value *compounding* stages: initial planning, decomposition,
  hard-problem reasoning, final verification
- Long-horizon autonomous runs that plan across stages
- Run at `high` / `xhigh` effort
- **Billing:** included in the Max plan only while Anthropic says so; check the
  current terms before relying on it. Beyond that it draws usage credits at
  roughly 2x the Opus burn. Reach it with `/orchestrate --fable` or `/model fable`;
  `settings.json` carries no `model` key on purpose, so it is never the default.

**Opus 4.8** (free frontier — 1M context, on the subscription):
- Default orchestrator when a task doesn't clear the "super high value" bar
- Deep-reasoning subagents: `architect`, `planner`, the auditors
- Complex single-context coding

**Sonnet 5** (main worker fleet):
- Code review, coding, and analysis workers under the orchestrator
- Fast, near-Opus quality — the default worker tier for fan-out

**Haiku 4.5** (mechanical / high-frequency workers):
- Deterministic-tool workers (`refactor-cleaner`), docs (`doc-updater`), status updates
- Anything mechanical enough to run at `low` effort

**Composition shapes** (see `/orchestrate`):
- **Fan-out** — parallel independent tasks (worktree isolation when they mutate files)
- **Pipeline** — sequential stages with handoffs (the default)
- **Verify-loop** — a frontier verifier checks worker output against the original spec
- **Observability tier** — choose *headless* (`/orchestrate`, `Workflow`) when you
  only need the result, vs *visible/steerable* (`/fleet`, agent-teams in tmux panes)
  when blast radius is high and you want to catch a wrong turn mid-flight. See
  `agent-fleet.md`.

## Context Window Management

Avoid last 20% of context window for:
- Large-scale refactoring
- Feature implementation spanning multiple files
- Debugging complex interactions

Lower context sensitivity tasks:
- Single-file edits
- Independent utility creation
- Documentation updates
- Simple bug fixes

## Extended Thinking + Plan Mode

Extended thinking is on by default (`alwaysThinkingEnabled` in `~/.claude/settings.json`).
For complex tasks: use Plan Mode, run more than one critique round, and use
split-role sub-agents for diverse perspectives.

## Build Troubleshooting

If build fails:
1. Use **build-error-resolver** agent
2. Analyze error messages
3. Fix incrementally
4. Verify after each fix
