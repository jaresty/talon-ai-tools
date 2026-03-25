# ADR-0180: Ground Prompt SWE Drift Closure

**Status**: Implemented
**Date**: 2026-03-24
**Supersedes**: Portions of ADR-0179

---

## Context

Orbit/drift analysis of a live SWE run (transcript: `Downloads/Untitled (31)`) identified five structural escape routes that survived the ADR-0179 axiomatic rewrite. All five share the same attractor: the model substitutes test-runner output for every rung's required artifact type, dissolving A2 (type discipline) in practice while satisfying it nominally.

Additionally, the session produced a series of iterative prompt fixes (meta-test rule, continuous traversal, formal notation content gate, sequential thread execution, criterion-emergence gate, manifest-labels-only) that addressed individual symptoms. This ADR consolidates the remaining gaps found in the SWE transcript.

---

## Observed Failures

### F1 — HARD STOP misfires at EV harness errors

**What happened**: 🛑 HARD STOP fired three times at the executable validation rung when the test produced a harness error (component not exported). The protocol rule says "a harness error is not a red run — fix the harness error before treating any run as a red witness," but does not prohibit HARD STOP at that position.

**Root cause**: HARD STOP has a positive precondition (requires VRO Execution observed + Gap) but no explicit prohibition at other positions. The model used it as a generic "start over" signal.

**Fix**: Add explicit prohibition: HARD STOP is prohibited unless a 🔴 Execution observed and 🔴 Gap have been emitted at the validation run observation rung in the current cycle. A harness error at the EV rung requires fixing the harness — it does not trigger HARD STOP.

---

### F2 — Manifest exhaustion miscounts threads

**What happened**: ✅ Manifest declared listed 5 gap labels (despite saying "4 threads"). ✅ Manifest exhausted was emitted as "2/2 threads complete" — the model re-counted using the Thread N complete sentinels rather than verifying against the declared manifest count.

**Root cause**: "Check the thread count before emitting" does not say *which* count to check against. The model checked how many Thread-complete sentinels existed rather than how many threads were declared in ✅ Manifest declared.

**Fix**: The exhaustion check must verify that the number of ✅ Thread N complete sentinels equals the count N stated in the ✅ Manifest declared sentinel — not a recount of completed sentinels.

---

### F3 — Formal notation const assignments not caught

**What happened**: The formal notation rung produced `const REQUIRED_COLUMNS = { ... } as const` — a TypeScript constant that compiles and runs as-is. The prohibition on "variable assignments" did not catch `const` assignments.

**Root cause**: The permitted/prohibited list says "prohibited: complete function bodies, variable assignments, working logic sequences." `const X = ...` is a constant, not a variable — the model read the prohibition as not applying.

**Fix**: Expand the prohibition to explicitly include constant declarations (`const`, `let`, `var` assignments) alongside variable assignments. The test: if the artifact contains an assignment operator (`=`) outside a type definition, it is implementation code.

---

### F4 — VRO rung skipped between EV harness error and OBR

**What happened**: Thread 1, cycle 2: after the harness-error red run at EV, the model emitted ✅ Validation artifact V complete and 🟢 Implementation gate cleared, then jumped directly to OBR. No VRO rung fired in cycle 2. The green run at OBR was the first post-implementation run for that cycle.

**Root cause**: The rule "🟢 Implementation gate cleared requires a 🔴 Execution observed from the current cycle's VRO rung" was not enforced because the harness-error run was treated as the VRO run. But a harness error at EV is not a VRO run — it never reached VRO.

**Fix**: Clarify that the VRO rung must fire as a named rung (its label must appear in the transcript) before 🟢 can be emitted. A run at the EV rung does not satisfy the VRO rung regardless of whether it produced a failure.

---

### F5 — OBR satisfied by test-runner output

**What happened**: The OBR Execution observed at both threads showed vitest test-pass output. The rule "a test pass/fail report is not valid OBS output" exists but was not applied. The model treated the green test run as behavioral observation.

**Root cause**: The prohibition exists but is stated as a property of invalid output rather than as a gate precondition. The model emitted OBR, ran tests, saw green, and emitted ✅ Thread N complete — the rule was read as advisory rather than blocking.

**Fix**: Add an explicit blocking gate: if the Execution observed at OBR contains test runner output (pass/fail summary, test names, duration), it does not satisfy the OBR gate — re-invoke the implemented artifact directly before continuing. ✅ Thread N complete may not be emitted after an OBR Execution observed that shows test runner output.

---

## Changes Required to `lib/groundPrompt.py`

### C1 — HARD STOP position prohibition
In the HARD STOP rule, add: "HARD STOP may not be emitted at the executable validation rung — a harness error at EV requires fixing the harness, not an upward return; only a post-VRO Gap justifies HARD STOP."

### C2 — Manifest exhaustion count anchor
In the manifest exhaustion rule, add: "before emitting ✅ Manifest exhausted, locate the N in the ✅ Manifest declared sentinel and count ✅ Thread N complete sentinels — if the count does not equal the declared N, the manifest is not exhausted."

### C3 — Formal notation const prohibition
In the formal notation content prohibition, add: "constant declarations (const, let, var assignments) are prohibited regardless of what they assign — the presence of an assignment operator outside a type definition indicates implementation code."

### C4 — VRO rung label requirement for impl gate
In the 🟢 Implementation gate cleared rule, add: "the VRO rung label must appear in the transcript for the current cycle — a run at the EV rung does not satisfy the VRO gate regardless of whether it produced a failure."

### C5 — OBR test-output blocking gate
In the ✅ Thread N complete rule, add: "if the Execution observed at the OBR rung contains test runner output (pass counts, test names, duration summary), it does not satisfy the OBR gate — ✅ Thread N complete may not be emitted; re-invoke the implemented artifact directly."

---

## Implementation Plan

Each change (C1–C5) is a ground cycle: test first, then prompt edit, then full suite. Implement in order C5 → C2 → C1 → C4 → C3 (highest-impact first).

---

## Also Fixed This Session (reference)

These were implemented and committed during the session that produced this ADR:

- Meta-test rule for test-modification intent (commit 6fec5e8b)
- Verbatim restatement at formal notation rung (commit b7ca6d1b)
- Continuous traversal + formal notation content gate + sequential thread gate (commit 1ea4541e)
- Criterion emergence gated on Thread N complete (commit 44b43ca6)
- Sequential thread gate extended to all rungs (commit 30ab9b6b)
- Immediate descent after criteria + formal notation coverage obligation (commit b2003117)
- Manifest entries constrained to gap labels only (commit c4259897)
- Restored missing Go test phrases (commit f112bd58)
