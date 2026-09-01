package barcli

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

type buildRunResult struct {
	Stdout string
	Stderr string
	Exit   int
}

func runBuildCLI(t *testing.T, args []string, stdin *os.File) buildRunResult {
	t.Helper()

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run(args, stdin, stdout, stderr)

	if stdin != nil {
		stdin.Close()
	}

	return buildRunResult{Stdout: stdout.String(), Stderr: stderr.String(), Exit: exit}
}

// TestRunBuildHelpShowsUsage covers Ground H1a/H1b: `bar build --help` and `-h`
// print build usage and do not emit the "task is required" error.
func TestRunBuildHelpShowsUsage(t *testing.T) {
	for _, flag := range []string{"--help", "-h"} {
		r := runBuildCLI(t, []string{"build", flag}, nil)
		if r.Exit != 0 {
			t.Fatalf("%s: expected exit 0, got %d (stderr: %s)", flag, r.Exit, r.Stderr)
		}
		combined := r.Stdout + r.Stderr
		if strings.Contains(combined, "task is required") {
			t.Fatalf("%s: help must not emit 'task is required', got:\n%s", flag, combined)
		}
		if !strings.Contains(combined, "bar build") || !strings.Contains(combined, "--subject") {
			t.Fatalf("%s: expected build usage text (bar build ... --subject), got:\n%s", flag, combined)
		}
	}
}

// TestRunBuildTaskRequiredErrorOmitsDefaultCompleteness covers Ground E1: a bare
// `bar build` (no explicit completeness) must not claim "You provided: full".
func TestRunBuildTaskRequiredErrorOmitsDefaultCompleteness(t *testing.T) {
	r := runBuildCLI(t, []string{"build", "bullets"}, nil) // "bullets" is a form token, no task, no explicit completeness
	combined := r.Stdout + r.Stderr
	if !strings.Contains(combined, "task is required") {
		t.Fatalf("expected task-required error, got:\n%s", combined)
	}
	if strings.Contains(combined, "You provided: full") {
		t.Fatalf("error must not report the default 'full' completeness as user-provided, got:\n%s", combined)
	}
}

// TestRunBuildTaskRequiredErrorKeepsExplicitCompleteness covers Ground E2: an
// explicitly-typed completeness token still appears in "You provided:".
func TestRunBuildTaskRequiredErrorKeepsExplicitCompleteness(t *testing.T) {
	r := runBuildCLI(t, []string{"build", "deep"}, nil) // "deep" is an explicit completeness token, still no task
	combined := r.Stdout + r.Stderr
	if !strings.Contains(combined, "task is required") {
		t.Fatalf("expected task-required error, got:\n%s", combined)
	}
	if !strings.Contains(combined, "You provided: deep") {
		t.Fatalf("explicit completeness 'deep' should appear in You-provided, got:\n%s", combined)
	}
}

// TestRunBuildSeedWordsInjectsSection specifies that --seed-words N adds the
// LATERAL SEED section to stdout and echoes the resolved seed to stderr (P2a, P5),
// and that identical (seed, N) inputs are reproducible (P3).
func TestRunBuildSeedWordsInjectsSection(t *testing.T) {
	a := runBuildCLI(t, []string{"build", "make", "--seed-words", "2", "--seed", "42"}, nil)
	if a.Exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", a.Exit, a.Stderr)
	}
	if !strings.Contains(a.Stdout, "=== LATERAL SEED 種 ===") {
		t.Fatalf("expected LATERAL SEED section in stdout, got:\n%s", a.Stdout)
	}
	if !strings.Contains(a.Stderr, "42") || !strings.Contains(strings.ToLower(a.Stderr), "seed") {
		t.Fatalf("expected resolved seed echoed to stderr, got: %q", a.Stderr)
	}

	// Reproducible: same seed + N yields identical stdout.
	b := runBuildCLI(t, []string{"build", "make", "--seed-words", "2", "--seed", "42"}, nil)
	if a.Stdout != b.Stdout {
		t.Fatalf("same seed produced different stdout:\n--- A ---\n%s\n--- B ---\n%s", a.Stdout, b.Stdout)
	}
}

