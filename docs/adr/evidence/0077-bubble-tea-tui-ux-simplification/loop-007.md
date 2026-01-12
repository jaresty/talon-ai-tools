## Behaviour outcome
Wrap sidebar sections to respect narrow terminal widths so Compose/History/Presets remain readable on smaller displays.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T08:33:16Z | exit 0
  - helper:diff-snapshot=1 file changed, 10 insertions(+), 1 deletion(-)
  - summary: validates that lipgloss-based width rendering keeps sidebar content within the column.

### go test ./cmd/bar/...
- green | 2026-01-12T08:33:16Z | exit 0
  - summary: confirms CLI snapshot fixtures remain aligned after wrapping changes.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T08:33:16Z | exit 0
  - summary: expect harness verifies sidebar sections wrap correctly on constrained terminals.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T08:33:16Z | exit 0
  - summary: ensures CLI integrations remain unaffected by sidebar wrapping changes.
