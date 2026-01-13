## Behaviour outcome
Implement fuzzy completion matching across all token categories with live filtering, selection navigation, and completion application.

## Commands executed

### Tests
- green | 2026-01-13T19:30:00Z | go test ./internal/bartui2
  - TestSnapshotBasicLayout: PASS
  - TestSnapshotEmptyTokens: PASS
  - TestParseTokensFromCommand: PASS
  - TestParseTokensFromCommandEmpty: PASS
  - TestFuzzyCompletionAllOptions: verifies all 6 options shown with no filter
  - TestFuzzyCompletionFiltering: verifies "fo" matches "focus" but not "todo"
  - TestFuzzyCompletionExcludesSelected: verifies selected tokens excluded from completions
  - TestCompletionSelection: verifies selecting completion adds to command
  - TestCompletionSelectionWithPartial: verifies partial replacement (fo → focus)
  - TestSnapshotWithCompletions: verifies completions render with categories and indicator
- green | 2026-01-13T19:30:00Z | go test ./internal/barcli
  - All existing tests pass; TokenCategories wired through tui2.go

## Implementation notes
- Added `completion` struct with Value, Category, Description fields
- Reuses `bartui.TokenCategory` and `bartui.TokenOption` types from existing package
- `updateCompletions()` performs fuzzy matching:
  - Extracts partial word from command input via `getFilterPartial()`
  - Iterates all categories/options, skipping already-selected tokens
  - Uses substring matching (`strings.Contains`) for fuzzy filter
  - Matches against both Value and Slug fields
- `selectCompletion()` applies selection:
  - Removes partial being typed from command
  - Appends selected token value with trailing space
  - Updates tokens list and refreshes completions
- Completion navigation:
  - Up/Down arrows change `completionIndex`
  - Tab/Enter selects current completion
- Rendering:
  - Shows completions with `▸` indicator for current selection
  - Displays category label next to each option
  - Truncates list with "... +N more" when exceeding pane height
- `tui2.go` updated to pass `BuildTokenCategories(grammar)` to bartui2

## Files modified
- `internal/bartui2/program.go` — Added completion type, fuzzy matching, selection, rendering
- `internal/bartui2/program_test.go` — Added 6 new tests for completion functionality
- `internal/barcli/tui2.go` — Wire TokenCategories from grammar to bartui2.Options
