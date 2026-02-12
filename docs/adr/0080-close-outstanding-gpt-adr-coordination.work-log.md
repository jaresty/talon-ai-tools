# Work Log — ADR-0080: Close Outstanding GPT Surface ADRs

**Helper version:** `helper:v20251223.1`
**Evidence root:** `docs/adr/evidence/0080/`
**VCS revert:** `git restore --source=HEAD`
**Validation target:** `.venv/bin/python -m pytest _tests/test_response_viewer_grammar.py -v`

---

## Loop 1 — 2026-02-11

**focus:** ADR-0080 Workstream 1 (ADR-0057) — add `model show response` and `model pass response` grammar rules

**active_constraint:** `model show response` and `model pass response` grammar rules are absent from all `.talon` files. The voice commands documented in ADR-0057 (and referenced in the streaming reminder toast) do not exist; users who follow the toast hint get a recognition failure.

**context cited:** ADR-0080 § Workstream 1 (remaining items); ADR-0057 § Decision 4/5 (grammar parity); `GPT/gpt-response-viewer.talon` (pre-loop: single rule); `GPT/gpt-confirmation-gui.talon` (pre-loop: `paste response` but no model-prefixed variant).

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | Medium | Grammar gap means the reminder toast's "say model show response" hint fails silently; parity goal of ADR-0057 unmet |
| Probability | High | Direct grammar additions; delegation to existing actions with no schema change |
| Time Sensitivity | Medium | Needed before streaming toast ships; low risk of conflict |

**validation_targets:**
- `.venv/bin/python -m pytest _tests/test_response_viewer_grammar.py -v`

**evidence:**
- red | 2026-02-11T00:00:00Z | exit 1 | `.venv/bin/python -m pytest _tests/test_response_viewer_grammar.py -v`
  - helper:diff-snapshot=0 files changed (test file added, grammar files untouched)
  - `show response` not found in gpt-response-viewer.talon; `pass response` not found in gpt-confirmation-gui.talon | inline
- green | 2026-02-11T00:05:00Z | exit 0 | `.venv/bin/python -m pytest _tests/test_response_viewer_grammar.py -v`
  - helper:diff-snapshot=2 files changed, 2 insertions(+)
  - Both rules present and delegation targets confirmed | inline
- removal | 2026-02-11T00:06:00Z | exit 1 | `git restore GPT/gpt-response-viewer.talon GPT/gpt-confirmation-gui.talon && .venv/bin/python -m pytest _tests/test_response_viewer_grammar.py -v`
  - helper:diff-snapshot=0 files changed (revert only)
  - `show response` not found in gpt-response-viewer.talon after revert | inline

**rollback_plan:** `git restore --source=HEAD GPT/gpt-response-viewer.talon GPT/gpt-confirmation-gui.talon _tests/test_response_viewer_grammar.py` then verify `.venv/bin/python -m pytest _tests/test_response_viewer_grammar.py` fails red.

**delta_summary:** 2 files changed, 2 insertions(+). Added `{user.model} show response$: user.model_response_canvas_open()` to `GPT/gpt-response-viewer.talon` (globally available, no tag gate). Added `^{user.model} pass response$: user.confirmation_gui_paste()` to `GPT/gpt-confirmation-gui.talon` (under existing `tag: user.model_window_open` context, alongside `paste response`). Also added `_tests/test_response_viewer_grammar.py` as specifying validation. Full suite: 1213 passed.

**loops_remaining_forecast:** 3 (medium confidence).
- Workstream 1 residual: streaming reminder toast referencing `model show response`; help surface copy refresh.
- Workstream 2 (ADR-0073): CLI discoverability — all items still outstanding.
- Workstream 3 (ADR-035): busy tag grammar — all items still outstanding.
- Workstream 4 (ADR-054): `make axis-guardrails-ci` docs regeneration — mechanical, one loop.

