package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

const (
	schemaRelativePath = "docs/schema/command-surface.json"
	runtimeName        = "go"
	executorName       = "compiled"
)

type healthPayload struct {
	Status     string `json:"status"`
	Version    string `json:"version"`
	Runtime    string `json:"runtime"`
	Executor   string `json:"executor"`
	BinaryPath string `json:"binary_path"`
}

func main() {
	os.Exit(run(os.Args[1:]))
}

func run(args []string) int {
	if len(args) == 0 {
		printUsage(os.Stdout)
		return 0
	}

	switch args[0] {
	case "--help", "-h":
		printUsage(os.Stdout)
		return 0
	case "--health":
		return runHealth()
	case "schema":
		return runSchema(args[1:])
	case "delegate":
		return runDelegate(args[1:])
	default:
		fmt.Fprintf(os.Stderr, "bar: unsupported command %s\n", strings.Join(args, " "))
		return 2
	}
}

func runHealth() int {
	root := repoRoot()
	payload := healthPayload{
		Status:     "ok",
		Version:    schemaVersion(root),
		Runtime:    runtimeName,
		Executor:   executorName,
		BinaryPath: runtimeBinaryPath(root),
	}

	if err := json.NewEncoder(os.Stdout).Encode(payload); err != nil {
		fmt.Fprintf(os.Stderr, "bar: failed to encode health payload: %v\n", err)
		return 1
	}

	return 0
}

func runSchema(args []string) int {
	if len(args) == 1 && (args[0] == "--help" || args[0] == "-h") {
		printSchemaUsage(os.Stdout)
		return 0
	}
	if len(args) > 0 {
		printSchemaUsage(os.Stderr)
		return 2
	}

	root := repoRoot()
	path := filepath.Join(root, schemaRelativePath)
	data, err := os.ReadFile(path)
	if errors.Is(err, fs.ErrNotExist) {
		fmt.Fprintf(os.Stderr, "bar: schema bundle missing at %s\n", path)
		return 1
	}
	if err != nil {
		fmt.Fprintf(os.Stderr, "bar: failed to read schema bundle: %v\n", err)
		return 1
	}

	if _, err := fmt.Fprint(os.Stdout, string(data)); err != nil {
		fmt.Fprintf(os.Stderr, "bar: failed to write schema bundle: %v\n", err)
		return 1
	}

	return 0
}

func runDelegate(args []string) int {
	if len(args) == 1 && (args[0] == "--help" || args[0] == "-h") {
		printDelegateUsage(os.Stdout)
		return 0
	}
	if len(args) > 0 {
		printDelegateUsage(os.Stderr)
		return 2
	}

	data, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "bar: failed to read request: %v\n", err)
		return 1
	}
	if len(strings.TrimSpace(string(data))) == 0 {
		fmt.Fprintln(os.Stderr, "bar: delegate requires JSON request on stdin")
		return 2
	}

	var request map[string]any
	if err := json.Unmarshal(data, &request); err != nil {
		fmt.Fprintf(os.Stderr, "bar: invalid request JSON: %v\n", err)
		return 1
	}

	promptPayload, ok := request["prompt"].(map[string]any)
	if !ok {
		fmt.Fprintln(os.Stderr, "bar: delegate requires prompt.text string")
		return 1
	}
	promptText, ok := promptPayload["text"].(string)
	if !ok || strings.TrimSpace(promptText) == "" {
		fmt.Fprintln(os.Stderr, "bar: delegate requires prompt.text string")
		return 1
	}

	result := map[string]any{
		"echo":       promptText,
		"echo_upper": strings.ToUpper(promptText),
	}

	response := map[string]any{
		"status":  "ok",
		"message": "CLI delegate processed request",
		"result":  result,
	}
	if requestID, ok := request["request_id"].(string); ok && strings.TrimSpace(requestID) != "" {
		response["request_id"] = requestID
	}

	if err := json.NewEncoder(os.Stdout).Encode(response); err != nil {
		fmt.Fprintf(os.Stderr, "bar: failed to encode delegate response: %v\n", err)
		return 1
	}

	return 0
}

func printUsage(out *os.File) {
	fmt.Fprintln(out, "usage: bar [--health] [schema] [delegate]")
}

func printSchemaUsage(out *os.File) {
	fmt.Fprintln(out, "usage: bar schema")
}

func printDelegateUsage(out *os.File) {
	fmt.Fprintln(out, "usage: bar delegate < request.json")
}

func repoRoot() string {
	if root := os.Getenv("BAR_ROOT"); root != "" {
		return root
	}

	wd, err := os.Getwd()
	if err != nil {
		return "."
	}

	current := wd
	for {
		candidate := filepath.Join(current, schemaRelativePath)
		if _, err := os.Stat(candidate); err == nil {
			return current
		}

		parent := filepath.Dir(current)
		if parent == current {
			return wd
		}
		current = parent
	}
}

func runtimeBinaryPath(root string) string {
	execPath, err := os.Executable()
	if err != nil {
		return "unknown"
	}

	if root != "" {
		if rel, relErr := filepath.Rel(root, execPath); relErr == nil {
			return filepath.ToSlash(rel)
		}
	}

	return filepath.ToSlash(execPath)
}

func schemaVersion(root string) string {
	path := filepath.Join(root, schemaRelativePath)
	data, err := os.ReadFile(path)
	if errors.Is(err, fs.ErrNotExist) {
		return "missing"
	}
	if err != nil {
		return "invalid"
	}

	var payload map[string]any
	if err := json.Unmarshal(data, &payload); err != nil {
		return "invalid"
	}

	version, ok := payload["version"]
	if !ok {
		return "unspecified"
	}

	return fmt.Sprint(version)
}
