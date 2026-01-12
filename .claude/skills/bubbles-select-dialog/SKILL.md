---
name: bubbles-select-dialog
description: Build filterable selects, command palettes, and grouped lists with Bubbles’ list and text input primitives.
---

# Bubbles Select Dialog

## Use this skill when
- Creating a searchable command palette
- Letting users choose models, sessions, or options from grouped lists
- Implementing keyboard-driven selects

## Workflow

1. **Set up dependencies**  
   ```go
   import (
     "github.com/charmbracelet/bubbles/list"
     "github.com/charmbracelet/bubbles/textinput"
     "github.com/charmbracelet/bubbletea"
   )
   ```

2. **List item implementation**  
   ```go
   type item struct{ title, desc string }
   func (i item) FilterValue() string { return i.title + " " + i.desc }
   func (i item) Title() string       { return i.title }
   func (i item) Description() string { return i.desc }
   ```

3. **Create the list**  
   ```go
   items := []list.Item{
     item{title: "Run Command", desc: "Execute selected action"},
     item{title: "Open File", desc: "Launch picker"},
   }
   delegate := list.NewDefaultDelegate()
   lst := list.New(items, delegate, width, height)
   lst.Title = "Commands"
   ```

4. **Add filter input**  
   `list.Model` includes a `FilterInput`; enable filtering with `list.SetFilteringEnabled(true)` and style the prompt via `delegate.Styles`.

5. **Handle updates**  
   ```go
   switch msg := msg.(type) {
   case tea.KeyMsg:
     switch msg.String() {
     case "enter":
       choice := lst.SelectedItem().(item)
       // handle selection
     case "esc":
       // close dialog
     }
   }
   lst, cmd := lst.Update(msg)
   ```

6. **Group sections (optional)**  
   Use Bubbles’ section support or maintain multiple lists and tabs if you need “System / Custom / Prompts” buckets.

## Tips

- Disable list navigation keys you override elsewhere by toggling delegate shortcuts.
- For multi-column layouts, render the list inside a Lip Gloss box and add sidebars or help text separately.
