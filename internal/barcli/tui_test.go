package barcli

import "testing"

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
