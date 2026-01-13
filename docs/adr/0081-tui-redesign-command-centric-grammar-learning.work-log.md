# ADR 0081 — TUI redesign: command-centric interface for grammar learning work log

## loop-001 | helper:v20251223.1 | 2026-01-13

focus: ADR 0081 Decision → establish `bar tui2` command entry point with basic three-pane Bubble Tea layout.

active_constraint: No entry point exists for the redesigned TUI; operators cannot launch the new interface to validate the three-pane layout concept (validation: `go test ./internal/bartui2`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Foundation for all subsequent ADR 0081 work; without entry point, no further development possible. |
| Probability | High | Creating new package and command routing is straightforward Go development. |
| Time Sensitivity | Medium | Needed before any UI refinement can begin. |
| Uncertainty note | Low | Standard Bubble Tea model implementation. |

validation_targets:
- `go test ./internal/bartui2`
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0081-tui-redesign-command-centric-grammar-learning/loop-001.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD~1 -- internal/bartui2 internal/barcli/tui2.go internal/barcli/app.go`; rerun `go test ./internal/bartui2` to confirm tests fail (package doesn't exist).

delta_summary: helper:diff-snapshot=4 files changed — creates `internal/bartui2/program.go` with three-pane Bubble Tea model (command input, tokens/completions, preview, hotkey bar), creates `internal/barcli/tui2.go` with `runTUI2()` entry point, adds `tui2` command routing to `app.go`, adds unit tests validating layout structure.

loops_remaining_forecast: 5-7 loops. Confidence: medium — remaining work includes fuzzy completion, token tree visualization, live preview integration, subject input modal, command execution, and polish.

residual_constraints:
- High — Completions pane is placeholder only; no actual fuzzy matching implemented. Mitigation: implement fuzzy search in next loop using token categories from grammar.
- Medium — Preview pane truncates without scroll; full preview requires viewport component. Mitigation: add bubbles viewport in subsequent loop.
- Low — No clipboard integration yet (Ctrl+B is placeholder). Mitigation: wire up clipboard copy after core interaction works.

next_work:
- Behaviour: Implement fuzzy completion matching across all token categories (validation: `go test ./internal/bartui2`).
- Behaviour: Add token tree visualization with category labels (validation: `go test ./internal/bartui2`).
