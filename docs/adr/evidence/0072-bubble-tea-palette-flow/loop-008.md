## Behaviour outcome
Deliver a two-column Bubble Tea layout that keeps the omnibox, status strip, and palette visible side-by-side on sufficiently wide terminals while preserving history/preset affordances.

## Commands executed

### go test ./...
- green | 2026-01-12T05:18:00Z | exit 0
  - helper:diff-snapshot=internal/bartui/program.go, internal/bartui/program_test.go, cmd/bar/testdata/tui_smoke.json
  - coverage: exercises the refactored Lip Gloss layout helpers and updated unit assertions across the bartui package.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T05:19:10Z | exit 0
  - helper:diff-snapshot=tests/integration/tui/tmp/
  - summary: refreshed expect fixtures confirm the docked palette, history bullets, and clipboard status render alongside the omnibox.
