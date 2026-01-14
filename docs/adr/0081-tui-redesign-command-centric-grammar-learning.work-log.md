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

## loop-004 | helper:v20251223.1 | 2026-01-13

focus: ADR 0081 Decision → implement subject input modal (Ctrl+L) for entering subject text that gets passed to preview.

active_constraint: No way to enter subject content; operators cannot provide context for prompt generation (validation: `go test ./internal/bartui2 -run TestSubject`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Subject input is essential for real-world prompt building; without it, prompts lack context. |
| Probability | High | Modal pattern well-documented in bubbles-inputs and bubbletea-overlays skills. |
| Time Sensitivity | Medium | Core functionality needed before user testing. |
| Uncertainty note | Low | Uses standard bubbles/textarea component with established patterns. |

validation_targets:
- `go test ./internal/bartui2`
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0081-tui-redesign-command-centric-grammar-learning/loop-004.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD~1 -- internal/bartui2/program.go internal/bartui2/program_test.go`; rerun `go test ./internal/bartui2 -run TestSubject` to confirm tests fail.

delta_summary: helper:diff-snapshot=2 files changed — adds bubbles/textarea for subject input, adds subject/subjectInput/showSubjectModal fields, implements updateSubjectModal() for modal input routing, adds renderSubjectModal() with distinct styling, updates hotkey bar with ^L shortcut, adds 4 new tests for modal functionality.

loops_remaining_forecast: 2-3 loops. Confidence: medium — remaining work includes clipboard copy (Ctrl+B), command execution (Ctrl+Enter), and polish.

residual_constraints:
- Medium — Preview pane truncates without scroll. Mitigation: add bubbles viewport component.
- Low — No clipboard integration (Ctrl+B placeholder). Mitigation: next loop priority.
- Low — No command execution (Ctrl+Enter). Mitigation: subsequent loop.

next_work:
- Behaviour: Wire clipboard copy (Ctrl+B) to copy bar build command (validation: `go test ./internal/bartui2`).
- Behaviour: Implement command execution (Ctrl+Enter) (validation: `go test ./internal/bartui2`).

## loop-005 | helper:v20251223.1 | 2026-01-13

focus: ADR 0081 Decision → implement clipboard copy (Ctrl+B) to copy bar build command with toast feedback.

active_constraint: No way to export the constructed command; operators cannot share or reuse their built commands outside the TUI (validation: `go test ./internal/bartui2 -run TestClipboard`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | Medium | Clipboard copy enables workflow integration; users can paste commands into scripts or terminals. |
| Probability | High | Uses existing atotto/clipboard package already in project. |
| Time Sensitivity | Medium | Essential for real-world usage but not blocking other features. |
| Uncertainty note | Low | Standard clipboard integration pattern. |

validation_targets:
- `go test ./internal/bartui2`
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0081-tui-redesign-command-centric-grammar-learning/loop-005.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD~1 -- internal/bartui2/program.go internal/bartui2/program_test.go internal/barcli/tui2.go`; rerun `go test ./internal/bartui2 -run TestClipboard` to confirm tests fail.

delta_summary: helper:diff-snapshot=3 files changed — adds ClipboardWrite option and clipboardWrite/toastMessage fields, implements copyCommandToClipboard() with toast feedback, adds toastStyle (green), toast replaces hotkey bar when present and clears on key press, wires clipboard.WriteAll in tui2.go, adds 5 tests for clipboard/toast.

loops_remaining_forecast: 1-2 loops. Confidence: medium — remaining work includes command execution (Ctrl+Enter) and polish/viewport scroll.

residual_constraints:
- Medium — Preview pane truncates without scroll. Mitigation: add bubbles viewport component.
- Low — No command execution (Ctrl+Enter). Mitigation: next loop priority.

next_work:
- Behaviour: Implement command execution (Ctrl+Enter) with output display (validation: `go test ./internal/bartui2`).
- Behaviour: Add viewport scroll to preview pane (validation: `go test ./internal/bartui2`).

## loop-006 | helper:v20251223.1 | 2026-01-13

focus: ADR 0081 Decision → implement command execution (Ctrl+Enter) to run shell commands with preview piped as stdin.

active_constraint: No way to execute commands with the generated prompt; operators cannot test their prompts against tools like `pbcopy` or `claude` (validation: `go test ./internal/bartui2 -run TestCommand`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Command execution completes the workflow: build prompt → run command → see result. |
| Probability | High | Shell execution via exec.CommandContext is standard Go pattern. |
| Time Sensitivity | Medium | Core workflow feature needed for real-world usage. |
| Uncertainty note | Low | Uses context timeout and stdin piping, well-established patterns. |

validation_targets:
- `go test ./internal/bartui2`
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0081-tui-redesign-command-centric-grammar-learning/loop-006.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD~1 -- internal/bartui2/program.go internal/bartui2/program_test.go internal/barcli/tui2.go`; rerun `go test ./internal/bartui2 -run TestCommand` to confirm tests fail.

delta_summary: helper:diff-snapshot=3 files changed — adds RunCommand/CommandTimeout options, adds command modal with textinput, implements executeCommand() with stdin piping and timeout, adds renderCommandModal()/renderResultPane(), adds result mode with ^Y copy result and ^R return to preview, wires exec.CommandContext runner in tui2.go, adds 12 tests for command execution.

loops_remaining_forecast: 1 loop. Confidence: high — remaining work is polish (viewport scroll for preview/result).

residual_constraints:
- Medium — Preview/result panes truncate without scroll. Mitigation: add bubbles viewport component in next loop.

next_work:
- Behaviour: Add viewport scroll to preview and result panes (validation: `go test ./internal/bartui2`).

## loop-007 | helper:v20251223.1 | 2026-01-13

focus: ADR 0081 Decision → add viewport scroll to preview and result panes using bubbles/viewport component.

active_constraint: Preview and result panes truncate long content with "..." instead of allowing scroll; operators cannot view full prompt or command output (validation: `go test ./internal/bartui2 -run TestViewport`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | Medium | Scroll enables viewing full content; important for long prompts and command output. |
| Probability | High | Using established bubbles/viewport component with clear API. |
| Time Sensitivity | Low | Polish feature; core functionality complete. |
| Uncertainty note | Low | Standard viewport integration pattern. |

validation_targets:
- `go test ./internal/bartui2`
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0081-tui-redesign-command-centric-grammar-learning/loop-007.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD~1 -- internal/bartui2/program.go internal/bartui2/program_test.go`; rerun `go test ./internal/bartui2 -run TestViewport` to confirm tests fail.

delta_summary: helper:diff-snapshot=2 files changed — adds bubbles/viewport import, adds previewViewport/resultViewport fields, implements Ctrl+U/Ctrl+D/PgUp/PgDown scroll handlers, adds getPreviewPaneHeight() helper, updates render functions to use viewport.View() with scroll percentage indicator, updates hotkey bar with scroll hints, adds 4 tests for viewport scrolling.

loops_remaining_forecast: 0 loops. Confidence: high — all ADR 0081 core features implemented (three-pane layout, fuzzy completion, token tree, subject input, clipboard copy, command execution, viewport scroll).

residual_constraints:
- Low — Fuzzy matching is simple substring; could enhance with proper fuzzy algorithm. Mitigation: monitor usability feedback.
- Low — Preset management (Ctrl+P) not yet implemented. Mitigation: defer to follow-up ADR if needed.

next_work:
- ADR 0081 core implementation complete. Follow-up work (presets, syntax highlighting) can be tracked in new ADRs if requested.

## loop-008 | helper:v20251223.1 | 2026-01-14

focus: ADR 0081 Decision → implement stage-based token progression where tokens are presented in grammar order with inline stage markers.

active_constraint: Tokens are treated as a flat, unordered set; operators cannot see where tokens belong in the CLI grammar structure (validation: `go test ./internal/bartui2`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Stage progression is core to teaching the grammar; users learn token order through interaction. |
| Probability | High | Uses existing token categories with stage ordering. |
| Time Sensitivity | High | Critical for learning-oriented design. |
| Uncertainty note | Medium | Requires significant refactoring of token storage and completion filtering. |

validation_targets:
- `go test ./internal/bartui2`
- `go test ./internal/barcli`

evidence: `docs/adr/evidence/0081-tui-redesign-command-centric-grammar-learning/loop-008.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD~1 -- internal/bartui2/program.go internal/bartui2/program_test.go docs/adr/0081-tui-redesign-command-centric-grammar-learning.md`; rerun `go test ./internal/bartui2` to confirm tests fail.

delta_summary: helper:diff-snapshot=3 files changed — adds stageOrder slice for grammar progression, changes tokens from flat list to tokensByCategory map, adds currentStageIndex for stage tracking, adds 11 helper methods for stage management, updates completions to filter by current stage, adds inline stage marker [Stage?] in command pane, shows stage name as completion header with "Then:" hint, updates Tab to skip stage, updates 7 tests for stage-based behavior.

loops_remaining_forecast: 0 loops. Confidence: high — ADR 0081 stage-based progression implemented; all core features complete.

residual_constraints:
- Low — Fuzzy matching is simple substring; could enhance with proper fuzzy algorithm. Mitigation: monitor usability feedback.
- Low — Preset management (Ctrl+P) not yet implemented. Mitigation: defer to follow-up ADR if needed.
- Low — Persona stage not included in stageOrder. Mitigation: add if requested.

next_work:
- ADR 0081 implementation complete with stage-based progression. Follow-up work (presets, persona stage, syntax highlighting) can be tracked in new ADRs if requested.
