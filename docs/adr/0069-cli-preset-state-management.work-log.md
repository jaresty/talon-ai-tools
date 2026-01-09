## 2026-01-09 — loop 001
- helper_version: helper:v20251223.1
- focus: Decision § update — clarify preset subject redaction requirement before implementation
- active_constraint: ADR 0069 omitted guidance that presets must strip prior subjects, leaving contributors free to persist sensitive text and blocking the subject-redaction mitigation planned for CLI presets.
- validation_targets:
  - git diff --no-index --stat /dev/null docs/adr/0069-cli-preset-state-management.md
  - git diff --no-index /dev/null docs/adr/0069-cli-preset-state-management.md
- evidence:
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-001.md#loop-001-green--helper-diff-snapshot-git-diff----no-index----stat--devnull-docs-adr-0069-cli-preset-state-management.md
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-001.md#loop-001-green--helper-diff-snapshot-git-diff----no-index--devnull-docs-adr-0069-cli-preset-state-management.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0069-cli-preset-state-management.md docs/adr/0069-cli-preset-state-management.work-log.md docs/adr/evidence/0069-cli-preset-state-management/loop-001.md`
- delta_summary: helper:diff-snapshot=docs/adr/0069-cli-preset-state-management.md | 46 insertions(+) — recorded subject redaction in preset save/use flow so downstream code work inherits the guardrail.
- loops_remaining_forecast: 4 loops (implement persistence changes, extend CLI output, add guardrail tests, document operational safeguards) — medium confidence pending state helper analysis.
- residual_constraints:
  - Persistence helpers still include subjects in `storedBuild`/`presetFile`, so saving presets would leak stale context if shipped today (severity: high; mitigation: refactor state serialization to drop subject fields; monitoring: go test ./internal/barcli).
- next_work:
  - Behaviour: Refactor `saveLastBuild`/`savePreset` to redact subjects and adjust CLI outputs (validation via go test ./internal/barcli).

## 2026-01-09 — loop 002
- helper_version: helper:v20251223.1
- focus: Decision § implementation — persist token-only preset state and surface subject omissions in CLI outputs
- active_constraint: State persistence still embedded subject/plain-text content into `last_build.json`, violating ADR 0069 and risking leaked prompts; guardrails lacked tests ensuring cached results drop subject text.
- validation_targets:
  - go test ./internal/barcli
- evidence:
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-002.md#loop-002-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-002.md#loop-002-green--helper-rerun-go-test-.-internal-barcli
- rollback_plan: `git restore --source=HEAD -- internal/barcli/app.go internal/barcli/build.go internal/barcli/completion.go internal/barcli/state.go internal/barcli/state_test.go internal/barcli/preset_render.go docs/adr/0069-cli-preset-state-management.md docs/adr/0069-cli-preset-state-management.work-log.md docs/adr/evidence/0069-cli-preset-state-management/loop-002.md`
- delta_summary: helper:diff-snapshot=token-only preset caching diff landed — removed subject/plain-text persistence, refreshed CLI messaging, added tests/completion helpers.
- loops_remaining_forecast: 2 loops (update public docs + integration flow, regenerate preset fixtures) — medium confidence pending doc review bandwidth.
- residual_constraints:
  - README and user guide still describe presets as caching subjects (severity: medium; mitigation: update docs & release notes to highlight token-only caches; monitoring: `python3 -m pytest _tests/test_generate_readme_axis_lists.py`).
- next_work:
  - Behaviour: Document token-only preset behaviour across README/help surfaces and refresh CLI integration snapshots (validation via `python3 -m pytest _tests/test_generate_readme_axis_lists.py`).

## 2026-01-09 — loop 003
- helper_version: helper:v20251223.1
- focus: Decision § documentation — update README to reflect token-only CLI preset caching and state controls
- active_constraint: Public docs still implied presets reused prior subject text, contradicting ADR 0069 and risking leakage for CLI-only users following README guidance.
- validation_targets:
  - python3 -m unittest _tests.test_readme_portable_cli
