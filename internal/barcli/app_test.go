package barcli

import (
	"bytes"
	"encoding/json"
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
	expectedPreset := fmt.Sprintf("persona coach_junior | slug: %s", presetSlug)
	if !strings.Contains(output, expectedPreset) {
		t.Fatalf("expected persona preset slug with command hint in help output, got:\n%s", output)
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
			expected := fmt.Sprintf("• %s | slug: %s", token, slug)
			if !strings.Contains(output, expected) {
				t.Fatalf("expected persona axis slug hint %q in help output, got:\n%s", expected, output)
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
			expected := fmt.Sprintf("• %s | slug: %s", token, slug)
			if !strings.Contains(output, expected) {
				t.Fatalf("expected persona intent slug hint %q in help output, got:\n%s", expected, output)
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

func TestParseTokenHelpFiltersDirectPersonaSections(t *testing.T) {
	filters, err := parseTokenHelpFilters([]string{"persona-presets", "persona-axes"})
	if err != nil {
		t.Fatalf("unexpected error parsing direct persona sections: %v", err)
	}

	if !filters["persona-presets"] {
		t.Fatalf("expected persona-presets to be enabled, got %#v", filters)
	}
	if !filters["persona-axes"] {
		t.Fatalf("expected persona-axes to be enabled, got %#v", filters)
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

func TestRunHelpTokensPersonaPresetsFilter(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exitCode := Run([]string{"help", "tokens", "persona-presets"}, strings.NewReader(""), stdout, stderr)
	if exitCode != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", exitCode, stderr.String())
	}

	output := stdout.String()
	if !strings.Contains(output, "PERSONA PRESETS") {
		t.Fatalf("expected persona presets heading in filtered output, got:\n%s", output)
	}
	if strings.Contains(output, "PERSONA AXES") {
		t.Fatalf("expected persona presets filter to omit persona axes, got:\n%s", output)
	}
}

func TestGeneralHelpMentionsSkipSentinel(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exitCode := Run([]string{"help"}, strings.NewReader(""), stdout, stderr)
	if exitCode != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", exitCode, stderr.String())
	}

	output := stdout.String()
	if !strings.Contains(output, "Skip remaining persona hints") {
		t.Fatalf("expected general help to describe //next persona skip, got:\n%s", output)
	}
	if !strings.Contains(output, "//next:<stage>") {
		t.Fatalf("expected general help to describe //next:<stage> syntax, got:\n%s", output)
	}
	if !strings.Contains(output, "Skip tokens do not appear") {
		t.Fatalf("expected general help to note skip tokens are ignored during build, got:\n%s", output)
	}
	if !strings.Contains(output, "bar build //next") {
		t.Fatalf("expected general help to include skip sentinel example, got:\n%s", output)
	}
}

func TestRunPresetUseBuildsRecipe(t *testing.T) {
	configDir := t.TempDir()
	t.Setenv(configDirEnv, configDir)

	if exit := Run([]string{"build", "todo", "focus", "--prompt", "Initial subject"}, strings.NewReader(""), &bytes.Buffer{}, &bytes.Buffer{}); exit != 0 {
		t.Fatalf("expected build exit 0, got %d", exit)
	}

	saveStdout := &bytes.Buffer{}
	saveStderr := &bytes.Buffer{}
	if exit := Run([]string{"preset", "save", "daily-plan"}, strings.NewReader(""), saveStdout, saveStderr); exit != 0 {
		t.Fatalf("expected preset save exit 0, got %d with stderr: %s", exit, saveStderr.String())
	}
	if !strings.Contains(saveStdout.String(), "Saved preset") {
		t.Fatalf("expected save output to confirm preset creation, got:\n%s", saveStdout.String())
	}

	useStdout := &bytes.Buffer{}
	useStderr := &bytes.Buffer{}
	if exit := Run([]string{"preset", "use", "daily-plan", "--prompt", "Fresh subject"}, strings.NewReader(""), useStdout, useStderr); exit != 0 {
		t.Fatalf("expected preset use exit 0, got %d with stderr: %s", exit, useStderr.String())
	}

	output := useStdout.String()
	if !strings.Contains(output, "Fresh subject") {
		t.Fatalf("expected preset use output to include new subject, got:\n%s", output)
	}
	if !strings.Contains(output, "=== TASK (DO THIS) ===") {
		t.Fatalf("expected preset use output to include task section, got:\n%s", output)
	}

	stored, err := loadLastBuild()
	if err != nil {
		t.Fatalf("loadLastBuild returned error: %v", err)
	}
	if stored.Result.Subject != "" {
		t.Fatalf("expected cached subject to remain empty, got %q", stored.Result.Subject)
	}
	if len(stored.Tokens) == 0 {
		t.Fatalf("expected cached tokens to persist, got %#v", stored.Tokens)
	}
}

func TestRunPresetUseJSON(t *testing.T) {
	configDir := t.TempDir()
	t.Setenv(configDirEnv, configDir)

	if exit := Run([]string{"build", "todo", "focus"}, strings.NewReader("Initial subject"), &bytes.Buffer{}, &bytes.Buffer{}); exit != 0 {
		t.Fatalf("expected build exit 0")
	}
	if exit := Run([]string{"preset", "save", "daily-plan"}, strings.NewReader(""), &bytes.Buffer{}, &bytes.Buffer{}); exit != 0 {
		t.Fatalf("expected preset save exit 0")
	}

	jsonStdout := &bytes.Buffer{}
	jsonStderr := &bytes.Buffer{}
	args := []string{"preset", "use", "daily-plan", "--json", "--prompt", "JSON subject"}
	if exit := Run(args, strings.NewReader(""), jsonStdout, jsonStderr); exit != 0 {
		t.Fatalf("expected preset use --json exit 0, got %d with stderr: %s", exit, jsonStderr.String())
	}

	var payload struct {
		Name    string   `json:"name"`
		Tokens  []string `json:"tokens"`
		Subject string   `json:"subject"`
	}
	if err := json.Unmarshal(jsonStdout.Bytes(), &payload); err != nil {
		t.Fatalf("failed to parse JSON output: %v\n%s", err, jsonStdout.String())
	}
	if payload.Subject != "JSON subject" {
		t.Fatalf("expected subject to match prompt, got %q", payload.Subject)
	}
	if len(payload.Tokens) == 0 {
		t.Fatalf("expected tokens in JSON output, got %#v", payload.Tokens)
	}
}
