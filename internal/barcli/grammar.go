package barcli

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"sort"
	"strings"
)

const (
	envGrammarPath = "BAR_GRAMMAR_PATH"
)

var (
	slugInvalidChars   = regexp.MustCompile(`[^a-z0-9_-]+`)
	slugHyphenCollapse = regexp.MustCompile(`-{2,}`)
)

// ReferenceKeyContracts holds per-section inline semantic contracts (ADR-0176).
// Each field is a short interpretation contract emitted inline in the rendered
// prompt immediately after the section header it describes. ConstraintsAxes
// holds per-axis contracts keyed by axis name (completeness, scope, method,
// form, channel, directional).
type ReferenceKeyContracts struct {
	Task            string            `json:"task"`
	Addendum        string            `json:"addendum"`
	Constraints     string            `json:"constraints"`
	ConstraintsAxes map[string]string `json:"constraints_axes"`
	Persona         string            `json:"persona"`
	Subject         string            `json:"subject"`
}

// Grammar represents the portable prompt grammar payload exported from Python.
type Grammar struct {
	SchemaVersion              string
	ReferenceKey               ReferenceKeyContracts
	ExecutionReminder          string
	PlanningDirective          string
	MetaInterpretationGuidance string
	SubjectFraming             string
	Axes              AxisSection
	Static        StaticSection
	Persona       PersonaSection
	Hierarchy     HierarchySection

	Sequences     map[string]Sequence // ADR-0225
	Patterns        []GrammarPattern
	StarterPacks    []StarterPack
	Compositions    []Composition // ADR-0227
	axisTokens      map[string]map[string]struct{}
	axisDocs        map[string]map[string]string
	axisPriority    []string
	personaTokens   map[string]map[string]struct{}
	personaDocs     map[string]map[string]string
	multiWordFirst  map[string][]multiWordToken
	canonicalToSlug map[string]string
	slugToCanonical map[string]string
}

type AxisSection struct {
	Definitions    map[string]map[string]string
	ListTokens     map[string][]string
	Labels         map[string]map[string]string // ADR-0109: short CLI-facing selection labels
	Kanji          map[string]map[string]string // ADR-0143: kanji icons for visual display
	Categories     map[string]map[string]string // ADR-0144: semantic family groupings for method tokens
	CategoryOrder  map[string][]string          // ADR-0144: canonical display order for category groups
	RoutingConcept      map[string]map[string]string            // ADR-0146: distilled routing concept phrases
	CrossAxisComposition   map[string]map[string]map[string]CrossAxisPair // ADR-0147: axis_a→token_a→axis_b→{natural,cautionary}
	AxisDescriptions       map[string]string                              // axis-level empty-state descriptions
	FormDefaultCompleteness map[string]string                             // ADR-0153: per-form-token completeness override
	Metadata                map[string]map[string]TaskMetadata            // ADR-0155: structured metadata per axis token
}

// CrossAxisPair holds the natural/cautionary composition data for one axis_a+token_a+axis_b triple (ADR-0147).
type CrossAxisPair struct {
	Natural         []string          `json:"natural"`
	Cautionary      map[string]string `json:"cautionary"`
	CautionaryNotes map[string]string `json:"cautionary_notes,omitempty"` // ADR-0153: render-time conflict notes
}

// TaskMetadataDistinction is a single cross-token distinction entry (ADR-0154).
type TaskMetadataDistinction struct {
	Token string `json:"token"`
	Note  string `json:"note"`
}

// TaskMetadata holds structured metadata for a task token (ADR-0154).
type TaskMetadata struct {
	Definition   string                    `json:"definition"`
	Heuristics   []string                  `json:"heuristics"`
	Distinctions []TaskMetadataDistinction `json:"distinctions"`
}

type StaticSection struct {
	Profiles       map[string]StaticProfile
	Descriptions   map[string]string
	Labels         map[string]string       // ADR-0109: short CLI-facing selection labels
	Kanji          map[string]string       // ADR-0143: kanji icons for visual display
	RoutingConcept map[string]string       // ADR-0146: distilled routing concept phrases
	Metadata       map[string]TaskMetadata // ADR-0154: structured definition, heuristics, distinctions
}

type StaticProfile struct {
	Description string         `json:"description"`
	Axes        map[string]any `json:"axes"`
}

type PersonaSection struct {
	Axes     map[string][]string
	Docs     map[string]map[string]string
	Labels   map[string]map[string]string // ADR-0111: short CLI-facing labels per axis token
	Kanji          map[string]map[string]string // ADR-0143: kanji icons for visual display
	RoutingConcept map[string]map[string]string // ADR-0146: distilled routing concept phrases
	Metadata       map[string]map[string]TaskMetadata // ADR-0156: structured metadata per persona token
	Presets        map[string]PersonaPreset
	Spoken         map[string]string
	Intent         IntentSection
}

type multiWordToken struct {
	wordsLower []string
	canonical  string
}

type NormalizedToken struct {
	Canonical string
	Source    string
}

type PersonaPreset struct {
	Key      string  `json:"key"`
	Label    string  `json:"label"`
	Spoken   *string `json:"spoken"`
	Voice    *string `json:"voice"`
	Audience *string `json:"audience"`
	Tone     *string `json:"tone"`
}

type IntentSection struct {
	AxisTokens map[string][]string
	Docs       map[string]string
}

type HierarchySection struct {
	AxisPriority          []string
	AxisSoftCaps          map[string]int
	AxisIncompatibilities map[string]map[string][]string
	Defaults              DefaultsSection
}

type DefaultsSection struct {
	Task         string
	Completeness string
}

