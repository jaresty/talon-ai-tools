## Behaviour outcome
Implement stage-based token progression where tokens are presented in grammar order with inline stage markers.

## Commands executed

### Tests
- green | 2026-01-14T00:00:00Z | go test ./internal/bartui2
  - All 39 tests pass
  - TestSnapshotBasicLayout: now checks for stage header (COMPLETENESS) instead of COMPLETIONS
  - TestFuzzyCompletionAllOptions: now expects 2 completions for static stage
  - TestFuzzyCompletionFiltering: tests filtering within current stage
  - TestFuzzyCompletionExcludesSelected: verifies stage advancement after selection
  - TestCompletionSelection: verifies stage advancement after selecting token
  - TestCompletionSelectionWithPartial: tests partial filtering and selection
  - TestSnapshotWithCompletions: checks for STATIC stage header
- green | 2026-01-14T00:00:00Z | go test ./internal/barcli
  - All existing tests pass

## Implementation notes
- Added `stageOrder` slice defining grammar progression order
- Changed model from `tokens []string` to `tokensByCategory map[string][]string`
- Added `currentStageIndex int` to track position in stage progression
- Added helper methods for stage management:
  - `getCurrentStage()`: returns current stage key
  - `getCategoryByKey()`: finds category by key
  - `isStageComplete()`: checks if stage has max selections
  - `advanceToNextIncompleteStage()`: moves to next incomplete stage
  - `skipCurrentStage()`: skips current stage (Tab key)
  - `getRemainingStages()`: returns names of remaining stages
  - `getAllTokensInOrder()`: returns tokens in grammar order
  - `getCategoryKeyForToken()`: finds category key for token
  - `removeLastToken()`: removes last token in reverse stage order
  - `updatePreview()`: regenerates preview from tokens
  - `rebuildCommandLine()`: reconstructs command in grammar order
- Updated `updateCompletions()` to filter by current stage only
- Updated `selectCompletion()` to add to tokensByCategory and advance stage
- Changed Tab key from select to skip stage
- Updated `renderCommandPane()` with inline stage marker `[Stage?]` and category annotations
- Updated `renderTokensPane()` to show stage name as header and "Then:" hint
- Updated hotkey bar to show "Tab: skip"
- Updated test categories to include MaxSelections field

## Files modified
- `docs/adr/0081-tui-redesign-command-centric-grammar-learning.md` - Updated design for stage-based progression
- `internal/bartui2/program.go` - Major refactoring for stage-based token progression
- `internal/bartui2/program_test.go` - Updated tests to match stage-based behavior
