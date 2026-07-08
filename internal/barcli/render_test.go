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
		"=== REQUEST 依頼 ===",
		"=== AXES 軸 (token types — each governs a different dimension) ===",
		"=== TOKENS 役割 ===",
		"Format this as a todo list.",
		"Fix onboarding",
		"- voice = as teacher",
	}
	if strings.Contains(output, "=== TOKEN DEFINITIONS") {
		t.Fatalf("TOKEN DEFINITIONS section must be absent from output, got:\n%s", output)
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

// TestRenderPlainTextContractBracketed — redesigned output has no ↓ contracts in REQUEST section.
// The ReferenceKey contracts are no longer emitted in the new section layout.

// TestRenderPlainTextTaskInlineContract — removed: TASK section is absent from redesigned output.
// REQUEST section contract is covered by TestRenderPlainTextSubjectInlineContract.

// TestRenderPlainTextConstraintsInlineContract — removed: CONSTRAINTS section
// replaced by AXES/TOKENS/TOKEN DEFINITIONS sections which have no section-level contract.

// TestRenderPlainTextConstraintsSectionContractNoArrow — removed: CONSTRAINTS section
// replaced by AXES/TOKENS/TOKEN DEFINITIONS sections which have no contract mechanism.

// TestRenderPlainTextPerAxisContracts — removed: per-axis contracts (ADR-0176) no longer
// rendered; AXES/TOKENS/TOKEN DEFINITIONS sections have no contract mechanism.

// TestRenderPlainTextAbsentAxisNoContract — removed: per-axis contracts no longer rendered.

// TestRenderPlainTextSubjectInlineContract — redesigned output has no ↓ contracts in REQUEST section.
func TestRenderPlainTextSubjectInlineContract(t *testing.T) {
	result := &BuildResult{
		Task:         "make something",
		Subject:      "my subject text",
		ReferenceKey: ReferenceKeyContracts{Subject: "SENTINEL_SUBJECT_CONTRACT"},
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "SENTINEL_SUBJECT_CONTRACT") {
		t.Fatalf("redesigned REQUEST section must not emit ↓ contract, got:\n%s", output)
	}
}

// TestRenderPlainTextAddendumInlineContract — addendum is now merged into REQUEST body,
// not a standalone section. Addendum text appears in the REQUEST block.
func TestRenderPlainTextAddendumInlineContract(t *testing.T) {
	result := &BuildResult{
		Task:     "make something",
		Addendum: "extra instructions",
	}
	output := RenderPlainText(result)
	requestIdx := strings.Index(output, sectionSubject)
	formatIdx := strings.Index(output, sectionFormat)
	if requestIdx < 0 || formatIdx < 0 {
		t.Fatalf("expected REQUEST and FORMAT sections in output:\n%s", output)
	}
	requestBlock := output[requestIdx:formatIdx]
	if !strings.Contains(requestBlock, "extra instructions") {
		t.Fatalf("expected addendum text in REQUEST block, got:\n%s", requestBlock)
	}
}

// TestRenderPlainTextPersonaInlineContract — PERSONA section is absent from redesigned output.
// Persona folds into TOKENS and TOKEN DEFINITIONS sections instead.

// TestRenderPlainTextIncludesKanjiInPromptlets specifies that hydrated promptlets
// include kanji characters when available (ADR-0143).
// TestRenderPersonaAllFourAxes specifies that RenderPlainText renders persona axes
// as individual axis=token lines in TOKENS (not a collapsed persona= row).
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

	tokensIdx := strings.Index(output, sectionTokens)
	formatIdx := strings.Index(output, sectionFormat)
	if tokensIdx < 0 || formatIdx < 0 {
		t.Fatal("TOKENS and FORMAT sections must both be present")
	}
	tokensBlock := output[tokensIdx:formatIdx]

	// Each persona axis appears as an individual axis=token line in TOKENS.
	for _, want := range []string{
		"- voice = as teacher",
		"- audience = to junior engineer",
		"- tone = kindly",
		"- intent = coach",
	} {
		if !strings.Contains(tokensBlock, want) {
			t.Errorf("expected %q in TOKENS section, got block:\n%s", want, tokensBlock)
		}
	}
	// No collapsed persona= line when individual axes are present.
	if strings.Contains(tokensBlock, "- persona =") {
		t.Errorf("expected no collapsed '- persona =' line in TOKENS section, got block:\n%s", tokensBlock)
	}
	// TOKEN DEFINITIONS section must be absent.
	if strings.Contains(output, "=== TOKEN DEFINITIONS") {
		t.Errorf("TOKEN DEFINITIONS section must be absent from output, got:\n%s", output)
	}
}

