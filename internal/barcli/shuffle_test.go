package barcli

import (
	"testing"
)

// TestGetStageTokensTopology specifies that getStageTokens returns a non-empty
// slice for the "topology" stage. ADR-0085: topology axis added to shuffle pool.
func TestGetStageTokensTopology(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	tokens := getStageTokens(grammar, "topology")
	if len(tokens) == 0 {
		t.Errorf("getStageTokens(grammar, \"topology\") returned empty slice; topology tokens must be included in shuffle pool")
	}
}

// TestShuffleIncludesTopology specifies that bar shuffle --include topology
// selects a topology token. ADR-0085.
func TestShuffleIncludesTopology(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	result, err := Shuffle(grammar, ShuffleOptions{
		Seed:    42,
		Include: []string{"topology"},
		Fill:    0.0,
	})
	if err != nil {
		t.Fatalf("Shuffle returned error: %v", err)
	}
	topologyTokens := getStageTokens(grammar, "topology")
	topologySet := make(map[string]bool, len(topologyTokens))
	for _, tok := range topologyTokens {
		topologySet[tok] = true
	}
	found := false
	for _, tok := range result.Tokens {
		if topologySet[tok] {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("Shuffle with --include topology produced no topology token; tokens: %v", result.Tokens)
	}
}
