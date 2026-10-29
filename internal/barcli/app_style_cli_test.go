package barcli

import (
	"strings"
	"testing"
)

// Prompt style: "plain" swaps in the grammar's plain scaffolding and drops kanji
// from non-token section labels; "standard" keeps the original rendering.

func TestGrammarLoadsPlainScaffolding(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	if g.Plain == nil {
		t.Fatal("grammar must carry a plain scaffolding block")
	}
	if !strings.Contains(g.Plain.PlanningDirective, "Token application") {
		t.Errorf("plain planning directive should ask for a Token application record, got %q", g.Plain.PlanningDirective)
	}
	if strings.TrimSpace(g.Plain.TokenLoading) == "" {
		t.Error("plain block must carry token_loading text for the TOKENS section")
	}
}

func TestBuildStylePlainUsesPlainScaffolding(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	out := runBuildCLI(t, []string{"build", "show", "mean", "--style", "plain"}, nil)
	if out.Exit != 0 {
		t.Fatalf("exit %d: %s", out.Exit, out.Stderr)
	}
	s := out.Stdout
	for _, want := range []string{"=== REQUEST ===", "=== FORMAT ===", "Token application", "軸", "役割"} {
		if !strings.Contains(s, want) {
			t.Errorf("plain output missing %q", want)
		}
	}
	for _, unwanted := range []string{"依頼", "形式", "Token derivations:", "Derived stance complete", "Loaded: <slug>", "verbatim and authoritative"} {
		if strings.Contains(s, unwanted) {
			t.Errorf("plain output should not contain %q", unwanted)
		}
	}
}

func TestBuildStyleStandardKeepsOriginalScaffolding(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	out := runBuildCLI(t, []string{"build", "show", "mean", "--style", "standard"}, nil)
	if out.Exit != 0 {
		t.Fatalf("exit %d: %s", out.Exit, out.Stderr)
	}
	for _, want := range []string{"=== REQUEST 依頼 ===", "=== FORMAT 形式 ===", "Token derivations:", "Loaded: <slug>"} {
		if !strings.Contains(out.Stdout, want) {
			t.Errorf("standard output missing %q", want)
		}
	}
}

func TestBuildStyleDefaultsToPlain(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	t.Setenv(styleEnv, "")
	out := runBuildCLI(t, []string{"build", "show", "mean"}, nil)
	if out.Exit != 0 {
		t.Fatalf("exit %d: %s", out.Exit, out.Stderr)
	}
	if !strings.Contains(out.Stdout, "=== REQUEST ===") || strings.Contains(out.Stdout, "Token derivations:") {
		t.Errorf("default build should render the plain style, got:\n%s", out.Stdout)
	}
}

func TestBuildStyleEnvOverridesDefaultAndFlagOverridesEnv(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	t.Setenv(styleEnv, "standard")
	out := runBuildCLI(t, []string{"build", "show", "mean"}, nil)
	if !strings.Contains(out.Stdout, "Token derivations:") {
		t.Errorf("env standard should select the standard style")
	}
	out = runBuildCLI(t, []string{"build", "show", "mean", "--style", "plain"}, nil)
	if strings.Contains(out.Stdout, "Token derivations:") {
		t.Errorf("--style plain should win over the environment")
	}
}

func TestBuildStyleRejectsUnknownValue(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	out := runBuildCLI(t, []string{"build", "show", "--style", "fancy"}, nil)
	if out.Exit == 0 {
		t.Fatal("expected a non-zero exit for an unknown style")
	}
	if !strings.Contains(out.Stderr+out.Stdout, "plain") {
		t.Errorf("error should name the valid styles, got stderr=%q", out.Stderr)
	}
}

func TestPlainStyleCompositionBlockHasNoLoadedLineCeremony(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	result := &BuildResult{
		Task:               "show",
		ActiveCompositions: []Composition{{Name: "demo-pair", Prose: "When both are active, do the combined thing."}},
	}
	ApplyStyle(result, g, StylePlain)
	out := RenderPlainText(result)
	if !strings.Contains(out, "demo-pair") || !strings.Contains(out, "bar help composition") {
		t.Errorf("plain composition block should still list the composition and how to look it up:\n%s", out)
	}
	for _, unwanted := range []string{"Composition active:", "Loaded: <slug>", "does not satisfy"} {
		if strings.Contains(out, unwanted) {
			t.Errorf("plain output should not contain %q", unwanted)
		}
	}
	if !strings.Contains(out, "合成") {
		t.Errorf("composition label should keep its kanji for token identification")
	}
}

func TestGrammarLoadsPlainSequenceText(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	if g.Plain == nil || g.Plain.Sequence == nil {
		t.Fatal("grammar plain block must carry sequence text")
	}
	if len(g.Plain.Sequence.BuildGate) == 0 || len(g.Plain.Sequence.ActionStep) == 0 {
		t.Error("plain sequence text must include build_gate and action_step lines")
	}
}

