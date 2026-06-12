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
	memberships := g.SequencesForToken("make form:prep")
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
	if !strings.Contains(out, "make form:prep") {
		t.Errorf("expected form:prep in bar sequence show output:\n%s", out)
	}
	if !strings.Contains(out, "check form:vet") {
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
// Behavior: the dispatch protocol requires a pre-dispatch bar build agent step that produces
// a ## Agent Configuration block passed inline to each Agent call prompt.
// Behavior: dispatch protocol (from bar help dispatch) requires a ## Agent Configuration block.
// The sequences section now points to bar help dispatch for the live protocol.
func TestHelpLLMDispatchProtocolRequiresAgentConfigBlock(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "dispatch"})
	if code != 0 {
		t.Fatalf("bar help dispatch exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "## Agent Configuration") {
		t.Errorf("expected dispatch protocol to require a '## Agent Configuration' block:\n%s", out)
	}
	if !strings.Contains(out, "bar build") {
		t.Errorf("expected dispatch protocol to reference bar build:\n%s", out)
	}
}

// Behavior: dispatch protocol (from bar help dispatch) includes a concrete ## Agent Configuration example
// showing task-context framing (not persona/goal, which come from agent's own bar invocations).
func TestHelpLLMDispatchProtocolAgentConfigBlockHasExample(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "dispatch"})
	if code != 0 {
		t.Fatalf("bar help dispatch exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "## Agent Configuration") {
		t.Errorf("expected dispatch protocol to include ## Agent Configuration example:\n%s", out)
	}
	if !strings.Contains(out, "agent's own bar build invocations") {
		t.Errorf("expected dispatch protocol to clarify persona/approach come from agent's bar build:\n%s", out)
	}
}

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
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
	}
	checks := []string{
		"[dispatch protocol — required]",
		"1. The orchestrator spawns Agent tool calls only",
		"2. fan_out: enumerate",
		"3. isolation: true",
		"4. [DISPATCH GATE]",
		"5. Each agent receives the step token string",
		"6. join: all",
		"7. Before running bar build for the next step: reproduce each ## Derivation block",
	}
	for _, want := range checks {
		if !strings.Contains(out, want) {
			t.Errorf("bar sequence show frame-eval missing dispatch protocol line %q:\n%s", want, out)
		}
	}
}

// Dim-0a: dispatch protocol 0a must prohibit channel tokens (agent/skill) in bar build command.
func TestSequenceShowDispatch0aNoChannelToken(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "no channel token") {
		t.Errorf("dispatch 0a must state 'no channel token' to prevent channel:agent/skill capture:\n%s", out)
	}
}

// Dim-0b: dispatch protocol 0b gate must discriminate on ## Agent Configuration, not === TASK ===.
func TestSequenceShowDispatch0bGatesOnAgentConfigBlock(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "`=== TASK 任務 (DO THIS) ===`") {
		t.Errorf("dispatch 0b must not use '=== TASK 任務 (DO THIS) ===' as gate discriminator — it appears with all bar builds:\n%s", out)
	}
	if !strings.Contains(out, "## Agent Configuration") {
		t.Errorf("dispatch 0b gate must reference '## Agent Configuration' as discriminator:\n%s", out)
	}
}

// Dim-0c: dispatch protocol 0c must state allow-list (what block may contain) and
// must not require persona/approach/goal (those come from agent's own bar invocations).
func TestSequenceShowDispatch0cNamesThreeLabeledFields(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "agent's own bar build invocations") {
		t.Errorf("dispatch 0c must state that persona/approach/goal come from agent's own bar build invocations:\n%s", out)
	}
	if !strings.Contains(out, "assigned item") {
		t.Errorf("dispatch 0c must name 'assigned item' as permitted content:\n%s", out)
	}
}

// Dim-4: dispatch protocol step 4 must require Agent call count equals item count.
func TestSequenceShowDispatch4RequiresCountEquality(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "number of Agent tool calls") {
		t.Errorf("dispatch step 4 must state count-equality requirement ('number of Agent tool calls'):\n%s", out)
	}
}

func TestSequenceShowDispatch0aSameTurnCoLocation(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "first Agent tool call must appear in the same response turn as that Bash result block") {
		t.Errorf("dispatch step 0a must state same-turn co-location requirement:\n%s", out)
	}
}

func TestSequenceShowDispatch4AllowListGateEntry(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "satisfies this step only when it contains at least one Agent tool call") {
		t.Errorf("dispatch step 4 must state allow-list gate at entry ('satisfies this step only when it contains at least one Agent tool call'):\n%s", out)
	}
}

func TestSequenceShowDispatch4DeferralClosureText(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Proceed to the Agent tool calls without announcing them first") {
		t.Errorf("dispatch step 4 must contain deferral closure text ('Proceed to the Agent tool calls without announcing them first'):\n%s", out)
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
		"→ make form:prep",
		"→ check form:vet",
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
	checks := []string{"inner mode: cycle", "inner stop_when:", "→ make form:prep", "→ check form:vet"}
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
	checks := []string{"inner mode: cycle", "inner stop_when:", "→ make form:prep", "→ check form:vet"}
	for _, want := range checks {
		if !strings.Contains(out, want) {
			t.Errorf("frame-explore dispatch step missing inner field %q:\n%s", want, out)
		}
	}
}

