package barcli

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func runCLI(t *testing.T, args []string) (stdout, stderr string, exit int) {
	t.Helper()
	stdoutBuf := &bytes.Buffer{}
	stderrBuf := &bytes.Buffer{}
	exit = Run(args, strings.NewReader(""), stdoutBuf, stderrBuf)
	return stdoutBuf.String(), stderrBuf.String(), exit
}

func TestRunPresetListEmpty(t *testing.T) {
	configRoot := t.TempDir()
	t.Setenv(configDirEnv, configRoot)

	stdout, stderr, exit := runCLI(t, []string{"preset", "list"})

	if exit != 0 {
		t.Fatalf("expected exit 0 for empty preset list, got %d with stderr: %s", exit, stderr)
	}
	if !strings.Contains(stdout, "No presets saved.") {
		t.Fatalf("expected message about empty preset list, got: %s", stdout)
	}
}

func TestRunPresetLifecycle(t *testing.T) {
	configRoot := t.TempDir()
	t.Setenv(configDirEnv, configRoot)

	// Build once to seed last build state for preset save/use flows.
	stdout, stderr, exit := runCLI(t, []string{"build", "make", "struct", "--prompt", "Initial subject"})
	if exit != 0 {
		t.Fatalf("build failed: %d, stderr: %s", exit, stderr)
	}
	if !strings.Contains(stdout, "Initial subject") {
		t.Fatalf("expected build output to include subject, got: %s", stdout)
	}

	// Save preset.
	stdout, stderr, exit = runCLI(t, []string{"preset", "save", "daily-plan"})
	if exit != 0 {
		t.Fatalf("preset save failed: %d, stderr: %s", exit, stderr)
	}
	if !strings.Contains(stdout, "Saved preset \"daily-plan\"") {
		t.Fatalf("expected save confirmation, got: %s", stdout)
	}

	// List presets should show entry.
	stdout, stderr, exit = runCLI(t, []string{"preset", "list"})
	if exit != 0 {
		t.Fatalf("preset list failed: %d, stderr: %s", exit, stderr)
	}
	if !strings.Contains(stdout, "daily-plan") {
		t.Fatalf("expected preset list to include daily-plan, got: %s", stdout)
	}

	// Show preset as JSON.
	jsonStdout := &bytes.Buffer{}
	jsonStderr := &bytes.Buffer{}
	jsonExit := Run([]string{"preset", "show", "daily-plan", "--json"}, strings.NewReader(""), jsonStdout, jsonStderr)
	if jsonExit != 0 {
		t.Fatalf("preset show --json failed: %d, stderr: %s", jsonExit, jsonStderr.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(jsonStdout.Bytes(), &payload); err != nil {
		t.Fatalf("failed to parse preset JSON: %v\n%s", err, jsonStdout.String())
	}
	if payload["name"] != "daily-plan" {
		t.Fatalf("expected preset JSON name daily-plan, got: %#v", payload["name"])
	}

	// Use preset with new prompt.
	stdout, stderr, exit = runCLI(t, []string{"preset", "use", "daily-plan", "--prompt", "Fresh subject"})
	if exit != 0 {
		t.Fatalf("preset use failed: %d, stderr: %s", exit, stderr)
	}
	if !strings.Contains(stdout, "Fresh subject") {
		t.Fatalf("expected preset use output to include new subject, got: %s", stdout)
	}

	// Delete without --force should fail.
	stdout, stderr, exit = runCLI(t, []string{"preset", "delete", "daily-plan"})
	if exit == 0 {
		t.Fatalf("expected delete without --force to fail")
	}
	if !strings.Contains(stderr, "requires --force") {
		t.Fatalf("expected force reminder, got: %s", stderr)
	}

	// Delete with --force succeeds.
	stdout, stderr, exit = runCLI(t, []string{"preset", "delete", "daily-plan", "--force"})
	if exit != 0 {
		t.Fatalf("preset delete --force failed: %d, stderr: %s", exit, stderr)
	}
	if !strings.Contains(stdout, "Deleted preset \"daily-plan\"") {
		t.Fatalf("expected delete confirmation, got: %s", stdout)
	}

	// After deletion, list should be empty again.
	stdout, stderr, exit = runCLI(t, []string{"preset", "list"})
	if exit != 0 {
		t.Fatalf("preset list after delete failed: %d, stderr: %s", exit, stderr)
	}
	if !strings.Contains(stdout, "No presets saved.") {
		t.Fatalf("expected empty preset list after deletion, got: %s", stdout)
	}
}

func TestRunPresetShowErrorsForMissingPreset(t *testing.T) {
	configRoot := t.TempDir()
	t.Setenv(configDirEnv, configRoot)

	stdout, stderr, exit := runCLI(t, []string{"preset", "show", "unknown"})

	if exit == 0 {
		t.Fatalf("expected non-zero exit when preset is missing")
	}
	if stdout != "" {
		t.Fatalf("expected no stdout for missing preset, got: %s", stdout)
	}
	if !strings.Contains(stderr, "unknown") {
		t.Fatalf("expected missing preset message, got: %s", stderr)
	}
}

func TestRunPresetListReadsExistingFiles(t *testing.T) {
	configRoot := t.TempDir()
	t.Setenv(configDirEnv, configRoot)

	// Manually craft a preset file to ensure loader handles arbitrary ordering.
	presetDir := filepath.Join(configRoot, presetsDirName)
	if err := os.MkdirAll(presetDir, 0o700); err != nil {
		t.Fatalf("mkdir presets: %v", err)
	}
	presetPath := filepath.Join(presetDir, "manual.json")
	payload := `{"version":3,"name":"manual","saved_at":"2026-01-12T00:00:00Z","source":"last_build","result":{"schema_version":"v1","subject":"","plain_text":"","axes":{"task":"make"},"persona":{}},"tokens":["make"]}`
	if err := os.WriteFile(presetPath, []byte(payload), 0o600); err != nil {
		t.Fatalf("write preset: %v", err)
	}

	stdout, stderr, exit := runCLI(t, []string{"preset", "list"})

	if exit != 0 {
		t.Fatalf("preset list failed: %d, stderr: %s", exit, stderr)
	}
	if !strings.Contains(stdout, "manual") {
		t.Fatalf("expected manually created preset to appear, got: %s", stdout)
	}
}
