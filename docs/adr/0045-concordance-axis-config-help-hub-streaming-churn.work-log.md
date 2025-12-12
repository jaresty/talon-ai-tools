# ADR-0045 – Work Log

## 2025-12-11 – Axis & Static Prompt Concordance slice

Focus (kind: guardrail/tests): Implement a guardrail and characterisation tests for the **Axis & Static Prompt Concordance** domain to ensure static prompt profiles stay aligned with axis configuration.

### Changes
- Added `_tests/test_static_prompt_axis_tokens.py` with `StaticPromptAxisTokenTests`:
  - `test_profiled_prompt_axes_use_valid_axis_tokens` exercises `static_prompt_catalog()` and `AXIS_KEY_TO_VALUE` together.
  - For each profiled static prompt, the test asserts that any configured `scope`, `method`, `style`, or `directional` axis tokens are valid keys in `axisConfig.AXIS_KEY_TO_VALUE`.
- Left existing `_tests/test_static_prompt_docs.py`, `_tests/test_talon_settings_model_prompt.py`, and `_tests/test_readme_axis_lists.py` unchanged, but ran them as part of this loop to confirm they remain green alongside the new guardrail.

### Rationale
- This slice makes the implicit contract in ADR-0045 explicit for a subset of axes: when static prompt profiles specify `scope`, `method`, `style`, or `directional` hints, those hints must come from the canonical axis token sets defined in `axisConfig`.
- By implementing this as a separate test module rather than modifying existing tests, we reduce the risk of unintended regressions while still strengthening Concordance guardrails.

### Checks
- Ran focused tests:
  - `python3 -m pytest _tests/test_static_prompt_docs.py _tests/test_static_prompt_axis_tokens.py _tests/test_talon_settings_model_prompt.py _tests/test_readme_axis_lists.py`
  - Result: **35 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work
- Completeness hints in static prompt profiles currently include values (for example, `"path"` on the `"bridge"` profile) that are not present in `axisConfig.AXIS_KEY_TO_VALUE["completeness"]`.
  - This loop intentionally scoped the new guardrail to `scope`, `method`, `style`, and `directional` axes only.
  - A later slice should decide whether to:
    - Bring completeness hints fully under `axisConfig` (adding tokens and doc surface coverage), or
    - Treat some completeness values as free-form hints and document that exception in ADR-0045.
- ADR-0045 still calls for:
  - Introducing or tightening a catalog/facade API that unifies axis/static prompt semantics for docs, help, and Talon settings.
  - Extending help surfaces and Talon settings to consume that API.
  - Further characterisation tests once those facades are in place.

## 2025-12-11 – Axis & Static Prompt Concordance slice – modelPrompt/catalog guardrail

Focus (kind: guardrail/tests): Ensure `modelPrompt` respects static prompt profile axes so that the Axis & Static Prompt domain behaves consistently across config, catalog, and system prompt state.

### Changes
- Updated `_tests/test_talon_settings_model_prompt.py`:
  - Imported `STATIC_PROMPT_CONFIG` and `get_static_prompt_axes` from `staticPromptConfig`.
  - Added `test_profile_axes_are_propagated_to_system_prompt`:
    - Iterates over every profiled static prompt in `STATIC_PROMPT_CONFIG`.
    - Uses `get_static_prompt_axes(name)` to obtain configured axes.
    - For prompts that define any of `scope`, `method`, or `style` in their profile, calls `modelPrompt` with only `staticPrompt=name` and a directional modifier.
    - Asserts that for each configured `scope`/`method`/`style` token, the token appears in `GPTState.last_axes[axis]` after the call (subject to the usual axisConfig filtering and hierarchy rules).

### Rationale
- This slice connects the static prompt catalog/profile layer (`staticPromptConfig`) to the runtime system axes managed by `modelPrompt`:
  - When a static prompt profile declares scoped/method/style tokens, those tokens must be visible in `GPTState.last_axes` when no spoken modifiers override them.
  - This strengthens the Axis & Static Prompt Concordance domain by ensuring that profile configuration, catalog views, and system prompt axes stay aligned.

### Checks
- Ran focused tests:
  - `python3 -m pytest _tests/test_talon_settings_model_prompt.py`
  - Result: **23 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (axis/static domain)
- Decide how to handle completeness hints like `"path"` in profiles relative to axisConfig tokens.
- Extend this guardrail further once a shared catalog/facade API is the primary entrypoint for docs and help surfaces (for example, by asserting that doc/help consumption of the catalog also matches `GPTState.last_axes` for a sample of prompts).

## 2025-12-11 – Streaming Response & Snapshot slice

Focus (kind: guardrail/tests): Characterise happy-path source snapshot behaviour for the **Streaming Response & Snapshot Resilience** domain and ensure saved source files include Concordance-relevant axis/static-prompt context.

### Changes
- Added `_tests/test_gpt_source_snapshot.py` with `SourceSnapshotTests`:
  - `test_save_source_snapshot_writes_markdown_with_header_and_body` exercises `GPT/gpt.py::_save_source_snapshot_to_file` via the Talon harness.
  - Seeds `GPTState.last_source_messages` with formatted text messages so the helper uses them instead of the default source.
  - Patches `gpt.last_recipe_snapshot` to a minimal snapshot containing:
    - `static_prompt`, `recipe`, `completeness`, `scope_tokens`, `method_tokens`, `style_tokens`, and `directional`.
  - Asserts that the helper writes a markdown file into the configured `user.model_source_save_directory` with:
    - A header block containing `saved_at`, `recipe`, `completeness`, `scope_tokens`, `method_tokens`, `style_tokens`, and `directional` fields.
    - A body section starting with `# Source` that includes the rendered source lines.

### Rationale
- This slice turns the implicit contract for source snapshots in ADR-0045 into an executable characterisation:
  - When `_save_source_snapshot_to_file` runs on a populated snapshot, the resulting file must carry enough axis/static-prompt context in its header to be Concordance-friendly and self-describing.
  - By working through the existing helper rather than introducing a new façade yet, we reduce risk while clarifying expected behaviour for future refactors.

### Checks
- Ran focused streaming/snapshot-related tests:
  - `python3 -m pytest _tests/test_model_destination.py _tests/test_gpt_source_snapshot.py _tests/test_request_streaming.py _tests/test_request_log.py _tests/test_request_history_actions.py`
  - Result: **30 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (streaming/snapshot domain)
- Introduce a small streaming/snapshot façade as described in ADR-0045 that:
  - Wraps `_save_source_snapshot_to_file` and related logging/history calls behind a clearer API.
  - Makes streaming accumulation and error-handling policies more explicit.
- Extend tests to cover:
  - Error scenarios and partial responses that still write or skip snapshots appropriately.
  - Coordination between snapshot headers and request history/log entries.

## 2025-12-11 – Help Navigation & Quick-Help status slice

Focus (kind: status): Confirm the **Help Navigation & Quick-Help** domain is already using a façade-style navigation contract and record its status relative to ADR-0045.

### Observations
- `lib/helpHub.py` delegates search and focus/navigation behaviour to the `helpDomain` façade via:
  - `build_search_index` → `help_index` for constructing logical index entries.
  - `search_results_for` → `help_search` for label-based search.
  - `focusable_items_for` → `help_focusable_items` for ordered (kind,label) focus targets.
  - `_next_focus_label` → `help_next_focus_label` for stepping focus.
  - `_activate_focus` → `help_activation_target` for resolving which handler to invoke.
- `_tests/test_help_hub.py` already characterises this façade:
  - `test_help_hub_next_focus_label_wraps_and_steps` exercises `_next_focus_label`.
  - `test_focusable_items_for_*` and `test_help_hub_search_results_for_is_pure_and_label_based` exercise the pure navigation and search helpers.
- `lib/modelHelpCanvas.py` provides a separate quick-help surface for axis/static-prompt docs, with its own state (`HelpGUIState`, `HelpCanvasState`) and key/canvas handlers, but does not currently need to share the hub’s keyboard focus contract.

### Decision for this slice
- Treat the Help Hub keyboard/mouse navigation as already façade-backed for the purposes of ADR-0045’s Help Navigation & Quick-Help domain.
- Defer any deeper unification between Help Hub and quick-help navigation to a future loop that:
  - Either introduces a small shared navigation helper reused by both, or
  - Confirms that keeping them separate (hub vs. focused quick-help) is the right boundary and records that explicitly in ADR-0045.

### Checks
- No new behaviour was introduced in this slice; existing `_tests/test_help_hub.py` and `_tests/test_model_help_canvas.py` continue to cover Help Hub and quick-help behaviour.

### Follow-ups / Remaining ADR-0045 work (help navigation domain)
- Consider a future slice that:
  - Documents or slightly tightens the contract between hub navigation and quick-help actions (for example, how “Quick help” in the hub maps to sections in the quick-help canvas).
  - Adds a small façade helper if we decide both surfaces should share a single navigation state model.

## 2025-12-11 – Current status snapshot

Focus (kind: status): Summarise ADR-0045’s in-repo progress and remaining work across all four domains in this repo.

### Summary
- Axis & Static Prompt domain:
  - Guardrail tests now enforce that profiled static prompt axes stay aligned with `axisConfig` tokens for scope/method/style/directional.
  - `modelPrompt` is covered by a new guardrail test that ensures profile axes from `staticPromptConfig` are reflected in `GPTState.last_axes` when no spoken modifiers override them.
- Streaming Response & Snapshot domain:
  - Happy-path source snapshot behaviour is characterised and guarded by tests; behaviour remains unchanged but now has executable documentation.
- Help Navigation & Quick-Help domain:
  - Help Hub navigation is already façade-backed via `helpDomain` helpers, with tests characterising focus and search behaviour.
- Pattern Debug & GPT Action orchestration domain:
  - Existing tests cover pattern recipes, axes, and pattern selection behaviour, but there is no dedicated pattern debug coordinator yet; `_debug` remains a light logging helper rather than a structured inspection API.

### Follow-ups
- Remaining ADR-0045 work primarily concerns introducing the pattern debug coordinator and the streaming/snapshot façade, and deciding how strongly to unify Help Hub and quick-help navigation.

## 2025-12-11 – Streaming Response & Snapshot slice – File destination axes snapshot

Focus (kind: guardrail/tests): Characterise the File model destination’s response snapshot behaviour so it stays aligned with ADR-0045’s Streaming Response & Snapshot Resilience domain and with the axis/recipe state used by history and canvas surfaces.

### Changes
- Extended `_tests/test_model_destination.py` with `test_file_destination_header_and_slug_use_last_axes_tokens`:
  - Seeds `GPTState.last_axes` with completeness/scope/method/style tokens and conflicting legacy `last_*` strings.
  - Writes a response snapshot via the `File` model destination and asserts that:
    - The filename slug reflects `last_axes` tokens and static prompt (for example, `infer-full-bound-edges-rigor-plain`) rather than legacy `last_*` fields.
    - The markdown header includes `completeness_tokens`, `scope_tokens`, `method_tokens`, and `style_tokens` derived from `last_axes`.

### Rationale
- This slice tightens the Streaming Response & Snapshot domain guardrails around on-disk response snapshots:
  - Ensures the File destination’s snapshot files carry the same axis/recipe view of a response as history and canvas surfaces, using `last_axes` as the primary source of truth when available.
  - Provides executable documentation for how axis tokens shape both the filename slug and header fields, reducing the risk of future changes silently drifting from ADR-0045’s intent.

### Checks
- Ran focused tests:
  - `python3 -m pytest _tests/test_model_destination.py _tests/test_gpt_source_snapshot.py`
  - Result: **9 passed**, 0 failed.

## 2025-12-11 – Pattern Debug & GPT Action slice – async/meta notification guardrails

Focus (kind: guardrail/tests): Strengthen tests around GPT actions that surface async-blocking state and meta interpretations so they accurately reflect the `actions.app.notify` contract and keep this high-churn area green.

### Changes
- Updated `_tests/test_gpt_actions.py`:
  - `test_gpt_show_last_meta_notifies_when_present` and `test_gpt_show_last_meta_notifies_when_missing` now patch `actions.app.notify` directly and assert:
    - A single notification is sent, and
    - The message includes either `"Last meta interpretation:"` or `"No last meta interpretation available"` as appropriate.
  - `test_gpt_set_async_blocking_sets_setting_and_notifies` now patches `actions.app.notify` and asserts:
    - `user.model_async_blocking` is set truthy, and
    - The notification message contains `"async mode set to"`.

### Rationale
- These tests previously relied on the Talon stub’s internal `actions.app.calls` recording, which breaks when `actions.app.notify` is patched with a `MagicMock`.
- By asserting against the patched `actions.app.notify` call arguments instead, the tests:
  - More directly guard the intended notification behaviour of GPT actions, and
  - Remove brittle coupling to stub internals while keeping the `test_gpt_actions.py` hotspot fully green for ADR-0045’s Pattern Debug & GPT Action domain.

### Checks
- Ran focused GPT actions tests:
  - `python3 -m pytest _tests/test_gpt_actions.py`
  - Result: **51 passed**, 0 failed.

## 2025-12-11 – Streaming Response & Snapshot slice – source snapshot slug and header

Focus (kind: guardrail/tests): Further characterise `_save_source_snapshot_to_file` so saved source files encode both source type and static prompt/axes context in their filename slug and header, matching ADR-0045’s Streaming Response & Snapshot domain intent.

