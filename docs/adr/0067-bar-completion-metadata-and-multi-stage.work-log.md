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
