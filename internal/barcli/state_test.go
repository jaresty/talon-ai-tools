package barcli

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestSaveLastBuildStripsSubject(t *testing.T) {
	configDir := t.TempDir()
	t.Setenv(configDirEnv, configDir)
	t.Setenv(disableStateEnv, "")

	originalResult := &BuildResult{
		SchemaVersion: "v1",
		Subject:       "Original subject",
		PlainText:     "Rendered prompt body\nWith multiple lines",
		Axes:          AxesResult{Static: "make"},
		Persona: PersonaResult{
			Voice:    "coach",
			Audience: "novice",
			Tone:     "friendly",
		},
		Tokens: []string{"make", "struct"},
	}
	tokens := []string{"make", "struct"}

	if err := saveLastBuild(originalResult, tokens); err != nil {
		t.Fatalf("saveLastBuild returned error: %v", err)
	}

	statePath := filepath.Join(configDir, stateDirName, lastBuildFile)
	data, err := os.ReadFile(statePath)
	if err != nil {
		t.Fatalf("reading cached build: %v", err)
	}

	var payload map[string]any
	if err := json.Unmarshal(data, &payload); err != nil {
		t.Fatalf("parsing cached build JSON: %v", err)
	}

	if _, exists := payload["plain_text"]; exists {
		t.Fatalf("unexpected plain_text field in cached build JSON: %v", payload["plain_text"])
	}

	resultPayload, ok := payload["result"].(map[string]any)
	if !ok {
		t.Fatalf("expected result object in cached build JSON, got %T", payload["result"])
	}

	if subject, ok := resultPayload["subject"].(string); !ok || subject != "" {
		t.Fatalf("expected result.subject to be empty string, got %#v", resultPayload["subject"])
	}

	tokensPayload, ok := resultPayload["tokens"].([]any)
	if !ok {
		t.Fatalf("expected result.tokens array, got %T", resultPayload["tokens"])
	}
	if len(tokensPayload) != len(tokens) {
		t.Fatalf("unexpected token count: got %d, want %d", len(tokensPayload), len(tokens))
	}

	stored, err := loadLastBuild()
	if err != nil {
		t.Fatalf("loadLastBuild returned error: %v", err)
	}
	if stored.Result.Subject != "" {
		t.Fatalf("cached result subject should be empty, got %q", stored.Result.Subject)
	}
	if stored.Result.PlainText != "" {
		t.Fatalf("cached result plain text should be empty, got %q", stored.Result.PlainText)
	}
	if !equalStrings(stored.Tokens, tokens) {
		t.Fatalf("cached tokens mismatch: got %v, want %v", stored.Tokens, tokens)
	}

	if originalResult.Subject != "Original subject" {
		t.Fatalf("original result subject mutated, got %q", originalResult.Subject)
	}
	if originalResult.PlainText == "" {
		t.Fatalf("original result plain text should remain populated")
	}
}

func TestSavePresetExcludesSubject(t *testing.T) {
	configDir := t.TempDir()
	t.Setenv(configDirEnv, configDir)

	build := &BuildResult{
		SchemaVersion: "v1",
		Subject:       "Preset subject",
		PlainText:     "Preset rendered plain text",
		Axes:          AxesResult{Static: "show"},
		Persona:       PersonaResult{Voice: "teacher"},
		Tokens:        []string{"show", "struct", "flow"},
	}

	if err := saveLastBuild(build, build.Tokens); err != nil {
		t.Fatalf("saveLastBuild returned error: %v", err)
	}

	stored, err := loadLastBuild()
	if err != nil {
		t.Fatalf("loadLastBuild returned error: %v", err)
	}

	slug, err := savePreset("Daily Plan", stored, true)
	if err != nil {
		t.Fatalf("savePreset returned error: %v", err)
	}
	if slug != "daily-plan" {
		t.Fatalf("unexpected slug: got %q", slug)
	}

	preset, _, err := loadPreset("Daily Plan")
	if err != nil {
		t.Fatalf("loadPreset returned error: %v", err)
	}
	if preset.Result.Subject != "" {
		t.Fatalf("preset subject should be empty, got %q", preset.Result.Subject)
	}
	if preset.Result.PlainText != "" {
		t.Fatalf("preset plain text should be empty, got %q", preset.Result.PlainText)
	}

	presetPath := filepath.Join(configDir, presetsDirName, slug+".json")
	payload, err := os.ReadFile(presetPath)
	if err != nil {
		t.Fatalf("reading preset file: %v", err)
	}
	if strings.Contains(string(payload), "plain_text") {
		t.Fatalf("expected preset file JSON to omit plain_text field, got:\n%s", payload)
	}

	var details bytes.Buffer
	renderPresetDetails(&details, preset)
	expectedHint := "Plain text: (re-run 'bar preset use Daily Plan' with a new prompt to render)"
	if !strings.Contains(details.String(), expectedHint) {
		t.Fatalf("expected preset details output to include plain text hint, got:\n%s", details.String())
	}
}

func equalStrings(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}
