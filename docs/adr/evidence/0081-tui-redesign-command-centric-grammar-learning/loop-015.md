## Behaviour outcome
Implement undo/redo for token selections using Ctrl+Z and Ctrl+Y.

## Commands executed

### Tests
- red | 2026-01-14T07:00:00Z | go test ./internal/bartui2 -run "TestUndo|TestRedo"
  - 5 tests fail: undo/redo not implemented
- green | 2026-01-14T07:30:00Z | go test ./internal/bartui2 ./internal/barcli ./internal/bartui
  - All tests pass (68 tests in bartui2, 5 new tests added)
  - TestUndoTokenSelection: verifies Ctrl+Z undoes last selection
  - TestRedoTokenSelection: verifies Ctrl+Y redoes after undo
  - TestUndoMultipleSelections: verifies multiple undos work
  - TestUndoShowsToast: verifies toast feedback
  - TestUndoNothingToUndo: verifies edge case handling

## Implementation notes
- Added stateSnapshot struct to capture token state
- Added undoStack and redoStack to model
- Added saveStateForUndo() called before selectCompletion()
- Added undo() and redo() methods to restore state
- Ctrl+Z triggers undo, Ctrl+Y triggers redo (or copy result if in result mode)
- History limited to 50 entries
- Redo stack cleared when new action is taken

## Files modified
- `internal/bartui2/program.go` - Added undo/redo infrastructure and handlers
- `internal/bartui2/program_test.go` - Added 5 new tests
