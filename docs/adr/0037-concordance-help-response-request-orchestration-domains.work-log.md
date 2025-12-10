# 0037 Concordance – Help, Response, and Request Orchestration Domains – Work Log

## 2025-12-10
- Slice: introduce an initial AxisDocs façade and characterization test (Axis docs & response surfaces – Phase 1).
- Changes:
  - Added `AxisDoc` dataclass, `axis_docs_for`, and `axis_docs_index` helpers in `lib/axisConfig.py` as the structured documentation façade over `AXIS_KEY_TO_VALUE`.
  - Added `_tests/test_axis_docs.py` to assert that `axis_docs_for("completeness")` stays consistent with the existing `axisMappings.axis_docs_map` façade.
- Validation: `python3 -m pytest _tests/test_axis_mappings.py _tests/test_axis_docs.py`.
- Follow-ups: wire `modelResponseCanvas`/`modelHelpCanvas` axis rendering onto `axis_docs_for`/`axis_docs_index` and extend tests to cover axis grouping/flags as they are introduced.

## 2025-12-10 (loop 2)
- Slice: expand AxisDocs characterization tests across core axes (Axis docs & response surfaces – Phase 1).
- Changes:
  - Extended `_tests/test_axis_docs.py` so `axis_docs_for` is checked for all core Concordance axes (`completeness`, `scope`, `method`, `style`) against `axisMappings.axis_docs_map`.
  - Added an `axis_docs_index` test to confirm it exposes the same key sets and descriptions as `axisMappings.axis_docs_map` for those axes.
- Validation: `python3 -m pytest _tests/test_axis_mappings.py _tests/test_axis_docs.py`.
- Follow-ups: next AxisDocs slices can introduce explicit group/flag structures and begin wiring `modelResponseCanvas` / `modelHelpCanvas` axis rendering onto the façade using these characterization tests as guardrails.

## 2025-12-10 (loop 3)
- Slice: wire quick-help axis listings onto AxisDocs façade (Axis docs & response surfaces – Phase 2).
- Changes:
  - Updated `lib/modelHelpCanvas.py` so `_axis_keys` derives axis keys from `axisConfig.axis_docs_for` (AxisDocs façade) instead of using `axisMappings.axis_docs_map` directly.
  - Swapped the `axisMappings` import in `modelHelpCanvas` for an `axisConfig` import to keep the quick-help canvas aligned with the AxisDocs single source of truth.
- Validation: `python3 -m pytest _tests/test_model_help_canvas.py _tests/test_axis_docs.py`.
- Follow-ups: similar wiring for `modelResponseCanvas` axis recap, then introduction of explicit group/flag structures in AxisDocs.

## 2025-12-10 (loop 4)
- Slice: introduce a reusable history axis token filter helper (Request lifecycle & history – Phase 1).
- Changes:
  - Added `_filter_axis_tokens(axis, tokens)` in `lib/requestHistoryActions.py` to centralise the existing axis token filtering semantics using `axis_key_to_value_map_for`.
  - Updated `_show_entry` in `requestHistoryActions` to use `_filter_axis_tokens` when hydrating `GPTState.last_axes` from history entries while keeping behaviour unchanged.
- Validation: `python3 -m pytest _tests/test_request_history_actions.py`.
- Follow-ups: future RequestLifecycle/HistoryQuery slices can call this helper from a façade module and extend tests to drive history queries directly.

## 2025-12-10 (status snapshot)
- Axis docs & response surfaces:
  - AxisDocs façade and tests are in place (`lib/axisConfig.py`, `_tests/test_axis_docs.py`).
  - `modelHelpCanvas` consumes AxisDocs for axis key order; response canvas still used legacy axis token helpers prior to loop 5.
- Help discovery & interaction:
  - Core help canvases/GUI logic remain wired through existing `helpHub` and `modelHelpGUI`; HelpDomain façade extraction is still entirely ahead.
- Request lifecycle & history orchestration:
  - History axis token filtering is centralised in `_filter_axis_tokens` in `requestHistoryActions` and exercised via existing tests.
  - A full RequestLifecycle façade and HistoryQuery module are not yet introduced; current work has only prepared the axis-filtering contract.
- Overall:
  - Recent slices have focused on AxisDocs and history preparation; next substantial slices can target response canvas AxisDocs wiring (completed in loop 5 below), HelpDomain extraction from `helpHub`, or an initial RequestLifecycle façade around the request state machine.

## 2025-12-10 (loop 5)
- Slice: wire response canvas axis hydration onto AxisDocs façade (Axis docs & response surfaces – Phase 2).
- Changes:
  - Updated `lib/modelResponseCanvas.py` to import `axis_docs_for` from `axisConfig` and to hydrate axis descriptions in `_hydrate_axis` via `axis_docs_for` instead of `axis_hydrate_tokens`.
  - This keeps the user-facing axis descriptions identical while having both quick help and the response canvas share the AxisDocs documentation source.
- Validation: `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_model_helpers_response_canvas.py _tests/test_axis_overlap_alignment.py _tests/test_readme_axis_lists.py _tests/test_axis_docs.py`.
- Follow-ups: future AxisDocs slices can add explicit group/flag metadata in `axisConfig` and, if needed, extend response/help canvases to surface those flags.

## 2025-12-10 (loop 6)
- Slice: extract a pure Help-domain navigation helper for Hub focus stepping (Help discovery & interaction – Phase 1).
- Changes:
  - Introduced `_next_focus_label(current, delta, items)` in `lib/helpHub.py` to compute the next focus target label given the current hover label, step, and the ordered focusable items from `_focusable_items`.
  - Updated `_focus_step` to delegate to `_next_focus_label` before updating `HelpHubState.hover_label`, keeping keyboard navigation behaviour identical while separating the pure navigation semantics.
  - Added `test_help_hub_next_focus_label_wraps_and_steps` in `_tests/test_help_hub.py` to characterise forward/backward wrapping behaviour across button and result items.
- Validation: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain slices can factor search indexing and ranking into similarly pure helpers and reuse `_next_focus_label` from a dedicated HelpDomain façade.

## 2025-12-10 (loop 7)
- Slice: introduce a pure Help-domain search helper for Hub filtering (Help discovery & interaction – Phase 1).
- Changes:
  - Added `search_results_for(query, index)` in `lib/helpHub.py` as a pure helper that computes Help Hub search matches from a query and `HubButton` index using the existing case-insensitive label substring semantics.
  - Updated `_recompute_search_results` in `helpHub` to delegate to `search_results_for`, keeping behaviour unchanged while making search semantics explicit and testable without canvas/global state.
  - Extended `_tests/test_help_hub.py` with `test_help_hub_search_results_for_is_pure_and_label_based` to characterise empty/whitespace queries and case-insensitive label matching for representative buttons.
- Validation: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain slices can build on `search_results_for` to introduce richer ranking or multi-field matching, and eventually extract a full HelpDomain façade over Help Hub indexing, search, and navigation.

## 2025-12-10 (loop 8)
- Slice: introduce a pure history axes normalisation helper for request history entries (Request lifecycle & history – Phase 1).
- Changes:
  - Added `history_axes_for(axes)` in `lib/requestHistoryActions.py` as a pure helper that normalises stored history axis tokens via the configured axis maps using the existing `_filter_axis_tokens` semantics.
  - Updated `_show_entry` in `requestHistoryActions` so the `entry.axes` branch delegates to `history_axes_for`, keeping behaviour unchanged while making the history axis-filtering contract reusable for future RequestLifecycle/HistoryQuery façades.
  - Extended `_tests/test_request_history_actions.py` with `test_history_axes_for_filters_invalid_tokens` to characterise filtering of invalid/hydrated tokens across all four axes in isolation from GPTState.
