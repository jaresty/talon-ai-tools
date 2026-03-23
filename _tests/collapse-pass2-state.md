# Ground Prompt Collapse Pass 2 — State Snapshot

Date: 2026-03-23
Commit: c5c6dbd0

## Completed

All 5 threads from ADR-0177 deeper collapse plan executed via ground protocol:

| Thread | Section | Before | After | Test added |
|--------|---------|--------|-------|------------|
| 1 | EV rung | 2182 | 1162 | test_ev_section_is_compact_gate_list (≤1250) |
| 2 | OBS rung | 1550 | 846 | test_obs_section_is_compact (≤850) |
| 3 | VRO red-witness | 694 | 558 | test_vro_section_is_compact (≤650) |
| 4 | Criteria rung | 1019 | 746 | test_criteria_section_is_compact (≤750) |
| 5 | Reconciliation gate | 524 | 355 | test_reconciliation_gate_is_compact (≤400) |

## Totals
- Before pass 2: 12981 chars
- After pass 2: 10759 chars (−2222, ~17%)
- From original 14745: −3986 chars (~27% total)
- Tests: 91 passing

## Key changes
- EV rung: removed verbose prohibition list, "unit of production" verbosity, /tmp restatement, static/runtime check expanded examples
- OBS rung: folded "Before Thread N complete, verify each criterion" into Thread N complete gate condition; removed "binary/command/script" invocation enumeration
- VRO: removed "rung label may not be written until tool output exists" (restatement of "invoke via tool call before writing label")
- Criteria: dropped useFoo example, shortened prose-vocabulary gate, removed "do not emit 🔴 Gap:" suffix
- Reconciliation gate: removed verbose transition enumeration, shortened document update clause

## Next steps (from ADR-0177)
Still at 10759 chars vs ADR target of ~5850. Further reduction requires:
- Structural gates for 3 drift risks (EV one-assertion gate, criteria prose-vocabulary gate, OBS non-test consumer)
- Remaining redundancy in rung sequence header, upward returns, and sentinel formats section
- Deferred: apply equivalent rules to GROUND_PARTS (full 4-section dict)

## Files changed
- lib/groundPrompt.py — 5 section rewrites
- _tests/test_ground_rewrite_thread1.py — 5 new section size-gate tests, 1 test threshold updated
- _tests/collapse-progress.md — pass 2 results recorded
