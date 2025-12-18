# ADR-0056 Work Log

## 2025-12-17 – Loop 1 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – characterize history_axes_for axis filtering.
- Change: Added a guardrail test asserting history_axes_for retains catalog-backed axis tokens (completeness/scope/method/form/channel/directional) while dropping unknown axes and tokens, aligning with the Axis Snapshot & History Tests-First plan.
- Artefact delta: `_tests/test_request_history_axes_catalog.py`.
- Checks: `python3 -m pytest _tests/test_request_history_axes_catalog.py` (pass).
- Removal test: reverting would remove the characterization test for history_axes_for axis filtering semantics, weakening ADR-0056’s Axis Snapshot & History domain guardrails and making future AxisSnapshot refactors less safe.

## 2025-12-17 – Loop 2 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – introduce an AxisSnapshot helper for history summaries.
- Change: Added an `AxisSnapshot` type alias and `axis_snapshot_from_axes` helper in `lib/requestHistoryActions.py`, and refactored `history_summary_lines` to build its axis view via this helper. Extended `_tests/test_history_query.py` to assert the snapshot helper returns the same normalized axes as `history_axes_for`, laying groundwork for a single snapshot contract shared by history summaries and future log adapters.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_history_query.py`.
- Checks: `python3 -m pytest _tests/test_history_query.py` (pass).
- Removal test: reverting would remove the named AxisSnapshot helper and its guardrail, leaving history summaries tied directly to `history_axes_for` and making it harder to introduce a shared AxisSnapshot type for both history and log payloads without touching multiple call sites.

## 2025-12-17 – Loop 3 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – add a log-side AxisSnapshot helper.
- Change: Introduced an `AxisSnapshot` type alias and `axis_snapshot_from_axes` helper in `lib/requestLog.py` that delegates to `_filter_axes_payload`, and added a guardrail in `_tests/test_request_log_axis_filter.py` asserting the snapshot helper returns the same normalized axes (including passthrough custom keys) as `_filter_axes_payload`. This mirrors the history helper and prepares requestLog to adopt a shared snapshot contract without changing behaviour.
- Artefact deltas: `lib/requestLog.py`, `_tests/test_request_log_axis_filter.py`.
- Checks: `python3 -m pytest _tests/test_request_log_axis_filter.py` (pass).
- Removal test: reverting would remove the log-side AxisSnapshot helper and its guardrail, keeping callers tied directly to `_filter_axes_payload` and making it harder to converge history and log payloads on a single AxisSnapshot façade as ADR-0056 recommends.

## 2025-12-17 – Loop 4 (kind: behaviour)
- Focus: Axis Snapshot & History – wire HistoryQuery’s drawer to the AxisSnapshot helper.
- Change: Updated `lib/historyQuery.py` so `history_drawer_entries_from` now builds its axis view via `axis_snapshot_from_axes` (imported from `requestHistoryActions`) instead of calling `history_axes_for` directly. This makes the history drawer consume the same AxisSnapshot façade as `history_summary_lines`, aligning the HistoryQuery surface with ADR-0056’s snapshot contract while preserving existing behaviour.
- Artefact delta: `lib/historyQuery.py`.
- Checks: `python3 -m pytest _tests/test_history_query.py` (pass).
- Removal test: reverting would reintroduce a separate direct call to `history_axes_for` in `history_drawer_entries_from`, weakening the emerging pattern where both history summaries and drawers consume the shared AxisSnapshot helper and slightly increasing the risk of future axis drift between these surfaces.

## 2025-12-17 – Loop 5 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – characterise stored log axes against AxisSnapshot.
- Change: Imported `axis_snapshot_from_axes` into `_tests/test_request_log.py` and added a test asserting that axes stored by `append_entry` for a representative axes payload (including hydrated values and a custom key) exactly match the output of `axis_snapshot_from_axes` for the same input. This pins the current log storage behaviour to the shared AxisSnapshot contract without changing runtime code.
- Artefact delta: `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass).
- Removal test: reverting would drop the explicit assertion that stored requestLog axes are equal to the AxisSnapshot view, weakening ADR-0056’s tests-first guardrail for aligning log storage semantics with the AxisSnapshot façade.

## 2025-12-17 – Loop 6 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align presets with persona/intent maps.
- Change: Extended `_tests/test_voice_audience_tone_purpose_lists.py` so that, in addition to checking intent buckets and spoken tokens, it now asserts every `PersonaPreset` voice/audience/tone value (when present) is a known key in `PERSONA_KEY_TO_VALUE` and every `IntentPreset.intent` is a canonical `intent` axis token. This establishes a tests-first guardrail that persona and intent presets remain consistent with the persona/intent axis maps described in ADR-0056’s Persona & Intent Preset domain.
- Artefact delta: `_tests/test_voice_audience_tone_purpose_lists.py`.
- Checks: `python3 -m pytest _tests/test_voice_audience_tone_purpose_lists.py` (pass).
- Removal test: reverting would drop the explicit assertion that persona and intent presets use only catalogued persona/intent tokens, weakening ADR-0056’s guardrails for keeping presets, persona axes, and Concordance-facing surfaces aligned.

## 2025-12-17 – Loop 7 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – introduce a keyed persona/intent catalog.
- Change: Added `persona_catalog()` and `intent_catalog()` helpers to `lib/personaConfig.py` that return dictionaries keyed by preset `key` with `PersonaPreset`/`IntentPreset` values, and extended `_tests/test_voice_audience_tone_purpose_lists.py` to assert that both catalogs round-trip all presets by key (each catalog’s keys exactly match the corresponding `PERSONA_PRESETS`/`INTENT_PRESETS` keys and each mapped preset’s `key` equals the dictionary key). This establishes a typed catalog surface for future GPT actions/help hub/suggestion GUIs to consume without yet changing runtime behaviour.
- Artefact deltas: `lib/personaConfig.py`, `_tests/test_voice_audience_tone_purpose_lists.py`.
- Checks: `python3 -m pytest _tests/test_voice_audience_tone_purpose_lists.py` (pass).
- Removal test: reverting would remove the persona/intent catalog helpers and their round-trip tests, weakening ADR-0056’s Persona & Intent Preset domain by dropping the emerging catalog façade that future callers can rely on as the single, test-backed source of persona/intent presets.

## 2025-12-17 – Loop 8 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – wire Help Hub cheat sheet to the persona catalog.
- Change: Updated `lib/helpHub.py` so its `_persona_presets()` helper now prefers `personaConfig.persona_catalog()` (falling back to `PERSONA_PRESETS`), and refactored `_cheat_sheet_text`’s internal persona helper to build its spoken preset names directly from the persona catalog or preset tuple. Added `test_cheat_sheet_persona_line_uses_persona_catalog` in `_tests/test_help_hub.py` to assert that the cheat sheet’s "Persona presets" line contains all spoken tokens from the persona catalog, ensuring Help Hub reflects the current PersonaPreset set. This aligns the Help Hub persona guidance with the Persona & Intent catalog without changing other Help Hub behaviour.
- Artefact deltas: `lib/helpHub.py`, `_tests/test_help_hub.py`.
- Checks: `python3 -m pytest _tests/test_help_hub.py` (pass).
- Removal test: reverting would drop the persona-catalog-backed `_persona_presets` wiring and the cheat sheet guardrail, allowing Help Hub’s persona line to drift away from the canonical PersonaPreset catalog and weakening ADR-0056’s Persona & Intent Preset domain guarantees for Concordance-facing help surfaces.

## 2025-12-17 – Loop 9 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align stance validation with the persona/intent catalogs.
- Change: Updated `lib/stanceValidation.py` so `_persona_presets()` and `_intent_presets()` now prefer `personaConfig.persona_catalog()` and `personaConfig.intent_catalog()` (falling back to `PERSONA_PRESETS`/`INTENT_PRESETS`), ensuring stance validation sees the same PersonaPreset/IntentPreset sets as other Concordance surfaces. Extended `_tests/test_suggestion_stance_validation.py` with `test_persona_catalog_spoken_tokens_are_valid_persona_commands`, which asserts that for every PersonaPreset in `persona_catalog()` with a non-empty `spoken` token, the corresponding `"persona <spoken>"` command is accepted by `valid_stance_command`. This ties the stance command validator directly to the persona catalog without changing its external command shapes.
- Artefact deltas: `lib/stanceValidation.py`, `_tests/test_suggestion_stance_validation.py`.
- Checks: `python3 -m pytest _tests/test_suggestion_stance_validation.py` (pass).
- Removal test: reverting would disconnect stanceValidation from the persona/intent catalogs and drop the guardrail that every catalog persona spoken token is a valid `persona …` command, weakening ADR-0056’s Persona & Intent Preset domain guarantees for suggestion stance validation.

## 2025-12-17 – Loop 10 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – wire Model Help Canvas persona commands to the persona catalog.
- Change: Updated `lib/modelHelpCanvas.py` so `_persona_presets()` now prefers `personaConfig.persona_catalog()` (falling back to `PERSONA_PRESETS`), ensuring the quick-help persona command block derives its presets from the same PersonaPreset catalog used by other Concordance surfaces. Extended `_tests/test_model_help_canvas_persona_commands.py` with `test_persona_commands_cover_catalog_spoken_tokens`, which renders `_default_draw_quick_help` into a stub canvas and asserts that the combined persona command lines contain every non-empty `spoken` token from `persona_catalog()`. This keeps the quick-help persona UI aligned with the canonical PersonaPreset set.
- Artefact deltas: `lib/modelHelpCanvas.py`, `_tests/test_model_help_canvas_persona_commands.py`.
- Checks: `python3 -m pytest _tests/test_model_help_canvas_persona_commands.py` (pass).
- Removal test: reverting would detach Model Help Canvas from the persona catalog and drop the guardrail that its persona command block covers all catalog spoken presets, weakening ADR-0056’s Persona & Intent Preset domain guarantees for quick-help guidance.

## 2025-12-17 – Loop 11 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align GPT persona presets helper with the persona catalog.
- Change: Updated `GPT/gpt.py` so `_persona_presets()` now prefers `personaConfig.persona_catalog()` (falling back to `PERSONA_PRESETS`), ensuring GPT’s internal persona preset helper sees the same PersonaPreset set as other Concordance surfaces. Extended `_tests/test_gpt_actions.py` with `test_gpt_persona_presets_align_with_persona_catalog`, which asserts that the set of `preset.key` values returned by `_persona_presets()` exactly matches the keys from `persona_catalog()`. This ties GPT’s persona presets logic directly to the persona catalog without altering public GPT actions.
- Artefact deltas: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass).
- Removal test: reverting would disconnect GPT’s `_persona_presets` helper from the persona catalog and drop the guardrail that their key sets must match, increasing the risk that GPT persona actions drift from the canonical PersonaPreset catalog.

## 2025-12-17 – Loop 12 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – wire Model Pattern GUI persona presets to the persona catalog.
- Change: Updated `lib/modelPatternGUI.py` so `_persona_presets()` now prefers `personaConfig.persona_catalog()` (falling back to `PERSONA_PRESETS`), ensuring the model pattern picker uses the same PersonaPreset set as other Concordance-facing UIs. Added `test_persona_presets_align_with_persona_catalog` to `_tests/test_model_pattern_gui.py`, which imports `persona_catalog` and `modelPatternGUI._persona_presets()` and asserts that their `preset.key` sets are identical. This keeps pattern-based persona usage aligned with the canonical persona catalog without changing pattern recipes or UI flows.
- Artefact deltas: `lib/modelPatternGUI.py`, `_tests/test_model_pattern_gui.py`.
- Checks: `python3 -m pytest _tests/test_model_pattern_gui.py` (pass).
- Removal test: reverting would detach Model Pattern GUI from the persona catalog and drop the guardrail that its persona presets helper covers the same PersonaPreset keys as the catalog, weakening ADR-0056’s Persona & Intent Preset domain guarantees for pattern-driven persona usage.

