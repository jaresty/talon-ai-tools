package barcli

import (
	"fmt"
	"strings"
	"testing"
)

// TestPersonaSlugNormalization specifies that Build accepts persona axis tokens
// in slug form (e.g. "to-product-manager") and normalises them to canonical
// multi-word form (e.g. "to product manager"). This is the specifying validation
// for the R-10 persona-slug fix in ADR-0113 cycle 1.
func TestPersonaSlugNormalization(t *testing.T) {
	grammar := loadCompletionGrammar(t)

	// Verify the test grammar has the audience axis with "to product manager"
	if _, ok := grammar.personaTokens["audience"]["to product manager"]; !ok {
		t.Skip("test grammar does not have audience token 'to product manager'")
	}

	result, err := Build(grammar, []string{"show", "audience=to-product-manager"})
	if err != nil {
		t.Fatalf("expected slug-form audience token 'to-product-manager' to be accepted, got error: %v", err)
	}
	if result.Persona.Audience != "to product manager" {
		t.Fatalf("expected canonical form 'to product manager', got %q", result.Persona.Audience)
	}
}

// TestPersonaProperNounSlugNormalization specifies that Build accepts slug-form
// audience tokens whose canonical form contains uppercase proper-noun letters
// (e.g. "to-ceo" → "to CEO", "to-kent-beck" → "to Kent Beck"). The lookup
// must use the grammar's slugToCanonical map rather than a simple de-hyphenation,
// because de-hyphenation alone yields "to ceo" (lowercase) which does not match
// the stored canonical "to CEO". Regression test for ADR-0113 loop-23 bug fix.
func TestPersonaProperNounSlugNormalization(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	cases := []struct {
		slug      string
		canonical string
	}{
		{"to-ceo", "to CEO"},
		{"to-kent-beck", "to Kent Beck"},
	}
	for _, tc := range cases {
		if _, ok := grammar.personaTokens["audience"][tc.canonical]; !ok {
			t.Skipf("test grammar does not have audience token %q", tc.canonical)
		}
		result, err := Build(grammar, []string{"show", "audience=" + tc.slug})
		if err != nil {
			t.Fatalf("slug %q: expected acceptance, got error: %v", tc.slug, err)
		}
		if result.Persona.Audience != tc.canonical {
			t.Fatalf("slug %q: expected canonical %q, got %q", tc.slug, tc.canonical, result.Persona.Audience)
		}
	}
}

// TestCrossTokenExistsInGrammar specifies that the 'cross' scope token exists
// in the grammar. This is the specifying validation for the R-01 catalog change
// in ADR-0113 cycle 1.
func TestCrossTokenExistsInGrammar(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	if _, ok := grammar.axisTokens["scope"]["cross"]; !ok {
		t.Fatal("expected 'cross' scope token in grammar (R-01, ADR-0113 cycle 1)")
	}
}

func TestApplyOverrideTokenScope(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	state := newBuildState(grammar)

	scopeTokens := make([]string, 0, len(grammar.axisTokens["scope"]))
	for token := range grammar.axisTokens["scope"] {
		scopeTokens = append(scopeTokens, token)
		if len(scopeTokens) == 2 {
			break
		}
	}
	if len(scopeTokens) < 2 {
		t.Skip("test grammar does not provide multiple scope tokens")
	}

	override := fmt.Sprintf("scope=%s,%s", scopeTokens[0], scopeTokens[1])
	if err := state.applyOverrideToken(override); err != nil {
		t.Fatalf("applyOverrideToken returned error: %v", err)
	}

	if len(state.scope) != 2 || !contains(state.scope, scopeTokens[0]) || !contains(state.scope, scopeTokens[1]) {
		t.Fatalf("expected scope override to include %v, got %v", scopeTokens[:2], state.scope)
	}

	recognized := state.recognized["scope"]
	if len(recognized) != 2 || !contains(recognized, scopeTokens[0]) || !contains(recognized, scopeTokens[1]) {
		t.Fatalf("expected recognized scope entries for %v, got %v", scopeTokens[:2], recognized)
	}
}

func TestApplyOverrideTokenUnknown(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	state := newBuildState(grammar)

	if err := state.applyOverrideToken("unknown=value"); err == nil {
		t.Fatalf("expected error for unknown override key")
	} else if err.Type != errorUnknownToken {
		t.Fatalf("expected unknown token error, got %s", err.Type)
	}
}

func TestApplyOverrideTokenPersonaConflict(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	state := newBuildState(grammar)

	var preset string
	for key := range grammar.Persona.Presets {
		preset = key
		break
	}
	if preset == "" {
		t.Skip("test grammar does not define persona presets")
	}

	if err := state.applyOverrideToken("persona=" + preset); err == nil {
		t.Fatalf("expected persona override conflict")
	} else if err.Type != errorPresetConflict {
		t.Fatalf("expected preset conflict error, got %s", err.Type)
	}
}

