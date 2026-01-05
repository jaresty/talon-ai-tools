package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"math"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
	"unicode/utf8"
)

const (
	schemaRelativePath            = "docs/schema/command-surface.json"
	runtimeName                   = "go"
	executorName                  = "compiled"
	defaultTelemetryWindowMinutes = 30
	maxTelemetrySamples           = 200
	defaultHTTPRecordLimit        = 50
	maxHTTPRecordLimit            = 500
	promptPreviewLimit            = 200
)

type fixturesOnlyMissingTranscriptError struct {
	message string
}

func (e fixturesOnlyMissingTranscriptError) Error() string {
	return e.message
}

type healthPayload struct {
	Status     string `json:"status"`
	Version    string `json:"version"`
	Runtime    string `json:"runtime"`
	Executor   string `json:"executor"`
	BinaryPath string `json:"binary_path"`
}

type latencyTelemetrySample struct {
	Timestamp  string  `json:"timestamp"`
	LatencyMs  float64 `json:"latency_ms"`
	HTTPStatus int     `json:"http_status"`
	Success    bool    `json:"success"`
}

type latencyTelemetryPayload struct {
	GeneratedAt   string                   `json:"generated_at"`
	WindowMinutes int                      `json:"window_minutes"`
	Samples       []latencyTelemetrySample `json:"samples"`
	SampleCount   int                      `json:"sample_count"`
	P50Ms         float64                  `json:"p50_ms"`
	P95Ms         float64                  `json:"p95_ms"`
	SuccessRate   float64                  `json:"success_rate"`
}

type httpRecording struct {
	Timestamp     string         `json:"timestamp"`
	Endpoint      string         `json:"endpoint"`
	HTTPStatus    int            `json:"http_status"`
	LatencyMs     float64        `json:"latency_ms"`
	Success       bool           `json:"success"`
	RequestID     string         `json:"request_id"`
	PromptPreview string         `json:"prompt_preview"`
	PromptHash    string         `json:"prompt_hash"`
	Response      map[string]any `json:"response"`
}

type httpRecordingPayload struct {
	GeneratedAt string          `json:"generated_at"`
	Limit       int             `json:"limit"`
	RecordCount int             `json:"record_count"`
	Records     []httpRecording `json:"records"`
}

