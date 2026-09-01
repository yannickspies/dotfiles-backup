---
argument-hint: [task description you want to watch a team work on]
description: Stand up a visible, steerable agent-team (tmux panes) for work you need to watch — the observable counterpart to headless /orchestrate
---

# Fleet (visible, steerable agent-team)

Run this task as a **visible team**: named teammates each work in their own tmux
pane so you can *watch intermediate behavior and redirect mid-flight*. This is the
observable counterpart to `/orchestrate` (which runs headless background
`Workflow` agents you can't glance at). Same manager-model economics — a frontier
model leads, cheap teammates execute — but here the point is **catching a wrong
turn at minute two instead of at the end.**

Requires the already-enabled `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` +
`teammateMode: auto`. See `rules/ecc/common/agent-fleet.md` for the surfaces table
and `performance.md` for model tiers.

## Task

$ARGUMENTS

## When to use this — vs `/orchestrate`

| Reach for `/fleet` (visible) | Reach for `/orchestrate` (headless) |
|---|---|
| Long-running, ambiguous, or high-blast-radius work | Well-specified, decomposable fan-out |
| You want to read panes and steer as it goes | You only need the final result |
| A wrong plan is expensive to unwind | Cheap ephemeral workers, no babysitting |

Not for one-liners or single-file edits — just work directly.

## Step 1 — pick the lead tier

Same rule as `/orchestrate`: **Opus 4.8** leads by default (free, 1M context);
**Fable 5** only when the task is genuinely high-value / long-horizon or the
invocation says `--fable` / "escalate". Teammates never run on Fable. State the
tier and why in one line.

## Step 2 — decompose into teammates

Break the task into independent, **named** units — each becomes one teammate in
one pane. Give every teammate: a short name, a scoped prompt, its `cwd`, and a
clear "report back when done" instruction. Keep the fleet small enough to watch
(≈2–5 panes); past that, prefer headless `/orchestrate`.

Route models per `performance.md`:

| Role | Model |
|---|---|
| Lead (you — plan, monitor, verify) | `opus` (or `fable` if escalated) |
| Coding / review / analysis teammates | `sonnet` |
| Mechanical teammates (rename, docs, deterministic tools) | `haiku` |

## Step 3 — spawn → monitor → steer → teardown

Use **only** the native primitives (do not invent CLI verbs):

- **spawn** — launch each teammate with the `Agent` tool, passing a `name:` so it
  becomes addressable; with `teammateMode: auto` it lands in its own tmux pane.
- **monitor** — glance at each pane; `ListAgents` shows who is still running.
- **steer** — redirect or abort a teammate mid-flight with `SendMessage` (by name).
  This is the whole reason to use `/fleet` — use it the moment a pane drifts.
- **teardown** — when a teammate's unit is done, have it report back and
  return; close its pane. End the team when the last unit lands.

## Step 4 — verify & synthesize

Lead does a **read-to-decide** verify pass: check each teammate's output against
the *original* spec, list anything unmet, and dispatch a follow-up teammate for
just those. Then report — lead with what happened, what each teammate did, and
anything the verify pass rejected.

## Worker-role safety

Teammates execute **one scoped unit and return** — a teammate must **not** spawn
its own team or run `/fleet` / `/orchestrate`. Only you, the lead, decompose and
delegate. (See `agent-fleet.md`.)
