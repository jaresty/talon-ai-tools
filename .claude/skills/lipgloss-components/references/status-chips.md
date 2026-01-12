# Lip Gloss Status Chips Reference

Design pills and progress chips that respond to hover, focus, and selection changes.

## Base Rendering

```go
func pill(base lipgloss.Style, label string, focused bool) string {
  style := base.Padding(0, 1)
  if focused {
    style = style.
      Bold(true).
      Border(lipgloss.RoundedBorder()).
      BorderForeground(primary)
  } else {
    style = style.Border(lipgloss.HiddenBorder())
  }
  return style.Render(label)
}
```

- Call `Padding(0, 1)` for interior spacing.
- Swap borders when the chip is focused vs. inactive.

## Progress + Counters

Combine glyphs with counts to show workload state:

```go
spinner := "…" // integrate bubbles/spinner for long tasks
content := fmt.Sprintf("%s To-Do %d/%d", spinner, done, total)
```

Render the result with `pill()` to keep styling consistent.

## Expanded Details

When pills expand into detail lists, join the child view vertically:

```go
details := lipgloss.JoinVertical(
  lipgloss.Left,
  pillRow,
  strings.Join(todoLines, "\n"),
)
```

Keep expansion widths fixed so overlays do not jump.

## Focus Handling

Distinguish between panel focus (the entire chip row) and chip focus (individual pill). Maintain state such as `focusedChip int` and `panelFocused bool` to decide how to style each row.

## Visual Enhancements

- Use `Foreground` gradients for animated bars or arrows.
- Provide monochrome-safe glyphs (`✓`, `•`, `…`) to keep state obvious without color.

## Accessibility

- Reserve space for truncated labels via `ansi.Truncate` to avoid wrapping.
- Ensure selected vs. focused chips have distinct borders or weights when color is unavailable.
