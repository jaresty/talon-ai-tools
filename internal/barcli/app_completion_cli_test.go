package barcli

import (
	"bytes"
	"strings"
	"testing"
)

func TestRunCompletionRequiresShell(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"completion"}, strings.NewReader(""), stdout, stderr)

	if exit == 0 {
		t.Fatalf("expected non-zero exit when shell argument is missing")
	}
	if !strings.Contains(stderr.String(), "completion requires a shell") {
		t.Fatalf("expected missing shell error, got: %s", stderr.String())
	}
}

func TestRunCompletionGeneratesScripts(t *testing.T) {
	shells := []struct {
		name     string
		expected string
	}{{"bash", "__complete bash"}, {"zsh", "#compdef bar"}, {"fish", "function __fish_bar_completions"}}

	for _, tc := range shells {
		t.Run(tc.name, func(t *testing.T) {
			stdout := &bytes.Buffer{}
			stderr := &bytes.Buffer{}
			exit := Run([]string{"completion", tc.name}, strings.NewReader(""), stdout, stderr)
			if exit != 0 {
				t.Fatalf("expected exit 0 for %s, got %d with stderr: %s", tc.name, exit, stderr.String())
			}
			if !strings.Contains(stdout.String(), tc.expected) {
				t.Fatalf("expected %s script to contain %q, got: %s", tc.name, tc.expected, stdout.String())
			}
		})
	}
}

func TestRunCompletionEngineProducesSuggestions(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"__complete", "bash", "2", "bar", "build", ""}, strings.NewReader(""), stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected completion engine exit 0, got %d with stderr: %s", exit, stderr.String())
	}
	if !strings.Contains(stdout.String(), "todo") {
		t.Fatalf("expected completion suggestions to include todo, got: %s", stdout.String())
	}
}

func TestRunCompletionEngineInvalidIndex(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"__complete", "bash", "not-an-int"}, strings.NewReader(""), stdout, stderr)

	if exit == 0 {
		t.Fatalf("expected non-zero exit for invalid index")
	}
	if !strings.Contains(stderr.String(), "invalid completion index") {
		t.Fatalf("expected invalid index error, got: %s", stderr.String())
	}
}
