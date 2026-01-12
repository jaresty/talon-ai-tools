package barcli

import (
	"fmt"
	"testing"
)

func TestApplyOverrideTokenScope(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	state := newBuildState(grammar)

	scopeTokens := make([]string, 0, len(grammar.axisTokens["scope"]))
	for token := range grammar.axisTokens["scope"] {
		scopeTokens = append(scopeTokens, token)
		if len(scopeTokens) == 2 {
			break
		}
	}
	if len(scopeTokens) < 2 {
		t.Skip("test grammar does not provide multiple scope tokens")
	}

	override := fmt.Sprintf("scope=%s,%s", scopeTokens[0], scopeTokens[1])
	if err := state.applyOverrideToken(override); err != nil {
		t.Fatalf("applyOverrideToken returned error: %v", err)
	}

	if len(state.scope) != 2 || !contains(state.scope, scopeTokens[0]) || !contains(state.scope, scopeTokens[1]) {
		t.Fatalf("expected scope override to include %v, got %v", scopeTokens[:2], state.scope)
	}

	recognized := state.recognized["scope"]
	if len(recognized) != 2 || !contains(recognized, scopeTokens[0]) || !contains(recognized, scopeTokens[1]) {
		t.Fatalf("expected recognized scope entries for %v, got %v", scopeTokens[:2], recognized)
	}
}

func TestApplyOverrideTokenUnknown(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	state := newBuildState(grammar)

	if err := state.applyOverrideToken("unknown=value"); err == nil {
		t.Fatalf("expected error for unknown override key")
	} else if err.Type != errorUnknownToken {
		t.Fatalf("expected unknown token error, got %s", err.Type)
	}
}

func TestApplyOverrideTokenPersonaConflict(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	state := newBuildState(grammar)

	var preset string
	for key := range grammar.Persona.Presets {
		preset = key
		break
	}
	if preset == "" {
		t.Skip("test grammar does not define persona presets")
	}

	if err := state.applyOverrideToken("persona=" + preset); err == nil {
		t.Fatalf("expected persona override conflict")
	} else if err.Type != errorPresetConflict {
		t.Fatalf("expected preset conflict error, got %s", err.Type)
	}
}
