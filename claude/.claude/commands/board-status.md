---
allowed-tools: mcp__trello__get_active_board_info, mcp__trello__get_lists, mcp__trello__get_cards_by_list_id, mcp__trello__get_recent_activity, mcp__trello__get_card_comments, mcp__trello__get_my_cards, mcp__trello__list_boards, mcp__trello__set_active_board
description: Status update on the active Trello board — recently completed, doing, top todos, and stalled items
---

## Task

Generate a **scannable status update** for the active Trello board. Use the Trello MCP tools, not raw HTTP.

If the user passed a board name as an argument (e.g. `/board-status LuisterLink`), call `mcp__trello__list_boards` and `mcp__trello__set_active_board` first. Otherwise use whatever board is active.

## Steps

1. `mcp__trello__get_active_board_info` — confirm the board name and label vocabulary.
2. `mcp__trello__get_lists` — discover list structure. Match list names case-insensitively against intent:
   - **Done** ≈ `done`, `shipped`, `released`, `complete`
   - **Doing** ≈ `doing`, `in progress`, `wip`
   - **ToDo** ≈ `todo`, `to do`, `next`, `up next`
   - **Backlog** ≈ `backlog`, `icebox`
3. `mcp__trello__get_recent_activity` with `limit: 50` — this is your audit log. Useful event types:
   - `createCard` — new work added
   - `updateCard` with `data.listAfter` — card moved between lists (filter to `listAfter.name == Done` for completions)
   - `commentCard` — discussion happening
   - `updateCheckItemStateOnCard` — checklist progress
4. `mcp__trello__get_cards_by_list_id` for **Doing** and **ToDo** (and **Done** if needed for fallback).
5. Apply the blocker heuristic defined below.

## Output format

Keep the **whole response under ~35 lines**. Bullet points, no filler.

```
## {Board name} — status as of {today's date}

### Recently completed (last 7 days)
- {Card name} — {moved to Done | created in Done} {N}d ago
- ... (max 5; if none, say "No completions in the last week")

### In progress ({count})
- {Card name} — {idle Nd | active today | last comment Nd ago}
- ... (all cards in Doing, ordered by staleness desc)

### Stalled
- {Card name} — idle {N}d
- ... (if none, say "Nothing flagged")

### Up next (top of ToDo)
- {Card name}
- ... (top 5 by position)

### Pulse
- {N} cards moved, {N} comments, {N} created in last 48h.
```

## Blocker heuristic

A card counts as **stalled** if it sits in **Doing** with no activity for **5+ days** — no comments, no checklist updates, no moves. Cross-reference `get_recent_activity` by card id to determine last-touched time; if no activity events exist for the card in the fetched window, fall back to the card's `dateLastActivity` field.

Report the line as `{card name} — idle {N}d`.

## Rules

- Use **relative dates** ("3d ago", "today") — easier to scan than ISO timestamps.
- Don't paginate or dump JSON. Synthesize.
- If a list has zero cards, omit the section entirely (don't print empty headers).
- For "Recently completed", prefer audit-log evidence (`updateCard` → Done) over current Done list contents — Done can grow indefinitely.
- If the board has no Doing/ToDo lists (e.g. only Done + Backlog), adapt: explain the structure and pick the most actionable equivalents.
