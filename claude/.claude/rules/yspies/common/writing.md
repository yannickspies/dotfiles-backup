# Writing documents

Applies to any document written for a human to read: memos, specs, audits, reports,
proposals, research write-ups, HTML dashboards. Not to code comments or commit messages.

## The rule

**No extra ideas. As many words per idea as clarity needs.** These are two different
axes and only the first one is a budget.

- **How many ideas**: nothing extra. Do not pad to look thorough. Do not keep the third
  example, the section that changes no decision, or the point a sibling doc already made.
- **How many words per idea**: whatever makes it readable in one pass. A reader who has
  to re-read a sentence has been failed, and saving them four words caused it.

Length is an output of both, never an input. This omits a word budget on purpose. Word
caps in prompts are violated 37–49% of the time by frontier models (arXiv:2406.17744),
and a cap forces padding on a hard doc while permitting fluff in an easy one. The rules
below remove the places fluff lives instead.

Plain language and brevity only look like opponents. Compression buys shortness by
stacking clauses and leaning on jargon, which moves the work onto the reader. Cutting a
whole point buys the same shortness for free.

## Ten rules

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

10. **Plain language.** Short sentences, everyday words, one idea per paragraph, jargon
    glossed once. See the section below — this is the rule most often broken, because
    breaking it is what density feels like from the inside.

## Plain language

A reader outside this codebase must be able to follow the argument without stopping.

- **One idea per sentence.** Two clauses joined by a comma, a semicolon or a dash are
  usually two sentences. Aim under 25 words; past 35 is a defect, not a style.
- **One idea per paragraph.** Three or four sentences, then a break.
- **Everyday words.** `use` not `utilise`, `before` not `prior to`, `help` not
  `facilitate`, `about` not `with regard to`, `find out` not `ascertain`, `so` not
  `therefore`.
- **Gloss jargon once, plain meaning first.** "the file that tells the browser what to
  load (the manifest)". After that, use the short term freely.
- **Expand an acronym on first use and say what it does**, not just what the letters
  stand for. "Meta's Conversions API (CAPI) — how your server tells Meta about a sale."
  Exempt: ones any reader knows — API, URL, HTML, CSS, SQL, HTTP, JSON, PDF, ID, UI.
- **Active voice.** "The webhook writes the row", not "the row is written by the webhook".
- **Mechanism before consequence.** Say how the thing works, then why it matters. A
  reader who does not yet understand the mechanism cannot evaluate the consequence.
- **A table cell holds a fact, not a paragraph.** If the reasoning does not fit, it
  belongs in prose.

This applies to Dutch as much as English. Dutch technical writing stacks subordinate
clauses even more readily; the same limits hold.

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

**Inflated words** — say the short one: `utilise/utilize → use` · `facilitate → help` ·
`commence → start` · `prior to → before` · `subsequent to → after` · `in order to → to` ·
`due to the fact that → because` · `at this point in time → now` · `in the event that → if` ·
`with regard to / with respect to → about` · `a number of → some` · `the majority of → most` ·
`is able to / has the ability to → can` · `in excess of → more than` · `ascertain → find out` ·
`endeavour → try` · `aforementioned → this` · `notwithstanding → despite` ·
`pursuant to → under` · `requisite → needed` · `necessitate → need` · `utilisation → use`

## Cutting

Cut whole points, not adjectives, and not clarity. Trimming modifiers is the documented
failure mode: the doc reads slightly tighter and stays the same length. Remove sections,
remove claims, remove the third example.

Never buy shortness by merging two sentences, dropping the gloss on a technical term, or
moving reasoning into a table cell. That is not cutting — it is handing the work to the
reader. If a draft is too long, the fix is one fewer point, not one denser paragraph.

When you cut something the reader might want back, say so in one line rather than
keeping it.

## Enforcement

Run the repo's doc linter before writing any generated document, and fix what it flags.
It reads both Markdown and HTML.

```
node scripts/lint-doc.mjs <file...>
```

The linter detects and never edits — deliberately. An LLM asked to "make this shorter"
produces a second long document; an LLM given a located list of violations fixes them.
The same reasoning rules out a rewrite pass by a smaller model: asked to simplify a
paragraph of this standard, a 3B local model inverted "~20%" into "80%" and deleted
every file path, while its prompt said to keep both (measured 2026-08-16).

It flags three families: **structure** (topic headers, recap sections, restatement),
**phrasing** (throat-clearing, hedge stacks, calques, weak openers, inflated words), and
**plainness** (`long-sentence` over 35 words, `clause-pileup`, `bare-acronym`). The
plainness checks skip table rows and headers on purpose.

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
