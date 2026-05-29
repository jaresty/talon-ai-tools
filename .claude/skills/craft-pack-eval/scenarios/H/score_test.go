package h

import "testing"

func TestScore(t *testing.T) {
	got := score([]int{3, 1, 4, 1, 5})
	if got != 14 {
		t.Fatalf("got %d, want 14", got)
	}
}
