## Behaviour outcome
Implement position-aware Tab completion for the CLI command input mode, enabling category-specific completions when typing `category=partial`.

## Commands executed

### Tests
- green | 2026-01-13T17:45:00Z | go test ./internal/bartui -count=1
  - All unit tests pass including new TestPositionAwareTabCompletion
- green | 2026-01-13T17:45:00Z | scripts/tools/run-tui-expect.sh --all
  - 8 tests passed: clipboard-history, environment-allowlist, focus-cycle, launch-status, sticky-summary, token-command-history, token-palette-history, token-palette-workflow

## Implementation notes
- Extended `getCompletionsForPartial` to detect `category=partial` format
- When `=` is present in the partial, extract category slug and complete values for that category only
- New `getCompletionsForCategory` returns completions in `category=value` format
- Added `categorySlugFromCategory` helper to extract slug from TokenCategory
- Position-aware behavior:
  - `static=to` → completes to `static=todo`
  - `scope=` → shows `scope=focus`, `scope=breadth`
  - `to` → shows `todo` (all categories)
- Added comprehensive unit test `TestPositionAwareTabCompletion` covering:
  - Partial without `=` completes from all categories
  - Empty partial returns all options
  - `static=` returns category-specific completions with prefix
  - `static=to` filters to matching values
  - `scope=` returns scope category options