// StarterPack maps a task framing to a suggested bar build command (ADR-0144 Phase 2).
type StarterPack struct {
	Name    string `json:"name"`
	Framing string `json:"framing"`
	Command string `json:"command"`
}

// GrammarPattern represents a named usage pattern from the SSOT (ADR-0134 D3).
type GrammarPattern struct {
	Title   string              `json:"title"`
	Command string              `json:"command"`
	Example string              `json:"example"`
	Desc    string              `json:"desc"`
	Tokens  map[string][]string `json:"tokens"`
}

type rawGrammar struct {
	SchemaVersion              string           `json:"schema_version"`
	ReferenceKey               ReferenceKeyContracts `json:"reference_key"`
	ExecutionReminder          string           `json:"execution_reminder"`
	PlanningDirective          string           `json:"planning_directive"`
	MetaInterpretationGuidance string           `json:"meta_interpretation_guidance"`
	SubjectFraming             string           `json:"subject_framing"`
	Axes              rawAxisSection   `json:"axes"`
	Static        rawStatic        `json:"tasks"`
	Persona       rawPersona       `json:"persona"`
	Hierarchy     rawHierarchy     `json:"hierarchy"`
	Slugs         rawSlugSection   `json:"slugs"`
	Sequences     map[string]Sequence `json:"sequences"` // ADR-0225
	Patterns      []GrammarPattern    `json:"patterns"`
	StarterPacks  []StarterPack       `json:"starter_packs"`
	Compositions  []Composition       `json:"compositions"` // ADR-0227
}

type rawAxisSection struct {
	Definitions    map[string]map[string]string `json:"definitions"`
	ListTokens     map[string][]string          `json:"list_tokens"`
	Labels         map[string]map[string]string `json:"labels"`           // ADR-0109
	Kanji          map[string]map[string]string `json:"kanji"`            // ADR-0143
	Categories     map[string]map[string]string `json:"categories"`        // ADR-0144
	CategoryOrder  map[string][]string          `json:"category_order"`    // ADR-0144
	RoutingConcept       map[string]map[string]string                `json:"routing_concept"`        // ADR-0146
	CrossAxisComposition    map[string]map[string]map[string]CrossAxisPair `json:"cross_axis_composition"`     // ADR-0147
	AxisDescriptions        map[string]string                              `json:"axis_descriptions"`          // axis-level empty-state descriptions
	FormDefaultCompleteness map[string]string                              `json:"form_default_completeness"`  // ADR-0153
	Metadata                map[string]map[string]TaskMetadata             `json:"metadata"`                   // ADR-0155
}


type rawStatic struct {
	Catalog struct {
		Profiled []struct {
			Name        string         `json:"name"`
			Description string         `json:"description"`
			Axes        map[string]any `json:"axes"`
		} `json:"profiled"`
	} `json:"catalog"`
	Profiles       map[string]StaticProfile `json:"profiles"`
	Descriptions   map[string]string        `json:"descriptions"`
	Labels         map[string]string        `json:"labels"`          // ADR-0109
	Kanji          map[string]string        `json:"kanji"`           // ADR-0143
	RoutingConcept map[string]string        `json:"routing_concept"` // ADR-0146
	Metadata       map[string]TaskMetadata  `json:"metadata"`        // ADR-0154
}

type rawPersona struct {
	Axes     map[string][]string          `json:"axes"`
	Docs     map[string]map[string]string `json:"docs"`
	Labels   map[string]map[string]string `json:"labels"`   // ADR-0111
	Kanji          map[string]map[string]string `json:"kanji"`           // ADR-0143
	RoutingConcept map[string]map[string]string `json:"routing_concept"` // ADR-0146
	Metadata       map[string]map[string]TaskMetadata `json:"metadata"` // ADR-0156
	Presets        map[string]PersonaPreset     `json:"presets"`
	Spoken   map[string]string            `json:"spoken_map"`
	Intent   struct {
		AxisTokens map[string][]string `json:"axis_tokens"`
		Docs       map[string]string   `json:"docs"`
	} `json:"intent"`
}

type rawSlugSection struct {
	Axes            map[string]map[string]string `json:"axes"`
	Static          map[string]string            `json:"task"`
	Persona         rawSlugPersonaSection        `json:"persona"`
	Commands        map[string]string            `json:"commands"`
	Overrides       map[string]map[string]string `json:"overrides"`
	CanonicalToSlug map[string]string            `json:"canonical_to_slug"`
}

type rawSlugPersonaSection struct {
	Axes    map[string]map[string]string `json:"axes"`
	Presets map[string]string            `json:"presets"`
}

type rawHierarchy struct {
	AxisPriority          []string                       `json:"axis_priority"`
	AxisSoftCaps          map[string]int                 `json:"axis_soft_caps"`
	AxisIncompatibilities map[string]map[string][]string `json:"axis_incompatibilities"`
	Defaults              struct {
		Task         string `json:"task"`
		Completeness string `json:"completeness"`
	} `json:"defaults"`
}