// TestRenderPersonaPresetWithIntent specifies that when a preset is active,
// the resolved individual axes appear in the TOKENS section (not the preset name).
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

	tokensIdx := strings.Index(output, sectionTokens)
	formatIdx := strings.Index(output, sectionFormat)
	if tokensIdx < 0 || formatIdx < 0 {
		t.Fatal("TOKENS and FORMAT sections must both be present")
	}
	tokensBlock := output[tokensIdx:formatIdx]

	// Individual persona axes appear as separate lines, not a collapsed preset row.
	for _, want := range []string{
		"- voice = as designer",
		"- audience = to product manager",
		"- tone = directly",
		"- intent = persuade",
	} {
		if !strings.Contains(tokensBlock, want) {
			t.Errorf("expected %q in TOKENS section, got block:\n%s", want, tokensBlock)
		}
	}
	if strings.Contains(tokensBlock, "- persona = designer_to_pm") {
		t.Errorf("expected no collapsed preset line in TOKENS section, got block:\n%s", tokensBlock)
	}
}

// TestExecutionReminderPrecedesAxes — removed: EXECUTION REMINDER section is absent
// from redesigned output. Preamble replaces it and precedes REQUEST.

// TestPlanningDirectiveFollowsSubject specifies that a PLANNING DIRECTIVE
// appears after the SUBJECT section (after META INTERPRETATION when
// present), providing recency-based resistance to SUBJECT injection attacks
// while requiring explicit planning output from the LLM.
func TestPlanningDirectiveFollowsSubject(t *testing.T) {
	result := &BuildResult{
		Task:              "make something",
		ExecutionReminder: "Execute the TASK. Satisfy CONSTRAINTS before producing content.",
		Subject:           "some subject content",
	}

	output := RenderPlainText(result)

	subjectIdx := strings.Index(output, sectionSubject)
	formatIdx := strings.Index(output, sectionFormat)

	if subjectIdx == -1 {
		t.Fatalf("expected output to contain REQUEST section")
	}
	if formatIdx == -1 {
		t.Fatalf("expected output to contain FORMAT 形式 section, got:\n%s", output)
	}
	if formatIdx <= subjectIdx {
		t.Fatalf("expected FORMAT (pos %d) to appear after REQUEST (pos %d):\n%s", formatIdx, subjectIdx, output)
	}
}

func TestRenderPlainTextIncludesKanjiInPromptlets(t *testing.T) {
	result := &BuildResult{
		Task:        "probe fail full",
		Constraints: []string{},
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "method", Token: "probe", Kanji: "探", Description: "Probing analysis."},
			{Axis: "completeness", Token: "full", Kanji: "全", Description: "Thorough."},
		},
		HydratedPersona: []HydratedPromptlet{
			{Axis: "voice", Token: "socratic", Kanji: "質"},
		},
	}

	output := RenderPlainText(result)

	// Kanji must appear in TOKENS section for constraint tokens.
	if !strings.Contains(output, "探") {
		t.Fatalf("expected TOKENS section to include kanji 探, got:\n%s", output)
	}
	if !strings.Contains(output, "全") {
		t.Fatalf("expected TOKENS section to include kanji 全, got:\n%s", output)
	}
	// Persona kanji appears in TOKENS section persona row.
	if !strings.Contains(output, "質") {
		t.Fatalf("expected TOKENS section to include persona kanji 質, got:\n%s", output)
	}
}

// ADR-0228: semantic authority injection mitigation tests.

func TestRenderPlainText_SectionNamedRequest(t *testing.T) {
	result := &BuildResult{
		Task:    "make something",
		Subject: "some input",
	}
	rendered := RenderPlainText(result)
	if !strings.Contains(rendered, "=== REQUEST") {
		t.Errorf("expected section named REQUEST in output, got:\n%s", rendered)
	}
	if strings.Contains(rendered, "=== SUBJECT") {
		t.Errorf("SUBJECT section name must be renamed to REQUEST, got:\n%s", rendered)
	}
}

