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

## 2026-01-08 — loop 009
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — remove personal attribution from follow-up guidance
- active_constraint: ADR follow-up referenced an individual maintainer, conflicting with documentation policy against naming people directly.
- validation_targets:
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-009.md#loop-009-green--helper-rerun-python3--m-pytest-_tests-test_generate_axis_cheatsheet.py
- rollback_plan: `git restore --source=HEAD -- docs/adr/0068-grammar-token-normalization-for-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-009.md`
- delta_summary: helper:diff-snapshot=1 file changed, 3 insertions(+) — rewrote follow-up guidance to assign ownership to the maintainer group instead of a named individual.
- loops_remaining_forecast: 1 loop — schedule fallback removal execution once owner/release target are confirmed.
- residual_constraints:
  - Label fallback removal remains unscheduled (severity: medium; mitigation: capture owner + release milestone in future loop; monitoring: python3 -m pytest _tests/test_generate_axis_cheatsheet.py).
- next_work:
  - Behaviour: Assign fallback removal owner + release milestone and update work-log (validation via python3 -m pytest _tests/test_generate_axis_cheatsheet.py).

## 2026-01-08 — loop 010
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — capture fallback removal tracking issue
- active_constraint: Follow-up guidance referenced work but lacked a concrete tracking artifact, leaving ownership ambiguous.
- validation_targets:
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-010.md#loop-010-green--helper-rerun-python3--m-pytest-_tests-test_generate_axis_cheatsheet.py
- rollback_plan: `git restore --source=HEAD -- docs/adr/0068-grammar-token-normalization-for-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-010.md`
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+) — linked the maintainer-owned fallback removal to issue `BAR-142` in the ADR follow-up.
- loops_remaining_forecast: 1 loop — schedule fallback removal execution once release target is finalized.
- residual_constraints:
  - Label fallback removal awaits milestone scheduling (severity: medium; mitigation: use BAR-142 to capture release target; monitoring: python3 -m pytest _tests/test_generate_axis_cheatsheet.py).
- next_work:
  - Behaviour: Update work-log with milestone decision once BAR-142 is resolved (validation via python3 -m pytest _tests/test_generate_axis_cheatsheet.py).

## 2026-01-08 — loop 011
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — record milestone confirmation for fallback removal
- active_constraint: ADR follow-up cited `BAR-142` but lacked the confirmed release milestone, leaving the deprecation timeline ambiguous.
- validation_targets:
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-011.md#loop-011-green--helper-rerun-python3--m-pytest-_tests-test_generate_axis_cheatsheet.py
- rollback_plan: `git restore --source=HEAD -- docs/adr/0068-grammar-token-normalization-for-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-011.md`
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+) — documented the `bar v0.2.0` milestone date referenced in release planning.
- loops_remaining_forecast: 1 loop — update work-log once BAR-142 closes with the final sunset checklist.
- residual_constraints:
  - Label fallback removal awaiting BAR-142 closure (severity: medium; mitigation: monitor release checklist; validation: python3 -m pytest _tests/test_generate_axis_cheatsheet.py).
- next_work:
  - Behaviour: Capture BAR-142 closure details and sunset checklist in work-log (validation via python3 -m pytest _tests/test_generate_axis_cheatsheet.py).

## 2026-01-08 — loop 012
- helper_version: helper:v20251223.1
- focus: Decision § implementation — remove label-input fallback and make slug usage mandatory
- active_constraint: Despite slug exports and warnings, the CLI still accepted label-form tokens, keeping scripts ambiguous and blocking full migration to slug-only behaviour.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m pytest _tests/test_bar_completion_cli.py
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-012.md#loop-012-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-012.md#loop-012-green--helper-rerun-python3--m-pytest-_tests-test_bar_completion_cli.py
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-012.md#loop-012-green--helper-rerun-python3--m-pytest-_tests-test_generate_axis_cheatsheet.py
- rollback_plan: `git restore --source=HEAD -- internal/barcli/build.go internal/barcli/app.go internal/barcli/app_test.go internal/barcli/build_test.go readme.md docs/adr/0065-portable-prompt-grammar-cli.md docs/adr/0068-grammar-token-normalization-for-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-012.md`
- delta_summary: helper:diff-snapshot=8 files changed, 89 insertions(+), 76 deletions(-) — enforced slug-only parsing in the CLI, updated guardrail tests, and refreshed README/ADR guidance to reflect immediate rejection of label inputs.
- loops_remaining_forecast: 0 loops — slug normalization contract is complete; monitoring continues via existing guardrails.
- residual_constraints:
  - None — label-form input paths are removed and scripts must use slugs.
- next_work:
  - None.

## 2026-01-08 — loop 013
- helper_version: helper:v20251223.1
- focus: Decision § documentation — clarify CLI help text for slug-only tokens
- active_constraint: CLI help still referenced generic slug usage without explaining that single-word tokens remain unchanged, risking confusion for operators verifying override inputs.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m pytest _tests/test_bar_completion_cli.py
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-013.md#loop-013-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-013.md#loop-013-green--helper-rerun-python3--m-pytest-_tests-test_bar_completion_cli.py
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-013.md#loop-013-green--helper-rerun-python3--m-pytest-_tests-test_generate_axis_cheatsheet.py
- rollback_plan: `git restore --source=HEAD -- internal/barcli/app.go docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-013.md`
- delta_summary: helper:diff-snapshot=2 files changed, 11 insertions(+), 8 deletions(-) — clarified help text to distinguish single-word tokens from multi-word slugs.
- loops_remaining_forecast: 0 loops — slug-only behaviour and documentation are aligned.
- residual_constraints:
  - None — CLI messaging reflects slug-only expectations.