// TestRunBuildNoSeedWordsNoSection specifies that without --seed-words the
// output contains no LATERAL SEED section (Ground P1: N=0 unchanged).
func TestRunBuildNoSeedWordsNoSection(t *testing.T) {
	r := runBuildCLI(t, []string{"build", "make"}, nil)
	if strings.Contains(r.Stdout, "LATERAL SEED") {
		t.Fatalf("expected no LATERAL SEED section without --seed-words, got:\n%s", r.Stdout)
	}
}

func TestRunBuildWithInputFile(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	subjectDir := t.TempDir()
	subjectPath := filepath.Join(subjectDir, "subject.txt")
	if err := os.WriteFile(subjectPath, []byte("Subject from file\n"), 0o600); err != nil {
		t.Fatalf("write subject: %v", err)
	}

	result := runBuildCLI(t, []string{"build", "make", "struct", "--input", subjectPath}, nil)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "Subject from file") {
		t.Fatalf("expected stdout to include subject, got: %s", result.Stdout)
	}
}

func TestRunBuildWithStdin(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("stdin pipe detection is not stable on Windows in go test")
	}
	t.Setenv(disableStateEnv, "1")

	r, w, err := os.Pipe()
	if err != nil {
		t.Fatalf("pipe: %v", err)
	}
	if _, err := w.WriteString("Subject from pipe\n"); err != nil {
		t.Fatalf("write pipe: %v", err)
	}
	w.Close()

	result := runBuildCLI(t, []string{"build", "make"}, r)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "Subject from pipe") {
		t.Fatalf("expected stdout to include piped subject, got: %s", result.Stdout)
	}
}

func TestRunBuildWithOutputFile(t *testing.T) {
	t.Setenv(disableStateEnv, "1")
	outDir := t.TempDir()
	outPath := filepath.Join(outDir, "output.txt")

	result := runBuildCLI(t, []string{"build", "make", "--subject", "from subject", "--output", outPath}, nil)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", result.Exit, result.Stderr)
	}
	if result.Stdout != "" {
		t.Fatalf("expected stdout to be empty when writing to file, got: %s", result.Stdout)
	}
	payload, err := os.ReadFile(outPath)
	if err != nil {
		t.Fatalf("read output: %v", err)
	}
	if !strings.Contains(string(payload), "from subject") {
		t.Fatalf("expected output file to include subject, got: %s", payload)
	}
}

func TestRunBuildJSONOutput(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "make", "--subject", "json subject", "--json"}, nil)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", result.Exit, result.Stderr)
	}
	var payload map[string]any
	if err := json.Unmarshal([]byte(result.Stdout), &payload); err != nil {
		t.Fatalf("expected valid JSON output, got error %v: %s", err, result.Stdout)
	}
	subject, ok := payload["subject"].(string)
	if !ok || subject != "json subject" {
		t.Fatalf("expected JSON subject, got: %#v", payload["subject"])
	}
}

func TestRunBuildInvalidTokenError(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "does-not-exist"}, nil)

	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit with invalid token")
	}
	if !strings.Contains(strings.ToLower(result.Stderr), "unrecognized token") {
		t.Fatalf("expected unrecognized token error, got: %s", result.Stderr)
	}

}

func TestRunBuildInvalidTokenBackwardCompatibility(t *testing.T) {
	// Validate that the enhanced error format maintains backward compatibility
	// with tests that check for "unrecognized token" strings.
	t.Setenv(disableStateEnv, "1")

	tests := []struct {
		name         string
		args         []string
		expectInErr  []string
		expectNotErr []string
	}{
		{
			name: "invalid shorthand token contains basic error",
			args: []string{"build", "does-not-exist"},
			expectInErr: []string{
				"unrecognized token",
				"does-not-exist",
			},
		},
		{
			name: "invalid override token contains basic error",
			args: []string{"build", "method=does-not-exist"},
			expectInErr: []string{
				"unrecognized token",
				"does-not-exist",
			},
		},
		{
			name: "new enhanced features dont break old expectations",
			args: []string{"build", "xyz"},
			expectInErr: []string{
				"unrecognized token",
				"bar help tokens",
			},
			// Should NOT contain these legacy exact-match patterns
			expectNotErr: []string{
				"error: unrecognized token\n", // Old format was just one line
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := runBuildCLI(t, tt.args, nil)

			if result.Exit == 0 {
				t.Errorf("expected non-zero exit")
			}

			for _, expected := range tt.expectInErr {
				if !strings.Contains(result.Stderr, expected) {
					t.Errorf("expected stderr to contain %q\nGot:\n%s", expected, result.Stderr)
				}
			}

			for _, unexpected := range tt.expectNotErr {
				if strings.Contains(result.Stderr, unexpected) {
					t.Errorf("expected stderr NOT to contain %q\nGot:\n%s", unexpected, result.Stderr)
				}
			}
		})
	}
}

