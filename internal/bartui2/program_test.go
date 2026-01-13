package bartui2

import (
	"strings"
	"testing"
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