- Validation: `python3 -m pytest _tests/test_request_history_actions.py`.
- Follow-ups: future RequestLifecycle/HistoryQuery slices can reuse `history_axes_for` when driving history queries or summarising axes directly, and can add higher-level façade tests that build on this normalisation step.

## 2025-12-10 (loop 9)
- Slice: extract a pure history summary formatter for recent request entries (Request lifecycle & history – Phase 1).
- Changes:
  - Added `history_summary_lines(entries)` in `lib/requestHistoryActions.py` as a pure helper that mirrors the existing `gpt_request_history_list` formatting of recent history entries (prompt snippet, optional duration, recipe + prompt payload).
  - Updated `gpt_request_history_list` to delegate to `history_summary_lines` for line construction while keeping the user-facing message and notification behaviour unchanged.
  - Extended `_tests/test_request_history_actions.py` with `test_history_summary_lines_matches_existing_formatting` to characterise the summary format using real `append_entry` / `all_entries` history entries.
- Validation: `python3 -m pytest _tests/test_request_history_actions.py`.
- Follow-ups: future HistoryQuery / RequestLifecycle façades can call `history_summary_lines` directly to drive drawers or help surfaces, reducing duplication of summary logic and making it easier to evolve history presentation under tests.

## 2025-12-10 (loop 10)
- Slice: introduce a pure Help-domain search index constructor for Hub results (Help discovery & interaction – Phase 1).
- Changes:
  - Added `build_search_index(buttons, patterns, presets, read_list_items)` in `lib/helpHub.py` as a pure helper that constructs the Help Hub search index from hub buttons, static prompt lists, axis lists, patterns, and prompt presets, mirroring the legacy `_build_search_index` behaviour.
  - Updated `_build_search_index` in `helpHub` to delegate to `build_search_index(_buttons, PATTERNS, PROMPT_PRESETS, _read_list_items)`, keeping runtime behaviour unchanged while making index construction testable without depending on globals.
  - Extended `_tests/test_help_hub.py` with `_DummyButton` and `test_build_search_index_uses_buttons_and_lists` to verify that the helper emits the expected "Hub:", "Prompt:", and axis entries when given stubbed buttons and list-file contents.
- Validation: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain façade slices can call `build_search_index` directly (with injected list readers and pattern sources) to build a richer help index and ranking layer without entangling it with canvas or key/mouse handlers.

## 2025-12-10 (loop 11)
- Slice: extract a pure Help-domain helper for Hub navigation focus targets (Help discovery & interaction – Phase 1).
- Changes:
  - Added `focusable_items_for(filter_text, buttons, results)` in `lib/helpHub.py` as a pure helper that mirrors `_focusable_items` semantics, computing the ordered `(kind, label)` focus targets from filter text, hub buttons, and search results.
  - Updated `_focusable_items` to delegate to `focusable_items_for(HelpHubState.filter_text or "", _buttons, _search_results)`, leaving keyboard focus behaviour unchanged while making the core navigation contract testable without HelpHub globals.
  - Extended `_tests/test_help_hub.py` with `_DummyButton` helpers and two tests: `test_focusable_items_for_uses_results_when_filtered` and `test_focusable_items_for_includes_buttons_when_unfiltered`, characterising the behaviour when a filter is present (only results focusable) versus absent (buttons then results).
- Validation: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain façades can combine `build_search_index`, `search_results_for`, `focusable_items_for`, and `_next_focus_label` into a fully pure search+navigation layer, loosening coupling between Help Hub's UI wiring and its discovery semantics.

## 2025-12-10 (loop 12)
- Slice: extend AxisDocs entries with explicit group/flags structure (Axis docs & response surfaces – Phase 1).
- Changes:
  - Updated `AxisDoc` in `lib/axisConfig.py` to include `group: str | None` and `flags: FrozenSet[str]` fields, with defaults of `None` and an empty `frozenset`, while keeping existing `axis`, `key`, and `description` fields and behaviour unchanged.
  - Left `axis_docs_for` and `axis_docs_index` behaviourally identical (they now populate the new fields with their defaults), so existing canvases and docs continue to consume AxisDocs without modification.
  - Extended `_tests/test_axis_docs.py` with `test_axis_docs_default_group_and_flags_are_empty` to assert that the new fields default to `None` and an empty `frozenset` for all `completeness` axis docs.
- Validation: `python3 -m pytest _tests/test_axis_docs.py`.
- Follow-ups: future AxisDocs slices can begin populating `group` and `flags` for selected axes (for example, marking guardrail axes or tune hotspots) and, if needed, extend response/help canvases to surface this metadata under these tests.

## 2025-12-10 (loop 13)
- Slice: introduce a minimal pure RequestLifecycle reducer façade (Request lifecycle & history – Phase 1).
- Changes:
  - Added `lib/requestLifecycle.py` with a `RequestLifecycleState` dataclass that tracks a logical `status` over the core request lifecycle (`pending`, `running`, `streaming`, `completed`, `errored`, `cancelled`) independent of transport or UI concerns.
  - Implemented `reduce_request_state(state, event)` as a pure reducer over high-level events (`start`, `stream_start`, `stream_end`, `complete`, `error`, `cancel`), including terminal semantics where `errored` and `cancelled` states ignore further lifecycle events.
  - Added `_tests/test_request_lifecycle.py` with `RequestLifecycleTests` to characterise happy-path streaming and non-streaming flows, error/cancel terminal behaviour, and the handling of unknown events.
- Validation: `python3 -m pytest _tests/test_request_lifecycle.py`.
- Follow-ups: future RequestLifecycle slices can wire `modelHelpers.send_request` / `_send_request_streaming` and request/history modules to emit and consume these events, and can extend the state to carry tags and axis/static-prompt context as called for in ADR-0037.

## 2025-12-10 (loop 14)
- Slice: extract a pure history drawer rendering helper for request history entries (Request lifecycle & history – Phase 1).
- Changes:
  - Added `history_drawer_entries_from(entries)` in `lib/requestHistoryDrawer.py` as a pure helper that mirrors the existing `_refresh_entries` formatting, rendering request log entries into `(label, body)` tuples for the history drawer.
  - Updated `_refresh_entries` in `requestHistoryDrawer` to delegate to `history_drawer_entries_from(entries)` after loading and reversing the entries from `all_entries()`, keeping drawer behaviour unchanged while making the rendering contract reusable.
  - Extended `_tests/test_request_history_drawer.py` with `test_history_drawer_entries_from_matches_label_and_body` to characterise the label (including duration) and body (recipe + prompt snippet) for a representative dummy entry.
- Validation: `python3 -m pytest _tests/test_request_history_drawer.py`.
- Follow-ups: future HistoryQuery façades can reuse `history_drawer_entries_from` together with `history_summary_lines` and `history_axes_for` to provide consistent, test-backed history views for drawers, logs, and potential help/history search surfaces.

## 2025-12-10 (loop 15)
- Slice: introduce a thin HelpDomain façade over existing Help Hub pure helpers (Help discovery & interaction – Phase 1).
- Changes:
  - Added `lib/helpDomain.py` with façade functions `help_index`, `help_search`, `help_focusable_items`, and `help_next_focus_label` that delegate to `helpHub.build_search_index`, `search_results_for`, `focusable_items_for`, and `_next_focus_label` respectively, providing a stable HelpDomain entrypoint without changing behaviour.
  - Added `_tests/test_help_domain.py` with `HelpDomainTests` that exercise `help_focusable_items` and `help_next_focus_label`, asserting that they preserve the existing `helpHub` semantics for unfiltered vs filtered focus targets and navigation wrapping.
