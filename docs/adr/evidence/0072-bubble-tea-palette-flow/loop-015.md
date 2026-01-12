## Behaviour outcome
Ensure toast overlays respect light and dark palettes by rendering with lipgloss adaptive colours and guarding the behaviour with unit tests.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T21:28:29Z | exit 0
  - helper:diff-snapshot=2 files changed, 38 insertions(+), 1 deletion(-)
  - summary: Bart UI unit suite passes with adaptive toast styling and coverage for both palette backgrounds.

### go test ./cmd/bar/...
- green | 2026-01-12T21:28:29Z | exit 0
  - helper:diff-snapshot=2 files changed, 38 insertions(+), 1 deletion(-)
  - summary: CLI fixtures remain in sync after toast styling update.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T21:28:29Z | exit 0
  - helper:diff-snapshot=2 files changed, 38 insertions(+), 1 deletion(-)
  - summary: Completion CLI guardrails unaffected by toast theming changes.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T21:28:29Z | exit 0
  - helper:diff-snapshot=2 files changed, 38 insertions(+), 1 deletion(-)
  - summary: Interactive expect transcripts capture toast messages with adaptive styling without regressions.
