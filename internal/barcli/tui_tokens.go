package barcli

import (
	"sort"
	"strings"

	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

func BuildTokenCategories(grammar *Grammar) []bartui.TokenCategory {
	if grammar == nil {
		return nil
	}

	categories := make([]bartui.TokenCategory, 0, 12)
	seen := map[string]bool{}

	if staticCategory, ok := buildStaticCategory(grammar); ok {
		categories = append(categories, staticCategory)
		seen[staticCategory.Key] = true
	}

	orderedAxes := []string{"completeness", "scope", "method", "form", "channel", "directional"}
	for _, axis := range orderedAxes {
		axisKey := normalizeAxis(axis)
		if axisKey == "" || seen[axisKey] {
			continue
		}
		options := buildAxisOptions(grammar, axisKey)
		if len(options) == 0 {
			continue
		}
		categories = append(categories, bartui.TokenCategory{
			Key:           axisKey,
			Label:         axisDisplayLabel(axisKey),
			Kind:          bartui.TokenCategoryKindAxis,
			MaxSelections: normalizeAxisCap(grammar.AxisSoftCap(axisKey)),
			Options:       options,
		})
		seen[axisKey] = true
	}

	for _, axis := range grammar.Hierarchy.AxisPriority {
		axisKey := normalizeAxis(axis)
		if axisKey == "" || seen[axisKey] {
			continue
		}
		options := buildAxisOptions(grammar, axisKey)
		if len(options) == 0 {
			continue
		}
		categories = append(categories, bartui.TokenCategory{
			Key:           axisKey,
			Label:         axisDisplayLabel(axisKey),
			Kind:          bartui.TokenCategoryKindAxis,
			MaxSelections: normalizeAxisCap(grammar.AxisSoftCap(axisKey)),
			Options:       options,
		})
		seen[axisKey] = true
	}

	personaAxes := []struct {
		key   string
		label string
	}{
		{key: "voice", label: "Voice"},
		{key: "audience", label: "Audience"},
		{key: "tone", label: "Tone"},
		{key: "intent", label: "Intent"},
	}
	for _, persona := range personaAxes {
		options := buildPersonaOptions(grammar, persona.key)
		if len(options) == 0 {
			continue
		}
		categories = append(categories, bartui.TokenCategory{
			Key:           persona.key,
			Label:         persona.label,
			Kind:          bartui.TokenCategoryKindPersona,
			MaxSelections: 1,
			Options:       options,
		})
	}

	return categories
}

func buildStaticCategory(grammar *Grammar) (bartui.TokenCategory, bool) {
	tokens := make(map[string]struct{})

	defaultStatic := strings.TrimSpace(grammar.Hierarchy.Defaults.StaticPrompt)
	if defaultStatic != "" {
		tokens[defaultStatic] = struct{}{}
	}

	for name := range grammar.Static.Profiles {
		tokens[name] = struct{}{}
	}
	for name := range grammar.Static.Descriptions {
		tokens[name] = struct{}{}
	}

	values := make([]string, 0, len(tokens))
	for token := range tokens {
		values = append(values, token)
	}
	if len(values) == 0 {
		return bartui.TokenCategory{}, false
	}
	sort.Slice(values, func(i, j int) bool {
		slugI := grammar.slugForToken(values[i])
		slugJ := grammar.slugForToken(values[j])
		if slugI == slugJ {
			return values[i] < values[j]
		}
		return slugI < slugJ
	})

	options := make([]bartui.TokenOption, 0, len(values))
	for _, value := range values {
		description := strings.TrimSpace(grammar.StaticPromptDescription(value))
		options = append(options, bartui.TokenOption{
			Value:       value,
			Slug:        grammar.slugForToken(value),
			Label:       displayLabel(value, description),
			Description: description,
		})
	}

	return bartui.TokenCategory{
		Key:           "static",
		Label:         "Static Prompt",
		Kind:          bartui.TokenCategoryKindStatic,
		MaxSelections: 1,
		Options:       options,
	}, true
}

func buildAxisOptions(grammar *Grammar, axis string) []bartui.TokenOption {
	set := grammar.AxisTokenSet(axis)
	if len(set) == 0 {
		return nil
	}
	values := make([]string, 0, len(set))
	for token := range set {
		values = append(values, token)
	}
	sortTokens(grammar, values)

	options := make([]bartui.TokenOption, 0, len(values))
	for _, value := range values {
		description := strings.TrimSpace(grammar.AxisDescription(axis, value))
		options = append(options, bartui.TokenOption{
			Value:       value,
			Slug:        grammar.slugForToken(value),
			Label:       displayLabel(value, description),
			Description: description,
		})
	}
	return options
}

func buildPersonaOptions(grammar *Grammar, axis string) []bartui.TokenOption {
	set := grammar.PersonaTokenSet(axis)
	if len(set) == 0 {
		return nil
	}
	values := make([]string, 0, len(set))
	for token := range set {
		values = append(values, token)
	}
	sortTokens(grammar, values)

	options := make([]bartui.TokenOption, 0, len(values))
	for _, value := range values {
		description := strings.TrimSpace(grammar.PersonaDescription(axis, value))
		options = append(options, bartui.TokenOption{
			Value:       value,
			Slug:        grammar.slugForToken(value),
			Label:       displayLabel(value, description),
			Description: description,
		})
	}
	return options
}

func sortTokens(grammar *Grammar, values []string) {
	sort.Slice(values, func(i, j int) bool {
		slugI := grammar.slugForToken(values[i])
		slugJ := grammar.slugForToken(values[j])
		if slugI == slugJ {
			return strings.Compare(values[i], values[j]) < 0
		}
		return strings.Compare(slugI, slugJ) < 0
	})
}

func axisDisplayLabel(axis string) string {
	switch axis {
	case "completeness":
		return "Completeness"
	case "scope":
		return "Scope"
	case "method":
		return "Method"
	case "form":
		return "Form"
	case "channel":
		return "Channel"
	case "directional":
		return "Directional"
	case "static":
		return "Static Prompt"
	default:
		return strings.Title(strings.ReplaceAll(axis, "_", " "))
	}
}

func displayLabel(value, description string) string {
	if description != "" {
		return description
	}
	replaced := strings.ReplaceAll(value, "-", " ")
	replaced = strings.ReplaceAll(replaced, "_", " ")
	replaced = strings.TrimSpace(replaced)
	if replaced == "" {
		return value
	}
	return strings.Title(replaced)
}

func normalizeAxisCap(cap int) int {
	if cap <= 0 {
		return 1
	}
	return cap
}