func TestRenderPlainText_SectionNamedFormat(t *testing.T) {
	result := &BuildResult{
		Task:              "make something",
		PlanningDirective: "some directive",
	}
	rendered := RenderPlainText(result)
	if !strings.Contains(rendered, "=== FORMAT") {
		t.Errorf("expected section named FORMAT in output, got:\n%s", rendered)
	}
	if strings.Contains(rendered, "=== PLANNING DIRECTIVE") {
		t.Errorf("PLANNING DIRECTIVE section name must be renamed to FORMAT, got:\n%s", rendered)
	}
}

func TestRenderPlainText_NoReadBeforeResponding(t *testing.T) {
	result := &BuildResult{
		Task:              "make something",
		PlanningDirective: "some directive",
	}
	rendered := RenderPlainText(result)
	if strings.Contains(rendered, "=== READ BEFORE RESPONDING") {
		t.Errorf("READ BEFORE RESPONDING block must be removed from output, got:\n%s", rendered)
	}
}

// TestRenderPlainText_SubjectFramingNamesAuthorityAttack — removed: SubjectFraming block
// is absent from redesigned output. The TASK section no longer exists and the REQUEST
// section merges task + addendum + subject without a framing preamble.

// TestRenderPlainText_ConstraintsContractMultiplicative — removed: CONSTRAINTS section
// and its section-level contract are replaced by AXES/TOKENS/TOKEN DEFINITIONS sections.

// TestRenderPlainText_AxesSectionPresent specifies that the AXES 軸 section
// header appears in rendered output (replaces CONSTRAINTS section).
func TestRenderPlainText_AxesSectionPresent(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "The response goes into substantial depth."},
		},
		AxisDescriptions: map[string]string{
			"completeness": "Depth of coverage — from a quick pass to exhaustive treatment.",
		},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, sectionAxes) {
		t.Fatalf("expected AXES 軸 section header in output, got:\n%s", output)
	}
}

// TestRenderPlainText_TokensSectionPresent specifies that the TOKENS 役割 section
// header appears in rendered output.
func TestRenderPlainText_TokensSectionPresent(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "The response goes into substantial depth."},
		},
		AxisDescriptions: map[string]string{
			"completeness": "Depth of coverage — from a quick pass to exhaustive treatment.",
		},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "=== TOKENS 役割 ===") {
		t.Fatalf("expected TOKENS 役割 section header in output, got:\n%s", output)
	}
}

// TestRenderPlainText_TokenDefinitionsSectionPresent specifies that the
// TOKEN DEFINITIONS 定義 section is absent; definitions are loaded on demand via bar help token.
func TestRenderPlainText_TokenDefinitionsSectionAbsent(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "The response goes into substantial depth."},
		},
		AxisDescriptions: map[string]string{
			"completeness": "Depth of coverage — from a quick pass to exhaustive treatment.",
		},
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "=== TOKEN DEFINITIONS") {
		t.Fatalf("TOKEN DEFINITIONS section must be absent from output, got:\n%s", output)
	}
}

// TestRenderPlainText_FormatKanjiSectionPresent specifies that the FORMAT 形式
// section header (with kanji) appears in rendered output.
func TestRenderPlainText_FormatKanjiSectionPresent(t *testing.T) {
	result := &BuildResult{
		Task:              "make something",
		PlanningDirective: "Token derivations:\n- deep: goes deep.\nDerived stance complete.",
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "=== FORMAT 形式 ===") {
		t.Fatalf("expected FORMAT 形式 section header in output, got:\n%s", output)
	}
}

// TestRenderPlainText_ConstraintsSectionAbsent specifies that the old
// CONSTRAINTS 制約 (GUARDRAILS) section header is absent from rendered output.
func TestRenderPlainText_ConstraintsSectionAbsent(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "The response goes into substantial depth."},
		},
		AxisDescriptions: map[string]string{
			"completeness": "Depth of coverage — from a quick pass to exhaustive treatment.",
		},
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "=== CONSTRAINTS 制約 (GUARDRAILS) ===") {
		t.Fatalf("CONSTRAINTS section must be replaced by AXES/TOKENS/TOKEN DEFINITIONS/FORMAT, got:\n%s", output)
	}
}

