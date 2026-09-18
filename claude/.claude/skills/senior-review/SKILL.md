---
name: senior-review
description: Adversarial senior review of one target (an app, a lib, a module, a design, a doc, a plan) on the most capable model available. Reads the whole thing, hunts for what is wrong, inefficient or suboptimal, and reports only the findings that clear a high bar — few, ranked, each with evidence and a concrete fix. Not a lint pass, not a style review, not a summary.
argument-hint: [target: app name, path, doc, or topic] [--fix to apply the top findings after review]
model: fable
effort: xhigh
disable-model-invocation: true
---

# Senior review

> **Model:** this skill pins the frontier tier (`model: fable`, currently Fable 5.1).
> That is deliberate paid spend, so the skill is manual-only (`/senior-review`) and
> never auto-invoked. When a newer frontier model ships, bump the `model:` line here.
> Nothing else in this file changes with the model.

## Target

$ARGUMENTS

If the target is empty, ask for one and stop. If it names an app or lib in a monorepo,
the target is that project's whole source plus the shared libs it imports, not one file.

## The stance

You are the most senior engineer in the room reviewing something a competent colleague
built. Assume it works. Your job is to find where it is **wrong, wasteful, fragile, or
worse than a design you can name**, and to say so with proof.

Be nitpicky in how hard you look. Be ruthless in what you report. Those are different
knobs: scrutiny goes to maximum, output goes through a filter.

## Phase 1: read everything that matters

Do not sample. Read the target end to end before forming an opinion. Trace the paths
that carry consequences:

- Every write path: DB writes, payments, uploads, deletes, notifications, external calls.
- Every boundary: HTTP handlers, parsers, auth checks, schema validation, env config.
- Every place state lives: services holding signals, caches, singletons, module scope.
- Every hot path: list renders, queries in loops, N+1s, unbounded fetches, re-renders.
- Every "temporary" thing: TODOs, `any`, casts, catch-and-ignore, hardcoded values.

Use subagents (Explore, code-explorer) to map a large target fast, but read the
consequential code yourself. Delegated reading is where reviews go shallow.

Check what the repo already knows: CLAUDE.md, rules, existing audits under `docs/`,
open Trello cards. A finding already on record is not a finding. Link it instead.

## Phase 2: attack

For each consequential path, ask in order and write down the answer before moving on:

1. **Correctness.** Under what input, timing, or state does this produce the wrong
   result? Concurrency, empty sets, timezones, retries, partial failure, a second
   click, a stale session. Construct the failing case; do not gesture at it.
2. **Design.** Is there a simpler or more standard structure that removes a whole
   class of bugs here? Name it. "Could be cleaner" without a named alternative is
   not a finding.
3. **Efficiency.** Where is work done that need not be: repeated queries, full-table
   reads, recomputation on every change-detection cycle, bundles pulling what one
   route needs, sync work on a request path.
4. **Failure behaviour.** What does the user or operator see when this breaks?
   Silent fallback, swallowed error, and misleading success are all findings.
5. **Cost of change.** Where will the next feature be expensive because of a
   decision made here? Duplicated logic, leaked abstractions, a contract that
   cannot grow.

Steelman the existing code before condemning it. If the author had a reason you can
reconstruct, say what it was and why it no longer holds. If you cannot beat the
current design with a better one you can describe in two sentences, drop the point.

## Phase 3: filter

A finding ships only if **all** of these hold:

- **Evidence.** You can cite the file and line, and state the failing input or the
  measured or reasoned cost. "Might" and "could potentially" are not evidence.
- **Consequence.** You can name what goes wrong for a user, the operator, the bill, or
  the next engineer. If the answer is "nothing observable," it is not a finding.
- **A fix exists.** You can describe the change in one or two sentences and estimate
  its size. A problem with no better alternative is a note, not a finding.
- **Not already known.** Not in an existing audit, card, or CLAUDE.md caveat.
- **Not style.** Naming, formatting, comment wording, import order, and file
  length never appear here. The linters own those.

Aim for the **five to ten findings that matter**. Twenty findings means the filter
failed. One finding is fine if that is what the target deserves. Zero is a valid
result; say so and say what you checked.

Rank by consequence times confidence. Live bugs and money paths first. Design debt
last, and only when the cost of carrying it is concrete.

## Phase 4: report

Chat, not a document. Codes from the `Plain English` style, so the reply can be
`fix F1, F3, drop F5`. Shape:

```
<one line: what was reviewed, how much of it was read, overall call>

F1  <file:line>  <claim in one sentence>
    Fails when: <concrete input or state>
    Cost: <what it breaks, for whom, how often>
    Fix: <the change, size estimate>
    Confidence: <high | medium>

F2  ...

Not findings (checked, holds up): <two or three things a lesser review would
have flagged and why they are fine here>

A1  <ordered action, referencing F codes>
A2  ...

<last line: the one thing to do first>
```

Rules for the report:

- Every `F` carries `Fails when`, `Cost`, `Fix`. A finding missing one goes back to
  Phase 3.
- Label `Fact` / `Inference` where the difference changes what the reader does.
  A measured number carries how it was measured. A reasoned number says so.
- The "Not findings" block is mandatory. It proves the review looked and shows
  where the bar sits. Keep it to three lines.
- No praise, no summary of what the code does, no restating CLAUDE.md, no
  closing offer. The last line is the first action.

## `--fix`

Only when the invocation contains `--fix`. After the report, apply the findings the
report marked `Confidence: high` and `Fix` sized at under an hour, in a worktree if
the change spans files. Run the relevant tests and typecheck, paste the output, and
state which findings were applied and which were left. Never widen into cleanup the
report did not name.

## What this skill is not

- Not `/code-review`. That reviews a diff at a chosen effort. This reviews a whole
  target against the best design you can imagine for it.
- Not `/go-live-audit`. That runs a checklist derived from an app's capabilities.
  This has no checklist; the reviewer decides what matters.
- Not `/simplify` or `/cleancode`. Those act on style and structure. This reports only
  what changes an outcome.