- Validation: `python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain slices can migrate more of the help indexing/search/navigation logic into `helpDomain.py` itself and gradually have `helpHub` import and use that façade, simplifying event handlers and further decoupling UI wiring from discovery semantics.

## 2025-12-10 (loop 16)
- Slice: route Help Hub search and navigation helpers through the HelpDomain façade (Help discovery & interaction – Phase 2).
- Changes:
  - Refactored `lib/helpDomain.py` so `help_search`, `help_focusable_items`, and `help_next_focus_label` implement the pure search and navigation semantics directly instead of delegating back into `helpHub`, keeping behaviour identical while removing the tight coupling.
  - Updated `lib/helpHub.py` to import the HelpDomain façade and delegate its `search_results_for`, `focusable_items_for`, and `_next_focus_label` helpers to `help_search`, `help_focusable_items`, and `help_next_focus_label` respectively, so Help Hub’s keyboard focus and filtering now flow through the HelpDomain surface.
  - Extended `_tests/test_help_domain.py` with `test_help_search_matches_label_substring_semantics` to characterise HelpDomain search behaviour (empty/whitespace queries and case-insensitive label substring matching), complementing the existing Help Hub search tests.
- Validation: `python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain slices can move index construction logic (`build_search_index` / `help_index`) into `helpDomain.py` proper and, if needed, further simplify `helpHub._on_key`/`_on_mouse` by leaning on the façade for higher-level “given event → next selection/scroll window” decisions.

## 2025-12-10 (loop 17)
- Slice: align UI-focused request state phases with the RequestLifecycle façade (Request lifecycle & history – Phase 1).
- Changes:
  - Added `lifecycle_status_for(state)` in `lib/requestState.py` as a pure helper that maps the existing `RequestPhase` values onto the logical `RequestLifecycleState` statuses (`pending`, `running`, `streaming`, `completed`, `errored`, `cancelled`), providing a thin adapter from the UI/state-machine view to the ADR-0037 RequestLifecycle façade.
  - Exported `lifecycle_status_for` from `requestState` so future RequestLifecycle/HistoryQuery slices can consume it when correlating UI phases with transport-agnostic lifecycle states.
  - Extended `_tests/test_request_state.py` with `test_lifecycle_status_for_maps_phases_to_logical_status`, asserting that each `RequestPhase` (idle/listening/transcribing/confirming, sending, streaming, done, error, cancelled) maps to the expected lifecycle status and returns a `RequestLifecycleState` instance.
- Validation: `python3 -m pytest _tests/test_request_state.py _tests/test_request_lifecycle.py`.
- Follow-ups: future RequestLifecycle slices can reuse `lifecycle_status_for` when wiring `modelHelpers`/controller code into the RequestLifecycle façade, and can introduce event-level adapters so streaming/logging/history surfaces operate on shared lifecycle events rather than ad-hoc phase checks.

## 2025-12-10 (loop 18)
- Slice: introduce a minimal HistoryQuery façade over existing history helpers (Request lifecycle & history – Phase 1).
- Changes:
  - Added `lib/historyQuery.py` with façade functions `history_axes_for`, `history_summary_lines`, and `history_drawer_entries_from` that delegate directly to the existing pure helpers in `requestHistoryActions` and `requestHistoryDrawer`, providing a single HistoryQuery entrypoint without changing behaviour.
  - Added `_tests/test_history_query.py` with `HistoryQueryTests` that exercise each façade function and assert that their outputs are identical to calling the underlying helpers directly on representative dummy entries and axis dicts.
- Validation: `python3 -m pytest _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py`.
- Follow-ups: future RequestLifecycle/HistoryQuery slices can import `historyQuery` instead of the lower-level modules when wiring drawers, help/history surfaces, or request orchestrators to shared history contracts.

## 2025-12-10 (loop 19)
- Slice: reconcile ADR-0037 Salient Tasks with current façade implementations (status snapshot).
- Changes:
  - Marked the first two AxisDocs façade sub-tasks as completed in `docs/adr/0037-concordance-help-response-request-orchestration-domains.md`, reflecting that `lib/axisConfig.py` now exposes an `AxisDoc` façade with typed fields and that both `modelResponseCanvas` and `modelHelpCanvas` consume it under tests.
  - Marked the first RequestLifecycle & HistoryQuery façade sub-task as completed in the same ADR, reflecting the presence of `lib/requestLifecycle.py`, `lib/requestState.lifecycle_status_for`, `lib/historyQuery.py`, and their associated unit tests.
- Validation: documentation-only status alignment; no code behaviour changes.
- Follow-ups: remaining RequestLifecycle & HistoryQuery items (migrating `modelHelpers`/drawers to the façades and removing duplicated lifecycle/history logic) are still open and will require future behaviour-changing slices guarded by the existing request/history test suites.

## 2025-12-10 (loop 20)
- Slice: characterise HelpDomain `help_index` against Help Hub’s `build_search_index` (Help discovery & interaction – Phase 1).
- Changes:
  - Extended `_tests/test_help_domain.py` to import `hub_build_search_index` from `helpHub` and added `test_help_index_matches_help_hub_build_search_index`, which builds a small index via both `help_index` and `helpHub.build_search_index` with a stubbed `read_list_items` and asserts that the resulting labels match exactly.
  - This test complements the existing `test_build_search_index_uses_buttons_and_lists` in `_tests/test_help_hub.py`, providing a direct guard that the HelpDomain façade remains consistent with Help Hub’s index construction semantics as future refactors move more logic into `helpDomain.py`.
- Validation: `python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py`.
- Follow-ups: future HelpDomain slices can safely migrate `help_index` away from delegating into `helpHub.build_search_index`, using this new test plus the existing help-hub tests to keep index behaviour stable.

## 2025-12-10 (loop 21)
- Slice: expose a RequestLifecycle adapter on the request bus (Request lifecycle & history – Phase 1).
- Changes:
  - Added `current_lifecycle_state()` in `lib/requestBus.py` as a thin adapter that maps the current `RequestState` returned by `current_state()` through `requestState.lifecycle_status_for`, exposing the logical `RequestLifecycle` status on the same bus surface used by controllers.
  - Extended `_tests/test_request_bus.py` with `test_current_lifecycle_state_tracks_bus_phase`, which drives the bus through `emit_begin_send`, `emit_begin_stream`, `emit_complete`, `emit_fail`, and `emit_cancel` and asserts that `current_lifecycle_state().status` matches the expected lifecycle values (`pending`, `running`, `streaming`, `completed`, `errored`, `cancelled`).
- Validation: `python3 -m pytest _tests/test_request_bus.py _tests/test_request_lifecycle.py _tests/test_request_state.py`.
- Follow-ups: future RequestLifecycle slices can reuse `current_lifecycle_state()` when wiring `modelHelpers` and history surfaces to the façade, and can introduce event-level adapters so streaming/logging/history behaviour operates on shared lifecycle events rather than ad-hoc phase checks.

