name: lipgloss-layout-utilities
description: Compose Lip Gloss views with horizontal/vertical joins, placement helpers, and width management for Bubble Tea layouts.
---

# Lip Gloss Layout Utilities

## Use this skill when
- You need to dock sidebars or palettes next to a main view using Lip Gloss
- Aligning content with consistent widths/heights before handing it to Bubble Tea
- Centering, right-aligning, or otherwise positioning blocks inside whitespace

## Workflow

1. **Define core styles with width/height guards**
   ```go
   mainStyle := lipgloss.NewStyle().Width(mainWidth).Padding(0, 1)
   sidebarStyle := lipgloss.NewStyle().Width(sidebarWidth).Padding(0, 1)
   ```
   - Use `Width`/`Height` (or `MaxWidth`/`MaxHeight`) to constrain each panel before joining.

2. **Render each panel independently**
   ```go
   mainView := mainStyle.Render(renderMain())
   sidebarView := sidebarStyle.Render(renderSidebar())
   ```
   - When you need to reference sizes later, keep the rendered strings around.

3. **Join columns or rows**
   ```go
   layout := lipgloss.JoinHorizontal(
     lipgloss.Top,
     mainView,
     lipgloss.NewStyle().Width(gap).Render(""),
     sidebarView,
   )
   ```
   - `JoinHorizontal`/`JoinVertical` accept alignment constants (`Top`, `Center`, `Bottom`) or a float ratio.
   - Insert styled gap strings when you need consistent spacing.

4. **Align paragraphs inside fixed regions**
   ```go
   status := lipgloss.NewStyle().
     Width(totalWidth).
     Align(lipgloss.Center).
     Render(statusLine)
   ```
   - Switch between `Align(lipgloss.Left|Center|Right)` as needed.

5. **Place content in whitespace**
   ```go
   footer := lipgloss.Place(
     containerHeight,
     containerWidth,
     lipgloss.Right,
     lipgloss.Bottom,
     footerView,
   )
   ```
   - Use `PlaceHorizontal`/`PlaceVertical` for one-dimensional alignment.

6. **Measure blocks when computing dynamic sizes**
   ```go
   w, h := lipgloss.Size(mainView)
   sidebarWidth = maxWidth - w - gap
   ```
   - `lipgloss.Width`/`Height` or `Size` help keep layouts responsive to runtime content.

7. **Inline rendering for single-line elements**
   ```go
   pill := baseStyle.Inline(true).MaxWidth(20).Render(label)
   ```
   - `Inline(true)` ignores margins/padding when you need tight chips inside another block.

## Tips
- Call `lipgloss.Width/Height` after rendering to account for ANSI-aware measurements.
- Keep joins symmetric: if the sidebar collapses, replace it with an empty string so layout width remains stable.
- When mixing adaptive colors or themes, reuse styles from `lipgloss-theme-foundations` and layer layout helpers on top.
- Test joins with `strings.Split(layout, "\n")` in unit tests to assert column counts or maximum widths.
