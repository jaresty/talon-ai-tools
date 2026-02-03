package main

import (
	"bytes"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
)

func TestUpdateHelpCommand(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"update", "--help"}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected update --help exit 0, got %d with stderr: %s", exit, stderr.String())
	}
	output := stdout.String()
	if !strings.Contains(output, "update") {
		t.Fatalf("expected help output to contain 'update', got: %s", output)
	}
	if !strings.Contains(output, "check") {
		t.Fatalf("expected help output to mention 'check' verb, got: %s", output)
	}
	if !strings.Contains(output, "install") {
		t.Fatalf("expected help output to mention 'install' verb, got: %s", output)
	}
	if !strings.Contains(output, "rollback") {
		t.Fatalf("expected help output to mention 'rollback' verb, got: %s", output)
	}
}