## 2025-12-10 (loop 22)
- Slice: move help index construction semantics into the HelpDomain façade (Help discovery & interaction – Phase 1).
- Changes:
  - Updated `lib/helpDomain.py` so `help_index` now builds the logical help search index directly, returning `HelpIndexEntry` dataclasses that capture `label`, `description`, `handler`, and `voice_hint` for hub buttons, static prompts, axis modifiers, patterns, and prompt presets, mirroring the previous `helpHub.build_search_index` behaviour under tests.
  - Adjusted `lib/helpHub.py` to import `help_index` and to have `build_search_index` delegate to it, adapting the returned entries into `HubButton` instances; this keeps Help Hub’s UI type and handlers intact while moving the indexing semantics into the HelpDomain layer.
  - Left existing Help Hub tests intact, relying on `_tests/test_help_domain.py::test_help_index_matches_help_hub_build_search_index` and `_tests/test_help_hub.py::test_build_search_index_uses_buttons_and_lists` to assert that labels produced by `help_index` and `build_search_index` remain identical for representative buttons/list contents.
- Validation: `python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain slices can extend `HelpIndexEntry` metadata if needed (for ranking or source annotations) and can further simplify Help Hub by treating HelpDomain as the canonical source for help indexing, while additional tests can focus on ranking and keyboard/mouse navigation contracts.

## 2025-12-10 (loop 23)
- Slice: characterise non-stream JSON fallback behaviour in `_send_request_streaming` (Request lifecycle & history – Phase 1).
- Changes:
  - Extended `_tests/test_request_streaming.py` with `test_streaming_falls_back_to_non_stream_json_response`, which patches `modelHelpers.settings.get` and `modelHelpers.requests.post` so `_send_request_streaming` receives a 200 OK response with `content-type: application/json` and a single JSON body, forcing the non-streaming fallback path.
  - The new test asserts that `_send_request_streaming` returns the parsed message content (`"Hello world"`), updates `GPTState.text_to_confirm` to the same value, and sets `GPTState.last_raw_response` to the parsed JSON structure, providing explicit coverage for the branch where the server ignores the `stream` flag.
- Validation: `python3 -m pytest _tests/test_request_streaming.py`.
- Follow-ups: future RequestLifecycle slices can build on this characterisation to safely refactor streaming behaviour (including cancellation and retry paths) under tests, and to integrate RequestLifecycle event emission without altering how non-streaming responses are parsed.

## 2025-12-10 (loop 24)
- Slice: add a consolidated ADR-0037 current status snapshot (status reconciliation).
- Changes:
  - Updated `docs/adr/0037-concordance-help-response-request-orchestration-domains.md` to include a new "Current Status (2025-12-10)" section just before Salient Tasks, summarising which façade tasks (AxisDocs, HelpDomain, RequestLifecycle & HistoryQuery) are complete versus still in-progress for this repo, and noting that Concordance hotspot scans have not yet been re-run after the latest refactors.
  - This snapshot draws from the existing work-log loops and Salient Tasks checkboxes so future ADR loops can more quickly see what remains in-repo (for example, canvas axis-logic cleanup, Help Hub event-handler simplification, and RequestLifecycle/HistoryQuery migrations for `modelHelpers` and drawers).
- Validation: documentation-only status alignment; no code or behaviour changes.
- Follow-ups: subsequent loops should focus on the remaining Salient Tasks bullets (especially RequestLifecycle/HistoryQuery migrations and Help Hub event-handler simplification), using this status summary as the starting point.

## 2025-12-10 (loop 25)
- Slice: characterise timeout handling in `_send_request_streaming` (Request lifecycle & history – Phase 1).
- Changes:
  - Rewrote `_tests/test_request_streaming.py` to keep the original streaming accumulation and cancellation behaviours while adding `test_streaming_timeout_raises_gpt_request_error`, which exercises the `requests.exceptions.Timeout` branch in `lib/modelHelpers._send_request_streaming` via the stubbed `requests` module.
  - The new test patches `modelHelpers.settings.get` so streaming is enabled and a short timeout is used, configures the stubbed `modelHelpers.requests.post` to raise a local `DummyTimeout` exception, and sets `modelHelpers.requests.exceptions.Timeout` to that type so the helper's `except requests.exceptions.Timeout` clause is taken. It asserts that `_send_request_streaming` raises `GPTRequestError` with a `status_code` of 408 and an error message beginning with `"Request timed out after"`.
- Validation: `python3 -m pytest _tests/test_request_streaming.py`.
- Follow-ups: future RequestLifecycle slices can rely on these streaming tests (accumulation, cancellation, JSON fallback, timeout) when refactoring `_send_request_streaming` and integrating the RequestLifecycle façade, ensuring all major streaming branches remain covered.

## 2025-12-10 (loop 26)
- Slice: migrate history drawer rendering semantics into the HistoryQuery façade (Request lifecycle & history – Phase 2).
- Changes:
  - Updated `lib/historyQuery.py` so `history_drawer_entries_from` now implements the drawer label/body formatting directly, mirroring the previous pure helper in `lib/requestHistoryDrawer.py` (request id, optional duration suffix, recipe + prompt snippet), rather than delegating back into the drawer module.
  - Updated `lib/requestHistoryDrawer.py` to import `history_drawer_entries_from` from `historyQuery` and use it in `_refresh_entries`, removing the local pure helper so the drawer now consumes the HistoryQuery façade for its entry rendering semantics.
  - Left `_tests/test_request_history_drawer.py` and `_tests/test_history_query.py` unchanged; both suites continue to pass and now exercise the shared HistoryQuery implementation instead of a duplicated helper in the drawer.
- Validation: `python3 -m pytest _tests/test_request_history_drawer.py _tests/test_history_query.py`.
- Follow-ups: future RequestLifecycle/HistoryQuery slices can treat `historyQuery` as the single entrypoint for history axes, summaries, and drawer entries, and can progressively migrate other history consumers (including potential Help/Concordance history views) away from lower-level modules.

## 2025-12-10 (loop 27)
- Slice: centralise Help Hub filter-text editing semantics in HelpDomain (Help discovery & interaction – Phase 2).
- Changes:
  - Added `help_edit_filter_text(text, key, *, alt, cmd)` in `lib/helpDomain.py` as a pure helper that mirrors Help Hub’s existing filter editing behaviour: plain backspace deletes one character, Alt+backspace/delete trims the last word (or clears when only one), Cmd+backspace/delete clears the whole filter, and printable characters append.
  - Updated `lib/helpHub.py`’s `_on_key` handler so backspace/delete branches and printable-character input delegate to `help_edit_filter_text`, preserving the prior modifier semantics (including the existing Alt/Cmd “active” window) while moving the string-editing contract into the HelpDomain façade.
  - Extended `_tests/test_help_domain.py` with `test_help_edit_filter_text_matches_help_hub_semantics`, and re-ran the focused help suites (`_tests/test_help_domain.py`, `_tests/test_help_hub.py`, `_tests/test_model_help_gui.py`, `_tests/test_model_help_canvas.py`) to confirm behaviour is unchanged.
- Validation: `python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain slices can further simplify `_on_key` and `_on_mouse` by delegating more of the navigation and selection logic to façade helpers, moving toward the ADR-0037 goal of thin event handlers over a testable help domain.

