# ADR-0193: Criteria Batch-Collection — Single-Thread Artifact Definition

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

A model transcript showed the criteria rung batch-collecting criteria for all 6 declared threads under a single criteria rung label — writing one criterion sentence per thread (each tagged with `[T: gap-name]`) before proceeding to formal notation. The result was:
- 6 criteria sentences under one label
- `[T: gap-name]` markers in the criteria rung (prohibited — prose-only)
- Formal notation encoding 6/6 criteria as if this were valid
- `✅ Formal notation R2 audit complete — 6/6 criteria encoded` with no actual descent

The existing prohibition rules were present:
- "batch-collecting criteria for multiple threads under one criteria label is a protocol violation"
- "writing criteria for Thread 2 before Thread 1 complete is a protocol violation"
- "[T: gap-name] markers are valid only in the prose rung"

But the rule "exactly one criterion may be written **per thread** per cycle" is structurally ambiguous — it reads as "at most one criterion PER thread" (a per-thread cap), which the model satisfies by writing exactly one criterion for each of the 6 threads. The intent is "exactly one criterion for the **current** thread total," but the phrasing permitted the batch interpretation.

---

## Decision

Add a positive artifact definition before the "exactly one criterion" rule:

> "the criteria rung artifact is exactly one criterion for the current thread only — not one criterion per thread, not criteria for all threads collected under one label"

This makes the criteria rung artifact definition unambiguous: the entire criteria rung produces one criterion for one thread. The prohibition rules that follow then reinforce a positive definition rather than standing alone.

---

## Implementation

Changes to `lib/groundPrompt.py`:
- Added sentence: `"the criteria rung artifact is exactly one criterion for the current thread only — not one criterion per thread, not criteria for all threads collected under one label"`
- Retained "exactly one criterion may be written per thread per cycle" and "second criterion for the same thread" verbatim (required by L17/ADR-0191 tests)

Updated `_tests/ground/test_ground_l24.py`:
- Proximity cap raised 1600 → 1750 (new sentence adds ~130 chars before the per-thread gate)

New test file: `_tests/ground/test_ground_adr0193_criteria_single_thread.py` — 2 tests

---

## Consequences

- **Positive**: criteria rung artifact has a positive definition as a single-thread artifact; batch-collecting is excluded structurally, not just by prohibition
- **Positive**: the `[T: gap-name]`-in-criteria pattern is now a clear violation of the artifact definition (not just a rule elsewhere)
- **Known limitation**: a model that writes the definition sentence and then ignores it is not addressed here — that requires a different mechanism