- next_work:
  - None.

## 2026-01-08 — loop 014
- helper_version: helper:v20251223.1
- focus: Decision § validation — ensure completions keep single-word shorthand tokens unslugged
- active_constraint: Without explicit coverage, shortcut suggestions could regress to slugged values, making the CLI help text inconsistent with completions.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m pytest _tests/test_bar_completion_cli.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-014.md#loop-014-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-014.md#loop-014-green--helper-rerun-python3--m-pytest-_tests-test_bar_completion_cli.py
- rollback_plan: `git restore --source=HEAD -- internal/barcli/completion_test.go docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-014.md`
- delta_summary: helper:diff-snapshot=1 file changed, 8 insertions(+), 1 deletion(-) — added regression coverage preventing slugged override values from leaking into shorthand completion suggestions.
- loops_remaining_forecast: 0 loops — slug-only behaviour is fully guarded by tests and documentation.
- residual_constraints:
  - None — completions and help messaging remain consistent.
- next_work:
  - None.

## 2026-01-08 — loop 015
- helper_version: helper:v20251223.1
- focus: Decision § implementation — accept canonical key=value overrides alongside slug inputs
- active_constraint: CLI overrides required slugified forms (`scope-focus`), confusing operators accustomed to `scope=focus` and causing unnecessary build failures.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m pytest _tests/test_bar_completion_cli.py
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-015.md#loop-015-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-015.md#loop-015-green--helper-rerun-python3--m-pytest-_tests-test_bar_completion_cli.py
- rollback_plan: `git restore --source=HEAD -- internal/barcli/build.go internal/barcli/build_test.go internal/barcli/completion.go internal/barcli/completion_test.go docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-015.md`
- delta_summary: helper:diff-snapshot=4 files changed, 53 insertions(+), 9 deletions(-) — relaxed slug enforcement for canonical overrides, adjusted completion suggestions, and added regression coverage for both build and completion flows.
- loops_remaining_forecast: 0 loops — slug-only behaviour and canonical override support are aligned and covered by tests.
- residual_constraints:
  - None — CLI override ergonomics now match documentation and completions.
- next_work:
  - None.

## 2026-01-08 — loop 016
- helper_version: helper:v20251223.1
- focus: Decision § documentation — clarify ADR consequences around canonical overrides
- active_constraint: ADR-0068 still implied that all inputs must use slug forms, overlooking the newly restored canonical override support and risking confusion for operators.
- validation_targets:
  - (doc-only) referenced loop-015 green evidence for behaviour enforcement.
- evidence:
  - doc-only: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-016.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0068-grammar-token-normalization-for-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-016.md`
- delta_summary: helper:diff-snapshot=1 file changed, 2 insertions(+), 2 deletions(-) — updated ADR decision/consequence sections to note canonical overrides remain valid while shorthand multi-word tokens use slugs.
- loops_remaining_forecast: 0 loops — documentation now matches the enforced CLI behaviour.
- residual_constraints:
  - None — canonical override support is fully documented.
- next_work:
  - None.

## 2026-01-08 — loop 017
- helper_version: helper:v20251223.1
- focus: Decision § documentation — align CLI help/README with canonical override support
- active_constraint: CLI help text and README note still implied slug-only inputs, ignoring that canonical key=value overrides remain valid, which could mislead operators and script authors.
- validation_targets:
  - go test ./internal/barcli
- evidence:
  - green: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-017.md#loop-017-green--helper-rerun-go-test-.-internal-barcli
- rollback_plan: `git restore --source=HEAD -- internal/barcli/app.go readme.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-017.md`
- delta_summary: helper:diff-snapshot=2 files changed, 5 insertions(+), 4 deletions(-) — refreshed CLI help text and README guidance to mention canonical overrides while reiterating slug requirements for shorthand tokens.
- loops_remaining_forecast: 0 loops — user-facing guidance now reflects current behaviour.
- residual_constraints:
  - None — documentation and help output align with slug-only shorthand plus canonical override support.
- next_work:
  - None.

## 2026-01-08 — loop 018
- helper_version: helper:v20251223.1
- focus: Decision § documentation — clarify multi-word override examples in ADR consequences
- active_constraint: Consequences section still referenced multi-word overrides generically, which could be misread as allowing space-delimited values; we need to explicitly reference the slugged form.
- validation_targets:
  - (doc-only) referenced loop-015 behaviour evidence.
- evidence:
  - doc-only: docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-018.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0068-grammar-token-normalization-for-cli.md docs/adr/0068-grammar-token-normalization-for-cli.work-log.md docs/adr/evidence/0068-grammar-token-normalization-for-cli/loop-018.md`
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+), 1 deletion(-) — clarified that multi-word override values continue to use dashed slugs such as `directional=fly-rog`.
- loops_remaining_forecast: 0 loops — documentation now makes slug requirements for overrides explicit.
- residual_constraints:
  - None — guidance matches CLI behaviour.
- next_work:
  - None.