## 2025-12-10 (loop 28)
- Slice: delegate Help Hub activation semantics to the HelpDomain façade (Help discovery & interaction – Phase 2).
- Changes:
  - Added `help_activation_target(current, buttons, results)` in `lib/helpDomain.py` as a pure helper that, given a `"kind:label"` focus identifier and the current hub buttons/search results, returns the underlying object whose handler should be invoked (or `None` when no match is found), mirroring the existing `_activate_focus` label resolution logic.
  - Updated `lib/helpHub.py`’s `_activate_focus` implementation to call `help_activation_target(HelpHubState.hover_label or "", _buttons, _search_results)` and, if a target is returned, invoke its `handler` if callable, making the Help Hub Enter-key activation path a thin adapter over the HelpDomain semantics.
  - Extended `_tests/test_help_domain.py` with `test_help_activation_target_matches_help_hub_semantics`, asserting that button and result focus labels resolve to the correct objects and that unknown labels return `None`, then re-ran the focused help suites to confirm behaviour remains unchanged.
- Validation: `python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: further HelpDomain slices can consider higher-level helpers that combine focus computation, activation, and scroll decisions, allowing `_on_key` and `_on_mouse` to delegate most of their logic to the façade while relying on existing help tests as guardrails.

## 2025-12-10 (loop 29)
- Slice: expose explicit terminal-state semantics on the RequestLifecycle façade (Request lifecycle & history – Phase 1).
- Changes:
  - Added `is_terminal(state)` in `lib/requestLifecycle.py` as a pure helper that returns `True` when the lifecycle status is `"errored"` or `"cancelled"` and `False` otherwise, matching the reducer’s contract that these states ignore subsequent lifecycle events while other statuses remain mutable.
  - Extended `_tests/test_request_lifecycle.py` with `test_is_terminal_matches_error_and_cancel_contract`, which asserts that `pending`, `running`, `streaming`, and `completed` are non-terminal and that `errored` and `cancelled` are terminal, providing a direct guard on the façade’s notion of terminal states.
- Validation: `python3 -m pytest _tests/test_request_lifecycle.py`.
- Follow-ups: future RequestLifecycle slices can reuse `is_terminal` when wiring model helpers and orchestrators to avoid emitting further lifecycle events after error/cancel, and can introduce additional helpers for common transitions as RequestLifecycle is threaded through `modelHelpers` and related modules.

## 2025-12-10 (loop 30)
- Slice: delegate Help Hub mouse-click activation semantics to the HelpDomain façade (Help discovery & interaction – Phase 2).
- Changes:
  - Updated the button and result click branches in `lib/helpHub.py`’s `_on_mouse` handler so that, when a click lands inside a button or result rect, `HelpHubState.hover_label` is set to the corresponding `"btn:<label>"` or `"res:<label>"` and activation is delegated to `help_activation_target`, invoking the target’s `handler` if callable.
  - This mirrors the Enter-key path that already uses `help_activation_target`, making mouse and keyboard activation go through the same HelpDomain resolution logic while leaving scroll/drag/close behaviour unchanged.
  - Re-ran the focused help suites (`_tests/test_help_hub.py`, `_tests/test_model_help_gui.py`, `_tests/test_model_help_canvas.py`), which all remained green, confirming that click activation semantics are preserved under the new façade delegation.
- Validation: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain slices can further centralise higher-level “event → focus/activation/scroll” decisions while keeping Help Hub’s handlers as thin adapters, with keyboard and mouse paths consistently routed through HelpDomain helpers.

## 2025-12-10 (loop 31)
- Slice: simplify Help Hub click handler to rely on HelpDomain activation (Help discovery & interaction – Phase 2).
- Changes:
  - Updated `lib/helpHub.py`’s `_handle_click` helper so it only handles the explicit close-box hit target and no longer re-implements button/result activation; button and result clicks now flow exclusively through `_on_mouse` and `help_activation_target`, keeping activation semantics centralised in the HelpDomain façade.
  - This removes duplicated activation logic from `_handle_click` while preserving the cheap close affordance, making Help Hub’s mouse handling a thinner adapter over HelpDomain.
  - Re-ran the focused help suites (`_tests/test_help_domain.py`, `_tests/test_help_hub.py`, `_tests/test_model_help_gui.py`, `_tests/test_model_help_canvas.py`), which all remained green.
- Validation: `python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
- Follow-ups: future HelpDomain slices can optionally centralise additional scroll/drag layout decisions, but the core help index/search/navigation/activation semantics now live in `lib/helpDomain.py` with Help Hub as a thin adapter.

## 2025-12-10 (loop 32)
- Slice: reconcile ADR-0037 Current Status with HelpDomain and HistoryQuery façade usage (status snapshot).
- Changes:
  - Updated the "Current Status" section in `docs/adr/0037-concordance-help-response-request-orchestration-domains.md` so the HelpDomain bullet reflects that Help Hub key/mouse handlers are now thin adapters over `lib/helpDomain.py` (index, search, focusable-items, navigation, filter editing, and activation) under the existing help tests.
  - Updated the RequestLifecycle & HistoryQuery status bullet to note that history drawers and the request-history listing now consume the `historyQuery` façade for labels, bodies, axes, and summary lines, leaving `modelHelpers` migration and duplicate lifecycle/history logic removal as the remaining in-repo work for this domain.
  - Left the AxisDocs and Concordance follow-up bullets unchanged, as axis-canvas cleanup and post-refactor hotspot scans are still outstanding.
- Validation: documentation-only status reconciliation; prior to updating the ADR, re-ran the focused help and history suites (`_tests/test_help_domain.py`, `_tests/test_help_hub.py`, `_tests/test_model_help_gui.py`, `_tests/test_model_help_canvas.py`, `_tests/test_history_query.py`, `_tests/test_request_history_drawer.py`) to confirm a green baseline.
- Follow-ups: future ADR-0037 loops should focus on the remaining AxisDocs canvas cleanup and RequestLifecycle migration for `modelHelpers` under the existing request/history tests.

## 2025-12-10 (loop 33)
- Slice: migrate request history drawer formatting to the HistoryQuery façade (Request lifecycle & history – Phase 2).
- Changes:
  - Removed the local `history_drawer_entries_from` helper from `lib/requestHistoryDrawer.py` so `_refresh_entries` now relies on the imported `historyQuery.history_drawer_entries_from` implementation for `(label, body)` rendering of history entries.
  - This removes a duplicated formatting implementation between `requestHistoryDrawer` and `historyQuery` while keeping `test_request_history_drawer` and `test_history_query` green, so the drawer and façade now share a single source of truth for history drawer labels/bodies.
- Validation: `python3 -m pytest _tests/test_history_query.py _tests/test_request_history_drawer.py`.
- Follow-ups: future RequestLifecycle & HistoryQuery slices can focus on wiring `modelHelpers` onto the RequestLifecycle façade and retiring duplicated lifecycle logic once guarded by the existing request/streaming tests.

## 2025-12-10 (loop 34)
- Slice: confirm AxisDocs façade coverage for response/help canvases (Axis docs & response surfaces – Phase 3 status snapshot).
- Changes:
  - Reviewed `lib/modelResponseCanvas.py` and `lib/modelHelpCanvas.py` to confirm that axis documentation semantics are sourced exclusively via the `AxisDocs` façade (`axis_docs_for` and `_hydrate_axis`/`_axis_keys`), and that remaining axis logic in canvases is limited to layout and token grouping rather than duplicating doc strings.
  - Re-ran the axis/canvas/readme tests (`_tests/test_model_response_canvas.py`, `_tests/test_model_helpers_response_canvas.py`, `_tests/test_axis_overlap_alignment.py`, `_tests/test_readme_axis_lists.py`), which all passed, confirming that canvases, AxisDocs, and README/list alignment remain in sync.
  - Updated the AxisDocs salient task in ADR-0037 to mark the "Remove duplicated axis doc logic from canvases" item as complete, since axis documentation is now single-sourced from `lib/axisConfig.py` and consumed by canvases via the façade.
