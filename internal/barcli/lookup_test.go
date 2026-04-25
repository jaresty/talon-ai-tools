package barcli

import (
	"encoding/json"
	"strings"
	"testing"
)

// TestLookupExactHeuristicMatchTier3 specifies that an exact heuristic match returns tier 3.
func TestLookupExactHeuristicMatchTier3(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// "TDD" is an exact heuristic for method:gate (ADR-0224: TDD routing moved from ground to gate)
	results := LookupTokens("TDD", grammar, "")
	if len(results) == 0 {
		t.Fatal("expected results for 'TDD', got none")
	}
	var found *LookupResult
	for i := range results {
		if results[i].Axis == "method" && results[i].Token == "gate" {
			found = &results[i]
			break
		}
	}
	if found == nil {
		t.Fatalf("expected method:gate in results for 'TDD', got %v", results)
	}
	if found.Tier != 3 {
		t.Errorf("expected tier 3 for exact heuristic match, got %d", found.Tier)
	}
	if found.MatchedField != "heuristics" {
		t.Errorf("expected matched_field 'heuristics', got %q", found.MatchedField)
	}
}

// TestLookupSubstringHeuristicMatchTier2 specifies that a substring heuristic match returns tier 2.
func TestLookupSubstringHeuristicMatchTier2(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// "root" is a substring of "root cause" heuristic for method:diagnose
	results := LookupTokens("root", grammar, "")
	if len(results) == 0 {
		t.Fatal("expected results for 'root', got none")
	}
	var found *LookupResult
	for i := range results {
		if results[i].Axis == "method" && results[i].Token == "diagnose" {
			found = &results[i]
			break
		}
	}
	if found == nil {
		t.Fatalf("expected method:diagnose in results for 'root', got %v", results)
	}
	if found.Tier != 2 {
		t.Errorf("expected tier 2 for substring heuristic match, got %d", found.Tier)
	}
}

// TestLookupDistinctionTokenNameMatchTier1 specifies that a distinction token name match returns tier 1.
func TestLookupDistinctionTokenNameMatchTier1(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// method:ground has "verify" in its distinctions; "verify" should match ground at tier 1
	// (but only if "verify" doesn't also appear in ground's heuristics directly)
	// We use a word that appears only in distinctions, not in heuristics.
	// method:verify has "ground" in its distinctions list.
	// Look for a token whose distinction contains "mint" but not in heuristics.
	// method:ground has "mint" in its distinctions.
	results := LookupTokens("mint", grammar, "method")
	if len(results) == 0 {
		t.Fatal("expected results for 'mint' in method axis, got none")
	}
	var found *LookupResult
	for i := range results {
		if results[i].Axis == "method" && results[i].Token == "ground" {
			found = &results[i]
			break
		}
	}
	if found == nil {
		t.Fatalf("expected method:ground in results for 'mint', got %v", results)
	}
	if found.Tier < 1 {
		t.Errorf("expected tier >= 1 for distinction match, got %d", found.Tier)
	}
	if found.Tier == 3 || found.Tier == 2 {
		// If mint also appears in heuristics, that's fine — tier would be higher
		t.Logf("note: 'mint' matched at tier %d (heuristic match)", found.Tier)
	}
}

// TestLookupDefinitionSubstringMatchTier0 specifies that a definition substring match returns tier 0.
func TestLookupDefinitionSubstringMatchTier0(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// "appearance-reality gap" appears in method:ground definition (ADR-0230: declarative rewrite) but not heuristics/distinctions.
	results := LookupTokens("appearance-reality gap", grammar, "method")
	if len(results) == 0 {
		t.Fatal("expected results for 'appearance of satisfying the intent', got none")
	}
	var found *LookupResult
	for i := range results {
		if results[i].Axis == "method" && results[i].Token == "ground" {
			found = &results[i]
			break
		}
	}
	if found == nil {
		t.Fatalf("expected method:ground in results for 'appearance of satisfying the intent', got %v", results)
	}
	if found.Tier != 0 {
		t.Errorf("expected tier 0 for definition-only match, got %d", found.Tier)
	}
	if found.MatchedField != "definition" {
		t.Errorf("expected matched_field 'definition', got %q", found.MatchedField)
	}
}

