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

// TestRenderPlainTextNoReferenceKeyBlock specifies that RenderPlainText no
// longer emits a standalone === REFERENCE KEY === block (ADR-0176).
func TestRenderPlainTextNoReferenceKeyBlock(t *testing.T) {
	result := &BuildResult{Task: "make something"}
	output := RenderPlainText(result)
	if strings.Contains(output, sectionReference) {
		t.Fatalf("expected RenderPlainText to omit REFERENCE KEY block, got:\n%s", output)
	}
}

// TestRenderPlainTextTaskInlineContract specifies that the TASK section emits
// its inline contract immediately after the header and before the task body (ADR-0176).
func TestRenderPlainTextTaskInlineContract(t *testing.T) {
	result := &BuildResult{
		Task:         "make something",
		ReferenceKey: ReferenceKeyContracts{Task: "SENTINEL_TASK_CONTRACT"},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "SENTINEL_TASK_CONTRACT") {
		t.Fatalf("expected TASK inline contract in output:\n%s", output)
	}
	taskIdx := strings.Index(output, sectionTask)
	contractIdx := strings.Index(output, "SENTINEL_TASK_CONTRACT")
	bodyIdx := strings.Index(output, "make something")
	if contractIdx <= taskIdx || contractIdx >= bodyIdx {
		t.Fatalf("expected TASK contract (pos %d) between header (pos %d) and body (pos %d):\n%s", contractIdx, taskIdx, bodyIdx, output)
	}
}

// TestRenderPlainTextConstraintsInlineContract specifies that the CONSTRAINTS
// section emits its section-level contract immediately after the header and
// before the first constraint bullet (ADR-0176).
func TestRenderPlainTextConstraintsInlineContract(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "full", Description: "Thorough."},
		},
		ReferenceKey: ReferenceKeyContracts{Constraints: "SENTINEL_CONSTRAINTS_CONTRACT"},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "SENTINEL_CONSTRAINTS_CONTRACT") {
		t.Fatalf("expected CONSTRAINTS contract in output:\n%s", output)
	}
	headerIdx := strings.Index(output, sectionConstraints)
	contractIdx := strings.Index(output, "SENTINEL_CONSTRAINTS_CONTRACT")
	bulletIdx := strings.Index(output, "- Completeness")
	if contractIdx <= headerIdx || contractIdx >= bulletIdx {
		t.Fatalf("expected CONSTRAINTS contract (pos %d) between header (pos %d) and first bullet (pos %d):\n%s", contractIdx, headerIdx, bulletIdx, output)
	}
}

// TestRenderPlainTextPerAxisContracts specifies that present axes in CONSTRAINTS
// emit their per-axis contract before that axis's bullet(s) (ADR-0176).
func TestRenderPlainTextPerAxisContracts(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "full", Description: "Thorough."},
			{Axis: "scope", Token: "struct", Description: "Structural."},
		},
		ReferenceKey: ReferenceKeyContracts{
			ConstraintsAxes: map[string]string{
				"completeness": "SENTINEL_COMPLETENESS_CONTRACT",
				"scope":        "SENTINEL_SCOPE_CONTRACT",
			},
		},
	}
	output := RenderPlainText(result)
	for _, sentinel := range []string{"SENTINEL_COMPLETENESS_CONTRACT", "SENTINEL_SCOPE_CONTRACT"} {
		if !strings.Contains(output, sentinel) {
			t.Fatalf("expected per-axis contract %q in output:\n%s", sentinel, output)
		}
	}
	completenessContractIdx := strings.Index(output, "SENTINEL_COMPLETENESS_CONTRACT")
	scopeContractIdx := strings.Index(output, "SENTINEL_SCOPE_CONTRACT")
	completenessBulletIdx := strings.Index(output, "- Completeness")
	scopeBulletIdx := strings.Index(output, "- Scope")
	if completenessContractIdx >= completenessBulletIdx {
		t.Fatalf("expected completeness contract (pos %d) before completeness bullet (pos %d):\n%s", completenessContractIdx, completenessBulletIdx, output)
	}
	if scopeContractIdx >= scopeBulletIdx {
		t.Fatalf("expected scope contract (pos %d) before scope bullet (pos %d):\n%s", scopeContractIdx, scopeBulletIdx, output)
	}
}

