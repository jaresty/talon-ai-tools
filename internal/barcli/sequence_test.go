package barcli

// ADR-0225: Named Workflow Sequences — governing test artifact (gate).
// Each test covers exactly one observable behavior. All tests must fail
// before implementation begins (gate protocol). Tests are written against
// the embedded grammar and CLI app surface.

import (
	"encoding/json"
	"os"
	"path/filepath"
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
	// action step (index 1) requires user input — user must run the experiment before vet.
	if len(seq.Steps) < 2 {
		t.Fatal("expected experiment-cycle to have at least 2 steps")
	}
	if !seq.Steps[1].RequiresUserInput {
		t.Error("expected experiment-cycle step 1 (action) RequiresUserInput=true")
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
	out, stderr, code := runCLI(t, []string{"help", "llm", "--section", "sequences"})
	if code != 0 {
		t.Fatalf("bar help llm --section sequences exited %d: %s", code, stderr)
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

// Behavior 24: Sequence.StopWhen is populated for a cycle-mode sequence.
func TestSequenceStopWhenPopulated(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["experiment-cycle"]
	if !ok {
		t.Fatal("experiment-cycle not found")
	}
	if seq.StopWhen == "" {
		t.Fatal("expected experiment-cycle StopWhen to be non-empty for a cycle-mode sequence")
	}
}

// Behavior 25: `bar sequence show experiment-cycle` human output includes stop_when label.
func TestSequenceShowIncludesStopWhen(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "stop_when:") {
		t.Errorf("expected \"stop_when:\" label in bar sequence show output:\n%s", out)
	}
}

// Behavior 26: `bar sequence show experiment-cycle --json` includes stop_when field.
func TestSequenceShowJSONIncludesStopWhen(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle", "--json"})
	if code != 0 {
		t.Fatalf("bar sequence show --json exited %d: %s", code, stderr)
	}
	type jsonSeq struct {
		StopWhen string `json:"stop_when"`
	}
	var result jsonSeq
	if err := json.Unmarshal([]byte(out), &result); err != nil {
		t.Fatalf("expected valid JSON: %v\noutput: %s", err, out)
	}
	if result.StopWhen == "" {
		t.Errorf("expected non-empty stop_when field in bar sequence show --json output:\n%s", out)
	}
}

// Behavior 22: `bar help llm --section sequences` includes a dispatch steps note separate from execution modes.
func TestHelpLLMSequencesIncludesDispatchNote(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "llm", "--section", "sequences"})
	if code != 0 {
		t.Fatalf("bar help llm --section sequences exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Dispatch steps") {
		t.Errorf("expected bar help llm --section sequences to include a \"Dispatch steps\" note:\n%s", out)
	}
	if strings.Contains(out, "autonomous` (all steps run cold) | `linear` (pause for user input) | `cycle` (repeat until user ends) | `dispatch`") {
		t.Errorf("dispatch must not appear as a sequence execution mode in the modes line:\n%s", out)
	}
}

// Behavior 23: `bar sequence show` renders the dispatch execution protocol inline for dispatch steps.
func TestSequenceShowDispatchProtocolInline(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "parallel-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show parallel-eval exited %d: %s", code, stderr)
	}
	checks := []string{
		"[dispatch protocol — required]",
		"1. The orchestrator spawns Agent tool calls only",
		"2. fan_out: enumerate",
		"3. isolation: true",
		"4. Spawn one Agent tool call per item using subagent_type: bar-agent",
		"5. Each agent receives the step token string",
		"6. join: all",
		"7. Pass the join result as --subject to the next step.",
	}
	for _, want := range checks {
		if !strings.Contains(out, want) {
			t.Errorf("bar sequence show parallel-eval missing dispatch protocol line %q:\n%s", want, out)
		}
	}
}

