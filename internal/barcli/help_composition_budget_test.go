package barcli

import (
	"bytes"
	"os"
	"strings"
	"testing"
)

// runHelpComposition runs `bar help composition <args...>` and returns stdout, stderr and the exit code.
func runHelpComposition(args ...string) (string, string, int) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run(append([]string{"help", "composition"}, args...), os.Stdin, stdout, stderr)
	return stdout.String(), stderr.String(), exit
}

// compositionHeaders returns the composition names, in output order, of every block
// that starts with a "# Composition: <name>" line.
func compositionHeaders(out string) []string {
	var names []string
	for _, line := range strings.Split(out, "\n") {
		if rest, ok := strings.CutPrefix(line, "# Composition: "); ok {
			if i := strings.Index(rest, " ("); i >= 0 {
				rest = rest[:i]
			}
			names = append(names, rest)
		}
	}
	return names
}

// footerRemainder returns the names listed after the footer prefix.
func footerRemainder(footer string) []string {
	rest := strings.TrimPrefix(footer, remainingPrefix)
	if i := strings.Index(rest, ";"); i >= 0 {
		rest = rest[:i]
	}
	var names []string
	for _, n := range strings.Split(rest, ",") {
		if n = strings.TrimSpace(n); n != "" {
			names = append(names, n)
		}
	}
	return names
}

// bigCompositionBatch totals more than the largest default budget the contract allows,
// so a footer is required under every budget in range.
var bigCompositionBatch = []string{
	"ground+falsify", "gate+atomic", "depends+atomic", "falsify+atomic",
	"prism+shoshin", "chain+shoshin", "paradox+fix",
}

// TestHelpCompositionBudgetPartialBatchFooter specifies that a batch outgrowing the
// default budget prints a whole-block prefix in argument order, then one closing
// footer naming exactly the unprinted names and the rerun command, and exits 0
// (Ground properties 1, 3, 4, 5, 6).
func TestHelpCompositionBudgetPartialBatchFooter(t *testing.T) {
	out, errOut, exit := runHelpComposition(bigCompositionBatch...)
	if exit != 0 {
		t.Fatalf("expected exit 0 on a partial batch, got %d: %.200s", exit, errOut)
	}
	printed := compositionHeaders(out)
	if len(printed) < 2 {
		t.Fatalf("expected at least two whole blocks under the default budget, got headers %v", printed)
	}
	for i, n := range printed {
		if bigCompositionBatch[i] != n {
			t.Fatalf("expected printed blocks to be a prefix in argument order, got %v", printed)
		}
	}
	footers := footerLines(out)
	if len(footers) != 1 || lastNonEmptyLine(out) != footers[0] {
		t.Fatalf("expected exactly one footer as the last line, got %v", footers)
	}
	rest := footerRemainder(footers[0])
	if strings.Join(append(append([]string{}, printed...), rest...), " ") != strings.Join(bigCompositionBatch, " ") {
		t.Fatalf("expected printed + remaining to equal the operands, got %v + %v", printed, rest)
	}
	if !strings.Contains(footers[0], "bar help composition "+strings.Join(rest, " ")) {
		t.Fatalf("expected the exact rerun command in the footer, got %q", footers[0])
	}
}

// TestHelpCompositionBudgetFirstBlockAlwaysEmitted specifies that the first block is
// emitted even when it alone exceeds the budget (Ground properties 2, 3, 6).
func TestHelpCompositionBudgetFirstBlockAlwaysEmitted(t *testing.T) {
	out, errOut, exit := runHelpComposition("falsify+atomic", "gate+atomic", "--max-bytes", "1")
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %.200s", exit, errOut)
	}
	if got := compositionHeaders(out); len(got) != 1 || got[0] != "falsify+atomic" {
		t.Fatalf("expected only the first block under a 1-byte budget, got %v", got)
	}
	footers := footerLines(out)
	if len(footers) != 1 || !strings.Contains(footers[0], "bar help composition gate+atomic") {
		t.Fatalf("expected one footer naming gate+atomic, got %v", footers)
	}
}

