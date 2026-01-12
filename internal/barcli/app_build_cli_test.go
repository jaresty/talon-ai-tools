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

	result := runBuildCLI(t, []string{"build", "todo", "focus", "--input", subjectPath}, nil)

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

	result := runBuildCLI(t, []string{"build", "todo"}, r)

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

	result := runBuildCLI(t, []string{"build", "todo", "--prompt", "from prompt", "--output", outPath}, nil)

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
	if !strings.Contains(string(payload), "from prompt") {
		t.Fatalf("expected output file to include prompt, got: %s", payload)
	}
}

func TestRunBuildJSONOutput(t *testing.T) {
	t.Setenv(disableStateEnv, "1")

	result := runBuildCLI(t, []string{"build", "todo", "--prompt", "json subject", "--json"}, nil)

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
	exit := Run([]string{"build", "todo", "--prompt", "warn subject"}, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected exit 0 even if state write fails, got %d: %s", exit, stderr.String())
	}
	if !strings.Contains(stderr.String(), "warning: failed to cache last build") {
		t.Fatalf("expected warning about caching last build, got: %s", stderr.String())
	}
}
