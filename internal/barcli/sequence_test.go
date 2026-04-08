package barcli

// ADR-0225: Named Workflow Sequences — governing test artifact (gate).
// Each test covers exactly one observable behavior. All tests must fail
// before implementation begins (gate protocol). Tests are written against
// the embedded grammar and CLI app surface.

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/bartui2"
)

// Behavior 1: Grammar has a non-empty Sequences map after loading.
func TestGrammarLoadsSequences(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	if len(g.Sequences) == 0 {
		t.Fatal("expected grammar.Sequences to be non-empty, got empty map")
	}
}

// Behavior 2: Grammar contains the canonical "experiment-cycle" sequence.
func TestGrammarContainsExperimentCycleSequence(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["experiment-cycle"]
	if !ok {
		t.Fatal("expected grammar.Sequences[\"experiment-cycle\"] to exist")
	}
	if len(seq.Steps) < 2 {
		t.Fatalf("expected experiment-cycle to have ≥2 steps, got %d", len(seq.Steps))
	}
}

// Behavior 3: SequencesForToken returns membership for a sequence-member token.
func TestSequencesForTokenReturnsMembership(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	memberships := g.SequencesForToken("form:prep")
	if len(memberships) == 0 {
		t.Fatal("expected SequencesForToken(\"form:prep\") to return at least one membership")
	}
	var found bool
	for _, m := range memberships {
		if m.Name == "experiment-cycle" {
			found = true
			if m.StepIndex != 0 {
				t.Errorf("expected form:prep at step index 0 in experiment-cycle, got %d", m.StepIndex)
			}
			if m.NextStep == nil {
				t.Error("expected form:prep to have a NextStep (it is not the last step)")
			}
		}
	}
	if !found {
		t.Error("expected membership in \"experiment-cycle\" for form:prep")
	}
}

// Behavior 4: SequencesForToken returns nil/empty for a non-member token.
func TestSequencesForTokenReturnsEmptyForNonMember(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	memberships := g.SequencesForToken("scope:struct")
	if len(memberships) != 0 {
		t.Fatalf("expected no sequence membership for scope:struct, got %v", memberships)
	}
}

// Behavior 5: `bar sequence list` prints one line per sequence.
func TestSequenceListSubcommand(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "list"})
	if code != 0 {
		t.Fatalf("bar sequence list exited %d: %s", code, stderr)
	}
	lines := nonEmptyLines(out)
	if len(lines) == 0 {
		t.Fatal("expected at least one line from bar sequence list")
	}
	// Each line must contain the sequence key and a description fragment.
	var foundExperiment bool
	for _, l := range lines {
		if strings.HasPrefix(l, "experiment-cycle") {
			foundExperiment = true
		}
	}
	if !foundExperiment {
		t.Errorf("expected experiment-cycle in bar sequence list output:\n%s", out)
	}
}

// Behavior 6: `bar sequence show experiment-cycle` prints step details.
func TestSequenceShowSubcommand(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "form:prep") {
		t.Errorf("expected form:prep in bar sequence show output:\n%s", out)
	}
	if !strings.Contains(out, "form:vet") {
		t.Errorf("expected form:vet in bar sequence show output:\n%s", out)
	}
}

// Behavior 7: `bar lookup form:prep --json` result includes sequence membership.
func TestLookupResultIncludesSequenceMembership(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"lookup", "prep", "--json"})
	if code != 0 {
		t.Fatalf("bar lookup exited %d: %s", code, stderr)
	}
	var results []json.RawMessage
	if err := json.Unmarshal([]byte(out), &results); err != nil {
		t.Fatalf("expected JSON array from bar lookup --json: %v\noutput: %s", err, out)
	}
	// Find the form:prep result and check it has a sequences field.
	type seqMember struct {
		Name      string `json:"name"`
		StepIndex int    `json:"step_index"`
	}
	type result struct {
		Axis      string      `json:"axis"`
		Token     string      `json:"token"`
		Sequences []seqMember `json:"sequences"`
	}
	var found bool
	for _, raw := range results {
		var r result
		if err := json.Unmarshal(raw, &r); err != nil {
			continue
		}
		if r.Axis == "form" && r.Token == "prep" {
			found = true
			if len(r.Sequences) == 0 {
				t.Error("expected form:prep lookup result to include sequence membership")
			}
		}
	}
	if !found {
		t.Errorf("form:prep not found in bar lookup output:\n%s", out)
	}
}

// Behavior 8: HarnessToken.Sequences is populated for a sequence-member token
// when the TUI is built from real grammar (integration via BuildTokenCategories + NewHarness).
func TestHarnessTokenSequencesPopulated(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	cats := BuildTokenCategories(g)
	// Find the form category and the "prep" token within it.
	var prepSequences []bartui2.HarnessTokenSequence
	for _, cat := range cats {
		if cat.Key != "form" {
			continue
		}
		for _, opt := range cat.Options {
			if opt.Value == "prep" {
				prepSequences = opt.Sequences
			}
		}
	}
	if len(prepSequences) == 0 {
		t.Fatal("expected form:prep TokenOption to have Sequences populated, got empty")
	}
	var foundExperiment bool
	for _, s := range prepSequences {
		if s.Name == "experiment-cycle" && s.StepIndex == 0 {
			foundExperiment = true
		}
	}
	if !foundExperiment {
		t.Errorf("expected experiment-cycle step 0 in form:prep sequences, got %v", prepSequences)
	}
}

