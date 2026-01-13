## Behaviour outcome
Fix TUI completion order to match CLI completion order (intent, persona, static, then axes).

## Commands executed

### Tests
- green | 2026-01-13T18:00:00Z | go test ./internal/bartui -count=1
  - All unit tests pass including new TestCompletionOrderMatchesCLI
- green | 2026-01-13T18:00:00Z | scripts/tools/run-tui-expect.sh --all
  - 8 tests passed: clipboard-history, environment-allowlist, focus-cycle, launch-status, sticky-summary, token-command-history, token-palette-history, token-palette-workflow

## Implementation notes
- Added `completionCategoryOrder` map mirroring CLI's `stageOrder` values from `completion.go`
- Order values: intent(16), voice(14), audience(13), tone(12), static(11), completeness(9), scope(8), method(7), form(6), channel(5), directional(4)
- Modified `getCompletionsForPartial` to sort category states by order before collecting completions
- Uses `sort.SliceStable` with descending order (higher values first)
- Added comprehensive unit test `TestCompletionOrderMatchesCLI` verifying:
  - Intent tokens appear before Static tokens
  - Static tokens appear before Scope tokens
  - Order matches CLI completion behavior
