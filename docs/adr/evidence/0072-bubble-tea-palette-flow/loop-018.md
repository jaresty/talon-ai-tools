## Behaviour outcome
Replace the toast overlay's hard-coded ANSI palette with a Charmtone-derived Lip Gloss theme so CLI reinforcement cues stay legible across dark and light terminals.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T22:57:06Z | exit 0
  - helper:diff-snapshot=7 files changed, 169 insertions(+), 39 deletions(-)
  - summary: Unit suite covers the new composerTheme palette, adaptive color assertions, and updated sidebar behaviour expectations.

### go test ./cmd/bar/...
- green | 2026-01-12T22:57:06Z | exit 0
  - helper:diff-snapshot=7 files changed, 169 insertions(+), 39 deletions(-)
  - summary: CLI snapshot harness accepts the regenerated fixture with the wrapped history hint and ensures the Bubble Tea snapshot stays deterministic.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T22:57:06Z | exit 0
  - helper:diff-snapshot=7 files changed, 169 insertions(+), 39 deletions(-)
  - summary: Completion guardrails remain unchanged after the toast theming updates.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T22:57:06Z | exit 0
  - helper:diff-snapshot=7 files changed, 169 insertions(+), 39 deletions(-)
  - summary: Expect transcripts confirm the history, shortcut, and toast flows still render as expected with the new palette and fixture text.
