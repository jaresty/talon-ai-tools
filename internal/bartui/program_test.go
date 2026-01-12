package bartui

import (
	"context"
	"errors"
	"fmt"
	"reflect"
	"strings"
	"testing"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	lipgloss "github.com/charmbracelet/lipgloss"
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
	update, cmd := updateModel(t, m, msg)
	if cmd != nil {
		t.Fatalf("unexpected command from update: %T", cmd)
	}
	return update
}

func defaultTokenCategories() []TokenCategory {
	return []TokenCategory{
		{
			Key:           "static",
			Label:         "Static Prompt",
			Kind:          TokenCategoryKindStatic,
			MaxSelections: 1,
			Options: []TokenOption{
				{Value: "todo", Slug: "todo", Label: "Todo"},
				{Value: "summary", Slug: "summary", Label: "Summary"},
			},
		},
		{
			Key:           "scope",
			Label:         "Scope",
			Kind:          TokenCategoryKindAxis,
			MaxSelections: 2,
			Options: []TokenOption{
				{Value: "focus", Slug: "focus", Label: "Focus"},
				{Value: "breadth", Slug: "breadth", Label: "Breadth"},
			},
		},
	}
}

func normalizeWhitespace(input string) string {
	return strings.Join(strings.Fields(input), " ")
}

func viewContains(view string, substr string) bool {
	return strings.Contains(normalizeWhitespace(view), normalizeWhitespace(substr))
}

func viewNotContains(view string, substr string) bool {
	return !viewContains(view, substr)
}

func historyMessages(m model) []string {
	messages := make([]string, len(m.paletteHistory))
	for i, event := range m.paletteHistory {
		messages[i] = event.Message
	}
	return messages
}

func historyKinds(m model) []historyEventKind {
	kinds := make([]historyEventKind, len(m.paletteHistory))
	for i, event := range m.paletteHistory {
		kinds[i] = event.Kind
	}
	return kinds
}

func TestLoadSubjectFromClipboard(t *testing.T) {
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "from clipboard", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.subject.SetValue("existing subject")
	m.refreshPreview()

	(&m).loadSubjectFromClipboard()
	if got := m.subject.Value(); got != "existing subject" {
		t.Fatalf("expected subject to remain unchanged until confirmation, got %q", got)
	}
	if m.pendingSubject == nil {
		t.Fatalf("expected pending subject replacement after clipboard load")
	}
	if m.pendingSubject.source != "clipboard text" {
		t.Fatalf("expected clipboard source label, got %q", m.pendingSubject.source)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if got := m.subject.Value(); got != "from clipboard" {
		t.Fatalf("expected subject to update after confirmation, got %q", got)
	}
	if m.preview != "preview:from clipboard" {
		t.Fatalf("expected preview to refresh, got %q", m.preview)
	}
	if !m.subjectUndoAvailable {
		t.Fatalf("expected undo to be available after replacement")
	}
	messages := historyMessages(m)
	kinds := historyKinds(m)
	if len(messages) == 0 || messages[0] != "Subject replaced via clipboard text" {
		t.Fatalf("expected history to record clipboard replacement, got %v", messages)
	}
	if len(kinds) == 0 || kinds[0] != historyEventKindSubject {
		t.Fatalf("expected subject history kind, got %v", kinds)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlZ})
	if got := m.subject.Value(); got != "existing subject" {
		t.Fatalf("expected undo to restore previous subject, got %q", got)
	}
	if m.subjectUndoAvailable {
		t.Fatalf("expected undo to be cleared after use")
	}
	messages = historyMessages(m)
	if len(messages) == 0 || messages[0] != "Subject undo (clipboard text)" {
		t.Fatalf("expected history to record subject undo, got %v", messages)
	}
	if len(historyKinds(m)) == 0 || historyKinds(m)[0] != historyEventKindSubject {
		t.Fatalf("expected subject history kind for undo, got %v", historyKinds(m))
	}
	if len(messages) < 2 || messages[1] != "Subject replaced via clipboard text" {
		t.Fatalf("expected replacement entry to stay in history, got %v", messages)
	}
}

func TestCancelSubjectReplacement(t *testing.T) {
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "alternate", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.subject.SetValue("keep me")
	m.refreshPreview()

	(&m).loadSubjectFromClipboard()
	if m.pendingSubject == nil {
		t.Fatalf("expected pending subject after clipboard load")
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEsc})
	if m.pendingSubject != nil {
		t.Fatalf("expected pending subject to clear after cancellation")
	}
	if got := m.subject.Value(); got != "keep me" {
		t.Fatalf("expected subject to remain unchanged, got %q", got)
	}
	if len(m.paletteHistory) != 0 {
		t.Fatalf("expected no history entry when replacement is cancelled, got %v", m.paletteHistory)
	}
}

func TestReinsertLastResultAppliesImmediately(t *testing.T) {
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.subject.SetValue("original")
	m.refreshPreview()
	m.lastResult = commandResult{Stdout: "updated via command"}

	(&m).reinsertLastResult()
	if m.pendingSubject != nil {
		t.Fatalf("expected subject replacement to apply immediately")
	}
	if got := m.subject.Value(); got != "updated via command" {
		t.Fatalf("expected subject replaced immediately, got %q", got)
	}
	if !m.subjectUndoAvailable {
		t.Fatalf("expected undo to be available after subject replacement")
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlZ})
	if got := m.subject.Value(); got != "original" {
		t.Fatalf("expected undo to restore original subject, got %q", got)
	}
	if m.subjectUndoAvailable {
		t.Fatalf("expected undo to clear after restoring original subject")
	}
}

func TestReinsertLastResultFallsBackToPreview(t *testing.T) {
	opts := Options{
		Tokens: []string{"todo"},
		Preview: func(subject string, tokens []string) (string, error) {
			return "preview line one\npreview line two\n", nil
		},
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.subject.SetValue("original")
	m.refreshPreview()
	m.lastResult = commandResult{Command: "cat", Stdout: ""}

	(&m).reinsertLastResult()
	if m.pendingSubject != nil {
		t.Fatalf("expected subject replacement to apply immediately")
	}
	expected := "preview line one\npreview line two"
	if got := m.subject.Value(); got != expected {
		t.Fatalf("expected subject replaced with preview, got %q", got)
	}
	if !m.subjectUndoAvailable {
		t.Fatalf("expected undo to be available after preview fallback")
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlZ})
	if got := m.subject.Value(); got != "original" {
		t.Fatalf("expected undo to restore original subject, got %q", got)
	}
	if m.subjectUndoAvailable {
		t.Fatalf("expected undo to clear after restoring original subject")
	}
}

func TestSubjectInputAcceptsNewlines(t *testing.T) {
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	type keySeq []tea.KeyMsg
	seq := keySeq{
		{Type: tea.KeyRunes, Runes: []rune{'H'}},
		{Type: tea.KeyEnter},
		{Type: tea.KeyRunes, Runes: []rune{'i'}},
	}

	for _, key := range seq {
		m, _ = updateModel(t, m, key)
	}

	expected := "H\ni"
	if got := m.subject.Value(); got != expected {
		t.Fatalf("expected subject to include newline, got %q", got)
	}
}

