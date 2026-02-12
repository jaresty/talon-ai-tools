package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"testing"
	"time"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
	"github.com/talonvoice/talon-ai-tools/internal/bartui"
	"github.com/talonvoice/talon-ai-tools/internal/updater"
)

func TestTUICommandLaunchesProgram(t *testing.T) {
	restore := barcli.SetTUIStarter(func(opts bartui.Options) error {
		if !opts.UseAltScreen {
			t.Fatalf("expected alt screen to be enabled by default")
		}
		if opts.Preview == nil {
			t.Fatalf("expected preview function")
		}
		if opts.RunCommand == nil {
			t.Fatalf("expected run command function")
		}
		if opts.ClipboardRead == nil || opts.ClipboardWrite == nil {
			t.Fatalf("expected clipboard integration to be wired")
		}
		if opts.CommandTimeout != 15*time.Second {
			t.Fatalf("expected default command timeout, got %s", opts.CommandTimeout)
		}
		if len(opts.AllowedEnv) != 0 {
			t.Fatalf("expected no env allowlist by default, got %v", opts.AllowedEnv)
		}
		if len(opts.MissingEnv) != 0 {
			t.Fatalf("expected no missing env entries, got %v", opts.MissingEnv)
		}
		if _, _, err := opts.RunCommand(context.Background(), "", "", nil); err == nil {
			t.Fatalf("expected empty command to fail")
		}

		preview, err := opts.Preview("Example subject", opts.Tokens)
		if err != nil {
			t.Fatalf("preview returned error: %v", err)
		}
		if preview == "" {
			t.Fatalf("expected preview output")
		}
		return nil
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui", "make", "struct"}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected tui exit 0, got %d with stderr: %s", exit, stderr.String())
	}
}

func TestTUICommandRespectsNoAltScreen(t *testing.T) {
	restore := barcli.SetTUIStarter(func(opts bartui.Options) error {
		if opts.UseAltScreen {
			t.Fatalf("expected alt screen to be disabled when --no-alt-screen is used")
		}
		return nil
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui", "--no-alt-screen"}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected tui exit 0 with --no-alt-screen, got %d with stderr: %s", exit, stderr.String())
	}
}

func TestTUICommandRejectsJSONFlag(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui", "--json"}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected non-zero exit for --json flag")
	}
	if !strings.Contains(stderr.String(), "does not support --json") {
		t.Fatalf("expected error message about --json, got: %s", stderr.String())
	}
}

func TestTUICommandSurfacesProgramErrors(t *testing.T) {
	restore := barcli.SetTUIStarter(func(opts bartui.Options) error {
		return errors.New("boom")
	})
	defer restore()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui"}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected non-zero exit when program fails")
	}
	if !strings.Contains(stderr.String(), "launch tui") {
		t.Fatalf("expected launch error message, got: %s", stderr.String())
	}
}

