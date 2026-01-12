package barcli

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

type tuiFixtureFile struct {
	Tokens          []string `json:"tokens"`
	Subject         string   `json:"subject"`
	ExpectedPreview string   `json:"expected_preview"`
	ExpectedView    string   `json:"expected_view"`
}

func loadSmokeFixture(t *testing.T) tuiFixtureFile {
	t.Helper()
	data, err := os.ReadFile(filepath.Join("..", "..", "cmd", "bar", "testdata", "tui_smoke.json"))
	if err != nil {
		t.Fatalf("read fixture: %v", err)
	}
	var fixture tuiFixtureFile
	if err := json.Unmarshal(data, &fixture); err != nil {
		t.Fatalf("parse fixture: %v", err)
	}
	return fixture
}

func TestRunTUIRejectsJSON(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"tui", "--json"}, os.Stdin, stdout, stderr)

	if exit == 0 {
		t.Fatalf("expected non-zero exit when --json is passed to tui")
	}
	if stdout.Len() != 0 {
		t.Fatalf("expected no stdout, got: %s", stdout.String())
	}
	if !bytes.Contains(stderr.Bytes(), []byte("does not support --json")) {
		t.Fatalf("expected --json error, got: %s", stderr.String())
	}
}

func TestRunTUIFixtureOutputsSnapshot(t *testing.T) {
	fixture := loadSmokeFixture(t)

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	fixturePath := filepath.Join("..", "..", "cmd", "bar", "testdata", "tui_smoke.json")
	args := []string{"tui", "--grammar", grammarPath, "--fixture", fixturePath}

	exit := Run(args, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected fixture run exit 0, got %d with stderr: %s", exit, stderr.String())
	}
	if stdout.String() != fixture.ExpectedView {
		t.Fatalf("expected fixture output to match stored view\n--- expected ---\n%s\n--- actual ---\n%s", fixture.ExpectedView, stdout.String())
	}
}

func TestRunTUIFixtureMismatchTriggersError(t *testing.T) {
	dir := t.TempDir()
	// Copy smoke fixture but tweak expected view.
	smoke := loadSmokeFixture(t)
	smoke.ExpectedView = "mismatched view"
	payload, err := json.MarshalIndent(smoke, "", "  ")
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	fixturePath := filepath.Join(dir, "fixture.json")
	if err := os.WriteFile(fixturePath, payload, 0o600); err != nil {
		t.Fatalf("write fixture: %v", err)
	}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	grammarPath := filepath.Join("..", "..", "cmd", "bar", "testdata", "grammar.json")
	args := []string{"tui", "--grammar", grammarPath, "--fixture", fixturePath}

	exit := Run(args, os.Stdin, stdout, stderr)

	if exit == 0 {
		t.Fatalf("expected non-zero exit for fixture mismatch")
	}
	if !bytes.Contains(stderr.Bytes(), []byte("snapshot view mismatch")) {
		t.Fatalf("expected mismatch error, got: %s", stderr.String())
	}
}

func TestRunTUILoadGrammarFailure(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"tui", "--grammar", filepath.Join(t.TempDir(), "missing.json")}, os.Stdin, stdout, stderr)

	if exit == 0 {
		t.Fatalf("expected non-zero exit for missing grammar")
	}
	if !bytes.Contains(stderr.Bytes(), []byte("no such file")) {
		t.Fatalf("expected file error, got: %s", stderr.String())
	}
}

func TestRunTUIEnvAllowlistMissingValues(t *testing.T) {
	captured := bartui.Options{}
	restore := SetTUIStarter(func(opts bartui.Options) error {
		captured = opts
		return nil
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"tui", "--env", "CHATGPT_API_KEY", "--no-alt-screen"}, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected tui run exit 0, got %d with stderr: %s", exit, stderr.String())
	}

	if len(captured.MissingEnv) != 1 || captured.MissingEnv[0] != "CHATGPT_API_KEY" {
		t.Fatalf("expected missing env to include CHATGPT_API_KEY, got: %v", captured.MissingEnv)
	}
	if captured.AllowedEnv["CHATGPT_API_KEY"] != "" {
		t.Fatalf("expected allowlist value to be empty for missing env, got: %v", captured.AllowedEnv)
	}
}