// Behavior 25: SequenceStep struct carries Inner field with mode, stop_when, and steps.
func TestSequenceStepInnerFieldPopulated(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["frame-debug"]
	if !ok {
		t.Fatal("frame-debug sequence not found in grammar")
	}
	var dispatchStep *SequenceStep
	for i := range seq.Steps {
		if seq.Steps[i].Type == "dispatch" {
			dispatchStep = &seq.Steps[i]
			break
		}
	}
	if dispatchStep == nil {
		t.Fatal("no dispatch step found in frame-debug")
	}
	if dispatchStep.Inner == nil {
		t.Fatal("dispatch step Inner field is nil — expected a populated inner sequence")
	}
	if dispatchStep.Inner.Mode == "" {
		t.Error("dispatch step Inner.Mode is empty")
	}
	if dispatchStep.Inner.StopWhen == "" {
		t.Error("dispatch step Inner.StopWhen is empty")
	}
	if len(dispatchStep.Inner.Steps) == 0 {
		t.Error("dispatch step Inner.Steps is empty")
	}
}

// Behavior 26: `bar sequence show` renders inner mode, stop_when, and nested steps indented.
func TestSequenceShowRendersInnerSequence(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	checks := []string{
		"inner mode:",
		"inner stop_when:",
		"→ form:prep",
		"→ form:vet",
	}
	for _, want := range checks {
		if !strings.Contains(out, want) {
			t.Errorf("bar sequence show frame-debug missing inner rendering %q:\n%s", want, out)
		}
	}
}

// Behavior 27: `bar sequence show --json` includes inner in JSON output.
func TestSequenceShowJSONIncludesInner(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug", "--json"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug --json exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, `"inner"`) {
		t.Errorf("bar sequence show frame-debug --json missing \"inner\" field:\n%s", out)
	}
}

// Behavior 28: `bar help llm --section sequences` documents the inner schema.
func TestHelpLLMSequencesDocumentsInnerSchema(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "llm", "--section", "sequences"})
	if code != 0 {
		t.Fatalf("bar help llm --section sequences exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "inner") {
		t.Errorf("bar help llm --section sequences does not document inner schema:\n%s", out)
	}
}

// Behavior 29: frame-debug dispatch step uses inner with mode, stop_when, and prep/vet steps.
func TestFrameDebugDispatchUsesInner(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	checks := []string{"inner mode: cycle", "inner stop_when:", "→ form:prep", "→ form:vet"}
	for _, want := range checks {
		if !strings.Contains(out, want) {
			t.Errorf("frame-debug dispatch step missing inner field %q:\n%s", want, out)
		}
	}
}

// Behavior 30: frame-explore dispatch step uses inner with mode, stop_when, and prep/vet steps.
func TestFrameExploreDispatchUsesInner(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	checks := []string{"inner mode: cycle", "inner stop_when:", "→ form:prep", "→ form:vet"}
	for _, want := range checks {
		if !strings.Contains(out, want) {
			t.Errorf("frame-explore dispatch step missing inner field %q:\n%s", want, out)
		}
	}
}

// Behavior 24: `bar help llm --section sequences` step summary for parallel-eval shows dispatch fan-out/join.
func TestHelpLLMSequencesDispatchStepShowsFanOut(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "llm", "--section", "sequences"})
	if code != 0 {
		t.Fatalf("bar help llm --section sequences exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "dispatch[enumerate→all]") {
		t.Errorf("expected parallel-eval step summary to contain \"dispatch[enumerate→all]\":\n%s", out)
	}
}

// Behavior 31: renderer prints action protocol block for action steps.
func TestSequenceShowRendersActionStep(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle"})
	if code != 0 {
		t.Fatalf("bar sequence show experiment-cycle exited %d: %s", code, stderr)
	}
	checks := []string{
		"[action protocol — required]",
		"Do NOT run bar build for this step.",
		"Execute the actions",
	}
	for _, want := range checks {
		if !strings.Contains(out, want) {
			t.Errorf("bar sequence show experiment-cycle missing action rendering %q:\n%s", want, out)
		}
	}
}