**residual_constraints:**
- severity: Medium | Workstream 1 remainder: streaming reminder toast referencing `model show response` is not yet implemented in `lib/requestUI.py`; users who receive the notification hint can now say the command but the notification itself doesn't fire yet. Mitigation: implement `_show_response_canvas_hint` delayed toast in requestUI. Monitoring: ADR-0057 status remains Proposed. Owning ADR: ADR-0057.
- severity: Low | Workstream 4 (ADR-054): `make axis-guardrails-ci` has not been run post preset-runtime changes; Help Hub may not reference new preset command syntax. Mitigation: run `make axis-guardrails-ci` in next docs loop. No code gap.
- severity: Low | Workstream 2 (ADR-0073), Workstream 3 (ADR-035): both entirely unimplemented; no active code breakage. Owning ADR: ADR-0073, ADR-035.

**next_work:**
- Behaviour: streaming reminder toast for `model show response` (Workstream 1 final item). Validation: `.venv/bin/python -m pytest _tests/test_request_ui.py` with new test asserting `_show_response_canvas_hint` fires after request completes for canvas-destination requests.
  → **Completed in Loop 2** (see below).
- Behaviour: guardrail regeneration for ADR-054 close-out (Workstream 4). Validation: `make axis-guardrails-ci` exits 0 with no unexpected drift.

---

## Loop 2 — 2026-02-11

**focus:** ADR-0080 Workstream 1 final item — update `_show_response_canvas_hint` to reference `model show response` (ADR-0057 D4)

**active_constraint:** `_show_response_canvas_hint` in `lib/requestUI.py` notifies "Say 'model last response'" — the toggle command — rather than the newly-added `model show response` open command. The hint is the only discoverable path to the feature; pointing at the wrong command causes user confusion.

**context cited:** ADR-0080 work-log Loop 1 `next_work`; ADR-0057 D4 (toast text spec); `lib/requestUI.py:111`; `lib/requestState.py:129–132` (COMPLETE event → `Surface.RESPONSE_CANVAS` → `_show_response_canvas_hint` fires).

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | Medium | Hint is the only discoverable path; wrong command erodes trust in the feature |
| Probability | High | One-line string change with direct test coverage |
| Time Sensitivity | Medium | Immediately corrects the Loop 1 grammar addition; low conflict risk |

**validation_targets:**
- `.venv/bin/python -m pytest _tests/test_request_ui.py::RequestUITests::test_response_canvas_hint_references_show_response_command -v`

**evidence:**
- red | 2026-02-11T01:00:00Z | exit 1 | `.venv/bin/python -m pytest _tests/test_request_ui.py::RequestUITests::test_response_canvas_hint_references_show_response_command -v`
  - helper:diff-snapshot=0 files changed (test added, implementation untouched)
  - `'model show response' not found in "Model done. Say 'model last response' to view details."` | inline
- green | 2026-02-11T01:02:00Z | exit 0 | `.venv/bin/python -m pytest _tests/test_request_ui.py::RequestUITests::test_response_canvas_hint_references_show_response_command -v`
  - helper:diff-snapshot=2 files changed, 21 insertions(+), 1 deletion(-)
  - hint now reads "Model done. Say 'model show response' to view." | inline
- removal | 2026-02-11T01:03:00Z | exit 1 | `git restore lib/requestUI.py && .venv/bin/python -m pytest _tests/test_request_ui.py::RequestUITests::test_response_canvas_hint_references_show_response_command -v`
  - helper:diff-snapshot=0 files changed (revert only)
  - `'model show response' not found` after revert | inline

**rollback_plan:** `git restore --source=HEAD lib/requestUI.py _tests/test_request_ui.py` then verify test fails red.

**delta_summary:** 2 files changed, 21 insertions(+), 1 deletion(-). Changed `_show_response_canvas_hint` toast from "Say 'model last response' to view details." to "Say 'model show response' to view." Added specifying validation `test_response_canvas_hint_references_show_response_command` to `_tests/test_request_ui.py`. Full suite: 1214 passed.

**loops_remaining_forecast:** 2 (medium confidence).
- Workstream 4 (ADR-054): `make axis-guardrails-ci` docs regeneration — one mechanical loop.
- Workstreams 2 & 3 (ADR-0073, ADR-035): CLI flags and busy tag — larger scope, future loops.

