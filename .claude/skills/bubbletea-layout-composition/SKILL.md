---
name: bubbletea-layout-composition
description: Compose Bubble Tea views with Lip Gloss layout helpers, handling full-screen resizing and overlay layering.
---

# Bubble Tea Layout Composition

## Use this skill when
- Building page-level layouts (sidebars, headers, footers)
- Switching between compact/expanded viewports
- Stacking overlays like dialogs or popovers

## Workflow

1. **Maintain window size in your model**  
   ```go
   type model struct {
     width, height int
     showOverlay   bool
     overlayView   string
     styles        Styles // from the theme skill
   }
   
   func (m *model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
     switch msg := msg.(type) {
     case tea.WindowSizeMsg:
       m.width = msg.Width
       m.height = msg.Height
     }
     …
   }
   ```

2. **Split layout using Lip Gloss joins**  
   ```go
   sidebar := m.styles.Base.
     Width(30).
     Render(renderSidebar())
   
   mainContent := lipgloss.JoinVertical(
     lipgloss.Left,
     renderHeader(),
     renderBody(),
     renderFooter(),
   )
   
   baseView := lipgloss.JoinHorizontal(
     lipgloss.Top,
     sidebar,
     m.styles.Base.Width(m.width-30).Render(mainContent),
   )
   ```

3. **Handle overlays with layers**  
   ```go
   view := lipgloss.NewCompositor(
     lipgloss.NewLayer(baseView),
   )
   if m.showOverlay {
     overlay := renderModal()
     view = lipgloss.NewCompositor(
       lipgloss.NewLayer(baseView),
       lipgloss.NewLayer(overlay).X((m.width-50)/2).Y((m.height-10)/2),
     )
   }
   return view.Render()
   ```

4. **Leave space for footers/status bars**  
   Deduct footer height when positioning interactive regions so they never overlap.

## Tips

- Keep component sizing logic (`SetSize`) close to the component; your root model just forwards window size messages.
- When creating responsive variants, define breakpoints (e.g. `if m.width < 120 { use compact layout }`).
