# ADR 0095: Future Token Migration Automation Improvements — Work Log

## 2026-01-28 — loop 001

- helper_version: helper:v20251223.1
- focus: ADR 0095 Decision section #1 → Implement grammar sync validation Make targets so grammar drift is caught in CI (salient task: item #1 from Decision section)
- active_constraint: No Make target exists to verify that `build/prompt-grammar.json`, `internal/barcli/embed/prompt-grammar.json`, and `cmd/bar/testdata/grammar.json` remain synchronized, allowing stale grammar copies to merge undetected and cause test failures (validated via attempting `make bar-grammar-check` which should fail with "no such target")
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | High | Prevents grammar drift test failures that block merges |
  | Probability | High | Make target is deterministic; git diff guarantees sync detection |
  | Time Sensitivity | Medium | Prevents future drift but no immediate deadline |
  | Uncertainty note | Low | Validation path is well-established (existing regeneration works) |
- validation_targets:
  - `make bar-grammar-check` (verifies grammar files are in sync)
  - `make bar-grammar-update` (regenerates grammar files)
- evidence:
  - red | 2026-01-28T22:35:00Z | exit 2 | make bar-grammar-check
    - helper:diff-snapshot=0 files changed
    - behaviour: grammar sync validation fails with "No rule to make target" proving target does not exist | inline
  - green | 2026-01-28T22:42:00Z | exit 0 | make bar-grammar-check
    - helper:diff-snapshot=Makefile | 17 +++++++++++++++++
    - behaviour: grammar sync validation passes after adding Make targets | inline
  - removal | 2026-01-28T22:44:00Z | exit 2 | git restore --source=HEAD -- Makefile && make bar-grammar-check
    - helper:diff-snapshot=0 files changed
    - behaviour: grammar sync validation fails again after revert, proving targets were required | inline
- rollback_plan: `git restore --source=HEAD -- Makefile`; rerun `make bar-grammar-check` to observe "No rule to make target" failure
- delta_summary: helper:diff-snapshot=Makefile | 17 insertions(+) — added `bar-grammar-check` and `bar-grammar-update` Make targets that validate and regenerate grammar synchronization across build/, embed/, and testdata/
- loops_remaining_forecast: 4 loops remaining (item #2 Go migration support, item #4 validation test, CI integration, final documentation) — high confidence that grammar validation targets work as specified
- residual_constraints:
  - CI integration not yet wired (severity: medium; mitigation: add `bar-grammar-check` step to `.github/workflows/test.yml` in next loop; monitoring: grammar drift will pass CI until this step is added; owning ADR: this ADR)
  - Go test migration support remains manual (severity: medium; mitigation: extend `migrate-test-tokens.py` per item #2; monitoring: next token migration will require manual Go updates; owning ADR: this ADR, item #2)
  - Test token constants not implemented (severity: low; mitigation: evaluate after observing migration patterns per item #3; monitoring: test coupling persists; owning ADR: this ADR, item #3)
  - Grammar validation test not yet created (severity: medium; mitigation: add `_tests/test_obsolete_tokens.py` per item #4; monitoring: obsolete tokens could linger undetected; owning ADR: this ADR, item #4)
- next_work:
  - Behaviour: Wire `bar-grammar-check` into CI workflow; Validation: `.github/workflows/test.yml` contains grammar check step and CI fails when grammar is out of sync; rerun `make ci-guardrails` or equivalent to prove CI detects drift
  - Behaviour: Add Python test to detect obsolete tokens per item #4; Validation: `python3 -m pytest _tests/test_obsolete_tokens.py` passes and detects when obsolete tokens exist in axisConfig