// LoadGrammar loads the prompt grammar, preferring the embedded payload unless an override is provided.
func LoadGrammar(path string) (*Grammar, error) {
	data, err := loadGrammarBytes(path)
	if err != nil {
		return nil, err
	}

	var raw rawGrammar
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("parse grammar JSON: %w", err)
	}

	profiles := make(map[string]StaticProfile)
	if len(raw.Static.Profiles) > 0 {
		profiles = raw.Static.Profiles
	} else {
		for _, entry := range raw.Static.Catalog.Profiled {
			profiles[entry.Name] = StaticProfile{
				Description: entry.Description,
				Axes:        entry.Axes,
			}
		}
	}

	personaSpoken := make(map[string]string, len(raw.Persona.Spoken))
	for alias, key := range raw.Persona.Spoken {
		personaSpoken[strings.ToLower(alias)] = key
	}

	grammar := &Grammar{
		SchemaVersion:              raw.SchemaVersion,
		ReferenceKey:               raw.ReferenceKey,
		ExecutionReminder:          raw.ExecutionReminder,
		PlanningDirective:          raw.PlanningDirective,
		MetaInterpretationGuidance: raw.MetaInterpretationGuidance,
		SubjectFraming:             raw.SubjectFraming,
		Sequences:     raw.Sequences,
		Patterns:          raw.Patterns,
		StarterPacks:  raw.StarterPacks,
		Compositions:  raw.Compositions,
		Axes: AxisSection{
			Definitions:    raw.Axes.Definitions,
			ListTokens:     raw.Axes.ListTokens,
			Labels:         raw.Axes.Labels,
			Kanji:          raw.Axes.Kanji,
			Categories:     raw.Axes.Categories,
			CategoryOrder:  raw.Axes.CategoryOrder,
			RoutingConcept:       raw.Axes.RoutingConcept,
			CrossAxisComposition:    raw.Axes.CrossAxisComposition,
			AxisDescriptions:        raw.Axes.AxisDescriptions,
			FormDefaultCompleteness: raw.Axes.FormDefaultCompleteness,
			Metadata:                raw.Axes.Metadata,
		},
		Static: StaticSection{
			Profiles:       profiles,
			Descriptions:   raw.Static.Descriptions,
			Labels:         raw.Static.Labels,
			Kanji:          raw.Static.Kanji,
			RoutingConcept: raw.Static.RoutingConcept,
			Metadata:       raw.Static.Metadata,
		},
		Persona: PersonaSection{
			Axes:           raw.Persona.Axes,
			Docs:           raw.Persona.Docs,
			Labels:         raw.Persona.Labels,
			Kanji:          raw.Persona.Kanji,
			RoutingConcept: raw.Persona.RoutingConcept,
			Metadata:       raw.Persona.Metadata,
			Presets:        raw.Persona.Presets,
			Spoken:   personaSpoken,
			Intent: IntentSection{
				AxisTokens: raw.Persona.Intent.AxisTokens,
				Docs:       raw.Persona.Intent.Docs,
			},
		},
		Hierarchy: HierarchySection{
			AxisPriority:          raw.Hierarchy.AxisPriority,
			AxisSoftCaps:          raw.Hierarchy.AxisSoftCaps,
			AxisIncompatibilities: raw.Hierarchy.AxisIncompatibilities,
			Defaults: DefaultsSection{
				Task:         raw.Hierarchy.Defaults.Task,
				Completeness: raw.Hierarchy.Defaults.Completeness,
			},
		},
	}

	if err := loadAndMergeExtraGrammar(grammar); err != nil {
		return nil, err
	}

	grammar.initialise()
	grammar.initialiseSlugs(raw.Slugs)
	if err := grammar.validateNoPersonaCollisions(); err != nil {
		return nil, err
	}

	return grammar, nil
}

func loadGrammarBytes(requestedPath string) ([]byte, error) {
	path := strings.TrimSpace(requestedPath)
	if path != "" {
		return readGrammarFile(path)
	}

	envPath := strings.TrimSpace(os.Getenv(envGrammarPath))
	if envPath != "" {
		return readGrammarFile(envPath)
	}

	return embeddedGrammarBytes()
}

func readGrammarFile(path string) ([]byte, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("open grammar: %w", err)
	}
	return data, nil
}

func (g *Grammar) initialise() {
	g.axisTokens = make(map[string]map[string]struct{})
	g.axisDocs = make(map[string]map[string]string)
	g.multiWordFirst = make(map[string][]multiWordToken)

	for axis, definitions := range g.Axes.Definitions {
		axisKey := normalizeAxis(axis)
		if axisKey == "" {
			continue
		}
		tokenSet := ensureTokenSet(g.axisTokens, axisKey)
		docMap := ensureDocMap(g.axisDocs, axisKey)
		for token, desc := range definitions {
			canonical := normalizeToken(token)
			if canonical == "" {
				continue
			}
			tokenSet[canonical] = struct{}{}
			storeDoc(docMap, canonical, desc)
			g.registerMultiWord(canonical)
		}
	}

	for axis, tokens := range g.Axes.ListTokens {
		axisKey := normalizeAxis(axis)
		if axisKey == "" {
			continue
		}
		tokenSet := ensureTokenSet(g.axisTokens, axisKey)
		docMap := ensureDocMap(g.axisDocs, axisKey)
		for _, token := range tokens {
			canonical := normalizeToken(token)
			if canonical == "" {
				continue
			}
			tokenSet[canonical] = struct{}{}
			if _, exists := docMap[canonical]; !exists {
				storeDoc(docMap, canonical, "")
			} else {
				storeDoc(docMap, canonical, docMap[canonical])
			}
			g.registerMultiWord(canonical)
		}
	}

	g.axisPriority = make([]string, 0, len(g.Hierarchy.AxisPriority))
	for _, axis := range g.Hierarchy.AxisPriority {
		axisKey := normalizeAxis(axis)
		if axisKey == "" {
			continue
		}
		g.axisPriority = append(g.axisPriority, axisKey)
	}

	g.personaTokens = make(map[string]map[string]struct{})
	g.personaDocs = make(map[string]map[string]string)

	for axis, tokens := range g.Persona.Axes {
		axisKey := normalizeAxis(axis)
		if axisKey == "" {
			continue
		}
		tokenSet := ensureTokenSet(g.personaTokens, axisKey)
		docMap := ensureDocMap(g.personaDocs, axisKey)
		for _, token := range tokens {
			canonical := normalizeToken(token)
			if canonical == "" {
				continue
			}
			tokenSet[canonical] = struct{}{}
			// Only add lowercase alias if different from canonical (for lookup).
			// Don't add duplicate to avoid showing same token twice in completions.
			g.registerMultiWord(canonical)
		}
		if docs, ok := g.Persona.Docs[axis]; ok {
			for token, desc := range docs {
				storeDoc(docMap, token, desc)
			}
		}
	}

	if docs, ok := g.Persona.Docs["intent"]; ok {
		docMap := ensureDocMap(g.personaDocs, "intent")
		for token, desc := range docs {
			storeDoc(docMap, token, desc)
		}
	}

	if docs := g.Persona.Intent.Docs; len(docs) > 0 {
		docMap := ensureDocMap(g.personaDocs, "intent")
		for token, desc := range docs {
			storeDoc(docMap, token, desc)
		}
	}

	if intents, ok := g.Persona.Intent.AxisTokens["intent"]; ok {
		tokenSet := ensureTokenSet(g.personaTokens, "intent")
		docMap := ensureDocMap(g.personaDocs, "intent")
		for _, token := range intents {
			canonical := normalizeToken(token)
			if canonical == "" {
				continue
			}
			tokenSet[canonical] = struct{}{}
			// Don't add lowercase alias to avoid showing same token twice in completions.
			if _, exists := docMap[canonical]; !exists {
				storeDoc(docMap, canonical, "")
			} else {
				storeDoc(docMap, canonical, docMap[canonical])
			}
			g.registerMultiWord(canonical)
		}
	}
}

