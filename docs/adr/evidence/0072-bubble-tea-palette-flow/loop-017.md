## Behaviour outcome
Include CLI command summaries alongside every palette history entry so pilots can replay actions directly from the docked history pane.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T21:54:43Z | exit 0
  - helper:diff-snapshot=3 files changed, 19 insertions(+), 8 deletions(-)
  - summary: Bart UI unit suite verifies history rendering now appends CLI summaries.

### go test ./cmd/bar/...
- green | 2026-01-12T21:54:43Z | exit 0
  - helper:diff-snapshot=3 files changed, 19 insertions(+), 8 deletions(-)
  - summary: CLI smoke fixture acknowledges CLI-summary change within history output.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T21:54:43Z | exit 0
  - helper:diff-snapshot=3 files changed, 19 insertions(+), 8 deletions(-)
  - summary: Completion guardrails remain unchanged.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T21:54:43Z | exit 0
  - helper:diff-snapshot=3 files changed, 19 insertions(+), 8 deletions(-)
  - summary: Expect transcripts now display `CLI: …` details inside history sections and history regex asserts the CLI text.