// Behavior 24: `bar help llm --section sequences` step summary for frame-eval shows dispatch fan-out/join.
func TestHelpLLMSequencesDispatchStepShowsFanOut(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"help", "llm", "--section", "sequences"})
	if code != 0 {
		t.Fatalf("bar help llm --section sequences exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "dispatch[enumerate→all]") {
		t.Errorf("expected frame-eval step summary to contain \"dispatch[enumerate→all]\":\n%s", out)
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
	out, stderr, code := runCLI(t, []string{"sequence", "show", "extract-and-package"})
	if code != 0 {
		t.Fatalf("bar sequence show extract-and-package exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "[no task token") {
		t.Errorf("bar sequence show extract-and-package missing no-task-token warning:\n%s", out)
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
	if !strings.Contains(out, "→ probe survive ghost") {
		t.Errorf("frame-debug inner sequence missing experiment execution step (probe survive ghost):\n%s", out)
	}
}

// Behavior 36: frame-explore inner steps are prep→probe survive ghost audit→vet.
func TestFrameExploreInnerHasActionStep(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "→ probe survive ghost") {
		t.Errorf("frame-explore inner sequence missing experiment execution step (probe survive ghost):\n%s", out)
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
		if dispatchStep.Inner.Steps[i].Token == "make form:prep verify" {
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

// Behavior 42: dispatch protocol point 4 tells spawning agents not to batch items.
func TestSequenceShowDispatchMentionsBarSkills(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "subagent_type: general-purpose") {
		t.Errorf("dispatch protocol point 4 must specify subagent_type: general-purpose:\n%s", out)
	}
}

// Behavior 43: dispatch protocol clause 1 is allow-list (names what orchestrator does, not what it must not do).
func TestSequenceShowDispatchClause1IsAllowList(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
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
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Each agent receives the step token string") {
		t.Errorf("dispatch protocol must contain 'Each agent receives the step token string' instruction:\n%s", out)
	}
}

// Behavior 45: dispatch protocol point 5 names the bar build command form with step token string.
func TestSequenceShowDispatchPoint5TraceabilityClause(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "bar build <step-token-string>") {
		t.Errorf("dispatch protocol point 5 must name 'bar build <step-token-string>' command form:\n%s", out)
	}
}

// Behavior 91: dispatch protocol includes pre-dispatch agent config gate (Criterion G).
// Before fanning out, the orchestrator must run bar build ... agent and include the output in each subagent prompt.
func TestDispatchProtocolPreAgentConfigGate(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "[pre-dispatch agent config gate — required]") {
		t.Errorf("dispatch protocol must contain '[pre-dispatch agent config gate — required]' block:\n%s", out)
	}
	if !strings.Contains(out, "bar build [tokens") {
		t.Errorf("dispatch protocol pre-dispatch gate must name 'bar build [tokens...]' as the required action:\n%s", out)
	}
	if !strings.Contains(out, "## Agent Configuration") {
		t.Errorf("dispatch protocol pre-dispatch gate must use '## Agent Configuration' as the observable discriminator:\n%s", out)
	}
	if !strings.Contains(out, "same response turn") {
		t.Errorf("dispatch protocol pre-dispatch gate must specify 'same response turn' as the structural position:\n%s", out)
	}
	if !strings.Contains(out, "agent's own bar build invocations") {
		t.Errorf("dispatch protocol pre-dispatch 0c must state persona/approach come from agent's own bar build:\n%s", out)
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

// Behavior 77: dispatch protocol point 4 references pre-dispatch derived config (applies to all dispatch steps).
func TestDispatchProtocolPoint4ContainsBarAgent(t *testing.T) {
	for _, seq := range []string{"frame-debug", "frame-eval"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
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
		if !strings.Contains(point4Line, "general-purpose") {
			t.Errorf("%s: point 4 must specify subagent_type: general-purpose, got: %s", seq, point4Line)
		}
	}
}

// Behavior 75: frame-debug dispatch references pre-dispatch derived agent config.
func TestFrameDebugInnerDispatchUsesBarAgent(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "pre-dispatch agent config gate") {
		t.Errorf("frame-debug dispatch must include pre-dispatch agent config gate:\n%s", out)
	}
}

// Behavior 76: frame-debug inner dispatch point 5 requires orchestrator to preserve all Derivation blocks.
func TestFrameDebugInnerDispatchPreservesDerivationBlocks(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "## Derivation block per agent") {
		t.Errorf("frame-debug inner dispatch point 5 must require orchestrator to preserve one '## Derivation block per agent':\n%s", out)
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

// Behavior 69: frame-debug dispatch prompt_hint names literal bar build make form:prep per cycle.
func TestFrameDebugDispatchPromptHintNamesBarBuildCommands(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "bar build make form:prep") {
		t.Errorf("frame-debug dispatch prompt_hint must name literal 'bar build make form:prep' command:\n%s", out)
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

// Behavior 71: frame-debug dispatch point 4 says not to batch items.
func TestFrameDebugDispatchPoint5RequiresBarWorkflowSkill(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "number of Agent tool calls in this turn must equal") {
		t.Errorf("frame-debug dispatch step 4 must state count-equality requirement:\n%s", out)
	}
}

// Behavior 72: frame-debug action step names structural gate condition as observable completion criterion.
func TestFrameDebugActionStepNamesBashToolCallResult(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "output that could not exist in the repository at rest") {
		t.Errorf("frame-debug experiment step must require live output via permit condition 'output that could not exist in the repository at rest':\n%s", out)
	}
}

// Behavior 73: frame-debug vet step names new bar build make form:prep following rejection as observable.
func TestFrameDebugVetStepNamesNewPrepAfterRejection(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "new bar build make form:prep") {
		t.Errorf("frame-debug vet step must name 'new bar build make form:prep' as the observable following rejection:\n%s", out)
	}
}

// Behavior 74: frame-explore experiment step requires structural gate condition (not static reads).
func TestFrameExploreActionStepRequiresBashToolCall(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "output that could not exist in the repository at rest") {
		t.Errorf("frame-explore experiment step must require live output via permit condition 'output that could not exist in the repository at rest':\n%s", out)
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
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
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
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "## Derivation") {
		t.Errorf("dispatch protocol point 5 must require agents to return a '## Derivation' block:\n%s", out)
	}
	if !strings.Contains(out, "## Derivation block per agent") {
		t.Errorf("dispatch protocol point 5 must require orchestrator to preserve one '## Derivation block per agent':\n%s", out)
	}
}

// Behavior 79: inner action protocol block explicitly requires structural gate condition (not just "tools").
func TestInnerActionProtocolRequiresBash(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "Execute actions from prior step using tools.") {
		t.Errorf("inner action protocol must not say 'using tools' — must require live Bash execution:\n%s", out)
	}
	if !strings.Contains(out, "output that could not exist in the repository at rest") {
		t.Errorf("inner action protocol must require live output via permit condition 'output that could not exist in the repository at rest':\n%s", out)
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

// Behavior 81: form:prep and form:vet step tokens always include a task prefix.
func TestPrepVetTokensHaveTaskPrefix(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	for name, seq := range g.Sequences {
		for _, step := range seq.Steps {
			if step.Token == "form:prep" {
				t.Errorf("sequence %q step token must be 'make form:prep' not bare 'form:prep'", name)
			}
			if step.Token == "form:vet" {
				t.Errorf("sequence %q step token must be 'check form:vet' not bare 'form:vet'", name)
			}
			if step.Inner != nil {
				for _, is := range step.Inner.Steps {
					if is.Token == "form:prep" {
						t.Errorf("sequence %q inner step token must be 'make form:prep' not bare 'form:prep'", name)
					}
					if is.Token == "form:vet" {
						t.Errorf("sequence %q inner step token must be 'check form:vet' not bare 'form:vet'", name)
					}
				}
			}
		}
	}
}

// Behavior 82: prompt_hints referencing bar build form:prep/form:vet use task-prefixed tokens.
func TestPrepVetPromptHintsHaveTaskPrefix(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "bar build form:prep") {
		t.Errorf("frame-debug output must not contain bare 'bar build form:prep':\n%s", out)
	}
	if strings.Contains(out, "bar build form:vet") {
		t.Errorf("frame-debug output must not contain bare 'bar build form:vet':\n%s", out)
	}
	if !strings.Contains(out, "bar build make form:prep") {
		t.Errorf("frame-debug output must contain 'bar build make form:prep':\n%s", out)
	}
	if !strings.Contains(out, "bar build check form:vet") {
		t.Errorf("frame-debug output must contain 'bar build check form:vet':\n%s", out)
	}
}

// Behavior 78: non-inner dispatch point 5 tells agents to run bar build with the step token string directly.
func TestDispatchPoint5TokenString(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "The orchestrator must construct and include this exact command") {
		t.Errorf("dispatch protocol point 5 must not contain orchestrator-constructs-literal-command prescription:\n%s", out)
	}
	if !strings.Contains(out, "Each agent receives the step token string") {
		t.Errorf("dispatch protocol point 5 must say 'Each agent receives the step token string':\n%s", out)
	}
}

