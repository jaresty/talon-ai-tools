# ADR-0191: Forward-Obligation Gaps — Criteria→FN Gate and R2 Audit Ordering

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

A model transcript demonstrated two protocol violations not blocked by existing rules:

### Gap 1 — Criteria rung stop (false pause belief)

After writing a criterion, a model stopped and stated "that's where the protocol requires me to pause," then continued only after the user asked why it stopped. The rule "after the first criterion is written, the only valid next token is the formal notation rung label" already existed but was embedded as a clause inside the "exactly one criterion" sentence — semantically linked to preventing a second criterion rather than governing forward motion. The general continuous-descent rule ("waiting for user confirmation between rungs is a protocol violation") was present but is a negative constraint that models override with confirmation-seeking behavior. A standalone positive forward obligation was absent.

### Gap 2 — R2 audit section implicit completion

The formal notation R2 audit was described as "separate and named" but no ordering rule required the audit section to appear before the completion sentinel. A model emitted `✅ Formal notation R2 audit complete — 1/1 criteria encoded` immediately after the notation body with no separate audit section, treating the sentinel itself as the audit. The constraint that the sentinel *closes* the audit section (rather than *constituting* it) was missing.

---

## Decision

### Fix 1 — Standalone criteria→FN forward gate

Add a standalone sentence immediately before the "exactly one criterion" block:

> "after the criterion is written, the only valid next token is the formal notation rung label — no confirmation, no pause, no additional content between them is valid"

Remove the embedded duplicate clause from the "exactly one criterion" sentence. The standalone position and explicit prohibition of confirmation/pause makes the forward obligation unambiguous.

### Fix 2 — R2 audit ordering rule

Extend the existing "audit section is separate and named" sentence:

> "the audit section is separate and named and must appear before the completion sentinel — the sentinel closes the audit section; it does not constitute it"

This establishes that the sentinel is a closing marker for an already-written section, not a self-sufficient claim of completion.

---

## Implementation

Changes to `lib/groundPrompt.py`:
1. Added standalone forward-gate sentence before "exactly one criterion" block
2. Removed the embedded forward-gate clause from the "exactly one criterion" sentence
3. Extended the audit section rule with the ordering and closing-vs-constituting distinction

New test files:
- `_tests/ground/test_ground_adr0191_criteria_forward_gate.py` — 2 tests
- `_tests/ground/test_ground_adr0191_r2_audit_ordering.py` — 2 tests

---

## Consequences

- **Positive**: Criteria→FN transition has an unambiguous positive forward obligation, not just a general no-pause rule
- **Positive**: R2 audit section now has a required ordering relative to its sentinel; implicit completion is not valid
- **Note**: Both fixes address emphasis/ordering gaps in existing rules; no new behavioral requirements introduced
