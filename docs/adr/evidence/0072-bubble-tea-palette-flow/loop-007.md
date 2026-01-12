## Behaviour outcome
Enable deterministic palette history coverage by wiring a `--no-clipboard` flag for `bar tui`, stubbing clipboard IO in Bubble Tea, and exercising clipboard/undo history via a new expect harness case.

## Commands executed

### go test ./...
- green | 2026-01-12T03:37:55Z | exit 0
  - helper:diff-snapshot=internal/barcli/app.go, internal/barcli/cli/config.go, internal/barcli/tui.go
  - coverage: confirms the bar CLI builds with the new flag and that clipboard stubbing compiles across entry points.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T03:37:55Z | exit 0
  - helper:diff-snapshot=tests/integration/tui/tmp/
  - summary: new `clipboard-history` expect case passes and existing cases stay green with the stubbed clipboard buffer.
