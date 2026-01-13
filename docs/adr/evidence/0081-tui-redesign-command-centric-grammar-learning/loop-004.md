## Behaviour outcome
Implement subject input modal (Ctrl+L) for entering/editing subject text that gets passed to preview generation.

## Commands executed

### Tests
- green | 2026-01-13T21:00:00Z | go test ./internal/bartui2
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
  - TestSubjectModalRendering: verifies modal shows header and hotkey hints
  - TestSubjectModalHidesMainView: verifies main view hidden when modal open
  - TestSubjectPassedToPreview: verifies subject passed to preview function
  - TestHotkeyBarShowsSubjectShortcut: verifies ^L shortcut in hotkey bar
- green | 2026-01-13T21:00:00Z | go test ./internal/barcli
  - All existing tests pass

## Implementation notes
- Added `bubbles/textarea` import for multiline subject input
- Added model fields:
  - `subject string` — stores the subject text
  - `subjectInput textarea.Model` — textarea for modal
  - `showSubjectModal bool` — tracks modal visibility
- Subject modal workflow:
  - Ctrl+L opens modal, focuses textarea, blurs command input
  - Ctrl+S saves subject and closes modal
  - Esc cancels and closes without saving
  - Subject passed to preview function for prompt generation
- Input routing:
  - Window size handled for all modes (resizes textarea)
  - Modal state gates input routing before main view handling
  - Per bubbles-inputs skill: global shortcuts handled before delegating to inputs
- Modal rendering:
  - Shows "SUBJECT INPUT" header with distinct border color (212)
  - Shows current subject stats (lines, chars) when subject exists
  - Shows hotkey hints: "Ctrl+S: save | Esc: cancel"
- Hotkey bar updated with shorter labels to fit width: "^L: subject"

## Files modified
- `internal/bartui2/program.go` — Added textarea import, subject fields, modal handling, renderSubjectModal()
- `internal/bartui2/program_test.go` — Added 4 tests for subject modal functionality
