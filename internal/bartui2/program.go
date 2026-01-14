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

	// Preview generates prompt text from subject and tokens.
	Preview func(subject string, tokens []string) (string, error)

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
}

// completion represents a single completion option with metadata.
type completion struct {
	Value       string
	Category    string
	Description string
	// Fills specifies other categories that get auto-filled when this option is selected.
	Fills map[string]string
}

// Stage order for grammar progression (matches CLI completion order).
// Each stage corresponds to a token category key.
// Persona stages come first (optional), then static and modifiers.
var stageOrder = []string{
	"intent",         // What the user wants to accomplish (optional)
	"persona_preset", // Saved persona configuration (optional)
	"voice",          // Speaking style or persona voice (optional)
	"audience",       // Target audience for the response (optional)
	"tone",           // Emotional tone of the response (optional)
	"static",         // Static Prompt - the main prompt type
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
	case "static":
		return "Static"
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

	// Token categories (for completion)
	tokenCategories []bartui.TokenCategory

	// Stage-based progression
	currentStageIndex int // index into stageOrder

	// Completions (pane 2 right side) - filtered to current stage
	completions     []completion
	completionIndex int

	// Subject input (modal)
	subject          string
	subjectInput     textarea.Model
	showSubjectModal bool

	// Preview (pane 3) with viewport for scrolling
	previewText     string
	previewViewport viewport.Model
	preview         func(subject string, tokens []string) (string, error)

	// Command execution with viewport for scrolling result
	shellCommandInput  textinput.Model
	showCommandModal   bool
	lastShellCommand   string
	runCommand         func(ctx context.Context, command string, stdin string) (string, string, error)
	commandTimeout     time.Duration
	commandResult      string
	resultViewport     viewport.Model
	showingResult      bool

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

	// Shell command input for execution modal
	sci := textinput.New()
	sci.Placeholder = "Enter shell command (e.g., pbcopy, claude)"
	sci.CharLimit = 512
	sci.Width = 60

	// Default timeout
	timeout := opts.CommandTimeout
	if timeout == 0 {
		timeout = 30 * time.Second
	}

	// Initialize viewports for preview and result scrolling
	previewVP := viewport.New(60, 10)
	previewVP.Style = lipgloss.NewStyle()

	resultVP := viewport.New(60, 10)
	resultVP.Style = lipgloss.NewStyle()

	m := model{
		commandInput:      ti,
		tokensByCategory:  make(map[string][]string),
		tokenCategories:   opts.TokenCategories,
		subjectInput:      ta,
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
		category := m.getCategoryForToken(token)
		if category != "" {
			categoryKey := m.getCategoryKeyForToken(token)
			m.tokensByCategory[categoryKey] = append(m.tokensByCategory[categoryKey], token)
		}
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
		tokens := m.getAllTokensInOrder()
		text, err := m.preview("", tokens)
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
		case "ctrl+l":
			// Open subject input modal
			m.showSubjectModal = true
			m.subjectInput.SetValue(m.subject)
			m.subjectInput.Focus()
			m.commandInput.Blur()
			return m, textarea.Blink
		case "ctrl+enter":
			// Open command execution modal
			m.showCommandModal = true
			m.shellCommandInput.SetValue(m.lastShellCommand)
			m.shellCommandInput.Focus()
			m.commandInput.Blur()
			return m, textinput.Blink
		case "ctrl+y":
			// Copy result to clipboard (if showing result)
			if m.showingResult && m.commandResult != "" {
				m.copyResultToClipboard()
			}
			return m, nil
		case "ctrl+r":
			// Return to preview (if showing result)
			if m.showingResult {
				m.showingResult = false
				m.commandResult = ""
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
			}
			return m, nil
		case "down":
			// Navigate completions down
			if m.completionIndex < len(m.completions)-1 {
				m.completionIndex++
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
			m.clearAllTokens()
			m.updateCompletions()
			m.updatePreview()
			m.toastMessage = "Cleared all tokens"
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

		// Fuzzy match against partial
		if partial == "" || fuzzyMatch(strings.ToLower(opt.Value), partial) ||
			fuzzyMatch(strings.ToLower(opt.Slug), partial) {
			results = append(results, completion{
				Value:       opt.Value,
				Category:    category.Label,
				Description: truncate(opt.Description, 40),
				Fills:       opt.Fills,
			})
		}
	}

	m.completions = results

	// Reset index if out of bounds
	if m.completionIndex >= len(m.completions) {
		m.completionIndex = 0
	}
}

// selectCompletion adds the selected completion to the current stage.
func (m *model) selectCompletion(c completion) {
	// Add token to current stage
	currentStage := m.getCurrentStage()
	if currentStage == "" {
		return // No stage to add to
	}

	m.tokensByCategory[currentStage] = append(m.tokensByCategory[currentStage], c.Value)

	// Apply auto-fills (e.g., persona presets fill voice/audience/tone)
	if len(c.Fills) > 0 {
		for category, value := range c.Fills {
			// Only fill if not already set
			if _, exists := m.tokensByCategory[category]; !exists || len(m.tokensByCategory[category]) == 0 {
				m.tokensByCategory[category] = []string{value}
			}
		}
	}

	// Rebuild command line in grammar order
	m.rebuildCommandLine()

	// Advance to next stage if current is complete
	m.advanceToNextIncompleteStage()

	// Update completions for new stage
	m.updateCompletions()
}

// rebuildCommandLine reconstructs the command from tokens in grammar order.
func (m *model) rebuildCommandLine() {
	tokens := m.getAllTokensInOrder()
	var cmd strings.Builder
	cmd.WriteString("bar build")
	for _, token := range tokens {
		cmd.WriteString(" ")
		cmd.WriteString(token)
	}
	cmd.WriteString(" ")
	m.commandInput.SetValue(cmd.String())
	m.commandInput.CursorEnd()
}

// removeLastToken removes the last token from any stage (in reverse order).
func (m *model) removeLastToken() {
	// Find the last stage that has tokens
	for i := len(stageOrder) - 1; i >= 0; i-- {
		stage := stageOrder[i]
		if tokens, ok := m.tokensByCategory[stage]; ok && len(tokens) > 0 {
			// Remove last token from this stage
			m.tokensByCategory[stage] = tokens[:len(tokens)-1]
			// Update current stage index to this stage (since it now has room)
			m.currentStageIndex = i
			m.rebuildCommandLine()
			return
		}
	}
}

// updatePreview regenerates the preview from current tokens.
func (m *model) updatePreview() {
	if m.preview != nil {
		tokens := m.getAllTokensInOrder()
		text, err := m.preview(m.subject, tokens)
		if err == nil {
			m.previewText = text
			m.previewViewport.SetContent(text)
		}
	}
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

// getPreviewPaneHeight returns the calculated height for the preview/result pane.
func (m model) getPreviewPaneHeight() int {
	paneHeight := (m.height - 10) / 2
	if paneHeight < 6 {
		paneHeight = 6
	}
	return paneHeight
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

// getCategoryKeyForToken returns the category key for a given token value.
// Returns empty string if the token is not found in any category.
func (m model) getCategoryKeyForToken(token string) string {
	tokenLower := strings.ToLower(token)
	for _, category := range m.tokenCategories {
		for _, opt := range category.Options {
			if strings.ToLower(opt.Value) == tokenLower || strings.ToLower(opt.Slug) == tokenLower {
				return category.Key
			}
		}
	}
	return ""
}

// getAllTokensInOrder returns all selected tokens in grammar order.
func (m model) getAllTokensInOrder() []string {
	var result []string
	for _, stage := range stageOrder {
		if tokens, ok := m.tokensByCategory[stage]; ok {
			result = append(result, tokens...)
		}
	}
	return result
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
	m.currentStageIndex = 0
	m.advanceToNextIncompleteStage()
	m.rebuildCommandLine()
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

// annotationStyle for the ╰─Category annotations
var annotationStyle = lipgloss.NewStyle().
	Foreground(lipgloss.Color("240"))

func (m model) renderCommandPane() string {
	width := m.width - 2
	if width < 20 {
		width = 20
	}

	// Build command line with stage marker
	var cmdLine strings.Builder
	cmdLine.WriteString("> bar build")

	tokens := m.getAllTokensInOrder()
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

	// Build annotation line showing category for each token
	var annotations strings.Builder
	annotations.WriteString("  ") // Indent to align with "> bar build"
	prefixLen := len("bar build")
	annotations.WriteString(strings.Repeat(" ", prefixLen))

	for _, token := range tokens {
		category := m.getCategoryForToken(token)
		// Pad to align under the token
		tokenLen := len(token) + 1 // +1 for space
		if category != "" {
			annotation := fmt.Sprintf("╰─%s", category)
			annotations.WriteString(annotationStyle.Render(annotation))
			// Pad remaining space
			if len(annotation) < tokenLen {
				annotations.WriteString(strings.Repeat(" ", tokenLen-len(annotation)))
			}
		} else {
			annotations.WriteString(strings.Repeat(" ", tokenLen))
		}
	}

	var content strings.Builder
	content.WriteString(cmdLine.String())
	if len(tokens) > 0 {
		content.WriteString("\n")
		content.WriteString(annotations.String())
	}

	return paneStyle.Width(width).Render(content.String())
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

	allTokens := m.getAllTokensInOrder()

	var left strings.Builder
	// Header with count
	if len(allTokens) == 0 {
		left.WriteString(headerStyle.Render("TOKENS"))
	} else {
		left.WriteString(headerStyle.Render(fmt.Sprintf("TOKENS (%d)", len(allTokens))))
	}
	left.WriteString("\n")

	if len(allTokens) == 0 {
		left.WriteString(dimStyle.Render("(none selected)"))
		left.WriteString("\n")
		left.WriteString(dimStyle.Render("Type to search, Enter to select"))
	} else {
		// Build tree with lipgloss/tree
		tokenTree := tree.New()
		for _, token := range allTokens {
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
	// Show current stage as header instead of generic "COMPLETIONS"
	currentStage := m.getCurrentStage()
	if currentStage != "" {
		right.WriteString(headerStyle.Render(strings.ToUpper(stageDisplayName(currentStage))))
	} else {
		right.WriteString(headerStyle.Render("COMPLETE"))
	}
	right.WriteString("\n")

	if currentStage == "" {
		right.WriteString(dimStyle.Render("All stages complete!"))
	} else if len(m.completions) == 0 {
		right.WriteString(dimStyle.Render("(no matches)"))
	} else {
		// Show completions with current selection highlighted
		maxShow := paneHeight - 3 // Leave room for "Then:" hint
		if maxShow < 1 {
			maxShow = 1
		}
		for i, c := range m.completions {
			if i >= maxShow {
				right.WriteString(dimStyle.Render(fmt.Sprintf("... +%d more", len(m.completions)-maxShow)))
				right.WriteString("\n")
				break
			}
			prefix := "  "
			style := dimStyle
			if i == m.completionIndex {
				prefix = "▸ "
				style = completionSelectedStyle
			}
			// Format: "▸ focus       single topic"
			entry := fmt.Sprintf("%s%-12s %s", prefix, c.Value, truncate(c.Description, 25))
			right.WriteString(style.Render(entry))
			right.WriteString("\n")
		}
	}

	// Add "Then:" hint for remaining stages
	remaining := m.getRemainingStages()
	if len(remaining) > 0 && currentStage != "" {
		hint := "Then: " + strings.Join(remaining, ", ")
		if len(hint) > 35 {
			hint = hint[:32] + "..."
		}
		right.WriteString(dimStyle.Render(hint))
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
			"^Enter: run",
			"^B: copy",
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
