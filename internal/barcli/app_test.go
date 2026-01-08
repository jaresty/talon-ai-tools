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
	args := []string{"--grammar", grammarPath, "--json", "build", "todo", "focus", "fog", "persona-coach_junior", "intent-coach"}

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
	args := []string{"--grammar", grammarPath, "--json", "build", "persona-coach_junior", "persona-coach_junior"}

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
	if payload.Error.Recognized == nil {
		t.Fatal("expected recognized tokens to be recorded")
	}
	if vals := payload.Error.Recognized["persona_preset"]; len(vals) == 0 || vals[0] != "coach_junior" {
		t.Fatalf("expected persona preset recognized, got %+v", payload.Error.Recognized)
	}
	if len(payload.Error.Unrecognized) != 0 {
		t.Fatalf("expected no unrecognized tokens, got %+v", payload.Error.Unrecognized)
	}
}

func TestRunPlainTextFormatting(t *testing.T) {
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"--grammar", grammarPath, "build", "todo", "steps", "fly-rog", "persona-coach_junior"}

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

func TestRunConflictErrorSchema(t *testing.T) {
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"--grammar", grammarPath, "--json", "build", "todo", "todo"}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exitCode := Run(args, strings.NewReader(""), stdout, stderr)
	if exitCode == 0 {
		t.Fatal("expected conflict error exit code")
	}

	var payload struct {
		Error CLIError `json:"error"`
	}
	if err := json.Unmarshal(stdout.Bytes(), &payload); err != nil {
		t.Fatalf("failed to parse error JSON: %v", err)
	}
	if payload.Error.Type != errorConflict {
		t.Fatalf("expected conflict error, got %s", payload.Error.Type)
	}
	staticVals, ok := payload.Error.Recognized["static"]
	if !ok || len(staticVals) == 0 || staticVals[0] != "todo" {
		t.Fatalf("expected static token recognized, got %+v", payload.Error.Recognized)
	}
	if len(payload.Error.Unrecognized) != 0 {
		t.Fatalf("expected no unrecognized tokens, got %+v", payload.Error.Unrecognized)
	}
}

func TestRunFormatErrorSchema(t *testing.T) {
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"--grammar", grammarPath, "--json", "build", "scope="}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exitCode := Run(args, strings.NewReader(""), stdout, stderr)
	if exitCode == 0 {
		t.Fatal("expected format error exit code")
	}

	var payload struct {
		Error CLIError `json:"error"`
	}
	if err := json.Unmarshal(stdout.Bytes(), &payload); err != nil {
		t.Fatalf("failed to parse error JSON: %v", err)
	}
	if payload.Error.Type != errorFormat {
		t.Fatalf("expected format error, got %s", payload.Error.Type)
	}
	if payload.Error.Recognized == nil {
		t.Fatal("expected recognized map to be present even when empty")
	}
	if len(payload.Error.Recognized) != 0 {
		t.Fatalf("expected empty recognized map, got %+v", payload.Error.Recognized)
	}
}

func TestRunUnknownOverrideRecordsUnrecognized(t *testing.T) {
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"--grammar", grammarPath, "--json", "build", "todo", "foo=bar"}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exitCode := Run(args, strings.NewReader(""), stdout, stderr)
	if exitCode == 0 {
		t.Fatal("expected unknown token exit code")
	}

	var payload struct {
		Error CLIError `json:"error"`
	}
	if err := json.Unmarshal(stdout.Bytes(), &payload); err != nil {
		t.Fatalf("failed to parse error JSON: %v", err)
	}
	if payload.Error.Type != errorUnknownToken {
		t.Fatalf("expected unknown token error, got %s", payload.Error.Type)
	}
	if len(payload.Error.Unrecognized) != 1 || payload.Error.Unrecognized[0] != "foo=bar" {
		t.Fatalf("expected unrecognized token to be recorded, got %+v", payload.Error.Unrecognized)
	}
	staticVals, ok := payload.Error.Recognized["static"]
	if !ok || len(staticVals) == 0 || staticVals[0] != "todo" {
		t.Fatalf("expected static token recognized, got %+v", payload.Error.Recognized)
	}
}

func TestRunRejectsLabelInputPlain(t *testing.T) {
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"--grammar", grammarPath, "build", "todo", "as", "teacher"}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exitCode := Run(args, strings.NewReader(""), stdout, stderr)
	if exitCode == 0 {
		t.Fatalf("expected failure for label input, got exit code 0 (stderr=%s)", stderr.String())
	}
	if !strings.Contains(stderr.String(), "use slug") {
		t.Fatalf("expected slug error message, got %q", stderr.String())
	}
}

func TestRunRejectsLabelInputJSON(t *testing.T) {
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"--grammar", grammarPath, "--json", "build", "todo", "as", "teacher"}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exitCode := Run(args, strings.NewReader(""), stdout, stderr)
	if exitCode == 0 {
		t.Fatalf("expected failure for label input, got exit code 0 (stderr=%s)", stderr.String())
	}

	var payload struct {
		Error CLIError `json:"error"`
	}
	if err := json.Unmarshal(stdout.Bytes(), &payload); err != nil {
		t.Fatalf("failed to parse JSON error output: %v", err)
	}
	if payload.Error.Type != errorUnknownToken {
		t.Fatalf("expected unknown token error, got %s", payload.Error.Type)
	}
	if !strings.Contains(payload.Error.Message, "use slug") {
		t.Fatalf("expected slug error message, got %q", payload.Error.Message)
	}
}
