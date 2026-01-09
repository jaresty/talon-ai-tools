## 2026-01-09 — loop 001
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — enumerate salient tasks so Bubble Tea TUI delivery stays loop-addressable
- active_constraint: ADR 0070 lacked enumerated salient tasks linking Bubble Tea TUI behaviours to validation targets, leaving contributors without a falsifiable backlog to sequence initial implementation work.
- validation_targets:
  - git diff --no-index --stat /dev/null docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff --no-index /dev/null docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-001.md#loop-001-green--helper-diff-snapshot-git-diff----no-index----stat--devnull-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-001.md#loop-001-green--helper-diff-snapshot-git-diff----no-index--devnull-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-001.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 56 insertions(+) — recorded a salient-task backlog capturing state modeling, Bubble Tea wiring, validation coverage, and documentation so future loops can sequence the build.
- loops_remaining_forecast: 6 loops (CLI entrypoint scaffolding, state model integration, async command pipeline, layout polish, automated tests, documentation updates) — medium confidence given new UI footprint.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented, so `bar` cannot yet launch a TUI (severity: high; mitigation: scaffold `bar tui` command backed by a Bubble Tea `tea.Program`; monitoring: go test ./cmd/bar/... once entrypoint lands).
- next_work:
  - Behaviour: Scaffold `bar tui` entrypoint that loads grammar metadata and boots a Bubble Tea program (validation via go test ./cmd/bar/... after implementation).

## 2026-01-09 — loop 002
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — lock Bubble Tea entrypoint to `bar tui` subcommand inside existing CLI
- active_constraint: ADR 0070 still presented ambiguous packaging guidance (“subcommand or separate binary”), preventing CLI maintainers from sequencing wiring work and release integration for the Bubble Tea TUI.
- validation_targets:
  - git diff --no-index --stat /dev/null docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff --no-index /dev/null docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-002.md#loop-002-green--helper-diff-snapshot-git-diff----no-index----stat--devnull-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-002.md#loop-002-green--helper-diff-snapshot-git-diff----no-index--devnull-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-002.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 56 insertions(+) — clarified Decision and Follow-up to mandate a `bar tui` subcommand so wiring, packaging, and release work can proceed without debating a separate binary.
- loops_remaining_forecast: 6 loops (CLI entrypoint scaffolding, state model integration, async command pipeline, layout polish, automated tests, documentation updates) — medium confidence with clarified entrypoint path.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement CLI wiring and program bootstrap; monitoring: go test ./cmd/bar/... once code lands).
- next_work:
  - Behaviour: Scaffold `bar tui` entrypoint that loads grammar metadata and boots a Bubble Tea program (validation via go test ./cmd/bar/... after implementation).

## 2026-01-09 — loop 003
- helper_version: helper:v20251223.1
- focus: Decision § validation — register canonical commands for Bubble Tea TUI guardrails
- active_constraint: ADR 0070 listed qualitative validation guidance only, leaving maintainers without canonical commands to prove the Bubble Tea TUI wiring, state parity, or interactive smoke tests.
- validation_targets:
  - git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-003.md#loop-003-green--helper-diff-snapshot-git-diff--stat-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-003.md#loop-003-green--helper-diff-snapshot-git-diff-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-003.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 8 ++++---- — enumerated explicit `go test` and `go run` validation commands so future loops can register evidence against the TUI behaviour.
- loops_remaining_forecast: 5 loops (CLI entrypoint scaffolding, state model integration, async command pipeline, layout polish, documentation/tests execution) — medium confidence with validation targets now anchored.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement CLI wiring and program bootstrap; monitoring: go test ./cmd/bar/... once code lands).
  - Interactive smoke test harness for Bubble Tea panes does not yet exist (severity: medium; mitigation: script `go run ./cmd/bar tui --fixture …` with transcript capture; monitoring: manual transcript diff until harness automated).
- next_work:
  - Behaviour: Scaffold `bar tui` entrypoint that loads grammar metadata and boots a Bubble Tea program (validation via go test ./cmd/bar/... after implementation).

## 2026-01-09 — loop 004
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — align `bar tui` wiring plan with CLI completion validation
- active_constraint: ADR 0070 follow-up omitted explicit CLI completion updates for the new subcommand, leaving release prep without a falsifiable check that `bar tui` appears in shell completions.
- validation_targets:
  - git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-004.md#loop-004-green--helper-diff-snapshot-git-diff--stat-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-004.md#loop-004-green--helper-diff-snapshot-git-diff-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-004.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 2 +-
  — expanded follow-up to require refreshing CLI completions and to cite `go test ./cmd/bar/...` plus `python3 -m pytest _tests/test_bar_completion_cli.py` as the validation path.
