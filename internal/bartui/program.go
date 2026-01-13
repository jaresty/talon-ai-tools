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

	"math"

	textarea "github.com/charmbracelet/bubbles/textarea"
	textinput "github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	lipgloss "github.com/charmbracelet/lipgloss"
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

type historyEventKind string

type historyEvent struct {
	Kind      historyEventKind
	Message   string
	Command   string
	Timestamp time.Time
}

type shortcutEntry struct {
	Keys        string
	Description string
}

type shortcutSection struct {
	Title   string
	Entries []shortcutEntry
}

const shortcutReferenceDialogID = "shortcut-reference"

type dialog interface {
	ID() string
	Init() tea.Cmd
	Update(tea.Msg) (dialog, tea.Cmd, bool)
	View(width int, height int) string
}

type dialogManager struct {
	dialogs []dialog
}

func (dm *dialogManager) open(d dialog) tea.Cmd {
	if d == nil {
		return nil
	}
	if dm.has(d.ID()) {
		return nil
	}
	dm.dialogs = append(dm.dialogs, d)
	return d.Init()
}

func (dm *dialogManager) close(id string) bool {
	for idx, dlg := range dm.dialogs {
		if dlg.ID() == id {
			dm.dialogs = append(dm.dialogs[:idx], dm.dialogs[idx+1:]...)
			return true
		}
	}
	return false
}

func (dm *dialogManager) closeTop() (string, bool) {
	if len(dm.dialogs) == 0 {
		return "", false
	}
	idx := len(dm.dialogs) - 1
	id := dm.dialogs[idx].ID()
	dm.dialogs = dm.dialogs[:idx]
	return id, true
}

func (dm *dialogManager) has(id string) bool {
	for _, dlg := range dm.dialogs {
		if dlg.ID() == id {
			return true
		}
	}
	return false
}

func (dm *dialogManager) top() (dialog, bool) {
	if len(dm.dialogs) == 0 {
		return nil, false
	}
	return dm.dialogs[len(dm.dialogs)-1], true
}

func (dm *dialogManager) update(msg tea.Msg) (tea.Cmd, bool, string) {
	if len(dm.dialogs) == 0 {
		return nil, false, ""
	}
	idx := len(dm.dialogs) - 1
	top := dm.dialogs[idx]
	updated, cmd, handled := top.Update(msg)
	if updated == nil {
		id := top.ID()
		dm.dialogs = dm.dialogs[:idx]
		return cmd, true, id
	}
	dm.dialogs[idx] = updated
	return cmd, handled, ""
}

type sidebarPreference int

const (
	sidebarPreferenceShown sidebarPreference = iota
	sidebarPreferenceHidden
)

const (
	historyEventKindTokens    historyEventKind = "Tokens"
	historyEventKindClipboard historyEventKind = "Clipboard"
	historyEventKindCommand   historyEventKind = "Command"
	historyEventKindSubject   historyEventKind = "Subject"
	historyEventKindPreset    historyEventKind = "Preset"
)

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
		m.isShortcutReferenceVisible(),
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

type viewportMode int

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

const (
	viewportModeNormal viewportMode = iota
	viewportModeSubject
	viewportModeResult
)

const tokenSparklineWindow = 12
const toastLifetime = 1500 * time.Millisecond
const historyHighlightLifetime = 2 * time.Second

// composerTheme centralizes the Lip Gloss palette for ADR 0072 so toast overlays
// and sidebar typography reinforce the CLI grammar cues across dark and light
// terminals.
var composerTheme = newGrammarComposerTheme()

type grammarComposerTheme struct {
	toastForeground           lipgloss.AdaptiveColor
	toastStyle                lipgloss.Style
	sectionHeaderForeground   lipgloss.AdaptiveColor
	sectionHeaderStyle        lipgloss.Style
	sectionHintForeground     lipgloss.AdaptiveColor
	sectionHintStyle          lipgloss.Style
	summaryStripForeground    lipgloss.AdaptiveColor
	summaryStripStyle         lipgloss.Style
	historyActiveForeground   lipgloss.AdaptiveColor
	historyActiveBackground   lipgloss.AdaptiveColor
	historyActiveStyle        lipgloss.Style
}

func newGrammarComposerTheme() grammarComposerTheme {
	toastForeground := lipgloss.AdaptiveColor{
		Light: "#3C1053", // Charmtone plum on light backgrounds
		Dark:  "#F3D57C", // Charmtone amber on dark backgrounds
	}
	sectionHeaderForeground := lipgloss.AdaptiveColor{
		Light: "#5B2A86", // Charmtone violet for headings on light backgrounds
		Dark:  "#EAD8FF", // Charmtone lilac for headings on dark backgrounds
	}
	sectionHintForeground := lipgloss.AdaptiveColor{
		Light: "#6F6B8A", // Charmtone slate for meta text on light backgrounds
		Dark:  "#B7B2D6", // Charmtone mist for meta text on dark backgrounds
	}
	summaryStripForeground := lipgloss.AdaptiveColor{
		Light: "#1E1633", // Charmtone ink for summary emphasis on light backgrounds
		Dark:  "#F5F1FF", // Charmtone pearl for summary emphasis on dark backgrounds
	}
	historyActiveForeground := lipgloss.AdaptiveColor{
		Light: "#1C1333", // Charmtone ink accent for highlighted history rows on light backgrounds
		Dark:  "#F6EFFF", // Charmtone pearl accent for highlighted history rows on dark backgrounds
	}
	historyActiveBackground := lipgloss.AdaptiveColor{
		Light: "#F2E8FF", // Charmtone lilac wash for highlighted history rows on light backgrounds
		Dark:  "#352040", // Charmtone plum wash for highlighted history rows on dark backgrounds
	}

	return grammarComposerTheme{
		toastForeground: toastForeground,
		toastStyle: lipgloss.NewStyle().
			Foreground(toastForeground).
			Bold(true),
		sectionHeaderForeground: sectionHeaderForeground,
		sectionHeaderStyle: lipgloss.NewStyle().
			Foreground(sectionHeaderForeground).
			Bold(true),
		sectionHintForeground: sectionHintForeground,
		sectionHintStyle: lipgloss.NewStyle().
			Foreground(sectionHintForeground).
			Faint(true),
		summaryStripForeground: summaryStripForeground,
		summaryStripStyle: lipgloss.NewStyle().
			Foreground(summaryStripForeground).
			Bold(true),
		historyActiveForeground: historyActiveForeground,
		historyActiveBackground: historyActiveBackground,
		historyActiveStyle: lipgloss.NewStyle().
			Foreground(historyActiveForeground).
			Background(historyActiveBackground).
			Bold(true),
	}
}

type toastExpiredMsg struct {
	sequence int
}

type historyHighlightExpiredMsg struct {
	sequence int
}

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

func categorySlug(category TokenCategory) string {
	if category.Key != "" {
		return strings.ToLower(strings.TrimSpace(category.Key))
	}
	return slugifyLabel(category.Label)
}

func slugifyLabel(label string) string {
	label = strings.TrimSpace(label)
	if label == "" {
		return ""
	}
	fields := strings.FieldsFunc(strings.ToLower(label), func(r rune) bool {
		return (r < 'a' || r > 'z') && (r < '0' || r > '9')
	})
	return strings.Join(fields, "-")
}

func splitGrammarFilter(input string) (slug string, value string) {
	trimmed := strings.TrimSpace(input)
	if trimmed == "" {
		return "", ""
	}
	parts := strings.SplitN(trimmed, "=", 2)
	slug = strings.TrimSpace(parts[0])
	if len(parts) == 1 {
		return slug, ""
	}
	value = strings.TrimSpace(parts[1])
	return slug, value
}