## 2025-12-17 – Loop 13 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – wire Model Suggestion GUI persona presets to the persona catalog.
- Change: Updated `lib/modelSuggestionGUI.py` so `_persona_presets()` now prefers `personaConfig.persona_catalog()` (falling back to `PERSONA_PRESETS`), ensuring the suggestion window uses the same PersonaPreset set as other Concordance-facing UIs. Added `test_persona_presets_align_with_persona_catalog` to `_tests/test_model_suggestion_gui.py`, which imports `persona_catalog` and `modelSuggestionGUI._persona_presets()` and asserts that their `preset.key` sets are identical. This keeps model suggestion persona usage aligned with the canonical persona catalog without changing suggestion behaviours or UI flows.
- Artefact deltas: `lib/modelSuggestionGUI.py`, `_tests/test_model_suggestion_gui.py`.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass).
- Removal test: reverting would detach Model Suggestion GUI from the persona catalog and drop the guardrail that its persona presets helper covers the same PersonaPreset keys as the catalog, weakening ADR-0056’s Persona & Intent Preset domain guarantees for suggestion persona usage.

## 2025-12-17 – Loop 14 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – characterise suggestion GUI request-in-flight gating.
- Change: Extended `_tests/test_model_suggestion_gui.py` with `test_request_is_in_flight_handles_request_phases`, which patches `modelSuggestionGUI.current_state` to return a streaming `RequestPhase` and each terminal phase (`IDLE`, `DONE`, `ERROR`, `CANCELLED`) and asserts `_request_is_in_flight()` returns `True` only for streaming. Added `test_reject_if_request_in_flight_notifies_and_blocks`, which patches `_request_is_in_flight` to return `True` and asserts `_reject_if_request_in_flight()` returns `True` and calls `notify` exactly once. This pins the current per-surface gating semantics for the suggestion window ahead of introducing a centralised RequestLifecycle-based gating API.
- Artefact delta: `_tests/test_model_suggestion_gui.py`.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass).
- Removal test: reverting would drop the explicit coverage that modelSuggestionGUI’s request-in-flight helper treats streaming as in-flight and terminal phases as idle, and that its reject helper both blocks and notifies once, weakening ADR-0056’s tests-first guardrails for the Request Gating & Streaming Lifecycle domain.

## 2025-12-17 – Loop 15 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – introduce a central RequestState `is_in_flight` helper and lifecycle guardrails.
- Change: Added an `is_in_flight(state: RequestState) -> bool` helper to `lib/requestState.py` that treats non-terminal phases (listening/transcribing/confirming/sending/streaming) as in-flight and `IDLE`/`DONE`/`ERROR`/`CANCELLED` as not in-flight, and exported it via `__all__`. Created `_tests/test_request_state_gating.py` with tests that (a) assert `is_in_flight` returns `True` for active phases and `False` for terminal ones, (b) characterise `lifecycle_status_for`’s mapping from every `RequestPhase` to the expected `RequestLifecycleState.status`, and (c) exercise `reduce_request_state`/`is_terminal` to confirm retry vs terminal semantics (errored/cancelled are terminal and only `retry` leaves them). This establishes a single, test-backed gating and lifecycle contract at the RequestState/RequestLifecycle layer ahead of wiring GUIs and GPT actions to it.
- Artefact deltas: `lib/requestState.py`, `_tests/test_request_state_gating.py`.
- Checks: `python3 -m pytest _tests/test_request_state_gating.py` (pass).
- Removal test: reverting would remove the central `is_in_flight` helper and its RequestState/RequestLifecycle characterisation tests, weakening ADR-0056’s Request Gating & Streaming Lifecycle domain by leaving gating semantics implicit in per-surface helpers and untested at the orchestrator level.

