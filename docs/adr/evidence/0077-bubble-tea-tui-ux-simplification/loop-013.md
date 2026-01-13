## Behaviour outcome
Ensure keyboard shortcut token changes (Enter/Delete on focused tokens) record history entries alongside palette-based changes, completing ADR 0077's history auditability for all token workflows.

## Commands executed

### go test ./internal/bartui
- red | 2026-01-13T06:05:00Z | exit 0 (behavioral gap, not test failure)
  - helper:diff-snapshot=0 files changed
  - summary: tests passed but `toggleCurrentTokenOption` and `removeCurrentTokenOption` did not call `recordPaletteHistory`, leaving history empty for keyboard shortcut token changes.

### go test ./internal/bartui
- green | 2026-01-13T06:08:00Z | exit 0
  - helper:diff-snapshot=1 file changed, 14 insertions(+)
  - summary: after adding `recordPaletteHistory` calls to both functions, all tests pass and keyboard shortcut token changes now appear in history.

### go test ./cmd/bar/...
- green | 2026-01-13T06:09:00Z | exit 0
  - helper:diff-snapshot=1 file changed, 14 insertions(+)
  - summary: CLI wiring remains stable; snapshot fixtures unaffected.

## Implementation notes
- Added `categoryLabel` extraction (matching `applyPaletteSelection` pattern)
- Added `historyEntry` formatting with "→ applied" or "→ removed" suffix
- Called `m.recordPaletteHistory(historyEventKindTokens, historyEntry)` in both code paths
- Fix was included in commit f28d314 alongside loop-012 tick mechanism work
