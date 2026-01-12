package barcli

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"runtime"
	"sort"
	"strings"
	"time"

	"github.com/atotto/clipboard"
	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

var startTUI = defaultTUIStarter

func defaultTUIStarter(opts bartui.Options) error {
	program, err := bartui.NewProgram(opts)
	if err != nil {
		return err
	}
	return program.Start()
}

func runTUI(opts *cli.Config, stdin io.Reader, stdout, stderr io.Writer) int {
	if opts.JSON {
		writeError(stderr, "tui does not support --json output")
		return 1
	}
	if opts.Prompt != "" || opts.InputPath != "" {
		writeError(stderr, "tui captures subject input interactively; remove --prompt/--input")
		return 1
	}
	if opts.OutputPath != "" {
		writeError(stderr, "tui does not support --output")
		return 1
	}
	if opts.Force {
		writeError(stderr, "tui does not accept --force")
		return 1
	}

	var fixture *tuiFixture
	if opts.FixturePath != "" {
		loaded, err := loadTUIFixture(opts.FixturePath)
		if err != nil {
			writeError(stderr, fmt.Sprintf("load fixture: %v", err))
			return 1
		}
		fixture = loaded
	}

	grammar, err := LoadGrammar(opts.GrammarPath)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	tokenCategories := BuildTokenCategories(grammar)

	tokens := append([]string(nil), opts.Tokens...)
	if fixture != nil && len(fixture.Tokens) > 0 {
		tokens = append([]string(nil), fixture.Tokens...)
	}

	preview := func(subject string, tokenSet []string) (string, error) {
		result, buildErr := Build(grammar, tokenSet)
		if buildErr != nil {
			return "", fmt.Errorf("build prompt: %s", buildErr.Message)
		}
		result.Subject = subject
		result.PlainText = RenderPlainText(result)
		return result.PlainText, nil
	}

	if fixture != nil {

		subject := fixture.Subject
		view, previewText, snapErr := bartui.Snapshot(bartui.Options{
			Tokens:          tokens,
			TokenCategories: tokenCategories,
			Preview:         preview,
			InitialWidth:    opts.FixtureWidth,
			InitialHeight:   opts.FixtureHeight,
		}, subject)
		if snapErr != nil {
			writeError(stderr, fmt.Sprintf("render snapshot: %v", snapErr))
			return 1
		}

		if fixture.ExpectedPreview != "" && previewText != fixture.ExpectedPreview {
			diff := formatSnapshotDiff(fixture.ExpectedPreview, previewText)
			writeError(stderr, fmt.Sprintf("snapshot preview mismatch\n%s", diff))
			return 1
		}

		if fixture.ExpectedView != "" && view != fixture.ExpectedView {
			diff := formatSnapshotDiff(fixture.ExpectedView, view)
			writeError(stderr, fmt.Sprintf("snapshot view mismatch\n%s", diff))
			return 1
		}

		for _, expected := range fixture.ExpectViewContains {
			if !strings.Contains(view, expected) {
				writeError(stderr, fmt.Sprintf("snapshot missing expected content %q", expected))
				return 1
			}
		}

		if !strings.HasSuffix(view, "\n") {
			view += "\n"
		}
		if _, err := io.WriteString(stdout, view); err != nil {
			writeError(stderr, fmt.Sprintf("write snapshot: %v", err))
			return 1
		}
		return 0
	}

	envValues, missingEnv := opts.ResolveEnvValues()

	listPresetsFn := func() ([]bartui.PresetSummary, error) {
		summaries, err := listPresets()
		if err != nil {
			return nil, err
		}
		converted := make([]bartui.PresetSummary, 0, len(summaries))
		for _, summary := range summaries {
			converted = append(converted, bartui.PresetSummary{
				Name:     summary.Name,
				SavedAt:  summary.SavedAt,
				Static:   summary.Static,
				Voice:    summary.Voice,
				Audience: summary.Audience,
				Tone:     summary.Tone,
			})
		}
		return converted, nil
	}

	loadPresetFn := func(name string) (bartui.PresetDetails, error) {
		preset, _, err := loadPreset(name)
		if err != nil {
			return bartui.PresetDetails{}, err
		}
		return bartui.PresetDetails{
			Name:    preset.Name,
			Tokens:  append([]string(nil), preset.Tokens...),
			SavedAt: preset.SavedAt,
		}, nil
	}

	savePresetFn := func(name string, description string, tokenSet []string) (bartui.PresetDetails, error) {
		result, buildErr := Build(grammar, tokenSet)
		if buildErr != nil {
			return bartui.PresetDetails{}, buildErr
		}
		stored := storedBuild{
			Version: stateSchemaVersion,
			SavedAt: time.Now().UTC(),
			Result:  cloneBuildResult(result),
			Tokens:  append([]string(nil), tokenSet...),
		}
		stored.Result.Subject = ""
		stored.Result.PlainText = ""
		if _, err := savePreset(name, &stored, false); err != nil {
			return bartui.PresetDetails{}, err
		}
		return bartui.PresetDetails{
			Name:    name,
			Tokens:  append([]string(nil), tokenSet...),
			SavedAt: stored.SavedAt,
		}, nil
	}

	deletePresetFn := func(name string) error {
		_, err := deletePreset(name, true)
		return err
	}

	err = startTUI(bartui.Options{
		Tokens:          tokens,
		TokenCategories: tokenCategories,
		Input:           stdin,
		Output:          stdout,
		Preview:         preview,
		UseAltScreen:    !opts.NoAltScreen,
		ClipboardRead:   clipboard.ReadAll,
		ClipboardWrite:  clipboard.WriteAll,
		RunCommand: func(ctx context.Context, command string, stdin string, env map[string]string) (string, string, error) {
			return runShellCommand(ctx, command, stdin, env)
		},
		CommandTimeout: 15 * time.Second,
		AllowedEnv:     envValues,
		MissingEnv:     missingEnv,
		ListPresets:    listPresetsFn,
		LoadPreset:     loadPresetFn,
		SavePreset:     savePresetFn,
		DeletePreset:   deletePresetFn,
	})
	if err != nil {
		writeError(stderr, fmt.Sprintf("launch tui: %v", err))
		return 1
	}
	return 0
}

