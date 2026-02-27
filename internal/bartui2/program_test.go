package bartui2

import (
	"context"
	"fmt"
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

func TestSnapshotBasicLayout(t *testing.T) {
	preview := func(subject string, addendum string, tokens []string) (string, error) {
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
	if !strings.Contains(view, "Task") {
		t.Error("expected 'Task' category label in view")
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
	preview := func(subject string, addendum string, tokens []string) (string, error) {
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
			Key:           "task",
			Label:         "Task",
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

// testCategoriesWithGuidance returns test categories that include guidance for testing ADR-0114.
func testCategoriesWithGuidance() []bartui.TokenCategory {
	return []bartui.TokenCategory{
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "fix", Slug: "fix", Label: "Fix", Description: "Reformat content", Guidance: "In bar's grammar, fix means reformat — not debug."},
				{Value: "make", Slug: "make", Label: "Make", Description: "Create new content"},
			},
		},
		{
			Key:           "channel",
			Label:         "Channel",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "codetour", Slug: "codetour", Label: "CodeTour", Description: "Code tour format", Guidance: "Best for code-navigation: fix, make, show. Avoid with sim, probe."},
				{Value: "slack", Slug: "slack", Label: "Slack", Description: "Slack format"},
			},
		},
	}
}

// testCategoriesWithUseWhen returns test categories that include use_when for testing ADR-0142.
func testCategoriesWithUseWhen() []bartui.TokenCategory {
	return []bartui.TokenCategory{
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "show", Slug: "show", Label: "Show", Description: "Explain or describe", UseWhen: "Use when explaining concepts to an audience."},
				{Value: "make", Slug: "make", Label: "Make", Description: "Create new content", UseWhen: "Use when creating new artifacts."},
			},
		},
		{
			Key:           "completeness",
			Label:         "Completeness",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "full", Slug: "full", Label: "Full", Description: "Thorough answer", UseWhen: "Use when you need comprehensive coverage."},
				{Value: "gist", Slug: "gist", Label: "Gist", Description: "Concise summary"},
			},
		},
	}
}

// TestCompletionDisplayUsesLabel specifies that when a TokenOption.Label is set,
// the completion Display uses it rather than the raw slug or value (ADR-0111 D4 tui2 fix).
func TestCompletionDisplayUsesLabel(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.commandInput.SetValue("bar build ")
	m.updateCompletions()

	// testCategories task options have Value "todo", Slug "todo", Label "Todo"
	// Display must be "slug — label" format (ADR-0111 D4)
	for _, c := range m.completions {
		if c.Value == "todo" {
			if c.Display != "todo — Todo" {
				t.Errorf("completion Display for 'todo' must be 'todo — Todo'; got %q (ADR-0111 D4)", c.Display)
			}
		}
	}
}

// TestCompletionGuidanceRenderedInDetailPane specifies that when a completion has Guidance,
// it appears in the detail pane when selected (ADR-0114).
func TestCompletionGuidanceRenderedInDetailPane(t *testing.T) {
	opts := Options{
		TokenCategories: testCategoriesWithGuidance(),
		InitialWidth:    80,
		InitialHeight:   24,
	}
	m := newModel(opts)
	m.commandInput.SetValue("bar build ")
	m.updateCompletions()

	// Select the first completion (fix, which has guidance)
	if len(m.completions) == 0 {
		t.Fatal("expected completions")
	}
	m.selectCompletion(m.completions[0])

	// Render the view
	view := m.View()

	// Guidance should appear in the detail pane with the arrow indicator
	// (The guidance shown is for the next stage's completions after selecting task)
	if !strings.Contains(view, "→ Best for code-navigation") {
		t.Errorf("expected guidance to appear in detail pane, got: %s", view)
	}

	// Verify the task completion was added
	tokens := m.getCommandTokens()
	if len(tokens) != 1 || tokens[0] != "fix" {
		t.Errorf("expected 'fix' token, got: %v", tokens)
	}
}

// TestCompletionUseWhenRenderedInDetailPane specifies that when a completion has UseWhen,
// it appears in the detail pane when selected (ADR-0142).
func TestCompletionUseWhenRenderedInDetailPane(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategoriesWithUseWhen(),
		InitialTokens:   []string{"show"}, // Select task first
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.updateCompletions()

	// After selecting "show" task, should be at completeness stage
	// Find the "full" completion which has UseWhen
	var fullCompletion *completion
	for i := range m.completions {
		if m.completions[i].Value == "full" {
			fullCompletion = &m.completions[i]
			break
		}
	}
	if fullCompletion == nil {
		t.Fatalf("expected to find 'full' completion, got: %v", m.completions)
	}

	// Select the full completion
	m.completionIndex = 0
	for i, c := range m.completions {
		if c.Value == "full" {
			m.completionIndex = i
			break
		}
	}

	// Render the view
	view := m.View()

	// UseWhen should appear in the detail pane
	if !strings.Contains(view, "Use when you need comprehensive coverage") {
		t.Errorf("expected use_when to appear in detail pane, got: %s", view)
	}
}

// testCategoriesWithKanji returns test categories that include kanji for testing ADR-0143.
func testCategoriesWithKanji() []bartui.TokenCategory {
	return []bartui.TokenCategory{
		{
			Key:           "completeness",
			Label:         "Completeness",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "full", Slug: "full", Label: "Full", Description: "Thorough answer", Kanji: "全"},
				{Value: "gist", Slug: "gist", Label: "Gist", Description: "Concise summary", Kanji: "略"},
			},
		},
		{
			Key:           "scope",
			Label:         "Scope",
			MaxSelections: 2,
			Options: []bartui.TokenOption{
				{Value: "act", Slug: "act", Label: "Act", Description: "Actions focus", Kanji: "為"},
				{Value: "thing", Slug: "thing", Label: "Thing", Description: "Entities focus", Kanji: "物"},
			},
		},
	}
}

// TestCompletionKanjiPresent specifies that when a TokenOption.Kanji is set,
// the completion includes it (ADR-0143).
func TestCompletionKanjiPresent(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategoriesWithKanji(),
		InitialTokens:   []string{"todo"}, // Select task first to advance to next stage
		InitialWidth:    80,
		InitialHeight:   24,
	})
	// After selecting "todo" task, should be at completeness stage
	// Completeness options should include kanji
	m.updateCompletions()

	// Find "full" which has Kanji "全"
	// The completion struct must include Kanji field for ADR-0143
	for _, c := range m.completions {
		if c.Value == "full" {
			// This will fail until we add Kanji field to completion struct
			if c.Kanji != "全" {
				t.Errorf("expected Kanji='全' for 'full', got Kanji=%q (ADR-0143)", c.Kanji)
			}
			return
		}
	}
	t.Errorf("expected to find completion for 'full', got: %v", m.completions)
}

