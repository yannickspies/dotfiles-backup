---
argument-hint: [task description; prefix with --fable to escalate planning/verify to Fable]
description: Manager-model orchestration — a frontier model plans and verifies while cheap workers execute in parallel (fan-out / pipeline / verify-loop)
---

# Orchestrate (manager-model pattern)

Run this task as a **manager-model** multi-agent job: a frontier model *leads*
(plans, delegates, verifies) while cheaper interchangeable workers do the scoped
execution in parallel. Orchestration decisions compound and worker output does
not — so intelligence goes on the orchestrator, and workers stay cheap and fast.

Invoking this command **is** the explicit opt-in to the `Workflow` tool.

## Task

$ARGUMENTS

## When to use this

Big, ambiguous, or multi-file work that decomposes into independent units —
audits, migrations, broad refactors, "do X across the whole app", research
sweeps. **Not** one-liners or single-file edits; for those, just work directly.

## Step 1 — pick the orchestrator tier

Parse the task text above:

- **Default → Opus 4.8** leads planning + verification. Free on the subscription,
  1M context. Use this unless the task clearly clears the "super high value" bar.
- **Escalate → Fable 5** when the invocation starts with `--fable` **or** contains
  "escalate" / "use fable", OR the task is genuinely high-value / complex /
  long-horizon (deep architectural planning, a hard problem where a wrong plan is
  expensive to unwind). Only the **plan + verify** stages run on Fable — workers
  never do.

> **Billing:** Fable is included in the Max weekly limit (≤50%) through
> **2026-07-12**, then draws **usage credits**. It burns ~2x faster than Opus.
> Escalate deliberately; never route workers to Fable.

Strip the `--fable` token from the task before decomposing. State which tier you
chose and why in one line before starting.

## Step 2 — decompose

Break the task into independent worker units. Identify what can fan out in
parallel vs. what must pipeline (later stage needs an earlier stage's output).

## Step 3 — author and run a `Workflow`

Route every stage by model:

| Stage | Model | Effort |
|---|---|---|
| Plan / decompose / verify | `opus` (default) or `fable` (escalated) | `high` / `xhigh` |
| Review, coding, analysis workers | `sonnet` | (default) |
| Mechanical workers (rename, deterministic tools, docs) | `haiku` | `low` |

Rules:
- **`pipeline()` by default.** Reach for `parallel()` only when a stage genuinely
  needs *all* prior results at once (dedup/merge, count-based early exit).
- **Workers that mutate files in parallel → `isolation: 'worktree'`** so they don't
  clobber each other's edits.
- **End with a verify-loop:** a final orchestrator-tier stage that checks the
  worker output against the *original* spec and flags anything unmet. On the
  escalated path this verifier runs on Fable.
- Use `schema` on any stage whose result you branch on, so you get structured
  output instead of parsing prose.

### Skeleton

```js
export const meta = {
  name: 'orchestrate',
  description: '<one line: what this run does>',
  phases: [{ title: 'Plan' }, { title: 'Execute' }, { title: 'Verify' }],
}

const ORCHESTRATOR = /* 'fable' if escalated, else */ 'opus'

// 1. Plan on the orchestrator tier — returns the worker unit list.
phase('Plan')
const plan = await agent(
  `Decompose this task into independent worker units with clear specs:\n<task>`,
  { model: ORCHESTRATOR, effort: 'xhigh', phase: 'Plan', schema: PLAN_SCHEMA },
)

// 2. Fan out workers on cheap models; pipeline each unit through execute→self-check.
const results = await pipeline(
  plan.units,
  (unit) => agent(unit.spec, {
    model: unit.mechanical ? 'haiku' : 'sonnet',
    effort: unit.mechanical ? 'low' : undefined,
    label: `exec:${unit.id}`, phase: 'Execute',
    isolation: unit.mutatesFiles ? 'worktree' : undefined,
    schema: RESULT_SCHEMA,
  }),
)

// 3. Verify-loop on the orchestrator tier — checks results against the spec.
phase('Verify')
const verdict = await agent(
  `Check these results against the original spec; list anything unmet:\n` +
  JSON.stringify(results.filter(Boolean)),
  { model: ORCHESTRATOR, effort: 'high', phase: 'Verify', schema: VERDICT_SCHEMA },
)

return { plan, results: results.filter(Boolean), verdict }
```

Scale the finder/worker count and verify rigor to the task: a few workers +
single verify for a scoped job; a larger fleet + adversarial multi-lens verify
for "audit everything" / "be comprehensive".

## Step 4 — synthesize

Read the verify verdict. If it flags unmet items, dispatch a follow-up worker
round for just those. Then report the outcome to the user — lead with what
happened, list what each worker did, and surface anything the verifier rejected.

---

**Lightweight alternative (no Workflow):** for a single hard *planning moment*
mid-session — not a full fan-out — just `/model fable`, think the problem
through in one turn, then `/model` back to Opus. Reserve `/orchestrate` for
actual multi-worker runs.