func TestRunBuildWithSubjectFlag(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "make", "--subject", "inline subject content"}, nil)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "inline subject content") {
		t.Fatalf("expected stdout to include subject from --subject flag, got: %s", result.Stdout)
	}
}

func TestRunBuildSubjectAndStdinConcatenated(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("stdin pipe detection is not stable on Windows in go test")
	}
	t.Setenv(disableStateEnv, "1")

	r, w, err := os.Pipe()
	if err != nil {
		t.Fatalf("pipe: %v", err)
	}
	if _, err := w.WriteString("piped content\n"); err != nil {
		t.Fatalf("write pipe: %v", err)
	}
	w.Close()

	result := runBuildCLI(t, []string{"build", "make", "--subject", "flag content"}, r)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0 when both --subject and stdin provided, got %d with stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "flag content") {
		t.Fatalf("expected stdout to include --subject content, got: %s", result.Stdout)
	}
	if !strings.Contains(result.Stdout, "piped content") {
		t.Fatalf("expected stdout to include stdin content, got: %s", result.Stdout)
	}
}

func TestRunBuildSubjectAndInputMutualExclusivity(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "make", "--subject", "inline", "--input", "file.txt"}, nil)

	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit when both --subject and --input provided")
	}
	if !strings.Contains(result.Stderr, "--subject and --input cannot be used together") {
		t.Fatalf("expected mutual exclusivity error, got: %s", result.Stderr)
	}
}

func TestRunBuildWithAddendumFlag(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "make", "--subject", "some content", "--addendum", "focus on security"}, nil)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stdout, "focus on security") {
		t.Fatalf("expected stdout to include addendum text, got: %s", result.Stdout)
	}
	// Addendum text is merged into REQUEST section in redesigned output.
	if !strings.Contains(result.Stdout, "=== REQUEST 依頼 ===") {
		t.Fatalf("expected REQUEST section heading in output, got: %s", result.Stdout)
	}
}

func TestRunBuildAddendumOmittedWhenEmpty(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "make", "--subject", "some content"}, nil)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", result.Exit, result.Stderr)
	}
	if strings.Contains(result.Stdout, "=== ADDENDUM 追加 (CLARIFICATION)") {
		t.Fatalf("expected no ADDENDUM section heading when flag not provided, got: %s", result.Stdout)
	}
}

func TestRunBuildAddendumInJSON(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "make", "--subject", "content", "--addendum", "clarify this", "--json"}, nil)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0, got %d with stderr: %s", result.Exit, result.Stderr)
	}
	var payload map[string]any
	if err := json.Unmarshal([]byte(result.Stdout), &payload); err != nil {
		t.Fatalf("expected valid JSON, got error %v: %s", err, result.Stdout)
	}
	addendum, ok := payload["addendum"].(string)
	if !ok || addendum != "clarify this" {
		t.Fatalf("expected JSON addendum field, got: %#v", payload["addendum"])
	}
}

func TestRunBuildPromptFlagRemoved(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "make", "--prompt", "some text"}, nil)

	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit when --prompt is used")
	}
	if !strings.Contains(result.Stderr, "--prompt flag has been removed") {
		t.Fatalf("expected removal error message, got: %s", result.Stderr)
	}
	if !strings.Contains(result.Stderr, "--subject") {
		t.Fatalf("expected migration guidance mentioning --subject, got: %s", result.Stderr)
	}
	if !strings.Contains(result.Stderr, "--addendum") {
		t.Fatalf("expected migration guidance mentioning --addendum, got: %s", result.Stderr)
	}
}

func TestRunBuildWarnsWhenStateWriteFails(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("file permission semantics differ on Windows")
	}

	root := t.TempDir()
	stateRoot := filepath.Join(root, "state-root")
	if err := os.Mkdir(stateRoot, 0o500); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	t.Setenv(configDirEnv, stateRoot)

	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"build", "make", "--subject", "warn subject"}, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected exit 0 even if state write fails, got %d: %s", exit, stderr.String())
	}
	if !strings.Contains(stderr.String(), "warning: failed to cache last build") {
		t.Fatalf("expected warning about caching last build, got: %s", stderr.String())
	}
}

