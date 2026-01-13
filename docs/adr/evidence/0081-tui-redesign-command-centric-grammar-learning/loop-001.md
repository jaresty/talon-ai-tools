## Behaviour outcome
Establish `bar tui2` command entry point with basic three-pane Bubble Tea layout for ADR 0081 redesigned TUI.

## Commands executed

### Tests
- green | 2026-01-13T19:00:00Z | go test ./internal/bartui2
  - TestSnapshotBasicLayout: verifies three-pane structure (TOKENS, COMPLETIONS, PREVIEW headers)
  - TestSnapshotEmptyTokens: verifies empty state messaging
  - TestParseTokensFromCommand: verifies token extraction from command input
  - TestParseTokensFromCommandEmpty: verifies empty command handling
- green | 2026-01-13T19:00:00Z | go test ./internal/barcli
  - All existing tests pass; tui2.go integrates without breaking existing functionality

## Implementation notes
- Created new `internal/bartui2/` package for redesigned TUI (clean slate per ADR 0081)
- Three-pane vertical layout:
  - Pane 1: Command input with `bar build ` prefix, using bubbles textinput
  - Pane 2: Tokens (left) & Completions (right) split horizontally
  - Pane 3: Preview with truncation for long content
  - Pane 4: Hotkey bar with available actions
- `bar tui2` command routed in `app.go` via `runTUI2()` in `tui2.go`
- Reuses existing `Build()` and `RenderPlainText()` for preview generation
- Lip Gloss styles: rounded borders, color-coded headers, dim placeholder text
- `Snapshot()` function for deterministic testing (like bartui)

## Files created/modified
- `internal/bartui2/program.go` (new) — Bubble Tea model with three-pane layout
- `internal/bartui2/program_test.go` (new) — Unit tests for layout and token parsing
- `internal/barcli/tui2.go` (new) — Command entry point wiring
- `internal/barcli/app.go` (modified) — Added `tui2` command routing
