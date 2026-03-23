# Ground Prompt F1–F5 Fix State Snapshot

Date: 2026-03-23

## Completed — 5 escape routes closed

| Fix | Thread | Escape route closed | Canonical marker phrase |
|-----|--------|--------------------|-----------------------|
| F1 | 1 | OBS cycle anchor — OBS could fire after Manifest exhausted | `"after the most recent 🟢 Implementation gate cleared in this thread"` (Thread N complete gate) |
| F2 | 2 | Red-witness cycle anchor — prior green from another thread satisfied gate | `"after the most recent 🟢 Implementation gate cleared for this thread"` (VRO section) |
| F3 | 3 | Structural criteria gate — column-header assertions satisfied criteria rung | `"column header is present does not satisfy this rung"` (criteria section) |
| F4 | 4 | OBS artifact type for UI — server-start / DOM query satisfied "rendered DOM content" | `"browser-visible text and values — not a test runner's DOM query result"` (OBS rung) |
| F5 | 5 | Per-criterion demonstration — aggregate test pass satisfied "directly demonstrates" | `"test pass is not a demonstration"` (Thread N complete gate) |

## Tests added (test_ground_rewrite_thread1.py)
- test_f1_thread_complete_has_cycle_anchor
- test_f2_red_witness_has_cycle_anchor
- test_f3_structural_criterion_gate_present
- test_f3_structural_criterion_names_counterexample
- test_f4_obs_ui_artifact_type_named
- test_f5_thread_complete_demonstration_excludes_test_pass

## Tests updated
- test_thread_complete_requires_obs_label_written → new anchor phrase
- test_obs_section_is_compact → ≤950 (was ≤850, +F4 ~90 chars)
- test_criteria_section_is_compact → ≤1050 (was ≤750, +F3 ~257 chars)

## Totals
- Before: 10759 chars
- After: 11249 chars (+490 for 5 escape-route closures)
- Tests: 97 passing (Python), all Go tests passing
