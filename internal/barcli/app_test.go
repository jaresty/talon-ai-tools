package barcli

import (
	"bytes"
	"encoding/json"
	"path/filepath"
	"strings"
	"testing"
)

func TestRunJSONOutput(t *testing.T) {
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"--grammar", grammarPath, "--json", "build", "todo", "focus", "fog", "persona=coach_junior", "intent=coach"}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exitCode := Run(args, strings.NewReader(""), stdout, stderr)
	if exitCode != 0 {
		t.Fatalf("expected exit code 0, got %d (%s)", exitCode, stderr.String())
	}

	var payload BuildResult
	if err := json.Unmarshal(stdout.Bytes(), &payload); err != nil {
		t.Fatalf("failed to parse JSON output: %v", err)
	}
	if payload.Axes.Static != "todo" {
		t.Fatalf("expected static todo, got %q", payload.Axes.Static)
	}
	if payload.Persona.Preset != "coach_junior" {
		t.Fatalf("expected preset coach_junior, got %q", payload.Persona.Preset)
	}
	if payload.Persona.Intent != "coach" {
		t.Fatalf("expected intent coach, got %q", payload.Persona.Intent)
	}
	if len(payload.Constraints) == 0 {
		t.Fatal("expected hydrated constraint strings")
	}
	joined := strings.Join(payload.Constraints, "\n")
	if !strings.Contains(joined, "The response provides") {
		t.Fatalf("expected descriptive promptlets, got %q", joined)
	}
	if len(payload.HydratedConstraints) == 0 {
		t.Fatal("expected structured hydrated constraints")
	}
}

func TestRunErrorJSON(t *testing.T) {
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"--grammar", grammarPath, "--json", "build", "persona=coach_junior", "persona=coach_junior"}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exitCode := Run(args, strings.NewReader(""), stdout, stderr)
	if exitCode == 0 {
		t.Fatal("expected non-zero exit code")
	}

	var payload struct {
		Error CLIError `json:"error"`
	}
	if err := json.Unmarshal(stdout.Bytes(), &payload); err != nil {
		t.Fatalf("failed to parse error JSON: %v", err)
	}
	if payload.Error.Type != errorPresetConflict {
		t.Fatalf("expected error type %s, got %s", errorPresetConflict, payload.Error.Type)
	}
}

func TestRunPlainTextFormatting(t *testing.T) {
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"--grammar", grammarPath, "build", "todo", "steps", "fly", "rog", "persona=coach_junior"}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exitCode := Run(args, strings.NewReader("Fix onboarding"), stdout, stderr)
	if exitCode != 0 {
		t.Fatalf("expected exit code 0, got %d (%s)", exitCode, stderr.String())
	}

	out := stdout.String()
	markers := []string{"=== TASK (DO THIS) ===", "=== CONSTRAINTS (GUARDRAILS) ===", "=== PERSONA (STANCE) ===", "=== SUBJECT (CONTEXT) ==="}
	for _, marker := range markers {
		if !strings.Contains(out, marker) {
			t.Fatalf("expected CLI output to contain %q, got:\n%s", marker, out)
		}
	}
}
