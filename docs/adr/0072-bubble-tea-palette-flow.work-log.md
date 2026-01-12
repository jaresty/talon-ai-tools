# ADR 0072 — Bubble Tea palette and inline editing refinements work log

## loop-001 | helper:v20251223.1 | 2026-01-11

focus: ADR 0072 Decision bullet 6 → add a Ctrl+H palette history toggle that keeps recent token adjustments visible without leaving the docked palette (salient task: palette history surface + shortcut binding).

active_constraint: `scripts/tools/run-tui-expect.sh token-palette-history` fails with `missing palette history toggle`, showing the Bubble Tea palette still lacks the history viewport required by ADR 0072.

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Palette history is mandated in ADR 0072 to help operators replay omnibox adjustments |
| Probability | High | Updating `internal/bartui` view/state and adding an expect guardrail directly relieves the failure |
| Time Sensitivity | Medium | Needed before broader palette omnibox work so later loops inherit the history UI |
| Uncertainty note | Low | Behaviour is deterministic through the expect harness |

validation_targets:
- `scripts/tools/run-tui-expect.sh token-palette-history`
- `go test ./internal/bartui`
- `go test ./cmd/bar/...`
- `python3 -m pytest _tests/test_bar_completion_cli.py`

evidence: See `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-001.md` for red/green/removal transcripts and test runs.

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go internal/bartui/program_test.go`; rerun `scripts/tools/run-tui-expect.sh token-palette-history` to confirm the `missing palette history toggle` failure returns before reapplying the loop diff.

delta_summary: helper:diff-snapshot=2 files changed, 114 insertions(+) — added palette history state, Ctrl+H toggle handling, history rendering, and a unit test plus expect coverage for the new behaviour.

loops_remaining_forecast: 4 loops (dock omnibox column layout parity, sticky summary strip updates, inline chip collapse affordances, command history integration). Confidence: medium — remaining work spans layout refactors and additional palette affordances.

residual_constraints:
- Medium — Palette history currently records token adjustments only; command invocations and copy/undo events still lack history entries. Mitigation: extend history logging to `executePreviewCommand`/clipboard paths with expect coverage; monitor via `scripts/tools/run-tui-expect.sh token-palette-history` and new CLI history expect cases once added.
- Medium — Sticky summary strip described in ADR 0072 Decision bullet 12 is still absent; mitigation: restructure view to keep preset divergence and CLI command visible, validated by `go test ./cmd/bar/...` snapshot updates.

next_work:
- Behaviour: Capture command invocations in the palette history and list them alongside token edits (validation: `scripts/tools/run-tui-expect.sh token-palette-history` + `go test ./internal/bartui`).
- Behaviour: Implement the sticky summary strip that mirrors preset divergence and CLI command (validation: `go test ./cmd/bar/...` + updated snapshot fixture).

assets:
- Expect case: `tests/integration/tui/cases/token-palette-history.exp`
- Evidence bundle: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-001.md`
- Transcripts: `loop-001-token-palette-history-red.log`, `loop-001-token-palette-history-green.log`

## loop-002 | helper:v20251223.1 | 2026-01-11

focus: ADR 0072 Decision bullets 5 and 6 → surface focus breadcrumbs/status at launch and capture command executions in palette history (salient task: command lifecycle visibility + focus breadcrumbs).

active_constraint: `scripts/tools/run-tui-expect.sh token-command-history` failed with `missing palette history header` and operators reported “invisible controls” on launch (no focus cues), so command history and focus breadcrumbs were absent.

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Palette history needs to show command activity and focus breadcrumbs unblock operators from guessing the active pane |
| Probability | High | Updating `internal/bartui` rendering + tests directly addresses the failing areas |
| Time Sensitivity | Medium | Needed before layering more omnibox changes; user feedback flagged confusion |
| Uncertainty note | Low | Expect harness and unit tests reproduce the gap deterministically |

validation_targets:
- `scripts/tools/run-tui-expect.sh token-command-history`
- `go test ./internal/bartui`
- `go test ./cmd/bar/...`
- `python3 -m pytest _tests/test_bar_completion_cli.py`

evidence: See `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-002.md` for red/green transcripts and test runs.

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go internal/bartui/program_test.go cmd/bar/testdata/tui_smoke.json tests/integration/tui/cases/token-command-history.exp`; rerun `scripts/tools/run-tui-expect.sh token-command-history` to watch the failure return before reapplying the loop diff.

delta_summary: helper:diff-snapshot=8 files changed, 716 insertions(+), 2 deletions(-) — adds focus breadcrumbs/status, command history logging/tests, updated smoke snapshot, new expect harness, and evidence transcripts.

loops_remaining_forecast: 3 loops (dock omnibox column layout parity, sticky status strip/preset divergence, expand palette history for clipboard/undo events). Confidence: medium — remaining work mixes layout refactors and history enrichment.

residual_constraints:
- Medium — Palette history still omits clipboard paste/undo events; mitigation: extend history logging to clipboard loaders and undo flows with expect coverage.
- Medium — Sticky summary strip is still absent (Decision bullet 12); mitigation unchanged: restructure view to keep divergence + CLI command visible and snapshot it.

next_work:
- Behaviour: Implement the sticky summary strip showing preset divergence and CLI command (validation: updated snapshot + `go test ./cmd/bar/...`).
- Behaviour: Extend palette history logging to clipboard insertions/undo and preview reinserts (validation: new expect cases + `go test ./internal/bartui`).

assets:
- Expect case: `tests/integration/tui/cases/token-command-history.exp`
- Evidence bundle: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-002.md`
- Transcripts: `loop-002-token-command-history-red.log`, `loop-002-token-command-history-green.log`