// validateNoPersonaCollisions ensures no persona token (voice, audience, tone, intent) shares
// a name with any non-persona axis token (tasks, completeness, scope, method, form, channel,
// directional). Such a collision would make positional persona syntax ambiguous.
func (g *Grammar) validateNoPersonaCollisions() error {
	// Build set of all non-persona tokens: axis tokens + static/task tokens.
	nonPersona := make(map[string]string) // canonical token → axis name
	for axis, tokenSet := range g.axisTokens {
		for token := range tokenSet {
			nonPersona[token] = axis
		}
	}
	for token := range g.Static.Profiles {
		if canonical := normalizeToken(token); canonical != "" {
			nonPersona[canonical] = "task"
		}
	}
	for token := range g.Static.Descriptions {
		if canonical := normalizeToken(token); canonical != "" {
			nonPersona[canonical] = "task"
		}
	}

	var collisions []string
	check := func(axisName, token string) {
		canonical := normalizeToken(token)
		if canonical == "" {
			return
		}
		if conflictAxis, ok := nonPersona[canonical]; ok {
			collisions = append(collisions, fmt.Sprintf("persona %s token %q collides with %s token", axisName, canonical, conflictAxis))
		}
	}
	for axisName, tokens := range g.Persona.Axes {
		for _, token := range tokens {
			check(axisName, token)
		}
	}
	if intentTokens, ok := g.Persona.Intent.AxisTokens["intent"]; ok {
		for _, token := range intentTokens {
			check("intent", token)
		}
	}

	if len(collisions) > 0 {
		sort.Strings(collisions)
		return fmt.Errorf("persona token collision(s) detected — positional persona syntax requires unique names: %s", strings.Join(collisions, "; "))
	}
	return nil
}

func normalizeAxis(axis string) string {
	return strings.ToLower(strings.TrimSpace(axis))
}

func normalizeToken(token string) string {
	return strings.TrimSpace(token)
}

func ensureTokenSet(m map[string]map[string]struct{}, axis string) map[string]struct{} {
	set, ok := m[axis]
	if !ok {
		set = make(map[string]struct{})
		m[axis] = set
	}
	return set
}

func ensureDocMap(m map[string]map[string]string, axis string) map[string]string {
	docs, ok := m[axis]
	if !ok {
		docs = make(map[string]string)
		m[axis] = docs
	}
	return docs
}

func storeDoc(docMap map[string]string, token, desc string) {
	canonical := normalizeToken(token)
	if canonical == "" {
		return
	}
	desc = strings.TrimSpace(desc)
	if existing, ok := docMap[canonical]; ok && existing != "" && desc == "" {
		desc = existing
	}
	docMap[canonical] = desc
	lowerKey := strings.ToLower(canonical)
	if existing, ok := docMap[lowerKey]; ok && existing != "" && desc == "" {
		return
	}
	docMap[lowerKey] = desc
}

func slugifyToken(value string) string {
	normalized := strings.ToLower(strings.TrimSpace(value))
	if normalized == "" {
		return ""
	}
	normalized = strings.ReplaceAll(normalized, " ", "-")
	normalized = slugInvalidChars.ReplaceAllString(normalized, "-")
	normalized = slugHyphenCollapse.ReplaceAllString(normalized, "-")
	normalized = strings.Trim(normalized, "-")
	if normalized == "" {
		normalized = "token"
	}
	return normalized
}

