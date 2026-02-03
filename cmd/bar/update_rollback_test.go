package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
)

func TestUpdateRollbackIntegration(t *testing.T) {
	// This test validates that the rollback command orchestrates BinaryInstaller.Rollback
	// Skip in short mode as it requires more setup
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	tmpDir := t.TempDir()

	// Create a fake current binary
	currentBinary := filepath.Join(tmpDir, "bar")
	if err := os.WriteFile(currentBinary, []byte("current-version"), 0755); err != nil {
		t.Fatalf("failed to create current binary: %v", err)
	}

	// Create backup directory with a backup file
	backupDir := filepath.Join(tmpDir, ".bar-backups")
	if err := os.MkdirAll(backupDir, 0755); err != nil {
		t.Fatalf("failed to create backup directory: %v", err)
	}

	backupFile := filepath.Join(backupDir, "bar.20240101-120000.bak")
	if err := os.WriteFile(backupFile, []byte("old-version"), 0755); err != nil {
		t.Fatalf("failed to create backup file: %v", err)
	}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	// Run update rollback command
	// Without a real binary to rollback, this will fail, but it should
	// attempt the operation (not show "not yet implemented")
	exitCode := barcli.Run([]string{"update", "rollback"}, strings.NewReader(""), stdout, stderr)

	// Should show an error (non-zero exit) but NOT "not yet implemented"
	stderrStr := stderr.String()
	if strings.Contains(stderrStr, "not yet implemented") {
		t.Errorf("rollback command still shows 'not yet implemented', expected real error")
	}

	// Should contain some indication it tried to do rollback
	output := stdout.String() + stderrStr
	if !strings.Contains(strings.ToLower(output), "rollback") &&
		!strings.Contains(strings.ToLower(output), "backup") &&
		!strings.Contains(strings.ToLower(output), "restore") {
		t.Errorf("expected output to mention rollback attempt, got: %s", output)
	}

	_ = exitCode // May be zero or non-zero depending on whether backups exist
}