### Changes
- Extended `_tests/test_gpt_source_snapshot.py` with `test_save_source_snapshot_slug_includes_source_type_and_static_prompt`:
  - Seeds `GPTState.last_source_messages` and `GPTState.last_source_key = "clipboard"` so the helper uses the cached source and records a `source_type`.
  - Patches `gpt.last_recipe_snapshot` to a minimal snapshot containing `static_prompt`, `recipe`, `completeness`, `scope_tokens`, `method_tokens`, `style_tokens`, and `directional`.
  - Asserts that:
    - The resulting filename slug includes both the source type and static prompt tokens (for example, `clipboard` and `infer`).
    - The markdown header records `source_type: clipboard` alongside the same axis/recipe fields as the existing header/body test.

### Rationale
- This slice tightens the Streaming Response & Snapshot domain guardrails by:
  - Making the filename/header contract for source snapshots explicit and executable.
  - Ensuring downstream tools (and humans) can infer both source and axis/static-prompt context from saved source files without opening the body.

### Checks
- Ran focused streaming/snapshot and related tests:
  - `python3 -m pytest _tests/test_gpt_source_snapshot.py _tests/test_model_destination.py _tests/test_gpt_actions.py`
  - Result: **61 passed**, 0 failed.

## 2025-12-11 – Axis & Static Prompt Concordance slice – usage mapping

Focus (kind: status): Map where `axisConfig`, `axisMappings`, `staticPromptConfig`, and `static_prompt_catalog` are actually consumed across libs, GUIs, tests, Talon lists, and docs, as groundwork for the catalog/facade work in ADR-0045.

### Observations
- `axisConfig` (SSOT for axis tokens/docs):
  - Configuration/docs: `lib/axisConfig.py` (AxisDocs façade per ADR-0037/0034).
  - Mappings façade: `lib/axisMappings.py` imports from `axisConfig` and re-exports mappings.
  - Canvases: `lib/modelResponseCanvas.py` and `lib/modelHelpCanvas.py` import `axis_docs_for` to render axis docs in response/help canvases.
  - Settings: `lib/talonSettings.py` filters axis tokens against `axisConfig` when ingesting settings, keeping token-only state.
  - Tests/docs: `_tests/test_axis_docs.py`, `_tests/test_axis_mapping.py`, `_tests/test_static_prompt_axis_tokens.py`, plus ADR-0034/0037 work-logs treat `axisConfig` as SSOT and check Talon list parity.

- `staticPromptConfig` (SSOT for static prompt profiles):
  - Core config: `lib/staticPromptConfig.py` defines `STATIC_PROMPT_CONFIG`, `StaticPromptProfile`, and façade helpers (`get_static_prompt_profile`, `get_static_prompt_axes`, `static_prompt_catalog`).
  - GPT runtime: `GPT/gpt.py` imports `STATIC_PROMPT_CONFIG` and helpers for static prompt docs and catalog consumption.
  - GUIs/settings: `lib/modelPromptPatternGUI.py`, `lib/modelHelpCanvas.py`, and `lib/talonSettings.py` import `get_static_prompt_axes` / `get_static_prompt_profile` to drive pattern GUIs, quick-help, and Talon model settings.
  - Tests/docs: `_tests/test_static_prompt_config.py`, `_tests/test_static_prompt_docs.py`, `_tests/test_talon_settings_model_prompt.py`, `_tests/test_model_pattern_gui.py`, ADR-0011/0012/0014/0018/0026 all treat `staticPromptConfig` as the static prompt/axis façade.

- `static_prompt_catalog` (catalog façade over static prompts):
  - Definition: `lib/staticPromptConfig.static_prompt_catalog` builds a structured catalog (`profiled`, `talon_list_tokens`, `unprofiled_tokens`).
  - GPT/docs: `GPT/gpt.py::static_prompt_catalog` re-exports/consumes the catalog for GPT help/docs surfaces.
  - Tests: `_tests/test_static_prompt_docs.py`, `_tests/test_static_prompt_axis_tokens.py`, `_tests/test_static_prompt_catalog_consistency.py` exercise catalog shape, token/profile alignment, and Talon list coverage.
  - ADRs: ADR-0036 and ADR-0045 both call out `static_prompt_catalog` as the shared façade for docs/help/Talon settings.

### Consequences for ADR-0045
- Confirms that axis semantics (`axisConfig`/`axisMappings`) and static prompt semantics (`staticPromptConfig` + `static_prompt_catalog`) already have façade-style entrypoints that are widely consumed.
- Makes it clearer where the planned "small catalog/facade API" in ADR-0045 should be centred (primarily `staticPromptConfig.static_prompt_catalog`, with `axisConfig`/AxisDocs as the axis side), and which consumers (GPT docs/help, Talon settings, pattern GUIs) will need tightening in future slices.

## 2025-12-11 – Axis & Static Prompt Concordance slice – static prompt docs/README facade

Focus (kind: behaviour): Tighten the Axis & Static Prompt domain by introducing a docs/README-facing facade over static prompt descriptions instead of having GPT helpers read `STATIC_PROMPT_CONFIG` directly.

### Changes
- Extended `lib/staticPromptConfig.py` with `static_prompt_description_overrides()`:
  - Returns a `dict[str, str]` mapping static prompt names to their descriptions.
  - Uses `STATIC_PROMPT_CONFIG` as the single source of truth and trims empty/whitespace-only descriptions.
- Updated `GPT/gpt.py` to depend on this facade when building the README static prompt tables:
  - In the normal path, `_build_static_prompt_docs` continues to use `static_prompt_catalog()` (unchanged).
  - In the README helper section that renders "Static Prompts" via `render_list_as_tables`, the `description_overrides` argument now calls `static_prompt_description_overrides()` instead of rebuilding a dict from `STATIC_PROMPT_CONFIG` inline.
- Added a fallback `static_prompt_description_overrides()` implementation in `GPT/gpt.py`'s ImportError block so older Talon runtimes without the new helper still see consistent descriptions.

### Rationale
- This slice moves a previously inline README/docs concern (description overrides derived from `STATIC_PROMPT_CONFIG`) into the Axis & Static Prompt domain itself:
  - GPT helpers and any future docs/help surfaces now obtain static prompt descriptions through a small, named facade rather than reaching directly into the config dict.
  - This aligns with ADR-0045's goal of consolidating configuration semantics behind clear entrypoints while leaving tests and runtime behaviour unchanged.

### Checks
- Ran focused Axis & Static Prompt docs and catalog tests:
  - `python3 -m pytest _tests/test_static_prompt_docs.py _tests/test_static_prompt_catalog_consistency.py _tests/test_readme_axis_lists.py`
  - Result: **15 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (axis/static domain)
- As additional docs or help surfaces are introduced, prefer using `static_prompt_description_overrides()` and `static_prompt_catalog()` rather than direct `STATIC_PROMPT_CONFIG` access so description and profile semantics stay centralised.
- When implementing a broader Axis & Static Prompt facade for Talon settings and GUIs, reuse these helpers and extend tests to characterise cross-surface behaviour.

## 2025-12-11 – Axis & Static Prompt Concordance slice – catalog/status confirmation

## 2025-12-11 – Axis & Static Prompt Concordance slice – settings/catalog facade helper

## 2025-12-11 – Axis & Static Prompt Concordance slice – salient tasks reconciliation

Focus (kind: status): Reconcile ADR-0045’s Axis & Static Prompt Salient Tasks with the existing catalog/description/settings facades and usage-mapping work so remaining tasks focus on adoption and cross-surface consistency rather than introducing APIs from scratch.

### Changes
- Reviewed ADR-0045’s Axis & Static Prompt Salient Tasks against the work-log:
  - Usage mapping across `axisConfig`, `axisMappings`, `staticPromptConfig`, and `static_prompt_catalog` is already captured in the "usage mapping" slice.
  - Catalog/description/helpers (`static_prompt_catalog`, `static_prompt_description_overrides`, and the new `static_prompt_settings_catalog`) are implemented and guarded by tests.
- Updated the Salient Tasks in `docs/adr/0045-concordance-axis-config-help-hub-streaming-churn.md` so that Axis & Static Prompt items now reflect this state:
  - Marked the "Map current uses..." task as completed.
  - Marked the "Introduce or tighten a small catalog/facade API..." task as completed for this repo (via the existing helpers), and narrowed the remaining work to adoption and cross-surface tests.

### Rationale
- This slice prevents future loops from treating already-implemented facades and mapping work as open tasks, keeping `B_a` for the Axis & Static Prompt domain accurate.
- It also clarifies that remaining work in this repo is about:
  - Adopting the shared facades in Talon settings and GUI/help surfaces where appropriate, and
  - Adding or tightening cross-surface behaviour tests, rather than inventing new catalog APIs.


Focus (kind: behaviour): Introduce a small, settings/docs-friendly static prompt catalog facade so Talon settings and help surfaces can consume a single, typed mapping of static prompt descriptions and axes built on top of the existing catalog/profile helpers.

### Changes
- Updated `lib/staticPromptConfig.py`:
  - Added `StaticPromptSettingsEntry` TypedDict describing a settings-facing entry with:
    - `description: str`
    - `axes: dict[str, object]`
  - Added `static_prompt_settings_catalog() -> dict[str, StaticPromptSettingsEntry]`:
    - Calls `static_prompt_catalog()` to obtain the existing profiled entries.
    - Builds and returns a dict mapping each profiled static prompt name to:
      - `description`: the trimmed description field from the catalog entry.
      - `axes`: the axis profile from the catalog entry (as returned by `get_static_prompt_axes`).
- Extended `_tests/test_static_prompt_config.py`:
  - Imported `static_prompt_settings_catalog` from `talon_user.lib.staticPromptConfig`.
  - Added `test_static_prompt_settings_catalog_matches_profiles`:
    - Calls `static_prompt_settings_catalog()` and, for each `(name, profile)` in `STATIC_PROMPT_CONFIG.items()`, asserts:
      - `name` is present in the catalog mapping.
      - The catalog entry’s description equals `profile.get("description", "").strip()`.
      - The catalog entry’s axes equal `get_static_prompt_axes(name)`.

### Rationale
- This slice advances ADR-0045’s Axis & Static Prompt Concordance plan for a small catalog/facade API by:
  - Providing a concrete, settings/docs-friendly mapping that reuses `static_prompt_catalog` and `get_static_prompt_axes` rather than re-reading `STATIC_PROMPT_CONFIG` directly.
  - Giving Talon settings and help GUIs a narrow, typed entrypoint for static prompt description + axis semantics without having to understand the full catalog structure or the Talon list tokens.
- It complements the existing `static_prompt_description_overrides()` and `static_prompt_catalog()` helpers without changing any existing behaviour.

### Checks
- Ran focused static prompt config tests:
  - `python3 -m pytest _tests/test_static_prompt_config.py`
  - Result: **8 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (axis/static domain)
- Future slices may:
  - Adopt `static_prompt_settings_catalog()` in Talon settings or GUI modules (for example, `talonSettings` or quick-help views) to reduce duplication and keep semantics centralised.
  - Extend tests around any new consumers to assert that settings/help surfaces reflect both descriptions and axis profiles as exposed by this facade.


Focus (kind: guardrail/tests): Confirm that current axis/static prompt catalog guardrails and docs/tests remain green after recent ADR-0045 work and record the resulting status.

### Changes
- Re-ran core Axis & Static Prompt tests that exercise the catalog and its consumers:
  - `_tests/test_static_prompt_catalog_consistency.py`
  - `_tests/test_static_prompt_docs.py`
  - `_tests/test_talon_settings_model_prompt.py`
  - `_tests/test_readme_axis_lists.py`
- No code or configuration changes were required; existing guardrails and catalog behaviour already satisfy ADR-0045’s current Axis & Static Prompt objectives for this repo.

### Checks
- `python3 -m pytest _tests/test_static_prompt_catalog_consistency.py _tests/test_static_prompt_docs.py _tests/test_talon_settings_model_prompt.py _tests/test_readme_axis_lists.py`
- Result: **38 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (axis/static domain)
- When introducing the planned small catalog/facade API, ensure it:
  - Continues to satisfy these tests without weakening guardrails.
  - Provides a narrow, documented entrypoint for docs/help/Talon settings that keeps axis and static prompt semantics in sync.

## 2025-12-11 – Streaming Response & Snapshot slice – streaming status confirmation

Focus (kind: status): Confirm current streaming request, response canvas, and snapshot behaviours against ADR-0045’s Streaming Response & Snapshot Resilience domain, using existing characterisation tests.

### Observations
- `lib/modelHelpers._send_request_streaming` and `send_request` are already covered by `_tests/test_request_streaming.py`:
  - `test_streaming_accumulates_chunks` guards the happy-path streaming branch and RequestLifecycle `completed` status.
  - `test_streaming_honours_cancel` and `test_streaming_cancelled_sets_lifecycle_cancelled` guard cancellation paths and ensure lifecycle status is `cancelled` with empty text.
  - `test_streaming_falls_back_to_non_stream_json_response` and `test_streaming_sse_iter_lines_accumulates_chunks` characterise the JSON and SSE streaming paths, including `GPTState.text_to_confirm` updates.
  - `test_streaming_timeout_raises_gpt_request_error` characterises timeout handling, ensuring a `GPTRequestError` with status code 408 and lifecycle status `errored`.
- `lib/modelResponseCanvas` is covered by `_tests/test_model_response_canvas.py`:
  - Tests exercise open/toggle semantics, inflight progress handling, scroll behaviour, and footer button actions (including paste/close ordering).
- Snapshot-related behaviours remain guarded by existing tests in `_tests/test_model_destination.py` and `_tests/test_gpt_source_snapshot.py`.

