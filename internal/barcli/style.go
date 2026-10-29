package barcli

import (
	"fmt"
	"strings"
)

// Prompt styles for `bar build`. "plain" is the default; "standard" restores the
// original derivation-span scaffolding.
const (
	StylePlain    = "plain"
	StyleStandard = "standard"

	styleEnv = "BAR_PROMPT_STYLE"
)

// ResolveStyle picks the style from an explicit flag value, then the environment
// value, then the default (plain). An unknown value is an error.
func ResolveStyle(flagValue, envValue string) (string, error) {
	for _, v := range []string{flagValue, envValue} {
		v = strings.ToLower(strings.TrimSpace(v))
		switch v {
		case "":
			continue
		case StylePlain, StyleStandard:
			return v, nil
		default:
			return "", fmt.Errorf("unknown prompt style %q; use %q or %q", v, StylePlain, StyleStandard)
		}
	}
	return StylePlain, nil
}

// ApplyStyle overlays the grammar's plain scaffolding onto the result when the
// plain style is selected and the grammar carries it. Otherwise the result keeps
// the standard text and an empty Style, so rendering is unchanged.
func ApplyStyle(result *BuildResult, g *Grammar, style string) {
	if style != StylePlain || g == nil || g.Plain == nil {
		return
	}
	p := g.Plain
	result.Style = StylePlain
	result.Preamble = p.Preamble
	result.AxisInteraction = p.AxisInteraction
	result.PlanningDirective = p.PlanningDirective
	result.SubjectFraming = p.SubjectFraming
	result.MetaInterpretationGuidance = p.MetaInterpretationGuidance
	result.TokenLoading = p.TokenLoading
	result.CompositionLoading = p.CompositionLoading
}
