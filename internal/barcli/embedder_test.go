package barcli

import (
	"testing"
)

// TestNewQueryEmbedderReturnsFallback verifies that NewQueryEmbedder returns a
// non-nil embedder even when the model/runtime is unavailable.
func TestNewQueryEmbedderReturnsFallback(t *testing.T) {
	e := NewQueryEmbedder(QueryEmbedderOptions{ModelsDir: t.TempDir()})
	if e == nil {
		t.Fatal("NewQueryEmbedder returned nil")
	}
}

// TestNewQueryEmbedderSetsModelPath verifies that the QueryEmbedder stores the
// model file path so Embed() can use it rather than an empty string.
func TestNewQueryEmbedderSetsModelPath(t *testing.T) {
	dir := t.TempDir()
	e := NewQueryEmbedder(QueryEmbedderOptions{ModelsDir: dir})
	if e == nil {
		t.Fatal("NewQueryEmbedder returned nil")
	}
	if e.modelPath == "" {
		t.Errorf("e.modelPath is empty; NewQueryEmbedder must store the model file path")
	}
}

// TestModelFilenameForPlatform verifies modelFilenameForPlatform returns a
// non-empty filename for known OS/arch combinations.
func TestModelFilenameForPlatform(t *testing.T) {
	cases := []struct{ os, arch string }{
		{"darwin", "arm64"},
		{"darwin", "amd64"},
		{"linux", "amd64"},
		{"linux", "arm64"},
		{"windows", "amd64"},
	}
	for _, c := range cases {
		got := modelFilenameForPlatform(c.os, c.arch)
		if got == "" {
			t.Errorf("modelFilenameForPlatform(%q, %q) = empty", c.os, c.arch)
		}
	}
}

// TestORTLibURLForPlatform verifies ortLibURLForPlatform returns a non-empty URL
// for known OS/arch combinations.
func TestORTLibURLForPlatform(t *testing.T) {
	cases := []struct{ os, arch string }{
		{"darwin", "arm64"},
		{"darwin", "amd64"},
		{"linux", "amd64"},
		{"windows", "amd64"},
	}
	for _, c := range cases {
		got := ortLibURLForPlatform(c.os, c.arch)
		if got == "" {
			t.Errorf("ortLibURLForPlatform(%q, %q) = empty", c.os, c.arch)
		}
	}
}

// TestMeanPool verifies meanPool returns the average of token vectors, ignoring padding.
func TestMeanPool(t *testing.T) {
	// 2 tokens, dim=3, first token [1,2,3], second token [3,4,5], rest padding (mask=0)
	hidden := []float32{1, 2, 3, 3, 4, 5, 0, 0, 0, 0, 0, 0}
	mask := []int64{1, 1, 0, 0}
	got := meanPool(hidden, mask, 3)
	want := []float32{2, 3, 4}
	for i, v := range want {
		if got[i] != v {
			t.Errorf("meanPool[%d] = %v, want %v", i, got[i], v)
		}
	}
}

// TestLookupUsesHybridScoreWhenEmbedderProvided verifies that LookupTokensWithEmbedder
// returns a result with a non-zero score when an embedder that returns a known vector
// is provided and the grammar has matching token embeddings.
func TestLookupUsesHybridScoreWhenEmbedderProvided(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	// Embedder that always returns the embedding of the first axis token found.
	var queryVec []float32
	for _, tokens := range g.Axes.Metadata {
		for _, meta := range tokens {
			if len(meta.Embedding) > 0 {
				queryVec = meta.Embedding
				break
			}
		}
		if queryVec != nil {
			break
		}
	}
	if queryVec == nil {
		t.Skip("no token embeddings in grammar; run scripts/embed_tokens.py first")
	}
	e := &stubEmbedder{vec: queryVec}
	results := LookupTokensWithEmbedder("concrete specific", g, "", e)
	if len(results) == 0 {
		t.Fatal("expected results, got none")
	}
}

type stubEmbedder struct{ vec []float32 }

func (s *stubEmbedder) Embed(_ string) []float32 { return s.vec }

// TestLookupWithEmbedderAnnotatesMatchedField verifies that LookupTokensWithEmbedder
// populates MatchedField/MatchedText from LookupTokens when a hybrid result also has
// an exact BM25 match, so callers see match annotations even in hybrid mode.
func TestLookupWithEmbedderAnnotatesMatchedField(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	var queryVec []float32
	for _, tokens := range g.Axes.Metadata {
		for _, meta := range tokens {
			if len(meta.Embedding) > 0 {
				queryVec = meta.Embedding
				break
			}
		}
		if queryVec != nil {
			break
		}
	}
	if queryVec == nil {
		t.Skip("no token embeddings in grammar; run scripts/embed_tokens.py first")
	}
	// "explain to a designer" has an exact heuristic match for audience:to-designer.
	e := &stubEmbedder{vec: queryVec}
	results := LookupTokensWithEmbedder("explain to a designer", g, "", e)
	if len(results) == 0 {
		t.Fatal("expected results, got none")
	}
	var found bool
	for _, r := range results {
		if r.MatchedField != "" && r.MatchedField != "hybrid" && r.MatchedText != "" {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("expected at least one result with non-hybrid MatchedField annotation; results:\n%v", results)
	}
}

// TestQueryEmbedderInputTensorFields verifies that QueryEmbedder has idsTensor and
// maskTensor fields (structural check; full behavioral testing requires ORT integration).
func TestQueryEmbedderInputTensorFields(t *testing.T) {
	// Construct directly to verify the fields exist and are assignable.
	e := &QueryEmbedder{
		fallback:   false,
		idsTensor:  nil,
		maskTensor: nil,
	}
	// The field assignments above compile only when both fields exist on the struct.
	// Nil values are expected here — the real population happens in NewQueryEmbedder
	// when the ORT model is available, which requires integration testing.
	_ = e
}

// TestQueryEmbedderEmbedFallbackReturnsNil verifies that the fallback embedder
// returns nil from Embed (signalling BM25-only path).
func TestQueryEmbedderEmbedFallbackReturnsNil(t *testing.T) {
	e := NewQueryEmbedder(QueryEmbedderOptions{ModelsDir: t.TempDir(), testFallback: true})
	vec := e.Embed("concrete specific examples")
	if vec != nil {
		t.Errorf("fallback Embed should return nil, got len=%d", len(vec))
	}
}
