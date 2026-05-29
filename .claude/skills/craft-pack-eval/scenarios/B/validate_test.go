package b

import "testing"

func TestValidateInput_empty(t *testing.T) {
	err := validateInput("")
	if err == nil {
		t.Fatal("expected error for empty string, got nil")
	}
}

func TestValidateInput_valid(t *testing.T) {
	err := validateInput("hello")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}
