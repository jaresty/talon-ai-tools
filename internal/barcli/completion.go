package barcli

import (
	"fmt"
	"io"
	"sort"
	"strconv"
	"strings"
)

const bashCompletionTemplate = `# Bash/Zsh completion for bar generated from the portable grammar CLI.
__bar_%s_completion() {
    local words=("${COMP_WORDS[@]}")
    local cword=$COMP_CWORD

    if [[ $cword -ge ${#words[@]} ]]; then
        words+=("")
    fi

    local suggestions=()
    local IFS=$'\n'
    while IFS=$'\n' read -r line; do
        if [[ -n "$line" ]]; then
            suggestions+=("$line")
        fi
    done < <(command bar __complete %s "$cword" "${words[@]}" 2>/dev/null)

    COMPREPLY=("${suggestions[@]}")
    return 0
}

if [[ -n ${ZSH_VERSION-} ]]; then
    autoload -U +X bashcompinit && bashcompinit
fi

complete -F __bar_%s_completion bar
`

const fishCompletionScript = `# Fish completion for bar generated from the portable grammar CLI.
function __fish_bar_completions
    set -l tokens (commandline -opc)
    if test (count $tokens) -eq 0
        return
    end

    set -l partial (commandline -p)
    if string match -q '* ' -- $partial
        set tokens $tokens ""
    end

    set -l index (math (count $tokens) - 1)
    set -l results (command bar __complete fish $index $tokens)
    for item in $results
        if test -n "$item"
            printf '%s\n' $item
        end
    end
end

complete -c bar -f -a '(__fish_bar_completions)'
`

type completionCatalog struct {
	static          []string
	completeness    []string
	scope           []string
	method          []string
	form            []string
	channel         []string
	directional     []string
	personaPreset   []string
	personaVoice    []string
	personaAudience []string
	personaTone     []string
	personaIntent   []string
	scopeCap        int
	methodCap       int
}

type completionState struct {
	override        bool
	static          bool
	completeness    bool
	scope           map[string]struct{}
	method          map[string]struct{}
	form            bool
	channel         bool
	directional     bool
	personaPreset   bool
	personaVoice    bool
	personaAudience bool
	personaTone     bool
	personaIntent   bool
	scopeCap        int
	methodCap       int
}

var (
	completionCommands = []string{"build", "help", "completion"}
	helpTopics         = []string{"tokens"}
	completionShells   = []string{"bash", "zsh", "fish"}
	buildFlags         = []string{"--prompt", "--input", "--output", "-o", "--json", "--grammar"}
	flagExpectingValue = map[string]struct{}{
		"--prompt":  {},
		"--input":   {},
		"--output":  {},
		"-o":        {},
		"--grammar": {},
	}
)

// GenerateCompletionScript emits the shell-specific completion installer script.
func GenerateCompletionScript(shell string, _ *Grammar) (string, error) {
	shell = strings.ToLower(strings.TrimSpace(shell))
	switch shell {
	case "bash":
		return fmt.Sprintf(bashCompletionTemplate, "bash", "bash", "bash"), nil
	case "zsh":
		return fmt.Sprintf(bashCompletionTemplate, "zsh", "zsh", "zsh"), nil
	case "fish":
		return fishCompletionScript, nil
	default:
		return "", fmt.Errorf("unsupported shell %q", shell)
	}
}

// Complete returns token suggestions for the given command line context.
func Complete(grammar *Grammar, shell string, words []string, index int) ([]string, error) {
	if grammar == nil {
		return nil, fmt.Errorf("grammar not loaded")
	}
	if index < 0 {
		index = 0
	}
	if len(words) == 0 {
		words = []string{"bar"}
	}
	if index >= len(words) {
		words = append(words, "")
	}

	current := ""
	if index < len(words) {
		current = words[index]
	}

	catalog := newCompletionCatalog(grammar)
	normalizedCurrent := strings.TrimSpace(current)

	if index <= 1 {
		return filterByPrefix(completionCommands, normalizedCurrent), nil
	}

	command := words[1]
	switch command {
	case "help":
		if index == 2 {
			return filterByPrefix(helpTopics, normalizedCurrent), nil
		}
		return []string{}, nil
	case "completion":
		if index == 2 {
			return filterByPrefix(completionShells, normalizedCurrent), nil
		}
		return []string{}, nil
	case "build":
		return completeBuild(grammar, catalog, words, index, normalizedCurrent)
	default:
		if index == 2 {
			return filterByPrefix(completionCommands, normalizedCurrent), nil
		}
		return []string{}, nil
	}
}

