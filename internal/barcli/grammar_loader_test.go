package barcli

import (
	"encoding/json"
	"path/filepath"
	"strings"
	"testing"
)

func TestLoadGrammarDefaultsToEmbedded(t *testing.T) {
	t.Setenv(envGrammarPath, "")

	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	if grammar.SchemaVersion == "" {
		t.Fatal("expected embedded grammar to provide a schema version")
	}
	if desc := strings.TrimSpace(grammar.TaskDescription("make")); desc == "" {
		t.Fatal("expected embedded grammar to include make task description")
	}
}

// TestLoadGrammarHasReferenceKey specifies that the embedded grammar provides a
// non-empty ReferenceKey field (ADR-0131). This is the specifying validation for
// Loop 2: Grammar struct must map the reference_key JSON field.
func TestLoadGrammarHasReferenceKey(t *testing.T) {
	t.Setenv(envGrammarPath, "")

	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	if strings.TrimSpace(grammar.ReferenceKey) == "" {
		t.Fatal("expected embedded grammar to provide a non-empty ReferenceKey (ADR-0131)")
	}
}

func TestEmbeddedGrammarUsesTaskKeys(t *testing.T) {
	data, err := embeddedGrammarBytes()
	if err != nil {
		t.Fatalf("read embedded grammar: %v", err)
	}
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		t.Fatalf("unmarshal grammar: %v", err)
	}
	if _, ok := raw["tasks"]; !ok {
		t.Fatal("expected top-level 'tasks' key in grammar JSON (found 'static_prompts'?)")
	}
	if _, ok := raw["static_prompts"]; ok {
		t.Fatal("grammar JSON still contains deprecated 'static_prompts' key; rename to 'tasks'")
	}

	var hierarchy struct {
		Defaults map[string]json.RawMessage `json:"defaults"`
	}
	if err := json.Unmarshal(raw["hierarchy"], &hierarchy); err != nil {
		t.Fatalf("unmarshal hierarchy: %v", err)
	}
	if _, ok := hierarchy.Defaults["task"]; !ok {
		t.Fatal("expected 'task' key in hierarchy.defaults (found 'static_prompt'?)")
	}
	if _, ok := hierarchy.Defaults["static_prompt"]; ok {
		t.Fatal("hierarchy.defaults still contains deprecated 'static_prompt' key; rename to 'task'")
	}

	var slugs struct {
		Task json.RawMessage `json:"task"`
	}
	if err := json.Unmarshal(raw["slugs"], &slugs); err != nil {
		t.Fatalf("unmarshal slugs: %v", err)
	}
	if slugs.Task == nil {
		t.Fatal("expected 'task' key in slugs section (found 'static'?)")
	}
}

func TestLoadGrammarEnvOverrideMissingFile(t *testing.T) {
	missing := filepath.Join(t.TempDir(), "missing.json")
	t.Setenv(envGrammarPath, missing)

	_, err := LoadGrammar("")
	if err == nil {
		t.Fatal("expected error when BAR_GRAMMAR_PATH points at a missing file")
	}
	if !strings.Contains(err.Error(), "open grammar") {
		t.Fatalf("expected open grammar error, got %v", err)
	}
}

// TestTaskMetadataForReturnsStructuredFields specifies that TaskMetadataFor returns
// definition, heuristics, and distinctions for task tokens from the embedded grammar
// (ADR-0154 T-5: wire Go grammar.go structs and accessor).
func TestTaskMetadataForReturnsStructuredFields(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	meta := grammar.TaskMetadataFor("probe")
	if meta == nil {
		t.Fatal("TaskMetadataFor(probe) must not return nil")
	}
	if meta.Definition == "" {
		t.Error("probe definition must not be empty")
	}
	if len(meta.Heuristics) == 0 {
		t.Error("probe heuristics must not be empty")
	}
	if len(meta.Distinctions) == 0 {
		t.Error("probe distinctions must not be empty")
	}

	// fix must have probe in its distinctions (ADR-0154 Loop 5 review gap)
	fixMeta := grammar.TaskMetadataFor("fix")
	if fixMeta == nil {
		t.Fatal("TaskMetadataFor(fix) must not return nil")
	}
	foundProbe := false
	for _, d := range fixMeta.Distinctions {
		if d.Token == "probe" {
			foundProbe = true
			break
		}
	}
	if !foundProbe {
		t.Error("fix distinctions must include probe (fix=reformat, not debug)")
	}

	// nil for unknown token
	if grammar.TaskMetadataFor("nonexistent") != nil {
		t.Error("TaskMetadataFor(nonexistent) must return nil")
	}
}

// TestAxisMetadataForReturnsNilWhenNoContent specifies T-2 pipeline wiring —
// AxisMetadataFor must exist and return nil before any axis content is added (ADR-0155 T-2).
func TestAxisMetadataForReturnsNilWhenNoContent(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// No axis metadata populated yet — accessor must return nil, not panic.
	if grammar.AxisMetadataFor("completeness", "gist") != nil {
		t.Error("AxisMetadataFor must return nil when no axis metadata is present")
	}

	// Unknown axis and token also return nil safely.
	if grammar.AxisMetadataFor("nonexistent", "nonexistent") != nil {
		t.Error("AxisMetadataFor must return nil for unknown axis/token")
	}
}

func TestLoadGrammarExplicitPathOverridesEnv(t *testing.T) {
	missing := filepath.Join(t.TempDir(), "missing.json")
	t.Setenv(envGrammarPath, missing)

	overridePath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	if _, err := LoadGrammar(overridePath); err != nil {
		t.Fatalf("expected explicit path override to succeed, got %v", err)
	}
}