// Behavior 32: renderer warns when step token has no task: prefix.
func TestSequenceShowWarnsNoTaskToken(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle"})
	if code != 0 {
		t.Fatalf("bar sequence show experiment-cycle exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "[no task token") {
		t.Errorf("bar sequence show experiment-cycle missing no-task-token warning:\n%s", out)
	}
}

// Behavior 33: validate_sequences accepts action steps without token field.
func TestSequenceValidatorAcceptsActionStep(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["experiment-cycle"]
	if !ok {
		t.Fatal("experiment-cycle sequence not found")
	}
	var hasAction bool
	for _, s := range seq.Steps {
		if s.Type == "action" {
			hasAction = true
		}
	}
	if !hasAction {
		t.Fatal("experiment-cycle has no action step — expected one after migration")
	}
}

// Behavior 34: bar help llm --section sequences documents action step type.
func TestHelpLLMSequencesDocumentsActionStep(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "llm", "--section", "sequences"})
	if code != 0 {
		t.Fatalf("bar help llm --section sequences exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Action steps") {
		t.Errorf("bar help llm --section sequences missing Action steps documentation:\n%s", out)
	}
}

// Behavior 35: frame-debug inner steps are prep→action→vet.
func TestFrameDebugInnerHasActionStep(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "[action protocol — required]") {
		t.Errorf("frame-debug inner sequence missing action step:\n%s", out)
	}
}

// Behavior 36: frame-explore inner steps are prep→action→vet.
func TestFrameExploreInnerHasActionStep(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "[action protocol — required]") {
		t.Errorf("frame-explore inner sequence missing action step:\n%s", out)
	}
}

// Behavior 37: experiment-cycle action step has requires_user_input true.
func TestExperimentCycleActionStepRequiresUserInput(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["experiment-cycle"]
	if !ok {
		t.Fatal("experiment-cycle sequence not found")
	}
	for _, s := range seq.Steps {
		if s.Type == "action" && !s.RequiresUserInput {
			t.Error("experiment-cycle action step must have requires_user_input: true")
		}
	}
}

// Behavior 38: renderer does NOT warn when step token contains a bare task slug (no false positive).
func TestSequenceShowNoFalsePositiveTaskWarning(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-work"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-work exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "[no task token") {
		t.Errorf("bar sequence show frame-work emitted false-positive 'no task token' warning:\n%s", out)
	}
}

// Behavior 39: frame-debug step 1 role is "frame enumeration" (not hypothesis enumeration).
func TestFrameDebugStep1RoleIsFrameEnumeration(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["frame-debug"]
	if !ok {
		t.Fatal("frame-debug sequence not found")
	}
	if len(seq.Steps) == 0 {
		t.Fatal("frame-debug has no steps")
	}
	step0 := seq.Steps[0]
	if !strings.Contains(step0.Role, "frame") {
		t.Errorf("frame-debug step 1 role must contain 'frame', got: %q", step0.Role)
	}
	if strings.Contains(step0.Role, "hypothesis") {
		t.Errorf("frame-debug step 1 role must not mention 'hypothesis', got: %q", step0.Role)
	}
}

// Behavior 40: frame-debug dispatch role says "frame investigation" not "fix attempts".
func TestFrameDebugDispatchRoleIsFrameInvestigation(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["frame-debug"]
	if !ok {
		t.Fatal("frame-debug sequence not found")
	}
	var dispatchStep *SequenceStep
	for i := range seq.Steps {
		if seq.Steps[i].Type == "dispatch" {
			dispatchStep = &seq.Steps[i]
			break
		}
	}
	if dispatchStep == nil {
		t.Fatal("frame-debug has no dispatch step")
	}
	if strings.Contains(dispatchStep.Role, "fix attempts") {
		t.Errorf("frame-debug dispatch role must not say 'fix attempts', got: %q", dispatchStep.Role)
	}
	if !strings.Contains(dispatchStep.Role, "frame") {
		t.Errorf("frame-debug dispatch role must contain 'frame', got: %q", dispatchStep.Role)
	}
}

