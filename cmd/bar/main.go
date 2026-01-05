package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"os/exec"
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

	fixture, err := fetchProviderFixture(request)
	if err != nil {
		fmt.Fprintf(os.Stderr, "bar: provider command failed: %v\n", err)
	}
	if fixture == nil {
		fixture, err = loadDelegateFixture(request, promptText)
		if err != nil {
			fmt.Fprintf(os.Stderr, "bar: failed to load delegate fixture: %v\n", err)
			return 1
		}
	}
	if fixture == nil {
		fixture = recordedTranscriptForRequest(request, promptText)
	}
	if fixture == nil {
		fixture = synthesizeDelegateFixture(request, promptText)
	}

	requestID := ensureRequestID(request)

	promptChunks := chunkPrompt(promptText)

	status := "ok"
	message := "CLI delegate processed request"
	processedAt := time.Now().UTC().Format(time.RFC3339)
	responseMeta := ""
	var fixtureEvents []map[string]any
	var fixtureResult map[string]any

	if fixture != nil {
		if text := trimmedStringValue(fixture["status"]); text != "" {
			status = text
		}
		if text := stringValue(fixture["message"]); strings.TrimSpace(text) != "" {
			message = text
		}
		if text := trimmedStringValue(fixture["processed_at"]); text != "" {
			processedAt = text
		}
		if text := stringValue(fixture["meta"]); strings.TrimSpace(text) != "" {
			responseMeta = text
		}
		if result, ok := fixture["result"].(map[string]any); ok {
			fixtureResult = result
		}
		if rawEvents, ok := fixture["events"]; ok {
			fixtureEvents = coerceFixtureEvents(rawEvents)
		}
	}

	baseResult := buildDelegateResult(promptText, promptChunks)
	result := mergeDelegateResults(baseResult, fixtureResult)

	chunks := extractResultChunks(result)
	if len(chunks) == 0 {
		chunks = promptChunks
		if len(chunks) > 0 {
			result["chunks"] = chunks
		}
	}
	result["chunk_count"] = len(chunks)
	if _, ok := result["analysis"]; !ok {
		result["analysis"] = map[string]any{
			"characters": utf8.RuneCountInString(promptText),
			"words":      len(strings.Fields(promptText)),
		}
	}
	replaySummary := fmt.Sprintf("%d chunk(s) replayed", len(chunks))
	if _, ok := result["summary"]; !ok {
		if len(chunks) > 0 {
			result["summary"] = replaySummary
		} else {
			result["summary"] = "no chunks generated"
		}
	}
	if _, ok := result["replay_summary"]; !ok {
		result["replay_summary"] = replaySummary
	}

	if responseMeta != "" {
		if _, exists := result["meta"]; !exists {
			result["meta"] = responseMeta
		}
	}

	events := buildDelegateEvents(requestID, chunks, fixtureEvents)

	response := map[string]any{
		"status":       status,
		"message":      message,
		"result":       result,
		"events":       events,
		"request_id":   requestID,
		"processed_at": processedAt,
	}
	if responseMeta != "" {
		response["meta"] = responseMeta
	}
	if fixture != nil {
		for key, value := range fixture {
			switch key {
			case "status", "message", "result", "events", "request_id", "processed_at", "meta":
			default:
				response[key] = value
			}
		}
	}

	if _, exists := response["meta"]; !exists {
		if metaValue, ok := result["meta"]; ok {
			response["meta"] = metaValue
		}
	}

	if axes, ok := request["axes"]; ok {
		response["axes"] = axes
	}
	if meta, ok := request["meta"]; ok {
		if _, exists := response["meta"]; !exists {
			response["meta"] = meta
		}
	}

	if err := json.NewEncoder(os.Stdout).Encode(response); err != nil {
		fmt.Fprintf(os.Stderr, "bar: failed to encode delegate response: %v\n", err)
		return 1
	}

	return 0
}

func mergeDelegateResults(base map[string]any, override map[string]any) map[string]any {
	merged := make(map[string]any, len(base))
	for key, value := range base {
		merged[key] = value
	}
	if override != nil {
		for key, value := range override {
			merged[key] = value
		}
	}
	return merged
}

func extractResultChunks(result map[string]any) []string {
	if result == nil {
		return nil
	}
	raw, ok := result["chunks"]
	if !ok {
		return nil
	}
	switch typed := raw.(type) {
	case []string:
		chunks := make([]string, 0, len(typed))
		for _, entry := range typed {
			if entry != "" {
				chunks = append(chunks, entry)
			}
		}
		if len(chunks) == 0 {
			return nil
		}
		return chunks
	case []any:
		chunks := make([]string, 0, len(typed))
		for _, entry := range typed {
			text := stringValue(entry)
			if text != "" {
				chunks = append(chunks, text)
			}
		}
		if len(chunks) == 0 {
			return nil
		}
		return chunks
	default:
		return nil
	}
}

