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

## 2026-01-28 — loop 002

- helper_version: helper:v20251223.1
- focus: ADR 0095 Decision section #1 → Wire grammar sync validation into CI so drift is caught before merge (salient task: CI integration for item #1 from Decision section)
- active_constraint: CI workflow checks only `build/prompt-grammar.json` cleanliness but does not verify that `internal/barcli/embed/prompt-grammar.json` and `cmd/bar/testdata/grammar.json` remain synchronized with it, allowing embed/testdata drift to merge undetected (validated via `.github/workflows/test.yml` inspection showing no `make bar-grammar-check` step)
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | High | Prevents grammar drift from merging and causing downstream test failures |
  | Probability | High | CI enforcement is deterministic; all PRs must pass |
  | Time Sensitivity | High | Grammar sync validation exists but provides no value until CI enforces it |
  | Uncertainty note | Low | Make target validated in loop 001; CI integration is straightforward |
- validation_targets:
  - Inspect `.github/workflows/test.yml` to confirm `make bar-grammar-check` step exists
  - Local simulation: `make bar-grammar-check` runs successfully as CI would
- evidence:
  - red | 2026-01-28T23:15:00Z | exit 0 | grep -q "bar-grammar-check" .github/workflows/test.yml && echo "Found" || echo "Not found"
    - helper:diff-snapshot=0 files changed
    - behaviour: grammar sync check absent from CI workflow; grep returns "Not found" proving step missing | inline
  - green | 2026-01-28T23:18:00Z | exit 0 | grep -q "bar-grammar-check" .github/workflows/test.yml && echo "Found" || echo "Not found"
    - helper:diff-snapshot=.github/workflows/test.yml | 3 +++
    - behaviour: grammar sync check present in CI workflow; grep returns "Found" proving step added | inline
  - removal | 2026-01-28T23:20:00Z | exit 0 | git restore --source=HEAD -- .github/workflows/test.yml && grep -q "bar-grammar-check" .github/workflows/test.yml && echo "Found" || echo "Not found"
    - helper:diff-snapshot=0 files changed
    - behaviour: grammar sync check absent again after revert; grep returns "Not found" proving step was required | inline
