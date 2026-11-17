package barcli

import (
	"bytes"
	"strings"
	"testing"
)

// TestHelpTextStatesScopeCapAsThree: property [4] — every scope-cap statement in the
// help output names 3, and none still names the old cap of 2.
func TestHelpTextStatesScopeCapAsThree(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	var buf bytes.Buffer
	renderLLMHelpAllSections(&buf, grammar)
	help := buf.String()

	if !strings.Contains(help, "**Scope**: maximum 3 tokens") {
		t.Errorf("property [4]: help must state '**Scope**: maximum 3 tokens'")
	}
	for _, stale := range []string{
		"**Scope**: maximum 2 tokens",
		"Too many scope tokens (max 2)",
		"scope accepts maximum 2 tokens",
		"- Scope: maximum 2 tokens",
	} {
		if strings.Contains(help, stale) {
			t.Errorf("property [4]: help still contains stale scope cap text %q", stale)
		}
	}
}