- Validation: `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_model_helpers_response_canvas.py _tests/test_axis_overlap_alignment.py _tests/test_readme_axis_lists.py`.
- Follow-ups: remaining ADR-0037 work is now concentrated in RequestLifecycle migration (`modelHelpers` and request orchestrators) and Concordance follow-up scans.

## 2025-12-10 (loop 35)
- Slice: re-run churn/heatmap Concordance scans after façade refactors (Concordance follow-up).
- Changes:
  - Ran `python3 scripts/tools/churn-git-log-stat.py` and `python3 scripts/tools/line-churn-heatmap.py` to regenerate `tmp/churn-scan/git-log-stat.txt` and `tmp/churn-scan/line-hotspots.json` over `lib/`, `GPT/`, `copilot/`, and `tests/` for the last 90 days.
  - Reviewed the refreshed `line-hotspots.json` and confirmed that the primary in-scope hotspots for ADR-0037 (AxisDocs/axisConfig, Help Hub/Help GUIs, and RequestLifecycle/history around `modelHelpers`, `requestHistoryActions`, and `requestLog`) remain prominent but are now governed by the new façades and associated tests.
  - Noted that static prompt and axis SSOT nodes (e.g. `staticPromptConfig`, `GPT/gpt.py` static prompt helpers, and `GPT/readme.md`) still appear as hotspots but continue to be governed by ADR-010/ADR-0011/ADR-0036, with this ADR focused on adjacent help/response/request domains.
- Validation: Concordance-only tooling run; no behaviour changes, but ADR-0037 status and Salient Tasks updated to reflect the completed Concordance follow-up scan.
- Follow-ups: future ADR-0037 loops should focus on the remaining RequestLifecycle migration for `modelHelpers` and related orchestrators under the existing request and history tests; additional Concordance scans can be re-run opportunistically after those slices land.

## 2025-12-10 (loop 36)
- Slice: reconcile ADR-0037 Salient Tasks for AxisDocs and HelpDomain with current façade usage (status snapshot).
- Changes:
  - Verified a green baseline for AxisDocs and HelpDomain by running `python3 -m pytest _tests/test_axis_docs.py _tests/test_model_response_canvas.py _tests/test_model_helpers_response_canvas.py _tests/test_help_domain.py _tests/test_help_hub.py _tests/test_model_help_gui.py _tests/test_model_help_canvas.py`.
  - Updated `docs/adr/0037-concordance-help-response-request-orchestration-domains.md` so the top-level Salient Task checkboxes for "AxisDocs façade" and "HelpDomain façade" are now marked as completed (`[x]`), reflecting that all of their sub-tasks (façade introduction, tests, and canvas/Help Hub wiring) are implemented and guarded by tests in this repo.
  - Left the RequestLifecycle & HistoryQuery Salient Tasks unchanged, as the remaining in-repo work (migrating `modelHelpers` onto RequestLifecycle and retiring duplicated lifecycle/history logic) is still outstanding and will require future behaviour-changing slices.
- Validation: documentation-only status reconciliation plus focused AxisDocs/HelpDomain tests (all green); no behavioural code changes in this loop.
- Follow-ups: subsequent ADR-0037 loops should concentrate on the open RequestLifecycle & HistoryQuery bullets and any remaining Concordance hotspots around request orchestration, using the existing request/history test suites as guardrails.

## 2025-12-10 (loop 37)
- Slice: reconcile RequestLifecycle & HistoryQuery Salient Tasks for history drawers with current façade usage (status snapshot).
- Changes:
  - Verified a green baseline for history and request-log behaviour by running `python3 -m pytest _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_request_log.py`.
  - Updated the RequestLifecycle & HistoryQuery Salient Tasks in `docs/adr/0037-concordance-help-response-request-orchestration-domains.md` so the "migrate" bullet is split into two lines: one that tracks remaining migration work for `modelHelpers.send_request`, `_send_request_streaming`, and `_append_text` (still `[ ]`), and a separate line that marks history drawer migration to the HistoryQuery façade as complete (`[x]`).
  - This aligns the ADR task list with the current implementation, where history drawers already consume `historyQuery.history_drawer_entries_from` and related helpers under `_tests/test_history_query.py` and `_tests/test_request_history_drawer.py`.
- Validation: documentation-only status reconciliation plus focused history/log tests (all green); no behavioural code changes in this loop.
- Follow-ups: future ADR-0037 loops should target the remaining RequestLifecycle migration for `modelHelpers` and the removal of duplicated lifecycle logic, using the existing request/streaming and end-to-end tests as guardrails.

## 2025-12-10 (loop 38)
- Slice: integrate RequestLifecycle tracking into `modelHelpers.send_request` and add explicit streaming completion/cancellation lifecycle tests (Request lifecycle & history – Phase 2).
- Changes:
  - Updated `lib/modelHelpers.send_request` to create and update a `RequestLifecycleState` via `reduce_request_state`, recording it on `GPTState.last_lifecycle` as the request moves through logical statuses: `pending` → `running` (on `start`), `streaming` (on `stream_start`), `completed` (on `stream_end`/`complete`), `errored` (on error/max-attempts), and `cancelled` when `CancelledRequest` is raised by the streaming helper.
  - Extended `_tests/test_request_streaming.py` so `test_streaming_accumulates_chunks` asserts that happy-path streaming leaves `GPTState.last_lifecycle.status == "completed"` when the RequestLifecycle façade is available, and split the original cancel test into:
    - `test_streaming_honours_cancel`, which focuses purely on behaviour (empty text result, no sync fallback) under a contrived `current_state(cancel_requested=True)` stub, and
    - `test_streaming_cancelled_sets_lifecycle_cancelled`, which patches `_send_request_streaming` to raise `modelHelpers.CancelledRequest` and asserts that `GPTState.last_lifecycle.status == "cancelled"` for this realistic streaming-cancel path.
  - Re-ran the focused RequestLifecycle/streaming tests (`_tests/test_request_streaming.py`, `_tests/test_request_lifecycle.py`, `_tests/test_request_state.py`, `_tests/test_request_bus.py`), all of which passed, confirming that the new lifecycle integration is consistent with the existing reducer/bus contracts.
- Validation: `python3 -m pytest _tests/test_request_streaming.py _tests/test_request_lifecycle.py _tests/test_request_state.py _tests/test_request_bus.py`.
- Follow-ups: remaining RequestLifecycle work for ADR-0037 is to migrate `_send_request_streaming` and `_append_text` themselves onto the façade (emitting lifecycle events from the streaming loop) and then retire duplicated lifecycle/history logic in `modelHelpers` once the broader `tests/test_request_*` and end-to-end suites (`tests/test_suggestion_coordinator.py`, `tests/test_gpt_actions.py`) are green.

## 2025-12-10 (loop 39)
- Slice: reconcile ADR-0037 Salient Tasks with the partial RequestLifecycle migration for `modelHelpers.send_request` (status snapshot).
- Changes:
  - Verified a green baseline for RequestLifecycle and streaming behaviour by running `python3 -m pytest _tests/test_request_streaming.py _tests/test_request_lifecycle.py _tests/test_request_state.py _tests/test_request_bus.py`.
  - Updated the RequestLifecycle & HistoryQuery Salient Tasks in `docs/adr/0037-concordance-help-response-request-orchestration-domains.md` so the single migration bullet is split into two: one marking `modelHelpers.send_request` as migrated to the RequestLifecycle façade (logical status via `RequestLifecycleState`/`reduce_request_state`), and a second bullet tracking the remaining migration work for `_send_request_streaming` and `_append_text` (still `[ ]`).
  - This aligns the task list with the current implementation: `send_request` now reports a logical lifecycle state while the lower-level streaming and text-append helpers are still to be brought under the façade and de-duplicated.
