# Bubble Tea Overlay Orchestration Reference

This reference captures the detailed workflow for building multi-pane Bubble Tea applications that host overlay stacks (dialogs, sheets, toasts) while leaning on Lip Gloss utilities for composition.

## Root Model Contract

A responsive root model always tracks the latest `tea.WindowSizeMsg` values and exposes helper methods so child components can size themselves lazily.

```go
import tea "github.com/charmbracelet/bubbletea"

type RootModel struct {
  width, height int
  overlays     OverlayStack
  routes       RouteState
  theme        Styles
}

func (m RootModel) Size() (int, int) {
  return m.width, m.height
}

func (m RootModel) Init() tea.Cmd {
  return tea.Batch(initRoutes(m.routes), m.overlays.Init())
}

func (m RootModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
  switch msg := msg.(type) {
  case tea.WindowSizeMsg:
    m.width = msg.Width
    m.height = msg.Height
    return m.handleResize(msg)
  }
  return m.routeMessage(msg)
}
```

Forward the size message into any child model that implements a `SetSize(width, height)` method. This keeps breakpoint logic close to the component that needs it.

## Layout Baseline

Lean on helpers from `lipgloss-layout-utilities` and `lipgloss-theme-foundations` for spacing, gutters, and palette choices.

```go
sidebar := m.theme.Frame.Width(32).Render(renderSidebar(m.routes))

main := lipgloss.JoinVertical(
  lipgloss.Left,
  renderHeader(m.routes),
  renderContent(m.routes),
  renderFooter(m.routes),
)

baseView := lipgloss.JoinHorizontal(
  lipgloss.Top,
  sidebar,
  m.theme.Frame.Width(m.width-32).Render(main),
)
```

When defining responsive variants, keep the breakpoint math declarative:

```go
func (m RootModel) layoutVariant() layoutVariant {
  width, _ := m.Size()
  switch {
  case width < 100:
    return layoutCompact
  case width < 160:
    return layoutMedium
  default:
    return layoutWide
  }
}
```

## Overlay Stack Manager

The modal stack lives behind a narrow interface so you can swap implementations. Components push models with domain-specific IDs; the manager forwards input only to the top entry.

```go
type Overlay interface {
  Init() tea.Cmd
  Update(tea.Msg) (Overlay, tea.Cmd)
  View() string
  ID() string
  Position(size tea.WindowSizeMsg) (x, y int)
}

type OverlayStack struct {
  overlays []Overlay
}

func (s *OverlayStack) Push(o Overlay) tea.Cmd {
  for i := range s.overlays {
    if s.overlays[i].ID() == o.ID() {
      s.overlays[i] = o
      return o.Init()
    }
  }
  s.overlays = append(s.overlays, o)
  return o.Init()
}

func (s *OverlayStack) Update(msg tea.Msg) (tea.Cmd, bool) {
  if len(s.overlays) == 0 {
    return nil, false
  }
  top := s.overlays[len(s.overlays)-1]
  updated, cmd := top.Update(msg)
  s.overlays[len(s.overlays)-1] = updated
  return cmd, true
}

func (s *OverlayStack) Close(id string) {
  for i := len(s.overlays) - 1; i >= 0; i-- {
    if s.overlays[i].ID() == id {
      s.overlays = append(s.overlays[:i], s.overlays[i+1:]...)
      return
    }
  }
}
```

Emit rich domain messages from overlays when they close so the root model can reconcile state.

## Rendering Layers

Compose overlays with `lipgloss.NewCompositor`. Keep the compositor construction in one function so you can add scrims, blur effects, or focus highlights consistently.

```go
func (m RootModel) render() string {
  base := lipgloss.NewLayer(m.renderBase())
  layers := []lipgloss.Layer{base}

  for _, overlay := range m.overlays.Items() {
    x, y := overlay.Position(tea.WindowSizeMsg{Width: m.width, Height: m.height})
    layer := lipgloss.NewLayer(overlay.View()).X(x).Y(y)
    layers = append(layers, layer)
  }

  return lipgloss.NewCompositor(layers...).Render()
}
```

Include a dimmed background layer whenever overlays are active to clarify focus. Reference `lipgloss-theme-foundations` for scrim colors.

## Input Routing

Short-circuit the root `Update` cycle when overlays consume a message:

```go
if cmd, handled := m.overlays.Update(msg); handled {
  return m, cmd
}
```

Only after the overlay manager declines a message should you forward it to the active route or focused component. Couple this with the input helpers from `bubbles-form-inputs` and `bubbles-select-dialog` to ensure consistent focus handling.

## Chrome Accounting

Reserve vertical space for persistent chrome (status bars, command palettes) so overlays stay centered regardless of footers.

```go
const statusHeight = 1
const commandPaletteHeight = 3

func (m RootModel) overlayOrigin() (int, int) {
  usableHeight := m.height - statusHeight - commandPaletteHeight
  return (m.width-60)/2, statusHeight + (usableHeight-16)/2
}
```

Expose these gutter values from a shared theme or layout package so other components reuse them.

## Checklist

- [ ] Capture the latest `tea.WindowSizeMsg` and forward to children
- [ ] Provide a reusable overlay stack manager with `Push`/`Close`
- [ ] Render base UI first, then composite overlays with scrim layers
- [ ] Block input while overlays are active
- [ ] Centralize gutter and chrome measurements to avoid overlapping content
- [ ] Emit domain messages from overlays for clean state transitions