## 2025-12-17 – Loop 16 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – wire history gating to the central `is_in_flight` helper.
- Change: Updated `lib/requestHistoryActions.py` so `_request_is_in_flight()` now delegates to `requestState.is_in_flight(current_state())` instead of reimplementing phase checks locally, keeping the same semantics (non-terminal phases are in-flight; idle/done/error/cancelled are not). Existing tests in `_tests/test_request_history_actions.py` that patch `current_state` with streaming vs terminal `RequestPhase` values and assert `_request_is_in_flight()` truthiness continue to pass, confirming behaviour is preserved while history gating is now aligned with the central RequestState contract.
- Artefact delta: `lib/requestHistoryActions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would reintroduce a bespoke phase check for history gating and break the emerging pattern of routing request-in-flight decisions through the shared `is_in_flight` helper, slightly increasing the risk of future drift between history gating and the core RequestState lifecycle semantics.

## 2025-12-17 – Loop 17 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – align GPT inflight helper with the central `is_in_flight` contract.
- Change: Updated `GPT/gpt.py` so `_request_is_in_flight()` now calls `requestState.is_in_flight(current_state())` instead of performing its own phase checks, keeping existing semantics (streaming/sending/listening/confirming are treated as in-flight; idle/done/error/cancelled as not) while sharing the same core gating logic as history and other callers. Existing inflight guard tests in `_tests/test_gpt_actions.py` (including those that assert `_request_is_in_flight()` is `False` after a terminal transition and that inflight notifications deduplicate correctly) continue to pass, confirming behaviour is preserved with the new centralised helper.
- Artefact delta: `GPT/gpt.py`.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass).
- Removal test: reverting would restore a bespoke phase-based `_request_is_in_flight` implementation in GPT and weaken ADR-0056’s Request Gating & Streaming Lifecycle guarantees by allowing GPT inflight semantics to drift away from the RequestState `is_in_flight` contract used by history and other GUIs.

## 2025-12-17 – Loop 18 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – align Help Hub inflight helper with the central `is_in_flight` contract.
- Change: Updated `lib/helpHub.py` so `_request_is_in_flight()` now delegates to `requestState.is_in_flight(current_state())` instead of re-implementing its own phase checks, preserving the existing semantics (non-terminal phases are treated as in-flight; idle/done/error/cancelled as not) while sharing the same core gating logic as GPT and history. Existing Help Hub tests in `_tests/test_help_hub.py`, `_tests/test_help_hub_guard.py`, and `_tests/test_help_hub_overlay_lifecycle.py` continue to pass, including guard tests that patch `_reject_if_request_in_flight` and lifecycle tests that stub `_request_is_in_flight`, confirming behaviour is unchanged with the new centralised helper.
- Artefact delta: `lib/helpHub.py`.
- Checks: `python3 -m pytest _tests/test_help_hub.py _tests/test_help_hub_guard.py _tests/test_help_hub_overlay_lifecycle.py` (pass).
- Removal test: reverting would restore a bespoke Help Hub gate that duplicates phase logic instead of calling the shared `is_in_flight` helper, increasing the risk that Help Hub’s notion of “in flight” drifts from the RequestState/RequestLifecycle contract and from other GUIs that are being migrated to the central gating API.

## 2025-12-17 – Loop 19 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – align Model Help Canvas inflight helper with the central `is_in_flight` contract.
- Change: Updated `lib/modelHelpCanvas.py` so `_request_is_in_flight()` now delegates to `requestState.is_in_flight(current_state())` instead of duplicating phase checks, preserving existing semantics (non-terminal phases are in-flight; idle/done/error/cancelled are not) while sharing the same core gating logic as GPT, history, and Help Hub. Existing help canvas and help GUI tests in `_tests/test_model_help_canvas.py` and `_tests/test_model_help_gui.py` continue to pass, confirming that quick-help canvas behaviour and guards are unchanged under the centralised helper.
- Artefact delta: `lib/modelHelpCanvas.py`.
- Checks: `python3 -m pytest _tests/test_model_help_canvas.py _tests/test_model_help_gui.py` (pass).
- Removal test: reverting would reintroduce a bespoke Model Help Canvas inflight check and weaken ADR-0056’s Request Gating & Streaming Lifecycle guarantees by allowing quick-help gating semantics to drift from the RequestState `is_in_flight` contract now shared by GPT, history, and Help Hub.

## 2025-12-17 – Loop 20 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – align Model Suggestion GUI inflight helper with the central `is_in_flight` contract.
- Change: Updated `lib/modelSuggestionGUI.py` so `_request_is_in_flight()` now delegates to `requestState.is_in_flight(current_state())` instead of re-implementing its own phase checks, preserving the existing semantics (non-terminal phases are in-flight; idle/done/error/cancelled are not) while sharing the same core gating logic as GPT, history, Help Hub, and Model Help Canvas. Existing Model Suggestion GUI tests in `_tests/test_model_suggestion_gui.py` – including earlier characterisation of request-phase handling and guard behaviour – continue to pass, confirming suggestion gating behaviour is unchanged under the centralised helper.
- Artefact delta: `lib/modelSuggestionGUI.py`.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass).
- Removal test: reverting would reinstate a bespoke inflight check for Model Suggestion GUI and weaken ADR-0056’s Request Gating & Streaming Lifecycle guarantees by allowing suggestion-window gating semantics to diverge from the RequestState `is_in_flight` contract now shared across GPT actions and multiple GUIs.

## 2025-12-17 – Loop 21 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – align Model Confirmation GUI inflight helper with the central `is_in_flight` contract.
- Change: Updated `lib/modelConfirmationGUI.py` so `_request_is_in_flight()` now delegates to `requestState.is_in_flight(current_state())` instead of duplicating its own phase checks, preserving existing semantics (non-terminal phases are in-flight; idle/done/error/cancelled are not) while sharing the same core gating logic as GPT, history, Help Hub, Model Help Canvas, and Model Suggestion GUI. Existing confirmation GUI tests in `_tests/test_model_confirmation_gui.py` and `_tests/test_model_confirmation_gui_guard.py` continue to pass, confirming confirmation gating behaviour and guard wiring remain unchanged under the centralised helper.
- Artefact delta: `lib/modelConfirmationGUI.py`.
- Checks: `python3 -m pytest _tests/test_model_confirmation_gui.py _tests/test_model_confirmation_gui_guard.py` (pass).
- Removal test: reverting would restore a bespoke Model Confirmation GUI inflight check and weaken ADR-0056’s Request Gating & Streaming Lifecycle guarantees by allowing confirmation-window gating semantics to diverge from the RequestState `is_in_flight` contract now shared across GPT actions and multiple GUIs.

## 2025-12-17 – Loop 22 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – align Model Response Canvas inflight helper with the central `is_in_flight` contract.
- Change: Updated `lib/modelResponseCanvas.py` so `_request_is_in_flight()` now delegates to `requestState.is_in_flight(current_state())` instead of re-implementing its own phase checks, preserving existing semantics (non-terminal phases are in-flight; idle/done/error/cancelled are not) while sharing the same core gating logic as GPT, history, Help Hub, Model Help Canvas, Model Suggestion GUI, and Model Confirmation GUI. Existing response canvas tests in `_tests/test_model_response_canvas.py` continue to pass, confirming that response viewer gating, including `allow_inflight` flows and notification behaviour, remains unchanged under the centralised helper.
- Artefact delta: `lib/modelResponseCanvas.py`.
- Checks: `python3 -m pytest _tests/test_model_response_canvas.py` (pass).
- Removal test: reverting would reinstate a bespoke inflight check for the Model Response Canvas and weaken ADR-0056’s Request Gating & Streaming Lifecycle guarantees by allowing response-viewer gating semantics to diverge from the RequestState `is_in_flight` contract now shared across GPT actions and Concordance-facing GUIs.

## 2025-12-17 – Loop 23 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – align Model Pattern GUI inflight helper with the central `is_in_flight` contract.
- Change: Updated `lib/modelPatternGUI.py` so `_request_is_in_flight()` now delegates to `requestState.is_in_flight(current_state())` (via a local import) instead of re-implementing its own phase checks, preserving existing semantics (non-terminal phases are in-flight; idle/done/error/cancelled are not) while sharing the same core gating logic as GPT, history, Help Hub, Model Help Canvas, Model Suggestion GUI, Model Confirmation GUI, and Model Response Canvas. Existing pattern GUI tests in `_tests/test_model_pattern_gui.py` continue to pass, confirming that pattern picker gating behaviour and guard wiring remain unchanged under the centralised helper.
- Artefact delta: `lib/modelPatternGUI.py`.
- Checks: `python3 -m pytest _tests/test_model_pattern_gui.py` (pass).
- Removal test: reverting would restore a bespoke inflight check for Model Pattern GUI and weaken ADR-0056’s Request Gating & Streaming Lifecycle guarantees by allowing pattern-picker gating semantics to diverge from the RequestState `is_in_flight` contract now shared across GPT actions and Concordance-facing GUIs.

## 2025-12-17 – Loop 24 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – align provider commands and history drawer inflight helpers with the central `is_in_flight` contract.
- Change: Updated `lib/providerCommands.py` and `lib/requestHistoryDrawer.py` so their `_request_is_in_flight()` helpers now delegate to `requestState.is_in_flight(current_state())` instead of re-implementing phase checks locally, keeping existing semantics (non-terminal phases are in-flight; idle/done/error/cancelled are not) while sharing the same core gating logic as GPT, history, Help Hub, Model Help Canvas, Model Suggestion GUI, Model Confirmation GUI, Model Response Canvas, and Model Pattern GUI. Added `test_request_is_in_flight_delegates_to_request_state_helper` to `_tests/test_provider_commands.py` and a new `_tests/test_request_history_drawer_gating.py` to assert that both modules call their imported `is_in_flight` helper for streaming vs terminal `RequestPhase` values, pinning the delegation contract.
- Artefact deltas: `lib/providerCommands.py`, `lib/requestHistoryDrawer.py`, `_tests/test_provider_commands.py`, `_tests/test_request_history_drawer_gating.py`.
- Checks: `python3 -m pytest _tests/test_provider_commands.py _tests/test_request_history_drawer_gating.py _tests/test_request_history_drawer.py _tests/test_request_history_overlay_lifecycle.py _tests/test_request_history_actions.py` (pass; 110 tests).
- Removal test: reverting would restore bespoke phase-based inflight checks for provider commands and the history drawer and break the new delegation tests, weakening ADR-0056’s Request Gating & Streaming Lifecycle guarantees by allowing these surfaces’ gating semantics to drift from the central RequestState `is_in_flight` contract now shared across GPT actions and Concordance-facing GUIs.

## 2025-12-17 – Loop 25 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align GPT persona/intent canonicalisation with the persona/intent catalogs.
- Change: Added `test_canonical_persona_values_align_with_persona_and_intent_catalogs` to `_tests/test_gpt_actions.py`, which imports `persona_catalog()` and `intent_catalog()` from `lib/personaConfig` and asserts that `_canonical_persona_value("voice", preset.voice)`, `_canonical_persona_value("audience", preset.audience)`, `_canonical_persona_value("tone", preset.tone)`, and `_canonical_persona_value("intent", preset.intent)` all return the original preset values for every non-empty field across all PersonaPreset and IntentPreset entries. This establishes a direct guardrail that GPT’s internal persona/intent canonicaliser accepts all catalogued persona/intent tokens as canonical, tying it explicitly to the Persona & Intent catalogs described in ADR-0056.
- Artefact delta: `_tests/test_gpt_actions.py`.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass; 104 tests).
- Removal test: reverting would drop the explicit assertion that `_canonical_persona_value` remains aligned with `persona_catalog` and `intent_catalog`, weakening ADR-0056’s Persona & Intent Preset domain guardrails by allowing future canonicalisation changes to drift away from the catalog-backed persona/intent tokens without detection.

## 2025-12-17 – Loop 26 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – introduce a central `try_start_request` helper with structured drop reasons.
- Change: Added `RequestDropReason` and `try_start_request(state)` to `lib/requestState.py` so callers can centralise “in flight” gating decisions and reason codes instead of duplicating phase checks. Updated `lib/providerCommands.py` and `lib/requestHistoryDrawer.py` so `_reject_if_request_in_flight()` now delegates to `try_start_request(current_state())` and only notifies when the drop reason is `in_flight`. Extended `_tests/test_request_state_gating.py` with coverage for `try_start_request` and extended `_tests/test_provider_commands.py` and `_tests/test_request_history_drawer_gating.py` to assert the reject helpers respect the `try_start_request` decision.
- Artefact deltas: `lib/requestState.py`, `lib/providerCommands.py`, `lib/requestHistoryDrawer.py`, `_tests/test_request_state_gating.py`, `_tests/test_provider_commands.py`, `_tests/test_request_history_drawer_gating.py`.
- Checks: `python3 -m pytest _tests/test_request_state_gating.py _tests/test_provider_commands.py _tests/test_request_history_drawer_gating.py` (pass; 12 tests).
- Removal test: reverting would remove the shared `try_start_request` API and restore local per-surface gating decisions in provider/history drawer reject helpers, weakening ADR-0056’s goal of centralising request gating policy and making it easier for drop reason semantics to drift across surfaces.

## 2025-12-17 – Loop 27 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align intent preset helpers with the intent catalog.
- Change: Updated `_intent_presets()` in `GPT/gpt.py`, `lib/modelHelpCanvas.py`, and `lib/modelPatternGUI.py` to prefer `personaConfig.intent_catalog()` (falling back to `INTENT_PRESETS`), mirroring prior persona catalog wiring so intent presets have a single canonical source across Concordance-facing surfaces. Added guardrail tests asserting each helper returns the same `IntentPreset.key` set as `intent_catalog()`: `test_gpt_intent_presets_align_with_intent_catalog` in `_tests/test_gpt_actions.py`, `test_intent_presets_align_with_intent_catalog` in `_tests/test_model_pattern_gui.py`, and `test_intent_presets_align_with_intent_catalog` in `_tests/test_model_help_canvas_persona_commands.py`.
- Artefact deltas: `GPT/gpt.py`, `lib/modelHelpCanvas.py`, `lib/modelPatternGUI.py`, `_tests/test_gpt_actions.py`, `_tests/test_model_pattern_gui.py`, `_tests/test_model_help_canvas_persona_commands.py`.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py _tests/test_model_pattern_gui.py _tests/test_model_help_canvas_persona_commands.py` (pass; 140 tests).
- Removal test: reverting would disconnect multiple intent preset helpers from the canonical `intent_catalog` surface and remove the alignment guardrails, increasing the risk that intent preset sets drift between GPT actions and UI surfaces without tests catching the inconsistency.

## 2025-12-17 – Loop 28 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – record in-flight gate outcomes as a drop reason.
- Change: Added `set_drop_reason()` to `lib/requestLog.py` and wired `GPT/gpt.py`, `lib/providerCommands.py`, and `lib/requestHistoryDrawer.py` so their in-flight `_reject_if_request_in_flight()` paths call `set_drop_reason(message)` before notifying. This makes “blocked because a request is running” visible to Concordance-facing surfaces that already read `last_drop_reason()` (for example the history drawer’s status line and history navigation notifications). Updated tests to assert `set_drop_reason` is called for in-flight rejects and not called when a request is allowed: `_tests/test_provider_commands.py`, `_tests/test_request_history_drawer_gating.py`, and `_tests/test_gpt_actions.py`.
- Artefact deltas: `lib/requestLog.py`, `GPT/gpt.py`, `lib/providerCommands.py`, `lib/requestHistoryDrawer.py`, `_tests/test_provider_commands.py`, `_tests/test_request_history_drawer_gating.py`, `_tests/test_gpt_actions.py`.
- Checks: `python3 -m pytest _tests/test_provider_commands.py _tests/test_request_history_drawer_gating.py _tests/test_gpt_actions.py` (pass; 111 tests).
- Removal test: reverting would remove the shared drop-reason recorder and return in-flight gating to being “notify-only”, reducing visibility of blocked outcomes for history/Concordance surfaces and increasing the risk of inconsistent drop reason handling across callers.

