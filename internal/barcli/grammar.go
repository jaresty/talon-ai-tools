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

// Grammar represents the portable prompt grammar payload exported from Python.
type Grammar struct {
	SchemaVersion string
	ReferenceKey  string
	Axes          AxisSection
	Static        StaticSection
	Persona       PersonaSection
	Hierarchy     HierarchySection

	Patterns        []GrammarPattern
	StarterPacks    []StarterPack
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
	Definitions map[string]map[string]string
	ListTokens  map[string][]string
	Labels      map[string]map[string]string // ADR-0109: short CLI-facing selection labels
	Guidance    map[string]map[string]string // ADR-0110: selection-oriented prose hints
	UseWhen     map[string]map[string]string // ADR-0132: task-type discoverability hints
	Kanji       map[string]map[string]string // ADR-0143: kanji icons for visual display
	Categories  map[string]map[string]string // ADR-0144: semantic family groupings for method tokens
}

type StaticSection struct {
	Profiles     map[string]StaticProfile
	Descriptions map[string]string
	Labels       map[string]string // ADR-0109: short CLI-facing selection labels
	Guidance     map[string]string // ADR-0110: selection-oriented prose hints
	UseWhen      map[string]string // ADR-0142: routing trigger phrases for nav surfaces
	Kanji        map[string]string // ADR-0143: kanji icons for visual display
}

type StaticProfile struct {
	Description string         `json:"description"`
	Axes        map[string]any `json:"axes"`
}

type PersonaSection struct {
	Axes     map[string][]string
	Docs     map[string]map[string]string
	Labels   map[string]map[string]string // ADR-0111: short CLI-facing labels per axis token
	Guidance map[string]map[string]string // ADR-0112: selection-oriented prose hints
	UseWhen  map[string]map[string]string // ADR-0133: discoverability hints for help llm
	Kanji    map[string]map[string]string // ADR-0143: kanji icons for visual display
	Presets  map[string]PersonaPreset
	Spoken   map[string]string
	Intent   IntentSection
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
	SchemaVersion string           `json:"schema_version"`
	ReferenceKey  string           `json:"reference_key"`
	Axes          rawAxisSection   `json:"axes"`
	Static        rawStatic        `json:"tasks"`
	Persona       rawPersona       `json:"persona"`
	Hierarchy     rawHierarchy     `json:"hierarchy"`
	Slugs         rawSlugSection   `json:"slugs"`
	Patterns      []GrammarPattern `json:"patterns"`
	StarterPacks  []StarterPack    `json:"starter_packs"`
}

type rawAxisSection struct {
	Definitions map[string]map[string]string `json:"definitions"`
	ListTokens  map[string][]string          `json:"list_tokens"`
	Labels      map[string]map[string]string `json:"labels"`   // ADR-0109
	Guidance    map[string]map[string]string `json:"guidance"` // ADR-0110
	UseWhen     map[string]map[string]string `json:"use_when"`    // ADR-0132
	Kanji       map[string]map[string]string `json:"kanji"`       // ADR-0143
	Categories  map[string]map[string]string `json:"categories"`  // ADR-0144
}

type rawStatic struct {
	Catalog struct {
		Profiled []struct {
			Name        string         `json:"name"`
			Description string         `json:"description"`
			Axes        map[string]any `json:"axes"`
		} `json:"profiled"`
	} `json:"catalog"`
	Profiles     map[string]StaticProfile `json:"profiles"`
	Descriptions map[string]string        `json:"descriptions"`
	Labels       map[string]string        `json:"labels"`   // ADR-0109
	Guidance     map[string]string        `json:"guidance"` // ADR-0110
	UseWhen      map[string]string        `json:"use_when"` // ADR-0142
	Kanji        map[string]string        `json:"kanji"`    // ADR-0143
}

