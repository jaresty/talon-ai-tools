// Package bartui2 implements the redesigned TUI for ADR 0081.
// This is a command-centric interface designed to teach the bar build grammar
// through direct interaction with the command line.
package bartui2

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"
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

	// Preview generates prompt text from subject, addendum, and tokens.
	Preview func(subject string, addendum string, tokens []string) (string, error)

	// ClipboardWrite writes text to the system clipboard.
	ClipboardWrite func(string) error

	// RunCommand executes a shell command with stdin and returns stdout/stderr.
	RunCommand func(ctx context.Context, command string, stdin string) (stdout string, stderr string, err error)

	// CommandTimeout limits how long a command can run.
	CommandTimeout time.Duration

	// InitialWidth overrides terminal width detection (for testing).
	InitialWidth int

	// InitialHeight overrides terminal height detection (for testing).
	InitialHeight int

	// NoAltScreen keeps output in the primary terminal buffer.
	NoAltScreen bool

	// InitialCommand seeds the Run Command text input at launch time.
	InitialCommand string
}

// completion represents a single completion option with metadata.
type completion struct {
	Value       string
	Display     string
	Category    string
	Description string
	Guidance    string
	UseWhen     string // ADR-0142: routing trigger phrases
	// Fills specifies other categories that get auto-filled when this option is selected.
	Fills map[string]string
}

// Stage order for grammar progression (matches CLI completion order).
// Each stage corresponds to a token category key.
// Persona stages come first (optional), then static and modifiers.
// Per ADR 0086: preset before intent (bundled vs unbundled decision fork).
var stageOrder = []string{
	"persona_preset", // Bundled persona configuration (optional) - Path 1: takes precedence
	"intent",         // What the user wants to accomplish (optional) - Path 2: for custom builds
	"voice",          // Speaking style (optional) - Path 2 continued
	"audience",       // Target audience (optional) - Path 2 continued
	"tone",           // Emotional tone (optional) - Path 2 continued
	"task",           // Task - the main task type
	"completeness",   // How thorough
	"scope",          // How focused
	"method",         // How to approach
	"form",           // Output format
	"channel",        // Communication style
	"directional",    // Emphasis direction
}

// stageDisplayName returns the display name for a stage.
func stageDisplayName(stage string) string {
	switch stage {
	case "intent":
		return "Intent"
	case "persona_preset":
		return "Preset"
	case "voice":
		return "Voice"
	case "audience":
		return "Audience"
	case "tone":
		return "Tone"
	case "task":
		return "Task"
	case "completeness":
		return "Completeness"
	case "scope":
		return "Scope"
	case "method":
		return "Method"
	case "form":
		return "Form"
	case "channel":
		return "Channel"
	case "directional":
		return "Directional"
	default:
		return strings.Title(stage)
	}
}

// model is the Bubble Tea model for the redesigned TUI.
type model struct {
	// Layout
	width  int
	height int

	// Command input (pane 1)
	commandInput textinput.Model

	// Tokens organized by category (maintains grammar order)
	tokensByCategory map[string][]string // key: category key, value: selected tokens

	// Track which tokens were auto-filled by presets (for excluding from copied command)
	autoFilledTokens map[string]bool // key: "category:value"

	// Track which token caused each auto-fill (for cascade removal)
	autoFillSource map[string]string // key: "category:value" of filled token, value: "category:value" of source

	// Token categories (for completion)
	tokenCategories []bartui.TokenCategory

	// Stage-based progression
	currentStageIndex int // index into stageOrder

	// Completions (pane 2 right side) - filtered to current stage
	completions            []completion
	completionIndex        int
	completionScrollOffset int // scroll offset for completion list

	// Subject input (modal)
	subject          string
	subjectInput     textarea.Model
	showSubjectModal bool

	// Addendum input (modal)
	addendum          string
	addendumInput     textarea.Model
	showAddendumModal bool

	// Preview (pane 3) with viewport for scrolling
	previewText     string
	previewViewport viewport.Model
	preview         func(subject string, addendum string, tokens []string) (string, error)

	// Command execution with viewport for scrolling result
	shellCommandInput textinput.Model
	showCommandModal  bool
	lastShellCommand  string
	runCommand        func(ctx context.Context, command string, stdin string) (string, string, error)
	commandTimeout    time.Duration
	commandResult     string
	resultViewport    viewport.Model
	showingResult     bool

	// Clipboard
	clipboardWrite func(string) error

	// Toast/status message
	toastMessage string

	// Undo/redo history
	undoStack []stateSnapshot
	redoStack []stateSnapshot

	// State
	ready bool
	err   error
}