## 2025-12-17 – Loop 29 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – centralise requestHistoryActions gating on `try_start_request` and record drop reasons.
- Change: Updated `lib/requestHistoryActions.py` so `_reject_if_request_in_flight()` now calls `try_start_request(current_state())` and, when the drop reason is `in_flight`, records the message via `requestLog.set_drop_reason()` before notifying. This brings request-history command gating in line with the newer shared gating + drop-reason pattern used by other Concordance-facing surfaces.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_actions_catalog.py` (pass; 93 tests).
- Removal test: reverting would restore bespoke `_request_is_in_flight` gating inside requestHistoryActions and remove explicit drop-reason recording for blocked history actions, increasing the risk of divergent gating semantics and reduced visibility in downstream history UI flows.
- Adversarial “what remains” check:
  - `lib/requestState.py`: expand `RequestDropReason` beyond `in_flight` to cover other structured drop outcomes already present in `requestLog.append_entry` (e.g., missing directional) and update callers/tests to use reason codes instead of message parsing.
  - `lib/helpHub.py` and `lib/modelHelpCanvas.py`: migrate `_reject_if_request_in_flight()` to use `try_start_request` + `set_drop_reason` so help surfaces share the same gating + drop reason contract.
  - `lib/requestLog.py` + `lib/requestHistoryActions.py`: converge axis snapshot/filtering on a single shared `AxisSnapshot` builder (currently duplicated: `requestLog.axis_snapshot_from_axes` vs `requestHistoryActions.axis_snapshot_from_axes`) and add a guardrail asserting both produce identical snapshots for representative inputs.

## 2025-12-17 – Loop 30 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – align Help Hub and Help Canvas in-flight rejects with `try_start_request` + `set_drop_reason`.
- Change: Updated `lib/helpHub.py` and `lib/modelHelpCanvas.py` so `_reject_if_request_in_flight()` now calls `try_start_request(current_state())` and, on `in_flight`, records the drop reason via `requestLog.set_drop_reason(message)` before notifying. Added guardrail tests ensuring these rejectors call `set_drop_reason` only when blocked: `_tests/test_help_hub_guard.py` and `_tests/test_model_help_canvas_guard.py`.
- Artefact deltas: `lib/helpHub.py`, `lib/modelHelpCanvas.py`, `_tests/test_help_hub_guard.py`, `_tests/test_model_help_canvas_guard.py`.
- Checks: `python3 -m pytest _tests/test_help_hub_guard.py _tests/test_model_help_canvas_guard.py _tests/test_help_hub.py _tests/test_model_help_canvas_guard.py` (pass; 26 tests).
- Removal test: reverting would return Help Hub and Help Canvas gating to “notify-only” without persisted drop reasons, reducing visibility for Concordance/history surfaces and allowing these entry points to drift from the shared gating contract.
- Adversarial “what remains” check:
  - `lib/requestState.py`: expand `RequestDropReason` beyond `in_flight` and migrate callers/tests to reason codes as the SSOT.
  - `lib/modelSuggestionGUI.py`, `lib/modelConfirmationGUI.py`, `lib/modelResponseCanvas.py`, `lib/modelPromptPatternGUI.py`, `lib/modelPatternGUI.py`: migrate `_reject_if_request_in_flight()` to `try_start_request` + `set_drop_reason` to complete the per-surface gating convergence.
  - `lib/requestLog.py` + `lib/requestHistoryActions.py`: converge axis snapshot building (`axis_snapshot_from_axes`) and add a guardrail asserting both implementations return identical snapshots.

## 2025-12-17 – Loop 31 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – converge history axis snapshot builder with request log snapshot contract.
- Change: Updated `lib/requestHistoryActions.py` so `axis_snapshot_from_axes()` now delegates to `requestLog.axis_snapshot_from_axes()` instead of a separate `history_axes_for` normaliser. Added `_tests/test_axis_snapshot_alignment.py` to assert both snapshot builders return identical snapshots for representative axes payloads (including filtered tokens and passthrough keys).
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_axis_snapshot_alignment.py`.
- Checks: `python3 -m pytest _tests/test_axis_snapshot_alignment.py _tests/test_request_log_axis_filter.py _tests/test_request_history_actions_catalog.py _tests/test_history_query.py` (pass; 19 tests).
- Removal test: reverting would reintroduce divergent axis snapshot normalisation between history actions and request logs and remove the explicit alignment guardrail.
- Adversarial “what remains” check:
  - `lib/requestLog.py`: migrate callers from free-form drop-reason strings to `RequestDropReason` codes (store the code and render message at the boundary).
  - `lib/requestState.py`: expand `RequestDropReason` beyond `in_flight` and add tests for each new code.
  - `lib/modelSuggestionGUI.py` + `lib/modelConfirmationGUI.py` + `lib/modelResponseCanvas.py` + `lib/modelPromptPatternGUI.py` + `lib/modelPatternGUI.py`: migrate `_reject_if_request_in_flight()` to `try_start_request` + `set_drop_reason` to complete per-surface gating convergence.

## 2025-12-17 – Loop 32 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – converge remaining UI rejectors on `try_start_request` + persisted drop reasons.
- Change: Updated `lib/modelSuggestionGUI.py`, `lib/modelConfirmationGUI.py`, `lib/modelResponseCanvas.py`, and `lib/modelPromptPatternGUI.py` so `_reject_if_request_in_flight()` now delegates to `try_start_request(current_state())` and, when the drop reason is `in_flight`, records the message via `requestLog.set_drop_reason()` before notifying. Updated `lib/modelPromptPatternGUI.py`’s `_request_is_in_flight()` to delegate to `requestState.is_in_flight` so this surface no longer maintains a bespoke phase check.
- Artefact deltas: `lib/modelSuggestionGUI.py`, `lib/modelConfirmationGUI.py`, `lib/modelResponseCanvas.py`, `lib/modelPromptPatternGUI.py`, `_tests/test_model_suggestion_gui.py`, `_tests/test_model_confirmation_gui_guard.py`, `_tests/test_model_response_canvas_guard.py`, `_tests/test_prompt_pattern_gui_guard.py`.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py _tests/test_model_confirmation_gui_guard.py _tests/test_model_response_canvas_guard.py _tests/test_prompt_pattern_gui_guard.py` (pass; 25 tests).
- Removal test: reverting would restore notify-only gating for these UI surfaces and drop their persisted drop reasons, weakening the shared gating contract and making Concordance/history surfaces less able to explain why actions were blocked.
- Adversarial “what remains” check:
  - `lib/modelPatternGUI.py`: migrate `_reject_if_request_in_flight()` to `try_start_request` + `set_drop_reason` and add a guardrail test mirroring the other UI surfaces.
  - `lib/requestState.py` + `lib/requestLog.py`: expand `RequestDropReason` beyond `in_flight` and store the code in `requestLog` so callers can render messages at the edge without string parsing.

## 2025-12-17 – Loop 33 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – finish per-surface gating convergence for the model pattern picker.
- Change: Updated `lib/modelPatternGUI.py` so `_reject_if_request_in_flight()` now delegates to `try_start_request(current_state())` and, when blocked with `in_flight`, records the message via `requestLog.set_drop_reason()` before notifying. This completes the per-surface migration for pattern-related GUIs to the shared gating + persisted drop reason contract.
- Artefact deltas: `lib/modelPatternGUI.py`, `_tests/test_model_pattern_gui_guard.py`.
- Checks: `python3 -m pytest _tests/test_model_pattern_gui_guard.py _tests/test_model_pattern_gui.py` (pass; 33 tests).
- Removal test: reverting would restore notify-only gating for the model pattern picker and remove the guardrail asserting that blocked outcomes persist a drop reason, weakening the shared request gating contract across Concordance-facing surfaces.
- Adversarial “what remains” check:
  - `lib/requestState.py` + `lib/requestLog.py`: expand `RequestDropReason` beyond `in_flight` and store the code in `requestLog` so callers can render messages at the edge without string parsing.

## 2025-12-17 – Loop 34 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – store structured drop reasons (codes + messages) in `requestLog`.
- Change: Expanded `RequestDropReason` in `lib/requestState.py` to include `missing_request_id` and `missing_directional`. Refactored `lib/requestLog.py` to store a structured `(code, message)` drop reason (via a `DropReason` dataclass) and added `drop_reason_message()` / `last_drop_reason_code()` helpers. Updated all in-flight gating call sites to record `set_drop_reason("in_flight")` and render the user message via `drop_reason_message("in_flight")`, avoiding free-form string reasons being treated as codes. Updated `_tests/test_request_log.py` to assert the drop reason code is set/cleared alongside the existing message-based contract.
- Artefact deltas: `lib/requestState.py`, `lib/requestLog.py`, `GPT/gpt.py`, `lib/helpHub.py`, `lib/modelHelpCanvas.py`, `lib/modelSuggestionGUI.py`, `lib/modelConfirmationGUI.py`, `lib/modelResponseCanvas.py`, `lib/modelPromptPatternGUI.py`, `lib/modelPatternGUI.py`, `lib/requestHistoryActions.py`, `lib/requestHistoryDrawer.py`, `lib/providerCommands.py`, `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_gpt_actions.py _tests/test_provider_commands.py _tests/test_request_history_drawer_gating.py _tests/test_help_hub_guard.py` (pass; 216 tests).
- Removal test: reverting would revert drop reasons to free-form strings, making it impossible for Concordance-facing surfaces to reason about blocked/dropped outcomes without string parsing, and would weaken the new guardrails that pin drop reason codes.
- Adversarial “what remains” check:
  - `lib/requestState.py` + `lib/requestLog.py`: decide whether additional drop reasons (beyond `missing_request_id`/`missing_directional`/`in_flight`) should be first-class codes, and add a small test per new code.

## 2025-12-17 – Loop 35 (kind: guardrail/tests)
- Focus: Request Gating & Streaming Lifecycle – assert in-flight rejectors record the `in_flight` drop reason code.
- Change: Tightened in-flight guard tests across provider/history/help/pattern/suggestion/canvas surfaces so they assert `set_drop_reason("in_flight")` (not just "called"), ensuring callers write a structured code and don’t regress to passing free-form strings.
- Artefact deltas: `_tests/test_provider_commands.py`, `_tests/test_request_history_drawer_gating.py`, `_tests/test_help_hub_guard.py`, `_tests/test_model_help_canvas_guard.py`, `_tests/test_model_suggestion_gui.py`, `_tests/test_model_confirmation_gui_guard.py`, `_tests/test_model_response_canvas_guard.py`, `_tests/test_prompt_pattern_gui_guard.py`, `_tests/test_model_pattern_gui_guard.py`, `_tests/test_request_history_actions.py`, `_tests/test_gpt_actions.py`.
- Checks: `python3 -m pytest _tests/test_provider_commands.py _tests/test_request_history_drawer_gating.py _tests/test_help_hub_guard.py _tests/test_model_help_canvas_guard.py _tests/test_model_suggestion_gui.py _tests/test_model_confirmation_gui_guard.py _tests/test_model_response_canvas_guard.py _tests/test_prompt_pattern_gui_guard.py _tests/test_model_pattern_gui_guard.py _tests/test_request_history_actions.py _tests/test_gpt_actions.py` (pass; 234 tests).
- Removal test: reverting would weaken the guardrails for the structured drop reason contract and allow call sites to silently regress to storing free-form drop reasons.
- Adversarial “what remains” check:
  - `lib/requestLog.py`: consider whether any other drop paths (beyond missing request id/directional/in-flight) should emit structured codes (and add one test per new code if introduced).

## 2025-12-17 – Loop 36 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – consume drop reasons when the history drawer displays them.
- Change: Added `consume_last_drop_reason_record()` to `lib/requestLog.py` so callers can consume the structured `(code, message)` record. Updated `lib/requestHistoryDrawer.py` to consume (clear) the drop reason when showing the “no entries” message, preventing stale drop reasons from persisting across repeated drawer opens. Extended `_tests/test_request_history_drawer.py` to assert the drop reason code is cleared after the drawer refreshes.
- Artefact deltas: `lib/requestLog.py`, `lib/requestHistoryDrawer.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py _tests/test_request_log.py` (pass; 24 tests).
- Removal test: reverting would restore sticky drop reasons in the history drawer, making it harder to tell whether a "no history" warning is fresh or a stale drop message.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: consider consuming drop reasons when `use_drop_reason=True` notifications are displayed (to avoid repeating old drop messages), with a small test asserting consumption semantics.
  - `lib/requestLog.py`: decide whether any other drop paths should become first-class `RequestDropReason` codes and add one focused test per new code.

## 2025-12-17 – Loop 37 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – consume drop reasons when request history commands surface them.
- Change: Updated `lib/requestHistoryActions.py` so `_notify_with_drop_reason()` consumes the structured drop reason record (via `consume_last_drop_reason_record()`) when `use_drop_reason=True`. Migrated `gpt_request_history_show_latest()` and `gpt_request_history_list()` to use `_notify_with_drop_reason()` (instead of manual `last_drop_reason()` peeks) so these commands no longer repeatedly emit stale drop reasons across runs. Updated `_tests/test_request_history_actions.py` expectations to reflect the new one-shot consumption semantics, including the fact that history drawer refresh and history list/show_latest can consume the reason.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_request_log.py` (pass; 116 tests).
- Removal test: reverting would restore "peek-only" drop reason handling for history commands, allowing old drop reasons to be re-notified indefinitely and weakening the request lifecycle visibility contract.
- Adversarial “what remains” check:
  - `lib/requestLog.py`: decide whether any other drop paths should become first-class `RequestDropReason` codes and add one focused test per new code.
  - `lib/requestHistoryActions.py`: consider whether any history commands should *not* consume drop reasons (for example, if a repeated notify is desirable for specific UX flows), and encode that as an explicit policy.

