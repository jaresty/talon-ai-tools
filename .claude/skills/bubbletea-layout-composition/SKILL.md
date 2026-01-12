---
name: bubbletea-overlays-layout
description: Orchestrate Bubble Tea root layout, responsive sizing, and overlay stacks while reusing Lip Gloss primitives.
---

# Bubble Tea Layout & Overlay Orchestration

## Use this skill when
- Designing top-level screens that combine persistent panes with transient dialogs
- Coordinating `tea.WindowSizeMsg` handling across nested components
- Mixing Bubble Tea programs with Lip Gloss compositors or Charm overlays

## Core ideas
- **Forward sizing data**: capture the latest `tea.WindowSizeMsg` in the root model, then pass `SetSize(width, height)` into child components so each can react to breakpoints locally.
- **Compose with Lip Gloss helpers**: reuse `lipgloss-layout-utilities` for joins and alignment, `lipgloss-theme-foundations` for shared styles, and `lipgloss-status-chips` or `lipgloss-table-rendering` for reusable widgets.
- **Layer overlays deliberately**: treat dialogs, sheets, and toasts as independent Bubble Tea models that render via `lipgloss.NewLayer` or `lipgloss.NewCompositor` and block background input while active.

## Workflow

1. **Shape the root model**  
   Track `width`, `height`, routing state, and an overlay stack. Provide `Init` helpers that seed child models with the initial size if available (e.g. from `tea.WindowSizeMsg`).

2. **Layout base content**  
   Use `lipgloss.JoinHorizontal` and `JoinVertical` for the structural skeleton. Defer styling to theme helpers (`lipgloss-theme-foundations`) so sizing math stays readable.

3. **Integrate overlays**  
   Maintain a slice-based overlay manager (see `bubbletea-dialog-stacking` skill) that forwards `Update` only to the top-most entry. Render base content first, then map overlays to Lip Gloss layers, adjusting `.X()`/`.Y()` relative to the captured window size.

4. **Route input**  
   When overlays are present, early-return from the root `Update` if the overlay manager handled the message. Otherwise propagate messages to focused child components such as forms (`bubbles-form-inputs`) or selects (`bubbles-select-dialog`).

5. **Account for chrome**  
   Reserve height for status bars or command palettes so overlays never crop essential UI. Keep constants or helper functions for gutter sizes in your theme package.

## References
- `lipgloss-layout-utilities` for layout primitives and responsive joins
- `lipgloss-theme-foundations` for shared color tokens and base styles
- `bubbletea-dialog-stacking` for stack-based dialog and sheet managers
- `bubbles-form-inputs` and `bubbles-select-dialog` for focused input models
