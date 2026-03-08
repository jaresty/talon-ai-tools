package main

import (
	"bytes"
	"errors"
	"strings"
	"testing"
	"time"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
	"github.com/talonvoice/talon-ai-tools/internal/bartui2"
	"github.com/talonvoice/talon-ai-tools/internal/updater"
)

func TestTUICommandLaunchesProgram(t *testing.T) {
	restore := barcli.SetTUI2Starter(func(opts bartui2.Options) error {
		if opts.NoAltScreen {
			t.Fatalf("expected alt screen to be enabled by default")
		}
		if opts.Preview == nil {
			t.Fatalf("expected preview function")
		}
		if opts.RunCommand == nil {
			t.Fatalf("expected run command function")
		}
		if opts.ClipboardWrite == nil {
			t.Fatalf("expected clipboard write to be wired")
		}
		if opts.CommandTimeout != 30*time.Second {
			t.Fatalf("expected default command timeout, got %s", opts.CommandTimeout)
		}
		preview, err := opts.Preview("Example subject", "", opts.InitialTokens)
		if err != nil {
			t.Fatalf("preview returned error: %v", err)
		}
		if preview == "" {
			t.Fatalf("expected preview output")
		}
		return nil
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui", "make", "struct"}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected tui exit 0, got %d with stderr: %s", exit, stderr.String())
	}
}

func TestTUICommandRespectsNoAltScreen(t *testing.T) {
	restore := barcli.SetTUI2Starter(func(opts bartui2.Options) error {
		if !opts.NoAltScreen {
			t.Fatalf("expected alt screen to be disabled when --no-alt-screen is used")
		}
		return nil
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui", "--no-alt-screen"}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected tui exit 0 with --no-alt-screen, got %d with stderr: %s", exit, stderr.String())
	}
}

func TestTUICommandRejectsJSONFlag(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui", "--json"}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected non-zero exit for --json flag")
	}
	if !strings.Contains(stderr.String(), "does not support --json") {
		t.Fatalf("expected error message about --json, got: %s", stderr.String())
	}
}

func TestTUICommandSurfacesProgramErrors(t *testing.T) {
	restore := barcli.SetTUI2Starter(func(opts bartui2.Options) error {
		return errors.New("boom")
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui"}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected non-zero exit when program fails")
	}
	if !strings.Contains(stderr.String(), "tui2") {
		t.Fatalf("expected launch error message, got: %s", stderr.String())
	}
}

func TestTUI2AliasEmitsDeprecationWarning(t *testing.T) {
	restore := barcli.SetTUI2Starter(func(opts bartui2.Options) error {
		return nil
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui2"}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected tui2 alias exit 0, got %d with stderr: %s", exit, stderr.String())
	}
	if !strings.Contains(stderr.String(), "deprecated") {
		t.Fatalf("expected deprecation warning for tui2, got: %s", stderr.String())
	}
}

func TestTUICommandIgnoresUpdateCheck(t *testing.T) {
	// Suppress background update check so no stale "update available" notice leaks into stderr.
	t.Setenv("BAR_CONFIG_DIR", t.TempDir())
	barcli.SetUpdateClient(&updater.MockGitHubClient{Releases: nil})
	defer barcli.SetUpdateClient(nil)

	restore := barcli.SetTUI2Starter(func(opts bartui2.Options) error {
		return nil
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui"}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected tui exit 0, got %d with stderr: %s", exit, stderr.String())
	}
}
