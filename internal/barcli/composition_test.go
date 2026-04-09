package barcli

import (
	"strings"
	"testing"
)

// ADR-0227: Composition injection tests.

func TestActiveCompositions_GroundGate(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"ground": {}, "gate": {}})
	if len(active) == 0 {
		t.Fatal("expected ground+gate to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "ground+gate" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'ground+gate', got %v", active)
	}
}

func TestActiveCompositions_GateAtomic(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"gate": {}, "atomic": {}})
	if len(active) == 0 {
		t.Fatal("expected gate+atomic to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "gate+atomic" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'gate+atomic', got %v", active)
	}
}

func TestActiveCompositions_GateChain(t *testing.T) {
	g := loadCompletionGrammar(t)
	active := g.ActiveCompositions(map[string]struct{}{"gate": {}, "chain": {}})
	if len(active) == 0 {
		t.Fatal("expected gate+chain to activate a composition")
	}
	found := false
	for _, c := range active {
		if c.Name == "gate+chain" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected composition named 'gate+chain', got %v", active)
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

// ADR-0227 token attribution audit — gate vocabulary tests.
// Gate must use gate-appropriate vocabulary, not borrow ground's "unilateral change" framing.

func TestGateDefinition_NoGroundVocabulary(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["gate"]
	if strings.Contains(def, "unilateral change to the task's intent") {
		t.Error("gate definition must not use ground vocabulary 'unilateral change to the task's intent'; use gate-appropriate phrasing instead")
	}
	if !strings.Contains(def, "structural scope violation") {
		t.Error("gate definition must contain 'structural scope violation' as the gate-appropriate replacement")
	}
}

func TestGateDefinition_NoDerivationVocabulary(t *testing.T) {
	g := loadCompletionGrammar(t)
	def := g.Axes.Definitions["method"]["gate"]
	if strings.Contains(def, "the derivation must identify a governing artifact per layer") {
		t.Error("gate definition must not use ground's 'derivation' vocabulary in the multi-layer clause; use assertion-appropriate phrasing instead")
	}
}
