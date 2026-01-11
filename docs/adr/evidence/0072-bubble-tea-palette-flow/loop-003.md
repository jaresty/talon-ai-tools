# loop-003 evidence — helper:v20251223.1

## Behaviour outcome
Add the sticky summary strip that keeps preset/divergence, CLI command, destination, and environment info visible (ADR 0072 decision bullet 12) and ensure expect coverage plus a fast command runner guard the behaviour.

## Commands executed

### scripts/tools/run-tui-expect.sh sticky-summary
- red | 2026-01-11T14:23:04Z | exit 1
  - helper:diff-snapshot=0 files changed
  - failure: Expect aborted with `missing sticky summary strip`, proving the launch view lacked the summary line.
  - log: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-003-sticky-summary-red.log`
- green | 2026-01-11T14:59:48Z | exit 0
  - helper:diff-snapshot=4 files changed, 195 insertions(+), 52 deletions(-)
  - success: Transcript shows `Summary strip: Preset: …` immediately after the focus breadcrumbs, confirming the sticky strip renders with CLI/destination/env details.
  - log: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-003-sticky-summary-green.log`

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-11T15:02:12Z | exit 0
  - helper:diff-snapshot=4 files changed, 195 insertions(+), 52 deletions(-)
  - coverage: Sequentially re-ran every expect case to ensure the new summary strip and history changes keep the whole suite green.

### go test ./internal/bartui
- green | 2026-01-11T21:59:12Z | exit 0
  - helper:diff-snapshot=internal/bartui/program.go, internal/bartui/program_test.go
  - coverage: New tests assert the summary strip content and destination updates when copying CLI/preview.

### go test ./cmd/bar/...
- green | 2026-01-11T21:59:12Z | exit 0
  - helper:diff-snapshot=cmd/bar/testdata/tui_smoke.json
  - coverage: Smoke snapshot reflects the new summary strip output.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-11T21:59:12Z | exit 0
  - helper:diff-snapshot=none (behavioural confirmation only)
  - coverage: CLI completion surface unaffected by sticky summary changes.

## Artifacts
- Red transcript: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-003-sticky-summary-red.log`
- Green transcript: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-003-sticky-summary-green.log`
