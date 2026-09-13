package barcli

import "testing"

// mutateTestTokens is a representative active token set: one task token ("make")
// and several non-task axis tokens.
var mutateTestTokens = []string{"make", "full", "order", "bullets", "fig"}

// mutateIsTask treats "make" as the task token for these tests.
func mutateIsTask(tok string) bool { return tok == "make" }

// TestDeriveMutationLocusMembership verifies the chosen locus is one of the
// active tokens (Ground P3a).
func TestDeriveMutationLocusMembership(t *testing.T) {
	set := map[string]bool{}
	for _, tok := range mutateTestTokens {
		set[tok] = true
	}
	locus := deriveMutationLocus(mutateTestTokens, mutateIsTask, 42)
	if !set[locus] {
		t.Fatalf("locus %q is not an active token %v", locus, mutateTestTokens)
	}
}

// TestDeriveMutationLocusNeverTask verifies the task token is never selected
// (Ground P3b).
func TestDeriveMutationLocusNeverTask(t *testing.T) {
	for seed := int64(0); seed < 200; seed++ {
		locus := deriveMutationLocus(mutateTestTokens, mutateIsTask, seed)
		if mutateIsTask(locus) {
			t.Fatalf("seed %d selected the task token %q", seed, locus)
		}
	}
}

// TestDeriveMutationLocusDeterministic verifies the same (tokens, seed) yields
// the same locus (Ground P2a).
func TestDeriveMutationLocusDeterministic(t *testing.T) {
	a := deriveMutationLocus(mutateTestTokens, mutateIsTask, 42)
	b := deriveMutationLocus(mutateTestTokens, mutateIsTask, 42)
	if a != b {
		t.Fatalf("same seed produced different loci: %q vs %q", a, b)
	}
}

// TestDeriveMutationLocusDifferentSeeds verifies distinct seeds are not all
// collapsed to a single constant locus (guards a degenerate selector).
func TestDeriveMutationLocusDifferentSeeds(t *testing.T) {
	seen := map[string]bool{}
	for seed := int64(0); seed < 200; seed++ {
		seen[deriveMutationLocus(mutateTestTokens, mutateIsTask, seed)] = true
	}
	if len(seen) < 2 {
		t.Fatalf("expected varied loci across seeds, got only %v", seen)
	}
}

// TestDeriveMutationLocusNoNonTask verifies an empty result when the only token
// is the task token.
func TestDeriveMutationLocusNoNonTask(t *testing.T) {
	if locus := deriveMutationLocus([]string{"make"}, mutateIsTask, 1); locus != "" {
		t.Fatalf("expected empty locus when no non-task token exists, got %q", locus)
	}
}
