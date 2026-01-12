---
name: bubbletea-overlays
description: Coordinate Bubble Tea layouts and overlay stacks while delegating detailed recipes to bundled references.
---

# Bubble Tea Overlays (Skill Capsule)

## Use this skill when
- A Bubble Tea screen needs both persistent layout regions and transient overlays.
- You must ensure window-size messages and focus routing flow through a shared overlay manager.
- The work can lean on Lip Gloss helpers plus dedicated Bubble Tea input skills.

## Quickstart
- Capture the latest `tea.WindowSizeMsg` in your root model and forward sizing data to children.
- Compose base panes with helpers from `lipgloss-layout-utilities` and styles from `lipgloss-theme-foundations`.
- Manage overlays with a slice-backed stack that blocks background updates while active.
- Composite views using `lipgloss.NewCompositor`, adding scrims or offset math per breakpoint.
- Emit domain messages from overlays so application state settles before the stack pops.

## Dive deeper
- Follow the full playbook in `references/overlays.md` for struct definitions, layout variants, compositor layering, and chrome sizing heuristics.
- Pair with:
  - `bubbletea-dialog-stacking` for overlay model patterns and message contracts.
  - `bubbles-form-inputs` / `bubbles-select-dialog` to handle focus within modal content.
  - `lipgloss-status-chips` or `lipgloss-table-rendering` for reusable widgets inside overlays.

## Checklist
- [ ] Window size stored and forwarded downstream
- [ ] Overlay stack gates `Update` before background routes
- [ ] Base view rendered before overlay layers
- [ ] Chrome gutters reserved to avoid clipping overlays
- [ ] Closure messages handled before removing overlays
