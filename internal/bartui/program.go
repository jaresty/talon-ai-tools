package bartui

import (
	"context"
	"errors"
	"fmt"
	"io"
	"sort"
	"strings"
	"time"

	textinput "github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
)

// PreviewFunc produces the preview text for the current subject.
type PreviewFunc func(subject string) (string, error)

// ClipboardReadFunc reads text from the clipboard.
type ClipboardReadFunc func() (string, error)

// ClipboardWriteFunc writes text to the clipboard.
type ClipboardWriteFunc func(string) error

// RunCommandFunc executes the provided shell command. The stdin parameter contains
// the input to provide on the command's standard input. The returned stdout and
// stderr values are rendered in the result pane regardless of the exit status.
type RunCommandFunc func(ctx context.Context, command string, stdin string, env map[string]string) (stdout string, stderr string, err error)

// Options configure the Bubble Tea prompt editor program.
type Options struct {
	Tokens         []string
	Input          io.Reader
	Output         io.Writer
	Preview        PreviewFunc
	UseAltScreen   bool
	ClipboardRead  ClipboardReadFunc
	ClipboardWrite ClipboardWriteFunc
	RunCommand     RunCommandFunc
	CommandTimeout time.Duration
	AllowedEnv     map[string]string
	MissingEnv     []string
}

const (
	defaultCommandTimeout = 15 * time.Second
)

func applyDefaults(opts Options) Options {
	if opts.CommandTimeout <= 0 {
		opts.CommandTimeout = defaultCommandTimeout
	}
	if opts.ClipboardRead == nil {
		opts.ClipboardRead = func() (string, error) {
			return "", fmt.Errorf("clipboard integration unavailable")
		}
	}
	if opts.ClipboardWrite == nil {
		opts.ClipboardWrite = func(string) error {
			return fmt.Errorf("clipboard integration unavailable")
		}
	}
	if opts.RunCommand == nil {
		opts.RunCommand = func(context.Context, string, string, map[string]string) (string, string, error) {
			return "", "", fmt.Errorf("shell command execution unavailable")
		}
	}
	if opts.AllowedEnv == nil {
		opts.AllowedEnv = make(map[string]string)
	}
	return opts
}

// NewProgram constructs a Bubble Tea program ready to start.
func NewProgram(opts Options) (*tea.Program, error) {
	opts = applyDefaults(opts)
	if opts.Preview == nil {
		return nil, fmt.Errorf("preview function is required")
	}

	model := newModel(opts)

	var programOptions []tea.ProgramOption
	if opts.Input != nil {
		programOptions = append(programOptions, tea.WithInput(opts.Input))
	}
	if opts.Output != nil {
		programOptions = append(programOptions, tea.WithOutput(opts.Output))
	}
	if opts.UseAltScreen {
		programOptions = append(programOptions, tea.WithAltScreen())
	}

	program := tea.NewProgram(model, programOptions...)
	return program, nil
}

type focusArea int

const (
	focusSubject focusArea = iota
	focusCommand
	focusEnvironment
)

type commandResult struct {
	Command     string
	Stdout      string
	Stderr      string
	Err         error
	UsedPreview bool
	EnvVars     []string
}

type commandMode int

const (
	commandModeSubject commandMode = iota
	commandModePreview
)

type commandFinishedMsg struct {
	result commandResult
	mode   commandMode
}

func (r commandResult) empty() bool {
	return r.Command == "" && r.Stdout == "" && r.Stderr == "" && r.Err == nil
}

type model struct {
	tokens         []string
	subject        textinput.Model
	command        textinput.Model
	focus          focusArea
	preview        string
	previewErr     error
	statusMessage  string
	previewFunc    PreviewFunc
	clipboardRead  ClipboardReadFunc
	clipboardWrite ClipboardWriteFunc
	runCommand     RunCommandFunc
	commandTimeout time.Duration
	lastResult     commandResult
	commandRunning bool
	cancelCommand  context.CancelFunc
	runningCommand string
	runningMode    commandMode
	allowedEnv     []string
	envNames       []string
	missingEnv     []string
	envValues      map[string]string
	envInitial     map[string]string
	envSelection   int
	helpVisible    bool
}

