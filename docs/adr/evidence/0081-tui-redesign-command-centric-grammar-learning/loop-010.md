## Behaviour outcome
Implement Shift+Tab backward navigation, Ctrl+K clear all, persona_preset category, and preset auto-fill.

## Commands executed

### Tests
- green | 2026-01-14T02:00:00Z | go test ./internal/bartui2
  - All 49 tests pass (4 new tests added)
  - TestShiftTabGoesToPreviousStage: verifies Shift+Tab goes to previous stage without removing tokens
  - TestCtrlKClearsAllTokens: verifies Ctrl+K clears all tokens and restarts
  - TestPresetAutoFillsOtherCategories: verifies preset selection auto-fills voice/audience/tone
- green | 2026-01-14T02:00:00Z | go test ./internal/barcli
  - All existing tests pass
- green | 2026-01-14T02:00:00Z | go test ./internal/bartui
  - All existing tests pass

## Implementation notes
- Added `Fills` field to `bartui.TokenOption` for auto-fill metadata
- Added `buildPersonaPresetOptions()` to `tui_tokens.go` to build preset category with Fills
- Added `Fills` field to `completion` struct in `program.go`
- Updated `updateCompletions()` to include Fills from TokenOption
- Updated `selectCompletion()` to apply Fills (auto-fill other categories)
- Added `goToPreviousStage()` for Shift+Tab navigation
- Added `clearAllTokens()` for Ctrl+K reset
- Updated key handlers for Shift+Tab and Ctrl+K

## Files modified
- `docs/adr/0081-tui-redesign-command-centric-grammar-learning.md` - Added Shift+Tab and Ctrl+K documentation
- `internal/bartui/tokens.go` - Added Fills field to TokenOption
- `internal/barcli/tui_tokens.go` - Added buildPersonaPresetOptions with Fills
- `internal/bartui2/program.go` - Added Shift+Tab, Ctrl+K, and preset auto-fill
- `internal/bartui2/program_test.go` - Added 4 new tests
