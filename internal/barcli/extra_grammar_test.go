package barcli

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

const extraGrammarYAML = `
method:
  zzz_test_assess:
    label: Evaluate readiness before committing
    routing_concept: Readiness evaluation pipeline
    kanji: 備
    definition: The response evaluates the subject against readiness criteria.
    heuristics:
      - are we ready
      - readiness check
      - go/no-go
    distinctions:
      - token: check
        note: check = evaluate against a condition; assess = evaluate readiness before committing
`

func writeTemp(t *testing.T, content, ext string) string {
	t.Helper()
	f, err := os.CreateTemp(t.TempDir(), "extra-grammar-*"+ext)
	if err != nil {
		t.Fatalf("create temp file: %v", err)
	}
	if _, err := f.WriteString(content); err != nil {
		t.Fatalf("write temp file: %v", err)
	}
	f.Close()
	return f.Name()
}

// TestLoadGrammarExtraGrammarYAML specifies that BAR_EXTRA_GRAMMAR pointing to a YAML
// file merges its tokens into the grammar with all fields populated.
func TestLoadGrammarExtraGrammarYAML(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	path := writeTemp(t, extraGrammarYAML, ".yaml")
	t.Setenv(envExtraGrammarPath, path)

	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}

	token := "zzz_test_assess"
	axis := "method"

	if _, ok := g.AxisTokenSet(axis)[token]; !ok {
		t.Errorf("extra token %q not found in axis %q token set", token, axis)
	}
	if got := g.Axes.Definitions[axis][token]; got == "" {
		t.Errorf("extra token %q definition not merged", token)
	}
	if got := g.Axes.Labels[axis][token]; got != "Evaluate readiness before committing" {
		t.Errorf("extra token %q label: got %q, want %q", token, got, "Evaluate readiness before committing")
	}
	if got := g.Axes.Kanji[axis][token]; got != "備" {
		t.Errorf("extra token %q kanji: got %q, want %q", token, got, "備")
	}
	if got := g.Axes.RoutingConcept[axis][token]; got != "Readiness evaluation pipeline" {
		t.Errorf("extra token %q routing_concept: got %q, want %q", token, got, "Readiness evaluation pipeline")
	}
	meta := g.Axes.Metadata[axis][token]
	if meta.Definition == "" {
		t.Errorf("extra token %q metadata.definition not merged", token)
	}
	if len(meta.Heuristics) != 3 {
		t.Errorf("extra token %q heuristics: got %d, want 3", token, len(meta.Heuristics))
	}
	if len(meta.Distinctions) != 1 {
		t.Errorf("extra token %q distinctions: got %d, want 1", token, len(meta.Distinctions))
	}
}

// TestLoadGrammarExtraGrammarJSON specifies that BAR_EXTRA_GRAMMAR pointing to a JSON
// file merges its tokens identically to the YAML path.
func TestLoadGrammarExtraGrammarJSON(t *testing.T) {
	t.Setenv(envGrammarPath, "")

	content, err := json.Marshal(map[string]interface{}{
		"method": map[string]interface{}{
			"zzz_test_json": map[string]interface{}{
				"label":           "JSON test token",
				"routing_concept": "JSON routing",
				"definition":      "A token loaded from JSON.",
				"heuristics":      []string{"json test"},
			},
		},
	})
	if err != nil {
		t.Fatalf("marshal JSON: %v", err)
	}

	path := writeTemp(t, string(content), ".json")
	t.Setenv(envExtraGrammarPath, path)

	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}

	token := "zzz_test_json"
	if _, ok := g.AxisTokenSet("method")[token]; !ok {
		t.Errorf("JSON extra token %q not found in method token set", token)
	}
	if got := g.Axes.Labels["method"][token]; got != "JSON test token" {
		t.Errorf("JSON extra token label: got %q, want %q", got, "JSON test token")
	}
}

// TestLoadGrammarExtraGrammarUserWins specifies that a user-defined token with the same
// key as a built-in token has its definition replace the built-in definition.
func TestLoadGrammarExtraGrammarUserWins(t *testing.T) {
	t.Setenv(envGrammarPath, "")

	override := "user override definition for ground"
	content := "method:\n  ground:\n    definition: " + override + "\n"
	path := writeTemp(t, content, ".yaml")
	t.Setenv(envExtraGrammarPath, path)

	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}

	if got := g.Axes.Definitions["method"]["ground"]; got != override {
		t.Errorf("user-wins: got definition %q, want %q", got, override)
	}
	if got := g.Axes.Metadata["method"]["ground"].Definition; got != override {
		t.Errorf("user-wins: metadata definition %q, want %q", got, override)
	}
}

// TestLoadGrammarExtraGrammarMissingFile specifies that BAR_EXTRA_GRAMMAR pointing to a
// nonexistent path returns an error.
func TestLoadGrammarExtraGrammarMissingFile(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	t.Setenv(envExtraGrammarPath, filepath.Join(t.TempDir(), "does-not-exist.yaml"))

	_, err := LoadGrammar("")
	if err == nil {
		t.Fatal("expected error for missing extra grammar file, got nil")
	}
}

// TestLoadGrammarExtraGrammarBadExtension specifies that an unsupported file extension
// returns an error.
func TestLoadGrammarExtraGrammarBadExtension(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	path := writeTemp(t, "method:\n  foo:\n    definition: bar\n", ".txt")
	t.Setenv(envExtraGrammarPath, path)

	_, err := LoadGrammar("")
	if err == nil {
		t.Fatal("expected error for unsupported extension, got nil")
	}
}

// TestLoadGrammarExtraGrammarNotSet specifies that when BAR_EXTRA_GRAMMAR is unset the
// grammar loads normally with no error.
func TestLoadGrammarExtraGrammarNotSet(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	t.Setenv(envExtraGrammarPath, "")

	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("expected clean load with no extra grammar, got: %v", err)
	}
	if _, ok := g.AxisTokenSet("task")["ground"]; !ok {
		t.Error("built-in task:ground missing after no-extra-grammar load")
	}
}