// Behavior 41: frame-debug inner prep prompt_hint mentions "frame" and "hypothesis".
func TestFrameDebugInnerPrepMentionsFrameAndHypothesis(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["frame-debug"]
	if !ok {
		t.Fatal("frame-debug sequence not found")
	}
	var dispatchStep *SequenceStep
	for i := range seq.Steps {
		if seq.Steps[i].Type == "dispatch" {
			dispatchStep = &seq.Steps[i]
			break
		}
	}
	if dispatchStep == nil || dispatchStep.Inner == nil {
		t.Fatal("frame-debug dispatch step missing inner sequence")
	}
	var prepStep *SequenceStep
	for i := range dispatchStep.Inner.Steps {
		if dispatchStep.Inner.Steps[i].Token == "form:prep" {
			prepStep = &dispatchStep.Inner.Steps[i]
			break
		}
	}
	if prepStep == nil {
		t.Fatal("frame-debug inner has no form:prep step")
	}
	if !strings.Contains(prepStep.PromptHint, "frame") {
		t.Errorf("frame-debug inner prep prompt_hint must mention 'frame', got: %q", prepStep.PromptHint)
	}
	if !strings.Contains(prepStep.PromptHint, "hypothesis") {
		t.Errorf("frame-debug inner prep prompt_hint must mention 'hypothesis', got: %q", prepStep.PromptHint)
	}
}

// Behavior 42: dispatch protocol point 4 tells spawning agents they need Bash and bar skills.
func TestSequenceShowDispatchMentionsBarSkills(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "parallel-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show parallel-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "subagent_type: bar-agent") {
		t.Errorf("dispatch protocol point 4 must mention 'subagent_type: bar-agent':\n%s", out)
	}
}

// Behavior 43: dispatch protocol clause 1 is allow-list (names what orchestrator does, not what it must not do).
func TestSequenceShowDispatchClause1IsAllowList(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "parallel-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show parallel-eval exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "Do NOT run bar build for this step") {
		t.Errorf("dispatch protocol clause 1 must not be a deny-list; found deny-list form:\n%s", out)
	}
	if !strings.Contains(out, "spawns Agent tool calls only") {
		t.Errorf("dispatch protocol clause 1 must contain 'spawns Agent tool calls only':\n%s", out)
	}
}

// Behavior 44: dispatch protocol includes explicit bar command instruction for spawned agents.
func TestSequenceShowDispatchAgentBarCommand(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "parallel-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show parallel-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Each agent receives the step token string") {
		t.Errorf("dispatch protocol must contain 'Each agent receives the step token string' instruction:\n%s", out)
	}
}

// Behavior 45: dispatch protocol point 5 names the bar build command form with step token string.
func TestSequenceShowDispatchPoint5TraceabilityClause(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "parallel-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show parallel-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "bar build <step-token-string>") {
		t.Errorf("dispatch protocol point 5 must name 'bar build <step-token-string>' command form:\n%s", out)
	}
}

// Behavior 52: frame-work inner scope claim prompt_hint instructs writing ground derivation to store.
func TestFrameWorkScopeClaimWritesDerivation(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["frame-work"]
	if !ok {
		t.Fatal("frame-work sequence not found")
	}
	var dispatchStep *SequenceStep
	for i := range seq.Steps {
		if seq.Steps[i].Type == "dispatch" {
			dispatchStep = &seq.Steps[i]
			break
		}
	}
	if dispatchStep == nil || dispatchStep.Inner == nil {
		t.Fatal("frame-work dispatch step missing inner sequence")
	}
	var actionStep *SequenceStep
	for i := range dispatchStep.Inner.Steps {
		if dispatchStep.Inner.Steps[i].Type == "action" && dispatchStep.Inner.Steps[i].Role == "scope claim" {
			actionStep = &dispatchStep.Inner.Steps[i]
			break
		}
	}
	if actionStep == nil {
		t.Fatal("frame-work inner has no 'scope claim' action step")
	}
	if !strings.Contains(actionStep.PromptHint, "write your ground derivation") {
		t.Errorf("frame-work scope claim prompt_hint must say 'write your ground derivation', got: %q", actionStep.PromptHint)
	}
}