// stateSnapshot captures token state for undo/redo.
type stateSnapshot struct {
	tokensByCategory  map[string][]string
	autoFilledTokens  map[string]bool
	autoFillSource    map[string]string
	currentStageIndex int
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

	// Addendum textarea for modal
	at := textarea.New()
	at.Placeholder = "Enter task clarification (e.g., focus on security, keep under 100 words)..."
	at.SetWidth(60)
	at.SetHeight(4)
	at.ShowLineNumbers = false

	// Shell command input for execution modal
	sci := textinput.New()
	sci.Placeholder = "Enter shell command (e.g., pbcopy, claude)"
	sci.CharLimit = 512
	sci.Width = 60
	if opts.InitialCommand != "" {
		sci.SetValue(opts.InitialCommand)
		sci.CursorEnd()
	}

	// Default timeout
	timeout := opts.CommandTimeout
	if timeout == 0 {
		timeout = 30 * time.Second
	}

	// Initialize viewports for preview and result scrolling
	previewVP := viewport.New(60, 10)
	previewVP.Style = lipgloss.NewStyle().Foreground(lipgloss.Color("252")) // Light gray for readability

	resultVP := viewport.New(60, 10)
	resultVP.Style = lipgloss.NewStyle()

	m := model{
		commandInput:      ti,
		tokensByCategory:  make(map[string][]string),
		autoFilledTokens:  make(map[string]bool),
		autoFillSource:    make(map[string]string),
		tokenCategories:   opts.TokenCategories,
		subjectInput:      ta,
		addendumInput:     at,
		shellCommandInput: sci,
		previewViewport:   previewVP,
		resultViewport:    resultVP,
		preview:           opts.Preview,
		runCommand:        opts.RunCommand,
		commandTimeout:    timeout,
		clipboardWrite:    opts.ClipboardWrite,
		width:             opts.InitialWidth,
		height:            opts.InitialHeight,
	}

	// Categorize initial tokens
	for _, token := range opts.InitialTokens {
		categoryKey := m.getCategoryKeyForToken(token)
		if categoryKey == "" {
			continue
		}
		normalized := m.normalizeTokenValue(categoryKey, token)
		m.tokensByCategory[categoryKey] = append(m.tokensByCategory[categoryKey], normalized)
	}

	if m.width > 0 && m.height > 0 {
		m.ready = true
	}

	// Advance stage index past any already-selected stages
	m.advanceToNextIncompleteStage()

	// Rebuild command line with initial tokens
	if len(opts.InitialTokens) > 0 {
		m.rebuildCommandLine()
	}

	// Generate initial completions (for current stage)
	m.updateCompletions()

	// Generate initial preview
	if m.preview != nil {
		tokens := m.getCommandTokens()
		text, err := m.preview("", "", tokens)
		if err == nil {
			m.previewText = text
			m.previewViewport.SetContent(text)
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
		// Resize viewports
		vpWidth := m.width - 6 // Account for pane border and padding
		vpHeight := m.getPreviewPaneHeight() - 2
		if vpWidth < 20 {
			vpWidth = 20
		}
		if vpHeight < 4 {
			vpHeight = 4
		}
		m.previewViewport.Width = vpWidth
		m.previewViewport.Height = vpHeight
		m.resultViewport.Width = vpWidth
		m.resultViewport.Height = vpHeight
	}

	// Route input based on modal state
	if m.showSubjectModal {
		return m.updateSubjectModal(msg)
	}
	if m.showAddendumModal {
		return m.updateAddendumModal(msg)
	}
	if m.showCommandModal {
		return m.updateCommandModal(msg)
	}

	switch msg := msg.(type) {
	case tea.KeyMsg:
		// Clear toast on any key press
		m.toastMessage = ""

		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		case "esc":
			// If showing result, return to preview
			if m.showingResult {
				m.showingResult = false
				m.commandResult = ""
				return m, nil
			}
			return m, tea.Quit
		case "ctrl+b":
			// Copy CLI to clipboard
			m.copyCommandToClipboard()
			return m, nil
		case "ctrl+g":
			// Copy prompt to clipboard
			m.copyPromptToClipboard()
			return m, nil
		case "ctrl+l":
			// Open subject input modal
			m.showSubjectModal = true
			m.subjectInput.SetValue(m.subject)
			m.subjectInput.Focus()
			m.commandInput.Blur()
			return m, textarea.Blink
		case "ctrl+a":
			// Open addendum input modal
			m.showAddendumModal = true
			m.addendumInput.SetValue(m.addendum)
			m.addendumInput.Focus()
			m.commandInput.Blur()
			return m, textarea.Blink
		case "ctrl+enter", "ctrl+x":
			// Open command execution modal (ctrl+x as fallback since ctrl+enter doesn't work in all terminals)
			m.showCommandModal = true
			m.shellCommandInput.SetValue(m.lastShellCommand)
			m.shellCommandInput.Focus()
			m.commandInput.Blur()
			return m, textinput.Blink
		case "ctrl+y":
			// In result mode: copy result; otherwise: redo
			if m.showingResult && m.commandResult != "" {
				m.copyResultToClipboard()
			} else {
				if m.redo() {
					m.toastMessage = "Redo"
				} else {
					m.toastMessage = "Nothing to redo"
				}
			}
			return m, nil
		case "ctrl+r":
			// Quick re-run last command (or open modal if no command)
			if m.showingResult {
				// If showing result, return to preview first
				m.showingResult = false
				m.commandResult = ""
				return m, nil
			}
			// If we have a last command, run it immediately
			if m.lastShellCommand != "" {
				m.executeCommand(m.lastShellCommand)
				return m, nil
			}
			// Otherwise open the command modal
			m.showCommandModal = true
			m.shellCommandInput.SetValue("")
			m.shellCommandInput.Focus()
			m.commandInput.Blur()
			return m, textinput.Blink
		case "ctrl+s":
			// Pipeline result into subject (when showing result)
			if m.showingResult && m.commandResult != "" {
				m.pipelineResultToSubject()
			}
			return m, nil
		case "pgup", "ctrl+u":
			// Scroll up in preview/result viewport
			if m.showingResult {
				m.resultViewport.HalfViewUp()
			} else {
				m.previewViewport.HalfViewUp()
			}
			return m, nil
		case "pgdown", "ctrl+d":
			// Scroll down in preview/result viewport
			if m.showingResult {
				m.resultViewport.HalfViewDown()
			} else {
				m.previewViewport.HalfViewDown()
			}
			return m, nil
		case "up":
			// Navigate completions up
			if m.completionIndex > 0 {
				m.completionIndex--
				// Adjust scroll offset if selection moved above visible window
				if m.completionIndex < m.completionScrollOffset {
					m.completionScrollOffset = m.completionIndex
				}
			}
			return m, nil
		case "down":
			// Navigate completions down
			if m.completionIndex < len(m.completions)-1 {
				m.completionIndex++
				// Adjust scroll offset if selection moved below visible window
				maxShow := m.getCompletionMaxShow()
				if m.completionIndex >= m.completionScrollOffset+maxShow {
					m.completionScrollOffset = m.completionIndex - maxShow + 1
				}
			}
			return m, nil
		case "tab":
			// Skip current stage
			m.skipCurrentStage()
			m.updateCompletions()
			return m, nil
		case "shift+tab":
			// Go to previous stage
			m.goToPreviousStage()
			m.updateCompletions()
			return m, nil
		case "ctrl+k":
			// Clear all tokens and restart
			m.saveStateForUndo()
			m.clearAllTokens()
			m.updateCompletions()
			m.updatePreview()
			m.toastMessage = "Cleared all tokens"
			return m, nil
		case "ctrl+z":
			// Undo
			if m.undo() {
				m.toastMessage = "Undo"
			} else {
				m.toastMessage = "Nothing to undo"
			}
			return m, nil
		case "enter":
			// Check for escape hatch syntax (category=value)
			partial := m.getFilterPartial()
			if category, value, ok := m.parseEscapeHatch(partial); ok {
				if m.applyEscapeHatch(category, value) {
					m.toastMessage = fmt.Sprintf("Added %s=%s", category, value)
				} else {
					m.toastMessage = fmt.Sprintf("Invalid: %s=%s", category, value)
				}
				return m, nil
			}
			// Select current completion
			if len(m.completions) > 0 && m.completionIndex < len(m.completions) {
				m.selectCompletion(m.completions[m.completionIndex])
			}
			return m, nil
		}
	}

	// For stage-based mode, we don't parse the command input - we manage tokens via stages
	// But we still need to handle text input for filtering
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.Type {
		case tea.KeyBackspace:
			// Check if there's a filter partial to delete first
			partial := m.getFilterPartial()
			if partial != "" {
				// Let the textinput handle deleting the partial
				var cmd tea.Cmd
				m.commandInput, cmd = m.commandInput.Update(msg)
				cmds = append(cmds, cmd)
				m.updateCompletions()
			} else {
				// Remove last token
				m.removeLastToken()
				m.updateCompletions()
			}
			m.updatePreview()
			return m, tea.Batch(cmds...)
		case tea.KeyRunes:
			// Handle typing for filter
			var cmd tea.Cmd
			m.commandInput, cmd = m.commandInput.Update(msg)
			cmds = append(cmds, cmd)
			m.updateCompletions()
			return m, tea.Batch(cmds...)
		}
	}

	// Update preview
	m.updatePreview()

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
			m.updatePreview()
			return m, textinput.Blink
		}
	}

	// Update textarea
	var cmd tea.Cmd
	m.subjectInput, cmd = m.subjectInput.Update(msg)
	return m, cmd
}