- evidence:
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-003.md#loop-003-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-003.md#loop-003-green--helper-rerun-python3--m-unittest-_tests-test_readme_portable_cli
- rollback_plan: `git restore --source=HEAD -- README.md docs/adr/0069-cli-preset-state-management.work-log.md docs/adr/evidence/0069-cli-preset-state-management/loop-003.md`
- delta_summary: helper:diff-snapshot=readme.md | 16 +++++++++++++--- — added CLI preset commands, warned that subjects are never stored, and documented config toggles.
- loops_remaining_forecast: 1 loop (refresh integration examples or CLI snapshots if needed) — medium confidence pending review of help hub surfaces.
- residual_constraints:
  - Help hub quickstart still references legacy preset behaviour (severity: low; mitigation: audit help hub copy during next documentation sweep; monitoring: manual check of `model help hub`).
- next_work:
  - Behaviour: Review help hub and quickstart docs for preset references and update as necessary (validation via curated manual help hub capture).

## 2026-01-09 — loop 004
- helper_version: helper:v20251223.1
- focus: Decision § implementation — have `bar preset use` rebuild recipes with saved tokens and fresh subject input
- active_constraint: CLI preset reuse still required manual piping into `bar build`, breaking parity with `bar build` command and discouraging quick reuse of recipes on new subjects.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m unittest _tests.test_readme_portable_cli
- evidence:
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-004.md#loop-004-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-004.md#loop-004-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-004.md#loop-004-green--helper-rerun-python3--m-unittest-_tests-test_readme_portable_cli
- rollback_plan: `git restore --source=HEAD -- internal/barcli/app.go internal/barcli/app_test.go internal/barcli/preset_render.go internal/barcli/state_test.go README.md docs/adr/0069-cli-preset-state-management.md docs/adr/0069-cli-preset-state-management.work-log.md docs/adr/evidence/0069-cli-preset-state-management/loop-004.md`
- delta_summary: helper:diff-snapshot=6 files changed, 134 insertions(+), 32 deletions(-) — taught `bar preset use` to call `Build` with saved tokens, accept `--prompt`/STDIN like `bar build`, refreshed tests/docs, and clarified preset guidance.
- loops_remaining_forecast: 1 loop (audit help hub quickstart references) — medium confidence pending manual doc sweep.
- residual_constraints:
  - Help hub copy may still reference legacy preset behaviour (severity: low; mitigation: include in upcoming documentation sweep; monitoring: manual `model help hub` check).
- next_work:
  - Behaviour: Review help hub and quickstart docs for preset references and update as necessary (validation via curated manual help hub capture).

## 2026-01-09 — loop 005
- helper_version: helper:v20251223.1
- focus: Decision § documentation — align CLI README and docs quickstart guidance with token-only preset reuse
- active_constraint: Public-facing CLI documentation (README and docs quickstart page) still implied piping presets back into `bar build`, leaving CLI users without guidance that `bar preset use` now rebuilds recipes directly when supplied fresh subject text.
- validation_targets:
  - go test ./internal/barcli
  - python3 -m unittest _tests.test_readme_portable_cli
- evidence:
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-005.md#loop-005-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-005.md#loop-005-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0069-cli-preset-state-management/loop-005.md#loop-005-green--helper-rerun-python3--m-unittest-_tests-test_readme_portable_cli
- rollback_plan: `git restore --source=HEAD -- internal/barcli/app.go readme.md .docs/src/content/docs/guides/quickstart.mdx docs/adr/0069-cli-preset-state-management.work-log.md docs/adr/evidence/0069-cli-preset-state-management/loop-005.md`
- delta_summary: helper:diff-snapshot=3 files changed, 21 insertions(+), 3 deletions(-) — refreshed CLI help text, README, and docs quickstart page to state that presets rebuild recipes when provided new prompts via --prompt/--input/STDIN.
- loops_remaining_forecast: 0 loops — CLI help text and documentation now reflect token-only preset reuse.
- residual_constraints:
  - None; Talon runtime surfaces remain unchanged in this slice.
- next_work:
  - Behaviour: None scheduled; reopen if Talon help hub copy needs a parallel update.
