package barcli

import (
	"encoding/json"
	"path/filepath"
	"strings"
	"testing"
)

func TestLoadGrammarDefaultsToEmbedded(t *testing.T) {
	t.Setenv(envGrammarPath, "")

	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	if grammar.SchemaVersion == "" {
		t.Fatal("expected embedded grammar to provide a schema version")
	}
	if desc := strings.TrimSpace(grammar.TaskDescription("make")); desc == "" {
		t.Fatal("expected embedded grammar to include make task description")
	}
}

// TestLoadGrammarHasReferenceKey specifies that the embedded grammar provides a
// non-empty ReferenceKey field (ADR-0131). This is the specifying validation for
// Loop 2: Grammar struct must map the reference_key JSON field.
func TestLoadGrammarHasReferenceKey(t *testing.T) {
	t.Setenv(envGrammarPath, "")

	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	if strings.TrimSpace(grammar.ReferenceKey) == "" {
		t.Fatal("expected embedded grammar to provide a non-empty ReferenceKey (ADR-0131)")
	}
}

// TestLoadGrammarHasMetaInterpretationGuidance specifies that the embedded
// grammar provides a non-empty MetaInterpretationGuidance field (ADR-0166).
func TestLoadGrammarHasMetaInterpretationGuidance(t *testing.T) {
	t.Setenv(envGrammarPath, "")

	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	if strings.TrimSpace(grammar.MetaInterpretationGuidance) == "" {
		t.Fatal("expected embedded grammar to provide a non-empty MetaInterpretationGuidance (ADR-0166)")
	}
	if !strings.Contains(grammar.MetaInterpretationGuidance, "Model interpretation") {
		t.Fatal("MetaInterpretationGuidance should reference the '## Model interpretation' heading (ADR-0166)")
	}
}

func TestEmbeddedGrammarUsesTaskKeys(t *testing.T) {
	data, err := embeddedGrammarBytes()
	if err != nil {
		t.Fatalf("read embedded grammar: %v", err)
	}
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(data, &raw); err != nil {
		t.Fatalf("unmarshal grammar: %v", err)
	}
	if _, ok := raw["tasks"]; !ok {
		t.Fatal("expected top-level 'tasks' key in grammar JSON (found 'static_prompts'?)")
	}
	if _, ok := raw["static_prompts"]; ok {
		t.Fatal("grammar JSON still contains deprecated 'static_prompts' key; rename to 'tasks'")
	}

	var hierarchy struct {
		Defaults map[string]json.RawMessage `json:"defaults"`
	}
	if err := json.Unmarshal(raw["hierarchy"], &hierarchy); err != nil {
		t.Fatalf("unmarshal hierarchy: %v", err)
	}
	if _, ok := hierarchy.Defaults["task"]; !ok {
		t.Fatal("expected 'task' key in hierarchy.defaults (found 'static_prompt'?)")
	}
	if _, ok := hierarchy.Defaults["static_prompt"]; ok {
		t.Fatal("hierarchy.defaults still contains deprecated 'static_prompt' key; rename to 'task'")
	}

	var slugs struct {
		Task json.RawMessage `json:"task"`
	}
	if err := json.Unmarshal(raw["slugs"], &slugs); err != nil {
		t.Fatalf("unmarshal slugs: %v", err)
	}
	if slugs.Task == nil {
		t.Fatal("expected 'task' key in slugs section (found 'static'?)")
	}
}

func TestLoadGrammarEnvOverrideMissingFile(t *testing.T) {
	missing := filepath.Join(t.TempDir(), "missing.json")
	t.Setenv(envGrammarPath, missing)

	_, err := LoadGrammar("")
	if err == nil {
		t.Fatal("expected error when BAR_GRAMMAR_PATH points at a missing file")
	}
	if !strings.Contains(err.Error(), "open grammar") {
		t.Fatalf("expected open grammar error, got %v", err)
	}
}

