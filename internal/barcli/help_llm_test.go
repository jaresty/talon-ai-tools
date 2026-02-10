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
