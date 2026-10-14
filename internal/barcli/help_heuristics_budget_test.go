package barcli

import (
	"strings"
	"testing"
)

// TestHelpTokenHeuristicsBudgetIsFive pins the number of heuristic phrases
// `bar help token` displays. Raising or lowering it changes what every token
// shows, so it must be a deliberate edit to this test.
func TestHelpTokenHeuristicsBudgetIsFive(t *testing.T) {
	if maxTokenHeuristics != 5 {
		t.Fatalf("maxTokenHeuristics changed to %d; update this test only if the display budget is meant to change", maxTokenHeuristics)
	}
}

// TestHelpTokenShowsOnlyFirstHeuristics specifies that a token with more heuristics
// than the budget displays exactly the first maxTokenHeuristics, in stored order,
// and that every token with at least that many fills the budget.
func TestHelpTokenShowsOnlyFirstHeuristics(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	for token, axis := range map[string]string{"ground": "method", "mirror": "completeness", "pin": "method"} {
		meta := grammar.AxisMetadataFor(axis, token)
		if meta == nil || len(meta.Heuristics) < maxTokenHeuristics {
			t.Fatalf("%s: expected at least %d stored heuristics", token, maxTokenHeuristics)
		}
		want := strings.Join(meta.Heuristics[:maxTokenHeuristics], "; ")
		out, errOut, exit := runHelpToken(t, token)
		if exit != 0 {
			t.Fatalf("%s: exit %d: %s", token, exit, errOut)
		}
		if !strings.Contains(out, "**Heuristics** (when to use): "+want+"\n") {
			t.Fatalf("%s: expected displayed heuristics %q, got:\n%.600s", token, want, out)
		}
	}
}
