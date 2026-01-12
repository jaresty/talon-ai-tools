## Behaviour outcome
Implement the in-app shortcut reference (`Ctrl+?`) with grouped sections, refreshed status copy, and palette hints so operators can discover commands without leaving the TUI.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T06:41:18Z | exit 0
  - helper:diff-snapshot=4 files changed, 200 insertions(+), 52 deletions(-)
  - summary: validates shortcut reference toggling, status restoration, and updated unit coverage for grouped entries.

### go test ./cmd/bar/...
- green | 2026-01-12T06:41:18Z | exit 0
  - summary: regenerates the CLI snapshot fixture to cover the new status copy and hint text.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T06:41:18Z | exit 0
  - summary: expect suites confirm the shortcut hint text, history toggles, and grouped overlay behaviour across TUI scenarios.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T06:41:18Z | exit 0
  - summary: ensures CLI completion remains stable with the refreshed shortcut reference commands.
