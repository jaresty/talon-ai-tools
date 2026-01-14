## Behaviour outcome
Fix truncated descriptions by storing full descriptions in completion struct and adding selected item description area.

## Commands executed

### Tests
- red | 2026-01-14T03:00:00Z | go test ./internal/bartui2 -run TestSelectedItemDescriptionArea
  - Test fails: expected view to contain full description
  - Descriptions were pre-truncated to 40 chars in updateCompletions()
- green | 2026-01-14T03:30:00Z | go test ./internal/bartui2
  - All 53 tests pass (1 new test added)
  - TestSelectedItemDescriptionArea: verifies full description appears in selected item area
- green | 2026-01-14T03:30:00Z | go test ./internal/barcli
  - All existing tests pass
- green | 2026-01-14T03:30:00Z | go test ./internal/bartui
  - All existing tests pass

## Implementation notes
- Root cause: `updateCompletions()` was calling `truncate(opt.Description, 40)` when building completions
- Fix: Store full `opt.Description` in completion struct; truncate only during display
- Added `wrapText()` helper to wrap long descriptions in selected item area
- Fixed layout calculations to properly account for border (2 chars) and padding (2 chars)
- Selected item description area shows full description below completion list with "─" separator

## Files modified
- `internal/bartui2/program.go` - Fixed updateCompletions() to store full description, added wrapText() helper, fixed layout calculations (boxWidth vs contentWidth)
- `internal/bartui2/program_test.go` - Added TestSelectedItemDescriptionArea test