**residual_constraints:**
- severity: Low | Workstream 4 (ADR-054): `make axis-guardrails-ci` still not run post preset-runtime changes. Mitigation: dedicate next loop to guardrail regeneration. No code gap.
- severity: Low | Workstream 2 (ADR-0073), Workstream 3 (ADR-035): unimplemented; no active code breakage. Owning ADR: ADR-0073, ADR-035.
- severity: Low | ADR-0057 Workstream 1 complete: grammar and hint shipped. ADR-0057 help surface refresh (Help Hub copy) not yet done; low urgency. Owning ADR: ADR-0057.

**next_work:**
- Behaviour: guardrail regeneration for ADR-054 close-out (Workstream 4). Validation: `make axis-guardrails-ci` exits 0; check generated docs reference `model run … preset …`.
  → **Completed in Loop 3** (no diff — already clean).
- Behaviour: grammar-level busy tag (Workstream 3 / ADR-035). Validation: `.venv/bin/python -m pytest` with new tests asserting `gpt_busy` tag toggles on request lifecycle transitions.
  → **Completed in Loop 3** (see below).

---

## Loop 3 — 2026-02-11

**focus:** ADR-0080 Workstream 4 (ADR-054 close-out) + Workstream 3 (ADR-035 busy tag lifecycle)

**Workstream 4 observation (no diff):** `make axis-guardrails-ci` ran clean — 2 tests passed, 0 files changed. The preset runtime changes (from ADR-054 Loop 1) did not introduce any axis-catalog drift. ADR-054 validation criterion met.

**active_constraint (Workstream 3):** No `user.gpt_busy` tag exists anywhere in the codebase. When a request is in-flight, Talon grammar continues matching `model run …` commands; the Python `_reject_if_request_in_flight` guard is the only protection, leaving the voice recognizer free to consume the phrase and produce spurious drop notifications.

**context cited:** ADR-035 § Implementation sketch; ADR-0080 work-log Loop 2 `next_work`; `lib/requestUI.py:_on_state_change` (existing phase-change hook); `_tests/stubs/talon/__init__.py` (Context stub pattern); `_tests/test_model_suggestion_overlay_lifecycle.py` (ctx.tags test pattern).

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | High | Eliminates spurious recognition during in-flight requests; closes a real user-trust gap |
| Probability | High | Tag toggle is a well-defined state machine; hooks into existing _on_state_change path |
| Time Sensitivity | Medium | No deadline, but foundational for grammar gating (next loop) |

**validation_targets:**
- `.venv/bin/python -m pytest _tests/test_gpt_busy_tag.py -v`

**evidence:**
- red | 2026-02-11T02:00:00Z | exit 1 | `.venv/bin/python -m pytest _tests/test_gpt_busy_tag.py -v`
  - helper:diff-snapshot=0 files changed (test file added, no gptBusyTag module)
  - `ModuleNotFoundError: No module named 'talon_user.lib.gptBusyTag'` — 9 tests fail | inline
- green | 2026-02-11T02:08:00Z | exit 0 | `.venv/bin/python -m pytest _tests/test_gpt_busy_tag.py -v`
  - helper:diff-snapshot=2 files changed (lib/gptBusyTag.py new + lib/requestUI.py +5 lines)
  - All 9 tests pass; full suite 1223 passed | inline
- removal | 2026-02-11T02:09:00Z | exit 1 | `git restore lib/requestUI.py && rm lib/gptBusyTag.py && .venv/bin/python -m pytest _tests/test_gpt_busy_tag.py -v`
  - helper:diff-snapshot=0 files changed (revert only)
  - 9 tests fail with ModuleNotFoundError | inline

**rollback_plan:** `git restore --source=HEAD lib/requestUI.py && rm -f lib/gptBusyTag.py && git restore _tests/test_gpt_busy_tag.py` then verify 9 tests fail red.

