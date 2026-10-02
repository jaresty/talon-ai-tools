package barcli

import (
	"bytes"
	"os"
	"strings"
	"testing"
)

// TestHelpTokenNameAsTopicSuggestsTokenSubcommand specifies that supplying a token
// name directly after `help` names the exact correction rather than falling back to
// general usage (Ground P1).
func TestHelpTokenNameAsTopicSuggestsTokenSubcommand(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "witness", "full"}, os.Stdin, stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected non-zero exit for malformed help invocation")
	}
	got := stderr.String() + stdout.String()
	if !strings.Contains(got, "bar help token witness") {
		t.Fatalf("expected suggestion naming `bar help token witness`, got:\n%s", got)
	}
	if !strings.Contains(got, "bar help token full") {
		t.Fatalf("expected suggestion naming `bar help token full`, got:\n%s", got)
	}
}

// TestHelpCompositionSplitMembersSuggestsPlusForm specifies that composition members
// supplied as separate arguments produce the joined form rather than the full
// composition catalog (Ground P2).
func TestHelpCompositionSplitMembersSuggestsPlusForm(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "composition", "ground", "falsify"}, os.Stdin, stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected non-zero exit for malformed composition invocation")
	}
	got := stderr.String() + stdout.String()
	if !strings.Contains(got, "bar help composition ground+falsify") {
		t.Fatalf("expected suggestion naming `bar help composition ground+falsify`, got:\n%s", got)
	}
}

// TestHelpTokenBatchRendersEveryOperandInOrder specifies that batch token help
// renders each requested token, in argument order (Ground P3a, P3b).
func TestHelpTokenBatchRendersEveryOperandInOrder(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "token", "witness", "atomic"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, stderr.String())
	}
	out := stdout.String()
	wIdx := strings.Index(out, "# Token: witness")
	aIdx := strings.Index(out, "# Token: atomic")
	if wIdx < 0 {
		t.Fatalf("expected witness definition in batch output, got:\n%s", out)
	}
	if aIdx < 0 {
		t.Fatalf("expected atomic definition in batch output (surplus operand silently dropped), got:\n%s", out)
	}
	if wIdx > aIdx {
		t.Fatalf("expected argument order witness-then-atomic, got atomic first")
	}
}

// TestHelpTokenBatchReportsUnknownToken specifies that an unknown token in a batch
// is reported explicitly rather than skipped (Ground P3a).
func TestHelpTokenBatchReportsUnknownToken(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "token", "witness", "notatoken"}, os.Stdin, stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected non-zero exit when a batch operand is unknown")
	}
	if !strings.Contains(stderr.String(), "notatoken") {
		t.Fatalf("expected unknown token named in stderr, got:\n%s", stderr.String())
	}
}

// TestHelpCompositionSplitMembersUnknownPairFallsBackToCatalog specifies that the
// targeted suggestion fires only when the joined name is a real composition;
// otherwise the existing catalog behavior is preserved (Ground P4).
func TestHelpCompositionSplitMembersUnknownPairFallsBackToCatalog(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "composition", "witness", "atomic"}, os.Stdin, stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected non-zero exit for unknown composition")
	}
	got := stderr.String() + stdout.String()
	if strings.Contains(got, "bar help composition witness+atomic") {
		t.Fatalf("should not suggest a composition that does not exist, got:\n%s", got)
	}
	if !strings.Contains(got, "available:") {
		t.Fatalf("expected catalog fallback, got:\n%s", got)
	}
}

// TestHelpTokenBatchSkipAppliesPerSlug specifies that --skip is evaluated against each
// batched token independently: a token whose definition contains the phrase collapses to
// a confirmation line while the others still render in full (Ground P3a, P4).
func TestHelpTokenBatchSkipAppliesPerSlug(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "token", "witness", "atomic", "--skip", "inspectable reasoning"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, stderr.String())
	}
	out := stdout.String()
	if !strings.Contains(out, "# Token: witness (confirmed: \"inspectable reasoning\")") {
		t.Fatalf("expected witness to collapse to a confirmation line, got:\n%s", out)
	}
	if !strings.Contains(out, "**Kanji**: 粒") {
		t.Fatalf("expected atomic to render in full (phrase absent from its definition), got:\n%s", out)
	}
	if strings.Contains(out, "# Token: atomic (confirmed:") {
		t.Fatalf("atomic must not be confirmed by a phrase absent from its definition, got:\n%s", out)
	}
}

// TestHelpTokenBatchSkipConfirmsEveryMatchingSlug specifies that a phrase common to every
// batched token collapses each one, so a fully-known batch stays cheap (Ground P3a, P3b).
func TestHelpTokenBatchSkipConfirmsEveryMatchingSlug(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "token", "witness", "atomic", "--skip", "**Axis**"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, stderr.String())
	}
	out := stdout.String()
	for _, want := range []string{
		"# Token: witness (confirmed: \"**Axis**\")",
		"# Token: atomic (confirmed: \"**Axis**\")",
	} {
		if !strings.Contains(out, want) {
			t.Fatalf("expected %q in batch skip output, got:\n%s", want, out)
		}
	}
	wIdx := strings.Index(out, "# Token: witness")
	aIdx := strings.Index(out, "# Token: atomic")
	if wIdx > aIdx {
		t.Fatalf("expected confirmation lines in argument order, got atomic first")
	}
}

// TestHelpDocumentsTokenAndCompositionSyntax specifies that top-level help documents
// the singular token form and the composition `+` form, so the correct syntax is
// discoverable from the output a malformed call produces (Ground P1, P2).
func TestHelpDocumentsTokenAndCompositionSyntax(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	if exit := Run([]string{"help"}, os.Stdin, stdout, stderr); exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, stderr.String())
	}
	out := stdout.String()
	if !strings.Contains(out, "bar help token") {
		t.Fatalf("expected `bar help token` documented in top-level help, got:\n%s", out)
	}
	if !strings.Contains(out, "bar help composition") {
		t.Fatalf("expected `bar help composition` documented in top-level help, got:\n%s", out)
	}
}
