package main

import (
	"bytes"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
)

func TestVersionFlag(t *testing.T) {
	// Set a test version
	barcli.SetVersion("1.2.3-test")

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exitCode := barcli.Run([]string{"--version"}, strings.NewReader(""), stdout, stderr)

	// Should succeed (exit 0)
	if exitCode != 0 {
		t.Errorf("--version should exit 0, got %d", exitCode)
	}

	output := stdout.String()
	if !strings.Contains(output, "1.2.3-test") {
		t.Errorf("--version output should contain version string, got: %s", output)
	}

	// Should not show "unknown flag" error
	stderrStr := stderr.String()
	if strings.Contains(stderrStr, "unknown flag") {
		t.Errorf("--version should not produce unknown flag error, got: %s", stderrStr)
	}
}