## 2025-12-17 – Loop 38 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – add a structured drop reason for history save failures.
- Change: Added `history_save_failed` to `RequestDropReason` in `lib/requestState.py` and extended the history save workflow in `lib/requestHistoryActions.py` so `_save_history_prompt_to_file()` records `set_drop_reason("history_save_failed", message)` for key failure paths (no entry, empty prompt, unable to create save dir, missing directional lens, write failure). Updated `_tests/test_request_history_actions.py` to assert `last_drop_reason_code() == "history_save_failed"` for representative failure branches.
- Artefact deltas: `lib/requestState.py`, `lib/requestHistoryActions.py`, `lib/requestLog.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_log.py` (pass; 103 tests).
- Removal test: reverting would restore untyped history-save failure notifications, forcing downstream surfaces to infer failure causes from free-form strings and weakening the ADR-0056 drop-reason contract.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: consider a dedicated drop code for "missing directional lens" during save (distinct from generic `history_save_failed`) if UX needs to branch on it.
  - `lib/requestLog.py`: decide whether other non-gating failures (e.g., clipboard/path open failures) merit first-class drop reason codes.

## 2025-12-17 – Loop 39 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – add a dedicated drop reason for history-save directional lens omissions.
- Change: Added `history_save_missing_directional` to `RequestDropReason` in `lib/requestState.py`, added a specific `drop_reason_message()` mapping in `lib/requestLog.py`, and updated `lib/requestHistoryActions.py::_save_history_prompt_to_file()` to record `set_drop_reason("history_save_missing_directional", message)` when saving is blocked due to a missing directional lens. Updated `_tests/test_request_history_actions.py` to assert `last_drop_reason_code()` uses this dedicated code for the missing-directional save case.
- Artefact deltas: `lib/requestState.py`, `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_log.py` (pass; 103 tests).
- Removal test: reverting would collapse the save-time missing-directional case back into the generic `history_save_failed` bucket, forcing downstream UX to parse messages to distinguish policy errors from other save failures.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: consider whether other save failures (directory creation vs write failure vs empty prompt) should be split into separate drop reason codes.
  - `lib/requestLog.py`: decide whether other non-gating failures (clipboard/path open failures) merit first-class drop reason codes.

## 2025-12-17 – Loop 40 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – split history save failures into more specific drop reason codes.
- Change: Added `history_save_dir_create_failed` and `history_save_write_failed` to `RequestDropReason` in `lib/requestState.py`, added `drop_reason_message()` mappings in `lib/requestLog.py`, and updated `lib/requestHistoryActions.py::_save_history_prompt_to_file()` to record these codes for directory creation failures and write failures (instead of the generic `history_save_failed`). Extended `_tests/test_request_history_actions.py` with a new `test_history_save_handles_write_failure` and updated the directory-creation failure test to assert the new codes.
- Artefact deltas: `lib/requestState.py`, `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_log.py` (pass; 104 tests).
- Removal test: reverting would collapse distinct save failures back into `history_save_failed`, reducing Concordance-facing visibility and forcing UI layers/tests to infer failures from free-form messages.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: decide whether "no entry" and "empty prompt" should become separate save-related drop codes (currently both use `history_save_failed`).
  - `lib/requestHistoryActions.py`: decide whether save-path clipboard/open failures should set typed drop reasons.

## 2025-12-17 – Loop 41 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – split history-save “no entry” and “empty prompt” into typed drop reason codes.
- Change: Added `history_save_no_entry` and `history_save_empty_prompt` to `RequestDropReason` in `lib/requestState.py`, added `drop_reason_message()` mappings in `lib/requestLog.py`, and updated `lib/requestHistoryActions.py::_save_history_prompt_to_file()` to record these codes for the “no history entry” and “empty prompt” early-return paths. Updated `_tests/test_request_history_actions.py` to assert the new codes for these branches.
- Artefact deltas: `lib/requestState.py`, `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py -k history_save` (pass; `25 passed, 68 deselected`).
- Removal test: reverting would collapse distinct history-save failure causes back into a generic code, reducing Concordance-facing visibility and weakening the typed drop reason contract.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: decide whether additional save failures ("no entry" vs empty prompt vs missing response/meta) deserve distinct codes or should remain grouped.
  - `lib/requestHistoryActions.py`: decide whether save-path clipboard/open failures should emit typed drop reasons (and add one focused test per new code).

## 2025-12-17 – Loop 42 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – add typed drop reasons for clipboard/open failures on history save path commands.
- Change: Added `history_save_copy_failed` and `history_save_open_failed` to `RequestDropReason` in `lib/requestState.py`, added `drop_reason_message()` mappings in `lib/requestLog.py`, and updated `lib/requestHistoryActions.py` so `gpt_request_history_copy_last_save_path()` and `gpt_request_history_open_last_save_path()` record these drop reason codes when copying/opening the saved history path fails.
- Artefact deltas: `lib/requestState.py`, `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py -k "history_copy_last_save_path or history_open_last_save_path"` (pass; `9 passed, 84 deselected`).
- Removal test: reverting would remove typed drop reason coverage for clipboard/open failures, reducing Concordance-facing visibility and forcing downstream surfaces to infer failure causes from free-form strings.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: decide whether `_last_history_save_path()` failures (no path set / path missing) should also emit typed drop reason codes, so callers can distinguish “no save yet” vs “file deleted”.
  - `lib/requestHistoryActions.py`: decide whether `app.open` unavailable should be a distinct code from generic open failures.

## 2025-12-17 – Loop 43 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – add typed drop reasons for last-history-save-path retrieval failures.
- Change: Added `history_save_path_unset` and `history_save_path_not_found` to `RequestDropReason` in `lib/requestState.py`, added `drop_reason_message()` mappings in `lib/requestLog.py`, and updated `lib/requestHistoryActions.py::_last_history_save_path()` so it records these codes via `set_drop_reason(...)` for (a) no saved path yet and (b) saved path missing/not-a-file. Updated `_tests/test_request_history_actions.py` to assert `last_drop_reason_code()` matches for the affected branches.
- Artefact deltas: `lib/requestState.py`, `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py -k "last_save_path_notifies_when_missing or last_save_path_clears_missing_file or copy_last_save_path_handles_missing_file or open_last_save_path_handles_missing_file"` (pass; `4 passed, 89 deselected`).
- Removal test: reverting would return these failures to untyped notifications, forcing Concordance-facing surfaces to infer “no save yet” vs “path missing” from free-form strings.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: decide whether successful history-save-path actions (show/copy/open) should clear stale drop reasons (to avoid an unrelated previous failure code lingering).
  - `lib/requestHistoryActions.py`: decide whether `history_save_open_failed` should be split into `history_save_open_action_unavailable` vs `history_save_open_exception`.

## 2025-12-17 – Loop 44 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – clear stale drop reasons after successful history-save-path actions.
- Change: Updated `lib/requestHistoryActions.py` so `gpt_request_history_last_save_path()`, `gpt_request_history_show_last_save_path()`, `gpt_request_history_copy_last_save_path()`, and `gpt_request_history_open_last_save_path()` call `set_drop_reason("")` after a successful path resolution/action, preventing unrelated prior failure codes from lingering. Updated `_tests/test_request_history_actions.py` to seed a failure drop reason and assert it is cleared on success.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py -k "history_copy_last_save_path or history_open_last_save_path or history_show_last_save_path or history_last_save_path"` (pass; `18 passed, 76 deselected`).
- Removal test: reverting would allow stale `RequestDropReason` codes to persist across successful history path commands, weakening the typed drop reason contract for Concordance-facing surfaces.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: decide whether a successful `gpt_request_history_save_latest_source()` should also clear any prior path-related drop reasons (or whether save failures should remain sticky until consumed).
  - `lib/requestState.py` / `lib/requestLog.py`: decide whether to split `history_save_open_failed` into more specific codes (`history_save_open_action_unavailable` vs `history_save_open_exception`).

## 2025-12-17 – Loop 45 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – split history-save-path open failures into typed drop reasons.
- Change: Replaced the generic `history_save_open_failed` code with `history_save_open_action_unavailable` and `history_save_open_exception` in `lib/requestState.py` and `lib/requestLog.py`. Updated `lib/requestHistoryActions.py::gpt_request_history_open_last_save_path()` so missing-path uses `history_save_path_not_found`, `app.open` unavailability uses `history_save_open_action_unavailable`, and runtime exceptions while opening use `history_save_open_exception`. Extended `_tests/test_request_history_actions.py` with a new test asserting the `open_action_unavailable` code.
- Artefact deltas: `lib/requestState.py`, `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py -k "open_last_save_path"` (pass; `5 passed, 90 deselected`).
- Removal test: reverting would collapse distinct open failure causes back into a single code, reducing Concordance-facing visibility and forcing callers to infer "action missing" vs "exception" from free-form messages.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: decide whether other open-related errors (e.g., OS-level "file not found" vs permission errors) should become distinct drop codes or remain under `history_save_open_exception`.
  - `lib/requestHistoryActions.py`: decide whether `gpt_request_history_save_latest_source()` should clear prior path-related drop reasons on success.

## 2025-12-17 – Loop 46 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – introduce a minimal `StreamingSession` façade and adopt it in the streaming sender.
- Adversarial prioritisation: The highest-risk/high-churn hotspot remaining in ADR-0056 is the streaming request path in `lib/modelHelpers.py::_send_request_streaming`, which still owns chunk accumulation + snapshot recording inline. A minimal, test-backed façade reduces future migration risk for the larger “StreamingSession emits lifecycle/history/log events” objective without requiring a rewrite this loop.
- Change: Added a `StreamingSession` wrapper and `new_streaming_session()` constructor to `lib/streamingCoordinator.py`, delegating to existing `StreamingRun` + `record_streaming_*` helpers. Refactored `lib/modelHelpers.py::_send_request_streaming` to create a `StreamingSession` and use `session.record_snapshot/chunk/error/complete` instead of calling `record_streaming_*` directly. Added `_tests/test_streaming_session.py` to pin the new façade’s snapshot/complete/error semantics.
- Artefact deltas: `lib/streamingCoordinator.py`, `lib/modelHelpers.py`, `_tests/test_streaming_session.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `16 passed`).
- Removal test: reverting would remove the `StreamingSession` façade and restore direct snapshot/chunk/error calls in `_send_request_streaming`, increasing coordination cost and risk for future streaming lifecycle refactors.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py`: migrate the remaining streaming-specific behaviours (axis filtering, lifecycle events, history/log writes) behind `StreamingSession` methods (or events) so `_send_request_streaming` becomes a thin orchestrator.
  - `lib/modelHelpers.py` + `lib/requestLog.py` + `lib/requestHistoryActions.py`: define/emit a small set of structured streaming events (history write, log entry, UI refresh) and add tests for ordering.

## 2025-12-17 – Loop 47 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – move streaming-request axis filtering behind `StreamingSession`.
- Adversarial prioritisation: Axis token filtering inside `lib/modelHelpers.py::_send_request_streaming` is a second hotspot within the streaming path; leaving it inline keeps a hidden contract (“which axes attach to StreamingRun”) that will be brittle when we start emitting history/log events from `StreamingSession`.
- Change: Added `filtered_axes_from_request()` and `StreamingSession.set_axes_from_request()` to `lib/streamingCoordinator.py` and refactored `lib/modelHelpers.py::_send_request_streaming` to call `session.set_axes_from_request(request)` instead of inlining catalog lookups. Extended `_tests/test_streaming_session.py` with a guardrail asserting unknown axis tokens are dropped and only catalog-backed tokens are retained.
- Artefact deltas: `lib/streamingCoordinator.py`, `lib/modelHelpers.py`, `_tests/test_streaming_session.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `17 passed`).
- Removal test: reverting would reintroduce inline axis filtering in `_send_request_streaming` and drop the explicit, test-backed contract for which axes attach to streaming snapshots.
- Adversarial “what remains” check:
  - `lib/streamingCoordinator.py`: consider moving more stream-side state transitions (e.g., cancel detection) behind `StreamingSession` methods so `modelHelpers` becomes orchestration-only.
  - `lib/modelHelpers.py` + `lib/requestLog.py` + `lib/requestHistoryActions.py`: define/emit a minimal set of structured streaming events (history write, log entry, UI refresh) and add ordering tests.

