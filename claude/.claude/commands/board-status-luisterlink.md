---
allowed-tools: mcp__trello__get_active_board_info, mcp__trello__get_lists, mcp__trello__get_cards_by_list_id, mcp__trello__get_recent_activity, mcp__trello__get_card_comments, mcp__trello__get_my_cards, mcp__trello__set_active_board
description: Status update on the Luisterlink Trello board (apps/luisterlink) — recently completed, doing, top todos, and stalled items
---

## Task

Generate a **scannable status update** for the **Luisterlink** Trello board (`apps/luisterlink`). Use the Trello MCP tools, not raw HTTP.

This board is pinned by id — do **not** prompt for a board name.

## Pinned board

- Board: **LuisterLink**
- Board id: `69f3a26162a1aa30c842880c` (shortLink `523slwVN`)

## Steps

1. `mcp__trello__set_active_board` with id `69f3a26162a1aa30c842880c` to pin this board first.
2. Then follow the full procedure in [`/board-status`](./board-status.md) — the list-matching, recent-activity audit, blocker heuristic, output format, and rules are defined there and are the single source of truth. Do not duplicate or diverge from them here.
