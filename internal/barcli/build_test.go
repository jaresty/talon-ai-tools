package barcli

import (
	"path/filepath"
	"strings"
	"testing"
)

func loadTestGrammar(t *testing.T) *Grammar {
	t.Helper()
	path := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	grammar, err := LoadGrammar(path)
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	return grammar
}

func TestBuildWithShorthandAndOverrides(t *testing.T) {
	grammar := loadTestGrammar(t)

	tokens := []string{
		"todo",
		"focus",
		"system",
		"steps",
		"fog",
		"persona-coach_junior",
		"intent-inform",
	}

	result, cliErr := Build(grammar, tokens)
	if cliErr != nil {
		t.Fatalf("build returned error: %v", cliErr)
	}

	if result.Axes.Static != "todo" {
		t.Fatalf("expected static todo, got %q", result.Axes.Static)
	}
	if result.Axes.Completeness != "full" {
		t.Fatalf("expected default completeness full, got %q", result.Axes.Completeness)
	}
	if len(result.Axes.Scope) != 2 || result.Axes.Scope[0] != "focus" || result.Axes.Scope[1] != "system" {
		t.Fatalf("unexpected scope %+v", result.Axes.Scope)
	}
	if result.Axes.Directional != "fog" {
		t.Fatalf("expected directional fog, got %q", result.Axes.Directional)
	}
	if result.Persona.Preset != "coach_junior" {
		t.Fatalf("expected preset coach_junior, got %q", result.Persona.Preset)
	}
	if result.Persona.Voice != "as teacher" {
		t.Fatalf("expected persona voice from preset, got %q", result.Persona.Voice)
	}
	if result.Persona.Intent != "inform" {
		t.Fatalf("expected persona intent override inform, got %q", result.Persona.Intent)
	}

	if result.Task == "" {
		t.Fatal("expected task description")
	}

	if len(result.Constraints) == 0 {
		t.Fatal("expected hydrated constraints")
	}
	joined := strings.Join(result.Constraints, "\n")
	if !strings.Contains(joined, "Completeness (full)") {
		t.Fatalf("expected completeness promptlet, got %q", joined)
	}
	if !strings.Contains(joined, "Scope (focus)") {
		t.Fatalf("expected scope promptlet, got %q", joined)
	}

	if len(result.HydratedConstraints) < 3 {
		t.Fatalf("expected multiple hydrated constraints, got %d", len(result.HydratedConstraints))
	}

	if result.Persona.PresetLabel == "" {
		t.Fatal("expected persona preset label to be populated")
	}
	if len(result.HydratedPersona) == 0 {
		t.Fatal("expected hydrated persona promptlets")
	}
}

func TestBuildIgnoresSkipTokens(t *testing.T) {
	grammar := loadTestGrammar(t)

	tokens := []string{
		skipValue("persona"),
		"todo",
		"full",
		skipValue("method"),
		skipValue("scope"),
		"checklist",
		"slack",
	}

	result, cliErr := Build(grammar, tokens)
	if cliErr != nil {
		t.Fatalf("unexpected error: %v", cliErr)
	}

	if result.Axes.Static != "todo" {
		t.Fatalf("expected static todo, got %q", result.Axes.Static)
	}
	if result.Axes.Completeness != "full" {
		t.Fatalf("expected completeness full, got %q", result.Axes.Completeness)
	}
	if len(result.Axes.Method) != 0 {
		t.Fatalf("expected method axis to remain empty after skip, got %+v", result.Axes.Method)
	}
	if len(result.Axes.Scope) != 0 {
		t.Fatalf("expected scope axis to remain empty after skip, got %+v", result.Axes.Scope)
	}
	if len(result.Axes.Form) != 1 || result.Axes.Form[0] != "checklist" {
		t.Fatalf("expected form checklist, got %+v", result.Axes.Form)
	}
	if len(result.Axes.Channel) != 1 || result.Axes.Channel[0] != "slack" {
		t.Fatalf("expected channel slack, got %+v", result.Axes.Channel)
	}
	if result.Persona != (PersonaResult{}) {
		t.Fatalf("expected persona to remain empty after skip tokens, got %+v", result.Persona)
	}
}

func TestBuildBareSkipDefaultsToPersonaStage(t *testing.T) {
	grammar := loadTestGrammar(t)

	tokens := []string{
		skipSectionPrefix,
		"todo",
		"focus",
		"steps",
	}

	result, cliErr := Build(grammar, tokens)
	if cliErr != nil {
		t.Fatalf("unexpected error: %v", cliErr)
	}

	if result.Persona != (PersonaResult{}) {
		t.Fatalf("expected persona to remain empty after bare skip, got %+v", result.Persona)
	}
	if result.Axes.Static != "todo" {
		t.Fatalf("expected static todo, got %q", result.Axes.Static)
	}
	if len(result.Axes.Scope) != 1 || result.Axes.Scope[0] != "focus" {
		t.Fatalf("expected scope focus, got %+v", result.Axes.Scope)
	}
	if len(result.Axes.Method) != 1 || result.Axes.Method[0] != "steps" {
		t.Fatalf("expected method steps, got %+v", result.Axes.Method)
	}
}

func TestBuildPresetConflict(t *testing.T) {
	grammar := loadTestGrammar(t)

	tokens := []string{"persona-coach_junior", "scope-focus", "persona-coach_junior"}

	_, cliErr := Build(grammar, tokens)
	if cliErr == nil {
		t.Fatal("expected preset conflict error")
	}
	if cliErr.Type != errorPresetConflict {
		t.Fatalf("expected error type %s, got %s", errorPresetConflict, cliErr.Type)
	}
}

func TestBuildAcceptsCanonicalOverrideValues(t *testing.T) {
	grammar := loadTestGrammar(t)

	tokens := []string{"todo", "scope=focus", "method=steps"}

	result, cliErr := Build(grammar, tokens)
	if cliErr != nil {
		t.Fatalf("unexpected error: %v", cliErr)
	}

	if len(result.Axes.Scope) != 1 || result.Axes.Scope[0] != "focus" {
		t.Fatalf("expected scope override to hydrate focus, got %+v", result.Axes.Scope)
	}
	if len(result.Axes.Method) != 1 || result.Axes.Method[0] != "steps" {
		t.Fatalf("expected method override to hydrate steps, got %+v", result.Axes.Method)
	}
}

func TestBuildHandlesMultiwordTokens(t *testing.T) {
	grammar := loadTestGrammar(t)

	tokens := []string{"todo", "focus", "steps", "fly-rog", "as-teacher", "to-team", "kindly", "coach"}

	result, cliErr := Build(grammar, tokens)
	if cliErr != nil {
		t.Fatalf("unexpected error: %v", cliErr)
	}

	if result.Axes.Directional != "fly rog" {
		t.Fatalf("expected directional 'fly rog', got %q", result.Axes.Directional)
	}
	if !strings.Contains(strings.Join(result.Constraints, "\n"), "Directional (fly rog)") {
		t.Fatalf("expected hydrated directional constraint, got %q", result.Constraints)
	}

	if result.Persona.Voice != "as teacher" {
		t.Fatalf("expected persona voice 'as teacher', got %q", result.Persona.Voice)
	}
	if result.Persona.Audience != "to team" {
		t.Fatalf("expected persona audience 'to team', got %q", result.Persona.Audience)
	}
	if result.Persona.Tone != "kindly" {
		t.Fatalf("expected persona tone 'kindly', got %q", result.Persona.Tone)
	}
	if result.Persona.Intent != "coach" {
		t.Fatalf("expected persona intent 'coach', got %q", result.Persona.Intent)
	}
}
