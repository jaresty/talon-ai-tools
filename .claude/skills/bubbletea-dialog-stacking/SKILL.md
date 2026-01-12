---
name: bubbletea-dialog-stacking
description: Pointer to the Bubble Tea overlays skill and reference material for stack-based dialogs.
---

# Bubble Tea Dialog Stacking (Pointer)

For full guidance on overlay orchestration load **`bubbletea-overlays`** and read `references/overlays.md` within that skill. Pair it with:

- `lipgloss-layout-utilities` to align modal shells and backdrop scrims
- `bubbles-inputs` for focus handling across forms, palettes, and list-driven dialogs
- `lipgloss-components` when dialogs display reusable rendered widgets

## Quick reminders
- Model each dialog or sheet as a Bubble Tea program implementing `Init`, `Update`, and `View` plus a stable `ID()`.
- Push overlays onto the shared stack and allow the root manager (defined in `references/overlays.md`) to gate `Update` before background routes fire.
- Emit domain messages on close (`ConfirmDeleteMsg`, `CancelMsg`) so the root model reconciles state prior to popping the stack.

👉 Use this pointer when the task mentions “dialog stacking” explicitly; otherwise start with `bubbletea-overlays` to get the full overlay playbook.
