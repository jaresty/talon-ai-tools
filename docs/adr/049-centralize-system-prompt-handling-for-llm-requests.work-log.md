# 049 – Centralize System-Prompt Handling for LLM Requests – Work Log

## 2025-12-13 – Loop 1 (kind: behaviour+tests)
- Added shared `build_system_prompt_messages` and `PromptSession.add_system_prompt` helpers so all flows hydrate and attach persona/intent/contract defaults via one path; refactored `model suggest` to use the helper and share `_suggest_prompt_text`/hydrated context formatting. Paths updated: `lib/modelHelpers.py`, `lib/promptSession.py`, `GPT/gpt.py`.
- Strengthened suggest coverage with a defaults-hydration characterization (`test_suggest_hydrates_system_prompt_defaults_from_settings`) and reused shared prompt text helpers; ensured pipeline stubbing uses module objects. Paths updated: `_tests/test_gpt_suggest_context_snapshot.py`.
- Checks: `python3 -m pytest _tests/test_gpt_suggest_context_snapshot.py` (pass, 4 tests).
- Removal test: reverting this loop would drop the centralized system-prompt helper and suggest refactor, causing suggest to bypass hydrated defaults and removing the new guardrail test that asserts defaults are sent to the model.

## 2025-12-13 – Loop 2 (kind: guardrail/tests)
- Added a PromptSession guardrail ensuring `add_system_prompt` attaches the hydrated persona/intent/contract lines so all flows using the helper remain covered. Path updated: `_tests/test_prompt_session.py`.
- Checks: `python3 -m pytest _tests/test_prompt_session.py _tests/test_gpt_suggest_context_snapshot.py` (pass, 12 tests).
- Removal test: reverting this loop would drop the guardrail that enforces hydrated system-prompt attachment for PromptSession clients, weakening confidence that all LLM requests include the centralized system prompt.

## 2025-12-13 – Loop 3 (kind: status/adversarial completion check)
- Adversarial completion check for ADR 049: re-read `lib/promptSession.py`, `lib/modelHelpers.py`, `GPT/gpt.py`, `_tests/test_prompt_session.py`, `_tests/test_gpt_suggest_context_snapshot.py`; reran `python3 -m pytest _tests/test_prompt_session.py _tests/test_gpt_suggest_context_snapshot.py` (pass, 12 tests).
- Plausible gaps considered:
  - Other manual builders bypassing the helper (pattern/debug/help flows). Inspection: gpt pattern/help debug flows rely on existing PromptSession for run/replay and no additional system-message injection paths were found outside PromptSession/suggest. Out-of-scope for this ADR unless new bespoke request builders appear.
  - Request-context inclusion for suggest: kept optional by design; ADR scope is system-prompt centralization, not forcing app/lang context into suggest.
  - Tools/async flows: PromptSession helper attaches system prompt before additional messages; append flow already reuses the shared helper. No remaining gap found.
- Conclusion: in-repo objectives for ADR 049 are satisfied; status remains Accepted with guardrail tests in place. Removal test: reverting this loop would erase the adversarial completion evidence and could mask remaining drift risk if new manual builders appear later.