**delta_summary:** 3 files changed (lib/gptBusyTag.py new 55 lines, lib/requestUI.py +5 lines, _tests/test_gpt_busy_tag.py new). gptBusyTag.py defines `mod.tag("gpt_busy")`, clears tag on module load (startup/reload safety), exposes `update(state)` that sets `["user.gpt_busy"]` for SENDING/STREAMING/TRANSCRIBING/LISTENING/CONFIRMING and clears for all other phases. requestUI._on_state_change calls `gptBusyTag.update(state)` on every transition. Full suite: 1223 passed.

**loops_remaining_forecast:** 2 (medium confidence).
- Workstream 3 residual: grammar gating — scope `model run` contexts to `not user.gpt_busy` in .talon files (requires identifying which grammar files contain the run commands and adding context guards).
- Workstream 2 (ADR-0073): CLI discoverability — all items still outstanding; larger scope.

**residual_constraints:**
- severity: Medium | Workstream 3 grammar gating: `user.gpt_busy` tag is now set on active phases but no Talon grammar file gates run commands on `not user.gpt_busy`. The tag exists but is not yet used to block recognition. Mitigation: next loop adds `not user.gpt_busy` context guards to gpt.talon run commands. Monitoring: ADR-035 status remains Proposed until grammar gating ships. Owning ADR: ADR-035.
- severity: Low | Workstream 2 (ADR-0073): CLI discoverability unimplemented. Owning ADR: ADR-0073.
- severity: Low | ADR-054 close-out: guardrails clean; ADR-054 can be marked Accepted pending support docs owners confirmation.

**next_work:**
- Behaviour: gate `model run` grammar on `not user.gpt_busy` (Workstream 3 final item).
  → **Completed in Loop 4** (see below).

---

## Loop 4 — 2026-02-11

**focus:** ADR-0080 Workstream 3 final item — gate `model run` grammar on `not user.gpt_busy` (ADR-035)

**active_constraint:** `user.gpt_busy` tag is toggled by the request lifecycle but no `.talon` file guards run commands against it. Talon grammar continues matching `{user.model} run …` phrases during in-flight requests; only the Python `_reject_if_request_in_flight` guard blocks execution.

**context cited:** ADR-035 § Decision (scope run contexts to `not gpt_busy`); ADR-0080 work-log Loop 3 `next_work`; `GPT/gpt.talon` (pre-loop: all run + non-run commands ungated); `_tests/test_request_history_talon_commands.py` (talon file content test pattern).

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | High | Eliminates recognition-layer duplicate runs; Talon stops matching the phrase entirely |
| Probability | High | Direct file split — context guard in new file header |
| Time Sensitivity | Medium | Completes ADR-035 definition of done |

**validation_targets:**
- `.venv/bin/python -m pytest _tests/test_gpt_run_busy_guard.py -v`

**evidence:**
- red | 2026-02-11T03:00:00Z | exit 1 | `.venv/bin/python -m pytest _tests/test_gpt_run_busy_guard.py -v`
  - helper:diff-snapshot=0 files changed (test file added, grammar unchanged)
  - `gpt-run-commands.talon does not exist` — 5 of 6 tests fail | inline
- green | 2026-02-11T03:08:00Z | exit 0 | `.venv/bin/python -m pytest _tests/test_gpt_run_busy_guard.py -v`
  - helper:diff-snapshot=3 files changed (gpt-run-commands.talon new, gpt.talon trimmed, test file)
  - All 6 tests pass; full suite 1229 passed | inline
- removal | 2026-02-11T03:09:00Z | exit 1 | `git restore GPT/gpt.talon && rm GPT/gpt-run-commands.talon && .venv/bin/python -m pytest _tests/test_gpt_run_busy_guard.py -v`
  - helper:diff-snapshot=0 files changed (revert only)
  - 5 tests fail; `gpt-run-commands.talon does not exist` | inline

**rollback_plan:** `git restore --source=HEAD GPT/gpt.talon && rm -f GPT/gpt-run-commands.talon && git restore _tests/test_gpt_run_busy_guard.py` then verify 5 tests fail red.