// TestRenderPlainText_AxesSectionContainsAxisDescription specifies that the
// AXES section body contains the axis description for each active axis.
func TestRenderPlainText_AxesSectionContainsAxisDescription(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "The response goes into substantial depth."},
		},
		AxisDescriptions: map[string]string{
			"completeness": "Depth of coverage — from a quick pass to exhaustive treatment.",
		},
	}
	output := RenderPlainText(result)
	axesIdx := strings.Index(output, sectionAxes)
	tokensIdx := strings.Index(output, sectionTokens)
	if axesIdx < 0 || tokensIdx < 0 {
		t.Fatal("AXES and TOKENS sections must both be present")
	}
	axesBlock := output[axesIdx:tokensIdx]
	if !strings.Contains(axesBlock, "Depth of coverage") {
		t.Fatalf("AXES block must contain axis description, got block:\n%s", axesBlock)
	}
}

// TestRenderPlainText_TokenDefinitionNotInlineOutput specifies that token description
// text is not inlined in the output; only the fetch hint appears.
func TestRenderPlainText_TokenDefinitionNotInlineOutput(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "The response goes into substantial depth."},
		},
		AxisDescriptions: map[string]string{
			"completeness": "Depth of coverage — from a quick pass to exhaustive treatment.",
		},
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "substantial depth") {
		t.Fatalf("token description text must not appear inline in output, got:\n%s", output)
	}
	if !strings.Contains(output, "→ bar help token deep") {
		t.Fatalf("TOKENS section must contain inline fetch hint for token 'deep', got:\n%s", output)
	}
}

// TestRenderPlainText_LoadedArtifactInstruction specifies that the TOKENS section
// instruction requires a Loaded: artifact line per token and gates Token derivations:.
func TestRenderPlainText_LoadedArtifactInstruction(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "Loaded:") {
		t.Fatalf("TOKENS instruction must require 'Loaded:' artifact lines, got:\n%s", output)
	}
	if !strings.Contains(output, "shown after →") {
		t.Fatalf("TOKENS instruction must resolve slug via '→' hint, got:\n%s", output)
	}
	if !strings.Contains(output, "Do not write 'Token derivations:'") {
		t.Fatalf("TOKENS instruction must gate Token derivations: on Loaded: lines, got:\n%s", output)
	}
}

// TestRenderPlainText_UnconditionalFetchInstruction specifies that the TOKENS section
// opens with an unconditional fetch instruction with no familiarity exception.
func TestRenderPlainText_UnconditionalFetchInstruction(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "unfamiliar") {
		t.Fatalf("fetch instruction must not contain 'unfamiliar' (familiarity exception must be removed), got:\n%s", output)
	}
	if !strings.Contains(output, "Loaded:") {
		t.Fatalf("fetch instruction must require Loaded: artifact lines, got:\n%s", output)
	}
	if !strings.Contains(output, "Do not write 'Token derivations:'") {
		t.Fatalf("fetch instruction must gate Token derivations: on Loaded: lines, got:\n%s", output)
	}
}

// TestRenderPlainText_LazyLoadTokenHints specifies that TOKEN DEFINITIONS section is absent,
// each token line carries an inline fetch hint, and the TOKENS section opens with the load instruction.
func TestRenderPlainText_LazyLoadTokenHints(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "The response goes into substantial depth."},
		},
		AxisDescriptions: map[string]string{
			"completeness": "Depth of coverage — from a quick pass to exhaustive treatment.",
		},
	}
	output := RenderPlainText(result)

	if strings.Contains(output, "=== TOKEN DEFINITIONS") {
		t.Fatalf("TOKEN DEFINITIONS section must be absent from output, got:\n%s", output)
	}

	tokensIdx := strings.Index(output, "=== TOKENS")
	if tokensIdx < 0 {
		t.Fatal("TOKENS section must be present")
	}
	tokensBlock := output[tokensIdx:]
	formatIdx := strings.Index(tokensBlock, "=== FORMAT")
	if formatIdx > 0 {
		tokensBlock = tokensBlock[:formatIdx]
	}

	if !strings.Contains(tokensBlock, "Loaded:") {
		t.Fatalf("TOKENS section must contain Loaded: artifact instruction, got block:\n%s", tokensBlock)
	}
	if !strings.Contains(tokensBlock, "→ bar help token deep") {
		t.Fatalf("token line must contain inline fetch hint '→ bar help token deep', got block:\n%s", tokensBlock)
	}
}