func completeBuild(grammar *Grammar, catalog completionCatalog, words []string, index int, current string) ([]string, error) {
	if index > 2 {
		prev := words[index-1]
		if _, expect := flagExpectingValue[prev]; expect {
			return []string{}, nil
		}
	}

	if strings.HasPrefix(current, "-") {
		return filterByPrefix(buildFlags, current), nil
	}

	prior := []string{}
	if index > 2 {
		prior = append(prior, words[2:index]...)
	}

	state := collectShorthandState(grammar, prior)
	if strings.Contains(current, "=") {
		state.override = true
	}

	if state.override {
		override := buildOverrideSuggestions(catalog)
		return filterByPrefix(override, current), nil
	}

	stage := state.nextStage(catalog)
	switch stage {
	case "static":
		return filterByPrefix(catalog.static, current), nil
	case "completeness":
		return filterByPrefix(catalog.completeness, current), nil
	case "scope":
		suggestions := excludeUsedTokens(catalog.scope, state.scope)
		return filterByPrefix(suggestions, current), nil
	case "method":
		suggestions := excludeUsedTokens(catalog.method, state.method)
		return filterByPrefix(suggestions, current), nil
	case "form":
		return filterByPrefix(catalog.form, current), nil
	case "channel":
		return filterByPrefix(catalog.channel, current), nil
	case "directional":
		return filterByPrefix(catalog.directional, current), nil
	case "persona":
		persona := buildPersonaSuggestions(catalog, state)
		return filterByPrefix(persona, current), nil
	default:
		return []string{}, nil
	}
}

func newCompletionCatalog(grammar *Grammar) completionCatalog {
	catalog := completionCatalog{
		static:          sortedStaticTokens(grammar),
		completeness:    sortedAxisTokens(grammar, "completeness"),
		scope:           sortedAxisTokens(grammar, "scope"),
		method:          sortedAxisTokens(grammar, "method"),
		form:            sortedAxisTokens(grammar, "form"),
		channel:         sortedAxisTokens(grammar, "channel"),
		directional:     sortedAxisTokens(grammar, "directional"),
		personaPreset:   sortedPersonaPresets(grammar),
		personaVoice:    sortedPersonaTokens(grammar, "voice"),
		personaAudience: sortedPersonaTokens(grammar, "audience"),
		personaTone:     sortedPersonaTokens(grammar, "tone"),
		personaIntent:   sortedPersonaTokens(grammar, "intent"),
		scopeCap:        grammar.Hierarchy.AxisSoftCaps["scope"],
		methodCap:       grammar.Hierarchy.AxisSoftCaps["method"],
	}
	return catalog
}

func sortedStaticTokens(grammar *Grammar) []string {
	set := make(map[string]struct{})
	for name := range grammar.Static.Profiles {
		set[name] = struct{}{}
	}
	for name := range grammar.Static.Descriptions {
		set[name] = struct{}{}
	}
	tokens := setToSortedSlice(set)
	return tokens
}

func sortedAxisTokens(grammar *Grammar, axis string) []string {
	set := grammar.AxisTokenSet(axis)
	return setToSortedSlice(set)
}

func sortedPersonaTokens(grammar *Grammar, axis string) []string {
	set := grammar.PersonaTokenSet(axis)
	return setToSortedSlice(set)
}

func sortedPersonaPresets(grammar *Grammar) []string {
	presets := make([]string, 0, len(grammar.Persona.Presets))
	for key := range grammar.Persona.Presets {
		trimmed := strings.TrimSpace(key)
		if trimmed == "" {
			continue
		}
		presets = append(presets, "persona="+trimmed)
	}
	sort.Strings(presets)
	return presets
}