// updateAddendumModal handles input when the addendum modal is open.
func (m model) updateAddendumModal(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		case "esc":
			// Close modal without saving
			m.showAddendumModal = false
			m.addendumInput.Blur()
			m.commandInput.Focus()
			return m, textinput.Blink
		case "ctrl+s":
			// Save and close modal
			m.addendum = m.addendumInput.Value()
			m.showAddendumModal = false
			m.addendumInput.Blur()
			m.commandInput.Focus()
			m.updatePreview()
			m.rebuildCommandLine()
			return m, textinput.Blink
		}
	}

	var cmd tea.Cmd
	m.addendumInput, cmd = m.addendumInput.Update(msg)
	return m, cmd
}

// copyCommandToClipboard copies the current bar build command to clipboard.
// Auto-filled tokens (from presets) are excluded from the copied command.
func (m *model) copyCommandToClipboard() {
	if m.clipboardWrite == nil {
		m.toastMessage = "Clipboard not available"
		return
	}

	// Build command excluding auto-filled tokens
	command := m.buildCommandForClipboard()

	if err := m.clipboardWrite(command); err != nil {
		m.toastMessage = fmt.Sprintf("Clipboard error: %v", err)
		return
	}
	m.toastMessage = "Copied command to clipboard!"
}

// buildCommandForClipboard builds the bar build command excluding auto-filled tokens.
func (m model) buildCommandForClipboard() string {
	tokens := m.getCommandTokens()
	if len(tokens) == 0 {
		return "bar build"
	}

	return "bar build " + strings.Join(tokens, " ")
}

// copyPromptToClipboard copies the generated prompt to clipboard.
func (m *model) copyPromptToClipboard() {
	if m.clipboardWrite == nil {
		m.toastMessage = "Clipboard not available"
		return
	}
	if m.previewText == "" {
		m.toastMessage = "No prompt to copy"
		return
	}
	if err := m.clipboardWrite(m.previewText); err != nil {
		m.toastMessage = fmt.Sprintf("Clipboard error: %v", err)
		return
	}
	m.toastMessage = "Copied prompt to clipboard!"
}

// copyResultToClipboard copies the command result to clipboard.
func (m *model) copyResultToClipboard() {
	if m.clipboardWrite == nil {
		m.toastMessage = "Clipboard not available"
		return
	}
	if err := m.clipboardWrite(m.commandResult); err != nil {
		m.toastMessage = fmt.Sprintf("Clipboard error: %v", err)
		return
	}
	m.toastMessage = "Result copied to clipboard!"
}

// pipelineResultToSubject loads the command result into the subject field.
func (m *model) pipelineResultToSubject() {
	m.subject = m.commandResult
	m.showingResult = false
	m.commandResult = ""
	m.updatePreview()
	m.toastMessage = "Result loaded into subject"
}

// updateCommandModal handles input when the command execution modal is open.
func (m model) updateCommandModal(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		case "esc":
			// Close modal without executing
			m.showCommandModal = false
			m.shellCommandInput.Blur()
			m.commandInput.Focus()
			return m, textinput.Blink
		case "enter":
			// Execute command and close modal
			shellCmd := m.shellCommandInput.Value()
			if shellCmd == "" {
				m.toastMessage = "No command entered"
				m.showCommandModal = false
				m.shellCommandInput.Blur()
				m.commandInput.Focus()
				return m, textinput.Blink
			}

			m.lastShellCommand = shellCmd
			m.showCommandModal = false
			m.shellCommandInput.Blur()
			m.commandInput.Focus()

			// Execute the command
			m.executeCommand(shellCmd)
			return m, textinput.Blink
		}
	}

	// Update text input
	var cmd tea.Cmd
	m.shellCommandInput, cmd = m.shellCommandInput.Update(msg)
	return m, cmd
}

