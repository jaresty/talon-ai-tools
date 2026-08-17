package barcli

import (
	"strings"
	"testing"
)

// ADR-0227: Composition injection tests.

func TestActiveCompositions_GroundFalsify(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"ground": {}, "falsify": {}})
	if len(active) == 0 {
		t.Fatal("expected ground+falsify to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "ground+falsify" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'ground+falsify', got %v", active)
	}
}

func TestActiveCompositions_FalsifyChain(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"falsify": {}, "chain": {}})
	if len(active) == 0 {
		t.Fatal("expected falsify+chain to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "falsify+chain" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'falsify+chain', got %v", active)
	}
}

func TestActiveCompositions_ProbeFalsify(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"probe": {}, "falsify": {}})
	if len(active) == 0 {
		t.Fatal("expected probe+falsify to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "probe+falsify" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'probe+falsify', got %v", active)
	}
}

func TestActiveCompositions_SkimGate(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"skim": {}, "gate": {}})
	if len(active) == 0 {
		t.Fatal("expected skim+gate to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "skim+gate" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'skim+gate', got %v", active)
	}
}

func TestActiveCompositions_CalcChain(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"calc": {}, "chain": {}})
	if len(active) == 0 {
		t.Fatal("expected calc+chain to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "calc+chain" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'calc+chain', got %v", active)
	}
}

func TestActiveCompositions_SingleTokenNoActivation(t *testing.T) {
	g := loadCompletionGrammar(t)
	for _, tok := range []string{"gate", "ground", "atomic", "chain"} {
		active := g.ActiveCompositions(map[string]struct{}{tok: {}})
		if len(active) != 0 {
			t.Errorf("single token %q should not activate any composition, got %v", tok, active)
		}
	}
}

func TestRenderPlainText_CompositionRulesSectionPresent(t *testing.T) {
	g := loadCompletionGrammar(t)
	result, cliErr := Build(g, []string{"make", "falsify", "chain"})
	if cliErr != nil {
		t.Fatalf("Build: %v", cliErr)
	}
	rendered := RenderPlainText(result)
	if !strings.Contains(rendered, "=== COMPOSITION RULES") {
		t.Error("rendered output must contain COMPOSITION RULES section")
	}
	tokensIdx := strings.Index(rendered, "=== TOKENS")
	compositionIdx := strings.Index(rendered, "=== COMPOSITION RULES")
	formatIdx := strings.Index(rendered, "=== FORMAT")
	if compositionIdx <= tokensIdx {
		t.Error("COMPOSITION RULES must appear after TOKENS")
	}
	if compositionIdx >= formatIdx {
		t.Error("COMPOSITION RULES must appear before FORMAT")
	}
}

func TestRenderPlainText_NoCompositionRulesWithoutTokenPair(t *testing.T) {
	g := loadCompletionGrammar(t)
	result, cliErr := Build(g, []string{"make", "gate"})
	if cliErr != nil {
		t.Fatalf("Build: %v", cliErr)
	}
	rendered := RenderPlainText(result)
	if strings.Contains(rendered, "=== COMPOSITION RULES") {
		t.Error("gate alone must not produce COMPOSITION RULES section")
	}
}

// Token attribution audit — falsify vocabulary tests.
// falsify is the renamed 'gate' token: it governs falsifiable artifact quality.
// The new 'gate' token is the general hard-blocking checkpoint.

func TestFalsifyDefinition_ObservesGap(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["falsify"]
	if !strings.Contains(def, "gap between intent and current state") && !strings.Contains(def, "observes each gap") {
		t.Error("falsify definition must require observing each gap between intent and current state")
	}
}

func TestFalsifyDefinition_RegressionGuard(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["falsify"]
	if !strings.Contains(def, "detect regression without human initiation") {
		t.Error("falsify definition must require a mechanism that detects regression without human initiation")
	}
}

func TestFalsifyDefinition_ObservingGapSentinel(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["falsify"]
	if !strings.Contains(def, "Observing gap:") {
		t.Error("falsify definition must require the 'Observing gap:' sentinel to open the shrinking cycle")
	}
}