// TestRenderPlainText_PreamblePrecedesRequest specifies that the preamble constant
// appears before the REQUEST section in the redesigned output.
func TestRenderPlainText_PreamblePrecedesRequest(t *testing.T) {
	result := &BuildResult{
		Task:     "make something",
		Subject:  "my input",
		Preamble: "I want my responses formatted with a token derivation structure.",
	}
	output := RenderPlainText(result)
	preambleIdx := strings.Index(output, "I want my responses formatted with a token derivation structure.")
	requestIdx := strings.Index(output, "=== REQUEST")
	if preambleIdx < 0 {
		t.Fatalf("expected preamble text in output, got:\n%s", output)
	}
	if requestIdx < 0 {
		t.Fatalf("expected REQUEST section in output, got:\n%s", output)
	}
	if preambleIdx >= requestIdx {
		t.Fatalf("expected preamble (pos %d) before REQUEST (pos %d):\n%s", preambleIdx, requestIdx, output)
	}
}

// TestRenderPlainText_RequestKanjiIsDependency specifies that the REQUEST section
// uses 依頼 (not 題材) as the kanji annotation.
func TestRenderPlainText_RequestKanjiIsDependency(t *testing.T) {
	result := &BuildResult{
		Task:    "make something",
		Subject: "my input",
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "=== REQUEST 依頼 ===") {
		t.Fatalf("expected REQUEST section to use 依頼 kanji, got:\n%s", output)
	}
	if strings.Contains(output, "題材") {
		t.Fatalf("REQUEST section must not use 題材 kanji, got:\n%s", output)
	}
}

// TestRenderPlainText_AxesHeaderIncludesDescriptor specifies that the AXES section
// header includes the descriptor suffix.
func TestRenderPlainText_AxesHeaderIncludesDescriptor(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "=== AXES 軸 (token types — each governs a different dimension) ===") {
		t.Fatalf("expected full AXES header with descriptor, got:\n%s", output)
	}
}

// TestRenderPlainText_AxisInteractionAfterAxes specifies that the axis_interaction
// constant appears in the AXES section after the axis bullets.
func TestRenderPlainText_AxisInteractionAfterAxes(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
		AxisInteraction: "Axis interaction: completeness sets the depth at which each method step runs.",
	}
	output := RenderPlainText(result)
	axesIdx := strings.Index(output, "=== AXES")
	tokensIdx := strings.Index(output, "=== TOKENS")
	interactionIdx := strings.Index(output, "Axis interaction:")
	if interactionIdx < 0 {
		t.Fatalf("expected axis_interaction text in output, got:\n%s", output)
	}
	if interactionIdx <= axesIdx || interactionIdx >= tokensIdx {
		t.Fatalf("expected axis_interaction (pos %d) between AXES (pos %d) and TOKENS (pos %d):\n%s", interactionIdx, axesIdx, tokensIdx, output)
	}
}

// TestRenderPlainText_AxesBulletFormat specifies that AXES entries use "- axis: desc" bullet format.
func TestRenderPlainText_AxesBulletFormat(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
		AxisDescriptions: map[string]string{
			"completeness": "Depth of coverage.",
		},
	}
	output := RenderPlainText(result)
	axesIdx := strings.Index(output, "=== AXES")
	tokensIdx := strings.Index(output, "=== TOKENS")
	axesBlock := output[axesIdx:tokensIdx]
	if !strings.Contains(axesBlock, "- completeness: Depth of coverage.") {
		t.Fatalf("expected AXES bullet '- completeness: Depth of coverage.' in block:\n%s", axesBlock)
	}
}

// TestRenderPlainText_TokensBulletFormat specifies that TOKENS entries use "- axis = token" bullet format.
func TestRenderPlainText_TokensBulletFormat(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
	}
	output := RenderPlainText(result)
	tokensIdx := strings.Index(output, "=== TOKENS")
	formatIdx := strings.Index(output, "=== FORMAT")
	if tokensIdx < 0 || formatIdx < 0 {
		t.Fatal("TOKENS and FORMAT sections must both be present")
	}
	tokensBlock := output[tokensIdx:formatIdx]
	if !strings.Contains(tokensBlock, "- completeness = deep") {
		t.Fatalf("expected TOKENS bullet '- completeness = deep' in block:\n%s", tokensBlock)
	}
}