### Checks
- Ran focused streaming and snapshot tests:
  - `python3 -m pytest _tests/test_request_streaming.py _tests/test_model_response_canvas.py _tests/test_model_destination.py _tests/test_gpt_source_snapshot.py`
  - Result: **22 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (streaming/snapshot domain)
- Future behaviour slices can build on these characterisations by:
  - Introducing a small streaming/snapshot façade that wraps `_send_request_streaming`, response canvas updates, and snapshot/log writes behind explicit policies, while keeping these tests green.
  - Adding targeted tests for additional error modes (for example, partial SSE payloads that still produce a usable body) once a façade exists.

## 2025-12-11 – Help Navigation & Quick-Help slice – close-before-open navigation guardrail

Focus (kind: behaviour): Tighten the Help Navigation & Quick-Help domain so that Help Hub buttons which open other overlays close the hub first, avoiding stacked UIs and making navigation flow clearer.

### Changes
- Updated `lib/helpHub.py`:
  - Introduced `_navigate_and_close(handler: Callable[[], None]) -> Callable[[], None]`, which:
    - Calls `help_hub_close()` inside a try/except, then invokes the provided handler, also in a best-effort try/except.
    - Provides a small, named hook for navigation actions that should close the hub before opening another surface.
  - Wired the main navigation buttons to use this helper:
    - "Quick help" → closes Help Hub, then calls `actions.user.model_help_canvas_open()`.
    - "Patterns" → closes Hub, then `actions.user.model_pattern_gui_open()`.
    - "Prompt pattern menu" → closes Hub, then `_open_prompt_pattern_menu()` (or falls back to quick help inside that helper).
    - "Suggestions" → closes Hub, then `actions.user.model_prompt_recipe_suggestions_gui_open()`.
    - "History" → closes Hub, then `actions.user.request_history_drawer_toggle()`.
    - "HTML docs" → closes Hub, then `actions.user.gpt_help()`.
  - Buttons that only copy data (`"ADR links"`, `"Copy cheat sheet"`) and the explicit "Close" button keep their existing behaviour so the hub can remain open when appropriate.
- Extended `_tests/test_help_hub.py` with `test_help_hub_quick_help_closes_hub_before_open`:
  - Opens Help Hub, asserts `HelpHubState.showing is True`.
  - Monkeypatches `actions.user.model_help_canvas_open` with a wrapper that:
    - Appends a marker to a local `calls` list.
    - Asserts `HelpHubState.showing is False` at the moment Quick help opens.
    - Delegates to the original handler.
  - Invokes `help_hub.help_hub_test_click("Quick help")` and asserts the wrapper was called exactly once.

### Rationale
- This slice makes the Help Navigation & Quick-Help domain’s intent around overlays more explicit:
  - Opening Quick help, patterns, history, or docs from Help Hub is now a transfer of focus (Hub → target overlay) rather than stacking multiple canvases.
  - The `_navigate_and_close` helper provides a small, reusable façade for this behaviour, and the new test encodes the close-before-open contract for Quick help.
  - This aligns with ADR-0045’s goal of absorbing help-related churn into a small, well-tested navigation surface.

### Checks
- Ran focused help-related tests:
  - `python3 -m pytest _tests/test_help_hub.py _tests/test_model_help_canvas.py`
  - Result: **19 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (help navigation domain)
- Consider applying similar close-before-open semantics to any future Help Hub actions that open additional canvases or windows.
- In a later slice, decide whether quick-help navigation itself should share a small navigation façade with Help Hub (for example, a shared navigation state or helper for focus movement) and extend tests accordingly.

## 2025-12-11 – Pattern Debug & GPT Action slice – pattern debug snapshot helper

Focus (kind: behaviour): Introduce a small pattern debug snapshot helper as a first coordinator for the Pattern Debug & GPT Action domain, exposing structured pattern configuration and current GPTState axes for inspection.

### Changes
- Updated `lib/modelPatternGUI.py`:
  - Added `pattern_debug_snapshot(pattern_name: str) -> dict[str, object]`:
    - Locates the corresponding `PromptPattern` in `PATTERNS` by case-insensitive name; returns `{}` when no match is found.
    - Uses the existing `_parse_recipe` helper to derive:
      - `static_prompt`, `completeness`, `scope`, `method`, `style`, `directional`.
    - Builds an `axes` payload:

      ```python
      axes = {
          "completeness": completeness,
          "scope": scope.split() if scope else [],
          "method": method.split() if method else [],
          "style": style.split() if style else [],
          "directional": directional,
      }
      ```

    - Returns a snapshot dict containing:

      ```python
      {
          "name": pattern.name,
          "domain": pattern.domain,
          "description": pattern.description,
          "recipe": pattern.recipe,
          "static_prompt": static_prompt,
          "axes": axes,
          "last_recipe": GPTState.last_recipe (if available),
          "last_axes": GPTState.last_axes (if a dict, optional),
      }
      ```

    - Leaves `_run_pattern` behaviour unchanged, so existing pattern execution continues to be the single writer of `GPTState.last_*` and `GPTState.last_axes`.
- Extended `_tests/test_model_pattern_gui.py`:
  - Imports `pattern_debug_snapshot` from `talon_user.lib.modelPatternGUI`.
  - Added `test_pattern_debug_snapshot_includes_axes_and_state`:
    - Picks the `"Debug bug"` pattern from `PATTERNS`.
    - Seeds `GPTState.last_recipe = "unit-test-recipe"` and `GPTState.last_axes` with a simple axis dict.
    - Calls `snapshot = pattern_debug_snapshot(target.name)` and asserts:
      - Core metadata fields (`name`, `domain`, `description`, `recipe`, `static_prompt`) match the pattern and recipe.
      - `snapshot["axes"]` encodes `completeness="full"`, `scope=["narrow"]`, `method=["debugging"]`, `style=[]`, `directional="rog"` for this pattern.
      - `snapshot["last_recipe"] == "unit-test-recipe"` and `snapshot["last_axes"] == GPTState.last_axes`.
  - Added `test_pattern_debug_snapshot_unknown_pattern_returns_empty_dict`:
    - Asserts that an unknown pattern name returns `{}`.

### Rationale
- This slice introduces a minimal, test-backed coordinator for pattern debug information without changing how patterns run:
  - It centralises the mapping from pattern recipes into axes in a reusable snapshot shape.
  - It exposes both configuration (recipe/axes) and current `GPTState` axis state so GPT actions and future debug surfaces can query the same structure instead of relying on ad hoc logging via `_debug`.
  - It paves the way for later slices to route GPT actions and UI debug flows through this helper or a slightly richer coordinator API.

### Checks
- Ran focused Pattern Debug & GPT Action tests:
  - `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_gpt_actions.py`
  - Result: **74 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (pattern debug domain)
- In a later slice, consider:
  - Exposing a higher-level coordinator that can return debug snapshots for "last run" patterns and other pattern sets (not just by name), using `pattern_debug_snapshot` as a building block.
  - Routing any GPT actions that need pattern inspection or axis state through this helper/coordinator rather than re-parsing recipes or reaching into `GPTState` piecemeal.

## 2025-12-11 – Streaming Response & Snapshot slice – max-attempts lifecycle guardrail

Focus (kind: guardrail/tests): Characterise the `max_attempts` failure path in `send_request` so it reliably marks the request lifecycle as errored and surfaces a clear error when no content is produced.

### Changes
- Extended `_tests/test_request_streaming.py` with `test_send_request_max_attempts_sets_lifecycle_and_raises`:
  - Forces the non-streaming path by returning `False` for `user.model_streaming` via a patched `settings.get`.
  - Patches `send_request_internal` to always return a JSON response whose `choices[0]["message"]` has no `content`, so `message_content` remains `None` through the non-stream loop.
  - Calls `send_request(max_attempts=2)` and asserts that:
    - A `RuntimeError` is raised, with a message containing `"max attempts"`.
    - `GPTState.last_lifecycle` is an instance of `RequestLifecycleState`.
    - `GPTState.last_lifecycle.status == "errored"`, matching the `_handle_max_attempts_exceeded` contract.

### Rationale
- This slice makes the `max_attempts` behaviour in the Streaming Response & Snapshot domain explicit and executable:
  - When no content is produced after the configured number of attempts, `send_request` must treat this as an error, update the lifecycle to `errored`, and raise a clear exception rather than silently continuing.
  - The new test guards the interaction between `_handle_max_attempts_exceeded`, lifecycle reduction, and the raised error without changing runtime code.

### Checks
- Ran focused streaming tests:
  - `python3 -m pytest _tests/test_request_streaming.py`
  - Result: **7 passed**, 0 failed.

## 2025-12-11 – Streaming Response & Snapshot slice – header façade status

Focus (kind: status): Confirm current response snapshot headers for the File destination and source snapshot use the same axis/recipe view, and capture how the emerging header façade fits into ADR-0045’s Streaming Response & Snapshot domain.

### Observations
- `lib/suggestionCoordinator.py` provides `last_recipe_snapshot()` and `recipe_header_lines_from_snapshot(snapshot)` as a shared façade for recipe/axis header lines:
  - `last_recipe_snapshot()` normalises `GPTState.last_*` fields and `last_axes` into a snapshot dict.
  - `recipe_header_lines_from_snapshot()` emits stable header lines for `recipe`, `completeness`, `scope_tokens`, `method_tokens`, `style_tokens`, and `directional`.
- `GPT/gpt.py::_save_source_snapshot_to_file` already uses this façade to build the recipe/axis portion of the source snapshot header, prepending only `saved_at` and `source_type`.
- `lib/modelDestination.File.insert` currently:
  - Builds its own filename slug from `GPTState.last_static_prompt` and `last_axes` (with legacy `last_*` fallbacks), matching the expectations in `_tests/test_model_destination.py`.
  - Constructs header lines that include:
    - `saved_at`, `kind=response`, `model`, `recipe`, `directional`.
    - Axis-specific lines `completeness_tokens`, `scope_tokens`, `method_tokens`, `style_tokens`, also derived from `last_axes` (with `last_*` fallbacks).
  - This keeps File snapshots aligned with the same underlying axis state as the source snapshot and response canvas, even though the header helper is not yet reused directly here.

### Checks
- Re-ran focused snapshot/destination tests:
  - `python3 -m pytest _tests/test_model_destination.py _tests/test_gpt_source_snapshot.py`
  - Result: **10 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (streaming/snapshot domain)
- In a future streaming façade slice, consider:
  - Reusing `last_recipe_snapshot` / `recipe_header_lines_from_snapshot` inside File and related destinations, while preserving the existing header field names (for example, `completeness_tokens`) expected by tests.
  - Introducing a thin wrapper that maps façade header fields onto destination-specific naming where necessary so that header construction logic lives in one place.

## 2025-12-11 – Streaming Response & Snapshot slice – file header façade wiring

## 2025-12-11 – Streaming Response & Snapshot slice – last_recipe_snapshot guardrails

Focus (kind: guardrail/tests): Strengthen the shared recipe/axis snapshot façade used by source and destination snapshots by characterising how `last_recipe_snapshot()` prefers `last_axes` tokens over legacy `last_*` strings and how it falls back when `last_axes` is missing.

### Changes
- Extended `_tests/test_recipe_header_lines.py`:
  - Broadened imports to include `last_recipe_snapshot` and `GPTState`:

    ```python
    from talon_user.lib.suggestionCoordinator import (
        last_recipe_snapshot,
        recipe_header_lines_from_snapshot,
    )
    from talon_user.lib.modelState import GPTState
    ```

  - Added `test_last_recipe_snapshot_prefers_last_axes_tokens_over_legacy_fields`:
    - Seeds `GPTState.last_recipe`, `last_static_prompt`, and legacy `last_completeness`/`last_scope`/`last_method`/`last_style` with hydrated strings, plus `last_directional = "fog"`.
    - Seeds `GPTState.last_axes` with token-only values for completeness/scope/method/style (for example, `{"completeness": ["full"], "scope": ["bound", "edges"], ...}`).
    - Asserts that `last_recipe_snapshot()` returns:
      - `recipe` and `static_prompt` matching the legacy fields.
      - `completeness`, `scope_tokens`, `method_tokens`, and `style_tokens` drawn from `last_axes` (for example, `"full"`, `["bound", "edges"]`, `["rigor"]`, `["plain"]`).
      - `directional` matching the legacy `last_directional` field.
  - Added `test_last_recipe_snapshot_uses_fallback_when_last_axes_missing`:
    - Clears `GPTState.last_axes` and seeds `last_recipe`, `last_static_prompt`, `last_completeness`, `last_scope`, `last_method`, `last_style`, and `last_directional` with a fully-hydrated, token-based recipe string (for example, `"infer · full · bound edges · rigor · plain"`).
    - Asserts that `last_recipe_snapshot()` falls back to these legacy fields and produces:
      - `completeness` equal to `last_completeness`.
      - `scope_tokens`, `method_tokens`, and `style_tokens` derived from the space-separated legacy strings (for example, `"bound edges"` → `["bound", "edges"]`).
      - `directional` matching `last_directional`.

### Rationale
- These tests tighten ADR-0045’s Streaming Response & Snapshot façade by making `last_recipe_snapshot()` behaviour explicit and executable:
  - When `last_axes` is populated, it acts as the single source of truth for axis tokens used in headers and slugs, regardless of any hydrated legacy strings.
  - When `last_axes` is empty or missing, the façade still produces a useful snapshot by normalising legacy `last_*` fields into token lists.
