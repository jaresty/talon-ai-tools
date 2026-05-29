package e

import (
	"bytes"
	"os"
	"testing"
)

func TestAdd_removed(t *testing.T) {
	content, err := os.ReadFile("calc.go")
	if err != nil {
		t.Fatalf("could not read calc.go: %v", err)
	}
	if bytes.Contains(content, []byte("func Add(")) {
		t.Fatal("Add is present — should have been removed")
	}
}

func TestAddInts(t *testing.T) {
	got := AddInts(2, 3)
	if got != 5 {
		t.Fatalf("got %d, want 5", got)
	}
}
