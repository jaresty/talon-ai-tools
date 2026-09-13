package barcli

import "math/rand"

// Mutation lookup surfacing (bar lookup): the --mutate build flag is exposed as
// a synthetic Kind="flag" lookup result so variation/selection intent queries
// discover it the same way they discover tokens, packs, and the lateral-seed
// flag. These constants are the single source of truth shared by the lookup
// registration and the emitted result's Command.
const (
	mutateFlagToken   = "mutate"
	mutateFlagCommand = "bar build <tokens>... --mutate"
	mutateFlagLabel   = "perturb one random active token's stance to generate a variant (opt-in --mutate)"
)

// mutateFlagHeuristics is the variation/selection vocabulary that makes the flag
// surface in `bar lookup`. Kept deliberately narrow so the flag appears only when
// the query signals wanting an intentional variation to compare, not on ordinary
// tasks.
var mutateFlagHeuristics = []string{
	"mutate", "variation", "variant", "perturb", "explore alternatives",
	"try a different angle", "natural selection", "mutate and select", "vary one token",
}

// flagLabelFor returns the lookup Label for a synthetic Kind="flag" result,
// keyed by the flag's token name. Defaults to the lateral-seed flag so existing
// callers that assume a single flag remain correct.
func flagLabelFor(token string) string {
	if token == mutateFlagToken {
		return mutateFlagLabel
	}
	return lateralSeedFlagLabel
}

// flagCommandFor returns the lookup Command for a synthetic Kind="flag" result,
// keyed by the flag's token name.
func flagCommandFor(token string) string {
	if token == mutateFlagToken {
		return mutateFlagCommand
	}
	return lateralSeedFlagCommand
}

// deriveMutationLocus selects one active non-task token to perturb ("mutate"),
// chosen deterministically from seed so a build is reproducible via --seed. The
// task token is never chosen. Returns "" when no non-task token is present.
//
// Reproducibility relies on math/rand seeded via rand.NewSource, matching the
// shuffle command and lateral-seed patterns.
func deriveMutationLocus(tokens []string, isTask func(string) bool, seed int64) string {
	candidates := make([]string, 0, len(tokens))
	for _, tok := range tokens {
		if tok == "" || isTask(tok) {
			continue
		}
		candidates = append(candidates, tok)
	}
	if len(candidates) == 0 {
		return ""
	}
	rng := rand.New(rand.NewSource(seed))
	return candidates[rng.Intn(len(candidates))]
}