// Behavior 85: bar sequence show renders [handoff protocol — required] block on requires_user_input (⏸) steps.
func TestHandoffProtocolBlock(t *testing.T) {
	for _, seq := range []string{"experiment-cycle", "probe-and-plan", "simulate-and-review"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "[handoff protocol — required]") {
			t.Errorf("bar sequence show %s must contain '[handoff protocol — required]' on ⏸ step:\n%s", seq, out)
		}
		if !strings.Contains(out, "When you have results, paste them here") {
			t.Errorf("bar sequence show %s must contain exact handoff string 'When you have results, paste them here':\n%s", seq, out)
		}
		// Verify handoff block appears on the ⏸ step (after its step marker)
		pauseIdx := strings.Index(out, "⏸")
		if pauseIdx < 0 {
			t.Errorf("bar sequence show %s missing ⏸ step marker", seq)
			continue
		}
		afterPause := out[pauseIdx:]
		if !strings.Contains(afterPause, "[handoff protocol — required]") {
			t.Errorf("bar sequence show %s: '[handoff protocol — required]' must appear after ⏸ marker", seq)
		}
		if !strings.Contains(afterPause, "When you have results, paste them here") {
			t.Errorf("bar sequence show %s: 'When you have results, paste them here' must appear after ⏸ marker", seq)
		}
	}
}

// Behavior 84: bar sequence show renders [cycle protocol — required] block before first inner step when inner mode is cycle.
func TestInnerCycleProtocolBlock(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		// The rendered inner step line has format: "\n          → make form:prep       <role>\n"
		// The leading newline+indent distinguishes the actual step line from cycle protocol prose that also mentions "→ make form:prep"
		prepIdx := strings.Index(out, "\n          → make form:prep")
		if prepIdx < 0 {
			t.Errorf("bar sequence show %s missing inner step line '→ make form:prep'", seq)
			continue
		}
		// Cycle protocol block must appear between inner stop_when and first → step
		innerStopIdx := strings.Index(out, "inner stop_when:")
		if innerStopIdx < 0 {
			t.Errorf("bar sequence show %s missing 'inner stop_when:'", seq)
			continue
		}
		between := out[innerStopIdx:prepIdx]
		if !strings.Contains(between, "[cycle protocol — required]") {
			t.Errorf("bar sequence show %s: '[cycle protocol — required]' must appear between 'inner stop_when:' and '→ make form:prep':\n%s", seq, between)
		}
		// Cycle protocol must name the falsifiable completion condition
		if !strings.Contains(between, "bar build check form:vet") {
			t.Errorf("bar sequence show %s: cycle protocol must name 'bar build check form:vet' as falsifiable completion condition:\n%s", seq, between)
		}
	}
}