// TestCompletionKanjiRenderedInView specifies that when a completion has Kanji,
// it appears in the rendered view (ADR-0143).
func TestCompletionKanjiRenderedInView(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategoriesWithKanji(),
		InitialTokens:   []string{"todo"}, // Select task first to advance to next stage
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.updateCompletions()

	// Render the view
	view := m.View()

	// Kanji "全" should appear in the rendered view for "full" token
	if !strings.Contains(view, "全") {
		t.Errorf("expected kanji '全' to appear in rendered view, got: %s", view)
	}
}

// TestCompletionEntryOmitsDescriptionWhenLabelPresent verifies that when a completion
// has a label (slug — label format), the rendered view entry does not also append the
// inline description. The label already provides context; description appears only in
// the detail pane. This prevents overflow on long labels (ADR-0111 D4 rendering fix).
func TestCompletionEntryOmitsDescriptionWhenLabelPresent(t *testing.T) {
	opts := Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	}
	view, err := Snapshot(opts)
	if err != nil {
		t.Fatalf("Snapshot failed: %v", err)
	}

	// The view must contain the slug-label form.
	if !strings.Contains(view, "todo — Todo") {
		t.Error("expected 'todo — Todo' in view (ADR-0111 D4)")
	}

	// The inline entry must NOT append the description after the label.
	// "Return a todo list" is the Description for "todo"; it should only appear
	// in the detail pane (after the separator line), not on the completion entry line.
	if strings.Contains(view, "todo — Todo  Return a todo list") ||
		strings.Contains(view, "todo — TodoReturn a todo list") {
		t.Error("completion entry must not include inline description when label is present (ADR-0111 D4)")
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

	// First stage is "task" which has 2 options in testCategories
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

	// Should show stage header (first stage is "task" -> "TASK")
	if !strings.Contains(view, "TASK") {
		t.Error("expected TASK stage header in view")
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
	if category != "Task" {
		t.Errorf("expected category 'Task' for 'todo', got %q", category)
	}

	// Test another category
	category = m.getCategoryForToken("focus")
	if category != "Scope" {
		t.Errorf("expected category 'Scope' for 'focus', got %q", category)
	}

	// Test case-insensitive matching
	category = m.getCategoryForToken("TODO")
	if category != "Task" {
		t.Errorf("expected category 'Task' for 'TODO' (case-insensitive), got %q", category)
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
	if !strings.Contains(view, "Task") {
		t.Error("expected 'Task' category label for 'todo' token")
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
	preview := func(subject string, addendum string, tokens []string) (string, error) {
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
		text, err := m.preview(m.subject, m.addendum, m.getAllTokensInOrder())
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

	// Copy command to clipboard (no tokens selected)
	m.copyCommandToClipboard()

	// Should have copied the command (no trailing space in copied command)
	if copiedText != "bar build" {
		t.Errorf("expected clipboard to contain 'bar build', got %q", copiedText)
	}

	// Should show toast
	if m.toastMessage != "Copied command to clipboard!" {
		t.Errorf("expected toast 'Copied command to clipboard!', got %q", m.toastMessage)
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
		InitialTokens:   []string{"todo", "focus"}, // Add tokens properly via InitialTokens
		ClipboardWrite:  clipboardWrite,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Copy command to clipboard
	m.copyCommandToClipboard()

	// Should have copied the command with tokens (no trailing space)
	if copiedText != "bar build todo focus" {
		t.Errorf("expected clipboard to contain 'bar build todo focus', got %q", copiedText)
	}
}

func TestPersonaPresetUsesSpokenSlugInCommand(t *testing.T) {
	categories := []bartui.TokenCategory{
		{
			Key:           "persona_preset",
			Label:         "Preset",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "coach_junior", Slug: "coach", Label: "Coach junior", Description: "Coach junior"},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true
	m.tokensByCategory["persona_preset"] = []string{"coach_junior"}

	m.rebuildCommandLine()

	// Persona presets no longer need persona= prefix - bar build recognizes them by order
	command := strings.TrimSpace(strings.TrimPrefix(m.commandInput.Value(), "bar build"))
	if command != "coach" {
		t.Fatalf("expected command input to use spoken slug without prefix, got %q", command)
	}

	clipboard := m.buildCommandForClipboard()
	if clipboard != "bar build coach" {
		t.Fatalf("expected clipboard command to use spoken slug without prefix, got %q", clipboard)
	}

	display := m.getDisplayTokens()
	if len(display) != 1 {
		t.Fatalf("expected display list with one entry, got %d", len(display))
	}
	if display[0].Value != "coach" {
		t.Fatalf("expected display to show spoken slug, got %q", display[0].Value)
	}
}

func TestDirectionalTokenUsesSlugInCommand(t *testing.T) {
	categories := []bartui.TokenCategory{
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "todo", Slug: "todo", Label: "Todo", Description: "Todo"},
			},
		},
		{
			Key:           "directional",
			Label:         "Directional",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "fly rog", Slug: "fly-rog", Label: "Fly rog", Description: "Fly rog"},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true
	m.tokensByCategory["task"] = []string{"todo"}
	m.tokensByCategory["directional"] = []string{"fly rog"}

	m.rebuildCommandLine()

	command := strings.TrimSpace(strings.TrimPrefix(m.commandInput.Value(), "bar build"))
	if !strings.Contains(command, "fly-rog") {
		t.Fatalf("expected command input to contain slug 'fly-rog', got %q", command)
	}

	clipboard := m.buildCommandForClipboard()
	if !strings.Contains(clipboard, "fly-rog") {
		t.Fatalf("expected clipboard command to contain slug 'fly-rog', got %q", clipboard)
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
		Preview: func(subject string, addendum string, tokens []string) (string, error) {
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

	preview := func(subject string, addendum string, tokens []string) (string, error) {
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

	preview := func(subject string, addendum string, tokens []string) (string, error) {
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

func TestBackspaceNavigatesBackward(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialTokens:   []string{"todo"},
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// After selecting "todo" (static), should be at completeness stage
	if m.getCurrentStage() != "completeness" {
		t.Fatalf("expected to be at completeness stage, got %s", m.getCurrentStage())
	}

	// Press Backspace with no filter - should remove "todo" and go back to static stage
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyBackspace})
	m2 := updated.(model)

	// Should be back at static stage
	if m2.getCurrentStage() != "task" {
		t.Errorf("expected to go back to static stage, got %s", m2.getCurrentStage())
	}

	// Should have no tokens
	if len(m2.getAllTokensInOrder()) != 0 {
		t.Errorf("expected no tokens after backspace, got %v", m2.getAllTokensInOrder())
	}
}

func TestParseEscapeHatch(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})

	// Valid escape hatch
	category, value, ok := m.parseEscapeHatch("scope=focus")
	if !ok {
		t.Error("expected escape hatch to parse successfully")
	}
	if category != "scope" {
		t.Errorf("expected category 'scope', got %q", category)
	}
	if value != "focus" {
		t.Errorf("expected value 'focus', got %q", value)
	}

	// Invalid - no equals
	_, _, ok = m.parseEscapeHatch("focus")
	if ok {
		t.Error("expected escape hatch without = to fail")
	}

	// Invalid - unknown category
	_, _, ok = m.parseEscapeHatch("unknown=value")
	if ok {
		t.Error("expected escape hatch with unknown category to fail")
	}

	// Invalid - empty value
	_, _, ok = m.parseEscapeHatch("scope=")
	if ok {
		t.Error("expected escape hatch with empty value to fail")
	}
}

func TestApplyEscapeHatch(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Apply escape hatch to add a token directly
	ok := m.applyEscapeHatch("scope", "focus")
	if !ok {
		t.Error("expected escape hatch to apply successfully")
	}

	// Check token was added
	tokens := m.tokensByCategory["scope"]
	if len(tokens) != 1 || tokens[0] != "focus" {
		t.Errorf("expected scope to have 'focus', got %v", tokens)
	}

	// Try to add duplicate - should fail
	ok = m.applyEscapeHatch("scope", "focus")
	if ok {
		t.Error("expected duplicate escape hatch to fail")
	}

	// Invalid value - should fail
	ok = m.applyEscapeHatch("scope", "nonexistent")
	if ok {
		t.Error("expected invalid value escape hatch to fail")
	}
}

func TestStageOrderIncludesPersonaStages(t *testing.T) {
	// Verify persona stages are at the beginning
	expectedPersonaStages := []string{"persona_preset", "intent", "voice", "audience", "tone"}
	for i, stage := range expectedPersonaStages {
		if i >= len(stageOrder) {
			t.Fatalf("stageOrder too short, missing %s", stage)
		}
		if stageOrder[i] != stage {
			t.Errorf("expected stageOrder[%d] to be %q, got %q", i, stage, stageOrder[i])
		}
	}

	// Verify static comes after persona stages
	if stageOrder[5] != "task" {
		t.Errorf("expected stageOrder[5] to be 'static', got %q", stageOrder[5])
	}
}

func TestStageDisplayNameForPersonaStages(t *testing.T) {
	tests := []struct {
		stage    string
		expected string
	}{
		{"intent", "Intent"},
		{"persona_preset", "Preset"},
		{"voice", "Voice"},
		{"audience", "Audience"},
		{"tone", "Tone"},
	}

	for _, tt := range tests {
		result := stageDisplayName(tt.stage)
		if result != tt.expected {
			t.Errorf("stageDisplayName(%q) = %q, expected %q", tt.stage, result, tt.expected)
		}
	}
}

func TestShiftTabGoesToPreviousStage(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialTokens:   []string{"todo"},
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// After selecting "todo" (static), should be at completeness stage
	if m.getCurrentStage() != "completeness" {
		t.Fatalf("expected to be at completeness stage, got %s", m.getCurrentStage())
	}

	// Press Shift+Tab - should go back to static stage
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyShiftTab})
	m2 := updated.(model)

	// Should be back at static stage
	if m2.getCurrentStage() != "task" {
		t.Errorf("expected to go back to static stage, got %s", m2.getCurrentStage())
	}

	// Token should NOT be removed (unlike Backspace)
	if len(m2.getAllTokensInOrder()) != 1 {
		t.Errorf("expected token to remain after Shift+Tab, got %v", m2.getAllTokensInOrder())
	}
}

func TestCtrlKClearsAllTokens(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialTokens:   []string{"todo", "full"},
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Should have tokens
	if len(m.getAllTokensInOrder()) != 2 {
		t.Fatalf("expected 2 tokens, got %d", len(m.getAllTokensInOrder()))
	}

	// Press Ctrl+K - should clear all tokens
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlK})
	m2 := updated.(model)

	// Should have no tokens
	if len(m2.getAllTokensInOrder()) != 0 {
		t.Errorf("expected no tokens after Ctrl+K, got %v", m2.getAllTokensInOrder())
	}

	// Should be at first stage (static, since test categories don't have persona stages)
	if m2.getCurrentStage() != "task" {
		t.Errorf("expected to be at static stage after clear, got %s", m2.getCurrentStage())
	}

	// Should show toast
	if m2.toastMessage != "Cleared all tokens" {
		t.Errorf("expected toast message, got %q", m2.toastMessage)
	}
}

func TestPresetAutoFillsOtherCategories(t *testing.T) {
	// Create categories with a preset that has Fills
	categories := []bartui.TokenCategory{
		{
			Key:           "persona_preset",
			Label:         "Preset",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{
					Value:       "coach",
					Label:       "Coach",
					Description: "Coach preset",
					Fills: map[string]string{
						"voice":    "supportive",
						"audience": "beginner",
						"tone":     "encouraging",
					},
				},
			},
		},
		{
			Key:           "voice",
			Label:         "Voice",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "supportive", Label: "Supportive"},
			},
		},
		{
			Key:           "audience",
			Label:         "Audience",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "beginner", Label: "Beginner"},
			},
		},
		{
			Key:           "tone",
			Label:         "Tone",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "encouraging", Label: "Encouraging"},
			},
		},
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "todo", Label: "Todo"},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Should be at persona_preset stage
	if m.getCurrentStage() != "persona_preset" {
		t.Fatalf("expected to start at persona_preset stage, got %s", m.getCurrentStage())
	}

	// Select the preset
	m.updateCompletions()
	if len(m.completions) == 0 {
		t.Fatal("expected preset completions")
	}
	m.selectCompletion(m.completions[0])

	// Check auto-filled values
	if voice := m.tokensByCategory["voice"]; len(voice) != 1 || voice[0] != "supportive" {
		t.Errorf("expected voice to be auto-filled with 'supportive', got %v", voice)
	}
	if audience := m.tokensByCategory["audience"]; len(audience) != 1 || audience[0] != "beginner" {
		t.Errorf("expected audience to be auto-filled with 'beginner', got %v", audience)
	}
	if tone := m.tokensByCategory["tone"]; len(tone) != 1 || tone[0] != "encouraging" {
		t.Errorf("expected tone to be auto-filled with 'encouraging', got %v", tone)
	}
}

