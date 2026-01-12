# ADR-0078 – Bubble Tea Grammar-Learning Overlays and Scaffolds
Status: Proposed
Date: 2026-01-11
Owners: Bubble Tea UX working group

## Context
- ADR 0077 (“Bubble Tea TUI interaction simplification and typography cues”) is reorganizing the sidebar into Compose, History, and Presets sections but intentionally defers how the interface teaches the bar build grammar.
- Expect fixtures (`tests/integration/tui/cases/token-palette-workflow.exp`, `token-palette-history.exp`, `clipboard-history.exp`, etc.) validate palette operations and history logging yet never expose positional grammar slots, invalid state feedback, or parse structure.
- A primary product goal is helping operators internalize the CLI’s positional grammar—orthogonal tokens, slot ordering, and compositional semantics—while staying within Bubble Tea and Charm tooling.
- Bubble Tea, Bubbles, Lip Gloss, and third-party helpers such as `github.com/Encephala/bubbletea-overlay` provide primitives for overlays, structured lists, and staged hints that can surface the grammar without abandoning the existing TUI.

## Problem
- The current TUI describes actions verbosely (“Ctrl+P opens palette”) but does not show which grammar slots are required, optional, or already satisfied; operators must infer the language shape from history text.
- Orthogonality and compositionality remain implicit: tokens appear as plain strings, the subject/command relationship is hidden, and history lacks metadata tying actions to grammar roles.
- There is no feedforward or learning-oriented error handling. Invalid or conflicting token combinations simply fail silently, missing an opportunity to teach the legal expression space.
- Progressive disclosure surfaces sections (history toggle, palette) but the content remains procedural copy instead of structural cues, limiting learnability despite ADR 0077’s layout improvements.

## Decision
- Introduce a grammar slot scaffold rendered inside the sidebar using Bubbles `list.Model` instances styled with Lip Gloss. Each list item maps to a positional slot (e.g., Subject, Token Modifiers, Command). Visual states (solid border = required and empty, dashed = optional, filled = satisfied) make orthogonality explicit.
- Add a Bubble Tea overlay, composed with `github.com/Encephala/bubbletea-overlay`, that presents a concise parse tree/BNF summary of the in-progress prompt. Trigger the overlay via a dedicated gesture (e.g., `Ctrl+/`) and when operators pause, showing how “whole = parts + structure.”
- Replace static status copy with stage-aware guidance using Bubbles `help.Model` and grouped `key.Binding`s. Feedforward hints adapt to the active slot and collapse once the operator demonstrates mastery, reinforcing progressive disclosure.
- Convert invalid combinations or missing required slots into educational modals: schedule a Bubble Tea command that opens an overlay summarizing the rule violation, acceptable substitutions, and a quick action to jump to the relevant slot.
- Extend expect coverage to capture the new scaffolds and overlays: update palette workflows to assert slot state output, add scenarios for overlay invocation, and characterize error-to-instruction flows.

## Implementation Approach
1. **Land ADR 0077 prerequisites** – Complete the remaining loops for sidebar headers, history metadata, and visibility toggles so the scaffold can piggyback on the Compose/History/Presets structure.
2. **Slot scaffold integration** – Introduce Bubbles list models for each sidebar section, apply Lip Gloss styling for state cues, and bind updates to the existing prompt-building state machine.
3. **Parse overlay** – Wrap the base TUI model with an overlay manager (background = current view, foreground = Lip Gloss tree/BNF view). Ensure overlay activation and dismissal compose cleanly with Bubble Tea commands.
4. **Adaptive help and errors** – Replace static status strings with `help.Model` output grouped by grammar stage; implement validation hooks that emit instructional modals on conflict.
5. **Expect and unit coverage** – Author new expect fixtures covering scaffold rendering, overlay toggles, and invalid-state guidance; backfill unit tests around slot-state derivation to keep grammar feedback deterministic.
6. **Documentation alignment** – Update operator docs and the Bubble Tea help surfaces to reference the grammar overlay gesture, reinforcing parity between CLI and TUI learning routes.

## Reference Patterns from Crush
The snippets below are lifted from the temporary Crush checkout so the patterns remain available after removing that repository.