// Behavior 86: all prism-step sequences prohibit backtick-wrapped text and specific tool invocations in frame descriptions.
func TestFrameEnumerationDepthProhibition(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug", "frame-eval", "frame-synthesis", "frame-work", "frame-orbit"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		// Step 1 is the frame enumeration step — find its output before the dispatch step
		step1End := strings.Index(out, "[dispatch: enumerate")
		if step1End < 0 {
			t.Errorf("bar sequence show %s missing dispatch step marker", seq)
			continue
		}
		step1 := out[:step1End]
		if !strings.Contains(step1, "belong to the dispatched agent, not this step") {
			t.Errorf("bar sequence show %s step 1 must contain 'belong to the dispatched agent, not this step':\n%s", seq, step1)
		}
		if !strings.Contains(strings.ToLower(step1), "no backtick-wrapped text") {
			t.Errorf("bar sequence show %s step 1 must contain 'no backtick-wrapped text' (case-insensitive):\n%s", seq, step1)
		}
	}
}

// Behavior 83: bar sequence show renders [bar build gate — required] block for inner non-action steps (prep, vet).
func TestInnerStepBarBuildGate(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		prepIdx := strings.Index(out, "→ make form:prep")
		vetIdx := strings.Index(out, "→ check form:vet")
		if prepIdx < 0 {
			t.Errorf("bar sequence show %s missing '→ make form:prep' inner step", seq)
			continue
		}
		if vetIdx < 0 {
			t.Errorf("bar sequence show %s missing '→ check form:vet' inner step", seq)
			continue
		}
		// Gate block must appear in the substring after → make form:prep (i.e., inside the prep inner step section)
		afterPrep := out[prepIdx:]
		if !strings.Contains(afterPrep, "[bar build gate — required]") {
			t.Errorf("bar sequence show %s: '[bar build gate — required]' must appear after '→ make form:prep':\n%s", seq, out)
		}
		// Gate block must appear in the substring after → check form:vet (i.e., inside the vet inner step section)
		afterVet := out[vetIdx:]
		if !strings.Contains(afterVet, "[bar build gate — required]") {
			t.Errorf("bar sequence show %s: '[bar build gate — required]' must appear after '→ check form:vet':\n%s", seq, out)
		}
		// Experiment execution step uses probe survive ghost and gets the bar build gate
		probeIdx := strings.Index(out, "→ probe survive ghost")
		if probeIdx < 0 {
			t.Errorf("bar sequence show %s missing inner step '→ probe survive ghost':\n%s", seq, out)
			continue
		}
		afterProbe := out[probeIdx:]
		if !strings.Contains(afterProbe, "[bar build gate — required]") {
			t.Errorf("bar sequence show %s: '[bar build gate — required]' must appear after '→ probe survive ghost':\n%s", seq, afterProbe[:min(len(afterProbe), 500)])
		}
	}
}

// Behavior 87: inner experiment execution step uses probe survive ghost token (not Bash-only action).
func TestInnerExperimentStepUsesProbeToken(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "→ probe survive ghost") {
			t.Errorf("bar sequence show %s inner experiment step must use 'probe survive ghost' token:\n%s", seq, out)
		}
		// Must not use the old Bash-only action protocol
		if strings.Contains(out, "[action protocol — required]") {
			t.Errorf("bar sequence show %s must not contain '[action protocol — required]' — experiment step now uses bar build:\n%s", seq, out)
		}
	}
}

// Behavior 88: frame-orbit appears in bar sequence list.
func TestFrameOrbitSequenceExists(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "list"})
	if code != 0 {
		t.Fatalf("bar sequence list exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "frame-orbit") {
		t.Errorf("bar sequence list must contain 'frame-orbit':\n%s", out)
	}
}

// Behavior 89: frame-orbit step structure: prism → dispatch[enumerate→all] → orbit synthesis.
func TestFrameOrbitStepStructure(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-orbit"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-orbit exited %d: %s", code, stderr)
	}
	for _, want := range []string{
		"make method:prism",
		"[dispatch: enumerate→all",
		"orbit",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("frame-orbit must contain %q:\n%s", want, out)
		}
	}
}

// Behavior 90: frame-orbit inner dispatch step includes show method:trace for trajectory narration.
func TestFrameOrbitInnerTraceStep(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-orbit"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-orbit exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "→ show method:trace") {
		t.Errorf("frame-orbit inner dispatch must include 'show method:trace' step:\n%s", out)
	}
}

// Behavior 91: bar sequence show step gate instructs agent to augment step token with additional tokens.
func TestSequenceShowStepGateInstructsTokenAugmentation(t *testing.T) {
	for _, seq := range []string{"check-and-rewrite", "make-and-review"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "at least one token from method/scope/completeness/form axes") {
			t.Errorf("bar sequence show %s: step gate must instruct token augmentation:\n%s", seq, out)
		}
		if !strings.Contains(out, "starting point") {
			t.Errorf("bar sequence show %s: step gate must describe step token as 'starting point':\n%s", seq, out)
		}
	}
}

// Fix B: step gate must warn against using sequence name as token
func TestSequenceShowStepGateNoSequenceNameAsToken(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "make-and-review"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Do not use the sequence name as a token") {
		t.Errorf("bar sequence show step gate must warn against using sequence name as token:\n%s", out)
	}
}

// Fix: bar sequence show must prompt agent to emit ## Sequence Derivation block before step 1
func TestSequenceShowRequiresDerivationBlock(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "make-and-review"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	for _, want := range []string{
		"## Sequence Derivation",
		"Before executing step 1",
		"Mode means:",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("bar sequence show must instruct agent to emit derivation block; missing %q:\n%s", want, out)
		}
	}
}

// Fix: derivation block insertion prompt must direct agent to re-read the task
func TestSequenceShowDerivationInsertionPromptReadsTask(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "make-and-review"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "re-read the task") {
		t.Errorf("bar sequence show derivation block must direct agent to re-read the task for missing inputs:\n%s", out)
	}
}

func TestSequenceShowDerivationInsertionRequiresTokenString(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "make-and-review"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "name the bar build token string for it") {
		t.Errorf("bar sequence show derivation block must require a bar build token string for the inserted step:\n%s", out)
	}
}

