package barcli

import (
	"bytes"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

// ADR-0237: Token Guidebook — Go-layer tests.

// Behavior 1: GuidesForToken returns ≥1 entry for a token that has a guide.
func TestGuidesForToken(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	entries := grammar.GuidesForToken("probe")
	if len(entries) == 0 {
		t.Errorf("GuidesForToken(probe): want ≥1 guide entry, got 0")
	}
	for _, e := range entries {
		if e.ID == "" {
			t.Errorf("guide entry has empty ID")
		}
		if e.Title == "" {
			t.Errorf("guide entry %q has empty Title", e.ID)
		}
		if e.Body == "" {
			t.Errorf("guide entry %q has empty Body", e.ID)
		}
	}
}

// Behavior 2: GuidesForToken returns non-nil empty slice for unknown token.
func TestGuidesForTokenUnknown(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	entries := grammar.GuidesForToken("__no_such_token__")
	if entries == nil {
		t.Errorf("GuidesForToken unknown: want empty slice, got nil")
	}
	if len(entries) != 0 {
		t.Errorf("GuidesForToken unknown: want 0 entries, got %d", len(entries))
	}
}

// Behavior 3: runGuide prints guide content for a known token.
func TestRunGuideOutput(t *testing.T) {
	var stdout, stderr bytes.Buffer
	opts := &cli.Config{Command: "guide", Tokens: []string{"probe"}}
	code := runGuide(opts, &stdout, &stderr)
	if code != 0 {
		t.Fatalf("runGuide(probe): exit %d stderr=%s", code, stderr.String())
	}
	out := stdout.String()
	if !strings.Contains(out, "probe") {
		t.Errorf("runGuide output missing 'probe', got: %s", out)
	}
}

// Behavior 4: runGuide exits 1 with "no guide" in stderr for unknown token.
func TestRunGuideUnknownToken(t *testing.T) {
	var stdout, stderr bytes.Buffer
	opts := &cli.Config{Command: "guide", Tokens: []string{"__no_such_token__"}}
	code := runGuide(opts, &stdout, &stderr)
	if code == 0 {
		t.Errorf("runGuide unknown token: want non-zero exit, got 0")
	}
	if !strings.Contains(stderr.String(), "no guide") {
		t.Errorf("runGuide unknown token: want 'no guide' in stderr, got: %s", stderr.String())
	}
}

// Behavior 6: bar help llm navigation output contains "bar guide <token>".
func TestHelpLLMGuideCommand(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	var buf bytes.Buffer
	renderNavigationGuide(&buf, grammar)
	out := buf.String()
	if !strings.Contains(out, "bar guide") {
		t.Errorf("bar help llm navigation: want 'bar guide' in output, got none\noutput:\n%s", out)
	}
}

// Behavior 7: bar lookup printed output includes [guide] annotation when HasGuide=true.
func TestLookupGuideAnnotation(t *testing.T) {
	var stdout, stderr bytes.Buffer
	opts := &cli.Config{Command: "lookup", Tokens: []string{"probe"}}
	code := runLookup(opts, &stdout, &stderr)
	if code != 0 {
		t.Fatalf("runLookup probe: exit %d stderr=%s", code, stderr.String())
	}
	out := stdout.String()
	if !strings.Contains(out, "[guide]") {
		t.Errorf("bar lookup 'probe': want '[guide]' annotation in output for token with guide entry, got none\noutput:\n%s", out)
	}
}

// Behavior 5: LookupResult.HasGuide is true for probe, which has a guide entry.
func TestLookupResultHasGuide(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	results := LookupTokens("probe", grammar, "")
	var found bool
	for _, r := range results {
		if r.Token == "probe" && r.HasGuide {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("LookupTokens('probe'): want probe result with HasGuide=true, not found")
	}
}
