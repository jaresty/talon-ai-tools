# ADR-0186: Rung Action Discipline (P4)

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

The ground protocol defines what each rung *produces* (artifact type) and when it may be
*entered* (gate condition), but not which tool calls are valid *within* the rung.
This omission is the root cause of a recurring class of escape routes:

- **L31** — V-complete emitted before the pre-existence check tool call
- **L34** — test runner invoked before the artifact file-write at EV
- **L35** — test file edited at the EV rung instead of (or alongside) the artifact write
- **Meta-test bypass** — prior EV artifact modified at the EI rung without declaring it as
  the implementation artifact and writing a meta-test as the new EV artifact

All four are instances of the same structural gap: no named principle bounds what actions
are permitted at a rung. Per-rung prohibitions are added reactively. Without a principle,
new rung-action violations will continue to appear as escape routes.

### Depends analysis

Rules that derive from P4 once stated (remain for explicitness, labeled P4-derivative):

| Rule | Derivation |
|------|-----------|
| L31 pre-existence forward gate | P4: pre-existence check is in EV action set; must precede V-complete |
| L34 file-write before test run | P4: action set ordering at EV rung |
| L35 no other edits at EV | P4: EV action set is closed — any other edit is outside it |
| Meta-test gate (line 239) | P4: EI action set allows one implementation edit; prior EV artifact is not implementation |

Rules that do **not** derive from P4 (genuine per-rung exceptions):

| Rule | Why not P4 |
|------|-----------|
| L32 harness-classification gate | About classification before HARD STOP, not action set membership |
| L33 unchanged-criterion trap | About criterion content identity, not action set |
| VRO re-run-without-edit prohibition | Cross-rung ordering across cycles, not action set |
| Carry-forward on EV artifact modification | Traversal record-keeping, not action set membership |

---

## Decision

Add **P4 (Rung action discipline)** as the fourth named principle in the ground prompt
alongside P1, P3, A3, and R2.

P4 states: **each rung has a closed action set; any tool call not in that rung's action
set is a protocol violation regardless of the outcome of the call.**

### Action sets per rung

The constraint is **type**, not count — multiple writes are permitted when all targets are
the correct type for that rung.

| Rung | Valid tool calls | Type constraint |
|------|----------------|----------------|
| Prose | none | — |
| Criteria | none | — |
| Formal notation | none | — |
| Executable validation (EV) | (1) pre-existence/pre-failure check, (2) validation artifact file-writes, (3) test runner — in order | validation artifacts only; writing implementation files is a violation |
| Validation run observation (VRO) | test runner only | — |
| Executable implementation (EI) | implementation file-writes | implementation files only; writing a file that was the EV artifact in any prior cycle is a violation unless meta-test pattern is in effect |
| Observation (OBR) | read-only tool calls | no writes of any type |

### Ordering within EV

The action set at EV is ordered:
1. Pre-existence/pre-failure check tool call
2. Validation artifact file-write(s)
3. Test-runner invocation

Emitting V-complete before step 1, or invoking the test runner before step 2, are P4
violations even if the outcome would be the same.

---

## Implementation

### Phase 1 — Add P4 to named principles block

Add P4 immediately after P3 in `lib/groundPrompt.py`:

```
P4 (Rung action discipline): each rung has a closed action set;
any tool call not in that rung's action set is a protocol violation.
Action sets:
  prose/criteria/formal notation — no tool calls;
  EV — pre-existence check, then artifact file-write, then test runner, in order;
  VRO — test runner only;
  EI — exactly one file-write to the implementation (not to a file that served as the EV artifact
       in a prior cycle of this thread, unless the meta-test pattern is in effect);
  OBR — read-only tool calls only.
```

### Phase 2 — Write tests

New test file: `_tests/ground/test_ground_adr0186_p4.py`

Tests verify:
1. P4 is named in the prompt
2. EV action set lists pre-existence check, file-write, and test runner
3. EV ordering constraint present (pre-existence before V-complete)
4. EI constraint names implementation as valid edit target
5. OBR read-only constraint present

### Phase 3 — Migrate P4-derivative test pins to behavioral-effect form

Migrate the assertIn anchors in `test_ground_l31_l34.py` (and any other files pinning
L31/L34/L35/meta-test prose) to OR-logic behavioral-effect form so they pass on both
the current prose and the post-deletion prompt. Pattern from ADR-0185 Phase 2:

```python
# Before (literal-phrase pin — breaks on deletion):
self.assertIn("only valid next action is that tool call", self.prompt)

# After (behavioral-effect OR-form — survives deletion):
has_gate = (
    "only valid next action is that tool call" in self.prompt
    or (
        "P4" in self.prompt
        and "pre-existence" in self.prompt
        and "executable validation" in self.prompt
    )
)
self.assertTrue(has_gate, "L31: pre-existence forward gate must be present via P4 or explicit rule")
```

Rules to migrate:
- L31: pre-existence check forward gate (`test_ground_l31_l34.py::TestL31VCompleteForwardGate`)
- L34: file-write before test run (`test_ground_l31_l34.py::TestL34EVArtifactSequencing`)
- L35: no other edits at EV (new test from Phase 2)
- Meta-test gate: EI edit to prior EV artifact requires meta-test (any existing pins)

### Phase 4 — Delete P4-derivative prose

Once Phase 3 migration passes, delete the explicit per-rung prohibitions that P4 subsumes:
- L31 explicit forward gate text (kept by P4's EV ordering rule)
- L34 explicit ordering text (kept by P4's EV action-set order)
- L35 explicit "no other edits at EV" text (kept by P4's closed action set)
- Meta-test gate explicit text at line 239 (kept by P4's EI action-set constraint)

Net size reduction: ~250–350 chars (offsetting P4 addition of ~150 chars).

---

## Consequences

- **Positive**: new rung-action violations are immediately named as P4 violations; no new
  principle required
- **Positive**: action set enumeration makes it obvious when a rung lacks constraints
- **Negative**: P4 adds ~150 chars to the prompt; partially offset when P4-derivative
  rules are eventually deleted
- **Neutral**: L31, L34, L35 remain for now — they are P4 instantiations, not redundant
  until P4 is proven to subsume them through test migration

---

## Size impact

| Phase | Delta |
|-------|-------|
| Phase 1 (add P4) | +~150 chars |
| Phase 2 (add P4 tests) | prompt unchanged |
| Phase 3 (migrate test pins) | prompt unchanged |
| Phase 4 (delete P4-derivative prose) | −~250–350 chars |
| **Net** | **−~100–200 chars** |
