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
	renderTokensHelp(&buf, grammar, nil, false)
	output := buf.String()

	presetSlug := grammar.slugForToken("persona=teach_junior_dev")
	if presetSlug == "" {
		presetSlug = "persona=teach_junior_dev"
	}
	expectedPreset := fmt.Sprintf("persona teach_junior_dev | slug: %s", presetSlug)
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
			t.Fatalf("expected task slug hint %q in help output, got:\n%s", expected, output)
		}
		staticVerified = true
		break
	}
	if !staticVerified {
		t.Skip("no tasks require slug hints in test grammar")
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

func TestRenderTokensHelpPlainIncludesTaskHeuristics(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	filters := map[string]bool{"task": true}
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar, filters, true)

	output := buf.String()
	// probe has heuristics in testdata: analyze, debug, troubleshoot, ...
	if !strings.Contains(output, "task:probe\t") {
		t.Fatalf("expected task:probe in plain output, got:\n%s", output)
	}
	// Must have a third tab-separated field with comma-joined heuristics
	for _, line := range strings.Split(output, "\n") {
		if strings.HasPrefix(line, "task:probe\t") {
			fields := strings.Split(line, "\t")
			if len(fields) < 3 {
				t.Fatalf("expected 3 tab-separated fields for task:probe, got %d: %q", len(fields), line)
			}
			if fields[2] == "" {
				t.Fatalf("expected non-empty heuristics field for task:probe, got empty third field in: %q", line)
			}
			// heuristics are comma-joined
			if !strings.Contains(fields[2], ",") {
				t.Fatalf("expected comma-separated heuristics for task:probe, got: %q", fields[2])
			}
			return
		}
	}
	t.Fatalf("task:probe line not found in output:\n%s", output)
}

func TestRenderTokensHelpPlainIncludesAxisHeuristics(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	filters := map[string]bool{"axis:method": true}
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar, filters, true)

	output := buf.String()
	// method:abduce has heuristics in testdata
	if !strings.Contains(output, "method:abduce\t") {
		t.Fatalf("expected method:abduce in plain output, got:\n%s", output)
	}
	for _, line := range strings.Split(output, "\n") {
		if strings.HasPrefix(line, "method:abduce\t") {
			fields := strings.Split(line, "\t")
			if len(fields) < 3 {
				t.Fatalf("expected 3 tab-separated fields for method:abduce, got %d: %q", len(fields), line)
			}
			if fields[2] == "" {
				t.Fatalf("expected non-empty heuristics field for method:abduce, got empty third field in: %q", line)
			}
			return
		}
	}
	t.Fatalf("method:abduce line not found in output:\n%s", output)
}

func TestRenderTokensHelpPlainOmitsHeuristicsWhenEmpty(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	// Find an axis token with no heuristics (directional:jog has none in testdata)
	filters := map[string]bool{"axis:directional": true}
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar, filters, true)

	output := buf.String()
	for _, line := range strings.Split(output, "\n") {
		if line == "" {
			continue
		}
		fields := strings.Split(line, "\t")
		// Tokens without heuristics must have exactly 1 or 2 fields, never a spurious empty third
		for _, f := range fields[2:] {
			if f == "" {
				t.Fatalf("got spurious empty third field in plain line: %q", line)
			}
		}
	}
}

func TestRenderTokensHelpPlainIncludesTaskDistinctions(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	filters := map[string]bool{"task": true}
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar, filters, true)

	output := buf.String()
	// probe has distinctions in testdata: [pull]
	for _, line := range strings.Split(output, "\n") {
		if strings.HasPrefix(line, "task:probe\t") {
			fields := strings.Split(line, "\t")
			if len(fields) < 4 {
				t.Fatalf("expected 4 tab-separated fields for task:probe, got %d: %q", len(fields), line)
			}
			if fields[3] == "" {
				t.Fatalf("expected non-empty distinctions field for task:probe, got empty fourth field in: %q", line)
			}
			return
		}
	}
	t.Fatalf("task:probe line not found in output:\n%s", output)
}