func TestSequenceShowDerivationInsertionGate(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "make-and-review"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "A bar build containing that token must appear in the transcript before") {
		t.Errorf("bar sequence show must gate inserted step execution: require bar build for it before canonical step:\n%s", out)
	}
}

func TestSequenceShowAutonomousModeGate(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "make-and-review"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "A response turn that completes a non-final step without a bar build call for the next step does not satisfy autonomous mode") {
		t.Errorf("bar sequence show autonomous mode must gate inter-step continuation:\n%s", out)
	}
}

func TestSequenceShowModeGlossaryInShowOutput(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "make-and-review"})
	if code != 0 {
		t.Fatalf("bar sequence show exited %d: %s", code, stderr)
	}
	for _, want := range []string{
		"autonomous",
		"all steps run without stopping",
		"proceed to the next step immediately",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("bar sequence show: mode glossary must contain %q:\n%s", want, out)
		}
	}
}

func TestSequenceListModeGlossary(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "list"})
	if code != 0 {
		t.Fatalf("bar sequence list exited %d: %s", code, stderr)
	}
	for _, want := range []string{
		"Execution modes:",
		"autonomous",
		"proceed to the next step immediately without waiting for user input",
		"linear",
		"cycle",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("bar sequence list: glossary must contain %q:\n%s", want, out)
		}
	}
}

// Behavior 90: frame-synthesis final step uses probe method:converge, not pick method:converge.
func TestFrameSynthesisFinalStepUsesProbeConverge(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-synthesis"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-synthesis exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "pick method:converge") {
		t.Errorf("frame-synthesis final step must not use 'pick method:converge' — use 'probe method:converge' for synthesis steps:\n%s", out)
	}
	if !strings.Contains(out, "probe method:converge") {
		t.Errorf("frame-synthesis final step must use 'probe method:converge':\n%s", out)
	}
}

// Behavior 92: all frame sequences have an optional terminal form:quiz step for knowledge transfer.
func TestFrameSequencesHaveOptionalQuizStep(t *testing.T) {
	sequences := []string{"frame-synthesis", "frame-explore", "frame-debug", "frame-work", "frame-eval"}
	for _, seq := range sequences {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "form:quiz") {
			t.Errorf("sequence %s must have a terminal form:quiz step for knowledge transfer:\n%s", seq, out)
		}
		if !strings.Contains(out, "optional") {
			t.Errorf("sequence %s quiz step must be marked optional:\n%s", seq, out)
		}
	}
}

// Behavior 93: frame-eval is renamed to frame-eval.
func TestFrameEvalSequenceExists(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "frame-eval") {
		t.Errorf("frame-eval sequence must exist and render its name:\n%s", out)
	}
}

// Behavior 94: SequenceStep DuringDispatch field is parsed from JSON.
func TestSequenceStepDuringDispatchFieldParsed(t *testing.T) {
	raw := `{"token":"prism","role":"prism","type":"dispatch","fan_out":"enumerate","join":"all","during_dispatch":"explain form:quiz"}`
	var step SequenceStep
	if err := json.Unmarshal([]byte(raw), &step); err != nil {
		t.Fatalf("failed to parse SequenceStep with during_dispatch: %v", err)
	}
	if step.DuringDispatch != "explain form:quiz" {
		t.Errorf("DuringDispatch: got %q, want %q", step.DuringDispatch, "explain form:quiz")
	}
}

// Behavior 95: writeDispatchStepBlock renders during_dispatch instruction when field is set.
func TestDispatchStepBlockRendersDuringDispatch(t *testing.T) {
	step := SequenceStep{
		Token:         "prism",
		Role:          "dispatch frames",
		Type:          "dispatch",
		FanOut:        "enumerate",
		Join:          "all",
		DuringDispatch: "explain form:quiz",
	}
	var buf strings.Builder
	writeDispatchStepBlock(&buf, step, 1, nil)
	out := buf.String()
	if !strings.Contains(out, "Dispatching N agents:") {
		t.Errorf("dispatch block must contain cardinality declaration 'Dispatching N agents:' when field is set:\n%s", out)
	}
	if !strings.Contains(out, "explain form:quiz") {
		t.Errorf("dispatch block must contain the during_dispatch command 'explain form:quiz':\n%s", out)
	}
	if !strings.Contains(out, "After spawning all agents") {
		t.Errorf("dispatch block must instruct LLM to run during_dispatch after spawning agents:\n%s", out)
	}
	if !strings.Contains(out, "result block for each Agent tool call") {
		t.Errorf("dispatch block must instruct waiting via result block presence before joining:\n%s", out)
	}
}

// Behavior 96: frame-debug dispatch step has during_dispatch set to show form:quiz.
func TestFrameDebugDispatchStepHasDuringDispatch(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	seq, ok := g.Sequences["frame-debug"]
	if !ok {
		t.Fatal("frame-debug sequence not found")
	}
	for _, step := range seq.Steps {
		if step.Type == "dispatch" {
			if step.DuringDispatch != "show form:quiz" {
				t.Errorf("frame-debug dispatch step DuringDispatch: got %q, want %q", step.DuringDispatch, "show form:quiz")
			}
			return
		}
	}
	t.Error("frame-debug has no dispatch step")
}

// Behavior 97: frame-explore dispatch step has during_dispatch set to show form:quiz.
func TestFrameExploreDispatchStepHasDuringDispatch(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	seq, ok := g.Sequences["frame-explore"]
	if !ok {
		t.Fatal("frame-explore sequence not found")
	}
	for _, step := range seq.Steps {
		if step.Type == "dispatch" {
			if step.DuringDispatch != "show form:quiz" {
				t.Errorf("frame-explore dispatch step DuringDispatch: got %q, want %q", step.DuringDispatch, "show form:quiz")
			}
			return
		}
	}
	t.Error("frame-explore has no dispatch step")
}

