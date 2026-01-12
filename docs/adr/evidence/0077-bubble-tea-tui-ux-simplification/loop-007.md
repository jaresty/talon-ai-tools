## Behaviour outcome
Document and guard Bubble Tea layout composition by asserting sidebar content wraps within the Lip Gloss-constrained column width.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T13:47:03Z | exit 0
  - helper:diff-snapshot=2 files changed, 54 insertions(+), 2 deletions(-)
  - summary: unit coverage (including the new sidebar width assertion) verifies the layout stays within Lip Gloss column constraints while keeping history and preset rendering stable.