func TestSelectedItemDescriptionArea(t *testing.T) {
	// Create categories with detailed descriptions
	categories := []bartui.TokenCategory{
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{
					Value:       "todo",
					Label:       "Todo",
					Description: "Returns a comprehensive todo list with prioritized action items",
				},
				{
					Value:       "describe",
					Label:       "Describe",
					Description: "Provides a detailed description of the subject matter",
				},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    120,
		InitialHeight:   30,
	})
	m.ready = true

	// Update completions to populate the list
	m.updateCompletions()

	// Should have completions
	if len(m.completions) == 0 {
		t.Fatal("expected completions")
	}

	// Get the view
	view := m.View()

	// Should show the full description of the selected item (first completion)
	// The selected item description should appear in the view
	expectedDesc := "Returns a comprehensive todo list with prioritized action items"
	if !strings.Contains(view, expectedDesc) {
		t.Errorf("expected view to contain full description %q", expectedDesc)
	}
}

func TestCtrlRQuickRerun(t *testing.T) {
	var runCount int
	runCommand := func(ctx context.Context, cmd string, stdin string) (string, string, error) {
		runCount++
		return fmt.Sprintf("run %d", runCount), "", nil
	}

	m := newModel(Options{
		TokenCategories: testCategories(),
		RunCommand:      runCommand,
		Preview: func(subject string, addendum string, tokens []string) (string, error) {
			return "preview text", nil
		},
		InitialWidth:  80,
		InitialHeight: 24,
	})
	m.ready = true
	m.previewText = "preview text"

	// First, configure a command via modal
	m.lastShellCommand = "echo test"

	// Now press Ctrl+R (not in result mode) - should run the last command immediately
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlR})
	m2 := updated.(model)

	// Should have run the command
	if runCount != 1 {
		t.Errorf("expected command to run once, ran %d times", runCount)
	}

	// Should be showing result
	if !m2.showingResult {
		t.Error("expected to be showing result after Ctrl+R quick rerun")
	}

	// Should have result
	if m2.commandResult != "run 1" {
		t.Errorf("expected result 'run 1', got %q", m2.commandResult)
	}
}