**delta_summary:** 3 files changed. Created `GPT/gpt-run-commands.talon` with `not user.gpt_busy` context header containing all 12 `{user.model} run` grammar rules. Removed those same run rules from `GPT/gpt.talon`, leaving only non-run commands (help, cancel, settings, last recipe, provider, persona, etc.) in the ungated file. Added `_tests/test_gpt_run_busy_guard.py` with 6 specifying validations. Full suite: 1229 passed.

**loops_remaining_forecast:** 1 (low confidence — depends on whether ADR-035 startup/reload cleanup and notification are required in the same ADR).
- ADR-035 definition of done is met: tag toggled, run grammar gated, Python guard intact, tag cleared on reload.
- Workstream 2 (ADR-0073): CLI discoverability — all items still outstanding; larger scope, future loops.

**residual_constraints:**
- severity: Low | ADR-035 optional item: notify when a run command is blocked by gpt_busy. The ADR marks this optional ("if Talon offers a hook"). No current Talon mechanism exposes a grammar-match-but-gated event. Mitigation: defer unless a hook becomes available. Owning ADR: ADR-035.
- severity: Low | Workstream 2 (ADR-0073): CLI discoverability unimplemented. Owning ADR: ADR-0073.
- severity: Low | ADR-035, ADR-0080 Workstream 3: mark ADR-035 Accepted pending stakeholder review.

**next_work:**
- Behaviour: mark ADR-035 Accepted and update ADR-0080 Workstream 3 status (documentation closure).
- Behaviour: Workstream 2 (ADR-0073) CLI discoverability. Validation: `go test ./cmd/bar ./internal/barcli` with new tests covering concise banner and flag validation.
  → **Completed first slice in Loop 5** (see below).

---

## Loop 5 — 2026-02-12

**focus:** ADR-0080 Workstream 2 (ADR-0073) first slice — advertise `bar tui2` in `generalHelpText` USAGE and COMMANDS sections

**active_constraint:** `generalHelpText` in `internal/barcli/app.go` mentions only `bar tui`; new users receive no signal that `bar tui2` exists as the recommended command-centric grammar learning surface (ADR-0081). First-time users following `bar help` cannot discover tui2 without reading ADR docs.

**context cited:** ADR-0080 work-log Loop 4 `next_work`; ADR-0073 § Decision (advertise `bar tui2` in `generalHelpText`); ADR-0081 § Migration Path (tui2 as preferred surface); `internal/barcli/app.go:70–187` (generalHelpText string).

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | Medium | Every `bar help` invocation omits the preferred interactive surface; direct discoverability gap |
| Probability | High | Two-string additions to generalHelpText + two Go tests; no schema change |
| Time Sensitivity | Medium | Foundational for further ADR-0073 work; unblocks `--command` and `--no-input` test scaffolding |

**validation_targets:**
- `go test ./internal/barcli -run "TestHelpAdvertisesTUI2|TestHelpTUI2IsRecommended" -v`

**evidence:**
- red | 2026-02-12T00:00:00Z | exit 1 | `go test ./internal/barcli -run "TestHelpAdvertisesTUI2|TestHelpTUI2IsRecommended" -v`
  - helper:diff-snapshot=0 files changed (test file added, app.go untouched)
  - `bar help output must mention tui2 as an interactive surface` — both tests fail | inline
- green | 2026-02-12T00:10:00Z | exit 0 | `go test ./internal/barcli -run "TestHelpAdvertisesTUI2|TestHelpTUI2IsRecommended" -v`
  - helper:diff-snapshot=2 files changed (app.go +7 lines, ADR-0073 doc updated)
  - Both tests pass; `internal/barcli` full suite passes | inline
- removal | 2026-02-12T00:11:00Z | exit 1 | `git stash && go test ./internal/barcli -run "TestHelpAdvertisesTUI2|TestHelpTUI2IsRecommended" -v`
  - helper:diff-snapshot=0 files changed (stash reverts app.go)
  - both tests fail: `tui2 as an interactive surface` / `tui2 must appear in the COMMANDS section` | inline
  - (restored with `git stash pop`)

**rollback_plan:** `git restore --source=HEAD internal/barcli/app.go && rm -f internal/barcli/app_help_cli_test.go` then verify both tests fail red.