func TestTUIFixtureEmitsSnapshot(t *testing.T) {
	// Suppress background update check: redirect cache dir so no stale
	// "update available" notice leaks into stderr, and use a no-release
	// mock client so any live check also stays silent.
	t.Setenv("BAR_CONFIG_DIR", t.TempDir())
	barcli.SetUpdateClient(&updater.MockGitHubClient{Releases: nil})
	defer barcli.SetUpdateClient(nil)

	subject := "Smoke subject"
	tokens := []string{"make", "struct"}
	grammarPath := filepath.Join("testdata", "grammar.json")

	grammar, err := barcli.LoadGrammar(grammarPath)
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	preview := func(subj string, tokenSet []string) (string, error) {
		result, buildErr := barcli.Build(grammar, tokenSet)
		if buildErr != nil {
			return "", buildErr
		}
		result.Subject = subj
		result.PlainText = barcli.RenderPlainText(result)
		return result.PlainText, nil
	}

	view, previewText, err := bartui.Snapshot(bartui.Options{
		Tokens:          tokens,
		TokenCategories: barcli.BuildTokenCategories(grammar),
		Preview:         preview,
	}, subject)
	if err != nil {
		t.Fatalf("snapshot failed: %v", err)
	}
	if !strings.Contains(view, subject) {
		t.Fatalf("expected snapshot view to include subject %q, got view:\n%s", subject, view)
	}
	if testing.Verbose() {
		t.Logf("snapshot view:\n%s", view)
		t.Logf("snapshot view literal: %q", view)
	}

	fixture := struct {
		Tokens          []string `json:"tokens"`
		Subject         string   `json:"subject"`
		ExpectedPreview string   `json:"expected_preview"`
		ExpectedView    string   `json:"expected_view"`
	}{
		Tokens:          tokens,
		Subject:         subject,
		ExpectedPreview: previewText,
		ExpectedView:    view,
	}

	data, err := json.MarshalIndent(fixture, "", "  ")
	if err != nil {
		t.Fatalf("failed to marshal fixture: %v", err)
	}

	dir := t.TempDir()
	fixturePath := filepath.Join(dir, "fixture.json")
	if err := os.WriteFile(fixturePath, data, 0o600); err != nil {
		t.Fatalf("failed to write fixture: %v", err)
	}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", fixturePath}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected fixture run exit 0, got %d with stderr: %s", exit, stderr.String())
	}

	if stderr.Len() != 0 {
		t.Fatalf("expected no stderr output, got: %s", stderr.String())
	}

	if stdout.String() != view {
		t.Fatalf("expected fixture view output to match snapshot\n--- expected ---\n%s\n--- actual ---\n%s", view, stdout.String())
	}

	stdout.Reset()
	stderr.Reset()
	repoFixture := filepath.Join("testdata", "tui_smoke.json")
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", repoFixture}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected repository fixture run exit 0, got %d with stderr: %s", exit, stderr.String())
	}
	if stdout.String() != view {
		t.Fatalf("expected repository fixture output to match snapshot\n--- expected ---\n%s\n--- actual ---\n%s", view, stdout.String())
	}
}

