# loop-004 evidence — helper:v20251223.1

## Behaviour outcome
Ensure the token palette workflow keeps Enter advancing from the filter to the options list and records an undo snapshot so Ctrl+Z restores the previous token selection, matching ADR 0071’s keyboard ergonomics requirement.

## Commands executed

### scripts/tools/run-tui-expect.sh token-palette-workflow
- red | 2026-01-11T12:26:15Z | exit 1
  - prereq: `git restore --source=HEAD^ -- internal/bartui/program.go internal/bartui/program_test.go`
  - helper:diff-snapshot=0 files changed (code temporarily restored to pre-fix state)
  - failure: Expect halted at `Status: No token change to undo.` showing the palette undo path still broken.
  - log: `docs/adr/evidence/0071-bubble-tea-tui-layout-ergonomics/loop-004-token-palette-red.log`
- green | 2026-01-11T12:26:55Z | exit 0
  - helper:diff-snapshot=8 files changed, 200 insertions(+), 6 deletions(-) (commit 0b6480b6)
  - success: Expect transcript shows `Status: Token selection restored.` and the palette closes cleanly after undo.
  - log: `docs/adr/evidence/0071-bubble-tea-tui-layout-ergonomics/loop-004-token-palette-green.log`
- removal | 2026-01-11T12:26:15Z | exit 1
  - command: `git restore --source=HEAD^ -- internal/bartui/program.go internal/bartui/program_test.go && scripts/tools/run-tui-expect.sh token-palette-workflow`
  - helper:diff-snapshot=0 files changed (after reverting)
  - outcome: same failure as red evidence (`No token change to undo.`) proving the guardrail.
  - log: `docs/adr/evidence/0071-bubble-tea-tui-layout-ergonomics/loop-004-token-palette-red.log`

### go test ./internal/bartui
- green | 2026-01-11T20:29:03Z | exit 0
  - helper:diff-snapshot=8 files changed, 200 insertions(+), 6 deletions(-)
  - coverage: unit assertions confirm palette undo snapshots and status messaging.

### go test ./cmd/bar/...
- green | 2026-01-11T20:29:36Z | exit 0
  - helper:diff-snapshot=8 files changed, 200 insertions(+), 6 deletions(-)
  - coverage: smoke snapshot stays in sync with the compact summary and palette messaging.

## Artifacts
- Red transcript: `docs/adr/evidence/0071-bubble-tea-tui-layout-ergonomics/loop-004-token-palette-red.log`
- Green transcript: `docs/adr/evidence/0071-bubble-tea-tui-layout-ergonomics/loop-004-token-palette-green.log`
