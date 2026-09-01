package barcli

import (
	"math/rand"
)

// Lateral-seed lookup surfacing (bar lookup): the --seed-words build flag is
// exposed as a synthetic Kind="flag" lookup result so creative-intent queries
// discover it the same way they discover tokens and starter packs. These
// constants are the single source of truth shared by the lookup registration
// and the emitted result's Command.
const (
	lateralSeedFlagToken = "seed-words"
	// lateralSeedFlagCommand is illustrative — lookup does not know the caller's
	// build tokens, so it shows the flag appended to a placeholder build.
	lateralSeedFlagCommand = "bar build <tokens>... --seed-words 2"
	// lateralSeedFlagLabel is the one-line description shown with the result.
	lateralSeedFlagLabel = "inject N random concrete nouns as an oblique creative seed (opt-in --seed-words)"
)

// lateralSeedFlagHeuristics is the creative-intent vocabulary that makes the flag
// surface in `bar lookup`. Kept deliberately narrow so the flag appears only when
// the query signals divergent/creative thinking, not on analytical tasks.
var lateralSeedFlagHeuristics = []string{
	"brainstorm", "ideate", "creative", "lateral", "novel",
	"unstuck", "fresh angle", "divergent", "oblique",
}

// deriveLateralSeed returns n words sampled without replacement from words,
// selected deterministically from seed. The same (seed, n) always yields the
// same ordered result, so a build is reproducible via --seed. When n exceeds
// the list size the result is capped at the list size (no repeats). n<=0 or an
// empty source returns no words.
//
// Reproducibility (Ground P3) relies on math/rand seeded via rand.NewSource,
// matching the shuffle command's pattern.
func deriveLateralSeed(words []string, seed int64, n int) []string {
	if n <= 0 || len(words) == 0 {
		return nil
	}
	if n > len(words) {
		n = len(words)
	}

	rng := rand.New(rand.NewSource(seed))

	// Partial Fisher-Yates over a copy: shuffle the first n positions and take them.
	pool := make([]string, len(words))
	copy(pool, words)
	for i := 0; i < n; i++ {
		j := i + rng.Intn(len(pool)-i)
		pool[i], pool[j] = pool[j], pool[i]
	}
	return pool[:n]
}