// --- ADR-0226: mode field + requires_user_input ---

// Behavior 9: Sequence.Mode is populated from grammar for experiment-cycle.
func TestSequenceModePopulated(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["experiment-cycle"]
	if !ok {
		t.Fatal("experiment-cycle not found")
	}
	if seq.Mode == "" {
		t.Fatal("expected Sequence.Mode to be non-empty for experiment-cycle, got empty")
	}
	if seq.Mode != "cycle" {
		t.Errorf("expected experiment-cycle Mode %q, got %q", "cycle", seq.Mode)
	}
}

// Behavior 10: SequenceStep.RequiresUserInput is populated for a step that declares it.
func TestSequenceStepRequiresUserInput(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["experiment-cycle"]
	if !ok {
		t.Fatal("experiment-cycle not found")
	}
	// form:prep step (index 0) requires user input — user must run the experiment before vet.
	if !seq.Steps[0].RequiresUserInput {
		t.Error("expected experiment-cycle step 0 (form:prep) RequiresUserInput=true")
	}
}

// Behavior 11: `bar sequence show experiment-cycle` human output includes a mode label.
func TestSequenceShowIncludesMode(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "mode:") {
		t.Errorf("expected \"mode:\" label in bar sequence show output:\n%s", out)
	}
}

// Behavior 12: `bar sequence show --json` includes mode field.
func TestSequenceShowJSONIncludesMode(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle", "--json"})
	if code != 0 {
		t.Fatalf("bar sequence show --json exited %d: %s", code, stderr)
	}
	type jsonSeq struct {
		Mode string `json:"mode"`
	}
	var result jsonSeq
	if err := json.Unmarshal([]byte(out), &result); err != nil {
		t.Fatalf("expected valid JSON from bar sequence show --json: %v\noutput: %s", err, out)
	}
	if result.Mode == "" {
		t.Errorf("expected mode field in bar sequence show --json output, got empty\noutput: %s", out)
	}
	if result.Mode != "cycle" {
		t.Errorf("expected mode %q, got %q", "cycle", result.Mode)
	}
}

// nonEmptyLines returns lines with whitespace-only lines removed.
func nonEmptyLines(s string) []string {
	var out []string
	for _, l := range strings.Split(s, "\n") {
		if strings.TrimSpace(l) != "" {
			out = append(out, l)
		}
	}
	return out
}

// Behavior 13: Sequence.Example is populated for a sequence that declares it.
func TestSequenceExamplePopulated(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["experiment-cycle"]
	if !ok {
		t.Fatal("experiment-cycle not found")
	}
	if seq.Example == "" {
		t.Error("expected experiment-cycle to have a non-empty Example field")
	}
}

// Behavior 14: `bar sequence show` human output includes example line.
func TestSequenceShowIncludesExample(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "example:") {
		t.Errorf("expected \"example:\" label in bar sequence show output:\n%s", out)
	}
}

// Behavior 15: `bar sequence show --json` includes example field.
func TestSequenceShowJSONIncludesExample(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle", "--json"})
	if code != 0 {
		t.Fatalf("bar sequence show --json exited %d: %s", code, stderr)
	}
	type jsonSeq struct {
		Example string `json:"example"`
	}
	var result jsonSeq
	if err := json.Unmarshal([]byte(out), &result); err != nil {
		t.Fatalf("expected valid JSON: %v\noutput: %s", err, out)
	}
	if result.Example == "" {
		t.Errorf("expected non-empty example field in bar sequence show --json output:\n%s", out)
	}
}

// Behavior 16: Grammar contains the "gather-and-synthesize" sequence.
func TestGrammarContainsGatherAndSynthesize(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	if _, ok := g.Sequences["gather-and-synthesize"]; !ok {
		t.Fatal("expected grammar.Sequences[\"gather-and-synthesize\"] to exist")
	}
}

// Behavior 17: Grammar contains the "plan-and-retrospect" sequence.
func TestGrammarContainsPlanAndRetrospect(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	if _, ok := g.Sequences["plan-and-retrospect"]; !ok {
		t.Fatal("expected grammar.Sequences[\"plan-and-retrospect\"] to exist")
	}
}

// Behavior 18: Grammar contains the "simulate-and-review" sequence.
func TestGrammarContainsSimulateAndReview(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	if _, ok := g.Sequences["simulate-and-review"]; !ok {
		t.Fatal("expected grammar.Sequences[\"simulate-and-review\"] to exist")
	}
}

// Behavior 19: `bar help sequences` exits 0 and contains sequence names.
func TestHelpSequencesExitsZero(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "sequences"})
	if code != 0 {
		t.Fatalf("bar help sequences exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "experiment-cycle") {
		t.Errorf("expected bar help sequences to include \"experiment-cycle\":\n%s", out)
	}
}

// Behavior 20: `bar help sequences` includes mode information.
func TestHelpSequencesIncludesMode(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "sequences"})
	if code != 0 {
		t.Fatalf("bar help sequences exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "cycle") || !strings.Contains(out, "linear") || !strings.Contains(out, "autonomous") {
		t.Errorf("expected bar help sequences to include all three modes:\n%s", out)
	}
}

// Behavior 21: `bar help llm` includes a Named Sequences section.
func TestHelpLLMIncludesSequencesSection(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "llm"})
	if code != 0 {
		t.Fatalf("bar help llm exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Named Sequences") {
		t.Errorf("expected bar help llm to include \"Named Sequences\" section:\n%s", out[:min(len(out), 500)])
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
