# Agent Fleet — Observability & Steering

How to run a fleet of agents so problems surface *early*, not at the end. The
principle (borrowed from cmux-style multi-agent orchestration): **without seeing
intermediate behavior you can't catch a wrong turn until the work is done — a
glance at a live pane catches it in seconds.** Pair this with `performance.md`
→ Model Selection Strategy (who leads, who executes) and `agents.md`.

## Two orchestration surfaces

Pick by **blast radius and how much you need to watch**, not by habit.

| | **Headless** — `/orchestrate` | **Visible/steerable** — `/fleet` |
|---|---|---|
| Backend | `Workflow` background agents | Native agent-teams (tmux panes) |
| Best for | Decomposable fan-out where you only need the *result* — audits, migrations, broad refactors, research sweeps | Long-running, ambiguous, or high-blast-radius work you want to *watch and redirect* |
| Visibility | Progress tree via `/workflows`; no mid-step glance | A pane per teammate; read intermediate output live |
| Steering | Abort/retry the run; re-dispatch a round | Redirect a teammate mid-flight via `SendMessage` |
| Cost shape | Cheapest fan-out; workers are ephemeral | Heavier; panes are long-lived |
| Requires | `skipWorkflowUsageWarning` (set) | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` + `teammateMode: auto` (both set) |

Default to **headless** for scoped, well-specified fan-out. Reach for **visible**
when a wrong plan is expensive to unwind and you'd rather catch it at minute two.

## Worker-role safety (no recursive fleets)

A worker executes **one scoped unit and returns.** A worker must **not** spawn its
own fleet — no nested `/orchestrate`, no nested `/fleet`, no teammate spawning
teammates. Recursion multiplies cost and destroys observability (the cmux
`PI_CMUX_ROLE=worker` guardrail: workers keep visibility/reporting, lose the
ability to sub-spawn). Only the top-level orchestrator decomposes and delegates.

## Lifecycle: spawn → monitor → steer → teardown

The same four verbs regardless of surface — map them to what this harness actually
provides:

| Verb | Headless (`Workflow`) | Visible (agent-teams) |
|---|---|---|
| **spawn** | `agent()` / `pipeline()` / `parallel()` | `Agent` tool with a `name:` → lands in a tmux pane |
| **monitor** | `/workflows` progress tree; journal | Read the teammate's pane; check `inboxes/` + `TaskList` |
| **steer** | abort/retry; dispatch a follow-up round | `SendMessage` to the teammate (redirect or abort) |
| **teardown** | run ends; results returned | close the pane / end the team; mark tasks done |

## Read-to-decide (structured verdicts, not prose)

Branch on **structured signals**, never re-parsed prose — the harness-native
version of cmux's `echo VERDICT=GREEN` / grep-the-screen pattern:

- In `Workflow`: pass `schema=` to any stage whose result you branch on; the
  agent is forced to return a validated object.
- For a shell/agent that prints to a pane: emit a single sentinel line
  (`VERDICT=GREEN` / `VERDICT=RED reason=...`) and grep for it.
- The verify-loop stage checks worker output against the **original spec** and
  returns `{ met: [...], unmet: [...] }` — dispatch a follow-up round for `unmet`.
