package barcli_test

import (
	"bytes"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
	"github.com/talonvoice/talon-ai-tools/internal/bartui2"
)

// TestTUI2CommandSeedsInitialCommand verifies that --command seeds InitialCommand
// into bartui2.Options so the Run Command field is pre-filled at launch.
func TestTUI2CommandSeedsInitialCommand(t *testing.T) {
	const cmd = "echo hello"
	restore := barcli.SetTUI2Starter(func(opts bartui2.Options) error {
		if opts.InitialCommand != cmd {
			t.Fatalf("expected InitialCommand %q, got %q", cmd, opts.InitialCommand)
		}
		return nil
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui2", "--command", cmd}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", exit, stderr.String())
	}
}

// TestTUI2CMDAlias verifies that --cmd is accepted as an alias for --command.
func TestTUI2CMDAlias(t *testing.T) {
	const cmd = "pbcopy"
	restore := barcli.SetTUI2Starter(func(opts bartui2.Options) error {
		if opts.InitialCommand != cmd {
			t.Fatalf("expected InitialCommand via --cmd %q, got %q", cmd, opts.InitialCommand)
		}
		return nil
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui2", "--cmd", cmd}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected exit 0 with --cmd alias, got %d with stderr: %s", exit, stderr.String())
	}
}

// TestTUI2CommandParsed verifies that cli.Parse records the --command value.
func TestTUI2CommandParsed(t *testing.T) {
	cfg, err := cli.Parse([]string{"tui2", "--command", "echo test"})
	if err != nil {
		t.Fatalf("unexpected parse error: %v", err)
	}
	if cfg.InitialCommand != "echo test" {
		t.Fatalf("expected InitialCommand %q, got %q", "echo test", cfg.InitialCommand)
	}
}
