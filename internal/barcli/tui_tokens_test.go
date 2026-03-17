package barcli

import (
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/bartui2"
)

// TestBuildAxisOptionsPopulatesHeuristics specifies that buildAxisOptions includes
// heuristics for axis tokens from the embedded grammar.
func TestBuildAxisOptionsPopulatesHeuristics(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildAxisOptions(grammar, "scope")

	if len(options) == 0 {
		t.Fatal("expected scope options, got none")
	}

	var actOption *bartui2.TokenOption
	for i := range options {
		if options[i].Value == "act" {
			actOption = &options[i]
			break
		}
	}

	if actOption == nil {
		t.Fatal("expected to find 'act' token in scope options")
	}

	if actOption.Heuristics == "" {
		t.Errorf("expected Heuristics to be populated for scope:act, got empty string")
	}
}

// TestBuildPersonaOptionsPopulatesHeuristics specifies that buildPersonaOptions includes
// heuristics for persona axis tokens from the embedded grammar.
func TestBuildPersonaOptionsPopulatesHeuristics(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildPersonaOptions(grammar, "voice")

	if len(options) == 0 {
		t.Fatal("expected voice options, got none")
	}

	var designerOption *bartui2.TokenOption
	for i := range options {
		if options[i].Value == "as designer" {
			designerOption = &options[i]
			break
		}
	}

	if designerOption == nil {
		t.Fatalf("expected to find 'as designer' token in voice options, got: %v", options)
	}

	if designerOption.Heuristics == "" {
		t.Errorf("expected Heuristics to be populated for voice:as designer, got empty string")
	}
}

// TestBuildStaticCategoryPopulatesKanji specifies that buildStaticCategory includes
// kanji for task tokens (ADR-0143).
func TestBuildStaticCategoryPopulatesKanji(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	category, ok := buildStaticCategory(grammar)
	if !ok {
		t.Fatal("expected static category, got none")
	}

	var makeOption *bartui2.TokenOption
	for i := range category.Options {
		if category.Options[i].Value == "make" {
			makeOption = &category.Options[i]
			break
		}
	}

	if makeOption == nil {
		t.Fatal("expected to find 'make' task option")
	}

	if makeOption.Kanji == "" {
		t.Errorf("expected Kanji to be populated for task:make (ADR-0143), got empty string")
	}
}

// TestBuildPersonaOptionsPopulatesKanji specifies that buildPersonaOptions includes
// kanji for persona axis tokens (ADR-0143).
func TestBuildPersonaOptionsPopulatesKanji(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildPersonaOptions(grammar, "voice")

	var designerOption *bartui2.TokenOption
	for i := range options {
		if options[i].Value == "as designer" {
			designerOption = &options[i]
			break
		}
	}

	if designerOption == nil {
		t.Fatalf("expected to find 'as designer' token in voice options")
	}

	if designerOption.Kanji == "" {
		t.Errorf("expected Kanji to be populated for voice:as designer (ADR-0143), got empty string")
	}
}

// TestBuildPersonaOptionsUsesStructuredMetadata specifies that buildPersonaOptions
// populates Heuristics from PersonaMetadataFor heuristics and Distinctions from distinctions.
func TestBuildPersonaOptionsUsesStructuredMetadata(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildPersonaOptions(grammar, "voice")

	var designerOption *bartui2.TokenOption
	for i := range options {
		if options[i].Value == "as designer" {
			designerOption = &options[i]
			break
		}
	}
	if designerOption == nil {
		t.Fatal("expected to find 'as designer' token in voice options")
	}

	if !strings.Contains(designerOption.Heuristics, "designer") {
		t.Errorf("voice/as designer Heuristics must contain heuristic content; got: %q", designerOption.Heuristics)
	}
	if !strings.Contains(designerOption.Distinctions, "to designer") {
		t.Errorf("voice/as designer Distinctions must contain distinction 'to designer'; got: %q", designerOption.Distinctions)
	}
}

// TestMethodAxisGroupedBySemanticCategory specifies that buildAxisOptions for the
// method axis returns tokens grouped by SemanticGroup (ADR-0144).
func TestMethodAxisGroupedBySemanticCategory(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildAxisOptions(grammar, "method")
	if len(options) == 0 {
		t.Fatal("buildAxisOptions returned no options for method axis")
	}

	seen := map[string]bool{}
	lastGroup := ""
	for _, opt := range options {
		g := opt.SemanticGroup
		if g == "" {
			continue
		}
		if g != lastGroup {
			if seen[g] {
				t.Errorf("SemanticGroup %q appears non-contiguously — tokens are not grouped by category", g)
			}
			seen[g] = true
			lastGroup = g
		}
	}
}

