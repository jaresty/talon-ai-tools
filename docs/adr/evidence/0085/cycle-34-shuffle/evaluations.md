# ADR-0085 Cycle 34 — form×channel, weighted toward today's changes

**Date:** 2026-09-30 | single-evaluator | fresh build

## Stratification

Seeds 500-539 surveyed (40). Weighted toward form+channel co-occurrence again, per the cycle-33
lesson that stratifying toward what a recent change affected finds defects faster than stratifying
for comparable means — five commits today touched that interaction. Chose 6 with distinct channels;
**all 6 carry a form**, and none of the 6 pairs had any existing entry, so all resolved purely via
the narrowed axis rule.

| Seed | Draw | Score | Note |
|---|---|---|---|
| 502 | witness + deep + product + walkthrough + **ledger** | 2 | ledger emits only Facts/Decisions/Constraints/Open-Questions and explicitly excludes reasoning traces — which is exactly what walkthrough and witness produce. The channel *starves* the form rather than lacking a construct for it. |
| 503 | full + jobs + table + **aloud** | 2 | Second independent seed (cycle 33 seed 412 was the first). Speech has no positional dimension; the adjacent-block branch is meaningless for TTS. **Acted on.** |
| 505 | grow + time + mod + checklist + **html** | 4 | `<ul>`/`<ol>` with checkbox inputs carry a checklist natively. Clean. |
| 513 | full + actors + quiz + **svg** | 2 → **3 (revised)** | Initially scored as a turn-taking collision. quiz already handles that ("An answer is permitted in the same response turn ... only when the current response is producing a static document"). The real issue is SVG having no text-sequence construct — an ordinary form/channel case the narrowed rule covers. |
| 515 | live + full + survive + reference + **shellscript** + fly-ong | 4 | reference says "The medium of each unit is unconstrained"; functions with comment labels carry it. |
| 519 | full + lever + models + stage + **presenterm** | 3 | stage maps well to slides (one state per slide). Mild volume tension: `full` + `models` (enumerate every absent model) against a 12-slide cap, uncautioned. |

**Mean: 3.00/5** (after the seed-513 revision), 6/6 channel-bearing, 6/6 form-bearing.
Not progress evidence at this sample size.

## Findings

**Acted on — `aloud` had no form entry.** Two independent seeds. `aloud` already cautions `max` and
`full` on completeness with the right reasoning ("spoken delivery condenses to speech density"), but
had no form axis entry at all, despite its definition instructing the response to "strip code blocks,
raw URLs, and long enumerations". Added cautionaries for the two forms whose structure is
*positional* — `table` (meaning in cell position within row and column) and `twin` (equal weight by
side-by-side placement) — since speech has no positional dimension and, unlike a written channel,
offers no adjacent block to put the grid in. Deliberately NOT extended to sequential enumerative
forms (`bullets`, `checklist`, `scorecard`, `reference`): speech carries those fine.

**Not acted on — two classes at one seed each:**
- `ledger` (and `gherkin`) as *content-excluding* channels: they discard categories of content by
  definition rather than lacking a construct. The narrowed axis rule assumes a channel either has a
  construct or lacks one; it has no branch for a channel that actively drops the form's material.
  `ledger` has no form or completeness entry at all. One seed.
- `presenterm` volume tension with enumerating methods (`models`) at `full`. One seed; presenterm's
  completeness cautionary covers `max`/`deep`/`zoom` but not a method that enumerates.
