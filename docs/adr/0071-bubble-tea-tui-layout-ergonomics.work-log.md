# ADR 0071 — Bubble Tea TUI layout ergonomics refinement work log

## loop-001 | helper:v20251223.1 | 2026-01-11

focus: ADR 0071 Decision → surface compact status strip and condensed token summary within `internal/bartui` view helpers (salient task: implement layout changes in `View()` and token viewport rendering).

active_constraint: The TUI view still prints the verbose status/preset blocks beneath the result pane, so the compact status strip required by ADR 0071 is absent; `go test ./cmd/bar/...` fails once the fixture expects the new above-the-fold summary.

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Keeps subject, tokens, and results visible on 24–30 row terminals per ADR 0071 |
| Probability | High | Updating `internal/bartui/program.go` and the snapshot fixture directly addresses the layout gap |
| Time Sensitivity | Medium | Needed before we iterate on palette ergonomics so subsequent loops inherit the compact baseline |
| Uncertainty note | Low | Behaviour matches prior prototype diff and snapshot harness exercises the same view |

validation_targets:
- `go test ./cmd/bar/...`
- `go test ./internal/bartui/...`

evidence:
- red | 2026-01-11T15:43:20Z | exit 1 | `go test ./cmd/bar/...`
    helper:diff-snapshot=0 files changed before fixture update
    Snapshot mismatch shows status strip absent from view (`Subject ...` header appears where status strip should be) | inline
- green | 2026-01-11T15:48:20Z | exit 0 | `go test ./cmd/bar/...`
    helper:diff-snapshot=2 files changed, 113 insertions(+), 139 deletions(-)
    Updated view renders compact status strip and condensed token summary above the fold | inline
- green | 2026-01-11T15:48:35Z | exit 0 | `go test ./internal/bartui/...`
    helper:diff-snapshot=2 files changed, 113 insertions(+), 139 deletions(-)
    Inline rendering helpers pass unit coverage after layout refactor | inline
- removal | 2026-01-11T15:50:10Z | exit 1 | `git restore internal/bartui/program.go && go test ./cmd/bar/...`
    helper:diff-snapshot=1 file changed, 1 insertion(+), 1 deletion(-)
    Reverting the view helper with new fixture still present reproduces the snapshot failure, confirming the guardrail | inline

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go cmd/bar/testdata/tui_smoke.json`; re-run `go test ./cmd/bar/...` to confirm the snapshot returns to the prior layout, then reapply `docs/adr/evidence/0071-bubble-tea-tui-layout-ergonomics/loop-001-final.patch` if the revert was temporary.

delta_summary: helper:diff-snapshot=2 files changed, 113 insertions(+), 139 deletions(-) — refactored `View()`/token summary to emit the status strip and condensed tokens plus regenerated `tui_smoke.json` snapshot so the guardrail covers the new layout.

loops_remaining_forecast: 2 loops (grouped help overlay shortcuts; result pane heading/status icons). Confidence: medium — core layout is stable but copy/typography refinements still pending.

residual_constraints:
- Medium — Help overlay still lists shortcuts as paragraphs instead of grouped lists; mitigation: reorganise overlay copy per ADR 0071 Decision bullet 3, validated by `go test ./internal/bartui/...`; monitor by watching for snapshot churn in `cmd/bar/testdata/tui_smoke.json`; owned by ADR 0071.
- Medium — Result pane lacks the elevated heading/status iconography described in ADR 0071 Decision bullet 4; mitigation: update render helpers to add concise status banner and ensure snapshots cover success/failure cues; monitor via `go test ./cmd/bar/...` diffs.

next_work:
- Behaviour: Group shortcut references into grouped lists inside the help overlay (ADR 0071 Decision bullet 3). Validation: `go test ./internal/bartui/...` plus `go test ./cmd/bar/...` snapshot refresh.
- Behaviour: Elevate result pane heading with status icon/summary (ADR 0071 Decision bullet 4). Validation: `go test ./cmd/bar/...` to refresh fixture and confirm visibility cues.

assets:
- helper:wip-preserve patch archived at `docs/adr/evidence/0071-bubble-tea-tui-layout-ergonomics/loop-001-wip.patch`
- Final diff replay patch stored at `docs/adr/evidence/0071-bubble-tea-tui-layout-ergonomics/loop-001-final.patch`
