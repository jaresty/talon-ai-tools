package barcli

// BM25 ranking for token lookup (ADR-0232).
//
// Adapted from nn/internal/note/bm25.go.
// Documents are grammar tokens; title = token name + label (weighted 5×),
// body = definition + heuristics + distinctions.

import (
	"math"
	"strings"
)

const (
	bm25K1      = 1.5
	bm25B       = 0.75
	titleWeight = 5
)

// tokenDoc is a BM25 document representing one grammar token.
type tokenDoc struct {
	id    string // "axis:token"
	title string // name + " " + label
	body  string // definition + heuristics + distinctions
}

// buildTokenDocs constructs the BM25 corpus from all grammar tokens.
// If axisFilter is non-empty, only tokens on that axis are included.
func buildTokenDocs(g *Grammar, axisFilter string) []tokenDoc {
	var docs []tokenDoc

	add := func(axis, token, label, definition string, heuristics, distinctions []string) {
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
			id:    axis + ":" + token,
			title: token + " " + label,
			body:  body,
		})
	}

	if axisFilter == "" || axisFilter == "task" {
		for _, taskName := range g.GetAllTasks() {
			meta := g.Static.Metadata[taskName]
			dists := make([]string, 0, len(meta.Distinctions))
			for _, d := range meta.Distinctions {
				dists = append(dists, d.Token)
			}
			add("task", taskName, g.TaskLabel(taskName), g.TaskDescription(taskName), meta.Heuristics, dists)
		}
	}

	for axis, tokenMap := range g.Axes.Metadata {
		for tokenName, meta := range tokenMap {
			dists := make([]string, 0, len(meta.Distinctions))
			for _, d := range meta.Distinctions {
				dists = append(dists, d.Token)
			}
			add(axis, tokenName, g.AxisLabel(axis, tokenName), meta.Definition, meta.Heuristics, dists)
		}
	}

	for axis, tokenMap := range g.Persona.Metadata {
		for tokenName, meta := range tokenMap {
			slug := slugifyToken(tokenName)
			dists := make([]string, 0, len(meta.Distinctions))
			for _, d := range meta.Distinctions {
				dists = append(dists, d.Token)
			}
			add(axis, slug, g.PersonaLabel(axis, tokenName), meta.Definition, meta.Heuristics, dists)
		}
	}

	return docs
}

// bm25Tokenize splits text into lowercase tokens (len > 1).
func bm25Tokenize(s string) []string {
	s = strings.ToLower(s)
	var tokens []string
	for _, word := range strings.FieldsFunc(s, func(r rune) bool {
		return !('a' <= r && r <= 'z') && !('0' <= r && r <= '9')
	}) {
		if len(word) > 1 {
			tokens = append(tokens, word)
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
