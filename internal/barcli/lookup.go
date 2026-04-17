package barcli

import (
	"sort"
	"strings"
)

// LookupResult holds a single ranked match from LookupTokens (ADR-0163).
type LookupResult struct {
	Axis         string
	Token        string
	Label        string
	Tier         int     // 0–3 = tier match; -1 = BM25-only result (ADR-0232)
	Score        float64 // BM25 score; 0 for tier-matched results
	MatchedField string  // "token", "heuristics", "distinctions", "definition", or "bm25"
	MatchedText  string  // the specific phrase that matched
	Sequences    []SequenceMembership // ADR-0225: sequence memberships for this token
}

// validLookupAxes lists all axis names that can be used as --axis filters.
var validLookupAxes = map[string]bool{
	"task":        true,
	"completeness": true,
	"scope":       true,
	"method":      true,
	"form":        true,
	"channel":     true,
	"directional": true,
	"voice":       true,
	"audience":    true,
	"tone":        true,
	"intent":      true,
	"presets":     true,
}

// LookupTokens searches all grammar tokens for those matching query, with optional
// axis filter. Query words are AND-matched across all tiers (ADR-0163).
//
// Tiers (highest first):
//
//	3 — query word exactly equals the token name or a heuristic trigger word (case-insensitive)
//	2 — query word is a case-insensitive substring of the token name or a heuristic trigger word
//	1 — query word is a case-insensitive substring of a distinction token name
//	0 — query word is a case-insensitive substring of the definition text
//
// A token must match ALL words. The tier assigned is the highest tier achieved
// across all words for that token. Results are sorted by tier desc then
// axis:token asc, capped at 10.
func LookupTokens(query string, g *Grammar, axisFilter string) []LookupResult {
	words := strings.Fields(query)
	if len(words) == 0 {
		return nil
	}

	type candidate struct {
		axis         string
		token        string
		label        string
		tier         int
		matchedField string
		matchedText  string
	}

	var candidates []candidate

	tryToken := func(axis, token, label, definition string, heuristics []string, distinctions []string) {
		if axisFilter != "" && axis != axisFilter {
			return
		}
		// For each word, find the best tier. A token must satisfy ALL words.
		overallTier := 3 // start optimistic; reduce if needed
		overallField := ""
		overallText := ""
		for _, word := range words {
			wordLower := strings.ToLower(word)
			bestTier := -1
			bestField := ""
			bestText := ""
			// Tier 3: exact token name match or exact heuristic match
			if strings.ToLower(token) == wordLower {
				bestTier = 3
				bestField = "token"
				bestText = token
			}
			for _, h := range heuristics {
				if strings.ToLower(h) == wordLower {
					if bestTier < 3 {
						bestTier = 3
						bestField = "heuristics"
						bestText = h
					}
				}
			}
			// Tier 2: substring token name match or substring heuristic match
			if bestTier < 2 && strings.Contains(strings.ToLower(token), wordLower) {
				bestTier = 2
				bestField = "token"
				bestText = token
			}
			if bestTier < 2 {
				for _, h := range heuristics {
					if strings.Contains(strings.ToLower(h), wordLower) {
						bestTier = 2
						bestField = "heuristics"
						bestText = h
						break
					}
				}
			}
			// Tier 1: distinction token name substring
			if bestTier < 1 {
				for _, d := range distinctions {
					if strings.Contains(strings.ToLower(d), wordLower) {
						bestTier = 1
						bestField = "distinctions"
						bestText = d
						break
					}
				}
			}
			// Tier 0: definition substring
			if bestTier < 0 && strings.Contains(strings.ToLower(definition), wordLower) {
				bestTier = 0
				bestField = "definition"
				// extract a short surrounding context as matched_text
				defLower := strings.ToLower(definition)
				idx := strings.Index(defLower, wordLower)
				start := idx - 20
				if start < 0 {
					start = 0
				}
				end := idx + len(word) + 20
				if end > len(definition) {
					end = len(definition)
				}
				bestText = strings.TrimSpace(definition[start:end])
			}
			if bestTier < 0 {
				// This word has no match — token fails AND requirement
				return
			}
			// Track the lowest tier across words (limiting tier)
			if bestTier < overallTier {
				overallTier = bestTier
				overallField = bestField
				overallText = bestText
			} else if overallField == "" {
				overallField = bestField
				overallText = bestText
			}
		}
		candidates = append(candidates, candidate{
			axis:         axis,
			token:        token,
			label:        label,
			tier:         overallTier,
			matchedField: overallField,
			matchedText:  overallText,
		})
	}

	// Search task tokens
	if axisFilter == "" || axisFilter == "task" {
		for _, taskName := range g.GetAllTasks() {
			meta := g.Static.Metadata[taskName]
			dists := make([]string, 0, len(meta.Distinctions))
			for _, d := range meta.Distinctions {
				dists = append(dists, d.Token)
			}
			tryToken("task", taskName, g.TaskLabel(taskName), g.TaskDescription(taskName), meta.Heuristics, dists)
		}
	}

	// Search axis tokens
	for axis, tokenMap := range g.Axes.Metadata {
		for tokenName, meta := range tokenMap {
			dists := make([]string, 0, len(meta.Distinctions))
			for _, d := range meta.Distinctions {
				dists = append(dists, d.Token)
			}
			tryToken(axis, tokenName, g.AxisLabel(axis, tokenName), meta.Definition, meta.Heuristics, dists)
		}
	}

	// Search persona tokens (voice, audience, tone, intent, presets)
	for axis, tokenMap := range g.Persona.Metadata {
		for tokenName, meta := range tokenMap {
			slug := slugifyToken(tokenName)
			dists := make([]string, 0, len(meta.Distinctions))
			for _, d := range meta.Distinctions {
				dists = append(dists, d.Token)
			}
			tryToken(axis, slug, g.PersonaLabel(axis, tokenName), meta.Definition, meta.Heuristics, dists)
		}
	}

	// Deduplicate tier candidates: keep highest-tier match per axis:token
	type key struct{ axis, token string }
	best := make(map[key]candidate)
	for _, c := range candidates {
		k := key{c.axis, c.token}
		if existing, ok := best[k]; !ok || c.tier > existing.tier {
			best[k] = c
		}
	}

	deduped := make([]candidate, 0, len(best))
	for _, c := range best {
		deduped = append(deduped, c)
	}

	sort.Slice(deduped, func(i, j int) bool {
		if deduped[i].tier != deduped[j].tier {
			return deduped[i].tier > deduped[j].tier
		}
		ki := deduped[i].axis + ":" + deduped[i].token
		kj := deduped[j].axis + ":" + deduped[j].token
		return ki < kj
	})

	// BM25 pass: score all tokens, exclude those already in tier results (ADR-0232).
	tierKeys := make(map[key]bool, len(best))
	for k := range best {
		tierKeys[k] = true
	}
	docs := buildTokenDocs(g, axisFilter)
	scores := bm25Scores(docs, query)

	type bm25Candidate struct {
		id    string
		score float64
	}
	var bm25Results []bm25Candidate
	for _, doc := range docs {
		score, ok := scores[doc.id]
		if !ok {
			continue
		}
		// parse "axis:token" — split on first colon
		colonIdx := strings.Index(doc.id, ":")
		if colonIdx < 0 {
			continue
		}
		axis := doc.id[:colonIdx]
		token := doc.id[colonIdx+1:]
		if tierKeys[key{axis, token}] {
			continue // already in tier results, skip
		}
		bm25Results = append(bm25Results, bm25Candidate{id: doc.id, score: score})
	}
	sort.Slice(bm25Results, func(i, j int) bool {
		return bm25Results[i].score > bm25Results[j].score
	})

	// Build label map for BM25 results
	labelFor := make(map[string]string, len(docs))
	for _, doc := range docs {
		labelFor[doc.id] = doc.title
	}

	// Merge: tier results first, then BM25-only results, cap at 10
	const resultCap = 10
	var results []LookupResult
	for _, c := range deduped {
		if len(results) >= resultCap {
			break
		}
		results = append(results, LookupResult{
			Axis:         c.axis,
			Token:        c.token,
			Label:        c.label,
			Tier:         c.tier,
			MatchedField: c.matchedField,
			MatchedText:  c.matchedText,
			Sequences:    g.SequencesForToken(c.axis + ":" + c.token),
		})
	}
	for _, br := range bm25Results {
		if len(results) >= resultCap {
			break
		}
		colonIdx := strings.Index(br.id, ":")
		if colonIdx < 0 {
			continue
		}
		axis := br.id[:colonIdx]
		token := br.id[colonIdx+1:]
		results = append(results, LookupResult{
			Axis:         axis,
			Token:        token,
			Label:        g.AxisLabel(axis, token),
			Tier:         -1,
			Score:        br.score,
			MatchedField: "bm25",
			Sequences:    g.SequencesForToken(br.id),
		})
	}
	if len(results) == 0 {
		return nil
	}
	return results
}
