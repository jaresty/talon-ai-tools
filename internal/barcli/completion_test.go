package barcli

import (
	"path/filepath"
	"strings"
	"testing"
)

func loadCompletionGrammar(t *testing.T) *Grammar {
	t.Helper()
	path := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	grammar, err := LoadGrammar(path)
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	return grammar
}

func containsSuggestion(list []string, needle string) bool {
	for _, item := range list {
		if item == needle {
			return true
		}
	}
	return false
}

func TestGenerateCompletionScriptBash(t *testing.T) {
	script, err := GenerateCompletionScript("bash", nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(script, "__complete bash") {
		t.Fatalf("expected script to invoke bash completion backend, got: %s", script)
	}
}

func TestCompleteSuggestsCommands(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	suggestions, err := Complete(grammar, "bash", []string{"bar"}, 1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !containsSuggestion(suggestions, "build") || !containsSuggestion(suggestions, "help") {
		t.Fatalf("expected subcommands in suggestions, got %v", suggestions)
	}
}

func TestCompleteStaticStage(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", ""}
	suggestions, err := Complete(grammar, "bash", words, 2)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !containsSuggestion(suggestions, "todo") || !containsSuggestion(suggestions, "infer") {
		t.Fatalf("expected static tokens, got %v", suggestions)
	}
}

func TestCompleteMovesToCompleteness(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", ""}
	suggestions, err := Complete(grammar, "bash", words, 3)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !containsSuggestion(suggestions, "full") || !containsSuggestion(suggestions, "gist") {
		t.Fatalf("expected completeness tokens, got %v", suggestions)
	}
}

func TestCompleteOverrideSuggestions(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "completeness=full", "scope="}
	suggestions, err := Complete(grammar, "bash", words, 4)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	expected := []string{"scope=focus", "scope=system"}
	for _, token := range expected {
		if !containsSuggestion(suggestions, token) {
			t.Fatalf("expected override suggestion %q in %v", token, suggestions)
		}
	}
}

func TestCompletePersonaStage(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "full", "focus", "system", "steps", "analysis", "checklist", "slack", "fog", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	expected := []string{"persona=coach_junior", "as teacher", "to team", "kindly", "coach"}
	for _, token := range expected {
		if !containsSuggestion(suggestions, token) {
			t.Fatalf("expected persona suggestion %q in %v", token, suggestions)
		}
	}
}
