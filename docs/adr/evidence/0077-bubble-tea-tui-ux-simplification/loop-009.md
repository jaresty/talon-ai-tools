## Behaviour outcome
Adopt the dialog stacking helper for the shortcut overlay so future Bubble Tea modals can layer without reflow artefacts.

## Commands executed

### go test ./internal/bartui
- green | 2026-01-12T14:15:16Z | exit 0
  - helper:diff-snapshot=2 files changed, 224 insertions(+), 39 deletions(-)
  - summary: unit coverage exercises the dialog stack refactor and the new Esc-close test for the shortcut reference overlay.
