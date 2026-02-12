package barcli

import (
	"bytes"
	"os"
	"strings"
	"testing"
)

// TestHelpAdvertisesTUI2 specifies that the general help output must mention
// bar tui2 as an available interactive surface (ADR-0073, ADR-0081).
// tui2 is the recommended command-centric grammar learning interface.
func TestHelpAdvertisesTUI2(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"help"}, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected bar help exit 0, got %d: %s", exit, stderr.String())
	}
	if !strings.Contains(stdout.String(), "tui2") {
		t.Fatalf("bar help output must mention tui2 as an interactive surface; got:\n%s", stdout.String())
	}
}

// TestPlainOutputTokensHelp specifies that --plain strips section headers and
// bullet decorations from bar help tokens output, leaving one slug per line
// suitable for piping to grep/fzf (ADR-0073).
func TestPlainOutputTokensHelp(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"help", "tokens", "--plain"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected bar help tokens --plain exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()

	if strings.Contains(output, "TASKS") {
		t.Error("--plain must not emit TASKS section header")
	}
	if strings.Contains(output, "CONTRACT AXES") {
		t.Error("--plain must not emit CONTRACT AXES section header")
	}
	if strings.Contains(output, "•") {
		t.Error("--plain must not emit bullet characters")
	}
	// Core task tokens must still be present
	if !strings.Contains(output, "make") {
		t.Error("--plain output must include token slug 'make'")
	}
	// Each line must be non-empty slug text (no leading spaces from bullets)
	for _, line := range strings.Split(strings.TrimSpace(output), "\n") {
		if strings.HasPrefix(line, " ") || strings.HasPrefix(line, "\t") {
			t.Errorf("--plain output must not indent lines; got: %q", line)
			break
		}
	}
}

// TestHelpConversationLoops specifies that bar help includes a CONVERSATION LOOPS
// section that bridges CLI and bar tui2 for grammar discovery (ADR-0073).
func TestHelpConversationLoops(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"help"}, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected bar help exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()
	loopsIdx := strings.Index(output, "CONVERSATION LOOPS")
	if loopsIdx < 0 {
		t.Fatalf("bar help must include a CONVERSATION LOOPS section; got:\n%s", output)
	}
	loopsSection := output[loopsIdx:]
	if !strings.Contains(loopsSection, "tui2") {
		t.Fatalf("CONVERSATION LOOPS section must reference bar tui2; section:\n%s", loopsSection)
	}
}

// TestHelpTUI2IsRecommended specifies that the help text positions tui2 as
// the recommended interactive surface for new users (ADR-0081 supersedes ADR-0077).
func TestHelpTUI2IsRecommended(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"help"}, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected bar help exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()
	// tui2 entry must appear in the COMMANDS section
	commandsIdx := strings.Index(output, "COMMANDS")
	if commandsIdx < 0 {
		t.Fatalf("bar help must have a COMMANDS section; got:\n%s", output)
	}
	commandsSection := output[commandsIdx:]
	if !strings.Contains(commandsSection, "tui2") {
		t.Fatalf("tui2 must appear in the COMMANDS section; commands section:\n%s", commandsSection)
	}
	// tui2 must be described as recommended
	if !strings.Contains(commandsSection, "recommended") {
		t.Fatalf("tui2 COMMANDS entry must mention 'recommended'; commands section:\n%s", commandsSection)
	}
}