// TestHelpCompositionBudgetNoFooterWhenAllFit specifies that a batch within budget
// prints every block in order with no footer (Ground properties 1, 4, 6).
func TestHelpCompositionBudgetNoFooterWhenAllFit(t *testing.T) {
	want := []string{"falsify+atomic", "prism+shoshin", "chain+shoshin"}
	out, errOut, exit := runHelpComposition(want...)
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %.200s", exit, errOut)
	}
	if got := compositionHeaders(out); strings.Join(got, " ") != strings.Join(want, " ") {
		t.Fatalf("expected every block in argument order, got %v", got)
	}
	if len(footerLines(out)) != 0 {
		t.Fatalf("expected no footer when every block fits")
	}
	out, _, _ = runHelpComposition(append(append([]string{}, bigCompositionBatch...), "--max-bytes=1000000")...)
	if got := compositionHeaders(out); len(got) != len(bigCompositionBatch) || len(footerLines(out)) != 0 {
		t.Fatalf("expected a large --max-bytes to print every block with no footer, got %v", got)
	}
}

// TestHelpCompositionUnknownOperandReported specifies that an unknown name is named on
// stderr and the exit is non-zero (Ground property 7).
func TestHelpCompositionUnknownOperandReported(t *testing.T) {
	_, errOut, exit := runHelpComposition("falsify+atomic", "notacomposition", "prism+shoshin")
	if exit == 0 {
		t.Fatalf("expected a non-zero exit when an operand is unknown")
	}
	if !strings.Contains(errOut, "notacomposition") {
		t.Fatalf("expected the unknown name on stderr, got %.200s", errOut)
	}
}

// TestHelpCompositionSkipAppliesPerOperand specifies that --skip is evaluated against
// each operand: the matching one collapses, the other renders in full (Ground property 8).
func TestHelpCompositionSkipAppliesPerOperand(t *testing.T) {
	phrase := "when the assertions or their perturbations are not yet established"
	out, errOut, exit := runHelpComposition("falsify+atomic", "gate+atomic", "--skip", phrase)
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %.200s", exit, errOut)
	}
	if !strings.Contains(out, "# Composition: falsify+atomic (confirmed: ") {
		t.Fatalf("expected falsify+atomic to collapse to a confirmation line")
	}
	if !strings.Contains(out, "# Composition: gate+atomic\n") || strings.Contains(out, "# Composition: gate+atomic (confirmed:") {
		t.Fatalf("expected gate+atomic to render in full, got:\n%.300s", out)
	}

	// The matching operand is not always the first one.
	out, _, _ = runHelpComposition("gate+atomic", "falsify+atomic", "--skip", phrase)
	if !strings.Contains(out, "# Composition: falsify+atomic (confirmed: ") {
		t.Fatalf("expected a later matching operand to collapse to a confirmation line, got:\n%.300s", out)
	}
}

// compositionGateParagraph returns the opening paragraph of the COMPOSITION RULES
// section, the gate text that governs how composition rules are loaded.
func compositionGateParagraph(t *testing.T) string {
	t.Helper()
	out := RenderPlainText(&BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
		ActiveCompositions: []Composition{{Name: "ground+falsify", Prose: "ground+falsify prose"}},
	})
	start := strings.Index(out, "Issue all `bar help composition")
	if start < 0 {
		t.Fatalf("composition gate paragraph not found in:\n%.400s", out)
	}
	rest := out[start:]
	if end := strings.Index(rest, "\n\n"); end >= 0 {
		rest = rest[:end]
	}
	return rest
}

// TestCompositionGateAllowsMultiNameForm specifies that the gate names the multi-name
// call shape and keeps the batch directive (Ground property 9).
func TestCompositionGateAllowsMultiNameForm(t *testing.T) {
	g := compositionGateParagraph(t)
	if !strings.Contains(g, "bar help composition <slug> <slug>") {
		t.Fatalf("expected the gate to name the multi-name call shape, got:\n%s", g)
	}
	if !strings.Contains(g, "batch") {
		t.Fatalf("expected the batch directive to remain, got:\n%s", g)
	}
}

// TestCompositionGateFooterSentences specifies that the gate calls a batch ending in a
// footer complete for the printed names, and requires a repeat with the remaining list
// (Ground properties 10, 11).
func TestCompositionGateFooterSentences(t *testing.T) {
	var complete, repeat bool
	for _, s := range strings.Split(compositionGateParagraph(t), ". ") {
		if !strings.Contains(s, "Remaining (not loaded)") {
			continue
		}
		complete = complete || strings.Contains(s, "complete")
		repeat = repeat || (strings.Contains(s, "repeat") && strings.Contains(s, "remaining"))
	}
	if !complete {
		t.Errorf("expected a gate sentence naming the footer and calling the printed names complete")
	}
	if !repeat {
		t.Errorf("expected a gate sentence naming the footer and requiring a repeat with the remaining list")
	}
}
