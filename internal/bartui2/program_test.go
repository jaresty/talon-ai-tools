package bartui2

import (
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
		InitialTokens: []string{"todo", "focus"},
		Preview:       preview,
		InitialWidth:  80,
		InitialHeight: 24,
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

	if !strings.Contains(view, "COMPLETIONS") {
		t.Error("expected COMPLETIONS header in view")
	}

	if !strings.Contains(view, "PREVIEW") {
		t.Error("expected PREVIEW header in view")
	}

	// Verify tokens are displayed
	if !strings.Contains(view, "todo") {
		t.Error("expected 'todo' token in view")
	}

	if !strings.Contains(view, "focus") {
		t.Error("expected 'focus' token in view")
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
			Key:   "static",
			Label: "Static Prompt",
			Options: []bartui.TokenOption{
				{Value: "todo", Slug: "todo", Label: "Todo", Description: "Return a todo list"},
				{Value: "infer", Slug: "infer", Label: "Infer", Description: "Infer the task"},
			},
		},
		{
			Key:   "scope",
			Label: "Scope",
			Options: []bartui.TokenOption{
				{Value: "focus", Slug: "focus", Label: "Focus", Description: "Concentrate on single topic"},
				{Value: "system", Slug: "system", Label: "System", Description: "Examine connected system"},
			},
		},
		{
			Key:   "completeness",
			Label: "Completeness",
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

	// With no filter, should show all 6 options
	m.commandInput.SetValue("bar build ")
	m.updateCompletions()

	if len(m.completions) != 6 {
		t.Fatalf("expected 6 completions with no filter, got %d: %v", len(m.completions), m.completions)
	}
}

func TestFuzzyCompletionFiltering(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})

	// Filter by "fo" should match "focus", "infer" (contains "f" but not "fo")
	// Actually "fo" should match "focus" and possibly "info" but we only have focus
	m.commandInput.SetValue("bar build fo")
	m.updateCompletions()

	// Should find "focus" (contains "fo")
	found := false
	for _, c := range m.completions {
		if c.Value == "focus" {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("expected 'focus' in completions for filter 'fo', got: %v", m.completions)
	}

	// Should NOT find "todo" (doesn't contain "fo")
	for _, c := range m.completions {
		if c.Value == "todo" {
			t.Errorf("did not expect 'todo' in completions for filter 'fo'")
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

	// "todo" is already selected, should not appear in completions
	m.commandInput.SetValue("bar build todo ")
	m.tokens = m.parseTokensFromCommand()
	m.updateCompletions()

	for _, c := range m.completions {
		if c.Value == "todo" {
			t.Errorf("selected token 'todo' should not appear in completions")
		}
	}

	// Should have 5 remaining options
	if len(m.completions) != 5 {
		t.Errorf("expected 5 completions (6 - 1 selected), got %d", len(m.completions))
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

	// Select the first completion
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
	for _, token := range m.tokens {
		if token == firstCompletion.Value {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("expected tokens to contain %q", firstCompletion.Value)
	}
}

func TestCompletionSelectionWithPartial(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})

	// Type partial "fo" then select "focus"
	m.commandInput.SetValue("bar build fo")
	m.updateCompletions()

	// Find and select "focus"
	var focusCompletion completion
	for _, c := range m.completions {
		if c.Value == "focus" {
			focusCompletion = c
			break
		}
	}

	m.selectCompletion(focusCompletion)

	// Should have "bar build focus " (partial replaced)
	expected := "bar build focus "
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

	// Should show completions in the view
	if !strings.Contains(view, "todo") || !strings.Contains(view, "Static Prompt") {
		t.Error("expected completions to show token values and categories")
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
		text, err := m.preview(m.subject, m.tokens)
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