## 2025-12-17 – Loop 48 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – emit a structured streaming event stream from `StreamingSession`.
- Adversarial prioritisation: Before wiring history/log/UI hooks off streaming, we need an explicit ordering contract for what streaming “does” (snapshot/chunk/complete/error). Without it, future changes will be brittle and hard to validate.
- Change: Extended `lib/streamingCoordinator.py::StreamingSession` to record a small ordered event list (persisted to `GPTState.last_streaming_events`) whenever `record_snapshot`, `record_chunk`, `record_error`, or `record_complete` is called. Updated `_tests/test_streaming_session.py` and `_tests/test_request_streaming.py` to assert event ordering for basic session usage and the JSON fallback path in `_send_request_streaming`.
- Artefact deltas: `lib/streamingCoordinator.py`, `_tests/test_streaming_session.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `17 passed`).
- Removal test: reverting would remove the explicit, test-backed streaming event ordering, making subsequent streaming lifecycle refactors (history/log/UI event emission) harder to validate and more likely to regress.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py` + `lib/requestLog.py` + `lib/requestHistoryActions.py`: start emitting real hooks off the event stream (e.g., a dedicated “history write requested” event) with one end-to-end test covering ordering.
  - `lib/streamingCoordinator.py`: consider recording event metadata needed by downstream consumers (e.g., axes snapshot or completion status) without bloating `last_streaming_snapshot`.

## 2025-12-17 – Loop 49 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – emit a log-entry integration hook from `StreamingSession`.
- Adversarial prioritisation: The streaming path is still the highest-churn coordination surface; without a "real" integration event beyond snapshot/chunk/complete/error, follow-on work to emit history/log/UI events will remain brittle and hard to validate.
- Change: Added `StreamingSession.record_log_entry()` in `lib/streamingCoordinator.py` which emits a `log_entry` event and delegates to `requestLog.append_entry_from_request`. Updated `new_streaming_session()` to stash the session on `GPTState.last_streaming_session`. Updated `lib/modelHelpers.py` to route `append_entry_from_request` through `session.record_log_entry(...)` when the session matches the current `request_id`, preserving existing log behaviour while making the log-write step observable in the streaming event stream.
- Artefact deltas: `lib/streamingCoordinator.py`, `lib/modelHelpers.py`, `_tests/test_streaming_session.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `18 passed`).
- Removal test: reverting would restore a direct `append_entry_from_request` call path and remove the first non-snapshot integration hook from `StreamingSession`, making it harder to validate ordering when future loops add history-write and UI-refresh streaming events.
- Adversarial “what remains” check:
  - `lib/streamingCoordinator.py` + `lib/modelHelpers.py`: add a dedicated streaming event for "history write requested" (with enough metadata to act on) and cover ordering with one end-to-end test.
  - `lib/streamingCoordinator.py`: expand event payloads so consumers can act without re-deriving state from `GPTState` globals.

## 2025-12-17 – Loop 50 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – make history writes explicit in the streaming event stream.
- Adversarial prioritisation: Streaming is still the highest-risk coordination surface. Without a distinct, metadata-bearing event for the post-stream history write, downstream integrations (history/log/UI hooks) will keep relying on implicit ordering and be hard to validate.
- Change: Updated `lib/streamingCoordinator.py` so `StreamingSession.record_log_entry()` now emits a dedicated `history_write_requested` event (with `answer_len`, `meta_len`, `axes_keys`, and `require_directional`) before delegating to `append_entry_from_request`, then emits `log_entry` with `prompt_len`. Updated `_tests/test_streaming_session.py` to assert the new two-event ordering and payload basics. Added an end-to-end ordering guard in `_tests/test_request_streaming.py` asserting `send_request()` produces events `snapshot → chunk → complete → history_write_requested → log_entry` when using the non-stream JSON fallback path.
- Artefact deltas: `lib/streamingCoordinator.py`, `_tests/test_streaming_session.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `19 passed`).
- Removal test: reverting would collapse the history-write step back into an untyped `log_entry` event and drop the end-to-end ordering test, making future streaming integrations harder to validate and easier to regress.
- Adversarial “what remains” check:
  - `lib/streamingCoordinator.py`: introduce an explicit streaming event for UI refresh attempts (throttled vs forced) so canvas behaviour can be validated without patching `modelHelpers` internals.
  - `lib/modelHelpers.py` + `lib/streamingCoordinator.py`: consider moving cancel detection and lifecycle transition emission behind `StreamingSession` to reduce orchestration duplication.

## 2025-12-17 – Loop 51 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – make UI refresh attempts observable in streaming events.
- Adversarial prioritisation: UI refresh behaviour is a high-churn, cross-surface coordination point during streaming. Without an explicit event, it’s hard to validate throttling/forced refresh policies without white-box patching `modelHelpers` internals.
- Change: Added `StreamingSession.record_ui_refresh_requested()` in `lib/streamingCoordinator.py` and wired `lib/modelHelpers.py::_send_request_streaming` to emit `ui_refresh_requested` events for canvas refresh attempts (including throttled skips via `reason="throttled"`). Added a guardrail test in `_tests/test_streaming_session.py` for the new event method, and an end-to-end ordering test in `_tests/test_request_streaming.py` asserting `send_request()` records `ui_refresh_requested` when `_should_show_response_canvas()` is enabled.
- Artefact deltas: `lib/streamingCoordinator.py`, `lib/modelHelpers.py`, `_tests/test_streaming_session.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `21 passed`).
- Removal test: reverting would hide UI refresh decisions again and remove the only black-box test that asserts canvas-enabled streaming emits a UI refresh event.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py` + `lib/streamingCoordinator.py`: consider moving cancel detection and lifecycle transition emission behind `StreamingSession` so request orchestration is thin and event-driven.
  - `lib/streamingCoordinator.py`: consider distinguishing `ui_refresh_requested` vs `ui_refresh_executed` if downstream consumers need to know whether the Talon action actually ran.

## 2025-12-17 – Loop 52 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – distinguish UI refresh requests vs executed outcomes.
- Adversarial prioritisation: UI refresh attempts are a cross-surface coordination hotspot. A request-only event still leaves ambiguity about whether refresh actually ran (or threw), forcing downstream consumers/tests to infer behaviour from side effects.
- Change: Added `StreamingSession.record_ui_refresh_executed()` in `lib/streamingCoordinator.py` and wired `lib/modelHelpers.py::_send_request_streaming` so `_maybe_refresh_canvas()` records `ui_refresh_executed` with `success` (and error text on failure) whenever it attempts `model_response_canvas_refresh()`. Updated `_tests/test_streaming_session.py` to assert `ui_refresh_requested → ui_refresh_executed` ordering, and updated `_tests/test_request_streaming.py` so the canvas-enabled streaming test now uses an SSE-style response and asserts the end-to-end event ordering includes both events.
- Artefact deltas: `lib/streamingCoordinator.py`, `lib/modelHelpers.py`, `_tests/test_streaming_session.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `21 passed`).
- Removal test: reverting would collapse refresh outcomes back into request-only events and remove the only black-box test that proves refresh attempts are recorded as executed-success.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py` + `lib/streamingCoordinator.py`: move cancel detection behind `StreamingSession` (e.g., `session.cancel_requested(state)` that records a `cancel_requested` event) and cover the cancel ordering with one focused test.
  - `lib/streamingCoordinator.py`: consider recording `ui_refresh_executed` for `_refresh_response_canvas()` (UI-thread dispatch) so *all* refresh paths share the same observability contract.

## 2025-12-17 – Loop 53 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – centralise cancel detection behind `StreamingSession`.
- Adversarial prioritisation: Cancel behaviour is a high-risk coordination surface (state machine + UI + history/log side effects). Leaving cancel checks as scattered `getattr(state, "cancel_requested")` branches keeps the contract implicit and hard to test for ordering.
- Change: Added `StreamingSession.cancel_requested(state, source=...)` in `lib/streamingCoordinator.py` which records a `cancel_requested` event (with `source` and `phase`) and returns the boolean. Updated `lib/modelHelpers.py::_send_request_streaming` to use this helper for both the per-chunk loop (`source="iter_lines"`) and the post-stream check (`source="after_stream"`). Added `_tests/test_streaming_session.py` coverage for the new helper and `_tests/test_request_streaming.py` coverage asserting `cancel_requested` is recorded before the first `error` event when cancellation is detected.
- Artefact deltas: `lib/streamingCoordinator.py`, `lib/modelHelpers.py`, `_tests/test_streaming_session.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `23 passed`).
- Removal test: reverting would restore ad-hoc cancel checks in `_send_request_streaming` and remove the only ordering test proving cancellation is observed before streaming error transitions.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py`: use `StreamingSession.cancel_requested` in the exception-path cancel handling too (currently still checks `getattr(state, "cancel_requested")`), and add a test for that ordering.
  - `lib/streamingCoordinator.py`: consider recording a distinct `cancel_executed` event when `emit_cancel`/transport cleanup runs so consumers can distinguish "cancel requested" from "cancel handled".

## 2025-12-17 – Loop 54 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – make exception-path cancellation observable and consistent.
- Adversarial prioritisation: The exception path inside `_send_request_streaming` is where subtle regressions hide: it handles transport errors, cancellation, and fallbacks. Leaving cancellation as a raw `getattr(state, "cancel_requested")` check keeps the policy implicit and makes event ordering inconsistent across cancel paths.
- Change: Updated `lib/modelHelpers.py::_send_request_streaming` so the exception-path cancel branch uses `session.cancel_requested(state, source="exception")`. When cancellation is detected in this branch, it now also records `session.record_error("cancelled")` and `_update_lifecycle("cancel")` before raising `CancelledRequest`, so the streaming event stream includes `cancel_requested → error` like the other cancel paths. Added `_tests/test_request_streaming.py` coverage asserting `cancel_requested(source="exception")` is recorded and precedes the `error` event.
- Artefact deltas: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `24 passed`).
- Removal test: reverting would reintroduce an implicit cancel check in the exception path and drop the only test that pins cancel ordering for exception-driven cancellations.
- Adversarial “what remains” check:
  - `lib/streamingCoordinator.py`: add a `cancel_executed` event (success/error) when transport cleanup + `emit_cancel` runs so consumers can distinguish "cancel requested" from "cancel handled".
  - `lib/modelHelpers.py`: consider routing the AttributeError-as-cancel path through `session.cancel_requested(..., source="attribute_error")` for visibility symmetry.

