# ADR 0077 — Bubble Tea TUI interaction simplification and typography cues work log

## loop-001 | helper:v20251223.1 | 2026-01-12

focus: ADR 0077 Decision bullet 2 → restructure the sidebar into Compose, History, and Presets sections with progressive disclosure so overlapping controls stop crowding the main column.

active_constraint: History and preset content still render as an unlabelled block in `internal/bartui/program.go`, forcing operators to parse mixed bullets because the sidebar lacks section headers or collapsed states (validation: `scripts/tools/run-tui-expect.sh --all`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Clear sections reduce cognitive load and align with ADR 0077’s sidebar guidance |
| Probability | High | Updating the bartui view/state directly addresses the visual mixing reported |
| Time Sensitivity | Medium | Needed before layering shortcut overlays so future loops inherit a cleaner layout |
| Uncertainty note | Low | Behaviour is fully exercised via unit and expect harnesses |

validation_targets:
- `go test ./...`
- `scripts/tools/run-tui-expect.sh --all`
- `python3 -m pytest _tests/test_bar_completion_cli.py`

evidence: `docs/adr/evidence/0077-bubble-tea-tui-ux-simplification/loop-001.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go internal/bartui/program_test.go cmd/bar/testdata/tui_smoke.json tests/integration/tui/cases/token-palette-history.exp`; rerun `scripts/tools/run-tui-expect.sh --all` to confirm the mixed sidebar returns before reapplying the loop diff.

delta_summary: helper:diff-snapshot=4 files changed, 93 insertions(+), 26 deletions(-) — adds Compose/History/Presets headers, collapsible history messaging, updates unit expectations, and refreshes the smoke snapshot plus the history expect case.

loops_remaining_forecast: 3 loops (history metadata & icons; sidebar visibility toggle with persisted preference; in-app shortcut cheat sheet & typography polish). Confidence: medium — remaining work spans additional state, expect coverage, and documentation updates.

residual_constraints:
- Medium — History entries still render as plain text without type icons or timestamps, leaving action provenance ambiguous. Mitigation: extend history event struct with metadata, update rendering/tests, validate with `scripts/tools/run-tui-expect.sh --all`. Monitor when pilots report difficulty auditing history, or when ADR 0077 Decision bullet 4 is addressed.
- Medium — Sidebar visibility remains width-driven; no operator toggle persists preferences. Mitigation: introduce a manual toggle + state persistence and guard with `go test ./internal/bartui` plus expect coverage. Monitor cases where narrow terminals still show undesired sections (owner: ADR 0077 Decision bullet 3).

next_work:
- Behaviour: Add metadata (type icon + timestamp) to history entries with expect coverage (validation: `go test ./internal/bartui`, `scripts/tools/run-tui-expect.sh --all`).
- Behaviour: Implement sidebar visibility toggle with persisted preference (validation: `go test ./internal/bartui`, `cmd/bar/testdata/tui_smoke.json`, `scripts/tools/run-tui-expect.sh --all`).

## loop-002 | helper:v20251223.1 | 2026-01-12

focus: ADR 0077 Decision bullet 4 → enrich history entries with type metadata and timestamps so operators can scan provenance without parsing free-form text.

active_constraint: Sidebar history entries render as undifferentiated strings with no timing or type cues, forcing operators to guess whether a row is clipboard, token, or command related (validation: `scripts/tools/run-tui-expect.sh --all`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Metadata clarifies provenance for every event, unlocking ADR 0077 history auditability goals. |
| Probability | High | Updating the bartui model, formatter, and tests directly addresses the missing metadata pathway. |
| Time Sensitivity | Medium | Needed before sidebar toggle and shortcut overlay work so later loops inherit the improved history baseline. |
| Uncertainty note | Low | Behaviour covered by unit tests and expect harness. |

validation_targets:
- `go test ./internal/bartui`
- `scripts/tools/run-tui-expect.sh --all`
- `python3 -m pytest _tests/test_bar_completion_cli.py`

evidence: `docs/adr/evidence/0077-bubble-tea-tui-ux-simplification/loop-002.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go internal/bartui/program_test.go cmd/bar/testdata/tui_smoke.json tests/integration/tui/cases/clipboard-history.exp tests/integration/tui/cases/token-palette-history.exp`; rerun `scripts/tools/run-tui-expect.sh --all` to confirm history rows revert to plain text before reapplying the loop diff.

delta_summary: helper:diff-snapshot=5 files changed, 292 insertions(+), 84 deletions(-) — introduces history event kinds/timestamps, updates view rendering/tests, and refreshes expect scripts plus the smoke snapshot for the new sidebar layout.

loops_remaining_forecast: 2 loops (sidebar visibility toggle with persisted preference; in-app shortcut reference overlay and typography polish). Confidence: medium — remaining work touches layout state and overlay interactions.

residual_constraints:
- Medium — Sidebar visibility remains width-driven with no operator toggle or persisted preference. Mitigation: implement manual toggle state and update expect coverage (`go test ./internal/bartui`, `scripts/tools/run-tui-expect.sh --all`). Monitor reports of unpredictable column changes in narrow terminals.
- Medium — In-app shortcut cheat sheet (`Ctrl+?`) still absent, leaving ADR 0077 Decision bullet 5 unmet. Mitigation: add overlay plus documentation updates, validate via `go test ./internal/bartui`, `scripts/tools/run-tui-expect.sh --all`, and CLI snapshot refresh; monitor operator feedback about shortcut discoverability.

next_work:
- Behaviour: Implement sidebar visibility toggle with persisted preference (validation: `go test ./internal/bartui`, `cmd/bar/testdata/tui_smoke.json`, `scripts/tools/run-tui-expect.sh --all`).
- Behaviour: Add in-app shortcut reference overlay with typography adjustments (validation: `go test ./internal/bartui`, `scripts/tools/run-tui-expect.sh --all`, `python3 -m pytest _tests/test_bar_completion_cli.py`).

## loop-003 | helper:v20251223.1 | 2026-01-12

focus: ADR 0077 Decision bullet 3 → introduce a keyboard-controlled sidebar toggle with persisted preference so operators can collapse the sidebar independently of auto layout.

active_constraint: Sidebar visibility remains width-driven with no operator override, forcing operators to endure cramped columns even when they prefer a single-column experience (validation: `scripts/tools/run-tui-expect.sh --all`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Manual toggle unlocks ADR 0077 layout goals, reducing distraction in constrained terminals. |
| Probability | High | Updating bartui state, layout, and help text directly addresses the missing control. |
| Time Sensitivity | Medium | Needed before layering shortcut overlays so future loops inherit the final layout behaviour. |
| Uncertainty note | Low | Behaviour fully exercised via unit checks and expect harness. |

validation_targets:
- `go test ./internal/bartui`
- `scripts/tools/run-tui-expect.sh --all`
- `python3 -m pytest _tests/test_bar_completion_cli.py`

evidence: `docs/adr/evidence/0077-bubble-tea-tui-ux-simplification/loop-003.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go internal/bartui/program_test.go cmd/bar/testdata/tui_smoke.json tests/integration/tui/cases/launch-status.exp`; rerun `scripts/tools/run-tui-expect.sh --all` to confirm the sidebar toggle disappears before reapplying the loop diff.

delta_summary: helper:diff-snapshot=4 files changed, 117 insertions(+), 3 deletions(-) — adds sidebar preference state, Ctrl+G toggle handling, status/help updates, unit coverage, and refreshed fixtures for the new status messaging.

loops_remaining_forecast: 1 loop (in-app shortcut reference overlay and typography polish). Confidence: medium — remaining work spans overlay rendering plus expect coverage updates.

residual_constraints:
- Medium — In-app shortcut cheat sheet (`Ctrl+?`) still absent, leaving ADR 0077 Decision bullet 5 unmet. Mitigation: add overlay plus documentation updates, validate via `go test ./internal/bartui`, `scripts/tools/run-tui-expect.sh --all`, and CLI snapshot refresh; monitor operator feedback about shortcut discoverability.

next_work:
- Behaviour: Add in-app shortcut reference overlay with typography adjustments (validation: `go test ./internal/bartui`, `scripts/tools/run-tui-expect.sh --all`, `python3 -m pytest _tests/test_bar_completion_cli.py`).

## loop-004 | helper:v20251223.1 | 2026-01-12

focus: ADR 0077 Decision bullet 5 → ship the in-app shortcut reference overlay with grouped sections and typography cues so operators discover key bindings without leaving the TUI.

active_constraint: Shortcut reference overlay remains absent, so pressing Ctrl+? renders nothing and `scripts/tools/run-tui-expect.sh --all` cannot verify grouped shortcut cues (validation: `go test ./internal/bartui`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Embedded shortcuts unblock ADR 0077 guidance promises and reduce reliance on external docs. |
| Probability | High | Updating bartui views, tests, and fixtures directly introduces the overlay and hints. |
| Time Sensitivity | Medium | Needed before handoff so future loops inherit accurate status copy and shortcut discoverability. |
| Uncertainty note | Low | Behaviour covered by unit tests, CLI snapshot, and expect harness. |

validation_targets:
- `go test ./internal/bartui`
- `go test ./cmd/bar/...`
- `scripts/tools/run-tui-expect.sh --all`
- `python3 -m pytest _tests/test_bar_completion_cli.py`

evidence: `docs/adr/evidence/0077-bubble-tea-tui-ux-simplification/loop-004.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go internal/bartui/program_test.go cmd/bar/testdata/tui_smoke.json tests/integration/tui/cases/launch-status.exp`; rerun `go test ./internal/bartui` and `scripts/tools/run-tui-expect.sh --all` to confirm the shortcut reference disappears and fixtures revert before reapplying the loop diff.

delta_summary: helper:diff-snapshot=4 files changed, 200 insertions(+), 52 deletions(-) — adds grouped shortcut reference overlay, refreshes status and hints, updates the CLI snapshot, and aligns expect scripts.

loops_remaining_forecast: 0 loops. Confidence: medium — monitor typography across palettes but active constraint resolved.

residual_constraints:
- Low — Typography cadence across alternative terminal themes still needs verification. Mitigation: audit Lip Gloss styles against dark and light palettes using `scripts/tools/run-tui-expect.sh --all` with theme overrides; monitor pilot readability feedback. Owner: ADR 0077 follow-up.

next_work:
- Behaviour: Run visual audit of shortcut typography across supported themes (validation: `scripts/tools/run-tui-expect.sh --all` with theme overrides).

## loop-005 | helper:v20251223.1 | 2026-01-12

focus: ADR 0077 Decision bullet 5 → harden the shortcut reference experience with typography cues that persist after closing and highlight the active token category inside the Compose sidebar.

active_constraint: After loop-004 the overlay still occupied the entire layout and left artefacts on close, and the Compose section offered no visual cue for the focused token category, muting ADR 0077’s typography guidance (validation: `go test ./internal/bartui`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Clearing the overlay and highlighting token focus restores trust in the UI guidance called out in ADR 0077. |
| Probability | High | Adjusting the Bubble Tea view plus state wiring directly addresses the residual artefacts. |
| Time Sensitivity | Medium | Needed before handoff so operators no longer see stale overlay text or ambiguous token focus. |
| Uncertainty note | Low | Behaviour covered by unit tests, CLI snapshot, and expect harness refresh. |

validation_targets:
- `go test ./internal/bartui`
- `go test ./cmd/bar/...`
- `scripts/tools/run-tui-expect.sh --all`
- `python3 -m pytest _tests/test_bar_completion_cli.py`

evidence: `docs/adr/evidence/0077-bubble-tea-tui-ux-simplification/loop-005.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go internal/bartui/program_test.go cmd/bar/testdata/tui_smoke.json`; rerun `go test ./internal/bartui` and `scripts/tools/run-tui-expect.sh --all` to confirm the overlay artefacts return before reapplying the loop diff.

delta_summary: helper:diff-snapshot=3 files changed, 82 insertions(+), 20 deletions(-) — ensures the shortcut overlay renders full-screen with ClearScreen support and adds token category indicators to the Compose sidebar plus updated tests and fixture.

loops_remaining_forecast: 0 loops. Confidence: medium — typography theme audit remains the only open residual.

residual_constraints:
- Low — Typography cadence across alternative terminal themes still needs verification. Mitigation: audit Lip Gloss styles against dark and light palettes using `scripts/tools/run-tui-expect.sh --all` with theme overrides; monitor pilot readability feedback. Owner: ADR 0077 follow-up.

next_work:
- Behaviour: Run visual audit of shortcut typography across supported themes (validation: `scripts/tools/run-tui-expect.sh --all` with theme overrides).

## loop-006 | helper:v20251223.1 | 2026-01-12

focus: ADR 0077 Decision bullet 5 → reinforce shortcut overlay typography with theme-agnostic dividers so grouped commands stay scannable on both light and dark terminals.

active_constraint: Shortcut reference sections relied solely on bolded prose without any structural separators, reducing readability on high-contrast themes and leaving ADR 0077’s typography cue partially unmet (validation: `scripts/tools/run-tui-expect.sh --all`).

expected_value:
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | Medium | ASCII dividers create clear visual hierarchy regardless of terminal color support, improving scan speed. |
| Probability | High | Updating the overlay renderer directly adds the missing typography cue. |
| Time Sensitivity | Medium | Addressing the residual now prevents future loops from inheriting a readability gap. |
| Uncertainty note | Low | Behaviour exercised via unit tests, CLI suites, and the expect harness. |

validation_targets:
- `go test ./internal/bartui`
- `go test ./cmd/bar/...`
- `scripts/tools/run-tui-expect.sh --all`
- `python3 -m pytest _tests/test_bar_completion_cli.py`

evidence: `docs/adr/evidence/0077-bubble-tea-tui-ux-simplification/loop-006.md`

rollback_plan: `<VCS_REVERT>` = `git restore --source=HEAD -- internal/bartui/program.go`; rerun `go test ./internal/bartui` and `scripts/tools/run-tui-expect.sh --all` to confirm the prior typography returns before reapplying the loop diff.

delta_summary: helper:diff-snapshot=1 file changed, 12 insertions(+), 5 deletions(-) — adds ASCII dividers to shortcut section headers while preserving existing key descriptions.

loops_remaining_forecast: 0 loops. Confidence: high — typography audit complete; continue monitoring during future feature additions.

residual_constraints:
- Low — Continue monitoring future sidebar or overlay additions for typography regressions. Mitigation: rerun `scripts/tools/run-tui-expect.sh --all` when new sections land and verify dividers remain consistent; monitor operator feedback channels for readability reports.

next_work:
- Behaviour: When new shortcut sections are introduced, rerun the typography audit (validation: `scripts/tools/run-tui-expect.sh --all`).
