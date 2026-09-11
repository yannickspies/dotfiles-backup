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

## Teammates in tmux panes never exit on their own

With `teammateMode: auto`, an `Agent` call that passes `name:` spawns a persistent
teammate in its own tmux pane. It finishes its turn, sends you its report, and then
idles at a prompt, holding its process and MCP servers, until it is told to stop.
Nothing else closes that pane.

- Prefer an unnamed `Agent` call (in-process subagent, exits when done) unless you
  need to message the worker mid-flight.
- Once a teammate's report is verified, shut it down:
  `SendMessage({to: "<name>", message: {type: "shutdown_request", reason: "done"}})`.
  The teammate approves, its process exits and the pane closes.
- Never end a multi-agent job with teammates alive. Shut down every remaining one
  before the final report.
- Safety net only: the `Stop` hook `hooks/teammate_reaper.py` kills panes of
  teammates idle for more than 10 minutes. Do not rely on it for the happy path.
- A teammate executes one scoped unit and reports back. It must not spawn its own
  team or run `/orchestrate`. Only the lead decomposes and delegates.

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
