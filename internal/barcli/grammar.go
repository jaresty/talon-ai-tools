package barcli

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

const (
	envGrammarPath     = "BAR_GRAMMAR_PATH"
	defaultGrammarPath = "build/prompt-grammar.json"
)

// Grammar represents the portable prompt grammar payload exported from Python.
type Grammar struct {
	SchemaVersion string
	Axes          AxisSection
	Static        StaticSection
	Persona       PersonaSection
	Hierarchy     HierarchySection

	axisTokens     map[string]map[string]struct{}
	axisDocs       map[string]map[string]string
	axisPriority   []string
	personaTokens  map[string]map[string]struct{}
	personaDocs    map[string]map[string]string
	multiWordFirst map[string][]multiWordToken
}

type AxisSection struct {
	Definitions map[string]map[string]string
	ListTokens  map[string][]string
}

type StaticSection struct {
	Profiles     map[string]StaticProfile
	Descriptions map[string]string
}

type StaticProfile struct {
	Description string         `json:"description"`
	Axes        map[string]any `json:"axes"`
}

type PersonaSection struct {
	Axes    map[string][]string
	Docs    map[string]map[string]string
	Presets map[string]PersonaPreset
	Spoken  map[string]string
	Intent  IntentSection
}

type multiWordToken struct {
	wordsLower []string
	canonical  string
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
	StaticPrompt string
	Completeness string
}

type rawGrammar struct {
	SchemaVersion string         `json:"schema_version"`
	Axes          rawAxisSection `json:"axes"`
	Static        rawStatic      `json:"static_prompts"`
	Persona       rawPersona     `json:"persona"`
	Hierarchy     rawHierarchy   `json:"hierarchy"`
}

type rawAxisSection struct {
	Definitions map[string]map[string]string `json:"definitions"`
	ListTokens  map[string][]string          `json:"list_tokens"`
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
}

type rawPersona struct {
	Axes    map[string][]string          `json:"axes"`
	Docs    map[string]map[string]string `json:"docs"`
	Presets map[string]PersonaPreset     `json:"presets"`
	Spoken  map[string]string            `json:"spoken_map"`
	Intent  struct {
		AxisTokens map[string][]string `json:"axis_tokens"`
		Docs       map[string]string   `json:"docs"`
	} `json:"intent"`
}

type rawHierarchy struct {
	AxisPriority          []string                       `json:"axis_priority"`
	AxisSoftCaps          map[string]int                 `json:"axis_soft_caps"`
	AxisIncompatibilities map[string]map[string][]string `json:"axis_incompatibilities"`
	Defaults              struct {
		StaticPrompt string `json:"static_prompt"`
		Completeness string `json:"completeness"`
	} `json:"defaults"`
}

// LoadGrammar loads the grammar JSON from disk and normalises it into a helper structure.
func LoadGrammar(path string) (*Grammar, error) {
	if path == "" {
		if env := os.Getenv(envGrammarPath); env != "" {
			path = env
		} else {
			path = defaultGrammarPath
		}
	}

	file, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("open grammar: %w", err)
	}

	var raw rawGrammar
	if err := json.Unmarshal(file, &raw); err != nil {
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
		Axes: AxisSection{
			Definitions: raw.Axes.Definitions,
			ListTokens:  raw.Axes.ListTokens,
		},
		Static: StaticSection{
			Profiles:     profiles,
			Descriptions: raw.Static.Descriptions,
		},
		Persona: PersonaSection{
			Axes:    raw.Persona.Axes,
			Docs:    raw.Persona.Docs,
			Presets: raw.Persona.Presets,
			Spoken:  personaSpoken,
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
				StaticPrompt: raw.Hierarchy.Defaults.StaticPrompt,
				Completeness: raw.Hierarchy.Defaults.Completeness,
			},
		},
	}

	grammar.initialise()

	return grammar, nil
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
			tokenSet[strings.ToLower(canonical)] = struct{}{}
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
			tokenSet[strings.ToLower(canonical)] = struct{}{}
			if _, exists := docMap[canonical]; !exists {
				storeDoc(docMap, canonical, "")
			} else {
				storeDoc(docMap, canonical, docMap[canonical])
			}
			g.registerMultiWord(canonical)
		}
	}
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
	if len(tokens) == 0 {
		return tokens
	}
	normalized := make([]string, 0, len(tokens))
	for i := 0; i < len(tokens); i++ {
		token := strings.TrimSpace(tokens[i])
		if token == "" {
			continue
		}
		if strings.Contains(token, "=") {
			normalized = append(normalized, token)
			continue
		}
		combined, consumed := g.combineMultiWordToken(token, tokens[i+1:])
		normalized = append(normalized, combined)
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

// StaticPromptDescription returns the human readable description for a static prompt.
func (g *Grammar) StaticPromptDescription(name string) string {
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
