// Package bartui2 implements the redesigned TUI for ADR 0081.
// This is a command-centric interface designed to teach the bar build grammar
// through direct interaction with the command line.
package bartui2

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/lipgloss/tree"
	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

// Options configures the TUI behavior.
type Options struct {
	// InitialTokens are pre-selected tokens to start with.
	InitialTokens []string

	// TokenCategories defines available tokens grouped by category.
	TokenCategories []bartui.TokenCategory

	// Preview generates prompt text from subject and tokens.
	Preview func(subject string, tokens []string) (string, error)

	// ClipboardWrite writes text to the system clipboard.
	ClipboardWrite func(string) error

	// InitialWidth overrides terminal width detection (for testing).
	InitialWidth int

	// InitialHeight overrides terminal height detection (for testing).
	InitialHeight int

	// NoAltScreen keeps output in the primary terminal buffer.
	NoAltScreen bool
}

// completion represents a single completion option with metadata.
type completion struct {
	Value       string
	Category    string
	Description string
}

// model is the Bubble Tea model for the redesigned TUI.
type model struct {
	// Layout
	width  int
	height int

	// Command input (pane 1)
	commandInput textinput.Model
	tokens       []string

	// Token categories (for completion)
	tokenCategories []bartui.TokenCategory

	// Completions (pane 2 right side)
	completions     []completion
	completionIndex int

	// Subject input (modal)
	subject          string
	subjectInput     textarea.Model
	showSubjectModal bool

	// Preview (pane 3)
	previewText string
	preview     func(subject string, tokens []string) (string, error)

	// Clipboard
	clipboardWrite func(string) error

	// Toast/status message
	toastMessage string

	// State
	ready bool
	err   error
}

// NewProgram creates a new Bubble Tea program for the redesigned TUI.
func NewProgram(opts Options) (*tea.Program, error) {
	m := newModel(opts)

	var teaOpts []tea.ProgramOption
	if opts.NoAltScreen {
		teaOpts = append(teaOpts, tea.WithoutCatchPanics())
	} else {
		teaOpts = append(teaOpts, tea.WithAltScreen())
	}

	return tea.NewProgram(m, teaOpts...), nil
}

func newModel(opts Options) model {
	ti := textinput.New()
	ti.Placeholder = "bar build "
	ti.Focus()
	ti.CharLimit = 256
	ti.Width = 60

	// Seed with "bar build " prefix
	ti.SetValue("bar build ")
	ti.CursorEnd()

	// Subject textarea for modal
	ta := textarea.New()
	ta.Placeholder = "Enter subject text (paste content here)..."
	ta.SetWidth(60)
	ta.SetHeight(8)
	ta.ShowLineNumbers = false

	m := model{
		commandInput:    ti,
		tokens:          opts.InitialTokens,
		tokenCategories: opts.TokenCategories,
		subjectInput:    ta,
		preview:         opts.Preview,
		clipboardWrite:  opts.ClipboardWrite,
		width:           opts.InitialWidth,
		height:          opts.InitialHeight,
	}

	if m.width > 0 && m.height > 0 {
		m.ready = true
	}

	// Generate initial completions (all options when no filter)
	m.updateCompletions()

	// Generate initial preview
	if m.preview != nil {
		text, err := m.preview("", m.tokens)
		if err == nil {
			m.previewText = text
		}
	}

	return m
}

// Init implements tea.Model.
func (m model) Init() tea.Cmd {
	return textinput.Blink
}

