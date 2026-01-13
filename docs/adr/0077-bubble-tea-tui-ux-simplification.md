Accepted — Bubble Tea TUI interaction simplification and typography cues (2026-01-12)

## Context
- ADR 0072 delivered a two-column Bubble Tea layout that keeps the omnibox, summary strip, palette, and history visible, but the resulting surface exposes overlapping controls and dense copy in the sidebar.
- Operators report cognitive load spikes when multiple affordances compete (inline chips, palette commands, clipboard actions, presets) without clear hierarchy or focus guidance.
- History items read as homogeneous bullet lines, making it hard to distinguish clipboard versus token edits during rapid workflows.
- Width-based auto layout toggles between single and dual columns without an operator-controlled override, causing unpredictable reflows in constrained terminals.
- Shortcut discovery still relies on external documentation; the interface provides no built-in cues or cheat sheet summarizing key bindings for the consolidated layout.
- The palette's "select from list" interaction model abstracts the CLI grammar, leaving operators unprepared to use `bar build` directly from the terminal; learning transfer is weak because the TUI hides the `category=value` syntax.

## Decision
- Converge redundant controls so each core action has a single primary affordance (e.g., keep inline chips for token toggles, expose clipboard copy solely from the command preview) while parking advanced search in an optional palette fold-out.
- Replace the palette's "select from list" interaction with a **CLI command input mode** where operators edit the actual `bar build` command directly: the input shows the live command (e.g., `bar build static=assumption minimal`), Tab cycles through completions at the cursor position, and category/option panes remain visible as scaffolding. This teaches the CLI grammar because the syntax you type is the syntax you'll use in the terminal, and muscle memory transfers directly.
- Restructure the sidebar with clearly labeled sections (Compose, History, Presets) that default to the most common view and support progressive disclosure through collapsible toggles persisted in model state.
- Introduce operator-driven layout controls: add a keyboard toggle to hide/show the sidebar and persist the preference, while exposing the current focus zone via breadcrumbs in the status strip.
- Align the root Bubble Tea model with the layout composition patterns defined in our Bubble Tea skills: persist the latest `tea.WindowSizeMsg`, recompute main/sidebar widths, and render columns with Lip Gloss width constraints so subject, result, and token viewports wrap predictably on narrow terminals.
- Enrich history entries with event metadata (type icon/label, timestamp) and highlight the active row, reducing the need to parse dense text.
- Add an in-app shortcut reference (`Ctrl+?`) rendered as a full-screen overlay (clearing the screen before drawing) and backed by a dialog stack so grouped commands, focus toggles, and section controls can layer without leaving the TUI.
- Provide lightweight feedback for applied palette changes by briefly highlighting affected rows or showing concise toast cues instead of duplicating confirmation text in history.
- Apply typography and spacing cues (section headers, dividers, contrast hierarchy) so the sidebar content is visually scannable across terminal themes.

## Rationale
- The CLI command input mode enables direct learning transfer: operators build commands using the exact `category=value` grammar they'll type in the terminal, Tab completion mimics shell behavior, and the resulting command is immediately copy-pasteable. This bridges the gap between TUI exploration and CLI fluency.
- Eliminating overlapping controls reduces decision fatigue and keeps the main task path obvious, supporting both novice onboarding and expert speed.
- Section headers, collapsible groups, and manual sidebar toggles clarify information architecture, allowing operators to focus on the content they need at a given moment.
- Breadcrumb-style focus indicators make keyboard directionality transparent, preventing disorientation when moving between columns or when the layout changes.
- Metadata-enhanced history entries improve auditability and make error recovery simpler by revealing what action fired and when it happened.
- An embedded shortcut sheet lowers reliance on external docs, keeps guidance versioned with the UI, and aids retention after the simplification refactor.
- Clear typographic hierarchy and transient feedback reinforce trust, letting pilots confirm success without reading long lines or scanning entire history lists.

