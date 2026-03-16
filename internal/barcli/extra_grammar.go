package barcli

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"
)

const envExtraGrammarPath = "BAR_EXTRA_GRAMMAR"

// loadAndMergeExtraGrammar reads the file referenced by BAR_EXTRA_GRAMMAR (if set) and
// merges its tokens into g. Must be called before g.initialise().
func loadAndMergeExtraGrammar(g *Grammar) error {
	path := strings.TrimSpace(os.Getenv(envExtraGrammarPath))
	if path == "" {
		return nil
	}

	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("open extra grammar: %w", err)
	}

	var raw map[string]interface{}
	switch ext := strings.ToLower(filepath.Ext(path)); ext {
	case ".yaml", ".yml":
		if err := yaml.Unmarshal(data, &raw); err != nil {
			return fmt.Errorf("parse extra grammar YAML: %w", err)
		}
	case ".json":
		if err := json.Unmarshal(data, &raw); err != nil {
			return fmt.Errorf("parse extra grammar JSON: %w", err)
		}
	default:
		return fmt.Errorf("extra grammar: unsupported file extension %q (use .yaml, .yml, or .json)", ext)
	}

	mergeUserTokenMap(g, raw)
	return nil
}

// mergeUserTokenMap applies parsed user token data to g. Top-level keys other than
// "namespace" are treated as axis names.
func mergeUserTokenMap(g *Grammar, raw map[string]interface{}) {
	for key, val := range raw {
		if key == "namespace" {
			continue // reserved for phase 3
		}
		axisMap, ok := val.(map[string]interface{})
		if !ok {
			continue
		}
		for tokenKey, tokenVal := range axisMap {
			tokenMap, ok := tokenVal.(map[string]interface{})
			if !ok {
				continue
			}
			mergeToken(g, key, tokenKey, extractUserToken(tokenMap))
		}
	}
}

// extractUserToken converts a raw parsed map into a structured user token.
func extractUserToken(m map[string]interface{}) rawUserToken {
	tok := rawUserToken{}
	if v, ok := m["definition"].(string); ok {
		tok.Definition = v
	}
	if v, ok := m["label"].(string); ok {
		tok.Label = v
	}
	if v, ok := m["routing_concept"].(string); ok {
		tok.RoutingConcept = v
	}
	if v, ok := m["kanji"].(string); ok {
		tok.Kanji = v
	}
	if vs, ok := m["heuristics"].([]interface{}); ok {
		for _, h := range vs {
			if s, ok := h.(string); ok {
				tok.Heuristics = append(tok.Heuristics, s)
			}
		}
	}
	if ds, ok := m["distinctions"].([]interface{}); ok {
		for _, d := range ds {
			dm, ok := d.(map[string]interface{})
			if !ok {
				continue
			}
			dist := TaskMetadataDistinction{}
			if t, ok := dm["token"].(string); ok {
				dist.Token = t
			}
			if n, ok := dm["note"].(string); ok {
				dist.Note = n
			}
			tok.Distinctions = append(tok.Distinctions, dist)
		}
	}
	return tok
}

// rawUserToken holds all fields a user may specify for a single token.
type rawUserToken struct {
	Label          string
	RoutingConcept string
	Kanji          string
	Definition     string
	Heuristics     []string
	Distinctions   []TaskMetadataDistinction
}

// mergeToken writes a single user token into all relevant Grammar axis maps.
// User values win on conflict; zero-value fields leave the existing value unchanged.
func mergeToken(g *Grammar, axis, token string, tok rawUserToken) {
	ensureAxisMaps(g, axis)

	if tok.Definition != "" {
		g.Axes.Definitions[axis][token] = tok.Definition
	}
	if tok.Label != "" {
		g.Axes.Labels[axis][token] = tok.Label
	}
	if tok.Kanji != "" {
		g.Axes.Kanji[axis][token] = tok.Kanji
	}
	if tok.RoutingConcept != "" {
		g.Axes.RoutingConcept[axis][token] = tok.RoutingConcept
	}

	existing := g.Axes.Metadata[axis][token]
	if tok.Definition != "" {
		existing.Definition = tok.Definition
	}
	if len(tok.Heuristics) > 0 {
		existing.Heuristics = tok.Heuristics
	}
	if len(tok.Distinctions) > 0 {
		existing.Distinctions = tok.Distinctions
	}
	g.Axes.Metadata[axis][token] = existing

	// Add to ListTokens if not already present.
	found := false
	for _, t := range g.Axes.ListTokens[axis] {
		if t == token {
			found = true
			break
		}
	}
	if !found {
		g.Axes.ListTokens[axis] = append(g.Axes.ListTokens[axis], token)
	}
}

// ensureAxisMaps initialises nil sub-maps for the given axis across all relevant fields.
func ensureAxisMaps(g *Grammar, axis string) {
	if g.Axes.Definitions == nil {
		g.Axes.Definitions = make(map[string]map[string]string)
	}
	if g.Axes.Definitions[axis] == nil {
		g.Axes.Definitions[axis] = make(map[string]string)
	}
	if g.Axes.Labels == nil {
		g.Axes.Labels = make(map[string]map[string]string)
	}
	if g.Axes.Labels[axis] == nil {
		g.Axes.Labels[axis] = make(map[string]string)
	}
	if g.Axes.Kanji == nil {
		g.Axes.Kanji = make(map[string]map[string]string)
	}
	if g.Axes.Kanji[axis] == nil {
		g.Axes.Kanji[axis] = make(map[string]string)
	}
	if g.Axes.RoutingConcept == nil {
		g.Axes.RoutingConcept = make(map[string]map[string]string)
	}
	if g.Axes.RoutingConcept[axis] == nil {
		g.Axes.RoutingConcept[axis] = make(map[string]string)
	}
	if g.Axes.Metadata == nil {
		g.Axes.Metadata = make(map[string]map[string]TaskMetadata)
	}
	if g.Axes.Metadata[axis] == nil {
		g.Axes.Metadata[axis] = make(map[string]TaskMetadata)
	}
	if g.Axes.ListTokens == nil {
		g.Axes.ListTokens = make(map[string][]string)
	}
	if g.Axes.ListTokens[axis] == nil {
		g.Axes.ListTokens[axis] = []string{}
	}
}