func TestCopyBuildCommandToClipboard(t *testing.T) {
	var copied string
	subject := "Need to review \"ADR 70\""
	opts := Options{
		Tokens: []string{"todo", "focus", "method=steps"},
		Preview: func(subject string, tokens []string) (string, error) {
			return "preview:" + subject + strings.Join(tokens, ","), nil
		},
		ClipboardRead: func() (string, error) { return "", nil },
		ClipboardWrite: func(text string) error {
			copied = text
			return nil
		},
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.subject.SetValue(subject)
	(&m).refreshPreview()

	msg := tea.KeyMsg{Type: tea.KeyCtrlB}
	m, cmd := updateModel(t, m, msg)
	if cmd != nil {
		t.Fatalf("expected no command after copying build command, got %T", cmd)
	}
	if copied == "" {
		t.Fatalf("expected clipboard write with build command, got empty string")
	}

	expected := "bar build todo focus method=steps --prompt 'Need to review \"ADR 70\"'"
	if copied != expected {
		t.Fatalf("expected copied command %q, got %q", expected, copied)
	}
	if !strings.Contains(m.statusMessage, "Copied bar build command") {
		t.Fatalf("expected status message to confirm copy, got %q", m.statusMessage)
	}
}

func TestExecuteSubjectCommand(t *testing.T) {
	var receivedStdin string
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
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
	m.subject.SetValue("original subject")
	m.refreshPreview()
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
		t.Fatalf("expected stdin to remain unset before execution, got %q", receivedStdin)
	}

	msg := cmd()
	m, next := updateModel(t, m, msg)
	if receivedStdin != "original subject" {
		t.Fatalf("expected subject text piped to stdin, got %q", receivedStdin)
	}
	if next != nil {
		t.Fatalf("unexpected follow-up command: %T", next)
	}
	if m.commandRunning {
		t.Fatalf("expected commandRunning to be false after completion")
	}
	if m.pendingSubject == nil {
		t.Fatalf("expected pending subject replacement after command completion")
	}
	if got := m.subject.Value(); got != "original subject" {
		t.Fatalf("expected subject to remain unchanged until confirmation, got %q", got)
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

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if got := m.subject.Value(); got != "new subject" {
		t.Fatalf("expected subject to update after confirmation, got %q", got)
	}
	if !m.subjectUndoAvailable {
		t.Fatalf("expected undo available after subject replacement")
	}
}

func TestExecutePreviewCommandAndReinsert(t *testing.T) {

	var receivedStdin string
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
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
	if m.pendingSubject != nil {
		t.Fatalf("expected subject replacement to apply immediately")
	}
	if got := m.subject.Value(); got != "command stdout" {
		t.Fatalf("expected subject replaced immediately, got %q", got)
	}
	if !m.subjectUndoAvailable {
		t.Fatalf("expected undo available after subject replacement")
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlZ})
	if got := m.subject.Value(); got != "" {
		t.Fatalf("expected undo to restore original subject, got %q", got)
	}
	if m.subjectUndoAvailable {
		t.Fatalf("expected undo to clear after restoring original subject")
	}
}

func TestCancelCommandWithEsc(t *testing.T) {
	started := make(chan struct{})
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
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
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
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
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
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
	if m.focus != focusCommand {
		t.Fatalf("expected focusCommand after first tab, got %v", m.focus)
	}

	m, cmd = updateModel(t, m, tab)
	if cmd != nil {
		t.Fatalf("unexpected command during second tab: %T", cmd)
	}
	if m.focus != focusResult {
		t.Fatalf("expected focusResult after second tab, got %v", m.focus)
	}

	m, cmd = updateModel(t, m, tab)
	if cmd != nil {
		t.Fatalf("unexpected command during third tab: %T", cmd)
	}
	if m.focus != focusEnvironment {
		t.Fatalf("expected focusEnvironment after third tab, got %v", m.focus)
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

func TestToggleShortcutReference(t *testing.T) {
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}

	m := newModel(opts)
	if strings.Contains(m.View(), "Shortcut reference") {
		t.Fatalf("expected shortcut reference to be hidden by default")
	}

	helpKey := tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'?'}}
	m, cmd := updateModel(t, m, helpKey)
	if cmd != nil {
		cmd()
	}
	view := m.View()
	if !strings.Contains(view, "Shortcut reference (press Ctrl+? to close)") {
		t.Fatalf("expected view to include shortcut reference contents, got:\n%s", view)
	}
	if !strings.Contains(view, "Press Ctrl+? or Esc to close the shortcut reference.") {
		t.Fatalf("expected shortcut reference close hint, got:\n%s", view)
	}
	if strings.Contains(view, "Subject (PgUp/PgDn") {
		t.Fatalf("expected shortcut overlay to replace main layout, got:\n%s", view)
	}
	if !strings.Contains(view, "Focus & Layout") {
		t.Fatalf("expected shortcut reference to group shortcuts under Focus & Layout, got:\n%s", view)
	}
	if !strings.Contains(strings.ToLower(m.statusMessage), "shortcut reference") {
		t.Fatalf("expected status message to reference shortcut reference, got %q", m.statusMessage)
	}

	m, cmd = updateModel(t, m, helpKey)
	if cmd != nil {
		cmd()
	}
	if strings.Contains(m.View(), "Shortcut reference (press Ctrl+? to close)") {
		t.Fatalf("expected shortcut reference to be hidden after second toggle")
	}
}

func TestShortcutReferenceEscClosesDialog(t *testing.T) {
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}

	m := newModel(opts)
	initialStatus := m.statusMessage

	helpKey := tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'?'}}
	m, cmd := updateModel(t, m, helpKey)
	if cmd != nil {
		cmd()
	}
	if !strings.Contains(m.View(), "Shortcut reference (press Ctrl+? to close)") {
		t.Fatalf("expected shortcut reference to be visible after toggle")
	}

	escKey := tea.KeyMsg{Type: tea.KeyEsc}
	m, cmd = updateModel(t, m, escKey)
	if cmd != nil {
		cmd()
	}
	if strings.Contains(m.View(), "Shortcut reference (press Ctrl+? to close)") {
		t.Fatalf("expected shortcut reference to be hidden after Esc")
	}
	if m.statusMessage != initialStatus {
		t.Fatalf("expected status message to restore after closing, got %q", m.statusMessage)
	}
}

func TestSidebarContentRespectsColumnWidth(t *testing.T) {
	longLabel := "SupercalifragilisticexpialidociousPromptAxisValue"
	categories := []TokenCategory{
		{
			Key:           "scope",
			Label:         "Scope",
			Kind:          TokenCategoryKindAxis,
			MaxSelections: 1,
			Options: []TokenOption{
				{Value: "long-scope", Slug: "scope=" + longLabel, Label: longLabel},
			},
		},
	}
	opts := Options{
		Tokens:          []string{"long-scope"},
		TokenCategories: categories,
		Preview:         func(subject string, tokens []string) (string, error) { return subject + strings.Join(tokens, ","), nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}

	m := newModel(opts)
	m.width = 90
	m.height = 32
	m.layoutViewports()
	if m.sidebarColumnWidth == 0 {
		t.Fatalf("expected sidebar column width to be positive after layout")
	}

	sidebarWidth := m.sidebarColumnWidth
	sidebar := m.renderSidebarContent()
	for _, line := range strings.Split(sidebar, "\n") {
		trimmed := strings.TrimRight(line, "\n")
		if strings.TrimSpace(trimmed) == "" {
			continue
		}
		w := lipgloss.Width(trimmed)
		t.Logf("sidebar line width=%d content=%q", w, trimmed)
		if w > sidebarWidth {
			t.Fatalf("expected sidebar line width <= %d, got %d: %q", sidebarWidth, w, trimmed)
		}
	}
}

func TestTokenKeyboardToggle(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	if !reflect.DeepEqual(m.tokens, []string{"todo", "focus"}) {
		t.Fatalf("expected initial tokens todo/focus, got %v", m.tokens)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	if m.focus != focusTokens {
		t.Fatalf("expected focusTokens after tab, got %v", m.focus)
	}
	if m.tokenCategoryIndex != 0 {
		t.Fatalf("expected initial token category index 0, got %d", m.tokenCategoryIndex)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRight})
	if m.tokenCategoryIndex != 1 {
		t.Fatalf("expected category index 1 after moving right, got %d", m.tokenCategoryIndex)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDown})
	if m.tokenOptionIndex != 1 {
		t.Fatalf("expected option index 1 after moving down, got %d", m.tokenOptionIndex)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	expectedTokens := []string{"todo", "focus", "breadth"}
	if !reflect.DeepEqual(m.tokens, expectedTokens) {
		t.Fatalf("expected tokens %v after adding breadth, got %v", expectedTokens, m.tokens)
	}

	if !reflect.DeepEqual(m.tokenStates[1].selected, []string{"focus", "breadth"}) {
		t.Fatalf("expected scope selections focus/breadth, got %v", m.tokenStates[1].selected)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDelete})
	if !reflect.DeepEqual(m.tokenStates[1].selected, []string{"focus"}) {
		t.Fatalf("expected scope selection to revert to focus, got %v", m.tokenStates[1].selected)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlZ})
	if !reflect.DeepEqual(m.tokenStates[1].selected, []string{"focus", "breadth"}) {
		t.Fatalf("expected undo to restore breadth, got %v", m.tokenStates[1].selected)
	}
	messages := historyMessages(m)
	if len(messages) == 0 || messages[0] != "Tokens undo restored" {
		t.Fatalf("expected history to record token undo, got %v", messages)
	}
	if len(historyKinds(m)) == 0 || historyKinds(m)[0] != historyEventKindTokens {
		t.Fatalf("expected token history kind, got %v", historyKinds(m))
	}
}

