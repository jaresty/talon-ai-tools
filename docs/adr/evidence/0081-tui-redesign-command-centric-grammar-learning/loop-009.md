## Behaviour outcome
Implement backward navigation via Backspace, add persona stages, and add category=value escape hatch.

## Commands executed

### Tests
- green | 2026-01-14T01:00:00Z | go test ./internal/bartui2
  - All 45 tests pass (6 new tests added)
  - TestBackspaceNavigatesBackward: verifies Backspace removes token and returns to that stage
  - TestParseEscapeHatch: verifies category=value parsing
  - TestApplyEscapeHatch: verifies escape hatch adds token to specified category
  - TestStageOrderIncludesPersonaStages: verifies persona stages are at beginning
  - TestStageDisplayNameForPersonaStages: verifies display names for persona stages
- green | 2026-01-14T01:00:00Z | go test ./internal/barcli
  - All existing tests pass

## Implementation notes
- Updated `stageOrder` to include persona stages at the beginning:
  - intent, persona_preset, voice, audience, tone (before static)
- Updated `stageDisplayName()` to handle persona stages
- Added `parseEscapeHatch()` to detect category=value syntax in filter partial
- Added `applyEscapeHatch()` to add token to specified category directly
- Updated Enter key handler to check for escape hatch before selecting completion
- Backward navigation via Backspace already worked (from loop-008) - `removeLastToken()` sets `currentStageIndex` to the removed token's stage
- After all stages complete, typing category=value and pressing Enter allows overriding any selection

## Files modified
- `docs/adr/0081-tui-redesign-command-centric-grammar-learning.md` - Updated design for backward navigation, full stage order, escape hatch
- `internal/bartui2/program.go` - Added persona stages, escape hatch parsing and application
- `internal/bartui2/program_test.go` - Added 6 new tests for new functionality
