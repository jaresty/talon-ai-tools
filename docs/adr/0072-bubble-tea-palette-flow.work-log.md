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

## 2026-01-12 – Loop 012 (helper:v20251223.1)
- focus: Decision §“Add focus breadcrumbs, toast-style transient feedback…” → keep toast overlays observable by integration expect cases.
- active_constraint: Toast overlays triggered by token applications were not asserted in the expect suite, allowing regressions to ship undetected despite passing unit tests; falsifiable via `scripts/tools/run-tui-expect.sh --all` missing toast guardrails.
- expected_value table:
  | Factor           | Value | Rationale |
  |------------------|-------|-----------|
  | Impact           | High  | Prevents regressions that would hide CLI reinforcement cues pilots rely on. |
  | Probability      | High  | Extending the canonical expect case directly asserts the toast text. |
  | Time Sensitivity | Medium| Guardrail needed before broader palette theming to avoid masking future changes. |
  | Uncertainty note | Low   | Behaviour deterministic once expect assertion added. |
- validation_targets:
  - `scripts/tools/run-tui-expect.sh --all`
  - `go test ./internal/bartui`
  - `go test ./cmd/bar/...`
  - `python3 -m pytest _tests/test_bar_completion_cli.py`
- evidence:
  - green | 2026-01-12T19:46:21Z | exit 0 | `scripts/tools/run-tui-expect.sh --all`
    helper:diff-snapshot=1 file changed, 4 insertions(+)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-012.md
  - green | 2026-01-12T19:46:21Z | exit 0 | `go test ./internal/bartui`
    helper:diff-snapshot=1 file changed, 4 insertions(+)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-012.md
  - green | 2026-01-12T19:46:21Z | exit 0 | `go test ./cmd/bar/...`
    helper:diff-snapshot=1 file changed, 4 insertions(+)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-012.md
  - green | 2026-01-12T19:46:21Z | exit 0 | `python3 -m pytest _tests/test_bar_completion_cli.py`
    helper:diff-snapshot=1 file changed, 4 insertions(+)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-012.md
- rollback_plan: `git restore --source=HEAD~1 tests/integration/tui/cases/token-palette-history.exp` followed by `scripts/tools/run-tui-expect.sh --case token-palette-history` to watch the toast assertion disappear.
- delta_summary: helper:diff-snapshot=1 file changed, 4 insertions(+); added expect guard that requires toast overlay when applying a token.
- loops_remaining_forecast: 1 loop (pilot playbook/docs refresh capturing grammar-first palette guidance). Confidence: medium — awaiting pilot feedback to finalise wording.
- residual_constraints:
  - Pilot-facing documentation updates for the grammar-first palette remain outstanding (severity: medium impact × low probability). Mitigation: schedule documentation loop once usage notes settle; monitor pilot feedback triage reviews. Owning ADR: 0072 follow-up §“Refresh docs…”.
- next_work:
  - Behaviour: Refresh pilot playbook/quickstart docs with grammar-first palette guidance; validation target `scripts/tools/run-tui-expect.sh --all` (to ensure examples stay aligned) plus documentation review checklist.

## 2026-01-12 – Loop 013 (helper:v20251223.1)
- focus: Decision §“Surface token telemetry beneath the grammar composer…” → ensure sparkline telemetry renders legibly in ASCII-only transcripts.
- active_constraint: Sparkline glyphs used box-drawing characters that rendered as garbled bytes in expect transcripts, obscuring telemetry feedback; proven by the existing `scripts/tools/run-tui-expect.sh --all` output showing `â` artefacts.
- expected_value table:
  | Factor           | Value | Rationale |
  |------------------|-------|-----------|
  | Impact           | Medium| Restores readability of telemetry trends that reinforce CLI grammar feedback. |
  | Probability      | High  | Swapping to ASCII glyphs deterministically fixes encoding issues. |
  | Time Sensitivity | Medium| Needed before distributing expect transcripts to pilots; otherwise feedback loops stall. |
  | Uncertainty note | Low   | Behaviour confirmed via snapshot/expect reruns. |
- validation_targets:
  - `go test ./internal/bartui`
  - `go test ./cmd/bar/...`
  - `python3 -m pytest _tests/test_bar_completion_cli.py`
  - `scripts/tools/run-tui-expect.sh --all`
- evidence:
  - green | 2026-01-12T20:05:43Z | exit 0 | `go test ./internal/bartui`
    helper:diff-snapshot=2 files changed, 2 insertions(+), 1 deletion(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-013.md
  - green | 2026-01-12T20:05:43Z | exit 0 | `go test ./cmd/bar/...`
    helper:diff-snapshot=2 files changed, 2 insertions(+), 1 deletion(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-013.md
  - green | 2026-01-12T20:05:43Z | exit 0 | `python3 -m pytest _tests/test_bar_completion_cli.py`
    helper:diff-snapshot=2 files changed, 2 insertions(+), 1 deletion(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-013.md
  - green | 2026-01-12T20:05:43Z | exit 0 | `scripts/tools/run-tui-expect.sh --all`
    helper:diff-snapshot=2 files changed, 2 insertions(+), 1 deletion(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-013.md
- rollback_plan: `git restore --source=HEAD~1 internal/bartui/program.go cmd/bar/testdata/tui_smoke.json` followed by `scripts/tools/run-tui-expect.sh --case token-palette-history` to observe the garbled sparkline glyphs return.
- delta_summary: helper:diff-snapshot=2 files changed, 2 insertions(+), 1 deletion(-); sparkline glyphs replaced with ASCII ramp and smoke snapshot updated to match.
- loops_remaining_forecast: 1 loop (pilot playbook/docs refresh capturing grammar-first palette guidance). Confidence: medium — awaiting pilot feedback to finalise wording.
- residual_constraints:
  - Pilot-facing documentation updates for the grammar-first palette remain outstanding (severity: medium impact × low probability). Mitigation: schedule documentation loop once usage notes settle; monitor pilot feedback triage reviews. Owning ADR: 0072 follow-up §“Refresh docs…”.
- next_work:
  - Behaviour: Refresh pilot playbook/quickstart docs with grammar-first palette guidance; validation target `scripts/tools/run-tui-expect.sh --all` plus documentation review checklist.
