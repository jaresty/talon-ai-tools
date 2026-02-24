package barcli_test

// Specifying validation for ADR-0144 Phase 2: bar starter subcommand.
//
// Tests:
//   ST1 — bar starter list exits 0 and prints all 10 pack names with framings
//   ST2 — bar starter <name> exits 0 and prints bare bar build command (no trailing newline noise)
//   ST3 — bar starter <unknown> exits 1 and prints error mentioning pack name
//   ST4 — bar starter <name> output starts with "bar build "
//   ST5 — bar starter list output contains every pack name from the grammar

import (
	"bytes"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
)

func runStarter(args ...string) (stdout, stderr string, code int) {
	var out, errBuf bytes.Buffer
	code = barcli.Run(append([]string{"starter"}, args...), nil, &out, &errBuf)
	return out.String(), errBuf.String(), code
}

func TestStarterList(t *testing.T) {
	// ST1: exits 0, prints pack names and framings
	out, _, code := runStarter("list")
	if code != 0 {
		t.Fatalf("ST1: bar starter list exited %d, want 0", code)
	}
	// Must contain at least one pack name from the grammar JSON
	for _, name := range []string{"debug", "design", "review", "dissect", "pitch", "audit", "model", "charter", "explain", "versus"} {
		if !strings.Contains(out, name) {
			t.Errorf("ST1: bar starter list output missing pack %q", name)
		}
	}
}

func TestStarterListIncludesFramings(t *testing.T) {
	// ST5: list output contains framing text (not just names)
	out, _, code := runStarter("list")
	if code != 0 {
		t.Fatalf("ST5: bar starter list exited %d, want 0", code)
	}
	if !strings.Contains(out, "Diagnosing") {
		t.Errorf("ST5: bar starter list missing framing text, got:\n%s", out)
	}
}

func TestStarterNamePrintsCommand(t *testing.T) {
	// ST2 + ST4: bar starter debug exits 0, prints bare bar build command
	out, _, code := runStarter("debug")
	if code != 0 {
		t.Fatalf("ST2: bar starter debug exited %d, want 0", code)
	}
	trimmed := strings.TrimSpace(out)
	if !strings.HasPrefix(trimmed, "bar build ") {
		t.Errorf("ST4: output must start with 'bar build ', got: %q", trimmed)
	}
}

func TestStarterUnknownExitsNonZero(t *testing.T) {
	// ST3: unknown pack name exits 1 and mentions the name in stderr
	_, errOut, code := runStarter("unknownpack")
	if code == 0 {
		t.Fatal("ST3: bar starter <unknown> must exit non-zero")
	}
	if !strings.Contains(errOut, "unknownpack") {
		t.Errorf("ST3: stderr must mention the unknown pack name, got: %q", errOut)
	}
}

func TestStarterNoArgsExitsNonZero(t *testing.T) {
	// bar starter with no args should exit non-zero and show usage
	_, errOut, code := runStarter()
	if code == 0 {
		t.Fatal("bar starter with no args must exit non-zero")
	}
	if errOut == "" {
		t.Error("bar starter with no args must write to stderr")
	}
}
