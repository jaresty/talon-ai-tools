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

## loop-002 | helper:v20251223.1 | 2026-01-13

focus: ADR 0081 Decision → implement fuzzy completion matching across all token categories with live filtering.

active_constraint: Completions pane shows placeholder text only; operators cannot discover available tokens by typing partial matches (validation: `go test ./internal/bartui2 -run TestFuzzyCompletion`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Fuzzy completion is core to the command-centric design; without it, token discovery is impossible. |
| Probability | High | Pattern matching and list filtering are well-understood implementations. |
| Time Sensitivity | Medium | Required before user testing can begin. |
| Uncertainty note | Low | Reuses bartui.TokenCategory structure; no new abstractions needed. |

validation_targets:
- `go test ./internal/bartui2`
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0081-tui-redesign-command-centric-grammar-learning/loop-002.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD~1 -- internal/bartui2/program.go internal/bartui2/program_test.go internal/barcli/tui2.go`; rerun `go test ./internal/bartui2 -run TestFuzzyCompletion` to confirm tests fail.

delta_summary: helper:diff-snapshot=3 files changed — adds `completion` type, `updateCompletions()` fuzzy matcher, `selectCompletion()` for applying selections, `getFilterPartial()` for extracting typed partial, renders completions with category labels and selection indicator, wires TokenCategories through tui2.go, adds 6 new tests for completion functionality.

loops_remaining_forecast: 4-5 loops. Confidence: medium — remaining work includes token tree with category labels, subject input modal, command execution, clipboard copy, and polish.

residual_constraints:
- Medium — Token tree shows flat list without category grouping. Mitigation: enhance tree rendering to show `Category: value` format in next loop.
- Medium — Preview pane truncates without scroll. Mitigation: add bubbles viewport component.
- Low — No clipboard integration (Ctrl+B placeholder). Mitigation: wire up after core interaction.
- Low — Fuzzy matching is simple substring; could enhance with proper fuzzy algorithm. Mitigation: monitor usability feedback.

next_work:
- Behaviour: Add token tree visualization with category labels (validation: `go test ./internal/bartui2`).
- Behaviour: Implement subject input modal (Ctrl+L) (validation: `go test ./internal/bartui2`).

## loop-003 | helper:v20251223.1 | 2026-01-13

focus: ADR 0081 Decision → implement token tree visualization with category labels using lipgloss/tree component.

active_constraint: Tokens displayed as flat list without category context; operators cannot see which grammar axis each selected token belongs to (validation: `go test ./internal/bartui2 -run TestTokenTree`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | Medium | Category labels help users understand token relationships and grammar structure. |
| Probability | High | Using established lipgloss/tree component with clear API. |
| Time Sensitivity | Medium | Improves UX but not blocking core functionality. |
| Uncertainty note | Low | Tree rendering pattern well-documented in skill references. |

validation_targets:
- `go test ./internal/bartui2`
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0081-tui-redesign-command-centric-grammar-learning/loop-003.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD~1 -- internal/bartui2/program.go internal/bartui2/program_test.go go.mod go.sum`; rerun `go test ./internal/bartui2 -run TestTokenTree` to confirm tests fail.

delta_summary: helper:diff-snapshot=4 files changed — upgrades lipgloss to v1.1.0 for tree package, adds `getCategoryForToken()` for category lookup, replaces manual tree rendering with `lipgloss/tree` using `RoundedEnumerator`, header shows "TOKENS (N)" count, adds 3 new tests for category features.

loops_remaining_forecast: 3-4 loops. Confidence: medium — remaining work includes subject input modal (Ctrl+L), command execution, clipboard copy, and polish.

residual_constraints:
- Medium — Preview pane truncates without scroll. Mitigation: add bubbles viewport component.
- Low — No clipboard integration (Ctrl+B placeholder). Mitigation: wire up after core interaction.
- Low — Subject input not yet implemented (Ctrl+L). Mitigation: next loop priority.

next_work:
- Behaviour: Implement subject input modal (Ctrl+L) (validation: `go test ./internal/bartui2`).
- Behaviour: Wire clipboard copy (Ctrl+B) (validation: `go test ./internal/bartui2`).
