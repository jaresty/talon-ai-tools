package barcli

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestInstallHooksPostCompact(t *testing.T) {
	dir := t.TempDir()
	settingsPath := filepath.Join(dir, "settings.json")

	stdout := &strings.Builder{}
	stderr := &strings.Builder{}

	opts := &installHooksOptions{
		settingsPath: settingsPath,
	}

	code := runInstallHooks(opts, stdout, stderr)
	if code != 0 {
		t.Fatalf("runInstallHooks returned %d; stderr: %s", code, stderr.String())
	}

	data, err := os.ReadFile(settingsPath)
	if err != nil {
		t.Fatalf("settings.json not created: %v", err)
	}

	var settings map[string]any
	if err := json.Unmarshal(data, &settings); err != nil {
		t.Fatalf("settings.json invalid JSON: %v", err)
	}

	hooks, ok := settings["hooks"].(map[string]any)
	if !ok {
		t.Fatal("settings.json missing 'hooks' key")
	}

	if _, ok := hooks["PostCompact"]; !ok {
		t.Fatal("settings.json missing 'hooks.PostCompact' entry")
	}
}

func TestInstallHooksIdempotent(t *testing.T) {
	dir := t.TempDir()
	settingsPath := filepath.Join(dir, "settings.json")

	opts := &installHooksOptions{settingsPath: settingsPath}

	// Run twice
	runInstallHooks(opts, &strings.Builder{}, &strings.Builder{})
	runInstallHooks(opts, &strings.Builder{}, &strings.Builder{})

	data, _ := os.ReadFile(settingsPath)
	var settings map[string]any
	json.Unmarshal(data, &settings) //nolint:errcheck

	hooks := settings["hooks"].(map[string]any)
	entries := hooks["PostCompact"].([]any)
	if len(entries) != 1 {
		t.Fatalf("expected 1 PostCompact hook entry after idempotent run, got %d", len(entries))
	}
}
