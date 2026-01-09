package main

import (
	"bytes"
	"errors"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

func TestTUICommandLaunchesProgram(t *testing.T) {
	restore := barcli.SetTUIStarter(func(opts bartui.Options) error {
		if opts.Preview == nil {
			t.Fatalf("expected preview function")
		}
		preview, err := opts.Preview("Example subject")
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
	exit := barcli.Run([]string{"tui", "todo", "focus"}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected tui exit 0, got %d with stderr: %s", exit, stderr.String())
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
	restore := barcli.SetTUIStarter(func(opts bartui.Options) error {
		return errors.New("boom")
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui"}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected non-zero exit when program fails")
	}
	if !strings.Contains(stderr.String(), "launch tui") {
		t.Fatalf("expected launch error message, got: %s", stderr.String())
	}
}
