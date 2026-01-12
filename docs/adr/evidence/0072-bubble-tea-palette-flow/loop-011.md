## Behaviour outcome
Introduce inline token telemetry under the compose pane and toast overlays for grammar actions so palette changes surface immediate CLI-oriented feedback without leaving the docked workflow.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T19:35:50Z | exit 0
  - helper:diff-snapshot=4 files changed, 307 insertions(+), 33 deletions(-)
  - summary: unit coverage now exercises sparkline rendering and toast sequence expiry for token operations.

### go test ./cmd/bar/...
- green | 2026-01-12T19:35:50Z | exit 0
  - helper:diff-snapshot=4 files changed, 307 insertions(+), 33 deletions(-)
  - summary: CLI fixture reflects telemetry line relocation and toast output in the snapshot harness.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T19:35:50Z | exit 0
  - helper:diff-snapshot=4 files changed, 307 insertions(+), 33 deletions(-)
  - summary: completion guardrails remain unchanged after telemetry/toast additions.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T19:35:50Z | exit 0
  - helper:diff-snapshot=4 files changed, 307 insertions(+), 33 deletions(-)
  - summary: expect transcripts updated for compose telemetry and toast messaging across scenarios.