func TestCtrlROpensModalWhenNoLastCommand(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		RunCommand: func(ctx context.Context, cmd string, stdin string) (string, string, error) {
			return "output", "", nil
		},
		InitialWidth:  80,
		InitialHeight: 24,
	})
	m.ready = true

	// No last command set
	m.lastShellCommand = ""

	// Press Ctrl+R - should open modal instead of running
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlR})
	m2 := updated.(model)

	// Should show command modal
	if !m2.showCommandModal {
		t.Error("expected command modal to open when no last command")
	}
}

func TestCtrlSPipelinesResultToSubject(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		Preview: func(subject string, addendum string, tokens []string) (string, error) {
			return "Preview with subject: " + subject, nil
		},
		InitialWidth:  80,
		InitialHeight: 24,
	})
	m.ready = true

	// Set up result mode with command output
	m.showingResult = true
	m.commandResult = "This is the command output that should become the subject"

	// Press Ctrl+S to pipeline result into subject
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlS})
	m2 := updated.(model)

	// Should no longer be showing result
	if m2.showingResult {
		t.Error("expected to exit result mode after Ctrl+S")
	}

	// Subject should now contain the command result
	if m2.subject != "This is the command output that should become the subject" {
		t.Errorf("expected subject to contain command result, got %q", m2.subject)
	}

	// Preview should be updated with the new subject
	if !strings.Contains(m2.previewText, "command output") {
		t.Errorf("expected preview to contain new subject content, got %q", m2.previewText)
	}
}

func TestCtrlSShowsToastConfirmation(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		Preview: func(subject string, addendum string, tokens []string) (string, error) {
			return "preview", nil
		},
		InitialWidth:  80,
		InitialHeight: 24,
	})
	m.ready = true

	// Set up result mode
	m.showingResult = true
	m.commandResult = "result"

	// Press Ctrl+S
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlS})
	m2 := updated.(model)

	// Should show toast confirmation
	if m2.toastMessage == "" {
		t.Error("expected toast message after pipelining result to subject")
	}
	if !strings.Contains(m2.toastMessage, "subject") {
		t.Errorf("expected toast to mention subject, got %q", m2.toastMessage)
	}
}

func TestHotkeyBarShowsPipelineShortcut(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Set up result mode
	m.showingResult = true
	m.commandResult = "result"

	view := m.View()

	// Should show Ctrl+S pipeline shortcut in result mode hotkey bar
	if !strings.Contains(view, "^S") {
		t.Error("expected '^S' shortcut in hotkey bar during result mode")
	}
}