func newModel(opts Options) model {
	subject := textinput.New()
	subject.Placeholder = "Describe the subject to update the preview"
	subject.Prompt = ""
	subject.CharLimit = 0
	subject.Focus()

	command := textinput.New()
	command.Placeholder = "Enter shell command (leave blank to opt out)"
	command.Prompt = ""
	command.CharLimit = 0
	command.Blur()

	envInitial := make(map[string]string, len(opts.AllowedEnv))
	envValues := make(map[string]string, len(opts.AllowedEnv))
	envNames := make([]string, 0, len(opts.AllowedEnv))
	for name, value := range opts.AllowedEnv {
		envInitial[name] = value
		envValues[name] = value
		envNames = append(envNames, name)
	}
	sort.Strings(envNames)

	allowedEnv := append([]string(nil), envNames...)

	missingEnv := append([]string(nil), opts.MissingEnv...)
	if len(missingEnv) > 0 {
		sort.Strings(missingEnv)
	}

	status := "Ready. Tab to the command field to configure shell actions. Leave command empty to opt out."
	if len(envNames) > 0 {
		status += " Environment allowlist: " + strings.Join(allowedEnv, ", ") + ". Tab again to focus the allowlist and press Ctrl+E to toggle entries."
	} else {
		status += " Environment allowlist: (none)."
	}
	if len(missingEnv) > 0 {
		status += " Missing environment variables: " + strings.Join(missingEnv, ", ") + " (not set)."
	}

	m := model{
		tokens:         append([]string(nil), opts.Tokens...),
		subject:        subject,
		command:        command,
		focus:          focusSubject,
		previewFunc:    opts.Preview,
		clipboardRead:  opts.ClipboardRead,
		clipboardWrite: opts.ClipboardWrite,
		runCommand:     opts.RunCommand,
		commandTimeout: opts.CommandTimeout,
		statusMessage:  status,
		allowedEnv:     allowedEnv,
		envNames:       envNames,
		missingEnv:     missingEnv,
		envValues:      envValues,
		envInitial:     envInitial,
		envSelection:   0,
	}
	if len(envNames) == 0 {
		m.envSelection = -1
	}
	m.refreshPreview()
	return m
}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch typed := msg.(type) {
	case commandFinishedMsg:
		m.commandRunning = false
		m.runningCommand = ""
		m.runningMode = commandModeSubject
		m.cancelCommand = nil
		m.lastResult = typed.result

		if errors.Is(typed.result.Err, context.Canceled) {
			m.statusMessage = "Command cancelled."
			return m, nil
		}
		if typed.result.Err != nil {
			m.statusMessage = fmt.Sprintf("Command failed: %v", typed.result.Err)
			return m, nil
		}

		if typed.mode == commandModeSubject {
			trimmed := strings.TrimRight(typed.result.Stdout, "\n")
			m.subject.SetValue(trimmed)
			m.refreshPreview()
			m.statusMessage = "Subject replaced with command stdout."
		} else {
			m.statusMessage = "Command completed; inspect result pane. Use Ctrl+Y to insert stdout into the subject."
		}
		return m, nil
	}

	if keyMsg, ok := msg.(tea.KeyMsg); ok {
		switch keyMsg.Type {
		case tea.KeyCtrlC, tea.KeyEsc:
			if m.helpVisible {
				m.helpVisible = false
				m.statusMessage = "Help overlay closed."
				return m, nil
			}
			if m.commandRunning {
				if m.cancelCommand != nil {
					m.cancelCommand()
					m.cancelCommand = nil
				}
				if m.runningCommand != "" {
					m.statusMessage = fmt.Sprintf("Cancelling %q…", m.runningCommand)
				} else {
					m.statusMessage = "Cancelling command…"
				}
				return m, nil
			}
			return m, tea.Quit

		case tea.KeyTab:
			m.toggleFocus()
			return m, nil
		case tea.KeyEnter:
			if m.focus == focusCommand {
				return m, (&m).executeSubjectCommand()
			}
			if m.focus == focusEnvironment {
				m.toggleSelectedEnv()
				return m, nil
			}
		case tea.KeyUp:
			if m.focus == focusEnvironment {
				m.moveEnvSelection(-1)
				return m, nil
			}
		case tea.KeyDown:
			if m.focus == focusEnvironment {
				m.moveEnvSelection(1)
				return m, nil
			}
		}

		switch keyMsg.String() {

		case "?":
			m.helpVisible = !m.helpVisible
			if m.helpVisible {
				m.statusMessage = "Help overlay open. Press ? to close."
			} else {
				m.statusMessage = "Help overlay closed."
			}
			return m, nil

		case "ctrl+l":

			m.loadSubjectFromClipboard()
			return m, nil
		case "ctrl+o":
			m.copyPreviewToClipboard()
			return m, nil
		case "ctrl+p":
			return m, (&m).executePreviewCommand()
		case "ctrl+e":
			if m.focus == focusEnvironment {
				m.toggleSelectedEnv()
			} else if len(m.envNames) > 0 {
				m.focus = focusEnvironment
				m.ensureEnvSelection()
				m.statusMessage = "Environment allowlist focused. Use Up/Down to choose a variable and Ctrl+E to toggle it."
			} else {
				m.statusMessage = "No environment variables configured to toggle."
			}
			return m, nil
		case "ctrl+a":
			if m.focus == focusEnvironment {
				m.setAllEnv(true)
				return m, nil
			}
		case "ctrl+x":
			if m.focus == focusEnvironment {
				m.setAllEnv(false)
				return m, nil
			}

		case "ctrl+y":
			m.reinsertLastResult()
			return m, nil
		}
	}

	var cmds []tea.Cmd

	previousValue := m.subject.Value()
	newSubject, subjectCmd := m.subject.Update(msg)
	if subjectCmd != nil {
		cmds = append(cmds, subjectCmd)
	}
	m.subject = newSubject
	if newSubject.Value() != previousValue {
		m.refreshPreview()
	}

	newCommand, commandCmd := m.command.Update(msg)
	if commandCmd != nil {
		cmds = append(cmds, commandCmd)
	}
	m.command = newCommand

	return m, tea.Batch(cmds...)
}

