package barcli

import (
	"bytes"
	"os"
	"strings"
	"testing"
)

// runHelpToken runs `bar help token <args...>` and returns stdout, stderr and the exit code.
func runHelpToken(t *testing.T, args ...string) (string, string, int) {
	t.Helper()
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run(append([]string{"help", "token"}, args...), os.Stdin, stdout, stderr)
	return stdout.String(), stderr.String(), exit
}

const remainingPrefix = "Remaining (not loaded):"

func footerLines(out string) []string {
	var lines []string
	for _, line := range strings.Split(out, "\n") {
		if strings.HasPrefix(line, remainingPrefix) {
			lines = append(lines, line)
		}
	}
	return lines
}

func lastNonEmptyLine(out string) string {
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	return lines[len(lines)-1]
}

// TestHelpTokenBudgetPartialBatchFooter specifies that a batch whose blocks outgrow the
// default budget stops at a whole-block boundary, ends with exactly one footer line
// naming the unprinted tokens in order plus the exact rerun command, and exits 0
// (Ground properties 1, 3, 4, 5).
func TestHelpTokenBudgetPartialBatchFooter(t *testing.T) {
	out, errOut, exit := runHelpToken(t, "witness", "ground", "gate")
	if exit != 0 {
		t.Fatalf("expected exit 0 on a partial batch, got %d: %s", exit, errOut)
	}
	if !strings.Contains(out, "# Token: witness") {
		t.Fatalf("expected the first block to be emitted whole, got:\n%.300s", out)
	}
	if strings.Contains(out, "# Token: ground") || strings.Contains(out, "# Token: gate") {
		t.Fatalf("expected blocks past the budget to be withheld whole, got a later block")
	}
	footers := footerLines(out)
	if len(footers) != 1 {
		t.Fatalf("expected exactly one footer line, got %d", len(footers))
	}
	if lastNonEmptyLine(out) != footers[0] {
		t.Fatalf("expected the footer to be the last line, got last line %q", lastNonEmptyLine(out))
	}
	if !strings.Contains(footers[0], "ground, gate") {
		t.Fatalf("expected footer to list the unprinted tokens in order, got %q", footers[0])
	}
	if !strings.Contains(footers[0], "bar help token ground gate") {
		t.Fatalf("expected footer to carry the exact rerun command, got %q", footers[0])
	}
}

// TestHelpTokenBudgetOversizedFirstStillEmitted specifies that the first block is emitted
// even when it alone exceeds the budget (Ground properties 2, 3).
func TestHelpTokenBudgetOversizedFirstStillEmitted(t *testing.T) {
	out, errOut, exit := runHelpToken(t, "ground", "witness")
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, errOut)
	}
	if !strings.Contains(out, "# Token: ground") {
		t.Fatalf("expected the oversized first block to be emitted")
	}
	if strings.Contains(out, "# Token: witness") {
		t.Fatalf("expected the second block to be withheld once the budget is exceeded")
	}
	footers := footerLines(out)
	if len(footers) != 1 || !strings.Contains(footers[0], "bar help token witness") {
		t.Fatalf("expected one footer naming witness, got %v", footers)
	}
}

// TestHelpTokenBudgetNoFooterWhenAllFit specifies that a batch within budget emits every
// block in argument order and no footer (Ground properties 1, 4).
func TestHelpTokenBudgetNoFooterWhenAllFit(t *testing.T) {
	out, errOut, exit := runHelpToken(t, "witness", "full", "atomic")
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, errOut)
	}
	if len(footerLines(out)) != 0 {
		t.Fatalf("expected no footer when every block fits")
	}
	w, f, a := strings.Index(out, "# Token: witness"), strings.Index(out, "# Token: full"), strings.Index(out, "# Token: atomic")
	if w < 0 || f < 0 || a < 0 || !(w < f && f < a) {
		t.Fatalf("expected witness, full, atomic in argument order, got indexes %d %d %d", w, f, a)
	}
}