var httpRecordingsMu sync.Mutex

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

	fixture, err := fetchProviderFixture(request)
	if err != nil {
		var fixturesErr fixturesOnlyMissingTranscriptError
		if errors.As(err, &fixturesErr) {
			fmt.Fprintln(os.Stderr, fixturesErr.message)
			response := map[string]any{
				"status":     "error",
				"message":    fixturesErr.message,
				"meta":       "fixtures-only missing recorded transcript",
				"request_id": requestID,
			}
			if err := json.NewEncoder(os.Stdout).Encode(response); err != nil {
				fmt.Fprintf(os.Stderr, "bar: failed to encode error response: %v\n", err)
			}
			return 1
		}
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
	endpoint := strings.TrimSpace(os.Getenv("BAR_PROVIDER_HTTP_ENDPOINT"))
	promptText := promptTextFromRequestMap(request)

	switch mode {
	case "disabled", "off", "recorded-only":
		return nil, nil
	case "fixtures-only", "fixtures", "fixture":
		if transcript := recordedTranscriptForRequest(request, promptText); transcript != nil {
			return transcript, nil
		}
		errorMessage := "fixtures-only mode requires recorded transcript"
		if promptText != "" {
			errorMessage = fmt.Sprintf("fixtures-only mode requires recorded transcript for '%s'", promptText)
		}
		return nil, fixturesOnlyMissingTranscriptError{message: errorMessage}
	case "http":
		return fetchHTTPProviderFixture(endpoint, request, promptText)
	}

	if endpoint != "" {
		return fetchHTTPProviderFixture(endpoint, request, promptText)
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

func applyHTTPFallbackMeta(fixture map[string]any, reason string) {
	fallback := fmt.Sprintf("HTTP fallback: %s", reason)
	existing := stringValue(fixture["meta"])
	trimmed := strings.TrimSpace(existing)
	if trimmed == "" {
		fixture["meta"] = fallback
	} else if !strings.Contains(trimmed, fallback) {
		fixture["meta"] = trimmed + "\n\n" + fallback
	}
}

func parseHTTPHeadersEnv() (map[string]string, error) {
	raw := strings.TrimSpace(os.Getenv("BAR_PROVIDER_HTTP_HEADERS"))
	if raw == "" {
		return nil, nil
	}
	var headers map[string]string
	if err := json.Unmarshal([]byte(raw), &headers); err != nil {
		return nil, fmt.Errorf("invalid BAR_PROVIDER_HTTP_HEADERS: %w", err)
	}
	return headers, nil
}

func telemetryLatencyPath(root string) string {
	override := strings.TrimSpace(os.Getenv("BAR_TELEMETRY_LATENCY_PATH"))
	if override != "" {
		return override
	}
	if root == "" {
		return ""
	}
	return filepath.Join(root, "var", "cli-telemetry", "latency.json")
}

func percentile(sortedValues []float64, quantile float64) float64 {
	switch {
	case len(sortedValues) == 0:
		return 0
	case quantile <= 0:
		return sortedValues[0]
	case quantile >= 1:
		return sortedValues[len(sortedValues)-1]
	}

	position := quantile * float64(len(sortedValues)-1)
	lower := int(math.Floor(position))
	upper := int(math.Ceil(position))
	if lower == upper {
		return sortedValues[lower]
	}
	weight := position - float64(lower)
	return sortedValues[lower]*(1-weight) + sortedValues[upper]*weight
}

func clampSampleWindow(samples []latencyTelemetrySample, cutoff time.Time) []latencyTelemetrySample {
	if len(samples) == 0 {
		return samples
	}
	clamped := make([]latencyTelemetrySample, 0, len(samples))
	for _, sample := range samples {
		if sample.Timestamp == "" {
			continue
		}
		timestamp, err := time.Parse(time.RFC3339, sample.Timestamp)
		if err != nil {
			continue
		}
		if timestamp.Before(cutoff) {
			continue
		}
		clamped = append(clamped, sample)
	}
	if len(clamped) > maxTelemetrySamples {
		clamped = clamped[len(clamped)-maxTelemetrySamples:]
	}
	return clamped
}

func sanitizeLatencyValue(value float64) float64 {
	if math.IsNaN(value) || math.IsInf(value, 0) {
		return 0
	}
	if value < 0 {
		return 0
	}
	return value
}

func recordLatencyTelemetry(root string, status int, latency time.Duration, success bool) {
	if root == "" {
		root = repoRoot()
	}
	path := telemetryLatencyPath(root)
	if path == "" {
		return
	}

	payload := latencyTelemetryPayload{}
	if data, err := os.ReadFile(path); err == nil {
		if err := json.Unmarshal(data, &payload); err != nil {
			payload = latencyTelemetryPayload{}
		}
	}

	now := time.Now().UTC()
	if payload.WindowMinutes <= 0 {
		payload.WindowMinutes = defaultTelemetryWindowMinutes
	}

	sample := latencyTelemetrySample{
		Timestamp:  now.Format(time.RFC3339),
		LatencyMs:  sanitizeLatencyValue(float64(latency) / float64(time.Millisecond)),
		HTTPStatus: status,
		Success:    success,
	}
	if latency <= 0 {
		sample.LatencyMs = 0
	}

	payload.Samples = append(payload.Samples, sample)
	cutoff := now.Add(-time.Duration(payload.WindowMinutes) * time.Minute)
	payload.Samples = clampSampleWindow(payload.Samples, cutoff)
	payload.SampleCount = len(payload.Samples)
	payload.GeneratedAt = now.Format(time.RFC3339)

	latencies := make([]float64, 0, len(payload.Samples))
	successCount := 0
	for _, entry := range payload.Samples {
		lat := sanitizeLatencyValue(entry.LatencyMs)
		latencies = append(latencies, lat)
		if entry.Success {
			successCount++
		}
	}

	if len(latencies) > 0 {
		sort.Float64s(latencies)
		payload.P50Ms = sanitizeLatencyValue(percentile(latencies, 0.50))
		payload.P95Ms = sanitizeLatencyValue(percentile(latencies, 0.95))
		payload.SuccessRate = float64(successCount) / float64(len(latencies))
	} else {
		payload.P50Ms = 0
		payload.P95Ms = 0
		if success {
			payload.SuccessRate = 1
		} else {
			payload.SuccessRate = 0
		}
	}

	output, err := json.MarshalIndent(payload, "", "  ")
	if err != nil {
		return
	}

	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return
	}

	_ = os.WriteFile(path, append(output, '\n'), 0o644)
}

func httpRecordingsPath(root string) string {
	override := strings.TrimSpace(os.Getenv("BAR_PROVIDER_HTTP_RECORD_PATH"))
	if override != "" {
		return override
	}
	if root == "" {
		return ""
	}
	return filepath.Join(root, "var", "cli-telemetry", "http-recordings.json")
}

func httpRecordingLimit() int {
	raw := strings.TrimSpace(os.Getenv("BAR_PROVIDER_HTTP_RECORD_LIMIT"))
	if raw == "" {
		return defaultHTTPRecordLimit
	}
	parsed, err := strconv.Atoi(raw)
	if err != nil || parsed <= 0 {
		return 0
	}
	if parsed > maxHTTPRecordLimit {
		return maxHTTPRecordLimit
	}
	return parsed
}

func promptFingerprint(prompt string) (string, string) {
	trimmed := strings.TrimSpace(prompt)
	if trimmed == "" {
		return "", ""
	}
	normalized := strings.Join(strings.Fields(strings.ReplaceAll(trimmed, "\n", " ")), " ")
	hashBytes := sha256.Sum256([]byte(strings.ToLower(normalized)))
	hash := hex.EncodeToString(hashBytes[:])
	runes := []rune(normalized)
	if len(runes) > promptPreviewLimit {
		return hash, string(runes[:promptPreviewLimit]) + "…"
	}
	return hash, normalized
}

func recordHTTPInteraction(root, endpoint string, request map[string]any, promptText string, response map[string]any, status int, latency time.Duration) {
	path := httpRecordingsPath(root)
	if path == "" {
		return
	}
	limit := httpRecordingLimit()
	if limit <= 0 {
		return
	}

	if promptText == "" {
		promptText = promptTextFromRequestMap(request)
	}
	hash, preview := promptFingerprint(promptText)

	now := time.Now().UTC()

	requestID := ""
	if raw, ok := request["request_id"].(string); ok {
		requestID = strings.TrimSpace(raw)
	}
	if requestID == "" {
		requestID = ensureRequestID(request)
	}

	record := httpRecording{
		Timestamp:     now.Format(time.RFC3339),
		Endpoint:      strings.TrimSpace(endpoint),
		HTTPStatus:    status,
		LatencyMs:     sanitizeLatencyValue(float64(latency) / float64(time.Millisecond)),
		Success:       status >= 200 && status < 400,
		RequestID:     requestID,
		PromptPreview: preview,
		PromptHash:    hash,
		Response:      cloneMap(response),
	}

	if record.Endpoint == "" {
		record.Endpoint = endpoint
	}

	httpRecordingsMu.Lock()
	defer httpRecordingsMu.Unlock()

	payload := httpRecordingPayload{}
	if data, err := os.ReadFile(path); err == nil {
		if err := json.Unmarshal(data, &payload); err != nil {
			payload = httpRecordingPayload{}
		}
	}

	payload.Records = append(payload.Records, record)
	if len(payload.Records) > limit {
		payload.Records = payload.Records[len(payload.Records)-limit:]
	}
	payload.RecordCount = len(payload.Records)
	payload.GeneratedAt = now.Format(time.RFC3339)
	payload.Limit = limit

	output, err := json.MarshalIndent(payload, "", "  ")
	if err != nil {
		return
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return
	}
	_ = os.WriteFile(path, append(output, '\n'), 0o644)
}

func fetchHTTPProviderFixture(endpoint string, request map[string]any, promptText string) (map[string]any, error) {
	if endpoint == "" {
		if transcript := recordedTranscriptForRequest(request, promptText); transcript != nil {
			reason := "missing HTTP endpoint configuration"
			applyHTTPFallbackMeta(transcript, reason)
			transcript["http_fallback_reason"] = reason
			transcript["http_fallback_attempts"] = 0
			return transcript, nil

		}
		return nil, fmt.Errorf("http mode requires BAR_PROVIDER_HTTP_ENDPOINT")
	}

	retries := 3
	if raw := strings.TrimSpace(os.Getenv("BAR_PROVIDER_HTTP_RETRIES")); raw != "" {
		if parsed, err := strconv.Atoi(raw); err == nil && parsed > 0 {
			retries = parsed
		}
	}

	bearer := strings.TrimSpace(os.Getenv("BAR_PROVIDER_HTTP_BEARER"))
	headers, headersErr := parseHTTPHeadersEnv()
	if headersErr != nil {
		return nil, headersErr
	}

	timeout := 5 * time.Second
	if raw := strings.TrimSpace(os.Getenv("BAR_PROVIDER_HTTP_TIMEOUT_MS")); raw != "" {
		if parsed, err := strconv.Atoi(raw); err == nil && parsed > 0 {
			timeout = time.Duration(parsed) * time.Millisecond
		}
	}

	payload, err := json.Marshal(request)
	if err != nil {
		return nil, err
	}

	fixture, err := invokeHTTPProviderWithRetries(endpoint, payload, bearer, headers, timeout, retries, request, promptText)
	if err != nil {
		if transcript := recordedTranscriptForRequest(request, promptText); transcript != nil {
			reason := err.Error()
			applyHTTPFallbackMeta(transcript, fmt.Sprintf("%s after %d attempt(s)", reason, retries))
			transcript["http_fallback_reason"] = reason
			transcript["http_fallback_attempts"] = retries
			return transcript, nil
		}
		return nil, err
	}

	return fixture, nil
}

func invokeHTTPProviderWithRetries(endpoint string, payload []byte, bearer string, headers map[string]string, timeout time.Duration, retries int, request map[string]any, promptText string) (map[string]any, error) {
	if retries < 1 {
		retries = 1
	}

	var lastErr error
	for attempt := 1; attempt <= retries; attempt++ {
		fixture, err := invokeHTTPProvider(endpoint, payload, bearer, headers, timeout, request, promptText)
		if err == nil {
			return fixture, nil
		}
		lastErr = err
		if attempt < retries {
			time.Sleep(time.Duration(attempt) * 100 * time.Millisecond)
		}
	}

	if lastErr == nil {
		lastErr = fmt.Errorf("unknown HTTP provider error")
	}

	return nil, lastErr
}

func invokeHTTPProvider(endpoint string, payload []byte, bearer string, headers map[string]string, timeout time.Duration, request map[string]any, promptText string) (map[string]any, error) {
	root := repoRoot()
	client := &http.Client{Timeout: timeout}
	req, err := http.NewRequest(http.MethodPost, endpoint, bytes.NewReader(payload))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	if bearer != "" {
		req.Header.Set("Authorization", "Bearer "+bearer)
	}
	for key, value := range headers {
		if strings.EqualFold(key, "Content-Length") {
			continue
		}
		req.Header.Set(key, value)
	}

	start := time.Now()
	resp, err := client.Do(req)
	latency := time.Since(start)
	if err != nil {
		recordLatencyTelemetry(root, 0, latency, false)
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		recordLatencyTelemetry(root, resp.StatusCode, latency, false)
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		snippet := strings.TrimSpace(string(body))
		recordLatencyTelemetry(root, resp.StatusCode, latency, false)
		if snippet != "" {
			return nil, fmt.Errorf("http provider returned status %d: %s", resp.StatusCode, snippet)
		}
		return nil, fmt.Errorf("http provider returned status %d", resp.StatusCode)
	}

	var fixture map[string]any
	if err := json.Unmarshal(body, &fixture); err != nil {
		recordLatencyTelemetry(root, resp.StatusCode, latency, false)
		return nil, fmt.Errorf("http provider produced invalid JSON: %w", err)
	}

	latencyMs := float64(latency) / float64(time.Millisecond)
	if latencyMs < 0 {
		latencyMs = 0
	}
	fixture["http_status"] = resp.StatusCode
	fixture["http_latency_ms"] = latencyMs
	if result, ok := fixture["result"].(map[string]any); ok {
		if _, exists := result["http_status"]; !exists {
			result["http_status"] = resp.StatusCode
		}
		if _, exists := result["http_latency_ms"]; !exists {
			result["http_latency_ms"] = latencyMs
		}
	}

	recordLatencyTelemetry(root, resp.StatusCode, latency, true)
	recordHTTPInteraction(root, endpoint, request, promptText, fixture, resp.StatusCode, latency)

	return cloneMap(fixture), nil
}

func parseCommandLine(command string) []string {
	fields := strings.Fields(command)
	return fields
}

func promptTextFromRequestMap(request map[string]any) string {
	if request == nil {
		return ""
	}
	promptPayload, ok := request["prompt"].(map[string]any)
	if !ok {
		return ""
	}
	text, err := promptTextFromPayload(promptPayload)
	if err != nil {
		return ""
	}
	return text
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