- Validation: documentation-only status reconciliation plus the focused RequestLifecycle/streaming test run above (all green); no additional behavioural changes in this loop.
- Follow-ups: future ADR-0037 loops should concentrate on migrating `_send_request_streaming`/`_append_text` and then retiring duplicated lifecycle/history logic under the broader `tests/test_request_*`, history, and end-to-end suites.

## 2025-12-10 (loop 40)
- Slice: characterise the core SSE streaming path in `_send_request_streaming` (Request lifecycle & history – Phase 1 tests-first reinforcement).
- Changes:
  - Added a new test `test_streaming_sse_iter_lines_accumulates_chunks` to `_tests/test_request_streaming.py` that patches `modelHelpers.requests.post` to return a `FakeResponse` with `content-type: text/event-stream` and an `iter_lines()` generator yielding two `data: {"choices":[{"delta":{"content": ...}}]}` SSE payloads followed by `data: [DONE]`.
  - The test drives `modelHelpers._send_request_streaming(GPTState.request, "req-sse")` directly under `user.model_streaming=True`, with canvas usage disabled, and asserts that the returned text and `GPTState.text_to_confirm` are both `"Hello world"`, providing explicit coverage for the normal chunk-by-chunk SSE path (as distinct from the non-stream JSON fallback and timeout branches characterised in earlier loops).
  - This complements the existing streaming accumulation, cancellation, JSON-fallback, and timeout tests and strengthens the guardrails around `_send_request_streaming` before any future RequestLifecycle-aware refactors of the streaming loop itself.
- Validation: `python3 -m pytest _tests/test_request_streaming.py` (6 tests, all passing).
- Follow-ups: future RequestLifecycle & HistoryQuery slices can rely on this SSE-characterisation test, together with the existing streaming tests, when migrating `_send_request_streaming` and `_append_text` onto the RequestLifecycle façade and de-duplicating lifecycle/history logic under the broader request suites.

## 2025-12-10 (loop 41)
- Slice: integrate RequestLifecycle tracking into `_send_request_streaming` and reinforce streaming lifecycle tests (Request lifecycle & history – Phase 2).
- Changes:
  - Updated `lib/modelHelpers._send_request_streaming` to initialise a local `RequestLifecycleState` and update it via `reduce_request_state` through a small `_update_lifecycle` helper when streaming starts, ends, errors, or is cancelled. When `GPTState.last_lifecycle` is already present (for example, from `send_request`), the helper treats lifecycle as externally managed and leaves it unchanged; otherwise, it records the evolving lifecycle state on `GPTState.last_lifecycle` for standalone streaming invocations.
  - Hooked lifecycle events into the streaming code paths: the first received chunk and the non-stream JSON fallback both emit `"stream_start"`, normal completion emits `"stream_end"`, error paths (HTTP error, unexpected exception) emit `"error"`, and cancellation paths emit `"cancel"`, aligning `_send_request_streaming` with the RequestLifecycle façade without changing its text/meta buffering behaviour.
  - Extended `_tests/test_request_streaming.py` so the existing non-stream JSON fallback, SSE streaming, and timeout tests assert the expected `GPTState.last_lifecycle.status` values (`"completed"` for happy-path SSE/JSON, `"errored"` for the timeout case) when `RequestLifecycleState` is available, and reset `GPTState.last_lifecycle` in `setUp` to keep tests isolated.
- Validation: `python3 -m pytest _tests/test_request_streaming.py _tests/test_request_lifecycle.py _tests/test_request_state.py _tests/test_request_bus.py`.
- Follow-ups: remaining ADR-0037 RequestLifecycle work is to retire duplicated lifecycle/history logic in `modelHelpers` once the broader `tests/test_request_*`, history, and end-to-end suites remain green.

## 2025-12-10 (loop 42)
- Slice: reconcile ADR-0037 Current Status with RequestLifecycle streaming migration (status snapshot).
- Changes:
  - Updated the RequestLifecycle & HistoryQuery bullet in the "Current Status" section of `docs/adr/0037-concordance-help-response-request-orchestration-domains.md` so it now reflects that `lib/modelHelpers.send_request` and `_send_request_streaming`/`_append_text` all track a logical RequestLifecycle state via the façade, and narrows the remaining work to retiring duplicated lifecycle/history logic under the broader request/history/end-to-end suites.
  - This snapshot brings the narrative status in line with the Salient Tasks checklist and the recent streaming lifecycle integration work recorded in loop 41.
- Validation: documentation-only status reconciliation; no new code changes beyond those already covered by the focused RequestLifecycle/streaming test runs.
- Follow-ups: future ADR-0037 loops should focus on identifying and removing concrete instances of duplicated lifecycle/history logic in `modelHelpers` and related orchestrators, using the existing `tests/test_request_*`, history, and end-to-end suites as guardrails.

## 2025-12-10 (loop 43)
- Slice: deduplicate cancel-handling lifecycle/history logic in `modelHelpers.send_request` (Request lifecycle & history – Phase 3 consolidation).
- Changes:
  - Introduced a small `_handle_cancelled_request()` helper nested inside `lib/modelHelpers.send_request` that centralises the shared cancel path behaviour: calling `emit_fail("cancelled", request_id=request_id)`, notifying "GPT: Request cancelled", cancelling the active request, and returning the formatted empty message via `format_message("")`.
  - Updated both non-streaming cancel branches in `send_request` (the early cancel check before `send_request_internal` and the post-loop `state_after.cancel_requested` check) to delegate to `_handle_cancelled_request()` after performing any lifecycle updates, removing duplicated emit/notify/cancel logic while preserving the existing lifecycle transitions and user-facing messages.
- Validation: `python3 -m pytest _tests/test_request_streaming.py _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_request_async.py _tests/test_request_controller.py _tests/test_request_state.py _tests/test_request_bus.py _tests/test_gpt_actions.py _tests/test_suggestion_coordinator.py` (89 tests, all passing).
- Follow-ups: further ADR-0037 RequestLifecycle slices can continue to fold remaining duplicated lifecycle/history behaviours into façade-backed helpers, but this loop concretely shrinks the "Remove duplicated lifecycle/history logic" task by unifying a pair of historically high-churn cancel paths in `send_request` under tests.

## 2025-12-10 (loop 44)
- Slice: decompose the remaining "Remove duplicated lifecycle/history logic" task into bounded subtasks (Request lifecycle & history – decomposition loop).
- Changes:
  - Updated the RequestLifecycle & HistoryQuery Salient Tasks in `docs/adr/0037-concordance-help-response-request-orchestration-domains.md` to replace the single broad bullet with a small set of explicit subtasks, each naming focus areas and intended helpers:
    - A completed item for deduplicating cancel-handling logic in `modelHelpers.send_request`.
    - Planned items for centralising non-stream error-handling, "max attempts exceeded" handling, streaming error behaviour in `_send_request_streaming`, and history-append semantics behind façade-backed helpers, plus a final "mark retired" step once the relevant request/history/end-to-end tests remain green.
  - This decomposition turns a diffuse, cross-cutting objective into several bounded, test-anchored tasks that future ADR-0037 loops can execute independently without silently redefining the ADR.