// Behavior 98: frame-eval dispatch step has during_dispatch set to show form:quiz.
func TestFrameEvalDispatchStepHasDuringDispatch(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	seq, ok := g.Sequences["frame-eval"]
	if !ok {
		t.Fatal("frame-eval sequence not found")
	}
	for _, step := range seq.Steps {
		if step.Type == "dispatch" {
			if step.DuringDispatch != "show form:quiz" {
				t.Errorf("frame-eval dispatch step DuringDispatch: got %q, want %q", step.DuringDispatch, "show form:quiz")
			}
			return
		}
	}
	t.Error("frame-eval has no dispatch step")
}

// Behavior 99: frame-synthesis dispatch step has during_dispatch set to show form:quiz.
func TestFrameSynthesisDispatchStepHasDuringDispatch(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	seq, ok := g.Sequences["frame-synthesis"]
	if !ok {
		t.Fatal("frame-synthesis sequence not found")
	}
	for _, step := range seq.Steps {
		if step.Type == "dispatch" {
			if step.DuringDispatch != "show form:quiz" {
				t.Errorf("frame-synthesis dispatch step DuringDispatch: got %q, want %q", step.DuringDispatch, "show form:quiz")
			}
			return
		}
	}
	t.Error("frame-synthesis has no dispatch step")
}

// Behavior 101: when DuringDispatch is set, dispatch gate instructs run_in_background: true on Agent calls.
func TestDispatchStepBlockRunsAgentsInBackgroundWhenDuringDispatchSet(t *testing.T) {
	step := SequenceStep{
		Token:          "prism",
		Role:           "dispatch frames",
		Type:           "dispatch",
		FanOut:         "enumerate",
		Join:           "all",
		DuringDispatch: "show form:quiz",
	}
	var buf strings.Builder
	writeDispatchStepBlock(&buf, step, 1, nil)
	out := buf.String()
	if !strings.Contains(out, "run_in_background: true") {
		t.Errorf("dispatch block with during_dispatch must instruct run_in_background: true on Agent calls:\n%s", out)
	}
}

// Behavior 102: when DuringDispatch is set, during_dispatch instruction tells LLM to wait for all background agents before joining.
func TestDispatchStepBlockWaitsForBackgroundNotificationsBeforeJoin(t *testing.T) {
	step := SequenceStep{
		Token:          "prism",
		Role:           "dispatch frames",
		Type:           "dispatch",
		FanOut:         "enumerate",
		Join:           "all",
		DuringDispatch: "show form:quiz",
	}
	var buf strings.Builder
	writeDispatchStepBlock(&buf, step, 1, nil)
	out := buf.String()
	if !strings.Contains(out, "background agent") {
		t.Errorf("dispatch block with during_dispatch must reference background agents:\n%s", out)
	}
	if !strings.Contains(out, "result block for each Agent tool call") {
		t.Errorf("dispatch block with during_dispatch must instruct waiting via result block presence:\n%s", out)
	}
}

// Behavior 103: when DuringDispatch is set, during_dispatch Bash instruction appears before Agent spawning instruction.
func TestDispatchStepBlockDuringDispatchBeforeAgentSpawn(t *testing.T) {
	step := SequenceStep{
		Token:          "prism",
		Role:           "dispatch frames",
		Type:           "dispatch",
		FanOut:         "enumerate",
		Join:           "all",
		DuringDispatch: "show form:quiz",
	}
	var buf strings.Builder
	writeDispatchStepBlock(&buf, step, 1, nil)
	out := buf.String()
	bashIdx := strings.Index(out, "show form:quiz")
	spawnIdx := strings.Index(out, "Spawn one Agent tool call")
	if bashIdx == -1 {
		t.Fatalf("dispatch block must contain during_dispatch command 'show form:quiz':\n%s", out)
	}
	if spawnIdx == -1 {
		t.Fatalf("dispatch block must contain Agent spawning instruction 'Spawn one Agent tool call':\n%s", out)
	}
	if spawnIdx > bashIdx {
		t.Errorf("Agent spawning instruction must appear before during_dispatch Bash instruction: spawnIdx=%d bashIdx=%d\n%s", spawnIdx, bashIdx, out)
	}
}

// Behavior 106: when DuringDispatch is set, dispatch block contains explicit interruption contract — agents returning mid-task is expected.
func TestDispatchStepBlockInterruptionContractPresent(t *testing.T) {
	step := SequenceStep{
		Token:          "prism",
		Role:           "dispatch frames",
		Type:           "dispatch",
		FanOut:         "enumerate",
		Join:           "all",
		DuringDispatch: "show form:quiz",
	}
	var buf strings.Builder
	writeDispatchStepBlock(&buf, step, 1, nil)
	out := buf.String()
	if !strings.Contains(out, "agents may return") {
		t.Errorf("dispatch block with during_dispatch must contain interruption contract ('agents may return'):\n%s", out)
	}
	if !strings.Contains(out, "complete the current question-answer exchange") {
		t.Errorf("dispatch block with during_dispatch must instruct completing the current question-answer exchange before stopping:\n%s", out)
	}
}

// Behavior 108: when DuringDispatch is set, the stop instruction names a permit-condition (complete the current question-answer exchange) rather than an unconditional stop command.
func TestDispatchStepBlockInterruptionContractPermitCondition(t *testing.T) {
	step := SequenceStep{
		Token:          "prism",
		Role:           "dispatch frames",
		Type:           "dispatch",
		FanOut:         "enumerate",
		Join:           "all",
		DuringDispatch: "show form:quiz",
	}
	var buf strings.Builder
	writeDispatchStepBlock(&buf, step, 1, nil)
	out := buf.String()
	if !strings.Contains(out, "complete the current question-answer exchange") {
		t.Errorf("during_dispatch stop instruction must name a permit-condition ('complete the current question-answer exchange') rather than an unconditional stop:\n%s", out)
	}
}