// executeCommand runs the shell command with the preview as stdin.
func (m *model) executeCommand(shellCmd string) {
	if m.runCommand == nil {
		m.toastMessage = "Command execution not available"
		return
	}

	// Get the preview text to pipe to the command
	stdin := m.previewText

	// Execute with timeout
	ctx, cancel := context.WithTimeout(context.Background(), m.commandTimeout)
	defer cancel()

	stdout, stderr, err := m.runCommand(ctx, shellCmd, stdin)

	// Build result
	var result strings.Builder
	if stdout != "" {
		result.WriteString(stdout)
	}
	if stderr != "" {
		if result.Len() > 0 {
			result.WriteString("\n--- stderr ---\n")
		}
		result.WriteString(stderr)
	}
	if err != nil {
		if result.Len() > 0 {
			result.WriteString("\n")
		}
		result.WriteString(fmt.Sprintf("Error: %v", err))
	}

	if result.Len() == 0 {
		result.WriteString("(no output)")
	}

	m.commandResult = result.String()
	m.resultViewport.SetContent(m.commandResult)
	m.resultViewport.GotoTop()
	m.showingResult = true
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

// updateCompletions rebuilds the completions list for the current stage only.
func (m *model) updateCompletions() {
	partial := strings.ToLower(m.getFilterPartial())

	// Build set of already-selected tokens
	selectedSet := make(map[string]bool)
	for _, tokens := range m.tokensByCategory {
		for _, t := range tokens {
			selectedSet[strings.ToLower(t)] = true
		}
	}

	var results []completion

	// Only show completions for the current stage
	currentStage := m.getCurrentStage()
	if currentStage == "" {
		// All stages complete
		m.completions = nil
		m.completionIndex = 0
		return
	}

	category := m.getCategoryByKey(currentStage)
	if category == nil {
		m.completions = nil
		m.completionIndex = 0
		return
	}

	for _, opt := range category.Options {
		// Skip already-selected tokens
		if selectedSet[strings.ToLower(opt.Value)] {
			continue
		}

		// Fuzzy match against partial (also match against label when set — ADR-0111 D4)
		if partial == "" || fuzzyMatch(strings.ToLower(opt.Value), partial) ||
			fuzzyMatch(strings.ToLower(opt.Slug), partial) ||
			(opt.Label != "" && fuzzyMatch(strings.ToLower(opt.Label), partial)) {
			// Use "slug — label" format when label available (ADR-0111 D4)
			slugDisplay := m.formatCompletionDisplay(category.Key, opt.Value, opt.Slug)
			display := slugDisplay
			if opt.Label != "" {
				display = slugDisplay + " \u2014 " + opt.Label
			}
			results = append(results, completion{
				Value:       opt.Value,
				Display:     display,
				Category:    category.Label,
				Description: opt.Description,
				Guidance:    opt.Guidance,
				UseWhen:     opt.UseWhen,
				Fills:       opt.Fills,
			})
		}
	}

	m.completions = results

	// Reset index and scroll offset if out of bounds
	if m.completionIndex >= len(m.completions) {
		m.completionIndex = 0
		m.completionScrollOffset = 0
	}
}

// selectCompletion adds the selected completion to the current stage.
func (m *model) selectCompletion(c completion) {
	// Add token to current stage
	currentStage := m.getCurrentStage()
	if currentStage == "" {
		return // No stage to add to
	}

	// Prevent adding when stage is already at MaxSelections (e.g., after shift-tab back)
	if m.isStageComplete(currentStage) {
		return
	}

	// Save state for undo before modifying
	m.saveStateForUndo()

	m.tokensByCategory[currentStage] = append(m.tokensByCategory[currentStage], c.Value)

	// Apply auto-fills (e.g., persona presets fill voice/audience/tone)
	if len(c.Fills) > 0 {
		sourceKey := currentStage + ":" + c.Value
		for category, value := range c.Fills {
			// Only fill if not already set
			if _, exists := m.tokensByCategory[category]; !exists || len(m.tokensByCategory[category]) == 0 {
				m.tokensByCategory[category] = []string{value}
				// Mark as auto-filled so it's excluded from copied command
				filledKey := category + ":" + value
				m.autoFilledTokens[filledKey] = true
				// Track source so we can cascade-remove when source is removed
				m.autoFillSource[filledKey] = sourceKey
			}
		}

		// Per ADR 0086: When preset selected, mark intent as implicitly satisfied
		// so user skips directly to static (bundled path).
		if currentStage == "persona_preset" {
			if _, exists := m.tokensByCategory["intent"]; !exists || len(m.tokensByCategory["intent"]) == 0 {
				m.tokensByCategory["intent"] = []string{"(implicit)"}
				intentKey := "intent:(implicit)"
				m.autoFilledTokens[intentKey] = true
				m.autoFillSource[intentKey] = sourceKey
			}
		}
	}

	// Rebuild command line in grammar order
	m.rebuildCommandLine()

	// Advance to next stage if current is complete
	m.advanceToNextIncompleteStage()

	// Update completions for new stage
	m.updateCompletions()

	// Update preview with new token selection
	m.updatePreview()
}

// rebuildCommandLine reconstructs the command from tokens in grammar order.
func (m *model) rebuildCommandLine() {
	tokens := m.getCommandTokens()
	var cmd strings.Builder
	cmd.WriteString("bar build")
	for _, token := range tokens {
		cmd.WriteString(" ")
		cmd.WriteString(token)
	}
	if m.addendum != "" {
		cmd.WriteString(fmt.Sprintf(" --addendum %q", m.addendum))
	}
	cmd.WriteString(" ")
	m.commandInput.SetValue(cmd.String())
	m.commandInput.CursorEnd()
}

// removeLastToken removes the last manually-selected token (skipping auto-filled tokens).
// If the removed token caused any auto-fills, those are also removed.
func (m *model) removeLastToken() {
	// Find the last stage that has a manually-selected token (not auto-filled)
	for i := len(stageOrder) - 1; i >= 0; i-- {
		stage := stageOrder[i]
		tokens, ok := m.tokensByCategory[stage]
		if !ok || len(tokens) == 0 {
			continue
		}

		// Check if the last token in this stage is auto-filled
		lastToken := tokens[len(tokens)-1]
		tokenKey := stage + ":" + lastToken
		if m.autoFilledTokens[tokenKey] {
			// This token is auto-filled, skip to earlier stage
			continue
		}

		// Found a manually-selected token - remove it
		m.tokensByCategory[stage] = tokens[:len(tokens)-1]

		// Cascade-remove any tokens that this token auto-filled
		m.removeAutoFilledBy(tokenKey)

		// Update current stage index to this stage (since it now has room)
		m.currentStageIndex = i
		m.rebuildCommandLine()
		return
	}
}

// removeAutoFilledBy removes all tokens that were auto-filled by the given source token.
func (m *model) removeAutoFilledBy(sourceKey string) {
	// Find all auto-filled tokens with this source and remove them
	for filledKey, source := range m.autoFillSource {
		if source == sourceKey {
			// Parse category:value from key
			parts := strings.SplitN(filledKey, ":", 2)
			if len(parts) != 2 {
				continue
			}
			category, value := parts[0], parts[1]

			// Remove from tokensByCategory
			if tokens, ok := m.tokensByCategory[category]; ok {
				var newTokens []string
				for _, t := range tokens {
					if t != value {
						newTokens = append(newTokens, t)
					}
				}
				m.tokensByCategory[category] = newTokens
			}

			// Clean up tracking
			delete(m.autoFilledTokens, filledKey)
			delete(m.autoFillSource, filledKey)
		}
	}
}

// updatePreview regenerates the preview from current tokens.
func (m *model) updatePreview() {
	if m.preview != nil {
		tokens := m.getCommandTokens()
		text, err := m.preview(m.subject, m.addendum, tokens)
		if err == nil {
			m.previewText = text
			m.previewViewport.SetContent(text)
		}
	}
}

func (m model) formatCompletionDisplay(stage, value, slug string) string {
	trimmed := strings.TrimSpace(value)
	slug = strings.TrimSpace(slug)
	if slug != "" {
		if stage == "persona_preset" || stage == "directional" || !strings.EqualFold(trimmed, slug) {
			return slug
		}
	}
	return trimmed
}

// parseEscapeHatch checks if the filter partial contains category=value syntax.
// Returns (category, value, true) if found, or ("", "", false) if not.
func (m model) parseEscapeHatch(partial string) (string, string, bool) {
	if !strings.Contains(partial, "=") {
		return "", "", false
	}
	parts := strings.SplitN(partial, "=", 2)
	if len(parts) != 2 {
		return "", "", false
	}
	category := strings.ToLower(strings.TrimSpace(parts[0]))
	value := strings.TrimSpace(parts[1])
	if category == "" || value == "" {
		return "", "", false
	}
	// Verify this is a valid category
	if m.getCategoryByKey(category) == nil {
		return "", "", false
	}
	return category, value, true
}

// applyEscapeHatch applies the category=value override, adding the token to the specified category.
func (m *model) applyEscapeHatch(category, value string) bool {
	cat := m.getCategoryByKey(category)
	if cat == nil {
		return false
	}

	// Find the token in the category
	var foundToken string
	valueLower := strings.ToLower(value)
	for _, opt := range cat.Options {
		if strings.ToLower(opt.Value) == valueLower || strings.ToLower(opt.Slug) == valueLower {
			foundToken = opt.Value
			break
		}
	}
	if foundToken == "" {
		return false
	}

	// Check if already selected
	for _, t := range m.tokensByCategory[category] {
		if strings.ToLower(t) == strings.ToLower(foundToken) {
			return false // Already selected
		}
	}

	// Add the token
	m.tokensByCategory[category] = append(m.tokensByCategory[category], foundToken)
	m.rebuildCommandLine()
	m.updateCompletions()
	m.updatePreview()
	return true
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

// wrapText wraps text to fit within maxWidth characters per line.
func wrapText(s string, maxWidth int) string {
	if maxWidth <= 0 {
		return s
	}
	var result strings.Builder
	words := strings.Fields(s)
	lineLen := 0
	for i, word := range words {
		wordLen := len(word)
		if lineLen > 0 && lineLen+1+wordLen > maxWidth {
			// Start a new line
			result.WriteString("\n")
			lineLen = 0
		}
		if lineLen > 0 {
			result.WriteString(" ")
			lineLen++
		}
		result.WriteString(word)
		lineLen += wordLen
		// Avoid trailing space check
		_ = i
	}
	return result.String()
}

// wrapAndTruncateText wraps text to fit within maxWidth characters per line,
// then truncates to maxLines, adding "..." if truncated.
func wrapAndTruncateText(s string, maxWidth, maxLines int) string {
	wrapped := wrapText(s, maxWidth)
	lines := strings.Split(wrapped, "\n")
	if len(lines) <= maxLines {
		return wrapped
	}
	// Truncate to maxLines and add ellipsis
	truncated := strings.Join(lines[:maxLines], "\n")
	return truncated + "..."
}

// getPreviewPaneHeight returns the calculated height for the preview/result pane.
func (m model) getPreviewPaneHeight() int {
	paneHeight := (m.height - 10) / 2
	if paneHeight < 6 {
		paneHeight = 6
	}
	return paneHeight
}

// getCompletionMaxShow returns the maximum number of completions that can be shown.
func (m model) getCompletionMaxShow() int {
	paneHeight := (m.height - 10) / 3
	if paneHeight < 4 {
		paneHeight = 4
	}
	// Reserve space for: header, "more above", completions, "more below", "Then:" hint, selected desc
	maxShow := paneHeight - 7
	if maxShow < 1 {
		maxShow = 1
	}
	return maxShow
}

// getCategoryForToken returns the category label for a given token value.
// Returns empty string if the token is not found in any category.
func (m model) getCategoryForToken(token string) string {
	tokenLower := strings.ToLower(strings.TrimSpace(token))
	for _, category := range m.tokenCategories {
		for _, opt := range category.Options {
			if strings.EqualFold(opt.Value, token) || strings.EqualFold(opt.Slug, token) {
				return category.Label
			}
			if category.Key == "persona_preset" && strings.HasPrefix(tokenLower, "persona=") {
				suffix := strings.TrimSpace(tokenLower[len("persona="):])
				if suffix == strings.ToLower(strings.TrimSpace(opt.Slug)) || suffix == strings.ToLower(strings.TrimSpace(opt.Value)) {
					return category.Label
				}
			}
		}
	}
	return ""
}

// getCategoryKeyForToken returns the category key for a given token value.
// Returns empty string if the token is not found in any category.
func (m model) getCategoryKeyForToken(token string) string {
	tokenLower := strings.ToLower(strings.TrimSpace(token))
	for _, category := range m.tokenCategories {
		for _, opt := range category.Options {
			if strings.EqualFold(opt.Value, token) || strings.EqualFold(opt.Slug, token) {
				return category.Key
			}
			if category.Key == "persona_preset" && strings.HasPrefix(tokenLower, "persona=") {
				suffix := strings.TrimSpace(tokenLower[len("persona="):])
				if suffix == strings.ToLower(strings.TrimSpace(opt.Slug)) || suffix == strings.ToLower(strings.TrimSpace(opt.Value)) {
					return category.Key
				}
			}
		}
	}
	return ""
}

// getAllTokensInOrder returns all selected tokens in grammar order.
// Persona preset tokens are prefixed with "persona=" as required by Build.
// Auto-filled tokens are skipped since their source (e.g., a preset) already provides them.
func (m model) getAllTokensInOrder() []string {
	var result []string
	for _, stage := range stageOrder {
		if tokens, ok := m.tokensByCategory[stage]; ok {
			for _, token := range tokens {
				// Skip auto-filled tokens - they're provided by their source (e.g., preset)
				if m.isAutoFilled(stage, token) {
					continue
				}
				if stage == "persona_preset" {
					result = append(result, "persona="+token)
				} else {
					result = append(result, token)
				}
			}
		}
	}
	return result
}

func (m model) getCommandTokens() []string {
	var result []string
	for _, stage := range stageOrder {
		tokens, ok := m.tokensByCategory[stage]
		if !ok {
			continue
		}
		for _, token := range tokens {
			if m.isAutoFilled(stage, token) {
				continue
			}
			cliToken := m.formatTokenForCLI(stage, token)
			if strings.TrimSpace(cliToken) != "" {
				result = append(result, cliToken)
			}
		}
	}
	return result
}

func (m model) formatTokenForCLI(stage, token string) string {
	slug := strings.TrimSpace(m.getTokenSlug(stage, token))
	if stage == "persona_preset" {
		// No prefix needed - bar build recognizes persona presets by order
		if slug == "" {
			slug = strings.TrimSpace(token)
		}
		return slug
	}
	if slug != "" {
		return slug
	}
	return strings.TrimSpace(token)
}

func (m model) normalizeTokenValue(stage, token string) string {
	trimmed := strings.TrimSpace(token)
	if stage == "" {
		return trimmed
	}
	tokenLower := strings.ToLower(trimmed)
	for _, category := range m.tokenCategories {
		if category.Key != stage {
			continue
		}
		for _, opt := range category.Options {
			if strings.EqualFold(opt.Value, trimmed) {
				return opt.Value
			}
			if strings.EqualFold(opt.Slug, trimmed) {
				return opt.Value
			}
			if stage == "persona_preset" && strings.HasPrefix(tokenLower, "persona=") {
				suffix := strings.TrimSpace(tokenLower[len("persona="):])
				if suffix == strings.ToLower(strings.TrimSpace(opt.Slug)) || suffix == strings.ToLower(strings.TrimSpace(opt.Value)) {
					return opt.Value
				}
			}
		}
		break
	}
	return trimmed
}

func (m model) getTokenSlug(stage, token string) string {
	tokenLower := strings.ToLower(strings.TrimSpace(token))
	for _, category := range m.tokenCategories {
		if category.Key != stage {
			continue
		}
		for _, opt := range category.Options {
			if strings.EqualFold(opt.Value, token) || strings.EqualFold(opt.Slug, token) {
				return opt.Slug
			}
			if category.Key == "persona_preset" && strings.HasPrefix(tokenLower, "persona=") {
				suffix := strings.TrimSpace(tokenLower[len("persona="):])
				if suffix == strings.ToLower(strings.TrimSpace(opt.Slug)) || suffix == strings.ToLower(strings.TrimSpace(opt.Value)) {
					return opt.Slug
				}
			}
		}
		break
	}
	return ""
}

// getDisplayTokens returns tokens for display purposes (without Build-specific prefixes).
// Auto-filled tokens are included for display but marked appropriately.
func (m model) getDisplayTokens() []struct {
	Category string
	Value    string
} {
	var result []struct {
		Category string
		Value    string
	}
	for _, stage := range stageOrder {
		if tokens, ok := m.tokensByCategory[stage]; ok {
			category := m.getCategoryByKey(stage)
			categoryLabel := ""
			if category != nil {
				categoryLabel = category.Label
			}
			for _, token := range tokens {
				display := m.formatTokenForDisplay(stage, token)
				result = append(result, struct {
					Category string
					Value    string
				}{categoryLabel, display})
			}
		}
	}
	return result
}

func (m model) formatTokenForDisplay(stage, token string) string {
	trimmed := strings.TrimSpace(token)
	if stage == "" {
		return trimmed
	}
	slug := strings.TrimSpace(m.getTokenSlug(stage, token))
	if stage == "persona_preset" {
		if slug != "" {
			return slug
		}
		return trimmed
	}
	if slug != "" {
		return slug
	}
	return trimmed
}

// getCurrentStage returns the current stage key based on what's been selected.
func (m model) getCurrentStage() string {
	if m.currentStageIndex >= len(stageOrder) {
		return "" // All stages complete
	}
	return stageOrder[m.currentStageIndex]
}

// getCategoryByKey returns the category with the given key.
func (m model) getCategoryByKey(key string) *bartui.TokenCategory {
	for i := range m.tokenCategories {
		if m.tokenCategories[i].Key == key {
			return &m.tokenCategories[i]
		}
	}
	return nil
}

// isStageComplete returns true if the current stage has max selections.
func (m model) isStageComplete(stage string) bool {
	category := m.getCategoryByKey(stage)
	if category == nil {
		return true // Unknown stage is complete
	}
	tokens := m.tokensByCategory[stage]
	return len(tokens) >= category.MaxSelections
}

// advanceToNextIncompleteStage moves to the next stage that needs selection.
func (m *model) advanceToNextIncompleteStage() {
	for m.currentStageIndex < len(stageOrder) {
		stage := stageOrder[m.currentStageIndex]
		if !m.isStageComplete(stage) {
			return // Stay at this stage
		}
		m.currentStageIndex++
	}
}

// skipCurrentStage moves to the next stage without selecting anything.
func (m *model) skipCurrentStage() {
	if m.currentStageIndex < len(stageOrder) {
		m.currentStageIndex++
		m.advanceToNextIncompleteStage()
	}
}

// goToPreviousStage moves to the previous stage (for Shift+Tab navigation).
func (m *model) goToPreviousStage() {
	if m.currentStageIndex > 0 {
		m.currentStageIndex--
		// Skip back over stages that don't have categories
		for m.currentStageIndex > 0 {
			stage := stageOrder[m.currentStageIndex]
			if m.getCategoryByKey(stage) != nil {
				break
			}
			m.currentStageIndex--
		}
	}
}

// clearAllTokens removes all tokens and resets to the first stage.
func (m *model) clearAllTokens() {
	m.tokensByCategory = make(map[string][]string)
	m.autoFilledTokens = make(map[string]bool)
	m.autoFillSource = make(map[string]string)
	m.currentStageIndex = 0
	m.advanceToNextIncompleteStage()
	m.rebuildCommandLine()
}

// isAutoFilled returns true if the given category:value was auto-filled by a preset.
func (m model) isAutoFilled(category, value string) bool {
	return m.autoFilledTokens[category+":"+value]
}

// saveStateForUndo saves the current token state to the undo stack.
func (m *model) saveStateForUndo() {
	snapshot := stateSnapshot{
		tokensByCategory:  copyStringSliceMap(m.tokensByCategory),
		autoFilledTokens:  copyBoolMap(m.autoFilledTokens),
		autoFillSource:    copyStringMap(m.autoFillSource),
		currentStageIndex: m.currentStageIndex,
	}
	m.undoStack = append(m.undoStack, snapshot)
	// Clear redo stack when new action is taken
	m.redoStack = nil
	// Limit history size
	if len(m.undoStack) > 50 {
		m.undoStack = m.undoStack[1:]
	}
}

// undo restores the previous state from the undo stack.
func (m *model) undo() bool {
	if len(m.undoStack) == 0 {
		return false
	}
	// Save current state to redo stack
	redoSnapshot := stateSnapshot{
		tokensByCategory:  copyStringSliceMap(m.tokensByCategory),
		autoFilledTokens:  copyBoolMap(m.autoFilledTokens),
		autoFillSource:    copyStringMap(m.autoFillSource),
		currentStageIndex: m.currentStageIndex,
	}
	m.redoStack = append(m.redoStack, redoSnapshot)

	// Pop and restore from undo stack
	snapshot := m.undoStack[len(m.undoStack)-1]
	m.undoStack = m.undoStack[:len(m.undoStack)-1]
	m.tokensByCategory = snapshot.tokensByCategory
	m.autoFilledTokens = snapshot.autoFilledTokens
	m.autoFillSource = snapshot.autoFillSource
	m.currentStageIndex = snapshot.currentStageIndex
	m.rebuildCommandLine()
	m.updateCompletions()
	m.updatePreview()
	return true
}

// redo restores the next state from the redo stack.
func (m *model) redo() bool {
	if len(m.redoStack) == 0 {
		return false
	}
	// Save current state to undo stack
	undoSnapshot := stateSnapshot{
		tokensByCategory:  copyStringSliceMap(m.tokensByCategory),
		autoFilledTokens:  copyBoolMap(m.autoFilledTokens),
		autoFillSource:    copyStringMap(m.autoFillSource),
		currentStageIndex: m.currentStageIndex,
	}
	m.undoStack = append(m.undoStack, undoSnapshot)

	// Pop and restore from redo stack
	snapshot := m.redoStack[len(m.redoStack)-1]
	m.redoStack = m.redoStack[:len(m.redoStack)-1]
	m.tokensByCategory = snapshot.tokensByCategory
	m.autoFilledTokens = snapshot.autoFilledTokens
	m.autoFillSource = snapshot.autoFillSource
	m.currentStageIndex = snapshot.currentStageIndex
	m.rebuildCommandLine()
	m.updateCompletions()
	m.updatePreview()
	return true
}

// Helper functions for copying maps
func copyStringSliceMap(m map[string][]string) map[string][]string {
	result := make(map[string][]string)
	for k, v := range m {
		result[k] = append([]string{}, v...)
	}
	return result
}

func copyBoolMap(m map[string]bool) map[string]bool {
	result := make(map[string]bool)
	for k, v := range m {
		result[k] = v
	}
	return result
}

func copyStringMap(m map[string]string) map[string]string {
	result := make(map[string]string)
	for k, v := range m {
		result[k] = v
	}
	return result
}

// getRemainingStages returns the names of stages after the current one.
func (m model) getRemainingStages() []string {
	var remaining []string
	for i := m.currentStageIndex + 1; i < len(stageOrder); i++ {
		remaining = append(remaining, stageDisplayName(stageOrder[i]))
	}
	return remaining
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

	// Show addendum modal if active
	if m.showAddendumModal {
		return m.renderAddendumModal()
	}

	// Show command modal if active
	if m.showCommandModal {
		return m.renderCommandModal()
	}

	var b strings.Builder

	// Pane 1: Command input
	b.WriteString(m.renderCommandPane())
	b.WriteString("\n")

	// Pane 2: Tokens & Completions
	b.WriteString(m.renderTokensPane())
	b.WriteString("\n")

	// Pane 3: Preview or Result
	if m.showingResult {
		b.WriteString(m.renderResultPane())
	} else {
		b.WriteString(m.renderPreviewPane())
	}
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

	// warningStyle for guidance text - uses yellow/amber to draw attention
	warningStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("220"))

	toastStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("78")).
			Bold(true)

	resultHeaderStyle = lipgloss.NewStyle().
				Bold(true).
				Foreground(lipgloss.Color("214"))
)

