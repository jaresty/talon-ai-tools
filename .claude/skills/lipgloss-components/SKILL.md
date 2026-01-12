---
name: lipgloss-components
description: Capsules for reusable Lip Gloss widgets (chips, lists, tables, trees) with references for detailed recipes.
---

# Lip Gloss Components (Skill Capsule)

## Use this skill when
- Building reusable UI widgets on top of `lipgloss` to embed inside Bubble Tea layouts.
- You need focused recipes for status chips, enumerated lists, tables, or tree views.
- A task references multiple Lip Gloss component skills and you want a shared entry point.

## Quickstart
- Lean on `lipgloss-theme-foundations` for palette definitions; this capsule focuses on structure and state styling.
- Keep layout math isolated: render each component first, then compose them with `lipgloss-layout-utilities` alongside overlays or forms.
- Maintain keyboard/selection state in your Bubble Tea model and rerender components with the appropriate styles from these references.

## Dive deeper
- `references/status-chips.md` — Pills, progress counters, and focus styling patterns.
- `references/list-rendering.md` — Enumerated lists and custom bullet glyphs.
- `references/table-rendering.md` — Tabular data with borders, zebra stripes, and width guards.
- `references/tree-rendering.md` — Hierarchical views with rounded enumerators and dynamic generation.

## Checklist
- [ ] Component styles sourced from the shared theme.
- [ ] Rendered widgets wrapped with layout constraints before composition.
- [ ] Keyboard focus reflected via bold/border changes when applicable.
- [ ] Accessibility considered (color fallback glyphs, truncation, readable labels).
