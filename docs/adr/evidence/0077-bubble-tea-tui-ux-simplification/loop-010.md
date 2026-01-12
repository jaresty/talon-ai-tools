## Behaviour outcome
Verify Bubble Tea sidebar typography and shortcut overlay legibility remain stable under the expect harness to support the theme audit called out in ADR 0077.

## Commands executed

### scripts/tools/run-tui-expect.sh --all
- green | 2026-01-12T14:24:04Z | exit 0
  - helper:diff-snapshot=0 files changed
  - summary: end-to-end expect suite confirms headings, dividers, and metadata render consistently with `NO_COLOR=1`, ensuring typography remains readable regardless of terminal themes.
