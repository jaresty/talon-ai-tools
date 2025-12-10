# 0036 Concordance – Static Prompt Axis SSOT and GUI Alignment – Work Log

## 2025-12-10
- Slice: establish a static prompt catalog helper to feed doc generation and Talon list drift checks (Phase 1 of ADR-0036).
- Changes:
  - Added a catalog helper in `lib/staticPromptConfig.py` that surfaces profiled entries, Talon list tokens, and unprofiled tokens for drift detection.
  - Rewired `GPT/gpt.py::_build_static_prompt_docs` to render from the catalog SSOT rather than reimplementing list/profile traversal.
  - Added a guardrail test to assert the catalog exposes a profiled prompt with axes and includes the Talon list token set.
- Validation: `python3 -m pytest _tests/test_static_prompt_docs.py`.
- Follow-ups: extend catalog to emit Talon-list rendering/validation for update tooling; retrofit GUIs to reuse the same catalog/hydrator façade (Phase 2); add a coordinator for suggest/rerun recap (Phase 3).

## 2025-12-10
- Slice: share axis hydration maps across GUIs (Phase 2 start) to reduce drift from Talon list parsing.
- Changes:
  - Added `axis_docs_map` / `axis_hydrate_token` helpers in `lib/axisMappings.py` as the SSOT for axis descriptions.
  - Updated `lib/modelPatternGUI.py` and `lib/modelPromptPatternGUI.py` to pull axis descriptions from `axisMappings` instead of re-parsing Talon list files.
  - Added `_tests/test_axis_mappings.py` to guard the new façade behaviour.
- Validation: `python3 -m pytest _tests/test_axis_mappings.py _tests/test_model_pattern_gui.py _tests/test_prompt_pattern_gui.py`.
- Follow-ups: route other GUIs (`modelHelpGUI`, `modelSuggestionGUI`) and Talon settings hydration through the same façade; add a coordinator for suggest/rerun recap (Phase 3).

## 2025-12-10
- Slice: align quick-help canvas axis keys with the shared axis mapping façade (Phase 2 continuation).
- Changes:
  - Swapped `lib/modelHelpCanvas.py` axis key sourcing from direct `axisConfig` access to `axis_docs_map`, keeping quick-help in lockstep with the SSOT hydrator.
- Validation: `python3 -m pytest _tests/test_axis_mappings.py _tests/test_model_help_canvas.py`.
- Follow-ups: reuse the façade in any remaining GUI axis surfaces (suggestion/source maps already share pattern GUI constants); proceed to Phase 3 suggestion/rerun coordinator.

## 2025-12-10
- Slice: introduce a suggestion state coordinator (Phase 3 start) to centralise `last_*` updates for suggestions.
- Changes:
  - Added `lib/suggestionCoordinator.py` with `record_suggestions` and `last_suggestions` over `GPTState`.
  - Wired `GPT/gpt.py::gpt_suggest_prompt_recipes_with_source` to record suggestions via the coordinator instead of writing GPTState directly.
  - Added `_tests/test_suggestion_coordinator.py` to guard the coordinator behaviour.
- Validation: `python3 -m pytest _tests/test_suggestion_coordinator.py`.
- Follow-ups: extend the coordinator to own rerun/recap inputs and route rerun entrypoints through it; consider lifting suggestion GUI consumption to the coordinator API.

## 2025-12-10
- Slice: route suggestion GUI consumption through the suggestion coordinator (Phase 3 continuation).
- Changes:
  - Added `suggestion_entries`/`suggestion_source` helpers in `lib/suggestionCoordinator.py` for validated records and source keys.
  - Updated `lib/modelSuggestionGUI.py` to pull suggestion entries and source from the coordinator instead of raw `GPTState`.
  - Extended `_tests/test_suggestion_coordinator.py` to cover the new helpers.
- Validation: `python3 -m pytest _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py`.
- Follow-ups: continue moving rerun/recap inputs under the coordinator to centralise `last_*` handling.

## 2025-12-10
- Slice: centralise suggestion selection state updates in the coordinator (Phase 3 continuation).
- Changes:
  - Added `set_last_recipe_from_selection` to `lib/suggestionCoordinator.py` to own `last_*` updates for suggestion selections.
  - Updated `lib/modelSuggestionGUI.py` to call the coordinator instead of mutating `GPTState` directly.
  - Extended `_tests/test_suggestion_coordinator.py` to characterise the new helper.
- Validation: `python3 -m pytest _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py`.
- Follow-ups: migrate rerun/recap entrypoints to reuse the coordinator for `last_*` updates.

## 2025-12-10
- Slice: centralise suggestion grammar hint generation in the coordinator (Phase 3 continuation).
- Changes:
  - Added `suggestion_grammar_phrase` to `lib/suggestionCoordinator.py`.
  - Updated `lib/modelSuggestionGUI.py` to render “Say:” hints via the coordinator instead of inlining string logic.
  - Extended `_tests/test_suggestion_coordinator.py` to cover the grammar helper.
