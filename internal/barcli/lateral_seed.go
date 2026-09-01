package barcli

import (
	"math/rand"
)

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