func setToSortedSlice(set map[string]struct{}) []string {
	if len(set) == 0 {
		return []string{}
	}
	tokens := make([]string, 0, len(set))
	for token := range set {
		trimmed := strings.TrimSpace(token)
		if trimmed == "" {
			continue
		}
		tokens = append(tokens, trimmed)
	}
	sort.Strings(tokens)
	return tokens
}

func collectShorthandState(grammar *Grammar, tokens []string) completionState {
	state := completionState{
		scope:     make(map[string]struct{}),
		method:    make(map[string]struct{}),
		scopeCap:  grammar.Hierarchy.AxisSoftCaps["scope"],
		methodCap: grammar.Hierarchy.AxisSoftCaps["method"],
	}

	normalized := grammar.NormalizeTokens(tokens)
	for i := 0; i < len(normalized); i++ {
		token := strings.TrimSpace(normalized[i])
		if token == "" {
			continue
		}
		lower := strings.ToLower(token)
		if _, ok := flagExpectingValue[token]; ok {
			i++
			continue
		}
		if strings.HasPrefix(lower, "--prompt=") || strings.HasPrefix(lower, "--input=") || strings.HasPrefix(lower, "--output=") || strings.HasPrefix(lower, "--grammar=") {
			continue
		}
		if strings.HasPrefix(token, "-") {
			continue
		}
		if strings.HasPrefix(token, "persona=") && !state.override {
			state.personaPreset = true
			continue
		}
		if strings.Contains(token, "=") {
			state.override = true
			break
		}
		if grammarStaticHas(grammar, token) {
			state.static = true
			continue
		}
		axis := detectAxis(grammar, token)
		switch axis {
		case "completeness":
			state.completeness = true
			continue
		case "scope":
			state.scope[token] = struct{}{}
			continue
		case "method":
			state.method[token] = struct{}{}
			continue
		case "form":
			state.form = true
			continue
		case "channel":
			state.channel = true
			continue
		case "directional":
			state.directional = true
			continue
		}
		personaAxis := detectPersonaAxis(grammar, token)
		switch personaAxis {
		case "voice":
			state.personaVoice = true
		case "audience":
			state.personaAudience = true
		case "tone":
			state.personaTone = true
		case "intent":
			state.personaIntent = true
		}
	}

	return state
}

func (s completionState) nextStage(catalog completionCatalog) string {
	if s.override {
		return "override"
	}
	if !s.static && len(catalog.static) > 0 {
		return "static"
	}
	if !s.completeness && len(catalog.completeness) > 0 {
		return "completeness"
	}
	if len(catalog.scope) > 0 {
		maxScope := len(catalog.scope)
		if s.scopeCap > 0 && s.scopeCap < maxScope {
			maxScope = s.scopeCap
		}
		if maxScope > 0 && len(s.scope) < maxScope {
			return "scope"
		}
	}
	if len(catalog.method) > 0 {
		maxMethod := len(catalog.method)
		if s.methodCap > 0 && s.methodCap < maxMethod {
			maxMethod = s.methodCap
		}
		if maxMethod > 0 && len(s.method) < maxMethod {
			return "method"
		}
	}

	if !s.form && len(catalog.form) > 0 {
		return "form"
	}
	if !s.channel && len(catalog.channel) > 0 {
		return "channel"
	}
	if !s.directional && len(catalog.directional) > 0 {
		return "directional"
	}
	return "persona"
}

func buildOverrideSuggestions(catalog completionCatalog) []string {
	suggestions := make([]string, 0, len(catalog.static)+len(catalog.completeness)+len(catalog.scope)+len(catalog.method)+len(catalog.form)+len(catalog.channel)+len(catalog.directional)+len(catalog.personaVoice)+len(catalog.personaAudience)+len(catalog.personaTone)+len(catalog.personaIntent))
	appendWithPrefix := func(prefix string, tokens []string) {
		for _, token := range tokens {
			suggestions = append(suggestions, prefix+token)
		}
	}

	appendWithPrefix("static=", catalog.static)
	appendWithPrefix("completeness=", catalog.completeness)
	appendWithPrefix("scope=", catalog.scope)
	appendWithPrefix("method=", catalog.method)
	appendWithPrefix("form=", catalog.form)
	appendWithPrefix("channel=", catalog.channel)
	appendWithPrefix("directional=", catalog.directional)
	appendWithPrefix("voice=", catalog.personaVoice)
	appendWithPrefix("audience=", catalog.personaAudience)
	appendWithPrefix("tone=", catalog.personaTone)
	appendWithPrefix("intent=", catalog.personaIntent)

	sort.Strings(suggestions)
	return suggestions
}

