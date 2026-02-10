package barcli

import (
	"bytes"
	"io/fs"
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
