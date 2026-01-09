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
		if item.TrimmedValue == needle {
			return item, true
		}
	}
	return completionSuggestion{}, false
}

func containsSuggestionValue(list []completionSuggestion, needle string) bool {
	_, ok := findSuggestion(list, needle)
	return ok
}

func indexOfSuggestion(list []completionSuggestion, needle string) int {
	for idx, item := range list {
		if item.TrimmedValue == needle {
			return idx
		}
	}
	return -1
}

func TestGenerateCompletionScriptBash(t *testing.T) {
	script, err := GenerateCompletionScript("bash", nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(script, "__complete bash") {
		t.Fatalf("expected script to invoke bash completion backend, got: %s", script)
	}
	if strings.Contains(script, "bashcompinit") {
		t.Fatalf("expected bash script to avoid zsh initialisation, got: %s", script)
	}
}

func TestGenerateCompletionScriptZsh(t *testing.T) {
	script, err := GenerateCompletionScript("zsh", nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.Contains(script, "#compdef bar") {
		t.Fatalf("expected zsh script to declare compdef, got: %s", script)
	}
	if !strings.Contains(script, "_describe 'bar completions'") {
		t.Fatalf("expected zsh script to use _describe for metadata, got: %s", script)
	}
	if !strings.Contains(script, "__complete zsh") {
		t.Fatalf("expected zsh script to invoke zsh completion backend, got: %s", script)
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
	if strings.HasSuffix(buildSuggestion.Value, " ") {
		t.Fatalf("expected build suggestion without trailing space, got %q", buildSuggestion.Value)
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
	if strings.HasSuffix(todo.Value, " ") {
		t.Fatalf("expected static suggestion without trailing space, got %q", todo.Value)
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
	if strings.HasSuffix(full.Value, " ") {
		t.Fatalf("expected completeness suggestion without trailing space, got %q", full.Value)
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
	if strings.HasSuffix(scopeSuggestion.Value, " ") {
		t.Fatalf("expected scope suggestion without trailing space, got %q", scopeSuggestion.Value)
	}
	if containsSuggestionValue(suggestions, "scope-focus") {
		t.Fatalf("expected scope override slug to be absent from shorthand suggestions, got %v", suggestions)
	}

	overrideSuggestions, err := Complete(grammar, "bash", []string{"bar", "build", "todo", "full", "scope="}, 4)
	if err != nil {
		t.Fatalf("unexpected error fetching overrides: %v", err)
	}
	if !containsSuggestionValue(overrideSuggestions, "scope=focus") {
		t.Fatalf("expected override suggestion scope=focus, got %v", overrideSuggestions)
	}

	methodSuggestion, ok := findSuggestion(suggestions, "steps")
	if !ok {
		t.Fatalf("expected method token 'steps', got %v", suggestions)
	}
	if methodSuggestion.Category != "method" {
		t.Fatalf("expected method category for steps, got %q", methodSuggestion.Category)
	}
	if strings.HasSuffix(methodSuggestion.Value, " ") {
		t.Fatalf("expected method suggestion without trailing space, got %q", methodSuggestion.Value)
	}
}

func TestCompleteOverrideSuggestions(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "completeness=full", "scope="}
	suggestions, err := Complete(grammar, "bash", words, 4)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	slug := "scope=focus"
	suggestion, ok := findSuggestion(suggestions, slug)
	if !ok {
		t.Fatalf("expected override suggestion %q, got %v", slug, suggestions)
	}
	if suggestion.Category != "override.scope" {
		t.Fatalf("expected override category 'override.scope', got %q", suggestion.Category)
	}
	if trimmed := strings.TrimSpace(suggestion.Value); trimmed != slug {
		t.Fatalf("expected override value %q, got %q", slug, trimmed)
	}
	if containsSuggestionValue(suggestions, "scope-focus") {
		t.Fatalf("did not expect slug-only override suggestion, got %v", suggestions)
	}
	if strings.HasSuffix(suggestion.Value, " ") {
		t.Fatalf("expected override suggestion without trailing space, got %q", suggestion.Value)
	}
	if strings.TrimSpace(suggestion.Description) == "" {
		t.Fatalf("expected override description to be populated")
	}
}

func TestCompleteDirectionalSuggestionsWithoutStatic(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !containsSuggestionValue(suggestions, "slack") {
		t.Fatalf("expected channel suggestion 'slack', got %v", suggestions)
	}
	if !containsSuggestionValue(suggestions, "fly-rog") {
		t.Fatalf("expected directional suggestion 'fly-rog', got %v", suggestions)
	}
}

func TestCompletePersonaStage(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "full", "focus", "system", "steps", "analysis", "checklist", "slack", "fog", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	presetSlug := grammar.slugForToken("persona=coach_junior")
	if presetSlug == "" {
		presetSlug = "persona=coach_junior"
	}
	preset, ok := findSuggestion(suggestions, presetSlug)
	if !ok {
		t.Fatalf("expected persona preset slug %q, got %v", presetSlug, suggestions)
	}
	if preset.Category != "persona.preset" {
		t.Fatalf("expected persona preset category, got %q", preset.Category)
	}
	if trimmed := strings.TrimSpace(preset.Value); trimmed != presetSlug {
		t.Fatalf("expected persona preset value %q, got %q", presetSlug, trimmed)
	}
	if strings.HasSuffix(preset.Value, " ") {
		t.Fatalf("expected persona preset suggestion without trailing space, got %q", preset.Value)
	}
	voiceSlug := "as-teacher"
	voice, ok := findSuggestion(suggestions, voiceSlug)
	if !ok {
		t.Fatalf("expected persona voice slug %q, got %v", voiceSlug, suggestions)
	}
	if voice.Category != "persona.voice" {
		t.Fatalf("expected persona voice category, got %q", voice.Category)
	}
	if trimmed := strings.TrimSpace(voice.Value); trimmed != voiceSlug {
		t.Fatalf("expected persona voice value %q, got %q", voiceSlug, trimmed)
	}
	if strings.HasSuffix(voice.Value, " ") {
		t.Fatalf("expected persona voice suggestion without trailing space, got %q", voice.Value)
	}
	if strings.TrimSpace(voice.Description) == "" {
		t.Fatalf("expected persona voice description to be populated")
	}
}

func TestCompleteDirectionalSuggestionsWithoutChannel(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "focus", "announce", "adr", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !containsSuggestionValue(suggestions, "slack") {
		t.Fatalf("expected channel suggestion 'slack', got %v", suggestions)
	}
	if !containsSuggestionValue(suggestions, "fly-rog") {
		t.Fatalf("expected directional suggestion 'fly-rog', got %v", suggestions)
	}
}

func TestCompleteDirectionalSuggestionsWithoutForm(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "focus", "announce", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !containsSuggestionValue(suggestions, "slack") {
		t.Fatalf("expected channel suggestion 'slack', got %v", suggestions)
	}
	if !containsSuggestionValue(suggestions, "fly-rog") {
		t.Fatalf("expected directional suggestion 'fly-rog', got %v", suggestions)
	}
}

func TestCompleteOptionalAxesWithoutStatic(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	catalog := newCompletionCatalog(grammar)

	words := []string{"bar", "build", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	expected := make([]string, 0)
	addToken := func(token string) {
		if token == "" {
			return
		}
		slug := grammar.slugForToken(token)
		if slug != "" {
			expected = append(expected, slug)
			return
		}
		expected = append(expected, token)
	}

	if len(catalog.completeness) > 0 {
		addToken(catalog.completeness[0])
	}
	if len(catalog.scope) > 0 {
		addToken(catalog.scope[0])
	}
	if len(catalog.method) > 0 {
		addToken(catalog.method[0])
	}
	if len(catalog.form) > 0 {
		addToken(catalog.form[0])
	}
	if len(catalog.channel) > 0 {
		addToken(catalog.channel[0])
	}
	if len(catalog.directional) > 0 {
		addToken(catalog.directional[0])
	}
	if len(catalog.personaPreset) > 0 {
		addToken(catalog.personaPreset[0])
	}
	if len(catalog.personaVoice) > 0 {
		addToken(catalog.personaVoice[0])
	}
	if len(catalog.personaAudience) > 0 {
		addToken(catalog.personaAudience[0])
	}
	if len(catalog.personaTone) > 0 {
		addToken(catalog.personaTone[0])
	}
	if len(catalog.personaIntent) > 0 {
		addToken(catalog.personaIntent[0])
	}

	for _, value := range expected {
		if !containsSuggestionValue(suggestions, value) {
			t.Fatalf("expected optional suggestion %q, got %v", value, suggestions)
		}
	}

	todoIdx := indexOfSuggestion(suggestions, "todo")
	if todoIdx == -1 {
		t.Fatalf("expected static suggestion 'todo', got %v", suggestions)
	}
	for _, value := range expected {
		idx := indexOfSuggestion(suggestions, value)
		if idx == -1 {
			t.Fatalf("expected suggestion %q to have index", value)
		}
		if idx < todoIdx {
			t.Fatalf("expected %q to appear after static suggestion 'todo'", value)
		}
	}
}

func TestCompleteOptionalOrderingFollowsAxisPriority(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	catalog := newCompletionCatalog(grammar)

	words := []string{"bar", "build", "todo", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	order := make([]string, 0)
	addToken := func(token string) {
		if token == "" {
			return
		}
		slug := grammar.slugForToken(token)
		if slug != "" {
			order = append(order, slug)
			return
		}
		order = append(order, token)
	}

	for _, axis := range grammar.axisPriority {
		var tokens []string
		switch axis {
		case "completeness":
			tokens = catalog.completeness
		case "scope":
			tokens = catalog.scope
		case "method":
			tokens = catalog.method
		case "form":
			tokens = catalog.form
		case "channel":
			tokens = catalog.channel
		case "directional":
			tokens = catalog.directional
		default:
			tokens = sortedAxisTokens(grammar, axis)
		}
		if len(tokens) == 0 {
			continue
		}
		addToken(tokens[0])
	}

	if len(catalog.personaPreset) > 0 {
		addToken(catalog.personaPreset[0])
	}
	if len(catalog.personaVoice) > 0 {
		addToken(catalog.personaVoice[0])
	}
	if len(catalog.personaAudience) > 0 {
		addToken(catalog.personaAudience[0])
	}
	if len(catalog.personaTone) > 0 {
		addToken(catalog.personaTone[0])
	}
	if len(catalog.personaIntent) > 0 {
		addToken(catalog.personaIntent[0])
	}

	for _, value := range order {
		if !containsSuggestionValue(suggestions, value) {
			t.Fatalf("expected suggestion %q, got %v", value, suggestions)
		}
	}
	for i := 0; i < len(order)-1; i++ {
		first := indexOfSuggestion(suggestions, order[i])
		second := indexOfSuggestion(suggestions, order[i+1])
		if first == -1 || second == -1 {
			t.Fatalf("expected indexes for %q and %q", order[i], order[i+1])
		}
		if first > second {
			t.Fatalf("expected %q to appear before %q", order[i], order[i+1])
		}
	}
}