// Update implements tea.Model.
func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmds []tea.Cmd

	// Handle window size for all modes
	if wsm, ok := msg.(tea.WindowSizeMsg); ok {
		m.width = wsm.Width
		m.height = wsm.Height
		m.ready = true
		m.commandInput.Width = m.width - 4
		// Resize subject textarea to fit modal
		m.subjectInput.SetWidth(m.width - 10)
		m.subjectInput.SetHeight((m.height - 10) / 2)
	}

	// Route input based on modal state
	if m.showSubjectModal {
		return m.updateSubjectModal(msg)
	}

	switch msg := msg.(type) {
	case tea.KeyMsg:
		// Clear toast on any key press
		m.toastMessage = ""

		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		case "esc":
			return m, tea.Quit
		case "ctrl+b":
			// Copy CLI to clipboard
			m.copyCommandToClipboard()
			return m, nil
		case "ctrl+l":
			// Open subject input modal
			m.showSubjectModal = true
			m.subjectInput.SetValue(m.subject)
			m.subjectInput.Focus()
			m.commandInput.Blur()
			return m, textarea.Blink
		case "up":
			// Navigate completions up
			if m.completionIndex > 0 {
				m.completionIndex--
			}
			return m, nil
		case "down":
			// Navigate completions down
			if m.completionIndex < len(m.completions)-1 {
				m.completionIndex++
			}
			return m, nil
		case "tab", "enter":
			// Select current completion
			if len(m.completions) > 0 && m.completionIndex < len(m.completions) {
				m.selectCompletion(m.completions[m.completionIndex])
			}
			return m, nil
		}
	}

	// Update text input
	var cmd tea.Cmd
	m.commandInput, cmd = m.commandInput.Update(msg)
	cmds = append(cmds, cmd)

	// Parse tokens from command input and update completions
	m.tokens = m.parseTokensFromCommand()
	m.updateCompletions()

	// Update preview with subject
	if m.preview != nil {
		text, err := m.preview(m.subject, m.tokens)
		if err == nil {
			m.previewText = text
		}
	}

	return m, tea.Batch(cmds...)
}

// updateSubjectModal handles input when the subject modal is open.
func (m model) updateSubjectModal(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		case "esc":
			// Close modal without saving
			m.showSubjectModal = false
			m.subjectInput.Blur()
			m.commandInput.Focus()
			return m, textinput.Blink
		case "ctrl+s":
			// Save and close modal
			m.subject = m.subjectInput.Value()
			m.showSubjectModal = false
			m.subjectInput.Blur()
			m.commandInput.Focus()
			// Update preview with new subject
			if m.preview != nil {
				text, err := m.preview(m.subject, m.tokens)
				if err == nil {
					m.previewText = text
				}
			}
			return m, textinput.Blink
		}
	}

	// Update textarea
	var cmd tea.Cmd
	m.subjectInput, cmd = m.subjectInput.Update(msg)
	return m, cmd
}

// copyCommandToClipboard copies the current bar build command to clipboard.
func (m *model) copyCommandToClipboard() {
	command := m.commandInput.Value()
	if m.clipboardWrite == nil {
		m.toastMessage = "Clipboard not available"
		return
	}
	if err := m.clipboardWrite(command); err != nil {
		m.toastMessage = fmt.Sprintf("Clipboard error: %v", err)
		return
	}
	m.toastMessage = "Copied to clipboard!"
}

// parseTokensFromCommand extracts tokens from the command input.
func (m model) parseTokensFromCommand() []string {
	value := m.commandInput.Value()
	value = strings.TrimPrefix(value, "bar build ")
	value = strings.TrimPrefix(value, "bar build")
	value = strings.TrimSpace(value)

	if value == "" {
		return nil
	}

	fields := strings.Fields(value)
	return fields
}

// getFilterPartial returns the partial word being typed (for filtering completions).
func (m model) getFilterPartial() string {
	value := m.commandInput.Value()
	value = strings.TrimPrefix(value, "bar build ")
	value = strings.TrimPrefix(value, "bar build")

	// If ends with space, no partial - ready for new token
	if strings.HasSuffix(value, " ") || value == "" {
		return ""
	}

	// Find the last word (the partial being typed)
	fields := strings.Fields(value)
	if len(fields) == 0 {
		return ""
	}
	return fields[len(fields)-1]
}

// updateCompletions rebuilds the completions list based on current input.
func (m *model) updateCompletions() {
	partial := strings.ToLower(m.getFilterPartial())
	selectedSet := make(map[string]bool)
	for _, t := range m.tokens {
		selectedSet[strings.ToLower(t)] = true
	}

	var results []completion
	for _, category := range m.tokenCategories {
		for _, opt := range category.Options {
			// Skip already-selected tokens
			if selectedSet[strings.ToLower(opt.Value)] {
				continue
			}

			// Fuzzy match against partial
			if partial == "" || fuzzyMatch(strings.ToLower(opt.Value), partial) ||
				fuzzyMatch(strings.ToLower(opt.Slug), partial) {
				results = append(results, completion{
					Value:       opt.Value,
					Category:    category.Label,
					Description: truncate(opt.Description, 40),
				})
			}
		}
	}

	m.completions = results

	// Reset index if out of bounds
	if m.completionIndex >= len(m.completions) {
		m.completionIndex = 0
	}
}

