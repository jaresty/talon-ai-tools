## Behaviour outcome
Extend the Charmtone `composerTheme` to history headers, hints, and the summary strip so sidebar typography consistently reinforces the CLI grammar cues described in ADR 0072.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T23:09:27Z | exit 0
  - helper:diff-snapshot=2 files changed, 107 insertions(+), 6 deletions(-)
  - summary: Unit suite verifies the new sidebar/summary theme helpers emit TrueColor sequences while keeping the existing text hints intact.

### go test ./cmd/bar/...
- green | 2026-01-12T23:09:27Z | exit 0
  - helper:diff-snapshot=2 files changed, 107 insertions(+), 6 deletions(-)
  - summary: CLI snapshot harness confirms the deterministic fixture output matches when the styled summary strip degrades to plain text under NO_COLOR.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T23:09:27Z | exit 0
  - helper:diff-snapshot=2 files changed, 107 insertions(+), 6 deletions(-)
  - summary: Completion CLI guardrails remain synchronized with the grammar composer shortcuts after the palette update.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T23:09:27Z | exit 0
  - helper:diff-snapshot=2 files changed, 107 insertions(+), 6 deletions(-)
  - summary: Expect transcripts keep the history and summary prompts readable while exercising the new Charmtone-styled hints in live TUI runs.