func TestGateDefinition_HardBlockingCheckpoint(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["gate"]
	if !strings.Contains(def, "hard-blocking checkpoint") {
		t.Error("gate definition must describe a hard-blocking checkpoint")
	}
	if !strings.Contains(def, "gate condition block") {
		t.Error("gate definition must require a gate condition block naming the specific string")
	}
	if !strings.Contains(def, "prior-executed result") {
		t.Error("gate definition must require a prior-executed result, not assertion")
	}
	if !strings.Contains(def, "does not qualify regardless of its content") {
		t.Error("gate definition must explicitly exclude non-qualifying results (reads/searches) from satisfying the condition")
	}
}

func TestChainDefinition_NoGateCycleClause(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["chain"]
	if strings.Contains(def, "including steps governed by a gate cycle") {
		t.Error("chain definition must not contain the gate-cycle clause — it belongs in gate+chain composition prose, not the chain definition")
	}
}

func TestAtomicDefinition_NoGranularitiesClause(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["atomic"]
	if strings.Contains(def, "these two granularities must match") {
		t.Error("atomic definition must not contain the granularities-match clause — it belongs in gate+atomic composition prose, not the atomic definition")
	}
}

// Cross-axis composition tests — compositions involving non-method tokens.
// These verify that ActiveCompositions matches against the full active token set,
// not only method tokens.

func TestActiveCompositions_PickIndirect(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"pick": {}, "indirect": {}})
	if len(active) == 0 {
		t.Fatal("expected pick+indirect to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "pick+indirect" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'pick+indirect', got %v", active)
	}
}

func TestActiveCompositions_ResetGood(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"reset": {}, "good": {}})
	if len(active) == 0 {
		t.Fatal("expected reset+good to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "reset+good" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'reset+good', got %v", active)
	}
}

// End-to-end: bar build pick indirect must inject COMPOSITION RULES section.
func TestBuildPickIndirectInjectsCompositionRules(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "pick", "indirect", "--subject", "x"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "COMPOSITION RULES") {
		t.Errorf("expected COMPOSITION RULES section for pick+indirect, got:\n%s", result.Stdout)
	}
}

// End-to-end: bar build probe falsify must inject COMPOSITION RULES section.
func TestBuildProbeFalsifyInjectsCompositionRules(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "probe", "falsify", "--subject", "x"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "COMPOSITION RULES") {
		t.Errorf("expected COMPOSITION RULES section for probe+falsify, got:\n%s", result.Stdout)
	}
}

// TestHelpComposition_KnownName verifies that bar help composition ground+falsify prints the composition prose.
func TestHelpComposition_KnownName(t *testing.T) {
	result := runBuildCLI(t, []string{"help", "composition", "ground+falsify"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "ground") {
		t.Errorf("expected composition prose containing 'ground', got:\n%s", result.Stdout)
	}
	if !strings.Contains(result.Stdout, "falsify") {
		t.Errorf("expected composition prose containing 'falsify', got:\n%s", result.Stdout)
	}
}

// TestHelpComposition_UnknownName verifies that bar help composition <unknown> exits non-zero with error.
func TestHelpComposition_UnknownName(t *testing.T) {
	result := runBuildCLI(t, []string{"help", "composition", "no-such-composition"}, nil)
	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit for unknown composition, got 0; stdout: %s", result.Stdout)
	}
	if !strings.Contains(result.Stderr, "no-such-composition") {
		t.Errorf("expected error mentioning unknown name, got stderr:\n%s", result.Stderr)
	}
}

// TestHelpComposition_NoArg verifies that bar help composition with no arg lists available names.
func TestHelpComposition_NoArg(t *testing.T) {
	result := runBuildCLI(t, []string{"help", "composition"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "ground+falsify") {
		t.Errorf("expected composition list to contain 'ground+falsify', got:\n%s", result.Stdout)
	}
}
