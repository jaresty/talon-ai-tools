package barcli

import (
	"strings"
	"testing"
)

func TestRenderPlainTextSections(t *testing.T) {
	result := &BuildResult{
		Subject: "Fix onboarding",
		Task:    "Task:\n  Format this as a todo list.",
		Constraints: []string{
			"Completeness (full): The response provides a thorough answer.",
			"Directional (fog): The response applies an abstracting perspective.",
		},
		Persona: PersonaResult{
			Preset:      "coach_junior",
			PresetLabel: "Coach junior",
			Voice:       "as teacher",
			Tone:        "gently",
		},
		HydratedPersona: []HydratedPromptlet{
			{Axis: "persona_preset", Token: "coach_junior", Description: "Coach junior"},
			{Axis: "voice", Token: "as teacher", Description: "Teaches kindly."},
		},
	}

	output := RenderPlainText(result)

	required := []string{
		"=== TASK (DO THIS) ===",
		"=== CONSTRAINTS (GUARDRAILS) ===",
		"=== PERSONA (STANCE) ===",
		"=== SUBJECT (CONTEXT) ===",
		"- Completeness (full):",
		"- Preset: coach_junior — Coach junior",
		"- Voice: as teacher — Teaches kindly.",
	}

	for _, marker := range required {
		if !strings.Contains(output, marker) {
			t.Fatalf("expected plain text output to contain %q, got:\n%s", marker, output)
		}
	}

	if strings.Contains(output, "- "+sectionPromptlets) {
		t.Fatalf("expected plain text output to omit legacy promptlets block, got:\n%s", output)
	}
}

// TestRenderPlainTextUsesResultReferenceKey specifies that RenderPlainText uses
// result.ReferenceKey when it is non-empty, rather than the hardcoded constant
// (ADR-0131, Loop 3). This is the specifying validation for the render.go change.
func TestRenderPlainTextUsesResultReferenceKey(t *testing.T) {
	customKey := "CUSTOM_REFERENCE_KEY_ADR0131_SENTINEL"
	result := &BuildResult{
		Task:         "make something",
		Constraints:  []string{},
		ReferenceKey: customKey,
	}

	output := RenderPlainText(result)

	if !strings.Contains(output, customKey) {
		t.Fatalf("expected RenderPlainText to use result.ReferenceKey %q, but output does not contain it:\n%s", customKey, output)
	}
}