func (g *Grammar) initialiseSlugs(raw rawSlugSection) {
	g.canonicalToSlug = make(map[string]string)
	g.slugToCanonical = make(map[string]string)
	for canonical, slug := range raw.CanonicalToSlug {
		trimmedCanonical := strings.TrimSpace(canonical)
		trimmedSlug := strings.TrimSpace(slug)
		if trimmedCanonical == "" || trimmedSlug == "" {
			continue
		}
		g.canonicalToSlug[trimmedCanonical] = trimmedSlug
		g.slugToCanonical[strings.ToLower(trimmedSlug)] = trimmedCanonical
	}

	ensure := func(token string) {
		trimmed := strings.TrimSpace(token)
		if trimmed == "" {
			return
		}
		slug, ok := g.canonicalToSlug[trimmed]
		if !ok {
			slug = slugifyToken(trimmed)
			g.canonicalToSlug[trimmed] = slug
		}
		lower := strings.ToLower(slug)
		if _, exists := g.slugToCanonical[lower]; !exists {
			g.slugToCanonical[lower] = trimmed
		}
	}

	for name := range g.Static.Profiles {
		ensure(name)
		ensure(fmt.Sprintf("task=%s", name))
	}
	for name := range g.Static.Descriptions {
		ensure(name)
		ensure(fmt.Sprintf("task=%s", name))
	}
	for axis, tokens := range g.Axes.Definitions {
		for token := range tokens {
			ensure(token)
			ensure(fmt.Sprintf("%s=%s", axis, token))
		}
	}
	for axis, tokens := range g.Axes.ListTokens {
		for _, token := range tokens {
			ensure(token)
			ensure(fmt.Sprintf("%s=%s", axis, token))
		}
	}
	for axis, tokens := range g.Persona.Axes {
		for _, token := range tokens {
			ensure(token)
			ensure(fmt.Sprintf("%s=%s", axis, token))
		}
	}
	for preset := range g.Persona.Presets {
		ensure(fmt.Sprintf("persona=%s", preset))
	}

	for key, preset := range g.Persona.Presets {
		canonical := fmt.Sprintf("persona=%s", strings.TrimSpace(key))
		if preset.Spoken == nil {
			continue
		}
		spoken := strings.TrimSpace(*preset.Spoken)
		if spoken == "" {
			continue
		}
		candidate := slugifyToken(spoken)
		if candidate == "" {
			continue
		}
		slug := candidate
		lower := strings.ToLower(slug)
		if existing, ok := g.slugToCanonical[lower]; ok && existing != canonical {
			slug = fmt.Sprintf("persona-%s", candidate)
			lower = strings.ToLower(slug)
			if existing, ok := g.slugToCanonical[lower]; ok && existing != canonical {
				slug = slugifyToken(canonical)
				lower = strings.ToLower(slug)
			}
		}
		g.canonicalToSlug[canonical] = slug
		g.slugToCanonical[lower] = canonical
	}

	if intentTokens, ok := g.Persona.Intent.AxisTokens["intent"]; ok {
		for _, token := range intentTokens {
			ensure(token)
			ensure(fmt.Sprintf("intent=%s", token))
		}
	}
	for _, command := range []string{"build", "completion", "help"} {
		ensure(command)
	}
}

// ResolveSlug returns the canonical token form for a slug (e.g. "fip-bog" → "fip bog").
// If no mapping exists, the input is returned unchanged.
func (g *Grammar) ResolveSlug(token string) string {
	canonical, _ := g.canonicalForInput(token)
	return canonical
}

func (g *Grammar) canonicalForInput(token string) (string, bool) {
	trimmed := strings.TrimSpace(token)
	if trimmed == "" {
		return "", false
	}
	lower := strings.ToLower(trimmed)
	if canonical, ok := g.slugToCanonical[lower]; ok {
		return canonical, true
	}
	return trimmed, false
}

func (g *Grammar) slugForToken(token string) string {
	canonical := strings.TrimSpace(token)
	if canonical == "" {
		return ""
	}
	if slug, ok := g.canonicalToSlug[canonical]; ok {
		return slug
	}
	slug := slugifyToken(canonical)
	g.canonicalToSlug[canonical] = slug
	lower := strings.ToLower(slug)
	if _, exists := g.slugToCanonical[lower]; !exists {
		g.slugToCanonical[lower] = canonical
	}
	return slug
}

func (g *Grammar) registerMultiWord(token string) {
	canonical := normalizeToken(token)
	if canonical == "" {
		return
	}
	words := strings.Fields(canonical)
	if len(words) <= 1 {
		return
	}
	wordsLower := make([]string, len(words))
	for i, word := range words {
		wordsLower[i] = strings.ToLower(word)
	}
	first := wordsLower[0]
	g.multiWordFirst[first] = append(g.multiWordFirst[first], multiWordToken{
		wordsLower: wordsLower,
		canonical:  canonical,
	})
}

func (g *Grammar) combineMultiWordToken(initial string, rest []string) (string, int) {
	canonical := normalizeToken(initial)
	if canonical == "" {
		return initial, 0
	}
	first := strings.ToLower(canonical)
	candidates := g.multiWordFirst[first]
	if len(candidates) == 0 {
		return canonical, 0
	}
	bestLen := 1
	bestCanonical := canonical
	for _, candidate := range candidates {
		length := len(candidate.wordsLower)
		if length <= 1 || length-1 > len(rest) {
			continue
		}
		match := true
		for i := 1; i < length; i++ {
			word := strings.TrimSpace(rest[i-1])
			if word == "" || !strings.EqualFold(word, candidate.wordsLower[i]) {
				match = false
				break
			}
		}
		if match && length > bestLen {
			bestLen = length
			bestCanonical = candidate.canonical
		}
	}
	return bestCanonical, bestLen - 1
}

// NormalizeTokens collapses multi-word tokens so the parser can consume them reliably.
func (g *Grammar) NormalizeTokens(tokens []string) []string {
	detailed := g.NormalizeTokensWithSource(tokens)
	if len(detailed) == 0 {
		return []string{}
	}
	normalized := make([]string, 0, len(detailed))
	for _, entry := range detailed {
		normalized = append(normalized, entry.Canonical)
	}
	return normalized
}

