## Behaviour outcome
Introduce sidebar section headers for Compose, History, and Presets with collapsible states so token controls stay clear, history defaults collapsed, and presets remain discoverable without crowding the main column.

## Commands executed

### go test ./...
- green | 2026-01-12T04:58:03Z | exit 0
  - helper:diff-snapshot=4 files changed, 93 insertions(+), 26 deletions(-)
  - summary: exercises bartui state/render helpers and ensures updated tests and snapshot fixture stay green across the workspace.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T04:58:03Z | exit 0
  - summary: refreshed expect harness confirms history status messaging and collapsible sections behave in interactive runs.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T04:58:03Z | exit 0
  - summary: guards CLI completion layer to ensure shortcuts remain aligned after UI refactor.
