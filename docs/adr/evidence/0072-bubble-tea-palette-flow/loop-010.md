## Behaviour outcome
Add keyboard shortcuts to maximise the subject or result viewports (Ctrl+J/Ctrl+K), updating Bubble Tea layout logic, help overlay, and tests so pilots can page through long content without losing CLI context.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T18:52:39Z | exit 0
  - helper:diff-snapshot=5 files changed, 291 insertions(+), 15 deletions(-)
  - summary: unit tests cover viewport toggles and shortcut reference updates.

### go test ./cmd/bar/...
- green | 2026-01-12T18:52:55Z | exit 0
  - helper:diff-snapshot=5 files changed, 291 insertions(+), 15 deletions(-)
  - summary: CLI layer remains in sync after viewport toggle wiring.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T18:53:14Z | exit 0
  - helper:diff-snapshot=5 files changed, 291 insertions(+), 15 deletions(-)
  - summary: completion guardrail stays aligned with grammar-first palette hints.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T18:54:41Z | exit 0
  - helper:diff-snapshot=5 files changed, 291 insertions(+), 15 deletions(-)
  - summary: expect harness verifies viewport toggle behaviour alongside existing palette and history flows.
