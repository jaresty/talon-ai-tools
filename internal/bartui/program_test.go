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
	if got := m.subject.Value(); got != "command stdout" {
		t.Fatalf("expected subject replaced with stdout, got %q", got)
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
		Preview:        func(subject string, tokens []string) (string, error) { return "preview:" + subject, nil },
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
		t.Fatalf("unexpected command when toggling help: %T", cmd)
	}
	if strings.Contains(m.View(), "Help overlay (press ? to close)") {
		t.Fatalf("expected help overlay to be hidden after second toggle")
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
	if m.tokenPaletteFilter.Value() != "" {
		t.Fatalf("expected palette filter to reset, got %q", m.tokenPaletteFilter.Value())
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})   // categories
	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyTab})   // options
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

	if len(m.tokenPaletteOptions) == 0 || m.tokenPaletteOptions[0] != tokenPaletteResetOption {
		t.Fatalf("expected reset option to appear when preset diverges")
	}

	m, _ = updateModel(t, m, tea.KeyMsg{Type: tea.KeyEnter})
	if !reflect.DeepEqual(m.tokenStates[1].selected, []string{"focus"}) {
		t.Fatalf("expected reset to preset to restore focus, got %v", m.tokenStates[1].selected)
	}
	if !reflect.DeepEqual(m.tokens, []string{"todo", "focus"}) {
		t.Fatalf("expected tokens to match preset after reset, got %v", m.tokens)
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
