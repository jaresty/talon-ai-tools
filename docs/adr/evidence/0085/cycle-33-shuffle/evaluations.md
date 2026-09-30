# ADR-0085 Cycle 33 — form×channel stratified shuffle

**Date:** 2026-09-30 | single-evaluator | fresh build

## Stratification

Surveyed seeds 400-437 (38 seeds); 24 channel-bearing. Cycle 33 weighted the draw toward
**form+channel co-occurrence**, since the delivered form/channel axis rule shipped in d2383ed7
earlier today and those draws are what test it. Selected 6 with distinct channels; 5 of 6 carry a form.

| Seed | Draw | Score | Note |
|---|---|---|---|
| 403 | full + walkthrough + video + dip-bog | 4 | walkthrough's stages become the video's temporal progression — the new rule resolves it cleanly. |
| 408 | skim + view + automate + facilitate + sketch | 4 | facilitate's own clause fires (output-exclusive channel → static guide). Confirms keeping the six token-specific clauses was right: it names WHICH of two modes, which the general rule cannot derive. |
| 410 | ration + storage + ontology + remote | 3 | ontology enumerates diagram/code/no-channel; `remote` is a delivery-mechanism channel matching no branch, so it falls off the end of the list to the prose default. Correct outcome, reached by fallthrough rather than by rule. |
| 412 | narrow + collapse + table + aloud + dip-bog | 2 | `table` is columnar; `aloud` is TTS and its own definition says strip long enumerations. Speech has no columnar construct. Genuine gap. |
| 419 | audit + full + bias + image | 2 | constructor-channel problem already covered generically by image's cautionaries. |
| 433 | witness + gist + relations + operations + commit + code + fip-ong | 3 | commit's type/scope header maps to a code comment; commit×fip-ong capacity cautionary also present (correctly). |

**Mean: 3.00/5 across 6 seeds, 6/6 channel-bearing, 5/6 form-bearing.**
Not evidence of progress at this sample size — the coverage findings below are the output.

## The finding: today's axis rule contradicted 10 shipped compositions

Scoring seed 433 (`commit`+`code`) sent me to check the shipped compositions for that shape, and
surfaced a direct conflict I had introduced hours earlier in d2383ed7:

- The axis clause said: a prose-excluding channel "carries the form in its own constructs rather
  than adding prose sections."
- `faq+code` and 7 others say: "Folding that content into the artifact — as comments, step text,
  or embedded strings — in place of the adjacent block does not satisfy faq."

**The composition forbids exactly what the axis rule mandated.** 10 compositions use the
adjacent-block resolution; 8 carry that explicit prohibition.

My cycle-32 falsification checked whether the new rule was DELIVERED. It never checked whether the
rule CONFLICTED with shipped compositions. That is the process gap this cycle found, and it is more
useful than any of the six scores.

Resolution (user decision): narrow the axis clause rather than retire the compositions. The clause
now says the form is expressed through a channel construct **where the channel has one**, goes in an
adjacent block **where it has none**, and that a composition for the specific pair governs over the
default. All 10 compositions intact; the 44 previously-unguided forms still covered.
