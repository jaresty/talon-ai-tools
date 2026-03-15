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
		"passing validation run",
		"executable implementation",
		"observed running behavior",
		"every feasible layer",
	} {
		if !strings.Contains(groundDesc, phrase) {
			t.Errorf("ground description missing expected phrase %q (ADR-0162)", phrase)
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
