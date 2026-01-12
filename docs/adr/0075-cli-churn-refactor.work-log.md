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

## loop-003 | helper:v20251223.1 | 2026-01-12

focus: ADR 0075 Refactor Plan step 3 → introduce the CLI configuration package and migrate Run/completion/TUI consumers to it (salient task 3).

active_constraint: `go test ./internal/barcli` failed with `undefined: cliOptions` once `cli.Parse` replaced `parseArgs`, demonstrating every entry point still depended on the removed struct until migration completed.

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Centralising parsing lowers churn across Run, completion engine, and TUI flows |
| Probability | High | Unit tests and expect harness lock behaviour in place |
| Time Sensitivity | Medium | Required before finishing ADR 0075 coordination cleanups |
| Uncertainty note | Medium | Multiple call sites needed staged updates, but behaviour is well covered |

validation_targets:
- `go test ./internal/barcli`
- `go test ./...`
- `scripts/tools/run-tui-expect.sh --all`

evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-003.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/barcli/app.go internal/barcli/completion.go internal/barcli/tui.go internal/barcli/app_parse_test.go internal/barcli/cli`; rerun `go test ./internal/barcli` to observe the undefined `cliOptions` failure reappear.

delta_summary: helper:diff-snapshot=internal/barcli/cli/config.go | internal/barcli/app.go | internal/barcli/completion.go | internal/barcli/tui.go | internal/barcli/app_parse_test.go — extracted CLI parsing into `cli.Parse`, rewired Run/completion/TUI/helpers to accept `*cli.Config`, and moved the characterization tests under the new package API.

loops_remaining_forecast: 2 loops (decouple residual TUI wiring, refresh grammar/expect scaffolding). Confidence: medium.

residual_constraints:
- Medium — TUI/preset coordination still handles fixture IO inline; mitigation: fold remaining helpers into the config/TUI boundary next loop.
- Low — Grammar expect assets need a final sweep after coordination refactor; mitigation: regenerate snapshots once wiring settles (`scripts/tools/run-tui-expect.sh --all`).

next_work:
- Behaviour: Finish decoupling TUI helpers from inline CLI plumbing and refresh expect/grammar assets (validation: targeted go tests, expect harness).

assets:
- Typed config: `internal/barcli/cli/config.go`
- Updated entry points: `internal/barcli/app.go`, `internal/barcli/completion.go`, `internal/barcli/tui.go`
- Updated tests: `internal/barcli/app_parse_test.go`
- Evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-003.md`

## loop-004 | helper:v20251223.1 | 2026-01-12

focus: ADR 0075 Refactor Plan step 3 → migrate environment bootstrap into the CLI coordination package so `runTUI` consumes typed config state (salient task 3).

