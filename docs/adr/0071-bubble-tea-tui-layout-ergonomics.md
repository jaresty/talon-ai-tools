Accepted — Bubble Tea TUI layout ergonomics refinement (2026-01-09)

## Context
- ADR 0070 established the Bubble Tea prompt editor baseline, but early review highlighted readability issues when viewed on 24–30 row terminals.
- The token summary currently expands every category, repeating “(none selected)” lines that push the subject and command panes below the fold.
- Shortcut guidance appears as dense paragraphs, mixing unrelated controls and increasing cognitive load for quick lookup.
- Result feedback lands after multiple instructional blocks, so command status can disappear from view precisely when pilots need it.
- Without stronger typographic hierarchy, headings, status indicators, and actionable controls blend together, making the UI harder to scan.

## Decision
- Introduce a compact status strip across the top that surfaces active tokens, preset name/divergence, environment allowlist state, and an equivalent CLI command on one line where possible.
- Collapse token categories that have no selections into single-line previews with expand/collapse affordances, while keeping active categories expanded with concise chip rows.
- Reformat shortcut references into grouped lists (inputs, tokens, palette, presets, environment, command lifecycle) with consistent indentation and short action-first labels.
- Elevate the result pane with a dedicated heading, divider, and compact summary (status icon, exit code, stdin source, environment) that remains visible without scrolling.
- Apply stronger typographic cues—bold section headers, hanging indentation for lists, and intentional vertical spacing—to differentiate instructional copy from interactive controls.
- Keep the help overlay synchronized with the new layout, presenting the same grouped shortcut structure instead of duplicating long-form prose.

## Rationale
- Compacting the status information preserves the subject/command editors and result pane above the fold on small terminals, reducing cursor travel.
- Collapsing empty token categories eliminates redundant filler while still hinting at available axes, improving scannability.
- Grouped shortcut lists let operators find the control they need quickly, supporting both novice discovery and expert recall.
- Highlighting result status ensures command outcomes stay obvious, reinforcing trust and keeping follow-up actions (e.g., copy stdout) discoverable.
- Typographic hierarchy provides faster visual parsing without relying solely on color, benefiting diverse terminal themes and accessibility needs.

## Consequences
- Snapshot fixtures (e.g., `cmd/bar/testdata/tui_smoke.json`) must be regenerated to capture the revised layout and condensed copy.
- Lip Gloss styling needs to reflect the new hierarchy while remaining legible across default terminal color palettes.
- Navigation logic must preserve keyboard-first workflows as categories collapse and expand, including predictable focus return paths.
- Documentation and quickstart captures referencing the previous layout require refresh to match the new information architecture.

## Validation
- Extend `go test ./cmd/bar/...` and `go test ./internal/bartui/...` with assertions covering collapsed categories, status strip rendering, and result-pane visibility cues.
- Update the deterministic `bar tui --fixture` snapshot harness to ensure the new layout remains stable.
- Run `python3 -m pytest _tests/test_bar_completion_cli.py` to keep CLI completions aligned after exposing any new flags or help entries.

## Follow-up
- Implement the layout changes within `internal/bartui` view/render helpers and adjust Lip Gloss styling accordingly.
- Refresh `docs/usage` snippets and the pilot playbook with screenshots or transcripts that reflect the compact layout.
- Monitor operator feedback post-launch to determine whether additional presets, palette affordances, or color themes are necessary.

## Anti-goals
- Do not introduce new functional capabilities beyond layout, typography, and information hierarchy adjustments described here.
- Do not replace the Bubble Tea stack or abandon the snapshot fixture workflow established in ADR 0070.
- Avoid adding mouse-exclusive interactions; keyboard parity must remain intact throughout the updates.
