package d

import "testing"

func TestParseToken_renamed(t *testing.T) {
	got := parseToken("hello")
	if got != "hello" {
		t.Fatalf("got %q, want %q", got, "hello")
	}
}

func TestRoute(t *testing.T) {
	got := route("world")
	if got != "world" {
		t.Fatalf("got %q, want %q", got, "world")
	}
}

func TestHandle(t *testing.T) {
	got := handle("foo")
	if got != "foo" {
		t.Fatalf("got %q, want %q", got, "foo")
	}
}