func TestTokenPaletteToggle(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	var cmd tea.Cmd

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRight})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDown})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter}) // add breadth inline
	if !reflect.DeepEqual(m.tokenStates[1].selected, []string{"focus", "breadth"}) {
		t.Fatalf("expected inline add to select focus/breadth, got %v", m.tokenStates[1].selected)
	}

	m, cmd = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	if !m.tokenPaletteVisible {
		t.Fatalf("expected token palette to be visible")
	}
	expectedFilter := categorySlug(m.tokenStates[m.tokenCategoryIndex].category) + "="
	if m.tokenPaletteFilter.Value() != expectedFilter {
		t.Fatalf("expected palette filter to reset to %q, got %q", expectedFilter, m.tokenPaletteFilter.Value())
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})   // categories
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})   // options
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDown})  // skip copy action entry
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter}) // toggle focus option off
	if !reflect.DeepEqual(m.tokenStates[1].selected, []string{"breadth"}) {
		t.Fatalf("expected palette toggle to remove focus, got %v", m.tokenStates[1].selected)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlZ})
	if !reflect.DeepEqual(m.tokenStates[1].selected, []string{"focus", "breadth"}) {
		t.Fatalf("expected undo inside palette to restore focus, got %v", m.tokenStates[1].selected)
	}

	m, cmd = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	if cmd != nil {
		t.Fatalf("expected no command when closing palette, got %T", cmd)
	}
	if m.tokenPaletteVisible {
		t.Fatalf("expected token palette to close on Ctrl+P")
	}
}

func TestTokenPaletteApplyUndoFromEmptyTokens(t *testing.T) {
	opts := Options{
		Tokens:          nil,
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	if !m.tokenPaletteVisible {
		t.Fatalf("expected token palette to be visible")
	}

	for _, r := range []rune{'t', 'o', 'd', 'o'} {
		m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{r}})
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter}) // move focus to options
	if m.tokenPaletteFocus != tokenPaletteFocusOptions {
		t.Fatalf("expected palette focus to move to options, got %v", m.tokenPaletteFocus)
	}
	if len(m.tokenPaletteOptions) == 0 {
		t.Fatalf("expected palette options to be populated")
	}

	for m.tokenPaletteOptionIndex < len(m.tokenPaletteOptions) && m.tokenPaletteOptions[m.tokenPaletteOptionIndex] < 0 {
		m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDown})
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter}) // apply selection

	if len(m.tokens) != 1 || m.tokens[0] != "todo" {
		t.Fatalf("expected todo token to be applied, got tokens=%v state=%v options=%v index=%d", m.tokens, m.tokenStates[0].selected, m.tokenPaletteOptions, m.tokenPaletteOptionIndex)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlZ})

	if len(m.tokens) != 0 {
		t.Fatalf("expected undo to restore empty token selection, got %v", m.tokens)
	}
	messages := historyMessages(m)
	if len(messages) == 0 || messages[0] != "Tokens undo restored" {
		t.Fatalf("expected history to record token undo, got %v", messages)
	}
}

