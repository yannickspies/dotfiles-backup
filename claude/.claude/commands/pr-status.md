---
argument-hint: "[--gate qa] [--mine] [--comments] [--format markdown]"
allowed-tools: Bash, Read
description: Teams-pasteable board of open Azure DevOps PRs with dev/QA approval status
---

# PR status board

Produce a shareable overview of the open pull requests on
`InShared/frontend/websites`, showing which of the two required approvals
(1 dev + 1 QA) each PR still needs.

## Run the tool

Always write the board to a file as well as stdout, so the user has something
easy to copy from:

```bash
cd ~/projects/frontend/automation/azure-devops \
  && python3 pr_status.py $ARGUMENTS -o output/pr-board.txt
```

(If `$ARGUMENTS` already contains `-o` or `--output`, use that path instead of
adding a second one.)

It authenticates through the existing `az login` session. If it reports that
`az` is missing or unauthenticated, tell the user to run `az login` — do not
attempt to create or store a PAT.

Useful argument combinations, if the user did not pass any:

- (no args) — the full board, everything grouped by state
- `--needs-review --no-drafts` — only what is actually blocking the team
- `--gate qa` — everything waiting on QA sign-off
- `--mine` — the user's own PRs
- `--comments` — adds unresolved comment counts (slower, ~20s)
- `--format markdown` — table form, for docs rather than Teams

## Present the result

1. Print the tool's output **verbatim in a fenced code block**, and tell the
   user the file path it was also written to. Do not reformat, re-sort,
   re-wrap or re-emoji it — the output is deliberately plain text with bare
   URLs, because Teams mangles pasted markdown links and tables but does
   auto-linkify bare URLs.
2. Below the block, add a short **"what I'd do next"** read of 2-4 bullets:
   - PRs that are one approval away from merging (quickest wins)
   - anything stale (`🕓`, open 7+ days) or with changes requested
   - if the user appears as an assigned-but-not-voted reviewer, call that out
3. Keep the commentary brief. The board is the deliverable; the analysis is a
   footnote.

Do not vote, comment, complete, or otherwise modify any PR. This command is
read-only.