## 2025-12-17 – Loop 55 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – distinguish cancel requested vs cancel handled.
- Adversarial prioritisation: Cancellation is a multi-step process (detect → mark cancelled → emit UI/lifecycle signals → clean up transport). Without an explicit "handled" event, consumers/tests cannot distinguish "cancel was requested" from "cancel cleanup/emit ran".
- Change: Added `StreamingSession.record_cancel_executed(source, emitted, error)` in `lib/streamingCoordinator.py`. Wired `lib/modelHelpers.py::_send_request_streaming` to emit `cancel_executed` in the `iter_lines`, `after_stream`, and `exception` cancel branches. Updated `_tests/test_streaming_session.py` with a new unit test for `cancel_executed`, and updated `_tests/test_request_streaming.py` cancel tests to assert ordering `cancel_requested → error → cancel_executed` and to assert `source`/`emitted` fields (notably `source="exception"` uses `emitted=False`).
- Artefact deltas: `lib/streamingCoordinator.py`, `lib/modelHelpers.py`, `_tests/test_streaming_session.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `25 passed`).
- Removal test: reverting would remove the only signal that cancel handling executed, forcing callers to infer cleanup/emit from side effects.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py`: route the AttributeError-as-cancel path through `session.cancel_requested(..., source="attribute_error")` and record a matching `cancel_executed` so all cancel sources share the same observability contract.
  - `lib/streamingCoordinator.py`: consider adding `cancel_executed.success` (rather than just `emitted`) once we can safely detect cleanup failures.

## 2025-12-17 – Loop 56 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – make AttributeError-as-cancel observable.
- Adversarial prioritisation: The AttributeError path is a classic "silent" cancel escape hatch: it previously raised `CancelledRequest()` without recording *why* cancellation happened. This is exactly where coordination bugs hide (transport errors vs user cancels vs other teardown).
- Change: Updated `lib/modelHelpers.py::_send_request_streaming` so the `isinstance(e, AttributeError)` branch is treated as a first-class cancel source (`source="attribute_error"`), recording `cancel_requested → error("cancelled") → cancel_executed` (with `emitted=False`). Added `_tests/test_request_streaming.py` coverage asserting the new event ordering and fields.
- Artefact deltas: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `26 passed`).
- Removal test: reverting would reintroduce a silent cancellation path with no source attribution.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py`: consider merging the AttributeError cancel branch with the exception-cancel branch to avoid duplicated cleanup logic.
  - `lib/streamingCoordinator.py`: consider capturing the AttributeError message in `cancel_requested.phase` or adding a dedicated `cancel_reason` field.

## 2025-12-17 – Loop 57 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – enrich cancel detection with a reason/detail.
- Adversarial prioritisation: A cancel source label (e.g. `exception`, `attribute_error`) is still ambiguous without the underlying exception/transport message. This ambiguity makes it harder to distinguish a true user cancel from a transport teardown disguised as cancel.
- Change: Extended `StreamingSession.cancel_requested(..., detail="")` in `lib/streamingCoordinator.py` to always record a `detail` string on the `cancel_requested` event. Updated `lib/modelHelpers.py::_send_request_streaming` to pass the exception message as `detail` for `source="exception"` and `source="attribute_error"`. Fixed and strengthened `_tests/test_request_streaming.py` so the exception and AttributeError cancel cases are separate tests again, and both assert `cancel_requested.detail` values (`"boom"` and `"transport closed"`).
- Artefact deltas: `lib/streamingCoordinator.py`, `lib/modelHelpers.py`, `_tests/test_streaming_session.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_streaming_session.py _tests/test_request_streaming.py` (pass; `26 passed`).
- Removal test: reverting would drop cancel reason visibility and reintroduce ambiguity in cancellation diagnostics.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py`: consider collapsing the cancel branches into one helper to reduce duplicated cleanup logic now that all cancel paths share a common event contract.
  - `lib/streamingCoordinator.py`: consider renaming `detail` to `reason` once stabilized across all callers.

## 2025-12-17 – Loop 58 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – deduplicate cancel error events during streaming.
- Adversarial prioritisation: Cancellation is a high-risk coordination surface (transport + lifecycle + UI). The most failure-prone path was double-recording `error("cancelled")` events (once at cancel detection and again in the `except CancelledRequest` handler), which made event streams harder to reason about and weakened the ordering contract ADR-0056 is trying to stabilize.
- Change: Refactored `lib/modelHelpers.py::_send_request_streaming` cancellation handling behind a single `_raise_cancel(...)` helper that records `error("cancelled")`, performs best-effort cleanup, records `cancel_executed`, updates lifecycle, and raises `CancelledRequest`. The outer `except CancelledRequest` is now a pass-through so cancellation no longer records a second redundant `error` event.
- Guardrail: Tightened cancellation tests in `_tests/test_request_streaming.py` so they assert exactly one `error` event is recorded for each cancel path and that `cancel_executed.emitted` is `True` for the `iter_lines` path.
- Artefact deltas: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_request_streaming.py _tests/test_streaming_session.py` (pass; `26 passed`).
- Removal test: reverting would reintroduce duplicated cancellation error events (and fail the new single-error assertions), weakening the test-backed ordering/observability contract for cancellations in the streaming event stream.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py`: consider moving emit/cleanup into `StreamingSession` so `_send_request_streaming` becomes orchestration-only (reducing the remaining duplication between cancel and non-cancel cleanup paths).
  - `lib/streamingCoordinator.py`: consider renaming `cancel_requested.detail` to `reason` once the field stabilizes across consumers/tests.

## 2025-12-17 – Loop 59 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – stop using `cancel_active_request()` during internal cancellation.
- Adversarial prioritisation: `cancel_active_request()` is meant for external/UI-driven cancellation. Calling it inside `_send_request_streaming` makes cancellation cleanup depend on shared global state (`_active_response`), increases coordination surface area, and risks double-closing the same response. The safer pattern is to clear `_active_response` directly and let `_send_request_streaming`’s own `finally` handle `raw_response.close()`.
- Change: Updated `lib/modelHelpers.py::_send_request_streaming`’s `_raise_cancel(...)` so it no longer calls `cancel_active_request()` or `raw_response.close()` during internal cancellation. It now clears `_active_response` via `_set_active_response(None)`, records the cancellation events, and relies on the function’s `finally` to close the response.
- Guardrail: Tightened cancellation tests in `_tests/test_request_streaming.py` so they patch `cancel_active_request` to raise if called during internal cancellation paths.
- Artefact deltas: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_request_streaming.py` (pass; `8 passed`).
- Removal test: reverting would reintroduce internal dependence on `cancel_active_request()` and would fail the new guardrail assertions that cancellation cleanup stays local to `_send_request_streaming`.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py`: consider reducing double-close risk further by consolidating all `raw_response.close()` calls behind a single helper/flag so cancellation and non-cancellation paths share the same closing semantics.
  - `lib/streamingCoordinator.py`: consider renaming `cancel_requested.detail` to `reason` once the field stabilizes across consumers/tests.

## 2025-12-17 – Loop 60 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – ensure streaming responses always close the HTTP response.
- Adversarial prioritisation: The non-event-stream fallback path (`content-type: application/json`) returns early from `_send_request_streaming` and previously skipped the `finally: raw_response.close()` block, leaking the HTTP response and creating an implicit “sometimes we close” contract. This is exactly the sort of hidden lifecycle ownership bug that drives high-churn coordination in the streaming path.
- Change: Added a local `_close_raw_response()` helper (with a one-shot flag) in `lib/modelHelpers.py::_send_request_streaming` and used it for:
  - The early non-event-stream JSON return path.
  - The non-200 status-code early raise path.
  - The main streaming `finally` block (replacing direct `raw_response.close()`), so response closing is consistent and idempotent.
- Guardrail: Updated `_tests/test_request_streaming.py` with:
  - `test_streaming_non_eventstream_response_closes_response` asserting the JSON fallback response gets `close()` called.
  - `test_streaming_cancel_records_cancel_requested_event` asserting cancel event ordering remains intact (and `cancel_active_request` is not invoked).
- Artefact deltas: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`.
- Checks: `python3 -m pytest _tests/test_request_streaming.py _tests/test_streaming_session.py` (pass; `16 passed`).
- Removal test: reverting would reintroduce a response leak on the non-event-stream early return path (and fail the new `response.closed` assertion), weakening the streaming lifecycle contract this ADR is trying to centralize.
- Adversarial “what remains” check:
  - `lib/modelHelpers.py`: consider moving response-close ownership behind `StreamingSession` (or a tiny transport helper) so the request sender never has to reason about close semantics directly.
  - `lib/requestLog.py` + `lib/requestHistoryActions.py`: use the streaming event stream to drive typed history/log write events beyond the current hooks (next step: consume `history_write_requested` as an explicit lifecycle event).

## 2025-12-17 – Loop 61 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – record history-save lifecycle in the streaming event stream.
- Adversarial prioritisation: History saves are lifecycle-critical and coordination-heavy (request state, filesystem write, UI hooks). Before we add more orchestration, we need an explicit, testable signal that "history save happened" in the same event stream we use for streaming/cancel diagnostics; otherwise consumers must infer from side effects or unrelated bus events.
- Change:
  - Added `StreamingSession.record_history_saved(path, success, error)` in `lib/streamingCoordinator.py` to capture history-save outcomes as structured events.
  - Wired `lib/requestHistoryActions.py::_save_history_prompt_to_file` to call `GPTState.last_streaming_session.record_history_saved(...)` on success when the session request id matches the entry request id.
- Guardrail:
  - Extended `_tests/test_request_history_actions.py::test_history_save_emits_lifecycle_hook` to seed a streaming session and assert a `history_saved` event is recorded with the saved path.
  - Added `_tests/test_streaming_session.py::test_session_history_saved_records_event` to pin the event shape.
- Artefact deltas: `lib/streamingCoordinator.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `_tests/test_streaming_session.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_streaming_session.py` (pass; `104 passed`).
- Removal test: reverting would remove the only explicit, test-backed linkage between history file saves and the streaming lifecycle event stream, increasing coordination risk for future lifecycle refactors.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: record failure outcomes (`success=False`, `error=...`) for write/dir/create failures to avoid a success-only event stream.
  - `GPT/gpt.py` + canvas GUIs: migrate remaining `_request_is_in_flight` / `_reject_if_request_in_flight` clones to `requestState.is_in_flight/try_start_request` and pin drop-reason behaviour.

## 2025-12-17 – Loop 62 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – make history-save failures observable in the streaming event stream.
- Adversarial prioritisation: A success-only `history_saved` event stream is misleading: the hard cases are failure modes (dir create, write failure, missing directional). Without explicit failure events, callers must infer outcomes from side effects (`last_history_save_path`, notifications) and error codes, which recreates the implicit lifecycle coupling ADR-0056 is trying to eliminate.
- Change: Updated `lib/requestHistoryActions.py::_save_history_prompt_to_file` to emit `history_saved(success=False, error=...)` via the active `StreamingSession` on major failure return paths:
  - Empty prompt.
  - Directory creation failure.
  - Missing directional lens.
  - Write failure (records attempted `path`).
  Success now uses the same helper path (`history_saved(success=True, path=...)`) for consistency.
