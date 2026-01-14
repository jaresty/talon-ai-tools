## Behaviour outcome
Add viewport scroll to preview and result panes using bubbles/viewport component for long content.

## Commands executed

### Tests
- green | 2026-01-13T22:30:00Z | go test ./internal/bartui2
  - All 35 existing tests pass
  - TestPreviewViewportScrolling: verifies Ctrl+D/Ctrl+U scroll preview
  - TestResultViewportScrolling: verifies result viewport scrolls
  - TestHotkeyBarShowsScrollShortcut: verifies ^U/^D hint in hotkey bar
  - TestPreviewShowsScrollPercentage: verifies scroll percentage indicator
- green | 2026-01-13T22:30:00Z | go test ./internal/barcli
  - All existing tests pass

## Implementation notes
- Added `bubbles/viewport` import
- Added `previewViewport` and `resultViewport` fields to model
- Initialized viewports in `newModel()` with default dimensions
- Updated `WindowSizeMsg` handler to resize viewports dynamically
- Added scroll key handlers:
  - `Ctrl+U` / `PgUp`: scroll up half page
  - `Ctrl+D` / `PgDown`: scroll down half page
- Added `getPreviewPaneHeight()` helper for consistent height calculation
- Updated all preview/result content setters to also call `viewport.SetContent()`
- Updated `renderPreviewPane()` to use viewport.View() and show scroll percentage
- Updated `renderResultPane()` to use viewport.View() and show scroll percentage
- Updated hotkey bar:
  - Normal mode: added `^U/^D: scroll`
  - Result mode: changed to shorter labels (`^Y: copy`, `^R: back`) with scroll hint
- Added 4 new tests for viewport scrolling functionality

## Files modified
- `internal/bartui2/program.go` — Added viewport import, viewport fields, scroll handlers, viewport rendering
- `internal/bartui2/program_test.go` — Fixed existing tests, added 4 new viewport tests
