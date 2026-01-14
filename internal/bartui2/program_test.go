package bartui2

import (
	"context"
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

func TestSnapshotBasicLayout(t *testing.T) {
	preview := func(subject string, tokens []string) (string, error) {
		return "=== TASK ===\nTest preview", nil
	}

	opts := Options{
		TokenCategories: testCategories(),
		InitialTokens:   []string{"todo", "focus"},
		Preview:         preview,
		InitialWidth:    80,
		InitialHeight:   24,
	}

	view, err := Snapshot(opts)
	if err != nil {
		t.Fatalf("Snapshot failed: %v", err)
	}

	// Verify three-pane structure
	if !strings.Contains(view, "bar build") {
		t.Error("expected command input to show 'bar build'")
	}

	if !strings.Contains(view, "TOKENS") {
		t.Error("expected TOKENS header in view")
	}

	// Stage-based: shows current stage name as header (not "COMPLETIONS")
	// With todo (static) and focus (scope) selected, should be at completeness stage
	if !strings.Contains(view, "COMPLETENESS") {
		t.Error("expected COMPLETENESS stage header in view")
	}

	if !strings.Contains(view, "PREVIEW") {
		t.Error("expected PREVIEW header in view")
	}

	// Verify tokens are displayed in the TOKENS section
	if !strings.Contains(view, "Static Prompt") {
		t.Error("expected 'Static Prompt' category label in view")
	}

	if !strings.Contains(view, "Scope") {
		t.Error("expected 'Scope' category label in view")
	}

	// Verify hotkey bar
	if !strings.Contains(view, "Esc: exit") {
		t.Error("expected hotkey bar with 'Esc: exit'")
	}
}

func TestSnapshotEmptyTokens(t *testing.T) {
	preview := func(subject string, tokens []string) (string, error) {
		return "", nil
	}

	opts := Options{
		InitialTokens: nil,
		Preview:       preview,
		InitialWidth:  80,
		InitialHeight: 24,
	}

	view, err := Snapshot(opts)
	if err != nil {
		t.Fatalf("Snapshot failed: %v", err)
	}

	// Verify empty state messaging
	if !strings.Contains(view, "(none selected)") {
		t.Error("expected '(none selected)' for empty tokens")
	}

	if !strings.Contains(view, "Type to search") {
		t.Error("expected 'Type to search' hint for empty state")
	}
}

func TestParseTokensFromCommand(t *testing.T) {
	m := newModel(Options{
		InitialWidth:  80,
		InitialHeight: 24,
	})

	// Test parsing tokens from command input
	m.commandInput.SetValue("bar build todo focus")
	tokens := m.parseTokensFromCommand()

	if len(tokens) != 2 {
		t.Fatalf("expected 2 tokens, got %d: %v", len(tokens), tokens)
	}

	if tokens[0] != "todo" {
		t.Errorf("expected first token 'todo', got %q", tokens[0])
	}

	if tokens[1] != "focus" {
		t.Errorf("expected second token 'focus', got %q", tokens[1])
	}
}

func TestParseTokensFromCommandEmpty(t *testing.T) {
	m := newModel(Options{
		InitialWidth:  80,
		InitialHeight: 24,
	})

	// Test with only "bar build " prefix
	m.commandInput.SetValue("bar build ")
	tokens := m.parseTokensFromCommand()

	if len(tokens) != 0 {
		t.Fatalf("expected 0 tokens for empty command, got %d: %v", len(tokens), tokens)
	}
}

func testCategories() []bartui.TokenCategory {
	return []bartui.TokenCategory{
		{
			Key:           "static",
			Label:         "Static Prompt",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "todo", Slug: "todo", Label: "Todo", Description: "Return a todo list"},
				{Value: "infer", Slug: "infer", Label: "Infer", Description: "Infer the task"},
			},
		},
		{
			Key:           "scope",
			Label:         "Scope",
			MaxSelections: 2,
			Options: []bartui.TokenOption{
				{Value: "focus", Slug: "focus", Label: "Focus", Description: "Concentrate on single topic"},
				{Value: "system", Slug: "system", Label: "System", Description: "Examine connected system"},
			},
		},
		{
			Key:           "completeness",
			Label:         "Completeness",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "full", Slug: "full", Label: "Full", Description: "Thorough answer"},
				{Value: "gist", Slug: "gist", Label: "Gist", Description: "Concise summary"},
			},
		},
	}
}

