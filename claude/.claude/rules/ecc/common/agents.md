# Agent Orchestration

## Available Agents

Located in `~/.claude/agents/`:

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| planner | Implementation planning | Complex features, refactoring |
| architect | System design | Architectural decisions |
| code-architect | Feature architecture blueprint from existing patterns | Designing a feature's file/interface layout |
| tdd-guide | Test-driven development | New features, bug fixes |
| code-reviewer | General / architecture code review (language-agnostic) | After writing code |
| typescript-reviewer | TS/JS-specific review | TS/JS changes |
| python-reviewer | Python-specific review | Python changes |
| security-reviewer | Security analysis (OWASP) | Auth, input, endpoints, secrets |
| silent-failure-hunter | Swallowed errors / bad fallbacks | Reviewing error handling |
| comment-analyzer | Comment accuracy / rot | Reviewing in-code comments |
| type-design-analyzer | Type design & invariants | Reviewing type/model design |
| pr-test-analyzer | PR test-coverage quality | Assessing tests on a change |
| code-simplifier | Clarity/consistency refactor | Simplifying recently-changed code |
| refactor-cleaner | Dead-code cleanup (`pnpm dlx knip`) | Removing unused code |
| build-error-resolver | Fix build/type errors (minimal diff) | When build fails |
| e2e-runner | E2E testing (Playwright) | Critical user flows |
| performance-optimizer | Perf profiling & optimization | Bottlenecks, bundle size |
| code-explorer | Read-only codebase tracing | Understanding an existing feature |
| doc-updater | Docs & codemaps | Updating documentation |
| component-harvest-auditor | @yspies/ui + design-token audit | Monorepo UI/token compliance |
| monorepo-health-auditor | Cross-cutting duplication / boundary audit | Monorepo consolidation checks |
| harness-optimizer | Improve local agent-harness config | Tuning agents/hooks/settings |
| meta-agent | Generate a new sub-agent config | Creating a new agent |
| conversation-analyzer | Find hook-worthy behaviors in transcripts | /hookify |
| luisterlink-growth-strategist | Dutch DTC growth & marketing strategy for Luisterlink | Channel research, campaign blueprints (`/plan-campaign`) |
| chief-of-staff | Multi-channel comms triage | Gmail wired; Slack/LINE/Messenger aspirational — see note |

## Parallel Task Execution

For big/ambiguous/multi-file work, run the **manager-model pattern** via
`/orchestrate` (frontier model plans + verifies, cheap workers execute in
parallel; `--fable` escalates the plan/verify tier). See `performance.md` →
Model Selection Strategy.

Two surfaces, by how much you need to watch (see `agent-fleet.md`):
- **`/orchestrate`** — *headless* fan-out; you get the result, no mid-flight glance.
- **`/fleet`** — *visible/steerable* agent-team in tmux panes; watch and redirect
  long-running or high-blast-radius work as it goes.

ALWAYS use parallel Task execution for independent operations:

```markdown
# GOOD: Parallel execution
Launch 3 agents in parallel:
1. Agent 1: Security analysis of auth module
2. Agent 2: Performance review of cache system
3. Agent 3: Type checking of utilities

# BAD: Sequential when unnecessary
First agent 1, then agent 2, then agent 3
```

## Multi-Perspective Analysis

For complex problems, use split role sub-agents:
- Factual reviewer
- Senior engineer
- Security expert
- Consistency reviewer
- Redundancy checker
