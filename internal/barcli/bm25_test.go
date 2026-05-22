package barcli

import (
	"strings"
	"testing"
)

// TestBM25ScoresStemming verifies that a query with an inflected form matches
// a document containing only the root form, via Porter stemming.
func TestBM25ScoresStemming(t *testing.T) {
	docs := []tokenDoc{
		{id: "a", title: "route planner", body: "optimizes route planning for navigation"},
		{id: "b", title: "database", body: "completely unrelated content about databases"},
	}
	scores := bm25Scores(docs, "routing")
	if scores["a"] == 0 {
		t.Errorf("bm25Scores: query 'routing' should match doc containing 'route' via stemming, got score 0")
	}
}


// TestBuildTokenDocsIncludesAxisHeuristics verifies buildTokenDocs includes axis-level
// heuristics in each token's BM25 body so queries like "reasoning approach" match method tokens.
func TestBuildTokenDocsIncludesAxisHeuristics(t *testing.T) {
	g := &Grammar{
		Axes: AxisSection{
			Metadata: map[string]map[string]TaskMetadata{
				"method": {"flow": {Definition: "Linear stage sequencing"}},
			},
			AxisHeuristics: map[string][]string{
				"method": {"reasoning approach", "how to think"},
			},
		},
	}
	docs := buildTokenDocs(g, "")
	var found *tokenDoc
	for i := range docs {
		if docs[i].id == "method:flow" {
			found = &docs[i]
			break
		}
	}
	if found == nil {
		t.Fatal("doc method:flow not found")
	}
	if !strings.Contains(found.body, "reasoning approach") {
		t.Errorf("buildTokenDocs: body for method:flow should contain axis heuristic 'reasoning approach', got: %q", found.body)
	}
}

// TestBuildTokenDocsIncludesAxisDescription verifies buildTokenDocs includes the axis-level
// description in each token's BM25 body.
func TestBuildTokenDocsIncludesAxisDescription(t *testing.T) {
	g := &Grammar{
		Axes: AxisSection{
			Metadata: map[string]map[string]TaskMetadata{
				"method": {"flow": {Definition: "Linear stage sequencing"}},
			},
			AxisDescriptions: map[string]string{
				"method": "Reasoning approach — how to think through the problem",
			},
		},
	}
	docs := buildTokenDocs(g, "")
	var found *tokenDoc
	for i := range docs {
		if docs[i].id == "method:flow" {
			found = &docs[i]
			break
		}
	}
	if found == nil {
		t.Fatal("doc method:flow not found")
	}
	if !strings.Contains(found.body, "Reasoning approach") {
		t.Errorf("buildTokenDocs: body for method:flow should contain axis description, got: %q", found.body)
	}
}

// TestBuildTokenDocsIncludesRoutingConcept verifies buildTokenDocs includes routing_concept
// in the BM25 body for axis tokens.
func TestBuildTokenDocsIncludesRoutingConcept(t *testing.T) {
	g := &Grammar{
		Axes: AxisSection{
			Metadata: map[string]map[string]TaskMetadata{
				"method": {"flow": {Definition: "Linear stage sequencing"}},
			},
			RoutingConcept: map[string]map[string]string{
				"method": {"flow": "sequence steps in a pipeline"},
			},
		},
	}
	docs := buildTokenDocs(g, "")
	var found *tokenDoc
	for i := range docs {
		if docs[i].id == "method:flow" {
			found = &docs[i]
			break
		}
	}
	if found == nil {
		t.Fatal("doc method:flow not found")
	}
	if !strings.Contains(found.body, "sequence steps in a pipeline") {
		t.Errorf("buildTokenDocs: body for method:flow should contain routing_concept, got: %q", found.body)
	}
}

// TestBM25TokenizeStem verifies that bm25Tokenize applies Porter stemming.
func TestBM25TokenizeStem(t *testing.T) {
	cases := []struct {
		in   string
		want string
	}{
		{"routing", "rout"},
		{"routes", "rout"},
	}
	for _, c := range cases {
		got := bm25Tokenize(c.in)
		if len(got) != 1 || got[0] != c.want {
			t.Errorf("bm25Tokenize(%q) = %v, want [%s]", c.in, got, c.want)
		}
	}
}