func (m model) View() string {
	var b strings.Builder
	b.WriteString("bar prompt editor (Bubble Tea prototype)\n\n")
	b.WriteString("Tokens: ")
	if len(m.tokens) == 0 {
		b.WriteString("<none>")
	} else {
		b.WriteString(strings.Join(m.tokens, " "))
	}
	b.WriteString("\n")

	if m.helpVisible {
		b.WriteString("\nHelp overlay (press ? to close):\n")
		b.WriteString("  Subject focus: type directly, Ctrl+L loads clipboard, Ctrl+O copies preview.\n")
		b.WriteString("  Command focus: Enter runs command, Ctrl+P pipes preview, Ctrl+Y inserts stdout, leave blank to skip.\n")
		b.WriteString("  Environment: Tab again to focus list, Up/Down move, Ctrl+E toggle, Ctrl+A enable all, Ctrl+X clear allowlist.\n")
		b.WriteString("  Cancellation: Esc or Ctrl+C closes help first, then cancels running commands, then exits.\n")
		b.WriteString("  Help: Press ? anytime to toggle this reference.\n\n")
	}

	b.WriteString("Environment allowlist: ")
	if len(m.allowedEnv) == 0 {
		b.WriteString("(none)")
	} else {
		b.WriteString(strings.Join(m.allowedEnv, ", "))
	}
	b.WriteString("\n")
	if len(m.envNames) == 0 {
		b.WriteString("Allowlist manager: (no environment variables configured)\n")
	} else {
		b.WriteString("Allowlist manager (Tab focuses · Up/Down move · Ctrl+E toggle · Ctrl+A enable all · Ctrl+X clear):\n")
		for i, name := range m.envNames {
			cursor := " "
			if m.focus == focusEnvironment && i == m.envSelection {
				cursor = ">"
			}
			indicator := "[ ]"
			if _, ok := m.envValues[name]; ok {
				indicator = "[x]"
			}
			b.WriteString("  ")
			b.WriteString(cursor)
			b.WriteString(" ")
			b.WriteString(indicator)
			b.WriteString(" ")
			b.WriteString(name)
			b.WriteString("\n")
		}
	}
	if len(m.missingEnv) > 0 {
		b.WriteString("Missing environment variables: ")
		b.WriteString(strings.Join(m.missingEnv, ", "))
		b.WriteString(" (not set)\n")
	} else {
		b.WriteString("Missing environment variables: (none)\n")
	}
	b.WriteString("\n")

	b.WriteString("Subject (Tab toggles focus):\n")

	b.WriteString(m.subject.View())
	if m.focus == focusSubject {
		b.WriteString("  ← editing")
	}
	b.WriteString("\n\n")

	b.WriteString("Command (Enter runs without preview):\n")
	b.WriteString(m.command.View())
	if m.focus == focusCommand {
		b.WriteString("  ← editing")
	}
	b.WriteString("\n\n")

	b.WriteString("Shortcuts: Tab switch input · Ctrl+L load subject from clipboard · Ctrl+O copy preview to clipboard · Ctrl+P pipe preview to command · Ctrl+Y replace subject with last command stdout · Ctrl+C/Esc exit.\n")
	b.WriteString("Env allowlist controls (when configured): Tab focus env list · Up/Down move selection · Ctrl+E toggle entry · Ctrl+A enable all · Ctrl+X clear allowlist.\n")
	b.WriteString("Leave command blank to opt out. Commands execute in the local shell; inspect output below and copy transcripts if you need logging.\n\n")

	if m.statusMessage != "" {
		b.WriteString("Status: ")
		b.WriteString(m.statusMessage)
		b.WriteString("\n\n")
	}

	if m.commandRunning {
		b.WriteString("Command running: ")
		b.WriteString(m.runningCommand)
		b.WriteString(" (press Esc to cancel)\n\n")
	}

	b.WriteString("Result pane (stdout/stderr):\n")
	if m.lastResult.empty() {
		b.WriteString("(no command has been executed)\n\n")
	} else {
		b.WriteString("Command: ")
		b.WriteString(m.lastResult.Command)
		b.WriteString("\n")
		if m.lastResult.UsedPreview {
			b.WriteString("Input: piped preview text\n")
		} else {
			b.WriteString("Input: (none)\n")
		}
		if m.lastResult.Err != nil {
			b.WriteString("Status: failed — ")
			b.WriteString(m.lastResult.Err.Error())
			b.WriteString("\n")
		} else {
			b.WriteString("Status: completed successfully\n")
		}
		b.WriteString("Environment: ")
		if len(m.lastResult.EnvVars) == 0 {
			b.WriteString("(none)\n")
		} else {
			b.WriteString(strings.Join(m.lastResult.EnvVars, ", "))
			b.WriteString("\n")
		}
		b.WriteString("Stdout:\n")

		if strings.TrimSpace(m.lastResult.Stdout) == "" {
			b.WriteString("(empty)\n")
		} else {
			b.WriteString(m.lastResult.Stdout)
			if !strings.HasSuffix(m.lastResult.Stdout, "\n") {
				b.WriteString("\n")
			}
		}
		b.WriteString("Stderr:\n")
		if strings.TrimSpace(m.lastResult.Stderr) == "" {
			b.WriteString("(empty)\n")
		} else {
			b.WriteString(m.lastResult.Stderr)
			if !strings.HasSuffix(m.lastResult.Stderr, "\n") {
				b.WriteString("\n")
			}
		}
		b.WriteString("\n")
	}

	if m.previewErr != nil {
		b.WriteString("Preview error: ")
		b.WriteString(m.previewErr.Error())
		b.WriteString("\n\n")
	}

	b.WriteString("Preview:\n")
	if strings.TrimSpace(m.preview) == "" {
		b.WriteString("(enter or import a subject to render the preview)\n")
	} else {
		b.WriteString(m.preview)
		if !strings.HasSuffix(m.preview, "\n") {
			b.WriteString("\n")
		}
	}

	b.WriteString("\nPress Ctrl+C or Esc to exit.\n")
	return b.String()
}