## Consequences
- The CLI command input mode requires refactoring the palette filter to seed with `bar build ` prefix, implementing cursor-position-aware Tab completion (after `=` completes values, elsewhere completes categories), and updating status messages to guide the new interaction.
- `internal/bartui/program.go` requires structural changes to consolidate controls, manage collapsible sections, render focus breadcrumbs, and style typography via Lip Gloss.
- Layout helpers now rely on persisted terminal dimensions; ensure `layoutViewports` responds to `tea.WindowSizeMsg` in `internal/bartui/program.go` with targeted tests in `internal/bartui/program_test.go`.
- Model state must extend to track sidebar visibility, section expansion, last-focused column, and history metadata; associated tests in `internal/bartui/program_test.go` need updates and new coverage.
- Expect fixtures and snapshots (e.g., `cmd/bar/testdata/tui_smoke.json`, `tests/integration/tui/cases/*.exp`) must be regenerated to reflect the simplified layout, section headers, and history formatting.
- New commands and overlays (sidebar toggle, cheat sheet) demand shortcut documentation updates and CLI help alignment in `internal/barcli` packages.
- Additional styles may require theme audits to ensure headers and metadata remain legible across supported palettes.

## Validation
- `go test ./internal/bartui` to cover focus breadcrumbs, sidebar toggles, history metadata, collapsible sections, and layout recomputation on `tea.WindowSizeMsg`.
- `go test ./cmd/bar/...` to ensure CLI integration, snapshot fixtures, and help text remain synchronized.
- `scripts/tools/run-tui-expect.sh --all` with updated cases verifying default collapsed sections, metadata-rich history entries, sidebar toggle behavior, and cheat sheet overlay.
- `python3 -m pytest _tests/test_bar_completion_cli.py` if new shortcuts or flags affect CLI coordination layers referenced by ADR 0075.

## Residuals (2026-01-13 audit)
The following gaps were identified during adversarial audit and are intentionally deferred:

- **Compose section not collapsible**: History (Ctrl+H) and Presets (Ctrl+S) support collapse toggles, but the Compose section remains always-visible with no equivalent toggle. This is acceptable because Compose contains the primary token state operators need during editing; hiding it would remove essential context. Add a toggle only if operators report the section creates noise during non-token workflows.
- **Focus breadcrumbs omit sidebar visibility state**: The status strip shows `Focus: Subject ▸ [TOKENS] ▸ Command ▸ Result` but does not indicate whether the sidebar is visible or hidden. Operators can infer sidebar state from the layout itself; adding explicit text (e.g., `· Sidebar hidden`) would clutter the already-dense status line. Revisit if operators report confusion about why token categories aren't visible.
- **Last-focused column not persisted across sessions**: `focusBeforePalette` tracks runtime focus for palette close restoration, but focus state does not persist to disk. Session-to-session focus persistence was not an ADR requirement; the TUI resets to Subject focus on launch, which matches expected behavior. Add persistence only if operators request "resume where I left off" functionality.

## Follow-up
- ~~Implement the CLI command input mode: refactor the palette filter to display and edit the live `bar build` command, add cursor-position-aware Tab completion, and keep category/option panes as visual scaffolding for discoverability.~~ (Done: loops 014-017)
- ~~Implement the interaction simplification and typography updates across Bubble Tea models and views in upcoming loops, referencing ADR 0072 as the baseline.~~ (Done: loops 001-013)
- ~~Apply the Bubble Tea dialog stacking helper to any additional overlays or modals introduced after the shortcut reference ships.~~ (Done: loop-009)
- Refresh operator documentation and quickstart guides once the simplified layout ships, keeping screenshots and shortcut summaries in sync.
- Monitor expect harness output for regression drift in section order or typography cues, expanding tests as additional sidebar sections are introduced.
- Evaluate the need for further accessibility refinements (contrast, focus indicators) after the initial simplification lands.
