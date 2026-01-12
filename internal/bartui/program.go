package bartui

import (
	"context"
	"errors"
	"fmt"
	"io"
	"os"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
	"unicode"
	"unicode/utf8"

	textinput "github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
)

// PreviewFunc produces the preview text for the given subject and tokens.
type PreviewFunc func(subject string, tokens []string) (string, error)

// ClipboardReadFunc reads text from the clipboard.
type ClipboardReadFunc func() (string, error)

// ClipboardWriteFunc writes text to the clipboard.
type ClipboardWriteFunc func(string) error

// RunCommandFunc executes the provided shell command. The stdin parameter contains
// the input to provide on the command's standard input. The returned stdout and
// stderr values are rendered in the result pane regardless of the exit status.
type RunCommandFunc func(ctx context.Context, command string, stdin string, env map[string]string) (stdout string, stderr string, err error)

type PresetSummary struct {
	Name     string
	SavedAt  time.Time
	Static   string
	Voice    string
	Audience string
	Tone     string
}

type PresetDetails struct {
	Name    string
	Tokens  []string
	SavedAt time.Time
}

const paletteHistoryLimit = 20
const commandHistoryErrorLimit = 80

var (
	paletteDebugMu     sync.Mutex
	paletteDebugWriter io.Writer
)

func init() {
	if path := os.Getenv("BARTUI_DEBUG_PALETTE"); path != "" {
		if f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644); err == nil {
			paletteDebugWriter = f
		}
	}
}

func paletteDebugLog(m *model, action string, detail string) {
	if paletteDebugWriter == nil {
		return
	}
	paletteDebugMu.Lock()
	defer paletteDebugMu.Unlock()
	fmt.Fprintf(paletteDebugWriter, "%s visible=%t focus=%d detail=%s\n", action, m.tokenPaletteVisible, m.focus, detail)
}

func paletteDebugViewSummary(m *model, view string) {
	if paletteDebugWriter == nil {
		return
	}
	tokensHeader := strings.Contains(view, "Tokens (")
	paletteHeader := strings.Contains(view, "Token palette (")
	envBlock := strings.Contains(view, "Environment allowlist:")
	presetBlock := strings.Contains(view, "Preset pane (")
	detail := fmt.Sprintf(
		"paletteFocus=%d paletteOptions=%d paletteIndex=%d filterLen=%d filter=%q help=%t presetPane=%t width=%d height=%d subjectViewport=%dx%d resultViewport=%dx%d subjectLen=%d commandLen=%d previewLen=%d statusLen=%d viewLen=%d tokensHeader=%t paletteBlock=%t envBlock=%t presetBlock=%t",
		m.tokenPaletteFocus,
		len(m.tokenPaletteOptions),
		m.tokenPaletteOptionIndex,
		len(m.tokenPaletteFilter.Value()),
		m.tokenPaletteFilter.Value(),
		m.helpVisible,
		m.presetPaneVisible,
		m.width,
		m.height,
		m.subjectViewport.Width,
		m.subjectViewport.Height,
		m.resultViewport.Width,
		m.resultViewport.Height,
		len(m.subject.Value()),
		len(m.command.Value()),
		len(m.preview),
		len(m.statusMessage),
		len(view),
		tokensHeader,
		paletteHeader,
		envBlock,
		presetBlock,
	)
	paletteDebugLog(m, "ViewSummary", detail)
}

type ListPresetsFunc func() ([]PresetSummary, error)
type LoadPresetFunc func(name string) (PresetDetails, error)
type SavePresetFunc func(name string, description string, tokens []string) (PresetDetails, error)
type DeletePresetFunc func(name string) error

