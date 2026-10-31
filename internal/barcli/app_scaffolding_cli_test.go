package barcli

import (
	"bytes"
	"os"
	"sort"
	"strings"
	"testing"
)

// The prompt scaffolding text comes from the grammar (lib/metaPromptConfig.py).
// These tests cover every command that renders a prompt, and the sequence and
// dispatch text printed by `bar sequence` and `bar help dispatch`.

var gatePhrases = []string{"does not satisfy", "An evaluator", "evaluator determines"}

func TestGrammarCarriesScaffoldingText(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	if !strings.Contains(g.PlanningDirective, "Token application") {
		t.Errorf("planning directive should ask for a Token application record, got %q", g.PlanningDirective)
	}
	if strings.TrimSpace(g.TokenLoading) == "" || strings.TrimSpace(g.CompositionLoading) == "" {
		t.Error("grammar must carry token_loading and composition_loading text")
	}
	st := g.SequenceText
	if st == nil || len(st.BuildGate) == 0 || len(st.ActionStep) == 0 || st.Dispatch == nil || len(st.Rewrites) == 0 {
		t.Fatalf("grammar must carry sequence_text with build_gate, action_step, dispatch, and rewrites: %+v", st)
	}
}

func assertScaffold(t *testing.T, what, out string) {
	t.Helper()
	if !strings.Contains(out, "=== REQUEST ===") {
		t.Errorf("%s: expected English headings (=== REQUEST ===), got:\n%.400s", what, out)
	}
	for _, unwanted := range []string{"依頼", "Token derivations:", "Derived stance complete", "Loaded: <slug>", "verbatim and authoritative"} {
		if strings.Contains(out, unwanted) {
			t.Errorf("%s: output should not contain %q", what, unwanted)
		}
	}
}

func TestBuildRendersTheScaffolding(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	out := runBuildCLI(t, []string{"build", "show", "mean"}, nil)
	if out.Exit != 0 {
		t.Fatalf("exit %d: %s", out.Exit, out.Stderr)
	}
	assertScaffold(t, "build", out.Stdout)
	for _, want := range []string{"=== FORMAT ===", "Token application", "軸", "役割", "before any other tool call"} {
		if !strings.Contains(out.Stdout, want) {
			t.Errorf("build output missing %q", want)
		}
	}
}

func TestStyleFlagIsGone(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	out := runBuildCLI(t, []string{"build", "show", "mean", "--style", "plain"}, nil)
	if out.Exit == 0 {
		t.Error("--style was removed; expected a non-zero exit for an unknown flag")
	}
}

func TestCompositionBlockHasLightLoadingInstruction(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	result := &BuildResult{
		Task:               "show",
		CompositionLoading: g.CompositionLoading,
		ActiveCompositions: []Composition{{Name: "demo-pair", Prose: "When both are active, do the combined thing."}},
	}
	out := RenderPlainText(result)
	if !strings.Contains(out, "demo-pair") || !strings.Contains(out, "bar help composition") {
		t.Errorf("composition block should list the composition and how to look it up:\n%s", out)
	}
	for _, unwanted := range []string{"Composition active:", "Loaded: <slug>", "does not satisfy"} {
		if strings.Contains(out, unwanted) {
			t.Errorf("composition block should not contain %q", unwanted)
		}
	}
	if !strings.Contains(out, "合成") {
		t.Errorf("composition label should keep its kanji for token identification")
	}
}

func TestShuffleRendersTheScaffolding(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	out, stderr, code := runCLI(t, []string{"shuffle", "--seed", "7"})
	if code != 0 {
		t.Fatalf("exit %d: %s", code, stderr)
	}
	assertScaffold(t, "shuffle", out)
}

func TestCompareRendersTheScaffolding(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	out := runBuildCLI(t, []string{"build", "show", "method=diagnose,hollow", "--subject", "x"}, nil)
	if out.Exit != 0 {
		t.Fatalf("exit %d: %s", out.Exit, out.Stderr)
	}
	assertScaffold(t, "compare", out.Stdout)
}

func TestPresetUseRendersTheScaffolding(t *testing.T) {
	t.Setenv(configDirEnv, t.TempDir())
	if exit := Run([]string{"build", "make", "struct", "--subject", "Initial"}, strings.NewReader(""), &bytes.Buffer{}, &bytes.Buffer{}); exit != 0 {
		t.Fatalf("build exit %d", exit)
	}
	if exit := Run([]string{"preset", "save", "scaffold-test"}, strings.NewReader(""), &bytes.Buffer{}, &bytes.Buffer{}); exit != 0 {
		t.Fatalf("preset save exit %d", exit)
	}
	out, stderr, code := runCLI(t, []string{"preset", "use", "scaffold-test", "--subject", "Fresh"})
	if code != 0 {
		t.Fatalf("preset use exit %d: %s", code, stderr)
	}
	assertScaffold(t, "preset use", out)
}

