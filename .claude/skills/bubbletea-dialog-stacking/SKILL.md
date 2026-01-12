---
name: bubbletea-dialog-stacking
description: When you need stacked overlays, compose them through the Bubble Tea overlays/layout skill and reuse its manager pattern.
---

# Bubble Tea Dialog Stacking (Pointer)

This skill now defers to **`bubbletea-overlays-layout`** for the complete overlay orchestration workflow. Use it in tandem with:

- `bubbletea-overlays-layout` for managing the root overlay stack and responsive placement
- `lipgloss-layout-utilities` to align modal shells and dimmed backdrops
- `bubbles-form-inputs` and `bubbles-select-dialog` for focused input handling inside dialogs

## How to apply it
- Treat each dialog, sheet, or toast as a Bubble Tea model that implements `Init`, `Update`, and `View`.
- Push models onto the shared overlay stack and let the root model (outlined in `bubbletea-overlays-layout`) gate all input through that stack before touching background components.
- Have dialogs dispatch domain messages (`ConfirmDeleteMsg`, `CancelMsg`, etc.) on close so the root model can update application state.

👉 Jump to `bubbletea-overlays-layout` for detailed sequencing, layering, and sizing guidance. This file stays as a quick reminder that dialog stacking is one facet of the broader overlay workflow rather than a standalone low-level recipe.
