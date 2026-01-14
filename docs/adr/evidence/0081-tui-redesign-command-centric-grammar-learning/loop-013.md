## Behaviour outcome
Hide preset-filled tokens in copied command by tracking which tokens were auto-filled.

## Commands executed

### Tests
- red | 2026-01-14T05:00:00Z | go test ./internal/bartui2 -run "TestAutoFilledTokensTracked|TestCopiedCommandExcludesAutoFilledTokens|..."
  - Tests fail to compile: model has no field or method isAutoFilled
- green | 2026-01-14T05:30:00Z | go test ./internal/bartui2 ./internal/barcli ./internal/bartui
  - All tests pass (62 tests in bartui2, 4 new tests added)
  - TestAutoFilledTokensTracked: verifies auto-filled tokens are marked
  - TestCopiedCommandExcludesAutoFilledTokens: verifies clipboard excludes auto-filled
  - TestDisplayCommandIncludesAllTokens: verifies display still shows all tokens
  - TestClearAllTokensClearsAutoFillTracking: verifies clear resets tracking

## Implementation notes
- Added `autoFilledTokens map[string]bool` field to model (key format: "category:value")
- Modified `selectCompletion()` to mark tokens as auto-filled when applying Fills
- Added `isAutoFilled(category, value)` helper method
- Added `buildCommandForClipboard()` that excludes auto-filled tokens
- Modified `copyCommandToClipboard()` to use new builder
- Modified `clearAllTokens()` to reset auto-fill tracking
- Updated existing clipboard tests to use InitialTokens instead of setting commandInput directly

## Files modified
- `internal/bartui2/program.go` - Added auto-fill tracking field, isAutoFilled(), buildCommandForClipboard()
- `internal/bartui2/program_test.go` - Added 4 new tests, updated 2 existing clipboard tests
