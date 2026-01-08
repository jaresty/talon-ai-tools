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
	renderTokensHelp(&buf, grammar, nil)
	output := buf.String()

	presetSlug := grammar.slugForToken("persona=coach_junior")
	if presetSlug == "" {
		presetSlug = "persona=coach_junior"
	}
	expectedPreset := fmt.Sprintf("%s (preset: coach_junior", presetSlug)
	if !strings.Contains(output, expectedPreset) {
		t.Fatalf("expected persona preset slug with spoken alias in help output, got:\n%s", output)
	}

	staticVerified := false
	for name := range grammar.Static.Profiles {
		slug := grammar.slugForToken(name)
		if slug == "" || slug == name {
			continue
		}
		expected := fmt.Sprintf("- %s (canonical: %s):", slug, name)
		if !strings.Contains(output, expected) {
			t.Fatalf("expected static prompt slug hint %q in help output, got:\n%s", expected, output)
		}
		staticVerified = true
		break
	}
	if !staticVerified {
		t.Skip("no static prompts require slug hints in test grammar")
	}

	expectedAxis := "• fly-rog (canonical: fly rog)"
	if !strings.Contains(output, expectedAxis) {
		t.Fatalf("expected contract axis slug hint %q in help output, got:\n%s", expectedAxis, output)
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

func TestRenderTokensHelpFiltersStaticSection(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	filters := map[string]bool{"static": true}
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar, filters)

	output := buf.String()
	if !strings.Contains(output, "STATIC PROMPTS") {
		t.Fatalf("expected static prompts heading in filtered output, got:\n%s", output)
	}
	forbidden := []string{"CONTRACT AXES", "PERSONA PRESETS", "PERSONA AXES", "PERSONA INTENTS"}
	for _, heading := range forbidden {
		if strings.Contains(output, heading) {
			t.Fatalf("expected filtered output to exclude %q, got:\n%s", heading, output)
		}
	}
}

func TestRenderTokensHelpPersonaFilterIncludesPresetsAndAxes(t *testing.T) {
	filters, err := parseTokenHelpFilters([]string{"persona"})
	if err != nil {
		t.Fatalf("unexpected error parsing persona filter: %v", err)
	}
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar, filters)

	output := buf.String()
	if !strings.Contains(output, "PERSONA PRESETS") {
		t.Fatalf("expected persona presets heading in persona filter output, got:\n%s", output)
	}
	if !strings.Contains(output, "PERSONA AXES") {
		t.Fatalf("expected persona axes heading in persona filter output, got:\n%s", output)
	}
	if strings.Contains(output, "CONTRACT AXES") {
		t.Fatalf("expected persona filter to skip contract axes, got:\n%s", output)
	}
}

func TestRunHelpTokensFiltersSections(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exitCode := Run([]string{"help", "tokens", "static"}, strings.NewReader(""), stdout, stderr)
	if exitCode != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", exitCode, stderr.String())
	}

	output := stdout.String()
	if !strings.Contains(output, "STATIC PROMPTS") {
		t.Fatalf("expected static prompts heading in CLI output, got:\n%s", output)
	}
	if strings.Contains(output, "CONTRACT AXES") {
		t.Fatalf("expected CLI filtered output to skip contract axes, got:\n%s", output)
	}
}

func TestRunHelpTokensUnknownSection(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exitCode := Run([]string{"help", "tokens", "static", "bogus"}, strings.NewReader(""), stdout, stderr)
	if exitCode == 0 {
		t.Fatalf("expected non-zero exit when unknown section provided")
	}

	errOutput := stderr.String()
	if !strings.Contains(errOutput, "unknown tokens help section \"bogus\"") {
		t.Fatalf("expected unknown section error, got: %s", errOutput)
	}
	if stdout.Len() == 0 {
		t.Fatalf("expected general help text to be printed for unknown section")
	}
}