**delta_summary:** 3 files changed. Added `bar tui2` to `generalHelpText` USAGE line and COMMANDS entry (marked "recommended for new users") in `internal/barcli/app.go`. Added `internal/barcli/app_help_cli_test.go` with 2 specifying validations: `TestHelpAdvertisesTUI2` (tui2 present in output) and `TestHelpTUI2IsRecommended` (tui2 with "recommended" in COMMANDS section). Also updated `docs/adr/0073-cli-discoverability-and-surface-parity.md` to redirect interactive surface references to `bar tui2` (ADR-0081). Pre-existing failure: `cmd/bar/TestTUIFixtureEmitsSnapshot` fails due to update banner on stderr — unrelated to this loop. `internal/barcli` full suite: passes.

**loops_remaining_forecast:** 3 (low confidence).
- ADR-0073 Workstream 2 residual: `--no-input` global flag, `--plain` formatter, `--command` flag for `bar tui2`, conversation-loops section in help — each a separate Go implementation loop.
- Pre-existing `TestTUIFixtureEmitsSnapshot` failure in `cmd/bar` should be addressed before full suite gates pass.

**residual_constraints:**
- severity: Medium | ADR-0073 remaining: `--no-input`, `--plain`, `--command` flags not yet implemented; help not yet tiered into sections. Mitigation: implement in subsequent loops, one flag per loop. Monitoring: ADR-0073 Proposed until all items ship. Owning ADR: ADR-0073.
- severity: Low | Pre-existing `cmd/bar/TestTUIFixtureEmitsSnapshot` failure: update banner prints to stderr, test asserts no stderr. Mitigation: suppress update banner in fixture/test mode or move banner to stdout. Owning ADR: none assigned.
- severity: Low | ADR-035 optional: notify when run command is blocked by gpt_busy. No Talon hook available. Owning ADR: ADR-035.

**next_work:**
- Behaviour: Workstream 2 — implement `--no-input` global flag in `bar build`, `bar preset use`, `bar tui`, `bar tui2` (ADR-0073 Decision item 3). Validation: `go test ./internal/barcli -run TestNoInput` with new tests asserting non-zero exit and guidance message when `--no-input` is passed and input would be prompted.
  → **Completed in Loop 6** (see below).

---

## Loop 6 — 2026-02-12

**focus:** ADR-0080 Workstream 2 (ADR-0073) second slice — implement `--no-input` flag; fix pre-existing `TestTUIFixtureEmitsSnapshot` failure

**active_constraint:** `--no-input` is not a recognised flag in `cli/config.go`; passing it to any `bar` subcommand produces `error: unknown flag --no-input` rather than a purposeful guidance message. Automation scripts cannot use `bar tui --no-input` to fail fast instead of launching an interactive session.

**context cited:** ADR-0080 work-log Loop 5 `next_work`; ADR-0073 § Decision item 3 (`--no-input` guard); `internal/barcli/cli/config.go` (Parse switch — no `--no-input` case); `internal/barcli/tui.go` / `tui2.go` (flag rejection pattern); `cmd/bar/main_test.go:177` (pre-existing stderr assertion failing due to cached update banner).

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | Medium | Automation scripts and CI fixtures can now pass `--no-input` to get fast failure instead of a hung interactive session |
| Probability | High | Direct flag addition + guard in runTUI/runTUI2; well-established pattern in codebase |
| Time Sensitivity | Medium | Unblocks future `--fixture … --no-input` smoke-test recipes referenced in ADR-0073 Validation |

**validation_targets:**
- `go test ./internal/barcli -run "TestNoInputRejectsTUI|TestNoInputRejectsTUI2|TestNoInputParsed" -v`
- `go test ./cmd/bar -run TestTUIFixtureEmitsSnapshot -v` (pre-existing failure fixed as part of this loop)

**evidence:**
- red | 2026-02-12T01:00:00Z | exit 1 | `go test ./internal/barcli -run "TestNoInputRejectsTUI|TestNoInputRejectsTUI2|TestNoInputParsed" -v`
  - helper:diff-snapshot=0 files changed (test file added, no implementation)
  - all 3 tests fail: `--no-input must be a recognised flag that produces guidance, not 'unknown flag'` | inline