func TestInitialFocusBreadcrumbs(t *testing.T) {
	opts := Options{
		Preview:        func(subject string, tokens []string) (string, error) { return subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	view := m.View()
	if !strings.Contains(view, "[SUBJECT]") {
		t.Fatalf("expected breadcrumbs to highlight subject, got view:\n%s", view)
	}
	if !strings.Contains(view, "Summary strip:") {
		t.Fatalf("expected summary strip to render, got view:\n%s", view)
	}
	if !strings.Contains(view, "Destination: clipboard — Ctrl+B copies CLI") {
		t.Fatalf("expected default destination summary, got view:\n%s", view)
	}
	if !strings.Contains(m.statusMessage, "Subject input focused") {
		t.Fatalf("expected status message to indicate subject focus, got %q", m.statusMessage)
	}
}

func TestSummaryStripUpdatesAfterCopy(t *testing.T) {
	var copied string
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(s string) error { copied = s; return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.activePresetName = "starter"
	m.activePresetTokens = []string{"todo"}

	view := m.View()
	if !strings.Contains(view, "Preset: starter") {
		t.Fatalf("expected summary to include preset, got view:\n%s", view)
	}
	if !strings.Contains(view, "Tokens: todo") {
		t.Fatalf("expected summary to include token list, got view:\n%s", view)
	}
	if !strings.Contains(view, "Destination: clipboard — Ctrl+B copies CLI") {
		t.Fatalf("expected default destination summary, got view:\n%s", view)
	}

	m.copyBuildCommandToClipboard()
	if copied == "" {
		t.Fatalf("expected CLI command to be copied")
	}
	view = m.View()
	if !strings.Contains(view, "Destination: clipboard — CLI command copied") {
		t.Fatalf("expected summary to note CLI copy, got view:\n%s", view)
	}
	messages := historyMessages(m)
	if len(messages) == 0 || messages[0] != "Clipboard → CLI command copied" {
		t.Fatalf("expected history to record CLI copy, got %v", messages)
	}

	m.copyPreviewToClipboard()
	view = m.View()
	if !strings.Contains(view, "Destination: clipboard — Preview copied") {
		t.Fatalf("expected summary to note preview copy, got view:\n%s", view)
	}
	messages = historyMessages(m)
	if len(messages) == 0 || messages[0] != "Clipboard → preview copied" {
		t.Fatalf("expected history to record preview copy, got %v", messages)
	}
	if len(messages) < 2 || messages[1] != "Clipboard → CLI command copied" {
		t.Fatalf("expected CLI copy entry to remain in history, got %v", messages)
	}
}

func TestTokenPaletteHistoryToggle(t *testing.T) {
	opts := Options{
		Tokens:          nil,
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	if !m.tokenPaletteVisible {
		t.Fatalf("expected palette to open")
	}

	for _, r := range []rune{'t', 'o', 'd', 'o'} {
		m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{r}})
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if m.tokenPaletteFocus != tokenPaletteFocusOptions {
		t.Fatalf("expected palette focus to move to options, got %v", m.tokenPaletteFocus)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if len(m.paletteHistory) == 0 {
		t.Fatalf("expected palette history to record an entry")
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlH})
	if !m.paletteHistoryVisible {
		t.Fatalf("expected palette history to be visible after Ctrl+H")
	}

	view := m.View()
	if !viewContains(view, "[TOKENS]") {
		t.Fatalf("expected focus breadcrumbs to highlight tokens, got view:\n%s", view)
	}
	if !viewContains(view, "HISTORY (Ctrl+H toggles)") {
		t.Fatalf("expected view to include history header, got view:\n%s", view)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlH})
	if m.paletteHistoryVisible {
		t.Fatalf("expected palette history to hide after second Ctrl+H")
	}
}

func TestSidebarToggleVisibility(t *testing.T) {
	opts := Options{
		Tokens:         []string{"todo"},
		Preview:        func(subject string, tokens []string) (string, error) { return subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
		InitialWidth:   120,
		InitialHeight:  40,
	}
	m := newModel(opts)

	if m.sidebarColumnWidth == 0 {
		t.Fatalf("expected sidebar to be visible initially, got width %d", m.sidebarColumnWidth)
	}

	toggle := tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{''}}
	m, _ = updateModel(t, m, toggle)
	if m.sidebarPreference != sidebarPreferenceHidden {
		t.Fatalf("expected sidebar preference hidden after toggle, got %v", m.sidebarPreference)
	}
	if m.sidebarColumnWidth != 0 {
		t.Fatalf("expected sidebar width 0 after hiding, got %d", m.sidebarColumnWidth)
	}
	view := m.View()
	if strings.Contains(view, "HISTORY (Ctrl+H toggles)") {
		t.Fatalf("expected history section to be hidden when sidebar is hidden, view:\n%s", view)
	}

	m, _ = updateModel(t, m, toggle)
	if m.sidebarPreference != sidebarPreferenceShown {
		t.Fatalf("expected sidebar preference shown after second toggle, got %v", m.sidebarPreference)
	}
	if m.sidebarColumnWidth == 0 {
		t.Fatalf("expected sidebar width to be restored, got %d", m.sidebarColumnWidth)
	}
	restored := m.View()
	if !strings.Contains(restored, "HISTORY (Ctrl+H toggles)") {
		t.Fatalf("expected history section when sidebar is visible, view:\n%s", restored)
	}

	narrow := tea.WindowSizeMsg{Width: 60, Height: 24}
	m, _ = updateModel(t, m, narrow)
	if m.sidebarPreference != sidebarPreferenceShown {
		t.Fatalf("expected sidebar preference to remain shown after resize, got %v", m.sidebarPreference)
	}
	if m.sidebarColumnWidth != 0 {
		t.Fatalf("expected sidebar width 0 when terminal is narrow, got %d", m.sidebarColumnWidth)
	}
	stacked := m.View()
	if !strings.Contains(stacked, "HISTORY (Ctrl+H toggles)") {
		t.Fatalf("expected history section to render in stacked layout, view:\n%s", stacked)
	}
}

func TestCommandHistoryRecordsSuccess(t *testing.T) {
	opts := Options{
		Preview:        func(subject string, tokens []string) (string, error) { return subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	result := commandResult{Command: "printf hi", ExitCode: 0, HasExitCode: true}
	m, _ = updateModel(t, m, commandFinishedMsg{result: result, mode: commandModeSubject})

	messages := historyMessages(m)
	kinds := historyKinds(m)
	if len(messages) == 0 {
		t.Fatalf("expected command history entry to be recorded")
	}
	if len(kinds) == 0 || kinds[0] != historyEventKindCommand {
		t.Fatalf("expected command history kind, got %v", kinds)
	}

	expected := "Command (subject) → \"printf hi\" exit 0"
	if messages[0] != expected {
		t.Fatalf("expected history entry %q, got %q", expected, messages[0])
	}
}

func TestCommandHistoryRecordsError(t *testing.T) {
	opts := Options{
		Preview:        func(subject string, tokens []string) (string, error) { return subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	err := errors.New("boom failure")
	result := commandResult{Command: "printf hi", Err: err}
	m, _ = updateModel(t, m, commandFinishedMsg{result: result, mode: commandModeSubject})

	messages := historyMessages(m)
	kinds := historyKinds(m)
	if len(messages) == 0 {
		t.Fatalf("expected command history entry to be recorded")
	}
	if len(kinds) == 0 || kinds[0] != historyEventKindCommand {
		t.Fatalf("expected command history kind, got %v", kinds)
	}

	if !strings.Contains(messages[0], "error: boom failure") {
		t.Fatalf("expected error status in history entry, got %q", messages[0])
	}
}

func TestCommandHistoryPreviewScope(t *testing.T) {
	opts := Options{
		Preview:        func(subject string, tokens []string) (string, error) { return subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	result := commandResult{Command: "printf hi", ExitCode: 0, HasExitCode: true, UsedPreview: true}
	m, _ = updateModel(t, m, commandFinishedMsg{result: result, mode: commandModePreview})

	messages := historyMessages(m)
	kinds := historyKinds(m)
	if len(messages) == 0 {
		t.Fatalf("expected command history entry to be recorded")
	}
	if len(kinds) == 0 || kinds[0] != historyEventKindCommand {
		t.Fatalf("expected command history kind, got %v", kinds)
	}

	expected := "Command (preview) → \"printf hi\" exit 0"
	if messages[0] != expected {
		t.Fatalf("expected preview history entry %q, got %q", expected, messages[0])
	}
}

func TestFormatHistoryEventIncludesMetadata(t *testing.T) {
	opts := Options{
		Preview:        func(subject string, tokens []string) (string, error) { return subject, nil },
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	fixed := time.Date(2026, time.January, 12, 15, 4, 0, 0, time.UTC)
	m.now = func() time.Time { return fixed }

	m.recordPaletteHistory(historyEventKindClipboard, "Clipboard → preview copied")

	if len(m.paletteHistory) != 1 {
		t.Fatalf("expected one history event, got %d", len(m.paletteHistory))
	}
	event := m.paletteHistory[0]
	if !event.Timestamp.Equal(fixed) {
		t.Fatalf("expected timestamp %v, got %v", fixed, event.Timestamp)
	}

	formatted := formatHistoryEvent(event)
	expected := "[15:04] 📋 Clipboard · Clipboard → preview copied"
	if formatted != expected {
		t.Fatalf("expected formatted history %q, got %q", expected, formatted)
	}
}

func TestTokenPaletteSummaryCondensedWhenVisible(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	// Focus tokens and open palette
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	if !m.tokenPaletteVisible {
		t.Fatalf("expected palette to be visible")
	}

	view := m.View()
	if !viewContains(view, "[TOKENS]") {
		t.Fatalf("expected focus breadcrumbs to highlight tokens, got view:\n%s", view)
	}
	if !viewContains(view, "Token palette (Esc closes") {
		t.Fatalf("expected palette section to be rendered, got view:\n%s", view)
	}
	filterLine := fmt.Sprintf("Filter: %s=", categorySlug(m.tokenStates[m.tokenCategoryIndex].category))
	if !viewContains(view, filterLine) {
		t.Fatalf("expected palette grammar composer to render, got view:\n%s", view)
	}
	if viewContains(view, "Tokens (Tab focuses tokens · Ctrl+P opens palette):") {
		t.Fatalf("expected condensed summary to replace default token header, got view:\n%s", view)
	}
}

func TestTokenPaletteEnterMovesFocusToOptions(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	if m.tokenPaletteFocus != tokenPaletteFocusFilter {
		t.Fatalf("expected palette focus to start on filter, got %v", m.tokenPaletteFocus)
	}
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if m.tokenPaletteFocus != tokenPaletteFocusOptions {
		t.Fatalf("expected Enter to move focus to options, got %v", m.tokenPaletteFocus)
	}
	if len(m.tokenPaletteOptions) == 0 {
		t.Fatalf("expected palette options to be populated")
	}
	if m.tokenPaletteOptionIndex < 0 || m.tokenPaletteOptionIndex >= len(m.tokenPaletteOptions) {
		t.Fatalf("expected palette option index to be within range, got %d", m.tokenPaletteOptionIndex)
	}
}

func TestCtrlRuneOpensPalette(t *testing.T) {

	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	combined := tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'\t', rune(16)}}
	m, _ = updateModel(t, m, combined)
	if !m.tokenPaletteVisible {
		t.Fatalf("expected palette to be visible after ctrl rune event")
	}
	if value := m.subject.Value(); value != "" {
		t.Fatalf("expected subject to remain empty, got %q", value)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	if m.tokenPaletteVisible {
		t.Fatalf("expected palette to close on Ctrl+P toggle")
	}

	single := tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{rune(16)}}
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, single)
	if !m.tokenPaletteVisible {
		t.Fatalf("expected palette to open from single ctrl rune")
	}
	if value := m.subject.Value(); value != "" {
		t.Fatalf("expected subject to remain empty after single ctrl rune, got %q", value)
	}

	m = newModel(opts)
	escaped := tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'\\', 't', '\\', 'u', '0', '0', '1', '0'}}
	m, _ = updateModel(t, m, escaped)
	if !m.tokenPaletteVisible {
		t.Fatalf("expected palette to open from escaped ctrl rune sequence")
	}
	if value := m.subject.Value(); value != "" {
		t.Fatalf("expected subject to remain empty after escaped ctrl rune sequence, got %q", value)
	}
}

func TestPaletteRemainsVisibleWithinWindowHeight(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	window := tea.WindowSizeMsg{Width: 80, Height: 20}
	m, _ = updateModel(t, m, window)
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	if !m.tokenPaletteVisible {
		t.Fatalf("expected palette to be visible after Ctrl+P")
	}

	view := m.View()
	if !viewContains(view, "Token palette (Esc closes") {
		t.Fatalf("expected token palette block to render within the terminal window, got:\n%s", view)
	}
	if !viewContains(view, "Filter:") {
		t.Fatalf("expected palette filter prompt to render within the window, got:\n%s", view)
	}
}

func TestTokenPaletteResetToPreset(t *testing.T) {

	opts := Options{
		Tokens:          []string{"todo", "breadth"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	(&m).setActivePreset("demo", []string{"todo", "focus"})

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRight})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab}) // categories
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab}) // options

	if len(m.tokenPaletteOptions) < 2 {
		t.Fatalf("expected palette to include action and reset entries, got %v", m.tokenPaletteOptions)
	}
	if m.tokenPaletteOptions[0] != tokenPaletteCopyCommandOption {
		t.Fatalf("expected first palette entry to be copy command action, got %d", m.tokenPaletteOptions[0])
	}
	if m.tokenPaletteOptions[1] != tokenPaletteResetOption {
		t.Fatalf("expected reset option to appear when preset diverges")
	}
	if m.tokenPaletteOptionIndex < 0 || m.tokenPaletteOptionIndex >= len(m.tokenPaletteOptions) {
		t.Fatalf("palette option index out of range: %d", m.tokenPaletteOptionIndex)
	}
	entryBefore := m.tokenPaletteOptions[m.tokenPaletteOptionIndex]
	if entryBefore != tokenPaletteCopyCommandOption {
		t.Fatalf("expected palette focus to begin on copy action, got entry %d (index %d)", entryBefore, m.tokenPaletteOptionIndex)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDown})
	if m.tokenPaletteOptions[m.tokenPaletteOptionIndex] != tokenPaletteResetOption {
		t.Fatalf("expected palette focus to land on reset option after moving down, got entry %d", m.tokenPaletteOptions[m.tokenPaletteOptionIndex])
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if !reflect.DeepEqual(m.tokenStates[1].selected, []string{"focus"}) {
		t.Fatalf("expected reset to preset to restore focus, got %v (status: %q)", m.tokenStates[1].selected, m.statusMessage)
	}
	if !reflect.DeepEqual(m.tokens, []string{"todo", "focus"}) {
		t.Fatalf("expected tokens to match preset after reset, got %v", m.tokens)
	}
}