- Validation: documentation-only decomposition; no new code changes beyond those already covered by prior RequestLifecycle/request-history test runs.
- Follow-ups: subsequent ADR-0037 loops can now pick individual subtasks (for example, non-stream error-handling or history-append centralisation) and implement them as behaviour-preserving refactors under the existing `tests/test_request_*`, history, and end-to-end suites.

## 2025-12-10 (loop 45)
- Slice: deduplicate non-stream error-handling lifecycle/history logic in `modelHelpers.send_request` (Request lifecycle & history – Phase 3 consolidation).
- Changes:
  - Added a small `_handle_request_error(exc: Exception)` helper nested inside `lib/modelHelpers.send_request` that centralises the non-stream error path behaviour: calling `emit_fail(str(exc), request_id=request_id)`, reducing the RequestLifecycle state to `"error"` via `reduce_request_state`, and updating `GPTState.last_lifecycle` accordingly.
  - Updated both non-stream error branches in the send loop (`except GPTRequestError as e` and the generic `except Exception as e`) to delegate to `_handle_request_error(e)` before re-raising, removing duplicated emit/lifecycle-update logic while preserving existing error semantics and call sites.
- Validation: `python3 -m pytest _tests/test_request_async.py _tests/test_request_controller.py _tests/test_request_state.py _tests/test_request_streaming.py _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_request_bus.py _tests/test_gpt_actions.py _tests/test_suggestion_coordinator.py`.
- Follow-ups: future ADR-0037 loops can apply the same pattern to the remaining subtasks ("max attempts exceeded" handling, streaming error lifecycle behaviour, and history append semantics) until the duplicated lifecycle/history logic task is fully retired under the broader request/history/end-to-end test suites.

## 2025-12-10 (loop 46)
- Slice: centralise "max attempts exceeded" lifecycle/history handling in `modelHelpers.send_request` behind a shared helper (Request lifecycle & history – Phase 3 consolidation).
- Changes:
  - Added a `_handle_max_attempts_exceeded()` helper nested inside `lib/modelHelpers.send_request` that centralises the behaviour for the "no content after max attempts" non-stream path: emitting `emit_fail("max_attempts_exceeded", request_id=request_id)`, reducing the RequestLifecycle state to `"error"` via `reduce_request_state`, updating `GPTState.last_lifecycle`, notifying the user with "GPT request failed after max attempts.", and raising `RuntimeError("GPT request failed after max attempts.")`.
  - Replaced the inline `if message_content is None:` block at the end of the non-stream loop with a call to `_handle_max_attempts_exceeded()`, removing duplicated emit/lifecycle/notify logic while preserving the existing error semantics and call sites.
- Validation: `python3 -m pytest _tests/test_request_async.py _tests/test_request_controller.py _tests/test_request_state.py _tests/test_request_streaming.py _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_request_bus.py _tests/test_gpt_actions.py _tests/test_suggestion_coordinator.py`.
- Follow-ups: future ADR-0037 loops should next target streaming error lifecycle behaviour in `_send_request_streaming` and history-append centralisation, after which the duplicated lifecycle/history logic task can be considered fully retired under the broader request/history/end-to-end test suites.

## 2025-12-10 (loop 47)
- Slice: centralise streaming error lifecycle/history behaviour in `_send_request_streaming` using the RequestLifecycle façade (Request lifecycle & history – Phase 3 consolidation).
- Changes:
  - Added a `_handle_streaming_error(exc: Exception)` helper nested inside `lib/modelHelpers._send_request_streaming` that centralises streaming error behaviour: calling `_update_lifecycle("error")`, emitting `emit_fail(str(exc), request_id=request_id)`, and logging a best-effort debug message.
  - Updated the `requests.post` exception path to delegate to `_handle_streaming_error(...)` for both timeout (wrapping in `GPTRequestError`) and generic exceptions, instead of duplicating lifecycle updates; similarly, updated the generic `except Exception as e` block at the end of the streaming loop to call `_handle_streaming_error(e)` after cancelling/normalising any in-flight cancel states.
- Validation: `python3 -m pytest _tests/test_request_streaming.py _tests/test_request_lifecycle.py _tests/test_request_state.py _tests/test_request_bus.py`.
- Follow-ups: future ADR-0037 loops should now focus on centralising history append semantics behind façade-backed helpers and, once that is complete and the broader request/history/end-to-end test suites remain green, marking the duplicated lifecycle/history logic task as retired for this repo.

## 2025-12-10 (loop 48)
- Slice: centralise history append semantics for completed requests behind a `requestLog` helper (Request lifecycle & history – Phase 3 consolidation).
- Changes:
  - Added `append_entry_from_request` in `lib/requestLog.py` as a small helper that extracts the first user-message text payload from a ChatGPT-style request dict, defensively clones the provided axes dict, and delegates to `append_entry`, returning the computed prompt text.
  - Updated `lib/modelHelpers.send_request` so the non-stream completion path calls `append_entry_from_request` with `GPTState.request`, `answer_text`, `meta_text`, `last_recipe`, timing, and `GPTState.last_axes`, removing the inline prompt/axes extraction logic while keeping request-history drawers and listings (via `historyQuery`) consuming the same history entries.
  - Extended `_tests/test_request_log.py` with `test_append_entry_from_request_uses_request_structure` to characterise the new helper’s behaviour, including prompt extraction, field wiring, and defensive copying of the axes dict.
- Validation: `python3 -m pytest _tests/test_request_log.py _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_gpt_actions.py _tests/test_suggestion_coordinator.py`.
- Follow-ups: a future ADR-0037 loop should run the broader `tests/test_request_*` and `tests/test_request_history_*` suites alongside `tests/test_suggestion_coordinator.py` and `tests/test_gpt_actions.py`, and, if they remain green, mark the final "duplicated lifecycle/history logic" Salient Task as retired for this repo.

## 2025-12-10 (loop 49)
- Slice: retire duplicated RequestLifecycle/history logic for `modelHelpers` under full request/history test suites (status reconciliation).
- Changes:
  - Fixed `_send_request_streaming`'s timeout branch in `lib/modelHelpers.py` to wrap the timeout in a `GPTRequestError(408, ...)`, call `_handle_streaming_error(err)` for lifecycle/fail emission, and re-raise `err`, restoring the original user-visible error type while keeping the centralised streaming error helper.
  - Ran the broader request and history-related tests for ADR-0037: `python3 -m pytest _tests/test_request_streaming.py` followed by `python3 -m pytest _tests/test_request_*.py _tests/test_request_history_*.py _tests/test_suggestion_coordinator.py _tests/test_gpt_actions.py`, all of which passed, confirming that `modelHelpers.send_request`/`_send_request_streaming` and history surfaces behave correctly under the RequestLifecycle & HistoryQuery façades.
  - Updated the RequestLifecycle & HistoryQuery Salient Tasks in `docs/adr/0037-concordance-help-response-request-orchestration-domains.md` to mark the final bullet ("mark duplicated lifecycle/history logic as retired for this repo") as completed, reflecting that the ADR-0037 request/history objectives are now fully implemented and test-backed in this repo.
- Validation: `python3 -m pytest _tests/test_request_streaming.py` and `python3 -m pytest _tests/test_request_*.py _tests/test_request_history_*.py _tests/test_suggestion_coordinator.py _tests/test_gpt_actions.py`.
- Follow-ups: future ADR-0037 loops, if any, should focus on higher-level Concordance monitoring or cross-ADR alignment rather than additional RequestLifecycle/history refactors, since B_a for this domain is now effectively 0 in this repo.
