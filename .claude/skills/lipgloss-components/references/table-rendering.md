# Lip Gloss Table Rendering Reference

Render structured data using `github.com/charmbracelet/lipgloss/table`.

## Setup

```go
import "github.com/charmbracelet/lipgloss/table"

rows := [][]string{
  {"Category", "Token", "Active"},
  {"scope", "system", "yes"},
  {"method", "analysis", "no"},
}

t := table.New().Rows(rows...)
```

Append rows incrementally with `t.Row(...)` when streaming data.

## Borders & Styles

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

Use `MarkdownBorder`, `RoundedBorder`, or `ASCIIBorder` for alternate looks.

## Headers & Column Widths

```go
t = t.Headers("CATEGORY", "TOKEN", "ACTIVE")
t = t.ColumnWidths(12, 18, 8)
```

Set widths to keep columns aligned even with uneven content. Measure the final output via `lipgloss.Width` if needed.

## Rendering

```go
tableView := t.Render()
```

Wrap with layout styles to enforce max widths or alignment.

## Integration Tips

- Treat tables as read-only; editing inline is awkward with multiline cells.
- Truncate cells with `ansi.Truncate` before adding them when necessary.
- Match colors with `lipgloss-theme-foundations` so tables honor the active palette.
- When scrolling is needed, render the table then pass it into a viewport component.