// NormalizeTokensWithSource returns canonical tokens and the raw user input that produced them.
func (g *Grammar) NormalizeTokensWithSource(tokens []string) []NormalizedToken {
	if len(tokens) == 0 {
		return []NormalizedToken{}
	}
	normalized := make([]NormalizedToken, 0, len(tokens))
	for i := 0; i < len(tokens); i++ {
		raw := strings.TrimSpace(tokens[i])
		if raw == "" {
			continue
		}
		sourceParts := []string{raw}
		token := raw
		if canonical, ok := g.canonicalForInput(token); ok {
			token = canonical
		}
		if strings.Contains(token, "=") {
			normalized = append(normalized, NormalizedToken{
				Canonical: token,
				Source:    strings.Join(sourceParts, " "),
			})
			continue
		}
		combined, consumed := g.combineMultiWordToken(token, tokens[i+1:])
		if consumed > 0 {
			for j := 0; j < consumed; j++ {
				part := strings.TrimSpace(tokens[i+1+j])
				if part != "" {
					sourceParts = append(sourceParts, part)
				}
			}
		}
		if canonical, ok := g.canonicalForInput(combined); ok {
			combined = canonical
		}
		normalized = append(normalized, NormalizedToken{
			Canonical: combined,
			Source:    strings.Join(sourceParts, " "),
		})
		i += consumed
	}
	return normalized
}

// AxisTokenSet returns a copy of the known tokens for the requested axis.
func (g *Grammar) AxisTokenSet(axis string) map[string]struct{} {
	axisKey := normalizeAxis(axis)
	set := make(map[string]struct{})

	// Special handling for task axis - tasks are stored in Static.Descriptions
	if axisKey == "task" {
		for token := range g.Static.Descriptions {
			canonical := normalizeToken(token)
			if canonical != "" {
				set[canonical] = struct{}{}
			}
		}
		return set
	}

	for token := range g.axisTokens[axisKey] {
		set[token] = struct{}{}
	}
	return set
}

// AxisSoftCap returns the configured selection cap for an axis (0 for unlimited/single-token axes).
func (g *Grammar) AxisSoftCap(axis string) int {
	if g == nil {
		return 0
	}
	axisKey := normalizeAxis(axis)
	if axisKey == "" {
		return 0
	}
	if cap, ok := g.Hierarchy.AxisSoftCaps[axisKey]; ok {
		return cap
	}
	if cap, ok := g.Hierarchy.AxisSoftCaps[axis]; ok {
		return cap
	}
	return 0
}

// AxisDescription returns the canonical description for the given axis token.
func (g *Grammar) AxisDescription(axis, token string) string {
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	if axisKey == "" || tokenKey == "" {
		return ""
	}

	// Special handling for task axis - use TaskDescription
	if axisKey == "task" {
		return g.TaskDescription(tokenKey)
	}

	docs := g.axisDocs[axisKey]
	if docs == nil {
		return ""
	}
	if desc, ok := docs[tokenKey]; ok && desc != "" {
		return desc
	}
	if desc, ok := docs[strings.ToLower(tokenKey)]; ok && desc != "" {
		return desc
	}
	return ""
}

// TaskDescription returns the human readable description for a task token.
func (g *Grammar) TaskDescription(name string) string {
	if p, ok := g.Static.Profiles[name]; ok {
		if p.Description != "" {
			return p.Description
		}
	}
	if d, ok := g.Static.Descriptions[name]; ok {
		return d
	}
	return ""
}

// ResolvePersonaPreset resolves a persona preset token or spoken alias to its canonical preset.
func (g *Grammar) ResolvePersonaPreset(token string) (string, PersonaPreset, bool) {
	if preset, ok := g.Persona.Presets[token]; ok {
		return token, preset, true
	}
	key, ok := g.Persona.Spoken[strings.ToLower(token)]
	if !ok {
		return "", PersonaPreset{}, false
	}
	preset, ok := g.Persona.Presets[key]
	if !ok {
		return "", PersonaPreset{}, false
	}
	return key, preset, true
}

// PersonaTokenSet returns a copy of persona tokens for the requested axis.
func (g *Grammar) PersonaTokenSet(axis string) map[string]struct{} {
	axisKey := normalizeAxis(axis)
	set := make(map[string]struct{})
	for token := range g.personaTokens[axisKey] {
		set[token] = struct{}{}
	}
	return set
}

// PersonaDescription returns the canonical description for the persona axis token.
func (g *Grammar) PersonaDescription(axis, token string) string {
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	if axisKey == "" || tokenKey == "" {
		return ""
	}
	docs := g.personaDocs[axisKey]
	if docs == nil {
		return ""
	}
	if desc, ok := docs[tokenKey]; ok && desc != "" {
		return desc
	}
	if desc, ok := docs[strings.ToLower(tokenKey)]; ok && desc != "" {
		return desc
	}
	return ""
}

// AxisLabel returns the short CLI-facing label for the given axis token (ADR-0109).
// Returns empty string if no label is defined.
func (g *Grammar) AxisLabel(axis, token string) string {
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	if axisKey == "" || tokenKey == "" {
		return ""
	}
	if labels, ok := g.Axes.Labels[axisKey]; ok {
		if label, ok := labels[tokenKey]; ok {
			return label
		}
		if label, ok := labels[strings.ToLower(tokenKey)]; ok {
			return label
		}
	}
	return ""
}

// AxisKanji returns the optional kanji icon for the given axis token (ADR-0143).
// Returns empty string if no kanji is defined.
func (g *Grammar) AxisKanji(axis, token string) string {
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	if axisKey == "" || tokenKey == "" {
		return ""
	}
	if kanjiMap, ok := g.Axes.Kanji[axisKey]; ok {
		if kanji, ok := kanjiMap[tokenKey]; ok {
			return kanji
		}
		if kanji, ok := kanjiMap[strings.ToLower(tokenKey)]; ok {
			return kanji
		}
	}
	return ""
}

