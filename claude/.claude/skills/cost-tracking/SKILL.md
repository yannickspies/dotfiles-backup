---
name: cost-tracking
description: Track and report Claude Code token usage and spending in EUR by shelling out to ccusage. Use when the user asks about costs, spending, usage, tokens, budgets, or cost breakdowns by project, session, model, or date.
origin: local
---

# Cost Tracking

Use this skill to analyze Claude Code cost and usage by shelling out to
[`ccusage`](https://github.com/ryoppippi/ccusage), which parses the local
session transcripts in `~/.claude/projects/**/*.jsonl` and applies current
per-model pricing. All amounts are presented to the user in **EUR**, using the
`eur_per_usd` rate from `~/.claude-cost-tracker/config.json`.

Live, per-message cost is shown in the Claude Code status bar via
`~/.claude/hooks/cost_statusline.py`. This skill answers retrospective
questions ("what did I spend today / this week / on project X?").

## When to Use

- The user asks "how much have I spent?", "what did this session cost?", or
  "what is my token usage?"
- The user mentions budgets, spending limits, overruns, or cost controls.
- The user wants a cost breakdown by project, session, model, or date.
- The user wants to compare today against yesterday or inspect a recent trend.

## Prerequisites

```bash
command -v npx >/dev/null && echo "npx available" || echo "npx missing"
test -f ~/.claude-cost-tracker/config.json && echo "config found" || echo "config missing"
```

If `npx` is missing, tell the user cost tracking requires Node.js (`sudo apt
install nodejs npm`). If the config file is missing, default
`eur_per_usd=0.92` is used silently — but recommend creating one for
explicit control.

## EUR Conversion

Before reporting any figures, read the rate:

```bash
jq -r '.eur_per_usd' ~/.claude-cost-tracker/config.json 2>/dev/null || echo "0.92"
```

Then multiply every USD figure from ccusage by that rate and present as `€X.XX`.

## Examples

> **Tip**: For snappier results, install ccusage globally once
> (`npm install -g ccusage`) and replace `npx -y ccusage@latest` with `ccusage`
> in the commands below.

### Today's Spend

```bash
npx -y ccusage@latest daily --json \
  --since "$(date +%Y%m%d)" --until "$(date +%Y%m%d)"
```

Parse `totals.totalCost` (USD), multiply by the EUR rate, present as
`Today: €X.XX`.

### Last Seven Days (daily breakdown)

```bash
npx -y ccusage@latest daily --json \
  --since "$(date -d '6 days ago' +%Y%m%d)"
```

Parse `daily[]`, convert each `totalCost` to EUR, render a small table:

```
Date         Cost     Input/Output tokens
2026-05-21   €1.13    234k / 18k
2026-05-20   €0.07    12k  /  1k
...
Total        €2.41
```

### Per-Session Breakdown (recent sessions)

```bash
npx -y ccusage@latest session --json | head -c 50000
```

Parse `sessions[]` (keys typically include `sessionId`, `totalCost`,
`inputTokens`, `outputTokens`, `cacheCreationTokens`, `cacheReadTokens`,
`lastActivity`). Sort by `totalCost` desc, show top 5 in EUR.

### Current 5-Hour Block

```bash
npx -y ccusage@latest blocks --json --active
```

Useful for "am I about to hit a rate-limit / block-cost ceiling?" answers.

### Monthly Roll-up

```bash
npx -y ccusage@latest monthly --json
```

## Reporting Guidance

When presenting cost data, include:

1. Today's spend in EUR, with a one-line "yesterday was €Y" comparison if
   data exists.
2. Total spend across the requested window.
3. Top sessions / projects ranked by cost (limit 5).
4. The FX rate used, so the user can audit (e.g. "at 0.92 EUR/USD").

For small amounts, format with 4 decimals (`€0.0123`). For ≥ €1, two decimals
(`€1.23`).

## Anti-Patterns

- Do not hard-code model pricing — `ccusage` is the source of truth.
- Do not estimate costs from raw token counts when ccusage can compute them.
- Do not skip the EUR conversion. The user explicitly prefers EUR over USD.
- Do not run unbounded `ccusage session --json` exports on large histories
  without `head -c` truncation; ccusage's output can be tens of MB after
  months of use.
- Do not present the answer without the `€` symbol.

## Related

- `~/.claude/hooks/cost_statusline.py` — live per-message cost in the status bar.
- `cost-aware-llm-pipeline` — model-routing and budget-design patterns.
- `token-budget-advisor` — context and token-budget planning.
- `strategic-compact` — context compaction to reduce repeated token spend.
