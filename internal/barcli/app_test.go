package barcli

import (
	"bytes"
	"fmt"
	"strings"
	"testing"
)

func TestRenderTokensHelpShowsPersonaSlugs(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar)
	output := buf.String()

	presetSlug := grammar.slugForToken("persona=coach_junior")
	if presetSlug == "" {
		presetSlug = "persona=coach_junior"
	}
	expectedPreset := fmt.Sprintf("%s (preset: coach_junior", presetSlug)
	if !strings.Contains(output, expectedPreset) {
		t.Fatalf("expected persona preset slug with spoken alias in help output, got:\n%s", output)
	}

	axisVerified := false
	for _, tokens := range grammar.Persona.Axes {
		for _, token := range tokens {
			slug := grammar.slugForToken(token)
			if slug == "" || slug == token {
				continue
			}
			expected := fmt.Sprintf("• %s (spoken: %s)", slug, token)
			if !strings.Contains(output, expected) {
				t.Fatalf("expected persona axis slug '%s' with spoken alias in help output, got:\n%s", expected, output)
			}
			axisVerified = true
			break
		}
		if axisVerified {
			break
		}
	}
	if !axisVerified {
		t.Skip("no persona axis tokens required slug transformation in test grammar")
	}

	intentVerified := false
	if intents, ok := grammar.Persona.Intent.AxisTokens["intent"]; ok {
		for _, token := range intents {
			slug := grammar.slugForToken(token)
			if slug == "" || slug == token {
				continue
			}
			expected := fmt.Sprintf("• %s (spoken: %s)", slug, token)
			if !strings.Contains(output, expected) {
				t.Fatalf("expected persona intent slug '%s' with spoken alias in help output, got:\n%s", expected, output)
			}
			intentVerified = true
			break
		}
	}
	if !intentVerified {
		t.Skip("no persona intent tokens required slug transformation in test grammar")
	}
}

func TestRenderTokensHelpShowsContractSlugHints(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar)
	output := buf.String()

	expected := "• fly-rog (canonical: fly rog)"
	if !strings.Contains(output, expected) {
		t.Fatalf("expected contract axis slug hint %q in help output, got:\n%s", expected, output)
	}
}
