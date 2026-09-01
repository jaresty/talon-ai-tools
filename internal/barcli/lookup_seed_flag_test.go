package barcli

import (
	"bytes"
	"os"
	"strings"
	"testing"
)

func lookupHasFlag(results []LookupResult) *LookupResult {
	for i := range results {
		if results[i].Kind == "flag" {
			return &results[i]
		}
	}
	return nil
}

// TestLookupSurfacesSeedWordsFlagOnCreativeIntent covers Ground P1a + P1b: a
// creative-intent query yields a Kind=flag result whose Command names --seed-words.
func TestLookupSurfacesSeedWordsFlagOnCreativeIntent(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	for _, q := range []string{"brainstorm", "ideate", "unstuck fresh angle", "lateral creative"} {
		results := LookupTokens(q, grammar, "")
		flag := lookupHasFlag(results)
		if flag == nil {
			t.Fatalf("expected a kind=flag result for creative query %q, got none", q)
		}
		if !strings.Contains(flag.Command, "--seed-words") {
			t.Fatalf("flag result for %q must have --seed-words in Command, got %q", q, flag.Command)
		}
	}
}

// TestLookupNoSeedWordsFlagOnTechnicalIntent covers Ground P2: a clearly
// non-creative technical query does not surface the seed flag.
func TestLookupNoSeedWordsFlagOnTechnicalIntent(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	for _, q := range []string{"fix the null pointer crash", "root cause of failing test"} {
		results := LookupTokens(q, grammar, "")
		if flag := lookupHasFlag(results); flag != nil {
			t.Fatalf("did not expect a kind=flag result for technical query %q, got %+v", q, *flag)
		}
	}
}

// TestLookupSeedWordsFlagSuppressedByAxisFilter covers P3-support: an axis filter
// (e.g. method) scopes to real axis tokens and must not inject the flag.
func TestLookupSeedWordsFlagSuppressedByAxisFilter(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	results := LookupTokens("brainstorm", grammar, "method")
	if flag := lookupHasFlag(results); flag != nil {
		t.Fatalf("axis-filtered lookup must not surface the flag, got %+v", *flag)
	}
}

// TestLookupFlagRendersCommandInText covers Ground P1b at the CLI surface: the
// text renderer must show the runnable --seed-words command inline, not only in JSON.
func TestLookupFlagRendersCommandInText(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	if exit := Run([]string{"lookup", "brainstorm"}, os.Stdin, stdout, stderr); exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, stderr.String())
	}
	out := stdout.String()
	if !strings.Contains(out, "flag:seed-words") {
		t.Fatalf("expected flag:seed-words in lookup text output, got:\n%s", out)
	}
	// The runnable command must render as its own inline command form (→ bar build
	// ... --seed-words), not merely be mentioned inside the label text.
	if !strings.Contains(out, "→ "+lateralSeedFlagCommand) {
		t.Fatalf("expected runnable command %q rendered inline (→ ...), got:\n%s", lateralSeedFlagCommand, out)
	}
}

// TestLookupTokenResultsUnaffectedByFlag covers Ground P3: adding the flag does
// not displace an established token result for the same query.
func TestLookupTokenResultsUnaffectedByFlag(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	// "TDD" is an exact heuristic for method:falsify — must still be present.
	results := LookupTokens("TDD", grammar, "")
	found := false
	for _, r := range results {
		if r.Axis == "method" && r.Token == "falsify" {
			found = true
			break
		}
	}
	if !found {
		t.Fatalf("method:falsify must still surface for 'TDD' after adding the flag kind")
	}
}