func TestCompletionListScrolling(t *testing.T) {
	// Create categories with many options to test scrolling
	var options []bartui.TokenOption
	for i := 1; i <= 20; i++ {
		options = append(options, bartui.TokenOption{
			Value:       fmt.Sprintf("option%d", i),
			Label:       fmt.Sprintf("Option %d", i),
			Description: fmt.Sprintf("Description for option %d", i),
		})
	}

	categories := []bartui.TokenCategory{
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options:       options,
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    120,
		InitialHeight:   30,
	})
	m.ready = true
	m.updateCompletions()

	// Should have many completions
	if len(m.completions) != 20 {
		t.Fatalf("expected 20 completions, got %d", len(m.completions))
	}

	// Initial state: first item selected, no scroll offset
	if m.completionIndex != 0 {
		t.Errorf("expected initial completionIndex 0, got %d", m.completionIndex)
	}
	if m.completionScrollOffset != 0 {
		t.Errorf("expected initial scroll offset 0, got %d", m.completionScrollOffset)
	}

	// Navigate down past visible area
	maxShow := m.getCompletionMaxShow()
	for i := 0; i < maxShow+2; i++ {
		newM, _ := m.Update(tea.KeyMsg{Type: tea.KeyDown})
		m = newM.(model)
	}

	// Should have scrolled to keep selection visible
	if m.completionIndex != maxShow+2 {
		t.Errorf("expected completionIndex %d, got %d", maxShow+2, m.completionIndex)
	}
	if m.completionScrollOffset == 0 {
		t.Error("expected scroll offset to increase after navigating past visible area")
	}

	// The selected item should still be visible in the view.
	// Options display as "slug — label" format (ADR-0111 D4).
	view := m.View()
	expectedOption := fmt.Sprintf("option%d — Option %d", maxShow+3, maxShow+3) // slug — label format
	if !strings.Contains(view, expectedOption) {
		t.Errorf("expected view to contain selected option %q after scrolling", expectedOption)
	}

	// Navigate back up
	for i := 0; i < maxShow+2; i++ {
		newM, _ := m.Update(tea.KeyMsg{Type: tea.KeyUp})
		m = newM.(model)
	}

	// Should be back at the top
	if m.completionIndex != 0 {
		t.Errorf("expected completionIndex 0 after navigating back up, got %d", m.completionIndex)
	}
	if m.completionScrollOffset != 0 {
		t.Errorf("expected scroll offset 0 after navigating back up, got %d", m.completionScrollOffset)
	}
}

func TestAutoFilledTokensTracked(t *testing.T) {
	// Create categories with a preset that has Fills
	categories := []bartui.TokenCategory{
		{
			Key:           "persona_preset",
			Label:         "Preset",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{
					Value:       "coach",
					Label:       "Coach",
					Description: "Coach preset",
					Fills: map[string]string{
						"voice":    "supportive",
						"audience": "beginner",
						"tone":     "encouraging",
					},
				},
			},
		},
		{
			Key:           "voice",
			Label:         "Voice",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "supportive", Label: "Supportive"},
			},
		},
		{
			Key:           "audience",
			Label:         "Audience",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "beginner", Label: "Beginner"},
			},
		},
		{
			Key:           "tone",
			Label:         "Tone",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "encouraging", Label: "Encouraging"},
			},
		},
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "todo", Label: "Todo"},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select the preset (which auto-fills voice/audience/tone)
	m.updateCompletions()
	m.selectCompletion(m.completions[0])

	// Auto-filled tokens should be tracked
	if !m.isAutoFilled("voice", "supportive") {
		t.Error("expected voice:supportive to be marked as auto-filled")
	}
	if !m.isAutoFilled("audience", "beginner") {
		t.Error("expected audience:beginner to be marked as auto-filled")
	}
	if !m.isAutoFilled("tone", "encouraging") {
		t.Error("expected tone:encouraging to be marked as auto-filled")
	}

	// The preset itself should NOT be auto-filled (it was manually selected)
	if m.isAutoFilled("persona_preset", "coach") {
		t.Error("expected persona_preset:coach to NOT be marked as auto-filled")
	}
}

func TestCopiedCommandExcludesAutoFilledTokens(t *testing.T) {
	var copiedText string
	clipboardWrite := func(text string) error {
		copiedText = text
		return nil
	}

	// Create categories with a preset that has Fills
	categories := []bartui.TokenCategory{
		{
			Key:           "persona_preset",
			Label:         "Preset",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{
					Value:       "coach",
					Label:       "Coach",
					Description: "Coach preset",
					Fills: map[string]string{
						"voice":    "supportive",
						"audience": "beginner",
					},
				},
			},
		},
		{
			Key:           "voice",
			Label:         "Voice",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "supportive", Label: "Supportive"},
			},
		},
		{
			Key:           "audience",
			Label:         "Audience",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "beginner", Label: "Beginner"},
			},
		},
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "todo", Label: "Todo"},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		ClipboardWrite:  clipboardWrite,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select the preset (auto-fills voice and audience)
	m.updateCompletions()
	m.selectCompletion(m.completions[0]) // coach preset

	// After preset selection, voice and audience are auto-filled.
	// Since test doesn't have tone/completeness/etc categories, we advance directly to static.
	m.updateCompletions()

	// Should now be at static stage
	currentStage := m.getCurrentStage()
	if currentStage != "task" {
		t.Fatalf("expected to be at static stage after preset selection, got %q (completions: %d)", currentStage, len(m.completions))
	}

	if len(m.completions) == 0 {
		t.Fatal("expected completions at static stage")
	}
	m.selectCompletion(m.completions[0]) // todo

	// Copy command to clipboard
	m.copyCommandToClipboard()

	// Copied command should include preset and manually selected tokens
	// but NOT the auto-filled tokens (voice, audience)
	if !strings.Contains(copiedText, "coach") {
		t.Errorf("expected copied command to contain 'coach', got %q", copiedText)
	}
	if !strings.Contains(copiedText, "todo") {
		t.Errorf("expected copied command to contain 'todo', got %q", copiedText)
	}

	// Auto-filled tokens should NOT be in the copied command
	if strings.Contains(copiedText, "supportive") {
		t.Errorf("expected copied command to NOT contain auto-filled 'supportive', got %q", copiedText)
	}
	if strings.Contains(copiedText, "beginner") {
		t.Errorf("expected copied command to NOT contain auto-filled 'beginner', got %q", copiedText)
	}
}

func TestDisplayCommandIncludesAllTokens(t *testing.T) {
	// Create categories with a preset that has Fills
	categories := []bartui.TokenCategory{
		{
			Key:           "persona_preset",
			Label:         "Preset",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{
					Value:       "coach",
					Label:       "Coach",
					Description: "Coach preset",
					Fills: map[string]string{
						"voice": "supportive",
					},
				},
			},
		},
		{
			Key:           "voice",
			Label:         "Voice",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "supportive", Label: "Supportive"},
			},
		},
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "todo", Label: "Todo"},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select the preset (auto-fills voice)
	m.updateCompletions()
	m.selectCompletion(m.completions[0])

	// The display (View) should show ALL tokens including auto-filled ones
	view := m.View()

	// Both preset and auto-filled token should appear in the display
	if !strings.Contains(view, "coach") {
		t.Error("expected display to contain 'coach'")
	}
	if !strings.Contains(view, "supportive") {
		t.Error("expected display to contain auto-filled 'supportive'")
	}
}

