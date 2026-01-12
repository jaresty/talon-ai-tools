# ADR 0075 — CLI Coordination Layer Refactor work log

## loop-001 | helper:v20251223.1 | 2026-01-11

focus: ADR 0075 Refactor Plan step 1 → characterize current CLI parsing (`parseArgs`/`Run`) before extraction (salient task 1).

active_constraint: `go test ./internal/barcli` lacked targeted coverage; running the new `TestParseArgsBuildCommand` skeleton failed with `track missing parseArgs coverage`, proving parseArgs behaviour was unguarded.

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Locking behaviour lets us refactor without regressions |
| Probability | High | Unit tests directly exercise parseArgs/Run flags |
| Time Sensitivity | Medium | Needed before moving logic into a new coordination package |
| Uncertainty note | Low | parseArgs behaviour is deterministic |

validation_targets:
- `go test ./internal/barcli -run TestParseArgsBuildCommand`
- `go test ./internal/barcli -run TestParseArgs`

evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-001.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/barcli/app_parse_test.go`; rerun `go test ./internal/barcli -run TestParseArgs` to confirm the characterization harness disappears if reverted.

delta_summary: helper:diff-snapshot=internal/barcli/app_parse_test.go — added CLI characterization tests covering build command flags, env deduplication, and failure paths.

loops_remaining_forecast: 4 loops (extract token override helpers, introduce Config package, migrate runTUI wrapper, regenerate grammar alignment). Confidence: medium.

residual_constraints:
- Medium — Token override helpers still live in `build.go`; mitigation: extract shared package next loop, validated via unit tests (`go test ./internal/barcli`).

next_work:
- Behaviour: Extract token override helpers into a shared package with unit coverage (validation: `go test ./internal/barcli`, expect harness).

assets:
- Test file: `internal/barcli/app_parse_test.go`
- Evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-001.md`

## loop-002 | helper:v20251223.1 | 2026-01-11

focus: ADR 0075 Refactor Plan step 2 → extract token override helpers into a shared package used by buildState (salient task 2).

active_constraint: Running `go test ./internal/barcli -run TestApplyOverrideToken_NotYetExtracted` failed with `token override helper extraction pending`, demonstrating override behaviour lacked coverage and could not be reused.

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Shared override helpers reduce churn across build/TUI pathways |
| Probability | High | Extracting logic and adding tests directly relieves the hotspot |
| Time Sensitivity | Medium | Needed before migrating Run/runTUI to the coordination package |
| Uncertainty note | Low | Overrides follow deterministic grammar rules |

validation_targets:
- `go test ./internal/barcli -run TestApplyOverrideToken_NotYetExtracted`
- `go test ./internal/barcli -run TestApplyOverrideToken`
- `go test ./...`

evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-002.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/barcli/build.go internal/barcli/build_test.go internal/barcli/tokens`; rerun `go test ./internal/barcli -run TestApplyOverrideToken` to watch the helper extraction failure return.

delta_summary: helper:diff-snapshot=internal/barcli/build.go, internal/barcli/build_test.go, internal/barcli/tokens/overrides.go — extracted override logic into `tokens` package, wrapped buildState with context adapters, and added unit tests for scope dedupe, unknown keys, and persona conflicts.

loops_remaining_forecast: 3 loops (introduce CLI config package, decouple runTUI wiring, regenerate grammar alignment/expect updates). Confidence: medium.

residual_constraints:
- Medium — CLI configuration still lives in `app.go`; mitigation: introduce typed config package next loop (validation: targeted unit tests + go test).
- Medium — TUI wiring still depends on CLI state; mitigation: decouple runTUI interface after config extraction.

next_work:
- Behaviour: Introduce CLI configuration package and migrate `Run`/`parseArgs` callers (validation: go test ./internal/barcli, expect harness).

assets:
- Helper package: `internal/barcli/tokens/`
- Updated build logic: `internal/barcli/build.go`
- Tests: `internal/barcli/build_test.go`
- Evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-002.md`
