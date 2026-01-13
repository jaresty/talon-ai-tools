## Behaviour outcome
Highlight the most recent history entry with ADR 0077 typography cues using a tick-based expiry mechanism so operators can immediately spot the active event inside the sidebar and the UI auto-refreshes when the highlight should clear.

## Commands executed

### go test ./internal/bartui
- red | 2026-01-13T05:40:00Z | exit 1
  - helper:diff-snapshot=1 file changed, 72 insertions(+)
  - summary: TestHistoryHighlightRecentEntry and TestHistoryHighlightExpires fail to compile due to missing historyHighlightExpiredMsg type and model fields.

### go test ./internal/bartui
- green | 2026-01-13T05:55:00Z | exit 0
  - helper:diff-snapshot=3 files changed, 154 insertions(+), 19 deletions(-)
  - summary: exercises the new highlight helper, tick-based expiry, and regression coverage for history rendering.

### go test ./cmd/bar/...
- green | 2026-01-13T05:56:00Z | exit 0
  - helper:diff-snapshot=3 files changed, 154 insertions(+), 19 deletions(-)
  - summary: confirms CLI wiring remains stable after the bartui layout adjustments.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-13T05:58:00Z | exit 0
  - helper:diff-snapshot=3 files changed, 154 insertions(+), 19 deletions(-)
  - summary: expect transcripts show the history row and confirm existing clipboard/history scenarios remain stable (excluding pre-existing token-palette-workflow failure unrelated to this change).

## Implementation notes
- Implemented hybrid approach: tick-based expiry for proper UI refresh combined with time-check at render time for correctness
- Added `historyHighlightActive` flag and `historyHighlightSequence` counter to model
- `recordPaletteHistory` now returns `tea.Cmd` that schedules tick for highlight expiry
- `shouldHighlightHistoryEntry` checks both the active flag AND time elapsed for robustness
- Updated expect test regex to handle sidebar word-wrapping
