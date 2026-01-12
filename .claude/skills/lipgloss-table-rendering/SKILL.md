name: lipgloss-table-rendering
description: Render tables with lipgloss/table for terminal UIs, including borders, column widths, and row styling.
---

# Lip Gloss Table Rendering

## Use this skill when
- Presenting structured data (history, presets, shortcuts) in a Bubble Tea view
- Showing aligned columns with borders or markdown-style output
- Reusing CLI-like tabular summaries inside the TUI

## Workflow

1. **Set up the table import**
   ```go
   import "github.com/charmbracelet/lipgloss/table"
   ```

2. **Define rows or incremental row additions**
   ```go
   rows := [][]string{
     {"Category", "Token", "Active"},
     {"scope", "system", "yes"},
     {"method", "analysis", "no"},
   }

   t := table.New().Rows(rows...)
   ```
   - Alternatively, call `t.Row(...)` to append rows one at a time.

3. **Choose a border and styles**
   ```go
   borderColor := lipgloss.Color("99")
   headerStyle := lipgloss.NewStyle().Bold(true).Align(lipgloss.Center)
   cellStyle := lipgloss.NewStyle().Padding(0, 1)

   t = t.
     Border(lipgloss.NormalBorder()).
     BorderStyle(lipgloss.NewStyle().Foreground(borderColor)).
     StyleFunc(func(row, col int) lipgloss.Style {
       switch row {
       case table.HeaderRow:
         return headerStyle
       case row % 2:
         return cellStyle.Foreground(lipgloss.Color("245"))
       default:
         return cellStyle.Foreground(lipgloss.Color("241"))
       }
     })
   ```
   - Use `Border(lipgloss.MarkdownBorder())` for GitHub/markdown-style tables or `lipgloss.ASCIIBorder()` for `+---+` borders.

4. **Set headers and column widths**
   ```go
   t = t.Headers("CATEGORY", "TOKEN", "ACTIVE")
   t = t.ColumnWidths(12, 18, 8)
   ```
   - Column widths prevent ragged columns when text varies.

5. **Render the table**
   ```go
   tableView := t.Render()
   ```
   - Use `lipgloss.Width(tableView)` in tests to confirm alignment.

6. **Integration tips**
   - When embedding in a layout, wrap with `lipgloss.NewStyle().Width(width).Render(tableView)` to keep the table within the desired column.
   - For scrollable content, render the table first, then split lines into a viewport widget.

## Tips
- Treat tables as read-only; keep editing interactions elsewhere to avoid multiline cursor issues.
- If you need truncated cells, pre-process the strings with `ansi.Truncate()` before passing them to the table.
- Match color/theme choices with `lipgloss-theme-foundations` so tables respect the active palette.
