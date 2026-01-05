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
	"time"
	"unicode/utf8"
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
	promptText, err := promptTextFromPayload(promptPayload)
	if err != nil {
		fmt.Fprintln(os.Stderr, err.Error())
		return 1
	}

	requestID := ensureRequestID(request)
	chunks := chunkPrompt(promptText)
	events := buildDelegateEvents(requestID, chunks)
	result := buildDelegateResult(promptText, chunks)

	response := map[string]any{
		"status":       "ok",
		"message":      "CLI delegate processed request",
		"result":       result,
		"events":       events,
		"request_id":   requestID,
		"processed_at": time.Now().UTC().Format(time.RFC3339),
	}

	if axes, ok := request["axes"]; ok {
		response["axes"] = axes
	}
	if meta, ok := request["meta"]; ok {
		response["meta"] = meta
	}

	if err := json.NewEncoder(os.Stdout).Encode(response); err != nil {
		fmt.Fprintf(os.Stderr, "bar: failed to encode delegate response: %v\n", err)
		return 1
	}

	return 0
}

func ensureRequestID(request map[string]any) string {
	if raw, ok := request["request_id"]; ok {
		if id, ok := raw.(string); ok {
			trimmed := strings.TrimSpace(id)
			if trimmed != "" {
				return trimmed
			}
		}
	}
	return fmt.Sprintf("cli-%d", time.Now().UnixNano())
}

func promptTextFromPayload(payload map[string]any) (string, error) {
	if raw, ok := payload["text"]; ok {
		if text, ok := raw.(string); ok {
			trimmed := strings.TrimSpace(text)
			if trimmed != "" {
				return trimmed, nil
			}
		}
	}

	if rawSegments, ok := payload["segments"]; ok {
		switch segs := rawSegments.(type) {
		case []any:
			parts := make([]string, 0, len(segs))
			for _, entry := range segs {
				if str, ok := entry.(string); ok {
					trimmed := strings.TrimSpace(str)
					if trimmed != "" {
						parts = append(parts, trimmed)
					}
				}
			}
			if len(parts) > 0 {
				return strings.Join(parts, "\n"), nil
			}
		case []string:
			parts := make([]string, 0, len(segs))
			for _, entry := range segs {
				trimmed := strings.TrimSpace(entry)
				if trimmed != "" {
					parts = append(parts, trimmed)
				}
			}
			if len(parts) > 0 {
				return strings.Join(parts, "\n"), nil
			}
		}
	}

	return "", errors.New("bar: delegate requires prompt.text string")
}

func chunkPrompt(text string) []string {
	cleaned := strings.TrimSpace(text)
	if cleaned == "" {
		return nil
	}

	if strings.Contains(cleaned, "\n") {
		lines := strings.Split(cleaned, "\n")
		chunks := make([]string, 0, len(lines))
		for _, line := range lines {
			trimmed := strings.TrimSpace(line)
			if trimmed != "" {
				chunks = append(chunks, trimmed)
			}
		}
		if len(chunks) > 0 {
			return chunks
		}
	}

	words := strings.Fields(cleaned)
	if len(words) <= 24 {
		return []string{cleaned}
	}

	const chunkSize = 24
	chunks := make([]string, 0, (len(words)/chunkSize)+1)
	for start := 0; start < len(words); start += chunkSize {
		end := start + chunkSize
		if end > len(words) {
			end = len(words)
		}
		chunks = append(chunks, strings.Join(words[start:end], " "))
	}
	return chunks
}

func buildDelegateEvents(requestID string, chunks []string) []map[string]any {
	events := []map[string]any{
		{"kind": "reset", "request_id": requestID},
		{"kind": "begin_send", "request_id": requestID},
		{"kind": "begin_stream", "request_id": requestID},
	}

	for _, chunk := range chunks {
		events = append(events, map[string]any{
			"kind":       "append",
			"request_id": requestID,
			"text":       chunk,
		})
	}

	events = append(events, map[string]any{
		"kind":       "complete",
		"request_id": requestID,
	})

	return events
}

func buildDelegateResult(promptText string, chunks []string) map[string]any {
	fields := strings.Fields(promptText)
	result := map[string]any{
		"echo":        promptText,
		"echo_upper":  strings.ToUpper(promptText),
		"chunk_count": len(chunks),
		"analysis": map[string]any{
			"characters": utf8.RuneCountInString(promptText),
			"words":      len(fields),
		},
	}

	if len(chunks) > 0 {
		result["chunks"] = chunks
		result["summary"] = fmt.Sprintf("%d chunk(s) replayed", len(chunks))
	} else {
		result["summary"] = "no chunks generated"
	}

	return result
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
