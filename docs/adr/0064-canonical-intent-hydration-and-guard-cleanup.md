# 056 — Canonical intent hydration and guard cleanup
# 0064 — Canonical intent hydration and guard cleanup

## Status
Proposed

## Context
- Canonical persona intent tokens now flow through the suggestion pipeline unchanged. System prompt hydration (`_tests/test_gpt_suggest_context_snapshot.py::test_suggest_uses_hydrated_system_prompt_for_llm`, `_tests/test_prompt_session.py::PromptSessionTests::test_add_system_prompt_attaches_hydrated_persona_and_axes`) still expects the human-readable descriptions that previously came from the docs map, so both tests fail with raw tokens like `for appreciation`.
- Help Hub and other discovery surfaces rely on the orchestrator display map to provide speech hints. After the canonical-token change they fall back to generic "Say: intent <token>" messaging (`_tests/test_help_hub.py::test_help_hub_search_intent_voice_hint_uses_orchestrator`).
- Quick-help rendering now wraps persona presets across columns, but the test still asserts the legacy single-row string (`_tests/test_model_help_canvas_persona_commands.py::ModelHelpPersonaCommandTests::test_persona_block_shows_command_forms`).
- Overlay/guard helpers picked up new kwargs (`suppress_attr`, `on_block`, `allow_inflight`) and stopped re-exporting some lifecycle helpers. Tests that patch `close_common_overlays`, `guard_surface_request`, `notify`, or `last_drop_reason` fail (`_tests/test_model_response_overlay_lifecycle.py`, `_tests/test_model_suggestion_gui_guard.py`, `_tests/test_request_history_drawer_gating.py`, `_tests/test_surface_guidance.py`).
- A follow-up audit (Loop 005) confirmed the codebase still lacks a shared intent hydration helper and that passive guard semantics remain ambiguous, so the ADR now treats those items as explicit deliverables.

## Decision
- **Hydrate canonical intents for human-facing prompts without reviving aliases.** Extend the system prompt builder and Help Hub hint generation to look up descriptions via the orchestrator/persona docs map when an intent token is canonical. Storage remains strictly single-token (`decide`, `appreciate`, etc.); no alias fallback or multi-word normalization is reintroduced, and UI hydration is the only layer that surfaces descriptive text.
- **Deliver a shared hydration helper.** Ship a single helper (e.g., `hydrate_intent_token`) that all surfaces call before rendering labels so quick-help, prompt session, Help Hub, and suggestion UIs stay consistent.
- **Document and adapt the guard API.** Keep the new keyword-only signature, but re-export `last_drop_reason`/`set_drop_reason` where tests expect them, and update unit tests to account for `passive`, `suppress_attr`, and `on_block` parameters. Provide helper shims to avoid brittle patch targets.
- **Stabilise quick-help persona rendering.** Emit an explicit "Persona presets:" header row that includes the spoken shortcut (e.g., `peer`). Hydrate alias tokens via the shared helper so canonical spoken presets remain first-class.
- **Honor passive guard semantics.** Ensure `close_common_overlays(..., passive=True)` never calls `try_begin_request`, and that suppression flags clear drop reasons just as the non-passive path does.

## Consequences
- Multiple modules (`gpt.py`, `promptSession.py`, `helpHub.py`, `modelHelpCanvas.py`, `surfaceGuidance.py`, overlay guard helpers) will require coordinated updates to restore descriptive text while keeping canonical tokens internally.
- Guard-related tests will patch higher-level helpers instead of private attributes, reducing brittleness when guard signatures evolve again.
- UX surfaces retain canonical storage but regain human-readable descriptions, avoiding regressions in spoken hints or quick-help docs.

## Implementation Plan
1. Add the shared `hydrate_intent_token` helper and wire it into the suggest pipeline, prompt session, Help Hub, and quick-help rendering so every surface hydrates canonical tokens the same way.
2. Update guard utilities to expose backwards-compatible attributes (or provide documented replacements), keep `close_common_overlays(..., passive=True)` side-effect free, and adjust tests to tolerate the new kwargs while still verifying suppression cleanup.
3. Tweak quick-help drawing to rely on the helper for alias presentation and keep canonical spoken shortcuts first in the rendered list.
4. Re-run the failing test modules, then the full suite, to confirm coverage remains green.