// selectCompletion adds the selected completion to the command.
func (m *model) selectCompletion(c completion) {
	value := m.commandInput.Value()

	// Remove any partial being typed
	partial := m.getFilterPartial()
	if partial != "" {
		// Remove the partial from the end
		value = strings.TrimSuffix(value, partial)
	}

	// Ensure there's a space before the new token
	if !strings.HasSuffix(value, " ") {
		value += " "
	}

	// Add the selected token
	value += c.Value + " "

	m.commandInput.SetValue(value)
	m.commandInput.CursorEnd()

	// Update tokens and completions
	m.tokens = m.parseTokensFromCommand()
	m.updateCompletions()
}

// fuzzyMatch returns true if the pattern matches the target using simple substring matching.
// For now, this is a basic contains check; can be enhanced with proper fuzzy matching later.
func fuzzyMatch(target, pattern string) bool {
	if pattern == "" {
		return true
	}
	return strings.Contains(target, pattern)
}

// truncate shortens a string to maxLen, adding "..." if truncated.
func truncate(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	if maxLen <= 3 {
		return s[:maxLen]
	}
	return s[:maxLen-3] + "..."
}

// getCategoryForToken returns the category label for a given token value.
// Returns empty string if the token is not found in any category.
func (m model) getCategoryForToken(token string) string {
	tokenLower := strings.ToLower(token)
	for _, category := range m.tokenCategories {
		for _, opt := range category.Options {
			if strings.ToLower(opt.Value) == tokenLower || strings.ToLower(opt.Slug) == tokenLower {
				return category.Label
			}
		}
	}
	return ""
}

// View implements tea.Model.
func (m model) View() string {
	if !m.ready {
		return "Initializing..."
	}

	// Show subject modal if active
	if m.showSubjectModal {
		return m.renderSubjectModal()
	}

	var b strings.Builder

	// Pane 1: Command input
	b.WriteString(m.renderCommandPane())
	b.WriteString("\n")

	// Pane 2: Tokens & Completions
	b.WriteString(m.renderTokensPane())
	b.WriteString("\n")

	// Pane 3: Preview
	b.WriteString(m.renderPreviewPane())
	b.WriteString("\n")

	// Pane 4: Hotkey bar
	b.WriteString(m.renderHotkeyBar())

	return b.String()
}

// Styles
var (
	paneStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("240")).
			Padding(0, 1)

	modalStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("212")).
			Padding(1, 2)

	headerStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("212"))

	dimStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("240"))

	tokenStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("78"))

	categoryStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("244"))

	completionSelectedStyle = lipgloss.NewStyle().
				Foreground(lipgloss.Color("212")).
				Bold(true)

	toastStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("78")).
			Bold(true)
)

func (m model) renderCommandPane() string {
	width := m.width - 2
	if width < 20 {
		width = 20
	}

	content := fmt.Sprintf("> %s", m.commandInput.View())

	return paneStyle.Width(width).Render(content)
}