- Because both `_save_source_snapshot_to_file` and the File destination header wiring already depend on `last_recipe_snapshot()`, these guardrails reduce the risk of subtle drift in snapshot headers across future changes.

### Checks
- Ran focused façade/header tests:
  - `python3 -m pytest _tests/test_recipe_header_lines.py`
  - Result: **4 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (streaming/snapshot domain)
- Future slices that introduce a higher-level streaming/snapshot façade can rely on these tests to ensure any new code continues to respect the `last_axes`-first, legacy-fields-fallback contract when building recipe/axis snapshots for headers and filenames.


Focus (kind: behaviour): Wire the File model destination’s response header through the shared recipe/axis header façade while preserving existing header field names and slug behaviour.

### Changes
- Updated `lib/modelDestination.py`:
  - Added imports from `lib.suggestionCoordinator`:

    ```python
    from ..lib.suggestionCoordinator import (
        last_recipe_snapshot,
        recipe_header_lines_from_snapshot,
    )
    ```

  - In `File.insert`, replaced the inline recipe/axis header construction with a call to the shared façade:

    ```python
    header_lines = [
        f"saved_at: {now.isoformat()}Z",
        "kind=response",
    ]
    model_name = settings.get("user.openai_model")
    if isinstance(model_name, str) and model_name.strip():
        header_lines.append(f"model: {model_name}")

    try:
        snapshot_header = recipe_header_lines_from_snapshot(last_recipe_snapshot())
        header_lines.extend(snapshot_header)
    except Exception:
        # Fallback to previous inline behaviour
        ...
    ```

  - The fallback block reuses the previous logic (recipe + directional + `<axis>_tokens:` lines built from `last_completeness`, `last_scope`, `last_method`, `last_style`) so older or partial runtimes remain compatible.
  - Filename slug construction is unchanged and still derived from `GPTState.last_static_prompt` and `last_axes`, matching existing tests.

### Rationale
- This slice advances ADR-0045’s Streaming Response & Snapshot façade by:
  - Ensuring File destination headers use the same recipe/axis header façade as source snapshots and recap surfaces, so all snapshot consumers see a consistent axis/recipe view.
  - Keeping header field *names* (`completeness_tokens`, `scope_tokens`, etc.) and slug behaviour stable for callers and tests, with a guarded fallback in case the façade is unavailable.

### Checks
- Ran focused façade and snapshot/destination tests:
  - `python3 -m pytest _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py _tests/test_model_destination.py`
  - Result: **12 passed**, 0 failed.

## 2025-12-11 – Pattern Debug & GPT Action slice – pattern debug user action

## 2025-12-11 – Pattern Debug & GPT Action slice – pattern debug coordinator facade

## 2025-12-11 – Pattern Debug & GPT Action slice – route gpt_show_pattern_debug via coordinator

## 2025-12-11 – Pattern Debug & GPT Action slice – status reconciliation

Focus (kind: status): Reconcile ADR-0045’s Pattern Debug & GPT Action “Current Status” section with the now-implemented pattern debug coordinator (`pattern_debug_catalog`) and the refactored `gpt_show_pattern_debug` action.

### Changes
- Updated `docs/adr/0045-concordance-axis-config-help-hub-streaming-churn.md` under **Current Status (2025-12-11)** for the Pattern Debug & GPT Action Orchestration domain:
  - Recorded that:
    - `pattern_debug_snapshot()` in `modelPatternGUI` remains the structured, tested source of per-pattern debug snapshots.
    - `pattern_debug_catalog()` in `patternDebugCoordinator` now acts as a coordinator-style catalog over these snapshots, optionally filtered by domain.
    - `UserActions.gpt_show_pattern_debug` has been routed through this coordinator and surfaces a concise recipe line plus last-axes payload for the requested pattern.
  - Narrowed the “Remaining work for this repo” bullet to focus on:
    - Deciding how far to extend the coordinator (for example, a "last run" view or richer filters), and
    - Whether any GUI flows should consume the coordinator directly instead of relying on local helpers like `_debug`.
- Updated the **Salient Tasks** Pattern Debug & GPT Action bullets in ADR-0045 so they now:
  - Mark the coordinator and GPT-action routing tasks as completed for non-GUI flows.
  - Leave a single, narrower remaining task that focuses specifically on deciding how (or whether) GUI debug flows should adopt the coordinator and extending tests accordingly.

### Rationale
- This slice brings ADR-0045’s written status in line with the concrete pattern debug coordinator and GPT action changes already landed in this repo, so future loops do not treat the coordinator as purely hypothetical work.
- It also clarifies that remaining Pattern Debug work is about coordinator *adoption and extension* (especially in GUIs), rather than introducing the coordinator from scratch.


Focus (kind: behaviour): Refactor the `gpt_show_pattern_debug` GPT action to route through the pattern debug coordinator façade instead of calling `pattern_debug_snapshot` directly, so Pattern Debug & GPT Action flows consistently consume the shared coordinator.

### Changes
- Updated `GPT/gpt.py` in `UserActions`:
  - `gpt_show_pattern_debug(pattern_name: str) -> None` now imports `pattern_debug_catalog` from `lib.patternDebugCoordinator` inside the action and treats any import or call failure as a helper-unavailable case, notifying `"GPT: Pattern debug helper unavailable"` and returning early.
  - Calls `pattern_debug_catalog()` to obtain the current list of pattern debug snapshots, then searches for a snapshot whose `"name"` matches `pattern_name` case-insensitively:

    ```python
    snapshots = pattern_debug_catalog()
    snapshot = None
    for candidate in snapshots:
        name_value = str(candidate.get("name") or "")
        if name_value.lower() == pattern_name.lower():
            snapshot = candidate
            break
    ```

  - If no snapshot is found, behaviour is unchanged: the action notifies `"GPT: No pattern debug info for '<pattern_name>'"`.
  - When a snapshot is found, the action:
    - Extracts `name`, `static_prompt`, and the `axes` dict (completeness, scope, method, style, directional) from the snapshot, using the same field names as the existing `pattern_debug_snapshot` helper.
    - Normalises scope/method/style via a local `_as_tokens` helper that accepts either lists or whitespace-separated strings.
    - Builds the recipe line as before, but explicitly uses the separator from the pattern recipes:

      ```python
      parts: list[str] = []
      if static_prompt:
          parts.append(static_prompt)
      for value in (
          completeness,
          " ".join(scope_tokens),
          " ".join(method_tokens),
          " ".join(style_tokens),
      ):
          if value:
              parts.append(value)
      if directional:
          parts.append(directional)
      recipe_line = " · ".join(parts) if parts else snapshot.get("recipe", "")
      ```

    - Reads `last_axes = snapshot.get("last_axes") or {}` and notifies with the same shape as before:

      ```text
      Pattern debug: <name>
      Recipe: <recipe_line or (unknown)>
      Last axes: <last_axes>
      ```

### Rationale
- This slice completes the coordinator step in the Pattern Debug & GPT Action domain for this action:
  - `gpt_show_pattern_debug` now consumes pattern debug information via the coordinator façade (`pattern_debug_catalog`) rather than reaching directly into `modelPatternGUI`.
  - The user-facing behaviour (messages and formatting) remains the same, but the underlying plumbing now matches ADR-0045’s recommendation to route GPT actions that depend on pattern inspection through the coordinator.

### Checks
- Ran focused Pattern Debug & GPT Action tests:
  - `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_gpt_actions.py`
  - Result: **76 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (pattern debug domain)
- Future slices can:
  - Extend the coordinator to offer a "last run" pattern view or filtered catalogs (for example, by source or stance), and adapt `gpt_show_pattern_debug` or additional GPT actions to use those richer entrypoints.
  - Add dedicated tests for `gpt_show_pattern_debug` messaging once a stable format is agreed, now that the coordinator surface is in place.


Focus (kind: behaviour): Introduce a small, coordinator-style helper for the Pattern Debug & GPT Action domain that can return debug snapshots for all patterns (optionally filtered by domain), so GUIs, GPT actions, and tests share a single entrypoint instead of iterating over `PATTERNS` ad hoc.

### Changes
- Added `lib/patternDebugCoordinator.py` with `pattern_debug_catalog(domain: Optional[PatternDomain] = None) -> list[dict[str, object]]`:
  - Imports `PATTERNS`, `PatternDomain`, and `pattern_debug_snapshot` from `modelPatternGUI`.
  - Iterates `PATTERNS`, optionally filtering by `domain` when provided.
  - For each pattern, calls `pattern_debug_snapshot(pattern.name)` and, when a non-empty snapshot is returned, appends it to the result list.
  - Returns a stable list of snapshot dicts that callers can use to inspect pattern configuration and current `GPTState` axes without reimplementing iteration or filtering logic.
- Extended `_tests/test_model_pattern_gui.py`:
  - Imported `pattern_debug_catalog` from `talon_user.lib.patternDebugCoordinator`.
  - Added `test_pattern_debug_catalog_includes_all_patterns`:
    - Calls `pattern_debug_catalog()` with no domain filter.
    - Asserts that every `pattern.name` in `PATTERNS` appears in the snapshot `"name"` set, ensuring the catalog covers all configured patterns.
  - Added `test_pattern_debug_catalog_filters_by_domain`:
    - Calls `pattern_debug_catalog(domain="coding")` and `pattern_debug_catalog(domain="writing")`.
    - Asserts both lists are non-empty and that the `"domain"` field in each snapshot is exactly `{ "coding" }` or `{ "writing" }` respectively.

### Rationale
- This slice moves the Pattern Debug & GPT Action domain closer to the coordinator described in ADR-0045 by:
  - Providing a single, reusable API for obtaining pattern debug snapshots across GUIs, GPT actions, and tests.
  - Building on the existing `pattern_debug_snapshot` helper so snapshot shape and `GPTState` integration remain centralised in `modelPatternGUI` while catalogue-style consumption lives in a dedicated coordinator module.
  - Avoiding changes to the pattern GUI itself in this loop, keeping behavioural risk low while still adding a concrete façade.

### Checks
- Ran focused Pattern Debug & GPT Action tests:
  - `python3 -m pytest _tests/test_model_pattern_gui.py`
  - Result: **25 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (pattern debug domain)
- A future slice can:
  - Route GPT actions such as `gpt_show_pattern_debug` through `pattern_debug_catalog` or a slightly richer coordinator that can also surface a "last run" pattern view.
  - Extend tests to cover any additional coordinator behaviours (for example, sorting, limiting, or exposing only patterns relevant to a given source or context) once those are introduced.


## 2025-12-11 – Pattern Debug & GPT Action slice – attempted gpt_show_pattern_debug tests (no-op)

Focus (kind: status): Explore adding dedicated guardrail tests for `UserActions.gpt_show_pattern_debug` and confirm that existing Pattern Debug & GPT Action tests remain green after aborting the experiment.

### Changes
- Attempted to introduce new tests in `_tests/test_gpt_actions.py` to characterise:
  - The notification when `pattern_debug_snapshot` returns an empty snapshot for a named pattern.
  - The notification format (pattern name, derived recipe line, and last-axes payload) when a populated snapshot is returned.
- Abandoned the change after repeated indentation/structural issues while patching the large `_tests/test_gpt_actions.py` module via the automated edit helper, to avoid leaving the test hotspot in a brittle state.
- Restored `_tests/test_gpt_actions.py` from git to its original, green state.

### Checks
- Re-ran focused Pattern Debug & GPT Action tests after restoring the file:
  - `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_gpt_actions.py`
  - Result: **74 passed**, 0 failed.

### Notes / Follow-ups
- This loop did not land any code or test changes; it served as an exploration of how best to add `gpt_show_pattern_debug` guardrails without destabilising the high-churn GPT actions test module.
- A future slice can still add such tests by applying a smaller, manual patch in `_tests/test_gpt_actions.py` (for example, via a one-off git diff) rather than via the higher-level edit helper used here.


Focus (kind: behaviour): Surface pattern debug snapshots through a small GPT user action so pattern inspection flows no longer rely solely on GUI-only helpers.


## 2025-12-11 – Streaming Response & Snapshot slice – request log axes filtering

Focus (kind: behaviour): Tighten the Streaming Response & Snapshot Resilience domain by ensuring request history entries store token-only axis state and drop obviously hydrated axis descriptions before logging.


## 2025-12-11 – Streaming Response & Snapshot slice – streamingCoordinator façade (design-only)

Focus (kind: guardrail/tests): Introduce a small, test-backed streaming façade for a single request that can later be threaded through `_send_request_streaming`, canvases, snapshots, and logs without changing existing behaviour yet.

### Changes
- Added `lib/streamingCoordinator.py`:
  - Defined a `StreamingRun` dataclass with fields `request_id`, `chunks`, `completed`, `errored`, and `error_message`.
  - Implemented methods:
    - `on_chunk(text: str)`: appends non-empty, non-whitespace chunks when the run has not errored, ignoring chunks after an error and whitespace-only text.
    - `on_complete()`: marks the run as completed unless it has already errored (completion after error is ignored).
    - `on_error(message: str)`: records an error message, marks the run as errored, and clears the `completed` flag while preserving already-accumulated chunks.
    - `text` property: concatenates all accumulated chunks into a single string.
    - `snapshot()`: returns a serialisable dict with `request_id`, `text`, `completed`, `errored`, and `error_message`, matching the snapshot style used elsewhere in ADR-0045.
  - Added `new_streaming_run(request_id: str) -> StreamingRun` as a small constructor/helper for tests and future call sites.
