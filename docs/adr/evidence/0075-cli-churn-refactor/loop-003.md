# loop-003 evidence — helper:v20251223.1

## Behaviour outcome
Introduce the CLI configuration package and migrate the bar entry points (Run, completion engine, TUI) plus unit tests to consume it while keeping the harness green.

## Commands executed

### go test ./internal/barcli
- green | 2026-01-12T01:00:31Z | exit 0
  - helper:diff-snapshot=internal/barcli/app.go, internal/barcli/app_parse_test.go, internal/barcli/completion.go, internal/barcli/tui.go, internal/barcli/cli/config.go
  - coverage: typed CLI config parsed from argv now powers Run/preset/help paths; targeted package tests stay green.

### go test ./...
- green | 2026-01-12T01:01:07Z | exit 0
  - helper:diff-snapshot=internal/barcli/app.go, internal/barcli/app_parse_test.go, internal/barcli/completion.go, internal/barcli/tui.go, internal/barcli/cli/config.go
  - assurance: full suite succeeds with the new config package on the module path.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T01:02:30Z | exit 0
  - helper:diff-snapshot=internal/barcli/app.go, internal/barcli/tui.go, internal/barcli/cli/config.go, tests/integration/tui/tmp/
  - summary: all Bubble Tea expect cases (`environment-allowlist`, `focus-cycle`, `launch-status`, `sticky-summary`, `token-command-history`, `token-palette-history`, `token-palette-workflow`) produced passing transcripts under `tests/integration/tui/tmp/`.