// extractFilterFromInput extracts the filter string from either CLI command format
// ("bar build token1 token2 partial") or legacy grammar format ("category=value").
// For CLI command format, it returns the last word being typed (the partial).
// For grammar format, it returns the value part after the "=".
func (m *model) extractFilterFromInput(input string) string {
	trimmed := strings.TrimSpace(input)
	if trimmed == "" {
		return ""
	}

	// Check for CLI command format (starts with "bar build")
	if strings.HasPrefix(trimmed, "bar build") {
		// Strip the "bar build" prefix
		rest := strings.TrimPrefix(trimmed, "bar build")
		rest = strings.TrimSpace(rest)
		if rest == "" {
			return ""
		}
		// Get the last word as the filter (what's being typed)
		fields := strings.Fields(rest)
		if len(fields) == 0 {
			return ""
		}
		return strings.ToLower(fields[len(fields)-1])
	}

	// Legacy grammar format (category=value)
	slugPart, valuePart := splitGrammarFilter(trimmed)
	slugPartLower := strings.ToLower(strings.TrimSpace(slugPart))
	if slugPartLower != "" {
		if idx, ok := m.findCategoryIndexBySlug(slugPartLower); ok && idx != m.tokenCategoryIndex {
			m.tokenCategoryIndex = idx
			m.clampTokenOptionIndex()
		}
	}
	filter := strings.ToLower(strings.TrimSpace(valuePart))
	if slugPartLower == "" {
		filter = strings.ToLower(strings.TrimSpace(trimmed))
	}
	return filter
}

func (m *model) currentCategorySlug() string {
	if m.tokenCategoryIndex < 0 || m.tokenCategoryIndex >= len(m.tokenStates) {
		return ""
	}
	return categorySlug(m.tokenStates[m.tokenCategoryIndex].category)
}

func (m *model) findCategoryIndexBySlug(slug string) (int, bool) {
	slug = strings.ToLower(strings.TrimSpace(slug))
	if slug == "" {
		return 0, false
	}
	for i, state := range m.tokenStates {
		if categorySlug(state.category) == slug {
			return i, true
		}
	}
	return 0, false
}

func (m *model) setGrammarFilter(slug string, value string) {
	slug = strings.TrimSpace(slug)
	value = strings.TrimSpace(value)
	if slug == "" {
		slug = m.currentCategorySlug()
	}
	var builder strings.Builder
	if slug != "" {
		builder.WriteString(strings.ToLower(slug))
		builder.WriteString("=")
	}
	builder.WriteString(value)
	m.tokenPaletteFilter.SetValue(builder.String())
	m.tokenPaletteFilter.CursorEnd()
}

func (m *model) seedGrammarFilter(preserveValue bool) {
	value := ""
	if preserveValue {
		_, existing := splitGrammarFilter(m.tokenPaletteFilter.Value())
		value = existing
	}
	m.setGrammarFilter("", value)
}

// seedCLICommand populates the palette filter with the current CLI command.
// This enables the CLI command input mode where operators edit the live command
// and Tab cycles through completions, teaching the bar build grammar directly.
func (m *model) seedCLICommand() {
	command := m.displayCommandString()
	if command == "" {
		command = "bar build"
	}
	// Add trailing space to allow immediate completion typing
	m.tokenPaletteFilter.SetValue(command + " ")
	m.tokenPaletteFilter.CursorEnd()
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
	paletteHistory             []historyEvent
	paletteHistoryVisible      bool
	historyHighlightActive     bool
	historyHighlightSequence   int
	lastPaletteCategoryIndex   int
	tokenPaletteFilter       textinput.Model
	tokenViewport            viewport.Model
	focusBeforePalette       focusArea
	unassignedTokens         []string
	lastTokenSnapshot        []string

	destinationSummary string

	sidebarPreference sidebarPreference
	sidebarAutoHidden bool

	now func() time.Time

	pendingSubject       *subjectReplacementPrompt
	subjectUndoValue     string
	subjectUndoSource    string
	subjectUndoAvailable bool

	width              int
	height             int
	mainColumnWidth    int
	sidebarColumnWidth int
	columnGap          int
	viewportMode       viewportMode
	subjectViewport    viewport.Model
	resultViewport     viewport.Model
	condensedPreview   bool
	tokenSparkline     []int
	toastMessage       string
	toastVisible       bool
	toastSequence      int

	subject textarea.Model
	command textinput.Model

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
	dialogs                dialogManager
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
	subject := textarea.New()
	subject.Placeholder = "Describe the subject to update the preview"
	subject.Prompt = ""
	subject.CharLimit = 0
	subject.EndOfBufferCharacter = ' '
	subject.ShowLineNumbers = false
	subject.SetWidth(defaultViewportWidth)
	subject.SetHeight(minSubjectViewport)
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

	status := "Subject input focused. Use Ctrl+L to load from clipboard. Tab cycles focus · Ctrl+P palette · Ctrl+B copy CLI · Ctrl+G toggle sidebar · Ctrl+? shortcuts."
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
		tokenViewport:          tokenViewport,
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
		width:                  initialWidth,
		height:                 initialHeight,
		viewportMode:           viewportModeNormal,
		subjectViewport:        subjectViewport,
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
		sidebarPreference:      sidebarPreferenceShown,
		now:                    time.Now,
	}
	m.tokenSparkline = []int{len(m.tokens)}
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

	switch m.viewportMode {
	case viewportModeSubject:
		tokenHeight = maxInt(minTokenViewport, tokenHeight)
		subjectHeight = maxInt(minSubjectViewport, available-tokenHeight-minResultViewport)
		if subjectHeight < minSubjectViewport {
			subjectHeight = minSubjectViewport
		}
		resultHeight = available - tokenHeight - subjectHeight
		if resultHeight < minResultViewport {
			resultHeight = minResultViewport
			subjectHeight = maxInt(minSubjectViewport, available-tokenHeight-resultHeight)
		}
	case viewportModeResult:
		tokenHeight = maxInt(minTokenViewport, tokenHeight)
		resultHeight = maxInt(minResultViewport, available-tokenHeight-minSubjectViewport)
		if resultHeight < minResultViewport {
			resultHeight = minResultViewport
		}
		subjectHeight = available - tokenHeight - resultHeight
		if subjectHeight < minSubjectViewport {
			subjectHeight = minSubjectViewport
			resultHeight = maxInt(minResultViewport, available-tokenHeight-subjectHeight)
		}
	}

	mainWidth, gap, sidebarWidth := computeColumnLayout(width)

	if m.sidebarPreference == sidebarPreferenceHidden {
		mainWidth = width
		gap = 0
		sidebarWidth = 0
	}

	autoHidden := m.sidebarPreference == sidebarPreferenceShown && sidebarWidth == 0
	m.sidebarAutoHidden = autoHidden
	m.mainColumnWidth = mainWidth
	m.sidebarColumnWidth = sidebarWidth
	m.columnGap = gap

	if sidebarWidth == 0 {
		m.subjectViewport.Width = maxInt(1, width)
		m.resultViewport.Width = maxInt(1, width)
		m.tokenViewport.Width = maxInt(1, width)
	} else {
		m.subjectViewport.Width = maxInt(1, mainWidth)
		m.resultViewport.Width = maxInt(1, mainWidth)
		m.tokenViewport.Width = maxInt(1, sidebarWidth)
	}

	m.tokenViewport.Height = maxInt(1, tokenHeight)
	m.subjectViewport.Height = maxInt(minSubjectViewport, subjectHeight)
	m.resultViewport.Height = maxInt(minResultViewport, resultHeight)

	m.subject.SetWidth(m.subjectViewport.Width)
	m.subject.SetHeight(m.subjectViewport.Height)
}

