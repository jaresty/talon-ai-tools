In Progress — Bubble Tea TUI palette and grammar-aligned palette flow (2026-01-11)

## Context
- ADR 0070 introduced the Bubble Tea prompt editor overlaying the existing `bar` CLI, while ADR 0071 compacted the layout for 24–30 row terminals.
- Operator feedback shows the current token palette feels modal, forcing a category selection before freeform search and breaking CLI muscle memory.
- Inline token controls still sprawl vertically, making it hard to see subject text, active selections, and preview output together on shorter terminals.
- We need a smoother flow that keeps the main view usable as a live form while leaving the palette helpful for fast token tweaks.

## Decision
- Treat the primary workspace as a single-page form: subject textarea, inline token rows, destination controls, preview, and command/status panes stacked with minimal context switching.
- Collapse empty token categories into single-line "+ Add …" affordances while keeping active categories expanded as chip rows that can be edited in place so chip density stays readable across themes.
- Replace the modal palette picker with a docked *grammar composer* that behaves like `bar build`: the input always shows `category=value`, Tab/Shift+Tab cycle completions in the same order as the CLI, and Enter commits staged changes. Mirror CLI hints inline so operators learn the grammar cadence.
- Keep the palette docked in a right-side viewport that stays visible while editing, staged tokens remain visible until applied, and keyboard-first flows stay primary. Pointer support is optional; when implemented it must reinforce the CLI command being learned.
- Add focus breadcrumbs, transient feedback, and a single-step undo stack tailored to token changes so pilots can experiment quickly without losing context. Favor simple Lip Gloss styling unless a Charm “skill” directly reinforces the learning objective.
- Expose a palette history toggle (`Ctrl+H`) for recent token adjustments and command invocations, echoing shell history search patterns and aiding recall. History entries should show the exact CLI command that would reproduce the action.
- Keep CLI summaries focused on grammar tokens and destinations; omit the raw subject/prompt text (skip `--prompt`) to prevent overwhelming the command line representation.

### Relevant Charm skills
- `lipgloss-theme-foundations` — establish text/background/hover styles for chips, status strip, and the grammar composer.
- `lipgloss-components` — reuse status chips, tables, lists, and tree widgets for palette summaries and history views.
- `lipgloss-layout-utilities` — assemble main + sidebar columns, manage widths, and place sticky status strips.
- `bubbletea-overlays` — manage Bubble Tea model/state split, overlay stacks, and viewport resizing alongside Lip Gloss joins.
- `bubbletea-dialog-stacking` / `bubbles-inputs` — reuse modal, select, and input patterns if the grammar composer needs staged forms or focused dialogs.

### Typography & information architecture recommendations
- Use `lipgloss-theme-foundations` to define a consistent text scale: body copy (~11–12 cols), small meta text for status strip, and bold/uppercase for section headers. Keep max line length ~70 columns in the main pane to avoid wrapping.
- Apply `Inline(true)` for chip rows so categories read as single lines with clear spacing; reserve double-line chips for multi-token explanations.
- Group related controls with subtle borders (`lipgloss.RoundedBorder` in the theme palette) so subject, tokens, preview, and history read as distinct sections.
- Provide a dedicated typography style for CLI hints (monospaced font or distinct color) to reinforce the learning context.
- Ensure breadcrumb/status text uses consistent casing and spacing; align breadcrumbs above the composer, status strip beneath, and preserve a single baseline grid (2-cell vertical rhythm) across sections.

## Rationale
- Inline tokens and a single-page flow keep subject, tokens, and preview aligned, reducing scroll churn and maintaining context during edits.
- A sticky status strip maintains awareness of presets, divergence, destinations, and corresponding CLI commands, supporting operators who switch between GUI and scripts.
- The grammar composer trains the same micro-interactions as `bar build`, letting pilots build the CLI muscle memory they will rely on in terminals.
- Breadcrumbs, undo, and history affordances encourage exploration while providing predictable focus recovery and literal CLI copy/paste cues.
- Charm skills (Bubbles, Lip Gloss, etc.) are supporting tools; reference the relevant Charm skills for patterns and helpers, but treat them as guidance—not mandates—when they advance the learning experience.

## Consequences
- View/render helpers must reorganise layout grids to keep the inline token pane scrollable while preserving the subject and preview above the fold.
- Palette logic must accept grammar-style `category=value` parsing, deterministic Tab cycling, staged application, and history storage without blocking the Bubble Tea event loop.
- Snapshot fixtures and UI tests need updates to capture the sticky status strip, docked grammar composer, inline feedback, and breadcrumb indicators.
- Shortcut documentation and in-app help overlays must reflect the grammar hints, staged application flow, undo, and history toggle.
- Styling must ensure the docked palette and summary strip remain legible across terminal themes, focusing the design on CLI reinforcement versus decorative telemetry.

## Validation
- Extend `go test ./internal/bartui/...` coverage for inline chip editing, staged palette changes, undo stack, and breadcrumb focus transitions.
- Update `bar tui --fixture …` snapshots to verify the docked grammar composer, summary strip, and inline feedback across typical terminal sizes.
- Run `python3 -m pytest _tests/test_bar_completion_cli.py` to keep CLI hints synchronised with the exposed grammar shortcuts and command summaries.
- Add expect coverage that mirrors the typical CLI workflow (type fragment → Tab → type fragment → Tab) so regressions are caught immediately.

## Follow-up
- Refresh docs, quickstart transcripts, and pilot playbook sections with the revised grammar-first palette flow and inline token editing guidance.
- Coordinate with ADR 0075 (CLI coordination layer refactor) so the grammar composer shortcuts and palette history stay in sync with the accepted `internal/barcli/cli` contracts.
- Monitor the two-column layout via `scripts/tools/run-tui-expect.sh --all` after palette or preset tweaks to catch regressions early.
- Gather pilot feedback after release to tune Tab defaults (e.g., staged apply behaviour, history length, category hinting).
- Add a viewport focus toggle (e.g., maximise Result or Subject panes with a shortcut) so pilots can page multi-line command output or subject drafts without distraction.
- When refreshing history/shortcut views, reuse the `lipgloss-components` recipes (tables, lists, trees) so the palette mirrors CLI artifacts with consistent styling.
- Pursue interaction simplification and typography cues outlined in ADR 0077.


## Anti-goals
- Do not re-litigate the core Bubble Tea architecture established in ADR 0070.
- Avoid introducing mouse-only interactions; keyboard parity and CLI-style shortcuts remain mandatory.
- Do not attempt to replace the existing command palette entirely; this ADR evolves it without removing established affordances.