func TestRemovingPresetRemovesAutoFilledTokens(t *testing.T) {
	// Create categories with a preset that has Fills
	categories := []bartui.TokenCategory{
		{
			Key:           "persona_preset",
			Label:         "Preset",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{
					Value: "coach",
					Label: "Coach",
					Fills: map[string]string{
						"voice":    "supportive",
						"audience": "beginner",
						"tone":     "encouraging",
					},
				},
				{
					Value: "expert",
					Label: "Expert",
					Fills: map[string]string{
						"voice":    "authoritative",
						"audience": "professional",
						"tone":     "confident",
					},
				},
			},
		},
		{
			Key:           "voice",
			Label:         "Voice",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "supportive", Label: "Supportive"},
				{Value: "authoritative", Label: "Authoritative"},
			},
		},
		{
			Key:           "audience",
			Label:         "Audience",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "beginner", Label: "Beginner"},
				{Value: "professional", Label: "Professional"},
			},
		},
		{
			Key:           "tone",
			Label:         "Tone",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "encouraging", Label: "Encouraging"},
				{Value: "confident", Label: "Confident"},
			},
		},
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "todo", Label: "Todo"},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select the coach preset (auto-fills voice/audience/tone)
	m.updateCompletions()
	m.selectCompletion(m.completions[0]) // coach

	// Verify auto-filled tokens exist
	if len(m.tokensByCategory["voice"]) != 1 {
		t.Fatal("expected voice to be auto-filled")
	}
	if len(m.tokensByCategory["audience"]) != 1 {
		t.Fatal("expected audience to be auto-filled")
	}
	if len(m.tokensByCategory["tone"]) != 1 {
		t.Fatal("expected tone to be auto-filled")
	}

	// Remove the preset via Backspace (go back and remove last token)
	m.removeLastToken()

	// Auto-filled tokens should also be removed
	if len(m.tokensByCategory["voice"]) != 0 {
		t.Errorf("expected voice to be removed with preset, got %v", m.tokensByCategory["voice"])
	}
	if len(m.tokensByCategory["audience"]) != 0 {
		t.Errorf("expected audience to be removed with preset, got %v", m.tokensByCategory["audience"])
	}
	if len(m.tokensByCategory["tone"]) != 0 {
		t.Errorf("expected tone to be removed with preset, got %v", m.tokensByCategory["tone"])
	}

	// Preset should also be removed
	if len(m.tokensByCategory["persona_preset"]) != 0 {
		t.Errorf("expected preset to be removed, got %v", m.tokensByCategory["persona_preset"])
	}

	// Should be back at preset stage
	if m.getCurrentStage() != "persona_preset" {
		t.Errorf("expected to be back at persona_preset stage, got %s", m.getCurrentStage())
	}
}

func TestClearAllTokensClearsAutoFillTracking(t *testing.T) {
	// Create categories with a preset that has Fills
	categories := []bartui.TokenCategory{
		{
			Key:           "persona_preset",
			Label:         "Preset",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{
					Value: "coach",
					Label: "Coach",
					Fills: map[string]string{
						"voice": "supportive",
					},
				},
			},
		},
		{
			Key:           "voice",
			Label:         "Voice",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "supportive", Label: "Supportive"},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select preset (auto-fills voice)
	m.updateCompletions()
	m.selectCompletion(m.completions[0])

	// Verify auto-fill is tracked
	if !m.isAutoFilled("voice", "supportive") {
		t.Fatal("expected voice:supportive to be auto-filled before clear")
	}

	// Clear all tokens
	m.clearAllTokens()

	// Auto-fill tracking should be cleared
	if m.isAutoFilled("voice", "supportive") {
		t.Error("expected auto-fill tracking to be cleared after clearAllTokens")
	}
}

func TestUndoTokenSelection(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select a token
	m.updateCompletions()
	m.selectCompletion(m.completions[0]) // select "todo"

	// Verify token was added
	if len(m.getAllTokensInOrder()) != 1 {
		t.Fatal("expected 1 token after selection")
	}

	// Undo with Ctrl+Z
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	m2 := updated.(model)

	// Token should be removed
	if len(m2.getAllTokensInOrder()) != 0 {
		t.Errorf("expected 0 tokens after undo, got %d", len(m2.getAllTokensInOrder()))
	}
}

func TestRedoTokenSelection(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select a token
	m.updateCompletions()
	m.selectCompletion(m.completions[0]) // select "todo"

	// Undo
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	m2 := updated.(model)

	// Verify undone
	if len(m2.getAllTokensInOrder()) != 0 {
		t.Fatal("expected 0 tokens after undo")
	}

	// Redo with Ctrl+Y
	updated, _ = m2.Update(tea.KeyMsg{Type: tea.KeyCtrlY})
	m3 := updated.(model)

	// Token should be restored
	if len(m3.getAllTokensInOrder()) != 1 {
		t.Errorf("expected 1 token after redo, got %d", len(m3.getAllTokensInOrder()))
	}
}

func TestUndoMultipleSelections(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select first token
	m.updateCompletions()
	m.selectCompletion(m.completions[0]) // select "todo"

	// Select second token (at completeness stage now)
	m.updateCompletions()
	if len(m.completions) > 0 {
		m.selectCompletion(m.completions[0]) // select "full"
	}

	// Verify 2 tokens
	if len(m.getAllTokensInOrder()) != 2 {
		t.Fatalf("expected 2 tokens, got %d", len(m.getAllTokensInOrder()))
	}

	// Undo once - should remove second token
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	m2 := updated.(model)

	if len(m2.getAllTokensInOrder()) != 1 {
		t.Errorf("expected 1 token after first undo, got %d", len(m2.getAllTokensInOrder()))
	}

	// Undo again - should remove first token
	updated, _ = m2.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	m3 := updated.(model)

	if len(m3.getAllTokensInOrder()) != 0 {
		t.Errorf("expected 0 tokens after second undo, got %d", len(m3.getAllTokensInOrder()))
	}
}

func TestUndoShowsToast(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select a token
	m.updateCompletions()
	m.selectCompletion(m.completions[0])

	// Undo
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	m2 := updated.(model)

	// Should show toast
	if m2.toastMessage == "" {
		t.Error("expected toast message after undo")
	}
}

