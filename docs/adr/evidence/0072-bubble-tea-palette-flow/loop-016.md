## Behaviour outcome
Remove raw `--prompt` text from Bubble Tea CLI summaries and toasts so operators see grammar tokens and destinations without leaking full subject content.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T21:42:02Z | exit 0
  - helper:diff-snapshot=3 files changed, 68 insertions(+), 7 deletions(-)
  - summary: Bart UI unit suite passes with new display-command helper and prompt-free summaries test.

### go test ./cmd/bar/...
- green | 2026-01-12T21:42:02Z | exit 0
  - helper:diff-snapshot=3 files changed, 68 insertions(+), 7 deletions(-)
  - summary: CLI fixture updated to expect prompt-less summaries.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T21:42:02Z | exit 0
  - helper:diff-snapshot=3 files changed, 68 insertions(+), 7 deletions(-)
  - summary: Completion guardrails unaffected by CLI display changes.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T21:42:02Z | exit 0
  - helper:diff-snapshot=3 files changed, 68 insertions(+), 7 deletions(-)
  - summary: Expect transcripts now show `CLI: bar build …` without subject text while remaining stable.
