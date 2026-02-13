package barcli

import (
	"strings"
	"testing"
)

// TestTUITokenCategoriesUseShortLabels specifies that BuildTokenCategories returns
// TokenOptions whose Label field is a short label (not the full long description)
// for axis, task, and persona tokens that have labels defined (ADR-0111 D4).
func TestTUITokenCategoriesUseShortLabels(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)

	findOption := func(categoryKey, slug string) (string, bool) {
		for _, cat := range categories {
			if cat.Key != categoryKey {
				continue
			}
			for _, opt := range cat.Options {
				if opt.Slug == slug {
					return opt.Label, true
				}
			}
		}
		return "", false
	}

	// Axis token: scope:act should have short label, not the full description.
	if label, ok := findOption("scope", "act"); !ok {
		t.Error("scope category must have an 'act' option (ADR-0111 D4)")
	} else if strings.Contains(label, "The response focuses on") {
		t.Errorf("scope:act tui label must be short label, not full description; got: %q", label)
	} else if label == "" {
		t.Error("scope:act tui label must be non-empty (ADR-0111 D4)")
	}

	// Task token: 'make' should have short label.
	if label, ok := findOption("task", "make"); !ok {
		t.Error("task category must have a 'make' option (ADR-0111 D4)")
	} else if strings.Contains(label, "The response creates new content") {
		t.Errorf("task:make tui label must be short label, not full description; got: %q", label)
	} else if label == "" {
		t.Error("task:make tui label must be non-empty (ADR-0111 D4)")
	}

	// Persona axis token: voice 'as-kent-beck' should have short label.
	if label, ok := findOption("voice", "as-kent-beck"); !ok {
		t.Error("voice category must have an 'as-kent-beck' option (ADR-0111 D4)")
	} else if strings.Contains(label, "The response channels") {
		t.Errorf("voice:as-kent-beck tui label must be short label, not full description; got: %q", label)
	} else if label == "" {
		t.Error("voice:as-kent-beck tui label must be non-empty (ADR-0111 D4)")
	}
}

func TestFormatSnapshotDiffLineMismatch(t *testing.T) {
	diff := formatSnapshotDiff("alpha\nbeta\n", "alpha\ngamma\n")
	if diff == "snapshots match" {
		t.Fatalf("expected mismatch, got %q", diff)
	}
	if want := "line 2"; len(diff) < len(want) || diff[:len(want)] != want {
		t.Fatalf("expected diff to start with %q, got %q", want, diff)
	}
}

func TestFormatSnapshotDiffLineCountMismatch(t *testing.T) {
	diff := formatSnapshotDiff("only one line", "only one line\nextra")
	if diff == "snapshots match" {
		t.Fatalf("expected mismatch, got %q", diff)
	}
	if want := "line count mismatch"; len(diff) < len(want) || diff[:len(want)] != want {
		t.Fatalf("expected diff to start with %q, got %q", want, diff)
	}
}