// TestTaskMetadataForReturnsStructuredFields specifies that TaskMetadataFor returns
// definition, heuristics, and distinctions for task tokens from the embedded grammar
// (ADR-0154 T-5: wire Go grammar.go structs and accessor).
func TestTaskMetadataForReturnsStructuredFields(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	meta := grammar.TaskMetadataFor("probe")
	if meta == nil {
		t.Fatal("TaskMetadataFor(probe) must not return nil")
	}
	if meta.Definition == "" {
		t.Error("probe definition must not be empty")
	}
	if len(meta.Heuristics) == 0 {
		t.Error("probe heuristics must not be empty")
	}
	if len(meta.Distinctions) == 0 {
		t.Error("probe distinctions must not be empty")
	}

	// fix must have probe in its distinctions (ADR-0154 Loop 5 review gap)
	fixMeta := grammar.TaskMetadataFor("fix")
	if fixMeta == nil {
		t.Fatal("TaskMetadataFor(fix) must not return nil")
	}
	foundProbe := false
	for _, d := range fixMeta.Distinctions {
		if d.Token == "probe" {
			foundProbe = true
			break
		}
	}
	if !foundProbe {
		t.Error("fix distinctions must include probe (fix=reformat, not debug)")
	}

	// nil for unknown token
	if grammar.TaskMetadataFor("nonexistent") != nil {
		t.Error("TaskMetadataFor(nonexistent) must return nil")
	}
}

// TestAxisMetadataForAccessorContract specifies T-2 pipeline wiring —
// AxisMetadataFor returns metadata for known populated axes and nil for unknown ones (ADR-0155 T-2/T-3).
func TestAxisMetadataForAccessorContract(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// Unknown axis/token must return nil safely (not panic).
	if grammar.AxisMetadataFor("nonexistent", "nonexistent") != nil {
		t.Error("AxisMetadataFor must return nil for unknown axis/token")
	}

	// completeness axis is populated (T-3): gist must have non-nil metadata.
	gistMeta := grammar.AxisMetadataFor("completeness", "gist")
	if gistMeta == nil {
		t.Fatal("AxisMetadataFor(completeness, gist) must not return nil after T-3 migration")
	}
	if gistMeta.Definition == "" {
		t.Error("completeness/gist definition must not be empty")
	}
	if len(gistMeta.Heuristics) == 0 {
		t.Error("completeness/gist heuristics must not be empty")
	}
}

// TestPersonaMetadataForNilSafety specifies T-1 pipeline wiring —
// PersonaMetadataFor is accessible and returns nil safely for unknown axis/token (ADR-0156 T-1).
func TestPersonaMetadataForNilSafety(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// Unknown axis/token must return nil safely (not panic).
	if grammar.PersonaMetadataFor("nonexistent", "nonexistent") != nil {
		t.Error("PersonaMetadataFor must return nil for unknown axis/token")
	}
	// Empty axis must return nil safely.
	if grammar.PersonaMetadataFor("", "token") != nil {
		t.Error("PersonaMetadataFor must return nil for empty axis")
	}
}