func TestFuzzyCompletionAllOptions(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})

	// With no filter, should show all options for current stage (static has 2 options)
	m.commandInput.SetValue("bar build ")
	m.updateCompletions()

	// First stage is "static" which has 2 options in testCategories
	if len(m.completions) != 2 {
		t.Fatalf("expected 2 completions for static stage, got %d: %v", len(m.completions), m.completions)
	}
}

func TestFuzzyCompletionFiltering(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})

	// In static stage, filter by "to" should match "todo"
	m.commandInput.SetValue("bar build to")
	m.updateCompletions()

	// Should find "todo" (contains "to")
	found := false
	for _, c := range m.completions {
		if c.Value == "todo" {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("expected 'todo' in completions for filter 'to', got: %v", m.completions)
	}

	// Should NOT find "infer" (doesn't contain "to")
	for _, c := range m.completions {
		if c.Value == "infer" {
			t.Errorf("did not expect 'infer' in completions for filter 'to'")
		}
	}
}

func TestFuzzyCompletionExcludesSelected(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialTokens:   []string{"todo"},
		InitialWidth:    80,
		InitialHeight:   24,
	})

	// "todo" is already selected, so we're now at completeness stage
	// The completeness stage has 2 options: full, gist
	m.updateCompletions()

	// Should be at completeness stage (static is complete with "todo")
	currentStage := m.getCurrentStage()
	if currentStage != "completeness" {
		t.Errorf("expected to be at completeness stage, got %s", currentStage)
	}

	// Should have 2 completeness options
	if len(m.completions) != 2 {
		t.Errorf("expected 2 completeness options, got %d: %v", len(m.completions), m.completions)
	}

	// Verify "todo" is not in completions (it's from a different stage anyway)
	for _, c := range m.completions {
		if c.Value == "todo" {
			t.Errorf("selected token 'todo' should not appear in completions")
		}
	}
}

func TestCompletionSelection(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})

	m.commandInput.SetValue("bar build ")
	m.updateCompletions()

	// Select the first completion (from static stage)
	if len(m.completions) == 0 {
		t.Fatal("expected completions to be available")
	}

	firstCompletion := m.completions[0]
	m.selectCompletion(firstCompletion)

	// Verify the token was added to the command
	if !strings.Contains(m.commandInput.Value(), firstCompletion.Value) {
		t.Errorf("expected command to contain %q, got %q", firstCompletion.Value, m.commandInput.Value())
	}

	// Verify tokens were updated
	found := false
	for _, token := range m.getAllTokensInOrder() {
		if token == firstCompletion.Value {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("expected tokens to contain %q", firstCompletion.Value)
	}

	// After selecting a static token, should advance to completeness stage
	if m.getCurrentStage() != "completeness" {
		t.Errorf("expected to advance to completeness stage, got %s", m.getCurrentStage())
	}
}

func TestCompletionSelectionWithPartial(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})

	// Type partial "to" then select "todo" (from static stage)
	m.commandInput.SetValue("bar build to")
	m.updateCompletions()

	// Find and select "todo"
	var todoCompletion completion
	for _, c := range m.completions {
		if c.Value == "todo" {
			todoCompletion = c
			break
		}
	}

	if todoCompletion.Value == "" {
		t.Fatal("expected to find 'todo' in completions")
	}

	m.selectCompletion(todoCompletion)

	// Should have "bar build todo " (partial replaced, token added in grammar order)
	expected := "bar build todo "
	if m.commandInput.Value() != expected {
		t.Errorf("expected command %q, got %q", expected, m.commandInput.Value())
	}
}