func buildPersonaSuggestions(catalog completionCatalog, state completionState) []string {
	suggestions := make([]string, 0)
	if !state.personaPreset {
		suggestions = append(suggestions, catalog.personaPreset...)
	} else {
		suggestions = append(suggestions, catalog.personaPreset...)
	}
	if !state.personaVoice {
		suggestions = append(suggestions, catalog.personaVoice...)
	}
	if !state.personaAudience {
		suggestions = append(suggestions, catalog.personaAudience...)
	}
	if !state.personaTone {
		suggestions = append(suggestions, catalog.personaTone...)
	}
	if !state.personaIntent {
		suggestions = append(suggestions, catalog.personaIntent...)
	}
	suggestions = uniqueStrings(suggestions)
	sort.Strings(suggestions)
	return suggestions
}

func excludeUsedTokens(tokens []string, used map[string]struct{}) []string {
	if len(tokens) == 0 {
		return []string{}
	}
	filtered := make([]string, 0, len(tokens))
	for _, token := range tokens {
		if _, ok := used[token]; ok {
			continue
		}
		filtered = append(filtered, token)
	}
	return filtered
}

func uniqueStrings(values []string) []string {
	if len(values) == 0 {
		return []string{}
	}
	seen := make(map[string]struct{}, len(values))
	out := make([]string, 0, len(values))
	for _, value := range values {
		if value == "" {
			continue
		}
		if _, ok := seen[value]; ok {
			continue
		}
		seen[value] = struct{}{}
		out = append(out, value)
	}
	return out
}

func filterByPrefix(values []string, prefix string) []string {
	if prefix == "" {
		result := make([]string, len(values))
		copy(result, values)
		return result
	}
	filtered := make([]string, 0, len(values))
	for _, value := range values {
		if strings.HasPrefix(value, prefix) {
			filtered = append(filtered, value)
		}
	}
	return filtered
}

func grammarStaticHas(grammar *Grammar, token string) bool {
	if _, ok := grammar.Static.Profiles[token]; ok {
		return true
	}
	if _, ok := grammar.Static.Descriptions[token]; ok {
		return true
	}
	return false
}

func detectAxis(grammar *Grammar, token string) string {
	for _, axis := range grammar.axisPriority {
		if grammarTokenExists(grammar.axisTokens[axis], token) {
			return axis
		}
	}
	for axis, set := range grammar.axisTokens {
		if grammarTokenExists(set, token) {
			return axis
		}
	}
	return ""
}

func detectPersonaAxis(grammar *Grammar, token string) string {
	lowered := strings.ToLower(token)
	for axis, set := range grammar.personaTokens {
		if grammarTokenExists(set, token) {
			return axis
		}
		if grammarTokenExists(set, lowered) {
			return axis
		}
	}
	return ""
}

func grammarTokenExists(set map[string]struct{}, token string) bool {
	if set == nil {
		return false
	}
	_, ok := set[token]
	return ok
}

// runCompletionEngine executes the hidden completion backend.
func runCompletionEngine(opts *cliOptions, stdout, stderr io.Writer) int {
	if len(opts.Tokens) < 2 {
		writeError(stderr, "__complete requires a shell and index")
		return 1
	}

	shell := strings.ToLower(strings.TrimSpace(opts.Tokens[0]))
	index, err := strconv.Atoi(opts.Tokens[1])
	if err != nil {
		writeError(stderr, "invalid completion index")
		return 1
	}

	words := append([]string(nil), opts.Tokens[2:]...)
	if len(words) == 0 {
		words = []string{"bar"}
	}

	grammar, err := LoadGrammar(opts.GrammarPath)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	suggestions, err := Complete(grammar, shell, words, index)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	for _, suggestion := range suggestions {
		if suggestion == "" {
			continue
		}
		fmt.Fprintln(stdout, suggestion)
	}
	return 0
}
