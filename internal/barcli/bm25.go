package barcli

// BM25 ranking for token lookup (ADR-0232).
//
// Adapted from nn/internal/note/bm25.go.
// Documents are grammar tokens; title = token name + label (weighted 5×),
// body = definition + heuristics + distinctions.

import (
	"math"
	"sort"
	"strings"

	"github.com/kljensen/snowball/english"
)

const (
	bm25K1      = 1.5
	bm25B       = 0.75
	titleWeight = 5
)

// tokenDoc is a BM25 document representing one grammar token.
type tokenDoc struct {
	id           string // "axis:token"
	title        string // name + " " + label
	body         string // definition + heuristics + distinctions + axis context (flat, for legacy callers)
	heuristics   string // heuristics text only
	distinctions string // distinctions text only
	definition   string // definition text only
}

// buildTokenDocs constructs the BM25 corpus from all grammar tokens.
// If axisFilter is non-empty, only tokens on that axis are included.
func buildTokenDocs(g *Grammar, axisFilter string) []tokenDoc {
	var docs []tokenDoc

	add := func(axis, token, label, definition string, heuristics, distinctions []string) {
		if axisFilter != "" && axis != axisFilter {
			return
		}
		heuristicsText := strings.Join(heuristics, " ")
		distinctionsText := strings.Join(distinctions, " ")
		body := definition
		if heuristicsText != "" {
			body += " " + heuristicsText
		}
		if distinctionsText != "" {
			body += " " + distinctionsText
		}
		if axisH := g.AxisLevelHeuristics(axis); len(axisH) > 0 {
			ah := strings.Join(axisH, " ")
			body += " " + ah
			heuristicsText += " " + ah
		}
		if axisDesc := g.AxisLevelDescription(axis); axisDesc != "" {
			body += " " + axisDesc
			heuristicsText += " " + axisDesc
		}
		if rc := g.AxisRoutingConcept(axis, token); rc != "" {
			body += " " + rc
			definition += " " + rc
		}
		docs = append(docs, tokenDoc{
			id:           axis + ":" + token,
			title:        token + " " + label,
			body:         body,
			heuristics:   strings.TrimSpace(heuristicsText),
			distinctions: strings.TrimSpace(distinctionsText),
			definition:   strings.TrimSpace(definition),
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

	if axisFilter == "" {
		for _, p := range g.StarterPacks {
			body := p.Framing + " " + p.Command
			if len(p.Heuristics) > 0 {
				body += " " + strings.Join(p.Heuristics, " ")
			}
			docs = append(docs, tokenDoc{
				id:    "pack:" + p.Name,
				title: p.Name,
				body:  body,
			})
		}
		for name, seq := range g.Sequences {
			body := seq.Description + " " + seq.Example
			if len(seq.Heuristics) > 0 {
				body += " " + strings.Join(seq.Heuristics, " ")
			}
			docs = append(docs, tokenDoc{
				id:    "sequence:" + name,
				title: name,
				body:  body,
			})
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
			tokens = append(tokens, english.Stem(word, false))
		}
	}
	return tokens
}

const rrfK = 60.0

// bm25ScoresRRF computes RRF-fused scores across four per-field corpora:
// title, heuristics, distinctions, definition. Each field is ranked independently
// by BM25; scores are fused as Σ 1/(k + rank_i(d)) with k=60.
// Returns a map from doc ID to RRF score; docs absent from all field rankings score 0 and are excluded.
func bm25ScoresRRF(docs []tokenDoc, query string) map[string]float64 {
	type fieldCorpus struct {
		docs []tokenDoc
	}
	corpora := []fieldCorpus{
		{docs: make([]tokenDoc, len(docs))}, // title
		{docs: make([]tokenDoc, len(docs))}, // heuristics
		{docs: make([]tokenDoc, len(docs))}, // distinctions
		{docs: make([]tokenDoc, len(docs))}, // definition
	}
	for i, d := range docs {
		corpora[0].docs[i] = tokenDoc{id: d.id, title: d.title}
		corpora[1].docs[i] = tokenDoc{id: d.id, title: d.heuristics}
		corpora[2].docs[i] = tokenDoc{id: d.id, title: d.distinctions}
		corpora[3].docs[i] = tokenDoc{id: d.id, title: d.definition}
	}

	rrf := make(map[string]float64)
	for _, corpus := range corpora {
		scores := bm25Scores(corpus.docs, query)
		if len(scores) == 0 {
			continue
		}
		type kv struct {
			id    string
			score float64
		}
		ranked := make([]kv, 0, len(scores))
		for id, s := range scores {
			ranked = append(ranked, kv{id, s})
		}
		sort.Slice(ranked, func(i, j int) bool { return ranked[i].score > ranked[j].score })
		for rank, entry := range ranked {
			rrf[entry.id] += 1.0 / (rrfK + float64(rank+1))
		}
	}
	return rrf
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
