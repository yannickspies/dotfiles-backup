# Writing documents

Applies to any document written for a human to read: memos, specs, audits, reports,
proposals, research write-ups, HTML dashboards. Not to code comments or commit messages.

## The rule

**Nothing extra.** Length is an output, never an input. Something genuinely complex and
detailed may need more; something simple gets a paragraph. Do not pad to look thorough,
and do not cut a real finding to hit a number.

This omits a word budget on purpose. Word caps in prompts are violated 37–49% of the time
by frontier models (arXiv:2406.17744), and a cap forces padding on a hard doc while
permitting fluff in an easy one. The rules below remove the places fluff lives instead.

## Nine rules

1. **Answer first.** The first two sentences state a full declarative claim that commits
   to something. Not a topic, not a question, not scope-setting. If the reader stops
   there, they should have the conclusion.

2. **Headers state findings, not topics.** `These were never competitors` beats
   `Competitive analysis`. A reader scanning only the headers should get the argument.
   No terminal period needed — that reads wrong in this voice.

3. **No Conclusion or Summary section.** The top carries it. A doc with an opening
   summary, per-section recaps and a conclusion is roughly a third redundant by
   construction.

4. **Tables over prose** for anything enumerable — options, findings, comparisons, costs,
   shot lists. Prose is for the argument only.

5. **Decide.** Never present options without naming the winner. Both-sidesing is the
   single biggest length multiplier: a doc that commits is short, a doc that surveys is
   long. State a confidence level if it is genuinely uncertain, but state the call.

6. **Label claims.** Fact / Inference / Assumption / Estimate — or cut the claim. Every
   number and every legal or market claim carries its source inline. If no reliable
   figure exists, say so rather than borrowing an adjacent one. See `epistemics.md`.

7. **Do not re-report.** If a sibling doc covers something, link it and say what it
   covers. Never restate it. Say so explicitly, e.g. "nothing from that doc is repeated
   here."

8. **No throat-clearing.** See the blocklist below.

9. **So what?** Every section must change a decision. If you cannot say which decision,
   delete the section.

## Blocklist

**Throat-clearing** — delete outright, never replace:
`It is worth noting` · `It's important to remember` · `Importantly,` · `Notably,` ·
`As we all know` · `At the end of the day` · `The fact of the matter is` ·
`In today's <anything>` · `Let's dive in` · `Here's a summary of` · `Before we begin`

**Weak openers** — no sentence starts with `It is`, `There is`, `There are`.
(US Army AR 25-50 §1-37b(8); one of the few genuinely mechanical writing rules.)

**Hedge stacking** — one qualifier, never two: `may potentially` · `could possibly` ·
`it seems likely that` · `roughly around`. A hedge on an invented number is still an
invented number.

**Announced transitions** — `What this means in practice:` · `Let's break this down` ·
`Now, let's turn to` · `With that said`

**Topic-label headers** — `Overview` · `Introduction` · `Background` · `Key Findings` ·
`Analysis` · `Conclusion` · `Summary` · `Final Thoughts` · `Next Steps` as a bare label.

**Consulting calques** — `leverage` (as a verb) · `value-add` · `deep dive` ·
`paradigm shift` · `best practice` · `mindset` · `journey` · `transformation`.
These translate one-to-one into Dutch (`bottleneck → knelpunt`), so the ban holds in
both languages.

## Cutting

Cut whole points, not adjectives. Trimming modifiers is the documented failure mode: the
doc reads slightly tighter and stays the same length. Remove sections, remove claims,
remove the third example.

When you cut something the reader might want back, say so in one line rather than
keeping it.

## Enforcement

Run the repo's doc linter before writing any generated document, and fix what it flags.
The linter detects and never edits — deliberately. An LLM asked to "make this shorter"
produces a second long document; an LLM given a located list of violations fixes them.

Reference documents (rules files, directory indexes, API tables) are looked up rather than
read, so section labels are correct there and the finding-header rule does not apply. Lint
them with `--reference`. Decision documents get no such exemption.

A separate audit pass may critique a draft against these rules. It must not rewrite.

## Calibration

The anchor is a doc that is short and still decides something. Its shape:

```
title
dated status / scope / method — 2-4 lines
what this doc is NOT, and what sibling doc covers that
tables
```
