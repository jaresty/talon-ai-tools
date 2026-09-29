# Cycle 27 addendum — render-class cautionary sweep

**Date:** 2026-09-29. Triggered by the question: *can composition rules let us avoid cautionary?*

## Method

Inventoried all **121** cautionary entries and classified them by the *reason* each states:

| Class | Count | Composable? |
|---|---|---|
| Capacity conflict (directional 35, completeness 9, tone 3) | ~47 | **No** — the constraint is how much fits, not where it goes |
| Render / "no prose slot" | 13 (form×channel) | **Yes** — adjacent block resolves it |
| Audience accessibility | 17 | **No, and should not** — not a structural conflict at all |
| Incoherent / narrative | 9 | Mixed |
| Other | ~35 | Mixed |

The answer to the question is **no, cautionary cannot be abolished** — capacity starvation and
audience fit are genuinely non-composable. But the **render class was entirely mis-layered**: a
reason of the form "has no prose slot" describes *where content goes*, which an adjacent block
answers.

## Disposition of the 13 render-class entries

**Converted to compositions (10):** faq+{code, codetour, shellscript}, log+codetour,
spike+codetour, questions+{gherkin, shellscript}, case+{gherkin, codetour, shellscript}.
Each keeps the artifact pure and places the form's content in an adjacent block, with a gate clause
rejecting both "folded into the artifact" and "no adjacent block".

**Retained as cautionary (3), with reasons:**
- `template`×{codetour, gherkin, shellscript} — template is a **whole-response form** (every
  position is an empty labeled slot; no prose outside slot positions). An adjacent block would *be*
  the response. This is the cycle-26 distinction: supplementary content composes; a whole-response
  form cannot.
- `socratic`×{codetour, shellscript} — kept, but the reason is **subject-absent**, not rendering
  (see c27-R2). socratic needs a claim from the user's input; no artifact supplies one.
- `case`×html — html is a *format* channel that can host argumentative prose, so this entry is
  questionable for a different reason. Left alone: no seed evidence, and re-opening it would be
  scope creep.

## Two contradictions found (the invariant that should have caught them)

`ghost+svg` and `deep+commit` each carried **both** a shipped composition and a cautionary for the
same pair — giving opposite instructions ("place the trace adjacent" vs "use plain or no channel").
Both cautionaries removed; `ghost`'s cross-axis entry became empty and was deleted entirely.

This motivated a new ADR invariant: **no token pair may have both a composition and a cautionary
entry.** Verified clean after the sweep.

## Also corrected

`channel/gherkin → form/recipe` still described "recipe prose steps" — the same misdiagnosis fixed
for recipe's own entries earlier this session, missed in the reverse direction. Reworded to the
notation-and-key reason.

## Result

| | Before | After |
|---|---|---|
| Compositions | 33 | **43** |
| Cautionary entries | 121 | **107** |
| Double-layered pairs | 2 | **0** |
| "prose slot" reasons | 14 | **0** |

## Test fallout (worth recording)

Two Go harness tests failed: `TestHarnessCautionFormToChannel` and
`TestHarnessCautionChannelToForm`. Neither tested the sweep — each used a now-converted pair
(`faq`+`shellscript`, `case`+`gherkin`) as a **fixture** to prove the caution UI renders.
Repointed to pairs that remain legitimately cautionary (`template`+`shellscript`,
`log`+`gherkin`). The caution mechanism itself is unchanged and still covered.

Lesson: cautionary pairs are load-bearing as *test fixtures*, so converting one to a composition can
break a test that has nothing to do with the pairing's correctness. Check `grep` for the pair in
test files before converting.