// TestPersonaMetadataForVoiceContent specifies T-2 — voice axis metadata populated (ADR-0156 T-2).
func TestPersonaMetadataForVoiceContent(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	voiceMeta := grammar.PersonaMetadataFor("voice", "as programmer")
	if voiceMeta == nil {
		t.Fatal("PersonaMetadataFor(voice, as programmer) must not return nil after T-2")
	}
	if voiceMeta.Definition == "" {
		t.Error("voice/as programmer definition must not be empty")
	}
	if len(voiceMeta.Heuristics) == 0 {
		t.Error("voice/as programmer heuristics must not be empty")
	}
	// as designer must distinguish from audience:to designer
	designerMeta := grammar.PersonaMetadataFor("voice", "as designer")
	if designerMeta == nil {
		t.Fatal("PersonaMetadataFor(voice, as designer) must not return nil after T-2")
	}
	designerDistinctions := make([]string, 0, len(designerMeta.Distinctions))
	for _, d := range designerMeta.Distinctions {
		designerDistinctions = append(designerDistinctions, d.Token)
	}
	found := false
	for _, tok := range designerDistinctions {
		if tok == "to designer" {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("voice/as designer must distinguish from audience:to designer; got distinctions: %v", designerDistinctions)
	}
}

// TestPersonaMetadataForAudienceContent specifies T-3 — audience axis populated (ADR-0156 T-3).
func TestPersonaMetadataForAudienceContent(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	managersMeta := grammar.PersonaMetadataFor("audience", "to managers")
	if managersMeta == nil {
		t.Fatal("PersonaMetadataFor(audience, to managers) must not return nil after T-3")
	}
	if len(managersMeta.Heuristics) == 0 {
		t.Error("audience/to managers heuristics must not be empty")
	}
	// to team must distinguish from to stakeholders
	teamMeta := grammar.PersonaMetadataFor("audience", "to team")
	if teamMeta == nil {
		t.Fatal("PersonaMetadataFor(audience, to team) must not return nil after T-3")
	}
	teamDistinctions := make([]string, 0)
	for _, d := range teamMeta.Distinctions {
		teamDistinctions = append(teamDistinctions, d.Token)
	}
	found := false
	for _, tok := range teamDistinctions {
		if tok == "to stakeholders" {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("audience/to team must distinguish from to stakeholders; got: %v", teamDistinctions)
	}
}

// TestPersonaMetadataForToneContent specifies T-4 — tone axis populated (ADR-0156 T-4).
func TestPersonaMetadataForToneContent(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	casuallyMeta := grammar.PersonaMetadataFor("tone", "casually")
	if casuallyMeta == nil {
		t.Fatal("PersonaMetadataFor(tone, casually) must not return nil after T-4")
	}
	if len(casuallyMeta.Heuristics) == 0 {
		t.Error("tone/casually heuristics must not be empty")
	}
	// gently must distinguish from kindly
	gentlyMeta := grammar.PersonaMetadataFor("tone", "gently")
	if gentlyMeta == nil {
		t.Fatal("PersonaMetadataFor(tone, gently) must not return nil after T-4")
	}
	found := false
	for _, d := range gentlyMeta.Distinctions {
		if d.Token == "kindly" {
			found = true
			break
		}
	}
	if !found {
		t.Error("tone/gently must distinguish from kindly")
	}
}

// TestPersonaMetadataForIntentContent specifies T-5 — intent axis populated (ADR-0156 T-5).
func TestPersonaMetadataForIntentContent(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	informMeta := grammar.PersonaMetadataFor("intent", "inform")
	if informMeta == nil {
		t.Fatal("PersonaMetadataFor(intent, inform) must not return nil after T-5")
	}
	if len(informMeta.Heuristics) == 0 {
		t.Error("intent/inform heuristics must not be empty")
	}
	// coach must distinguish from teach
	coachMeta := grammar.PersonaMetadataFor("intent", "coach")
	if coachMeta == nil {
		t.Fatal("PersonaMetadataFor(intent, coach) must not return nil after T-5")
	}
	found := false
	for _, d := range coachMeta.Distinctions {
		if d.Token == "teach" {
			found = true
			break
		}
	}
	if !found {
		t.Error("intent/coach must distinguish from teach")
	}
}

// TestPersonaMetadataForPresetsContent specifies T-6 — presets axis populated (ADR-0156 T-6).
func TestPersonaMetadataForPresetsContent(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	peerMeta := grammar.PersonaMetadataFor("presets", "peer_engineer_explanation")
	if peerMeta == nil {
		t.Fatal("PersonaMetadataFor(presets, peer_engineer_explanation) must not return nil after T-6")
	}
	if len(peerMeta.Heuristics) == 0 {
		t.Error("presets/peer_engineer_explanation heuristics must not be empty")
	}
	// executive_brief must distinguish from stakeholder_facilitator
	execMeta := grammar.PersonaMetadataFor("presets", "executive_brief")
	if execMeta == nil {
		t.Fatal("PersonaMetadataFor(presets, executive_brief) must not return nil after T-6")
	}
	found := false
	for _, d := range execMeta.Distinctions {
		if d.Token == "stakeholder_facilitator" {
			found = true
			break
		}
	}
	if !found {
		t.Error("presets/executive_brief must distinguish from stakeholder_facilitator")
	}
}

// TestADR0162GroundConsolidation specifies that observe and enforce are retired as
// method tokens and ground carries the full mandatory-advancement ladder (ADR-0162).
func TestADR0162GroundConsolidation(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}

	// observe and enforce must not exist as method tokens.
	methodTokens := grammar.AxisTokenSet("method")
	if _, ok := methodTokens["observe"]; ok {
		t.Error("method token 'observe' must be retired (ADR-0162)")
	}
	if _, ok := methodTokens["enforce"]; ok {
		t.Error("method token 'enforce' must be retired (ADR-0162)")
	}

	// ground must carry the full mandatory-advancement ladder.
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}
	for _, phrase := range []string{
		"prose",
		"executable validation",
		"validation run observation",
		"executable implementation",
		"observed running behavior",
		"every feasible rung",
	} {
		if !strings.Contains(groundDesc, phrase) {
			t.Errorf("ground description missing expected phrase %q (ADR-0162)", phrase)
		}
	}
}

