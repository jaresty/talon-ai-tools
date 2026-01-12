## Behaviour outcome
Extend the sidebar history entries with type metadata (icon + label) and UTC timestamps so operators can distinguish clipboard, token, command, and subject events at a glance.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T05:45:10Z | exit 0
  - helper:diff-snapshot=5 files changed, 292 insertions(+), 84 deletions(-)
  - summary: exercises history event recording, timestamp injection, and formatting helpers across bartui unit tests.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T05:45:10Z | exit 0
  - summary: expect suites reflect timestamped history rows and continue to cover clipboard, token, and command scenarios.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T05:45:10Z | exit 0
  - summary: completion CLI tests remain green after history metadata changes.