func TestTokenPaletteResetRenderingHasNoSideEffects(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "breadth"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	(&m).setActivePreset("demo", []string{"todo", "focus"})

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRight})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})

	if len(m.tokenPaletteOptions) < 2 || m.tokenPaletteOptions[1] != tokenPaletteResetOption {
		t.Fatalf("expected reset option to appear when preset diverges")
	}

	beforeSelection := append([]string(nil), m.tokenStates[1].selected...)
	beforeTokens := append([]string(nil), m.tokens...)

	view := m.View()
	if !strings.Contains(view, "[reset] Reset to preset") {
		t.Fatalf("expected view to mention reset option, got:\n%s", view)
	}
	if !reflect.DeepEqual(m.tokenStates[1].selected, beforeSelection) {
		t.Fatalf("expected rendering not to change selection, got %v", m.tokenStates[1].selected)
	}
	if !reflect.DeepEqual(m.tokens, beforeTokens) {
		t.Fatalf("expected rendering not to change tokens, got %v", m.tokens)
	}
}

func TestTokenPaletteKeepsIndexAfterOptionUpdate(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})  // filter -> categories
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})  // categories -> options
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDown}) // highlight scope option

	if len(m.tokenPaletteOptions) == 0 {
		t.Fatalf("expected palette options to be present")
	}
	beforeEntry := m.tokenPaletteOptions[m.tokenPaletteOptionIndex]

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter}) // toggle selection

	if len(m.tokenPaletteOptions) == 0 {
		t.Fatalf("expected palette options to remain after toggle")
	}
	afterEntry := m.tokenPaletteOptions[m.tokenPaletteOptionIndex]
	if beforeEntry != afterEntry {
		t.Fatalf("expected palette to keep focus on same entry, got %d then %d", beforeEntry, afterEntry)
	}
}

func TestTokenPaletteFilterNoMatchesWithoutPreset(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'x'}})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'z'}})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'z'}})

	if m.tokenPaletteOptionIndex != -1 {
		t.Fatalf("expected palette option index to be -1, got %d", m.tokenPaletteOptionIndex)
	}

	view := m.View()
	normalized := normalizeWhitespace(view)
	if strings.Contains(normalized, "[reset] Reset to preset") {
		t.Fatalf("expected no reset option when no preset is active, got:\n%s", view)
	}
	if !strings.Contains(normalized, "no options match") {
		t.Fatalf("expected view to mention missing options, got:\n%s", view)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlW})
	expectedGrammarFilter := categorySlug(m.tokenStates[m.tokenCategoryIndex].category) + "="
	if m.tokenPaletteFilter.Value() != expectedGrammarFilter {
		t.Fatalf("expected filter to reset to %q, got %q", expectedGrammarFilter, m.tokenPaletteFilter.Value())
	}
	if m.tokenPaletteOptionIndex < 0 {
		t.Fatalf("expected palette option index to reset, got %d", m.tokenPaletteOptionIndex)
	}
	t.Logf("status after clear: %q", m.statusMessage)
	if !strings.Contains(m.statusMessage, "Grammar composer reset") {
		t.Fatalf("expected status to mention grammar composer reset, got %q", m.statusMessage)
	}
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected cleared-status to retain copy command hint, got %q", m.statusMessage)
	}

	view = m.View()
	normalized = normalizeWhitespace(view)
	if strings.Contains(normalized, "no options match") {
		t.Fatalf("expected options to repopulate after clearing filter, got:\n%s", view)
	}
}

func TestHelpOverlayMentionsCopyCommandPaletteHint(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	// Toggle help overlay
	view := m.View()
	if strings.Contains(view, "copy command") {
		t.Fatalf("expected help overlay to be hidden in initial view")
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'?'}})
	view = m.View()

	if !strings.Contains(view, "Type category=value") {
		t.Fatalf("expected help overlay to instruct category=value palette input, got:\n%s", view)
	}
	if !strings.Contains(view, "Apply staged edits") {
		t.Fatalf("expected shortcut reference to mention applying staged edits, got:\n%s", view)
	}
	if !strings.Contains(view, "Clear palette filter") {
		t.Fatalf("expected shortcut reference to mention clearing the palette filter, got:\n%s", view)
	}
}

func TestResultSummaryNoCommand(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	view := m.View()
	if !strings.Contains(view, "Result summary:") {
		t.Fatalf("expected result summary heading in view, got:\n%s", view)
	}
	if !strings.Contains(view, "∅ No command executed yet") {
		t.Fatalf("expected default result summary, got:\n%s", view)
	}
}

func TestResultSummaryRunning(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.commandRunning = true
	m.runningCommand = "echo hello"
	m.runningMode = commandModePreview
	m.allowedEnv = []string{"FOO"}
	view := m.View()
	if !strings.Contains(view, "Running \"echo hello\"") {
		t.Fatalf("expected running summary with command, got:\n%s", view)
	}
	if !strings.Contains(view, "input preview") {
		t.Fatalf("expected running summary to note preview input, got:\n%s", view)
	}
	if !strings.Contains(view, "env FOO") {
		t.Fatalf("expected running summary to list environment, got:\n%s", view)
	}
}

