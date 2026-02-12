package barcli

import (
	"bytes"
	"os"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

// TestNoInputRejectsTUI specifies that bar tui --no-input must exit non-zero
// and emit guidance pointing to --fixture as the non-interactive alternative (ADR-0073).
// The message must NOT be a generic "unknown flag" error — it must be a purposeful rejection.
func TestNoInputRejectsTUI(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"tui", "--no-input"}, os.Stdin, stdout, stderr)

	if exit == 0 {
		t.Fatalf("expected non-zero exit for bar tui --no-input")
	}
	errMsg := stderr.String()
	if strings.Contains(errMsg, "unknown flag") {
		t.Fatalf("--no-input must be a recognised flag that produces guidance, not 'unknown flag'; got: %s", errMsg)
	}
	if !strings.Contains(errMsg, "--fixture") {
		t.Fatalf("bar tui --no-input guidance must mention --fixture as the non-interactive alternative; got: %s", errMsg)
	}
}

// TestNoInputRejectsTUI2 specifies that bar tui2 --no-input must exit non-zero
// and emit guidance pointing to --fixture as the non-interactive alternative (ADR-0073).
func TestNoInputRejectsTUI2(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"tui2", "--no-input"}, os.Stdin, stdout, stderr)

	if exit == 0 {
		t.Fatalf("expected non-zero exit for bar tui2 --no-input")
	}
	errMsg := stderr.String()
	if strings.Contains(errMsg, "unknown flag") {
		t.Fatalf("--no-input must be a recognised flag that produces guidance, not 'unknown flag'; got: %s", errMsg)
	}
	if !strings.Contains(errMsg, "--fixture") {
		t.Fatalf("bar tui2 --no-input guidance must mention --fixture as the non-interactive alternative; got: %s", errMsg)
	}
}

// TestNoInputParsed specifies that --no-input is a recognised flag (not an error).
func TestNoInputParsed(t *testing.T) {
	_, err := cli.Parse([]string{"build", "--no-input"})
	if err != nil {
		t.Fatalf("--no-input must be a recognised flag; got error: %v", err)
	}
}
