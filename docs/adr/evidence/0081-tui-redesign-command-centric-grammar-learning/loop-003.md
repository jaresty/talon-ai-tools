## Behaviour outcome
Implement token tree visualization with category labels using lipgloss/tree component.

## Commands executed

### Tests
- green | 2026-01-13T20:00:00Z | go test ./internal/bartui2
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
  - TestGetCategoryForToken: verifies category lookup by token value
  - TestTokenTreeWithCategoryLabels: verifies tree shows categories and rounded enumerator
  - TestTokenTreeEmptyShowsNoCount: verifies header shows just "TOKENS" when empty
- green | 2026-01-13T20:00:00Z | go test ./internal/barcli
  - All existing tests pass

## Implementation notes
- Upgraded `lipgloss` from v0.9.1 to v1.1.0 to access `lipgloss/tree` package
- Added `getCategoryForToken()` method to look up category label for any token value
  - Performs case-insensitive matching against both Value and Slug fields
  - Returns empty string for unknown tokens
- Token tree rendering now uses `lipgloss/tree` component:
  - `tree.RoundedEnumerator` produces curved `╰─` glyphs
  - Each token shown as "Category: value" format with styled components
- Header shows token count: "TOKENS (2)" when tokens selected, "TOKENS" when empty
- Styles:
  - `categoryStyle`: subtle gray (color 244) for category labels
  - `tokenStyle`: green (color 78) for token values

## Files modified
- `internal/bartui2/program.go` — Added tree import, getCategoryForToken(), updated renderTokensPane() to use lipgloss/tree
- `internal/bartui2/program_test.go` — Added TestGetCategoryForToken, TestTokenTreeWithCategoryLabels, TestTokenTreeEmptyShowsNoCount
- `go.mod` — Upgraded lipgloss and dependencies
