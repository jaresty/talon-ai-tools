---
name: bubbles-inputs
description: Coordinate Bubble Tea text inputs, text areas, and command palettes using shared focus and filtering patterns.
---

# Bubbles Inputs (Skill Capsule)

## Use this skill when
- You need cohesive patterns for multi-field forms, chat editors, or keyboard-driven selects.
- A task involves managing focus, shortcuts, or filtering across Bubbles text inputs and lists.
- You want to reuse shared styling and layout helpers across overlays or root layouts.

## Quickstart
- Capture user keystrokes at the model level before delegating to `textinput`, `textarea`, or `list` so that global shortcuts win.
- Maintain a focus controller that can advance/blurs inputs and toggles between list filtering vs. selection intents.
- Feed layout dimensions from the parent Bubble Tea model (see `bubbletea-overlays`) so forms and palettes adapt across breakpoints.
- Reuse theme styles from `lipgloss-theme-foundations` to keep input, filter, and list accents consistent.

## Dive deeper
- See `references/form-inputs.md` for multi-field forms, mode toggles, and accessibility notes.
- See `references/select-dialog.md` for command palette wiring, list delegates, and grouped selections.
- Pair with `bubbletea-overlays` when inputs live inside modal stacks, and with `lipgloss-layout-utilities` to position labels, previews, or side panels.

## Checklist
- [ ] Global shortcuts handled before delegating to inputs/lists.
- [ ] Focus manager keeps `textinput`/`textarea` states synchronized.
- [ ] Filter prompts and selection commits share theme-aware styling.
- [ ] Overlay or layout container reserves space for filter bars, result panes, and help rows.
