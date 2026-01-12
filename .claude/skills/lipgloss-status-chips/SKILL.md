---
name: lipgloss-status-chips
description: Render compact status pills, progress chips, and counters with Lip Gloss, including hover/focus affordances.
---

# Lip Gloss Status Chips

## Use this skill when
- Showing queue length or todo progress
- Creating toggleable pills that can expand into detailed lists
- Highlighting “warning/success/error” states inline

## Workflow

1. **Base style**  
   ```go
   func pill(base lipgloss.Style, label string, focused bool) string {
     style := base.Padding(0, 1)
     if focused {
       style = style.Bold(true).Border(lipgloss.RoundedBorder()).BorderForeground(primary)
     } else {
       style = style.Border(lipgloss.HiddenBorder())
     }
     return style.Render(label)
   }
   ```

2. **Progress text**  
   Combine icons and counts using theme colors.

   ```go
   spinner := "..." // or Bubbles spinner view
   content := fmt.Sprintf("%s To-Do %d/%d", spinner, done, total)
   ```

3. **Expansion**  
   When a pill is selected, render an expanded list below:

   ```go
   details := lipgloss.JoinVertical(
     lipgloss.Left,
     pillRow,
     strings.Join(todoLines, "\n"),
   )
   ```

4. **Keyboard focus**  
   Maintain separate state for “panel focused” vs “pill focused” so you can highlight correctly during navigation.

5. **Gradients / animations**  
   Use `lipgloss.Style.Foreground` gradient helpers to create dynamic arrows or bars.

## Tips

- Keep line width under the terminal width by truncating with an ellipsis (`ansi.StringWidth`, `ansi.Truncate`).
- Use accessible glyphs (✓, •, …) so the UI works without color.
