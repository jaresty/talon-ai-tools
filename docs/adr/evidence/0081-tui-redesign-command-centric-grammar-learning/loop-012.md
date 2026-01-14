## Behaviour outcome
Implement command execution workflow with Ctrl+R quick re-run and Ctrl+S pipeline result to subject.

## Commands executed

### Tests
- red | 2026-01-14T04:00:00Z | go test ./internal/bartui2 -run "TestCtrlRQuickRerun|TestCtrlROpensModalWhenNoLastCommand|TestCtrlSPipelinesResultToSubject|TestCtrlSShowsToastConfirmation|TestHotkeyBarShowsPipelineShortcut"
  - 5 tests fail: Ctrl+R does not quick re-run, Ctrl+S not implemented, hotkey bar missing ^S
- green | 2026-01-14T04:30:00Z | go test ./internal/bartui2 ./internal/barcli ./internal/bartui
  - All tests pass (58 tests in bartui2, 5 new tests added)
  - TestCtrlRQuickRerun: verifies Ctrl+R runs last command without modal
  - TestCtrlROpensModalWhenNoLastCommand: verifies Ctrl+R opens modal when no command configured
  - TestCtrlSPipelinesResultToSubject: verifies Ctrl+S loads result into subject
  - TestCtrlSShowsToastConfirmation: verifies toast feedback
  - TestHotkeyBarShowsPipelineShortcut: verifies ^S appears in result mode hotkey bar

## Implementation notes
- Ctrl+R behavior now depends on context:
  - If showing result: returns to preview (existing behavior)
  - If lastShellCommand is set: runs command immediately without modal
  - If no lastShellCommand: opens command configuration modal
- Added `pipelineResultToSubject()` method that:
  - Sets subject to commandResult
  - Exits result mode
  - Updates preview with new subject
  - Shows toast confirmation
- Updated hotkey bar to show "^S: to subject" in result mode

## Files modified
- `internal/bartui2/program.go` - Added Ctrl+S handler, modified Ctrl+R handler, added pipelineResultToSubject(), updated hotkey bar
- `internal/bartui2/program_test.go` - Added 5 new tests for command execution workflow