func loadDelegateFixture(request map[string]any, promptText string) (map[string]any, error) {
	path := strings.TrimSpace(os.Getenv("BAR_DELEGATE_FIXTURE"))
	if path != "" {
		data, err := os.ReadFile(path)
		if err != nil {
			return nil, err
		}
		var fixture map[string]any
		if err := json.Unmarshal(data, &fixture); err != nil {
			return nil, err
		}
		return fixture, nil
	}

	if rawKey, ok := request["delegate_fixture_key"].(string); ok {
		if fixture := embeddedDelegateFixture(rawKey); fixture != nil {
			return fixture, nil
		}
	}

	return nil, nil
}

func fetchProviderFixture(request map[string]any) (map[string]any, error) {
	mode := strings.ToLower(strings.TrimSpace(os.Getenv("BAR_PROVIDER_COMMAND_MODE")))
	switch mode {
	case "disabled", "off", "recorded-only":
		return nil, nil
	case "fixtures-only", "fixtures", "fixture":
		return recordedTranscriptForRequest(request, ""), nil
	}

	command := strings.TrimSpace(os.Getenv("BAR_PROVIDER_COMMAND"))
	if command == "" {
		return nil, nil
	}

	args := parseCommandLine(command)
	if len(args) == 0 {
		return nil, nil
	}

	payload, err := json.Marshal(request)
	if err != nil {
		return nil, err
	}

	cmd := exec.Command(args[0], args[1:]...)
	cmd.Stdin = bytes.NewReader(payload)

	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		trimmed := strings.TrimSpace(stderr.String())
		if trimmed != "" {
			return nil, fmt.Errorf("provider command failed: %w (%s)", err, trimmed)
		}
		return nil, fmt.Errorf("provider command failed: %w", err)
	}

	data := bytes.TrimSpace(stdout.Bytes())
	if len(data) == 0 {
		return nil, errors.New("provider command returned empty response")
	}

	var fixture map[string]any
	if err := json.Unmarshal(data, &fixture); err != nil {
		return nil, fmt.Errorf("provider command produced invalid JSON: %w", err)
	}

	return cloneMap(fixture), nil
}

func parseCommandLine(command string) []string {
	fields := strings.Fields(command)
	return fields
}

func recordedTranscriptForRequest(request map[string]any, promptText string) map[string]any {
	if request == nil && strings.TrimSpace(promptText) == "" {
		return nil
	}

	if rawKey, ok := request["recorded_transcript_key"].(string); ok {
		if fixture := providerTranscriptByKey(rawKey); fixture != nil {
			return fixture
		}
	}

	if rawKey, ok := request["delegate_fixture_key"].(string); ok {
		if fixture := providerTranscriptByKey(rawKey); fixture != nil {
			return fixture
		}
	}

	trimmedPrompt := strings.ToLower(strings.TrimSpace(promptText))
	if trimmedPrompt != "" {
		if fixture := providerTranscriptByKey("prompt:" + trimmedPrompt); fixture != nil {
			return fixture
		}
	}

	if providerRaw, ok := request["provider_id"].(string); ok {
		providerKey := strings.ToLower(strings.TrimSpace(providerRaw))
		if providerKey != "" && trimmedPrompt != "" {
			combined := fmt.Sprintf("provider:%s|prompt:%s", providerKey, trimmedPrompt)
			if fixture := providerTranscriptByKey(combined); fixture != nil {
				return fixture
			}
		}
	}

	return nil
}