// Behavior 53: frame-work adversarial step prompt_hint instructs reading derivations from store.
func TestFrameWorkAdversarialReadsDerivations(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	seq, ok := g.Sequences["frame-work"]
	if !ok {
		t.Fatal("frame-work sequence not found")
	}
	var adversarialStep *SequenceStep
	for i := range seq.Steps {
		if strings.Contains(seq.Steps[i].Token, "adversarial") {
			adversarialStep = &seq.Steps[i]
			break
		}
	}
	if adversarialStep == nil {
		t.Fatal("frame-work has no adversarial step")
	}
	if !strings.Contains(adversarialStep.PromptHint, "read derivations") {
		t.Errorf("frame-work adversarial step prompt_hint must say 'read derivations', got: %q", adversarialStep.PromptHint)
	}
}

// Behavior 77: dispatch protocol point 4 contains subagent_type: bar-agent (applies to all dispatch steps).
func TestDispatchProtocolPoint4ContainsBarAgent(t *testing.T) {
	// Use frame-debug (inner) and parallel-eval (non-inner) — both must have it in point 4.
	for _, seq := range []string{"frame-debug", "parallel-eval"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		// Point 4 line must contain subagent_type: bar-agent.
		var point4Line string
		for _, line := range strings.Split(out, "\n") {
			if strings.Contains(line, "4.") && strings.Contains(line, "Spawn") {
				point4Line = line
				break
			}
		}
		if point4Line == "" {
			t.Errorf("%s: could not find point 4 (Spawn) line in output", seq)
			continue
		}
		if !strings.Contains(point4Line, "subagent_type: bar-agent") {
			t.Errorf("%s: point 4 must contain 'subagent_type: bar-agent', got: %s", seq, point4Line)
		}
	}
}

// Behavior 75: frame-debug inner dispatch point 5 requires subagent_type: bar-agent.
func TestFrameDebugInnerDispatchUsesBarAgent(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "subagent_type: bar-agent") {
		t.Errorf("frame-debug inner dispatch point 5 must require 'subagent_type: bar-agent':\n%s", out)
	}
}

// Behavior 76: frame-debug inner dispatch point 5 requires orchestrator to preserve all Derivation blocks.
func TestFrameDebugInnerDispatchPreservesDerivationBlocks(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "preserve all Derivation blocks") {
		t.Errorf("frame-debug inner dispatch point 5 must require orchestrator to 'preserve all Derivation blocks':\n%s", out)
	}
}

// Behavior 68: frame-debug step 1 names observable frame name criteria (no verb, no causal claim).
func TestFrameDebugStep1NamesObservableFrameNameCriteria(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "no verb") && !strings.Contains(out, "no causal claim") {
		t.Errorf("frame-debug step 1 must name observable frame name criteria ('no verb' or 'no causal claim'):\n%s", out)
	}
}

// Behavior 69: frame-debug dispatch prompt_hint names literal bar build form:prep per cycle.
func TestFrameDebugDispatchPromptHintNamesBarBuildCommands(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "bar build form:prep") {
		t.Errorf("frame-debug dispatch prompt_hint must name literal 'bar build form:prep' command:\n%s", out)
	}
}

// Behavior 70: frame-debug dispatch point 3 names observable Agent call contents.
func TestFrameDebugDispatchPoint3NamesAgentCallContents(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "must not contain") && !strings.Contains(out, "must include only") {
		t.Errorf("frame-debug dispatch point 3 must name Agent call contents ('must not contain' or 'must include only'):\n%s", out)
	}
}

// Behavior 71: frame-debug dispatch point 5 (inner) requires subagent_type: bar-agent (bar-agent has bar-workflow pre-loaded).
func TestFrameDebugDispatchPoint5RequiresBarWorkflowSkill(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "subagent_type: bar-agent") {
		t.Errorf("frame-debug dispatch point 5 must require 'subagent_type: bar-agent' (bar-agent has bar-workflow pre-loaded):\n%s", out)
	}
}