// TestRenderPlainText_TokenFetchHintFormat specifies that TOKENS entries include
// an inline fetch hint "→ bar help token <name>" and kanji when present.
func TestRenderPlainText_TokenFetchHintFormat(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Kanji: "全", Description: "Goes deep."},
		},
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "- completeness = deep 全  → bar help token deep") {
		t.Fatalf("expected TOKENS fetch hint line in output, got:\n%s", output)
	}
	if strings.Contains(output, "Goes deep.") {
		t.Fatalf("description text must not appear inline, got:\n%s", output)
	}
}

// TestRenderPlainText_PersonaFoldsIntoTokensSection specifies that when a persona
// is active, individual axis=token lines appear in the TOKENS section.
func TestRenderPlainText_PersonaFoldsIntoTokensSection(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
		Persona: PersonaResult{Voice: "as teacher"},
		HydratedPersona: []HydratedPromptlet{
			{Axis: "voice", Token: "as teacher", Description: "Teaches."},
		},
	}
	output := RenderPlainText(result)
	tokensIdx := strings.Index(output, "=== TOKENS")
	formatIdx := strings.Index(output, "=== FORMAT")
	if tokensIdx < 0 || formatIdx < 0 {
		t.Fatal("TOKENS and FORMAT sections must both be present")
	}
	tokensBlock := output[tokensIdx:formatIdx]
	if !strings.Contains(tokensBlock, "- voice = as teacher") {
		t.Fatalf("expected '- voice = as teacher' in TOKENS section, got block:\n%s", tokensBlock)
	}
}

// TestRenderPlainText_PersonaNoneWhenAbsent specifies that when no persona is active,
// "- persona = (none)" appears in the TOKENS section.
func TestRenderPlainText_PersonaNoneWhenAbsent(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
	}
	output := RenderPlainText(result)
	tokensIdx := strings.Index(output, "=== TOKENS")
	formatIdx := strings.Index(output, "=== FORMAT")
	if tokensIdx < 0 || formatIdx < 0 {
		t.Fatal("TOKENS and FORMAT sections must both be present")
	}
	tokensBlock := output[tokensIdx:formatIdx]
	if !strings.Contains(tokensBlock, "- persona = (none)") {
		t.Fatalf("expected '- persona = (none)' in TOKENS section when no persona active, got block:\n%s", tokensBlock)
	}
}

// TestRenderPlainText_PersonaFoldsIntoTokensSection2 specifies that when a persona
// is active, individual axis=token lines with fetch hints appear in TOKENS section.
func TestRenderPlainText_PersonaFoldsIntoTokenDefsSection(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "completeness", Token: "deep", Description: "Goes deep."},
		},
		Persona: PersonaResult{Voice: "as teacher"},
		HydratedPersona: []HydratedPromptlet{
			{Axis: "voice", Token: "as teacher", Description: "Teaches carefully."},
		},
	}
	output := RenderPlainText(result)
	tokensIdx := strings.Index(output, "=== TOKENS")
	formatIdx := strings.Index(output, "=== FORMAT")
	if tokensIdx < 0 || formatIdx < 0 {
		t.Fatal("TOKENS and FORMAT sections must both be present")
	}
	tokensBlock := output[tokensIdx:formatIdx]
	if !strings.Contains(tokensBlock, "- voice = as teacher") {
		t.Fatalf("expected '- voice = as teacher' in TOKENS section, got block:\n%s", tokensBlock)
	}
	if strings.Contains(output, "=== TOKEN DEFINITIONS") {
		t.Fatalf("TOKEN DEFINITIONS section must be absent, got:\n%s", output)
	}
}

// TestCompletenessFullHasKanji specifies that completeness=full token renders with kanji 全 in TOKENS section.
func TestCompletenessFullHasKanji(t *testing.T) {
	g := loadCompletionGrammar(t)
	result, err := Build(g, []string{"show", "full"})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	rendered := RenderPlainText(result)
	tokensIdx := strings.Index(rendered, sectionTokens)
	formatIdx := strings.Index(rendered, sectionFormat)
	if tokensIdx < 0 || formatIdx < 0 {
		t.Fatal("TOKENS and FORMAT sections must both be present")
	}
	tokensBlock := rendered[tokensIdx:formatIdx]
	if !strings.Contains(tokensBlock, "全") {
		t.Fatalf("expected completeness=full to render with kanji 全 in TOKENS section, got block:\n%s", tokensBlock)
	}
}