func (m *model) toggleFocus() {
	switch m.focus {
	case focusSubject:
		m.subject.Blur()
		m.command.Focus()
		m.focus = focusCommand
		m.statusMessage = "Command input focused. Enter runs without preview. Use Ctrl+P to pipe preview text."
	case focusCommand:
		if len(m.envNames) == 0 {
			m.command.Blur()
			m.subject.Focus()
			m.focus = focusSubject
			m.statusMessage = "Subject input focused. Type directly or use Ctrl+L to load from clipboard."
			return
		}
		m.command.Blur()
		m.focus = focusEnvironment
		m.ensureEnvSelection()
		m.statusMessage = "Environment allowlist focused. Use Up/Down to choose a variable and Ctrl+E to toggle it."
	case focusEnvironment:
		m.focus = focusSubject
		m.subject.Focus()
		m.statusMessage = "Subject input focused. Type directly or use Ctrl+L to load from clipboard."
	}
}

func (m *model) ensureEnvSelection() {
	if len(m.envNames) == 0 {
		m.envSelection = -1
		return
	}
	if m.envSelection < 0 {
		m.envSelection = 0
	}
	if m.envSelection >= len(m.envNames) {
		m.envSelection = len(m.envNames) - 1
	}
}

func (m *model) moveEnvSelection(delta int) {
	if len(m.envNames) == 0 {
		m.statusMessage = "No environment variables configured."
		return
	}
	m.ensureEnvSelection()
	if len(m.envNames) == 0 {
		return
	}
	m.envSelection = (m.envSelection + delta) % len(m.envNames)
	if m.envSelection < 0 {
		m.envSelection += len(m.envNames)
	}
	current := m.envNames[m.envSelection]
	if _, ok := m.envValues[current]; ok {
		m.statusMessage = fmt.Sprintf("%s selected (allowed). Press Ctrl+E to remove it or Ctrl+X to clear all.", current)
	} else {
		m.statusMessage = fmt.Sprintf("%s selected (not allowed). Press Ctrl+E to include it.", current)
	}
}