func TestBuildErrorIncludesBNFGrammarHint(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "does-not-exist"}, nil)

	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit with invalid token")
	}
	if !strings.Contains(result.Stderr, "bar build make") {
		t.Errorf("expected BNF grammar hint containing 'bar build' in error, got:\n%s", result.Stderr)
	}
	if !strings.Contains(result.Stderr, "axis:token") {
		t.Errorf("expected BNF hint to show axis:token prefix form, got:\n%s", result.Stderr)
	}
}

func TestAxisAsFlagProducesRedirectHint(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "--channel"}, nil)

	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit with axis-as-flag")
	}
	if !strings.Contains(result.Stderr, "channel:<token>") {
		t.Errorf("expected redirect hint containing 'channel:<token>' in error, got:\n%s", result.Stderr)
	}
}

func TestAxisColonTokenScopedToNamedAxis(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	// channel:fog — fog is a directional token, not a channel token.
	// Should error scoped to "channel", not silently match directional:fog.
	result := runBuildCLI(t, []string{"build", "make", "channel:fog"}, nil)

	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit: 'fog' is not a channel token")
	}
	// Error must be scoped: "unrecognized token for channel"
	if !strings.Contains(result.Stderr, "unrecognized token for channel") {
		t.Errorf("expected scoped error 'unrecognized token for channel', got:\n%s", result.Stderr)
	}
}

func TestBuildPackNameExpandsToCommand(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	// "debug" is a starter pack → should expand, not error
	result := runBuildCLI(t, []string{"build", "debug"}, nil)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0 when pack name given, got %d\nstderr: %s", result.Exit, result.Stderr)
	}
	if !strings.Contains(result.Stderr, "Expanding pack: debug") {
		t.Errorf("expected 'Expanding pack: debug' on stderr, got:\n%s", result.Stderr)
	}
	if !strings.Contains(result.Stdout, "=== REQUEST 依頼 ===") {
		t.Errorf("expected prompt output after expansion, got:\n%s", result.Stdout)
	}
}

func TestBuildPackNameWithAdditionalTokensExpands(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	// "craft" is a starter pack; "aloud" is a valid axis token.
	// When combined, craft should expand and aloud should be included.
	result := runBuildCLI(t, []string{"build", "craft", "aloud"}, nil)

	if result.Exit != 0 {
		t.Fatalf("expected exit 0 when pack name given with additional tokens, got %d\nstderr: %s\nstdout: %s", result.Exit, result.Stderr, result.Stdout)
	}
	if !strings.Contains(result.Stderr, "Expanding pack: craft") {
		t.Errorf("expected 'Expanding pack: craft' on stderr, got:\n%s", result.Stderr)
	}
	if !strings.Contains(result.Stdout, "=== REQUEST 依頼 ===") {
		t.Errorf("expected prompt output after expansion, got:\n%s", result.Stdout)
	}
}

func TestStarterPackNamesDoNotCollideWithTokenNames(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	tokenNames := make(map[string]string) // name → "axis:name"
	for _, task := range grammar.GetAllTasks() {
		tokenNames[task] = "task:" + task
	}
	for _, axis := range grammar.GetAllAxisTokens() {
		tokenNames[axis] = axis
	}

	for _, pack := range grammar.StarterPacks {
		if where, collision := tokenNames[pack.Name]; collision {
			t.Errorf("starter pack %q collides with token %s — pack names must not shadow token names", pack.Name, where)
		}
	}
}

func TestPersonaAxisColonPrefixResolved(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	tests := []struct {
		name string
		args []string
	}{
		{"voice colon prefix", []string{"build", "make", "voice:as-teacher"}},
		{"audience colon prefix", []string{"build", "make", "audience:to-ceo"}},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := runBuildCLI(t, tt.args, nil)
			if result.Exit != 0 {
				t.Errorf("expected exit 0, got %d\nstderr: %s", result.Exit, result.Stderr)
			}
		})
	}
}

func TestPersonaAxisColonPrefixScopedError(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "make", "voice:nonexistent"}, nil)
	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit for unknown persona token")
	}
	if !strings.Contains(result.Stderr, "unrecognized token for voice") {
		t.Errorf("expected scoped error 'unrecognized token for voice', got:\n%s", result.Stderr)
	}
}
