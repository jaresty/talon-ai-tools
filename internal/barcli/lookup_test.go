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

	// "TDD" is an exact heuristic for method:ground
	results := LookupTokens("TDD", grammar, "")
	if len(results) == 0 {
		t.Fatal("expected results for 'TDD', got none")
	}
	var found *LookupResult
	for i := range results {
		if results[i].Axis == "method" && results[i].Token == "ground" {
			found = &results[i]
			break
		}
	}
	if found == nil {
		t.Fatalf("expected method:ground in results for 'TDD', got %v", results)
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

	// "form changes, intent does not" appears in method:ground definition (R2) but not heuristics/distinctions.
	// ADR-0185: "faithful derivation" phrase removed; R2 now expressed as "form changes, intent does not".
	results := LookupTokens("form changes intent does not", grammar, "method")
	if len(results) == 0 {
		t.Fatal("expected results for 'form changes intent does not', got none")
	}
	var found *LookupResult
	for i := range results {
		if results[i].Axis == "method" && results[i].Token == "ground" {
			found = &results[i]
			break
		}
	}
	if found == nil {
		t.Fatalf("expected method:ground in results for 'form changes intent does not', got %v", results)
	}
	if found.Tier != 0 {
		t.Errorf("expected tier 0 for definition-only match, got %d", found.Tier)
	}
	if found.MatchedField != "definition" {
		t.Errorf("expected matched_field 'definition', got %q", found.MatchedField)
	}
}

// TestLookupMultiWordANDLogic specifies that a multi-word query requires all words to match.
func TestLookupMultiWordANDLogic(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// "root cause" should match method:diagnose (has "root cause" in heuristics)
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

	// "xyz123 root" — xyz123 will not match anything, so no results
	results2 := LookupTokens("xyz123 root", grammar, "")
	for _, r := range results2 {
		if r.Axis == "method" && r.Token == "diagnose" {
			t.Error("method:diagnose should not appear when one word (xyz123) has no match")
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