// stageMarkerStyle for the [Stage?] marker
var stageMarkerStyle = lipgloss.NewStyle().
	Foreground(lipgloss.Color("214")).
	Bold(true)

func (m model) renderCommandPane() string {
	width := m.width - 2
	if width < 20 {
		width = 20
	}

	// Build command line with stage marker
	var cmdLine strings.Builder
	cmdLine.WriteString("> bar build")

	tokens := m.getCommandTokens()
	for _, token := range tokens {
		cmdLine.WriteString(" ")
		cmdLine.WriteString(token)
	}

	// Add stage marker if there's a current stage
	currentStage := m.getCurrentStage()
	if currentStage != "" {
		cmdLine.WriteString(" ")
		cmdLine.WriteString(stageMarkerStyle.Render(fmt.Sprintf("[%s?]", stageDisplayName(currentStage))))
	}

	// Show cursor/filter partial
	partial := m.getFilterPartial()
	if partial != "" {
		cmdLine.WriteString(" ")
		cmdLine.WriteString(partial)
	}
	cmdLine.WriteString("_")

	return paneStyle.Width(width).Render(cmdLine.String())
}

func (m model) renderTokensPane() string {
	// paneStyle has border (2 chars) and padding (2 chars), so content area is width - 4
	boxWidth := m.width - 2      // width for the pane box itself
	contentWidth := boxWidth - 4 // subtract border (2) + padding (2) for content area
	if contentWidth < 20 {
		contentWidth = 20
	}

	// Calculate available height for this pane
	paneHeight := (m.height - 10) / 3
	if paneHeight < 4 {
		paneHeight = 4
	}

	displayTokens := m.getDisplayTokens()

	var left strings.Builder
	// Header with count
	if len(displayTokens) == 0 {
		left.WriteString(headerStyle.Render("TOKENS"))
	} else {
		left.WriteString(headerStyle.Render(fmt.Sprintf("TOKENS (%d)", len(displayTokens))))
	}
	left.WriteString("\n")

	if len(displayTokens) == 0 {
		left.WriteString(dimStyle.Render("(none selected)"))
		left.WriteString("\n")
		left.WriteString(dimStyle.Render("Type to search, Enter to select"))
	} else {
		// Build tree with lipgloss/tree
		tokenTree := tree.New()
		for _, dt := range displayTokens {
			if dt.Category != "" {
				// Show "Category: value" format
				tokenTree = tokenTree.Child(fmt.Sprintf("%s: %s",
					categoryStyle.Render(dt.Category),
					tokenStyle.Render(dt.Value)))
			} else {
				// Fallback for unknown tokens
				tokenTree = tokenTree.Child(tokenStyle.Render(dt.Value))
			}
		}
		tokenTree = tokenTree.Enumerator(tree.RoundedEnumerator)
		left.WriteString(tokenTree.String())
	}

	var right strings.Builder
	// Show current stage as header instead of generic "COMPLETIONS"
	currentStage := m.getCurrentStage()
	if currentStage != "" {
		right.WriteString(headerStyle.Render(strings.ToUpper(stageDisplayName(currentStage))))
	} else {
		right.WriteString(headerStyle.Render("COMPLETE"))
	}
	right.WriteString("\n")

	// Calculate description width based on available space
	// Right pane gets more space; use dynamic description truncation
	rightWidth := contentWidth - (contentWidth / 3) - 3 // Give 2/3 to completions
	descWidth := rightWidth - 16                        // Account for prefix and value column
	if descWidth < 20 {
		descWidth = 20
	}
	var selectedDesc string     // Store full description of selected item
	var selectedGuidance string // Store guidance of selected item
	var selectedUseWhen string  // Store routing trigger phrase (ADR-0142)

	if currentStage == "" {
		right.WriteString(dimStyle.Render("All stages complete!"))
	} else if len(m.completions) == 0 {
		right.WriteString(dimStyle.Render("(no matches)"))
	} else {
		// Show completions with current selection highlighted
		// Reserve space for: header, "more above", completions, "more below", "Then:" hint, selected desc
		maxShow := paneHeight - 7 // -1 header, -2 scroll indicators, -2 Then+desc, -2 padding
		if maxShow < 1 {
			maxShow = 1
		}

		// Calculate visible range based on scroll offset
		startIdx := m.completionScrollOffset
		endIdx := startIdx + maxShow
		if endIdx > len(m.completions) {
			endIdx = len(m.completions)
		}

		// Always show "more above" line (empty if at top) to keep layout stable
		if startIdx > 0 {
			right.WriteString(dimStyle.Render(fmt.Sprintf("... %d more above", startIdx)))
		}
		right.WriteString("\n")

		for i := startIdx; i < endIdx; i++ {
			c := m.completions[i]
			prefix := "  "
			style := dimStyle
			if i == m.completionIndex {
				prefix = "▸ "
				style = completionSelectedStyle
				selectedDesc = c.Description   // Capture full description
				selectedGuidance = c.Guidance  // Capture guidance if present
				selectedUseWhen = c.UseWhen    // Capture routing phrase if present
			}
			display := c.Display
			if strings.TrimSpace(display) == "" {
				display = c.Value
			}
			// When display includes a label (slug — label), it already conveys context;
			// omit the inline description to avoid overflow and redundancy (ADR-0111 D4).
			// When display is just a slug, append description for context.
			var entry string
			if strings.Contains(display, "\u2014") {
				entry = fmt.Sprintf("%s%s", prefix, display)
			} else {
				entry = fmt.Sprintf("%s%-12s %s", prefix, display, truncate(c.Description, descWidth))
			}
			right.WriteString(style.Render(entry))
			right.WriteString("\n")
		}

		// Always show "more below" line (empty if at bottom) to keep layout stable
		if endIdx < len(m.completions) {
			right.WriteString(dimStyle.Render(fmt.Sprintf("... %d more below", len(m.completions)-endIdx)))
		}
		right.WriteString("\n")
	}

	// Add "Then:" hint for remaining stages
	remaining := m.getRemainingStages()
	if len(remaining) > 0 && currentStage != "" {
		hint := "Then: " + strings.Join(remaining, ", ")
		hintMaxLen := rightWidth - 2
		if hintMaxLen < 20 {
			hintMaxLen = 20
		}
		if len(hint) > hintMaxLen {
			hint = hint[:hintMaxLen-3] + "..."
		}
		right.WriteString(dimStyle.Render(hint))
		right.WriteString("\n")
	}

	// Add selected item description area (truncated description preview)
	if selectedDesc != "" || selectedGuidance != "" || selectedUseWhen != "" {
		right.WriteString("\n")
		right.WriteString(dimStyle.Render("─"))
		right.WriteString("\n")
		// Show use_when first if present — routing trigger phrase (ADR-0142)
		if selectedUseWhen != "" {
			// Show just the first sentence for brevity in the TUI
			line := selectedUseWhen
			if idx := strings.Index(selectedUseWhen, "."); idx > 0 {
				line = selectedUseWhen[:idx]
			}
			right.WriteString(dimStyle.Render("When: " + line))
			right.WriteString("\n")
		}
		// Show guidance if present (higher priority disambiguation notes)
		if selectedGuidance != "" {
			right.WriteString(warningStyle.Render("→ " + selectedGuidance))
			right.WriteString("\n")
		}
		if selectedDesc != "" {
			// Wrap and truncate description to prevent screen overflow
			// Limit to 3 lines to keep the UI compact
			wrappedDesc := wrapAndTruncateText(selectedDesc, rightWidth-2, 3)
			right.WriteString(dimStyle.Render(wrappedDesc))
		}
	}

	// Split horizontally - give 1/3 to token tree, 2/3 to completions
	leftWidth := contentWidth / 3
	rightLayoutWidth := contentWidth - leftWidth - 1 // subtract 1 for space separator

	leftContent := lipgloss.NewStyle().Width(leftWidth).Render(left.String())
	rightContent := lipgloss.NewStyle().Width(rightLayoutWidth).Render(right.String())

	combined := lipgloss.JoinHorizontal(lipgloss.Top, leftContent, " ", rightContent)

	return paneStyle.Width(boxWidth).Height(paneHeight).Render(combined)
}