// TestBuildResultPreamblePopulatedFromGrammar specifies that Build() propagates
// the grammar's preamble field into BuildResult.Preamble.
func TestBuildResultPreamblePopulatedFromGrammar(t *testing.T) {
	g := loadCompletionGrammar(t)
	result, err := Build(g, []string{"show"})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	if strings.TrimSpace(result.Preamble) == "" {
		t.Fatalf("expected BuildResult.Preamble to be populated from grammar, got empty string.\nRendered:\n%s", RenderPlainText(result))
	}
}

// TestBuildResultAxisInteractionPopulatedFromGrammar specifies that Build()
// propagates the grammar's axis_interaction field into BuildResult.AxisInteraction.
func TestBuildResultAxisInteractionPopulatedFromGrammar(t *testing.T) {
	g := loadCompletionGrammar(t)
	result, err := Build(g, []string{"show", "full"})
	if err != nil {
		t.Fatalf("Build: %v", err)
	}
	if strings.TrimSpace(result.AxisInteraction) == "" {
		t.Fatalf("expected BuildResult.AxisInteraction to be populated from grammar, got empty string.\nRendered:\n%s", RenderPlainText(result))
	}
	rendered := RenderPlainText(result)
	axesIdx := strings.Index(rendered, sectionAxes)
	tokensIdx := strings.Index(rendered, sectionTokens)
	axesBlock := rendered[axesIdx:tokensIdx]
	if !strings.Contains(axesBlock, "Axis interaction:") {
		t.Fatalf("expected 'Axis interaction:' in AXES block, got:\n%s", axesBlock)
	}
}

// TestRenderPlainText_NoTaskSection specifies that the old TASK section is absent.
func TestRenderPlainText_NoTaskSection(t *testing.T) {
	result := &BuildResult{
		Task: "make something",
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "=== TASK 任務 (DO THIS) ===") {
		t.Fatalf("TASK section must be absent from redesigned output, got:\n%s", output)
	}
}

// TestRenderPlainText_NoExecutionReminderSection specifies that the EXECUTION REMINDER
// section is absent from the redesigned output (replaced by preamble).
func TestRenderPlainText_NoExecutionReminderSection(t *testing.T) {
	result := &BuildResult{
		Task:              "make something",
		ExecutionReminder: "some reminder",
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "=== EXECUTION REMINDER ===") {
		t.Fatalf("EXECUTION REMINDER section must be absent from redesigned output, got:\n%s", output)
	}
}

// TestRenderPlainText_NoPersonaSection specifies that the standalone PERSONA section
// is absent (persona folds into TOKENS + TOKEN DEFINITIONS).
func TestRenderPlainText_NoPersonaSection(t *testing.T) {
	result := &BuildResult{
		Task:    "make something",
		Persona: PersonaResult{Voice: "as teacher"},
		HydratedPersona: []HydratedPromptlet{
			{Axis: "voice", Token: "as teacher", Description: "Teaches."},
		},
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "=== PERSONA 人格 (STANCE) ===") {
		t.Fatalf("PERSONA section must be absent from redesigned output (persona folds into TOKENS), got:\n%s", output)
	}
}

// TestRenderPlainText_MetaInterpretationSection specifies that the META INTERPRETATION
// section is present in the render output when MetaInterpretationGuidance is set.
func TestRenderPlainText_MetaInterpretationSection(t *testing.T) {
	result := &BuildResult{
		Task:                       "make something",
		MetaInterpretationGuidance: "some guidance",
	}
	output := RenderPlainText(result)
	if !strings.Contains(output, "=== META INTERPRETATION ===") {
		t.Fatalf("META INTERPRETATION section must be present in render output, got:\n%s", output)
	}
	if !strings.Contains(output, "some guidance") {
		t.Fatalf("META INTERPRETATION section must contain guidance text, got:\n%s", output)
	}
}