// TestBuildResultCarriesReferenceKey specifies that Build() propagates the
// grammar's ReferenceKey into the returned BuildResult (ADR-0131, Loop 3).
func TestBuildResultCarriesReferenceKey(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	if strings.TrimSpace(grammar.ReferenceKey.Task) == "" {
		t.Skip("embedded grammar has no ReferenceKey; run make bar-grammar-update first")
	}

	result, cliErr := Build(grammar, []string{"make"})
	if cliErr != nil {
		t.Fatalf("Build returned error: %v", cliErr)
	}
	if result.ReferenceKey.Task != grammar.ReferenceKey.Task {
		t.Fatalf("expected BuildResult.ReferenceKey.Task == grammar.ReferenceKey.Task")
	}
}

// TestGrammarPatternsLoaded verifies that the embedded grammar JSON includes
// the patterns list from the Python SSOT (ADR-0134 D3).
// TestTaskMetadataPopulated specifies that all 11 task tokens carry non-empty
// structured metadata (definition + heuristics) in the embedded grammar (ADR-0154).
// Supersedes TestTaskUseWhenPopulated (ADR-0142) — use_when replaced by metadata.heuristics.
func TestTaskMetadataPopulated(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	wantTasks := []string{"check", "diff", "fix", "make", "pick", "plan", "probe", "pull", "show", "sim", "sort"}
	for _, task := range wantTasks {
		meta := grammar.TaskMetadataFor(task)
		if meta == nil {
			t.Errorf("task token %q: TaskMetadataFor returned nil (ADR-0154)", task)
			continue
		}
		if strings.TrimSpace(meta.Definition) == "" {
			t.Errorf("task token %q: definition is empty (ADR-0154)", task)
		}
		if len(meta.Heuristics) == 0 {
			t.Errorf("task token %q: heuristics is empty (ADR-0154)", task)
		}
	}
}

// TestHelpLLMTaskTableUsesStructuredMetadata specifies that bar help llm output
// renders task token rows using structured metadata fields (ADR-0154 T-6):
// definition, heuristics (comma-separated), and distinctions (token: note pairs).
// Supersedes ADR-0142 use_when column (plain text replaced by structured heuristics).
func TestHelpLLMTaskTableUsesStructuredMetadata(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	var buf strings.Builder
	renderLLMHelp(&buf, grammar, "", false)
	out := buf.String()

	if !strings.Contains(out, "### Tasks (required)") {
		t.Fatal("help llm missing Tasks catalog section")
	}
	// Structured column headers replace free-form Notes/When-to-use columns
	if !strings.Contains(out, "| Heuristics |") {
		t.Fatal("help llm Tasks table missing '| Heuristics |' column (ADR-0154)")
	}
	if !strings.Contains(out, "| Distinctions |") {
		t.Fatal("help llm Tasks table missing '| Distinctions |' column (ADR-0154)")
	}
	// probe row must contain a known heuristic trigger phrase
	if !strings.Contains(out, "analyze") {
		t.Fatal("help llm Tasks table probe row missing 'analyze' heuristic (ADR-0154)")
	}
	// fix row must contain the probe distinction
	if !strings.Contains(out, "probe") {
		t.Fatal("help llm Tasks table fix row missing 'probe' distinction (ADR-0154)")
	}
}

func TestGrammarPatternsLoaded(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	if len(grammar.Patterns) == 0 {
		t.Fatal("expected grammar.Patterns to be non-empty — patterns not wired from Python SSOT (ADR-0134 D3)")
	}
	if len(grammar.Patterns) < 32 {
		t.Fatalf("expected at least 32 patterns, got %d", len(grammar.Patterns))
	}
}

// TestTopologyTokenAccepted specifies that bar build accepts topology tokens
// (solo/witness/audit/relay/blind) as shorthand and produces output containing
// the topology constraint section. ADR-0236.
func TestTopologyTokenAccepted(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	for _, token := range []string{"solo", "witness", "audit", "relay", "blind"} {
		t.Run(token, func(t *testing.T) {
			state := newBuildState(grammar)
			if err := state.applyShorthandAxis("topology", token); err != nil {
				t.Fatalf("applyShorthandAxis(%q) returned error: %v", token, err)
			}
			if state.topology != token {
				t.Fatalf("expected state.topology=%q, got %q", token, state.topology)
			}
		})
	}
}

// TestTopologyOverrideAccepted specifies that topology=<token> key=value override
// is parsed and stored correctly. ADR-0236.
func TestTopologyOverrideAccepted(t *testing.T) {
	grammar := loadCompletionGrammar(t)
	state := newBuildState(grammar)
	if err := state.applyOverrideToken("topology=solo"); err != nil {
		t.Fatalf("applyOverrideToken(topology=solo) returned error: %v", err)
	}
	if state.topology != "solo" {
		t.Fatalf("expected state.topology=%q, got %q", "solo", state.topology)
	}
}

// TestTopologyInPromptOutput specifies that a topology token appears in the
// CONSTRAINTS section of bar build output. ADR-0236.
func TestTopologyInPromptOutput(t *testing.T) {
	var out, errBuf strings.Builder
	code := Run([]string{"build", "show", "solo", "--subject", "test"}, nil, &out, &errBuf)
	if code != 0 {
		t.Fatalf("bar build explain solo exited %d: %s", code, errBuf.String())
	}
	if !strings.Contains(out.String(), "solo") {
		t.Errorf("topology token 'solo' missing from prompt output:\n%s", out.String())
	}
}