// Behavior 72: frame-debug action step names Bash tool call result as observable completion criterion.
func TestFrameDebugActionStepNamesBashToolCallResult(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Bash tool call") {
		t.Errorf("frame-debug action step must name 'Bash tool call' as observable completion criterion:\n%s", out)
	}
}

// Behavior 73: frame-debug vet step names new bar build form:prep following rejection as observable.
func TestFrameDebugVetStepNamesNewPrepAfterRejection(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "new bar build form:prep") {
		t.Errorf("frame-debug vet step must name 'new bar build form:prep' as the observable following rejection:\n%s", out)
	}
}

// Behavior 74: frame-explore action step requires Bash tool call result (live behavior, not code reads).
func TestFrameExploreActionStepRequiresBashToolCall(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Bash tool call") {
		t.Errorf("frame-explore action step must name 'Bash tool call' as observable (live behavior, not code reads):\n%s", out)
	}
}

// Behavior 67: frame-synthesis dispatch prompt_hint explicitly instructs agents to read the material first.
func TestFrameSynthesisDispatchInstructsReadFirst(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-synthesis"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-synthesis exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "First, read") && !strings.Contains(out, "first, read") && !strings.Contains(out, "Read the files") && !strings.Contains(out, "read the files") {
		t.Errorf("frame-synthesis dispatch prompt_hint must explicitly instruct agents to read the files/material before running bar build:\n%s", out)
	}
}

// Behavior 64: sequence list contains frame-synthesis.
func TestSequenceListContainsFrameSynthesis(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "list"})
	if code != 0 {
		t.Fatalf("bar sequence list exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "frame-synthesis") {
		t.Errorf("sequence list must contain 'frame-synthesis':\n%s", out)
	}
}

// Behavior 65: frame-synthesis dispatch step has no inner steps (no experiment cycle).
func TestFrameSynthesisDispatchHasNoInnerSteps(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-synthesis"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-synthesis exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "inner mode") {
		t.Errorf("frame-synthesis dispatch step must have no inner sequence — no experiment cycle:\n%s", out)
	}
}

// Behavior 66: frame-synthesis dispatch prompt_hint directs agents to run bar build.
func TestFrameSynthesisDispatchMentionsBarBuild(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-synthesis"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-synthesis exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "bar build") {
		t.Errorf("frame-synthesis dispatch step must mention 'bar build' for agents to run:\n%s", out)
	}
}

// Behavior 62: frame-debug step 1 defines frames as domains containing multiple hypotheses, not as hypotheses themselves.
func TestFrameDebugStep1DefinesFrameAsMultipleHypotheses(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "multiple hypotheses") {
		t.Errorf("frame-debug step 1 must define a frame as an investigation domain containing multiple hypotheses:\n%s", out)
	}
}

// Behavior 63: frame-debug vet step says 'next hypothesis' on rejection, not just 'stop'.
func TestFrameDebugVetStepContinuesToNextHypothesis(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "next hypothesis") {
		t.Errorf("frame-debug vet step must direct agent to 'next hypothesis' on rejection — not just 'stop':\n%s", out)
	}
}

// Behavior 58: frame-debug inner cycle action step does not list 'code reads' as a valid method.
func TestFrameDebugActionStepNoCodeReads(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "code reads") {
		t.Errorf("frame-debug action step must not list 'code reads' as a valid method — experimentation requires running commands that produce new output:\n%s", out)
	}
}

// Behavior 59: frame-explore inner cycle action step does not list 'code reads' or 'document review'.
func TestFrameExploreActionStepNoStaticAnalysis(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "code reads") {
		t.Errorf("frame-explore action step must not list 'code reads':\n%s", out)
	}
	if strings.Contains(out, "document review") {
		t.Errorf("frame-explore action step must not list 'document review' — experimentation requires running commands that produce new output:\n%s", out)
	}
}