func TestSnapshotWithCompletions(t *testing.T) {
	opts := Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	}

	view, err := Snapshot(opts)
	if err != nil {
		t.Fatalf("Snapshot failed: %v", err)
	}

	// Should show stage header (first stage is "static" -> "STATIC")
	if !strings.Contains(view, "STATIC") {
		t.Error("expected STATIC stage header in view")
	}

	// Should show static stage completions (todo, infer)
	if !strings.Contains(view, "todo") {
		t.Error("expected 'todo' completion in view")
	}

	// Should show the selection indicator
	if !strings.Contains(view, "▸") {
		t.Error("expected completion selection indicator '▸' in view")
	}
}

func TestGetCategoryForToken(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})

	// Test known token
	category := m.getCategoryForToken("todo")
	if category != "Static Prompt" {
		t.Errorf("expected category 'Static Prompt' for 'todo', got %q", category)
	}

	// Test another category
	category = m.getCategoryForToken("focus")
	if category != "Scope" {
		t.Errorf("expected category 'Scope' for 'focus', got %q", category)
	}

	// Test case-insensitive matching
	category = m.getCategoryForToken("TODO")
	if category != "Static Prompt" {
		t.Errorf("expected category 'Static Prompt' for 'TODO' (case-insensitive), got %q", category)
	}

	// Test unknown token
	category = m.getCategoryForToken("unknown")
	if category != "" {
		t.Errorf("expected empty category for unknown token, got %q", category)
	}
}

func TestTokenTreeWithCategoryLabels(t *testing.T) {
	opts := Options{
		TokenCategories: testCategories(),
		InitialTokens:   []string{"todo", "focus"},
		InitialWidth:    80,
		InitialHeight:   24,
	}

	view, err := Snapshot(opts)
	if err != nil {
		t.Fatalf("Snapshot failed: %v", err)
	}

	// Should show token count in header
	if !strings.Contains(view, "TOKENS (2)") {
		t.Error("expected 'TOKENS (2)' header showing token count")
	}

	// Should show category labels with tokens
	if !strings.Contains(view, "Static Prompt") {
		t.Error("expected 'Static Prompt' category label for 'todo' token")
	}

	if !strings.Contains(view, "Scope") {
		t.Error("expected 'Scope' category label for 'focus' token")
	}

	// Should use tree notation (rounded enumerator uses ╰─)
	if !strings.Contains(view, "╰─") {
		t.Error("expected tree notation '╰─' in token display")
	}
}

func TestTokenTreeEmptyShowsNoCount(t *testing.T) {
	opts := Options{
		TokenCategories: testCategories(),
		InitialTokens:   nil,
		InitialWidth:    80,
		InitialHeight:   24,
	}

	view, err := Snapshot(opts)
	if err != nil {
		t.Fatalf("Snapshot failed: %v", err)
	}

	// Should show just "TOKENS" without count when empty
	if strings.Contains(view, "TOKENS (") {
		t.Error("expected 'TOKENS' without count when no tokens selected")
	}

	if !strings.Contains(view, "TOKENS") {
		t.Error("expected 'TOKENS' header")
	}
}

func TestSubjectModalRendering(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Open subject modal
	m.showSubjectModal = true
	m.subjectInput.Focus()

	view := m.View()

	// Should show subject modal header
	if !strings.Contains(view, "SUBJECT INPUT") {
		t.Error("expected 'SUBJECT INPUT' header in modal")
	}

	// Should show hotkey hints for modal
	if !strings.Contains(view, "Ctrl+S: save") {
		t.Error("expected 'Ctrl+S: save' in modal")
	}

	if !strings.Contains(view, "Esc: cancel") {
		t.Error("expected 'Esc: cancel' in modal")
	}
}

func TestSubjectModalHidesMainView(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialTokens:   []string{"todo"},
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Open subject modal
	m.showSubjectModal = true

	view := m.View()

	// Should NOT show main view elements when modal is open
	if strings.Contains(view, "COMPLETIONS") {
		t.Error("main view COMPLETIONS should be hidden when modal is open")
	}

	if strings.Contains(view, "PREVIEW") {
		t.Error("main view PREVIEW should be hidden when modal is open")
	}
}