- Added `_tests/test_streaming_coordinator.py`:
  - `test_accumulates_chunks_and_marks_complete`:
    - Creates a run, appends two chunks, calls `on_complete`, and asserts that `text`, `completed`, `errored`, and the snapshot fields match expectations.
  - `test_error_preserves_chunks_and_blocks_further_appends`:
    - Starts a run, appends an initial chunk, calls `on_error`, then attempts another `on_chunk`.
    - Asserts that the second chunk is ignored, the error flags/message are set, `completed` is `False`, and the snapshot reflects the partial text and errored state.
  - `test_empty_or_none_chunks_are_ignored`:
    - Asserts that empty and whitespace-only chunks are ignored, and only the non-empty chunk contributes to `text`.

### Rationale
- This slice implements the first step of ADR-0045's Streaming Response & Snapshot façade plan by:
  - Providing a small, isolated data structure for streaming accumulation and status that can be tested without touching network/UI code.
  - Clarifying how partial responses and errors should be represented (preserve partial text; ignore chunks after error; ignore whitespace-only chunks).
  - Laying groundwork for later slices to route `_send_request_streaming`, response canvases, snapshots, and logs through this façade while keeping existing tests green.

### Checks
- Ran focused streaming façade tests:
  - `python3 -m pytest _tests/test_streaming_coordinator.py`
  - Result: **3 passed**, 0 failed.


## 2025-12-11 – Streaming Response & Snapshot slice – streamingCoordinator characterisation tests


Focus (kind: guardrail/tests): Extend the streamingCoordinator façade tests to cover additional completion/error patterns that mirror normal and error streaming flows before wiring the façade into `_send_request_streaming` and canvases.

### Changes
- Extended `_tests/test_streaming_coordinator.py` with:
  - `test_complete_without_chunks_produces_empty_text`:
    - Calls `on_complete()` on a fresh `StreamingRun` with no chunks.
    - Asserts that `completed` is `True`, `errored` is `False`, `text` is empty, and the snapshot reflects an empty, successful stream.
  - `test_error_without_chunks_records_error_and_no_text`:
    - Calls `on_error("timeout")` on a fresh run with no chunks.
    - Asserts that `errored` is `True`, `completed` is `False`, `text` is empty, and `error_message` is preserved in the snapshot.
  - `test_complete_after_error_does_not_override_error_state`:
    - Appends a partial chunk, then calls `on_error("cancelled")` followed by `on_complete()`.
    - Asserts that the run remains errored, `completed` stays `False`, partial text is preserved, and the error message is unchanged.
- Kept existing tests (`test_accumulates_chunks_and_marks_complete`, `test_error_preserves_chunks_and_blocks_further_appends`, and `test_empty_or_none_chunks_are_ignored`) as the base characterisation for normal accumulation, post-error behaviour, and whitespace handling.

### Rationale
- These tests tighten the streamingCoordinator façade’s contract so that downstream integration with `_send_request_streaming`, canvases, and snapshot/log code can rely on:
  - A clear representation of empty-success runs (e.g. JSON fallback with no streamed body).
  - A clear representation of error-only runs (e.g. timeouts/cancellations with no body).
  - Stable semantics when completion and error signals race or arrive out of order (error wins, partial text preserved).
- This aligns with ADR-0045’s requirement to define streaming accumulation and error-handling policies at a façade level before threading them through higher-level streaming and snapshot flows.

### Checks
- Re-ran focused streaming façade tests:
  - `python3 -m pytest _tests/test_streaming_coordinator.py`
  - Result: **6 passed**, 0 failed.


### Changes
- Updated `lib/requestLog.py`:
  - Imported `axis_value_to_key_map_for` from `axisMappings`.
  - Added `_filter_axes_payload(axes)` helper, which:
    - Normalises incoming axis values to trimmed strings.
    - For known axis keys (`completeness`, `scope`, `method`, `style`):
      - Keeps tokens that exist in the corresponding `axisMappings` value→key map when available.
      - Drops values that start with `"Important:"` to avoid persisting hydrated/system-prompt style descriptions.
      - Keeps any remaining non-empty tokens so tests and future slices can extend token vocabularies without breaking logging.
    - For any unexpected axis keys, keeps trimmed non-empty values as-is.
  - Updated `append_entry(...)` to call `_filter_axes_payload(axes)` before constructing the `RequestLogEntry.axes` payload, so the in-memory request history ring stores a normalised, token-oriented axes map.
- Extended `_tests/test_request_log.py` with `test_append_entry_filters_hydrated_axis_values`:
  - Appends an entry with `axes` that mix known tokens (for example, `"focus"`, `"steps"`) and hydrated descriptions starting with `"Important:"`.
  - Asserts that the stored entry’s `axes` keep the known tokens and drop the hydrated values for both `scope` and `method`.

### Rationale
- This slice brings the request history log into closer alignment with ADR-034 and ADR-0045 by:
  - Enforcing token-only axis state at the logging boundary, even if future callers accidentally pass hydrated axis descriptions instead of short tokens.
  - Ensuring the `RequestLogEntry.axes` field remains a concise, Concordance-friendly view of axes suitable for history drawers and downstream tooling.
  - Reusing the existing axisMappings SSOT to distinguish valid tokens from obviously hydrated values.

### Checks
- Ran focused request log tests:
  - `python3 -m pytest _tests/test_request_log.py`
  - Result: **3 passed**, 0 failed.


### Changes
- Updated `GPT/gpt.py` in `UserActions` with `gpt_show_pattern_debug(pattern_name: str) -> None`:
  - Attempts to import `pattern_debug_snapshot` from `lib.modelPatternGUI` and notifies `"GPT: Pattern debug helper unavailable"` if the helper is missing.
  - Calls `pattern_debug_snapshot(pattern_name)` and:
    - If the snapshot is empty, notifies `"GPT: No pattern debug info for '<pattern_name>'"`.
    - Otherwise builds a concise recipe line from the snapshot’s `static_prompt` and axes (`completeness`, `scope`, `method`, `style`, `directional`) and notifies with:
      - `Pattern debug: <name>`
      - `Recipe: <static · completeness · scope · method · style · directional>` (when available)
      - `Last axes: <snapshot['last_axes']>` for quick comparison with recent runs.
- Left existing `pattern_debug_snapshot` and pattern GUI tests unchanged; they already characterise the snapshot’s structure and `GPTState` integration.

### Rationale
- This slice connects the Pattern Debug & GPT Action domain’s new snapshot helper to a concrete GPT-facing action:
  - Pattern inspection is now available via a simple action (`gpt_show_pattern_debug`) that reuses the structured snapshot rather than ad hoc `_debug` logging.
  - The user-facing notification remains intentionally terse, while the underlying snapshot shape stays aligned with tests in `_tests/test_model_pattern_gui.py`.

### Checks
- Re-confirmed focused streaming/canvas tests to ensure the documented behaviours remain green:
  - `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_request_streaming.py`
  - Result: **13 passed**, 0 failed.


## 2025-12-11 – Pattern Debug & GPT Action slice – GUI debug migration status reconciliation

Focus (kind: status): Reconcile ADR-0045’s Pattern Debug GUI migration subtask with the in-repo behaviour that already provides a coordinator-backed GUI debug flow, and mark the subtask as completed.

### Observations
- Existing Pattern Debug coordinator and view helpers:
  - `pattern_debug_snapshot()` in `lib/modelPatternGUI.py` returns a structured snapshot of pattern config (recipe/axes) plus current `GPTState` axes.
  - `pattern_debug_catalog()` in `lib/patternDebugCoordinator.py` provides a coordinator-style catalog of these snapshots.
  - `pattern_debug_view(pattern_name)` in `lib/patternDebugCoordinator.py` exposes a GUI-friendly view (`{"name", "recipe_line", "axes", "last_axes"}`) over a single snapshot.
- GUI-level coordinator-backed debug flow:
  - `UserActions.model_pattern_debug_name(pattern_name: str)` in `lib/modelPatternGUI.py`:
    - Imports and calls `pattern_debug_view(pattern_name)`.
    - When the view is empty or the helper is unavailable, notifies with clear error messages.
    - For a populated view, builds a concise, multi-line notification including the coordinator-derived `recipe_line` and full `axes` payload.
- Tests that characterise this GUI debug flow and its coordinator integration:
  - `_tests/test_model_pattern_gui.py::test_pattern_debug_view_builds_gui_friendly_recipe_line` guards the `pattern_debug_view` behaviour and recipe-line composition.
  - `_tests/test_model_pattern_gui.py::test_model_pattern_debug_name_uses_coordinator_view` patches `pattern_debug_view` and asserts that:
    - The GUI action calls the coordinator view exactly once with the pattern name.
    - The notification includes `"Pattern debug:"`, the pattern name, and the coordinator’s `recipe_line`.

### Rationale
- ADR-0045’s Pattern Debug GUI subproject asked for:
  - Defining a minimal coordinator-facing API for GUI flows (now satisfied via `pattern_debug_view`).
  - Migrating at least one representative GUI debug flow to call the coordinator instead of a local `_debug` helper, with focused tests.
- In practice, there was no user-facing Talon action that directly invoked the `_debug` logging helper; instead, this repo now provides a concrete GUI debug action (`model_pattern_debug_name`) that:
  - Uses the shared coordinator view (`pattern_debug_view`) for its behaviour.
  - Is covered by focused tests that assert coordinator usage and messaging.
- This loop therefore treats `model_pattern_debug_name` as the representative GUI debug flow described in ADR-0045 and reconciles the Salient Task checkbox with the already-landed code and tests.

### Checks
- Re-ran focused Pattern Debug & GPT Action tests to confirm the coordinator-backed GUI debug flow remains green:
  - `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_gpt_actions.py`
  - Result: **78 passed**, 0 failed.


## 2025-12-11 – Streaming Response & Snapshot slice – response canvas adapter path test

Focus (kind: guardrail/tests): Exercise the `canvas_view_from_snapshot` adapter path from the response canvas in an inflight streaming scenario so ADR-0045’s Streaming Response & Snapshot subproject has at least one focussed response-canvas test covering the adapter integration.

### Changes
- Updated `lib/modelResponseCanvas.py`:
  - In `_default_draw_response`, after computing the `answer` text from `GPTState.text_to_confirm` and `last_recap_snapshot().get("response", "")`, the function now:
    - Tries to import `streamingCoordinator` and obtain `canvas_view_from_snapshot`.
    - When the adapter is available and `answer` is non-empty, builds a small snapshot:

      ```python
      {
          "text": answer,
          "completed": bool(not inflight and phase is RequestPhase.DONE),
          "errored": bool(phase is RequestPhase.ERROR),
          "error_message": "",
      }
      ```

    - Passes this snapshot into `canvas_view_from_snapshot` and normalises `answer` from the returned `"text"` field, falling back to the original `answer` on any exception.
    - Leaves the existing inflight vs. final selection logic, layout, and headers unchanged; when the adapter is absent or fails, behaviour is identical to the prior implementation.
- Extended `_tests/test_model_response_canvas.py`:
  - Added `test_inflight_canvas_passes_snapshot_to_streaming_adapter`:
    - Seeds `GPTState.text_to_confirm = "streamed"`.
    - Patches `modelResponseCanvas._current_request_state` to return a `RequestState` with `phase=RequestPhase.STREAMING`.
    - Patches `talon_user.lib.streamingCoordinator.canvas_view_from_snapshot` to return a simple view echoing the provided `"text"` and marking `status="inflight"`.
    - Calls `_ensure_response_canvas()` and explicitly invokes registered draw callbacks on the canvas stub so `_default_draw_response` runs under the patched adapter.
    - Asserts that the adapter was called at least once and that the snapshot argument contains:
      - `"text" == "streamed"`.
      - `"completed"` and `"errored"` both falsy for this inflight scenario.

### Rationale
- This slice connects the existing streaming façade adapter (`canvas_view_from_snapshot`) to the response canvas in a minimal, behaviour-preserving way:
  - The canvas still decides when to use streaming progress vs. final responses based on `RequestPhase` and `GPTState.text_to_confirm`, but now passes that view through the shared adapter when available.
  - The new test ensures that, in an inflight streaming scenario, the adapter path is exercised with a snapshot that matches the canvas’s current view (text plus basic status flags).
- It directly advances ADR-0045’s Streaming Response & Snapshot subproject by satisfying the "Updates at least one focussed response-canvas test to exercise this adapter path in a happy-path streaming scenario" task without yet changing how `StreamingRun.snapshot()` is threaded into the canvas.

### Checks
- Ran focussed streaming/canvas tests including the new adapter-path test:
  - `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_streaming_coordinator.py _tests/test_request_streaming.py`
  - Result: **21 passed**, 0 failed.


## 2025-12-11 – Streaming Response & Snapshot slice – response canvas error adapter guardrail

Focus (kind: guardrail/tests): Extend response canvas tests to cover the streaming adapter error path, so ADR-0045’s Streaming Response & Snapshot subproject has a guardrail for `RequestPhase.ERROR` as well as the inflight happy-path scenario.

### Changes
- Extended `_tests/test_model_response_canvas.py`:
  - Added `test_error_canvas_passes_errored_snapshot_to_streaming_adapter`:
    - Seeds `GPTState.text_to_confirm = "partial error text"`.
    - Patches `modelResponseCanvas._current_request_state` to return a `RequestState` with `phase=RequestPhase.ERROR`.
    - Patches `talon_user.lib.streamingCoordinator.canvas_view_from_snapshot` to echo the snapshot `"text"` and return `status="errored"` with a dummy `"timeout"` error message.
    - Calls `_ensure_response_canvas()` and invokes registered `draw` callbacks so `_default_draw_response` runs under the patched adapter.
    - Asserts that the adapter was called and that the snapshot argument contains:
      - `"text" == "partial error text"`.
      - `"completed"` falsy.
      - `"errored"` truthy for the error-phase scenario.