- loops_remaining_forecast: 5 loops (CLI entrypoint scaffolding, state model integration, async command pipeline, layout polish, documentation/tests execution) — medium confidence now that completions validation is recorded.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement CLI wiring and program bootstrap; monitoring: go test ./cmd/bar/... once code lands).
  - CLI completion metadata has not yet been regenerated to include `bar tui` (severity: medium; mitigation: extend completion command tables alongside entrypoint work; monitoring: python3 -m pytest _tests/test_bar_completion_cli.py).
  - Interactive smoke test harness for Bubble Tea panes does not yet exist (severity: medium; mitigation: script `go run ./cmd/bar tui --fixture …` with transcript capture; monitoring: manual transcript diff until harness automated).
- next_work:
  - Behaviour: Scaffold `bar tui` entrypoint that loads grammar metadata, boots a Bubble Tea program, and updates completion metadata (validation via go test ./cmd/bar/... and python3 -m pytest _tests/test_bar_completion_cli.py after implementation).

## 2026-01-09 — loop 005
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — document package reuse expectations for `bar tui`
- active_constraint: ADR 0070 follow-up did not state that the new `bar tui` subcommand must reuse existing `cmd/bar` and `internal/barcli` packages, risking duplicate wiring and inconsistent guardrails across binaries.
- validation_targets:
  - git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-005.md#loop-005-green--helper-diff-snapshot-git-diff--stat-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-005.md#loop-005-green--helper-diff-snapshot-git-diff-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-005.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 2 +- — clarified follow-up to note package reuse so implementation avoids duplicating CLI wiring.
- loops_remaining_forecast: 4 loops (CLI entrypoint scaffolding, state model integration, async command pipeline, documentation/tests execution) — medium confidence with reuse guidance now recorded.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement CLI wiring and program bootstrap; monitoring: go test ./cmd/bar/... once code lands).
  - CLI completion metadata has not yet been regenerated to include `bar tui` (severity: medium; mitigation: extend completion command tables alongside entrypoint work; monitoring: python3 -m pytest _tests/test_bar_completion_cli.py).
  - Interactive smoke test harness for Bubble Tea panes does not yet exist (severity: medium; mitigation: script `go run ./cmd/bar tui --fixture …` with transcript capture; monitoring: manual transcript diff until harness automated).
- next_work:
  - Behaviour: Scaffold `bar tui` entrypoint that loads grammar metadata, boots a Bubble Tea program, reuses shared packages, and updates completion metadata (validation via go test ./cmd/bar/... and python3 -m pytest _tests/test_bar_completion_cli.py after implementation).

## 2026-01-09 — loop 006
- helper_version: helper:v20251223.1
- focus: Salient Tasks — add CLI completion/packaging backlog item for `bar tui`
- active_constraint: ADR 0070 Salient Tasks omitted a work item for refreshing CLI completions and release automation, leaving teams without a tracked rung to deliver the `bar tui` shell experience.
- validation_targets:
  - git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-006.md#loop-006-green--helper-diff-snapshot-git-diff--stat-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-006.md#loop-006-green--helper-diff-snapshot-git-diff-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-006.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 1 + — added a Salient Task to track CLI completion refresh, release notes, and packaging updates required for `bar tui` launch.
- loops_remaining_forecast: 4 loops (CLI entrypoint scaffolding, state model integration, async command pipeline, documentation/tests execution) — medium confidence with completion backlog now explicit.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement CLI wiring and program bootstrap; monitoring: go test ./cmd/bar/... once code lands).
  - CLI completion metadata has not yet been regenerated to include `bar tui` (severity: medium; mitigation: extend completion command tables alongside entrypoint work; monitoring: python3 -m pytest _tests/test_bar_completion_cli.py).
  - Interactive smoke test harness for Bubble Tea panes does not yet exist (severity: medium; mitigation: script `go run ./cmd/bar tui --fixture …` with transcript capture; monitoring: manual transcript diff until harness automated).
- next_work:
  - Behaviour: Scaffold `bar tui` entrypoint that loads grammar metadata, boots a Bubble Tea program, reuses shared packages, and updates completion metadata (validation via go test ./cmd/bar/... and python3 -m pytest _tests/test_bar_completion_cli.py after implementation).

## 2026-01-09 — loop 007
- helper_version: helper:v20251223.1
- focus: Follow-up — define MVP scope and pilot plan for `bar tui`
- active_constraint: ADR 0070 still listed a broad follow-up backlog that obscured the minimal product needed for early users, preventing the team from focusing on a shippable MVP slice.
- validation_targets:
  - git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-007.md#loop-007-green--helper-diff-snapshot-git-diff--stat-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-007.md#loop-007-green--helper-diff-snapshot-git-diff-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-007.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 1 + — reframed follow-up to emphasize an MVP `bar tui` slice, pilot guide, and backlog triage after feedback.
- loops_remaining_forecast: 3 loops (implement MVP entrypoint, capture pilot feedback, decide next backlog) — medium confidence now that MVP is scoped.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement minimal entrypoint with preview; monitoring: go test ./cmd/bar/... once code lands).
- next_work:
  - Behaviour: Implement MVP `bar tui` entrypoint with shared packages, add smoke run, and document pilot instructions (validation via go test ./cmd/bar/... and go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen).