func TestSubjectPassedToPreview(t *testing.T) {
	var capturedSubject string
	preview := func(subject string, tokens []string) (string, error) {
		capturedSubject = subject
		return "Preview: " + subject, nil
	}

	m := newModel(Options{
		TokenCategories: testCategories(),
		Preview:         preview,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Set subject and trigger preview update
	m.subject = "Test subject content"
	if m.preview != nil {
		text, err := m.preview(m.subject, m.getAllTokensInOrder())
		if err == nil {
			m.previewText = text
		}
	}

	if capturedSubject != "Test subject content" {
		t.Errorf("expected subject 'Test subject content' passed to preview, got %q", capturedSubject)
	}
}

func TestHotkeyBarShowsSubjectShortcut(t *testing.T) {
	opts := Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	}

	view, err := Snapshot(opts)
	if err != nil {
		t.Fatalf("Snapshot failed: %v", err)
	}

	// Should show subject shortcut in hotkey bar
	if !strings.Contains(view, "subject") {
		t.Error("expected 'subject' shortcut in hotkey bar")
	}
}

func TestClipboardCopyCommand(t *testing.T) {
	var copiedText string
	clipboardWrite := func(text string) error {
		copiedText = text
		return nil
	}

	m := newModel(Options{
		TokenCategories: testCategories(),
		ClipboardWrite:  clipboardWrite,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Copy command to clipboard
	m.copyCommandToClipboard()

	// Should have copied the command
	if copiedText != "bar build " {
		t.Errorf("expected clipboard to contain 'bar build ', got %q", copiedText)
	}

	// Should show toast
	if m.toastMessage != "Copied to clipboard!" {
		t.Errorf("expected toast 'Copied to clipboard!', got %q", m.toastMessage)
	}
}

func TestClipboardCopyWithTokens(t *testing.T) {
	var copiedText string
	clipboardWrite := func(text string) error {
		copiedText = text
		return nil
	}

	m := newModel(Options{
		TokenCategories: testCategories(),
		ClipboardWrite:  clipboardWrite,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Add tokens to command
	m.commandInput.SetValue("bar build todo focus ")

	// Copy command to clipboard
	m.copyCommandToClipboard()

	// Should have copied the command with tokens
	if copiedText != "bar build todo focus " {
		t.Errorf("expected clipboard to contain 'bar build todo focus ', got %q", copiedText)
	}
}

func TestClipboardUnavailable(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		ClipboardWrite:  nil, // No clipboard
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Try to copy command
	m.copyCommandToClipboard()

	// Should show error toast
	if m.toastMessage != "Clipboard not available" {
		t.Errorf("expected toast 'Clipboard not available', got %q", m.toastMessage)
	}
}

func TestToastDisplaysInHotkeyBar(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Set toast message
	m.toastMessage = "Test toast!"

	view := m.View()

	// Should show toast instead of hotkeys
	if !strings.Contains(view, "Test toast!") {
		t.Error("expected toast message in view")
	}
}

func TestToastClearedOnKeyPress(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true
	m.toastMessage = "Test toast!"

	// Simulate a key press (down arrow) and capture returned model
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyDown})
	m2 := updated.(model)

	// Toast should be cleared
	if m2.toastMessage != "" {
		t.Errorf("expected toast to be cleared, got %q", m2.toastMessage)
	}
}

func TestCommandModalRendering(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Open command modal
	m.showCommandModal = true
	m.shellCommandInput.Focus()

	view := m.View()

	// Should show command modal header
	if !strings.Contains(view, "RUN COMMAND") {
		t.Error("expected 'RUN COMMAND' header in modal")
	}

	// Should show hotkey hints for modal
	if !strings.Contains(view, "Enter: run") {
		t.Error("expected 'Enter: run' in modal")
	}

	if !strings.Contains(view, "Esc: cancel") {
		t.Error("expected 'Esc: cancel' in modal")
	}
}

func TestCommandModalHidesMainView(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialTokens:   []string{"todo"},
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Open command modal
	m.showCommandModal = true

	view := m.View()

	// Should NOT show main view elements when modal is open
	if strings.Contains(view, "COMPLETIONS") {
		t.Error("main view COMPLETIONS should be hidden when modal is open")
	}

	if strings.Contains(view, "PREVIEW") {
		t.Error("main view PREVIEW should be hidden when modal is open")
	}
}

func TestCommandExecution(t *testing.T) {
	var capturedCmd, capturedStdin string
	runCommand := func(ctx context.Context, cmd string, stdin string) (string, string, error) {
		capturedCmd = cmd
		capturedStdin = stdin
		return "output result", "", nil
	}

	m := newModel(Options{
		TokenCategories: testCategories(),
		RunCommand:      runCommand,
		Preview: func(subject string, tokens []string) (string, error) {
			return "preview text", nil
		},
		InitialWidth:  80,
		InitialHeight: 24,
	})
	m.ready = true
	m.previewText = "preview text"

	// Execute a command
	m.executeCommand("echo test")

	if capturedCmd != "echo test" {
		t.Errorf("expected command 'echo test', got %q", capturedCmd)
	}

	if capturedStdin != "preview text" {
		t.Errorf("expected stdin 'preview text', got %q", capturedStdin)
	}

	if m.commandResult != "output result" {
		t.Errorf("expected result 'output result', got %q", m.commandResult)
	}

	if !m.showingResult {
		t.Error("expected showingResult to be true after command execution")
	}
}

func TestCommandExecutionWithStderr(t *testing.T) {
	runCommand := func(ctx context.Context, cmd string, stdin string) (string, string, error) {
		return "stdout", "stderr", nil
	}

	m := newModel(Options{
		RunCommand:    runCommand,
		InitialWidth:  80,
		InitialHeight: 24,
	})
	m.ready = true

	m.executeCommand("test")

	// Should contain both stdout and stderr
	if !strings.Contains(m.commandResult, "stdout") {
		t.Error("expected result to contain stdout")
	}
	if !strings.Contains(m.commandResult, "stderr") {
		t.Error("expected result to contain stderr")
	}
}

func TestCommandExecutionUnavailable(t *testing.T) {
	m := newModel(Options{
		RunCommand:    nil, // No command runner
		InitialWidth:  80,
		InitialHeight: 24,
	})
	m.ready = true

	m.executeCommand("test")

	if m.toastMessage != "Command execution not available" {
		t.Errorf("expected toast 'Command execution not available', got %q", m.toastMessage)
	}
}

func TestResultPaneRendering(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Set up result state (must also set viewport content)
	m.showingResult = true
	m.commandResult = "test output"
	m.resultViewport.SetContent("test output")
	m.lastShellCommand = "echo test"

	view := m.View()

	// Should show result header
	if !strings.Contains(view, "RESULT") {
		t.Error("expected 'RESULT' header in view")
	}

	// Should show command that was run
	if !strings.Contains(view, "echo test") {
		t.Error("expected command name in result header")
	}

	// Should show result content
	if !strings.Contains(view, "test output") {
		t.Error("expected result content in view")
	}
}

func TestResultModeHotkeyBar(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Set up result mode
	m.showingResult = true
	m.commandResult = "test"

	view := m.View()

	// Should show result-specific shortcuts
	if !strings.Contains(view, "^Y: copy") {
		t.Error("expected '^Y: copy' in hotkey bar during result mode")
	}

	if !strings.Contains(view, "^R: back") {
		t.Error("expected '^R: back' in hotkey bar during result mode")
	}

	// Should show scroll shortcut
	if !strings.Contains(view, "scroll") {
		t.Error("expected 'scroll' in hotkey bar during result mode")
	}
}

func TestCopyResultToClipboard(t *testing.T) {
	var copiedText string
	clipboardWrite := func(text string) error {
		copiedText = text
		return nil
	}

	m := newModel(Options{
		ClipboardWrite: clipboardWrite,
		InitialWidth:   80,
		InitialHeight:  24,
	})
	m.ready = true
	m.commandResult = "result to copy"

	m.copyResultToClipboard()

	if copiedText != "result to copy" {
		t.Errorf("expected clipboard to contain 'result to copy', got %q", copiedText)
	}

	if m.toastMessage != "Result copied to clipboard!" {
		t.Errorf("expected toast 'Result copied to clipboard!', got %q", m.toastMessage)
	}
}

func TestEscReturnFromResult(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true
	m.showingResult = true
	m.commandResult = "some result"

	// Press Esc to return to preview
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyEsc})
	m2 := updated.(model)

	if m2.showingResult {
		t.Error("expected showingResult to be false after Esc")
	}

	if m2.commandResult != "" {
		t.Error("expected commandResult to be cleared after Esc")
	}
}

func TestCtrlRReturnFromResult(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true
	m.showingResult = true
	m.commandResult = "some result"

	// Press Ctrl+R to return to preview
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'r'}, Alt: false})
	// Actually need to simulate ctrl+r properly
	updated, _ = m.Update(tea.KeyMsg{Type: tea.KeyCtrlR})
	m2 := updated.(model)

	if m2.showingResult {
		t.Error("expected showingResult to be false after Ctrl+R")
	}
}

