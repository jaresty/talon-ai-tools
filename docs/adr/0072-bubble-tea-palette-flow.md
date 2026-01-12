Proposed — Bubble Tea TUI palette and inline editing refinements (2026-01-11)

## Context
- ADR 0070 introduced the Bubble Tea prompt editor overlaying the existing `bar` CLI, while ADR 0071 compacted the layout for 24–30 row terminals.
- Operator feedback shows the current token palette feels modal, forcing a category selection before freeform search and breaking CLI muscle memory.
- Inline token controls still sprawl vertically, making it hard to see subject text, active selections, and preview output together on shorter terminals.
- We need a smoother flow that keeps the main view usable as a live form while leaving the palette helpful for fast token tweaks.

## Decision
- Treat the primary workspace as a single-page form: subject textarea, inline token rows, destination controls, preview, and command/status panes stacked with minimal context switching.
- Collapse empty token categories into single-line “+ Add …” affordances while keeping active categories expanded as chip rows that can be edited in place, styled with Lip Gloss flex primitives so chip density stays readable across themes.
- Replace the modal palette category picker with a docked omnibox that accepts `category=value` input (matching `bar build` syntax), tab-cycles suggestion columns, and mirrors CLI completion shortcuts (Tab for forward, Shift+Tab for reverse) using Bubbles input and list components to inherit our CLI key bindings.
- Keep the palette docked in a right-side viewport that stays visible while editing, allowing staged multiple token changes before hitting `Enter` to apply, and wire the region through BubbleZone so pointer focus and chip clicks mirror keyboard targets.
- Add focus breadcrumbs, transient confirmation toasts, and `Ctrl+Z` undo for the most recent token change so pilots can experiment quickly without losing context, employing Harmonica spring transitions for toast/undo animation consistency.
- Expose a palette history toggle (`Ctrl+H`) for recent token adjustments and command invocations, echoing shell history search patterns and aiding recall while learning the grammar by backing the view with the Bubbles list model we already ship.
- Render inline telemetry for staged tokens with ntcharts sparkline blocks tucked beneath the omnibox so operators see impact trends without sacrificing the subject preview.


## Rationale
- Inline tokens and a single-page flow keep subject, tokens, and preview aligned, reducing scroll churn and maintaining context during edits.
- A sticky status strip maintains awareness of presets, divergence, destinations, and corresponding CLI commands, supporting operators who switch between GUI and scripts.
- A docked omnibox palette lets pilots reuse CLI-style completion habits without modal interruptions, improving discovery and velocity.
- Breadcrumbs and undo affordances encourage exploration while providing predictable focus recovery, important when the TUI replaces tab-completion muscle memory.
- Palette history and staged edits reduce cognitive load when adjusting multiple tokens or replaying frequent combinations.

## Consequences
- View/render helpers must reorganize layout grids to keep the inline token pane scrollable while preserving the subject and preview above the fold.
- Palette logic must accept freeform `category=value` parsing, Tab cycling, staged application, and history storage without blocking the Bubble Tea event loop.
- Snapshot fixtures and UI tests need updates to capture the sticky status strip, docked palette viewport, confirmation toasts, and breadcrumb indicators.
- Shortcut documentation and in-app help overlays must reflect the new omnibox commands, staged application flow, undo, and history toggle.
- Styling must ensure the docked palette and summary strip remain legible across terminal themes, including focus highlights for breadcrumbs and chips.

## Validation
- Extend `go test ./internal/bartui/...` coverage for inline chip editing, staged palette changes, undo stack, and breadcrumb focus transitions.
- Update `bar tui --fixture …` snapshots to verify the docked palette, summary strip, and inline confirmation messages across typical terminal sizes.
- Run `python3 -m pytest _tests/test_bar_completion_cli.py` to keep CLI hints synchronized with the exposed palette shortcuts and command summaries.

## Follow-up
- Implement viewport refactors to house the docked palette and ensure PgUp/PgDn/Home/End map to the appropriate scroll targets.
- Refresh docs, quickstart transcripts, and pilot playbook sections with the new palette flow and inline token editing guidance.
- Coordinate with ADR 0075 (CLI coordination layer refactor) so the docked omnibox shortcuts and palette history stay in sync with the accepted `internal/barcli/cli` contracts.
- Add expect harness coverage for the new clipboard/undo/destination history entries alongside the docked omnibox layout refactor.
- Gather pilot feedback after release to tune omnibox defaults (e.g., staged apply behavior, history length, category hinting).

## Anti-goals
- Do not re-litigate the core Bubble Tea architecture established in ADR 0070.
- Avoid introducing mouse-only interactions; keyboard parity and CLI-style shortcuts remain mandatory.
- Do not attempt to replace the existing command palette entirely; this ADR evolves it without removing established affordances.
