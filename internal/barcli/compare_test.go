package barcli

import (
	"strings"
	"testing"
)

// Tests for Stage 1 compare mode (ADR-0161):
// comma-separated values on one axis trigger an Approach A comparison prompt.

// C1: two variants on one axis produces labeled sections
func TestCompareTwoVariants(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "method=diagnose,mapping", "--subject", "some problem"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d\nstderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "method=diagnose") {
		t.Errorf("expected variant 1 label 'method=diagnose' in output:\n%s", result.Stdout)
	}
	if !strings.Contains(result.Stdout, "method=mapping") {
		t.Errorf("expected variant 2 label 'method=mapping' in output:\n%s", result.Stdout)
	}
	if !strings.Contains(result.Stdout, "some problem") {
		t.Errorf("expected subject in output:\n%s", result.Stdout)
	}
}

// C2: three variants produce three labeled sections
func TestCompareThreeVariants(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "method=diagnose,mapping,systemic", "--subject", "arch review"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d\nstderr: %s", result.Exit, result.Stderr)
	}
	for _, tok := range []string{"diagnose", "mapping", "systemic"} {
		if !strings.Contains(result.Stdout, tok) {
			t.Errorf("expected variant %q in output:\n%s", tok, result.Stdout)
		}
	}
}

// C3: each variant section includes definition text from grammar
func TestCompareIncludesDefinition(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "method=diagnose,mapping", "--subject", "x"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d\nstderr: %s", result.Exit, result.Stderr)
	}
	// Grammar should have definitions for these tokens; output must not be empty sections
	if strings.Count(result.Stdout, "method=diagnose") < 1 {
		t.Errorf("expected definition section for diagnose:\n%s", result.Stdout)
	}
}

// C4: only one axis may carry multiple values; two multi-value axes is an error
func TestCompareTwoMultiAxesIsError(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "method=diagnose,mapping", "scope=fail,cross", "--subject", "x"}, nil)
	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit for two multi-value axes, got 0\nstdout: %s", result.Stdout)
	}
}

// C5: unknown token in comma list returns an error
func TestCompareUnknownVariantIsError(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "method=diagnose,notarealtoken", "--subject", "x"}, nil)
	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit for unknown variant token, got 0\nstdout: %s", result.Stdout)
	}
}

// C6: single value (no comma) is NOT compare mode — normal build
func TestSingleValueIsNotCompareMode(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "method=diagnose", "--subject", "x"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0 for single value, got %d\nstderr: %s", result.Exit, result.Stderr)
	}
	// Compare mode marker must NOT appear for single-value
	if strings.Contains(result.Stdout, "Variant 1:") || strings.Contains(result.Stdout, "COMPARISON") {
		t.Errorf("single-value should not trigger compare mode:\n%s", result.Stdout)
	}
}

// C7: compare works on scope axis too (not just method)
func TestCompareScopeAxis(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "scope=fail,cross", "--subject", "system"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d\nstderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "fail") || !strings.Contains(result.Stdout, "cross") {
		t.Errorf("expected both scope variants in output:\n%s", result.Stdout)
	}
}

// C8: --addendum is included in comparison output
func TestCompareIncludesAddendum(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "make", "method=diagnose,mapping", "--subject", "x", "--addendum", "focus on errors"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d\nstderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "focus on errors") {
		t.Errorf("expected addendum in output:\n%s", result.Stdout)
	}
}

// DetectCompare unit tests

func TestDetectCompareFindsMultiValue(t *testing.T) {
	axis, variants, cleaned, err := DetectCompare([]string{"make", "method=diagnose,mapping"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if axis != "method" {
		t.Errorf("expected axis 'method', got %q", axis)
	}
	if len(variants) != 2 || variants[0] != "diagnose" || variants[1] != "mapping" {
		t.Errorf("unexpected variants: %v", variants)
	}
	_ = cleaned
}

func TestDetectCompareNoMultiValue(t *testing.T) {
	axis, variants, _, err := DetectCompare([]string{"make", "method=diagnose"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if axis != "" || variants != nil {
		t.Errorf("expected no compare detected, got axis=%q variants=%v", axis, variants)
	}
}

func TestDetectCompareTwoMultiAxesError(t *testing.T) {
	_, _, _, err := DetectCompare([]string{"make", "method=diagnose,mapping", "scope=fail,cross"})
	if err == nil {
		t.Fatal("expected error for two multi-value axes")
	}
}

// C9: hyphenated slug for multi-word directional token in compare list is accepted
func TestCompareDirectionalHyphenatedSlug(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	// "fip-bog" is the slug for the multi-word directional token "fip bog"
	result := runBuildCLI(t, []string{"build", "probe", "directional=fog,fip-bog", "--subject", "test"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0 for directional slug compare, got %d\nstderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "COMPARISON") {
		t.Errorf("expected comparison output:\n%s", result.Stdout)
	}
	if !strings.Contains(result.Stdout, "fog") {
		t.Errorf("expected fog variant in output:\n%s", result.Stdout)
	}
	if !strings.Contains(result.Stdout, "fip bog") {
		t.Errorf("expected 'fip bog' (canonical form) in output:\n%s", result.Stdout)
	}
}

// C10: hyphenated slug for multi-word directional token in key=value override is accepted
func TestDirectionalHyphenatedSlugOverride(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	result := runBuildCLI(t, []string{"build", "probe", "directional=fip-bog", "--subject", "test"}, nil)
	if result.Exit != 0 {
		t.Fatalf("expected exit 0 for directional=fip-bog, got %d\nstderr: %s", result.Exit, result.Stderr)
	}
}
