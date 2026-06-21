---
allowed-tools: mcp__trello__get_active_board_info, mcp__trello__get_lists, mcp__trello__get_cards_by_list_id, mcp__trello__get_recent_activity, mcp__trello__get_card_comments, mcp__trello__get_my_cards, mcp__trello__set_active_board
description: Status update on the Portfolio Trello board (apps/portfolio) — recently completed, doing, top todos, and stalled items
---

## Task

Generate a **scannable status update** for the **Portfolio** Trello board (`apps/portfolio`). Use the Trello MCP tools, not raw HTTP.

This board is pinned by id — do **not** prompt for a board name.

## Pinned board

- Board: **Portfolio**
- Board id: `6a29bf025ec72a7ee424706b` (shortLink `69j1i9xL`)

## Steps

1. `mcp__trello__set_active_board` with id `6a29bf025ec72a7ee424706b` to pin this board first.
2. Then follow the full procedure in [`/board-status`](./board-status.md) — the list-matching, recent-activity audit, blocker heuristic, output format, and rules are defined there and are the single source of truth. Do not duplicate or diverge from them here.