// TestHelpTokenBudgetStopsOnlyWhenNextWouldExceed specifies that emission continues while
// the next block still fits and stops once it would not (Ground property 3).
func TestHelpTokenBudgetStopsOnlyWhenNextWouldExceed(t *testing.T) {
	out, _, _ := runHelpToken(t, "falsify", "full")
	if !strings.Contains(out, "# Token: full") || len(footerLines(out)) != 0 {
		t.Fatalf("expected a second block that still fits to be emitted without a footer")
	}
	out, _, _ = runHelpToken(t, "falsify", "witness", "gate")
	if !strings.Contains(out, "# Token: falsify") {
		t.Fatalf("expected the first block to be emitted")
	}
	if strings.Contains(out, "# Token: witness") && strings.Contains(out, "# Token: gate") {
		t.Fatalf("expected emission to stop before the batch exceeds the default budget")
	}
	if len(footerLines(out)) != 1 {
		t.Fatalf("expected a footer for the withheld remainder")
	}
}

// TestHelpTokenMaxBytesFlagSetsBudget specifies that --max-bytes N replaces the default
// budget in both directions (Ground property 6).
func TestHelpTokenMaxBytesFlagSetsBudget(t *testing.T) {
	out, errOut, exit := runHelpToken(t, "witness", "full", "--max-bytes", "1")
	if exit != 0 {
		t.Fatalf("expected exit 0 with --max-bytes, got %d: %s", exit, errOut)
	}
	if !strings.Contains(out, "# Token: witness") || strings.Contains(out, "# Token: full") {
		t.Fatalf("expected a 1-byte budget to emit only the first block")
	}
	footers := footerLines(out)
	if len(footers) != 1 || !strings.Contains(footers[0], "bar help token full") {
		t.Fatalf("expected one footer naming full, got %v", footers)
	}

	out, errOut, exit = runHelpToken(t, "witness", "ground", "gate", "--max-bytes=1000000")
	if exit != 0 {
		t.Fatalf("expected exit 0 with --max-bytes=, got %d: %s", exit, errOut)
	}
	if !strings.Contains(out, "# Token: gate") || len(footerLines(out)) != 0 {
		t.Fatalf("expected a large budget to emit every block with no footer")
	}
}

// tokenLoadGateParagraph returns the opening paragraph of the TOKENS section, the gate
// text that governs how token blocks are loaded into the transcript.
func tokenLoadGateParagraph(t *testing.T) string {
	t.Helper()
	out := RenderPlainText(&BuildResult{
		Task: "Task:\n  Do it.",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "full", Description: "The response provides a thorough answer."},
		},
	})
	start := strings.Index(out, "Issue all `bar help token")
	if start < 0 {
		t.Fatalf("TOKENS gate paragraph not found in:\n%.400s", out)
	}
	rest := out[start:]
	if end := strings.Index(rest, "\n\n"); end >= 0 {
		rest = rest[:end]
	}
	return rest
}

func gateSentencesMentioning(t *testing.T, marker string) []string {
	t.Helper()
	var hits []string
	for _, s := range strings.Split(tokenLoadGateParagraph(t), ". ") {
		if strings.Contains(s, marker) {
			hits = append(hits, s)
		}
	}
	return hits
}

// TestTokenLoadGateAllowsMultiTokenForm specifies that the gate accepts the multi-token
// call alongside the joined form (Ground property 7).
func TestTokenLoadGateAllowsMultiTokenForm(t *testing.T) {
	g := tokenLoadGateParagraph(t)
	if !strings.Contains(g, "bar help token <slug> <slug>") {
		t.Fatalf("expected the gate to name the multi-token call shape, got:\n%s", g)
	}
	if !strings.Contains(g, "&&") {
		t.Fatalf("expected the joined form to remain accepted, got:\n%s", g)
	}
}

// TestTokenLoadGateTreatsFooterBatchAsCompleteForPrinted specifies that the gate says a
// batch ending in a remainder footer is complete for the tokens it printed (Ground property 8).
func TestTokenLoadGateTreatsFooterBatchAsCompleteForPrinted(t *testing.T) {
	for _, s := range gateSentencesMentioning(t, "Remaining (not loaded)") {
		if strings.Contains(s, "complete") {
			return
		}
	}
	t.Fatalf("expected a gate sentence naming the footer and calling the printed tokens complete")
}

// TestTokenLoadGateRequiresRepeatWithRemainder specifies that the gate says to repeat the
// call with the remaining list (Ground property 9).
func TestTokenLoadGateRequiresRepeatWithRemainder(t *testing.T) {
	for _, s := range gateSentencesMentioning(t, "Remaining (not loaded)") {
		if strings.Contains(s, "repeat") && strings.Contains(s, "remaining") {
			return
		}
	}
	t.Fatalf("expected a gate sentence naming the footer and requiring a repeat with the remaining list")
}
