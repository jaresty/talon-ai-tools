package barcli

import (
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

// TestBuildAxisOptionsPopulatesUseWhen specifies that buildAxisOptions includes
// use_when for axis tokens from the embedded grammar (ADR-0132).
func TestBuildAxisOptionsPopulatesUseWhen(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	// Test that scope:act has use_when populated
	options := buildAxisOptions(grammar, "scope")

	if len(options) == 0 {
		t.Fatal("expected scope options, got none")
	}

	// Find act token and verify it has use_when
	var actOption *bartui.TokenOption
	for i := range options {
		if options[i].Value == "act" {
			actOption = &options[i]
			break
		}
	}

	if actOption == nil {
		t.Fatal("expected to find 'act' token in scope options")
	}

	if actOption.UseWhen == "" {
		t.Errorf("expected UseWhen to be populated for scope:act (ADR-0132), got empty string")
	}
}

// TestBuildPersonaOptionsPopulatesUseWhen specifies that buildPersonaOptions includes
// use_when for persona axis tokens from the embedded grammar (ADR-0133).
func TestBuildPersonaOptionsPopulatesUseWhen(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	// Test that voice:as designer has use_when populated
	options := buildPersonaOptions(grammar, "voice")

	if len(options) == 0 {
		t.Fatal("expected voice options, got none")
	}

	// Find "as designer" token and verify it has use_when
	var designerOption *bartui.TokenOption
	for i := range options {
		if options[i].Value == "as designer" {
			designerOption = &options[i]
			break
		}
	}

	if designerOption == nil {
		t.Fatalf("expected to find 'as designer' token in voice options, got: %v", options)
	}

	if designerOption.UseWhen == "" {
		t.Errorf("expected UseWhen to be populated for voice:as designer (ADR-0133), got empty string")
	}
}
