package barcli

import (
	"fmt"
	"io"
	"sort"
	"strconv"
	"strings"
	"unicode"
)

const bashCompletionTemplate = `# Bash completion for bar generated from the portable grammar CLI.
__bar_%s_completion() {
    local words=("${COMP_WORDS[@]}")
    local cword=$COMP_CWORD

    if [[ $cword -ge ${#words[@]} ]]; then
        words+=("")
    fi

    local suggestions=()
    local line value
    while IFS= read -r line; do
        if [[ -z "$line" ]]; then
            continue
        fi
        value="${line%%$'\t'*}"
        suggestions+=("$value")
    done < <(command bar __complete %s "$cword" "${words[@]}" 2>/dev/null)

    COMPREPLY=("${suggestions[@]}")
    return 0
}

complete -F __bar_%s_completion bar
`

const zshCompletionScript = `#compdef bar

function _bar_cli_completion {
    emulate -L zsh -o no_aliases
    setopt local_options pipefail

    local -a words_array
    words_array=("${words[@]}")

    local cword=$(( CURRENT - 1 ))
    if (( cword < 0 )); then
        cword=0
    fi

    if (( cword >= ${#words_array[@]} )); then
        words_array+=("")
    fi

    local -a candidates
    local value category description display

    while IFS=$'\t' read -r value category description; do
        if [[ -z "$value" ]]; then
            continue
        fi

        display=""
        if [[ -n "$category" ]]; then
            display="$category"
        fi
        if [[ -n "$description" ]]; then
            if [[ -n "$display" ]]; then
                display="$display — $description"
            else
                display="$description"
            fi
        fi
        if [[ -z "$display" ]]; then
            display="$value"
        fi

        display=${display//:/\\:}
        candidates+=("$value:$display")
    done < <(command bar __complete zsh "$cword" "${words_array[@]}" 2>/dev/null)

    if (( ${#candidates[@]} == 0 )); then
        return 1
    fi

    _describe 'bar completions' candidates
}

compdef _bar_cli_completion bar
`

