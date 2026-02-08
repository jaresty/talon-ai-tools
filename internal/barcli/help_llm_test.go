package barcli

import (
	"bytes"
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