active_constraint: Environment allowlist resolution lived only in `runTUI`, preventing the new `cli.Config` from owning the canonical env bootstrap path (validated via `scripts/tools/run-tui-expect.sh --all`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Consolidating env handling into the coordination package reduces divergent behaviour between CLI and TUI |
| Probability | High | Refactoring the single helper guarantees the TUI path consumes the new method |
| Time Sensitivity | Medium | Needed before finalising remaining coordination cleanups |
| Uncertainty note | Low | Behaviour already characterised by expect harness |

validation_targets:
- `go test ./internal/barcli`
- `go test ./...`
- `scripts/tools/run-tui-expect.sh --all`

evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-004.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/barcli/cli/config.go internal/barcli/tui.go`; rerun `scripts/tools/run-tui-expect.sh --all` to observe the env allowlist regression.

delta_summary: helper:diff-snapshot=internal/barcli/cli/config.go | internal/barcli/tui.go | docs/adr/evidence/0075-cli-churn-refactor/loop-004.md — added `Config.ResolveEnvValues`, rewired `runTUI` to use it, and logged evidence for the consolidated env handling.

loops_remaining_forecast: 1 loop (refresh grammar/embed scaffolding and final ADR cross-links). Confidence: medium.

residual_constraints:
- Medium — TUI fixture snapshot wiring still sits in `runTUI`; mitigation: lift fixture loading into the coordination package next loop, monitored via `scripts/tools/run-tui-expect.sh --all`.
- Low — Grammar/embed assets need a final sweep once coordination stabilises; mitigation: regenerate embeds and expect fixtures (`scripts/tools/run-tui-expect.sh --all`, `go test ./cmd/bar`).

next_work:
- Behaviour: Extract remaining TUI fixture wiring into the coordination package and refresh grammar/embed assets (validation: `go test ./internal/barcli`, `scripts/tools/run-tui-expect.sh --all`).

assets:
- Env helper: `internal/barcli/cli/config.go`
- Updated TUI launcher: `internal/barcli/tui.go`
- Evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-004.md`

## loop-005 | helper:v20251223.1 | 2026-01-12

focus: ADR 0075 Refactor Plan step 4 → confirm embedded grammar assets align with the coordination layer refactor (salient task 4).

active_constraint: Embedded grammar freshness was unverified after the CLI coordination changes; `python3 -m prompts.export` had not been rerun to confirm the mirror under `internal/barcli/embed/prompt-grammar.json` remained canonical.

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | Medium | Ensures CLI/TUI rely on the same canonical grammar payload before continuing coordination cleanups |
| Probability | High | Regeneration deterministically validates the embed |
| Time Sensitivity | Medium | Needed before closing ADR 0075 loops that depend on grammar fixtures |
| Uncertainty note | Low | Command exit status directly reports freshness |

validation_targets:
- `python3 -m prompts.export`
- `go test ./internal/barcli`
- `go test ./...`

evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-005.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/barcli/embed/prompt-grammar.json`; rerun `python3 -m prompts.export` to reapply the canonical payload if needed.

delta_summary: helper:diff-snapshot=0 files changed — execution confirmed the embedded prompt grammar already matched the exported payload; no code changes were necessary.

loops_remaining_forecast: 0 loops remain for ADR 0075 plan items; coordination package, overrides, and grammar alignment are complete. Confidence: high.

residual_constraints:
- Low — ADR 0072 documentation still needs pointer to the coordination layer work; mitigation: update ADR 0072 work log separately (outside current loop).

next_work:
- Behaviour: Update ADR 0072 follow-ups to reference the coordination layer (validation: docs review).

assets:
- Grammar embed verification: `internal/barcli/embed/prompt-grammar.json`
- Evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-005.md`

## loop-006 | helper:v20251223.1 | 2026-01-12

focus: ADR 0075 completion entry → record final coordination status and close out salient tasks 1–4.

active_constraint: ADR 0075 lacked a completion summary confirming all refactor plan items were satisfied, risking ambiguity for downstream contributors until the work-log captured the closure (validated via work-log update review).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | Medium | Capturing completion prevents duplicate work and clarifies remaining follow-ups |
| Probability | High | Updating the work-log directly documents status |
| Time Sensitivity | Medium | Needed before shifting coordination efforts to ADR 0072 |
| Uncertainty note | Low | Work-log edit is deterministic |

validation_targets:
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-006.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- docs/adr/0075-cli-churn-refactor.work-log.md`; rerun `go test ./internal/barcli` to confirm nothing else changed.

loops_remaining_forecast: 0 loops remain; ADR 0075 refactor plan items are complete. Confidence: high.

residual_constraints:
- Low — ADR 0072 documentation still needs a coordination-layer pointer; mitigation: follow-up documentation loop under ADR 0072.

next_work:
- Behaviour: Reflect ADR 0075 coordination outcomes in ADR 0072 follow-ups (validation: docs review under ADR 0072).

assets:
- Completion log: `docs/adr/0075-cli-churn-refactor.work-log.md`

## loop-007 | helper:v20251223.1 | 2026-01-12

focus: ADR 0075 governance → update ADR status to Accepted after completing plan items.

active_constraint: The ADR header still reported `Status: Proposed`, leaving governance ambiguous despite the refactor landing (observable via ADR metadata review).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | Medium | Accurately signalling completion prevents duplicate work and clarifies coordination owners |
| Probability | High | Editing the ADR status directly resolves the inconsistency |
| Time Sensitivity | Medium | Needed before handing off follow-up documentation to ADR 0072 |
| Uncertainty note | Low | Status change is deterministic |

validation_targets:
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0075-cli-churn-refactor/loop-007.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- docs/adr/0075-cli-churn-refactor.md docs/adr/0075-cli-churn-refactor.work-log.md`; rerun `go test ./internal/barcli` to confirm no behaviour changed.

loops_remaining_forecast: 0 loops remain; ADR 0075 is accepted. Confidence: high.

residual_constraints:
- Low — Update ADR 0072 follow-ups to reference the accepted coordination layer (mitigation planned separately).

next_work:
- Behaviour: Reflect coordination layer completion in ADR 0072 documentation (validation: docs review under ADR 0072).

assets:
- Accepted ADR: `docs/adr/0075-cli-churn-refactor.md`