func TestResultSummaryLastResultSuccess(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.lastResult = commandResult{
		Command:     "echo hello",
		Stdout:      "hello\n",
		UsedPreview: false,
		EnvVars:     []string{},
		ExitCode:    0,
		HasExitCode: true,
	}
	view := m.View()
	if !strings.Contains(view, "✔ Command \"echo hello\" completed") {
		t.Fatalf("expected success summary, got:\n%s", view)
	}
	if !strings.Contains(view, "exit 0") {
		t.Fatalf("expected success summary to include exit code, got:\n%s", view)
	}
}

func TestResultSummaryLastResultFailure(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.lastResult = commandResult{
		Command:     "echo boom",
		UsedPreview: true,
		EnvVars:     []string{"FOO"},
		Err:         errors.New("boom"),
		ExitCode:    1,
		HasExitCode: true,
	}
	view := m.View()
	if !viewContains(view, "✖ Command \"echo boom\" failed: boom") {
		t.Fatalf("expected failure summary to include command and failure, got view:\n%s", view)
	}
	summaryLine := m.renderResultSummaryLine()
	if !strings.Contains(summaryLine, "input preview") {
		t.Fatalf("expected failure summary line to reference preview input, got %q", summaryLine)
	}
	if !strings.Contains(summaryLine, "env FOO") {
		t.Fatalf("expected failure summary line to include env list, got %q", summaryLine)
	}

	if !strings.Contains(view, "exit 1") {
		t.Fatalf("expected failure summary to include exit code, got:\n%s", view)
	}
	if !strings.Contains(view, "input preview") {
		t.Fatalf("expected failure summary to reference preview input, got:\n%s", view)
	}
	if !strings.Contains(view, "env FOO") {
		t.Fatalf("expected failure summary to list env vars, got:\n%s", view)
	}
}

func TestPaletteOpenStatusMentionsCopyCommand(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})

	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected palette status to mention copy command hint, got %q", m.statusMessage)
	}
	if !strings.Contains(m.statusMessage, "Enter") {
		t.Fatalf("expected palette status to mention Enter key, got %q", m.statusMessage)
	}
	if !strings.Contains(m.statusMessage, "Ctrl+W") {
		t.Fatalf("expected palette status to mention Ctrl+W clear hint, got %q", m.statusMessage)
	}
}

func TestPaletteClearWhenEmptyRetainsCopyHint(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	applyKey := func(msg tea.KeyMsg) {
		var cmd tea.Cmd
		m, cmd = updateModel(t, m, msg)
		if cmd != nil {
			if follow := cmd(); follow != nil {
				m, _ = updateModel(t, m, follow)
			}
		}
	}

	applyKey(tea.KeyMsg{Type: tea.KeyCtrlP})
	applyKey(tea.KeyMsg{Type: tea.KeyCtrlW})

	if !strings.Contains(m.statusMessage, "Grammar composer reset") {
		t.Fatalf("expected status to mention grammar composer reset, got %q", m.statusMessage)
	}
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected empty-filter status to retain copy command hint, got %q", m.statusMessage)
	}
}

func TestPaletteOptionsNoMatchesStillHintsCopyCommand(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	applyKey := func(msg tea.KeyMsg) {
		var cmd tea.Cmd
		m, cmd = updateModel(t, m, msg)
		if cmd != nil {
			if follow := cmd(); follow != nil {
				m, _ = updateModel(t, m, follow)
			}
		}
	}

	applyKey(tea.KeyMsg{Type: tea.KeyCtrlP})
	applyKey(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'x'}})
	applyKey(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'z'}})
	applyKey(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'z'}})
	applyKey(tea.KeyMsg{Type: tea.KeyTab}) // categories focus
	applyKey(tea.KeyMsg{Type: tea.KeyTab}) // options focus

	if m.tokenPaletteFocus != tokenPaletteFocusOptions {
		t.Fatalf("expected options focus, got %v", m.tokenPaletteFocus)
	}
	if len(m.tokenPaletteOptions) != 0 {
		t.Fatalf("expected no palette options, got %v", m.tokenPaletteOptions)
	}

	status := m.statusMessage
	if !strings.Contains(status, "No palette entries match the filter") {
		t.Fatalf("expected status to mention no matching entries, got %q", status)
	}
	if !strings.Contains(status, "copy command") {
		t.Fatalf("expected no-match status to hint copy command, got %q", status)
	}
}

func TestTokenControlsFocusMentionsCopyHint(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	applyKey := func(msg tea.KeyMsg) {
		var cmd tea.Cmd
		m, cmd = updateModel(t, m, msg)
		if cmd != nil {
			if follow := cmd(); follow != nil {
				m, _ = updateModel(t, m, follow)
			}
		}
	}

	applyKey(tea.KeyMsg{Type: tea.KeyTab})

	if m.focus != focusTokens {
		t.Fatalf("expected focusTokens after tab, got %v", m.focus)
	}
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected token controls status to mention copy hint, got %q", m.statusMessage)
	}
}

func TestPaletteCloseStatusMentionsCopyHint(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	applyKey := func(msg tea.KeyMsg) {
		var cmd tea.Cmd
		m, cmd = updateModel(t, m, msg)
		if cmd != nil {
			if follow := cmd(); follow != nil {
				m, _ = updateModel(t, m, follow)
			}
		}
	}

	applyKey(tea.KeyMsg{Type: tea.KeyCtrlP})
	if !m.tokenPaletteVisible {
		t.Fatalf("expected palette to be visible after Ctrl+P")
	}

	applyKey(tea.KeyMsg{Type: tea.KeyCtrlP})
	if m.tokenPaletteVisible {
		t.Fatalf("expected palette to close after second Ctrl+P")
	}
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected palette close status to mention copy hint, got %q", m.statusMessage)
	}
}

func TestHelpOverlayCloseRestoresTokenCopyHint(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	applyKey := func(msg tea.KeyMsg) {
		var cmd tea.Cmd
		m, cmd = updateModel(t, m, msg)
		if cmd != nil {
			if follow := cmd(); follow != nil {
				m, _ = updateModel(t, m, follow)
			}
		}
	}

	applyKey(tea.KeyMsg{Type: tea.KeyTab})
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected token controls status to mention copy hint, got %q", m.statusMessage)
	}
	statusBefore := m.statusMessage

	applyKey(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'?'}})
	if strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected help overlay to replace copy hint, got %q", m.statusMessage)
	}

	applyKey(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'?'}})
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected help overlay close to restore copy hint, got %q", m.statusMessage)
	}
	if m.statusMessage != statusBefore {
		t.Fatalf("expected status to restore previous message, got %q vs %q", m.statusMessage, statusBefore)
	}
}

func TestHelpOverlayCloseRestoresPaletteCopyHint(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	applyKey := func(msg tea.KeyMsg) {
		var cmd tea.Cmd
		m, cmd = updateModel(t, m, msg)
		if cmd != nil {
			if follow := cmd(); follow != nil {
				m, _ = updateModel(t, m, follow)
			}
		}
	}

	applyKey(tea.KeyMsg{Type: tea.KeyCtrlP})
	if !m.tokenPaletteVisible {
		t.Fatalf("expected palette to be visible after Ctrl+P")
	}

	applyKey(tea.KeyMsg{Type: tea.KeyCtrlP})
	if m.tokenPaletteVisible {
		t.Fatalf("expected palette to close after second Ctrl+P")
	}
	statusBefore := m.statusMessage

	applyKey(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'?'}})
	if strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected help overlay to replace copy hint, got %q", m.statusMessage)
	}

	applyKey(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'?'}})
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected closing help overlay to restore copy hint, got %q", m.statusMessage)
	}
	if m.statusMessage != statusBefore {
		t.Fatalf("expected palette status to restore previous message, got %q vs %q", m.statusMessage, statusBefore)
	}
}