func TestTUIPreviewRendersTheScaffolding(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatal(err)
	}
	out, err := buildPreviewPrompt(g, []string{"show", "mean"}, "x", "")
	if err != nil {
		t.Fatal(err)
	}
	assertScaffold(t, "tui preview", out)
}

func TestSequenceShowScaffolding(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "token-rewrite"})
	if code != 0 {
		t.Fatalf("exit %d: %s", code, stderr)
	}
	for _, want := range []string{
		"extra step:", "[bar build step]", "Step N complete.", "Agents complete:", // opening, gate, mode markers
		"[dispatch step]", "Dispatching N agents:", "## Agent Configuration", "subagent_type: general-purpose",
		"run_in_background: true", "## Derivation", "shoshin", "join: all", "one Agent call per item",
		"starting point", "The sequence name is not a token", // token augmentation and no sequence-name tokens
	} {
		if !strings.Contains(out, want) {
			t.Errorf("sequence show token-rewrite missing %q", want)
		}
	}
	for _, unwanted := range []string{"## Sequence Derivation", "[bar build gate — required]", "[DISPATCH GATE]", "pre-dispatch agent config gate", "[dispatch protocol — required]"} {
		if strings.Contains(out, unwanted) {
			t.Errorf("sequence show should not contain %q", unwanted)
		}
	}
}

func TestSequenceListModeLines(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "list"})
	if code != 0 {
		t.Fatalf("exit %d: %s", code, stderr)
	}
	for _, want := range []string{"autonomous", "linear", "cycle", "Step N complete."} {
		if !strings.Contains(out, want) {
			t.Errorf("sequence list missing %q", want)
		}
	}
	for _, phrase := range gatePhrases {
		if strings.Contains(out, phrase) {
			t.Errorf("sequence list should not contain %q", phrase)
		}
	}
}

func TestEverySequenceShowHasNoGateClauses(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatal(err)
	}
	for name := range g.Sequences {
		out, stderr, code := runCLI(t, []string{"sequence", "show", name})
		if code != 0 {
			t.Fatalf("sequence show %s: exit %d: %s", name, code, stderr)
		}
		for _, phrase := range gatePhrases {
			if strings.Contains(out, phrase) {
				t.Errorf("`sequence show %s` should not contain %q", name, phrase)
			}
		}
	}
}

func TestSequenceRewritesKeepTheRules(t *testing.T) {
	out, _, _ := runCLI(t, []string{"sequence", "show", "token-rewrite"})
	if !strings.Contains(out, "reproduce each `## Derivation` block") {
		t.Errorf("token-rewrite should still require reproducing the Derivation blocks")
	}
	for name, literal := range map[string]string{"frame-explore": "Goal condition: met", "frame-debug": "Root cause: confirmed"} {
		out, _, code := runCLI(t, []string{"sequence", "show", name})
		if code != 0 {
			t.Fatalf("%s: exit %d", name, code)
		}
		if !strings.Contains(out, literal) || !strings.Contains(out, "If it does not, start a new cycle.") {
			t.Errorf("%s: stop_when must gate on %q and say what happens when it is absent", name, literal)
		}
	}
}

func TestSequenceDispatchVariants(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatal(err)
	}
	cmd := ""
	for _, step := range g.Sequences["frame-work"].Steps {
		if step.DuringDispatch != "" {
			cmd = step.DuringDispatch
		}
	}
	if cmd != "" {
		out, _, code := runCLI(t, []string{"sequence", "show", "frame-work"})
		if code != 0 || !strings.Contains(out, "run `"+cmd+"`") {
			t.Errorf("during_dispatch command %q should be run while agents work (exit %d)", cmd, code)
		}
		for _, want := range []string{"Dispatching N agents:", "run_in_background: true", "as --subject", "carry it out", "not user messages", "own stop condition", "Do not quote"} {
			if !strings.Contains(out, want) {
				t.Errorf("during-dispatch step missing %q", want)
			}
		}
	}
	out, _, code := runCLI(t, []string{"sequence", "show", "assay-cycle"})
	if code != 0 || !strings.Contains(out, "[cycle] The steps below form one cycle") {
		t.Errorf("assay-cycle should print the cycle block (exit %d)", code)
	}
}

func TestHelpDispatchScaffolding(t *testing.T) {
	out, _, code := runCLI(t, []string{"help", "dispatch"})
	if code != 0 {
		t.Fatalf("exit %d", code)
	}
	for _, want := range []string{"## Agent Configuration", "Dispatching N agents:"} {
		if !strings.Contains(out, want) {
			t.Errorf("help dispatch missing %q", want)
		}
	}
	for _, unwanted := range []string{"[DISPATCH GATE]", "An evaluator", "pre-dispatch agent config gate"} {
		if strings.Contains(out, unwanted) {
			t.Errorf("help dispatch should not contain %q", unwanted)
		}
	}
}

