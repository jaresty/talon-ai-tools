## Behaviour outcome
Amend ADR 0077 with CLI command input mode design direction so future loops implement Tab-to-complete behavior that teaches the CLI grammar directly.

## Commands executed

### ADR review
- green | 2026-01-13T07:00:00Z | manual review
  - helper:diff-snapshot=1 file changed, 6 insertions(+)
  - summary: ADR 0077 amended with CLI command input mode — Context bullet documents learning gap, Decision bullet describes Tab completion design, Rationale bullet explains learning transfer, Consequences bullet outlines implementation, Follow-up bullet queues execution.

## Implementation notes
- User reported Tab claimed to "cycle completions" but actually cycled focus between palette panes
- Investigation revealed the mismatch stemmed from a deeper design gap: the "select from list" palette abstracts the CLI grammar
- Designed CLI command input mode where:
  - Palette filter shows live `bar build` command (e.g., `bar build static=assumption minimal`)
  - Tab cycles through completions at cursor position (after `=` completes values, elsewhere completes categories)
  - Category/option panes remain visible as visual scaffolding for discoverability
  - Learning transfer is direct: syntax typed matches syntax used in terminal
- ADR 0077 amended with this direction; implementation deferred to subsequent loops
