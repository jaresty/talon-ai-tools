# Lip Gloss List Rendering Reference

Build bullet, numbered, or custom enumerated lists for terminal summaries.

## Basic Usage

```go
import "github.com/charmbracelet/lipgloss/list"

l := list.New(
  "Ctrl+P opens palette",
  "Tab cycles suggestions",
  "Enter applies tokens",
)
```

- Items can be strings or nested lists (`list.New("Category", list.New("scope", "method"))`).

## Enumerators

```go
l = l.Enumerator(list.Bullet)   // • item
l = l.Enumerator(list.Numeric)  // 1. item
l = l.Enumerator(list.Roman)    // I. item
```

Supply a custom enumerator when you need selection arrows:

```go
func highlightCurrent(idx int) string {
  if idx == current {
    return "→"
  }
  return "•"
}

l = l.Enumerator(list.EnumeratorFunc(highlightCurrent))
```

## Styling

```go
enumeratorStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("99")).MarginRight(1)
itemStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("246"))

l = l.
  EnumeratorStyle(enumeratorStyle).
  ItemStyle(itemStyle)
```

Render with `listView := l.String()` and wrap inside layout styles for padding or width constraints.

## Nested Lists

Combine enumerators:

```go
outer := list.New("Shortcuts", list.New("Primary", "Ctrl+P"))
outer = outer.Enumerator(list.Numeric)
```

Ensure nested items have shorter text to avoid overflow.

## Integration Tips

- Use `lipgloss-layout-utilities` to dock lists next to tables or previews.
- Manage focus externally; rerender selected items with bold or color changes.
- When mixing with overlays, keep list width constant so overlays do not shift.
