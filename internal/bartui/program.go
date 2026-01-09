package bartui

import (
	"context"
	"fmt"
	"io"
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
type RunCommandFunc func(ctx context.Context, command string, stdin string) (stdout string, stderr string, err error)

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
		opts.RunCommand = func(context.Context, string, string) (string, string, error) {
			return "", "", fmt.Errorf("shell command execution unavailable")
		}
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
)

type commandResult struct {
	Command     string
	Stdout      string
	Stderr      string
	Err         error
	UsedPreview bool
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
		statusMessage:  "Ready. Tab to the command field to configure shell actions. Leave command empty to opt out.",
	}
	m.refreshPreview()
	return m
}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	if keyMsg, ok := msg.(tea.KeyMsg); ok {
		switch keyMsg.Type {
		case tea.KeyCtrlC, tea.KeyEsc:
			return m, tea.Quit
		case tea.KeyTab:
			m.toggleFocus()
			return m, nil
		case tea.KeyEnter:
			if m.focus == focusCommand {
				m.executeSubjectCommand()
				return m, nil
			}
		}

		switch keyMsg.String() {
		case "ctrl+l":
			m.loadSubjectFromClipboard()
			return m, nil
		case "ctrl+o":
			m.copyPreviewToClipboard()
			return m, nil
		case "ctrl+p":
			m.executePreviewCommand()
			return m, nil
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
	b.WriteString("\n\n")

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
	b.WriteString("Leave command blank to opt out. Commands execute in the local shell; inspect output below and copy transcripts if you need logging.\n\n")

	if m.statusMessage != "" {
		b.WriteString("Status: ")
		b.WriteString(m.statusMessage)
		b.WriteString("\n\n")
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
		m.command.Blur()
		m.subject.Focus()
		m.focus = focusSubject
		m.statusMessage = "Subject input focused. Type directly or use Ctrl+L to load from clipboard."
	}
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

func (m *model) executeSubjectCommand() {
	command := strings.TrimSpace(m.command.Value())
	if command == "" {
		m.statusMessage = "No command configured; leave blank to opt out."
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), m.commandTimeout)
	defer cancel()

	stdout, stderr, err := m.runCommand(ctx, command, "")
	m.lastResult = commandResult{
		Command:     command,
		Stdout:      stdout,
		Stderr:      stderr,
		Err:         err,
		UsedPreview: false,
	}

	if err != nil {
		m.statusMessage = fmt.Sprintf("Command failed: %v", err)
		return
	}

	trimmed := strings.TrimRight(stdout, "\n")
	m.subject.SetValue(trimmed)
	m.refreshPreview()
	m.statusMessage = "Subject replaced with command stdout."
}

func (m *model) executePreviewCommand() {
	command := strings.TrimSpace(m.command.Value())
	if command == "" {
		m.statusMessage = "No command configured; leave blank to opt out."
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), m.commandTimeout)
	defer cancel()

	stdout, stderr, err := m.runCommand(ctx, command, m.preview)
	m.lastResult = commandResult{
		Command:     command,
		Stdout:      stdout,
		Stderr:      stderr,
		Err:         err,
		UsedPreview: true,
	}

	if err != nil {
		m.statusMessage = fmt.Sprintf("Command failed: %v", err)
		return
	}

	m.statusMessage = "Command completed; inspect result pane. Use Ctrl+Y to insert stdout into the subject."
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
