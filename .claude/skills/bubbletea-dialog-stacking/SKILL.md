---
name: bubbletea-dialog-stacking
description: Manage modal dialogs in Bubble Tea using a stack, forwarding events and layering views.
---

# Bubble Tea Dialog Stacking

## Use this skill when
- Multiple modal dialogs can be opened (command palette, permission prompts)
- You need to block background components while a dialog is active
- Overlays must be composited with Lip Gloss layers

## Workflow

1. **Dialog interface**  
   ```go
   type Dialog interface {
     Init() tea.Cmd
     Update(tea.Msg) (Dialog, tea.Cmd)
     View() string
     Position() (x, y int)
     ID() string
   }
   ```

2. **Dialog manager**  
   Keep a slice stack and forward `Update` only to the top dialog. Allow reusing a dialog if its ID is already in the stack.

   ```go
   type dialogManager struct {
     dialogs []Dialog
   }

   func (m *dialogManager) Update(msg tea.Msg) (tea.Cmd, bool) {
     if len(m.dialogs) == 0 {
       return nil, false
     }
     top := m.dialogs[len(m.dialogs)-1]
     updated, cmd := top.Update(msg)
     m.dialogs[len(m.dialogs)-1] = updated
     return cmd, true
   }
   ```

3. **Open/close messages**  
   Define `OpenDialogMsg{Dialog}` and `CloseDialogMsg{ID}`; your root model processes these and manipulates the stack.

4. **Rendering**  
   In `View()`, render the base UI, then map dialogs to `lipgloss.NewLayer`. Use each dialog’s `Position()` to place it accurately.

5. **Input handling**  
   Prevent background components from reacting while a dialog is active by early-returning when the dialog manager handled the message.

## Tips

- Give dialogs access to the terminal dimensions via `tea.WindowSizeMsg` so they can scale to different sizes.
- For confirm/cancel flows, ensure dialogs emit a message your main model can handle after closing.