func TestRunningCommandStatusIncludesCopyHint(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(ctx context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			select {
			case <-ctx.Done():
				return "", "", ctx.Err()
			case <-time.After(10 * time.Millisecond):
				return "stdout", "stderr", nil
			}
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.command.SetValue("echo test")

	cmd := (&m).executeSubjectCommand()
	if cmd == nil {
		t.Fatalf("expected executeSubjectCommand to return a tea.Cmd")
	}
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected running-status to include copy hint, got %q", m.statusMessage)
	}

	msg := cmd()
	m, next := updateModel(t, m, msg)
	if next != nil {
		t.Fatalf("unexpected follow-up command: %T", next)
	}
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected completion status to include copy hint, got %q", m.statusMessage)
	}
	if !strings.Contains(strings.ToLower(m.statusMessage), "replace subject with command stdout") {
		t.Fatalf("expected subject replacement prompt, got %q", m.statusMessage)
	}
	if m.pendingSubject == nil {
		t.Fatalf("expected pending subject replacement after command completion")
	}
	if got := m.subject.Value(); got != "" {
		t.Fatalf("expected subject to remain unchanged until confirmation, got %q", got)
	}
}

func TestRunningPreviewCommandStatusIncludesCopyHint(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(ctx context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			select {
			case <-ctx.Done():
				return "", "", ctx.Err()
			case <-time.After(10 * time.Millisecond):
				return "stdout", "stderr", nil
			}
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)
	m.command.SetValue("echo preview")
	m.preview = "preview text"

	cmd := (&m).executePreviewCommand()
	if cmd == nil {
		t.Fatalf("expected executePreviewCommand to return a tea.Cmd")
	}
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected running-status to include copy hint, got %q", m.statusMessage)
	}

	msg := cmd()
	m, next := updateModel(t, m, msg)
	if next != nil {
		t.Fatalf("unexpected follow-up command: %T", next)
	}
	if !strings.Contains(m.statusMessage, "copy command") {
		t.Fatalf("expected completion status to include copy hint, got %q", m.statusMessage)
	}
	if !strings.Contains(m.statusMessage, "Command completed") {
		t.Fatalf("expected completion message, got %q", m.statusMessage)
	}
}

func TestPaletteCopyActionStatusHint(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})

	if !strings.Contains(m.statusMessage, "Enter to copy") && !strings.Contains(m.statusMessage, "Enter copies") {
		t.Fatalf("expected palette status to mention Enter copy action, got %q", m.statusMessage)
	}
	if !strings.Contains(m.statusMessage, "Ctrl+W") {
		t.Fatalf("expected palette status to remind about Ctrl+W, got %q", m.statusMessage)
	}
	if !strings.Contains(m.statusMessage, "Esc closes") {
		t.Fatalf("expected palette status to mention Esc closure, got %q", m.statusMessage)
	}
}

func TestPaletteCategoryStatusIncludesLabel(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})

	status := m.statusMessage
	if !strings.Contains(status, "Static Prompt") {
		t.Fatalf("expected status to include current category label, got %q", status)
	}
	if !strings.Contains(status, "Up/Down") {
		t.Fatalf("expected status to mention category navigation, got %q", status)
	}
	if !strings.Contains(status, "copy command") {
		t.Fatalf("expected category status to retain copy hint, got %q", status)
	}
}

func TestPaletteFilterStatusIncludesValue(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	applyKey := func(msg tea.KeyMsg) {
		var cmd tea.Cmd
		m, cmd = updateModel(t, m, msg)
		if cmd != nil {
			if follow := cmd(); follow != nil {
				m, _ = updateModel(t, m, follow)
			}
		}
	}

	applyKey(tea.KeyMsg{Type: tea.KeyCtrlP})
	applyKey(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'s'}})
	applyKey(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{'c'}})

	status := m.statusMessage

	expectedFragment := fmt.Sprintf("%s=sc", categorySlug(m.tokenStates[m.tokenCategoryIndex].category))
	if !strings.Contains(status, expectedFragment) {
		t.Fatalf("expected status to include current filter text %q, got %q", expectedFragment, status)
	}
	if !strings.Contains(status, "Ctrl+W") {
		t.Fatalf("expected status to remind about Ctrl+W, got %q", status)
	}
	if !strings.Contains(status, "copy command") {
		t.Fatalf("expected status to remind about copy command shortcut, got %q", status)
	}
	if !strings.Contains(status, "Type \"copy command\"") {
		t.Fatalf("expected status to mention typing \"copy command\" for the copy action, got %q", status)
	}
}

func TestPaletteOptionStatusNamesToken(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})  // focus categories
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDown}) // move to Scope category
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})  // focus options
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDown}) // skip copy action to first token option

	status := m.statusMessage

	if !strings.Contains(status, "Scope") {
		t.Fatalf("expected status to cite category, got %q", status)
	}
	if !strings.Contains(status, "focus") {
		t.Fatalf("expected status to include token slug, got %q", status)
	}
	if !strings.Contains(status, "toggle") {
		t.Fatalf("expected status to mention toggling, got %q", status)
	}
}

func TestTokenPaletteCopyCommandAction(t *testing.T) {
	var copied string
	subject := "Palette subject"
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview: func(s string, tokens []string) (string, error) {
			return "preview:" + s + strings.Join(tokens, ","), nil
		},
		ClipboardRead: func() (string, error) { return "", nil },
		ClipboardWrite: func(text string) error {
			copied = text
			return nil
		},
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}

	m := newModel(opts)
	m.subject.SetValue(subject)
	(&m).refreshPreview()

	m, cmd := updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlP})
	if cmd == nil {
		t.Fatalf("expected palette open command")
	}
	if !m.tokenPaletteVisible {
		t.Fatalf("expected token palette to be visible")
	}

	m, cmd = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	if cmd != nil {
		t.Fatalf("unexpected command when tabbing to categories: %T", cmd)
	}
	m, cmd = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})
	if cmd != nil {
		t.Fatalf("unexpected command when tabbing to options: %T", cmd)
	}
	if m.tokenPaletteFocus != tokenPaletteFocusOptions {
		t.Fatalf("expected palette focus options, got %v", m.tokenPaletteFocus)
	}

	view := m.View()
	normalized := normalizeWhitespace(view)
	if !strings.Contains(normalized, "Token palette (Esc closes") {
		t.Fatalf("expected palette view, got view:\n%s", view)
	}
	if !strings.Contains(normalized, "[action] Copy bar") {
		t.Fatalf("expected palette to include copy command action, normalized=%q original=\n%s", normalized, view)
	}

	if copied != "" {
		t.Fatalf("expected clipboard to be empty before selecting action, got %q", copied)
	}

	m, cmd = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if cmd != nil {
		t.Fatalf("unexpected command when selecting palette action: %T", cmd)
	}
	if copied == "" {
		t.Fatalf("expected copy action to write to clipboard")
	}
	expected := "bar build todo focus --prompt 'Palette subject'"
	if copied != expected {
		t.Fatalf("expected copied command %q, got %q", expected, copied)
	}
	if !strings.Contains(m.statusMessage, "Copied bar build command") {
		t.Fatalf("expected status message to confirm copy, got %q", m.statusMessage)
	}
	if m.tokenPaletteVisible {
		t.Fatalf("expected palette to close after copy action")
	}
	if m.focus != focusSubject {
		t.Fatalf("expected focus to return to subject, got %v", m.focus)
	}
	if !m.subject.Focused() {
		t.Fatalf("expected subject input to be focused after copy action")
	}
}

func TestTokenSummaryNoHighlightWhenSubjectFocused(t *testing.T) {
	opts := Options{
		Tokens:          []string{"todo", "focus"},
		TokenCategories: defaultTokenCategories(),
		Preview:         func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
		ClipboardRead:   func() (string, error) { return "", nil },
		ClipboardWrite:  func(string) error { return nil },
		RunCommand: func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
	}
	m := newModel(opts)

	view := m.View()
	if strings.Contains(view, "» [ ") {
		t.Fatalf("expected no highlighted token when subject is focused, got:\n%s", view)
	}
}

