## Behaviour outcome
Add a manual sidebar visibility toggle (Ctrl+G) that persists operator preference, adjusts layout width handling, and informs status/help text while respecting narrow-terminal auto-collapse.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T06:10:57Z | exit 0
  - helper:diff-snapshot=4 files changed, 117 insertions(+), 3 deletions(-)
  - summary: validates sidebar toggle state, layout computations, and updated unit coverage.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T06:10:57Z | exit 0
  - summary: expect suites confirm new status copy, sidebar behaviour, and history metadata outputs across TUI scenarios.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T06:10:57Z | exit 0
  - summary: ensures CLI completion flows remain unaffected by sidebar preference changes.
