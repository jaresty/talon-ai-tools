package o

import "testing"

func TestDouble(t *testing.T) {
	got := double(3)
	if got != 6 {
		t.Fatalf("got %d, want 6", got)
	}
}