// TestRenderPlainTextAbsentAxisNoContract specifies that axes not present in
// the rendered CONSTRAINTS do not emit their per-axis contract (ADR-0176).
func TestRenderPlainTextAbsentAxisNoContract(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "full", Description: "Thorough."},
		},
		ReferenceKey: ReferenceKeyContracts{
			ConstraintsAxes: map[string]string{
				"completeness": "SENTINEL_COMPLETENESS_CONTRACT",
				"method":       "SENTINEL_METHOD_CONTRACT",
			},
		},
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "SENTINEL_METHOD_CONTRACT") {
		t.Fatalf("expected absent axis contract to be omitted, got:\n%s", output)
	}
}

// TestRenderPlainTextSubjectInlineContract specifies that the SUBJECT section
// emits its inline contract immediately after the header and before the body (ADR-0176).
func TestRenderPlainTextSubjectInlineContract(t *testing.T) {
	result := &BuildResult{
		Task:         "make something",
		Subject:      "my subject text",
		ReferenceKey: ReferenceKeyContracts{Subject: "SENTINEL_SUBJECT_CONTRACT"},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "SENTINEL_SUBJECT_CONTRACT") {
		t.Fatalf("expected SUBJECT contract in output:\n%s", output)
	}
	headerIdx := strings.Index(output, sectionSubject)
	contractIdx := strings.Index(output, "SENTINEL_SUBJECT_CONTRACT")
	bodyIdx := strings.Index(output, "my subject text")
	if contractIdx <= headerIdx || contractIdx >= bodyIdx {
		t.Fatalf("expected SUBJECT contract (pos %d) between header (pos %d) and body (pos %d):\n%s", contractIdx, headerIdx, bodyIdx, output)
	}
}

// TestRenderPlainTextAddendumInlineContract specifies that the ADDENDUM section
// emits its inline contract when addendum is present (ADR-0176).
func TestRenderPlainTextAddendumInlineContract(t *testing.T) {
	result := &BuildResult{
		Task:         "make something",
		Addendum:     "extra instructions",
		ReferenceKey: ReferenceKeyContracts{Addendum: "SENTINEL_ADDENDUM_CONTRACT"},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "SENTINEL_ADDENDUM_CONTRACT") {
		t.Fatalf("expected ADDENDUM contract in output:\n%s", output)
	}
	headerIdx := strings.Index(output, sectionAddendum)
	contractIdx := strings.Index(output, "SENTINEL_ADDENDUM_CONTRACT")
	bodyIdx := strings.Index(output, "extra instructions")
	if contractIdx <= headerIdx || contractIdx >= bodyIdx {
		t.Fatalf("expected ADDENDUM contract (pos %d) between header (pos %d) and body (pos %d):\n%s", contractIdx, headerIdx, bodyIdx, output)
	}
}

// TestRenderPlainTextPersonaInlineContract specifies that the PERSONA section
// emits its inline contract when a persona is present (ADR-0176).
func TestRenderPlainTextPersonaInlineContract(t *testing.T) {
	result := &BuildResult{
		Task:    "make something",
		Persona: PersonaResult{Voice: "as teacher"},
		HydratedPersona: []HydratedPromptlet{
			{Axis: "voice", Token: "as teacher", Description: "Teaches."},
		},
		ReferenceKey: ReferenceKeyContracts{Persona: "SENTINEL_PERSONA_CONTRACT"},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "SENTINEL_PERSONA_CONTRACT") {
		t.Fatalf("expected PERSONA contract in output:\n%s", output)
	}
	headerIdx := strings.Index(output, sectionPersona)
	contractIdx := strings.Index(output, "SENTINEL_PERSONA_CONTRACT")
	if contractIdx <= headerIdx {
		t.Fatalf("expected PERSONA contract (pos %d) after header (pos %d):\n%s", contractIdx, headerIdx, output)
	}
}

