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

	// Add persona presets category
	if presetOptions := buildPersonaPresetOptions(grammar); len(presetOptions) > 0 {
		categories = append(categories, bartui.TokenCategory{
			Key:           "persona_preset",
			Label:         "Preset",
			Kind:          bartui.TokenCategoryKindPersona,
			MaxSelections: 1,
			Options:       presetOptions,
		})
	}

	return categories
}

// buildPersonaPresetOptions builds options for persona presets.
func buildPersonaPresetOptions(grammar *Grammar) []bartui.TokenOption {
	if grammar.Persona.Presets == nil || len(grammar.Persona.Presets) == 0 {
		return nil
	}

	values := make([]string, 0, len(grammar.Persona.Presets))
	for key := range grammar.Persona.Presets {
		trimmed := strings.TrimSpace(key)
		if trimmed != "" {
			values = append(values, trimmed)
		}
	}
	sort.Strings(values)

	options := make([]bartui.TokenOption, 0, len(values))
	for _, value := range values {
		preset := grammar.Persona.Presets[value]
		label := preset.Label
		if label == "" {
			label = displayLabel(value, "")
		}

		// Build fills map from preset's voice, audience, tone
		fills := make(map[string]string)
		if preset.Voice != nil && *preset.Voice != "" {
			fills["voice"] = *preset.Voice
		}
		if preset.Audience != nil && *preset.Audience != "" {
			fills["audience"] = *preset.Audience
		}
		if preset.Tone != nil && *preset.Tone != "" {
			fills["tone"] = *preset.Tone
		}

		personaSlug := ""
		if preset.Spoken != nil {
			personaSlug = strings.TrimSpace(*preset.Spoken)
		}
		if personaSlug == "" {
			personaSlug = strings.TrimSpace(grammar.slugForToken(value))
		}

		options = append(options, bartui.TokenOption{
			Value:       value,
			Slug:        personaSlug,
			Label:       label,
			Description: label,
			Guidance:    grammar.PersonaGuidance("presets", value),
			UseWhen:     grammar.PersonaUseWhen("presets", value),
			Fills:       fills,
		})
	}
	return options
}

func buildStaticCategory(grammar *Grammar) (bartui.TokenCategory, bool) {
	tokens := make(map[string]struct{})

	defaultStatic := strings.TrimSpace(grammar.Hierarchy.Defaults.Task)
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
		description := strings.TrimSpace(grammar.TaskDescription(value))
		shortLabel := grammar.TaskLabel(value)
		label := shortLabel
		if label == "" {
			label = displayLabel(value, description)
		}
		options = append(options, bartui.TokenOption{
			Value:       value,
			Slug:        grammar.slugForToken(value),
			Label:       label,
			Description: description,
			Guidance:    grammar.TaskGuidance(value),
			UseWhen:     grammar.TaskUseWhen(value),
			Kanji:       grammar.TaskKanji(value),
		})
	}

	return bartui.TokenCategory{
		Key:           "task",
		Label:         "Task",
		Kind:          bartui.TokenCategoryKindTask,
		MaxSelections: 1,
		Options:       options,
	}, true
}

// methodCategoryOrder is the canonical display order for method semantic groups (ADR-0144).
var methodCategoryOrder = []string{
	"Reasoning", "Exploration", "Structural", "Diagnostic",
	"Actor-centered", "Temporal/Dynamic", "Comparative", "Generative",
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
		shortLabel := grammar.AxisLabel(axis, value)
		label := shortLabel
		if label == "" {
			label = displayLabel(value, description)
		}
		options = append(options, bartui.TokenOption{
			Value:          value,
			Slug:           grammar.slugForToken(value),
			Label:          label,
			Description:    description,
			Guidance:       grammar.AxisGuidance(axis, value),
			UseWhen:        grammar.AxisUseWhen(axis, value),
			Kanji:          grammar.AxisKanji(axis, value),
			SemanticGroup:  grammar.AxisCategory(axis, value),
			RoutingConcept: grammar.AxisRoutingConcept(axis, value),
		})
	}

	// For axes that have semantic groups, re-sort by (categoryOrder, slug) so
	// tokens are contiguous within each group (ADR-0144).
	if axis == "method" {
		catRank := make(map[string]int, len(methodCategoryOrder))
		for i, cat := range methodCategoryOrder {
			catRank[cat] = i
		}
		sort.SliceStable(options, func(i, j int) bool {
			ri, rj := len(methodCategoryOrder), len(methodCategoryOrder) // uncategorised sink to end
			if r, ok := catRank[options[i].SemanticGroup]; ok {
				ri = r
			}
			if r, ok := catRank[options[j].SemanticGroup]; ok {
				rj = r
			}
			if ri != rj {
				return ri < rj
			}
			return strings.Compare(options[i].Slug, options[j].Slug) < 0
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
		shortLabel := grammar.PersonaLabel(axis, value)
		label := shortLabel
		if label == "" {
			label = displayLabel(value, description)
		}
		options = append(options, bartui.TokenOption{
			Value:       value,
			Slug:        grammar.slugForToken(value),
			Label:       label,
			Description: description,
			Guidance:    grammar.PersonaGuidance(axis, value),
			UseWhen:     grammar.PersonaUseWhen(axis, value),
			Kanji:       grammar.PersonaKanji(axis, value),
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
	case "task":
		return "Task"
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
