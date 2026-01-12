## Behaviour outcome
Refine the shortcut reference and token focus indicators so the overlay clears cleanly, full-layout content returns without residue, and the sidebar highlights the active token category.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T07:02:36Z | exit 0
  - helper:diff-snapshot=3 files changed, 82 insertions(+), 20 deletions(-)
  - summary: exercises overlay toggling, ClearScreen handling, and refreshed token summary rendering.

### go test ./cmd/bar/...
- green | 2026-01-12T07:02:36Z | exit 0
  - summary: verifies CLI snapshot alignment with the new categories block and overlay presentation.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T07:02:36Z | exit 0
  - summary: expect harness confirms token category highlights, overlay clearing, and history/status messaging across workflows.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T07:02:36Z | exit 0
  - summary: ensures CLI completion integrations stay stable after UI refinements.