// SetTUIStarter overrides the Bubble Tea starter for testing. It returns a restore
// function that resets the previous starter when invoked. Passing nil restores the
// default starter immediately.
func SetTUIStarter(starter func(bartui.Options) error) func() {
	previous := startTUI
	if starter == nil {
		startTUI = defaultTUIStarter
	} else {
		startTUI = starter
	}
	return func() {
		startTUI = previous
	}
}

type tuiFixture struct {
	Tokens             []string `json:"tokens"`
	Subject            string   `json:"subject"`
	ExpectedPreview    string   `json:"expected_preview"`
	ExpectedView       string   `json:"expected_view"`
	ExpectViewContains []string `json:"expect_view_contains"`
}

func loadTUIFixture(path string) (*tuiFixture, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read fixture: %w", err)
	}
	var fixture tuiFixture
	if err := json.Unmarshal(data, &fixture); err != nil {
		return nil, fmt.Errorf("parse fixture: %w", err)
	}
	return &fixture, nil
}

func runShellCommand(ctx context.Context, command string, stdin string, env map[string]string) (string, string, error) {
	trimmed := strings.TrimSpace(command)
	if trimmed == "" {
		return "", "", fmt.Errorf("no command provided")
	}

	cmd := buildShellCommand(ctx, trimmed)
	if stdin != "" {
		cmd.Stdin = strings.NewReader(stdin)
	}

	cmd.Env = buildCommandEnvironment(env)

	var stdoutBuf, stderrBuf bytes.Buffer
	cmd.Stdout = &stdoutBuf
	cmd.Stderr = &stderrBuf

	err := cmd.Run()
	return stdoutBuf.String(), stderrBuf.String(), err
}

func formatSnapshotDiff(expected, actual string) string {
	if expected == actual {
		return "snapshots match"
	}

	expLines := strings.Split(expected, "\n")
	actLines := strings.Split(actual, "\n")
	max := len(expLines)
	if len(actLines) > max {
		max = len(actLines)
	}
	for i := 0; i < max; i++ {
		if i >= len(expLines) || i >= len(actLines) {
			return fmt.Sprintf("line count mismatch: expected %d lines, actual %d lines", len(expLines), len(actLines))
		}
		expLine := expLines[i]
		actLine := actLines[i]
		if expLine != actLine {
			return fmt.Sprintf("line %d:\n  expected: %q\n  actual:   %q", i+1, expLine, actLine)
		}
	}
	if len(expLines) != len(actLines) {
		return fmt.Sprintf("line count mismatch: expected %d lines, actual %d lines", len(expLines), len(actLines))
	}
	return "snapshot outputs differ"
}

func buildShellCommand(ctx context.Context, command string) *exec.Cmd {
	if runtime.GOOS == "windows" {
		return exec.CommandContext(ctx, "cmd", "/C", command)
	}
	return exec.CommandContext(ctx, "sh", "-c", command)
}

var defaultCommandEnvVars = []string{
	"HOME",
	"LANG",
	"LC_ALL",
	"LC_CTYPE",
	"PATH",
	"PWD",
	"SHELL",
	"TERM",
	"TMPDIR",
	"USER",
}

func buildCommandEnvironment(extra map[string]string) []string {
	base := make(map[string]string)
	for _, kv := range os.Environ() {
		parts := strings.SplitN(kv, "=", 2)
		if len(parts) != 2 {
			continue
		}
		base[parts[0]] = parts[1]
	}

	result := make(map[string]string)
	for _, key := range defaultCommandEnvVars {
		if value, ok := base[key]; ok {
			result[key] = value
		}
	}

	if extra != nil {
		for name, value := range extra {
			result[name] = value
		}
	}

	keys := make([]string, 0, len(result))
	for name := range result {
		keys = append(keys, name)
	}
	sort.Strings(keys)

	envList := make([]string, 0, len(keys))
	for _, name := range keys {
		envList = append(envList, name+"="+result[name])
	}
	return envList
}