// TestGroundIFormationPermittedPreManifest specifies that the ground definition
// permits observation of existing code or running behavior before the manifest
// when I cannot be declared from context alone (I-formation), while still
// prohibiting rung work and planning text pre-manifest.
func TestGroundIFormationPermittedPreManifest(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}
	for _, phrase := range []string{
		"I-formation",
		"observation of existing code",
	} {
		if !strings.Contains(groundDesc, phrase) {
			t.Errorf("ground boundary clause missing I-formation phrase %q", phrase)
		}
	}
	// The old blanket prohibition on all pre-manifest domain exploration must
	// not survive — it is replaced by the I-formation distinction.
	if strings.Contains(groundDesc, "state minimal assumptions and write it from I") {
		t.Error("ground boundary clause must not retain blanket 'state minimal assumptions' prohibition — replaced by I-formation distinction")
	}
}

// TestGroundMotivationalReframe specifies that ground explicitly reframes
// the cost model: the ladder is the shortest path to valid output, not the
// longest. Eagerness to implement is named as the primary failure mode.
func TestGroundMotivationalReframe(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}
	if !strings.Contains(groundDesc, "shortest path") {
		t.Error("ground must state that strict rung adherence is the shortest path to valid output")
	}
	if !strings.Contains(groundDesc, "primary failure mode") {
		t.Error("ground must name eagerness to implement as the primary failure mode")
	}
}

// TestGroundCompletenessTokensGovernDepthNotExistence specifies that ground
// defines how completeness tokens interact with the process: they govern
// depth within each rung, not whether rungs exist.
func TestGroundCompletenessTokensGovernDepthNotExistence(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}
	if !strings.Contains(groundDesc, "completeness governs rung depth, not rung existence") {
		t.Error("ground must state that completeness governs rung depth, not rung existence")
	}
}

// TestGroundExecutableValidationNoImplementation specifies that the ground
// definition explicitly prohibits producing implementation code at the
// executable validation rung — permission to write artifacts at R4 applies
// only to validation artifacts, not implementation.
func TestGroundExecutableValidationNoImplementation(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}
	if !strings.Contains(groundDesc, "implementation code is not permitted at this rung") {
		t.Error("ground must state that implementation code is not permitted at the executable validation rung")
	}
}

// TestGroundExecutableValidationRequiresRunnable specifies that the ground
// definition makes clear that executable validation must be a file artifact
// invocable by an automated tool — file reads, grep output, and manual
// inspection do not satisfy the rung regardless of label.
func TestGroundExecutableValidationRequiresRunnable(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}
	if !strings.Contains(groundDesc, "file reads") || !strings.Contains(groundDesc, "do not constitute executable validation") {
		t.Error("ground must state that file reads do not constitute executable validation")
	}
	if !strings.Contains(groundDesc, "automated tool") {
		t.Error("ground must state that executable validation requires an artifact invocable by an automated tool")
	}
}

