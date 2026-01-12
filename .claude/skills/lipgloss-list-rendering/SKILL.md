name: lipgloss-list-rendering
description: Build bullet, numbered, and nested lists with lipgloss/list for structured TUI summaries.
---

# Lip Gloss List Rendering

## Use this skill when
- Displaying recent palette history entries, shortcuts, or step-by-step instructions
- Building nested bullet lists in a Bubble Tea panel
- Highlighting selected items with consistent styling

## Workflow

1. **Import the list package**
   ```go
   import "github.com/charmbracelet/lipgloss/list"
   ```

2. **Create a list with items**
   ```go
   l := list.New("Ctrl+P opens palette", "Tab cycles suggestions", "Enter applies tokens")
   ```
   - Items can be `string` or nested lists: `list.New("Category", list.New("scope", "method"))`.

3. **Choose an enumerator**
   ```go
   l = l.Enumerator(list.Bullet)     // • item
   l = l.Enumerator(list.Numeric)    // 1. item
   l = l.Enumerator(list.Roman)      // I. item
   ```
   - Use `list.Tree` for tree-like indentation with branch connectors.

4. **Style enumerators and items**
   ```go
   enumeratorStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("99")).MarginRight(1)
   itemStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("246"))

   l = l.
     EnumeratorStyle(enumeratorStyle).
     ItemStyle(itemStyle)
   ```
   - For selected items, render separately with a different style (e.g., `itemStyle.Copy().Bold(true)`).

5. **Render the list**
   ```go
   listView := l.String()
   ```
   - The list supports multi-line items and will indent appropriately.

6. **Custom enumerators**
   ```go
   func highlightCurrent(items list.Items, idx int) string {
     if idx == currentIndex {
       return "→"
     }
     return "•"
   }

   l = l.Enumerator(highlightCurrent)
   ```
   - Custom enumerators let you include state (selection, status icons).

## Tips
- Combine with `lipgloss-layout-utilities` by wrapping the rendered list in a styled block (`lipgloss.NewStyle().Width(...).Render(listView)`).
- When interleaving with tables or other components, ensure margins/padding are set on the outer block to maintain spacing.
- For interactive lists, manage focus separately and rerender with the selected style to show which item has keyboard focus.
