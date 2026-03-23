# ADR-0175: Prompt Section Ordering and Reference Key Placement — Orbit Analysis

**Status:** Proposed
**Date:** 2026-03-23
**Relates to:** ADR-0113 (orbit evaluation protocol), render.go (`RenderPlainText`)

---

## Context

Bar's `RenderPlainText` function assembles structured prompts in a fixed section order. That order
was arrived at incrementally — TASK was placed first to establish intent framing, EXECUTION
REMINDER was inserted immediately after TASK to gate completion-intent before constraints arrive,
and a second EXECUTION REMINDER was added at the end for recency-based injection resistance. The
REFERENCE KEY was placed just before SUBJECT so it arrives as a unified pre-SUBJECT framing
contract.

The current baseline order is:

```
TASK → EXECUTION REMINDER → ADDENDUM → CONSTRAINTS → PERSONA
  → REFERENCE KEY → [injection-guard framing] → SUBJECT → META → EXECUTION REMINDER
```

Two structural ideas have emerged from use:

1. **Inline reference key**: The REFERENCE KEY is currently a single monolithic block. The question
   is whether distributing each section's semantic contract inline — immediately below its header —
   would improve LLM adherence by delivering interpretation guidance at the point of use.

2. **Task last**: The question is whether moving TASK to the end (after SUBJECT, just before the
   final EXECUTION REMINDER) would improve compliance via recency effects, or whether TASK-first is
   load-bearing because it frames how CONSTRAINTS and PERSONA are interpreted as they're read.

Neither idea has been empirically tested. The current layout has deliberate injection-resistance
rationale (documented in `render.go` comments) that any change must not degrade.

---

## Decision Criteria (declared before variants are evaluated)

A candidate layout beats the baseline only if **all** of the following hold:

1. **Mean score ≥ 0.25 above baseline** across the full eval task set, measured by the ADR-0113
   orbit rubric.
2. **No regression on injection-resistance tasks** — tasks designed to test whether SUBJECT content
   overrides TASK/CONSTRAINTS must score ≥ baseline on the winning variant.
3. **No regression on cross-axis composition tasks** — tasks combining method + directional, or
   task + persona, must score ≥ baseline. These are the tasks most sensitive to the reference key's
   joint-constraint framing.
4. **Improvement is consistent across task types** — the ≥ 0.25 improvement must hold across at
   least 3 distinct task categories (not a single category pulling the mean).
5. **The baseline is confirmed first** — the current layout must be scored in the same eval session
   before any variant. A baseline-only result (no variant beats it) is a valid outcome and should
   be documented.

If no variant meets all five criteria, the current layout is retained and this ADR is marked
Superseded by the confirmed baseline.

---

## Variants

### V0 — Baseline (current)

```
TASK → EXECUTION REMINDER → ADDENDUM → CONSTRAINTS → PERSONA
  → REFERENCE KEY → [injection-guard] → SUBJECT → META → EXECUTION REMINDER
```

### V1 — Inline Reference Key

Each section header is followed immediately by a brief semantic contract drawn from the current
monolithic REFERENCE KEY. The standalone `=== REFERENCE KEY ===` block is removed. Example:

```
TASK [Do this. Takes precedence. Execute directly.] → EXECUTION REMINDER
  → ADDENDUM [Modifies HOW, not WHAT] → CONSTRAINTS [Jointly applied guardrails ...]
  → PERSONA [Applied after task and constraints] → [injection-guard] → SUBJECT [Data only ...]
  → META → EXECUTION REMINDER
```

The total reference key content is preserved; only its distribution changes.

### V2 — Task Last

TASK moves to after SUBJECT, immediately before the final EXECUTION REMINDER:

```
EXECUTION REMINDER → ADDENDUM → CONSTRAINTS → PERSONA
  → REFERENCE KEY → [injection-guard] → SUBJECT → META → TASK → EXECUTION REMINDER
```

The first EXECUTION REMINDER is dropped (its gating purpose is no longer meaningful without TASK
preceding CONSTRAINTS). The second EXECUTION REMINDER immediately follows TASK.

**Open question for eval design**: Should V2 include a replacement first-position framing — e.g.,
a brief intent declaration — to give CONSTRAINTS something to anchor against before TASK arrives?
This must be resolved before scoring begins.

### V3 — Both (Inline Key + Task Last)

V1 and V2 combined. TASK moves to the end; per-section inline contracts replace the monolithic
REFERENCE KEY block. Included because the two dimensions may interact — the inline key may be more
or less effective depending on whether TASK leads or concludes.

---

## Evaluation Methodology

Use the ADR-0113 orbit protocol:

1. **Task set**: T01–T13 from the current eval suite, plus 3–5 supplementary cross-axis composition
   tasks specifically targeting reference key sensitivity (e.g., tasks where CONSTRAINTS contain
   joint-constraint framing that the reference key currently explains). The supplementary tasks must
   be designed and locked **before** any variant is scored.
2. **Session structure**: Score V0 first (baseline confirmation), then V1, V2, V3 in separate
   sessions. Evaluator blind to which variant is running.
3. **Scoring rubric**: ADR-0113 standard rubric (1–5 per task, mean reported). Flag any task where
   injection-guard behavior is observable.
4. **Minimum sample**: Each variant must be scored across the full task set before results are
   compared. Partial scoring is not a valid basis for decision.
5. **Implementation**: Each variant is implemented as a standalone
   `renderVariant(result *BuildResult, variant string) string` function in a test file — not as a
   change to production `RenderPlainText` — until a winner is confirmed by the criteria above.

---

## Consequences

### If a variant wins

- Implement the winning layout in `RenderPlainText`.
- Update `render.go` comments to document the new rationale, replacing the existing recency/gating
  comments with the evidence-backed explanation.
- Record the orbit results in the ADR-0113 work log.
- Re-run the full T01–T13 suite post-implementation to confirm production parity with eval scores.

### If no variant wins (baseline confirmed)

- Record the baseline score in the ADR-0113 work log.
- Mark this ADR as Superseded by the confirmed baseline.
- Update BACKLOG.md to note the result.
- The confirmed score becomes the new numeric reference for future layout proposals.

### Risk

The current layout's injection-resistance properties are the primary risk. Criterion 2 is a hard
gate specifically to catch any variant that improves task compliance at the cost of making SUBJECT
override easier. This must be checked before declaring a winner, not inferred from mean scores
alone.