- Validation: `python3 -m pytest _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py`.
- Follow-ups: continue moving rerun/recap entrypoints onto the coordinator.

## 2025-12-10
- Slice: share rerun base-state reading through the coordinator (Phase 3 continuation).
- Changes:
  - Added `last_recipe_snapshot` to `lib/suggestionCoordinator.py` to expose the canonical last static/axis tokens and directional.
  - Updated `GPT/gpt.py::gpt_rerun_last_recipe` to consume the snapshot instead of reading `GPTState` directly.
  - Extended `_tests/test_suggestion_coordinator.py` to characterise the snapshot helper.
- Validation: `python3 -m pytest _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py _tests/test_gpt_actions.py`.
- Follow-ups: continue centralising recap/rerun updates through the coordinator so all `last_*` handling lives in one place.

## 2025-12-10
- Slice: route rerun `last_*` updates through the coordinator (Phase 3 continuation).
- Changes:
  - Updated `GPT/gpt.py::gpt_rerun_last_recipe` to use `set_last_recipe_from_selection` for `last_*` updates instead of mutating `GPTState` directly.
  - Tests kept green via the existing suites.
- Validation: `python3 -m pytest _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py _tests/test_gpt_actions.py`.
- Follow-ups: centralise recap updates next to finish consolidating `last_*` handling.

## 2025-12-10
- Slice: share recap recipe snapshot via the coordinator (Phase 3 continuation).
- Changes:
  - `last_recipe_snapshot` now includes `recipe` so recap callers can fall back when axes are empty.
  - `gpt_show_last_recipe` reads the snapshot for both axes and base recipe text.
  - Extended `_tests/test_suggestion_coordinator.py` to cover recap snapshot content; regression suite stays green.
- Validation: `python3 -m pytest _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py _tests/test_gpt_actions.py`.
- Follow-ups: finish centralising recap/meta updates and consider a recap helper that uses `last_recap_snapshot`.

## 2025-12-10
- Slice: route meta recap through the coordinator (Phase 3 continuation).
- Changes:
  - `gpt_show_last_meta` now reads `last_recap_snapshot` instead of touching `GPTState` directly.
- Validation: `python3 -m pytest _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py _tests/test_gpt_actions.py`.
- Follow-ups: consider a shared recap helper for response/meta surfaces to complete `last_*` consolidation.

## 2025-12-10
- Slice: add recap clear helper and centralise recap fields (Phase 3 continuation).
- Changes:
  - Added `clear_recap_state` to `lib/suggestionCoordinator.py` to reset last response/recipe/meta axes.
  - Added `gpt_clear_last_recap` action to invoke the reset and notify.
  - Tests remain green.
- Validation: `python3 -m pytest _tests/test_gpt_actions.py`.
- Follow-ups: consider adopting `last_recap_snapshot`/`clear_recap_state` in recap surfaces (response canvas) to finish consolidation.

## 2025-12-10
- Slice: adopt recap snapshots in response canvas (Phase 3 continuation).
- Changes:
  - `lib/modelResponseCanvas.py` now reads recipe/directional via `last_recipe_snapshot`, meta/response via `last_recap_snapshot`, and grammar hints via `suggestion_grammar_phrase`.
  - Keeps recap render in sync with the coordinator SSOT instead of raw `GPTState`.
- Validation: `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_gpt_actions.py _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py`.
- Follow-ups: audit any remaining recap consumers for direct `GPTState` access; otherwise Phase 3 consolidation is effectively done.

## 2025-12-10
- Slice: align Help Hub recap with coordinator snapshots (Phase 3 wrap-up).
- Changes:
  - `lib/helpHub.py` now renders the last recipe/directional from `last_recipe_snapshot` instead of raw `GPTState`.
- Validation: `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_gpt_actions.py` (unchanged suites stay green).
- Follow-ups: quick audit shows remaining recap consumers now flow through coordinator surfaces; Phase 3 consolidation effectively complete.

## 2025-12-10
- Slice: Phase 3 consolidation status check — no further in-repo work identified.
- Changes:
  - Audited recap/rerun/suggestion surfaces; all now consume coordinator helpers (`last_recipe_snapshot`, `last_recap_snapshot`, `set_last_recipe_from_selection`, `clear_recap_state`, `suggestion_grammar_phrase`, `suggestion_entries`/`source`).
  - No code changes required beyond prior slices.
- Validation: relies on previous green runs (`python3 -m pytest _tests/test_model_response_canvas.py _tests/test_gpt_actions.py _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py`).
- Follow-ups: future slices (if needed) would be new features, not consolidation; ADR execution phase effectively complete for in-repo scope.