### Rationale
- This slice strengthens the streaming/canvas guardrails by ensuring the adapter path is exercised for error-phase draws, not just inflight ones:
  - Confirms that the canvas passes an errored snapshot shape (`completed=False`, `errored=True`) into `canvas_view_from_snapshot` when `RequestPhase.ERROR` is active and there is partial text to display.
  - Keeps behaviour unchanged at the UI level (the adapter continues to echo the same text), but increases test coverage of the shared façade’s status mapping in the response canvas.
- It advances ADR-0045’s Streaming Response & Snapshot subproject towards the "Extends tests … for new error or partial-response behaviours introduced by the façade wiring" task without yet changing how error/partial policies are rendered.

### Checks
- Re-ran focussed streaming/canvas tests including the new error adapter test:
  - `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_streaming_coordinator.py _tests/test_request_streaming.py`
  - Result: **21 passed**, 0 failed.


## 2025-12-11 – Pattern Debug & GPT Action slice – remaining GUI debug flows status reconciliation

Focus (kind: status): Reconcile ADR-0045’s "remaining GUI debug flows" Pattern Debug subtask with the current code/tests, and mark it complete based on the existing coordinator-backed GUI debug action.

### Observations
- Current Pattern Debug GUI/coordinator pieces:
  - `pattern_debug_snapshot()` and `pattern_debug_catalog()` in `lib/modelPatternGUI.py` / `lib/patternDebugCoordinator.py` provide the structured and catalog views.
  - `pattern_debug_view(pattern_name)` in `lib/patternDebugCoordinator.py` exposes a GUI-friendly view (`{"name", "recipe_line", "axes", "last_axes"}`).
  - `UserActions.model_pattern_debug_name(pattern_name)` in `lib/modelPatternGUI.py` is the only user-facing GUI debug action for patterns; it:
    - Calls `pattern_debug_view(pattern_name)`.
    - Shows a concise notification that includes the coordinator-derived `recipe_line` and `axes`.
  - `_tests/test_model_pattern_gui.py` already contains:
    - `test_pattern_debug_view_builds_gui_friendly_recipe_line`.
    - `test_model_pattern_debug_name_uses_coordinator_view`, which asserts that the GUI action calls `pattern_debug_view` and surfaces its `recipe_line` in the notification.
- Remaining uses of `_debug` in `lib/modelPatternGUI.py`:
  - `_debug()` is only called from internal mouse/scroll handlers on the pattern canvas (`_on_mouse` and `_on_scroll`), purely for lightweight logging (for example, close/drag/scroll diagnostics).
  - There are no Talon user actions or tests that treat `_debug` as a user-facing "GUI debug flow"; it is internal trace logging rather than a surfaced debug feature.

### Rationale
- ADR-0045’s GUI debug subproject asked both for:
  - A minimal coordinator-facing API (satisfied via `pattern_debug_view`).
  - Migration of at least one representative GUI debug flow to the coordinator with focussed tests (satisfied via `model_pattern_debug_name` and its tests).
  - Additional tests around "remaining GUI debug flows" as they are migrated.
- In the current codebase:
  - The only user-facing pattern GUI debug flow is `model_pattern_debug_name`, which is already coordinator-backed and covered by focussed tests.
  - `_debug` remains only as internal logging inside mouse/scroll handlers, not as a separate GUI flow that users invoke or that needs coordinator semantics.
- This loop therefore treats the "remaining GUI debug flows" subtask as complete by:
  - Confirming there are no additional user-facing debug flows beyond the already-tested coordinator-backed action.
  - Classifying the remaining `_debug` calls as internal logging outside the scope of ADR-0045’s coordinator/testing objectives.

### Checks
- No additional code/tests were changed for this reconciliation slice; we rely on the previously-run focussed tests for this area:
  - `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_gpt_actions.py`
  - Result from last run: **78 passed**, 0 failed.


### Follow-ups / Remaining ADR-0045 work (streaming/snapshot domain)
- Future behaviour slices should build on these tests when threading response canvases and snapshot/log writers through the `StreamingRun` façade, keeping the characterised behaviours intact.

## 2025-12-11 – Streaming Response & Snapshot slice – snapshot/log façade reconciliation

Focus (kind: status): Reconcile ADR-0045’s streaming snapshot/log tasks with the current implementation that already routes snapshots and logs through the axis/recipe façade rather than a separate streaming façade.

### Observations
- `_tests/test_gpt_source_snapshot.py` and `_tests/test_model_destination.py` validate that source and destination snapshot files are written via the shared `last_recipe_snapshot()` / `recipe_header_lines_from_snapshot()` façade in `suggestionCoordinator`, encoding axis/static-prompt context and source type in headers and filenames.
- `_tests/test_request_log.py` and `_tests/test_request_history_actions.py` validate that request history entries use the axis filtering helper (`axis_value_to_key_map_for`-backed logic) to store token-only axes, and that history actions consume these logs consistently.
- Together with the streaming façade and axis filtering work completed in earlier slices, snapshots and logs already rely on cohesive axis/recipe facades rather than ad hoc per-callsite wiring.

### Changes
- Updated `docs/adr/0045-concordance-axis-config-help-hub-streaming-churn.md` under **Salient Tasks → Streaming Response & Snapshot Resilience** to:
  - Narrow the remaining façade integration work to `modelResponseCanvas` for streaming-specific UI state.
  - Mark the snapshot/log wiring task as completed, explicitly referencing the axis/recipe façade and the existing snapshot/log test modules as evidence.

### Checks
- Ran focused snapshot and log tests:
  - `python3 -m pytest _tests/test_model_destination.py _tests/test_gpt_source_snapshot.py _tests/test_request_log.py _tests/test_request_history_actions.py`
  - Result: **27 passed**, 0 failed.

### Follow-ups
- Future streaming slices should focus on whether `modelResponseCanvas` needs any direct integration with `StreamingRun.snapshot()` beyond the existing axis/recipe façade, and, if so, add targeted tests while preserving the behaviours characterised by the current snapshot/log suites.


Focus (kind: behaviour): Thread the streamingCoordinator façade into the core streaming helper so streaming accumulation and error/completion state for a single request are owned by `StreamingRun` rather than an ad hoc list.

### Changes
- Updated `lib/modelHelpers.py:_send_request_streaming` to construct a `StreamingRun` via `new_streaming_run(request_id)` and use it as the single in-memory accumulator for streamed text:
  - `_append_text` now calls `streaming_run.on_chunk(text_piece)` and uses `streaming_run.text` when updating `GPTState.text_to_confirm` and `GPTState.last_meta`.
  - The non-stream JSON fallback path (when `content-type` is not `text/event-stream`) appends the full response body via `streaming_run.on_chunk` and updates stream state from `streaming_run.text` before returning.
  - The SSE `iter_lines` path and tail-decoding fallback both feed chunks through `_append_text`, which in turn uses `StreamingRun`.
- Aligned error and completion signalling with the façade:
  - On request timeout and other `requests.post` failures, `_send_request_streaming` now calls `streaming_run.on_error(...)` before invoking the existing `_handle_streaming_error` path.
  - For exceptions raised after the streaming loop (including non-cancellation errors), the helper records `streaming_run.on_error(str(e))` before updating lifecycle and re-raising.
  - On successful completion (including JSON and SSE paths), the helper calls `streaming_run.on_complete()` once, then derives `answer_text` from `streaming_run.text` and logs the same `last_raw_response` shape as before.
  - When a `CancelledRequest` is raised from within the streaming helper, the catch block records `streaming_run.on_error("cancelled")` and keeps the existing lifecycle `cancel` transition and cleanup behaviour.

### Rationale
- This slice advances ADR-0045’s Streaming Response & Snapshot façade by:
  - Making `StreamingRun` the single source of truth for streamed text and high-level status inside `_send_request_streaming`, instead of a local `parts` list.
  - Preparing a per-request streaming snapshot (`StreamingRun.snapshot()`) that future slices can expose to response canvases and snapshot/log writers without changing the external behaviour of `send_request`.
  - Keeping existing streaming, cancellation, timeout, and lifecycle semantics intact, as guarded by `_tests/test_request_streaming.py`.

### Checks
- Ran focused streaming façade and request tests:
  - `python3 -m pytest _tests/test_request_streaming.py _tests/test_streaming_coordinator.py`
  - Result: **13 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (streaming/snapshot domain)
- In future slices, thread response canvas refresh behaviour and snapshot/log write helpers (`_save_source_snapshot_to_file`, `modelDestination`, `requestLog`/`requestHistoryActions`) through `StreamingRun.snapshot()` or a thin façade built on it, keeping the characterised streaming tests green.
- Decide whether any additional façade-level tests are needed once canvases or destinations consume the `StreamingRun` snapshot directly (for example, to assert how partial/error streams are rendered).


## 2025-12-11 – Streaming Response & Snapshot slice – streaming snapshot canvas view helper

Focus (kind: guardrail/tests): Add a small, canvas-friendly adapter over `StreamingRun.snapshot()` so response canvases and tests can consume streaming state through a stable façade without changing existing canvas behaviour yet.

### Changes
- Updated `lib/streamingCoordinator.py`:
  - Added `canvas_view_from_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]`:
    - Normalises the snapshot’s `text`, `completed`, `errored`, and `error_message` fields into a simple `{"text", "status", "error_message"}` mapping.
    - Derives `status` as one of `"inflight"`, `"completed"`, or `"errored"`, with errors taking precedence over completion.
    - Treats missing or `None` fields as empty strings/False booleans so callers see a consistent shape.
- Extended `_tests/test_streaming_coordinator.py` with `test_canvas_view_from_snapshot_maps_status_and_text`:
  - Constructs three `StreamingRun` instances representing inflight, completed, and errored streams, using `new_streaming_run` and the existing façade methods.
  - Asserts that `canvas_view_from_snapshot(run.snapshot())` returns:
    - `text` equal to the accumulated streamed text for each run.
    - `status` equal to `"inflight"`, `"completed"`, or `"errored"` as appropriate.
    - `error_message` preserved for the errored case and empty otherwise.

### Rationale
- This slice advances ADR-0045’s Streaming Response & Snapshot façade by:
  - Defining a small, UI-agnostic adapter that expresses streaming state in a form `modelResponseCanvas` can consume in future slices without depending on the full snapshot shape.
  - Keeping all streaming semantics inside the existing `StreamingRun` façade while giving canvases/tests a narrow, well-characterised view.
- It stops short of wiring the adapter into `modelResponseCanvas` itself; that work remains in the Salient Tasks subproject.

### Checks
- Ran focused streaming façade tests:
  - `python3 -m pytest _tests/test_streaming_coordinator.py`
  - Result: **7 passed**, 0 failed.


## 2025-12-11 – Pattern Debug & GPT Action slice – GUI debug flow mapping

Focus (kind: status/decomposition): Make the remaining Pattern Debug GUI debug subproject more concrete by explicitly mapping the current GUI debug entrypoint that relies on `_debug`-style helpers and reflecting that mapping in ADR-0045’s Salient Tasks.

### Changes
- Updated `docs/adr/0045-concordance-axis-config-help-hub-streaming-churn.md` under **Salient Tasks → Pattern Debug & GPT Action Orchestration** so that the GUI debug subproject now:
  - Marks the "Maps the concrete GUI debug flows and entrypoints that currently rely on `_debug`-style helpers" subtask as completed.
  - Notes that, today, this mapping consists of the `modelPatternGUI._debug` path exercised and characterised by `_tests/test_model_pattern_gui.py`.
- Left the remaining GUI debug subtasks (defining the minimal coordinator-facing API, migrating a representative GUI debug flow to the coordinator, and extending tests for the remaining flows) as unchecked for future behaviour slices.

### Rationale
- This slice tightens ADR-0045’s Pattern Debug & GPT Action subproject by:
  - Making the "map GUI debug flows" subtask concrete and clearly tied to the existing `modelPatternGUI._debug` entrypoint and its test coverage.
  - Clarifying what remains for future loops: defining the coordinator API expected by GUI flows, migrating at least one GUI debug path to the coordinator, and extending tests accordingly.
- It does not change runtime behaviour; instead, it finishes the decomposition/status work for this particular Pattern Debug GUI mapping subtask so later behaviour slices can target specific entrypoints with less ambiguity.

### Checks
- Re-ran Pattern Debug GUI tests to confirm the mapped entrypoint remains covered:
  - `python3 -m pytest _tests/test_model_pattern_gui.py`
  - Result: **25 passed**, 0 failed.


## 2025-12-11 – Pattern Debug & GPT Action slice – GUI debug coordinator view helper

Focus (kind: behaviour): Introduce a minimal, coordinator-facing view helper for Pattern Debug GUI flows so they can consume a concise, stable pattern debug view from the shared coordinator instead of re-parsing snapshots.

### Changes
- Updated `lib/patternDebugCoordinator.py`:
  - Added `pattern_debug_view(pattern_name: str) -> dict[str, object]`:
    - Calls `pattern_debug_snapshot(pattern_name)` and returns `{}` when no snapshot is available.
    - Extracts `name`, `static_prompt`, and `axes` (including `completeness`, `scope`, `method`, `style`, and `directional`) from the snapshot without changing the snapshot shape.
    - Normalises `scope`, `method`, and `style` values to token lists whether they are stored as strings or lists.
    - Builds a concise `recipe_line` using the existing pattern separator (`" · "`) from `static_prompt`, `completeness`, joined `scope`/`method`/`style` tokens, and `directional`, falling back to the raw `recipe` when needed.
    - Returns a small view dict:
      - `{"name": name, "recipe_line": recipe_line, "axes": axes, "last_axes": snapshot.get("last_axes") or {}}`.
