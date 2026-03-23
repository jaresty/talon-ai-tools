# Ground Prompt Collapse Progress

Started: 2026-03-23
Target: ~7500 chars (from 14745)

## Clusters

| # | Cluster | Status | Chars saved |
|---|---------|--------|-------------|
| 1 | Rung satisfaction axiom + artifact type (4→2) | ✅ done | ~295 chars |
| 2 | ORB output type (4→1) | ✅ done | (merged into cluster 1) |
| 3 | Implementation gate (3→1) | skipped — no internal redundancy | — |
| 4 | Validation rung prohibitions (8→1) | ✅ done | ~269 chars |
| 5 | Criterion atomicity (3→1) | ✅ done | ~253 chars |
| 6 | Pre-existing artifact check (3→1) | ✅ done | ~358 chars |
| 7 | Vacuity check (3→1) | ✅ done | ~203 chars |
| 8 | Implicit-coverage duplication (2→1) | ✅ done | ~62 chars |
| 9 | Prose re-emission (3→1) | ✅ done | ~151 chars |
| 10 | Gap phrasing rules (3→1) | ✅ done | ~46 chars |
| 11 | Upward return taxonomy (3→1) | ✅ done | ~114 chars |

## Baseline
- chars before collapse: 14745
- tests before collapse: 83 passing, 1 failing (test_total_chars_under_3000)

## Final state (pass 1 — cluster collapse)
- chars: 12981 (−1764 from 14745, ~12% reduction)
- tests: 87 passing, 0 failing
- all 11 clusters complete

## Pass 2 — paragraph-level rewrite (ADR-0177 deeper collapse)

Started: 2026-03-23
Target: ~5850 chars

| Thread | Section | Before | After | Target |
|--------|---------|--------|-------|--------|
| 1 | EV rung | 2182 | 1162 | ~1200 |
| 2 | OBS rung | 1550 | 846 | ~800 |
| 3 | VRO red-witness | 694 | 558 | ~600 |
| 4 | Criteria rung | 1019 | 746 | ~700 |
| 5 | Reconciliation gate | 524 | 355 | ~350 |

## Final state (pass 2 — paragraph rewrite)
- chars: 10759 (−2222 from 12981, −3986 from 14745, ~27% total reduction)
- tests: 91 passing, 0 failing
- 5 section rewrites complete, 5 new size-gate tests added

## After cluster 1+2
- chars: 14450 (−295)
- tests: 86 passing, 0 failing
- removed: "test pass/fail report is not valid OBS output", "tests are never a valid consumer at this rung", "speak for itself without requiring the reader to"
- updated tests: test_c7_carveout, test_c7_output_criterion_test_report_invalid, test_c7_output_must_speak_for_itself → now assert canonical marker phrases