func TestSequenceShowPlainStyleDropsGateCeremony(t *testing.T) {
	t.Setenv(styleEnv, "")
	out, stderr, code := runCLI(t, []string{"sequence", "show", "token-rewrite"})
	if code != 0 {
		t.Fatalf("exit %d: %s", code, stderr)
	}
	for _, want := range []string{"extra step:", "[bar build step]", "Step N complete.", "Agents complete:", "[action step]"} {
		if !strings.Contains(out, want) && want != "[action step]" {
			t.Errorf("plain sequence show missing %q", want)
		}
	}
	for _, unwanted := range []string{"## Sequence Derivation", "[bar build gate — required]", "has not derived the sequence rules"} {
		if strings.Contains(out, unwanted) {
			t.Errorf("plain sequence show should not contain %q", unwanted)
		}
	}
}

func TestSequenceShowStandardStyleKeepsOriginal(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "token-rewrite", "--style", "standard"})
	if code != 0 {
		t.Fatalf("exit %d: %s", code, stderr)
	}
	for _, want := range []string{"## Sequence Derivation", "[bar build gate — required]"} {
		if !strings.Contains(out, want) {
			t.Errorf("standard sequence show missing %q", want)
		}
	}
}

func TestSequenceListPlainStyleModeLines(t *testing.T) {
	t.Setenv(styleEnv, "")
	out, stderr, code := runCLI(t, []string{"sequence", "list"})
	if code != 0 {
		t.Fatalf("exit %d: %s", code, stderr)
	}
	if strings.Contains(out, "does not satisfy") || strings.Contains(out, "autonomous sequences contain no requires_user_input") {
		t.Errorf("plain list mode lines should use the plain text:\n%s", out)
	}
}

func dispatchBannedPhrases() []string {
	return []string{"[DISPATCH GATE]", "An evaluator", "pre-dispatch agent config gate", "[dispatch protocol — required]"}
}

func TestSequenceShowPlainDispatchKeepsFunctionalRules(t *testing.T) {
	t.Setenv(styleEnv, "")
	out, stderr, code := runCLI(t, []string{"sequence", "show", "token-rewrite"})
	if code != 0 {
		t.Fatalf("exit %d: %s", code, stderr)
	}
	for _, want := range []string{"[dispatch step]", "Dispatching N agents:", "## Agent Configuration", "subagent_type: general-purpose", "run_in_background: true", "## Derivation", "shoshin", "fan_out: ", "join: all"} {
		if want == "fan_out: " {
			want = "enumerate"
		}
		if !strings.Contains(out, want) {
			t.Errorf("plain dispatch output missing %q", want)
		}
	}
	for _, unwanted := range dispatchBannedPhrases() {
		if strings.Contains(out, unwanted) {
			t.Errorf("plain dispatch output should not contain %q", unwanted)
		}
	}
}

func TestSequenceShowStandardDispatchKeepsOriginal(t *testing.T) {
	out, _, code := runCLI(t, []string{"sequence", "show", "token-rewrite", "--style", "standard"})
	if code != 0 {
		t.Fatalf("exit %d", code)
	}
	for _, want := range []string{"[DISPATCH GATE]", "[dispatch protocol — required]"} {
		if !strings.Contains(out, want) {
			t.Errorf("standard dispatch output missing %q", want)
		}
	}
}

func TestSequenceShowPlainDuringDispatchRunsTheCommand(t *testing.T) {
	t.Setenv(styleEnv, "")
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
	if cmd == "" {
		t.Skip("frame-work has no during_dispatch step")
	}
	out, _, code := runCLI(t, []string{"sequence", "show", "frame-work"})
	if code != 0 || !strings.Contains(out, "run `"+cmd+"`") {
		t.Errorf("plain output should tell the agent to run the during_dispatch command %q (exit %d)", cmd, code)
	}
}

func TestSequenceShowPlainCycleUsesPlainWording(t *testing.T) {
	t.Setenv(styleEnv, "")
	out, _, code := runCLI(t, []string{"sequence", "show", "assay-cycle"})
	if code != 0 {
		t.Fatalf("exit %d", code)
	}
	if !strings.Contains(out, "[cycle] The steps below form one cycle") || strings.Contains(out, "[cycle protocol — required]") {
		t.Errorf("plain cycle block should use the plain wording")
	}
}

func TestHelpDispatchPlainStyle(t *testing.T) {
	t.Setenv(styleEnv, "")
	out, _, code := runCLI(t, []string{"help", "dispatch"})
	if code != 0 {
		t.Fatalf("exit %d", code)
	}
	for _, unwanted := range dispatchBannedPhrases() {
		if strings.Contains(out, unwanted) {
			t.Errorf("plain help dispatch should not contain %q", unwanted)
		}
	}
	if !strings.Contains(out, "## Agent Configuration") {
		t.Error("plain help dispatch should still describe the Agent Configuration block")
	}
}
