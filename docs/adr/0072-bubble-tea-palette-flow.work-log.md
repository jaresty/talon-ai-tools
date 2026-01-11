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