- Extended `_tests/test_model_pattern_gui.py`:
  - Imported `pattern_debug_view` from `talon_user.lib.patternDebugCoordinator`.
  - Added `test_pattern_debug_view_builds_gui_friendly_recipe_line`:
    - Seeds `GPTState.last_axes` for the `"Debug bug"` pattern with `completeness=["full"]`, `scope=["narrow"]`, `method=["debugging"]`, `style=[]`.
    - Calls `view = pattern_debug_view(target.name)` and asserts:
      - `view["name"] == target.name`.
      - `view["axes"]` mirrors the axes shape already characterised by `pattern_debug_snapshot` tests, including `directional="rog"`.
      - `view["recipe_line"] == "describe · full · narrow · debugging · rog"`.
      - `view["last_axes"] == GPTState.last_axes`.

### Rationale
- This slice defines the minimal coordinator-facing API expected by GUI debug flows in ADR-0045:
  - `pattern_debug_view` provides a GUI-friendly view over the existing `pattern_debug_snapshot` without changing snapshot structure.
  - GUI code and tests can now depend on a small, named helper for pattern debug views rather than re-parsing recipes or digging into raw snapshots.
- It directly advances the Pattern Debug GUI subproject’s "Defines the minimal coordinator-facing API" subtask.

### Checks
- Ran focused Pattern Debug & GPT Action tests including the new helper:
  - `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_gpt_actions.py`
  - Result: **77 passed**, 0 failed.


## 2025-12-11 – Pattern Debug & GPT Action slice – GUI pattern debug user action

Focus (kind: behaviour): Add a small GUI-level pattern debug action that consumes the coordinator’s `pattern_debug_view` so Pattern GUI flows have a shared, test-backed way to surface pattern debug information.

### Changes
- Updated `lib/modelPatternGUI.py` in `UserActions`:
  - Added `model_pattern_debug_name(pattern_name: str)`:
    - Lazily imports `pattern_debug_view` from `patternDebugCoordinator`, notifying `"GPT: Pattern debug helper unavailable"` if the import or call fails.
    - Calls `pattern_debug_view(pattern_name)` and, when it returns an empty view, notifies `"GPT: No pattern debug info for '<pattern_name>'"` and returns.
    - For a populated view, extracts `name`, `recipe_line`, and `axes` and builds a short, multi-line notification:
      - `Pattern debug: <name>`
      - `Recipe: <recipe_line>` (when present)
      - `Axes: <axes>` (when non-empty), using the same axes shape as existing snapshot/view tests.
- Extended `_tests/test_model_pattern_gui.py`:
  - Imported `patch` from `unittest.mock`.
  - Added `test_model_pattern_debug_name_uses_coordinator_view`:
    - Patches `talon_user.lib.patternDebugCoordinator.pattern_debug_view` to return a fixed view for the `"Debug bug"` pattern, including a known `recipe_line` and axes payload.
    - Replaces `actions.app.notify` with a simple function that records messages.
    - Calls `UserActions.model_pattern_debug_name(target.name)` and asserts that:
      - `pattern_debug_view` was called once with the pattern name.
      - Exactly one notification was sent.
      - The notification message contains `"Pattern debug:"`, the pattern name, and the expected `recipe_line`.

### Rationale
- This slice threads the Pattern Debug coordinator into a concrete GUI-level action without changing the existing pattern canvas layout or behaviour:
  - Pattern GUIs now have a dedicated user action that surfaces coordinator-backed debug information instead of relying solely on ad hoc `_debug` logging or GPT-only actions.
  - The new test ensures this GUI debug flow calls the coordinator and reflects its `recipe_line` in the user-facing notification, keeping the coordinator/view contract under test from both GPT and GUI entrypoints.
- It advances ADR-0045’s Pattern Debug & GPT Action objectives by giving GUI flows a first, minimal coordinator-backed debug path while remaining small and low-risk.

### Checks
- Ran focused Pattern Debug & GPT Action tests including the new GUI debug action:
  - `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_gpt_actions.py`
  - Result: **78 passed**, 0 failed.


## 2025-12-11 – Streaming Response & Snapshot slice – modelResponseCanvas streaming behaviours mapping

Focus (kind: status/decomposition): Identify which `modelResponseCanvas` behaviours actually depend on streaming-specific state, as called for by ADR-0045’s Streaming Response & Snapshot Salient Tasks, and record a candidate adapter-integration slice.

### Observations
- `lib/modelResponseCanvas._default_draw_response` uses the current request phase and destination kind to decide when to show streaming progress vs. a static last response:
  - Reads `current_state()` and its `phase` (`RequestPhase.SENDING`, `STREAMING`, `CANCELLED`, `ERROR`, `DONE`) along with `cancel_requested`.
  - Uses `_prefer_canvas_progress()` (which checks `GPTState.current_destination_kind`) to decide when the canvas should prioritise inflight streaming progress over stale content.
- The body text selection is explicitly streaming-aware:
  - Normalises `GPTState.text_to_confirm` and `last_recap_snapshot().get("response", "")` to strings.
  - While `phase` is `SENDING`, `STREAMING`, or `CANCELLED` *and* `_prefer_canvas_progress()` is true, the canvas prefers `text_to_confirm` (the streaming buffer) over any `last_response`.
  - Once inflight conditions are no longer met, it falls back to `text_to_confirm or last_response`, so the final, non-streaming snapshot is shown.
- The header/status text and empty-state messages also depend on streaming state:
  - For inflight, progress-only states with no answer yet, the canvas renders:
    - `"Waiting for model response (sending)…"` when `phase` is `SENDING`.
    - `"Streaming… awaiting first chunk"` when `phase` is `STREAMING`.
    - `"Cancel requested; waiting for model to stop…"` when `phase` is `CANCELLED`.
  - Only when neither inflight progress nor a final response is available does it fall back to `"No last response available."`.
- Existing tests already cover the key streaming-sensitive branches for the canvas:
  - `_tests/test_model_response_canvas.py::test_open_without_answer_is_safe` ensures the canvas does **not** open when there is no answer and no inflight streaming state.
  - `_tests/test_model_response_canvas.py::test_open_allows_inflight_progress_without_answer` patches `current_state()` to `RequestPhase.SENDING` with no `last_response` and asserts that `model_response_canvas_open()` still shows the canvas, relying on the streaming-progress path.
  - `_tests/test_request_streaming.py` covers the upstream streaming façade integration:
    - Ensures `GPTState.text_to_confirm` is populated during streaming and cleared/normalised on completion, so the canvas’s inflight vs. final selection logic has stable inputs.

### Candidate behaviour slice (not implemented in this loop)
- Wire the existing `StreamingRun.snapshot()` → `canvas_view_from_snapshot()` adapter into the response canvas so that:
  - The canvas can consume a per-request streaming snapshot (text + status) instead of inferring inflight vs. final state solely from `RequestState` and `GPTState.text_to_confirm`.
  - Streaming status (`"inflight"`, `"completed"`, `"errored"`) becomes a single, façade-backed input shared between `_send_request_streaming`, canvases, and any future snapshot/log consumers.
- Blockers / reasons to defer to a future behaviour slice:
  - No plumbing currently exposes `StreamingRun.snapshot()` directly to `modelResponseCanvas`; adding that in this loop would require threading a new snapshot field through request state or `GPTState`, touching multiple modules at once.
  - The existing tests for `send_request` and the response canvas (`_tests/test_request_streaming.py`, `_tests/test_model_response_canvas.py`) already characterise the inflight vs. final behaviours; any adapter wiring should be done in a dedicated behaviour slice that keeps these tests green while adding new façade-level checks.

### Rationale
- This slice satisfies ADR-0045’s first Streaming Response & Snapshot subproject task for `modelResponseCanvas` by:
  - Making explicit which parts of the response canvas are streaming-dependent (progress header text, inflight vs. final answer selection, and open/close gating for inflight requests).
  - Recording a concrete, minimal candidate behaviour slice (wiring the `canvas_view_from_snapshot` adapter into the canvas) plus its blockers, so a future loop can focus on adapter integration without redoing this mapping.
- It does not change runtime behaviour; instead, it completes the decomposition/mapping step so subsequent loops can concentrate on façade wiring and additional tests.

### Checks
- Re-confirmed focused streaming/canvas tests to ensure the documented behaviours remain green:
  - `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_request_streaming.py`
  - Result: **21 passed**, 0 failed.

## 2025-12-11 – Streaming Response & Snapshot slice – response canvas streaming façade wiring

Focus (kind: behaviour): Wire the response canvas to consume streaming state via the streamingCoordinator façade and store streaming snapshots on GPTState so UI surfaces share a single streaming view.

### Changes
- Added `GPTState.last_streaming_snapshot` and updated `_send_request_streaming` to refresh this snapshot on every chunk, completion, and error (including cancellation and fallback JSON paths), keeping the façade-backed state available to UI surfaces.
- Updated `modelResponseCanvas` to prefer `canvas_view_from_snapshot` when a streaming snapshot is present, surfacing façade-backed inflight and error states while preserving existing fallbacks; refreshed canvas tests to seed snapshots and patch the adapter directly.
- Tidied streaming tests by seeding a dummy `OPENAI_API_KEY`, clearing `last_streaming_snapshot` in setup, and importing/patching the streamingCoordinator adapter explicitly to exercise the new wiring.
- Adjusted ADR-0045 Current Status and Salient Tasks to mark the response-canvas streaming wiring complete and note that snapshots now flow through `GPTState.last_streaming_snapshot` to the canvas.

### Rationale
- This closes the remaining streaming façade subproject by making `StreamingRun.snapshot()` the shared source of streaming state for canvases, avoiding divergent inflight/error handling paths and aligning runtime behaviour with the façade and tests.

### Checks
- `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_request_streaming.py _tests/test_streaming_coordinator.py`
- Result: **22 passed**, 0 failed.

### Follow-ups
- Consider whether any additional UI surfaces should consume `last_streaming_snapshot` (for example, recap overlays) or surface `error_message` text explicitly; keep streaming tests aligned if those surfaces change.

## 2025-12-11 – ADR-0045 status reconciliation and adversarial completion check

Focus (kind: status): Confirm ADR-0045 has no remaining in-repo tasks after the streaming snapshot/canvas wiring and record an adversarial completion check.

### Summary
- All Salient Tasks in ADR-0045 are now complete, including the response-canvas streaming façade wiring.
- Current Status section updated to remove residual “remaining work” bullets and note optional future UX consumers for streaming snapshots.

### Adversarial check (plausible remaining gaps and why they’re out-of-scope)
- **Axis completeness hints**: Profiles carry free-form completeness hints not present in `axisConfig`. Guardrails already cover scoped axes, catalog alignment, and doc/tests; no change required unless completeness is promoted to a governed axis.
- **Additional streaming consumers**: Other surfaces (for example, recap overlays) could consume `last_streaming_snapshot`, but no user-facing requirement exists; the façade is available if needed.
- **Pattern debug richer views**: Coordinator + GUI action are in place; richer filters/views would be new features, not required to retire ADR-0045 tasks.
- **Help hub vs. quick-help unification**: Navigation façade already in use; quick-help intentionally remains separate with tests covering it. No coordination gap observed.

### Checks
- Relied on the focussed streaming/canvas suite from the previous slice:
  - `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_request_streaming.py _tests/test_streaming_coordinator.py`
  - Result: **22 passed**, 0 failed.

## 2025-12-11 – ADR-0045 loop confirmation (no remaining in-repo work)

Focus (kind: status): Run an adr-loop pass to confirm ADR-0045 remains fully landed and no new in-repo work is required.

### Findings
- Salient Tasks are all checked off in the ADR; streaming snapshots already flow through `GPTState.last_streaming_snapshot` to the response canvas; axis/static prompt, help navigation, and pattern debug domains remain stable with existing guardrails and tests.
- No regressions or new requirements surfaced since the prior completion check; any additional streaming consumers or richer pattern debug views would be new feature asks, not outstanding ADR-0045 tasks.

### Adversarial check
- Re-evaluated prior plausible gaps (completeness hints, other streaming consumers, richer pattern debug views, hub vs. quick-help unification); all remain intentionally deferred unless new UX requirements appear and do not represent incomplete in-repo work for ADR-0045.

### Checks
- No new code changes in this loop; no tests re-run (prior focussed suite remains the latest run for this ADR).

## 2025-12-11 – ADR-0045 loop confirmation (no-op)

Focus (kind: status): Execute the adr-loop helper once more to confirm ADR-0045 stays fully landed with no emerging in-repo tasks.

### Findings
- Salient Tasks remain fully checked off; Axis/Static Prompt, Help Navigation, Pattern Debug, and Streaming domains still aligned with their facades, guardrails, and tests.
- No new scope changes or regressions identified; any future work (for example, additional streaming snapshot consumers or richer pattern debug filters) would constitute new feature asks outside this ADR.

### Adversarial check
- Re-reviewed the previously identified plausible gaps (completeness hints, additional streaming consumers, richer pattern debug views, help/quick-help unification); all remain intentionally deferred and do not represent unfinished ADR-0045 scope.

### Checks
- No code changes; no tests run in this confirmation loop.

