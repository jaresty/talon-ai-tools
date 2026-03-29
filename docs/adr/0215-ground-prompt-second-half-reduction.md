# ADR-0215: Ground Prompt — Second Half Reduction

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

ADR-0214 replaced the P4 prose enumeration and `_type_taxonomy_block()` with a generative kernel, reducing `core` by ~1,383 chars (33,473 → 32,090). That reduction targeted the first third of the prompt. The remaining ~20,000 chars of escape-route-closer prose (lines ~244–513 of `groundPrompt.py`) was not analyzed for the same treatment.

A classification audit of the second half (using the same A/B/C/D taxonomy from ADR-0214) identifies three reduction targets:

**Target 1 — VRO harness error routing block (~350 chars → ~130 chars)**

The three harness error subtypes each state "the only valid next token is X" in full prose:
- `when VRO exec_observed is a harness error caused by a missing implementation file` → EI directly
- `when VRO exec_observed is a harness error caused by a test file error` → EV repair
- `when VRO exec_observed is a test-interaction failure` → EV repair

This is non-derivable (each subtype routes differently and can't be inferred from type discipline alone). But the structure is three parallel `when [condition]: [route]` clauses padded with explanatory prose that restates the same conclusion three times ("not HARD STOP", "not Gap:", "not impl_gate"). A compact routing table preserves all three routes with none of the repetition.

**Target 2 — Criteria rung A2/sequencing restatements (~350 chars)**

Two passages in the criteria block restate rules already present in the generative kernel:

1. `"after the criterion is written, the only valid next token is the formal notation rung label; each rung label opens a content-type context — criteria-type content… belongs to the criteria rung, notation-type content… belongs to the formal notation rung; emitting content whose type belongs to a different rung before that rung's label fires is a type violation under A2"` (~200 chars) — pure A2 restatement applied per-rung. The gate formula already states this; applying it at the criteria level adds no new information.

2. `"the criteria rung label is per-thread — writing criteria for Thread 2 or any subsequent thread before ✅ Thread 1 complete is a protocol violation; batch-collecting criteria for multiple threads under one criteria label bypasses sequential descent and is a protocol violation; each thread's criterion is only valid in the context of that thread's descent"` (~250 chars) — thread sequencing policy already stated in the axiom block ("all seven rungs for Thread N must complete before any content for Thread N+1 may appear"). This is that rule applied to the criteria rung specifically.

**Target 3 — OBR "none of the following" enumeration (~100 chars)**

`"none of the following satisfies the OBR gate: passing tests, functionally complete implementation, prior work stopped at EI, or precedent"` — A1 enumerated for OBR. Derivable from A1 ("only tool-executed events have evidential standing"). However models specifically rationalize each of these, so this warrants a why-sentence rather than full removal.

**Non-targets (keep as-is):**

The following blocks are non-derivable and should NOT be reduced:
- Harness error routing (the classification of subtypes) — routes differ, must enumerate
- Conjunction splitting rule at criteria rung — models rationalize compound criteria
- "narrowing the criterion / substituting a weaker behavior" prohibition — most common escape
- HARD STOP valid-in-one-case + position gate — already in Section 5, load-bearing
- "query must exercise criterion's behavior directly, not merely confirm server is running" — closes liveness-as-proof
- Thread N complete block: "most recent exec_observed shows any test failure → blocked" — non-derivable; models argue "it's basically passing"
- All three VRO harness error ROUTES — keep; only the verbose per-clause prose shrinks

---

## Decision

### Change 1 — VRO harness error routing: compact table replaces three verbose clauses

**Remove** (~350 chars):
```
when VRO exec_observed is a harness error caused by a missing implementation file:
🔴 Gap: and 🟢 Implementation gate cleared may not be emitted after a harness error;
the only valid next token is the executable implementation rung label; HARD STOP is not valid.
when VRO exec_observed is a harness error caused by a test file error
(syntax error, import of a non-existent component in the test itself):
same block rule applies; the only valid next token is a tool call that repairs the test file at the EV rung — not HARD STOP.
when VRO exec_observed is a test-interaction failure —
the tests loaded and ran but could not interact with the component under test
(e.g., pointer-events: none, role not found, element not accessible) —
🔴 Gap: may not be emitted and 🟢 Implementation gate cleared is not valid;
the only valid next token is a tool call that repairs the component's accessibility
or the test's interaction strategy at the EV rung;
this is a harness error class, not a behavioral failure.
```

**Replace with** (~130 chars):
```
Harness error routing (all three block 🔴 Gap: and 🟢 Implementation gate cleared; HARD STOP is not valid):
missing-implementation-file → EI directly;
test-file-error (syntax error, import of non-existent component) → EV repair;
test-interaction-failure (pointer-events: none, role not found, element not accessible) → EV repair; this is a harness error class, not a behavioral failure.
```

**Rationale**: The three repeated "not HARD STOP", "not Gap:", "not impl_gate" clauses are derivable from the routing table itself — once you know the route, the invalid alternatives are determined. The routing table preserves all three case distinctions with none of the repetition.

### Change 2 — Criteria rung: remove A2 restatement and thread-sequencing restatement

**Remove** the A2 type-context paragraph (~200 chars):
```
after the criterion is written, the only valid next token is the formal notation rung label;
each rung label opens a content-type context — criteria-type content (a falsifiable behavioral assertion) belongs to the criteria rung,
notation-type content (type signatures, interfaces, invariants, pseudocode) belongs to the formal notation rung;
emitting content whose type belongs to a different rung before that rung's label fires
is a type violation under A2 regardless of whether the correct label eventually follows.
```

**Rationale**: This is A2 applied to the criteria-to-notation transition. The gate formula states A2 globally; restating it per-rung for one specific transition adds no new constraint.

**Remove** the batch-collect paragraph (~250 chars):
```
the criteria rung label is per-thread —
writing criteria for Thread 2 or any subsequent thread before ✅ Thread 1 complete is a protocol violation;
batch-collecting criteria for multiple threads under one criteria label bypasses sequential descent
and is a protocol violation;
each thread's criterion is only valid in the context of that thread's descent —
writing criteria for all threads before descending any treats the rung as a planning step, which it is not.
```

**Rationale**: The thread-sequencing policy in the axiom block already states "all seven rungs for Thread N must complete before any content for Thread N+1 may appear." The batch-collect rule is that policy applied at the criteria rung. A model that has applied the sequencing policy correctly cannot batch-collect criteria — it's derivable.

**Risk**: If the batch-collect rationalization proves to resurface in transcripts after this removal, re-add as a why-sentence in ADR-0216.

### Change 3 — OBR "none of the following" enumeration: compress to why-sentence

**Replace** (~100 chars):
```
none of the following satisfies the OBR gate: passing tests, functionally complete implementation,
prior work stopped at EI, or precedent —
the gate requires a manual live-process invocation in the current cycle.
```

**Replace with** (~80 chars):
```
prior evidence — passing tests, complete implementation, or prior cycles — does not satisfy the OBR gate;
only a live-process invocation in the current cycle does.
```

**Rationale**: The enumeration is A1 applied to OBR, but the specific items (passing tests, prior work) are seductive enough to warrant naming. Compressing to a shorter why-sentence preserves the non-derivable intent without the full clause.

---

## Classification Audit

| Rule | Category | Disposition |
|---|---|---|
| VRO harness error routing (3 subtypes) | C — non-derivable routes | Keep routes; compact verbose per-clause prose → routing table |
| "after criterion, only valid next token is formal notation" | A — A2 restatement | Remove |
| "emitting content whose type belongs to different rung is A2 violation" | A — A2 restatement | Remove |
| "criteria rung label is per-thread / batch-collecting" | B — thread sequencing restatement | Remove |
| "none of the following satisfies OBR gate" enumeration | A — A1 applied to OBR | Compress to why-sentence |
| Conjunction splitting rule | C — non-derivable | Keep |
| "narrowing criterion / substituting weaker behavior" | C — non-derivable | Keep |
| HARD STOP valid-in-one-case | C — non-derivable | Keep (already in Section 5) |
| "query must exercise criterion directly" | C — non-derivable | Keep |
| Thread N complete block | C — non-derivable | Keep |
| Green-without-red vacuity | C — non-derivable | Keep (already in Section 5) |

---

## Consequences

**Expected reduction**: ~700–800 chars (from 32,090 → ~31,300).

**Escape-route durability test**: After applying this ADR, run the ground method on 2–3 transcripts that previously triggered:
- Batch-collect at criteria (to confirm sequencing policy covers it)
- A2 type-context at criteria-to-notation (to confirm gate formula covers it)
- Harness error routing (to confirm compact table is sufficient)

If any previously-closed escape route reopens, re-add as a why-sentence per the ADR-0198 framework.

**Implementation**: Edit `GROUND_PARTS_MINIMAL["core"]` directly. Run `make axis-regenerate-apply` to propagate. Tests for removed phrases in the criteria and VRO sections need to be updated (same pattern as ADR-0214).