// Behavior 60: frame-debug prep step requires naming what command or test will produce evidence.
func TestFrameDebugPrepRequiresRunnableExperiment(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "runnable") && !strings.Contains(out, "command or test") && !strings.Contains(out, "what to run") {
		t.Errorf("frame-debug prep step must require naming a runnable experiment (command or test), not just a code path to inspect:\n%s", out)
	}
}

// Behavior 61: frame-explore prep step requires naming a runnable experiment.
func TestFrameExplorePrepRequiresRunnableExperiment(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "runnable") && !strings.Contains(out, "command or test") && !strings.Contains(out, "what to run") {
		t.Errorf("frame-explore prep step must require naming a runnable experiment (command or test), not just a hypothesis:\n%s", out)
	}
}

// Behavior 56: dispatch protocol point 5 tells orchestrator to construct and include a literal bar build command.
func TestDispatchProtocolLiteralBarCommand(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "parallel-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show parallel-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "bar build <step-token-string>") {
		t.Errorf("dispatch protocol point 5 must include literal command template 'bar build <step-token-string>':\n%s", out)
	}
}

// Behavior 57: bar-agent.md when-dispatched section says to run the literal command and not discover tokens.
func TestBarAgentNoDiscovery(t *testing.T) {
	dir := t.TempDir()
	_, _, code := runCLI(t, []string{"install-agents", "--location", dir})
	if code != 0 {
		t.Fatalf("bar install-agents failed")
	}
	content, err := os.ReadFile(filepath.Join(dir, "bar-agent.md"))
	if err != nil {
		t.Fatalf("could not read bar-agent.md: %v", err)
	}
	s := string(content)
	if !strings.Contains(s, "Run the literal") {
		t.Errorf("bar-agent.md when-dispatched section must say 'Run the literal':\n%s", s)
	}
	if !strings.Contains(s, "Do not run") && !strings.Contains(s, "do not run") {
		t.Errorf("bar-agent.md when-dispatched section must say 'do not run' (bar help llm):\n%s", s)
	}
}

// Behavior 55: dispatch protocol point 5 requires agents to return a Derivation block and orchestrator to preserve all.
func TestDispatchProtocolPreservesDerivationBlocks(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "parallel-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show parallel-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "## Derivation") {
		t.Errorf("dispatch protocol point 5 must require agents to return a '## Derivation' block:\n%s", out)
	}
	if !strings.Contains(out, "preserve all Derivation blocks") {
		t.Errorf("dispatch protocol point 5 must require orchestrator to 'preserve all Derivation blocks':\n%s", out)
	}
}

// Behavior 79: inner action protocol block explicitly requires Bash tool calls (not just "tools").
func TestInnerActionProtocolRequiresBash(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "Execute actions from prior step using tools.") {
		t.Errorf("inner action protocol must not say 'using tools' — must require live Bash execution:\n%s", out)
	}
	if !strings.Contains(out, "output from the running subject") {
		t.Errorf("inner action protocol must require 'output from the running subject':\n%s", out)
	}
}

// Behavior 80: inner dispatch point 5 prohibits token discovery — agents must run only the bar build commands shown.
func TestInnerDispatchPoint5NoTokenDiscovery(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "do not run bar help llm") {
		t.Errorf("inner dispatch point 5 must say 'do not run bar help llm':\n%s", out)
	}
}

// Behavior 78: non-inner dispatch point 5 tells agents to run bar build with the step token string directly.
func TestDispatchPoint5TokenString(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "parallel-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show parallel-eval exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "The orchestrator must construct and include this exact command") {
		t.Errorf("dispatch protocol point 5 must not contain orchestrator-constructs-literal-command prescription:\n%s", out)
	}
	if !strings.Contains(out, "Each agent receives the step token string") {
		t.Errorf("dispatch protocol point 5 must say 'Each agent receives the step token string':\n%s", out)
	}
}
