## Behaviour outcome
Replace sparkline glyphs with ASCII-safe characters so telemetry trends render cleanly in plain UTF-8 transcripts and expect logs.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T20:05:43Z | exit 0
  - helper:diff-snapshot=2 files changed, 2 insertions(+), 1 deletion(-)
  - summary: bartui unit suite validates sparkline helper after glyph update.

### go test ./cmd/bar/...
- green | 2026-01-12T20:05:43Z | exit 0
  - helper:diff-snapshot=2 files changed, 2 insertions(+), 1 deletion(-)
  - summary: CLI snapshot refreshed to reflect ASCII sparkline output.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T20:05:43Z | exit 0
  - helper:diff-snapshot=2 files changed, 2 insertions(+), 1 deletion(-)
  - summary: CLI completion guardrail unchanged by telemetry glyphs.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T20:05:43Z | exit 0
  - helper:diff-snapshot=2 files changed, 2 insertions(+), 1 deletion(-)
  - summary: Expect transcripts now show ASCII sparkline characters (`.#`) without rendering artifacts.
