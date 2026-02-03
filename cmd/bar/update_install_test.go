package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
	"github.com/talonvoice/talon-ai-tools/internal/updater"
)

func TestUpdateInstallIntegration(t *testing.T) {
	// This test validates that the install command orchestrates all components
	// Skip in short mode as it requires more setup
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	tmpDir := t.TempDir()

	// Create a fake current binary
	currentBinary := filepath.Join(tmpDir, "bar")
	if err := os.WriteFile(currentBinary, []byte("old-version"), 0755); err != nil {
		t.Fatalf("failed to create current binary: %v", err)
	}

	// Set up environment to point to our test binary
	oldExecutable, _ := os.Executable()
	defer func() {
		// Restore after test
		_ = oldExecutable
	}()

	// Create mock client with no releases
	mockClient := &updater.MockGitHubClient{
		Releases: []updater.MockRelease{},
	}

	// Set up test environment by injecting mock client
	barcli.SetVersion("1.0.0")
	barcli.SetUpdateClient(mockClient)
	defer func() {
		// Reset to defaults after test
		barcli.SetVersion("dev")
		barcli.SetUpdateClient(nil)
	}()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	// Run update install command
	// This should fail because we haven't set up a real GitHub release
	// But we're testing that the code path exists and attempts the operation
	exitCode := barcli.Run([]string{"update", "install"}, strings.NewReader(""), stdout, stderr)

	// For now, we expect this to fail with a real error message
	// (not "not yet implemented")
	if exitCode == 0 {
		t.Errorf("expected non-zero exit code for install without available release")
	}

	stderrStr := stderr.String()
	if strings.Contains(stderrStr, "not yet implemented") {
		t.Errorf("install command still shows 'not yet implemented', expected real error")
	}

	// Should contain indication that no releases are available
	output := stdout.String() + stderrStr
	if !strings.Contains(strings.ToLower(output), "no releases") {
		t.Errorf("expected output to mention no releases available, got: %s", output)
	}
}
