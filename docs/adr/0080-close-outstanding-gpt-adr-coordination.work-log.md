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
- Behaviour: guardrail regeneration for ADR-054 close-out (Workstream 4). Validation: `make axis-guardrails-ci` exits 0 with no unexpected drift.
