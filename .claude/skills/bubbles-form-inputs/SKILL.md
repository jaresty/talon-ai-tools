---
name: bubbles-form-inputs
description: Use Bubbles text inputs, text areas, and key handling to build multi-field forms and editors.
---

# Bubbles Form Inputs

## Use this skill when
- Building modal forms (API keys, arguments)
- Creating chat editors with multiline support
- Handling attachments or toggles in the editor

## Workflow

1. **Text input basics**  
   ```go
   ti := textinput.New()
   ti.Placeholder = "Project name"
   ti.Focus()
   ti.CharLimit = 64
   ti.Width = 40
   ```

2. **Textarea for multiline editors**  
   ```go
   ta := textarea.New()
   ta.SetWidth(80)
   ta.SetHeight(5)
   ta.Placeholder = "Type message..."
   ta.ShowLineNumbers = false
   ```

3. **Key handling**  
   - Use `textinput.Cursor()` to place the terminal cursor correctly.
   - Map `esc`, `enter`, `tab`, `shift+enter` manually to step through fields or insert newlines.

   ```go
   switch msg.String() {
   case "tab":
     inputs[current].Blur()
     current = (current + 1) % len(inputs)
     inputs[current].Focus()
   case "enter":
     if current == len(inputs)-1 {
       return submitForm()
     }
   }
   ```

4. **Attachment or mode toggles**  
   Track additional state (e.g., `deleteMode bool`) and use key sequences (`ctrl+r`) to switch modes.

5. **Styling**  
   Apply Lip Gloss styles to inputs by calling `ti.SetStyles(textinput.Styles{…})`, reusing your theme colors.

## Tips

- For external editor support, open a temp file and use `tea.ExecProcess` to run `$EDITOR`.
- To show completion popovers (e.g. for “@file” mentions), open a secondary Bubble component when the current word matches your trigger.