// AxisCategory returns the semantic family category for the given axis token (ADR-0144).
// Returns empty string if no category is defined.
func (g *Grammar) AxisCategory(axis, token string) string {
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	if axisKey == "" || tokenKey == "" {
		return ""
	}
	if catMap, ok := g.Axes.Categories[axisKey]; ok {
		if cat, ok := catMap[tokenKey]; ok {
			return cat
		}
		if cat, ok := catMap[strings.ToLower(tokenKey)]; ok {
			return cat
		}
	}
	return ""
}

// TaskLabel returns the short CLI-facing label for the given task token (ADR-0109).
// Returns empty string if no label is defined.
func (g *Grammar) TaskLabel(name string) string {
	key := normalizeToken(name)
	if label, ok := g.Static.Labels[key]; ok {
		return label
	}
	if label, ok := g.Static.Labels[strings.ToLower(key)]; ok {
		return label
	}
	return ""
}

// AxisLevelDescription returns the axis-level empty-state description for a given axis.
// Used by SPA and TUI2 to explain the axis when no token is selected.
func (g *Grammar) AxisLevelDescription(axis string) string {
	if g.Axes.AxisDescriptions == nil {
		return ""
	}
	return g.Axes.AxisDescriptions[normalizeAxis(axis)]
}

// AxisRoutingConcept returns the distilled routing concept phrase for a token (ADR-0146).
// Returns empty string if no concept is defined (only scope and form axes are populated).
func (g *Grammar) AxisRoutingConcept(axis, token string) string {
	if g.Axes.RoutingConcept == nil {
		return ""
	}
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	if axisKey == "" || tokenKey == "" {
		return ""
	}
	if concepts, ok := g.Axes.RoutingConcept[axisKey]; ok {
		if text, ok := concepts[tokenKey]; ok {
			return text
		}
		if text, ok := concepts[strings.ToLower(tokenKey)]; ok {
			return text
		}
	}
	return ""
}

// CrossAxisCompositionFor returns the cross-axis composition entry for a given axis+token pair (ADR-0147).
// Returns nil if no entry is defined. The returned map is keyed by partner axis, each value being
// a CrossAxisPair{Natural: [...], Cautionary: {token: description}}.
func (g *Grammar) CrossAxisCompositionFor(axis, token string) map[string]CrossAxisPair {
	if g.Axes.CrossAxisComposition == nil {
		return nil
	}
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	if axisKey == "" || tokenKey == "" {
		return nil
	}
	if byToken, ok := g.Axes.CrossAxisComposition[axisKey]; ok {
		if entry, ok := byToken[tokenKey]; ok {
			return entry
		}
	}
	return nil
}

// FormDefaultCompletenessFor returns the preferred default completeness token for a form token (ADR-0153).
// Returns "" if no override is defined for the token.
func (g *Grammar) FormDefaultCompletenessFor(formToken string) string {
	if g.Axes.FormDefaultCompleteness == nil {
		return ""
	}
	return g.Axes.FormDefaultCompleteness[normalizeToken(formToken)]
}

// TaskKanji returns the kanji icon for the given task token (ADR-0143).
// Returns empty string if no kanji is defined.
func (g *Grammar) TaskKanji(name string) string {
	key := normalizeToken(name)
	if kanji, ok := g.Static.Kanji[key]; ok {
		return kanji
	}
	if kanji, ok := g.Static.Kanji[strings.ToLower(key)]; ok {
		return kanji
	}
	return ""
}

// TaskRoutingConcept returns the distilled routing concept phrase for a task token (ADR-0146).
// Returns empty string if no concept is defined.
func (g *Grammar) TaskRoutingConcept(name string) string {
	key := normalizeToken(name)
	if concept, ok := g.Static.RoutingConcept[key]; ok {
		return concept
	}
	return ""
}

// TaskMetadataFor returns the structured metadata for a task token (ADR-0154).
// Returns nil if no metadata is defined for the given token.
func (g *Grammar) TaskMetadataFor(name string) *TaskMetadata {
	if g.Static.Metadata == nil {
		return nil
	}
	key := normalizeToken(name)
	if meta, ok := g.Static.Metadata[key]; ok {
		return &meta
	}
	if meta, ok := g.Static.Metadata[strings.ToLower(key)]; ok {
		return &meta
	}
	return nil
}

// AxisMetadataFor returns the structured metadata for an axis token (ADR-0155).
// Returns nil if no metadata is defined for the given axis/token pair.
func (g *Grammar) AxisMetadataFor(axis, token string) *TaskMetadata {
	if g.Axes.Metadata == nil {
		return nil
	}
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	axisMap, ok := g.Axes.Metadata[axisKey]
	if !ok {
		return nil
	}
	if meta, ok := axisMap[tokenKey]; ok {
		return &meta
	}
	if meta, ok := axisMap[strings.ToLower(tokenKey)]; ok {
		return &meta
	}
	return nil
}

// TaskHeuristics returns the heuristic trigger words for a task token (ADR-0154).
// Returns nil if no heuristics are defined for the given token.
func (g *Grammar) TaskHeuristics(name string) []string {
	if meta := g.TaskMetadataFor(name); meta != nil {
		return meta.Heuristics
	}
	return nil
}

// AxisTokenHeuristics returns the heuristic trigger words for an axis token (ADR-0155).
// Returns nil if no heuristics are defined for the given axis/token pair.
func (g *Grammar) AxisTokenHeuristics(axis, token string) []string {
	if meta := g.AxisMetadataFor(axis, token); meta != nil {
		return meta.Heuristics
	}
	return nil
}

