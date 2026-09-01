package barcli

import (
	"reflect"
	"testing"
)

var testSeedWords = []string{"lighthouse", "anchor", "kettle", "lantern", "compass", "harbor"}

// TestDeriveLateralSeedCount verifies exactly N words are returned (Ground P2b).
func TestDeriveLateralSeedCount(t *testing.T) {
	got := deriveLateralSeed(testSeedWords, 42, 3)
	if len(got) != 3 {
		t.Fatalf("expected 3 words, got %d (%v)", len(got), got)
	}
}

// TestDeriveLateralSeedDeterministic verifies same (seed, n) yields the same
// ordered selection (Ground P3).
func TestDeriveLateralSeedDeterministic(t *testing.T) {
	a := deriveLateralSeed(testSeedWords, 42, 3)
	b := deriveLateralSeed(testSeedWords, 42, 3)
	if !reflect.DeepEqual(a, b) {
		t.Fatalf("same seed produced different selections: %v vs %v", a, b)
	}
}

// TestDeriveLateralSeedDifferentSeeds verifies different seeds generally differ
// (guards against a degenerate constant selector).
func TestDeriveLateralSeedDifferentSeeds(t *testing.T) {
	a := deriveLateralSeed(testSeedWords, 1, 3)
	b := deriveLateralSeed(testSeedWords, 999, 3)
	if reflect.DeepEqual(a, b) {
		t.Fatalf("distinct seeds produced identical selections: %v", a)
	}
}

// TestDeriveLateralSeedMembership verifies every returned word is drawn from the
// source list (Ground P4).
func TestDeriveLateralSeedMembership(t *testing.T) {
	set := map[string]bool{}
	for _, w := range testSeedWords {
		set[w] = true
	}
	for _, w := range deriveLateralSeed(testSeedWords, 7, 4) {
		if !set[w] {
			t.Fatalf("returned word %q is not in the source list", w)
		}
	}
}

// TestDeriveLateralSeedNoRepeatWithinDraw verifies a single draw does not repeat
// a word when N <= list size (sample without replacement).
func TestDeriveLateralSeedNoRepeatWithinDraw(t *testing.T) {
	got := deriveLateralSeed(testSeedWords, 3, len(testSeedWords))
	seen := map[string]bool{}
	for _, w := range got {
		if seen[w] {
			t.Fatalf("word %q repeated within a single draw: %v", w, got)
		}
		seen[w] = true
	}
}

// TestDeriveLateralSeedCappedAtListSize verifies N greater than the list size
// returns at most the list size rather than repeating.
func TestDeriveLateralSeedCappedAtListSize(t *testing.T) {
	got := deriveLateralSeed(testSeedWords, 5, len(testSeedWords)+10)
	if len(got) != len(testSeedWords) {
		t.Fatalf("expected cap at %d, got %d", len(testSeedWords), len(got))
	}
}

// TestDeriveLateralSeedZeroOrEmpty verifies edge cases return no words.
func TestDeriveLateralSeedZeroOrEmpty(t *testing.T) {
	if got := deriveLateralSeed(testSeedWords, 1, 0); len(got) != 0 {
		t.Fatalf("n=0 should return no words, got %v", got)
	}
	if got := deriveLateralSeed(nil, 1, 3); len(got) != 0 {
		t.Fatalf("empty source should return no words, got %v", got)
	}
}
