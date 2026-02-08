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

func TestLoadGrammarExplicitPathOverridesEnv(t *testing.T) {
	missing := filepath.Join(t.TempDir(), "missing.json")
	t.Setenv(envGrammarPath, missing)

	overridePath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	if _, err := LoadGrammar(overridePath); err != nil {
		t.Fatalf("expected explicit path override to succeed, got %v", err)
	}
}
