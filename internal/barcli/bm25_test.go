package barcli

import "testing"

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