// TestRenderPlainTextIncludesKanjiInPromptlets specifies that hydrated promptlets
// include kanji characters when available (ADR-0143).
// TestRenderPersonaAllFourAxes specifies that RenderPlainText renders all four
// persona axes (voice, audience, tone, intent) with their descriptions when all
// are present in PersonaResult and HydratedPersona.
func TestRenderPersonaAllFourAxes(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		Persona: PersonaResult{
			Voice:    "as teacher",
			Audience: "to junior engineer",
			Tone:     "kindly",
			Intent:   "coach",
		},
		HydratedPersona: []HydratedPromptlet{
			{Axis: "voice", Token: "as teacher", Description: "Teaches carefully."},
			{Axis: "audience", Token: "to junior engineer", Description: "Clear for juniors."},
			{Axis: "tone", Token: "kindly", Description: "Kind and warm."},
			{Axis: "intent", Token: "coach", Description: "Guide growth."},
		},
	}

	output := RenderPlainText(result)

	for _, want := range []string{
		"- Voice (as teacher): Teaches carefully.",
		"- Audience (to junior engineer): Clear for juniors.",
		"- Tone (kindly): Kind and warm.",
		"- Intent (coach): Guide growth.",
	} {
		if !strings.Contains(output, want) {
			t.Errorf("expected output to contain %q\ngot:\n%s", want, output)
		}
	}
}

// TestRenderPersonaPresetWithIntent specifies that when a preset is combined
// with an explicit intent, both the preset axes and the intent appear in the
// PERSONA section.
func TestRenderPersonaPresetWithIntent(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		Persona: PersonaResult{
			Preset:      "designer_to_pm",
			PresetLabel: "Designer to PM",
			Voice:       "as designer",
			Audience:    "to product manager",
			Tone:        "directly",
			Intent:      "persuade",
		},
		HydratedPersona: []HydratedPromptlet{
			{Axis: "persona_preset", Token: "designer_to_pm", Description: "Designer to PM"},
			{Axis: "voice", Token: "as designer", Description: "Designer voice."},
			{Axis: "audience", Token: "to product manager", Description: "PM audience."},
			{Axis: "tone", Token: "directly", Description: "Direct tone."},
			{Axis: "intent", Token: "persuade", Description: "Persuade the audience."},
		},
	}

	output := RenderPlainText(result)

	for _, want := range []string{
		"- Preset:",
		"- Voice (as designer): Designer voice.",
		"- Intent (persuade): Persuade the audience.",
	} {
		if !strings.Contains(output, want) {
			t.Errorf("expected output to contain %q\ngot:\n%s", want, output)
		}
	}
}

// TestExecutionReminderPrecedesConstraints specifies that the EXECUTION REMINDER
// section appears before the CONSTRAINTS section in RenderPlainText output, so
// it gates completion-intent before constraints arrive rather than functioning
// as a late-position advisory.
func TestExecutionReminderPrecedesConstraints(t *testing.T) {
	result := &BuildResult{
		Task:             "make something",
		ExecutionReminder: "Execute the TASK. Satisfy CONSTRAINTS before producing content.",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "full", Description: "Thorough answer."},
		},
	}

	output := RenderPlainText(result)

	reminderIdx := strings.Index(output, sectionExecution)
	constraintsIdx := strings.Index(output, sectionConstraints)

	if reminderIdx == -1 {
		t.Fatalf("expected output to contain EXECUTION REMINDER section, got:\n%s", output)
	}
	if constraintsIdx == -1 {
		t.Fatalf("expected output to contain CONSTRAINTS section, got:\n%s", output)
	}
	if reminderIdx >= constraintsIdx {
		t.Fatalf("expected EXECUTION REMINDER (pos %d) to appear before CONSTRAINTS (pos %d):\n%s", reminderIdx, constraintsIdx, output)
	}
}

// TestExecutionReminderAlsoFollowsSubject specifies that a second EXECUTION
// REMINDER appears after the SUBJECT section (after META INTERPRETATION when
// present), providing recency-based resistance to SUBJECT injection attacks.
func TestExecutionReminderAlsoFollowsSubject(t *testing.T) {
	result := &BuildResult{
		Task:              "make something",
		ExecutionReminder: "Execute the TASK. Satisfy CONSTRAINTS before producing content.",
		Subject:           "some subject content",
	}

	output := RenderPlainText(result)

	subjectIdx := strings.Index(output, sectionSubject)
	// Find the last occurrence of sectionExecution
	lastReminderIdx := strings.LastIndex(output, sectionExecution)

	if subjectIdx == -1 {
		t.Fatalf("expected output to contain SUBJECT section")
	}
	if lastReminderIdx == -1 {
		t.Fatalf("expected output to contain EXECUTION REMINDER section")
	}
	if lastReminderIdx <= subjectIdx {
		t.Fatalf("expected a second EXECUTION REMINDER (pos %d) to appear after SUBJECT (pos %d):\n%s", lastReminderIdx, subjectIdx, output)
	}
}

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