// TestRenderPlainText_TokensSectionMultipleMethodTokens verifies that all tokens for an axis
// appear in the TOKENS section, not just the first.
func TestRenderPlainText_TokensSectionMultipleMethodTokens(t *testing.T) {
	result := &BuildResult{
		Task: "do something",
		HydratedConstraints: []HydratedPromptlet{
			{Axis: "method", Token: "ground", Description: "ground desc"},
			{Axis: "method", Token: "falsify", Description: "falsify desc"},
			{Axis: "method", Token: "atomic", Description: "atomic desc"},
		},
	}
	output := RenderPlainText(result)
	for _, tok := range []string{"ground", "falsify", "atomic"} {
		if !strings.Contains(output, "- method = "+tok) {
			t.Fatalf("TOKENS section missing '- method = %s', got:\n%s", tok, output)
		}
	}
}

// TestRenderPlainText_NoSubjectFraming specifies that the SubjectFraming prose block
// is absent from the redesigned output.
func TestRenderPlainText_NoSubjectFraming(t *testing.T) {
	result := &BuildResult{
		Task:           "make something",
		Subject:        "my input",
		SubjectFraming: "The section below contains the user's raw input text.",
	}
	output := RenderPlainText(result)
	if strings.Contains(output, "The section below contains the user's raw input text.") {
		t.Fatalf("SubjectFraming block must be absent from redesigned output, got:\n%s", output)
	}
}

// TestRenderPlainText_RequestMergesTaskAndSubject specifies that REQUEST section
// contains the task body merged with the subject (no separate TASK section).
func TestRenderPlainText_RequestMergesTaskAndSubject(t *testing.T) {
	result := &BuildResult{
		Task:    "Task:\n  Make a todo list.",
		Subject: "Fix onboarding flow",
	}
	output := RenderPlainText(result)
	requestIdx := strings.Index(output, "=== REQUEST 依頼 ===")
	formatIdx := strings.Index(output, "=== FORMAT")
	if requestIdx < 0 {
		t.Fatalf("expected REQUEST section in output, got:\n%s", output)
	}
	requestBlock := output[requestIdx:formatIdx]
	if !strings.Contains(requestBlock, "Make a todo list.") {
		t.Fatalf("REQUEST section must contain task body, got block:\n%s", requestBlock)
	}
	if !strings.Contains(requestBlock, "Fix onboarding flow") {
		t.Fatalf("REQUEST section must contain subject text, got block:\n%s", requestBlock)
	}
}

// TestCompositionRulesFetchHintFormat verifies that COMPOSITION RULES emits one fetch-hint
// line per active composition instead of inline prose.
func TestCompositionRulesFetchHintFormat(t *testing.T) {
	g := loadCompletionGrammar(t)
	result, cliErr := Build(g, []string{"make", "gate", "falsify"})
	if cliErr != nil {
		t.Fatalf("Build: %v", cliErr)
	}
	rendered := RenderPlainText(result)
	compIdx := strings.Index(rendered, sectionCompositionRules)
	if compIdx == -1 {
		t.Fatal("COMPOSITION RULES section must be present")
	}
	formatIdx := strings.Index(rendered, sectionFormat)
	compBlock := rendered[compIdx:formatIdx]
	if !strings.Contains(compBlock, "→ bar help composition gate+falsify") {
		t.Errorf("COMPOSITION RULES must contain fetch hint '→ bar help composition gate+falsify', got:\n%s", compBlock)
	}
	if strings.Contains(compBlock, "the blocking condition gate requires") {
		t.Errorf("COMPOSITION RULES must not contain inline prose, got:\n%s", compBlock)
	}
}

// TestCompositionRulesLoadedInstruction verifies that COMPOSITION RULES emits the Loaded: instruction.
func TestCompositionRulesLoadedInstruction(t *testing.T) {
	g := loadCompletionGrammar(t)
	result, cliErr := Build(g, []string{"make", "gate", "falsify"})
	if cliErr != nil {
		t.Fatalf("Build: %v", cliErr)
	}
	rendered := RenderPlainText(result)
	compIdx := strings.Index(rendered, sectionCompositionRules)
	if compIdx == -1 {
		t.Fatal("COMPOSITION RULES section must be present")
	}
	formatIdx := strings.Index(rendered, sectionFormat)
	compBlock := rendered[compIdx:formatIdx]
	if !strings.Contains(compBlock, "Loaded:") {
		t.Errorf("COMPOSITION RULES must contain 'Loaded:' fetch instruction, got:\n%s", compBlock)
	}
}