func TestHotkeyBarShowsRunShortcut(t *testing.T) {
	opts := Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	}

	view, err := Snapshot(opts)
	if err != nil {
		t.Fatalf("Snapshot failed: %v", err)
	}

	// Should show run shortcut in hotkey bar
	if !strings.Contains(view, "run") {
		t.Error("expected 'run' shortcut in hotkey bar")
	}
}

func TestPreviewViewportScrolling(t *testing.T) {
	// Create long preview content that exceeds viewport height
	longContent := strings.Repeat("Line of preview content\n", 50)

	preview := func(subject string, tokens []string) (string, error) {
		return longContent, nil
	}

	m := newModel(Options{
		TokenCategories: testCategories(),
		Preview:         preview,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Initial position should be at top
	if m.previewViewport.YOffset != 0 {
		t.Errorf("expected viewport at top, got offset %d", m.previewViewport.YOffset)
	}

	// Scroll down with Ctrl+D
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlD})
	m2 := updated.(model)

	// Should have scrolled down
	if m2.previewViewport.YOffset == 0 {
		t.Error("expected viewport to scroll down after Ctrl+D")
	}

	// Scroll back up with Ctrl+U
	updated, _ = m2.Update(tea.KeyMsg{Type: tea.KeyCtrlU})
	m3 := updated.(model)

	// Should have scrolled up
	if m3.previewViewport.YOffset >= m2.previewViewport.YOffset {
		t.Error("expected viewport to scroll up after Ctrl+U")
	}
}

