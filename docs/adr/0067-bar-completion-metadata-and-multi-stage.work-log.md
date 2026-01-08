# 0067 — Enrich `bar` CLI completions with multi-stage context (work log)

## 2026-01-08 — loop 001
- helper_version: helper:v20251223.1
- focus: Decision § baseline evidence — capture current completion behaviour for multi-stage + metadata gap
- active_constraint: `go run ./cmd/bar completion fish` emits a script that forwards only a single staged context and provides no metadata, so shells cannot show parallel axis suggestions or describe tokens.
- validation_targets:
  - go run ./cmd/bar completion fish
- evidence:
  - red: docs/adr/evidence/0067-bar-completion-metadata-and-multi-stage/loop-001.md#loop-001-red--helper-rerun-go-run-.-cmd-bar-completion-fish
- rollback_plan: `git restore --source=HEAD -- docs/adr/0067-bar-completion-metadata-and-multi-stage.work-log.md docs/adr/evidence/0067-bar-completion-metadata-and-multi-stage/loop-001.md`
- delta_summary: helper:diff-snapshot=2 files changed, 37 insertions(+) — recorded baseline completion output and logged active constraint
- loops_remaining_forecast: 2 loops (design metadata payload; implement backend & shell updates) — medium confidence pending solution design
- residual_constraints:
  - Shell scripts and backend still return string-only suggestions; future loops must design metadata schema (severity: high; mitigation: draft completion response structure; owning ADR 0067 Decision)
- next_work:
  - Behaviour: Design completion metadata schema and multi-stage response format (validation via new completion unit tests)

## 2026-01-08 — loop 002
- helper_version: helper:v20251223.1
- focus: Decision § schema design — formalise multi-stage availability order and metadata contract for completion suggestions
- active_constraint: Without a documented schema, we cannot evolve the completion engine; the ADR needed explicit staging and payload definitions before implementation can proceed.
- validation_targets:
  - *(design-only loop; no executable validation)*
- evidence:
  - green (design): docs/adr/0067-bar-completion-metadata-and-multi-stage.md#multi-stage-availability-model
  - green (design): docs/adr/0067-bar-completion-metadata-and-multi-stage.md#metadata-contract
- rollback_plan: `git restore --source=HEAD -- docs/adr/0067-bar-completion-metadata-and-multi-stage.md docs/adr/0067-bar-completion-metadata-and-multi-stage.work-log.md`
- delta_summary: helper:diff-snapshot=1 file changed, 34 insertions(+), 0 deletions(-) — captured staging order, payload format, and metadata fields in ADR body
- loops_remaining_forecast: 1 loop (implement backend + shell updates per design) — medium confidence pending coding effort
- residual_constraints:
  - Completion engine still returns plain strings; implementation loop must produce tab-delimited metadata and update scripts (severity: high; mitigation: extend `Complete` API; owning ADR 0067 Decision)
- next_work:
  - Behaviour: Implement completion engine changes and shell formatters per schema (validation via go tests + shell script snapshots)

## 2026-01-08 — loop 003
- helper_version: helper:v20251223.1
- focus: Decision § implementation — enrich completion engine outputs with metadata and multi-stage suggestion sets
- active_constraint: The completion backend emitted plain strings for a single stage, so shells could neither show concurrent scope/method tokens nor surface category metadata.
- validation_targets:
  - go test ./internal/barcli
  - go run ./cmd/bar __complete fish 4 bar build todo full ""
- evidence:
  - green: docs/adr/evidence/0067-bar-completion-metadata-and-multi-stage/loop-003.md#loop-003-green--helper-rerun-go-test-.-internal-barcli
  - green: docs/adr/evidence/0067-bar-completion-metadata-and-multi-stage/loop-003.md#loop-003-green--helper-rerun-go-run-.-cmd-bar-__complete-fish-4-bar-build-todo-full-
- rollback_plan: `git restore --source=HEAD -- internal/barcli/completion.go internal/barcli/completion_test.go docs/adr/0067-bar-completion-metadata-and-multi-stage.md docs/adr/0067-bar-completion-metadata-and-multi-stage.work-log.md docs/adr/evidence/0067-bar-completion-metadata-and-multi-stage/loop-003.md`
- delta_summary: helper:diff-snapshot=4 files changed, 548 insertions(+), 116 deletions(-) — add metadata-aware completion backend, update tests, and enhance shell scripts
- loops_remaining_forecast: 0 loops (ADR ready to integrate with docs/installer updates as needed) — medium confidence pending user validation
- residual_constraints:
  - Update CLI documentation/installer guidance to mention metadata-rich completions (severity: low; mitigation: follow-up docs sweep; owning ADR 0067 Consequences)
- next_work:
  - Behaviour: Refresh docs/help text to reference metadata completions (validation via doc build or review)

## 2026-01-08 — loop 004
- helper_version: helper:v20251223.1
- focus: Decision § documentation — update CLI help and README to describe metadata-rich completions and close ADR 0067
- active_constraint: Without documentation, users would not discover that completions now return category/description metadata; ADR status remained Proposed.
- validation_targets:
  - *(documentation-only loop; no executable validation)*
- evidence:
  - green (docs): internal/barcli/app.go:17
  - green (docs): readme.md:79
  - green (ADR): docs/adr/0067-bar-completion-metadata-and-multi-stage.md:3
- rollback_plan: `git restore --source=HEAD -- internal/barcli/app.go readme.md docs/adr/0067-bar-completion-metadata-and-multi-stage.md docs/adr/0067-bar-completion-metadata-and-multi-stage.work-log.md`
- delta_summary: helper:diff-snapshot=4 files changed, 23 insertions(+), 4 deletions(-) — documented metadata completions, updated help text, and marked ADR completed
- loops_remaining_forecast: 0 loops — ADR closed; continue passive monitoring during release validation
- residual_constraints: *(none — documentation complete)*
- next_work: None (monitor release notes as part of normal process)
