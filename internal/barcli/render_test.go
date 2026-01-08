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
		"=== SUBJECT ===",
		"=== TASK ===",
		"=== CONSTRAINTS ===",
		"=== PERSONA ===",
		"1. Completeness (full):",
		"Promptlets:",
		"• Voice (as teacher):",
	}

	for _, marker := range required {
		if !strings.Contains(output, marker) {
			t.Fatalf("expected plain text output to contain %q, got:\n%s", marker, output)
		}
	}
}
