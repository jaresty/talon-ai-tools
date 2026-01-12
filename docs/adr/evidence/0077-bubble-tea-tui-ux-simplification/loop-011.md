## Behaviour outcome
Finalize ADR 0077 by re-running the full validation matrix and marking the decision as accepted with all guardrails passing.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T14:34:08Z | exit 0
  - helper:diff-snapshot=1 file changed, 1 insertion(+)
  - summary: unit suite confirms dialog stack, layout guards, and typography helpers remain stable.

### go test ./cmd/bar/...
- green | 2026-01-12T14:34:28Z | exit 0
  - helper:diff-snapshot=1 file changed, 1 insertion(+)
  - summary: CLI integration tests remain aligned with the accepted ADR behaviours.

### python3 -m pytest _tests/test_bar_completion_cli.py
- green | 2026-01-12T14:34:50Z | exit 0
  - helper:diff-snapshot=1 file changed, 1 insertion(+)
  - summary: CLI completion guardrail passes, confirming coordination layers unchanged.

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T14:37:12Z | exit 0
  - helper:diff-snapshot=1 file changed, 1 insertion(+)
  - summary: expect transcripts verify sidebar typography, dialog stacking, and clipboard/history flows across the full scenario suite.
