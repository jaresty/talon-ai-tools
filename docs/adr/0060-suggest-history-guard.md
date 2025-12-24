# 0060 – Harden suggest flow history guards

## Status
Proposed

## Context
- `model run suggest` streams currently set `current_destination_kind = "suggest"` so the history append helper skips logging, but the skip logic is implicit. Telemetry still records `missing_directional` drops, causing confusion because the history contract is being reported even when the GUI intentionally drops entries lacking a directional axis (fog/fig/dig/ong/rog/bog/jog).
- When the model emits a suggestion without a directional token, the parser drops the entry and the GUI stays closed. This is expected, but there is no regression test covering the “missing directional → no history append” scenario, so it is easy to misinterpret telemetry as a logging bug.
- Suggest runs use the shared history append helper, which mixes synchronous and streaming flows. There is no explicit “skip history” parameter; callers must rely on destination checks or custom state.

## Decision
- Introduce an explicit `skip_history` flag in the history append helper so callers (e.g., the suggest flow) bypass history without relying solely on `current_destination_kind`.
- Add a regression test that feeds a suggest response without a directional token and asserts that `append_entry_from_request` is not invoked while telemetry still records the guardrail drop.
- Update developer-facing documentation and ADR 0059 to clarify that `missing_directional` in telemetry is expected when the model omits a directional lens; the absence of history entries is the intended outcome.

## Rationale
- Making the skip explicit removes confusion for future contributors, ensures async code paths cannot accidentally bypass the guard, and documents the responsible party for controlling history logging.
- Tests capturing the missing directional scenario provide confidence that telemetry drops do not imply history writes, preventing future regressions.

## Implementation Plan
1. Refactor `modelHelpers.append_entry_from_request` usage behind a new `_append_history_entry(..., skip_history=False)` helper shared by streaming/sync paths.
2. Thread `skip_history=True` from `_process_suggest_result` through `_finish_suggest` into the history helper.
3. Extend `_tests/test_gpt_actions.py` (or a new targeted test) to simulate a suggest response lacking a directional token and assert history append stays untouched.
4. Update ADR 0059 (Verification section) to call out the new regression test.

## Verification
- `python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_gpt_suggest_prompt_recipes_skips_history_append`
- `python3 -m pytest _tests/test_model_suggestion_gui.py`
- Review telemetry export after a suggest run to confirm only `missing_directional` drops remain when warranted and no history entries are recorded.

## Consequences
- The history helper becomes more explicit, reducing accidental logging for non-history destinations.
- Telemetry interpretation is clarified, reducing false alarms when the model violates the directional contract.
- Future features can opt-in to skip history cleanly (e.g., other Silent destinations) without duplicating guard code.