func (m model) renderPreviewPane() string {
	width := m.width - 2
	if width < 20 {
		width = 20
	}

	paneHeight := m.getPreviewPaneHeight()

	var content strings.Builder
	content.WriteString(headerStyle.Render("PREVIEW"))

	// Show scroll indicator if content is scrollable
	if m.previewViewport.TotalLineCount() > m.previewViewport.Height {
		scrollPct := int(m.previewViewport.ScrollPercent() * 100)
		content.WriteString(dimStyle.Render(fmt.Sprintf(" (%d%%)", scrollPct)))
	}
	content.WriteString("\n")

	if m.previewText == "" {
		content.WriteString(dimStyle.Render("(select tokens to see preview)"))
	} else {
		// Use default style (not dimmed) for better readability
		content.WriteString(m.previewViewport.View())
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

	var keys []string
	if m.showingResult {
		keys = []string{
			"^U/^D: scroll",
			"^Y: copy",
			"^S: to subject",
			"^R: back",
			"Esc: exit",
		}
	} else {
		keys = []string{
			"Enter: select",
			"Tab: skip",
			"BS: remove",
			"^U/^D: scroll",
			"^L: subject",
			"^A: addendum",
			"^X: run",
			"^B: copy cmd",
			"^G: copy prompt",
			"Esc: exit",
		}
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

func (m model) renderAddendumModal() string {
	width := m.width - 4
	if width < 40 {
		width = 40
	}

	var content strings.Builder
	content.WriteString(headerStyle.Render("ADDENDUM INPUT"))
	content.WriteString("\n\n")
	content.WriteString(m.addendumInput.View())
	content.WriteString("\n\n")

	if m.addendum != "" {
		chars := len(m.addendum)
		content.WriteString(dimStyle.Render(fmt.Sprintf("Current: %d chars", chars)))
		content.WriteString("\n")
	}

	content.WriteString(dimStyle.Render("Ctrl+S: save | Esc: cancel"))

	return modalStyle.Width(width).Render(content.String())
}

func (m model) renderCommandModal() string {
	width := m.width - 4
	if width < 40 {
		width = 40
	}

	var content strings.Builder
	content.WriteString(headerStyle.Render("RUN COMMAND"))
	content.WriteString("\n\n")
	content.WriteString(m.shellCommandInput.View())
	content.WriteString("\n\n")

	// Show last command if different
	if m.lastShellCommand != "" && m.lastShellCommand != m.shellCommandInput.Value() {
		content.WriteString(dimStyle.Render(fmt.Sprintf("Last: %s", m.lastShellCommand)))
		content.WriteString("\n")
	}

	content.WriteString(dimStyle.Render("Enter: run | Esc: cancel"))

	return modalStyle.Width(width).Render(content.String())
}

func (m model) renderResultPane() string {
	width := m.width - 2
	if width < 20 {
		width = 20
	}

	paneHeight := m.getPreviewPaneHeight()

	var content strings.Builder
	content.WriteString(resultHeaderStyle.Render("RESULT"))
	content.WriteString(dimStyle.Render(fmt.Sprintf(" (%s)", m.lastShellCommand)))

	// Show scroll indicator if content is scrollable
	if m.resultViewport.TotalLineCount() > m.resultViewport.Height {
		scrollPct := int(m.resultViewport.ScrollPercent() * 100)
		content.WriteString(dimStyle.Render(fmt.Sprintf(" %d%%", scrollPct)))
	}
	content.WriteString("\n")

	if m.commandResult == "" {
		content.WriteString(dimStyle.Render("(no output)"))
	} else {
		content.WriteString(m.resultViewport.View())
	}

	return paneStyle.Width(width).Height(paneHeight).Render(content.String())
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
