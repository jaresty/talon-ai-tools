package bartui

import (
	"context"
	"errors"
	"strings"
	"testing"
	"time"

	tea "github.com/charmbracelet/bubbletea"
)

func updateModel(t *testing.T, m model, msg tea.Msg) (model, tea.Cmd) {
	t.Helper()
	updated, cmd := m.Update(msg)
	mm, ok := updated.(model)
	if !ok {
		t.Fatalf("expected model, got %T", updated)
	}
	return mm, cmd
}

func updateExpectNoCmd(t *testing.T, m model, msg tea.Msg) model {
	t.Helper()
	updated, cmd := updateModel(t, m, msg)
	if cmd != nil {
		t.Fatalf("unexpected command from update: %T", cmd)
	}
	return updated
}

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
	cmd := (&m).executeSubjectCommand()
	if cmd == nil {
		t.Fatalf("expected executeSubjectCommand to return a tea.Cmd")
	}
	if !m.commandRunning {
		t.Fatalf("expected commandRunning to be true while command executes")
	}
	if !strings.Contains(m.statusMessage, "Running") {
		t.Fatalf("expected status message to indicate running, got %q", m.statusMessage)
	}
	if receivedStdin != "" {
		t.Fatalf("expected empty stdin for subject command, got %q", receivedStdin)
	}

	msg := cmd()
	m, next := updateModel(t, m, msg)
	if next != nil {
		t.Fatalf("unexpected follow-up command: %T", next)
	}
	if m.commandRunning {
		t.Fatalf("expected commandRunning to be false after completion")
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
	cmd := (&m).executePreviewCommand()
	if cmd == nil {
		t.Fatalf("expected executePreviewCommand to return a tea.Cmd")
	}
	if !m.commandRunning {
		t.Fatalf("expected commandRunning to be true while command executes")
	}

	msg := cmd()
	m, next := updateModel(t, m, msg)
	if next != nil {
		t.Fatalf("unexpected follow-up command: %T", next)
	}

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

func TestCancelCommandWithEsc(t *testing.T) {
	started := make(chan struct{})
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(ctx context.Context, command string, stdin string) (string, string, error) {
			close(started)
			<-ctx.Done()
			return "", "", ctx.Err()
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.command.SetValue("sleep")
	cmd := (&m).executePreviewCommand()
	if cmd == nil {
		t.Fatalf("expected executePreviewCommand to return a tea.Cmd")
	}

	msgCh := make(chan tea.Msg, 1)
	go func() {
		msgCh <- cmd()
	}()
	<-started

	escMsg := tea.KeyMsg{Type: tea.KeyEsc}
	m, next := updateModel(t, m, escMsg)
	if next != nil {
		t.Fatalf("expected no quit command while cancelling, got %T", next)
	}

	msg := <-msgCh
	m, next = updateModel(t, m, msg)
	if next != nil {
		t.Fatalf("unexpected follow-up command after cancellation: %T", next)
	}

	if m.commandRunning {
		t.Fatalf("expected commandRunning to be false after cancellation")
	}
	if !errors.Is(m.lastResult.Err, context.Canceled) {
		t.Fatalf("expected last result error to be context.Canceled, got %v", m.lastResult.Err)
	}
	if !strings.Contains(strings.ToLower(m.statusMessage), "cancel") {
		t.Fatalf("expected status message to mention cancellation, got %q", m.statusMessage)
	}
}
