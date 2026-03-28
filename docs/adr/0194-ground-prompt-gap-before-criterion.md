# ADR-0194: Gap-Before-Criterion Ordering at Criteria Rung

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

A model transcript wrote the criterion sentence before the 🔴 Gap declaration at the criteria rung:

```
criteria
The system displays an "add attribute" button that when clicked opens a form...

🔴 Gap: The add attribute button and form do not exist in the current UI.
```

The generic rule "Before writing the criteria... label, emit 🔴 Gap:" exists but applies at the rung-label level (emit Gap before the label), not at the intra-rung ordering level (Gap before criterion within the rung). The model interpreted the rule as applying to the rung entry, not to artifact ordering within the rung.

The correct ordering is: criteria rung label → 🔴 Gap → criterion sentence.

---

## Decision

Add a criteria-rung-specific ordering rule immediately before the manifest-anchor rule:

> "🔴 Gap: must be the first content after the criteria rung label — the criterion sentence may not precede the Gap declaration; writing the criterion before 🔴 Gap: is a protocol violation"

This is a positive ordering constraint within the rung, distinct from the generic gap-emission rule.

---

## Implementation

Changes to `lib/groundPrompt.py`:
- Added three-sentence ordering rule before "before writing the criteria artifact, locate ✅ Manifest declared"

Updated `_tests/ground/test_ground_l24.py`:
- Proximity cap raised 1750 → 1900

New test file: `_tests/ground/test_ground_adr0194_gap_before_criterion.py` — 2 tests

---

## Consequences

- **Positive**: criteria rung has an explicit intra-rung ordering rule; criterion-before-Gap is named a protocol violation
- **Note**: threads 2–4 from the observed transcript (exec_observed summary line, V-complete gate, R2 audit section) were either non-violations (interrupted display) or already addressed by ADR-0191/ADR-0192