func TestRenderTokensHelpPlainIncludesAxisDistinctions(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	filters := map[string]bool{"axis:method": true}
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar, filters, true)

	output := buf.String()
	// method:abduce has distinctions in testdata: [diagnose, induce]
	for _, line := range strings.Split(output, "\n") {
		if strings.HasPrefix(line, "method:abduce\t") {
			fields := strings.Split(line, "\t")
			if len(fields) < 4 {
				t.Fatalf("expected 4 tab-separated fields for method:abduce, got %d: %q", len(fields), line)
			}
			if fields[3] == "" {
				t.Fatalf("expected non-empty distinctions field for method:abduce, got empty fourth field in: %q", line)
			}
			return
		}
	}
	t.Fatalf("method:abduce line not found in output:\n%s", output)
}

func TestRenderTokensHelpFiltersStaticSection(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	filters := map[string]bool{"task": true}
	var buf bytes.Buffer
	renderTokensHelp(&buf, grammar, filters, false)

	output := buf.String()
	if !strings.Contains(output, "TASKS") {
		t.Fatalf("expected tasks heading in filtered output, got:\n%s", output)
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
	renderTokensHelp(&buf, grammar, filters, false)

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
	exitCode := Run([]string{"help", "tokens", "task"}, strings.NewReader(""), stdout, stderr)
	if exitCode != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", exitCode, stderr.String())
	}

	output := stdout.String()
	if !strings.Contains(output, "TASKS") {
		t.Fatalf("expected tasks heading in CLI output, got:\n%s", output)
	}
	if strings.Contains(output, "CONTRACT AXES") {
		t.Fatalf("expected CLI filtered output to skip contract axes, got:\n%s", output)
	}
}

func TestRunHelpTokensUnknownSection(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exitCode := Run([]string{"help", "tokens", "task", "bogus"}, strings.NewReader(""), stdout, stderr)
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

func TestGeneralHelpUsesSubjectAndAddendumFlags(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exitCode := Run([]string{"help"}, strings.NewReader(""), stdout, stderr)
	if exitCode != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", exitCode, stderr.String())
	}
	output := stdout.String()
	if strings.Contains(output, "--prompt") {
		t.Fatalf("expected help text not to mention removed --prompt flag, got:\n%s", output)
	}
	if !strings.Contains(output, "--subject") {
		t.Fatalf("expected help text to mention --subject flag, got:\n%s", output)
	}
	if !strings.Contains(output, "--addendum") {
		t.Fatalf("expected help text to mention --addendum flag, got:\n%s", output)
	}
}

func TestRunPresetUseBuildsRecipe(t *testing.T) {
	configDir := t.TempDir()
	t.Setenv(configDirEnv, configDir)

	if exit := Run([]string{"build", "make", "struct", "--subject", "Initial subject"}, strings.NewReader(""), &bytes.Buffer{}, &bytes.Buffer{}); exit != 0 {
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
	if exit := Run([]string{"preset", "use", "daily-plan", "--subject", "Fresh subject"}, strings.NewReader(""), useStdout, useStderr); exit != 0 {
		t.Fatalf("expected preset use exit 0, got %d with stderr: %s", exit, useStderr.String())
	}

	output := useStdout.String()
	if !strings.Contains(output, "Fresh subject") {
		t.Fatalf("expected preset use output to include new subject, got:\n%s", output)
	}
	if !strings.Contains(output, "=== TASK 任務 (DO THIS) ===") {
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

	if exit := Run([]string{"build", "make", "struct"}, strings.NewReader("Initial subject"), &bytes.Buffer{}, &bytes.Buffer{}); exit != 0 {
		t.Fatalf("expected build exit 0")
	}
	if exit := Run([]string{"preset", "save", "daily-plan"}, strings.NewReader(""), &bytes.Buffer{}, &bytes.Buffer{}); exit != 0 {
		t.Fatalf("expected preset save exit 0")
	}

	jsonStdout := &bytes.Buffer{}
	jsonStderr := &bytes.Buffer{}
	args := []string{"preset", "use", "daily-plan", "--json", "--subject", "JSON subject"}
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
