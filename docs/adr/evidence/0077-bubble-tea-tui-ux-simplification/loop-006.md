## Behaviour outcome
Improve the in-app shortcut reference typography with ASCII dividers so section headers remain scannable across terminal themes.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T07:43:58Z | exit 0
  - helper:diff-snapshot=1 file changed, 12 insertions(+), 5 deletions(-)
  - summary: unit coverage validates the refreshed shortcut overlay rendering and token summary output.

### go test ./cmd/bar/...
- green | 2026-01-12T07:43:58Z | exit 0
  - summary: ensures CLI snapshot fixtures remain aligned after typography adjustments.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T07:43:58Z | exit 0
  - summary: expect harness confirms overlay hints, sidebar messaging, and history cues render cleanly with the new dividers.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T07:43:58Z | exit 0
  - summary: verifies CLI completion remains stable with no regressions introduced by the TUI typography change.