// Behavior 107: frame dispatch sequences (frame-eval, frame-explore, frame-synthesis, frame-debug) have mode linear, not autonomous — they contain during_dispatch steps which are user-interactive.
func TestFrameDispatchSequencesAreLinear(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	for _, name := range []string{"frame-eval", "frame-explore", "frame-synthesis", "frame-debug"} {
		seq, ok := g.Sequences[name]
		if !ok {
			t.Errorf("sequence %q not found", name)
			continue
		}
		if seq.Mode != "linear" {
			t.Errorf("sequence %q mode: got %q, want %q — sequences with during_dispatch steps must be linear", name, seq.Mode, "linear")
		}
	}
}

// Behavior 104: bar sequence list autonomous description states that autonomous sequences contain no requires_user_input steps.
func TestSequenceListAutonomousNoRequiresUserInput(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "list"})
	if code != 0 {
		t.Fatalf("bar sequence list exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "no requires_user_input steps") {
		t.Errorf("bar sequence list autonomous description must state 'no requires_user_input steps':\n%s", out)
	}
}

// Behavior 91: frame-explore final step uses probe method:converge, not pick method:converge.
func TestFrameExploreFinalStepUsesProbeConverge(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if strings.Contains(out, "pick method:converge") {
		t.Errorf("frame-explore final step must not use 'pick method:converge' — use 'probe method:converge' for synthesis steps:\n%s", out)
	}
	if !strings.Contains(out, "probe method:converge") {
		t.Errorf("frame-explore final step must use 'probe method:converge':\n%s", out)
	}
}

// Behavior 108: frame-explore inner stop_when gates on literal string "Goal condition: met" in vet output.
func TestFrameExploreInnerStopWhenGatesOnLiteralString(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Goal condition: met") {
		t.Errorf("frame-explore inner stop_when must gate on literal string 'Goal condition: met':\n%s", out)
	}
	if !strings.Contains(out, "does not contain this exact string") {
		t.Errorf("frame-explore inner stop_when must name the absent-string consequence:\n%s", out)
	}
}

// Behavior 109: frame-explore vet prompt_hint requires ending with "Goal condition: met" or "Goal condition: unmet".
func TestFrameExploreVetPromptHintRequiresGoalConditionString(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Goal condition: unmet") {
		t.Errorf("frame-explore vet prompt_hint must require 'Goal condition: unmet' output when not met:\n%s", out)
	}
}

// Behavior 110: frame-debug inner stop_when gates on literal string "Root cause: confirmed" in vet output.
func TestFrameDebugInnerStopWhenGatesOnLiteralString(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Root cause: confirmed") {
		t.Errorf("frame-debug inner stop_when must gate on literal string 'Root cause: confirmed':\n%s", out)
	}
	if !strings.Contains(out, "does not contain this exact string") {
		t.Errorf("frame-debug inner stop_when must name the absent-string consequence:\n%s", out)
	}
}

// Behavior 111: frame-debug vet prompt_hint requires ending with "Root cause: confirmed" or "Root cause: unconfirmed".
func TestFrameDebugVetPromptHintRequiresRootCauseString(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "Root cause: unconfirmed") {
		t.Errorf("frame-debug vet prompt_hint must require 'Root cause: unconfirmed' output when not confirmed:\n%s", out)
	}
}

// Behavior 112: survive step prompt_hint names Bash tool calls exclusively — "Bash or tool call" must not appear.
func TestSurvivePromptHintNamesBashExclusively(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if strings.Contains(out, "Bash or tool call") {
			t.Errorf("%s survive prompt_hint must not contain 'Bash or tool call' — Read tool calls must be excluded explicitly:\n%s", seq, out)
		}
		if !strings.Contains(out, "Bash tool call") {
			t.Errorf("%s survive prompt_hint must name 'Bash tool call' exclusively:\n%s", seq, out)
		}
	}
}

// Behavior 113: survive step prompt_hint contains absence clause naming Read-only transcripts as non-compliant.
func TestSurvivePromptHintContainsReadAbsenceClause(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "identify every factual claim") {
			t.Errorf("%s survive prompt_hint must contain precondition verification clause 'identify every factual claim':\n%s", seq, out)
		}
	}
}

// Behavior 114: survive step prompt_hint requires live execution output (stdout or stderr).
func TestSurvivePromptHintRequiresLiveOutput(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "stdout lines, stderr lines, log entries, test result records, application trace") {
			t.Errorf("%s survive prompt_hint must contain valid-class enumeration 'stdout lines, stderr lines, log entries, test result records, application trace':\n%s", seq, out)
		}
	}
}

// Behavior 115: frame-explore prism prompt_hint names the root criterion and names valid signal classes.
func TestFrameExplorePrismRequiresLiveSignal(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "cannot exist in the repository at rest") {
		t.Errorf("frame-explore prism prompt_hint must contain root criterion 'cannot exist in the repository at rest':\n%s", out)
	}
	if !strings.Contains(out, "stdout lines, stderr lines, log entries, test result records, application trace") {
		t.Errorf("frame-explore prism prompt_hint must contain valid signal class enumeration:\n%s", out)
	}
}

// Behavior 116: frame-debug prism prompt_hint names the root criterion, names valid signal classes,
// and contains the code-artifact exclusion list.
func TestFrameDebugPrismRequiresLiveSignalAndScopesDelegation(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "cannot exist in the repository at rest") {
		t.Errorf("frame-debug prism prompt_hint must contain root criterion 'cannot exist in the repository at rest':\n%s", out)
	}
	if !strings.Contains(out, "type definitions, mapping tables, switch branches, schema files, function signatures") {
		t.Errorf("frame-debug prism prompt_hint must contain code-artifact exclusion list:\n%s", out)
	}
}

