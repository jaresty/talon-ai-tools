package barcli

import (
	"math/rand"
	"sort"
	"time"
)

// ShuffleOptions configures random prompt generation.
type ShuffleOptions struct {
	Seed    int64
	Include []string
	Exclude []string
	Fill    float64
	Subject string
}

// shuffleStageOrder defines the category order for shuffle, matching TUI2's sequence.
// Per ADR 0086: preset before intent (bundled decision fork first).
var shuffleStageOrder = []string{
	"persona_preset", // Path 1: bundled (preset includes implicit intent)
	"intent",         // Path 2: unbundled (custom build)
	"voice",
	"audience",
	"tone",
	"task",
	"completeness",
	"scope",
	"method",
	"form",
	"channel",
	"directional",
}

// Shuffle generates a prompt by randomly selecting tokens from available categories.
func Shuffle(g *Grammar, opts ShuffleOptions) (*BuildResult, *CLIError) {
	seed := opts.Seed
	if seed == 0 {
		seed = time.Now().UnixNano()
	}
	rng := rand.New(rand.NewSource(seed))

	excludeSet := toSet(opts.Exclude)
	includeSet := toSet(opts.Include)

	var tokens []string
	hasPersonaPreset := false

	for _, stage := range shuffleStageOrder {
		if excludeSet[stage] {
			continue
		}

		// Per ADR 0086: If we selected a persona_preset, skip intent and individual persona axes
		// (voice, audience, tone) since the preset bundles all of them with implicit intent.
		if hasPersonaPreset && (stage == "intent" || stage == "voice" || stage == "audience" || stage == "tone") {
			continue
		}

		// Always include task for valid output
		mustInclude := stage == "task" || includeSet[stage]
		if !mustInclude && rng.Float64() > opts.Fill {
			continue
		}

		// Get tokens for this stage
		stageTokens := getStageTokens(g, stage)
		if len(stageTokens) == 0 {
			continue
		}

		// Pick random token from stage
		token := stageTokens[rng.Intn(len(stageTokens))]
		tokens = append(tokens, token)

		if stage == "persona_preset" {
			hasPersonaPreset = true
		}
	}

	result, err := Build(g, tokens)
	if err != nil {
		return nil, err
	}

	result.Subject = opts.Subject
	result.Tokens = tokens
	result.ReferenceKey = g.ReferenceKey
	result.PlainText = RenderPlainText(result)

	return result, nil
}

// getStageTokens returns available tokens for a given stage, sorted for reproducibility.
func getStageTokens(g *Grammar, stage string) []string {
	var tokens []string

	switch stage {
	case "task":
		tokens = make([]string, 0, len(g.Static.Profiles))
		for name := range g.Static.Profiles {
			tokens = append(tokens, name)
		}
	case "persona_preset":
		tokens = make([]string, 0, len(g.Persona.Presets))
		for name := range g.Persona.Presets {
			tokens = append(tokens, name)
		}
	case "voice", "audience", "tone":
		if axisTokens, ok := g.Persona.Axes[stage]; ok {
			tokens = append([]string(nil), axisTokens...)
		}
	case "intent":
		if intents, ok := g.Persona.Intent.AxisTokens["intent"]; ok {
			tokens = append([]string(nil), intents...)
		}
	case "completeness", "scope", "method", "form", "channel", "directional":
		tokenSet := g.AxisTokenSet(stage)
		tokens = make([]string, 0, len(tokenSet))
		for token := range tokenSet {
			tokens = append(tokens, token)
		}
	default:
		return nil
	}

	// Sort for reproducibility with --seed
	sort.Strings(tokens)
	return tokens
}

// toSet converts a slice to a map for O(1) lookup.
func toSet(items []string) map[string]bool {
	set := make(map[string]bool, len(items))
	for _, item := range items {
		set[item] = true
	}
	return set
}