// Options configure the Bubble Tea prompt editor program.
type Options struct {
	Tokens          []string
	TokenCategories []TokenCategory
	Input           io.Reader
	Output          io.Writer
	Preview         PreviewFunc
	UseAltScreen    bool
	ClipboardRead   ClipboardReadFunc
	ClipboardWrite  ClipboardWriteFunc
	RunCommand      RunCommandFunc
	CommandTimeout  time.Duration
	AllowedEnv      map[string]string
	MissingEnv      []string
	ListPresets     ListPresetsFunc
	LoadPreset      LoadPresetFunc
	SavePreset      SavePresetFunc
	DeletePreset    DeletePresetFunc
	InitialWidth    int
	InitialHeight   int
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
	if opts.ListPresets == nil {
		opts.ListPresets = func() ([]PresetSummary, error) {
			return nil, nil
		}
	}
	if opts.LoadPreset == nil {
		opts.LoadPreset = func(string) (PresetDetails, error) {
			return PresetDetails{}, fmt.Errorf("preset loading unavailable")
		}
	}
	if opts.SavePreset == nil {
		opts.SavePreset = func(name string, description string, tokens []string) (PresetDetails, error) {
			return PresetDetails{}, fmt.Errorf("preset saving unavailable")
		}
	}
	if opts.DeletePreset == nil {
		opts.DeletePreset = func(string) error {
			return fmt.Errorf("preset deletion unavailable")
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
	focusTokens
	focusCommand
	focusResult
	focusEnvironment
)

const (
	defaultViewportWidth  = 80
	defaultViewportHeight = 32
	frameOverheadLines    = 8
	minTokenViewport      = 6
	minSubjectViewport    = 4
	minResultViewport     = 8
)

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func clampInt(value, minValue, maxValue int) int {
	if maxValue < minValue {
		maxValue = minValue
	}
	if value < minValue {
		return minValue
	}
	if value > maxValue {
		return maxValue
	}
	return value
}

type tokenPaletteFocus int

const (
	tokenPaletteFocusFilter tokenPaletteFocus = iota
	tokenPaletteFocusCategories
	tokenPaletteFocusOptions
)

const (
	tokenPaletteResetOption       = -1
	tokenPaletteCopyCommandOption = -2
)

type presetPaneMode int

const (
	presetModeList presetPaneMode = iota
	presetModeSaving
	presetModeConfirmDelete
)

type commandResult struct {
	Command     string
	Stdout      string
	Stderr      string
	Err         error
	UsedPreview bool
	EnvVars     []string
	ExitCode    int
	HasExitCode bool
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

func exitCodeFromError(err error) (int, bool) {
	if err == nil {
		return 0, true
	}
	type exitCoder interface{ ExitCode() int }
	var coder exitCoder
	if errors.As(err, &coder) {
		return coder.ExitCode(), true
	}
	return 0, false
}

type subjectReplacementPrompt struct {
	source         string
	newValue       string
	previousValue  string
	snippet        string
	newLength      int
	previousLength int
	message        string
}

func newSubjectReplacementPrompt(source, previous, newValue string) *subjectReplacementPrompt {
	snippet := subjectSnippet(newValue)
	prevLen := subjectContentLength(previous)
	newLen := subjectContentLength(newValue)
	message := fmt.Sprintf("Replace subject with %s: %q (new %d chars, was %d). Press Enter to confirm, Esc to cancel.", source, snippet, newLen, prevLen)
	return &subjectReplacementPrompt{
		source:         source,
		newValue:       newValue,
		previousValue:  previous,
		snippet:        snippet,
		newLength:      newLen,
		previousLength: prevLen,
		message:        message,
	}
}

func subjectContentLength(text string) int {
	trimmed := strings.TrimRight(text, "\r\n")
	if trimmed == "" {
		trimmed = strings.TrimSpace(text)
	}
	return utf8.RuneCountInString(trimmed)
}

func subjectSnippet(text string) string {
	trimmed := strings.TrimSpace(text)
	if trimmed == "" {
		return "(empty)"
	}
	firstLine := trimmed
	if idx := strings.IndexRune(trimmed, '\n'); idx >= 0 {
		firstLine = trimmed[:idx]
	}
	runes := []rune(firstLine)
	if len(runes) > 60 {
		firstLine = string(runes[:57]) + "\u2026"
	}
	if strings.Count(trimmed, "\n") > 0 {
		firstLine += " \u2026"
	}
	return firstLine
}

func (r commandResult) empty() bool {
	return r.Command == "" && r.Stdout == "" && r.Stderr == "" && r.Err == nil
}

type tokenOptionReference struct {
	categoryIndex int
	optionIndex   int
}

type tokenCategoryState struct {
	category      TokenCategory
	selected      []string
	selectedIndex map[string]int
}

func newTokenCategoryState(category TokenCategory) tokenCategoryState {
	return tokenCategoryState{
		category:      category,
		selected:      []string{},
		selectedIndex: make(map[string]int),
	}
}

func (s *tokenCategoryState) clear() {
	s.selected = s.selected[:0]
	s.selectedIndex = make(map[string]int)
}

func (s *tokenCategoryState) has(value string) bool {
	if s == nil {
		return false
	}
	_, ok := s.selectedIndex[value]
	return ok
}

func (s *tokenCategoryState) add(value string, max int) bool {
	if s == nil || value == "" {
		return false
	}
	if s.has(value) {
		return false
	}
	if max > 0 && len(s.selected) >= max {
		return false
	}
	s.selected = append(s.selected, value)
	s.selectedIndex[value] = len(s.selected) - 1
	return true
}

func (s *tokenCategoryState) remove(value string) bool {
	if s == nil {
		return false
	}
	index, ok := s.selectedIndex[value]
	if !ok {
		return false
	}
	s.selected = append(s.selected[:index], s.selected[index+1:]...)
	delete(s.selectedIndex, value)
	for i := index; i < len(s.selected); i++ {
		s.selectedIndex[s.selected[i]] = i
	}
	return true
}

func (s *tokenCategoryState) setSelected(values []string, max int) {
	s.clear()
	for _, value := range values {
		if max > 0 && len(s.selected) >= max {
			break
		}
		s.add(value, max)
	}
}

type model struct {
	tokens                   []string
	tokenCategories          []TokenCategory
	tokenStates              []tokenCategoryState
	tokenOptionLookup        map[string]tokenOptionReference
	tokenCategoryIndex       int
	tokenOptionIndex         int
	tokenPaletteVisible      bool
	tokenPaletteFocus        tokenPaletteFocus
	tokenPaletteOptions      []int
	tokenPaletteOptionIndex  int
	paletteHistory           []string
	paletteHistoryVisible    bool
	lastPaletteCategoryIndex int
	tokenPaletteFilter       textinput.Model
	tokenViewport            viewport.Model
	focusBeforePalette       focusArea
	unassignedTokens         []string
	lastTokenSnapshot        []string

	destinationSummary string

	pendingSubject       *subjectReplacementPrompt
	subjectUndoValue     string
	subjectUndoSource    string
	subjectUndoAvailable bool

	width            int
	height           int
	subjectViewport  viewport.Model
	resultViewport   viewport.Model
	condensedPreview bool

	subject                textinput.Model
	command                textinput.Model
	focus                  focusArea
	preview                string
	previewErr             error
	statusMessage          string
	statusBeforeHelp       string
	previewFunc            PreviewFunc
	clipboardRead          ClipboardReadFunc
	clipboardWrite         ClipboardWriteFunc
	runCommand             RunCommandFunc
	commandTimeout         time.Duration
	lastResult             commandResult
	commandRunning         bool
	cancelCommand          context.CancelFunc
	runningCommand         string
	runningMode            commandMode
	allowedEnv             []string
	envNames               []string
	missingEnv             []string
	envValues              map[string]string
	envInitial             map[string]string
	envSelection           int
	helpVisible            bool
	listPresets            ListPresetsFunc
	loadPreset             LoadPresetFunc
	savePreset             SavePresetFunc
	deletePreset           DeletePresetFunc
	presetPaneVisible      bool
	presetSummaries        []PresetSummary
	presetSelection        int
	presetMode             presetPaneMode
	presetNameInput        textinput.Model
	presetDescriptionInput textinput.Model
	pendingDeleteName      string
	activePresetName       string
	activePresetTokens     []string
	focusBeforePane        focusArea
	lastDeletedPreset      *PresetDetails
	lastDeletedDescription string
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

	presetNameInput := textinput.New()
	presetNameInput.Placeholder = "Preset name"
	presetNameInput.Prompt = ""
	presetNameInput.CharLimit = 64

	presetDescriptionInput := textinput.New()
	presetDescriptionInput.Placeholder = "(optional) description"
	presetDescriptionInput.Prompt = ""
	presetDescriptionInput.CharLimit = 120

	tokenPaletteFilter := textinput.New()
	tokenPaletteFilter.Placeholder = "Filter tokens"
	tokenPaletteFilter.Prompt = ""
	tokenPaletteFilter.CharLimit = 64
	tokenPaletteFilter.Blur()

	status := "Subject input focused. Use Ctrl+L to load from clipboard. Tab cycles focus · Ctrl+P palette · Ctrl+B copy CLI."
	if len(envNames) > 0 {
		status += " Environment allowlist: " + strings.Join(allowedEnv, ", ") + ". Tab again to focus the allowlist and press Ctrl+E to toggle entries."
	} else {
		status += " Environment allowlist: (none)."
	}
	if len(missingEnv) > 0 {
		status += " Missing environment variables: " + strings.Join(missingEnv, ", ") + " (not set)."
	}

	subjectViewport := viewport.New(defaultViewportWidth, minSubjectViewport)
	tokenViewport := viewport.New(defaultViewportWidth, minTokenViewport)
	resultViewport := viewport.New(defaultViewportWidth, minResultViewport)

	initialWidth := opts.InitialWidth
	if initialWidth <= 0 {
		initialWidth = defaultViewportWidth
	}
	initialHeight := opts.InitialHeight
	if initialHeight <= 0 {
		initialHeight = defaultViewportHeight
	}

	m := model{
		tokens:                 append([]string(nil), opts.Tokens...),
		tokenCategories:        cloneTokenCategories(opts.TokenCategories),
		tokenPaletteFilter:     tokenPaletteFilter,
		focusBeforePalette:     focusSubject,
		subject:                subject,
		command:                command,
		focus:                  focusSubject,
		previewFunc:            opts.Preview,
		clipboardRead:          opts.ClipboardRead,
		clipboardWrite:         opts.ClipboardWrite,
		runCommand:             opts.RunCommand,
		commandTimeout:         opts.CommandTimeout,
		statusMessage:          status,
		allowedEnv:             allowedEnv,
		envNames:               envNames,
		missingEnv:             missingEnv,
		envValues:              envValues,
		envInitial:             envInitial,
		envSelection:           0,
		helpVisible:            false,
		width:                  initialWidth,
		height:                 initialHeight,
		subjectViewport:        subjectViewport,
		tokenViewport:          tokenViewport,
		resultViewport:         resultViewport,
		listPresets:            opts.ListPresets,
		loadPreset:             opts.LoadPreset,
		savePreset:             opts.SavePreset,
		deletePreset:           opts.DeletePreset,
		presetPaneVisible:      false,
		presetSummaries:        nil,
		presetSelection:        -1,
		presetMode:             presetModeList,
		presetNameInput:        presetNameInput,
		presetDescriptionInput: presetDescriptionInput,
		pendingDeleteName:      "",
		activePresetName:       "",
		activePresetTokens:     nil,
		focusBeforePane:        focusSubject,
		lastDeletedPreset:      nil,
		lastDeletedDescription: "",
	}
	m.destinationSummary = "clipboard — Ctrl+B copies CLI"
	m.initializeTokenCategories()
	if len(envNames) == 0 {
		m.envSelection = -1
	}
	m.refreshPreview()
	m.layoutViewports()
	m.updateTokenViewportContent()
	m.updateSubjectViewportContent()
	m.updateResultViewportContent()
	return m
}

func (m *model) layoutViewports() {
	width := m.width
	if width <= 0 {
		width = defaultViewportWidth
	}
	height := m.height
	if height <= 0 {
		height = defaultViewportHeight
	}

	available := height - frameOverheadLines
	if available < 3 {
		available = 3
	}

	tokenHeight := minTokenViewport
	subjectHeight := minSubjectViewport
	resultHeight := minResultViewport

	totalMin := tokenHeight + subjectHeight + resultHeight
	if totalMin > available {
		scale := float64(available) / float64(totalMin)
		tokenHeight = maxInt(1, int(float64(tokenHeight)*scale))
		subjectHeight = maxInt(1, int(float64(subjectHeight)*scale))
		resultHeight = maxInt(1, available-tokenHeight-subjectHeight)
	} else {
		remaining := available - totalMin
		if remaining > 0 {
			extraToken := remaining / 3
			tokenHeight += extraToken
			remaining -= extraToken

			extraSubject := remaining / 2
			subjectHeight += extraSubject
			remaining -= extraSubject

			resultHeight += remaining
		}
	}

	m.tokenViewport.Width = maxInt(1, width)
	m.tokenViewport.Height = maxInt(1, tokenHeight)
	m.subjectViewport.Width = maxInt(1, width)
	m.subjectViewport.Height = maxInt(minSubjectViewport, subjectHeight)
	m.resultViewport.Width = maxInt(1, width)
	m.resultViewport.Height = maxInt(minResultViewport, resultHeight)
}

func (m *model) updateSubjectViewportContent() {
	var builder strings.Builder
	builder.WriteString(m.subject.View())
	if m.focus == focusSubject {
		builder.WriteString("  ← editing")
	}
	m.subjectViewport.SetContent(builder.String())
}

func (m *model) renderResultViewportContent() string {
	var builder strings.Builder

	builder.WriteString("Result pane (stdout/stderr):\n")
	if m.lastResult.empty() {
		builder.WriteString("(no command has been executed)\n\n")
	} else {
		builder.WriteString("Command: ")
		builder.WriteString(m.lastResult.Command)
		builder.WriteString("\n")
		if m.lastResult.UsedPreview {
			builder.WriteString("Input: piped preview text\n")
		} else {
			builder.WriteString("Input: (none)\n")
		}
		if m.lastResult.HasExitCode {
			builder.WriteString(fmt.Sprintf("Exit code: %d\n", m.lastResult.ExitCode))
		} else {
			builder.WriteString("Exit code: (unknown)\n")
		}
		if m.lastResult.Err != nil {
			builder.WriteString("Status: failed\n")
			builder.WriteString("Error: ")
			builder.WriteString(m.lastResult.Err.Error())
			builder.WriteString("\n")
		} else {
			builder.WriteString("Status: completed successfully\n")
		}
		builder.WriteString("Environment: ")
		builder.WriteString(strings.TrimPrefix(summarizeEnvList(m.lastResult.EnvVars), "env "))
		builder.WriteString("\n")
		builder.WriteString("\n")
		builder.WriteString("Stdout:\n")

		stdout := strings.TrimSpace(m.lastResult.Stdout)
		if stdout == "" {
			builder.WriteString("(empty)\n")
		} else {
			builder.WriteString(m.lastResult.Stdout)
			if !strings.HasSuffix(m.lastResult.Stdout, "\n") {
				builder.WriteString("\n")
			}
		}
		builder.WriteString("Stderr:\n")
		stderr := strings.TrimSpace(m.lastResult.Stderr)
		if stderr == "" {
			builder.WriteString("(empty)\n")
		} else {
			builder.WriteString(m.lastResult.Stderr)
			if !strings.HasSuffix(m.lastResult.Stderr, "\n") {
				builder.WriteString("\n")
			}
		}
		builder.WriteString("\n")
	}

	if m.previewErr != nil {
		builder.WriteString("Preview error: ")
		builder.WriteString(m.previewErr.Error())
		builder.WriteString("\n")
		return builder.String()
	}

	builder.WriteString("Preview:\n")
	if strings.TrimSpace(m.preview) == "" {
		builder.WriteString("(enter or import a subject to render the preview)\n")
	} else if m.condensedPreview {
		builder.WriteString("(condensed) Preview hidden; press Ctrl+T to expand.\n")
	} else {
		builder.WriteString(m.preview)
		if !strings.HasSuffix(m.preview, "\n") {
			builder.WriteString("\n")
		}
	}

	return builder.String()
}

func (m *model) updateResultViewportContent() {
	m.resultViewport.SetContent(m.renderResultViewportContent())
}

func (m *model) handleWindowSize(msg tea.WindowSizeMsg) {
	if msg.Width <= 0 {
		return
	}
	m.width = msg.Width
	m.height = msg.Height
	m.layoutViewports()
	m.updateTokenViewportContent()
	m.updateSubjectViewportContent()
	m.updateResultViewportContent()
}

func (m *model) handleViewportScroll(v *viewport.Model, key tea.KeyMsg, allowHalf bool) bool {
	switch key.Type {
	case tea.KeyPgUp:
		v.ViewUp()
		return true
	case tea.KeyPgDown:
		v.ViewDown()
		return true
	case tea.KeyHome:
		v.GotoTop()
		return true
	case tea.KeyEnd:
		v.GotoBottom()
		return true
	}
	if !allowHalf {
		return false
	}
	switch key.String() {
	case "ctrl+u":
		v.HalfViewUp()
		return true
	case "ctrl+d":
		v.HalfViewDown()
		return true
	}
	return false
}

func (m *model) handleSubjectViewportKey(key tea.KeyMsg) bool {
	if m.focus != focusSubject {
		return false
	}
	return m.handleViewportScroll(&m.subjectViewport, key, false)
}

func (m *model) handleResultViewportKey(key tea.KeyMsg) bool {
	if m.focus != focusResult {
		return false
	}
	if m.handleViewportScroll(&m.resultViewport, key, true) {
		return true
	}
	switch key.String() {
	case "ctrl+t":
		m.condensedPreview = !m.condensedPreview
		m.updateResultViewportContent()
		return true
	}
	return false
}

func (m *model) handleTokenViewportKey(key tea.KeyMsg) bool {
	if m.focus != focusTokens && !m.tokenPaletteVisible {
		return false
	}
	return m.handleViewportScroll(&m.tokenViewport, key, false)
}

func (m *model) initializeTokenCategories() {
	m.lastPaletteCategoryIndex = -1
	if len(m.tokenCategories) == 0 {
		m.tokenStates = nil
		m.tokenOptionLookup = nil
		m.unassignedTokens = nil
		m.tokenCategoryIndex = 0
		m.tokenOptionIndex = -1
		m.updatePaletteOptions()
		return
	}

	m.tokenOptionLookup = make(map[string]tokenOptionReference)
	m.tokenStates = make([]tokenCategoryState, len(m.tokenCategories))
	for i, category := range m.tokenCategories {
		state := newTokenCategoryState(category)
		m.tokenStates[i] = state
		for j, option := range category.Options {
			value := strings.TrimSpace(option.Value)
			if value == "" {
				continue
			}
			ref := tokenOptionReference{categoryIndex: i, optionIndex: j}
			m.tokenOptionLookup[value] = ref
			m.tokenOptionLookup[strings.ToLower(value)] = ref
			slug := strings.TrimSpace(option.Slug)
			if slug != "" {
				m.tokenOptionLookup[slug] = ref
				m.tokenOptionLookup[strings.ToLower(slug)] = ref
			}
		}
	}

	m.resetTokenStatesFromTokens(m.tokens)
	m.clampTokenCategoryIndex()
	m.clampTokenOptionIndex()
	m.updatePaletteOptions()
}

func (m *model) resetTokenStatesFromTokens(tokens []string) {
	m.unassignedTokens = m.unassignedTokens[:0]
	for i := range m.tokenStates {
		m.tokenStates[i].clear()
	}

	for _, raw := range tokens {
		value := strings.TrimSpace(raw)
		if value == "" {
			continue
		}
		ref, ok := m.tokenOptionLookup[value]
		if !ok {
			m.unassignedTokens = append(m.unassignedTokens, value)
			continue
		}
		if ref.categoryIndex < 0 || ref.categoryIndex >= len(m.tokenStates) {
			m.unassignedTokens = append(m.unassignedTokens, value)
			continue
		}
		state := &m.tokenStates[ref.categoryIndex]
		if ref.optionIndex < 0 || ref.optionIndex >= len(state.category.Options) {
			m.unassignedTokens = append(m.unassignedTokens, value)
			continue
		}
		option := state.category.Options[ref.optionIndex]
		if !state.add(option.Value, state.category.MaxSelections) {
			m.unassignedTokens = append(m.unassignedTokens, value)
		}
	}
}

func (m *model) clampTokenCategoryIndex() {
	if len(m.tokenStates) == 0 {
		m.tokenCategoryIndex = 0
		return
	}
	if m.tokenCategoryIndex < 0 || m.tokenCategoryIndex >= len(m.tokenStates) {
		m.tokenCategoryIndex = 0
	}
}

func (m *model) clampTokenOptionIndex() {
	if len(m.tokenStates) == 0 {
		m.tokenOptionIndex = -1
		return
	}
	state := m.tokenStates[m.tokenCategoryIndex]
	optionsLen := len(state.category.Options)
	if optionsLen == 0 {
		m.tokenOptionIndex = -1
		return
	}
	if m.tokenOptionIndex < 0 {
		m.tokenOptionIndex = 0
	}
	if m.tokenOptionIndex >= optionsLen {
		m.tokenOptionIndex = optionsLen - 1
	}
}

func (m *model) updatePaletteOptions() {
	if len(m.tokenStates) == 0 {
		m.tokenPaletteOptions = nil
		m.tokenPaletteOptionIndex = -1
		return
	}

	prevEntry := 0
	hadPrev := false
	if len(m.tokenPaletteOptions) > 0 && m.tokenPaletteOptionIndex >= 0 && m.tokenPaletteOptionIndex < len(m.tokenPaletteOptions) && m.lastPaletteCategoryIndex == m.tokenCategoryIndex {
		prevEntry = m.tokenPaletteOptions[m.tokenPaletteOptionIndex]
		hadPrev = true
	}

	state := m.tokenStates[m.tokenCategoryIndex]
	filter := strings.ToLower(strings.TrimSpace(m.tokenPaletteFilter.Value()))
	options := make([]int, 0, len(state.category.Options)+2)
	if m.shouldShowCopyCommandAction(filter) {
		options = append(options, tokenPaletteCopyCommandOption)
	}
	if m.shouldShowPresetReset(m.tokenCategoryIndex) {
		options = append(options, tokenPaletteResetOption)
	}
	for idx, option := range state.category.Options {
		if optionMatchesFilter(option, filter) {
			options = append(options, idx)
		}
	}
	if len(options) == 0 {
		m.tokenPaletteOptions = nil
		m.tokenPaletteOptionIndex = -1
		m.lastPaletteCategoryIndex = -1
		return
	}

	m.tokenPaletteOptions = options
	m.lastPaletteCategoryIndex = m.tokenCategoryIndex

	if hadPrev {
		for i, entry := range options {
			if entry == prevEntry {
				m.tokenPaletteOptionIndex = i
				return
			}
		}
	}

	if m.tokenPaletteOptionIndex < 0 || m.tokenPaletteOptionIndex >= len(options) {
		m.tokenPaletteOptionIndex = 0
	}
}

func optionMatchesFilter(option TokenOption, filter string) bool {
	if filter == "" {
		return true
	}
	fields := []string{option.Value, option.Slug, option.Label, option.Description}
	for _, field := range fields {
		if field == "" {
			continue
		}
		if strings.Contains(strings.ToLower(field), filter) {
			return true
		}
	}
	return false
}

func (m *model) clearPaletteFilter() bool {
	trimmed := strings.TrimSpace(m.tokenPaletteFilter.Value())
	if trimmed == "" {
		m.refreshPaletteStatus()
		m.statusMessage = "Token filter already empty. " + m.statusMessage
		return false
	}

	m.tokenPaletteFilter.SetValue("")
	m.tokenPaletteFilter.CursorStart()
	m.updatePaletteOptions()
	m.refreshPaletteStatus()
	m.statusMessage = "Token filter cleared. " + m.statusMessage
	return true
}

func (m *model) shouldShowCopyCommandAction(filter string) bool {
	if filter == "" {
		return true
	}
	keywords := []string{"copy", "command", "clipboard", "bar", "build"}
	for _, keyword := range keywords {
		if strings.Contains(filter, keyword) {
			return true
		}
	}
	return false
}

func (m *model) shouldShowPresetReset(categoryIndex int) bool {
	if m.activePresetName == "" {
		return false
	}
	presetValues := m.presetTokensForCategory(categoryIndex)
	if len(presetValues) == 0 {
		return false
	}
	current := m.tokenStates[categoryIndex].selected
	return !tokensSliceEqual(current, presetValues)
}

func (m *model) presetTokensForCategory(categoryIndex int) []string {
	if m.activePresetName == "" {
		return nil
	}
	if categoryIndex < 0 || categoryIndex >= len(m.tokenStates) {
		return nil
	}
	state := m.tokenStates[categoryIndex]
	max := state.category.MaxSelections
	result := make([]string, 0, len(state.selected))
	seen := make(map[string]struct{})
	for _, token := range m.activePresetTokens {
		ref, ok := m.tokenOptionLookup[token]
		if !ok || ref.categoryIndex != categoryIndex {
			continue
		}
		if ref.optionIndex < 0 || ref.optionIndex >= len(state.category.Options) {
			continue
		}
		value := state.category.Options[ref.optionIndex].Value
		if _, dup := seen[value]; dup {
			continue
		}
		seen[value] = struct{}{}
		result = append(result, value)
		if max > 0 && len(result) >= max {
			break
		}
	}
	return result
}

func tokensSliceEqual(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func containsToken(list []string, value string) bool {
	for _, existing := range list {
		if existing == value {
			return true
		}
	}
	return false
}

func (m *model) recordTokenUndo() {
	snapshot := make([]string, len(m.tokens))
	copy(snapshot, m.tokens)
	m.lastTokenSnapshot = snapshot
}

func (m *model) recordPaletteHistory(entry string) {
	trimmed := strings.TrimSpace(entry)
	if trimmed == "" {
		return
	}
	m.paletteHistory = append([]string{trimmed}, m.paletteHistory...)
	if len(m.paletteHistory) > paletteHistoryLimit {
		m.paletteHistory = m.paletteHistory[:paletteHistoryLimit]
	}
}

func (m *model) recordCommandHistory(result commandResult, mode commandMode) {
	entry := formatCommandHistoryEntry(result, mode)
	if entry == "" {
		return
	}
	m.recordPaletteHistory(entry)
}

func formatCommandHistoryEntry(result commandResult, mode commandMode) string {
	command := strings.TrimSpace(result.Command)
	if command == "" {
		command = "(blank)"
	} else {
		command = sanitizeShellCommand(command)
	}

	scope := "subject"
	if mode == commandModePreview || result.UsedPreview {
		scope = "preview"
	}

	status := "completed"
	switch {
	case errors.Is(result.Err, context.Canceled):
		status = "cancelled"
	case result.Err != nil:
		msg := strings.TrimSpace(result.Err.Error())
		if msg == "" {
			msg = "error"
		} else if idx := strings.IndexRune(msg, '\n'); idx >= 0 {
			msg = msg[:idx]
		}
		runes := []rune(msg)
		if len(runes) > commandHistoryErrorLimit {
			runes = append(runes[:commandHistoryErrorLimit-1], '…')
			msg = string(runes)
		}
		status = fmt.Sprintf("error: %s", msg)
	case result.HasExitCode:
		status = fmt.Sprintf("exit %d", result.ExitCode)
	}

	return fmt.Sprintf("Command (%s) → \"%s\" %s", scope, command, status)
}

func (m *model) togglePaletteHistory() {
	if !m.paletteHistoryVisible && len(m.paletteHistory) == 0 {
		m.statusMessage = "No palette history yet. Make a palette change before toggling history."
		return
	}
	m.paletteHistoryVisible = !m.paletteHistoryVisible
	if m.paletteHistoryVisible {
		m.statusMessage = "Palette history visible. Press Ctrl+H to hide."
	} else {
		m.statusMessage = "Palette history hidden."
	}
}

func (m *model) rebuildTokensFromStates() {
	total := len(m.unassignedTokens)
	for _, state := range m.tokenStates {
		total += len(state.selected)
	}
	result := make([]string, 0, total)
	for _, state := range m.tokenStates {
		result = append(result, state.selected...)
	}
	result = append(result, m.unassignedTokens...)
	m.setTokens(result)
}

func (m *model) moveTokenCategory(delta int) {
	if len(m.tokenStates) == 0 {
		return
	}
	count := len(m.tokenStates)
	m.tokenCategoryIndex = (m.tokenCategoryIndex + delta) % count
	if m.tokenCategoryIndex < 0 {
		m.tokenCategoryIndex += count
	}
	m.clampTokenOptionIndex()
	m.updatePaletteOptions()
	m.refreshPaletteStatus()
}

func (m *model) moveTokenOption(delta int) {
	if len(m.tokenStates) == 0 {
		return
	}
	state := m.tokenStates[m.tokenCategoryIndex]
	optionCount := len(state.category.Options)
	if optionCount == 0 {
		m.tokenOptionIndex = -1
		m.statusMessage = fmt.Sprintf("%s has no options to adjust.", state.category.Label)
		return
	}
	m.tokenOptionIndex = (m.tokenOptionIndex + delta) % optionCount
	if m.tokenOptionIndex < 0 {
		m.tokenOptionIndex += optionCount
	}
	option := state.category.Options[m.tokenOptionIndex]
	slug := option.Slug
	if slug == "" {
		slug = option.Value
	}
	label := option.Label
	if label != "" && !strings.EqualFold(slug, label) {
		m.statusMessage = fmt.Sprintf("%s → %s (%s)", state.category.Label, slug, label)
	} else {
		m.statusMessage = fmt.Sprintf("%s → %s", state.category.Label, slug)
	}
}

func (m *model) movePaletteOption(delta int) {
	if len(m.tokenPaletteOptions) == 0 {
		m.tokenPaletteOptionIndex = -1
		return
	}
	count := len(m.tokenPaletteOptions)
	m.tokenPaletteOptionIndex = (m.tokenPaletteOptionIndex + delta) % count
	if m.tokenPaletteOptionIndex < 0 {
		m.tokenPaletteOptionIndex += count
	}
	m.refreshPaletteStatus()
}

func (m *model) currentTokenOption() (TokenOption, bool) {
	if len(m.tokenStates) == 0 {
		return TokenOption{}, false
	}
	state := m.tokenStates[m.tokenCategoryIndex]
	if len(state.category.Options) == 0 {
		return TokenOption{}, false
	}
	if m.tokenOptionIndex < 0 || m.tokenOptionIndex >= len(state.category.Options) {
		return TokenOption{}, false
	}
	return state.category.Options[m.tokenOptionIndex], true
}

func (m *model) toggleCurrentTokenOption() {
	option, ok := m.currentTokenOption()
	if !ok {
		m.statusMessage = "No token option available to toggle."
		return
	}
	state := &m.tokenStates[m.tokenCategoryIndex]
	slug := option.Slug
	if slug == "" {
		slug = option.Value
	}
	if state.has(option.Value) {
		m.recordTokenUndo()
		state.remove(option.Value)
		m.rebuildTokensFromStates()
		m.statusMessage = fmt.Sprintf("%s → %s removed.", state.category.Label, slug)
		return
	}
	max := state.category.MaxSelections
	if max > 0 && len(state.selected) >= max {
		suffix := ""
		if max > 1 {
			suffix = "s"
		}
		m.statusMessage = fmt.Sprintf("%s already has %d selection%s; remove one before adding another.", state.category.Label, max, suffix)
		return
	}
	m.recordTokenUndo()
	state.add(option.Value, max)
	m.rebuildTokensFromStates()
	m.statusMessage = fmt.Sprintf("%s → %s applied.", state.category.Label, slug)
}

func (m *model) removeCurrentTokenOption() {
	option, ok := m.currentTokenOption()
	if !ok {
		m.statusMessage = "No token option highlighted to remove."
		return
	}
	state := &m.tokenStates[m.tokenCategoryIndex]
	if !state.has(option.Value) {
		slug := option.Slug
		if slug == "" {
			slug = option.Value
		}
		m.statusMessage = fmt.Sprintf("%s not selected; nothing to remove.", slug)
		return
	}
	slug := option.Slug
	if slug == "" {
		slug = option.Value
	}
	m.recordTokenUndo()
	state.remove(option.Value)
	m.rebuildTokensFromStates()
	m.statusMessage = fmt.Sprintf("%s → %s removed.", state.category.Label, slug)
}

func (m *model) undoTokenChange() {
	if m.lastTokenSnapshot == nil {
		m.statusMessage = "No token change to undo."
		return
	}
	snapshot := append([]string(nil), m.lastTokenSnapshot...)
	m.lastTokenSnapshot = nil
	m.setTokens(snapshot)
	m.statusMessage = "Token selection restored."
	m.recordPaletteHistory("Tokens undo restored")
}

func (m *model) openTokenPalette() tea.Cmd {
	if len(m.tokenStates) == 0 {
		m.statusMessage = "No token categories available."
		return nil
	}
	m.focusBeforePalette = m.focus
	m.tokenPaletteVisible = true
	m.paletteHistoryVisible = false
	m.tokenPaletteFocus = tokenPaletteFocusFilter
	m.tokenPaletteFilter.SetValue("")
	cmd := m.tokenPaletteFilter.Focus()
	m.updatePaletteOptions()
	m.refreshPaletteStatus()
	paletteDebugLog(m, "openTokenPalette", fmt.Sprintf("focusBefore=%d", m.focusBeforePalette))
	return cmd
}

func (m *model) closeTokenPalette() tea.Cmd {
	return m.closeTokenPaletteWithStatus("Token palette closed. Press Ctrl+P to reopen and type \"copy command\" to focus the copy action.")
}

func (m *model) closeTokenPaletteWithStatus(status string) tea.Cmd {
	if !m.tokenPaletteVisible {
		return nil
	}
	m.tokenPaletteVisible = false
	m.paletteHistoryVisible = false
	m.tokenPaletteFilter.Blur()
	m.tokenPaletteOptionIndex = 0
	m.tokenPaletteFocus = tokenPaletteFocusFilter

	switch m.focusBeforePalette {
	case focusSubject:
		m.subject.Focus()
		m.command.Blur()
		m.focus = focusSubject
	case focusCommand:
		m.command.Focus()
		m.subject.Blur()
		m.focus = focusCommand
	case focusEnvironment:
		m.focus = focusEnvironment
	case focusTokens:
		m.focus = focusTokens
	default:
		m.focus = m.focusBeforePalette
	}

	if status != "" {
		m.statusMessage = status
	}
	paletteDebugLog(m, "closeTokenPalette", fmt.Sprintf("focusBefore=%d", m.focusBeforePalette))
	return nil
}

func controlRuneKey(r rune) (string, bool) {
	if r < 1 || r > 26 {
		return "", false
	}
	return fmt.Sprintf("ctrl+%c", 'a'+r-1), true
}

func decodeKeyRunes(raw []rune) []rune {
	if len(raw) == 0 {
		return raw
	}
	decoded := string(raw)
	if !strings.ContainsRune(decoded, '\\') {
		return raw
	}
	unquoted, err := strconv.Unquote("\"" + decoded + "\"")
	if err != nil {
		return raw
	}
	return []rune(unquoted)
}

func (m *model) handleCancelKey() (tea.Cmd, bool) {
	if m.helpVisible {
		m.helpVisible = false
		m.restoreStatusAfterHelp()
		return nil, true
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
		return nil, true
	}
	return tea.Quit, true
}

func (m *model) handleKeyString(key string) (bool, tea.Cmd) {
	switch key {
	case "tab":
		m.toggleFocus()
		return true, nil
	case "?":
		if m.helpVisible {
			m.helpVisible = false
			m.restoreStatusAfterHelp()
		} else {
			m.statusBeforeHelp = m.statusMessage
			m.helpVisible = true
			m.statusMessage = "Help overlay open. Press ? to close."
		}
		return true, nil
	case "ctrl+l":
		m.loadSubjectFromClipboard()
		return true, nil
	case "ctrl+o":
		m.copyPreviewToClipboard()
		return true, nil
	case "ctrl+b":
		m.copyBuildCommandToClipboard()
		return true, nil
	case "ctrl+r":
		return true, m.executePreviewCommand()
	case "ctrl+p":
		if m.tokenPaletteVisible {
			return true, m.closeTokenPalette()
		}
		return true, m.openTokenPalette()
	case "ctrl+h":
		m.togglePaletteHistory()
		return true, nil
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
		return true, nil
	case "ctrl+a":
		if m.focus == focusEnvironment {
			m.setAllEnv(true)
			return true, nil
		}
		return false, nil
	case "ctrl+x":
		if m.focus == focusEnvironment {
			m.setAllEnv(false)
			return true, nil
		}
		return false, nil
	case "ctrl+y":
		m.reinsertLastResult()
		return true, nil
	case "ctrl+c":
		if cmd, handled := m.handleCancelKey(); handled {
			return true, cmd
		}
		return false, nil
	case "esc":
		if cmd, handled := m.handleCancelKey(); handled {
			return true, cmd
		}
		return false, nil
	default:
		return false, nil
	}
}

func ensureCopyHint(status string) string {

	if strings.Contains(status, "copy command") {
		return status
	}
	return status + " Type \"copy command\" to focus the copy action."
}

func (m *model) restoreStatusAfterHelp() {
	if m.tokenPaletteVisible {
		m.statusBeforeHelp = ""
		m.refreshPaletteStatus()
		return
	}
	if m.statusBeforeHelp != "" {
		m.statusMessage = m.statusBeforeHelp
		m.statusBeforeHelp = ""
		return
	}
	switch m.focus {
	case focusTokens:
		m.statusMessage = "Token controls focused. Use arrow keys to adjust; Ctrl+P opens the palette (type \"copy command\" to focus the copy action)."
	case focusSubject:
		m.statusMessage = "Subject input focused. Type directly or use Ctrl+L to load from clipboard."
	case focusCommand:
		m.statusMessage = "Command input focused. Enter runs without preview. Use Ctrl+R to pipe preview text."
	case focusEnvironment:
		if len(m.envNames) == 0 {
			m.statusMessage = "No environment variables configured."
		} else {
			m.statusMessage = "Environment allowlist focused. Use Up/Down to choose a variable and Ctrl+E to toggle it."
		}
	default:
		m.statusMessage = "Help overlay closed."
	}
	m.statusBeforeHelp = ""
}

func (m *model) refreshPaletteStatus() {
	if !m.tokenPaletteVisible {
		return
	}

	switch m.tokenPaletteFocus {
	case tokenPaletteFocusFilter:
		filter := strings.TrimSpace(m.tokenPaletteFilter.Value())
		if filter == "" {
			m.statusMessage = "Token palette open. Type to filter (try \"copy command\"), Tab cycles focus, Enter applies or copies, Ctrl+W clears the filter, Esc closes."
		} else {
			m.statusMessage = fmt.Sprintf("Token palette open (filter=\"%s\"). Enter applies or copies; type \"copy command\" to focus the copy action. Tab cycles focus, Ctrl+W clears the filter, Esc closes.", filter)
		}
	case tokenPaletteFocusCategories:
		label := ""
		if m.tokenCategoryIndex >= 0 && m.tokenCategoryIndex < len(m.tokenStates) {
			label = m.tokenStates[m.tokenCategoryIndex].category.Label
			if label == "" {
				label = m.tokenStates[m.tokenCategoryIndex].category.Key
			}
		}
		if label == "" {
			m.statusMessage = ensureCopyHint("Palette categories focused. Up/Down move categories, Tab cycles focus, Ctrl+W clears the filter, Esc closes.")
		} else {
			m.statusMessage = ensureCopyHint(fmt.Sprintf("%s category focused. Up/Down move categories, Tab cycles focus, Ctrl+W clears the filter, Esc closes.", label))
		}
	case tokenPaletteFocusOptions:
		if len(m.tokenPaletteOptions) == 0 {
			m.statusMessage = ensureCopyHint("No palette entries match the filter. Type to search or press Ctrl+W to clear, Esc closes.")
			return
		}
		if m.tokenPaletteOptionIndex < 0 || m.tokenPaletteOptionIndex >= len(m.tokenPaletteOptions) {
			m.statusMessage = ensureCopyHint("Palette options focused. Use Up/Down to choose an entry, Ctrl+W clears the filter, Esc closes.")
			return
		}
		entry := m.tokenPaletteOptions[m.tokenPaletteOptionIndex]
		switch entry {
		case tokenPaletteCopyCommandOption:
			m.statusMessage = "Copy command action focused. Press Enter to copy the current bar build CLI, Ctrl+W clears the filter, Esc closes."
		case tokenPaletteResetOption:
			m.statusMessage = ensureCopyHint("Reset-to-preset action focused. Press Enter to restore preset tokens, Ctrl+W clears the filter, Esc closes.")
		default:
			if entry < 0 {
				m.statusMessage = ensureCopyHint("Palette option focused. Press Enter to toggle selection, Ctrl+W clears the filter, Esc closes.")
				return
			}
			if m.tokenCategoryIndex < 0 || m.tokenCategoryIndex >= len(m.tokenStates) {
				m.statusMessage = ensureCopyHint("Palette option focused. Press Enter to toggle selection, Ctrl+W clears the filter, Esc closes.")
				return
			}
			state := m.tokenStates[m.tokenCategoryIndex]
			if entry >= len(state.category.Options) {
				m.statusMessage = ensureCopyHint("Palette option focused. Press Enter to toggle selection, Ctrl+W clears the filter, Esc closes.")
				return
			}
			option := state.category.Options[entry]
			categoryLabel := state.category.Label
			if categoryLabel == "" {
				categoryLabel = state.category.Key
			}
			slug := option.Slug
			if slug == "" {
				slug = option.Value
			}
			label := option.Label
			if label != "" && !strings.EqualFold(label, slug) {
				m.statusMessage = ensureCopyHint(fmt.Sprintf("%s → %s (%s). Press Enter to toggle, Ctrl+W clears the filter, Esc closes.", categoryLabel, slug, label))
			} else {
				m.statusMessage = ensureCopyHint(fmt.Sprintf("%s → %s. Press Enter to toggle, Ctrl+W clears the filter, Esc closes.", categoryLabel, slug))
			}
		}
	}
}

func (m *model) applyPaletteSelection() {
	if len(m.tokenPaletteOptions) == 0 || m.tokenPaletteOptionIndex < 0 || m.tokenPaletteOptionIndex >= len(m.tokenPaletteOptions) {
		m.statusMessage = "No token options available for the current filter."
		return
	}
	index := m.tokenPaletteOptions[m.tokenPaletteOptionIndex]
	if index == tokenPaletteCopyCommandOption {
		m.copyBuildCommandToClipboard()
		m.closeTokenPaletteWithStatus("")
		return
	}
	if index == tokenPaletteResetOption {
		m.applyPaletteReset()
		return
	}
	state := &m.tokenStates[m.tokenCategoryIndex]
	if index < 0 || index >= len(state.category.Options) {
		return
	}
	option := state.category.Options[index]
	slug := option.Slug
	if slug == "" {
		slug = option.Value
	}
	categoryLabel := state.category.Label
	if categoryLabel == "" {
		categoryLabel = state.category.Key
	}
	if state.has(option.Value) {
		m.recordTokenUndo()
		state.remove(option.Value)
		m.rebuildTokensFromStates()
		historyEntry := fmt.Sprintf("%s → %s removed", categoryLabel, slug)
		m.recordPaletteHistory(historyEntry)
		m.statusMessage = fmt.Sprintf("%s → %s removed.", state.category.Label, slug)
	} else {
		max := state.category.MaxSelections
		if max > 0 && len(state.selected) >= max {
			suffix := ""
			if max > 1 {
				suffix = "s"
			}
			m.statusMessage = fmt.Sprintf("%s already has %d selection%s; remove one before adding another.", state.category.Label, max, suffix)
			return
		}
		m.recordTokenUndo()
		state.add(option.Value, max)
		m.rebuildTokensFromStates()
		historyEntry := fmt.Sprintf("%s → %s applied", categoryLabel, slug)
		m.recordPaletteHistory(historyEntry)
		m.statusMessage = fmt.Sprintf("%s → %s applied.", state.category.Label, slug)
	}
	m.updatePaletteOptions()
}

func (m *model) applyPaletteReset() {
	presetValues := m.presetTokensForCategory(m.tokenCategoryIndex)
	if len(presetValues) == 0 {
		m.statusMessage = "Active preset has no tokens for this category."
		return
	}
	state := &m.tokenStates[m.tokenCategoryIndex]
	if tokensSliceEqual(state.selected, presetValues) {
		m.statusMessage = "Category already matches preset."
		return
	}
	m.recordTokenUndo()
	state.setSelected(presetValues, state.category.MaxSelections)
	m.rebuildTokensFromStates()
	categoryLabel := state.category.Label
	if categoryLabel == "" {
		categoryLabel = state.category.Key
	}
	m.recordPaletteHistory(fmt.Sprintf("%s reset to preset", categoryLabel))
	m.statusMessage = fmt.Sprintf("%s reset to preset.", state.category.Label)
}

func (m *model) handleTokenPaletteKey(key tea.KeyMsg) (bool, tea.Cmd) {
	if !m.tokenPaletteVisible {
		return false, nil
	}
	switch key.Type {
	case tea.KeyEsc:
		cmd := m.closeTokenPalette()
		return true, cmd
	case tea.KeyCtrlC:
		cmd := m.closeTokenPalette()
		return true, cmd
	case tea.KeyTab:
		cmd := m.advancePaletteFocus(1)
		return true, cmd
	case tea.KeyShiftTab:
		cmd := m.advancePaletteFocus(-1)
		return true, cmd
	case tea.KeyUp:
		return m.handlePaletteNavigation(-1, key)
	case tea.KeyDown:
		return m.handlePaletteNavigation(1, key)
	case tea.KeyEnter, tea.KeySpace:
		if m.tokenPaletteFocus == tokenPaletteFocusFilter {
			if len(m.tokenPaletteOptions) == 0 {
				return true, nil
			}
			m.tokenPaletteFilter.Blur()
			m.tokenPaletteFocus = tokenPaletteFocusOptions
			if m.tokenPaletteOptionIndex < 0 || m.tokenPaletteOptionIndex >= len(m.tokenPaletteOptions) {
				m.tokenPaletteOptionIndex = 0
			}
			m.refreshPaletteStatus()
			return true, nil
		}
		m.applyPaletteSelection()
		return true, nil
	case tea.KeyCtrlZ:
		m.undoTokenChange()
		return true, nil
	}

	switch key.String() {
	case "ctrl+p":
		cmd := m.closeTokenPalette()
		return true, cmd
	case "ctrl+h":
		m.togglePaletteHistory()
		return true, nil
	case "ctrl+w":
		m.clearPaletteFilter()
		return true, nil
	}

	if m.tokenPaletteFocus == tokenPaletteFocusFilter {
		updatedFilter, cmd := m.tokenPaletteFilter.Update(key)
		m.tokenPaletteFilter = updatedFilter
		m.updatePaletteOptions()
		m.refreshPaletteStatus()
		return true, cmd

	}

	return true, nil
}

func (m *model) handlePaletteNavigation(delta int, key tea.KeyMsg) (bool, tea.Cmd) {
	switch m.tokenPaletteFocus {
	case tokenPaletteFocusCategories:
		m.moveTokenCategory(delta)
		m.refreshPaletteStatus()
		return true, nil
	case tokenPaletteFocusOptions:
		if len(m.tokenPaletteOptions) == 0 {
			return true, nil
		}
		m.movePaletteOption(delta)
		return true, nil
	case tokenPaletteFocusFilter:
		updatedFilter, cmd := m.tokenPaletteFilter.Update(key)
		m.tokenPaletteFilter = updatedFilter
		m.updatePaletteOptions()
		m.refreshPaletteStatus()
		return true, cmd
	}
	return true, nil
}

func (m *model) advancePaletteFocus(delta int) tea.Cmd {
	focusValue := int(m.tokenPaletteFocus)
	total := 3
	focusValue = (focusValue + delta) % total
	if focusValue < 0 {
		focusValue += total
	}
	m.tokenPaletteFocus = tokenPaletteFocus(focusValue)

	var cmd tea.Cmd
	switch m.tokenPaletteFocus {
	case tokenPaletteFocusFilter:
		cmd = m.tokenPaletteFilter.Focus()
	case tokenPaletteFocusCategories:
		m.tokenPaletteFilter.Blur()
	case tokenPaletteFocusOptions:
		m.tokenPaletteFilter.Blur()
	}

	m.refreshPaletteStatus()
	return cmd
}

func formatTokenOptionLine(option TokenOption, selected bool, highlight bool) string {
	marker := "[ ]"
	if selected {
		marker = "[x]"
	}
	slug := option.Slug
	if slug == "" {
		slug = option.Value
	}
	label := option.Label
	prefix := "      "
	if highlight {
		prefix = "    » "
	}
	if label != "" && !strings.EqualFold(slug, label) {
		return fmt.Sprintf("%s%s %s — %s\n", prefix, marker, slug, label)
	}
	return fmt.Sprintf("%s%s %s\n", prefix, marker, slug)
}

func shortenString(input string, limit int) string {
	runes := []rune(input)
	if len(runes) <= limit {
		return input
	}
	if limit <= 1 {
		return string(runes[:limit])
	}
	return string(runes[:limit-1]) + "…"
}

func summarizeEnvList(names []string) string {
	if len(names) == 0 {
		return "env (none)"
	}
	if len(names) <= 3 {
		return "env " + strings.Join(names, ", ")
	}
	return fmt.Sprintf("env %d vars", len(names))
}

func unsetCategoryLabels(states []tokenCategoryState) []string {
	var unset []string
	for _, state := range states {
		if len(state.selected) > 0 {
			continue
		}
		label := state.category.Label
		if label == "" {
			label = state.category.Key
		}
		unset = append(unset, label)
	}
	return unset
}

func (m *model) tokensSummaryList() string {
	if len(m.tokens) == 0 {
		return "none"
	}
	return strings.Join(m.tokens, ", ")
}

func (m *model) renderFocusBreadcrumbs() string {
	labels := []struct {
		focus focusArea
		label string
	}{
		{focusSubject, "Subject"},
		{focusTokens, "Tokens"},
		{focusCommand, "Command"},
		{focusResult, "Result"},
	}

	if len(m.envNames) > 0 {
		labels = append(labels, struct {
			focus focusArea
			label string
		}{focusEnvironment, "Env"})
	}

	highlight := m.focus
	if m.tokenPaletteVisible {
		highlight = focusTokens
	}

	parts := make([]string, 0, len(labels))
	for _, item := range labels {
		display := item.label
		if item.focus == highlight {
			display = fmt.Sprintf("[%s]", strings.ToUpper(display))
		}
		parts = append(parts, display)
	}

	if len(parts) == 0 {
		return ""
	}

	return "Focus: " + strings.Join(parts, " ▸ ")
}

func (m *model) renderStatusStrip() string {
	status := strings.TrimSpace(m.statusMessage)
	if status == "" {
		status = "Ready"
	}

	parts := []string{fmt.Sprintf("Status: %s", status)}

	tokenSummary := m.tokensSummaryList()
	parts = append(parts, fmt.Sprintf("Tokens: %s", tokenSummary))

	preset := "(none)"
	if m.activePresetName != "" {
		preset = m.activePresetName
		if m.tokensDiverged() {
			preset += " (diverged)"
		}
	}
	parts = append(parts, fmt.Sprintf("Preset: %s", preset))

	commandForClipboard := joinShellArgs(m.buildCommandArgs())
	displayCommand := sanitizeShellCommand(commandForClipboard)
	if displayCommand == "" {
		displayCommand = "bar build"
	}
	parts = append(parts, fmt.Sprintf("CLI: %s", shortenString(displayCommand, 48)))

	env := "none"
	if len(m.allowedEnv) > 0 {
		env = strings.Join(m.allowedEnv, ", ")
		if len(env) > 32 {
			env = fmt.Sprintf("%d set", len(m.allowedEnv))
		}
	}
	parts = append(parts, fmt.Sprintf("Env: %s", env))

	return strings.Join(parts, " | ")
}

func (m *model) renderSummaryStrip() string {
	preset := "(none)"
	if m.activePresetName != "" {
		preset = m.activePresetName
		if m.tokensDiverged() {
			preset += " (diverged)"
		}
	}

	tokenSummary := "none"
	if len(m.tokens) > 0 {
		tokenSummary = shortenString(strings.Join(m.tokens, ", "), 40)
	}

	commandForClipboard := joinShellArgs(m.buildCommandArgs())
	displayCommand := sanitizeShellCommand(commandForClipboard)
	if displayCommand == "" {
		displayCommand = "bar build"
	}
	displayCommand = shortenString(displayCommand, 56)

	destination := m.destinationSummary
	if strings.TrimSpace(destination) == "" {
		destination = "clipboard — Ctrl+B copies CLI"
	}

	envSummary := summarizeEnvList(m.allowedEnv)
	envSummary = strings.TrimPrefix(envSummary, "env ")
	if envSummary == "" {
		envSummary = "(none)"
	}

	parts := []string{
		fmt.Sprintf("Preset: %s", preset),
		fmt.Sprintf("Tokens: %s", tokenSummary),
		fmt.Sprintf("CLI: %s", displayCommand),
		fmt.Sprintf("Destination: %s", destination),
		fmt.Sprintf("Env: %s", envSummary),
	}

	return "Summary strip: " + strings.Join(parts, " | ")
}

func (m *model) renderResultSummaryLine() string {
	if m.commandRunning {
		label := "input none"
		if m.runningMode == commandModePreview {
			label = "input preview"
		}
		env := summarizeEnvList(m.allowedEnv)
		cmd := shortenString(m.runningCommand, 48)
		if cmd == "" {
			cmd = "(blank command)"
		}
		return fmt.Sprintf("… Running %q · %s · %s · Press Esc to cancel.", cmd, label, env)
	}

	if m.lastResult.empty() {
		env := summarizeEnvList(m.allowedEnv)
		return fmt.Sprintf("∅ No command executed yet · input optional · %s", env)
	}

	cmd := shortenString(m.lastResult.Command, 48)
	if cmd == "" {
		cmd = "(blank command)"
	}
	cmdQuoted := fmt.Sprintf("%q", cmd)
	exitPart := "exit ?"
	if m.lastResult.HasExitCode {
		exitPart = fmt.Sprintf("exit %d", m.lastResult.ExitCode)
	}
	inputPart := "input none"
	if m.lastResult.UsedPreview {
		inputPart = "input preview"
	}
	env := summarizeEnvList(m.lastResult.EnvVars)
	if m.lastResult.Err != nil {
		reason := shortenString(m.lastResult.Err.Error(), 64)
		return fmt.Sprintf("✖ Command %s failed: %s · %s · %s · %s", cmdQuoted, reason, exitPart, inputPart, env)
	}
	return fmt.Sprintf("✔ Command %s completed · %s · %s · %s", cmdQuoted, exitPart, inputPart, env)
}

func (m *model) renderTokenSummary(b *strings.Builder) {
	if len(m.tokenStates) == 0 {
		if len(m.tokens) == 0 {
			b.WriteString("Tokens: (none selected)\n")
			return
		}
		b.WriteString("Tokens: " + strings.Join(m.tokens, ", ") + "\n")
		return
	}

	var selections []string
	for idx, state := range m.tokenStates {
		if len(state.selected) == 0 {
			continue
		}
		label := state.category.Label
		if label == "" {
			label = state.category.Key
		}
		var values []string
		for _, value := range state.selected {
			if ref, ok := m.tokenOptionLookup[value]; ok {
				if ref.categoryIndex == idx && ref.optionIndex >= 0 && ref.optionIndex < len(state.category.Options) {
					option := state.category.Options[ref.optionIndex]
					slug := option.Slug
					if slug == "" {
						slug = option.Value
					}
					if option.Label != "" && !strings.EqualFold(option.Label, slug) {
						values = append(values, fmt.Sprintf("%s — %s", slug, option.Label))
					} else {
						values = append(values, slug)
					}
					continue
				}
			}
			values = append(values, value)
		}
		selections = append(selections, fmt.Sprintf("%s: %s", label, strings.Join(values, ", ")))
	}

	if len(selections) == 0 {
		b.WriteString("Tokens: (none selected)\n")
	} else {
		b.WriteString("Tokens: " + strings.Join(selections, " · ") + "\n")
	}

	unset := unsetCategoryLabels(m.tokenStates)
	if len(unset) > 0 {
		b.WriteString("Unset: " + strings.Join(unset, ", ") + "\n")
	}

	if len(m.unassignedTokens) > 0 {
		b.WriteString("Other tokens: " + strings.Join(m.unassignedTokens, ", ") + "\n")
	}
}

func (m *model) renderTokenPalette(b *strings.Builder) {
	if !m.tokenPaletteVisible {
		return
	}
	summaryLine := "Token palette (Esc closes · Tab cycles focus · Enter applies option)"
	active := m.tokensSummaryList()
	if active != "" {
		summaryLine += " · Active: " + shortenString(active, 40)
	}
	unset := unsetCategoryLabels(m.tokenStates)
	if len(unset) > 0 {
		summaryLine += " · Unset: " + shortenString(strings.Join(unset, ", "), 24)
	}
	b.WriteString(summaryLine + "\n")
	filterPrefix := "    "
	if m.tokenPaletteFocus == tokenPaletteFocusFilter {
		filterPrefix = "  » "
	}
	b.WriteString(fmt.Sprintf("%sFilter: %s\n", filterPrefix, m.tokenPaletteFilter.View()))

	b.WriteString("  Categories:\n")

	for i, state := range m.tokenStates {
		prefix := "      "
		if m.tokenPaletteFocus == tokenPaletteFocusCategories && i == m.tokenCategoryIndex {
			prefix = "    » "
		}
		b.WriteString(fmt.Sprintf("%s%s\n", prefix, state.category.Label))
	}

	b.WriteString("  Options:\n")
	filterActive := strings.TrimSpace(m.tokenPaletteFilter.Value()) != ""

	if len(m.tokenPaletteOptions) == 0 {
		if filterActive {
			b.WriteString("      (no options match filter)\n")
		} else {
			b.WriteString("      (no options available)\n")
		}
		return
	}

	state := m.tokenStates[m.tokenCategoryIndex]

	for i, entry := range m.tokenPaletteOptions {
		highlight := m.tokenPaletteFocus == tokenPaletteFocusOptions && i == m.tokenPaletteOptionIndex
		if entry == tokenPaletteCopyCommandOption {
			prefix := "      "
			if highlight {
				prefix = "    » "
			}
			b.WriteString(fmt.Sprintf("%s[action] Copy bar build command\n", prefix))
			continue
		}
		if entry == tokenPaletteResetOption {
			prefix := "      "
			if highlight {
				prefix = "    » "
			}
			b.WriteString(fmt.Sprintf("%s[reset] Reset to preset\n", prefix))
			continue
		}

		if entry < 0 || entry >= len(state.category.Options) {
			continue
		}
		option := state.category.Options[entry]
		selected := state.has(option.Value)
		line := formatTokenOptionLine(option, selected, highlight)
		b.WriteString(line)
	}
}

func (m *model) renderTokenViewportContent() string {
	var builder strings.Builder

	if m.tokenPaletteVisible {
		var paletteBuilder strings.Builder
		m.renderTokenPalette(&paletteBuilder)
		paletteContent := paletteBuilder.String()
		builder.WriteString(paletteContent)
		if !strings.HasSuffix(paletteContent, "\n") {
			builder.WriteString("\n")
		}
		m.renderTokenSummary(&builder)
	} else {
		m.renderTokenSummary(&builder)
		m.renderTokenPalette(&builder)
	}

	return strings.TrimRight(builder.String(), "\n")
}

func (m *model) updateTokenViewportContent() {
	m.tokenViewport.SetContent(m.renderTokenViewportContent())
}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	defer func() {
		(&m).updateTokenViewportContent()
	}()

	switch typed := msg.(type) {
	case commandFinishedMsg:
		m.commandRunning = false
		m.runningCommand = ""
		m.runningMode = commandModeSubject
		m.cancelCommand = nil
		m.lastResult = typed.result
		m.recordCommandHistory(typed.result, typed.mode)

		if errors.Is(typed.result.Err, context.Canceled) {
			m.statusMessage = "Command cancelled."
			m.updateResultViewportContent()
			return m, nil
		}
		if typed.result.Err != nil {
			m.statusMessage = fmt.Sprintf("Command failed: %v", typed.result.Err)
			m.updateResultViewportContent()
			return m, nil
		}

		if typed.mode == commandModeSubject {
			trimmed := strings.TrimRight(typed.result.Stdout, "\n")
			(&m).requestSubjectReplacement("command stdout", trimmed)
		} else {
			m.statusMessage = ensureCopyHint("Command completed; inspect result pane. Use Ctrl+Y to insert stdout into the subject.")
		}
		m.updateResultViewportContent()

		return m, nil
	case tea.WindowSizeMsg:
		paletteDebugLog(&m, "WindowSize", fmt.Sprintf("width=%d height=%d", typed.Width, typed.Height))
		(&m).handleWindowSize(typed)
		return m, nil
	}

	if keyMsg, ok := msg.(tea.KeyMsg); ok {
		decodedRunes := decodeKeyRunes(keyMsg.Runes)
		paletteDebugLog(&m, "UpdateKey", fmt.Sprintf("key=%q type=%v len=%d runes=%v decoded=%q palette=%t focus=%d", keyMsg.String(), keyMsg.Type, len(keyMsg.Runes), keyMsg.Runes, string(decodedRunes), m.tokenPaletteVisible, m.focus))
		if handled, cmd := (&m).handleSubjectReplacementKey(keyMsg); handled {
			if cmd != nil {
				return m, cmd
			}
			return m, nil
		}
		if (&m).handleSubjectViewportKey(keyMsg) {
			return m, nil
		}
		if (&m).handleResultViewportKey(keyMsg) {
			return m, nil
		}
		if (&m).handleTokenViewportKey(keyMsg) {
			return m, nil
		}
		if handled, cmd := m.handlePresetPaneKey(keyMsg); handled {
			if cmd != nil {
				return m, cmd
			}
			return m, nil
		}
		if handled, cmd := m.handleTokenPaletteKey(keyMsg); handled {
			if cmd != nil {
				return m, cmd
			}
			return m, nil
		}
		if keyMsg.Type == tea.KeyRunes && len(decodedRunes) > 0 {
			handledRunes := false
			var seqCmds []tea.Cmd
			for _, r := range decodedRunes {
				if r == '\t' {
					if handled, cmd := m.handleKeyString("tab"); handled {
						handledRunes = true
						if cmd != nil {
							seqCmds = append(seqCmds, cmd)
						}
					}
					continue
				}
				if ctrlKey, ok := controlRuneKey(r); ok {
					if handled, cmd := m.handleKeyString(ctrlKey); handled {
						handledRunes = true
						if cmd != nil {
							seqCmds = append(seqCmds, cmd)
						}
					}
				}
			}
			if handledRunes {
				if len(seqCmds) > 0 {
					return m, tea.Batch(seqCmds...)
				}
				return m, nil
			}
		}
		switch keyMsg.Type {
		case tea.KeyCtrlC, tea.KeyEsc:
			if cmd, handled := m.handleCancelKey(); handled {
				if cmd != nil {
					return m, cmd
				}
				return m, nil
			}
		case tea.KeyTab:
			if handled, cmd := m.handleKeyString("tab"); handled {
				if cmd != nil {
					return m, cmd
				}
				return m, nil
			}
		case tea.KeyEnter:
			if m.focus == focusCommand {
				return m, (&m).executeSubjectCommand()
			}
			if m.focus == focusTokens {
				m.toggleCurrentTokenOption()
				return m, nil
			}
			if m.focus == focusEnvironment {
				m.toggleSelectedEnv()
				return m, nil
			}
		case tea.KeySpace:
			if m.focus == focusTokens {
				m.toggleCurrentTokenOption()
				return m, nil
			}
		case tea.KeyUp:
			if m.focus == focusTokens {
				m.moveTokenOption(-1)
				return m, nil
			}
			if m.focus == focusEnvironment {
				m.moveEnvSelection(-1)
				return m, nil
			}
		case tea.KeyDown:
			if m.focus == focusTokens {
				m.moveTokenOption(1)
				return m, nil
			}
			if m.focus == focusEnvironment {
				m.moveEnvSelection(1)
				return m, nil
			}
		case tea.KeyLeft:
			if m.focus == focusTokens {
				m.moveTokenCategory(-1)
				return m, nil
			}
		case tea.KeyRight:
			if m.focus == focusTokens {
				m.moveTokenCategory(1)
				return m, nil
			}
		case tea.KeyDelete, tea.KeyBackspace:
			if m.focus == focusTokens {
				m.removeCurrentTokenOption()
				return m, nil
			}
			if m.focus == focusEnvironment {
				m.setAllEnv(false)
				return m, nil
			}
		case tea.KeyCtrlZ:
			if m.focus == focusTokens || m.tokenPaletteVisible {
				m.undoTokenChange()
				return m, nil
			}
			if m.focus == focusSubject {
				(&m).undoSubjectReplacement()
				return m, nil
			}

			if m.focus == focusEnvironment {
				m.moveEnvSelection(1)
				return m, nil
			}

		}

		if handled, cmd := m.handleKeyString(keyMsg.String()); handled {
			if cmd != nil {
				return m, cmd
			}
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
		m.subjectUndoAvailable = false
		m.refreshPreview()
	}
	m.updateSubjectViewportContent()

	newCommand, commandCmd := m.command.Update(msg)
	if commandCmd != nil {
		cmds = append(cmds, commandCmd)
	}
	m.command = newCommand

	if _, isKey := msg.(tea.KeyMsg); !isKey && m.presetPaneVisible && m.presetMode == presetModeSaving {
		var inputCmd tea.Cmd
		m.presetNameInput, inputCmd = m.presetNameInput.Update(msg)
		if inputCmd != nil {
			cmds = append(cmds, inputCmd)
		}
		m.presetDescriptionInput, inputCmd = m.presetDescriptionInput.Update(msg)
		if inputCmd != nil {
			cmds = append(cmds, inputCmd)
		}
	}

	return m, tea.Batch(cmds...)
}

func (m *model) handleSubjectReplacementKey(key tea.KeyMsg) (bool, tea.Cmd) {
	if m.pendingSubject == nil {
		return false, nil
	}

	switch key.Type {
	case tea.KeyEnter:
		m.applyPendingSubjectReplacement()
		return true, nil
	case tea.KeyEsc, tea.KeyCtrlC:
		m.cancelPendingSubjectReplacement()
		return true, nil
	case tea.KeyCtrlZ:
		m.cancelPendingSubjectReplacement()
		return true, nil
	}

	if key.String() == "?" {
		return false, nil
	}

	m.statusMessage = ensureCopyHint(m.pendingSubject.message)
	return true, nil
}

func (m *model) requestSubjectReplacement(source, newValue string) {
	previous := m.subject.Value()
	if strings.TrimRight(newValue, "\r\n") == strings.TrimRight(previous, "\r\n") {
		m.pendingSubject = nil
		m.statusMessage = ensureCopyHint(fmt.Sprintf("Subject already matches %s.", source))
		return
	}

	m.pendingSubject = newSubjectReplacementPrompt(source, previous, newValue)
	m.statusMessage = ensureCopyHint(m.pendingSubject.message)
}

func (m *model) applyPendingSubjectReplacement() {
	if m.pendingSubject == nil {
		return
	}

	prompt := m.pendingSubject
	m.pendingSubject = nil
	m.subjectUndoValue = prompt.previousValue
	m.subjectUndoSource = prompt.source
	m.subjectUndoAvailable = true
	m.subject.SetValue(prompt.newValue)
	m.updateSubjectViewportContent()
	m.refreshPreview()
	m.statusMessage = ensureCopyHint(fmt.Sprintf("Subject replaced with %s. Press Ctrl+Z to undo.", prompt.source))
	m.recordPaletteHistory(fmt.Sprintf("Subject replaced via %s", prompt.source))
}

func (m *model) cancelPendingSubjectReplacement() {
	if m.pendingSubject == nil {
		return
	}

	source := m.pendingSubject.source
	m.pendingSubject = nil
	m.statusMessage = ensureCopyHint(fmt.Sprintf("%s replacement cancelled.", source))
}

func (m *model) undoSubjectReplacement() {
	if !m.subjectUndoAvailable {
		m.statusMessage = ensureCopyHint("No subject replacement to undo.")
		return
	}

	m.subject.SetValue(m.subjectUndoValue)
	m.updateSubjectViewportContent()
	m.refreshPreview()
	m.subjectUndoAvailable = false
	source := m.subjectUndoSource

	if source == "" {
		source = "recent"
	}
	m.statusMessage = ensureCopyHint(fmt.Sprintf("Subject restored after %s replacement.", source))
	m.recordPaletteHistory(fmt.Sprintf("Subject undo (%s)", source))
}

func (m model) View() string {
	paletteDebugLog(&m, "View", "")
	var b strings.Builder
	b.WriteString("bar prompt editor (Bubble Tea prototype)\n\n")

	if m.pendingSubject != nil {
		prompt := m.pendingSubject
		b.WriteString(fmt.Sprintf("Pending subject replacement from %s: %q (new %d chars, was %d). Enter confirms, Esc cancels.\n", prompt.source, prompt.snippet, prompt.newLength, prompt.previousLength))
	}

	statusStrip := m.renderStatusStrip()
	if statusStrip != "" {
		b.WriteString(statusStrip)
		b.WriteString("\n\n")
	}

	breadcrumbs := m.renderFocusBreadcrumbs()
	if breadcrumbs != "" {
		b.WriteString(breadcrumbs)
		b.WriteString("\n\n")
	}

	summaryStrip := m.renderSummaryStrip()
	if summaryStrip != "" {
		b.WriteString(summaryStrip)
		b.WriteString("\n\n")
	}

	if m.helpVisible {
		b.WriteString("Help overlay (press ? to close):\n")
		b.WriteString("  Inputs:\n")
		b.WriteString("    • Subject focus — Type directly; Ctrl+L loads clipboard; Ctrl+O copies preview; Ctrl+B copies CLI; Ctrl+Z undoes subject replacement.\n")
		b.WriteString("    • Subject viewport — PgUp/PgDn scroll; Home/End jump.\n")
		b.WriteString("    • Command focus — Enter runs command; Ctrl+R pipes preview; Ctrl+Y inserts stdout; blank command skips execution.\n")
		b.WriteString("    • Result viewport — PgUp/PgDn scroll; Home/End jump; Ctrl+T toggles condensed preview.\n")
		b.WriteString("  Tokens:\n")
		b.WriteString("    • Tab focuses tokens; Left/Right change categories; Up/Down browse options; Enter/Space toggles; Delete removes; Ctrl+P opens palette; Ctrl+Z undoes last change.\n")
		b.WriteString("  Palette:\n")
		b.WriteString("    • Type category=value to filter/apply; Tab cycles columns; Shift+Tab reverses; Enter applies staged edits; Ctrl+W clears filter.\n")
		b.WriteString("  Presets:\n")
		b.WriteString("    • Ctrl+S toggles pane; Ctrl+N starts save; Delete removes; Ctrl+Z undoes last preset change.\n")
		b.WriteString("  Environment:\n")
		b.WriteString("    • Tab focuses list; Up/Down move; Ctrl+E toggles; Ctrl+A enables all; Ctrl+X clears allowlist.\n")
		b.WriteString("  Command lifecycle:\n")
		b.WriteString("    • Enter executes; Ctrl+C cancels running commands; follow on-screen prompts for stdout reinsertion.\n")
		b.WriteString("  Exit & help:\n")
		b.WriteString("    • Esc closes overlays (help → palette → prompts) then exits; press ? anytime to toggle this reference.\n\n")
	}

	b.WriteString("Subject (PgUp/PgDn scroll · Home/End jump):\n")
	b.WriteString(m.subjectViewport.View())
	b.WriteString("\n\n")

	b.WriteString("Command (Enter runs without preview):\n")
	b.WriteString(m.command.View())
	b.WriteString("\n\n")

	b.WriteString("Hint: press ? for shortcut help · Ctrl+P toggles the palette · Leave command blank to opt out.\n\n")

	b.WriteString("Result summary:\n")
	b.WriteString(m.renderResultSummaryLine())
	b.WriteString("\n\n")

	b.WriteString("Result & preview (PgUp/PgDn scroll · Home/End jump · Ctrl+T toggle condensed preview):\n")
	b.WriteString(m.resultViewport.View())
	b.WriteString("\n")

	localTokenViewport := m.tokenViewport
	localTokenViewport.SetContent(m.renderTokenViewportContent())
	tokenSection := localTokenViewport.View()
	b.WriteString(tokenSection)
	if tokenSection != "" && !strings.HasSuffix(tokenSection, "\n") {
		b.WriteString("\n")
	}
	if tokenSection != "" {
		b.WriteString("\n")
	}

	if m.paletteHistoryVisible {
		b.WriteString("Palette history (Ctrl+H toggles):\n")
		if len(m.paletteHistory) == 0 {
			b.WriteString("  (empty)\n\n")
		} else {
			for _, entry := range m.paletteHistory {
				b.WriteString(fmt.Sprintf("  • %s\n", entry))
			}
			b.WriteString("\n")
		}
	}

	if m.presetPaneVisible {
		m.renderPresetPane(&b)
	}

	b.WriteString("Press Ctrl+C or Esc to exit.\n")
	output := b.String()
	paletteDebugViewSummary(&m, output)
	return output
}

func (m *model) toggleFocus() {
	switch m.focus {
	case focusSubject:
		m.subject.Blur()
		if len(m.tokenStates) > 0 {
			m.focus = focusTokens
			m.clampTokenOptionIndex()
			m.statusMessage = "Token controls focused. Use arrow keys to adjust; Ctrl+P opens the palette (type \"copy command\" to focus the copy action)."
			return
		}
		m.command.Focus()
		m.focus = focusCommand
		m.statusMessage = "Command input focused. Enter runs without preview. Use Ctrl+R to pipe preview text."
	case focusTokens:
		m.focus = focusCommand
		m.command.Focus()
		m.statusMessage = "Command input focused. Enter runs without preview. Use Ctrl+R to pipe preview text."
	case focusCommand:
		m.command.Blur()
		m.focus = focusResult
		m.statusMessage = "Result viewport focused. Use PgUp/PgDn to scroll, Home/End to jump, Ctrl+T toggles preview."
	case focusResult:
		if len(m.envNames) > 0 {
			m.focus = focusEnvironment
			m.ensureEnvSelection()
			m.statusMessage = "Environment allowlist focused. Use Up/Down to choose a variable and Ctrl+E to toggle it."
			return
		}
		m.subject.Focus()
		m.focus = focusSubject
		m.statusMessage = "Subject input focused. Type directly or use Ctrl+L to load from clipboard."
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

func cloneStrings(in []string) []string {
	if len(in) == 0 {
		return nil
	}
	out := make([]string, len(in))
	copy(out, in)
	return out
}

func tokensEqual(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func (m *model) tokensDiverged() bool {
	if m.activePresetName == "" {
		return false
	}
	return !tokensEqual(m.activePresetTokens, m.tokens)
}

func (m *model) setTokens(tokens []string) {
	m.tokens = cloneStrings(tokens)
	if len(m.tokenStates) > 0 {
		m.resetTokenStatesFromTokens(m.tokens)
		m.clampTokenOptionIndex()
		m.updatePaletteOptions()
	}
	m.refreshPreview()
}

func (m *model) refreshPreview() {
	defer m.updateResultViewportContent()

	if m.previewFunc == nil {
		m.preview = ""
		m.previewErr = fmt.Errorf("preview unavailable")
		return
	}

	preview, err := m.previewFunc(m.subject.Value(), m.tokens)
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
	m.requestSubjectReplacement("clipboard text", text)
}

func (m *model) copyPreviewToClipboard() {
	if err := m.clipboardWrite(m.preview); err != nil {
		m.statusMessage = fmt.Sprintf("Clipboard write failed: %v", err)
		return
	}
	m.destinationSummary = "clipboard — Preview copied"
	m.statusMessage = "Copied preview to clipboard."
	m.recordPaletteHistory("Clipboard → preview copied")
}

func (m *model) copyBuildCommandToClipboard() {
	command := joinShellArgs(m.buildCommandArgs())
	if err := m.clipboardWrite(command); err != nil {
		m.statusMessage = fmt.Sprintf("Clipboard write failed: %v", err)
		return
	}
	m.destinationSummary = "clipboard — CLI command copied"
	m.statusMessage = "Copied bar build command to clipboard."
	m.recordPaletteHistory("Clipboard → CLI command copied")
}

func (m *model) buildCommandArgs() []string {
	args := []string{"bar", "build"}
	for _, token := range m.tokens {
		trimmed := strings.TrimSpace(token)
		if trimmed == "" {
			continue
		}
		args = append(args, trimmed)
	}
	subject := m.subject.Value()
	if subject != "" {
		args = append(args, "--prompt", subject)
	}
	return args
}

func joinShellArgs(args []string) string {
	if len(args) == 0 {
		return ""
	}
	quoted := make([]string, len(args))
	for i, arg := range args {
		quoted[i] = shellQuote(arg)
	}
	return strings.Join(quoted, " ")
}

func shellQuote(arg string) string {
	if arg == "" {
		return "''"
	}
	if !shellNeedsQuoting(arg) {
		return arg
	}
	replaced := strings.ReplaceAll(arg, "'", "'\"'\"'")
	return "'" + replaced + "'"
}

func shellNeedsQuoting(arg string) bool {
	for _, r := range arg {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			continue
		}
		switch r {
		case '-', '_', '.', '/', '=', ':', '@':
			continue
		}
		return true
	}
	return false
}

func sanitizeShellCommand(command string) string {
	if command == "" {
		return command
	}
	replaced := strings.ReplaceAll(command, "\n", "\\n")
	replaced = strings.ReplaceAll(replaced, "\r", "\\r")
	return replaced
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
			m.statusMessage = ensureCopyHint(fmt.Sprintf("Running %q with preview input and env %s… Press Esc to cancel.", command, envSummary))
		} else {
			m.statusMessage = ensureCopyHint(fmt.Sprintf("Running %q with preview input… Press Esc to cancel.", command))
		}
	} else {
		if len(m.allowedEnv) > 0 {
			m.statusMessage = ensureCopyHint(fmt.Sprintf("Running %q with env %s… Press Esc to cancel.", command, envSummary))
		} else {
			m.statusMessage = ensureCopyHint(fmt.Sprintf("Running %q… Press Esc to cancel.", command))
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
		exitCode, hasExitCode := exitCodeFromError(err)
		return commandFinishedMsg{
			result: commandResult{
				Command:     command,
				Stdout:      stdout,
				Stderr:      stderr,
				Err:         err,
				UsedPreview: mode == commandModePreview,
				EnvVars:     allowedEnv,
				ExitCode:    exitCode,
				HasExitCode: hasExitCode,
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
	m.requestSubjectReplacement("command stdout", trimmed)
}

func (m *model) refreshPresetSummaries() error {
	summaries, err := m.listPresets()
	if err != nil {
		m.presetSummaries = nil
		m.presetSelection = -1
		return err
	}
	m.presetSummaries = summaries
	if len(m.presetSummaries) == 0 {
		m.presetSelection = -1
		return nil
	}
	if m.presetSelection < 0 || m.presetSelection >= len(m.presetSummaries) {
		m.presetSelection = 0
	}
	return nil
}

func (m *model) openPresetPane() {
	if !m.presetPaneVisible {
		m.focusBeforePane = m.focus
	}
	m.presetPaneVisible = true
	m.presetMode = presetModeList
	m.pendingDeleteName = ""
	m.presetNameInput.Blur()
	m.presetDescriptionInput.Blur()
	if err := m.refreshPresetSummaries(); err != nil {
		m.statusMessage = fmt.Sprintf("List presets failed: %v", err)
	} else if len(m.presetSummaries) == 0 {
		m.statusMessage = "Preset pane open. No presets found."
	} else {
		m.statusMessage = "Preset pane open. Use Up/Down to select, Enter to load, Ctrl+N to save, Delete to remove."
	}
}

func (m *model) closePresetPane() {
	m.presetPaneVisible = false
	m.presetMode = presetModeList
	m.pendingDeleteName = ""
	m.presetNameInput.Blur()
	m.presetDescriptionInput.Blur()
	m.presetNameInput.SetValue("")
	m.presetDescriptionInput.SetValue("")
	m.statusMessage = "Preset pane closed."
	switch m.focusBeforePane {
	case focusCommand:
		m.command.Focus()
		m.subject.Blur()
	case focusEnvironment:
		m.focus = focusEnvironment
		return
	default:
		m.subject.Focus()
		m.command.Blur()
	}
	m.focus = m.focusBeforePane
}

func (m *model) movePresetSelection(delta int) {
	if len(m.presetSummaries) == 0 {
		return
	}
	m.presetSelection = (m.presetSelection + delta) % len(m.presetSummaries)
	if m.presetSelection < 0 {
		m.presetSelection += len(m.presetSummaries)
	}
	selected := m.presetSummaries[m.presetSelection]
	m.statusMessage = fmt.Sprintf("Preset %q selected.%s", selected.Name, formatPresetDivergenceHint(selected.Name, m.activePresetName))
}

func formatPresetDivergenceHint(selected, active string) string {
	if active == "" {
		return ""
	}
	if selected == active {
		return " (active)"
	}
	return ""
}

func (m *model) currentPresetSummary() (PresetSummary, bool) {
	if m.presetSelection < 0 || m.presetSelection >= len(m.presetSummaries) {
		return PresetSummary{}, false
	}
	return m.presetSummaries[m.presetSelection], true
}

func (m *model) setActivePreset(name string, tokens []string) {
	m.activePresetName = name
	m.activePresetTokens = cloneStrings(tokens)
	m.lastDeletedPreset = nil
	m.lastDeletedDescription = ""
}

func (m *model) applyPreset(name string) {
	details, err := m.loadPreset(name)
	if err != nil {
		m.statusMessage = fmt.Sprintf("Load preset failed: %v", err)
		return
	}
	m.setTokens(details.Tokens)
	m.setActivePreset(details.Name, details.Tokens)
	m.statusMessage = fmt.Sprintf("Preset %q applied.", details.Name)
}

func (m *model) enterPresetSaveMode() {
	m.presetMode = presetModeSaving
	m.presetNameInput.SetValue(m.suggestPresetName())
	m.presetDescriptionInput.SetValue("")
	m.presetNameInput.Focus()
	m.presetDescriptionInput.Blur()
	m.statusMessage = "Enter a preset name (and optional description). Press Enter to save or Esc to cancel."
}

func (m *model) cancelPresetSave() {
	m.presetMode = presetModeList
	m.presetNameInput.Blur()
	m.presetDescriptionInput.Blur()
	m.presetNameInput.SetValue("")
	m.presetDescriptionInput.SetValue("")
	m.statusMessage = "Preset save cancelled."
}

func (m *model) submitPresetSave() {
	name := strings.TrimSpace(m.presetNameInput.Value())
	description := strings.TrimSpace(m.presetDescriptionInput.Value())
	if name == "" {
		m.statusMessage = "Preset name required."
		return
	}
	details, err := m.savePreset(name, description, m.tokens)
	if err != nil {
		m.statusMessage = fmt.Sprintf("Save preset failed: %v", err)
		return
	}
	m.setActivePreset(details.Name, details.Tokens)
	if err := m.refreshPresetSummaries(); err != nil {
		m.statusMessage = fmt.Sprintf("List presets failed: %v", err)
	} else {
		m.selectPresetByName(details.Name)
	}
	m.presetMode = presetModeList
	m.presetNameInput.Blur()
	m.presetDescriptionInput.Blur()
	m.presetNameInput.SetValue("")
	m.presetDescriptionInput.SetValue("")
	if description != "" {
		m.statusMessage = fmt.Sprintf("Preset %q saved (%s).", details.Name, description)
	} else {
		m.statusMessage = fmt.Sprintf("Preset %q saved.", details.Name)
	}
}

func (m *model) selectPresetByName(name string) {
	for i, summary := range m.presetSummaries {
		if summary.Name == name {
			m.presetSelection = i
			return
		}
	}
}

func (m *model) startPresetDelete() {
	summary, ok := m.currentPresetSummary()
	if !ok {
		m.statusMessage = "No preset selected to delete."
		return
	}
	m.presetMode = presetModeConfirmDelete
	m.pendingDeleteName = summary.Name
	m.statusMessage = fmt.Sprintf("Delete preset %q? Press Enter to confirm or Esc to cancel.", summary.Name)
}

func (m *model) cancelPresetDelete() {
	m.presetMode = presetModeList
	m.pendingDeleteName = ""
	m.statusMessage = "Preset deletion cancelled."
}

func (m *model) confirmPresetDelete() {
	name := m.pendingDeleteName
	if name == "" {
		m.presetMode = presetModeList
		return
	}
	details, err := m.loadPreset(name)
	if err != nil {
		m.statusMessage = fmt.Sprintf("Load preset failed: %v", err)
		m.presetMode = presetModeList
		m.pendingDeleteName = ""
		return
	}
	if err := m.deletePreset(name); err != nil {
		m.statusMessage = fmt.Sprintf("Delete preset failed: %v", err)
		m.presetMode = presetModeList
		m.pendingDeleteName = ""
		return
	}
	m.lastDeletedPreset = &details
	m.lastDeletedDescription = ""
	m.pendingDeleteName = ""
	m.presetMode = presetModeList
	if err := m.refreshPresetSummaries(); err != nil {
		m.statusMessage = fmt.Sprintf("List presets failed: %v", err)
	} else {
		m.presetSelection = -1
		if len(m.presetSummaries) > 0 {
			m.presetSelection = 0
		}
	}
	if m.activePresetName == details.Name {
		m.activePresetName = ""
		m.activePresetTokens = nil
	}
	m.statusMessage = fmt.Sprintf("Preset %q deleted. Press Ctrl+Z to undo.", details.Name)
}

func (m *model) undoLastDeletedPreset() {
	if m.lastDeletedPreset == nil {
		m.statusMessage = "No preset deletion to undo."
		return
	}
	details := *m.lastDeletedPreset
	if _, err := m.savePreset(details.Name, m.lastDeletedDescription, details.Tokens); err != nil {
		m.statusMessage = fmt.Sprintf("Undo delete failed: %v", err)
		return
	}
	if err := m.refreshPresetSummaries(); err != nil {
		m.statusMessage = fmt.Sprintf("List presets failed: %v", err)
	} else {
		m.selectPresetByName(details.Name)
	}
	m.lastDeletedPreset = nil
	m.lastDeletedDescription = ""
	m.statusMessage = fmt.Sprintf("Preset %q restored.", details.Name)
}

func (m *model) suggestPresetName() string {
	if m.activePresetName != "" {
		return m.activePresetName
	}
	return ""
}

func (m *model) handlePresetPaneKey(key tea.KeyMsg) (bool, tea.Cmd) {
	if key.Type == tea.KeyCtrlS && !m.presetPaneVisible {
		m.openPresetPane()
		return true, nil
	}
	if !m.presetPaneVisible {
		return false, nil
	}

	switch key.Type {
	case tea.KeyCtrlC, tea.KeyEsc:
		if m.presetMode == presetModeSaving {
			m.cancelPresetSave()
		} else if m.presetMode == presetModeConfirmDelete {
			m.cancelPresetDelete()
		} else {
			m.closePresetPane()
		}
		return true, nil
	case tea.KeyCtrlS:
		if m.presetMode == presetModeSaving {
			m.submitPresetSave()
			return true, nil
		}
		if m.presetMode == presetModeConfirmDelete {
			return true, nil
		}
		m.closePresetPane()
		return true, nil
	case tea.KeyCtrlN:
		if m.presetMode == presetModeList {
			m.enterPresetSaveMode()
		}
		return true, nil
	case tea.KeyCtrlZ:
		m.undoLastDeletedPreset()
		return true, nil
	case tea.KeyEnter:
		switch m.presetMode {
		case presetModeSaving:
			m.submitPresetSave()
		case presetModeConfirmDelete:
			m.confirmPresetDelete()
		default:
			if summary, ok := m.currentPresetSummary(); ok {
				m.applyPreset(summary.Name)
			}
		}
		return true, nil
	case tea.KeyUp:
		if m.presetMode == presetModeList && len(m.presetSummaries) > 0 {
			m.movePresetSelection(-1)
		}
		return true, nil
	case tea.KeyDown, tea.KeyTab:
		if m.presetMode == presetModeList && len(m.presetSummaries) > 0 {
			m.movePresetSelection(1)
		}
		return true, nil
	case tea.KeyDelete, tea.KeyBackspace:
		if m.presetMode == presetModeList {
			m.startPresetDelete()
		}
		return true, nil
	}

	if m.presetMode == presetModeSaving {
		var cmds []tea.Cmd
		var cmd tea.Cmd
		m.presetNameInput, cmd = m.presetNameInput.Update(key)
		if cmd != nil {
			cmds = append(cmds, cmd)
		}
		m.presetDescriptionInput, cmd = m.presetDescriptionInput.Update(key)
		if cmd != nil {
			cmds = append(cmds, cmd)
		}
		if len(cmds) > 0 {
			return true, tea.Batch(cmds...)
		}
		return true, nil
	}

	return true, nil
}

func (m *model) renderPresetPane(b *strings.Builder) {
	b.WriteString("Preset pane (Ctrl+S closes, Ctrl+N save, Delete delete, Ctrl+Z undo).\n")
	if len(m.presetSummaries) == 0 {
		b.WriteString("  (no presets found)\n")
	} else {
		for i, summary := range m.presetSummaries {
			cursor := " "
			if i == m.presetSelection {
				cursor = ">"
			}
			state := ""
			if summary.Name == m.activePresetName {
				if m.tokensDiverged() {
					state = " [active, diverged]"
				} else {
					state = " [active]"
				}
			}
			b.WriteString(fmt.Sprintf("  %s %s%s\n", cursor, summary.Name, state))
			b.WriteString(fmt.Sprintf("    saved %s | static=%s | voice=%s | audience=%s | tone=%s\n",
				formatPresetTime(summary.SavedAt),
				safeValue(summary.Static),
				safeValue(summary.Voice),
				safeValue(summary.Audience),
				safeValue(summary.Tone)))
		}
	}
	if m.presetMode == presetModeSaving {
		b.WriteString("\n  Save preset\n")
		b.WriteString("    Name: " + m.presetNameInput.View() + "\n")
		b.WriteString("    Description: " + m.presetDescriptionInput.View() + "\n")
		b.WriteString("    Press Enter to save or Esc to cancel.\n")
	}
	if m.presetMode == presetModeConfirmDelete {
		b.WriteString(fmt.Sprintf("\n  Confirm delete %q (Enter to confirm, Esc to cancel).\n", m.pendingDeleteName))
	}
	b.WriteString("\n")
}

func safeValue(input string) string {
	trimmed := strings.TrimSpace(input)
	if trimmed == "" {
		return "(none)"
	}
	return trimmed
}

func formatPresetTime(t time.Time) string {
	if t.IsZero() {
		return "(unknown)"
	}
	return t.UTC().Format(time.RFC3339)
}

// Snapshot renders the current view and preview without starting an interactive program.
func Snapshot(opts Options, subject string) (view string, preview string, err error) {
	opts = applyDefaults(opts)
	if opts.Preview == nil {
		return "", "", fmt.Errorf("preview function is required")
	}

	model := newModel(opts)
	model.subject.SetValue(subject)
	model.updateSubjectViewportContent()
	model.refreshPreview()
	return model.View(), model.preview, nil
}
