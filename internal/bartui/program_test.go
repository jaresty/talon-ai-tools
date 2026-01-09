package bartui

import (
	"context"
	"testing"
	"time"
)

func TestLoadSubjectFromClipboard(t *testing.T) {
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "from clipboard", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	(&m).loadSubjectFromClipboard()
	if got := m.subject.Value(); got != "from clipboard" {
		t.Fatalf("expected subject to load from clipboard, got %q", got)
	}
	if m.preview != "preview:from clipboard" {
		t.Fatalf("expected preview to refresh, got %q", m.preview)
	}
}

func TestExecuteSubjectCommand(t *testing.T) {
	var receivedStdin string
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string) (string, string, error) {
			if command != "echo-subject" {
				t.Fatalf("unexpected command %q", command)
			}
			receivedStdin = stdin
			return "new subject\n", "stderr output", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.command.SetValue("echo-subject")
	(&m).executeSubjectCommand()

	if receivedStdin != "" {
		t.Fatalf("expected empty stdin for subject command, got %q", receivedStdin)
	}
	if got := m.subject.Value(); got != "new subject" {
		t.Fatalf("expected subject to update, got %q", got)
	}
	if m.lastResult.Stdout != "new subject\n" {
		t.Fatalf("expected stdout recorded, got %q", m.lastResult.Stdout)
	}
	if m.lastResult.Stderr != "stderr output" {
		t.Fatalf("expected stderr recorded, got %q", m.lastResult.Stderr)
	}
	if m.lastResult.UsedPreview {
		t.Fatalf("expected UsedPreview to be false")
	}
}

func TestExecutePreviewCommandAndReinsert(t *testing.T) {
	var receivedStdin string
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string) (string, string, error) {
			if command != "cat" {
				t.Fatalf("unexpected command %q", command)
			}
			receivedStdin = stdin
			return "command stdout\n", "stderr", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.command.SetValue("cat")
	(&m).executePreviewCommand()

	if receivedStdin != "preview:"+m.subject.Value() {
		t.Fatalf("expected preview to be piped, got %q", receivedStdin)
	}
	if m.lastResult.Stdout != "command stdout\n" {
		t.Fatalf("expected stdout recorded, got %q", m.lastResult.Stdout)
	}
	if !m.lastResult.UsedPreview {
		t.Fatalf("expected UsedPreview to be true")
	}

	(&m).reinsertLastResult()
	if got := m.subject.Value(); got != "command stdout" {
		t.Fatalf("expected subject replaced with stdout, got %q", got)
	}
}