func (m *model) toggleSelectedEnv() {
	if len(m.envNames) == 0 {
		m.statusMessage = "No environment variables configured."
		return
	}
	m.ensureEnvSelection()
	if m.envSelection < 0 || m.envSelection >= len(m.envNames) {
		return
	}
	name := m.envNames[m.envSelection]
	var message string
	if _, ok := m.envValues[name]; ok {
		delete(m.envValues, name)
		message = fmt.Sprintf("Removed %s from environment allowlist.", name)
	} else {
		value, ok := m.envInitial[name]
		if !ok {
			m.statusMessage = fmt.Sprintf("Cannot add %s; variable missing from initial allowlist.", name)
			return
		}
		m.envValues[name] = value
		message = fmt.Sprintf("Added %s to environment allowlist.", name)
	}
	m.updateEnvSummaries()
	if len(m.allowedEnv) > 0 {
		m.statusMessage = fmt.Sprintf("%s Current allowlist: %s.", message, strings.Join(m.allowedEnv, ", "))
	} else {
		m.statusMessage = message + " Current allowlist: (none)."
	}
}

func (m *model) setAllEnv(enabled bool) {
	if len(m.envNames) == 0 {
		m.statusMessage = "No environment variables configured."
		return
	}
	if enabled {
		for _, name := range m.envNames {
			if value, ok := m.envInitial[name]; ok {
				m.envValues[name] = value
			}
		}
	} else {
		for _, name := range m.envNames {
			delete(m.envValues, name)
		}
	}
	m.updateEnvSummaries()
	if enabled {
		if len(m.allowedEnv) > 0 {
			m.statusMessage = fmt.Sprintf("Enabled all environment variables in the allowlist. Current allowlist: %s.", strings.Join(m.allowedEnv, ", "))
		} else {
			m.statusMessage = "Enabled all environment variables in the allowlist. Current allowlist: (none)."
		}
	} else {
		m.statusMessage = "Cleared the environment allowlist. Current allowlist: (none)."
	}
}

func (m *model) updateEnvSummaries() {
	names := make([]string, 0, len(m.envValues))
	for name := range m.envValues {
		names = append(names, name)
	}
	sort.Strings(names)
	m.allowedEnv = names
}