func synthesizeDelegateFixture(request map[string]any, promptText string) map[string]any {
	trimmed := strings.TrimSpace(promptText)
	if trimmed == "" {
		trimmed = "(empty prompt)"
	}
	words := strings.Fields(trimmed)
	wordCount := len(words)
	if wordCount == 0 {
		words = []string{"(empty)"}
		wordCount = 1
	}

	summaryLine := fmt.Sprintf("Summary: %s", summariseWords(words, 16))
	echoLine := fmt.Sprintf("Echo: %s", trimmed)
	highlights := extractHighlights(words, 3)
	highlightText := "(none)"
	if len(highlights) > 0 {
		highlightText = strings.Join(highlights, ", ")
	}
	insightLine := fmt.Sprintf("Highlights: %s", highlightText)

	answer := strings.Join([]string{summaryLine, echoLine, insightLine}, "\n\n")
	chunks := chunkPrompt(answer)
	if len(chunks) == 0 {
		chunks = []string{answer}
	}

	meta := fmt.Sprintf(
		"## Model interpretation\nEchoed %d word(s) over %d chunk(s).",
		wordCount,
		len(chunks),
	)

	responseAnalysis := map[string]any{
		"characters": utf8.RuneCountInString(answer),
		"lines":      len(chunks),
	}

	replaySummary := fmt.Sprintf("%d chunk(s) replayed", len(chunks))
	completionTokens := len(strings.Fields(answer))
	usage := map[string]any{
		"prompt_tokens":     wordCount,
		"completion_tokens": completionTokens,
		"total_tokens":      wordCount + completionTokens,
	}

	result := map[string]any{
		"answer":            answer,
		"chunks":            chunks,
		"chunk_count":       len(chunks),
		"summary":           summaryLine,
		"replay_summary":    replaySummary,
		"highlights":        highlights,
		"response_analysis": responseAnalysis,
		"usage":             usage,
		"echo":              trimmed,
	}

	if axes, ok := request["axes"].(map[string]any); ok {
		result["axes"] = axes
	}

	events := make([]map[string]any, 0, len(chunks)+2)
	for index, chunk := range chunks {
		events = append(events, map[string]any{
			"kind": "append",
			"delta": map[string]any{
				"role":  "assistant",
				"type":  "text",
				"index": index,
				"text":  chunk,
			},
		})
	}
	events = append(events, map[string]any{
		"kind":  "usage",
		"usage": usage,
	})

	return map[string]any{
		"status":  "ok",
		"message": answer,
		"meta":    meta,
		"result":  result,
		"events":  events,
	}
}

func summariseWords(words []string, limit int) string {
	if len(words) <= limit {
		return strings.Join(words, " ")
	}
	summary := strings.Join(words[:limit], " ")
	return summary + "…"
}

func extractHighlights(words []string, limit int) []string {
	highlights := make([]string, 0, limit)
	seen := make(map[string]struct{})
	for _, word := range words {
		clean := sanitizeHighlightWord(word)
		if clean == "" {
			continue
		}
		clean = strings.ToLower(clean)
		if _, ok := seen[clean]; ok {
			continue
		}
		seen[clean] = struct{}{}
		highlights = append(highlights, "#"+clean)
		if len(highlights) >= limit {
			break
		}
	}
	return highlights
}

func sanitizeHighlightWord(word string) string {
	return strings.Trim(word, `.,;:!?"'()[]{}<>`)
}

func coerceFixtureEvents(raw any) []map[string]any {

	var events []map[string]any
	switch typed := raw.(type) {
	case []map[string]any:
		for _, entry := range typed {
			events = append(events, sanitizeFixtureEvent(entry))
		}
	case []any:
		for _, entry := range typed {
			if eventMap, ok := entry.(map[string]any); ok {
				events = append(events, sanitizeFixtureEvent(eventMap))
			}
		}
	}
	return events
}

func sanitizeFixtureEvent(raw map[string]any) map[string]any {
	sanitized := make(map[string]any, len(raw))
	for key, value := range raw {
		switch key {
		case "kind":
			sanitized["kind"] = strings.ToLower(strings.TrimSpace(stringValue(value)))
		case "request_id":
			sanitized["request_id"] = strings.TrimSpace(stringValue(value))
		default:
			sanitized[key] = value
		}
	}
	return sanitized
}

func stringValue(v any) string {
	if v == nil {
		return ""
	}
	switch value := v.(type) {
	case string:
		return value
	case fmt.Stringer:
		return value.String()
	default:
		return fmt.Sprint(value)
	}
}

func trimmedStringValue(v any) string {
	return strings.TrimSpace(stringValue(v))
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

func buildDelegateEvents(requestID string, chunks []string, additional []map[string]any) []map[string]any {
	events := []map[string]any{
		{"kind": "reset", "request_id": requestID},
		{"kind": "begin_send", "request_id": requestID},
		{"kind": "begin_stream", "request_id": requestID},
	}

	if len(additional) > 0 {
		for _, rawEvent := range additional {
			kindValue, _ := rawEvent["kind"].(string)
			kind := strings.TrimSpace(kindValue)
			if kind == "" {
				continue
			}
			kind = strings.ToLower(kind)
			event := make(map[string]any, len(rawEvent))
			for key, value := range rawEvent {
				if key == "kind" {
					event["kind"] = kind
					continue
				}
				event[key] = value
			}
			if req, ok := event["request_id"]; ok {
				trimmed := strings.TrimSpace(stringValue(req))
				if trimmed == "" {
					event["request_id"] = requestID
				} else {
					event["request_id"] = trimmed
				}
			} else {
				event["request_id"] = requestID
			}
			events = append(events, event)
		}
	} else {
		for _, chunk := range chunks {
			events = append(events, map[string]any{
				"kind":       "append",
				"request_id": requestID,
				"text":       chunk,
			})
		}
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
