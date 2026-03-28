# ADR-0192: VRO Harness Loop — Missing Implementation File and V-Complete Gate

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

A model transcript showed an infinite loop: EV artifact written → test runner invoked → harness error (import failure because `CreateAttributeForm` component does not exist) → `🔴 Gap: component does not exist` → `🛑 HARD STOP` → criteria → formal notation → `✅ Validation artifact V complete` → repeat. The component was never created. The loop ran 8+ times without reaching the EI rung.

Two gaps caused this:

### Gap 1 — VRO harness error has no HARD STOP prohibition

The prompt blocks HARD STOP at EV for harness errors:
> "HARD STOP may not be emitted at the executable validation rung — a harness error at EV requires fixing the harness, not an upward return"

No equivalent rule exists for the VRO rung. When the VRO harness fails because the implementation file is missing, the model has no rule preventing HARD STOP and fires it repeatedly.

The existing rule "fix the harness error before treating any run as a red witness" is ambiguous at VRO — it doesn't say whether "fix" means go back to EV, go to EI, or return to criteria.

### Gap 2 — `✅ Validation artifact V complete` emitted without P4 step (1) result

The P4 EV action sequence states step (1) is "pre-existence or pre-failure check." The `✅ Validation artifact V complete` gate only required artifact content to appear — it did not require the P4 step (1) tool-call result to be in the transcript. The model emitted the sentinel after writing the file without any pre-existence check, making the gate vacuous.

---

## Decision

### Fix 1 — VRO-specific harness error routing

Add explicit rules distinguishing the two VRO harness error cases:

- **Missing implementation file**: this is an EI gap, not a spec gap — HARD STOP is not valid; the only valid next action is to proceed to EI and create the file
- **Test file error** (syntax, import of a non-existent component in the test itself): return to EV and fix the test file — not HARD STOP

### Fix 2 — V-complete gate requires P4 step (1) result

Add to the `✅ Validation artifact V complete` gate: the P4 EV step (1) pre-existence or pre-failure check must have produced a tool-executed result in the transcript — asserting non-existence without a tool call result does not satisfy this gate.

---

## Implementation

Changes to `lib/groundPrompt.py`:
1. After "fix the harness error before treating any run as a red witness" — added two VRO-specific harness routing rules
2. Before "emitting the sentinel without quoting the artifact" — added P4 step (1) tool-call result requirement

Updated `_tests/ground/test_ground_rewrite_thread1.py`:
- VRO section size cap raised from 810 → 960 chars (new VRO harness routing text adds ~123 chars)

New test files:
- `_tests/ground/test_ground_adr0192_vro_harness_routing.py` — 2 tests
- `_tests/ground/test_ground_adr0192_v_complete_gate.py` — 2 tests

---

## Consequences

- **Positive**: VRO harness error caused by a missing implementation file now has an unambiguous routing rule — proceed to EI, never HARD STOP
- **Positive**: `✅ Validation artifact V complete` gate now requires the P4 pre-existence check tool call to be in the transcript
- **Known limitation**: the loop could still occur if the model emits the V-complete sentinel vacuously (without checking) — but the gate now has a clear prohibition that enables detection