// TestAxisCategoryOrderInGrammar specifies that grammar.Axes.CategoryOrder is populated
// from the JSON export (ADR-0144). This is the ground-rung test: it fails until grammar.go
// reads the new category_order field.
func TestAxisCategoryOrderInGrammar(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	order, ok := grammar.Axes.CategoryOrder["method"]
	if !ok || len(order) == 0 {
		t.Fatal("grammar.Axes.CategoryOrder[\"method\"] must be non-empty (wired from JSON category_order)")
	}
	// Conduct must be present (added in this ADR cycle)
	found := false
	for _, cat := range order {
		if cat == "Conduct" {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("grammar.Axes.CategoryOrder[\"method\"] must include \"Conduct\", got %v", order)
	}
}

// TestMethodAxisCanonicalCategoryOrder specifies that the canonical category order is preserved (ADR-0144).
// After wiring, canonicalOrder is derived from grammar — not hardcoded here.
func TestMethodAxisCanonicalCategoryOrder(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildAxisOptions(grammar, "method")

	canonicalOrder := grammar.Axes.CategoryOrder["method"]
	if len(canonicalOrder) == 0 {
		// Fallback for before grammar.go is wired — keeps test runnable
		canonicalOrder = []string{
			"Reasoning", "Exploration", "Structural", "Diagnostic",
			"Actor-centered", "Temporal/Dynamic", "Comparative", "Generative",
			"Conduct",
		}
	}
	orderIndex := map[string]int{}
	for i, cat := range canonicalOrder {
		orderIndex[cat] = i
	}

	lastIdx := -1
	lastGroup := ""
	for _, opt := range options {
		g := opt.SemanticGroup
		if g == "" || g == lastGroup {
			continue
		}
		idx, known := orderIndex[g]
		if !known {
			t.Logf("unknown category %q — skipping order check", g)
			lastGroup = g
			continue
		}
		if idx < lastIdx {
			t.Errorf("category %q (index %d) appears after %q (index %d) — wrong canonical order",
				g, idx, lastGroup, lastIdx)
		}
		lastIdx = idx
		lastGroup = g
	}
}

// TestBuildAxisOptionsPopulatesRoutingConceptForScopeToken specifies that buildAxisOptions
// includes RoutingConcept for scope tokens (ADR-0146).
func TestBuildAxisOptionsPopulatesRoutingConceptForScopeToken(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildAxisOptions(grammar, "scope")
	if len(options) == 0 {
		t.Fatal("expected scope options, got none")
	}

	var failOption *bartui2.TokenOption
	for i := range options {
		if options[i].Value == "fail" {
			failOption = &options[i]
			break
		}
	}
	if failOption == nil {
		t.Fatal("expected to find 'fail' token in scope options")
	}
	if failOption.RoutingConcept == "" {
		t.Errorf("expected RoutingConcept to be populated for scope:fail (ADR-0146), got empty string")
	}
	const want = "Failure modes"
	if failOption.RoutingConcept != want {
		t.Errorf("expected scope:fail RoutingConcept %q, got %q", want, failOption.RoutingConcept)
	}
}

// TestBuildAxisOptionsRoutingConceptForMethodToken specifies that buildAxisOptions
// populates RoutingConcept for method tokens (ADR-0146 Phase 3).
func TestBuildAxisOptionsRoutingConceptForMethodToken(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildAxisOptions(grammar, "method")
	if len(options) == 0 {
		t.Fatal("expected method options, got none")
	}

	var automateOption *bartui2.TokenOption
	for i := range options {
		if options[i].Value == "automate" {
			automateOption = &options[i]
			break
		}
	}
	if automateOption == nil {
		t.Fatal("expected to find 'automate' token in method options")
	}
	const want = "Automate repeatable steps"
	if automateOption.RoutingConcept != want {
		t.Errorf("expected RoutingConcept %q for method:automate (ADR-0146 Phase 3), got %q", want, automateOption.RoutingConcept)
	}
}

// TestBuildAxisOptionsSharedRoutingConceptPhrase specifies that tokens with the same
// routing concept are assigned identical phrases (ADR-0146).
func TestBuildAxisOptionsSharedRoutingConceptPhrase(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildAxisOptions(grammar, "scope")
	if len(options) == 0 {
		t.Fatal("expected scope options, got none")
	}

	concepts := make(map[string]string)
	for _, opt := range options {
		if opt.Value == "thing" || opt.Value == "struct" {
			concepts[opt.Value] = opt.RoutingConcept
		}
	}
	for _, token := range []string{"thing", "struct"} {
		if concepts[token] == "" {
			t.Errorf("expected RoutingConcept to be populated for scope:%s (ADR-0146), got empty", token)
		}
	}
	if concepts["thing"] != concepts["struct"] {
		t.Errorf("expected scope:thing and scope:struct to share RoutingConcept phrase, got thing=%q struct=%q",
			concepts["thing"], concepts["struct"])
	}
}

// TestBuildAxisOptionsUsesStructuredMetadata specifies that buildAxisOptions derives
// Heuristics from heuristics[] and Distinctions from distinctions (ADR-0155 T-11).
func TestBuildAxisOptionsUsesStructuredMetadata(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	options := buildAxisOptions(grammar, "completeness")
	var gistOpt *bartui2.TokenOption
	for i := range options {
		if options[i].Value == "gist" {
			gistOpt = &options[i]
			break
		}
	}
	if gistOpt == nil {
		t.Fatal("expected to find 'gist' token in completeness options")
	}
	if gistOpt.Heuristics == "" {
		t.Error("completeness/gist Heuristics must be populated from heuristics[] (ADR-0155 T-11)")
	}
	if gistOpt.Distinctions == "" {
		t.Error("completeness/gist Distinctions must be populated from distinctions (ADR-0155 T-11)")
	}
	if !strings.Contains(gistOpt.Heuristics, "brief") && !strings.Contains(gistOpt.Heuristics, "gist") && !strings.Contains(gistOpt.Heuristics, "summary") {
		t.Errorf("completeness/gist Heuristics must contain a trigger phrase, got %q", gistOpt.Heuristics)
	}
	if !strings.Contains(gistOpt.Distinctions, "skim") {
		t.Errorf("completeness/gist Distinctions must reference 'skim' distinction, got %q", gistOpt.Distinctions)
	}
}
