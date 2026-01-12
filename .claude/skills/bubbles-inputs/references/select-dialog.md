# Bubbles Select Dialog Reference

Use this reference to build searchable command palettes, grouped pickers, or keyboard-driven selects using `bubbles/list` and `bubbles/textinput` components.

## Core Building Blocks

### List Items
Implement the `list.Item` interface to expose title, description, and filterable text.

```go
type item struct {
  title string
  desc  string
}

func (i item) Title() string       { return i.title }
func (i item) Description() string { return i.desc }
func (i item) FilterValue() string { return i.title + " " + i.desc }
```

### List Model Setup

```go
items := []list.Item{
  item{title: "Run Command", desc: "Execute selected action"},
  item{title: "Open File", desc: "Launch picker"},
}

delegate := list.NewDefaultDelegate()
lst := list.New(items, delegate, width, height)
lst.Title = "Commands"
lst.SetShowStatusBar(false)
lst.SetFilteringEnabled(true)
```

Enable filtering and customize prompts:

```go
lst.FilterInput.Placeholder = "Filter actions"
lst.FilterInput.Focus()
```

## Update Loop

Handle keyboard shortcuts before delegating to the list:

```go
switch msg := msg.(type) {
case tea.KeyMsg:
  switch msg.String() {
  case "enter":
    if choice, ok := lst.SelectedItem().(item); ok {
      return m.handleSelection(choice)
    }
  case "esc":
    return m.close()
  }
}

var cmd tea.Cmd
lst, cmd = lst.Update(msg)
return m, cmd
```

Use `list.Select` when you need to jump to a specific index after filtering.

## Grouped or Sectioned Lists

For grouped options, either:
- Encode section headers as `Item`s that render differently via the delegate, or
- Maintain multiple `list.Model` instances and swap between tabs using `lipgloss-components` status chips as tab indicators.

## Styling

Reference `lipgloss-theme-foundations` for colors. Delegate styles control title, pagination, and item rendering:

```go
delegate.Styles.SelectedTitle = theme.Title.Copy().Foreground(theme.Primary)
delegate.Styles.SelectedDesc = theme.Muted
lst.Styles.Title = theme.Title
lst.Styles.FilterPrompt = theme.SubtleText
```

Consider shrinking `SetShowHelp(true)` for palettes by providing custom help text at the bottom of the overlay.

## Accessibility

- Provide unique filter values so fuzzy matching differentiates items.
- Keep title + description short; overflow can be trimmed via `ansi.Truncate` in the delegate.
- Support `ctrl+n`/`ctrl+p` or arrow keys for users accustomed to alternate navigation schemes.

## Integration Notes

- Embed the list inside an overlay via `bubbletea-overlays`. Reserve space for filter input, results pane, and optional right rail (preview pane).
- Combine with `markdown-diff-rendering` or other preview components by rendering the list and preview side-by-side using `lipgloss-layout-utilities`.