// Behavior 117: frame-explore prism prompt_hint contains the live-signal derivation instruction.
func TestFrameExplorePrismLiveSignalRejectionClause(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-explore"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-explore exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "invoking the system") {
		t.Errorf("frame-explore prism must contain 'invoking the system':\n%s", out)
	}
	if !strings.Contains(out, "would show, would appear, could be observed as") {
		t.Errorf("frame-explore prism must contain conditional-prediction closure strings:\n%s", out)
	}
}

// Behavior 118: frame-debug prism prompt_hint contains the live-signal derivation instruction.
func TestFrameDebugPrismLiveSignalRejectionClause(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "frame-debug"})
	if code != 0 {
		t.Fatalf("bar sequence show frame-debug exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "invoking the system") {
		t.Errorf("frame-debug prism must contain 'invoking the system':\n%s", out)
	}
	if !strings.Contains(out, "would show, would appear, could be observed as") {
		t.Errorf("frame-debug prism must contain conditional-prediction closure strings:\n%s", out)
	}
}

// Behavior 119: both prism prompt_hints require a class of output, not a single specific instance.
func TestPrismLiveSignalRequiresClassOfOutput(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "cannot exist in the repository at rest") {
			t.Errorf("%s prism must contain root criterion 'cannot exist in the repository at rest':\n%s", seq, out)
		}
	}
}

// Behavior 122: prep step token includes verify to enforce falsification criterion before running.
func TestPrepStepIncludesVerify(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "make form:prep verify") {
			t.Errorf("%s prep step must use token 'make form:prep verify' to enforce falsification criterion:\n%s", seq, out)
		}
	}
}

// Behavior 123: vet step token includes audit to enforce locally-defensible verdicts.
func TestVetStepIncludesAudit(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "check form:vet audit") {
			t.Errorf("%s vet step must use token 'check form:vet audit' to enforce adversarial verdict scrutiny:\n%s", seq, out)
		}
	}
}

// Behavior 120: frame-explore and frame-debug prism prompt_hints name application trace
// (stack frames from a running process) as a valid live-signal output class.
func TestPrismNamesApplicationTraceAsValidOutput(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "application trace") {
			t.Errorf("%s prism must name 'application trace' as a valid output class:\n%s", seq, out)
		}
	}
}

// Behavior 121: survive step prompt_hints name runtime traces alongside stdout/stderr.
func TestSurviveNamesRuntimeTraces(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "run a Bash command whose output would differ if the claim were false") {
			t.Errorf("%s survive step must name precondition verification requirement 'run a Bash command whose output would differ if the claim were false':\n%s", seq, out)
		}
	}
}

// Behavior 124: experiment-cycle prep step includes verify.
func TestExperimentCyclePrepIncludesVerify(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "experiment-cycle"})
	if code != 0 {
		t.Fatalf("bar sequence show experiment-cycle exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "make form:prep verify") {
		t.Errorf("experiment-cycle prep step must use token 'make form:prep verify':\n%s", out)
	}
}

// Behavior 126: inner cycle stop_when check uses allow-list gate naming the Findings block permission condition.
func TestCycleStopWhenPermissionString(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "The Findings block is permitted only when") {
			t.Errorf("bar sequence show %s: cycle stop_when check must contain 'The Findings block is permitted only when':\n%s", seq, out)
		}
	}
}

// Behavior 127: inner cycle stop_when check names positional constraint on Findings block.
func TestCycleStopWhenMustNotAppear(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "must not appear before the literal stop_when string") {
			t.Errorf("bar sequence show %s: cycle stop_when check must contain 'must not appear before the literal stop_when string':\n%s", seq, out)
		}
	}
}

// Behavior 128: inner cycle stop_when check does not use the old deny-list re-entry clause.
func TestCycleStopWhenOldStringAbsent(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if strings.Contains(out, "If stop_when is not met, begin a new cycle") {
			t.Errorf("bar sequence show %s: cycle stop_when check must not contain old deny-list clause 'If stop_when is not met, begin a new cycle':\n%s", seq, out)
		}
	}
}

// Behavior 129: inner cycle stop_when check uses token-agnostic language, not token-specific 'vet output'.
func TestCycleStopWhenNoVetOutputReference(t *testing.T) {
	for _, seq := range []string{"frame-explore", "frame-debug"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		// Locate only the cycle protocol block — starts at [cycle protocol — required], ends before the first inner step line.
		cycleProtoIdx := strings.Index(out, "[cycle protocol — required]")
		firstStepIdx := strings.Index(out, "\n          → ")
		if cycleProtoIdx < 0 || firstStepIdx < 0 || firstStepIdx < cycleProtoIdx {
			t.Errorf("bar sequence show %s: could not locate cycle protocol block", seq)
			continue
		}
		cycleBlock := out[cycleProtoIdx:firstStepIdx]
		if strings.Contains(cycleBlock, "vet output") || strings.Contains(cycleBlock, "vet tool call result") {
			t.Errorf("bar sequence show %s: cycle stop_when block must not contain token-specific 'vet output' or 'vet tool call result':\n%s", seq, cycleBlock)
		}
	}
}

// Behavior 125: experiment-cycle, make-and-vet, and plan-and-retrospect vet steps include audit.
func TestVetStepsIncludeAuditAcrossSequences(t *testing.T) {
	for _, seq := range []string{"experiment-cycle", "make-and-review", "plan-and-retrospect"} {
		out, stderr, code := runCLI(t, []string{"sequence", "show", seq})
		if code != 0 {
			t.Fatalf("bar sequence show %s exited %d: %s", seq, code, stderr)
		}
		if !strings.Contains(out, "check form:vet audit") {
			t.Errorf("%s vet step must use token 'check form:vet audit':\n%s", seq, out)
		}
	}
}
