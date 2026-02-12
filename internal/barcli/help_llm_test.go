package barcli

import (
	"bytes"
	"io/fs"
	"regexp"
	"strings"
	"testing"
)

func TestLLMHelpUsesTaskTerminology(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderLLMHelp(&buf, grammar, "", false)

	output := buf.String()

	// "static prompt" should not appear anywhere in LLM help output
	if strings.Contains(strings.ToLower(output), "static prompt") {
		// Find the offending line for a helpful error message
		for i, line := range strings.Split(output, "\n") {
			if strings.Contains(strings.ToLower(line), "static prompt") {
				t.Errorf("line %d contains 'static prompt': %s", i+1, strings.TrimSpace(line))
			}
		}
	}

	// Key sections should use "task" terminology
	if !strings.Contains(output, "Tasks") {
		t.Error("expected LLM help to contain 'Tasks' heading")
	}
	if !strings.Contains(output, "task is required") {
		t.Error("expected LLM help error example to say 'task is required'")
	}
}

func TestEmbeddedSkillsUseSubjectFlag(t *testing.T) {
	promptCount := 0
	addendumMentioned := false

	err := fs.WalkDir(embeddedSkills, "skills", func(path string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() || !strings.HasSuffix(path, ".md") {
			return err
		}
		data, readErr := fs.ReadFile(embeddedSkills, path)
		if readErr != nil {
			t.Fatalf("failed to read %s: %v", path, readErr)
		}
		content := string(data)
		for i, line := range strings.Split(content, "\n") {
			// --prompt flag must not appear in skill files
			if strings.Contains(line, "--prompt") {
				t.Errorf("%s:%d uses removed --prompt flag: %s", path, i+1, strings.TrimSpace(line))
				promptCount++
			}
		}
		if strings.Contains(content, "--addendum") {
			addendumMentioned = true
		}
		return nil
	})
	if err != nil {
		t.Fatalf("failed to walk embedded skills: %v", err)
	}
	if !addendumMentioned {
		t.Error("no embedded skill file mentions --addendum; at least one skill should document addendum usage")
	}
}

// TestLLMHelpHeuristicsTokensExist verifies that every token name cited in the
// Token Selection Heuristics section of bar help llm is a recognized token in
// the current grammar. This prevents stale references (e.g. deprecated tokens
// or phantom names) from silently persisting in the heuristics.
func TestLLMHelpHeuristicsTokensExist(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	// Build a set of all known single-word tokens across all axes.
	knownTokens := make(map[string]bool)
	for _, tokenDefs := range grammar.Axes.Definitions {
		for token := range tokenDefs {
			if !strings.Contains(token, " ") {
				knownTokens[token] = true
			}
		}
	}
	for token := range grammar.Static.Descriptions {
		knownTokens[token] = true
	}

	var buf bytes.Buffer
	renderLLMHelp(&buf, grammar, "", false)
	output := buf.String()

	// Extract the heuristics section only.
	heuristicsStart := strings.Index(output, "## Token Selection Heuristics")
	heuristicsEnd := strings.Index(output, "## Advanced Features")
	if heuristicsStart == -1 || heuristicsEnd == -1 {
		t.Fatal("could not locate Token Selection Heuristics section in bar help llm output")
	}
	heuristics := output[heuristicsStart:heuristicsEnd]

	// Extract all backtick-quoted tokens. Skip CLI flags (--*), commands
	// (bar ...), and key=value overrides (*=*).
	backtickRe := regexp.MustCompile("`([^`]+)`")
	matches := backtickRe.FindAllStringSubmatch(heuristics, -1)
	for _, m := range matches {
		token := m[1]
		if strings.HasPrefix(token, "--") ||
			strings.HasPrefix(token, "bar ") ||
			strings.Contains(token, "=") ||
			strings.Contains(token, " ") {
			continue
		}
		if !knownTokens[token] {
			t.Errorf("heuristics references unknown token %q — update help_llm.go to use a current token name", token)
		}
	}
}

