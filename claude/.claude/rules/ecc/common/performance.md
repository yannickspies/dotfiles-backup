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
- **Billing:** under the current terms it's included in the Max weekly limit for
  ≤50% of it; beyond that it draws **usage credits** (pay-as-you-go). Check the
  current Fable billing terms before relying on inclusion. Invoke
  deliberately via `/orchestrate --fable`, not for routine turns.

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

Extended thinking is enabled by default, reserving up to 31,999 tokens for internal reasoning.

Control extended thinking via:
- **Toggle**: Option+T (macOS) / Alt+T (Windows/Linux)
- **Config**: Set `alwaysThinkingEnabled` in `~/.claude/settings.json`
- **Budget cap**: `export MAX_THINKING_TOKENS=10000`
- **Verbose mode**: Ctrl+O to see thinking output

For complex tasks requiring deep reasoning:
1. Ensure extended thinking is enabled (on by default)
2. Enable **Plan Mode** for structured approach
3. Use multiple critique rounds for thorough analysis
4. Use split role sub-agents for diverse perspectives

## Build Troubleshooting

If build fails:
1. Use **build-error-resolver** agent
2. Analyze error messages
3. Fix incrementally
4. Verify after each fix
