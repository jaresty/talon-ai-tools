# loop-001 evidence — helper:v20251223.1

## Behaviour outcome
Expose a keyboard-accessible palette history toggle (Ctrl+H) that lists recent token adjustments so pilots can review and replay omnibox edits without leaving the docked palette, per ADR 0072 Decision bullet 6.

## Commands executed

### scripts/tools/run-tui-expect.sh token-palette-history
- red | 2026-01-11T20:47:33Z | exit 1
  - helper:diff-snapshot=0 files changed (pre-change baseline)
  - failure: Expect halted with `missing palette history toggle`, proving Ctrl+H produced no history output.
  - log: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-001-token-palette-history-red.log`
- green | 2026-01-11T20:48:52Z | exit 0
  - helper:diff-snapshot=4 files changed, 167 insertions(+)
  - success: Expect transcript shows `Palette history (Ctrl+H toggles)` with the most recent `Static Prompt → todo applied` entry listed.
  - log: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-001-token-palette-history-green.log`
- removal | 2026-01-11T20:47:33Z | exit 1 | `git restore --source=HEAD -- internal/bartui/program.go internal/bartui/program_test.go && scripts/tools/run-tui-expect.sh token-palette-history`
  - helper:diff-snapshot=0 files changed after temporary revert
  - outcome: Replays the missing history failure, confirming the guardrail.
  - log: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-001-token-palette-history-red.log`

### go test ./internal/bartui
- green | 2026-01-11T20:51:01Z | exit 0
  - helper:diff-snapshot=4 files changed, 167 insertions(+)
  - coverage: Unit test `TestTokenPaletteHistoryToggle` verifies Ctrl+H toggles history visibility and records entries.

### go test ./cmd/bar/...
- green | 2026-01-11T20:51:36Z | exit 0
  - helper:diff-snapshot=4 files changed, 167 insertions(+)
  - coverage: Smoke snapshot remains stable with inline palette summary updates.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-11T20:52:09Z | exit 0
  - helper:diff-snapshot=4 files changed, 167 insertions(+)
  - coverage: CLI completion hints remain consistent with palette shortcut messaging.

## Artifacts
- Red transcript: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-001-token-palette-history-red.log`
- Green transcript: `docs/adr/evidence/0072-bubble-tea-palette-flow/loop-001-token-palette-history-green.log`