// TaskDistinctionTokens returns the token names from distinctions for a task token.
// Returns nil if no distinctions are defined.
func (g *Grammar) TaskDistinctionTokens(name string) []string {
	meta := g.TaskMetadataFor(name)
	if meta == nil || len(meta.Distinctions) == 0 {
		return nil
	}
	tokens := make([]string, len(meta.Distinctions))
	for i, d := range meta.Distinctions {
		tokens[i] = d.Token
	}
	return tokens
}

// AxisTokenDistinctionTokens returns the token names from distinctions for an axis token.
// Returns nil if no distinctions are defined.
func (g *Grammar) AxisTokenDistinctionTokens(axis, token string) []string {
	meta := g.AxisMetadataFor(axis, token)
	if meta == nil || len(meta.Distinctions) == 0 {
		return nil
	}
	tokens := make([]string, len(meta.Distinctions))
	for i, d := range meta.Distinctions {
		tokens[i] = d.Token
	}
	return tokens
}

// PersonaLabel returns the short CLI-facing label for the given persona axis token (ADR-0111).
// Returns empty string if no label is defined.
func (g *Grammar) PersonaLabel(axis, token string) string {
	if g.Persona.Labels == nil {
		return ""
	}
	axisKey := strings.ToLower(strings.TrimSpace(axis))
	if axisKey == "" {
		return ""
	}
	labels, ok := g.Persona.Labels[axisKey]
	if !ok {
		return ""
	}
	// Try exact key, then lowercased.
	tokenKey := strings.TrimSpace(token)
	if label, ok := labels[tokenKey]; ok && label != "" {
		return label
	}
	if label, ok := labels[strings.ToLower(tokenKey)]; ok && label != "" {
		return label
	}
	return ""
}

// PersonaMetadataFor returns the structured metadata for a persona token (ADR-0156).
// Returns nil if no structured metadata is defined for the given axis/token.
func (g *Grammar) PersonaMetadataFor(axis, token string) *TaskMetadata {
	if g.Persona.Metadata == nil {
		return nil
	}
	axisKey := strings.ToLower(strings.TrimSpace(axis))
	if axisKey == "" {
		return nil
	}
	tokens, ok := g.Persona.Metadata[axisKey]
	if !ok {
		return nil
	}
	tokenKey := strings.TrimSpace(token)
	if m, ok := tokens[tokenKey]; ok {
		return &m
	}
	if m, ok := tokens[strings.ToLower(tokenKey)]; ok {
		return &m
	}
	return nil
}

// PersonaKanji returns the kanji icon for the given persona axis token (ADR-0143).
// Returns empty string if no kanji is defined.
func (g *Grammar) PersonaKanji(axis, token string) string {
	if g.Persona.Kanji == nil {
		return ""
	}
	axisKey := strings.ToLower(strings.TrimSpace(axis))
	if axisKey == "" {
		return ""
	}
	kanjiMap, ok := g.Persona.Kanji[axisKey]
	if !ok {
		return ""
	}
	tokenKey := strings.TrimSpace(token)
	if kanji, ok := kanjiMap[tokenKey]; ok && kanji != "" {
		return kanji
	}
	if kanji, ok := kanjiMap[strings.ToLower(tokenKey)]; ok && kanji != "" {
		return kanji
	}
	return ""
}

// PersonaRoutingConcept returns the distilled routing concept phrase for a persona axis token (ADR-0146).
// Returns empty string if no concept is defined.
func (g *Grammar) PersonaRoutingConcept(axis, token string) string {
	if g.Persona.RoutingConcept == nil {
		return ""
	}
	axisKey := strings.ToLower(strings.TrimSpace(axis))
	if axisKey == "" {
		return ""
	}
	rcMap, ok := g.Persona.RoutingConcept[axisKey]
	if !ok {
		return ""
	}
	tokenKey := strings.TrimSpace(token)
	if concept, ok := rcMap[tokenKey]; ok && concept != "" {
		return concept
	}
	if concept, ok := rcMap[strings.ToLower(tokenKey)]; ok && concept != "" {
		return concept
	}
	return ""
}

// GetValidTokensForAxis returns all valid tokens for the specified axis.
// Returns nil if the axis is not recognized.
func (g *Grammar) GetValidTokensForAxis(axis string) []string {
	axisKey := normalizeAxis(axis)
	if axisKey == "" {
		return nil
	}

	// Check if it's a contract axis
	if tokens, ok := g.axisTokens[axisKey]; ok {
		result := make([]string, 0, len(tokens))
		for token := range tokens {
			result = append(result, token)
		}
		sort.Strings(result)
		return result
	}

	// Check if it's a persona axis
	if tokens, ok := g.personaTokens[axisKey]; ok {
		result := make([]string, 0, len(tokens))
		for token := range tokens {
			result = append(result, token)
		}
		sort.Strings(result)
		return result
	}

	return nil
}

// GetAllTasks returns all valid task tokens.
func (g *Grammar) GetAllTasks() []string {
	result := make([]string, 0, len(g.Static.Descriptions))
	for token := range g.Static.Descriptions {
		result = append(result, token)
	}
	sort.Strings(result)
	return result
}

// GetAllAxisTokens returns all valid tokens across all contract axes.
func (g *Grammar) GetAllAxisTokens() []string {
	tokenSet := make(map[string]struct{})

	// Collect all axis tokens
	for _, axisMap := range g.axisTokens {
		for token := range axisMap {
			tokenSet[token] = struct{}{}
		}
	}

	result := make([]string, 0, len(tokenSet))
	for token := range tokenSet {
		result = append(result, token)
	}
	sort.Strings(result)
	return result
}
