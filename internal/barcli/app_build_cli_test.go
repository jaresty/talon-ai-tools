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

func TestRunBuildSubjectAndStdinMutualExclusivity(t *testing.T) {
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

	if result.Exit == 0 {
		t.Fatalf("expected non-zero exit when both --subject and stdin provided")
	}
	if !strings.Contains(result.Stderr, "cannot provide both --subject flag and stdin input") {
		t.Fatalf("expected mutual exclusivity error, got: %s", result.Stderr)
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
	if !strings.Contains(result.Stdout, "ADDENDUM 追加 (CLARIFICATION)") {
		t.Fatalf("expected ADDENDUM section heading in output, got: %s", result.Stdout)
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
