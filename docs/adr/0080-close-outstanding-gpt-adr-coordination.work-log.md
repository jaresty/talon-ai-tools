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
- Behaviour: grammar-level busy tag (Workstream 3 / ADR-035). Validation: `.venv/bin/python -m pytest` with new tests asserting `gpt_busy` tag toggles on request lifecycle transitions.
