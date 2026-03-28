# ADR-0195: VRO Gap-Block for Harness Errors and V-Complete Emission Blocker

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

The ADR-0192 VRO harness routing rules (HARD STOP not valid; proceed to EI) were added but the infinite loop persisted. Two structural reasons:

### Gap 1 — Gap-then-HARD-STOP chain survives the ADR-0192 prohibition

ADR-0192 said "HARD STOP is not valid" for VRO harness errors, but:
1. The generic VRO rule says "emit 🔴 Execution observed then 🔴 Gap:" — an unconditional positive instruction
2. Once 🔴 Gap: is emitted at VRO, the rule "after emitting 🔴 Gap: at the observation rung, the criteria rung label is the only valid next token" activates
3. HARD STOP is the path to the criteria rung label
4. The model satisfies the HARD STOP gate (exec_observed + Gap at VRO) and fires it

The root fix: **🔴 Gap: may not be emitted at VRO for harness errors**. A harness error names a missing file, not a behavioral gap. Blocking Gap eliminates the entire chain.

ADR-0192's HARD STOP prohibition is a negative constraint after the Gap is already emitted — too late. The fix must be upstream: block Gap itself.

### Gap 2 — V-complete stated as a requirement, not a blocker

ADR-0192 added: "P4 EV step (1) result must have produced a tool-executed result in the transcript." This is a description of a requirement, not an emission blocker. The model could read it as "this should be done" rather than "the sentinel cannot fire without it."

The fix: rewrite as "if no P4 step (1) tool-call result exists, ✅ Validation artifact V complete **may not be emitted**" — a direct blocker on the sentinel.

---

## Decision

### Fix 1 — Block 🔴 Gap: at VRO for harness errors

Replace the ADR-0192 HARD STOP prohibition rules with positive token prescriptions:

> "when VRO exec_observed is a harness error caused by a missing implementation file:
> 🔴 Gap: may not be emitted — there is no behavioral gap, only a missing file;
> the only valid next token is the executable implementation rung label; HARD STOP is not valid"

> "when VRO exec_observed is a harness error caused by a test file error:
> 🔴 Gap: may not be emitted; the only valid next token is a tool call that repairs the test file at the EV rung — not HARD STOP"

### Fix 2 — V-complete as hard blocker

Replace: "P4 EV step (1) result must have produced a tool-executed result"
With: "if no P4 EV step (1) pre-existence or pre-failure check tool-call result exists in the transcript, ✅ Validation artifact V complete **may not be emitted**"

---

## Implementation

Changes to `lib/groundPrompt.py`:
1. Rewrote VRO harness routing to use "🔴 Gap: may not be emitted" + positive next-token prescription
2. Rewrote V-complete P4 gate as an emission blocker ("may not be emitted") not a requirement statement

Updated tests:
- `_tests/ground/test_ground_adr0192_vro_harness_routing.py` — added idx_vro_harness3 pattern
- `_tests/ground/test_ground_rewrite_thread1.py` — VRO cap raised 960 → 1120

New test files:
- `_tests/ground/test_ground_adr0195_vro_gap_block.py` — 2 tests
- `_tests/ground/test_ground_adr0195_v_complete_block.py` — 1 test

---

## Consequences

- **Positive**: VRO harness error no longer opens the Gap→HARD STOP→criteria chain; the only path is forward to EI or backward to EV
- **Positive**: V-complete sentinel is now a hard blocker, not a soft requirement
- **Structural note**: the ADR-0192 "HARD STOP is not valid" language is preserved as a redundant safety but the primary block is now Gap-upstream