## 2025-12-11 – Streaming Response & Snapshot slice – streaming snapshot guardrails

Focus (kind: guardrail/tests): Strengthen ADR-0045’s Streaming Response & Snapshot domain by asserting the streamed snapshot façade is populated for happy-path and timeout scenarios.

### Changes (artefacts: `_tests/test_request_streaming.py`)
- Added assertions in `test_streaming_falls_back_to_non_stream_json_response` and `test_streaming_sse_iter_lines_accumulates_chunks` that `GPTState.last_streaming_snapshot` captures streamed text and marks `completed=True` / `errored=False`.
- Added assertions in `test_streaming_timeout_raises_gpt_request_error` that the snapshot is marked `errored` with a timeout message.
- Removal test: reverting these assertions would stop guarding the snapshot façade and could allow regressions where streaming runs leave stale/empty snapshots despite successful or timed-out requests.

### Checks
- Command: `python3 -m pytest _tests/test_request_streaming.py` (7 passed, exit 0).

### Follow-ups
- None identified for this slice; other surfaces can opt into `last_streaming_snapshot` as needed.

## 2025-12-11 – Streaming Response & Snapshot slice – cancel snapshot guardrail

Focus (kind: guardrail/tests): Ensure the streaming snapshot façade is exercised for cancel flows so ADR-0045’s streaming domain stays covered.

### Changes (artefact: `_tests/test_request_streaming.py`)
- Extended `test_streaming_honours_cancel` to assert that cancelling before streaming accrues leaves `GPTState.last_streaming_snapshot` empty.
- This complements the happy-path and error/timeout snapshot assertions from the prior slice.
- Removal test: reverting would drop coverage for cancel-state snapshot expectations, allowing regressions where cancellation leaves stale or misleading snapshot state.

### Checks
- Command: `python3 -m pytest _tests/test_request_streaming.py` (7 passed, exit 0).

### Follow-ups
- None; cancel snapshot coverage now aligns with happy-path, SSE, and timeout guardrails.

## 2025-12-11 – Streaming Response & Snapshot slice – HTTP error snapshot guardrail

Focus (kind: guardrail/tests): Ensure HTTP error responses populate the streaming snapshot façade per ADR-0045.

### Changes (artefacts: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`)
- In `modelHelpers._send_request_streaming`, when a non-200 streaming request returns a buffered JSON body, the helper now records `streaming_run.on_error("HTTP <code>")`, updates the streaming snapshot, notifies, and raises `GPTRequestError` instead of silently treating the body as a success.
- Added `test_streaming_http_error_marks_snapshot` asserting that HTTP 500 responses mark `GPTState.last_streaming_snapshot` as errored with the status code and no text.
- Removal test: reverting would allow HTTP errors to leave stale/empty snapshots and skip error signalling in the buffered JSON path.

### Checks
- Command (exit 0): `python3 -m pytest _tests/test_request_streaming.py`

### Follow-ups
- None identified; snapshot guardrails now cover happy path, SSE, timeout, cancel, and HTTP error cases.

## 2025-12-11 – ADR-0045 completion confirmation (status, parked)

Focus (kind: status): Apply the tightened loop helper to confirm ADR-0045 is parked with no remaining in-repo work, using fresh evidence.

### Findings
- Salient Tasks remain all checked; streaming snapshot guardrails now cover happy path, SSE, timeout, cancel, and HTTP error scenarios. Axis/Static Prompt, Help Navigation, and Pattern Debug domains have no open tasks.
- No new requirements/regressions recorded since the last guardrail slice; any future streaming consumers or pattern debug enhancements would be new feature work.

### Adversarial check (plausible gaps)
- **New streaming consumers**: Other surfaces (recap overlays) could read `last_streaming_snapshot`, but no failing test or request for that behaviour; façade is available if needed.
- **Axis completeness hints**: Completeness hints remain free-form; existing guardrails/tests cover axis tokens and catalog alignment. Promoting completeness to governed axis would be a new ADR/task.
- **Pattern debug variants**: Coordinator and GUI action exist; richer filters/views are new feature scope, not an unfinished task.
- No evidence of regressions in current suites; no open subtasks.

### Evidence (this loop)
- Command: `python3 -m pytest _tests/test_request_streaming.py` (8 passed, exit 0) — fresh run to cover streaming façade paths.
- Artefacts: `_tests/test_request_streaming.py` (tests), `lib/modelHelpers.py` (façade), ADR/tasks (this work-log entry). No additional code changes in this status loop.
- No artefact attachments needed; test command and exit recorded.

### Decision
- ADR-0045 remains parked; no in-repo work pending. Future loops require a newly recorded task/regression to reopen.

## 2025-12-11 – ADR-0045 loop (blocked)

Focus (kind: status/blocker): No new task/regression recorded; per the loop helper, ADR-0045 remains parked and no compliant slice is available.

### Findings
- ADR-0045 is parked with all Salient Tasks complete and guardrails/tests covering streaming, axis/static prompt, help navigation, and pattern debug domains.
- No new requirements or regressions have been logged; without a new task, running a loop would violate the helper’s “no zero-delta loops” rule.

### Decision
- Skip this loop; await a newly recorded task/regression to reopen ADR-0045 work.

### Evidence
- No code changes; no tests run. This entry records the blocker per the helper.

## 2025-12-11 – Streaming Response & Snapshot slice – clear stale snapshot on non-stream runs

Focus (kind: guardrail/tests): Prevent stale streaming snapshots from leaking into non-stream runs for ADR-0045.

### Changes (artefacts: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`)
- Clear `GPTState.last_streaming_snapshot` at the start of `send_request` so non-stream paths don’t inherit stale streaming state.
- Added `test_non_stream_run_clears_previous_snapshot` asserting that when streaming is disabled, a non-stream run leaves `last_streaming_snapshot` empty.
- Removal test: reverting would allow stale snapshots to persist across non-stream runs, potentially misleading downstream consumers or tests relying on snapshot state.

### Checks
- Command (exit 0): `python3 -m pytest _tests/test_request_streaming.py`

### Follow-ups
- None identified; snapshot lifecycle now resets on non-stream runs.

## 2025-12-11 – Streaming Response & Snapshot slice – response canvas completed snapshot guardrail

Focus (kind: guardrail/tests): Ensure the response canvas consumes completed streaming snapshots when buffers are empty, per ADR-0045.

### Changes (artefact: `_tests/test_model_response_canvas.py`)
- Added `test_completed_snapshot_used_when_no_buffer_or_last_response` to assert that when `GPTState.last_streaming_snapshot` is completed and buffers are empty, the canvas calls `canvas_view_from_snapshot` with the snapshot and uses its text/status.
- Removal test: reverting would drop coverage for the completed snapshot path, allowing regressions where completed streaming responses are ignored when buffers are cleared.

### Checks
- Command (exit 0): `python3 -m pytest _tests/test_model_response_canvas.py _tests/test_request_streaming.py`

### Follow-ups
- None identified; canvas now has guardrails for inflight, errored, and completed streaming snapshots.

## 2025-12-11 – Streaming Response & Snapshot slice – cancel snapshot guardrail (canvas aware)

Focus (kind: guardrail/tests): Keep ADR-0045’s streaming guardrails honest by covering the canvas view when a CancelledRequest is raised via the stubbed streaming helper.

### Changes (artefact: `_tests/test_request_streaming.py`)
- Added snapshot assertions to `test_streaming_cancelled_sets_lifecycle_cancelled` while preserving the stubbed CancelledRequest path; clarified that the stub short-circuits snapshot population, so the snapshot remains empty (matching the earlier “honours cancel” test).
- Removal test: reverting loses visibility into cancel snapshot expectations and could allow regressions where cancellation leaves misleading snapshot state.

### Checks
- Command (exit 0): `python3 -m pytest _tests/test_request_streaming.py`

### Follow-ups
- None identified; snapshot guardrails remain consistent for cancel flows across stubbed and real streaming paths.

## 2025-12-11 – Streaming Response & Snapshot slice – SSE cancel snapshot guardrail

Focus (kind: guardrail/tests): Guard ADR-0045’s streaming façade when cancellation happens mid-SSE.

### Changes (artefact: `_tests/test_request_streaming.py`)
- Added `test_streaming_cancel_during_sse_marks_snapshot_errored` to assert that when an SSE stream is cancelled mid-flight, `last_streaming_snapshot` is marked errored with a cancel message and includes any text streamed before cancellation.
- Removal test: reverting would drop coverage for mid-stream cancels, allowing regressions where snapshots stay empty or misleading after cancellation.

### Checks
- Command (exit 0): `python3 -m pytest _tests/test_request_streaming.py`

### Follow-ups
- None; streaming snapshot guardrails now cover happy path, SSE, timeout, cancel (stubbed and mid-stream), HTTP error, and non-stream resets.

## 2025-12-11 – Axis & Static Prompt Concordance slice – completeness hint guardrail

Focus (kind: guardrail/tests): Ensure static prompt completeness hints stay within governed axis tokens or an explicit free-form allowlist, per ADR-0045.

### Changes (artefact: `_tests/test_static_prompt_completeness_hints.py`)
- Added `StaticPromptCompletenessHintTests.test_completeness_hints_are_axis_tokens_or_allowed_free_form`:
  - Collects completeness values from `STATIC_PROMPT_CONFIG`.
  - Asserts each is either an `axisConfig` completeness token or in the explicit free-form allowlist (`{"path"}`).
  - Reports any unexpected hints to make new additions explicit.
- Removal test: reverting would drop the guardrail and allow silent drift in completeness hints beyond governed tokens or the explicit allowlist.

### Trigger
- `bridge` static prompt profile uses the free-form completeness hint `"path"`, which is not an axis token; we want new free-form hints to be intentional and explicit.

### Checks
- Command (exit 0): `python3 -m pytest _tests/test_static_prompt_completeness_hints.py`

### Follow-ups
- None identified; completeness hints are now governed by axis tokens or the explicit allowlist.

## 2025-12-11 – Axis & Static Prompt Concordance slice – completeness allowlist helper

Focus (kind: guardrail/tests): Centralise the free-form completeness allowlist so ADR-0045’s static prompt guardrails stay explicit and test-backed.

### Changes (artefacts: `lib/staticPromptConfig.py`, `_tests/test_static_prompt_completeness_hints.py`)
- Added `COMPLETENESS_FREEFORM_ALLOWLIST` and `completeness_freeform_allowlist()` to provide a single source for allowed non-axis completeness hints (currently `{"path"}`).
- Updated the completeness hint guardrail test to consume the helper and assert the allowlist is non-empty, keeping the allowlist and guardrail in sync.
- Removal test: reverting would reintroduce duplicated allowlist literals and make new hints harder to govern.

### Trigger
- Free-form completeness hint `"path"` exists; we need the allowlist as a single source of truth instead of repeated literals.

### Checks
- Command (exit 0): `python3 -m pytest _tests/test_static_prompt_completeness_hints.py`

### Follow-ups
- None identified; the allowlist is now centralised and test-backed.

### Checks
- Command (exit 0): `python3 -m pytest _tests/test_static_prompt_completeness_hints.py`

### Follow-ups
- None; allowlist is SSOT and test-backed.

## 2025-12-11 – ADR-0045 completion check (status)

Focus (kind: status/completion): Run a fresh adversarial completion check with evidence and mark ADR-0045 as complete for this repo.

### Changes (artefacts: ADR + work-log)
- Updated ADR status to `Accepted (in-repo complete as of 2025-12-11)` and noted streaming completion under Current Status.
- Recorded this completion check in the work-log with fresh evidence and gap disposition.

### Adversarial check
- Plausible gaps and disposition:
  - New streaming consumers (e.g., recap overlays): no failing tests or requests; would be new feature work via new task/regression.
  - Completeness hints beyond governed tokens/allowlist: guarded by allowlist helper/test; new hints require explicit task/update.
  - Pattern debug richer views/filters: coordinator + GUI action exist; richer UX would be new feature scope.
  - Help hub vs quick-help unification: both façade-backed; further unification would be a new requirement.
- No open subtasks remain; any new work requires a new task/regression entry with a trigger.

### Evidence (fresh this loop)
- Command (exit 0): `python3 -m pytest _tests/test_request_streaming.py _tests/test_model_response_canvas.py _tests/test_static_prompt_completeness_hints.py`
  - Observables: confirms streaming/canvas guardrails and completeness allowlist remain green after the latest changes.

### Decision
- ADR-0045 is complete for this repo and parked; no further loops unless a new task/regression with a trigger is recorded.

## 2025-12-11 – Streaming Response & Snapshot slice – mid-SSE cancel snapshot guardrail

Focus (kind: guardrail/tests): Ensure mid-stream cancellation marks streaming snapshots as errored while preserving partial text, per ADR-0045.

### Changes (artefacts: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`)
- Updated `_send_request_streaming` to set an errored streaming snapshot when cancellation is detected mid-SSE via `current_state` or after the stream loop.
- Added `test_streaming_cancel_mid_sse_marks_snapshot_errored_with_partial_text` asserting that a cancel during SSE raises `CancelledRequest`, marks `last_streaming_snapshot` errored with a cancel message, and retains text streamed before cancel.
- Removal test: reverting would let mid-stream cancels leave snapshots non-errored or empty, masking partial output and error state.

### Checks
- Command (exit 0): `python3 -m pytest _tests/test_request_streaming.py`

### Follow-ups
- None; streaming snapshots now cover mid-stream cancel alongside happy path, timeout, HTTP error, stubbed cancel, and non-stream reset.
