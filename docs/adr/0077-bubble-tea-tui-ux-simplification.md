Proposed — Bubble Tea TUI interaction simplification and typography cues (2026-01-12)

## Context
- ADR 0072 delivered a two-column Bubble Tea layout that keeps the omnibox, summary strip, palette, and history visible, but the resulting surface exposes overlapping controls and dense copy in the sidebar.
- Operators report cognitive load spikes when multiple affordances compete (inline chips, palette commands, clipboard actions, presets) without clear hierarchy or focus guidance.
- History items read as homogeneous bullet lines, making it hard to distinguish clipboard versus token edits during rapid workflows.
- Width-based auto layout toggles between single and dual columns without an operator-controlled override, causing unpredictable reflows in constrained terminals.
- Shortcut discovery still relies on external documentation; the interface provides no built-in cues or cheat sheet summarizing key bindings for the consolidated layout.

## Decision
- Converge redundant controls so each core action has a single primary affordance (e.g., keep inline chips for token toggles, expose clipboard copy solely from the command preview) while parking advanced search in an optional palette fold-out.
- Restructure the sidebar with clearly labeled sections (Compose, History, Presets) that default to the most common view and support progressive disclosure through collapsible toggles persisted in model state.
- Introduce operator-driven layout controls: add a keyboard toggle to hide/show the sidebar and persist the preference, while exposing the current focus zone via breadcrumbs in the status strip.
- Align the root Bubble Tea model with the layout composition patterns defined in our Bubble Tea skills: persist the latest `tea.WindowSizeMsg`, recompute main/sidebar widths, and render columns with Lip Gloss width constraints so subject, result, and token viewports wrap predictably on narrow terminals.
- Enrich history entries with event metadata (type icon/label, timestamp) and highlight the active row, reducing the need to parse dense text.
- Add an in-app shortcut reference (`Ctrl+?`) rendered as a full-screen overlay (clearing the screen before drawing) that surfaces grouped commands, focus toggles, and section controls without leaving the TUI.
- Provide lightweight feedback for applied palette changes by briefly highlighting affected rows or showing concise toast cues instead of duplicating confirmation text in history.
- Apply typography and spacing cues (section headers, dividers, contrast hierarchy) so the sidebar content is visually scannable across terminal themes.

## Rationale
- Eliminating overlapping controls reduces decision fatigue and keeps the main task path obvious, supporting both novice onboarding and expert speed.
- Section headers, collapsible groups, and manual sidebar toggles clarify information architecture, allowing operators to focus on the content they need at a given moment.
- Breadcrumb-style focus indicators make keyboard directionality transparent, preventing disorientation when moving between columns or when the layout changes.
- Metadata-enhanced history entries improve auditability and make error recovery simpler by revealing what action fired and when it happened.
- An embedded shortcut sheet lowers reliance on external docs, keeps guidance versioned with the UI, and aids retention after the simplification refactor.
- Clear typographic hierarchy and transient feedback reinforce trust, letting pilots confirm success without reading long lines or scanning entire history lists.

## Consequences
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

## Follow-up
- Implement the interaction simplification and typography updates across Bubble Tea models and views in upcoming loops, referencing ADR 0072 as the baseline.
- Evaluate migrating overlay handling to the Bubble Tea dialog stacking skill so future modals can layer cleanly without reflow artefacts.
- Refresh operator documentation and quickstart guides once the simplified layout ships, keeping screenshots and shortcut summaries in sync.
- Monitor expect harness output for regression drift in section order or typography cues, expanding tests as additional sidebar sections are introduced.
- Evaluate the need for further accessibility refinements (contrast, focus indicators) after the initial simplification lands.
