# loop-004 evidence — helper:v20251223.1

## Behaviour outcome
Expose environment allowlist resolution on `cli.Config` and migrate the TUI launcher to consume it so the coordination package owns env bootstrap logic.

## Commands executed

### go test ./internal/barcli
- green | 2026-01-12T01:09:00Z | exit 0
  - helper:diff-snapshot=internal/barcli/cli/config.go, internal/barcli/tui.go
  - coverage: validates the CLI configuration helpers and TUI wiring continue to pass package tests with the new `ResolveEnvValues` method.

### go test ./...
- green | 2026-01-12T01:09:09Z | exit 0
  - helper:diff-snapshot=internal/barcli/cli/config.go, internal/barcli/tui.go
  - assurance: full suite remains green, confirming other entry points observe the consolidated environment handling.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T01:11:30Z | exit 0
  - helper:diff-snapshot=internal/barcli/cli/config.go, internal/barcli/tui.go, tests/integration/tui/tmp/
  - summary: all Bubble Tea expect cases completed successfully with refreshed transcripts under `tests/integration/tui/tmp/`, exercising the updated env bootstrap path.
