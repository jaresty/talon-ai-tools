package bartui

import (
	"fmt"
	"io"
	"strings"

	textinput "github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
)

// PreviewFunc produces the preview text for the current subject.
type PreviewFunc func(subject string) (string, error)

// Options configure the Bubble Tea prompt editor program.
type Options struct {
	Tokens       []string
	Input        io.Reader
	Output       io.Writer
	Preview      PreviewFunc
	UseAltScreen bool
}

// NewProgram constructs a Bubble Tea program ready to start.
func NewProgram(opts Options) (*tea.Program, error) {
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

type model struct {
	tokens      []string
	input       textinput.Model
	preview     string
	err         error
	previewFunc PreviewFunc
}

func newModel(opts Options) model {
	input := textinput.New()
	input.Placeholder = "Describe the subject to update the preview"
	input.Prompt = ""
	input.CharLimit = 0
	input.Focus()

	m := model{
		tokens:      append([]string(nil), opts.Tokens...),
		input:       input,
		previewFunc: opts.Preview,
	}
	m.refreshPreview()
	return m
}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch key := msg.(type) {
	case tea.KeyMsg:
		switch key.String() {
		case "ctrl+c", "esc":
			return m, tea.Quit
		}
	}

	var cmd tea.Cmd
	previous := m.input.Value()
	newInput, inputCmd := m.input.Update(msg)
	if inputCmd != nil {
		cmd = inputCmd
	}
	m.input = newInput

	if newInput.Value() != previous {
		m.refreshPreview()
	}

	return m, cmd
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
	b.WriteString("\n\nSubject:\n")
	b.WriteString(m.input.View())
	b.WriteString("\n\n")

	if m.err != nil {
		b.WriteString("Error: ")
		b.WriteString(m.err.Error())
		b.WriteString("\n\n")
	}

	b.WriteString("Preview:\n")
	if strings.TrimSpace(m.preview) == "" {
		b.WriteString("(enter a subject to render the preview)\n")
	} else {
		b.WriteString(m.preview)
		if !strings.HasSuffix(m.preview, "\n") {
			b.WriteString("\n")
		}
	}

	b.WriteString("\nPress Ctrl+C or Esc to exit.\n")
	return b.String()
}

func (m *model) refreshPreview() {
	if m.previewFunc == nil {
		m.preview = ""
		m.err = fmt.Errorf("preview unavailable")
		return
	}

	preview, err := m.previewFunc(m.input.Value())
	if err != nil {
		m.preview = ""
		m.err = err
		return
	}

	m.preview = preview
	m.err = nil
}

// Snapshot renders the current view and preview without starting an interactive program.
func Snapshot(opts Options, subject string) (view string, preview string, err error) {
	if opts.Preview == nil {
		return "", "", fmt.Errorf("preview function is required")
	}

	model := newModel(opts)
	model.input.SetValue(subject)
	model.refreshPreview()
	return model.View(), model.preview, nil
}