func TestPresetPaneLoadPreset(t *testing.T) {
	presets := []PresetSummary{
		{Name: "daily", SavedAt: time.Unix(100, 0), Static: "todo", Voice: "coach", Audience: "team", Tone: "warm"},
		{Name: "weekly", SavedAt: time.Unix(200, 0), Static: "plan", Voice: "mentor", Audience: "group", Tone: "calm"},
	}
	loadCalls := make(map[string]int)
	opts := Options{
		Tokens: []string{"todo"},
		Preview: func(subject string, tokens []string) (string, error) {
			return strings.Join(tokens, ",") + ":" + subject, nil
		},
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
		ListPresets: func() ([]PresetSummary, error) {
			out := make([]PresetSummary, len(presets))
			copy(out, presets)
			return out, nil
		},
		LoadPreset: func(name string) (PresetDetails, error) {
			loadCalls[name]++
			switch name {
			case "daily":
				return PresetDetails{Name: "daily", Tokens: []string{"daily", "focus"}, SavedAt: presets[0].SavedAt}, nil
			case "weekly":
				return PresetDetails{Name: "weekly", Tokens: []string{"weekly", "scope"}, SavedAt: presets[1].SavedAt}, nil
			default:
				return PresetDetails{}, fmt.Errorf("unknown preset %s", name)
			}
		},
		SavePreset: func(name string, description string, tokens []string) (PresetDetails, error) {
			return PresetDetails{}, fmt.Errorf("unexpected save for %s", name)
		},
		DeletePreset: func(string) error { return nil },
	}

	m := newModel(opts)
	m, cmd := updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlS})
	if cmd != nil {
		t.Fatalf("unexpected command opening pane: %T", cmd)
	}
	if !m.presetPaneVisible {
		t.Fatalf("expected preset pane to be visible")
	}

	m, cmd = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if cmd != nil {
		t.Fatalf("unexpected command when applying preset: %T", cmd)
	}
	if loadCalls["daily"] != 1 {
		t.Fatalf("expected daily preset to be loaded once, got %v", loadCalls)
	}
	if m.activePresetName != "daily" {
		t.Fatalf("expected active preset daily, got %q", m.activePresetName)
	}
	if !tokensEqual(m.tokens, []string{"daily", "focus"}) {
		t.Fatalf("expected tokens updated to preset values, got %v", m.tokens)
	}
	if m.tokensDiverged() {
		t.Fatalf("expected no divergence immediately after loading preset")
	}
	view := m.View()
	if !strings.Contains(view, "Preset: daily") {
		t.Fatalf("expected view to show active preset, got:\n%s", view)
	}
	if !strings.Contains(view, "Preset pane") {
		t.Fatalf("expected view to include preset pane, got:\n%s", view)
	}
}

func TestPresetPaneSavePreset(t *testing.T) {
	presets := []PresetSummary{}
	savedNames := []string{}
	opts := Options{
		Tokens: []string{"todo"},
		Preview: func(subject string, tokens []string) (string, error) {
			return strings.Join(tokens, ",") + ":" + subject, nil
		},
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
		ListPresets: func() ([]PresetSummary, error) {
			out := make([]PresetSummary, len(presets))
			copy(out, presets)
			return out, nil
		},
		LoadPreset: func(name string) (PresetDetails, error) {
			for _, p := range presets {
				if p.Name == name {
					return PresetDetails{Name: name, Tokens: []string{name, "focus"}, SavedAt: p.SavedAt}, nil
				}
			}
			return PresetDetails{}, fmt.Errorf("unknown preset %s", name)
		},
		SavePreset: func(name string, description string, tokens []string) (PresetDetails, error) {
			savedNames = append(savedNames, name)
			savedAt := time.Unix(int64(len(savedNames)), 0)
			presets = append(presets, PresetSummary{Name: name, SavedAt: savedAt})
			return PresetDetails{Name: name, Tokens: append([]string(nil), tokens...), SavedAt: savedAt}, nil
		},
		DeletePreset: func(string) error { return nil },
	}

	m := newModel(opts)
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlS})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlN})
	if m.presetMode != presetModeSaving {
		t.Fatalf("expected preset save mode, got %v", m.presetMode)
	}
	m.presetNameInput.SetValue("daily")
	m.presetDescriptionInput.SetValue("morning plan")

	m, cmd := updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if cmd != nil {
		t.Fatalf("unexpected command when saving preset: %T", cmd)
	}
	if len(savedNames) != 1 || savedNames[0] != "daily" {
		t.Fatalf("expected preset save to be invoked, got %v", savedNames)
	}
	if m.activePresetName != "daily" {
		t.Fatalf("expected active preset to update, got %q", m.activePresetName)
	}
	if m.presetMode != presetModeList {
		t.Fatalf("expected preset pane to return to list mode, got %v", m.presetMode)
	}
	if len(m.presetSummaries) != 1 {
		t.Fatalf("expected preset summaries to include saved preset, got %v", m.presetSummaries)
	}
	if !strings.Contains(strings.ToLower(m.statusMessage), "saved") {
		t.Fatalf("expected status message to mention save, got %q", m.statusMessage)
	}
}

func TestPresetPaneDeleteAndUndo(t *testing.T) {
	presets := []PresetSummary{{Name: "daily", SavedAt: time.Unix(10, 0)}}
	opts := Options{
		Tokens: []string{"todo"},
		Preview: func(subject string, tokens []string) (string, error) {
			return strings.Join(tokens, ",") + ":" + subject, nil
		},
		ClipboardRead:  func() (string, error) { return "", nil },
		ClipboardWrite: func(string) error { return nil },
		RunCommand: func(_ context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			return "", "", nil
		},
		CommandTimeout: time.Second,
		ListPresets: func() ([]PresetSummary, error) {
			out := make([]PresetSummary, len(presets))
			copy(out, presets)
			return out, nil
		},
		LoadPreset: func(name string) (PresetDetails, error) {
			return PresetDetails{Name: name, Tokens: []string{name, "focus"}, SavedAt: time.Unix(10, 0)}, nil
		},
		SavePreset: func(name string, description string, tokens []string) (PresetDetails, error) {
			presets = append(presets, PresetSummary{Name: name, SavedAt: time.Unix(20, 0)})
			return PresetDetails{Name: name, Tokens: append([]string(nil), tokens...), SavedAt: time.Unix(20, 0)}, nil
		},
		DeletePreset: func(name string) error {
			for i, p := range presets {
				if p.Name == name {
					presets = append(presets[:i], presets[i+1:]...)
					return nil
				}
			}
			return fmt.Errorf("preset %s not found", name)
		},
	}

	m := newModel(opts)
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlS})
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if m.activePresetName != "daily" {
		t.Fatalf("expected daily to be active after loading, got %q", m.activePresetName)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyDelete})
	if m.presetMode != presetModeConfirmDelete {
		t.Fatalf("expected confirm delete mode, got %v", m.presetMode)
	}
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if len(presets) != 0 {
		t.Fatalf("expected preset to be removed, got %v", presets)
	}
	if m.activePresetName != "" {
		t.Fatalf("expected active preset cleared, got %q", m.activePresetName)
	}
	if m.lastDeletedPreset == nil {
		t.Fatalf("expected lastDeletedPreset to be recorded")
	}
	if !strings.Contains(strings.ToLower(m.statusMessage), "deleted") {
		t.Fatalf("expected status message to mention deletion, got %q", m.statusMessage)
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyCtrlZ})
	if len(presets) != 1 {
		t.Fatalf("expected preset to be restored, got %v", presets)
	}
	if m.lastDeletedPreset != nil {
		t.Fatalf("expected lastDeletedPreset to be cleared after undo")
	}
	if !strings.Contains(strings.ToLower(m.statusMessage), "restored") {
		t.Fatalf("expected status message to mention restore, got %q", m.statusMessage)
	}
}
