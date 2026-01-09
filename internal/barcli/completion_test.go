package barcli

import (
	"fmt"
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

func containsSuggestionCategory(list []completionSuggestion, category string) bool {
	for _, item := range list {
		if item.Category == category {
			return true
		}
	}
	return false
}

func indexOfSuggestion(list []completionSuggestion, needle string) int {
	for idx, item := range list {
		if item.TrimmedValue == needle {
			return idx
		}
	}
	return -1
}

func skipValue(stage string) string {
	return fmt.Sprintf("%s:%s", skipSectionPrefix, stage)
}

func TestCompleteBareSkipDefaultsToPersonaStage(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", skipSectionPrefix, ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	personaCategories := []string{
		"Why (intent)",
		"Who (persona preset)",
		"Who (voice)",
		"Who (audience)",
		"How (tone)",
	}
	for _, category := range personaCategories {
		if containsSuggestionCategory(suggestions, category) {
			t.Fatalf("did not expect persona category %q after bare skip, got %v", category, suggestions)
		}
	}

	staticSlug := grammar.slugForToken("todo")
	if staticSlug == "" {
		staticSlug = "todo"
	}
	if !containsSuggestionValue(suggestions, staticSlug) {
		t.Fatalf("expected static suggestion %q after bare skip, got %v", staticSlug, suggestions)
	}
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
	if !strings.Contains(script, "complete -k -c bar -f -a") {
		t.Fatalf("expected fish script to keep completion order, got: %s", script)
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
	tuiSuggestion, ok := findSuggestion(suggestions, "tui")
	if !ok {
		t.Fatalf("expected tui command in suggestions, got %v", suggestions)
	}
	if tuiSuggestion.Category != "command" {
		t.Fatalf("expected tui category 'command', got %q", tuiSuggestion.Category)
	}
	if strings.HasSuffix(tuiSuggestion.Value, " ") {
		t.Fatalf("expected tui suggestion without trailing space, got %q", tuiSuggestion.Value)
	}
}

func TestCompleteTUIFlagsAndTokens(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	tokenSuggestions, err := Complete(grammar, "bash", []string{"bar", "tui", ""}, 2)
	if err != nil {
		t.Fatalf("unexpected error collecting token suggestions: %v", err)
	}
	if _, ok := findSuggestion(tokenSuggestions, "todo"); !ok {
		t.Fatalf("expected static token suggestions for bar tui, got %v", tokenSuggestions)
	}

	flagSuggestions, err := Complete(grammar, "bash", []string{"bar", "tui", "-"}, 2)
	if err != nil {
		t.Fatalf("unexpected error collecting flag suggestions: %v", err)
	}

	flagValues := make([]string, 0, len(flagSuggestions))
	for _, suggestion := range flagSuggestions {
		flagValues = append(flagValues, suggestion.TrimmedValue)
	}

	if !containsSuggestionValue(flagSuggestions, "--grammar") {
		t.Fatalf("expected --grammar flag suggestion for bar tui, got %v", flagValues)
	}

	forbiddenFlags := []string{"--prompt", "--input", "--output", "--json"}
	for _, forbidden := range forbiddenFlags {
		if containsSuggestionValue(flagSuggestions, forbidden) {
			t.Fatalf("did not expect %q flag suggestion for bar tui, got %v", forbidden, flagValues)
		}
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
	skipPersonaValue := skipValue("persona")
	skipPersona, ok := findSuggestion(suggestions, skipPersonaValue)
	if !ok {
		t.Fatalf("expected persona skip suggestion %q, got %v", skipPersonaValue, suggestions)
	}
	if !strings.HasPrefix(skipPersona.Category, "Skip") {
		t.Fatalf("expected skip category for persona, got %q", skipPersona.Category)
	}
	if trimmed := strings.TrimSpace(skipPersona.Value); trimmed != skipPersonaValue {
		t.Fatalf("expected persona skip suggestion value %q, got %q", skipPersonaValue, trimmed)
	}

	skipStaticValue := skipValue("static")
	skipStatic, ok := findSuggestion(suggestions, skipStaticValue)
	if !ok {
		t.Fatalf("expected static skip suggestion %q, got %v", skipStaticValue, suggestions)
	}
	if !strings.HasPrefix(skipStatic.Category, "Skip") {
		t.Fatalf("expected skip category for static, got %q", skipStatic.Category)
	}
	if trimmed := strings.TrimSpace(skipStatic.Value); trimmed != skipStaticValue {
		t.Fatalf("expected static skip suggestion value %q, got %q", skipStaticValue, trimmed)
	}

	if todo.Category != "What (static prompt)" {
		t.Fatalf("expected category 'What (static prompt)' for todo, got %q", todo.Category)
	}
	if strings.HasSuffix(todo.Value, " ") {
		t.Fatalf("expected static suggestion without trailing space, got %q", todo.Value)
	}
	if strings.TrimSpace(todo.Description) == "" {
		t.Fatalf("expected todo description to be populated")
	}
}

func TestCompleteSkipsPersonaAfterSkipToken(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", skipValue("persona"), ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	personaCategories := []string{
		"Why (intent)",
		"Who (persona preset)",
		"Who (voice)",
		"Who (audience)",
		"How (tone)",
	}
	for _, category := range personaCategories {
		if containsSuggestionCategory(suggestions, category) {
			t.Fatalf("did not expect persona category %q after skip, got %v", category, suggestions)
		}
	}

	if containsSuggestionValue(suggestions, skipValue("persona")) {
		t.Fatalf("did not expect persona skip suggestion after consuming it, got %v", suggestions)
	}

	if !containsSuggestionValue(suggestions, skipValue("static")) {
		t.Fatalf("expected static skip suggestion after persona skip, got %v", suggestions)
	}

	staticSlug := grammar.slugForToken("todo")
	if staticSlug == "" {
		staticSlug = "todo"
	}
	staticIndex := indexOfSuggestion(suggestions, staticSlug)
	if staticIndex == -1 {
		t.Fatalf("expected static suggestion %q after skipping persona, got %v", staticSlug, suggestions)
	}

	firstAxisIndex := len(suggestions)
	for idx, suggestion := range suggestions {
		if strings.HasPrefix(suggestion.Category, "How ") {
			firstAxisIndex = idx
			break
		}
	}
	if firstAxisIndex <= staticIndex {
		t.Fatalf("expected What suggestions to appear before How suggestions, got indexes %d and %d", staticIndex, firstAxisIndex)
	}
}

func TestCompleteSkipsStaticAfterSkipToken(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", skipValue("persona"), skipValue("static"), ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	staticSlug := grammar.slugForToken("todo")
	if staticSlug == "" {
		staticSlug = "todo"
	}
	if containsSuggestionValue(suggestions, staticSlug) {
		t.Fatalf("did not expect static suggestion %q after skip, got %v", staticSlug, suggestions)
	}

	if containsSuggestionValue(suggestions, skipValue("static")) {
		t.Fatalf("did not expect static skip suggestion after consuming it, got %v", suggestions)
	}

	completenessSlug := grammar.slugForToken("full")
	if completenessSlug == "" {
		completenessSlug = "full"
	}
	if !containsSuggestionValue(suggestions, completenessSlug) {
		t.Fatalf("expected completeness suggestion %q after skipping static, got %v", completenessSlug, suggestions)
	}
}

func TestCompleteSkipsMethodAfterSkipToken(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "full", skipValue("method"), ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	stepsSlug := grammar.slugForToken("steps")
	if stepsSlug == "" {
		stepsSlug = "steps"
	}
	if containsSuggestionValue(suggestions, stepsSlug) {
		t.Fatalf("did not expect method suggestion %q after skip, got %v", stepsSlug, suggestions)
	}

	analysisSlug := grammar.slugForToken("analysis")
	if analysisSlug == "" {
		analysisSlug = "analysis"
	}
	if containsSuggestionValue(suggestions, analysisSlug) {
		t.Fatalf("did not expect method suggestion %q after skip, got %v", analysisSlug, suggestions)
	}

	if containsSuggestionValue(suggestions, skipValue("method")) {
		t.Fatalf("did not expect method skip suggestion after consuming it, got %v", suggestions)
	}

	scopeSlug := grammar.slugForToken("focus")
	if scopeSlug == "" {
		scopeSlug = "focus"
	}
	if !containsSuggestionValue(suggestions, scopeSlug) {
		t.Fatalf("expected scope suggestion %q after skipping method, got %v", scopeSlug, suggestions)
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
	if full.Category != "How (completeness axis)" {
		t.Fatalf("expected category 'How (completeness axis)' for full, got %q", full.Category)
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
	if scopeSuggestion.Category != "How (scope axis)" {
		t.Fatalf("expected scope category 'How (scope axis)' for focus, got %q", scopeSuggestion.Category)
	}
	if strings.HasSuffix(scopeSuggestion.Value, " ") {
		t.Fatalf("expected scope suggestion without trailing space, got %q", scopeSuggestion.Value)
	}
	if containsSuggestionValue(suggestions, "scope-focus") {
		t.Fatalf("expected scope override slug to be absent from shorthand suggestions, got %v", suggestions)
	}
	if containsSuggestionValue(suggestions, "todo") {
		t.Fatalf("expected static tokens to be absent after axis selection, got %v", suggestions)
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
	if methodSuggestion.Category != "How (method axis)" {
		t.Fatalf("expected method category 'How (method axis)' for steps, got %q", methodSuggestion.Category)
	}
	if strings.HasSuffix(methodSuggestion.Value, " ") {
		t.Fatalf("expected method suggestion without trailing space, got %q", methodSuggestion.Value)
	}
}

func TestCompleteStopsSuggestingScopeAfterCap(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "full", "focus", "relations", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if containsSuggestionValue(suggestions, "focus") {
		t.Fatalf("expected scope tokens to be exhausted after reaching cap, got %v", suggestions)
	}
	if containsSuggestionValue(suggestions, "relations") {
		t.Fatalf("expected existing scope tokens to be filtered from suggestions, got %v", suggestions)
	}
	if containsSuggestionValue(suggestions, "todo") {
		t.Fatalf("expected static tokens to remain hidden after axis progression, got %v", suggestions)
	}
}

func TestCompleteSkipsEarlierAxesAfterAdvancing(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "todo", "full", "analysis", "checklist", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if containsSuggestionValue(suggestions, "focus") {
		t.Fatalf("expected scope tokens to be hidden after selecting later axis, got %v", suggestions)
	}
	if containsSuggestionValue(suggestions, "analysis") {
		t.Fatalf("expected method tokens to be hidden after advancing past method axis, got %v", suggestions)
	}
	if !containsSuggestionValue(suggestions, "slack") {
		t.Fatalf("expected channel suggestions to remain available, got %v", suggestions)
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
	if preset.Category != "Who (persona preset)" {
		t.Fatalf("expected persona preset category 'Who (persona preset)', got %q", preset.Category)
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
	if voice.Category != "Who (voice)" {
		t.Fatalf("expected persona voice category 'Who (voice)', got %q", voice.Category)
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

func TestPersonaPresetSkipsPersonaDetailSuggestions(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	words := []string{"bar", "build", "persona=coach_junior", ""}
	suggestions, err := Complete(grammar, "bash", words, len(words)-1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if containsSuggestionCategory(suggestions, "Who (voice)") {
		t.Fatalf("did not expect persona voice suggestions after preset, got %v", suggestions)
	}
	if containsSuggestionCategory(suggestions, "Who (audience)") {
		t.Fatalf("did not expect persona audience suggestions after preset, got %v", suggestions)
	}
	if containsSuggestionCategory(suggestions, "How (tone)") {
		t.Fatalf("did not expect persona tone suggestions after preset, got %v", suggestions)
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

	if len(catalog.personaIntent) > 0 || len(catalog.personaPreset) > 0 {
		if !containsSuggestionValue(suggestions, skipValue("persona")) {
			t.Fatalf("expected skip token for persona stage, got %v", suggestions)
		}
	}
	if len(catalog.static) > 0 {
		if !containsSuggestionValue(suggestions, skipValue("static")) {
			t.Fatalf("expected skip token for static stage, got %v", suggestions)
		}
	}

	skipAxes := map[string][]string{
		"completeness": catalog.completeness,
		"scope":        catalog.scope,
		"method":       catalog.method,
		"form":         catalog.form,
		"channel":      catalog.channel,
		"directional":  catalog.directional,
	}
	for axis, tokens := range skipAxes {
		if len(tokens) == 0 {
			continue
		}
		if !containsSuggestionValue(suggestions, skipValue(axis)) {
			t.Fatalf("expected skip token for axis %q, got %v", axis, suggestions)
		}
	}

	todoIdx := indexOfSuggestion(suggestions, "todo")
	if todoIdx == -1 {
		t.Fatalf("expected static suggestion 'todo', got %v", suggestions)
	}

	for _, value := range expected {
		suggestion, ok := findSuggestion(suggestions, value)
		if !ok {
			t.Fatalf("expected suggestion %q", value)
		}
		idx := indexOfSuggestion(suggestions, value)
		if idx == -1 {
			t.Fatalf("expected suggestion %q to have index", value)
		}
		category := suggestion.Category
		if category == "Why (intent)" || strings.HasPrefix(category, "Who ") || category == "How (tone)" {
			if idx > todoIdx {
				t.Fatalf("expected persona suggestion %q (%s) to appear before static 'todo'", value, category)
			}
			continue
		}
		if idx < todoIdx {
			t.Fatalf("expected %q (%s) to appear after static suggestion 'todo'", value, category)
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

	axisOrder := make([]string, 0)
	personaOrder := make([]string, 0)
	addAxisToken := func(token string) {
		if token == "" {
			return
		}
		slug := grammar.slugForToken(token)
		if slug != "" {
			axisOrder = append(axisOrder, slug)
			return
		}
		axisOrder = append(axisOrder, token)
	}
	addPersonaToken := func(token string) {
		if token == "" {
			return
		}
		slug := grammar.slugForToken(token)
		if slug != "" {
			personaOrder = append(personaOrder, slug)
			return
		}
		personaOrder = append(personaOrder, token)
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
		addAxisToken(tokens[0])
	}

	if len(catalog.personaPreset) > 0 {
		addPersonaToken(catalog.personaPreset[0])
	}
	if len(catalog.personaVoice) > 0 {
		addPersonaToken(catalog.personaVoice[0])
	}
	if len(catalog.personaAudience) > 0 {
		addPersonaToken(catalog.personaAudience[0])
	}
	if len(catalog.personaTone) > 0 {
		addPersonaToken(catalog.personaTone[0])
	}
	if len(catalog.personaIntent) > 0 {
		addPersonaToken(catalog.personaIntent[0])
	}

	minAxisIdx := len(suggestions)
	for _, value := range axisOrder {
		idx := indexOfSuggestion(suggestions, value)
		if idx == -1 {
			t.Fatalf("expected axis suggestion %q", value)
		}
		if idx < minAxisIdx {
			minAxisIdx = idx
		}
	}
	for _, value := range personaOrder {
		if !containsSuggestionValue(suggestions, value) {
			t.Fatalf("expected persona suggestion %q, got %v", value, suggestions)
		}
	}

	if len(axisOrder) > 0 {
		for _, value := range personaOrder {
			idx := indexOfSuggestion(suggestions, value)
			if idx == -1 {
				t.Fatalf("expected persona suggestion %q", value)
			}
			if idx > minAxisIdx {
				t.Fatalf("expected persona suggestion %q to appear before axis suggestions", value)
			}
		}
	}

	for i := 0; i < len(axisOrder)-1; i++ {
		first := indexOfSuggestion(suggestions, axisOrder[i])
		second := indexOfSuggestion(suggestions, axisOrder[i+1])
		if first == -1 || second == -1 {
			t.Fatalf("expected indexes for %q and %q", axisOrder[i], axisOrder[i+1])
		}
		if first > second {
			t.Fatalf("expected %q to appear before %q", axisOrder[i], axisOrder[i+1])
		}
	}
}