func (m model) renderTokensPane() string {
	width := m.width - 2
	if width < 20 {
		width = 20
	}

	// Calculate available height for this pane
	paneHeight := (m.height - 10) / 3
	if paneHeight < 4 {
		paneHeight = 4
	}

	var left strings.Builder
	// Header with count
	if len(m.tokens) == 0 {
		left.WriteString(headerStyle.Render("TOKENS"))
	} else {
		left.WriteString(headerStyle.Render(fmt.Sprintf("TOKENS (%d)", len(m.tokens))))
	}
	left.WriteString("\n")

	if len(m.tokens) == 0 {
		left.WriteString(dimStyle.Render("(none selected)"))
		left.WriteString("\n")
		left.WriteString(dimStyle.Render("Type to search, Enter to select"))
	} else {
		// Build tree with lipgloss/tree
		tokenTree := tree.New()
		for _, token := range m.tokens {
			category := m.getCategoryForToken(token)
			if category != "" {
				// Show "Category: value" format
				tokenTree = tokenTree.Child(fmt.Sprintf("%s: %s",
					categoryStyle.Render(category),
					tokenStyle.Render(token)))
			} else {
				// Fallback for unknown tokens
				tokenTree = tokenTree.Child(tokenStyle.Render(token))
			}
		}
		tokenTree = tokenTree.Enumerator(tree.RoundedEnumerator)
		left.WriteString(tokenTree.String())
	}

	var right strings.Builder
	right.WriteString(headerStyle.Render("COMPLETIONS"))
	right.WriteString("\n")

	if len(m.completions) == 0 {
		right.WriteString(dimStyle.Render("(no matches)"))
	} else {
		// Show completions with current selection highlighted
		maxShow := paneHeight - 2
		if maxShow < 1 {
			maxShow = 1
		}
		for i, c := range m.completions {
			if i >= maxShow {
				right.WriteString(dimStyle.Render(fmt.Sprintf("... +%d more", len(m.completions)-maxShow)))
				break
			}
			prefix := "  "
			style := dimStyle
			if i == m.completionIndex {
				prefix = "▸ "
				style = completionSelectedStyle
			}
			// Format: "▸ todo        Static Prompt"
			entry := fmt.Sprintf("%s%-12s %s", prefix, c.Value, c.Category)
			right.WriteString(style.Render(entry))
			right.WriteString("\n")
		}
	}

	// Split horizontally
	leftWidth := width / 2
	rightWidth := width - leftWidth - 3

	leftContent := lipgloss.NewStyle().Width(leftWidth).Render(left.String())
	rightContent := lipgloss.NewStyle().Width(rightWidth).Render(right.String())

	combined := lipgloss.JoinHorizontal(lipgloss.Top, leftContent, " ", rightContent)

	return paneStyle.Width(width).Height(paneHeight).Render(combined)
}

func (m model) renderPreviewPane() string {
	width := m.width - 2
	if width < 20 {
		width = 20
	}

	// Calculate available height for this pane
	paneHeight := (m.height - 10) / 2
	if paneHeight < 6 {
		paneHeight = 6
	}

	var content strings.Builder
	content.WriteString(headerStyle.Render("PREVIEW"))
	content.WriteString("\n")

	if m.previewText == "" {
		content.WriteString(dimStyle.Render("(select tokens to see preview)"))
	} else {
		// Truncate preview to fit
		lines := strings.Split(m.previewText, "\n")
		maxLines := paneHeight - 2
		if len(lines) > maxLines {
			lines = lines[:maxLines]
			lines = append(lines, dimStyle.Render("..."))
		}
		content.WriteString(strings.Join(lines, "\n"))
	}

	return paneStyle.Width(width).Height(paneHeight).Render(content.String())
}

func (m model) renderHotkeyBar() string {
	width := m.width - 2
	if width < 20 {
		width = 20
	}

	// Show toast message if present
	if m.toastMessage != "" {
		return toastStyle.Width(width).Render(m.toastMessage)
	}

	keys := []string{
		"Enter: select",
		"BS: remove",
		"^L: subject",
		"^B: copy",
		"Esc: exit",
	}

	return dimStyle.Width(width).Render(strings.Join(keys, " | "))
}

func (m model) renderSubjectModal() string {
	width := m.width - 4
	if width < 40 {
		width = 40
	}

	var content strings.Builder
	content.WriteString(headerStyle.Render("SUBJECT INPUT"))
	content.WriteString("\n\n")
	content.WriteString(m.subjectInput.View())
	content.WriteString("\n\n")

	// Show subject indicator
	if m.subject != "" {
		lines := strings.Count(m.subject, "\n") + 1
		chars := len(m.subject)
		content.WriteString(dimStyle.Render(fmt.Sprintf("Current: %d lines, %d chars", lines, chars)))
		content.WriteString("\n")
	}

	content.WriteString(dimStyle.Render("Ctrl+S: save | Esc: cancel"))

	return modalStyle.Width(width).Render(content.String())
}

// Snapshot renders a single frame for testing.
func Snapshot(opts Options) (string, error) {
	m := newModel(opts)
	m.ready = true
	if m.width == 0 {
		m.width = 80
	}
	if m.height == 0 {
		m.height = 24
	}
	return m.View(), nil
}