func (m *model) refreshPreview() {
	if m.previewFunc == nil {
		m.preview = ""
		m.previewErr = fmt.Errorf("preview unavailable")
		return
	}

	preview, err := m.previewFunc(m.subject.Value())
	if err != nil {
		m.preview = ""
		m.previewErr = err
		return
	}

	m.preview = preview
	m.previewErr = nil
}

func (m *model) loadSubjectFromClipboard() {
	text, err := m.clipboardRead()
	if err != nil {
		m.statusMessage = fmt.Sprintf("Clipboard read failed: %v", err)
		return
	}
	m.subject.SetValue(text)
	m.refreshPreview()
	m.statusMessage = "Loaded subject from clipboard."
}

func (m *model) copyPreviewToClipboard() {
	if err := m.clipboardWrite(m.preview); err != nil {
		m.statusMessage = fmt.Sprintf("Clipboard write failed: %v", err)
		return
	}
	m.statusMessage = "Copied preview to clipboard."
}

func (m *model) startCommand(mode commandMode) tea.Cmd {
	if m.commandRunning {
		m.statusMessage = fmt.Sprintf("Command %q is already running; press Esc to cancel before starting another.", m.runningCommand)
		return nil
	}

	command := strings.TrimSpace(m.command.Value())
	if command == "" {
		m.statusMessage = "No command configured; leave blank to opt out."
		return nil
	}

	input := ""
	if mode == commandModePreview {
		input = m.preview
	}

	ctx, cancel := context.WithTimeout(context.Background(), m.commandTimeout)
	m.cancelCommand = cancel
	m.commandRunning = true
	m.runningCommand = command
	m.runningMode = mode

	envSummary := "(none)"
	if len(m.allowedEnv) > 0 {
		envSummary = strings.Join(m.allowedEnv, ", ")
	}

	if mode == commandModePreview {
		if len(m.allowedEnv) > 0 {
			m.statusMessage = fmt.Sprintf("Running %q with preview input and env %s… Press Esc to cancel.", command, envSummary)
		} else {
			m.statusMessage = fmt.Sprintf("Running %q with preview input… Press Esc to cancel.", command)
		}
	} else {
		if len(m.allowedEnv) > 0 {
			m.statusMessage = fmt.Sprintf("Running %q with env %s… Press Esc to cancel.", command, envSummary)
		} else {
			m.statusMessage = fmt.Sprintf("Running %q… Press Esc to cancel.", command)
		}
	}

	runCommand := m.runCommand
	envValues := make(map[string]string, len(m.envValues))
	for name, value := range m.envValues {
		envValues[name] = value
	}
	allowedEnv := append([]string(nil), m.allowedEnv...)
	return func() tea.Msg {
		defer cancel()
		stdout, stderr, err := runCommand(ctx, command, input, envValues)
		if err == nil && ctx.Err() != nil {
			err = ctx.Err()
		}
		return commandFinishedMsg{
			result: commandResult{
				Command:     command,
				Stdout:      stdout,
				Stderr:      stderr,
				Err:         err,
				UsedPreview: mode == commandModePreview,
				EnvVars:     allowedEnv,
			},
			mode: mode,
		}
	}
}

func (m *model) executeSubjectCommand() tea.Cmd {
	return m.startCommand(commandModeSubject)
}

func (m *model) executePreviewCommand() tea.Cmd {
	return m.startCommand(commandModePreview)
}

func (m *model) reinsertLastResult() {
	if m.lastResult.empty() {
		m.statusMessage = "No command output available to insert."
		return
	}
	if strings.TrimSpace(m.lastResult.Stdout) == "" {
		m.statusMessage = "Last command stdout was empty; nothing to insert."
		return
	}
	trimmed := strings.TrimRight(m.lastResult.Stdout, "\n")
	m.subject.SetValue(trimmed)
	m.refreshPreview()
	m.statusMessage = "Subject replaced with last command stdout."
}

// Snapshot renders the current view and preview without starting an interactive program.
func Snapshot(opts Options, subject string) (view string, preview string, err error) {
	opts = applyDefaults(opts)
	if opts.Preview == nil {
		return "", "", fmt.Errorf("preview function is required")
	}

	model := newModel(opts)
	model.subject.SetValue(subject)
	model.refreshPreview()
	return model.View(), model.preview, nil
}
