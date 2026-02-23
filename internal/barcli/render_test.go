package barcli

import (
	"strings"
	"testing"
)

func TestRenderPlainTextSections(t *testing.T) {
	result := &BuildResult{
		Subject: "Fix onboarding",
		Task:    "Task:\n  Format this as a todo list.",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "full", Description: "The response provides a thorough answer."},
			{Axis: "directional", Token: "fog", Description: "The response applies an abstracting perspective."},
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
		"=== TASK 任務 (DO THIS) ===",
		"=== CONSTRAINTS 制約 (GUARDRAILS) ===",
		"=== PERSONA 人格 (STANCE) ===",
		"=== SUBJECT 題材 (CONTEXT) ===",
		"Completeness (full):",
		"- Preset: coach_junior — Coach junior",
		"- Voice (as teacher): Teaches kindly.",
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

// TestRenderPlainTextIncludesKanjiInPromptlets specifies that hydrated promptlets
// include kanji characters when available (ADR-0143).
func TestRenderPlainTextIncludesKanjiInPromptlets(t *testing.T) {
	result := &BuildResult{
		Task:        "probe fail full",
		Constraints: []string{},
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "method", Token: "probe", Kanji: "探"},
			{Axis: "scope", Token: "fail", Kanji: "敗"},
			{Axis: "completeness", Token: "full", Kanji: "全"},
		},
		HydratedPersona: []HydratedPromptlet{
			{Axis: "voice", Token: "socratic", Kanji: "質"},
		},
	}

	output := RenderPlainText(result)

	if !strings.Contains(output, "探") {
		t.Fatalf("expected hydrated constraint to include kanji 探, got:\n%s", output)
	}
	if !strings.Contains(output, "敗") {
		t.Fatalf("expected hydrated constraint to include kanji 敗, got:\n%s", output)
	}
	if !strings.Contains(output, "全") {
		t.Fatalf("expected hydrated constraint to include kanji 全, got:\n%s", output)
	}
	if !strings.Contains(output, "質") {
		t.Fatalf("expected hydrated persona to include kanji 質, got:\n%s", output)
	}
}
