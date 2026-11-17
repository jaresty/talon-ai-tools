package barcli

import (
	"bytes"
	"strings"
	"testing"
)

const helpHeuristicsPrefix = "**Heuristics** (when to use): "

// TestHelpTokenHeuristicsBudgetIsFive pins the number of heuristic phrases a
// table cell in `bar help llm` displays. Raising or lowering it changes what
// every table shows, so it must be a deliberate edit to this test.
func TestHelpTokenHeuristicsBudgetIsFive(t *testing.T) {
	if maxTokenHeuristics != 5 {
		t.Fatalf("maxTokenHeuristics changed to %d; update this test only if the display budget is meant to change", maxTokenHeuristics)
	}
}

// TestTableCellHeuristicsAreFirstFive specifies that for every axis token a table
// cell lists exactly the first maxTokenHeuristics stored heuristics, in stored order.
func TestTableCellHeuristicsAreFirstFive(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	checked := 0
	for axis, tokens := range grammar.Axes.Metadata {
		for token, meta := range tokens {
			if len(meta.Heuristics) == 0 {
				continue
			}
			h := meta.Heuristics
			if len(h) > maxTokenHeuristics {
				h = h[:maxTokenHeuristics]
			}
			want := strings.Join(h, "; ")
			if got := axisTokenHeuristics(grammar, axis, token); got != want {
				t.Errorf("TestTableCellHeuristicsAreFirstFive: %s:%s cell = %q, want %q", axis, token, got, want)
			}
			checked++
		}
	}
	if checked == 0 {
		t.Fatalf("TestTableCellHeuristicsAreFirstFive: no tokens checked")
	}
}

// TestHelpTokenListsEveryHeuristic specifies that the single-token view prints every
// stored heuristic of an axis token, however many it has. Only the table cell is capped.
func TestHelpTokenListsEveryHeuristic(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	checked, hiding := 0, 0
	example := ""
	for axis, tokens := range grammar.Axes.Metadata {
		for token, meta := range tokens {
			if len(meta.Heuristics) == 0 {
				continue
			}
			var buf bytes.Buffer
			slug := strings.ReplaceAll(token, " ", "-")
			if err := renderHelpToken(&buf, grammar, slug); err != nil {
				t.Errorf("TestHelpTokenListsEveryHeuristic: %s:%s render error: %v", axis, token, err)
				continue
			}
			out := buf.String()
			if !strings.Contains(out, "# Token: "+slug+" ("+axis+")") {
				continue // slug resolves to a same-named token on another axis
			}
			checked++
			line := ""
			for l := range strings.SplitSeq(out, "\n") {
				if strings.HasPrefix(l, helpHeuristicsPrefix) {
					line = l
					break
				}
			}
			for _, h := range meta.Heuristics {
				if !strings.Contains(line, h) {
					hiding++
					if example == "" {
						example = axis + ":" + token + " omits " + `"` + h + `"`
					}
					break
				}
			}
		}
	}
	if checked == 0 {
		t.Fatalf("TestHelpTokenListsEveryHeuristic: no tokens checked")
	}
	if hiding > 0 {
		t.Errorf("TestHelpTokenListsEveryHeuristic: %d of %d tokens hide heuristics in `bar help token`; first: %s", hiding, checked, example)
	}
}
