# Bubbles Form Inputs Reference

Use this reference when building multi-field forms, chat editors, or focused input workflows with Charmbracelet’s `bubbles/textinput` and `bubbles/textarea` components.

## Core Components

### Text Inputs
- Construct via `textinput.New()` and set placeholder, width, and optional character limits.
- Invoke `Focus()` on the active field; blur previous fields to keep cursor state consistent.
- For read-only values (e.g., generated IDs), leave the field blurred and render with a secondary style.

```go
import "github.com/charmbracelet/bubbles/textinput"

ti := textinput.New()
ti.Placeholder = "Project name"
ti.CharLimit = 64
ti.Width = 40
ti.Focus()
```

### Text Areas
- Use `textarea.New()` for multiline editors.
- Configure width/height and placeholder text, and disable line numbers unless editing code snippets.

```go
import "github.com/charmbracelet/bubbles/textarea"

ta := textarea.New()
ta.SetWidth(80)
ta.SetHeight(6)
ta.Placeholder = "Type message…"
ta.ShowLineNumbers = false
```

## Managing Focus Across Fields

Maintain a slice of inputs and track the active index. On navigation keys (`tab`, `shift+tab`, arrow keys), blur the current input before focusing the next.

```go
func (m *model) focusNext(delta int) {
  m.inputs[m.focused].Blur()
  m.focused = (m.focused + delta + len(m.inputs)) % len(m.inputs)
  m.inputs[m.focused].Focus()
}
```

Inside `Update`:

```go
switch msg := msg.(type) {
case tea.KeyMsg:
  switch msg.String() {
  case "tab":
    m.focusNext(+1)
  case "shift+tab":
    m.focusNext(-1)
  case "enter":
    if m.focused == len(m.inputs)-1 {
      return m.submit()
    }
    m.focusNext(+1)
  }
}
```

## Mode Toggles and Attachments

Track supplementary state (e.g., `attachMode`, `deleteMode`). Map chorded shortcuts (`ctrl+r`) to flip those flags and rerender accessory panels.

```go
case "ctrl+r":
  m.attachMode = !m.attachMode
  return m, nil
```

Render attachment previews or toggles adjacent to the focused input using Lip Gloss layout helpers.

## Styling

Apply theme-aware styles via `textinput.Styles{}` or `textarea.Styles{}`.

```go
styles := textinput.Styles{
  Text:       theme.Base.Foreground(theme.Text),
  Placeholder: theme.Subtle,
  Cursor:     theme.Primary,
  Focused:    theme.Base.Copy().Border(theme.PrimaryColor),
}

ti.SetStyles(styles)
```

Allow the root theme to supply sizes so the form adapts to compact vs. wide layouts.

## External Editor Support

For advanced editing, launch `$EDITOR` in a temporary file:

1. Write the current value to a temp file.
2. Use `tea.ExecProcess` to open the editor.
3. Reload the file contents on process exit.

## Accessibility Tips

- Keep placeholders short; rely on labels beside inputs for clarity.
- Provide keyboard-only submission paths (`enter` on final field, `ctrl+s`).
- Announce validation errors inline by styling the offending field with warning colors from `lipgloss-theme-foundations`.
