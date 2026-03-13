package barcli

import (
	"fmt"
	"strings"
)

// DetectCompare scans a token list for exactly one axis carrying comma-separated values
// (e.g. "method=diagnose,mapping"). Returns the axis name, the variant slugs, and a
// cleaned token list with the multi-value entry replaced by the first variant only
// (so the cleaned list can be passed to Build for token validation).
//
// Returns ("", nil, tokens, nil) when no multi-value axis is found.
// Returns an error when more than one axis carries multiple values.
func DetectCompare(tokens []string) (axis string, variants []string, cleaned []string, err error) {
	cleaned = make([]string, 0, len(tokens))
	var multiAxis string
	var multiVariants []string

	for _, tok := range tokens {
		tok = strings.TrimSpace(tok)
		if idx := strings.Index(tok, "="); idx >= 0 {
			key := strings.TrimSpace(tok[:idx])
			val := strings.TrimSpace(tok[idx+1:])
			if strings.Contains(val, ",") {
				parts := splitCSV(val)
				if multiAxis != "" && multiAxis != key {
					return "", nil, nil, fmt.Errorf(
						"compare mode: only one axis may carry multiple values; found %q and %q",
						multiAxis, key,
					)
				}
				multiAxis = key
				multiVariants = parts
				// Replace with first variant for the cleaned list
				cleaned = append(cleaned, key+"="+parts[0])
				continue
			}
		}
		cleaned = append(cleaned, tok)
	}

	if multiAxis == "" {
		return "", nil, tokens, nil
	}
	return multiAxis, multiVariants, cleaned, nil
}

// BuildCompare generates an Approach A comparison prompt: a single prompt with N labeled
// sections, one per variant, each prefixed with the token's definition and heuristics.
//
// baseTokens must not contain the multi-value entry (use cleaned from DetectCompare).
// subject and addendum are the raw user inputs.
func BuildCompare(g *Grammar, baseTokens []string, axis string, variants []string, subject, addendum string) (string, *CLIError) {
	// Validate all variants exist in the grammar before generating output
	for _, v := range variants {
		testTokens := append(append([]string(nil), baseTokens...), axis+"="+v)
		if _, err := Build(g, testTokens); err != nil {
			return "", err
		}
	}

	var b strings.Builder

	b.WriteString("=== COMPARISON 比較 ===\n")
	b.WriteString(fmt.Sprintf(
		"Respond to the subject %d times, once per %s variant below.\n",
		len(variants), axis,
	))
	b.WriteString("For each variant, apply only that token's framing and label your response clearly.\n")
	b.WriteString("Do not blend or average across variants — each section is independent.\n")

	if subject != "" {
		b.WriteString("\n=== SUBJECT 題材 ===\n")
		b.WriteString(subject)
		b.WriteString("\n")
	}

	if addendum != "" {
		b.WriteString("\n=== ADDENDUM 追加 ===\n")
		b.WriteString(addendum)
		b.WriteString("\n")
	}

	for _, v := range variants {
		canonical := g.ResolveSlug(v)

		b.WriteString("\n---\n\n")
		b.WriteString(fmt.Sprintf("## Variant: %s=%s\n", axis, canonical))

		desc := g.AxisDescription(axis, canonical)
		if desc != "" {
			b.WriteString(fmt.Sprintf("**Definition**: %s\n", desc))
		}

		heuristics := g.AxisTokenHeuristics(axis, canonical)
		if len(heuristics) > 0 {
			b.WriteString(fmt.Sprintf("**Heuristics**: %s\n", strings.Join(heuristics, ", ")))
		}

		b.WriteString("\n[Respond here using " + axis + "=" + canonical + " framing]\n")
	}

	return b.String(), nil
}

// splitCSV splits a comma-separated string, trimming whitespace from each part,
// and drops empty parts.
func splitCSV(s string) []string {
	parts := strings.Split(s, ",")
	result := make([]string, 0, len(parts))
	for _, p := range parts {
		trimmed := strings.TrimSpace(p)
		if trimmed != "" {
			result = append(result, trimmed)
		}
	}
	return result
}
