## Behaviour outcome
Highlight the most recent history entry with ADR 0077 typography cues so operators can immediately spot the active event inside the sidebar.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-13T01:24:12Z | exit 0
  - helper:diff-snapshot=2 files changed, 115 insertions(+), 2 deletions(-)
  - summary: exercises the new highlight helper plus regression coverage for history rendering and the recently added tests.

### go test ./cmd/bar/...
- green | 2026-01-13T01:20:12Z | exit 0
  - helper:diff-snapshot=2 files changed, 115 insertions(+), 2 deletions(-)
  - summary: confirms CLI wiring remains stable after the bartui layout adjustments.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-13T01:20:24Z | exit 0
  - helper:diff-snapshot=2 files changed, 115 insertions(+), 2 deletions(-)
  - summary: validates the CLI completion guardrail that depends on bartui shortcut messaging.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-13T01:22:35Z | exit 0
  - helper:diff-snapshot=2 files changed, 115 insertions(+), 2 deletions(-)
  - summary: expect transcripts show the highlighted history row and confirm existing clipboard/history scenarios remain stable.
