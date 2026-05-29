package a

import "testing"

func TestParseToken(t *testing.T) {
	got := parseToken("foo:bar")
	if got != "bar" {
		t.Fatalf("got %q, want %q", got, "bar")
	}
}