type rawPersona struct {
	Axes     map[string][]string          `json:"axes"`
	Docs     map[string]map[string]string `json:"docs"`
	Labels   map[string]map[string]string `json:"labels"`   // ADR-0111
	Guidance map[string]map[string]string `json:"guidance"` // ADR-0112
	UseWhen  map[string]map[string]string `json:"use_when"` // ADR-0133
	Kanji    map[string]map[string]string `json:"kanji"`    // ADR-0143
	Presets  map[string]PersonaPreset     `json:"presets"`
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
		SchemaVersion: raw.SchemaVersion,
		ReferenceKey:  raw.ReferenceKey,
		Patterns:      raw.Patterns,
		StarterPacks:  raw.StarterPacks,
		Axes: AxisSection{
			Definitions: raw.Axes.Definitions,
			ListTokens:  raw.Axes.ListTokens,
			Labels:      raw.Axes.Labels,
			Guidance:    raw.Axes.Guidance,
			UseWhen:     raw.Axes.UseWhen,
			Kanji:       raw.Axes.Kanji,
			Categories:  raw.Axes.Categories,
		},
		Static: StaticSection{
			Profiles:     profiles,
			Descriptions: raw.Static.Descriptions,
			Labels:       raw.Static.Labels,
			Guidance:     raw.Static.Guidance,
			UseWhen:      raw.Static.UseWhen,
			Kanji:        raw.Static.Kanji,
		},
		Persona: PersonaSection{
			Axes:     raw.Persona.Axes,
			Docs:     raw.Persona.Docs,
			Labels:   raw.Persona.Labels,
			Guidance: raw.Persona.Guidance,
			UseWhen:  raw.Persona.UseWhen,
			Kanji:    raw.Persona.Kanji,
			Presets:  raw.Persona.Presets,
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

// AxisGuidance returns the optional selection-guidance text for the given axis token (ADR-0110).
// Returns empty string if no guidance is defined.
func (g *Grammar) AxisGuidance(axis, token string) string {
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	if axisKey == "" || tokenKey == "" {
		return ""
	}
	if guidance, ok := g.Axes.Guidance[axisKey]; ok {
		if text, ok := guidance[tokenKey]; ok {
			return text
		}
		if text, ok := guidance[strings.ToLower(tokenKey)]; ok {
			return text
		}
	}
	return ""
}

// AxisGuidanceMap returns all guidance text for a given axis as a map.
// Used to render guidance section dynamically from axis configuration.
func (g *Grammar) AxisGuidanceMap(axis string) map[string]string {
	axisKey := normalizeAxis(axis)
	if axisKey == "" {
		return nil
	}
	if guidance, ok := g.Axes.Guidance[axisKey]; ok {
		return guidance
	}
	return nil
}

// AxisUseWhen returns the use_when discoverability hint for a token (ADR-0132).
// Returns empty string if no hint is defined.
func (g *Grammar) AxisUseWhen(axis, token string) string {
	if g.Axes.UseWhen == nil {
		return ""
	}
	axisKey := normalizeAxis(axis)
	tokenKey := normalizeToken(token)
	if axisKey == "" || tokenKey == "" {
		return ""
	}
	if hints, ok := g.Axes.UseWhen[axisKey]; ok {
		if text, ok := hints[tokenKey]; ok {
			return text
		}
		if text, ok := hints[strings.ToLower(tokenKey)]; ok {
			return text
		}
	}
	return ""
}

// TaskGuidance returns the optional selection-guidance text for the given task token (ADR-0110).
// Returns empty string if no guidance is defined.
func (g *Grammar) TaskGuidance(name string) string {
	key := normalizeToken(name)
	if text, ok := g.Static.Guidance[key]; ok {
		return text
	}
	if text, ok := g.Static.Guidance[strings.ToLower(key)]; ok {
		return text
	}
	return ""
}

// TaskUseWhen returns the routing trigger phrase for the given task token (ADR-0142).
// Returns empty string if no use_when is defined.
func (g *Grammar) TaskUseWhen(name string) string {
	key := normalizeToken(name)
	if text, ok := g.Static.UseWhen[key]; ok {
		return text
	}
	if text, ok := g.Static.UseWhen[strings.ToLower(key)]; ok {
		return text
	}
	return ""
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

// PersonaGuidance returns the optional selection-guidance text for the given persona axis token (ADR-0112).
// Returns empty string if no guidance is defined.
func (g *Grammar) PersonaGuidance(axis, token string) string {
	if g.Persona.Guidance == nil {
		return ""
	}
	axisKey := strings.ToLower(strings.TrimSpace(axis))
	if axisKey == "" {
		return ""
	}
	guidance, ok := g.Persona.Guidance[axisKey]
	if !ok {
		return ""
	}
	tokenKey := strings.TrimSpace(token)
	if text, ok := guidance[tokenKey]; ok && text != "" {
		return text
	}
	if text, ok := guidance[strings.ToLower(tokenKey)]; ok && text != "" {
		return text
	}
	return ""
}

// PersonaUseWhen returns the use_when discoverability hint for the given persona axis token (ADR-0133).
// Returns empty string if no hint is defined.
func (g *Grammar) PersonaUseWhen(axis, token string) string {
	if g.Persona.UseWhen == nil {
		return ""
	}
	axisKey := strings.ToLower(strings.TrimSpace(axis))
	if axisKey == "" {
		return ""
	}
	hints, ok := g.Persona.UseWhen[axisKey]
	if !ok {
		return ""
	}
	tokenKey := strings.TrimSpace(token)
	if text, ok := hints[tokenKey]; ok && text != "" {
		return text
	}
	if text, ok := hints[strings.ToLower(tokenKey)]; ok && text != "" {
		return text
	}
	return ""
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