- rollback_plan: `git restore --source=HEAD -- .github/workflows/test.yml`; inspect workflow to confirm `bar-grammar-check` step is missing
- delta_summary: helper:diff-snapshot=.github/workflows/test.yml | 3 insertions(+) — added grammar sync validation step after grammar regeneration to catch drift in all three copies (build/, embed/, testdata/) before merge
- loops_remaining_forecast: 3 loops remaining (item #4 validation test, item #2 Go migration support, final documentation update) — high confidence that CI integration works as grammar check target is validated
- residual_constraints:
  - Go test migration support remains manual (severity: medium; mitigation: extend `migrate-test-tokens.py` per item #2; monitoring: next token migration will require manual Go updates; owning ADR: this ADR, item #2)
  - Test token constants not implemented (severity: low; mitigation: evaluate after observing migration patterns per item #3; monitoring: test coupling persists; owning ADR: this ADR, item #3)
  - Grammar validation test not yet created (severity: medium; mitigation: add `_tests/test_obsolete_tokens.py` per item #4 in next loop; monitoring: obsolete tokens could linger undetected; owning ADR: this ADR, item #4)
  - Pre-commit hook not implemented (severity: low; mitigation: defer until team requests it per item #5; monitoring: developers can commit obsolete tokens without CI feedback; owning ADR: this ADR, item #5)
- next_work:
  - Behaviour: Add Python test to detect obsolete tokens per item #4; Validation: `python3 -m pytest _tests/test_obsolete_tokens.py` passes and detects when obsolete tokens exist in axisConfig; create test that fails when OBSOLETE_TOKENS set contains tokens found in AXIS_KEY_TO_VALUE

## 2026-01-28 — loop 003

- helper_version: helper:v20251223.1
- focus: ADR 0095 Decision section #4 → Add Python test to detect obsolete tokens in axisConfig so removed tokens don't linger undetected (salient task: item #4 from Decision section)
- active_constraint: No automated test verifies that obsolete tokens (from ADR 0091/0092 migrations) are actually removed from `lib/axisConfig.py`, allowing legacy tokens to persist and cause confusion during future migrations (validated via attempting to run `python3 -m unittest _tests.test_obsolete_tokens` which should fail with module not found)
- expected_value:
  | Factor | Value | Rationale |
  | --- | --- | --- |
  | Impact | Medium | Prevents obsolete tokens from lingering but doesn't block current functionality |
  | Probability | High | Test is deterministic and directly checks axisConfig dictionary |
  | Time Sensitivity | Medium | Useful for future migrations but no immediate deadline |
  | Uncertainty note | Low | OBSOLETE_TOKENS set can be populated from ADR 0091/0092 migration history |
- validation_targets:
  - `python3 -m unittest _tests.test_obsolete_tokens -v` (verifies obsolete tokens are not in axisConfig)
- evidence:
  - red | 2026-01-28T23:50:00Z | exit 1 | python3 -m unittest _tests.test_obsolete_tokens -v
    - helper:diff-snapshot=0 files changed
    - behaviour: obsolete token test fails with "Failed to import test module" proving file does not exist | inline
  - green | 2026-01-28T23:52:00Z | exit 0 | python3 -m unittest _tests.test_obsolete_tokens -v
    - helper:diff-snapshot=_tests/test_obsolete_tokens.py | 50 ++++++++++++++++++++++++++++++++++++++++++++++++++
    - behaviour: obsolete token test passes, verifying no obsolete tokens from ADR 0091/0092 exist in axisConfig | inline
  - removal | 2026-01-28T23:53:00Z | exit 1 | rm _tests/test_obsolete_tokens.py && python3 -m unittest _tests.test_obsolete_tokens -v
    - helper:diff-snapshot=0 files changed
    - behaviour: test collection fails again after deletion proving test file was required | inline
- rollback_plan: `rm _tests/test_obsolete_tokens.py`; rerun unittest to observe "Failed to import test module" failure
- delta_summary: helper:diff-snapshot=_tests/test_obsolete_tokens.py | 50 insertions(+) — created unittest test to verify obsolete tokens from ADR 0091/0092 (todo, focus, system, relations, steps, announce, coach_junior) are not present in AXIS_KEY_TO_VALUE, preventing legacy vocabulary from persisting after migrations
- loops_remaining_forecast: 2 loops remaining (item #2 Go migration support, final ADR status update) — high confidence that obsolete token detection works as specified
- residual_constraints:
  - Go test migration support remains manual (severity: medium; mitigation: extend `migrate-test-tokens.py` per item #2 in next loop; monitoring: next token migration will require manual Go updates; owning ADR: this ADR, item #2)
  - Test token constants not implemented (severity: low; mitigation: defer per item #3 unless migration patterns show clear benefit; monitoring: test coupling persists; owning ADR: this ADR, item #3)
  - Pre-commit hook not implemented (severity: low; mitigation: defer until team requests it per item #5; monitoring: developers can commit obsolete tokens without local feedback; owning ADR: this ADR, item #5)
  - OBSOLETE_TOKENS set requires manual updates for future migrations (severity: low; mitigation: document in test comments that set should be updated when tokens are removed; monitoring: future migrations may add to this set; owning ADR: this ADR, maintenance of item #4)
- next_work:
  - Behaviour: Extend migrate-test-tokens.py to support Go files per item #2; Validation: `python scripts/tools/migrate-test-tokens.py --go --dry-run` executes successfully and shows Go test files in scope; verify script can process internal/barcli/*_test.go files
  - Behaviour: Update ADR 0095 status to reflect completed items; Validation: ADR document clearly indicates items #1 and #4 are complete, items #2/#3/#5 remain proposed
