package e

import "testing"

func TestAdd_removed(t *testing.T) {
	_ = Add
	t.Fatal("Add is present — should have been removed")
}

func TestAddInts(t *testing.T) {
	got := AddInts(2, 3)
	if got != 5 {
		t.Fatalf("got %d, want 5", got)
	}
}