## 2026-01-09 — loop 011
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — remove external pilot planning steps from ADR
- active_constraint: ADR 0070 follow-up still referenced extra pilot artefacts outside the repo, creating expectations that no longer match the actual single-user rollout.
- validation_targets:
  - git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-011.md#loop-011-green--helper-diff-snapshot-git-diff--stat-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-011.md#loop-011-green--helper-diff-snapshot-git-diff-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-011.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 3 --- — removed external quickstart/personal-note instructions so the ADR stays focused on in-repo work.
- loops_remaining_forecast: 2 loops (ship MVP entrypoint, review personal feedback) — medium confidence with implementation still pending.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement minimal entrypoint with preview; monitoring: go test ./cmd/bar/... once code lands).
- next_work:
  - Behaviour: Implement MVP `bar tui` entrypoint with shared packages, add smoke run, and note outcomes in this work-log (validation via go test ./cmd/bar/... and go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen).

## 2026-01-09 — loop 012
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — keep validation scoped to repository artefacts
- active_constraint: ADR 0070 still called for personal note-taking as part of validation, exceeding the in-repo responsibilities of this loop.
- validation_targets:
  - git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-012.md#loop-012-green--helper-diff-snapshot-git-diff--stat-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-012.md#loop-012-green--helper-diff-snapshot-git-diff-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-012.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 3 --- — dropped personal note-taking references from validation and residual constraints so only in-repo actions remain.
- loops_remaining_forecast: 2 loops (ship MVP entrypoint, review implementation feedback) — medium confidence with build work still pending.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement minimal entrypoint with preview; monitoring: go test ./cmd/bar/... once code lands).
- next_work:
  - Behaviour: Implement MVP `bar tui` entrypoint with shared packages, add smoke run, and document pilot instructions (validation via go test ./cmd/bar/... and go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen).


## 2026-01-09 — loop 008
- helper_version: helper:v20251223.1
- focus: Validation — streamline MVP guardrail commands for pilot launch
- active_constraint: ADR 0070 validation still expected broader test coverage than the MVP requires, slowing down the small-cohort rollout and adding unnecessary process.
- validation_targets:
  - git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-008.md#loop-008-green--helper-diff-snapshot-git-diff--stat-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-008.md#loop-008-green--helper-diff-snapshot-git-diff-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-008.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 7 +++---- — pared validation to `go test ./cmd/bar/...`, a `go run` smoke check, and structured pilot feedback capture so the cohort can iterate quickly.
- loops_remaining_forecast: 2 loops (ship MVP entrypoint, review pilot feedback) — medium confidence with validation shrink-wrapped.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement minimal entrypoint with preview; monitoring: go test ./cmd/bar/... once code lands).
- next_work:
  - Behaviour: Implement MVP `bar tui` entrypoint with shared packages, add smoke run, and document pilot instructions (validation via go test ./cmd/bar/... and go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen).

## 2026-01-09 — loop 010
- helper_version: helper:v20251223.1
- focus: Decision § follow-up — tailor MVP docs to a single-operator pilot
- active_constraint: ADR 0070 still described a multi-person pilot, misrepresenting the actual single-user rollout and creating unnecessary coordination steps.
- validation_targets:
  - git diff --stat docs/adr/0070-bubble-tea-prompt-editor-tui.md
  - git diff docs/adr/0070-bubble-tea-prompt-editor-tui.md
- evidence:
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-010.md#loop-010-green--helper-diff-snapshot-git-diff--stat-docs-adr-0070-bubble-tea-prompt-editor-tui.md
  - green: docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-010.md#loop-010-green--helper-diff-snapshot-git-diff-docs-adr-0070-bubble-tea-prompt-editor-tui.md
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-bubble-tea-prompt-editor-tui.md docs/adr/0070-bubble-tea-prompt-editor-tui.work-log.md docs/adr/evidence/0070-bubble-tea-prompt-editor-tui/loop-010.md`
- delta_summary: helper:diff-snapshot=docs/adr/0070-bubble-tea-prompt-editor-tui.md | 7 ++++--- — narrowed validation, follow-up, and salient tasks to reflect single-user trials and personal feedback tracking.
- loops_remaining_forecast: 2 loops (ship MVP entrypoint, review personal feedback) — medium confidence with implementation still pending.
- residual_constraints:
  - Bubble Tea entrypoint remains unimplemented; `bar tui` subcommand still needs scaffolding (severity: high; mitigation: implement minimal entrypoint with preview; monitoring: go test ./cmd/bar/... once code lands).
- next_work:
  - Behaviour: Implement MVP `bar tui` entrypoint with shared packages, add smoke run, and document pilot instructions (validation via go test ./cmd/bar/... and go run ./cmd/bar tui --fixture cmd/bar/testdata/grammar.json --no-alt-screen).