## loop-003 | helper:v20251223.1 | 2026-01-11

focus: ADR 0072 Decision bullet 12 → add a sticky summary strip that surfaces preset/divergence, staged tokens, CLI command, destination, and environment state (salient task: summary strip + CLI/destination visibility).

active_constraint: `scripts/tools/run-tui-expect.sh sticky-summary` failed with `missing sticky summary strip`, and operators could not see presets/CLI/destination after launch, leaving the summary strip unimplemented.

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Summary strip keeps preset/divergence and CLI parity visible, anchoring the single-page flow |
| Probability | High | Updating `renderStatusStrip`/View and wiring expect coverage directly addresses the missing strip |
| Time Sensitivity | Medium | Needed before broader omnibox/palette refactors so transcripts remain audit-ready |
| Uncertainty note | Low | Failure and success reproduced deterministically via expect harness |

validation_targets:
- `scripts/tools/run-tui-expect.sh sticky-summary`
- `scripts/tools/run-tui-expect.sh --all`
- `go test ./internal/bartui`
- `go test ./cmd/bar/...`
- `python3 -m pytest _tests/test_bar_completion_cli.py`

evidence: See `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-003.md` for red/green transcripts and test runs.

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go internal/bartui/program_test.go cmd/bar/testdata/tui_smoke.json scripts/tools/run-tui-expect.sh tests/integration/tui/cases/sticky-summary.exp`; rerun `scripts/tools/run-tui-expect.sh sticky-summary` to confirm the missing strip returns.

delta_summary: helper:diff-snapshot=4 files changed, 195 insertions(+), 52 deletions(-) — added sticky summary strip rendering/state, destination tracking, expect helper for batch runs, new expect case, updated smoke snapshot, and unit coverage for summary content.

loops_remaining_forecast: 2 loops (dock omnibox layout/parity with Bubbles components; extend palette history/destination telemetry including ntcharts sparkline). Confidence: medium — remaining scope spans layout refactors and telemetry enrichment.

residual_constraints:
- Medium — Palette history still omits clipboard/undo events; mitigation: extend command/destination logging for clipboard inserts and undo flows with expect coverage.
- Medium — Docked omnibox layout refactor (Decision bullet 10/13) still pending; mitigation: rework viewports using Lip Gloss/Bubbles components, validated with updated snapshots.

next_work:
- Behaviour: Rework the docked omnibox layout and integrate Bubbles list/input components for staged edits (validation: updated snapshot + `go test ./cmd/bar/...`).
- Behaviour: Extend palette history/destination summaries to capture clipboard insertions, undo events, and command destinations (validation: augmented expect cases + `go test ./internal/bartui`).

assets:
- Expect case: `tests/integration/tui/cases/sticky-summary.exp`
- Evidence bundle: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-003.md`
- Transcripts: `loop-003-sticky-summary-red.log`, `loop-003-sticky-summary-green.log`

## loop-004 | helper:v20251223.1 | 2026-01-12

focus: ADR 0072 Follow-up section → reference the accepted CLI coordination layer from ADR 0075 so palette workflows track the canonical CLI contracts (salient follow-up bullet alignment).

active_constraint: Follow-up guidance omitted ADR 0075, risking divergence between the docked omnibox shortcuts and the now-accepted `internal/barcli/cli` configuration layer; doc review showed contributors lacked a pointer to the coordination package (validated via ADR comparison).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | Medium | Linking to ADR 0075 keeps palette work aligned with the canonical CLI contract |
| Probability | High | Updating the follow-up bullet directly resolves the missing guidance |
| Time Sensitivity | Medium | Needed before future loops expand the omnibox so they reuse the accepted coordination layer |
| Uncertainty note | Low | Documentation change is deterministic |

validation_targets:
- `go test ./internal/bartui`

evidence: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-004.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- docs/adr/0072-bubble-tea-palette-flow.md docs/adr/0072-bubble-tea-palette-flow.work-log.md`; rerun `go test ./internal/bartui` to confirm behaviour unchanged after revert.

delta_summary: helper:diff-snapshot=docs/adr/0072-bubble-tea-palette-flow.md | docs/adr/0072-bubble-tea-palette-flow.work-log.md — added a follow-up bullet linking ADR 0072 palette work to ADR 0075 and logged the completion entry.

loops_remaining_forecast: 2 loops (dock omnibox layout/telemetry and extend palette history with clipboard/undo events). Confidence: medium — layout refactors and telemetry enrichment remain.

residual_constraints:
- Medium — Palette history still omits clipboard/undo events; mitigation remains extending history logging with expect coverage.
- Medium — Docked omnibox layout refactor is still pending; mitigation: rework Lip Gloss/Bubbles layout with updated snapshots.

next_work:
- Behaviour: Implement docked omnibox layout refactor using Bubbles components (validation: updated snapshots + `go test ./cmd/bar/...`).
- Behaviour: Extend palette history for clipboard/undo events (validation: new expect cases + `go test ./internal/bartui`).

assets:
- Updated ADR reference: `docs/adr/0072-bubble-tea-palette-flow.md`
- Evidence: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-004.md`
