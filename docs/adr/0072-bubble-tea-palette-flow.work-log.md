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
  - Behaviour: Monitor toast palette against future theme tokens; validation target `scripts/tools/run-tui-expect.sh --all` (rerun when theme assets change).

## 2026-01-12 – Loop 017 (helper:v20251223.1)
- focus: Decision §“Expose a palette history toggle… History entries should show the exact CLI command that would reproduce the action.”
- active_constraint: Palette history entries only listed human-readable messages (e.g., "Static Prompt → todo applied") without the CLI command, preventing operators from replaying changes directly per ADR guidance; evidenced by the history pane lacking a CLI summary even after previous loops.
- expected_value table:
  | Factor           | Value | Rationale |
  |------------------|-------|-----------|
  | Impact           | High  | Adds the reproducible CLI command to every history line, fulfilling the ADR decision and improving learnability. |
  | Probability      | High  | Appending the existing `displayCommandString()` output is deterministic and covered by tests/expect snapshots. |
  | Time Sensitivity | Medium| Needed during pilot so transcripts teach the grammar composer workflow without external notes. |
  | Uncertainty note | Low   | Behaviour validated via unit + integration tests and expect transcripts. |
- validation_targets:
  - `go test ./internal/bartui`
  - `go test ./cmd/bar/...`
  - `python3 -m pytest _tests/test_bar_completion_cli.py`
  - `scripts/tools/run-tui-expect.sh --all`
- evidence:
  - green | 2026-01-12T21:54:43Z | exit 0 | `go test ./internal/bartui`
    helper:diff-snapshot=3 files changed, 19 insertions(+), 8 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-017.md
  - green | 2026-01-12T21:54:43Z | exit 0 | `go test ./cmd/bar/...`
    helper:diff-snapshot=3 files changed, 19 insertions(+), 8 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-017.md
  - green | 2026-01-12T21:54:43Z | exit 0 | `python3 -m pytest _tests/test_bar_completion_cli.py`
    helper:diff-snapshot=3 files changed, 19 insertions(+), 8 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-017.md
  - green | 2026-01-12T21:54:43Z | exit 0 | `scripts/tools/run-tui-expect.sh --all`
    helper:diff-snapshot=3 files changed, 19 insertions(+), 8 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-017.md
- rollback_plan: `git restore --source=HEAD~1 internal/bartui/program.go internal/bartui/program_test.go tests/integration/tui/cases/token-palette-history.exp` followed by `go test ./internal/bartui` to confirm the history pane reverts to message-only entries.
- delta_summary: helper:diff-snapshot=3 files changed, 19 insertions(+), 8 deletions(-); history events now persist CLI summaries, tests ensure prompts stay hidden, and expect transcripts explicitly assert the CLI display.
- loops_remaining_forecast: 0 loops; confidence high — palette history now meets ADR expectations.
- residual_constraints:
  - Palette theming remains hard-coded to ANSI 256 values (severity: low impact × medium probability). Mitigation unchanged: revisit with ADR 0077 theme work and rerun `scripts/tools/run-tui-expect.sh --all` after palette updates.
- next_work:
  - Behaviour: Monitor toast palette against future theme tokens; validation target `scripts/tools/run-tui-expect.sh --all` (rerun when theme assets change).


## 2026-01-12 – Loop 016 (helper:v20251223.1)
- focus: Decision §“Keep CLI summaries focused on grammar tokens…” → hide raw subject prompts from all Bubble Tea CLI summaries and toasts.
- active_constraint: Status strips, summary strips, and toast notifications still echoed the entire `--prompt` argument (`bar build … --prompt '<subject>'`), overwhelming pilots and violating ADR guidance; validated by existing smoke snapshot and toast output.
- expected_value table:
  | Factor           | Value | Rationale |
  |------------------|-------|-----------|
  | Impact           | High  | Prevents subject leakage in UI summaries and keeps CLI reinforcement focused on grammar tokens. |
  | Probability      | High  | A dedicated display-command helper guarantees prompt filtering across all summary surfaces. |
  | Time Sensitivity | Medium| Needed before broader pilot rollout so transcripts and toasts stay concise. |
  | Uncertainty note | Low   | Behaviour confirmed via unit, fixture, and expect updates. |
- validation_targets:
  - `go test ./internal/bartui`
  - `go test ./cmd/bar/...`
  - `python3 -m pytest _tests/test_bar_completion_cli.py`
  - `scripts/tools/run-tui-expect.sh --all`
- evidence:
  - green | 2026-01-12T21:42:02Z | exit 0 | `go test ./internal/bartui`
    helper:diff-snapshot=3 files changed, 68 insertions(+), 7 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-016.md
  - green | 2026-01-12T21:42:02Z | exit 0 | `go test ./cmd/bar/...`
    helper:diff-snapshot=3 files changed, 68 insertions(+), 7 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-016.md
  - green | 2026-01-12T21:42:02Z | exit 0 | `python3 -m pytest _tests/test_bar_completion_cli.py`
    helper:diff-snapshot=3 files changed, 68 insertions(+), 7 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-016.md
  - green | 2026-01-12T21:42:02Z | exit 0 | `scripts/tools/run-tui-expect.sh --all`
    helper:diff-snapshot=3 files changed, 68 insertions(+), 7 deletions(-)
    docs/adr/evidence/0072-bubble-tea-palette-flow/loop-016.md
- rollback_plan: `git restore --source=HEAD~1 internal/bartui/program.go internal/bartui/program_test.go cmd/bar/testdata/tui_smoke.json` then rerun `go test ./internal/bartui` to confirm CLI summaries revert to raw prompts.
- delta_summary: helper:diff-snapshot=3 files changed, 68 insertions(+), 7 deletions(-); added display-command helper, prompt-free status/summary/toast rendering, regression tests, and updated smoke snapshot.
- loops_remaining_forecast: 0 loops; confidence high — pending items are limited to future theming work tracked in residual constraints.
- residual_constraints:
  - Palette theming remains hard-coded to ANSI 256 values (severity: low impact × medium probability). Mitigation: revisit once consolidated theme palette lands per ADR 0077; monitor design sync updates and rerun `scripts/tools/run-tui-expect.sh --all` after theme changes.
- next_work:
  - Behaviour: Monitor toast palette against future theme tokens; validation target `scripts/tools/run-tui-expect.sh --all` (rerun when theme assets change).
