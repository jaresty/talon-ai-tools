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

// TestBuildStaticCategoryPopulatesKanji specifies that buildStaticCategory includes
// kanji for task tokens (ADR-0143).
func TestBuildStaticCategoryPopulatesKanji(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	category, ok := buildStaticCategory(grammar)
	if !ok {
		t.Fatal("expected static category, got none")
	}

	// Find "make" task and verify it has kanji
	var makeOption *bartui.TokenOption
	for i := range category.Options {
		if category.Options[i].Value == "make" {
			makeOption = &category.Options[i]
			break
		}
	}

	if makeOption == nil {
		t.Fatal("expected to find 'make' task option")
	}

	if makeOption.Kanji == "" {
		t.Errorf("expected Kanji to be populated for task:make (ADR-0143), got empty string")
	}
}

// TestBuildPersonaOptionsPopulatesKanji specifies that buildPersonaOptions includes
// kanji for persona axis tokens (ADR-0143).
func TestBuildPersonaOptionsPopulatesKanji(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	// Test that voice:as designer has kanji populated
	options := buildPersonaOptions(grammar, "voice")

	// Find "as designer" token and verify it has kanji
	var designerOption *bartui.TokenOption
	for i := range options {
		if options[i].Value == "as designer" {
			designerOption = &options[i]
			break
		}
	}

	if designerOption == nil {
		t.Fatalf("expected to find 'as designer' token in voice options")
	}

	if designerOption.Kanji == "" {
		t.Errorf("expected Kanji to be populated for voice:as designer (ADR-0143), got empty string")
	}
}