// TestLLMHelpIncompatibilitiesPopulated verifies that the § Incompatibilities
// section in bar help llm is not empty and contains the three documented conflict
// categories from ADR-0105: output-exclusive channel conflicts, codetour/gherkin
// task-affinity restrictions, and the make+rewrite semantic conflict.
func TestLLMHelpIncompatibilitiesPopulated(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderLLMHelp(&buf, grammar, "", false)
	output := buf.String()

	incompStart := strings.Index(output, "### Incompatibilities")
	if incompStart == -1 {
		t.Fatal("could not locate ### Incompatibilities section in bar help llm output")
	}
	// Advance past the heading to capture section body.
	sectionStart := incompStart + len("### Incompatibilities")
	// Find the next heading to bound the section.
	sectionEnd := strings.Index(output[sectionStart:], "\n##")
	var incompatibilities string
	if sectionEnd == -1 {
		incompatibilities = output[sectionStart:]
	} else {
		incompatibilities = output[sectionStart : sectionStart+sectionEnd]
	}

	checks := []struct {
		description string
		contains    string
	}{
		{"output-exclusive channel conflict rule", "output-exclusive"},
		{"codetour task-affinity restriction", "codetour"},
		{"gherkin task-affinity restriction", "gherkin"},
		{"rewrite+make semantic conflict", "rewrite"},
	}
	for _, c := range checks {
		if !strings.Contains(incompatibilities, c.contains) {
			t.Errorf("§ Incompatibilities missing %s (expected to contain %q)", c.description, c.contains)
		}
	}
}

// TestLLMHelpChannelAffinityAndTokenClarity verifies ADR-0106 decisions are
// reflected in bar help llm output:
//   D1: code/html/shellscript mention sim/probe task-affinity restriction
//   D3: § Token Catalog mentions compound directionals
//   D4: taxonomy and visual descriptions are channel-adaptive ("Adapts to the channel")
//   D5: fix task description contains disambiguation note
//   D6: order method description contains sort disambiguation note
func TestLLMHelpChannelAffinityAndTokenClarity(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderLLMHelp(&buf, grammar, "", false)
	output := buf.String()

	incompStart := strings.Index(output, "### Incompatibilities")
	if incompStart == -1 {
		t.Fatal("could not locate ### Incompatibilities section")
	}
	sectionStart := incompStart + len("### Incompatibilities")
	sectionEnd := strings.Index(output[sectionStart:], "\n##")
	var incomp string
	if sectionEnd == -1 {
		incomp = output[sectionStart:]
	} else {
		incomp = output[sectionStart : sectionStart+sectionEnd]
	}

	// D1: sim/probe task-affinity for code-output channels
	if !strings.Contains(incomp, "sim") || !strings.Contains(incomp, "prose") {
		t.Error("D1: § Incompatibilities missing sim/probe task-affinity rule for code-output channels (expected 'sim' and 'prose')")
	}

	// D3: compound directionals documented somewhere in the output
	if !strings.Contains(output, "compound") || !strings.Contains(output, "fly rog") {
		t.Error("D3: bar help llm output missing compound directional documentation (expected 'compound' and 'fly rog')")
	}

	// D4: taxonomy and visual descriptions are channel-adaptive
	catalogStart := strings.Index(output, "## Token Catalog")
	if catalogStart == -1 {
		t.Fatal("could not locate ## Token Catalog section")
	}
	catalog := output[catalogStart:]
	if !strings.Contains(catalog, "Adapts to the channel") {
		t.Error("D4: Token Catalog missing channel-adaptive description for taxonomy/visual (expected 'Adapts to the channel')")
	}

	// D5 and D6 are token description changes validated by the grammar itself;
	// the grammar load and TestLLMHelpHeuristicsTokensExist cover regressions.
	// Spot-check that fix and order descriptions contain new guidance by checking
	// the catalog section contains the key phrases.
	if !strings.Contains(catalog, "reformat") {
		t.Error("D5: Token Catalog missing 'reformat' disambiguation in fix task description")
	}
	if !strings.Contains(catalog, "sort") || !strings.Contains(strings.ToLower(catalog), "order") {
		t.Error("D6: Token Catalog missing sort/order disambiguation text")
	}
}

// TestLLMHelpADR0107TokenDescriptions verifies that ADR-0107 token description
// updates are reflected in the Token Catalog section of bar help llm output.
// Note: D1c (interactive-form constraint) is superseded by ADR-0108 which
// rewrites these forms as channel-adaptive; D2–D5 remain in force.
//
//	D2:  adr channel description notes task-affinity
//	D3:  facilitate form description notes sim+facilitate combination
//	D4:  scaffold form description notes audience guidance
//	D5:  bug form description notes context-affinity
func TestLLMHelpADR0107TokenDescriptions(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderLLMHelp(&buf, grammar, "", false)
	output := buf.String()

	catalogStart := strings.Index(output, "## Token Catalog")
	if catalogStart == -1 {
		t.Fatal("could not locate ## Token Catalog section")
	}
	catalog := output[catalogStart:]

	// D2: adr channel task-affinity in description
	if !strings.Contains(catalog, "decision-making tasks") {
		t.Error("D2: Token Catalog missing 'decision-making tasks' note in adr channel description")
	}

	// D3: sim+facilitate guidance
	if !strings.Contains(catalog, "facilitation") {
		t.Error("D3: Token Catalog missing facilitation guidance in facilitate description")
	}

	// D4: scaffold audience guidance
	if !strings.Contains(catalog, "learning-oriented") {
		t.Error("D4: Token Catalog missing 'learning-oriented' audience note in scaffold description")
	}

	// D5: bug form context-affinity
	if !strings.Contains(catalog, "diagnostic and debugging") {
		t.Error("D5: Token Catalog missing 'diagnostic and debugging' note in bug form description")
	}
}

