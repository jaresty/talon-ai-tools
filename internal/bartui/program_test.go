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
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
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
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			if command != "echo-subject" {
				t.Fatalf("unexpected command %q", command)
			}
			if len(env) != 0 {
				t.Fatalf("expected no env variables, got %v", env)
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
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			if command != "cat" {
				t.Fatalf("unexpected command %q", command)
			}
			if len(env) != 0 {
				t.Fatalf("expected no env variables, got %v", env)
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
		RunCommand: func(ctx context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			if len(env) != 0 {
				t.Fatalf("expected no env variables, got %v", env)
			}
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

func TestEnvironmentAllowlistVisible(t *testing.T) {
	allowed := map[string]string{
		"CHATGPT_API_KEY": "secret",
		"ORG_ID":          "org",
	}
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			if command != "echo" {
				t.Fatalf("unexpected command %q", command)
			}
			if len(env) != len(allowed) {
				t.Fatalf("expected %d env variables, got %v", len(allowed), env)
			}
			for name, value := range allowed {
				if env[name] != value {
					t.Fatalf("expected env %s to equal %q, got %q", name, value, env[name])
				}
			}
			return "ok", "", nil
		},
		CommandTimeout: time.Second,
		AllowedEnv:     allowed,
		MissingEnv:     []string{"NOT_SET"},
	}

	m := newModel(opts)
	if !strings.Contains(m.statusMessage, "Environment allowlist: CHATGPT_API_KEY, ORG_ID") {
		t.Fatalf("expected status message to mention allowlist, got %q", m.statusMessage)
	}
	if !strings.Contains(m.statusMessage, "Missing environment variables: NOT_SET") {
		t.Fatalf("expected status message to mention missing vars, got %q", m.statusMessage)
	}

	view := m.View()
	if !strings.Contains(view, "Environment allowlist: CHATGPT_API_KEY, ORG_ID") {
		t.Fatalf("expected view to include allowlist, got:\n%s", view)
	}
	if !strings.Contains(view, "Missing environment variables: NOT_SET") {
		t.Fatalf("expected view to include missing env, got:\n%s", view)
	}

	m.command.SetValue("echo")
	cmd := (&m).executeSubjectCommand()
	if cmd == nil {
		t.Fatalf("expected executeSubjectCommand to return a tea.Cmd")
	}
	msg := cmd()
	m, next := updateModel(t, m, msg)
	if next != nil {
		t.Fatalf("unexpected follow-up command: %T", next)
	}
	if !strings.EqualFold(m.lastResult.Stdout, "ok") {
		t.Fatalf("expected stdout to be ok, got %q", m.lastResult.Stdout)
	}
	if len(m.lastResult.EnvVars) != len(allowed) {
		t.Fatalf("expected last result to record env vars, got %v", m.lastResult.EnvVars)
	}
}

func TestToggleEnvironmentAllowlist(t *testing.T) {
	allowed := map[string]string{
		"CHATGPT_API_KEY": "secret",
		"ORG_ID":          "org",
	}
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
		AllowedEnv:     allowed,
	}

	m := newModel(opts)
	if got := len(m.allowedEnv); got != 2 {
		t.Fatalf("expected 2 allowed env entries, got %d", got)
	}

	tab := tea.KeyMsg{Type: tea.KeyTab}
	m, cmd := updateModel(t, m, tab)
	if cmd != nil {
		t.Fatalf("unexpected command during first tab: %T", cmd)
	}
	m, cmd = updateModel(t, m, tab)
	if cmd != nil {
		t.Fatalf("unexpected command during second tab: %T", cmd)
	}
	if m.focus != focusEnvironment {
		t.Fatalf("expected focusEnvironment after two tabs, got %v", m.focus)
	}

	toggle := tea.KeyMsg{Type: tea.KeyCtrlE}
	m, cmd = updateModel(t, m, toggle)
	if cmd != nil {
		t.Fatalf("unexpected command when toggling: %T", cmd)
	}
	if len(m.allowedEnv) != 1 || m.allowedEnv[0] != "ORG_ID" {
		t.Fatalf("expected only ORG_ID to remain, got %v", m.allowedEnv)
	}

	selectAll := tea.KeyMsg{Type: tea.KeyCtrlA}
	m, cmd = updateModel(t, m, selectAll)
	if cmd != nil {
		t.Fatalf("unexpected command when selecting all: %T", cmd)
	}
	if len(m.allowedEnv) != 2 {
		t.Fatalf("expected allowlist to repopulate, got %v", m.allowedEnv)
	}

	clear := tea.KeyMsg{Type: tea.KeyCtrlX}
	m, cmd = updateModel(t, m, clear)
	if cmd != nil {
		t.Fatalf("unexpected command when clearing: %T", cmd)
	}
	if len(m.allowedEnv) != 0 {
		t.Fatalf("expected allowlist to clear, got %v", m.allowedEnv)
	}

	m, cmd = updateModel(t, m, selectAll)
	if cmd != nil {
		t.Fatalf("unexpected command when restoring after clear: %T", cmd)
	}
	if len(m.allowedEnv) != 2 {
		t.Fatalf("expected allowlist to repopulate after clear, got %v", m.allowedEnv)
	}

	down := tea.KeyMsg{Type: tea.KeyDown}
	m, cmd = updateModel(t, m, down)
	if cmd != nil {
		t.Fatalf("unexpected command when moving selection: %T", cmd)
	}
	if m.envSelection != 1 {
		t.Fatalf("expected envSelection to move to index 1, got %d", m.envSelection)
	}

	m, cmd = updateModel(t, m, toggle)
	if cmd != nil {
		t.Fatalf("unexpected command when toggling second entry: %T", cmd)
	}
	if len(m.allowedEnv) != 1 || m.allowedEnv[0] != "CHATGPT_API_KEY" {
		t.Fatalf("expected only CHATGPT_API_KEY to remain, got %v", m.allowedEnv)
	}
}

func TestToggleHelpOverlay(t *testing.T) {
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}

	m := newModel(opts)
	if strings.Contains(m.View(), "Help overlay") {
		t.Fatalf("expected help overlay to be hidden by default")
	}

	helpKey := tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'?'}}
	m, cmd := updateModel(t, m, helpKey)
	if cmd != nil {
		t.Fatalf("unexpected command when toggling help: %T", cmd)
	}
	view := m.View()
	if !strings.Contains(view, "Help overlay (press ? to close)") {
		t.Fatalf("expected view to include help overlay contents, got:\n%s", view)
	}
	if !strings.Contains(strings.ToLower(m.statusMessage), "help overlay") {
		t.Fatalf("expected status message to reference help overlay, got %q", m.statusMessage)
	}

	m, cmd = updateModel(t, m, helpKey)
	if cmd != nil {
		t.Fatalf("unexpected command when toggling help off: %T", cmd)
	}
	view = m.View()
	if strings.Contains(view, "Help overlay (press ? to close)") {
		t.Fatalf("expected help overlay to be hidden after toggling off, got:\n%s", view)
	}
	if !strings.Contains(strings.ToLower(m.statusMessage), "help overlay closed") {
		t.Fatalf("expected status message to acknowledge closing help, got %q", m.statusMessage)
	}
}
