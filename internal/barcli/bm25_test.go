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

// TestBM25ScoresRRFFormula verifies that bm25ScoresRRF computes Σ 1/(60+rank_f)
// across per-field corpora: a token ranking 1st in title only scores 1/61.
func TestBM25ScoresRRFFormula(t *testing.T) {
	// doc "a" has query word in title only; doc "b" has it in definition only.
	docs := []tokenDoc{
		{id: "a", title: "widget", heuristics: "unrelated", distinctions: "unrelated", definition: "unrelated"},
		{id: "b", title: "unrelated", heuristics: "unrelated", distinctions: "unrelated", definition: "widget"},
	}
	scores := bm25ScoresRRF(docs, "widget")
	if scores["a"] == 0 {
		t.Error("bm25ScoresRRF: doc with query in title should have non-zero RRF score")
	}
	if scores["b"] == 0 {
		t.Error("bm25ScoresRRF: doc with query in definition should have non-zero RRF score")
	}
	// Both rank 1st in their respective field and are absent from the other three.
	// Each should score exactly 1/(60+1) = 1/61.
	want := 1.0 / 61.0
	const eps = 1e-9
	if got := scores["a"]; got < want-eps || got > want+eps {
		t.Errorf("bm25ScoresRRF: doc 'a' (title-only match) score = %v, want %v", got, want)
	}
	if got := scores["b"]; got < want-eps || got > want+eps {
		t.Errorf("bm25ScoresRRF: doc 'b' (definition-only match) score = %v, want %v", got, want)
	}
}

// TestBM25ScoresRRFExclusion verifies tokens absent from all field rankings are excluded.
func TestBM25ScoresRRFExclusion(t *testing.T) {
	docs := []tokenDoc{
		{id: "match", title: "widget", heuristics: "widget", distinctions: "widget", definition: "widget"},
		{id: "nomatch", title: "unrelated", heuristics: "unrelated", distinctions: "unrelated", definition: "unrelated"},
	}
	scores := bm25ScoresRRF(docs, "widget")
	if _, ok := scores["nomatch"]; ok {
		t.Error("bm25ScoresRRF: token absent from all field rankings should be excluded from results")
	}
	// Also verify no zero-score entry leaks into the result map.
	for id, s := range scores {
		if s == 0 {
			t.Errorf("bm25ScoresRRF: result map contains zero-score entry for %q", id)
		}
	}
}

// TestBM25ScoresRRFFieldIsolation verifies each field corpus contains only its own text.
// Doc "a" has "alpha" only in heuristics; doc "b" has empty heuristics but "alpha" must not
// bleed from doc "a"'s heuristics into the definition corpus where doc "b" ranks.
func TestBM25ScoresRRFFieldIsolation(t *testing.T) {
	docs := []tokenDoc{
		// "alpha" in heuristics only; definition is unique "zeta"
		{id: "a", title: "unrelated", heuristics: "alpha", distinctions: "unrelated", definition: "zeta"},
		// "alpha" absent from all fields; definition is unique "zeta" too — so if heuristics bled into definition, both would rank in definition corpus
		{id: "b", title: "unrelated", heuristics: "", distinctions: "unrelated", definition: "zeta"},
	}
	scores := bm25ScoresRRF(docs, "alpha")
	if scores["a"] == 0 {
		t.Error("bm25ScoresRRF field isolation: doc with query in heuristics should score non-zero")
	}
	if _, ok := scores["b"]; ok {
		t.Error("bm25ScoresRRF field isolation: doc without query in any field should be excluded even if other fields share text")
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
