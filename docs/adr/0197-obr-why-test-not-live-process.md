# ADR-0197: OBR Why-Sentence — Test Output Is Not Live-Process Evidence

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

Analysis of a transcript (pre-ADR-0196) revealed a model closing Thread 2 and Thread 3 with test runner output as OBR evidence — never opening a browser or invoking the live process. The type taxonomy block already states that test runner output is VRO-type and cannot satisfy the OBR gate, but gives no reason. A model that doesn't understand *why* treats the prohibition as bureaucratic and substitutes the closest available evidence (passing tests) for the required evidence (live-process output).

The specific escape route: the model ran 32 tests, saw them pass, emitted `✅ Thread N complete` — having never demonstrated the behavior as a running system. The criterion for each thread named observable UI behavior; the evidence was unit test assertions.

The missing why: **a passing test proves the test harness's assertions pass — not that the described behavior exists as a running system.** Tests are hypotheses about behavior encoded as assertions; a passing test means the assertions didn't fail, not that you can observe the behavior. The OBR rung exists because these are different claims.

---

## Decision

Add one why-sentence to `_type_taxonomy_block()` in `lib/groundPrompt.py`, immediately after the OBR-type classification rule:

> "a passing test proves the test harness's assertions pass — not that the described behavior exists as a running system; this is why test runner output is VRO-type and cannot satisfy the OBR gate regardless of the result"

---

## Implementation

- `lib/groundPrompt.py`: one sentence added to `_type_taxonomy_block()` notes
- `_tests/ground/test_ground_adr0197_obr_why.py`: new test file, 2 tests
- Three size-cap baselines updated: redundancy_audit, rung_table, rewrite_thread1 (+220 chars)

---

## Consequences

- **Positive**: models understand the OBR gate is not satisfied by inference from test results — it requires a distinct kind of evidence production
- **Known limitation**: a model that has decided to skip OBR will not be stopped by this sentence; why-framing helps at margins and with category errors, not adversarial non-compliance
