package main

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"sync"
)

//go:embed internal/delegate_fixtures.json
var embeddedDelegateFixtures []byte

var (
	fixtureOnce   sync.Once
	fixtureLookup map[string]map[string]any
)

func loadEmbeddedFixtures() map[string]map[string]any {
	fixtureOnce.Do(func() {
		if len(strings.TrimSpace(string(embeddedDelegateFixtures))) == 0 {
			fixtureLookup = map[string]map[string]any{}
			return
		}
		var raw map[string]map[string]any
		if err := json.Unmarshal(embeddedDelegateFixtures, &raw); err != nil {
			fmt.Fprintf(os.Stderr, "bar: failed to parse embedded delegate fixtures: %v\n", err)
			fixtureLookup = map[string]map[string]any{}
			return
		}

		normalised := make(map[string]map[string]any, len(raw))
		for key, value := range raw {
			if key == "" {
				continue
			}
			lowered := strings.ToLower(strings.TrimSpace(key))
			if lowered == "" {
				continue
			}
			normalised[lowered] = value
		}
		fixtureLookup = normalised
	})
	return fixtureLookup
}

func embeddedDelegateFixture(key string) map[string]any {
	fixtures := loadEmbeddedFixtures()
	if fixtures == nil {
		return nil
	}
	normalised := strings.ToLower(strings.TrimSpace(key))
	if normalised == "" {
		return nil
	}
	payload, ok := fixtures[normalised]
	if !ok {
		return nil
	}
	return cloneMap(payload)
}

func cloneMap(source map[string]any) map[string]any {
	if source == nil {
		return nil
	}
	clone := make(map[string]any, len(source))
	for key, value := range source {
		clone[key] = cloneValue(value)
	}
	return clone
}

func cloneSlice(source []any) []any {
	if source == nil {
		return nil
	}
	clone := make([]any, len(source))
	for index, value := range source {
		clone[index] = cloneValue(value)
	}
	return clone
}

func cloneValue(value any) any {
	switch typed := value.(type) {
	case map[string]any:
		return cloneMap(typed)
	case []any:
		return cloneSlice(typed)
	default:
		return typed
	}
}
