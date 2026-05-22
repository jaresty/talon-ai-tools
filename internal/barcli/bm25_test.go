package barcli

import (
	"math"
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

// TestHybridScore verifies hybridScore returns a weighted combination of BM25 and cosine scores.
func TestHybridScore(t *testing.T) {
	// bm25=1.0, cosine=0.0 → 0.4*1.0 + 0.6*0.0 = 0.4
	got := hybridScore(1.0, 0.0)
	if math.Abs(got-0.4) > 1e-9 {
		t.Errorf("hybridScore(1.0, 0.0) = %v, want 0.4", got)
	}
	// bm25=0.0, cosine=1.0 → 0.4*0.0 + 0.6*1.0 = 0.6
	got2 := hybridScore(0.0, 1.0)
	if math.Abs(got2-0.6) > 1e-9 {
		t.Errorf("hybridScore(0.0, 1.0) = %v, want 0.6", got2)
	}
	// hybrid of unequal scores differs from both inputs
	got3 := hybridScore(1.0, 0.5)
	// 0.4*1.0 + 0.6*0.5 = 0.7
	if math.Abs(got3-0.7) > 1e-9 {
		t.Errorf("hybridScore(1.0, 0.5) = %v, want 0.7", got3)
	}
}

// TestBuildTokenDocsPopulatesEmbedding verifies buildTokenDocs copies Embedding from TaskMetadata.
func TestBuildTokenDocsPopulatesEmbedding(t *testing.T) {
	g := &Grammar{
		Axes: AxisSection{
			Metadata: map[string]map[string]TaskMetadata{
				"scope": {
					"narrow": {Definition: "narrow scope", Embedding: []float32{0.1, 0.2}},
				},
			},
		},
	}
	docs := buildTokenDocs(g, "")
	if len(docs) == 0 {
		t.Fatal("expected at least one doc")
	}
	var found *tokenDoc
	for i := range docs {
		if docs[i].id == "scope:narrow" {
			found = &docs[i]
			break
		}
	}
	if found == nil {
		t.Fatal("doc scope:narrow not found")
	}
	if len(found.embedding) != 2 {
		t.Errorf("buildTokenDocs: embedding not populated, got len %d", len(found.embedding))
	}
}

// TestEmbeddingScores verifies embeddingScores returns cosine scores for docs with stored embeddings.
func TestEmbeddingScores(t *testing.T) {
	// Two docs: one parallel to query vector, one orthogonal.
	docs := []tokenDoc{
		{id: "parallel", embedding: []float32{1, 0, 0}},
		{id: "orthogonal", embedding: []float32{0, 1, 0}},
	}
	query := []float32{1, 0, 0}
	scores := embeddingScores(docs, query)
	if scores["parallel"] <= 0 {
		t.Errorf("embeddingScores: parallel doc should have positive score, got %v", scores["parallel"])
	}
	if scores["orthogonal"] != 0 {
		t.Errorf("embeddingScores: orthogonal doc should have score 0, got %v", scores["orthogonal"])
	}
}

// TestTaskMetadataEmbeddingField verifies TaskMetadata has an Embedding field that round-trips via JSON.
func TestTaskMetadataEmbeddingField(t *testing.T) {
	m := TaskMetadata{Embedding: []float32{0.1, 0.2, 0.3}}
	if len(m.Embedding) != 3 {
		t.Errorf("TaskMetadata.Embedding: got len %d, want 3", len(m.Embedding))
	}
}

// TestCosineSimilarity verifies cosineSimilarity returns 1.0 for identical unit vectors.
func TestCosineSimilarity(t *testing.T) {
	v := []float32{1, 0, 0}
	got := cosineSimilarity(v, v)
	if math.Abs(float64(got)-1.0) > 1e-6 {
		t.Errorf("cosineSimilarity(v,v) = %v, want 1.0", got)
	}
	// orthogonal vectors → 0
	a := []float32{1, 0, 0}
	b := []float32{0, 1, 0}
	got2 := cosineSimilarity(a, b)
	if math.Abs(float64(got2)) > 1e-6 {
		t.Errorf("cosineSimilarity(orthogonal) = %v, want 0.0", got2)
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