// TestLLMHelpADR0107Decisions verifies that ADR-0107 D2 (adr channel
// task-affinity) is reflected in bar help llm § Incompatibilities.
// Note: D1 (interactive-form conflicts) is superseded by ADR-0108.
func TestLLMHelpADR0107Decisions(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderLLMHelp(&buf, grammar, "", false)
	output := buf.String()

	incompStart := strings.Index(output, "### Incompatibilities")
	if incompStart == -1 {
		t.Fatal("could not locate ### Incompatibilities section")
	}
	sectionStart := incompStart + len("### Incompatibilities")
	sectionEnd := strings.Index(output[sectionStart:], "\n##")
	var incomp string
	if sectionEnd == -1 {
		incomp = output[sectionStart:]
	} else {
		incomp = output[sectionStart : sectionStart+sectionEnd]
	}

	// D2: adr channel task-affinity restriction
	if !strings.Contains(incomp, "`adr` channel") {
		t.Error("D2: § Incompatibilities missing adr channel task-affinity restriction (expected '`adr` channel')")
	}
}

// TestLLMHelpADR0108Decisions verifies that ADR-0108 decisions are reflected:
//
//	D1: quiz/cocreate/facilitate Token Catalog entries contain channel-adaptive language
//	D2: § Incompatibilities does NOT contain an interactive-form conflict rule for these tokens
func TestLLMHelpADR0108Decisions(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderLLMHelp(&buf, grammar, "", false)
	output := buf.String()

	catalogStart := strings.Index(output, "## Token Catalog")
	if catalogStart == -1 {
		t.Fatal("could not locate ## Token Catalog section")
	}
	catalog := output[catalogStart:]

	// D1: channel-adaptive language in form descriptions
	if !strings.Contains(catalog, "output-exclusive channel") {
		t.Error("D1: Token Catalog missing channel-adaptive language (expected 'output-exclusive channel') in quiz/cocreate/facilitate")
	}

	// D2: interactive-form conflict section is gone from § Incompatibilities
	incompStart := strings.Index(output, "### Incompatibilities")
	if incompStart == -1 {
		t.Fatal("could not locate ### Incompatibilities section")
	}
	sectionStart := incompStart + len("### Incompatibilities")
	sectionEnd := strings.Index(output[sectionStart:], "\n##")
	var incomp string
	if sectionEnd == -1 {
		incomp = output[sectionStart:]
	} else {
		incomp = output[sectionStart : sectionStart+sectionEnd]
	}
	if strings.Contains(incomp, "Interactive-form conflicts") {
		t.Error("D2: § Incompatibilities still contains 'Interactive-form conflicts' section — should be removed by ADR-0108")
	}
}

func TestEmbeddedSkillsUseTaskTerminology(t *testing.T) {
	err := fs.WalkDir(embeddedSkills, "skills", func(path string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() || !strings.HasSuffix(path, ".md") {
			return err
		}
		data, readErr := fs.ReadFile(embeddedSkills, path)
		if readErr != nil {
			t.Fatalf("failed to read %s: %v", path, readErr)
		}
		content := string(data)
		for i, line := range strings.Split(content, "\n") {
			if strings.Contains(strings.ToLower(line), "static prompt") {
				t.Errorf("%s:%d contains 'static prompt': %s", path, i+1, strings.TrimSpace(line))
			}
		}
		return nil
	})
	if err != nil {
		t.Fatalf("failed to walk embedded skills: %v", err)
	}
}

// TestHelpLLMAutomationFlags verifies that bar help llm documents --no-input and
// --command so LLMs and automation scripts can discover non-interactive usage.
func TestHelpLLMAutomationFlags(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	var buf bytes.Buffer
	renderLLMHelp(&buf, grammar, "", false)
	output := buf.String()

	if !strings.Contains(output, "--no-input") {
		t.Error("bar help llm must document --no-input for automation scripts")
	}
	if !strings.Contains(output, "--command") {
		t.Error("bar help llm must document --command for bar tui2 seeding")
	}
}