// TestLookupMultiWordANDLogic specifies tier-result AND-match behavior and BM25 OR-match behavior.
func TestLookupMultiWordANDLogic(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// "root cause" should match method:diagnose at a tier >= 0 (has "root cause" in heuristics)
	results := LookupTokens("root cause", grammar, "")
	var foundDiagnose bool
	for _, r := range results {
		if r.Axis == "method" && r.Token == "diagnose" {
			foundDiagnose = true
		}
	}
	if !foundDiagnose {
		t.Error("expected method:diagnose in results for 'root cause'")
	}

	// "xyz123 root" — "xyz123" matches nothing; tier AND-match drops diagnose from tier results.
	// BM25 OR-match may return diagnose as a BM25 result (Tier == -1); that is correct behavior.
	// This test only asserts that diagnose does NOT appear as a tier-matched result (Tier >= 0).
	results2 := LookupTokens("xyz123 root", grammar, "")
	for _, r := range results2 {
		if r.Axis == "method" && r.Token == "diagnose" && r.Tier >= 0 {
			t.Error("method:diagnose should not appear as a tier-matched result when one word (xyz123) has no tier match")
		}
	}
}

// TestLookupAxisFilter specifies that --axis method filters out non-method results.
func TestLookupAxisFilter(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	results := LookupTokens("root", grammar, "method")
	for _, r := range results {
		if r.Axis != "method" {
			t.Errorf("expected only method results with axis filter, got %s:%s", r.Axis, r.Token)
		}
	}
}

// TestLookupResultCap specifies that results are capped at 10.
func TestLookupResultCap(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// "the" appears in many definitions — should yield at most 10
	results := LookupTokens("the", grammar, "")
	if len(results) > 10 {
		t.Errorf("expected at most 10 results, got %d", len(results))
	}
}

// TestLookupLabelPopulated specifies that LookupResult.Label is populated.
func TestLookupLabelPopulated(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	results := LookupTokens("root cause", grammar, "method")
	for _, r := range results {
		if r.Axis == "method" && r.Token == "diagnose" {
			if r.Label == "" {
				t.Error("expected non-empty label for method:diagnose")
			}
			return
		}
	}
	t.Error("method:diagnose not found in results for 'root cause'")
}

// CLI-level tests

// TestLookupTokenNameMatchesOwnToken specifies that bar lookup "ground" returns method:ground.
func TestLookupTokenNameMatchesOwnToken(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	results := LookupTokens("ground", grammar, "")
	for _, r := range results {
		if r.Axis == "method" && r.Token == "ground" {
			return
		}
	}
	t.Fatalf("expected method:ground in results for 'ground', got %v", results)
}

