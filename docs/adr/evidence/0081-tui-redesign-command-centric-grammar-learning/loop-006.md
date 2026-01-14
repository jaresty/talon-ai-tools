## Behaviour outcome
Implement command execution (Ctrl+Enter) to run shell commands with the preview piped as stdin, displaying results in a dedicated pane.

## Commands executed

### Tests
- green | 2026-01-13T22:00:00Z | go test ./internal/bartui2
  - TestSnapshotBasicLayout: PASS
  - TestSnapshotEmptyTokens: PASS
  - TestParseTokensFromCommand: PASS
  - TestParseTokensFromCommandEmpty: PASS
  - TestFuzzyCompletionAllOptions: PASS
  - TestFuzzyCompletionFiltering: PASS
  - TestFuzzyCompletionExcludesSelected: PASS
  - TestCompletionSelection: PASS
  - TestCompletionSelectionWithPartial: PASS
  - TestSnapshotWithCompletions: PASS
  - TestGetCategoryForToken: PASS
  - TestTokenTreeWithCategoryLabels: PASS
  - TestTokenTreeEmptyShowsNoCount: PASS
  - TestSubjectModalRendering: PASS
  - TestSubjectModalHidesMainView: PASS
  - TestSubjectPassedToPreview: PASS
  - TestHotkeyBarShowsSubjectShortcut: PASS
  - TestClipboardCopyCommand: PASS
  - TestClipboardCopyWithTokens: PASS
  - TestClipboardUnavailable: PASS
  - TestToastDisplaysInHotkeyBar: PASS
  - TestToastClearedOnKeyPress: PASS
  - TestCommandModalRendering: verifies modal shows RUN COMMAND header
  - TestCommandModalHidesMainView: verifies modal replaces main view
  - TestCommandExecution: verifies command runs with preview as stdin
  - TestCommandExecutionWithStderr: verifies stdout/stderr combined in result
  - TestCommandExecutionUnavailable: verifies toast when no runner
  - TestResultPaneRendering: verifies result pane shows output
  - TestResultModeHotkeyBar: verifies result-specific shortcuts
  - TestCopyResultToClipboard: verifies Ctrl+Y copies result
  - TestEscReturnFromResult: verifies Esc returns to preview
  - TestCtrlRReturnFromResult: verifies Ctrl+R returns to preview
  - TestHotkeyBarShowsRunShortcut: verifies ^Enter hint in hotkey bar
- green | 2026-01-13T22:00:00Z | go test ./internal/barcli
  - All existing tests pass

## Implementation notes
- Added `RunCommand func(ctx context.Context, command string, stdin string) (stdout, stderr string, err error)` to Options struct
- Added `CommandTimeout time.Duration` to Options (default 30s)
- Added model fields: `shellCommandInput`, `showCommandModal`, `lastShellCommand`, `runCommand`, `commandTimeout`, `commandResult`, `showingResult`
- `updateCommandModal()` handles modal input:
  - Enter: execute command and close modal
  - Esc: cancel and return to main view
- `executeCommand()` method:
  - Pipes preview text as stdin to the shell command
  - Captures stdout, stderr, and errors
  - Sets `showingResult = true` to switch view
- `renderCommandModal()` shows modal with command input and hints
- `renderResultPane()` shows command output with:
  - RESULT header with command name
  - Truncated output (respects pane height)
- Updated hotkey bar:
  - Normal mode: ^Enter: run
  - Result mode: ^Y: copy result | ^R: back to preview | Esc: back
- Added Ctrl+Y to copy result to clipboard
- Added Ctrl+R and Esc to return from result to preview
- Wired `exec.CommandContext` runner in tui2.go
- Added 12 new tests for command execution functionality

## Files modified
- `internal/bartui2/program.go` — Added RunCommand/CommandTimeout options, command modal state, executeCommand(), renderCommandModal(), renderResultPane(), result mode hotkey bar
- `internal/bartui2/program_test.go` — Added context import, 12 tests for command execution
- `internal/barcli/tui2.go` — Added bytes/context/exec/time imports, wired runCommand function