- green | 2026-02-12T01:10:00Z | exit 0 | `go test ./internal/barcli/... ./cmd/bar/... -v`
  - helper:diff-snapshot=4 files changed, 21 insertions(+) — config.go +5, tui.go +4, tui2.go +4, main_test.go +8
  - all 3 no-input tests pass; `TestTUIFixtureEmitsSnapshot` passes; full suite green | inline
- removal | 2026-02-12T01:11:00Z | exit 1 | `git stash && go test ./internal/barcli -run "TestNoInputRejectsTUI|TestNoInputRejectsTUI2|TestNoInputParsed" -v`
  - helper:diff-snapshot=0 files changed (stash reverts)
  - all 3 fail: `unknown flag --no-input` | inline
  - (restored with `git stash pop`)

**rollback_plan:** `git restore --source=HEAD internal/barcli/cli/config.go internal/barcli/tui.go internal/barcli/tui2.go cmd/bar/main_test.go && rm -f internal/barcli/app_no_input_cli_test.go` then verify 3 tests fail red.

**delta_summary:** 5 files changed. Added `NoInput bool` field + `--no-input` parse case to `cli/config.go`. Added `NoInput` guard (exit 1 + `--fixture` guidance) at top of `runTUI` and `runTUI2`. Added `internal/barcli/app_no_input_cli_test.go` with 3 specifying validations. Fixed pre-existing `TestTUIFixtureEmitsSnapshot` failure by adding `t.Setenv("BAR_CONFIG_DIR", t.TempDir())` + mock update client to suppress cached update banner on stderr. Full suite: `internal/barcli` + `cmd/bar` both pass.

**loops_remaining_forecast:** 2 (low confidence).
- ADR-0073 residual: `--plain` formatter, `--command` flag for `bar tui2`, tiered help sections, conversation-loops section.
- Pre-existing `TestTUIFixtureEmitsSnapshot` fixed in this loop — no longer a blocker.

**residual_constraints:**
- severity: Medium | ADR-0073 remaining: `--plain` formatter, `--command` for `bar tui2` (`bartui2.Options.InitialCommand` field needed), tiered help sections. Mitigation: implement one per loop. Owning ADR: ADR-0073.
- severity: Low | `--no-input` for `bar build` with piped stdin not yet gated (test requires real pipe fixture). Defer until `--no-input` semantics are confirmed with automation teams. Owning ADR: ADR-0073.
- severity: Low | ADR-035 optional: notify when run command blocked by gpt_busy; no Talon hook available. Owning ADR: ADR-035.

**next_work:**
- Behaviour: Workstream 2 — implement `--command` flag for `bar tui2` (`bartui2.Options.InitialCommand` field + `cli/config.go` parse case). Validation: `go test ./internal/barcli -run TestTUI2Command` with new tests asserting initial command is seeded into the TUI options.
  → **Completed in Loop 7** (see below).

---

## Loop 7 — 2026-02-12

**focus:** ADR-0080 Workstream 2 (ADR-0073) third slice — implement `--command`/`--cmd` flag for `bar tui2`; add `SetTUI2Starter` for testability

**active_constraint:** `bartui2.Options` has no `InitialCommand` field; `cli/config.go` has no `--command`/`--cmd` parse case; `tui2.go` has no exported `SetTUI2Starter`. Passing `--command echo hello` to `bar tui2` fails with `unknown flag`. Operators cannot seed the Run Command field at launch time for reproducible demos or CI fixtures.

**context cited:** ADR-0080 work-log Loop 6 `next_work`; ADR-0073 § Decision (`--command` alias `--cmd` for `bar tui2`); `internal/bartui2/program.go` Options struct (no `InitialCommand` field); `internal/barcli/tui2.go` (no `SetTUI2Starter` export); `internal/barcli/cli/config.go` (no `--command` parse case).

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | Medium | Enables reproducible demos and CI fixtures that pre-fill the Run Command field; ADR-0073 Decision item |
| Probability | High | Direct field addition + parse cases + model seed; follows established pattern in codebase |
| Time Sensitivity | Low | No deadline dependency; next ADR-0073 items (`--plain`, tiered help) are independent |