- Guardrail: Extended existing failure tests in `_tests/test_request_history_actions.py`:
  - `test_history_save_handles_directory_creation_failure` asserts a `history_saved` event with `success=False`, empty `path`, and an error string.
  - `test_history_save_handles_write_failure` asserts `success=False`, a non-empty attempted `path` under the configured directory, and an error string.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py -k "history_save_handles_directory_creation_failure or history_save_handles_write_failure"` (pass; `2 passed`). Also `python3 -m pytest _tests/test_request_history_actions.py _tests/test_streaming_session.py` (pass; `104 passed`).
- Removal test: reverting would restore a success-only history-save lifecycle stream, making failure outcomes invisible to any consumer relying on `StreamingSession` events.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: consider recording failure events for the "no entry" path too (no request id available; may need a separate event shape).
  - `GPT/gpt.py` + canvas GUIs: migrate remaining `_request_is_in_flight` / `_reject_if_request_in_flight` clones to `requestState.is_in_flight/try_start_request` and assert drop reasons via tests.

## 2025-12-17 – Loop 63 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – align GPT in-flight gating with central `try_start_request` semantics.
- Adversarial prioritisation: `GPT/gpt.py::_reject_if_request_in_flight` was still doing bespoke phase checks, diverging from the central `requestState.try_start_request` contract used by other canvases. That divergence is a coordination hazard: any evolution in what counts as "in flight" would require updating `GPT/gpt.py` independently.
- Change:
  - Updated `GPT/gpt.py` to import `is_in_flight` and `try_start_request` from `lib/requestState`.
  - Refactored `_reject_if_request_in_flight` to use `try_start_request(state)` to decide whether to block, while preserving the existing notify suppression + once-per-request dedupe behaviour.
- Artefact deltas: `GPT/gpt.py`.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py -k "inflight_guard"` (pass; `2 passed`). Also `python3 -m pytest _tests/test_gpt_actions.py -k "inflight_notifications_deduplicate_across_guards or request_is_in_flight"` (pass; `1 passed`).
- Removal test: reverting would restore bespoke phase checks in `GPT/gpt.py`, reintroducing semantic drift from `requestState.try_start_request` even though other surfaces already rely on it.
- Adversarial “what remains” check:
  - `lib/modelPatternGUI.py` / `lib/modelPromptPatternGUI.py`: confirm their gating helpers also call `try_start_request` (and add tests if any still use phase checks).
  - `lib/requestState.py`: consider extending `try_start_request` to return structured context beyond "in_flight" (request id or phase) once callers need more than a boolean.

## 2025-12-17 – Loop 64 (kind: behaviour)
- Focus: Request Gating & Streaming Lifecycle – record no-history save failures in the streaming event stream.
- Adversarial prioritisation: After adding `history_saved` lifecycle events, the "no history entry" case was still invisible in the event stream because there is no `entry.request_id` to match. That leaves a hole in observability right at the boundary where callers most need consistent signals (users often hit save with no history yet).
- Change: Updated `lib/requestHistoryActions.py::_save_history_prompt_to_file` so the `entry is None` branch records `history_saved(success=False, error=...)` on the latest `StreamingSession` when available.
- Guardrail: Extended `_tests/test_request_history_actions.py::test_history_save_latest_source_returns_none_when_no_history` to seed a streaming session and assert a `history_saved` event is recorded with `success=False`, empty `path`, and an error message.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py -k "history_save_latest_source_returns_none_when_no_history"` (pass; `1 passed`). Also `python3 -m pytest _tests/test_request_history_actions.py _tests/test_streaming_session.py` (pass; `104 passed`).
- Removal test: reverting would reintroduce a silent "no entry" save failure with no corresponding streaming lifecycle event, forcing consumers back to side-effect inference.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: decide whether `history_saved` should include `request_id` explicitly (today it's implicit via session matching) so consumers can correlate without relying on global state.
  - `lib/requestHistoryActions.py`: consider emitting `history_saved` for other early-return failures that currently do not have a stable `request_id` (if any remain after the existing failure coverage).

## 2025-12-17 – Loop 65 (kind: behaviour)
- Focus: Axis Snapshot & History – route history save/show axis normalization through the shared request-log snapshot.
- Adversarial prioritisation: `lib/requestHistoryActions.py` still used `history_axes_for(...)` in key user-facing flows (saving history source files and hydrating GPTState from history). That creates a drift risk versus the shared log normalization contract (`requestLog.axis_snapshot_from_axes`) already used in other history surfaces, and it forces contributors to reason about two subtly different axis “snapshots”.
- Change: Updated `lib/requestHistoryActions.py` so both:
  - `_save_history_prompt_to_file` header generation, and
  - `_show_entry` / GPTState hydration
  use the shared `axis_snapshot_from_axes(...)` (delegating to `lib/requestLog.py`) instead of `history_axes_for(...)`.
- Guardrail:
  - `python3 -m pytest _tests/test_request_history_axes_catalog.py` (pass; `3 passed`).
  - `python3 -m pytest _tests/test_request_history_actions.py -k "show_latest or history_summary_lines"` (pass; `13 passed`).
- Artefact deltas: `lib/requestHistoryActions.py`.
- Removal test: reverting would reintroduce dual normalization paths for history surfaces, increasing the probability of axis snapshot drift across save/show/list workflows.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: decide whether `history_axes_for` should be narrowed to only legacy/backfill use-cases, or deprecated in favor of `axis_snapshot_from_axes` entirely once tests confirm no remaining callers.
  - Axis Snapshot domain: introduce an explicit `AxisSnapshot` structure (beyond `dict[str, list[str]]`) once callers need to carry derived flags (e.g., legacy style) consistently.

## 2025-12-17 – Loop 66 (kind: behaviour)
- Focus: Axis Snapshot & History – collapse `history_axes_for` onto the shared axis snapshot contract.
- Change:
  - Removed the bespoke `_filter_axis_tokens` helper in `lib/requestHistoryActions.py`.
  - Reimplemented `history_axes_for` as a thin wrapper over `axis_snapshot_from_axes`, trimming the snapshot down to the known history axes (`completeness/scope/method/form/channel/directional`).
  - Dropped the now-unused import `axis_key_to_value_map_for`.
- Guardrail:
  - `python3 -m pytest _tests/test_request_history_axes_catalog.py` (pass; `3 passed`).
  - `python3 -m pytest _tests/test_request_history_actions.py -k "history_save_latest_source_returns_none_when_no_history or history_save_handles_write_failure or history_save_handles_directory_creation_failure"` (pass; `3 passed`).
- Artefact deltas: `lib/requestHistoryActions.py`.
- Removal test: reverting would reintroduce a second, divergent axis-normalization implementation for history helpers, undermining the ADR’s Axis Snapshot single-source-of-truth goal.
- Adversarial “what remains” check:
  - `lib/requestLog.py::axis_snapshot_from_axes`: consider tightening the contract around unknown keys (currently passed through) once downstream consumers stop relying on them.
  - Axis Snapshot domain: introduce an explicit `AxisSnapshot` type (beyond a plain dict) when callers need to carry derived flags (like `legacy_style`) across log/history.

## 2025-12-17 – Loop 67 (kind: behaviour)
- Focus: Axis Snapshot & History – promote the AxisSnapshot facade to a structured Concordance snapshot.
- Change: Introduced a frozen `AxisSnapshot` dataclass in `lib/requestLog.py` that separates known axes, passthrough extras, and the `legacy_style` flag; updated `axis_snapshot_from_axes` to build the structured snapshot; migrated history consumers in `lib/requestHistoryActions.py` (history summaries, slug/save flows, `_show_entry`) to use the new API; and refreshed guardrail tests to assert extras and known axes round-trip via the dataclass helpers.
- Artefact deltas: `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_log_axis_filter.py`, `_tests/test_request_log.py`, `_tests/test_history_query.py`.
- Checks: `python3 -m pytest _tests/test_request_log_axis_filter.py _tests/test_request_log.py _tests/test_history_query.py _tests/test_axis_snapshot_alignment.py _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would collapse the structured snapshot back to plain dicts, dropping the new guardrails and reintroducing drift risk between log/history consumers and the Concordance-aligned axis view.
- Adversarial “what remains” check:
  - `lib/historyQuery.py`: ensure downstream rendering/doc helpers explicitly ignore or surface `AxisSnapshot.extras` so passthrough axes cannot silently drift.
  - Axis docs/help generators (`scripts/generate_readme_axis_lists.py`, `_tests/test_static_prompt_docs.py` surfaces): migrate these to consume the structured `AxisSnapshot` to keep documentation aligned with the Concordance snapshot contract.
  - `lib/requestLog.py`: add a guardrail (or immutability enforcement) so `AxisSnapshot` extras remain copy-on-read, preventing accidental mutations once more consumers share the structured object.

## 2025-12-17 – Loop 68 (kind: behaviour)
- Focus: Axis Snapshot & History – harden the AxisSnapshot immutability contract.
- Change: Updated `lib/requestLog.py` so `AxisSnapshot` now stores axes/extras as tuple-backed `MappingProxyType` views, ensuring consumers cannot mutate the shared snapshot; the helper strips empties when materialising the immutable mappings, while existing getters still hand back defensive copies. Added `test_axis_snapshot_is_immutable` to `_tests/test_request_log_axis_filter.py` to assert tuple storage, mutation failures, and copy-on-write semantics.
- Checks: `python3 -m pytest _tests/test_request_log_axis_filter.py _tests/test_request_log.py _tests/test_history_query.py` (pass).
- Removal test: reverting would return mutability to the shared snapshot, allowing downstream code to mutate Concordance-aligned axis state in-place and weakening ADR-0056’s axis snapshot single-source-of-truth guarantees.
- Adversarial “what remains” check:
  - `lib/historyQuery.py`: inspect callers to ensure any future surfacing of passthrough axes explicitly opts in via `AxisSnapshot.extra_axes()` so unexpected keys do not leak silently into rendered summaries.
  - Axis docs/help generators: migrate doc-generation helpers to consume the immutable snapshot (or stamped dict copies) so documentation stays aligned with runtime behaviour and respects the new copy-on-read contract.
  - `lib/requestLog.py`: consider adding an explicit method (e.g., `known_axes_items()`) if future consumers need tuple views without materialising lists, keeping the immutable contract clear while avoiding unnecessary copies.

## 2025-12-17 – Loop 69 (kind: behaviour)
- Focus: Axis Snapshot & History – keep history saves and replay flows constrained to Concordance-known axes.
- Change: Updated `lib/requestHistoryActions.py` so history summaries, saves, and replay helpers consume `AxisSnapshot.known_axes()` (dropping passthrough extras) before building slugs, headers, and GPT state; fallback directional tokens are now added to the known-axis map only when required. Added `test_history_save_omits_extra_axis_tokens` and `test_history_show_latest_ignores_extra_axes` in `_tests/test_request_history_actions.py` to assert that non-Concordance axes neither appear in saved markdown headers nor leak into `GPTState.last_axes`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py _tests/test_history_query.py` (pass).
- Removal test: reverting would reintroduce passthrough axis tokens into history saves and replay state, allowing Concordance-irrelevant axes to drift into user-visible metadata and weakening ADR-0056’s snapshot contract.
- Adversarial “what remains” check:
  - `lib/historyQuery.py`: add an explicit guardrail covering drawer/summary rendering so passthrough extras stay suppressed (or are surfaced intentionally) when we introduce richer AxisSnapshot consumers.
  - Axis docs/help generators: align list/readme generation with `AxisSnapshot.known_axes()` so Concordance-facing documentation cannot drift from the runtime snapshot contract.
  - `lib/requestLog.py`: consider exposing a structured iterator (e.g., `known_axis_items`) for callers that prefer tuple views without allocating new lists, reinforcing the immutable snapshot semantics.