func TestUndoNothingToUndo(t *testing.T) {
	m := newModel(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Try to undo with no history
	updated, _ := m.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	m2 := updated.(model)

	// Should show "nothing to undo" toast
	if !strings.Contains(m2.toastMessage, "undo") {
		t.Errorf("expected toast about nothing to undo, got %q", m2.toastMessage)
	}
}

func TestPersonaPresetTokenPrefixed(t *testing.T) {
	// Create categories with a persona_preset category
	categories := []bartui.TokenCategory{
		{
			Key:           "persona_preset",
			Label:         "Preset",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "coach_junior", Label: "Coach Junior"},
			},
		},
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "todo", Label: "Todo"},
			},
		},
	}

	m := newModel(Options{
		TokenCategories: categories,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select the preset
	m.updateCompletions()
	m.selectCompletion(m.completions[0]) // coach_junior

	// Skip to static and select todo
	m.updateCompletions()
	m.selectCompletion(m.completions[0]) // todo

	// Get all tokens - persona_preset should be prefixed with "persona="
	tokens := m.getAllTokensInOrder()

	// Should have 2 tokens
	if len(tokens) != 2 {
		t.Fatalf("expected 2 tokens, got %d: %v", len(tokens), tokens)
	}

	// First token should be "persona=coach_junior" (prefixed)
	if tokens[0] != "persona=coach_junior" {
		t.Errorf("expected first token to be 'persona=coach_junior', got %q", tokens[0])
	}

	// Second token should be "todo" (not prefixed)
	if tokens[1] != "todo" {
		t.Errorf("expected second token to be 'todo', got %q", tokens[1])
	}
}

func TestPreviewReceivesSelectedTokens(t *testing.T) {
	var capturedTokens []string
	preview := func(subject string, addendum string, tokens []string) (string, error) {
		capturedTokens = append([]string{}, tokens...)
		return "Preview with tokens: " + strings.Join(tokens, ", "), nil
	}

	m := newModel(Options{
		TokenCategories: testCategories(),
		Preview:         preview,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	// Select "todo" from static stage
	m.updateCompletions()
	var todoCompletion completion
	for _, c := range m.completions {
		if c.Value == "todo" {
			todoCompletion = c
			break
		}
	}
	if todoCompletion.Value == "" {
		t.Fatal("expected 'todo' completion to be available")
	}
	m.selectCompletion(todoCompletion)

	// Verify token was captured by preview
	if len(capturedTokens) != 1 {
		t.Fatalf("expected 1 token captured, got %d: %v", len(capturedTokens), capturedTokens)
	}
	if capturedTokens[0] != "todo" {
		t.Errorf("expected token 'todo', got %q", capturedTokens[0])
	}

	// Now select "focus" from scope stage
	// First skip completeness stage
	m.skipCurrentStage()
	m.updateCompletions()

	var focusCompletion completion
	for _, c := range m.completions {
		if c.Value == "focus" {
			focusCompletion = c
			break
		}
	}
	if focusCompletion.Value == "" {
		t.Fatal("expected 'focus' completion to be available")
	}
	m.selectCompletion(focusCompletion)

	// Verify both tokens captured
	if len(capturedTokens) != 2 {
		t.Fatalf("expected 2 tokens captured, got %d: %v", len(capturedTokens), capturedTokens)
	}
	if capturedTokens[0] != "todo" {
		t.Errorf("expected first token 'todo', got %q", capturedTokens[0])
	}
	if capturedTokens[1] != "focus" {
		t.Errorf("expected second token 'focus', got %q", capturedTokens[1])
	}

	// Verify preview text was updated
	if !strings.Contains(m.previewText, "todo") || !strings.Contains(m.previewText, "focus") {
		t.Errorf("expected previewText to contain 'todo' and 'focus', got %q", m.previewText)
	}
}

// testCategoriesWithComposition returns test categories for ADR-0148 cross-axis composition tests.
// Categories are channel-only so the TUI starts at the channel stage immediately.
func testCategoriesChannelOnly() []bartui.TokenCategory {
	return []bartui.TokenCategory{
		{
			Key:           "channel",
			Label:         "Channel",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "shellscript", Slug: "shellscript", Label: "ShellScript", Description: "Shell script output for executable code."},
				{Value: "slack", Slug: "slack", Label: "Slack", Description: "Slack message format."},
			},
		},
	}
}

// testCategoriesTaskChannel returns test categories for direction-B tests: task+channel.
// Initializing with "shellscript" advances past channel to the task stage.
func testCategoriesTaskChannel() []bartui.TokenCategory {
	return []bartui.TokenCategory{
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "sim", Slug: "sim", Label: "Sim", Description: "Simulate a scenario."},
				{Value: "make", Slug: "make", Label: "Make", Description: "Create new content."},
			},
		},
		{
			Key:           "channel",
			Label:         "Channel",
			MaxSelections: 1,
			Options: []bartui.TokenOption{
				{Value: "shellscript", Slug: "shellscript", Label: "ShellScript", Description: "Shell script output."},
			},
		},
	}
}

// TestCrossAxisCompositionDirectionA specifies that when a channel token is in focus,
// the detail panel shows "✓ Natural" and "⚠ Caution" lines from CrossAxisCompositionFor (ADR-0148).
func TestCrossAxisCompositionDirectionA(t *testing.T) {
	compositionFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		if axis == "channel" && token == "shellscript" {
			return map[string][]string{
					"task": {"make", "fix"},
				},
				map[string]map[string]string{
					"task": {"sim": "tends to produce thin output — simulation is inherently narrative"},
				}
		}
		return nil, nil
	}

	// Height 50: paneHeight = (50-10)/3 = 13 >= 12, enabling composition sections (ADR-0148 R1).
	m := newModel(Options{
		TokenCategories:         testCategoriesChannelOnly(),
		CrossAxisCompositionFor: compositionFor,
		InitialWidth:            80,
		InitialHeight:           50,
	})
	m.ready = true
	m.updateCompletions()
	// Confirm we're at channel stage with shellscript as first completion
	if m.getCurrentStage() != "channel" {
		t.Fatalf("expected channel stage, got %q", m.getCurrentStage())
	}
	m.completionIndex = 0 // select shellscript

	view := m.View()

	if !strings.Contains(view, "✓") {
		t.Errorf("direction A: expected natural pairing indicator (✓) in view for shellscript; got:\n%s", view)
	}
	if !strings.Contains(view, "make") {
		t.Errorf("direction A: expected natural task 'make' in view for shellscript; got:\n%s", view)
	}
	if !strings.Contains(view, "⚠") {
		t.Errorf("direction A: expected cautionary indicator (⚠) in view for shellscript; got:\n%s", view)
	}
	if !strings.Contains(view, "sim") {
		t.Errorf("direction A: expected cautionary token 'sim' in view for shellscript; got:\n%s", view)
	}
}

