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
