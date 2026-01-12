# ADR 0072 – Bubble Tea palette flow work log

## 2026-01-12 – Loop 011 (helper:v20251223.1)
- focus: Decision §“Add focus breadcrumbs, toast-style transient feedback…” → reinforce CLI learning with inline telemetry and toasts.
- active_constraint: Token adjustments lacked inline CLI feedback, causing operators to miss grammar reinforcement; falsified previously by `go test ./internal/bartui` lacking toast/sparkline coverage, now relieved by extending the Bubble Tea model and tests.
- expected_value table:
  | Factor           | Value | Rationale |
  |------------------|-------|-----------|
  | Impact           | High  | Restores immediate CLI reinforcement inside the compose pane, unlocking ADR 0072’s feedback objective. |
  | Probability      | High  | Directly implements telemetry + toast mechanisms in the canonical Bubble Tea model and tests them. |
  | Time Sensitivity | Medium| Pilot feedback needed before next CLI release window; delay would defer usability learnings but not block deploy pipeline. |
  | Uncertainty note | N/A   | Behaviour proven green via unit, integration, and expect validations. |
- validation_targets:
  - `go test ./internal/bartui`
  - `go test ./cmd/bar/...`
  - `python3 -m pytest _tests/test_bar_completion_cli.py`
  - `scripts/tools/run-tui-expect.sh --all`
- evidence:
  - green | 2026-01-12T19:35:50Z | exit 0 | `go test ./internal/bartui`
    helper:diff-snapshot=4 files changed, 307 insertions(+), 33 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-011.md
  - green | 2026-01-12T19:35:50Z | exit 0 | `go test ./cmd/bar/...`
    helper:diff-snapshot=4 files changed, 307 insertions(+), 33 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-011.md
  - green | 2026-01-12T19:35:50Z | exit 0 | `python3 -m pytest _tests/test_bar_completion_cli.py`
    helper:diff-snapshot=4 files changed, 307 insertions(+), 33 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-011.md
  - green | 2026-01-12T19:35:50Z | exit 0 | `scripts/tools/run-tui-expect.sh --all`
    helper:diff-snapshot=4 files changed, 307 insertions(+), 33 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-011.md
- rollback_plan: `git revert <commit-sha>` followed by `scripts/tools/run-tui-expect.sh --all` to watch the toast feedback regress.
- delta_summary: helper:diff-snapshot=4 files changed, 307 insertions(+), 33 deletions(-); added toast state/commands, sparkline relocation, updated smoke fixture, ADR decision text, and evidence loop.
- loops_remaining_forecast: 2 loops (toast styling polish in expect snapshots; pilot playbook/docs refresh). Confidence: medium — telemetry visuals may need tuning after operator feedback.
- residual_constraints:
  - Toast theming parity across dark/light palettes remains unverified (severity: medium impact × medium probability). Mitigation: capture screenshot-based expect fixtures once theming assets land; monitor via nightly `scripts/tools/run-tui-expect.sh --all`. Owning ADR: 0072 (styling follow-up).
- next_work:
  - Behaviour: Capture toast styling parity in expect transcripts and palette docs; validation target `scripts/tools/run-tui-expect.sh --all` (extend cases to assert toast lines).
