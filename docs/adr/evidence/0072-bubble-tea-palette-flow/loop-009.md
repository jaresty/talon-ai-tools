## Behaviour outcome
Implement the grammar-first palette composer: seed the filter with `category=` slugs, parse `category=value` input, and mirror CLI-style status hints.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T16:09:58Z | exit 0
  - helper:diff-snapshot=3 files changed, 136 insertions(+), 26 deletions(-)
  - summary: unit coverage passes with updated grammar composer behaviour and refreshed status messages.

### go test ./cmd/bar/...
- green | 2026-01-12T16:10:15Z | exit 0
  - helper:diff-snapshot=3 files changed, 136 insertions(+), 26 deletions(-)
  - summary: CLI integration tests remain green after grammar composer updates.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T16:10:36Z | exit 0
  - helper:diff-snapshot=3 files changed, 136 insertions(+), 26 deletions(-)
  - summary: completion guardrail stays aligned with grammar-first hints.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T16:13:23Z | exit 0
  - helper:diff-snapshot=3 files changed, 136 insertions(+), 26 deletions(-)
  - summary: expect suite confirms docked grammar composer, history, and status prompts across scenarios.
