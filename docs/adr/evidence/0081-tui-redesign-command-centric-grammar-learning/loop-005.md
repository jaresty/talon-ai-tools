## Behaviour outcome
Implement clipboard copy (Ctrl+B) to copy the bar build command to system clipboard with toast feedback.

## Commands executed

### Tests
- green | 2026-01-13T21:30:00Z | go test ./internal/bartui2
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
  - TestClipboardCopyCommand: verifies command copied to clipboard
  - TestClipboardCopyWithTokens: verifies command with tokens copied
  - TestClipboardUnavailable: verifies error toast when no clipboard
  - TestToastDisplaysInHotkeyBar: verifies toast renders in place of hotkeys
  - TestToastClearedOnKeyPress: verifies toast dismissed on next key
- green | 2026-01-13T21:30:00Z | go test ./internal/barcli
  - All existing tests pass

## Implementation notes
- Added `ClipboardWrite func(string) error` to Options struct
- Added `clipboardWrite` and `toastMessage` fields to model
- `copyCommandToClipboard()` method:
  - Gets current command from textinput
  - Calls clipboardWrite function
  - Sets toast message for success/error feedback
- Toast system:
  - `toastMessage` field stores current toast
  - `toastStyle` renders in green (color 78)
  - Toast replaces hotkey bar when present
  - Toast clears on any key press
- Wired `github.com/atotto/clipboard.WriteAll` in tui2.go
- Added 5 new tests for clipboard and toast functionality

## Files modified
- `internal/bartui2/program.go` — Added ClipboardWrite option, clipboardWrite/toastMessage fields, copyCommandToClipboard(), toastStyle, toast rendering
- `internal/bartui2/program_test.go` — Added tea import, 5 tests for clipboard/toast
- `internal/barcli/tui2.go` — Added clipboard import, wired ClipboardWrite option
