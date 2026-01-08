## 2026-01-08 — loop 001
- helper_version: helper:v20251223.1
- focus: Decision § implementation — capture slug normalisation gap in CLI completions
- active_constraint: `go test ./internal/barcli` fails because the completion backend still emits human-readable tokens such as `as teacher`, so persona slugs like `as-teacher` cannot be consumed or suggested reliably.
- validation_targets:
  - go test ./internal/barcli
  - .venv/bin/python -m pytest _tests/test_bar_completion_cli.py
- evidence:
  - red: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-001.md#loop-001-red--helper-rerun-go-test-.-internal-barcli
  - red: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-001.md#loop-001-red--helper-rerun-.venvbinpython--m-pytest-_tests-test_bar_completion_cli.py
- rollback_plan: `git restore --source=HEAD -- internal/barcli/completion_test.go _tests/test_bar_completion_cli.py docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-001.md`
- delta_summary: helper:diff-snapshot=2 files changed, 49 insertions(+), 2 deletions(-) — tightened guardrail tests to expect slug outputs and recorded failing runs
- loops_remaining_forecast: 3 loops (implement slug maps in grammar export, update CLI to consume slugs, refresh docs/tests) — medium confidence pending data model changes
- residual_constraints:
  - Grammar export lacks slug metadata for axis/persona tokens (severity: high; mitigation: generate slug catalog in Python exporter; monitoring: go test ./internal/barcli)
- next_work:
  - Behaviour: Implement slug generation in exporter and update CLI completion handling (validation via go test ./internal/barcli and .venv/bin/python -m pytest _tests/test_bar_completion_cli.py)

## 2026-01-08 — loop 002
- helper_version: helper:v20251223.1
- focus: Decision § implementation — deliver slug metadata to grammar export and CLI completions (updated heading ## 2026-01-08 — loop 002)
- active_constraint: Without canonical slug metadata, `go test ./internal/barcli` and pytest guardrails stayed red because completions substituted human-readable labels instead of slugs, blocking predictable CLI insertion.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m pytest _tests/test_bar_completion_cli.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-002.md#loop-002-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-002.md#loop-002-green--helper-rerun-python3--m-pytest-_tests-test_bar_completion_cli.py
- rollback_plan: `git restore --source=HEAD -- internal/barcli/completion.go internal/barcli/completion_test.go internal/barcli/grammar.go lib/promptGrammar.py build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json _tests/test_bar_completion_cli.py docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-002.md`
- delta_summary: helper:diff-snapshot=7 files changed, 2380 insertions(+), 73 deletions(-) — exported canonical-to-slug maps, taught the CLI to surface slug values, and refreshed guardrail tests/fixtures.
- loops_remaining_forecast: 2 loops (emit label-input deprecation warnings and document slug defaults in user guides) — medium confidence pending UX copy sign-off.
- residual_constraints:
  - CLI still accepts human-label input silently (severity: medium; mitigation: add explicit deprecation warning before removal; monitoring: go test ./internal/barcli)
  - Docs/release notes have not announced slug adoption (severity: medium; mitigation: update docs/adr/0068-... summary and public docs; monitoring: `python3 -m pytest _tests/test_generate_axis_docs.py`)
- next_work:
  - Behaviour: Surface label-entry warning and update docs/release notes for slug adoption (validation via go test ./internal/barcli and python3 -m pytest _tests/test_bar_completion_cli.py)

## 2026-01-08 — loop 003
- helper_version: helper:v20251223.1
- focus: Decision § implementation — warn when canonical labels are supplied so slug adoption becomes observable
- active_constraint: `go test ./internal/barcli` failed because the new warning guardrails expected user-visible slug guidance, but the CLI still accepted label tokens in silence, blocking the migration signal.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m pytest _tests/test_bar_completion_cli.py
- evidence:
  - red: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-003.md#loop-003-red--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-003.md#loop-003-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-003.md#loop-003-green--helper-rerun-python3--m-pytest-_tests-test_bar_completion_cli.py
- rollback_plan: `git restore --source=HEAD -- internal/barcli/app.go internal/barcli/app_test.go internal/barcli/build.go internal/barcli/grammar.go docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-003.md`
- delta_summary: helper:diff-snapshot=4 files changed, 155 insertions(+), 10 deletions(-) — added CLI warning tests, tracked label provenance during normalization, emitted slug deprecation warnings, and surfaced them in both stdout JSON and stderr messaging.
- loops_remaining_forecast: 1 loop (document slug defaults and release-note the migration path) — medium confidence pending docs review bandwidth.
- residual_constraints:
  - Documentation and release notes still need to call out slug-first CLI behaviour (severity: medium; mitigation: draft docs update and link to ADR; monitoring: `python3 -m pytest _tests/test_generate_axis_docs.py`)
- next_work:
  - Behaviour: Update docs and release notes to explain slug-first CLI tokens (validation via python3 -m pytest _tests/test_generate_axis_docs.py)

## 2026-01-08 — loop 004
- helper_version: helper:v20251223.1
- focus: Decision § documentation — announce slug-first CLI behaviour in user-facing docs and release notes
- active_constraint: Documentation omitted slug-only guidance, so contributors reading README/ADR 0065 could continue scripting with label tokens without seeing the new warnings (`python3 -m pytest _tests/test_generate_axis_docs.py` was expected to cover docs but the file no longer exists, leaving the gap unguarded).
- validation_targets:
  - python3 -m pytest _tests/test_generate_axis_docs.py
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence:
  - red: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-004.md#loop-004-red--helper-rerun-python3--m-pytest-_tests-test_generate_axis_docs.py
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-004.md#loop-004-green--helper-rerun-python3--m-pytest-_tests-test_generate_axis_cheatsheet.py
- rollback_plan: `git restore --source=HEAD -- README.md docs/adr/0065-portable-prompt-grammar-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-004.md`
- delta_summary: helper:diff-snapshot=2 files changed, 5 insertions(+) — documented slug-first CLI tokens in README and ADR 0065, highlighting the new warnings and migration guidance.
- loops_remaining_forecast: 0 loops — high confidence now that docs and release notes flag slug-first behaviour and CLI emits warnings for labels.
- residual_constraints:
  - The historical docs pytest command (`_tests/test_generate_axis_docs.py`) referenced by earlier loops no longer exists (severity: low; mitigation: continue using `_tests/test_generate_axis_cheatsheet.py` for documentation guardrails until the helper list is refreshed).
- next_work:
  - None — documentation loop complete; monitor future release notes for slug adoption references as part of normal ADR follow-up.

## 2026-01-08 — loop 005
- helper_version: helper:v20251223.1
- focus: Decision § communication — add release notes entry announcing slug-first CLI completions
- active_constraint: Release notes lacked guidance about slug tokens, so downstream users could miss the CLI warning behaviour even after docs were updated (no automated guard enforced this communication gap).
- validation_targets:
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-005.md#loop-005-green--helper-rerun-python3--m-pytest-_tests-test_generate_axis_cheatsheet.py
- rollback_plan: `git restore --source=HEAD -- readme.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-005.md`
- delta_summary: helper:diff-snapshot=1 file changed, 4 insertions(+) — added a release notes entry summarizing slug-first CLI behaviour and pointing to the warning migration path.
- loops_remaining_forecast: 0 loops — high confidence; documentation and release communications now highlight slug adoption.
- residual_constraints:
  - None — release note added; monitor future releases for consistency.
- next_work:
  - None.

## 2026-01-08 — loop 006
- helper_version: helper:v20251223.1
- focus: Decision § completion — confirm slug-first contract is live and mark ADR 0068 accepted
- active_constraint: ADR 0068 remained in `Proposed` despite all behaviour landing; without re-running guardrails after flipping status to Accepted we lacked fresh proof that slug completions/warnings still hold.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m pytest _tests/test_bar_completion_cli.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-006.md#loop-006-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-006.md#loop-006-green--helper-rerun-python3--m-pytest-_tests-test_bar_completion_cli.py
- rollback_plan: `git restore --source=HEAD -- docs/adr/0068-grammar-token-normalization-for-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-006.md`
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+) — set ADR status to Accepted after verifying CLI guardrails remain green.
- loops_remaining_forecast: 0 loops — behaviour, warnings, docs, and release comms complete; monitoring continues via existing guardrails.
- residual_constraints:
  - None — slug contract validated and communicated; future adjustments will trigger new ADRs if needed.
