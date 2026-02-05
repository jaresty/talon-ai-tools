package barcli

import (
	"sort"
	"strings"
)

// fuzzyMatch returns up to 3 candidate strings that are within maxDist edit distance
// from the input string, excluding exact matches. Results are sorted by:
// 1. Prefix matches first (case-insensitive)
// 2. Edit distance (lower is better)
// 3. Alphabetical order for ties
func fuzzyMatch(input string, candidates []string, maxDist int) []string {
	if input == "" || len(candidates) == 0 {
		return []string{}
	}

	inputLower := strings.ToLower(input)

	type match struct {
		candidate string
		distance  int
		isPrefix  bool
	}

	var matches []match

	for _, candidate := range candidates {
		candidateLower := strings.ToLower(candidate)

		// Skip exact matches
		if candidateLower == inputLower {
			continue
		}

		dist := levenshteinDistance(inputLower, candidateLower)
		if dist <= maxDist {
			isPrefix := strings.HasPrefix(candidateLower, inputLower)
			matches = append(matches, match{
				candidate: candidate,
				distance:  dist,
				isPrefix:  isPrefix,
			})
		}
	}

	// Sort by: prefix first, then distance, then alphabetically
	sort.Slice(matches, func(i, j int) bool {
		if matches[i].isPrefix != matches[j].isPrefix {
			return matches[i].isPrefix // prefix matches come first
		}
		if matches[i].distance != matches[j].distance {
			return matches[i].distance < matches[j].distance
		}
		return matches[i].candidate < matches[j].candidate
	})

	// Return up to 3 suggestions
	limit := 3
	if len(matches) < limit {
		limit = len(matches)
	}

	result := make([]string, limit)
	for i := 0; i < limit; i++ {
		result[i] = matches[i].candidate
	}

	return result
}

// levenshteinDistance calculates the Levenshtein edit distance between two strings
// using a space-optimized dynamic programming approach (O(min(m,n)) space).
func levenshteinDistance(s1, s2 string) int {
	if s1 == s2 {
		return 0
	}

	// Ensure s1 is the shorter string for space optimization
	if len(s1) > len(s2) {
		s1, s2 = s2, s1
	}

	m, n := len(s1), len(s2)

	// Handle empty string cases
	if m == 0 {
		return n
	}

	// Use single array that we update in place
	prev := make([]int, m+1)
	for i := 0; i <= m; i++ {
		prev[i] = i
	}

	for j := 1; j <= n; j++ {
		curr := j // First column value
		for i := 1; i <= m; i++ {
			cost := 1
			if s1[i-1] == s2[j-1] {
				cost = 0
			}

			// Calculate minimum of three operations:
			// - deletion: prev[i] + 1
			// - insertion: curr + 1
			// - substitution: prev[i-1] + cost
			next := min(prev[i]+1, min(curr+1, prev[i-1]+cost))

			prev[i-1] = curr
			curr = next
		}
		prev[m] = curr
	}

	return prev[m]
}
