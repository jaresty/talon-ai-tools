## Behaviour outcome
Improve preset UX: when removing a preset via Backspace, automatically remove all tokens it auto-filled.

## Commands executed

### Tests
- red | 2026-01-14T06:00:00Z | go test ./internal/bartui2 -run TestRemovingPresetRemovesAutoFilledTokens
  - Test fails: auto-filled tokens not removed with preset
  - voice/audience/tone remained after removing coach preset
- green | 2026-01-14T06:30:00Z | go test ./internal/bartui2 ./internal/barcli ./internal/bartui
  - All tests pass (63 tests in bartui2, 1 new test added)
  - TestRemovingPresetRemovesAutoFilledTokens: verifies cascade removal works

## Implementation notes
- Added `autoFillSource map[string]string` to track which token caused each auto-fill
- Modified `selectCompletion()` to record source when auto-filling
- Modified `removeLastToken()` to:
  - Skip auto-filled tokens when finding last token to remove
  - Call `removeAutoFilledBy()` to cascade-remove after removing source
- Added `removeAutoFilledBy(sourceKey)` helper that removes all tokens filled by a source
- Updated `clearAllTokens()` to also clear autoFillSource

## Files modified
- `internal/bartui2/program.go` - Added autoFillSource tracking, modified removeLastToken(), added removeAutoFilledBy()
- `internal/bartui2/program_test.go` - Added TestRemovingPresetRemovesAutoFilledTokens test
