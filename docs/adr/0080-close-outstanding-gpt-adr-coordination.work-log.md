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
