package barcli

import (
	"fmt"
	"strings"
	"testing"
)

// TestPersonaSlugNormalization specifies that Build accepts persona axis tokens
// in slug form (e.g. "to-product-manager") and normalises them to canonical
// multi-word form (e.g. "to product manager"). This is the specifying validation
// for the R-10 persona-slug fix in ADR-0113 cycle 1.
func TestPersonaSlugNormalization(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	// Verify the test grammar has the audience axis with "to product manager"
	if _, ok := grammar.personaTokens["audience"]["to product manager"]; !ok {
		t.Skip("test grammar does not have audience token 'to product manager'")
	}

	result, err := Build(grammar, []string{"show", "audience=to-product-manager"})
	if err != nil {
		t.Fatalf("expected slug-form audience token 'to-product-manager' to be accepted, got error: %v", err)
	}
	if result.Persona.Audience != "to product manager" {
		t.Fatalf("expected canonical form 'to product manager', got %q", result.Persona.Audience)
	}
}

// TestCrossTokenExistsInGrammar specifies that the 'cross' scope token exists
// in the grammar. This is the specifying validation for the R-01 catalog change
// in ADR-0113 cycle 1.
func TestCrossTokenExistsInGrammar(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	if _, ok := grammar.axisTokens["scope"]["cross"]; !ok {
		t.Fatal("expected 'cross' scope token in grammar (R-01, ADR-0113 cycle 1)")
	}
}

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

// TestBuildResultCarriesReferenceKey specifies that Build() propagates the
// grammar's ReferenceKey into the returned BuildResult (ADR-0131, Loop 3).
func TestBuildResultCarriesReferenceKey(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	if strings.TrimSpace(grammar.ReferenceKey) == "" {
		t.Skip("embedded grammar has no ReferenceKey; run python3 -m prompts.export first")
	}

	result, cliErr := Build(grammar, []string{"make"})
	if cliErr != nil {
		t.Fatalf("Build returned error: %v", cliErr)
	}
	if result.ReferenceKey != grammar.ReferenceKey {
		t.Fatalf("expected BuildResult.ReferenceKey == grammar.ReferenceKey, got %q", result.ReferenceKey)
	}
}

// TestGrammarPatternsLoaded verifies that the embedded grammar JSON includes
// the patterns list from the Python SSOT (ADR-0134 D3).
func TestGrammarPatternsLoaded(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	if len(grammar.Patterns) == 0 {
		t.Fatal("expected grammar.Patterns to be non-empty — patterns not wired from Python SSOT (ADR-0134 D3)")
	}
	if len(grammar.Patterns) < 32 {
		t.Fatalf("expected at least 32 patterns, got %d", len(grammar.Patterns))
	}
}