const fishCompletionScript = `# Fish completion for bar generated from the portable grammar CLI.
function __fish_bar_completions
    set -l tokens (commandline -opc)
    set -l partial (commandline -p)
    set -l current (commandline -ct)

    if test (count $tokens) -eq 0
        set tokens ""
    end

    if string match -q '* ' -- $partial
        set tokens $tokens ""
    else if test -n "$current"
        set tokens $tokens $current
    end

    set -l index (math (count $tokens) - 1)
    for item in (command bar __complete fish $index $tokens 2>/dev/null)
        set -l parts (string split '\t' -- "$item")
        set -l value $parts[1]
        if test -z "$value"
            continue
        end
        set -l parts_count (count $parts)
        set -l category ""
        if test $parts_count -ge 2
            set category (string trim -- $parts[2])
        end
        set -l description ""
        if test $parts_count -ge 3
            set -l extras $parts[3..-1]
            set description (string trim -- (string join ' ' $extras))
        end
        set -l display ""
        if test -n "$category" -a -n "$description"
            set display "$category — $description"
        else if test -n "$category"
            set display "$category"
        else if test -n "$description"
            set display "$description"
        end
        if test -n "$display"
            printf "%s\t%s\n" "$value" "$display"
        else
            printf "%s\n" "$value"
        end
    end
end

complete -c bar -e
complete -k -c bar -f -a '(__fish_bar_completions)'
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
	override         bool
	static           bool
	staticClosed     bool
	highestAxisIndex int
	completeness     bool
	scope            map[string]struct{}
	method           map[string]struct{}
	form             bool
	channel          bool
	directional      bool
	personaPreset    bool
	personaVoice     bool
	personaAudience  bool
	personaTone      bool
	personaIntent    bool
	scopeCap         int
	methodCap        int
}

type completionSuggestion struct {
	Value        string
	TrimmedValue string
	Category     string
	Description  string
	AppendSpace  bool
}

func newSuggestion(grammar *Grammar, value, category, description string, appendSpace bool, useSlug bool) completionSuggestion {
	canonicalValue := strings.TrimSpace(value)
	displayValue := canonicalValue
	if useSlug && grammar != nil {
		if slug := grammar.slugForToken(canonicalValue); slug != "" {
			displayValue = slug
		}
	}

	sanitizedValue := sanitizeCompletionField(displayValue)
	trimmedValue := strings.TrimSpace(sanitizedValue)

	sanitizedCategory := strings.TrimSpace(sanitizeCompletionField(category))
	sanitizedDescription := strings.TrimSpace(sanitizeCompletionField(description))
	if sanitizedDescription == "" {
		sanitizedDescription = canonicalValue
	}

	return completionSuggestion{
		Value:        trimmedValue,
		TrimmedValue: trimmedValue,
		Category:     sanitizedCategory,
		Description:  sanitizedDescription,
		AppendSpace:  appendSpace && trimmedValue != "",
	}
}

func suggestionsWithDescriptions(grammar *Grammar, tokens []string, category string, descriptionFn func(string) string, appendSpace bool, useSlug bool) []completionSuggestion {
	suggestions := make([]completionSuggestion, 0, len(tokens))
	for _, token := range tokens {
		desc := ""
		if descriptionFn != nil {
			desc = descriptionFn(token)
		}
		suggestion := newSuggestion(grammar, token, category, desc, appendSpace, useSlug)
		if suggestion.TrimmedValue == "" {
			continue
		}
		suggestions = append(suggestions, suggestion)
	}
	return suggestions
}

func suggestionsFromTokens(grammar *Grammar, tokens []string, category, description string, appendSpace bool, useSlug bool) []completionSuggestion {
	return suggestionsWithDescriptions(grammar, tokens, category, func(string) string {
		return description
	}, appendSpace, useSlug)
}

func sanitizeCompletionField(input string) string {
	if input == "" {
		return ""
	}

	var builder strings.Builder
	builder.Grow(len(input))
	lastWasSpace := false

	for _, r := range input {
		switch r {
		case '\t', '\n', '\r':
			if !lastWasSpace {
				builder.WriteByte(' ')
				lastWasSpace = true
			}
			continue
		}

		if unicode.IsControl(r) {
			continue
		}

		if unicode.IsSpace(r) && r != ' ' {
			if !lastWasSpace {
				builder.WriteByte(' ')
				lastWasSpace = true
			}
			continue
		}

		if r == ' ' {
			if lastWasSpace {
				continue
			}
			builder.WriteByte(' ')
			lastWasSpace = true
			continue
		}

		builder.WriteRune(r)
		lastWasSpace = false
	}

	return builder.String()
}

func appendUniqueSuggestion(list []completionSuggestion, seen map[string]struct{}, suggestion completionSuggestion) []completionSuggestion {
	key := strings.ToLower(strings.TrimSpace(suggestion.TrimmedValue))
	if key == "" {
		return list
	}
	if _, exists := seen[key]; exists {
		return list
	}
	seen[key] = struct{}{}
	return append(list, suggestion)
}

func appendUniqueSuggestions(list []completionSuggestion, seen map[string]struct{}, suggestions []completionSuggestion) []completionSuggestion {
	for _, suggestion := range suggestions {
		list = appendUniqueSuggestion(list, seen, suggestion)
	}
	return list
}

func filterSuggestionsByPrefix(grammar *Grammar, suggestions []completionSuggestion, prefix string) []completionSuggestion {
	trimmedPrefix := strings.TrimSpace(prefix)
	if trimmedPrefix == "" {
		return suggestions
	}

	lowerPrefix := strings.ToLower(trimmedPrefix)
	filtered := make([]completionSuggestion, 0, len(suggestions))
	for _, suggestion := range suggestions {
		value := strings.TrimSpace(suggestion.TrimmedValue)
		if value == "" {
			continue
		}
		lowerValue := strings.ToLower(value)
		if strings.HasPrefix(lowerValue, lowerPrefix) {
			filtered = append(filtered, suggestion)
			continue
		}

		if canonical, ok := grammar.canonicalForInput(value); ok {
			if strings.HasPrefix(strings.ToLower(canonical), lowerPrefix) {
				filtered = append(filtered, suggestion)
				continue
			}
		}

		if slug := grammar.slugForToken(value); slug != "" {
			if strings.HasPrefix(strings.ToLower(slug), lowerPrefix) {
				filtered = append(filtered, suggestion)
			}
		}
	}
	return filtered
}

func buildStaticSuggestions(grammar *Grammar, catalog completionCatalog) []completionSuggestion {
	return suggestionsWithDescriptions(grammar, catalog.static, "static", func(token string) string {
		return strings.TrimSpace(grammar.StaticPromptDescription(token))
	}, false, true)
}

func buildAxisSuggestions(grammar *Grammar, axis string, tokens []string) []completionSuggestion {
	return suggestionsWithDescriptions(grammar, tokens, axis, func(token string) string {
		desc := strings.TrimSpace(grammar.AxisDescription(axis, token))
		if desc == "" {
			return token
		}
		return desc
	}, false, true)
}

func buildScopeSuggestions(grammar *Grammar, catalog completionCatalog, state completionState) []completionSuggestion {
	maxScope := len(catalog.scope)
	if state.scopeCap > 0 && state.scopeCap < maxScope {
		maxScope = state.scopeCap
	}
	if maxScope > 0 && len(state.scope) >= maxScope {
		return nil
	}
	suggestions := excludeUsedTokens(catalog.scope, state.scope)
	if len(suggestions) == 0 {
		return nil
	}
	return suggestionsWithDescriptions(grammar, suggestions, "scope", func(token string) string {
		return strings.TrimSpace(grammar.AxisDescription("scope", token))
	}, false, true)
}

func buildMethodSuggestions(grammar *Grammar, catalog completionCatalog, state completionState) []completionSuggestion {
	maxMethod := len(catalog.method)
	if state.methodCap > 0 && state.methodCap < maxMethod {
		maxMethod = state.methodCap
	}
	if maxMethod > 0 && len(state.method) >= maxMethod {
		return nil
	}
	suggestions := excludeUsedTokens(catalog.method, state.method)
	if len(suggestions) == 0 {
		return nil
	}
	return suggestionsWithDescriptions(grammar, suggestions, "method", func(token string) string {
		return strings.TrimSpace(grammar.AxisDescription("method", token))
	}, false, true)
}

func personaPresetDescription(grammar *Grammar, preset string) string {
	if presetDef, ok := grammar.Persona.Presets[preset]; ok {
		label := strings.TrimSpace(presetDef.Label)
		if label != "" {
			return label
		}
	}
	return preset
}

func buildPersonaSuggestions(grammar *Grammar, catalog completionCatalog, state completionState) []completionSuggestion {
	seen := make(map[string]struct{})
	results := make([]completionSuggestion, 0)
	if !state.personaPreset {
		results = appendUniqueSuggestions(results, seen, suggestionsWithDescriptions(grammar, catalog.personaPreset, "persona.preset", func(token string) string {
			return personaPresetDescription(grammar, token)
		}, false, true))
	}
	if !state.personaVoice {
		results = appendUniqueSuggestions(results, seen, suggestionsWithDescriptions(grammar, catalog.personaVoice, "persona.voice", func(token string) string {
			desc := strings.TrimSpace(grammar.PersonaDescription("voice", token))
			if desc == "" {
				return token
			}
			return desc
		}, false, true))
	}
	if !state.personaAudience {
		results = appendUniqueSuggestions(results, seen, suggestionsWithDescriptions(grammar, catalog.personaAudience, "persona.audience", func(token string) string {
			desc := strings.TrimSpace(grammar.PersonaDescription("audience", token))
			if desc == "" {
				return token
			}
			return desc
		}, false, true))
	}
	if !state.personaTone {
		results = appendUniqueSuggestions(results, seen, suggestionsWithDescriptions(grammar, catalog.personaTone, "persona.tone", func(token string) string {
			desc := strings.TrimSpace(grammar.PersonaDescription("tone", token))
			if desc == "" {
				return token
			}
			return desc
		}, false, true))
	}
	if !state.personaIntent {
		results = appendUniqueSuggestions(results, seen, suggestionsWithDescriptions(grammar, catalog.personaIntent, "persona.intent", func(token string) string {
			desc := strings.TrimSpace(grammar.PersonaDescription("intent", token))
			if desc == "" {
				return token
			}
			return desc
		}, false, true))
	}

	return results
}

func buildOverrideSuggestions(grammar *Grammar, catalog completionCatalog) []completionSuggestion {
	seen := make(map[string]struct{})
	results := make([]completionSuggestion, 0)
	add := func(prefix, category string, tokens []string, descFn func(string) string) {
		for _, token := range tokens {
			slug := token
			if grammar != nil {
				if candidate := strings.TrimSpace(grammar.slugForToken(token)); candidate != "" {
					slug = candidate
				}
			}
			value := prefix + slug
			desc := ""
			if descFn != nil {
				desc = descFn(token)
			}
			if strings.TrimSpace(desc) == "" {
				desc = token
			}
			suggestion := newSuggestion(grammar, value, category, desc, false, false)
			results = appendUniqueSuggestion(results, seen, suggestion)
		}

	}

	add("static=", "override.static", catalog.static, func(token string) string {
		return strings.TrimSpace(grammar.StaticPromptDescription(token))
	})
	add("completeness=", "override.completeness", catalog.completeness, func(token string) string {
		return strings.TrimSpace(grammar.AxisDescription("completeness", token))
	})
	add("scope=", "override.scope", catalog.scope, func(token string) string {
		return strings.TrimSpace(grammar.AxisDescription("scope", token))
	})
	add("method=", "override.method", catalog.method, func(token string) string {
		return strings.TrimSpace(grammar.AxisDescription("method", token))
	})
	add("form=", "override.form", catalog.form, func(token string) string {
		return strings.TrimSpace(grammar.AxisDescription("form", token))
	})
	add("channel=", "override.channel", catalog.channel, func(token string) string {
		return strings.TrimSpace(grammar.AxisDescription("channel", token))
	})
	add("directional=", "override.directional", catalog.directional, func(token string) string {
		return strings.TrimSpace(grammar.AxisDescription("directional", token))
	})
	add("voice=", "override.voice", catalog.personaVoice, func(token string) string {
		return strings.TrimSpace(grammar.PersonaDescription("voice", token))
	})
	add("audience=", "override.audience", catalog.personaAudience, func(token string) string {
		return strings.TrimSpace(grammar.PersonaDescription("audience", token))
	})
	add("tone=", "override.tone", catalog.personaTone, func(token string) string {
		return strings.TrimSpace(grammar.PersonaDescription("tone", token))
	})
	add("intent=", "override.intent", catalog.personaIntent, func(token string) string {
		return strings.TrimSpace(grammar.PersonaDescription("intent", token))
	})
	return results
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
		return zshCompletionScript, nil
	case "fish":
		return fishCompletionScript, nil
	default:
		return "", fmt.Errorf("unsupported shell %q", shell)
	}
}

// Complete returns token suggestions for the given command line context.
func Complete(grammar *Grammar, shell string, words []string, index int) ([]completionSuggestion, error) {
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
	prefix := strings.TrimSpace(current)

	if index <= 1 {
		return filterSuggestionsByPrefix(grammar, suggestionsFromTokens(grammar, completionCommands, "command", "", false, true), prefix), nil
	}

	command := words[1]
	switch command {
	case "help":
		if index == 2 {
			return filterSuggestionsByPrefix(grammar, suggestionsFromTokens(grammar, helpTopics, "help", "", false, true), prefix), nil
		}
		return nil, nil
	case "completion":
		if index == 2 {
			return filterSuggestionsByPrefix(grammar, suggestionsFromTokens(grammar, completionShells, "completion.shell", "", false, true), prefix), nil
		}
		return nil, nil
	case "build":
		return completeBuild(grammar, catalog, words, index, current)
	default:
		if index == 2 {
			return filterSuggestionsByPrefix(grammar, suggestionsFromTokens(grammar, completionCommands, "command", "", false, true), prefix), nil
		}
		return nil, nil
	}
}

func completeBuild(grammar *Grammar, catalog completionCatalog, words []string, index int, current string) ([]completionSuggestion, error) {
	if index > 2 {
		prev := words[index-1]
		if _, expect := flagExpectingValue[prev]; expect {
			return nil, nil
		}
	}

	prefix := strings.TrimSpace(current)

	canonicalCurrent, canonicalOK := grammar.canonicalForInput(current)

	if strings.HasPrefix(current, "-") {
		return filterSuggestionsByPrefix(grammar, suggestionsFromTokens(grammar, buildFlags, "flag", "", false, false), prefix), nil
	}

	prior := []string{}
	if index > 2 {
		prior = append(prior, words[2:index]...)
	}

	state := collectShorthandState(grammar, prior)
	if canonicalOK && strings.Contains(canonicalCurrent, "=") {
		state.override = true
	} else if strings.Contains(current, "=") {
		state.override = true
	}

	seen := make(map[string]struct{})
	staticSuggestions := make([]completionSuggestion, 0)
	optionalSuggestions := make([]completionSuggestion, 0)

	if state.override {
		staticSuggestions = appendUniqueSuggestions(staticSuggestions, seen, buildOverrideSuggestions(grammar, catalog))
		return filterSuggestionsByPrefix(grammar, staticSuggestions, prefix), nil
	}

	if !state.static && !state.staticClosed {
		staticSuggestions = appendUniqueSuggestions(staticSuggestions, seen, buildStaticSuggestions(grammar, catalog))
	}

	axisOrder := make(map[string]int, len(grammar.axisPriority))
	for idx, axis := range grammar.axisPriority {
		axisOrder[axis] = idx
	}

	axisIncluded := make(map[string]bool)

	for idx, axis := range grammar.axisPriority {
		axisIncluded[axis] = true
		if idx < state.highestAxisIndex {
			continue
		}
		switch axis {
		case "completeness":
			if state.completeness {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, "completeness", catalog.completeness))
		case "scope":
			if suggestions := buildScopeSuggestions(grammar, catalog, state); len(suggestions) > 0 {
				optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, suggestions)
			}
		case "method":
			if suggestions := buildMethodSuggestions(grammar, catalog, state); len(suggestions) > 0 {
				optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, suggestions)
			}
		case "form":
			if state.form {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, "form", catalog.form))
		case "channel":
			if state.channel {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, "channel", catalog.channel))
		case "directional":
			if state.directional {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, "directional", catalog.directional))
		default:
			tokens := sortedAxisTokens(grammar, axis)
			if len(tokens) == 0 {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, axis, tokens))
		}
	}

	extraAxes := make([]string, 0)
	for axis := range grammar.axisTokens {
		if axisIncluded[axis] {
			continue
		}
		extraAxes = append(extraAxes, axis)
	}
	sort.Strings(extraAxes)

	for _, axis := range extraAxes {
		axisIncluded[axis] = true
		switch axis {
		case "completeness":
			if state.completeness {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, "completeness", catalog.completeness))
		case "scope":
			if suggestions := buildScopeSuggestions(grammar, catalog, state); len(suggestions) > 0 {
				optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, suggestions)
			}
		case "method":
			if suggestions := buildMethodSuggestions(grammar, catalog, state); len(suggestions) > 0 {
				optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, suggestions)
			}
		case "form":
			if state.form {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, "form", catalog.form))
		case "channel":
			if state.channel {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, "channel", catalog.channel))
		case "directional":
			if state.directional {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, "directional", catalog.directional))
		default:
			tokens := sortedAxisTokens(grammar, axis)
			if len(tokens) == 0 {
				continue
			}
			optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, buildAxisSuggestions(grammar, axis, tokens))
		}
	}

	if persona := buildPersonaSuggestions(grammar, catalog, state); len(persona) > 0 {
		optionalSuggestions = appendUniqueSuggestions(optionalSuggestions, seen, persona)
	}

	results := append(staticSuggestions, optionalSuggestions...)

	return filterSuggestionsByPrefix(grammar, results, prefix), nil
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
	axisOrder := make(map[string]int, len(grammar.axisPriority))
	for idx, axis := range grammar.axisPriority {
		axisOrder[axis] = idx
	}

	state := completionState{
		scope:            make(map[string]struct{}),
		method:           make(map[string]struct{}),
		scopeCap:         grammar.Hierarchy.AxisSoftCaps["scope"],
		methodCap:        grammar.Hierarchy.AxisSoftCaps["method"],
		highestAxisIndex: -1,
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
			if !state.static && !state.staticClosed {
				state.staticClosed = true
			}
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
		if idx, ok := axisOrder[axis]; ok {
			if idx > state.highestAxisIndex {
				state.highestAxisIndex = idx
			}
		} else if axis != "" {
			if state.highestAxisIndex < len(grammar.axisPriority) {
				state.highestAxisIndex = len(grammar.axisPriority)
			}
		}
		if axis != "" && !state.static && !state.staticClosed {
			state.staticClosed = true
		}
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
		if personaAxis != "" {
			if !state.static && !state.staticClosed {
				state.staticClosed = true
			}
		}
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
		if suggestion.TrimmedValue == "" {
			continue
		}
		value := sanitizeCompletionField(suggestion.Value)
		if strings.TrimSpace(value) == "" {
			continue
		}
		category := sanitizeCompletionField(suggestion.Category)
		description := sanitizeCompletionField(suggestion.Description)
		fmt.Fprintf(stdout, "%s\t%s\t%s\n", value, category, description)
	}
	return 0
}
