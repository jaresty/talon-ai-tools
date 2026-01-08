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

func findSuggestion(list []completionSuggestion, needle string) (completionSuggestion, bool) {
	for _, item := range list {
		if item.Value == needle {
			return item, true
		}
	}
	return completionSuggestion{}, false
}

func containsSuggestionValue(list []completionSuggestion, needle string) bool {
	_, ok := findSuggestion(list, needle)
	return ok
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

func TestGenerateCompletionScriptFish(t *testing.T) {
	script, err := GenerateCompletionScript("fish", nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(script, "commandline -ct") {
		t.Fatalf("expected fish script to capture current token, got: %s", script)
	}
	if !strings.Contains(script, "string split '\\t'") {
		t.Fatalf("expected fish script to parse metadata columns, got: %s", script)
	}
	if !strings.Contains(script, "complete -c bar -e") {
		t.Fatalf("expected fish script to clear existing definitions, got: %s", script)
	}
}

func TestCompleteSuggestsCommands(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	suggestions, err := Complete(grammar, "bash", []string{"bar"}, 1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	buildSuggestion, ok := findSuggestion(suggestions, "build")
	if !ok {
		t.Fatalf("expected build command in suggestions, got %v", suggestions)
	}
	if buildSuggestion.Category != "command" {
		t.Fatalf("expected build category 'command', got %q", buildSuggestion.Category)
	}
	helpsuggestion, ok := findSuggestion(suggestions, "help")
	if !ok {
		t.Fatalf("expected help command in suggestions, got %v", suggestions)
	}
	if helpsuggestion.Category != "command" {
		t.Fatalf("expected help category 'command', got %q", helpsuggestion.Category)
	}
}

func TestCompleteStaticStage(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", ""}
	suggestions, err := Complete(grammar, "bash", words, 2)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	todo, ok := findSuggestion(suggestions, "todo")
	if !ok {
		t.Fatalf("expected static token 'todo', got %v", suggestions)
	}
	if todo.Category != "static" {
		t.Fatalf("expected category 'static' for todo, got %q", todo.Category)
	}
	if strings.TrimSpace(todo.Description) == "" {
		t.Fatalf("expected todo description to be populated")
	}
}

func TestCompleteMovesToCompleteness(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", ""}
	suggestions, err := Complete(grammar, "bash", words, 3)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	full, ok := findSuggestion(suggestions, "full")
	if !ok {
		t.Fatalf("expected completeness token 'full', got %v", suggestions)
	}
	if full.Category != "completeness" {
		t.Fatalf("expected category 'completeness' for full, got %q", full.Category)
	}
	if strings.TrimSpace(full.Description) == "" {
		t.Fatalf("expected completeness description to be populated")
	}
}

func TestCompleteScopeAndMethodConcurrent(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "full", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	scopeSuggestion, ok := findSuggestion(suggestions, "focus")
	if !ok {
		t.Fatalf("expected scope token 'focus', got %v", suggestions)
	}
	if scopeSuggestion.Category != "scope" {
		t.Fatalf("expected scope category for focus, got %q", scopeSuggestion.Category)
	}
	methodSuggestion, ok := findSuggestion(suggestions, "steps")
	if !ok {
		t.Fatalf("expected method token 'steps', got %v", suggestions)
	}
	if methodSuggestion.Category != "method" {
		t.Fatalf("expected method category for steps, got %q", methodSuggestion.Category)
	}
}

func TestCompleteOverrideSuggestions(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "completeness=full", "scope="}
	suggestions, err := Complete(grammar, "bash", words, 4)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	suggestion, ok := findSuggestion(suggestions, "scope=focus")
	if !ok {
		t.Fatalf("expected override suggestion 'scope=focus', got %v", suggestions)
	}
	if suggestion.Category != "override.scope" {
		t.Fatalf("expected override category 'override.scope', got %q", suggestion.Category)
	}
	if strings.TrimSpace(suggestion.Description) == "" {
		t.Fatalf("expected override description to be populated")
	}
}

func TestCompletePersonaStage(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "full", "focus", "system", "steps", "analysis", "checklist", "slack", "fog", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	preset, ok := findSuggestion(suggestions, "persona=coach_junior")
	if !ok {
		t.Fatalf("expected persona preset suggestion, got %v", suggestions)
	}
	if preset.Category != "persona.preset" {
		t.Fatalf("expected persona preset category, got %q", preset.Category)
	}
	voice, ok := findSuggestion(suggestions, "as teacher")
	if !ok {
		t.Fatalf("expected persona voice suggestion, got %v", suggestions)
	}
	if voice.Category != "persona.voice" {
		t.Fatalf("expected persona voice category, got %q", voice.Category)
	}
	if strings.TrimSpace(voice.Description) == "" {
		t.Fatalf("expected persona voice description to be populated")
	}
}