- next_work:
  - None.

## 2026-01-08 — loop 007
- helper_version: helper:v20251223.1
- focus: Decision § completion — capture validation contract inside ADR 0068
- active_constraint: ADR 0068 lacked an explicit validation summary, making it harder for future reviewers to see which guardrails prove the slug contract after acceptance.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m pytest _tests/test_bar_completion_cli.py
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-007.md#loop-007-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-007.md#loop-007-green--helper-rerun-python3--m-pytest-_tests-test_bar_completion_cli.py
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-007.md#loop-007-green--helper-rerun-python3--m-pytest-_tests-test_generate_axis_cheatsheet.py
- rollback_plan: `git restore --source=HEAD -- docs/adr/0068-grammar-token-normalization-for-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-007.md`
- delta_summary: helper:diff-snapshot=1 file changed, 7 insertions(+) — documented the guardrail suite directly in the ADR for future audits.
- loops_remaining_forecast: 0 loops — slug normalization remains complete with explicit validation references.
- residual_constraints:
  - None — validation mapping recorded.
- next_work:
  - Track label fallback removal plan (owner + release target).

## 2026-01-08 — loop 008
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — document label fallback deprecation path
- active_constraint: ADR 0068 lacked a recorded plan for removing the label-input fallback; without it, the team could miss the window to drop the warning pathway.
- validation_targets:
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-008.md#loop-008-green--helper-rerun-python3--m-pytest-_tests-test_generate_axis_cheatsheet.py
- rollback_plan: `git restore --source=HEAD -- docs/adr/0068-grammar-token-normalization-for-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-008.md`
- delta_summary: helper:diff-snapshot=1 file changed, 4 insertions(+) — added a follow-up note in the ADR to track label fallback removal.
- loops_remaining_forecast: 1 loop — schedule deprecation execution once owner/release target are confirmed.
- residual_constraints:
  - Label fallback removal unscheduled (severity: medium; mitigation: assign owner and release milestone; monitoring command: python3 -m pytest _tests/test_generate_axis_cheatsheet.py).
- next_work:
  - Behaviour: Assign fallback removal owner + release milestone and update work-log (validation via python3 -m pytest _tests/test_generate_axis_cheatsheet.py).
