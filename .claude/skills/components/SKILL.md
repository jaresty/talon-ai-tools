---
name: components
description: Directory of UI component skills, pointing to Bubbles inputs and Lip Gloss presentation recipes.
---

# Components (Index)

Load this when you need to find component-oriented skills quickly. It acts as a map:

- **`bubbles-inputs`** — Interactive input patterns (multi-field forms, command palettes). See `references/form-inputs.md` and `references/select-dialog.md` within that skill for detailed recipes.
- **`lipgloss-components`** — Presentation widgets (status chips, enumerated lists, tables, tree views). Each widget has its own reference file under that capsule.
- **`bubbletea-overlays`** — Layout and overlay orchestration, useful when components live inside modal stacks or layered views.

## When to use this index
- The user asks for “components” or you’re unsure which skill covers the requested widget.
- A task spans both Bubble Tea input state and Lip Gloss rendering; start here, then load the specific capsule(s).

## Tips
- Combine `bubbles-inputs` and `lipgloss-components` for end-to-end flows: inputs capture data, Lip Gloss renders summaries or previews.
- Keep theme and layout helpers (`lipgloss-theme-foundations`, `lipgloss-layout-utilities`) in mind; most component recipes rely on them for consistent styling.