- **Root model orchestration** (source: https://github.com/charmbracelet/crush/blob/main/internal/tui/tui.go)
```go
type appModel struct {
    wWidth, wHeight int
    currentPage     page.PageID
    pages           map[page.PageID]util.Model
    loadedPages     map[page.PageID]bool
    status          status.StatusCmp
}

func (a appModel) Init() tea.Cmd {
    var cmds []tea.Cmd
    if pageModel, ok := a.pages[a.currentPage]; ok {
        cmds = append(cmds, pageModel.Init())
        a.loadedPages[a.currentPage] = true
    }
    cmds = append(cmds, a.status.Init())
    return tea.Batch(cmds...)
}

func (a *appModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    var cmds []tea.Cmd
    switch msg := msg.(type) {
    case tea.KeyboardEnhancementsMsg:
        for id, child := range a.pages {
            updated, cmd := child.Update(msg)
            a.pages[id] = updated
            if cmd != nil {
                cmds = append(cmds, cmd)
            }
        }
        return a, tea.Batch(cmds...)
    case tea.WindowSizeMsg:
        a.wWidth, a.wHeight = msg.Width, msg.Height
        return a, a.handleWindowResize(msg.Width, msg.Height)
    }
    ...
    return a, tea.Batch(cmds...)
}
```

- **Completion popovers** (source: https://github.com/charmbracelet/crush/blob/main/internal/tui/components/completions/completions.go)
```go
type OpenCompletionsMsg struct {
    Completions []Completion
    X, Y        int
    MaxResults  int
}

type completionsCmp struct {
    wWidth, wHeight int
    width, height   int
    x, y            int
    open            bool
    list            listModel
}

func (c *completionsCmp) Update(msg tea.Msg) (util.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case RepositionCompletionsMsg:
        c.x, c.y = msg.X, msg.Y
        c.adjustPosition()
    case OpenCompletionsMsg:
        c.open = true
        c.x, c.y = msg.X, msg.Y
        items := buildItems(msg.Completions)
        c.width = listWidth(items)
        c.height = max(min(maxCompletionsHeight, len(items)), 1)
        return c, tea.Batch(
            c.list.SetItems(items),
            c.list.SetSize(c.width, c.height),
        )
    }
    ...
    return c, nil
}
```

- **Status/help strip** (source: https://github.com/charmbracelet/crush/blob/main/internal/tui/components/core/status/status.go)
```go
type statusCmp struct {
    info       util.InfoMsg
    width      int
    messageTTL time.Duration
    help       help.Model
    keyMap     help.KeyMap
}

func (m *statusCmp) Update(msg tea.Msg) (util.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.WindowSizeMsg:
        m.width = msg.Width
        m.help.SetWidth(msg.Width - 2)
    case util.InfoMsg:
        m.info = msg
        ttl := msg.TTL
        if ttl == 0 {
            ttl = m.messageTTL
        }
        return m, m.clearMessageCmd(ttl)
    case util.ClearStatusMsg:
        m.info = util.InfoMsg{}
    }
    return m, nil
}
```

- **Rich history items** (source: https://github.com/charmbracelet/crush/blob/main/internal/tui/components/chat/messages/messages.go)
```go
type messageCmp struct {
    width   int
    focused bool
    message message.Message
    anim    *anim.Anim
}

func (m *messageCmp) View() string {
    if m.spinning && m.message.ReasoningContent().Thinking == "" {
        m.anim.SetLabel("Thinking")
        return m.style().PaddingLeft(1).Render(m.anim.View())
    }
    switch m.message.Role {
    case message.User:
        return m.renderUserMessage()
    default:
        return m.renderAssistantMessage()
    }
}

func (msg *messageCmp) style() lipgloss.Style {
    t := styles.CurrentTheme()
    border := lipgloss.NormalBorder()
    if msg.focused {
        border = lipgloss.Border{Left: "▌"}
    }
    style := t.S().Text
    if msg.message.Role == message.User {
        style = style.PaddingLeft(1).
            BorderLeft(true).
            BorderStyle(border).
            BorderForeground(t.Primary)
    } else if msg.focused {
        style = style.PaddingLeft(1).
            BorderLeft(true).
            BorderStyle(border).
            BorderForeground(t.GreenDark)
    } else {
        style = style.PaddingLeft(2)
    }
    return style
}
```

- **Responsive layouts** (source: https://github.com/charmbracelet/crush/blob/main/internal/tui/page/chat/chat.go)
```go
const (
    CompactModeWidthBreakpoint  = 120
    SideBarWidth                = 31
)

type chatPage struct {
    width, height int
    compact       bool
    forceCompact  bool
    sidebar       sidebar.Sidebar
    editor        editor.Editor
}

func (p *chatPage) Init() tea.Cmd {
    cfg := config.Get()
    p.compact = cfg.Options.TUI.CompactMode
    p.forceCompact = p.compact
    p.sidebar.SetCompactMode(p.compact)
    return tea.Batch(
        p.sidebar.Init(),
        p.editor.Init(),
    )
}

func (p *chatPage) Update(msg tea.Msg) (util.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.WindowSizeMsg:
        p.width, p.height = msg.Width, msg.Height
        p.compact = p.forceCompact || msg.Width < CompactModeWidthBreakpoint
        p.sidebar.SetCompactMode(p.compact)
    }
    ...
    return p, nil
}
```

## Validation Targets
- `go test ./internal/bartui/...`
- `scripts/tools/run-tui-expect.sh --all`
- `python3 -m pytest _tests/test_bar_completion_cli.py`
- New expect cases covering overlay activation, slot-state rendering, and invalid-state modals

## Consequences
- Operators gain an in-product curriculum for the bar build grammar, reducing reliance on external docs and accelerating mastery.
- Overlay compositing and dynamic help introduce additional model complexity and state transitions; strict expect coverage mitigates regressions.
- Dependency on `bubbletea-overlay` and deeper Lip Gloss integration increases styling surface area but stays within Charm ecosystem norms.
- Future ADRs can extend the scaffold (e.g., iconography, persisted mastery) without reshaping the underlying layout established in ADR 0077.

## Open Questions
- What heuristics should trigger the parse overlay automatically versus requiring explicit gestures?
- How should we persist learner progress (e.g., hide hints after repeated success) without frustrating experts?
- Do we need a reduced mode for operators who prefer the pre-overlay interface, and how would that preference persist across sessions?
