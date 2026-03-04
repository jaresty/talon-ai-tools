// Specifying validation for ADR-0153: Composition Conflict Resolution.
//
// T-1: form tokens with a declared default_completeness override the global
// "full" default when the user has not specified completeness explicitly.
//
// T-2: cautionary pairs with a cautionary_note render an indented ↳ conflict
// line beneath the conflicting constraint bullet.
package barcli

import (
	"strings"
	"testing"
)

// TestCommitFormDefaultsToGist specifies ADR-0153 T-1: bar build make commit
// must render gist completeness (not full) when no completeness token is given.
func TestCommitFormDefaultsToGist(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "commit", "--subject", "x"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "Completeness (gist") {
		t.Errorf("ADR-0153 T-1: expected commit to default to gist completeness, got:\n%s", result.Stdout)
	}
	if strings.Contains(result.Stdout, "Completeness (full") {
		t.Errorf("ADR-0153 T-1: commit must not use full completeness as default, got:\n%s", result.Stdout)
	}
}

// TestCommitFormExplicitCompletenessNotOverridden specifies that an explicit
// completeness token is not overridden by the form's default.
func TestCommitFormExplicitCompletenessNotOverridden(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "full", "commit", "--subject", "x"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "Completeness (full") {
		t.Errorf("ADR-0153 T-1: explicit full completeness must not be overridden by form default, got:\n%s", result.Stdout)
	}
}

// TestGistFigRendersConflictNote specifies ADR-0153 T-2: bar build make gist fig
// must render a ↳ conflict note beneath the completeness bullet.
func TestGistFigRendersConflictNote(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "gist", "fig", "--subject", "x"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "↳") {
		t.Errorf("ADR-0153 T-2: expected conflict note (↳) in gist+fig prompt, got:\n%s", result.Stdout)
	}
	if !strings.Contains(result.Stdout, "completeness governs") {
		t.Errorf("ADR-0153 T-2: conflict note must declare which constraint governs, got:\n%s", result.Stdout)
	}
}

// TestSkimFogRendersConflictNote specifies that skim+fog also renders a conflict note.
func TestSkimFogRendersConflictNote(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "skim", "fog", "--subject", "x"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "↳") {
		t.Errorf("ADR-0153 T-2: expected conflict note (↳) in skim+fog prompt, got:\n%s", result.Stdout)
	}
}

// TestNonConflictingPairsHaveNoNote specifies that non-cautionary combinations
// do not render any conflict note.
func TestNonConflictingPairsHaveNoNote(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	cases := [][]string{
		{"build", "make", "gist", "rog", "--subject", "x"},
		{"build", "make", "full", "fig", "--subject", "x"},
		{"build", "make", "deep", "bog", "--subject", "x"},
	}
	for _, args := range cases {
		result := runBuildCLI(t, args, nil)
		if result.Exit != 0 {
			t.Fatalf("expected exit 0 for %v, got %d; stderr: %s", args, result.Exit, result.Stderr)
		}
		if strings.Contains(result.Stdout, "↳") {
			t.Errorf("ADR-0153 T-2: non-conflicting pair %v must not render a conflict note, got:\n%s", args, result.Stdout)
		}
	}
}

// TestFormDefaultCompletenessGrammarField specifies that the grammar JSON
// contains the form_default_completeness field with commit→gist (ADR-0153 T-1).
func TestFormDefaultCompletenessGrammarField(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	if grammar.Axes.FormDefaultCompleteness == nil {
		t.Fatal("ADR-0153 T-1: grammar must have form_default_completeness field")
	}
	if got := grammar.FormDefaultCompletenessFor("commit"); got != "gist" {
		t.Errorf("ADR-0153 T-1: commit form default completeness must be 'gist', got %q", got)
	}
}

// TestCautionaryNotesGrammarField specifies that the grammar JSON contains
// cautionary_notes for completeness.gist × directional.fig (ADR-0153 T-2).
func TestCautionaryNotesGrammarField(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	cac := grammar.CrossAxisCompositionFor("completeness", "gist")
	if cac == nil {
		t.Fatal("ADR-0153 T-2: completeness.gist must have cross_axis_composition entry")
	}
	pair, ok := cac["directional"]
	if !ok {
		t.Fatal("ADR-0153 T-2: completeness.gist must have directional composition entry")
	}
	if len(pair.CautionaryNotes) == 0 {
		t.Fatal("ADR-0153 T-2: completeness.gist directional entry must have cautionary_notes")
	}
	if pair.CautionaryNotes["fig"] == "" {
		t.Error("ADR-0153 T-2: completeness.gist must have cautionary_notes for fig")
	}
}