**validation_targets:**
- `go test ./internal/barcli -run "TestTUI2CommandSeedsInitialCommand|TestTUI2CMDAlias|TestTUI2CommandParsed" -v`

**evidence:**
- red | 2026-02-12T02:00:00Z | exit 1 | `go test ./internal/barcli -run "TestTUI2CommandSeedsInitialCommand|TestTUI2CMDAlias|TestTUI2CommandParsed" -v`
  - helper:diff-snapshot=0 files changed (test file added, no implementation)
  - build failed: `undefined: barcli.SetTUI2Starter`, `opts.InitialCommand undefined`, `cfg.InitialCommand undefined` | inline
- green | 2026-02-12T02:10:00Z | exit 0 | `go test ./internal/barcli/... ./cmd/bar/... -v`
  - helper:diff-snapshot=3 files changed, 36 insertions(+)
  - all 3 tests pass; full suite passes (`internal/barcli` + `cmd/bar`) | inline
- removal | 2026-02-12T02:11:00Z | exit 1 | `git stash && go test ./internal/barcli -run "TestTUI2CommandSeedsInitialCommand|TestTUI2CMDAlias|TestTUI2CommandParsed" -v`
  - helper:diff-snapshot=0 files changed (stash reverts 3 modified files)
  - build failed: `undefined: barcli.SetTUI2Starter` / `opts.InitialCommand undefined` | inline
  - (restored with `git stash pop`)

**rollback_plan:** `git restore --source=HEAD internal/barcli/cli/config.go internal/barcli/tui2.go internal/bartui2/program.go && rm -f internal/barcli/app_tui2_command_cli_test.go` then verify 3 tests fail red.

**delta_summary:** 3 files changed, 36 insertions(+). Added `InitialCommand string` field + `--command`/`--cmd` parse cases (including `=` forms) to `cli/config.go`. Added `InitialCommand string` to `bartui2.Options` and seeded `shellCommandInput` with `opts.InitialCommand` in `newModel`. Added `InitialCommand` to `tuiOpts` in `runTUI2`, and added `SetTUI2Starter` export (mirrors `SetTUIStarter` pattern). Added `internal/barcli/app_tui2_command_cli_test.go` with 3 specifying validations. Full suite: `internal/barcli` + `cmd/bar` both pass.

**loops_remaining_forecast:** 2 (low confidence).
- ADR-0073 residual: `--plain` formatter for token/preset listings, tiered help sections, conversation-loops section, `bar help llm` automation flags documentation.
- Each remaining item is independent; 1–2 loops expected.

**residual_constraints:**
- severity: Medium | ADR-0073 remaining: `--plain` formatter (shared textual output mode), tiered help sections (grouped COMMANDS), conversation-loops section not yet in generalHelpText. Mitigation: implement in subsequent loops. Owning ADR: ADR-0073.
- severity: Low | `bar help llm` does not document `--no-input` or automation flags for TUI surfaces; LLMs consuming the reference cannot discover these flags. Mitigation: add an "Automation Flags" or "Non-interactive Usage" section to `help_llm.go`. Monitoring: user flagged this in session; defer to next loop. Owning ADR: ADR-0073.
- severity: Low | `--no-input` for `bar build` with piped stdin not yet gated. Defer until semantics confirmed. Owning ADR: ADR-0073.
- severity: Low | ADR-035 optional: notify when run command blocked by gpt_busy; no Talon hook available. Owning ADR: ADR-035.

**next_work:**
- Behaviour: Workstream 2 — document `--no-input` and `bar tui2 --command` in `bar help llm` output (add "Automation Flags" section to `internal/barcli/help_llm.go`). Validation: `go test ./internal/barcli -run TestHelpLLMAutomationFlags` with a test asserting `--no-input` and `--command` appear in the LLM reference.
