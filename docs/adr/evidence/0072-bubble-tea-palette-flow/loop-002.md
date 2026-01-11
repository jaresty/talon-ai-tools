# loop-002 evidence — helper:v20251223.1

## Behaviour outcome
Record command executions in the palette history and surface focus breadcrumbs/status so operators can immediately see which pane is active when the TUI launches (ADR 0072 decision bullets 5 and 6).

## Commands executed

### scripts/tools/run-tui-expect.sh token-command-history
- red | 2026-01-11T13:28:53Z | exit 1
  - helper:diff-snapshot=0 files changed
  - failure: Expect halted with `missing palette history header`, showing the palette history did not capture the executed command.
  - log: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-002-token-command-history-red.log`
- green | 2026-01-11T13:48:24Z | exit 0
  - helper:diff-snapshot=3 files changed, 196 insertions(+), 2 deletions(-) plus new expect case
  - success: Transcript lists the new `Palette history (Ctrl+H toggles)` section with `Command (subject) → "printf hi" exit 0`, and the viewport shows focus breadcrumbs.
  - log: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-002-token-command-history-green.log`

### go test ./internal/bartui
- green | 2026-01-11T21:53:28Z | exit 0
  - helper:diff-snapshot=internal/bartui/program.go, internal/bartui/program_test.go
  - coverage: New unit tests verify command history formatting, preview scope labelling, and initial focus breadcrumbs.

### go test ./cmd/bar/...
- green | 2026-01-11T21:53:28Z | exit 0
  - helper:diff-snapshot=cmd/bar/testdata/tui_smoke.json
  - coverage: Updated snapshot expectation reflects the focus breadcrumbs and subject-focused status strip.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-11T21:53:28Z | exit 0
  - helper:diff-snapshot=none (behavioural confirmation only)
  - coverage: CLI completion surface unaffected by palette history updates.

## Artifacts
- Red transcript: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-002-token-command-history-red.log`
- Green transcript: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-002-token-command-history-green.log`
