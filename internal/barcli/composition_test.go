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

func TestActiveCompositions_FalsifyAtomic(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"falsify": {}, "atomic": {}})
	if len(active) == 0 {
		t.Fatal("expected falsify+atomic to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "falsify+atomic" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'falsify+atomic', got %v", active)
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

func TestActiveCompositions_GateFalsify(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"gate": {}, "falsify": {}})
	if len(active) == 0 {
		t.Fatal("expected gate+falsify to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "gate+falsify" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'gate+falsify', got %v", active)
	}
}

func TestActiveCompositions_AtomicGround(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"atomic": {}, "ground": {}})
	if len(active) == 0 {
		t.Fatal("expected atomic+ground to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "atomic+ground" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'atomic+ground', got %v", active)
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
	result, cliErr := Build(g, []string{"make", "ground", "gate", "atomic", "chain"})
	if cliErr != nil {
		t.Fatalf("Build: %v", cliErr)
	}
	rendered := RenderPlainText(result)
	if !strings.Contains(rendered, "=== COMPOSITION RULES") {
		t.Error("rendered output must contain COMPOSITION RULES section")
	}
	constraintsIdx := strings.Index(rendered, "=== CONSTRAINTS")
	compositionIdx := strings.Index(rendered, "=== COMPOSITION RULES")
	personaIdx := strings.Index(rendered, "=== PERSONA")
	if compositionIdx <= constraintsIdx {
		t.Error("COMPOSITION RULES must appear after CONSTRAINTS")
	}
	if compositionIdx >= personaIdx {
		t.Error("COMPOSITION RULES must appear before PERSONA")
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

func TestFalsifyDefinition_AbsenceDetection(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["falsify"]
	if !strings.Contains(def, "written to assert that specific behavior") && !strings.Contains(def, "behavior is absent") && !strings.Contains(def, "behavior absent") && !strings.Contains(def, "detected absence of the behavior") && !strings.Contains(def, "absence of each governed behavior") {
		t.Error("falsify definition must require artifact to be written to assert the specific governed behavior")
	}
}

func TestFalsifyDefinition_FiredBeforeImplementation(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["falsify"]
	if !strings.Contains(def, "before any tool call that modifies") && !strings.Contains(def, "before any edit tool call") && !strings.Contains(def, "FAIL tool result already present") && !strings.Contains(def, "before any implementation") {
		t.Error("falsify definition must require FAIL result to precede any tool call that modifies a governed file")
	}
}

func TestFalsifyDefinition_ImplementationStepConstraint(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["falsify"]
	if !strings.Contains(def, "result block immediately following") {
		t.Error("falsify implementation step constraint must be stated as a transcript-observable post-step check: result block immediately following the tool call")
	}
	if !strings.Contains(def, "zero occurrences of") {
		t.Error("falsify implementation step constraint must require a tool-executed search showing zero occurrences before removing a definition")
	}
	if !strings.Contains(def, "call-site positions") {
		t.Error("falsify implementation step constraint must name 'call-site positions' as the search scope")
	}
}

func TestGateDefinition_HardBlockingCheckpoint(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["gate"]
	if !strings.Contains(def, "hard-blocking checkpoint") {
		t.Error("gate definition must describe a hard-blocking checkpoint")
	}
	if !strings.Contains(def, "prior-executed result") {
		t.Error("gate definition must require a prior-executed result, not assertion")
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