// TestGroundR4GateEmphasis specifies that the ground definition makes the
// validation→implementation gate prominent by:
// (1) stating the blocking rule before the R4 sequence, not only in a
//     post-sequence parenthetical, and
// (2) explicitly marking the gate inside the R4 sequence itself so it reads
//     as a distinct step rather than one item in a flat arrow chain.
func TestGroundR4GateEmphasis(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}

	// The "may not be skipped or combined" rule must appear adjacent to R4.
	if !strings.Contains(groundDesc, "may not be skipped or combined") {
		t.Error("ground R4 section must state rungs may not be skipped or combined")
	}

	// The blocking rule must appear before the R4 sequence, not only after it.
	blockedIdx := strings.Index(groundDesc, "executable implementation rung is blocked")
	r4Idx := strings.Index(groundDesc, "R4 instantiates as")
	if blockedIdx == -1 {
		t.Fatal("ground must state that executable implementation rung is blocked until gap declared")
	}
	if r4Idx == -1 {
		t.Fatal("ground must contain R4 instantiation")
	}
	if blockedIdx > r4Idx {
		t.Error("blocking rule must appear before R4 instantiation, not only in the post-sequence parenthetical")
	}
}

// TestGroundRungLabelNotSectionHeading specifies that the ground definition
// distinguishes between a rung label in the manifest (a plan entry) and a rung
// label during execution (a marker that the artifact begins immediately). A rung
// label must not be used as a section heading for planning text or exploration.
func TestGroundRungLabelNotSectionHeading(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}
	if !strings.Contains(groundDesc, "rung label during execution") {
		t.Error("ground must distinguish rung labels during execution from manifest plan entries")
	}
}

// TestGroundImplementationGateBroadScope specifies that the ground definition
// gates all implementation artifact types — not just file-tool invocations —
// before valid execution sentinels. Planning text and code blocks are explicitly
// named as gated, closing the loophole where Thinking-block implementation
// content bypasses the gate.
func TestGroundImplementationGateBroadScope(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}
	// The gate must cover planning text and code blocks, not just file tool calls.
	for _, phrase := range []string{
		"planning text",
		"code blocks",
	} {
		if !strings.Contains(groundDesc, phrase) {
			t.Errorf("ground implementation gate missing broad-scope phrase %q — gate must cover all implementation artifact types", phrase)
		}
	}
	// The narrow gate (file tool calls only) must not be the primary statement.
	if strings.Contains(groundDesc, "no file-creating or file-editing tool call for an implementation rung may be invoked") {
		t.Error("ground implementation gate must not lead with file-tool-call-only scope — broader gate should be primary")
	}
}

// TestGroundDefinitionReverseCheck specifies that the ground definition includes the
// bidirectional obligation: when beginning at any rung, first locate the highest
// already-instantiated rung and update it before descending.
func TestGroundDefinitionReverseCheck(t *testing.T) {
	t.Setenv(envGrammarPath, "")
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load embedded grammar: %v", err)
	}
	groundDesc := grammar.AxisDescription("method", "ground")
	if groundDesc == "" {
		t.Fatal("ground description must not be empty")
	}
	for _, phrase := range []string{
		"highest already-instantiated",
		"then descend",
	} {
		if !strings.Contains(groundDesc, phrase) {
			t.Errorf("ground description missing reverse-check phrase %q", phrase)
		}
	}
}

func TestLoadGrammarExplicitPathOverridesEnv(t *testing.T) {
	missing := filepath.Join(t.TempDir(), "missing.json")
	t.Setenv(envGrammarPath, missing)

	overridePath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	if _, err := LoadGrammar(overridePath); err != nil {
		t.Fatalf("expected explicit path override to succeed, got %v", err)
	}
}