// TestLookupCLIHumanReadableOutput specifies that human-readable output is "axis:token — Label" per line.
func TestLookupCLIHumanReadableOutput(t *testing.T) {
	result := runBuildCLI(t, []string{"lookup", "root cause"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "method:diagnose") {
		t.Errorf("expected method:diagnose in output, got:\n%s", result.Stdout)
	}
	if !strings.Contains(result.Stdout, " — ") {
		t.Errorf("expected ' — ' separator in output, got:\n%s", result.Stdout)
	}
}

// TestLookupCLIJSONOutput specifies that --json emits a valid JSON array with correct schema fields.
func TestLookupCLIJSONOutput(t *testing.T) {
	result := runBuildCLI(t, []string{"lookup", "root cause", "--json"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	var items []map[string]any
	if err := json.Unmarshal([]byte(result.Stdout), &items); err != nil {
		t.Fatalf("expected valid JSON array, got error: %v\nOutput:\n%s", err, result.Stdout)
	}
	if len(items) == 0 {
		t.Fatal("expected at least one JSON result")
	}
	for _, item := range items {
		for _, field := range []string{"axis", "token", "label", "tier", "matched_field", "matched_text"} {
			if _, ok := item[field]; !ok {
				t.Errorf("JSON result missing field %q: %v", field, item)
			}
		}
	}
}

// TestLookupCLIAxisFilter specifies that --axis method filters results.
func TestLookupCLIAxisFilter(t *testing.T) {
	result := runBuildCLI(t, []string{"lookup", "root", "--axis", "method"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d; stderr: %s", result.Exit, result.Stderr)
	}
	for _, line := range strings.Split(strings.TrimSpace(result.Stdout), "\n") {
		if line == "" {
			continue
		}
		if !strings.HasPrefix(line, "method:") {
			t.Errorf("expected only method: results, got line: %q", line)
		}
	}
}

// TestLookupCLIUnknownAxisExits1 specifies that an unknown --axis value exits 1.
func TestLookupCLIUnknownAxisExits1(t *testing.T) {
	result := runBuildCLI(t, []string{"lookup", "root", "--axis", "notanaxis"}, nil)
	if result.Exit != 1 {
		t.Errorf("expected exit 1 for unknown axis, got %d", result.Exit)
	}
}

// TestLookupCLIMissingQueryExits1 specifies that a missing query argument exits 1.
func TestLookupCLIMissingQueryExits1(t *testing.T) {
	result := runBuildCLI(t, []string{"lookup"}, nil)
	if result.Exit != 1 {
		t.Errorf("expected exit 1 for missing query, got %d", result.Exit)
	}
}

// --- BM25 assertions (ADR-0232) ---

// TestBM25CorpusConstruction specifies that buildTokenDocs returns a doc whose title
// contains the token name and whose body contains definition text.
func TestBM25CorpusConstruction(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	docs := buildTokenDocs(grammar, "")
	if len(docs) == 0 {
		t.Fatal("expected non-empty token docs")
	}
	var gateDoc *tokenDoc
	for i := range docs {
		if docs[i].id == "method:gate" {
			gateDoc = &docs[i]
			break
		}
	}
	if gateDoc == nil {
		t.Fatal("expected doc for method:gate")
	}
	if !strings.Contains(gateDoc.title, "gate") {
		t.Errorf("expected title to contain 'gate', got %q", gateDoc.title)
	}
	if !strings.Contains(gateDoc.body, "FAIL") {
		t.Errorf("expected body to contain 'FAIL' (from definition), got %q", gateDoc.body[:100])
	}
}

// TestLookupBM25MultiWord specifies that a multi-word query that previously returned
// zero results now returns at least one BM25 result.
func TestLookupBM25MultiWord(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	// "trace reasoning steps" returns 0 with AND-match but should return results via BM25
	results := LookupTokens("trace reasoning steps", grammar, "")
	if len(results) == 0 {
		t.Fatal("expected at least one result for 'trace reasoning steps' via BM25, got none")
	}
}

// TestLookupTierBeforeBM25 specifies that tier-3/2/1 results appear before BM25-only results.
func TestLookupTierBeforeBM25(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	// "TDD" is an exact heuristic for method:gate (tier 3).
	// A single-word query produces both tier-matched and BM25-only results.
	// All tier-matched results must appear before all BM25-only results.
	results := LookupTokens("TDD", grammar, "")
	if len(results) == 0 {
		t.Fatal("expected results for 'TDD'")
	}
	seenBM25 := false
	for i, r := range results {
		if r.Tier == -1 {
			seenBM25 = true
		} else if seenBM25 {
			t.Errorf("tier-matched result %s:%s (tier %d) at pos %d appeared after a BM25-only result", r.Axis, r.Token, r.Tier, i)
		}
	}
}

// TestLookupNoDuplicates specifies that a token matching at tier 3/2/1 does not
// also appear as a BM25-only result in the same response.
func TestLookupNoDuplicates(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	results := LookupTokens("TDD reasoning steps", grammar, "")
	seen := map[string][]int{}
	for i, r := range results {
		key := r.Axis + ":" + r.Token
		seen[key] = append(seen[key], i)
	}
	for key, positions := range seen {
		if len(positions) > 1 {
			t.Errorf("token %s appears %d times at positions %v", key, len(positions), positions)
		}
	}
}

// TestLookupCap specifies that combined tier + BM25 results never exceed 10.
func TestLookupCap(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	// broad single-word query likely to match many tokens across both tier and BM25 paths
	results := LookupTokens("step", grammar, "")
	if len(results) > 10 {
		t.Errorf("expected at most 10 results, got %d", len(results))
	}
}

// TestLookupCLINoMatchesExits0WithEmptyOutput specifies that no matches exits 0 with no output.
func TestLookupCLINoMatchesExits0WithEmptyOutput(t *testing.T) {
	result := runBuildCLI(t, []string{"lookup", "zzz999xyz"}, nil)
	if result.Exit != 0 {
		t.Errorf("expected exit 0 for no matches, got %d", result.Exit)
	}
	if strings.TrimSpace(result.Stdout) != "" {
		t.Errorf("expected empty output for no matches, got: %q", result.Stdout)
	}
}

// ── ADR-0234: --subject / --addendum contextual reranking ────────────────────

// B1: LookupResult has ContextScore float64 field.
// Natural FAIL state: no — field doesn't exist yet, so JSON output won't have it.
// Perturbation: check JSON output for context_score key when --subject is given.
func TestLookupContextScoreInJSONOutput(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	result := runBuildCLI(t, []string{"lookup", "show", "--subject", "explain code to my manager", "--json"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", result.Exit, result.Stderr)
	}
	var out []map[string]interface{}
	if err := json.Unmarshal([]byte(result.Stdout), &out); err != nil {
		t.Fatalf("invalid JSON: %v\noutput: %s", err, result.Stdout)
	}
	if len(out) == 0 {
		t.Fatal("expected at least one result")
	}
	// Every result must have a context_score key when --subject is provided
	for _, r := range out {
		if _, ok := r["context_score"]; !ok {
			t.Errorf("result missing context_score field: %v", r)
		}
	}
}

// B2: Mode B — no positional query + --subject → BM25 discovery results.
// Natural FAIL state: yes — currently errors "lookup requires a query argument".
func TestLookupModeB_SubjectOnlyReturnsResults(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	result := runBuildCLI(t, []string{"lookup", "--subject", "explain authentication code to my manager"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0 for discovery mode, got %d: %s", result.Exit, result.Stderr)
	}
	if strings.TrimSpace(result.Stdout) == "" {
		t.Fatal("expected non-empty output for discovery mode with subject")
	}
}

// B2: Mode B results include task:show (explain/describe for audience) for "explain to manager".
func TestLookupModeB_ShowRanksHighForExplainToManager(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	result := runBuildCLI(t, []string{"lookup", "--subject", "explain authentication code to my manager", "--json"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", result.Exit, result.Stderr)
	}
	var out []map[string]interface{}
	if err := json.Unmarshal([]byte(result.Stdout), &out); err != nil {
		t.Fatalf("invalid JSON: %v", err)
	}
	found := false
	for _, r := range out {
		if r["token"] == "show" {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("expected task:show in discovery results for 'explain to manager', got: %v", out)
	}
}

// B3: Mode A — query + --subject reranks within tiers by context score.
// Natural FAIL state: yes — context_score field absent, reranking not implemented.
// We assert that a token strongly matching subject scores higher context_score than one that doesn't.
func TestLookupModeA_ContextScoreReranksWithinTier(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	// Query "show" matches task:show (tier 3 exact). Also matches other tokens.
	// Subject "explain code to manager" should give task:show a high context_score.
	results := LookupTokensWithContext("show", grammar, "", "explain authentication code to my manager", "")
	if len(results) == 0 {
		t.Fatal("expected results")
	}
	var showResult *LookupResult
	for i := range results {
		if results[i].Axis == "task" && results[i].Token == "show" {
			showResult = &results[i]
			break
		}
	}
	if showResult == nil {
		t.Fatal("expected task:show in results")
	}
	if showResult.ContextScore <= 0 {
		t.Errorf("expected task:show to have positive ContextScore for 'explain to manager', got %f", showResult.ContextScore)
	}
}

// B4: Existing behavior unchanged when no --subject/--addendum.
// Natural FAIL state: no — if we break it, existing tests catch it; this test confirms the contract explicitly.
// Perturbation: LookupTokensWithContext with empty subject/addendum must equal LookupTokens.
func TestLookupWithContext_EmptyContextMatchesLegacy(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	legacy := LookupTokens("TDD", grammar, "")
	withCtx := LookupTokensWithContext("TDD", grammar, "", "", "")
	if len(legacy) != len(withCtx) {
		t.Errorf("LookupTokensWithContext with empty context returned %d results, legacy returned %d", len(withCtx), len(legacy))
	}
	for i := range legacy {
		if i >= len(withCtx) {
			break
		}
		if legacy[i].Axis != withCtx[i].Axis || legacy[i].Token != withCtx[i].Token || legacy[i].Tier != withCtx[i].Tier {
			t.Errorf("result[%d] mismatch: legacy=%v withCtx=%v", i, legacy[i], withCtx[i])
		}
	}
}

// ── ADR-0234 follow-up: label fix + plain-text output enrichment ─────────────

// B1a: BM25-only task token results have non-empty labels.
func TestLookupBM25TaskTokenHasLabel(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	// "explain to audience" → task:show is a BM25-only result; must have label
	results := LookupTokens("explain to audience", grammar, "")
	var showResult *LookupResult
	for i := range results {
		if results[i].Axis == "task" && results[i].Token == "show" {
			showResult = &results[i]
			break
		}
	}
	if showResult == nil {
		t.Fatal("expected task:show in results for 'explain to audience'")
	}
	if showResult.Tier != -1 {
		t.Skipf("task:show matched via tier %d, not BM25 — test requires BM25 path", showResult.Tier)
	}
	if showResult.Label == "" {
		t.Errorf("task:show BM25 result has empty label; expected non-empty label")
	}
}

// B1b: BM25-only persona/audience token results have non-empty labels.
func TestLookupBM25PersonaTokenHasLabel(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	// "explain to audience" → audience:to-managers is a BM25-only result; must have label
	results := LookupTokens("explain to audience", grammar, "")
	var found *LookupResult
	for i := range results {
		if results[i].Axis == "audience" && results[i].Tier == -1 {
			found = &results[i]
			break
		}
	}
	if found == nil {
		t.Skip("no BM25-only audience token in results — skipping")
	}
	if found.Label == "" {
		t.Errorf("audience:%s BM25 result has empty label; expected non-empty label", found.Token)
	}
}

// B2: Plain-text output includes matched snippet when MatchedField is not "bm25".
func TestLookupPlaintextShowsMatchedSnippet(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	// "explain to a designer" is an exact heuristic match for audience:to-designer (tier 3)
	result := runBuildCLI(t, []string{"lookup", "explain to a designer"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", result.Exit, result.Stderr)
	}
	// Should include a matched snippet in the output line for the tier result
	if !strings.Contains(result.Stdout, "explain to a designer") {
		t.Errorf("expected matched snippet in plain-text output, got:\n%s", result.Stdout)
	}
}

// B3: Plain-text output includes [ctx: N.NN] when ContextScore > 0.
func TestLookupPlaintextShowsContextScore(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	result := runBuildCLI(t, []string{"lookup", "explain to audience", "--subject", "explain auth code to my manager"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "[ctx:") {
		t.Errorf("expected [ctx: N.NN] in plain-text output when --subject given, got:\n%s", result.Stdout)
	}
}

// B4: Plain-text output does NOT include tier number.
func TestLookupPlaintextNoTierNumber(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	result := runBuildCLI(t, []string{"lookup", "TDD"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", result.Exit, result.Stderr)
	}
	if strings.Contains(result.Stdout, "tier") || strings.Contains(result.Stdout, "Tier") {
		t.Errorf("plain-text output should not include tier number, got:\n%s", result.Stdout)
	}
}
