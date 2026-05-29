package c

import "testing"

func TestFormatDate(t *testing.T) {
	got := formatDate(2026, 5, 29)
	if got != "2026-05-29" {
		t.Fatalf("got %q, want %q", got, "2026-05-29")
	}
}

func TestFormatTime(t *testing.T) {
	got := formatTime(9, 5)
	if got != "09:05" {
		t.Fatalf("got %q, want %q", got, "09:05")
	}
}
