package barcli

// BM25 ranking for token lookup (ADR-0232).
//
// Adapted from nn/internal/note/bm25.go.
// Documents are grammar tokens; title = token name + label (weighted 5×),
// body = definition + heuristics + distinctions.

import (
	"math"
	"strings"

	"github.com/kljensen/snowball/english"
)

const (
	bm25K1          = 1.5
	bm25B           = 0.75
	titleWeight     = 5
	hybridBM25Weight = 0.4
	hybridEmbWeight  = 0.6
)

// hybridScore combines a normalised BM25 score and a cosine similarity score
// into a single ranking signal: 0.4*bm25 + 0.6*cosine.
func hybridScore(bm25, cosine float64) float64 {
	return hybridBM25Weight*bm25 + hybridEmbWeight*cosine
}

// cosineSimilarity returns the dot product of two pre-normalised float32 vectors.
// Vectors are expected to be unit-length (as produced by sentence-transformers with
// normalize_embeddings=True), so dot product equals cosine similarity.
func cosineSimilarity(a, b []float32) float32 {
	if len(a) != len(b) {
		return 0
	}
	var sum float32
	for i := range a {
		sum += a[i] * b[i]
	}
	return sum
}

// tokenDoc is a BM25 document representing one grammar token.
type tokenDoc struct {
	id        string    // "axis:token"
	title     string    // name + " " + label
	body      string    // definition + heuristics + distinctions
	embedding []float32 // pre-normalised sentence embedding (nil when absent)
}

// buildTokenDocs constructs the BM25 corpus from all grammar tokens.
// If axisFilter is non-empty, only tokens on that axis are included.
func buildTokenDocs(g *Grammar, axisFilter string) []tokenDoc {
	var docs []tokenDoc

	add := func(axis, token, label, definition string, heuristics, distinctions []string, emb []float32) {
		if axisFilter != "" && axis != axisFilter {
			return
		}
		body := definition
		if len(heuristics) > 0 {
			body += " " + strings.Join(heuristics, " ")
		}
		if len(distinctions) > 0 {
			body += " " + strings.Join(distinctions, " ")
		}
		docs = append(docs, tokenDoc{
			id:        axis + ":" + token,
			title:     token + " " + label,
			body:      body,
			embedding: emb,
		})
	}

	if axisFilter == "" || axisFilter == "task" {
		for _, taskName := range g.GetAllTasks() {
			meta := g.Static.Metadata[taskName]
			dists := make([]string, 0, len(meta.Distinctions))
			for _, d := range meta.Distinctions {
				dists = append(dists, d.Token)
			}
			add("task", taskName, g.TaskLabel(taskName), g.TaskDescription(taskName), meta.Heuristics, dists, meta.Embedding)
		}
	}

	for axis, tokenMap := range g.Axes.Metadata {
		for tokenName, meta := range tokenMap {
			dists := make([]string, 0, len(meta.Distinctions))
			for _, d := range meta.Distinctions {
				dists = append(dists, d.Token)
			}
			add(axis, tokenName, g.AxisLabel(axis, tokenName), meta.Definition, meta.Heuristics, dists, meta.Embedding)
		}
	}

	for axis, tokenMap := range g.Persona.Metadata {
		for tokenName, meta := range tokenMap {
			slug := slugifyToken(tokenName)
			dists := make([]string, 0, len(meta.Distinctions))
			for _, d := range meta.Distinctions {
				dists = append(dists, d.Token)
			}
			add(axis, slug, g.PersonaLabel(axis, tokenName), meta.Definition, meta.Heuristics, dists, meta.Embedding)
		}
	}

	return docs
}

// embeddingScores computes cosine similarity between queryVec and each doc's stored
// embedding. Docs without an embedding or with score ≤ 0 are excluded from the result.
func embeddingScores(docs []tokenDoc, queryVec []float32) map[string]float64 {
	if len(queryVec) == 0 {
		return nil
	}
	scores := make(map[string]float64)
	for _, d := range docs {
		if len(d.embedding) != len(queryVec) {
			continue
		}
		if s := float64(cosineSimilarity(d.embedding, queryVec)); s > 0 {
			scores[d.id] = s
		}
	}
	return scores
}

// bm25Tokenize splits text into lowercase tokens (len > 1).
func bm25Tokenize(s string) []string {
	s = strings.ToLower(s)
	var tokens []string
	for _, word := range strings.FieldsFunc(s, func(r rune) bool {
		return !('a' <= r && r <= 'z') && !('0' <= r && r <= '9')
	}) {
		if len(word) > 1 {
			tokens = append(tokens, english.Stem(word, false))
		}
	}
	return tokens
}

// bm25Scores computes BM25 relevance scores for each tokenDoc against the query.
// Returns a map from doc ID to score; docs scoring 0 are excluded.
func bm25Scores(docs []tokenDoc, query string) map[string]float64 {
	terms := bm25Tokenize(query)
	if len(terms) == 0 {
		return nil
	}

	type docInfo struct {
		tf  map[string]int
		len int
	}
	infos := make([]docInfo, len(docs))
	totalLen := 0
	for i, d := range docs {
		tf := make(map[string]int)
		for _, t := range bm25Tokenize(d.title) {
			tf[t] += titleWeight
		}
		for _, t := range bm25Tokenize(d.body) {
			tf[t]++
		}
		dlen := len(bm25Tokenize(d.title))*titleWeight + len(bm25Tokenize(d.body))
		infos[i] = docInfo{tf: tf, len: dlen}
		totalLen += dlen
	}

	N := float64(len(docs))
	avgdl := float64(totalLen) / math.Max(N, 1)

	idf := make(map[string]float64, len(terms))
	for _, term := range terms {
		df := 0
		for _, info := range infos {
			if info.tf[term] > 0 {
				df++
			}
		}
		idf[term] = math.Log((N-float64(df)+0.5)/(float64(df)+0.5) + 1)
	}

	scores := make(map[string]float64)
	for i, d := range docs {
		info := infos[i]
		score := 0.0
		for _, term := range terms {
			tf := float64(info.tf[term])
			if tf == 0 {
				continue
			}
			dl := float64(info.len)
			score += idf[term] * (tf * (bm25K1 + 1)) /
				(tf + bm25K1*(1-bm25B+bm25B*dl/avgdl))
		}
		if score > 0 {
			scores[d.id] = score
		}
	}
	return scores
}