// firstSequenceWith returns the name of a sequence (sorted for determinism) with a step matching pred.
func firstSequenceWith(t *testing.T, g *Grammar, pred func(SequenceStep) bool) string {
	t.Helper()
	names := make([]string, 0, len(g.Sequences))
	for n := range g.Sequences {
		names = append(names, n)
	}
	sort.Strings(names)
	for _, n := range names {
		for _, step := range g.Sequences[n].Steps {
			if pred(step) {
				return n
			}
		}
	}
	return ""
}

func showSequence(t *testing.T, name string) string {
	t.Helper()
	out, stderr, code := runCLI(t, []string{"sequence", "show", name})
	if code != 0 {
		t.Fatalf("sequence show %s: exit %d: %s", name, code, stderr)
	}
	return out
}

func TestInnerDispatchAgentsDoNotDiscoverTokens(t *testing.T) {
	g, _ := LoadGrammar("")
	name := firstSequenceWith(t, g, func(s SequenceStep) bool { return s.Type == "dispatch" && s.Inner != nil })
	if name == "" {
		t.Skip("no sequence has an inner dispatch step")
	}
	out := showSequence(t, name)
	if !strings.Contains(out, "do not run `bar help llm` or discover tokens") {
		t.Errorf("%s: inner dispatch agents should run only the given commands, not discover tokens", name)
	}
}

func TestActionStepsDoNotRunBarBuild(t *testing.T) {
	g, _ := LoadGrammar("")
	name := firstSequenceWith(t, g, func(s SequenceStep) bool { return s.Type == "action" })
	if name == "" {
		t.Skip("no sequence has an action step")
	}
	out := showSequence(t, name)
	for _, want := range []string{"[action step]", "Do not run `bar build` here.", "Record the results before moving on."} {
		if !strings.Contains(out, want) {
			t.Errorf("%s: action step missing %q", name, want)
		}
	}
}

func TestCycleStopsOnlyWhenTheStopStringAppears(t *testing.T) {
	g, _ := LoadGrammar("")
	name := firstSequenceWith(t, g, func(s SequenceStep) bool { return s.Inner != nil && s.Inner.Mode == "cycle" })
	if name == "" {
		t.Skip("no sequence has an inner cycle")
	}
	out := showSequence(t, name)
	for _, want := range []string{"The steps below form one cycle", "only then write the Findings block", "start a new cycle from step 1"} {
		if !strings.Contains(out, want) {
			t.Errorf("%s: cycle block missing %q", name, want)
		}
	}
}

func TestHandoffStepsEndAtTheHandoffLine(t *testing.T) {
	g, _ := LoadGrammar("")
	name := firstSequenceWith(t, g, func(s SequenceStep) bool { return s.RequiresUserInput })
	if name == "" {
		t.Skip("no sequence has a user-input step")
	}
	out := showSequence(t, name)
	for _, want := range []string{"When you have results, paste them here", "Do not produce any further content after this line in the same response."} {
		if !strings.Contains(out, want) {
			t.Errorf("%s: handoff step missing %q", name, want)
		}
	}
}

func TestSequenceNamesAreNotTokensInTheBuildGate(t *testing.T) {
	out := showSequence(t, "token-rewrite")
	for _, want := range []string{"The sequence name is not a token", "as the starting point", "plus at least one"} {
		if !strings.Contains(out, want) {
			t.Errorf("build gate missing %q", want)
		}
	}
}

// The help llm manual text lives in help_llm.go; the token catalog it prints comes from the
// grammar and is covered by the token-description protocols, so this checks the manual source.
func TestHelpLLMManualHasNoGateClauses(t *testing.T) {
	src, err := os.ReadFile("help_llm.go")
	if err != nil {
		t.Fatal(err)
	}
	text := string(src)
	for _, phrase := range gatePhrases {
		if strings.Contains(text, phrase) {
			t.Errorf("help_llm.go manual text should not contain %q", phrase)
		}
	}
	if strings.Contains(text, "Sequence Derivation") {
		t.Errorf("help llm still tells agents to emit a Sequence Derivation block, which bar sequence show no longer asks for")
	}
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatal(err)
	}
	var buf strings.Builder
	renderLLMHelp(&buf, g, "", true)
	if !strings.Contains(buf.String(), "extra step:") {
		t.Errorf("help llm should describe the one-line `Sequence: ...; extra step: ...` opening that bar sequence show asks for")
	}
}
