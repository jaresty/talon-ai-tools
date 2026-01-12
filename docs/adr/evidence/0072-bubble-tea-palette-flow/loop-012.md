## Behaviour outcome
Assert toast overlays during grammar composer actions so CLI reinforcement stays visible in automated TUI runs.

## Commands executed

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T19:46:21Z | exit 0
  - helper:diff-snapshot=1 file changed, 4 insertions(+)
  - summary: expect suite captures token apply toasts without regressions in other cases.

### go test ./internal/bartui
- green | 2026-01-12T19:46:21Z | exit 0
  - helper:diff-snapshot=1 file changed, 4 insertions(+)
  - summary: bartui unit tests remain green after expect assertion update.

### go test ./cmd/bar/...
- green | 2026-01-12T19:46:21Z | exit 0
  - helper:diff-snapshot=1 file changed, 4 insertions(+)
  - summary: bar CLI integration suite unchanged by expect guardrail.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T19:46:21Z | exit 0
  - helper:diff-snapshot=1 file changed, 4 insertions(+)
  - summary: CLI completion contract unaffected, preserving grammar hint coverage.
