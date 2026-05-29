package f

import "testing"

func TestNormalize(t *testing.T) {
	got := normalize("Hello World")
	if got != "hello_world" {
		t.Fatalf("got %q, want %q", got, "hello_world")
	}
}