func computeColumnLayout(width int) (mainWidth int, gap int, sidebarWidth int) {
	const (
		minMainWidth    = 44
		minSidebarWidth = 30
		minGap          = 2
	)

	if width <= 0 {
		width = defaultViewportWidth
	}

	if width < minMainWidth+minSidebarWidth+minGap {
		return width, 0, 0
	}

	gap = 4
	if width < 90 {
		gap = 2
	}

	available := width - gap
	maxSidebar := available - minMainWidth
	if maxSidebar < minSidebarWidth {
		return width, 0, 0
	}

	sidebarWidth = clampInt(width/3, minSidebarWidth, maxSidebar)
	mainWidth = available - sidebarWidth
	if mainWidth < minMainWidth {
		return width, 0, 0
	}

	return mainWidth, gap, sidebarWidth
}

func (m *model) updateSubjectViewportContent() {
	content := m.subject.View()
	if m.focus == focusSubject {
		if !strings.HasSuffix(content, "\n") {
			content += "\n"
		}
		content += "  ← editing"
	}
	m.subjectViewport.SetContent(content)
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
	prevAutoHidden := m.sidebarAutoHidden
	m.width = msg.Width
	m.height = msg.Height
	m.layoutViewports()
	if m.sidebarPreference == sidebarPreferenceShown {
		switch {
		case m.sidebarAutoHidden && !prevAutoHidden:
			m.statusMessage = "Sidebar hidden automatically because the terminal is too narrow. Press Ctrl+G to hide manually or widen the window."
		case !m.sidebarAutoHidden && prevAutoHidden:
			m.statusMessage = "Sidebar visible again. Press Ctrl+G to hide."
		}
	}
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

	rawFilter := m.tokenPaletteFilter.Value()

	// Extract filter from CLI command format or grammar format
	filter := m.extractFilterFromInput(rawFilter)

	state := m.tokenStates[m.tokenCategoryIndex]
	options := make([]int, 0, len(state.category.Options)+2)
	if m.shouldShowCopyCommandAction(filter) {
		options = append(options, tokenPaletteCopyCommandOption)
	}
	if m.shouldShowPresetReset(m.tokenCategoryIndex) {
		options = append(options, tokenPaletteResetOption)
	}
	for idx, option := range state.category.Options {
		if optionMatchesValue(option, filter) {
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

func optionMatchesValue(option TokenOption, filter string) bool {
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

	m.seedCLICommand()
	m.updatePaletteOptions()
	m.refreshPaletteStatus()
	m.statusMessage = ensureCopyHint("CLI command reset. Type to add tokens, Tab cycles completions.")
	return true
}

// applyNextCompletion cycles through token completions in the CLI command input.
// It finds the partial word at the end of the filter and replaces it with a matching
// token option, or appends a token if the filter ends with a space.
func (m *model) applyNextCompletion(delta int) {
	filterValue := m.tokenPaletteFilter.Value()

	// Find the partial word at the end for completion
	partial, prefix := m.extractCompletionContext(filterValue)

	// Get matching completions
	completions := m.getCompletionsForPartial(partial)
	if len(completions) == 0 {
		m.statusMessage = "No completions match. Try a different prefix."
		return
	}

	// Find the current completion index (if partial matches one)
	currentIdx := -1
	for i, c := range completions {
		if c == partial {
			currentIdx = i
			break
		}
	}

	// Calculate next index
	nextIdx := (currentIdx + delta) % len(completions)
	if nextIdx < 0 {
		nextIdx += len(completions)
	}

	// Apply the completion
	newValue := prefix + completions[nextIdx] + " "
	m.tokenPaletteFilter.SetValue(newValue)
	m.tokenPaletteFilter.CursorEnd()
	m.updatePaletteOptions()
	m.refreshPaletteStatus()
}

// extractCompletionContext parses the filter value to find the partial word
// being typed and the prefix before it.
func (m *model) extractCompletionContext(filterValue string) (partial, prefix string) {
	// Strip "bar build " prefix if present for parsing
	trimmed := filterValue
	if strings.HasPrefix(trimmed, "bar build ") {
		trimmed = strings.TrimPrefix(trimmed, "bar build ")
	} else if strings.HasPrefix(trimmed, "bar build") {
		trimmed = strings.TrimPrefix(trimmed, "bar build")
	}

	// If filter ends with space, no partial - ready for new token
	if strings.HasSuffix(filterValue, " ") || trimmed == "" {
		return "", filterValue
	}

	// Find the last word (the partial being typed)
	lastSpace := strings.LastIndex(filterValue, " ")
	if lastSpace == -1 {
		return filterValue, ""
	}
	return filterValue[lastSpace+1:], filterValue[:lastSpace+1]
}

// getCompletionsForPartial returns token options matching the partial string.
func (m *model) getCompletionsForPartial(partial string) []string {
	partial = strings.ToLower(strings.TrimSpace(partial))
	var completions []string
	seen := make(map[string]bool)

	// Collect all matching token options across categories
	for _, state := range m.tokenStates {
		for _, opt := range state.category.Options {
			value := opt.Value
			if seen[value] {
				continue
			}

			// Match if partial is empty or value starts with/contains partial
			valueLower := strings.ToLower(value)
			if partial == "" || strings.HasPrefix(valueLower, partial) || strings.Contains(valueLower, partial) {
				completions = append(completions, value)
				seen[value] = true
			}
		}
	}

	return completions
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

func (m *model) historyTimestamp() time.Time {
	if m.now != nil {
		return m.now().UTC()
	}
	return time.Now().UTC()
}

func (m *model) recordPaletteHistory(kind historyEventKind, entry string) tea.Cmd {
	trimmed := strings.TrimSpace(entry)
	if trimmed == "" {
		return nil
	}
	command := strings.TrimSpace(m.displayCommandString())
	event := historyEvent{
		Kind:      kind,
		Message:   trimmed,
		Command:   command,
		Timestamp: m.historyTimestamp(),
	}
	m.paletteHistory = append([]historyEvent{event}, m.paletteHistory...)
	if len(m.paletteHistory) > paletteHistoryLimit {
		m.paletteHistory = m.paletteHistory[:paletteHistoryLimit]
	}
	m.historyHighlightActive = true
	m.historyHighlightSequence++
	sequence := m.historyHighlightSequence
	return tea.Tick(historyHighlightLifetime, func(time.Time) tea.Msg {
		return historyHighlightExpiredMsg{sequence: sequence}
	})
}

func (m *model) recordCommandHistory(result commandResult, mode commandMode) tea.Cmd {
	entry := formatCommandHistoryEntry(result, mode)
	if entry == "" {
		return nil
	}
	return m.recordPaletteHistory(historyEventKindCommand, entry)
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
		m.statusMessage = "No history entries yet. Make a palette change before expanding history."
		return
	}
	m.paletteHistoryVisible = !m.paletteHistoryVisible
	if m.paletteHistoryVisible {
		m.statusMessage = "History expanded. Press Ctrl+H to collapse. Press Ctrl+Shift+H to copy the latest CLI command."
	} else {
		m.statusMessage = "History collapsed. Press Ctrl+H to expand."
	}
}

func (m *model) toggleSidebarVisibility() {
	if m.sidebarPreference == sidebarPreferenceHidden {
		m.sidebarPreference = sidebarPreferenceShown
		m.layoutViewports()
		if m.sidebarAutoHidden {
			m.statusMessage = "Sidebar expanded, but the terminal is too narrow to render it. Resize or press Ctrl+G to hide."
		} else {
			m.statusMessage = "Sidebar expanded. Press Ctrl+G to hide."
		}
	} else {
		m.sidebarPreference = sidebarPreferenceHidden
		m.layoutViewports()
		m.statusMessage = "Sidebar hidden. Press Ctrl+G to show."
	}
	m.updateTokenViewportContent()
	m.updateSubjectViewportContent()
	m.updateResultViewportContent()
}

func (m *model) toggleViewportFocus(area focusArea) {
	var status string
	switch area {
	case focusSubject:
		if m.viewportMode == viewportModeSubject {
			m.viewportMode = viewportModeNormal
			status = "Subject viewport restored to default layout."
		} else {
			m.viewportMode = viewportModeSubject
			status = "Subject viewport maximised. Press Ctrl+J to restore the default layout."
		}
	case focusResult:
		if m.viewportMode == viewportModeResult {
			m.viewportMode = viewportModeNormal
			status = "Result viewport restored to default layout."
		} else {
			m.viewportMode = viewportModeResult
			status = "Result viewport maximised. Press Ctrl+K to restore the default layout."
		}
	default:
		return
	}

	m.layoutViewports()
	m.updateTokenViewportContent()
	m.updateSubjectViewportContent()
	m.updateResultViewportContent()
	m.statusMessage = status
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
	m.seedGrammarFilter(false)
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

func (m *model) toggleCurrentTokenOption() tea.Cmd {
	option, ok := m.currentTokenOption()
	if !ok {
		m.statusMessage = "No token option available to toggle."
		return nil
	}
	state := &m.tokenStates[m.tokenCategoryIndex]
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
		m.recordPaletteHistory(historyEventKindTokens, historyEntry)
		m.statusMessage = fmt.Sprintf("%s → %s removed.", state.category.Label, slug)
		return m.toastTokenChange(state.category, option, "removed")
	}
	max := state.category.MaxSelections
	if max > 0 && len(state.selected) >= max {
		suffix := ""
		if max > 1 {
			suffix = "s"
		}
		m.statusMessage = fmt.Sprintf("%s already has %d selection%s; remove one before adding another.", state.category.Label, max, suffix)
		return nil
	}
	m.recordTokenUndo()
	state.add(option.Value, max)
	m.rebuildTokensFromStates()
	historyEntry := fmt.Sprintf("%s → %s applied", categoryLabel, slug)
	m.recordPaletteHistory(historyEventKindTokens, historyEntry)
	m.statusMessage = fmt.Sprintf("%s → %s applied.", state.category.Label, slug)
	return m.toastTokenChange(state.category, option, "applied")
}

func (m *model) removeCurrentTokenOption() tea.Cmd {
	option, ok := m.currentTokenOption()
	if !ok {
		m.statusMessage = "No token option highlighted to remove."
		return nil
	}
	state := &m.tokenStates[m.tokenCategoryIndex]
	if !state.has(option.Value) {
		slug := option.Slug
		if slug == "" {
			slug = option.Value
		}
		m.statusMessage = fmt.Sprintf("%s not selected; nothing to remove.", slug)
		return nil
	}
	slug := option.Slug
	if slug == "" {
		slug = option.Value
	}
	categoryLabel := state.category.Label
	if categoryLabel == "" {
		categoryLabel = state.category.Key
	}
	m.recordTokenUndo()
	state.remove(option.Value)
	m.rebuildTokensFromStates()
	historyEntry := fmt.Sprintf("%s → %s removed", categoryLabel, slug)
	m.recordPaletteHistory(historyEventKindTokens, historyEntry)
	m.statusMessage = fmt.Sprintf("%s → %s removed.", state.category.Label, slug)
	return m.toastTokenChange(state.category, option, "removed")
}

func (m *model) undoTokenChange() tea.Cmd {
	if m.lastTokenSnapshot == nil {
		m.statusMessage = "No token change to undo."
		return nil
	}
	snapshot := append([]string(nil), m.lastTokenSnapshot...)
	m.lastTokenSnapshot = nil
	m.setTokens(snapshot)
	m.statusMessage = "Token selection restored."
	m.recordPaletteHistory(historyEventKindTokens, "Tokens undo restored")
	return m.toastUndoRestored()
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
	m.seedCLICommand()
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
	if id, closed := m.dialogs.closeTop(); closed {
		m.onDialogClosed(id)
		return tea.ClearScreen, true
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

func (m *model) toggleShortcutReference() tea.Cmd {
	if m.isShortcutReferenceVisible() {
		if m.dialogs.close(shortcutReferenceDialogID) {
			m.onDialogClosed(shortcutReferenceDialogID)
			return tea.ClearScreen
		}
		return nil
	}

	m.onDialogOpened(shortcutReferenceDialogID)
	dialog := newShortcutReferenceDialog(m.shortcutReferenceSections())
	cmd := m.dialogs.open(dialog)
	return tea.Batch(tea.ClearScreen, cmd)
}

func (m *model) handleKeyString(key string) (bool, tea.Cmd) {
	switch key {
	case "tab":
		m.toggleFocus()
		return true, nil
	case "?":
		return true, m.toggleShortcutReference()
	case "ctrl+/":
		return true, m.toggleShortcutReference()
	case "ctrl+?":
		return true, m.toggleShortcutReference()
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
	case "ctrl+shift+h", "ctrl+H":
		if cmd := m.copyHistoryCommandToClipboard(); cmd != nil {
			return true, cmd
		}
		return true, nil
	case "ctrl+g":
		m.toggleSidebarVisibility()
		return true, nil
	case "ctrl+j":
		m.toggleViewportFocus(focusSubject)
		return true, nil
	case "ctrl+k":
		m.toggleViewportFocus(focusResult)
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

const copyHint = "Type \"copy command\" to focus the copy action."
const statusLimit = 180

func ensureCopyHint(status string) string {
	status = strings.TrimSpace(status)
	if status == "" {
		return limitStatusMessage(copyHint)
	}
	if strings.Contains(status, "copy command") {
		return limitStatusMessage(status)
	}
	return limitStatusMessage(status + " " + copyHint)
}

func limitStatusMessage(status string) string {
	status = strings.TrimSpace(status)
	if status == "" {
		return ""
	}
	runes := []rune(status)
	if len(runes) <= statusLimit {
		return status
	}
	cut := statusLimit - 1
	if cut <= 0 {
		return "…"
	}
	for i := cut; i >= 0; i-- {
		switch runes[i] {
		case ' ', '|', '·', '•', '—', '-', '.', ',', ';':
			cut = i
			goto done
		}
	}
	cut = statusLimit - 1

done:
	trimmed := strings.TrimSpace(string(runes[:cut]))
	if trimmed == "" {
		trimmed = strings.TrimSpace(string(runes[:statusLimit-1]))
	}
	return trimmed + "…"
}

func (m *model) restoreStatusAfterShortcutReference() {
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
		m.statusMessage = "Shortcut reference closed."
	}
	m.statusBeforeHelp = ""
}

func (m *model) isShortcutReferenceVisible() bool {
	return m.dialogs.has(shortcutReferenceDialogID)
}

func (m *model) onDialogOpened(id string) {
	switch id {
	case shortcutReferenceDialogID:
		m.statusBeforeHelp = m.statusMessage
		m.statusMessage = "Shortcut reference open. Press Ctrl+? to close."
	}
}

func (m *model) onDialogClosed(id string) {
	switch id {
	case shortcutReferenceDialogID:
		m.restoreStatusAfterShortcutReference()
	}
}

func (m model) dialogViewWidth() int {
	if m.mainColumnWidth > 0 {
		return m.mainColumnWidth
	}
	if m.width > 0 {
		return m.width
	}
	return defaultViewportWidth
}

func (m *model) refreshPaletteStatus() {
	if !m.tokenPaletteVisible {
		return
	}

	switch m.tokenPaletteFocus {
	case tokenPaletteFocusFilter:
		slug, value := splitGrammarFilter(m.tokenPaletteFilter.Value())
		slug = strings.TrimSpace(slug)
		value = strings.TrimSpace(value)
		slugDisplay := slug
		if slugDisplay == "" {
			slugDisplay = m.currentCategorySlug()
		}
		if slugDisplay != "" {
			if value == "" {
				m.statusMessage = ensureCopyHint(fmt.Sprintf("%s= — type a value, press Tab to cycle completions, Enter applies an option, Ctrl+W clears, Esc closes.", slugDisplay))
			} else {
				m.statusMessage = ensureCopyHint(fmt.Sprintf("%s=%s. Tab cycles completions, Enter applies an option, Ctrl+W clears, Esc closes.", slugDisplay, value))
			}
		} else {
			if value == "" {
				m.statusMessage = ensureCopyHint("Token palette open. Type to filter, Tab cycles focus, Enter applies or copies, Ctrl+W clears the filter, Esc closes.")
			} else {
				m.statusMessage = ensureCopyHint(fmt.Sprintf("Palette filter \"%s\" active. Tab cycles focus, Enter applies or copies, Ctrl+W clears the filter, Esc closes.", value))
			}
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

func (m *model) applyPaletteSelection() tea.Cmd {
	if len(m.tokenPaletteOptions) == 0 || m.tokenPaletteOptionIndex < 0 || m.tokenPaletteOptionIndex >= len(m.tokenPaletteOptions) {
		m.statusMessage = "No token options available for the current filter."
		return nil
	}
	index := m.tokenPaletteOptions[m.tokenPaletteOptionIndex]
	if index == tokenPaletteCopyCommandOption {
		m.copyBuildCommandToClipboard()
		return m.closeTokenPaletteWithStatus("")
	}
	if index == tokenPaletteResetOption {
		return m.applyPaletteReset()
	}
	state := &m.tokenStates[m.tokenCategoryIndex]
	if index < 0 || index >= len(state.category.Options) {
		return nil
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
	var toast tea.Cmd
	if state.has(option.Value) {
		m.recordTokenUndo()
		state.remove(option.Value)
		m.rebuildTokensFromStates()
		historyEntry := fmt.Sprintf("%s → %s removed", categoryLabel, slug)
		m.recordPaletteHistory(historyEventKindTokens, historyEntry)
		m.statusMessage = fmt.Sprintf("%s → %s removed.", state.category.Label, slug)
		toast = m.toastTokenChange(state.category, option, "removed")
	} else {
		max := state.category.MaxSelections
		if max > 0 && len(state.selected) >= max {
			suffix := ""
			if max > 1 {
				suffix = "s"
			}
			m.statusMessage = fmt.Sprintf("%s already has %d selection%s; remove one before adding another.", state.category.Label, max, suffix)
			return nil
		}
		m.recordTokenUndo()
		state.add(option.Value, max)
		m.rebuildTokensFromStates()
		historyEntry := fmt.Sprintf("%s → %s applied", categoryLabel, slug)
		m.recordPaletteHistory(historyEventKindTokens, historyEntry)
		m.statusMessage = fmt.Sprintf("%s → %s applied.", state.category.Label, slug)
		toast = m.toastTokenChange(state.category, option, "applied")
	}
	m.updatePaletteOptions()
	return toast
}

func (m *model) applyPaletteReset() tea.Cmd {
	presetValues := m.presetTokensForCategory(m.tokenCategoryIndex)
	if len(presetValues) == 0 {
		m.statusMessage = "Active preset has no tokens for this category."
		return nil
	}
	state := &m.tokenStates[m.tokenCategoryIndex]
	if tokensSliceEqual(state.selected, presetValues) {
		m.statusMessage = "Category already matches preset."
		return nil
	}
	m.recordTokenUndo()
	state.setSelected(presetValues, state.category.MaxSelections)
	m.rebuildTokensFromStates()
	categoryLabel := state.category.Label
	if categoryLabel == "" {
		categoryLabel = state.category.Key
	}
	m.recordPaletteHistory(historyEventKindTokens, fmt.Sprintf("%s reset to preset", categoryLabel))
	m.statusMessage = fmt.Sprintf("%s reset to preset.", state.category.Label)
	return m.toastCategoryReset(state.category)
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
		if m.tokenPaletteFocus == tokenPaletteFocusFilter {
			// Tab cycles through completions when in filter mode (CLI command input)
			m.applyNextCompletion(1)
			return true, nil
		}
		cmd := m.advancePaletteFocus(1)
		return true, cmd
	case tea.KeyShiftTab:
		if m.tokenPaletteFocus == tokenPaletteFocusFilter {
			// Shift+Tab cycles backwards through completions
			m.applyNextCompletion(-1)
			return true, nil
		}
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
		cmd := m.applyPaletteSelection()
		return true, cmd
	case tea.KeyCtrlZ:
		cmd := m.undoTokenChange()
		return true, cmd
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
	status := limitStatusMessage(strings.TrimSpace(m.statusMessage))
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

	displayCommand := m.displayCommandString()
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

	if len(m.missingEnv) > 0 {
		missing := strings.Join(m.missingEnv, ", ")
		if len(missing) > 32 {
			missing = fmt.Sprintf("%d missing", len(m.missingEnv))
		}
		parts = append(parts, fmt.Sprintf("Missing: %s", missing))
	}

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

	displayCommand := m.displayCommandString()
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

	content := "Summary strip: " + strings.Join(parts, " | ")
	return composerTheme.summaryStripStyle.Render(content)
}

func renderSidebarSectionHeader(title string) string {
	title = strings.TrimSpace(title)
	if title == "" {
		return ""
	}
	return composerTheme.sectionHeaderStyle.Render(strings.ToUpper(title))
}

func renderSidebarSectionHint(hint string) string {
	hint = strings.TrimSpace(hint)
	if hint == "" {
		return ""
	}
	return composerTheme.sectionHintStyle.Render(hint)
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
		} else {
			b.WriteString("Tokens: " + strings.Join(m.tokens, ", ") + "\n")
		}
		if len(m.unassignedTokens) > 0 {
			b.WriteString("Other tokens: " + strings.Join(m.unassignedTokens, ", ") + "\n")
		}
		return
	}

	tokenSummaries := make([]string, 0, len(m.tokenStates))
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
		tokenSummaries = append(tokenSummaries, fmt.Sprintf("%s: %s", label, strings.Join(values, ", ")))
	}

	if len(tokenSummaries) == 0 {
		b.WriteString("Tokens: (none selected)\n")
	} else {
		b.WriteString("Tokens: " + strings.Join(tokenSummaries, " · ") + "\n")
	}

	unset := unsetCategoryLabels(m.tokenStates)
	if len(unset) > 0 {
		b.WriteString("Unset: " + strings.Join(unset, ", ") + "\n")
	}

	if len(m.unassignedTokens) > 0 {
		b.WriteString("Other tokens: " + strings.Join(m.unassignedTokens, ", ") + "\n")
	}

	b.WriteString("Categories:\n")
	for idx, state := range m.tokenStates {
		label := state.category.Label
		if label == "" {
			label = state.category.Key
		}
		indicator := "○"
		suffix := ""
		if idx == m.tokenCategoryIndex {
			indicator = "•"
			if m.focus == focusTokens || m.tokenPaletteVisible {
				indicator = "»"
				suffix = " (focus)"
			}
		}
		if len(state.selected) == 0 {
			b.WriteString(fmt.Sprintf("  %s %s — (none)%s\n", indicator, label, suffix))
			continue
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
		b.WriteString(fmt.Sprintf("  %s %s — %s%s\n", indicator, label, strings.Join(values, ", "), suffix))
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
	case toastExpiredMsg:
		if typed.sequence == m.toastSequence {
			m.toastVisible = false
			m.toastMessage = ""
		}
		return m, nil
	case historyHighlightExpiredMsg:
		if typed.sequence == m.historyHighlightSequence {
			m.historyHighlightActive = false
		}
		return m, nil
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
	}

	if cmdDialog, handledDialog, closedID := (&m).dialogs.update(msg); handledDialog || closedID != "" || cmdDialog != nil {
		if closedID != "" {
			(&m).onDialogClosed(closedID)
		}
		if cmdDialog != nil {
			return m, cmdDialog
		}
		if handledDialog {
			return m, nil
		}
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
				if cmd := m.toggleCurrentTokenOption(); cmd != nil {
					return m, cmd
				}
				return m, nil
			}
			if m.focus == focusEnvironment {
				m.toggleSelectedEnv()
				return m, nil
			}
		case tea.KeySpace:
			if m.focus == focusTokens {
				if cmd := m.toggleCurrentTokenOption(); cmd != nil {
					return m, cmd
				}
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
				if cmd := m.removeCurrentTokenOption(); cmd != nil {
					return m, cmd
				}
				return m, nil
			}
			if m.focus == focusEnvironment {
				m.setAllEnv(false)
				return m, nil
			}
		case tea.KeyCtrlZ:
			if m.focus == focusTokens || m.tokenPaletteVisible {
				if cmd := m.undoTokenChange(); cmd != nil {
					return m, cmd
				}
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
	m.recordPaletteHistory(historyEventKindSubject, fmt.Sprintf("Subject replaced via %s", prompt.source))
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
	m.recordPaletteHistory(historyEventKindSubject, fmt.Sprintf("Subject undo (%s)", source))
}

func (m *model) renderMainColumnContent() string {
	var builder strings.Builder

	builder.WriteString("Subject (PgUp/PgDn scroll · Home/End jump):\n")
	builder.WriteString(m.subjectViewport.View())
	builder.WriteString("\n\n")

	builder.WriteString("Command (Enter runs without preview):\n")
	builder.WriteString(m.command.View())
	builder.WriteString("\n\n")

	builder.WriteString("Hint: press Ctrl+? for shortcuts · Ctrl+P toggles the palette · Leave command blank to opt out.\n\n")

	builder.WriteString("Result summary:\n")
	builder.WriteString(m.renderResultSummaryLine())
	builder.WriteString("\n\n")

	builder.WriteString("Result & preview (PgUp/PgDn scroll · Home/End jump · Ctrl+T toggle condensed preview):\n")
	builder.WriteString(m.resultViewport.View())
	builder.WriteString("\n")

	return strings.TrimRight(builder.String(), "\n")
}

func (m *model) renderComposeSection() string {
	var builder strings.Builder
	builder.WriteString(renderSidebarSectionHeader("Compose"))
	builder.WriteString("\n")

	localTokenViewport := m.tokenViewport
	localTokenViewport.SetContent(m.renderTokenViewportContent())
	tokenSection := strings.TrimRight(localTokenViewport.View(), "\n")
	hasTokenContent := strings.TrimSpace(tokenSection) != ""
	if !hasTokenContent {
		builder.WriteString("  No token controls available.\n")
	} else {
		builder.WriteString(tokenSection)
	}

	if spark := strings.TrimSpace(m.renderTokenSparklineLine()); spark != "" {
		if hasTokenContent {
			builder.WriteString("\n\n")
		} else {
			builder.WriteString("\n")
		}
		builder.WriteString("  ")
		builder.WriteString(spark)
		builder.WriteString("\n")
	}

	return strings.TrimRight(builder.String(), "\n")
}

func (m *model) renderHistorySection() string {
	var builder strings.Builder
	builder.WriteString(renderSidebarSectionHeader("History"))
	hint := renderSidebarSectionHint("(Ctrl+H toggles · Ctrl+Shift+H copies CLI)")
	if hint != "" {
		builder.WriteString(" ")
		builder.WriteString(hint)
	}
	builder.WriteString("\n")

	if !m.paletteHistoryVisible {
		builder.WriteString("  History collapsed. Press Ctrl+H to expand.\n")
		return strings.TrimRight(builder.String(), "\n")
	}

	if len(m.paletteHistory) == 0 {
		builder.WriteString("  (empty)\n")
	} else {
		for idx, entry := range m.paletteHistory {
			line := fmt.Sprintf("  • %s", formatHistoryEvent(entry))
			if m.shouldHighlightHistoryEntry(idx, entry) {
				line = composerTheme.historyActiveStyle.Render(line)
			}
			builder.WriteString(line)
			builder.WriteString("\n")
		}
	}

	return strings.TrimRight(builder.String(), "\n")
}

func (m *model) shouldHighlightHistoryEntry(index int, event historyEvent) bool {
	if index != 0 {
		return false
	}
	if !m.historyHighlightActive {
		return false
	}
	if event.Timestamp.IsZero() {
		return true
	}
	now := m.historyTimestamp()
	if now.IsZero() {
		return true
	}
	age := now.Sub(event.Timestamp)
	if age < 0 {
		return true
	}
	return age <= historyHighlightLifetime
}

func historyEventIcon(kind historyEventKind) string {
	switch kind {
	case historyEventKindTokens:
		return "🎛"
	case historyEventKindClipboard:
		return "📋"
	case historyEventKindCommand:
		return "⌘"
	case historyEventKindSubject:
		return "📝"
	case historyEventKindPreset:
		return "⭐"
	default:
		return ""
	}
}

func historyEventLabel(kind historyEventKind) string {
	label := strings.TrimSpace(string(kind))
	if label == "" {
		return "Event"
	}
	return label
}

func formatHistoryEvent(event historyEvent) string {
	label := historyEventLabel(event.Kind)
	icon := historyEventIcon(event.Kind)
	if icon != "" {
		label = fmt.Sprintf("%s %s", icon, label)
	}

	timePart := ""
	if !event.Timestamp.IsZero() {
		timePart = event.Timestamp.UTC().Format("15:04")
	}

	var base string
	if timePart != "" {
		base = fmt.Sprintf("[%s] %s · %s", timePart, label, event.Message)
	} else {
		base = fmt.Sprintf("%s · %s", label, event.Message)
	}

	command := strings.TrimSpace(event.Command)
	if command != "" {
		base = fmt.Sprintf("%s · CLI: %s", base, shortenString(command, 56))
	}

	return base
}

func (m *model) renderPresetsSection() string {
	var builder strings.Builder
	builder.WriteString(renderSidebarSectionHeader("Presets"))
	hint := renderSidebarSectionHint("(Ctrl+S toggles)")
	if hint != "" {
		builder.WriteString(" ")
		builder.WriteString(hint)
	}
	builder.WriteString("\n")

	if !m.presetPaneVisible {
		builder.WriteString("  Presets collapsed. Press Ctrl+S to expand.\n")
		return strings.TrimRight(builder.String(), "\n")
	}

	var presetBuilder strings.Builder
	m.renderPresetPane(&presetBuilder)
	presetContent := strings.TrimRight(presetBuilder.String(), "\n")
	if strings.TrimSpace(presetContent) == "" {
		builder.WriteString("  (no presets available)\n")
	} else {
		builder.WriteString(presetContent)
	}

	return strings.TrimRight(builder.String(), "\n")
}

func renderShortcutReferenceOverlayContent(sections []shortcutSection) string {
	if len(sections) == 0 {
		return ""
	}

	maxKeyLength := 0
	for _, section := range sections {
		for _, entry := range section.Entries {
			length := utf8.RuneCountInString(strings.TrimSpace(entry.Keys))
			if length > maxKeyLength {
				maxKeyLength = length
			}
		}
	}

	headerRule := func(title string) string {
		title = strings.TrimSpace(title)
		if title == "" {
			return ""
		}
		rule := strings.Repeat("-", utf8.RuneCountInString(title))
		return fmt.Sprintf("  %s\n  %s\n", title, rule)
	}

	var builder strings.Builder
	builder.WriteString("Shortcut reference (press Ctrl+? to close):\n\n")

	for i, section := range sections {
		if len(section.Entries) == 0 {
			continue
		}
		titleBlock := headerRule(section.Title)
		if titleBlock != "" {
			builder.WriteString(titleBlock)
		}
		for _, entry := range section.Entries {
			keys := strings.TrimSpace(entry.Keys)
			if keys == "" {
				continue
			}
			description := strings.TrimSpace(entry.Description)
			keyWidth := utf8.RuneCountInString(keys)
			padding := maxKeyLength - keyWidth
			if padding < 0 {
				padding = 0
			}
			builder.WriteString("    • ")
			builder.WriteString(keys)
			if padding > 0 {
				builder.WriteString(strings.Repeat(" ", padding))
			}
			if description != "" {
				builder.WriteString(" — ")
				builder.WriteString(description)
			}
			builder.WriteString("\n")
		}
		if i < len(sections)-1 {
			builder.WriteString("\n")
		}
	}

	return strings.TrimRight(builder.String(), "\n")
}

func newShortcutReferenceDialog(sections []shortcutSection) dialog {
	return &shortcutReferenceDialog{sections: sections}
}

type shortcutReferenceDialog struct {
	sections []shortcutSection
}

func (d *shortcutReferenceDialog) ID() string {
	return shortcutReferenceDialogID
}

func (d *shortcutReferenceDialog) Init() tea.Cmd {
	return nil
}

func (d *shortcutReferenceDialog) Update(msg tea.Msg) (dialog, tea.Cmd, bool) {
	keyMsg, ok := msg.(tea.KeyMsg)
	if !ok {
		return d, nil, false
	}

	switch keyMsg.String() {
	case "?", "ctrl+?", "ctrl+/":
		return nil, tea.ClearScreen, true
	case "esc":
		return nil, tea.ClearScreen, true
	case "ctrl+c":
		return d, nil, false
	default:
		return d, nil, true
	}
}

func (d *shortcutReferenceDialog) View(width int, height int) string {
	if width <= 0 {
		width = defaultViewportWidth
	}
	content := renderShortcutReferenceOverlayContent(d.sections)
	rendered := lipgloss.NewStyle().Width(width).Render(content)

	var builder strings.Builder
	builder.WriteString(rendered)
	builder.WriteString("\n\nPress Ctrl+? or Esc to close the shortcut reference.\n")
	builder.WriteString("Press Ctrl+C or Esc to exit.\n")
	return builder.String()
}

func (m *model) shortcutReferenceSections() []shortcutSection {
	return []shortcutSection{
		{
			Title: "Focus & Layout",
			Entries: []shortcutEntry{
				{Keys: "Tab", Description: "Cycle focus between subject, command, tokens, and environment"},
				{Keys: "Shift+Tab", Description: "Reverse the focus cycle"},
				{Keys: "Ctrl+G", Description: "Toggle sidebar visibility"},
				{Keys: "Ctrl+J", Description: "Toggle subject viewport maximisation"},
				{Keys: "Ctrl+K", Description: "Toggle result viewport maximisation"},
				{Keys: "Ctrl+?", Description: "Toggle this shortcut reference (aliases: ? / Ctrl+/)"},
				{Keys: "Esc", Description: "Close overlays (reference → palette) then exit"},
			},
		},
		{
			Title: "Subject & Clipboard",
			Entries: []shortcutEntry{
				{Keys: "Ctrl+L", Description: "Load subject from clipboard"},
				{Keys: "Ctrl+O", Description: "Copy preview text to clipboard"},
				{Keys: "Ctrl+B", Description: "Copy bar CLI command to clipboard"},
				{Keys: "Ctrl+Z", Description: "Undo last subject replacement"},
				{Keys: "PgUp/PgDn", Description: "Scroll subject viewport (Home/End jump)"},
			},
		},
		{
			Title: "Command Execution",
			Entries: []shortcutEntry{
				{Keys: "Enter", Description: "Run command when command input is focused"},
				{Keys: "Ctrl+R", Description: "Pipe preview text into command input"},
				{Keys: "Ctrl+Y", Description: "Insert last command stdout into subject"},
				{Keys: "Ctrl+C", Description: "Cancel running command"},
			},
		},
		{
			Title: "Result View",
			Entries: []shortcutEntry{
				{Keys: "PgUp/PgDn", Description: "Scroll result viewport (Home/End jump)"},
				{Keys: "Ctrl+T", Description: "Toggle condensed result preview"},
			},
		},
		{
			Title: "Tokens",
			Entries: []shortcutEntry{
				{Keys: "Tab", Description: "Focus tokens from main inputs"},
				{Keys: "Left/Right", Description: "Change token category"},
				{Keys: "Up/Down", Description: "Browse token options"},
				{Keys: "Enter/Space", Description: "Toggle highlighted token"},
				{Keys: "Delete", Description: "Remove highlighted token"},
				{Keys: "Ctrl+P", Description: "Toggle token palette"},
				{Keys: "Ctrl+Z", Description: "Undo last token change"},
			},
		},
		{
			Title: "Palette",
			Entries: []shortcutEntry{
				{Keys: "Type category=value", Description: "Filter or apply palette entries by slug"},
				{Keys: "Tab", Description: "Advance palette focus (filter → categories → options)"},
				{Keys: "Shift+Tab", Description: "Reverse palette focus order"},
				{Keys: "Enter", Description: "Apply staged edits or move focus into options"},
				{Keys: "Ctrl+W", Description: "Clear palette filter"},
			},
		},
		{
			Title: "History & Presets",
			Entries: []shortcutEntry{
				{Keys: "Ctrl+H", Description: "Toggle history section"},
				{Keys: "Ctrl+Shift+H", Description: "Copy latest history CLI to clipboard"},
				{Keys: "Ctrl+S", Description: "Toggle preset pane"},
				{Keys: "Ctrl+N", Description: "Start preset save"},
				{Keys: "Delete", Description: "Delete selected preset"},
				{Keys: "Ctrl+Z", Description: "Undo last preset deletion"},
			},
		},
		{
			Title: "Environment",
			Entries: []shortcutEntry{
				{Keys: "Tab", Description: "Focus environment allowlist"},
				{Keys: "Up/Down", Description: "Move allowlist selection"},
				{Keys: "Ctrl+E", Description: "Toggle highlighted environment variable"},
				{Keys: "Ctrl+A", Description: "Enable all environment variables"},
				{Keys: "Ctrl+X", Description: "Clear environment allowlist"},
			},
		},
	}
}

func (m *model) renderSidebarContent() string {
	if m.sidebarPreference == sidebarPreferenceHidden {
		return ""
	}
	sections := []string{
		m.renderComposeSection(),
		m.renderHistorySection(),
		m.renderPresetsSection(),
	}

	width := m.sidebarColumnWidth
	if width <= 0 {
		width = 36
	}
	style := lipgloss.NewStyle().Width(width)

	var filtered []string
	for _, section := range sections {
		section = strings.TrimRight(section, "\n")
		if strings.TrimSpace(section) == "" {
			continue
		}
		rendered := style.Render(section)
		filtered = append(filtered, strings.TrimRight(rendered, "\n"))
	}

	if len(filtered) == 0 {
		return ""
	}

	return strings.TrimRight(strings.Join(filtered, "\n\n"), "\n")
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

	if toast := m.renderToastOverlay(); toast != "" {
		b.WriteString(toast)
		b.WriteString("\n\n")
	}

	mainContent := m.renderMainColumnContent()
	sidebarContent := m.renderSidebarContent()

	if m.sidebarColumnWidth > 0 && m.mainColumnWidth > 0 {
		mainRendered := lipgloss.NewStyle().Width(m.mainColumnWidth).Render(mainContent)
		sideRendered := lipgloss.NewStyle().Width(m.sidebarColumnWidth).Render(sidebarContent)
		gap := ""
		if m.columnGap > 0 {
			gap = strings.Repeat(" ", m.columnGap)
		}
		joined := lipgloss.JoinHorizontal(lipgloss.Top, mainRendered, gap, sideRendered)
		b.WriteString(joined)
		b.WriteString("\n")
	} else {
		b.WriteString(mainContent)
		if sidebarContent != "" {
			b.WriteString("\n\n")
			b.WriteString(sidebarContent)
			b.WriteString("\n")
		}
	}

	b.WriteString("Press Ctrl+C or Esc to exit.\n")
	output := b.String()

	if dlg, ok := m.dialogs.top(); ok {
		dialogView := dlg.View(m.dialogViewWidth(), m.height)
		paletteDebugViewSummary(&m, dialogView)
		return dialogView
	}

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
	m.recordTokenSparkline(len(m.tokens))
	m.refreshPreview()
}

func (m *model) recordTokenSparkline(value int) {
	if value < 0 {
		value = 0
	}
	m.tokenSparkline = append(m.tokenSparkline, value)
	if len(m.tokenSparkline) > tokenSparklineWindow {
		trimmed := make([]int, tokenSparklineWindow)
		copy(trimmed, m.tokenSparkline[len(m.tokenSparkline)-tokenSparklineWindow:])
		m.tokenSparkline = trimmed
	}
}

func sparklineBounds(values []int) (int, int) {
	if len(values) == 0 {
		return 0, 0
	}
	min := values[0]
	max := values[0]
	for _, v := range values[1:] {
		if v < min {
			min = v
		}
		if v > max {
			max = v
		}
	}
	return min, max
}

func sparklineString(values []int) string {
	if len(values) == 0 {
		return ""
	}
	const levels = ".:-=+*#@"
	min, max := sparklineBounds(values)
	var builder strings.Builder
	if min == max {
		char := levels[len(levels)-2]
		for range values {
			builder.WriteRune(rune(char))
		}
		return builder.String()
	}
	span := float64(max - min)
	if span <= 0 {
		span = 1
	}
	for _, v := range values {
		normalized := float64(v-min) / span
		idx := int(math.Round(normalized * float64(len(levels)-1)))
		if idx < 0 {
			idx = 0
		}
		if idx >= len(levels) {
			idx = len(levels) - 1
		}
		builder.WriteRune(rune(levels[idx]))
	}
	return builder.String()
}

func (m *model) renderTokenSparklineLine() string {
	if len(m.tokenSparkline) == 0 {
		return ""
	}
	line := sparklineString(m.tokenSparkline)
	if line == "" {
		return ""
	}
	min, max := sparklineBounds(m.tokenSparkline)
	current := len(m.tokens)
	label := fmt.Sprintf("Token telemetry (%d tokens", current)
	if len(m.tokenSparkline) > 1 && min != max {
		label += fmt.Sprintf(", %d–%d", min, max)
	}
	label += fmt.Sprintf("): %s", line)
	return label
}

func tokenToastFragment(category TokenCategory, option TokenOption) string {
	slug := strings.TrimSpace(option.Slug)
	if slug == "" {
		slug = strings.TrimSpace(option.Value)
	}
	categorySegment := strings.TrimSpace(categorySlug(category))
	if categorySegment != "" && slug != "" && !strings.Contains(slug, "=") {
		return fmt.Sprintf("%s=%s", categorySegment, slug)
	}
	if slug != "" {
		return slug
	}
	return categorySegment
}

func (m *model) toastCommandSummary() string {
	command := m.displayCommandString()
	if command == "" {
		command = "bar build"
	}
	return shortenString(command, 48)
}

func (m *model) showToast(message string) tea.Cmd {
	trimmed := limitStatusMessage(strings.TrimSpace(message))
	if trimmed == "" {
		return nil
	}
	m.toastMessage = trimmed
	m.toastVisible = true
	m.toastSequence++
	sequence := m.toastSequence
	return tea.Tick(toastLifetime, func(time.Time) tea.Msg {
		return toastExpiredMsg{sequence: sequence}
	})
}

func (m *model) toastTokenChange(category TokenCategory, option TokenOption, action string) tea.Cmd {
	fragment := strings.TrimSpace(tokenToastFragment(category, option))
	if fragment == "" {
		fragment = "Token"
	}
	action = strings.TrimSpace(action)
	message := fragment
	if action != "" {
		message = fmt.Sprintf("%s %s", fragment, action)
	}
	if command := strings.TrimSpace(m.toastCommandSummary()); command != "" {
		message = fmt.Sprintf("%s · CLI: %s · Ctrl+Z undo", message, command)
	} else {
		message += " · Ctrl+Z undo"
	}
	return m.showToast(message)
}

func (m *model) toastCategoryReset(category TokenCategory) tea.Cmd {
	name := strings.TrimSpace(categorySlug(category))
	if name == "" {
		name = "Tokens"
	}
	message := fmt.Sprintf("%s reset to preset", name)
	if command := strings.TrimSpace(m.toastCommandSummary()); command != "" {
		message = fmt.Sprintf("%s · CLI: %s · Ctrl+Z undo", message, command)
	} else {
		message += " · Ctrl+Z undo"
	}
	return m.showToast(message)
}

func (m *model) toastUndoRestored() tea.Cmd {
	if command := strings.TrimSpace(m.toastCommandSummary()); command != "" {
		return m.showToast(fmt.Sprintf("Tokens undo restored · CLI: %s", command))
	}
	return m.showToast("Tokens undo restored.")
}

func (m *model) renderToastOverlay() string {
	if !m.toastVisible {
		return ""
	}
	message := strings.TrimSpace(m.toastMessage)
	if message == "" {
		return ""
	}
	return composerTheme.toastStyle.Render("Toast: " + message)
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
	m.recordPaletteHistory(historyEventKindClipboard, "Clipboard → preview copied")
}

func (m *model) copyBuildCommandToClipboard() {
	command := joinShellArgs(m.buildCommandArgs())
	if err := m.clipboardWrite(command); err != nil {
		m.statusMessage = fmt.Sprintf("Clipboard write failed: %v", err)
		return
	}
	m.destinationSummary = "clipboard — CLI command copied"
	m.statusMessage = "Copied bar build command to clipboard."
	m.recordPaletteHistory(historyEventKindClipboard, "Clipboard → CLI command copied")
}

func (m *model) copyHistoryCommandToClipboard() tea.Cmd {
	if !m.paletteHistoryVisible {
		m.statusMessage = "History collapsed. Press Ctrl+H to expand before copying."
		return nil
	}
	if len(m.paletteHistory) == 0 {
		m.statusMessage = "No history entries to copy."
		return nil
	}
	for _, event := range m.paletteHistory {
		command := strings.TrimSpace(event.Command)
		if command == "" {
			continue
		}
		if err := m.clipboardWrite(command); err != nil {
			m.statusMessage = fmt.Sprintf("Clipboard write failed: %v", err)
			return nil
		}
		m.destinationSummary = "clipboard — CLI command copied"
		m.statusMessage = "Copied history CLI command to clipboard."
		m.recordPaletteHistory(historyEventKindClipboard, "Clipboard → history CLI command copied")
		return m.showToast(fmt.Sprintf("History CLI copied · CLI: %s", shortenString(command, 48)))
	}
	m.statusMessage = "History entries do not include CLI commands yet."
	return nil
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

func filterPromptArgs(args []string) []string {
	if len(args) == 0 {
		return args
	}
	filtered := make([]string, 0, len(args))
	skipNext := false
	for i := 0; i < len(args); i++ {
		if skipNext {
			skipNext = false
			continue
		}
		if args[i] == "--prompt" {
			skipNext = true
			continue
		}
		filtered = append(filtered, args[i])
	}
	return filtered
}

func (m *model) displayCommandArgs() []string {
	return filterPromptArgs(m.buildCommandArgs())
}

func (m *model) displayCommandString() string {
	command := joinShellArgs(m.displayCommandArgs())
	return sanitizeShellCommand(command)
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
	switch mode {
	case commandModePreview:
		input = m.preview
	case commandModeSubject:
		input = m.subject.Value()
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

	trimmed := strings.TrimRight(m.lastResult.Stdout, "\r\n")
	source := "command stdout"

	if strings.TrimSpace(trimmed) == "" {
		fallback := strings.TrimSpace(m.preview)
		if fallback == "" {
			m.statusMessage = "Last command stdout was empty; nothing to insert."
			return
		}
		trimmed = strings.TrimRight(m.preview, "\r\n")
		source = "preview text"
	}

	m.requestSubjectReplacement(source, trimmed)
	if m.pendingSubject != nil {
		m.applyPendingSubjectReplacement()
	}
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
