# 049 – Centralize System-Prompt Handling for LLM Requests

## Status

Accepted

## Context

- Normal `model run` flows hydrate persona/intent/contract defaults into `GPTState.system_prompt` via `modelPrompt` (in `lib/talonSettings.py`) and send it automatically through `PromptSession.prepare_prompt` / `_build_request_context` / `build_request`.
- `model suggest` builds its request manually inside `_suggest_prompt_recipes_core_impl` and appends the system prompt ad hoc. This duplicates logic and risks drift if defaults/hydration rules change.
- There are scattered manual `format_messages("user", …)` calls; most still route through `PromptSession`, but suggest does not. Future flows could repeat the pattern and diverge.
- Tests cover system-prompt hydration for normal flows (`_tests/test_model_types_system_prompt.py`, `_tests/test_gpt_system_prompt_axes_hydration.py`, `_tests/test_system_prompt_meta_contract.py`) and now a characterization that suggest includes the system prompt, but we do not assert hydrated defaults (from `user.model_default_*`) are present in suggest.
- The system prompt is the single source of truth for persona/intent/contract defaults; we want every LLM request (run/suggest/pattern/etc.) to include the hydrated system prompt via the same path and rules.

## Decision

Centralize system-prompt attachment for all LLM requests and refactor suggest to use the same path as normal requests.

## Rationale

- Avoid drift between suggest and run: one helper applies hydrated persona/intent/contract defaults everywhere.
- Ensure defaults (`user.model_default_*`) and explicit stance settings are consistently hydrated and sent with every request.
- Simplify testing: a single surface to assert that hydrated system prompt is present.

## Plan

1) Extract a shared helper (for example, `build_system_messages()` or `PromptSession.add_system_prompt()`) that:
   - Hydrates `GPTState.system_prompt.format_as_array()` (persona/intent/contract defaults) and returns system messages.
   - Optionally appends `_build_request_context` snippets (app/lang/timeout/snippet) if not already applied.
2) Update `PromptSession.prepare_prompt` to call the helper (maintain current behavior).
3) Refactor `_suggest_prompt_recipes_core_impl` to use the helper instead of manual `append_request_messages`:
   - Build `user_text` via a small helper (`_suggest_prompt_text`) for testability.
   - Create a session, call `add_system_prompt`/helper, then add the suggest user message.
4) Add a characterization test that stubs `user.model_default_*` (or injects a `GPTSystemPrompt` with defaults) and asserts the suggest request includes hydrated system-prompt lines (persona, intent, completeness/scope/method/form/channel).
5) Audit other manual request builders (pattern debug, help/debug flows) to ensure they route through the same helper; document the rule: all LLM calls must include the shared system-prompt builder.

## Consequences

- Single code path for system prompts removes duplication and reduces drift risk.
- Tests become more meaningful: we can assert hydrated defaults appear in both run and suggest.
- Slight refactor cost in suggest; future features have a clear contract: use the shared helper.