// TestCrossAxisCompositionDirectionB specifies that when a task token is in focus and an active
// channel token has a cautionary entry for that task, the detail panel shows "⚠ With <channel>: ..."
// (ADR-0148 direction B).
func TestCrossAxisCompositionDirectionB(t *testing.T) {
	compositionFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		if axis == "channel" && token == "shellscript" {
			return map[string][]string{"task": {"make", "show"}},
				map[string]map[string]string{
					"task": {"sim": "tends to produce thin output — simulation is inherently narrative"},
				}
		}
		return nil, nil
	}

	// Initialize with shellscript channel pre-selected; task stage becomes current.
	// Height 50: paneHeight = (50-10)/3 = 13 >= 12, enabling composition sections (ADR-0148 R1).
	m := newModel(Options{
		TokenCategories:         testCategoriesTaskChannel(),
		InitialTokens:           []string{"shellscript"},
		CrossAxisCompositionFor: compositionFor,
		InitialWidth:            80,
		InitialHeight:           50,
	})
	m.ready = true
	m.updateCompletions()

	if m.getCurrentStage() != "task" {
		t.Fatalf("expected task stage after shellscript pre-selected, got %q", m.getCurrentStage())
	}

	// Select "sim" — should show cautionary signal.
	for i, c := range m.completions {
		if c.Value == "sim" {
			m.completionIndex = i
			break
		}
	}
	view := m.View()
	if !strings.Contains(view, "⚠") {
		t.Errorf("direction B: expected cautionary indicator (⚠) for sim+shellscript; got:\n%s", view)
	}
	if !strings.Contains(view, "shellscript") {
		t.Errorf("direction B: expected 'shellscript' in cautionary warning; got:\n%s", view)
	}

	// Select "make" — should show natural signal.
	for i, c := range m.completions {
		if c.Value == "make" {
			m.completionIndex = i
			break
		}
	}
	view = m.View()
	if !strings.Contains(view, "✓") {
		t.Errorf("direction B: expected natural indicator (✓) for make+shellscript; got:\n%s", view)
	}
	if !strings.Contains(view, "shellscript") {
		t.Errorf("direction B: expected 'shellscript' in natural line; got:\n%s", view)
	}
}

// TestCrossAxisChipPrefixColumn specifies that when browsing the task axis with an active
// channel token that has composition data, each task row shows a 1-char prefix:
// ✓ for natural, ⚠ for cautionary, and a space for neutral (ADR-0148 Phase 1c).
func TestCrossAxisChipPrefixColumn(t *testing.T) {
	compositionFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		if axis == "channel" && token == "shellscript" {
			return map[string][]string{
					"task": {"make"},
				},
				map[string]map[string]string{
					"task": {"sim": "tends to produce thin output — simulation is inherently narrative"},
				}
		}
		return nil, nil
	}

	// testCategoriesTaskChannel has task={sim, make} and channel={shellscript}.
	// Initializing with shellscript advances past channel to task stage.
	// Height 50: paneHeight = 13 >= 12, prefix column enabled (ADR-0148 R1).
	m := newModel(Options{
		TokenCategories:         testCategoriesTaskChannel(),
		InitialTokens:           []string{"shellscript"},
		CrossAxisCompositionFor: compositionFor,
		InitialWidth:            80,
		InitialHeight:           50,
	})
	m.ready = true
	m.updateCompletions()

	if m.getCurrentStage() != "task" {
		t.Fatalf("expected task stage, got %q", m.getCurrentStage())
	}

	view := m.View()

	if !strings.Contains(view, "⚠") {
		t.Errorf("chip prefix: expected ⚠ before cautionary token 'sim'; view:\n%s", view)
	}
	if !strings.Contains(view, "✓") {
		t.Errorf("chip prefix: expected ✓ before natural token 'make'; view:\n%s", view)
	}
}

func TestAddendumPassedToPreviewAndCommand(t *testing.T) {
	var capturedAddendum string
	preview := func(subject string, addendum string, tokens []string) (string, error) {
		capturedAddendum = addendum
		return "Preview subject=" + subject + " addendum=" + addendum, nil
	}

	m := newModel(Options{
		TokenCategories: testCategories(),
		Preview:         preview,
		InitialWidth:    80,
		InitialHeight:   24,
	})
	m.ready = true

	m.addendum = "focus on security"
	m.updatePreview()

	if capturedAddendum != "focus on security" {
		t.Errorf("expected addendum 'focus on security' passed to preview, got %q", capturedAddendum)
	}

	m.rebuildCommandLine()
	cmd := m.commandInput.Value()
	if !strings.Contains(cmd, `--addendum "focus on security"`) {
		t.Errorf("expected command to contain --addendum flag, got %q", cmd)
	}
}

// TestCrossAxisChipPrefixColumnReverse specifies that when browsing the channel axis
// with an active task token, each channel row shows a 1-char prefix:
// ⚠ if the active task is in that channel's cautionary map, ✓ if in natural list.
func TestCrossAxisChipPrefixColumnReverse(t *testing.T) {
	compositionFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		if axis == "channel" && token == "shellscript" {
			return map[string][]string{"task": {"make"}},
				map[string]map[string]string{
					"task": {"sim": "tends to produce thin output"},
				}
		}
		return nil, nil
	}

	// Initialize with sim task pre-selected; channel stage becomes current.
	m := newModel(Options{
		TokenCategories:         testCategoriesTaskChannel(),
		InitialTokens:           []string{"sim"},
		CrossAxisCompositionFor: compositionFor,
		InitialWidth:            80,
		InitialHeight:           50,
	})
	m.ready = true
	m.updateCompletions()

	if m.getCurrentStage() != "channel" {
		t.Fatalf("expected channel stage after sim pre-selected, got %q", m.getCurrentStage())
	}

	view := m.View()
	// The prefix must appear on the same line as the completion label (not just in the meta pane).
	foundPrefixOnRow := false
	for _, line := range strings.Split(view, "\n") {
		if strings.Contains(line, "⚠") && strings.Contains(line, "ShellScript") {
			foundPrefixOnRow = true
			break
		}
	}
	if !foundPrefixOnRow {
		t.Errorf("reverse prefix: expected ⚠ on same line as ShellScript when sim active; got:\n%s", view)
	}
}