func TestResultViewportScrolling(t *testing.T) {
	// Create long result content
	longResult := strings.Repeat("Result line\n", 50)

	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true
	m.showingResult = true
	m.commandResult = longResult
	m.resultViewport.SetContent(longResult)

	// Scroll down with Ctrl+D
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlD})
	m2 := updated.(model)

	// Should have scrolled down
	if m2.resultViewport.YOffset == 0 {
		t.Error("expected result viewport to scroll down after Ctrl+D")
	}
}

func TestHotkeyBarShowsScrollShortcut(t *testing.T) {
	opts := Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	}

	view, err := Snapshot(opts)
	if err != nil {
		t.Fatalf("Snapshot failed: %v", err)
	}

	// Should show scroll shortcut in hotkey bar
	if !strings.Contains(view, "scroll") {
		t.Error("expected 'scroll' shortcut in hotkey bar")
	}
}

func TestPreviewShowsScrollPercentage(t *testing.T) {
	// Create long preview content
	longContent := strings.Repeat("Line of content\n", 100)

	preview := func(subject string, tokens []string) (string, error) {
		return longContent, nil
	}

	m := newModel(Options{
		TokenCategories: testCategories(),
		Preview:         preview,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Set viewport dimensions to make content scrollable
	m.previewViewport.Width = 70
	m.previewViewport.Height = 10
	m.previewViewport.SetContent(longContent)

	view := m.View()

	// Should show scroll percentage when content is scrollable
	if !strings.Contains(view, "%") {
		t.Error("expected scroll percentage indicator in preview pane")
	}
}