func TestTUIFixtureWidthFlagAdjustsSnapshot(t *testing.T) {
	subject := "Smoke subject"
	tokens := []string{"make", "struct"}
	grammarPath := filepath.Join("testdata", "grammar.json")

	grammar, err := barcli.LoadGrammar(grammarPath)
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	preview := func(subj string, tokenSet []string) (string, error) {
		result, buildErr := barcli.Build(grammar, tokenSet)
		if buildErr != nil {
			return "", buildErr
		}
		result.Subject = subj
		result.PlainText = barcli.RenderPlainText(result)
		return result.PlainText, nil
	}

	defaultView, _, err := bartui.Snapshot(bartui.Options{
		Tokens:          tokens,
		TokenCategories: barcli.BuildTokenCategories(grammar),
		Preview:         preview,
	}, subject)
	if err != nil {
		t.Fatalf("default snapshot failed: %v", err)
	}

	const width = 40
	narrowView, narrowPreview, err := bartui.Snapshot(bartui.Options{
		Tokens:          tokens,
		TokenCategories: barcli.BuildTokenCategories(grammar),
		Preview:         preview,
		InitialWidth:    width,
	}, subject)
	if err != nil {
		t.Fatalf("narrow snapshot failed: %v", err)
	}
	if narrowView == defaultView {
		t.Fatalf("expected narrow snapshot to differ from default width view")
	}

	const height = 12
	shortView, shortPreview, err := bartui.Snapshot(bartui.Options{
		Tokens:          tokens,
		TokenCategories: barcli.BuildTokenCategories(grammar),
		Preview:         preview,
		InitialHeight:   height,
	}, subject)
	if err != nil {
		t.Fatalf("short snapshot failed: %v", err)
	}
	if shortView == defaultView {
		t.Fatalf("expected height-adjusted snapshot to differ from default view")
	}

	fixture := struct {
		Tokens          []string `json:"tokens"`
		Subject         string   `json:"subject"`
		ExpectedPreview string   `json:"expected_preview"`
		ExpectedView    string   `json:"expected_view"`
	}{
		Tokens:          tokens,
		Subject:         subject,
		ExpectedPreview: narrowPreview,
		ExpectedView:    narrowView,
	}

	data, err := json.MarshalIndent(fixture, "", "  ")
	if err != nil {
		t.Fatalf("failed to marshal narrow fixture: %v", err)
	}

	dir := t.TempDir()
	fixturePath := filepath.Join(dir, "fixture.json")
	if err := os.WriteFile(fixturePath, data, 0o600); err != nil {
		t.Fatalf("failed to write narrow fixture: %v", err)
	}

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", fixturePath}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected width mismatch to fail without --fixture-width")
	}
	if !strings.Contains(stderr.String(), "snapshot view mismatch") {
		t.Fatalf("expected snapshot mismatch error without width flag, got: %s", stderr.String())
	}

	stdout.Reset()
	stderr.Reset()
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", fixturePath, "--fixture-width", "0"}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected zero width to fail validation")
	}
	if !strings.Contains(stderr.String(), "positive integer") {
		t.Fatalf("expected zero width error, got: %s", stderr.String())
	}

	stdout.Reset()
	stderr.Reset()
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", fixturePath, "--width", "0"}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected zero width via alias to fail validation")
	}
	if !strings.Contains(stderr.String(), "positive integer") {
		t.Fatalf("expected zero width alias error, got: %s", stderr.String())
	}

	stdout.Reset()
	stderr.Reset()
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", fixturePath, "--fixture-width", strconv.Itoa(width)}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected width-adjusted fixture run exit 0, got %d with stderr: %s", exit, stderr.String())
	}
	if stdout.String() != narrowView {
		t.Fatalf("expected width-adjusted fixture output to match narrow snapshot\n--- expected ---\n%s\n--- actual ---\n%s", narrowView, stdout.String())
	}

	stdout.Reset()
	stderr.Reset()
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", fixturePath, "--width", strconv.Itoa(width)}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected width alias to succeed, got %d with stderr: %s", exit, stderr.String())
	}
	if stdout.String() != narrowView {
		t.Fatalf("expected width alias output to match narrow snapshot\n--- expected ---\n%s\n--- actual ---\n%s", narrowView, stdout.String())
	}

	heightFixture := struct {
		Tokens          []string `json:"tokens"`
		Subject         string   `json:"subject"`
		ExpectedPreview string   `json:"expected_preview"`
		ExpectedView    string   `json:"expected_view"`
	}{
		Tokens:          tokens,
		Subject:         subject,
		ExpectedPreview: shortPreview,
		ExpectedView:    shortView,
	}

	heightData, err := json.MarshalIndent(heightFixture, "", "  ")
	if err != nil {
		t.Fatalf("failed to marshal height fixture: %v", err)
	}

	heightFixturePath := filepath.Join(dir, "fixture_height.json")
	if err := os.WriteFile(heightFixturePath, heightData, 0o600); err != nil {
		t.Fatalf("failed to write height fixture: %v", err)
	}

	stdout.Reset()
	stderr.Reset()
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", heightFixturePath}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected height mismatch to fail without --fixture-height")
	}
	if !strings.Contains(stderr.String(), "snapshot view mismatch") {
		t.Fatalf("expected snapshot mismatch for height fixture, got: %s", stderr.String())
	}

	stdout.Reset()
	stderr.Reset()
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", heightFixturePath, "--fixture-height", "0"}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected zero height to fail validation")
	}
	if !strings.Contains(stderr.String(), "positive integer") {
		t.Fatalf("expected zero height error, got: %s", stderr.String())
	}

	stdout.Reset()
	stderr.Reset()
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", heightFixturePath, "--height", "0"}, strings.NewReader(""), stdout, stderr)
	if exit == 0 {
		t.Fatalf("expected zero height alias to fail validation")
	}
	if !strings.Contains(stderr.String(), "positive integer") {
		t.Fatalf("expected zero height alias error, got: %s", stderr.String())
	}

	stdout.Reset()
	stderr.Reset()
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", heightFixturePath, "--fixture-height", strconv.Itoa(height)}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected height-adjusted fixture run exit 0, got %d with stderr: %s", exit, stderr.String())
	}
	if stdout.String() != shortView {
		t.Fatalf("expected height-adjusted fixture output to match short snapshot\n--- expected ---\n%s\n--- actual ---\n%s", shortView, stdout.String())
	}

	stdout.Reset()
	stderr.Reset()
	exit = barcli.Run([]string{"tui", "--grammar", grammarPath, "--fixture", heightFixturePath, "--height", strconv.Itoa(height)}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected height alias run exit 0, got %d with stderr: %s", exit, stderr.String())
	}
	if stdout.String() != shortView {
		t.Fatalf("expected height alias output to match short snapshot\n--- expected ---\n%s\n--- actual ---\n%s", shortView, stdout.String())
	}
}
