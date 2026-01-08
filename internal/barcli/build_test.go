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
		"steps",
		"fog",
		"persona=coach_junior",
		"intent=inform",
		"scope=focus system",
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

func TestBuildPresetConflict(t *testing.T) {
	grammar := loadTestGrammar(t)

	tokens := []string{"persona=coach_junior", "scope=focus", "persona=coach_junior"}

	_, cliErr := Build(grammar, tokens)
	if cliErr == nil {
		t.Fatal("expected preset conflict error")
	}
	if cliErr.Type != errorPresetConflict {
		t.Fatalf("expected error type %s, got %s", errorPresetConflict, cliErr.Type)
	}
}

func TestBuildHandlesMultiwordTokens(t *testing.T) {
	grammar := loadTestGrammar(t)

	tokens := []string{"todo", "focus", "steps", "fly", "rog", "as", "teacher", "to", "team", "kindly", "coach"}

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
