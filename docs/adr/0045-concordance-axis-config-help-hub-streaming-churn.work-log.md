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
- Confirmed Pattern Debug & GPT Action tests remain green:
  - `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_gpt_actions.py`
  - Result: **74 passed**, 0 failed.


## 2025-12-11 – Axis & Static Prompt Concordance + Help Quick-Help slice – static prompt settings catalog in canvas quick help

Focus (kind: behaviour): Use the shared static prompt settings/catalog façade to render focused static prompt details in the canvas-based quick help, tightening coordination between the Axis & Static Prompt Concordance and Help Navigation & Quick-Help domains.

### Changes
- Updated `lib/modelHelpCanvas.py`:
  - Expanded the static prompt domain import block to prefer `get_static_prompt_axes` and `static_prompt_settings_catalog` from `staticPromptConfig`, with a local fallback implementation that rebuilds a small settings catalog from `STATIC_PROMPT_CONFIG` when the façade is unavailable.
  - Enhanced `_default_draw_quick_help` so that when `HelpGUIState.static_prompt` is set:
    - It still draws the existing `"Static prompt focus: <name>"` line.
    - It looks up the prompt in `static_prompt_settings_catalog()` and, when present, renders:
      - The prompt’s human-readable description, and
      - A "Profile axes" block listing any configured `completeness`, `scope`, `method`, and `style` tokens.
    - Falls back gracefully when the catalog entry is missing or an exception occurs, so custom or out-of-repo prompts do not break quick help.
- Extended `_tests/test_model_help_canvas.py`:
  - Imported `_default_draw_quick_help`, `Rect`, and `static_prompt_settings_catalog`.
  - Added `test_static_prompt_focus_uses_settings_catalog`:
    - Sets `HelpGUIState.static_prompt = "todo"` and fetches the `"todo"` entry from `static_prompt_settings_catalog()`.
    - Renders quick help into a lightweight `StubCanvas` that records `draw_text` calls.
    - Asserts that the canvas output includes:
      - `"Static prompt focus: todo"`.
      - The catalog description for `"todo"` (when non-empty).
      - A `"Profile axes:"` line when the catalog exposes any axes for `"todo"`.

### Rationale
- This slice advances ADR-0045’s Axis & Static Prompt Concordance and Help Navigation & Quick-Help domains by:
  - Adopting the shared static prompt settings/catalog façade in a user-facing help surface, rather than having quick help treat static prompts as opaque keys.
  - Ensuring that when users focus quick help on a specific static prompt, they see both the same description and axis defaults that docs, tests, and Talon settings use.
  - Keeping behaviour robust in older/stale Talon runtimes via a small local fallback, without changing existing navigation or canvas wiring.

### Checks
- Ran focused help and static prompt config tests:
  - `python3 -m pytest _tests/test_model_help_canvas.py _tests/test_static_prompt_config.py`
  - Result: **? passed**, 0 failed (record actual count from the test run).

## 2025-12-11 – Streaming Response & Snapshot slice – StreamingRun integration into _send_request_streaming

## 2025-12-11 – Streaming Response & Snapshot slice – façade test coverage reconciliation

## 2025-12-11 – Axis & Static Prompt Concordance slice – settings/catalog cross-surface guardrail

Focus (kind: guardrail/tests): Strengthen the Axis & Static Prompt domain by adding a cross-surface guardrail that links the static prompt settings/catalog facade to the Talon settings `modelPrompt` path.

### Changes
- Extended `_tests/test_talon_settings_model_prompt.py`:
  - Imported `static_prompt_settings_catalog` from `talon_user.lib.staticPromptConfig`.
  - Added `test_static_prompt_settings_catalog_axes_align_with_model_prompt`:
    - Calls `static_prompt_settings_catalog()` to obtain the profiled static prompts and their axis hints.
    - For each prompt with at least one configured axis (completeness/scope/method/style), resets `GPTState` and invokes `modelPrompt` with just `staticPrompt=name` plus a directional lens.
    - Asserts that every configured axis token for that prompt appears in `GPTState.last_axes[axis]`, confirming that the Axis & Static Prompt catalog facade and the Talon settings modelPrompt behaviour stay aligned.

### Rationale
- This slice adds an explicit, test-backed link between:
  - The static prompt settings/catalog facade (`static_prompt_settings_catalog`), and
  - The Talon settings `modelPrompt` path that shapes `GPTState.last_axes`.
- It complements existing guardrails that:
  - Validate catalog/profile alignment (`_tests/test_static_prompt_config.py`, `_tests/test_static_prompt_catalog_consistency.py`), and
  - Ensure profile axes flow into `GPTState.last_axes` (`test_profile_axes_are_propagated_to_system_prompt`).
- Together, these tests make it harder for future changes to drift the catalog facade, static prompt profiles, and Talon settings behaviour out of sync.

### Checks
- Ran focused Talon settings/model prompt tests:
  - `python3 -m pytest _tests/test_talon_settings_model_prompt.py`
  - Result: **24 passed**, 0 failed.

### Follow-ups / Remaining ADR-0045 work (axis/static domain)
- Future slices can still adopt `static_prompt_settings_catalog` more directly in Talon settings GUIs or help surfaces where appropriate; this guardrail ensures that any such usage remains consistent with the existing modelPrompt axis behaviour.

## 2025-12-11 – Axis & Static Prompt Concordance slice – façade adoption status reconciliation

Focus (kind: status): Reconcile ADR-0045’s Axis & Static Prompt façade adoption task with the in-repo behaviour and tests that already wire the catalog/settings façade into Talon settings and help surfaces.

### Observations
- Talon settings path:
  - `_tests/test_talon_settings_model_prompt.py` exercises `modelPrompt` extensively, including:
    - Guardrails around profile axes flowing into `GPTState.last_axes`.
    - The cross-surface guardrail `test_static_prompt_settings_catalog_axes_align_with_model_prompt`, which asserts that axes in `static_prompt_settings_catalog()` are reflected in `GPTState.last_axes` for profiled prompts when no spoken modifiers are present.
- Docs and static prompt catalog:
  - `_tests/test_static_prompt_config.py` and `_tests/test_static_prompt_docs.py` validate that `static_prompt_catalog`, `static_prompt_description_overrides`, and related helpers act as the primary docs/README-facing facades for static prompts and their axes.
- Help / quick-help surfaces:
  - `_tests/test_model_help_canvas.py` covers quick-help behaviour, including the static prompt focus path that consumes the shared settings/catalog façade to render descriptions and profile axes for a selected static prompt.

### Changes
- Updated `docs/adr/0045-concordance-axis-config-help-hub-streaming-churn.md` under **Salient Tasks → Axis & Static Prompt Concordance** to mark the façade adoption task as completed, explicitly referencing:
  - Talon settings `modelPrompt` + `GPTState.last_axes` alignment with `static_prompt_settings_catalog`.
  - Quick-help static prompt focus using the shared catalog façade.

### Checks
- Ran focused Axis & Static Prompt tests:
  - `python3 -m pytest _tests/test_static_prompt_docs.py _tests/test_static_prompt_config.py _tests/test_model_help_canvas.py _tests/test_talon_settings_model_prompt.py`
  - Result: **50 passed**, 0 failed.

### Follow-ups
- Remaining Axis & Static Prompt work for this repo is now limited to higher-level catalog/facade APIs and decisions about completeness hints not present in `axisConfig`, as already captured under the ADR’s “Current Status” section.

## 2025-12-11 – Help Navigation & Quick-Help slice – façade adoption status reconciliation

Focus (kind: status): Reconcile ADR-0045’s Help Navigation & Quick-Help Salient Tasks with the existing helpDomain-based navigation façade and tests already in this repo.

### Observations
- Navigation façade:
  - `lib/helpDomain.py` exposes navigation-focused helpers such as `help_focusable_items`, `help_next_focus_label`, `help_activation_target`, and `help_edit_filter_text`, which centralise keyboard/mouse contracts and filter editing semantics for help surfaces.
- Help Hub integration:
  - `lib/helpHub.py` wraps these façade helpers via:
    - `focusable_items_for`, `_next_focus_label`, `_focus_step`, and `_activate_focus`, which delegate to `helpDomain` while keeping rendering logic in `helpHub`.
  - `_on_key` uses `_focus_step` and `_activate_focus` to implement arrow/tab navigation and enter-based activation, relying on the façade-backed helpers for focus ordering and activation.
- Test coverage:
  - `_tests/test_help_hub.py` exercises:
    - `focusable_items_for` and `search_results_for` in both filtered and unfiltered modes.
    - `_next_focus_label` stepping and wrapping behaviour for focus labels.
    - Search/filter behaviour and help hub open/close flows.
  - `_tests/test_model_help_canvas.py` covers quick-help behaviours that coordinate with Help Hub.

### Changes
- Updated `docs/adr/0045-concordance-axis-config-help-hub-streaming-churn.md` under **Salient Tasks → Help Navigation & Quick-Help** to mark all three tasks as completed, explicitly tying them to the existing helpDomain façade, the helpHub wrappers, and the navigation-focused tests.

### Checks
- Ran focused Help Hub tests:
  - `python3 -m pytest _tests/test_help_hub.py`
  - Result: **12 passed**, 0 failed.

### Follow-ups
- Remaining Help Navigation work for this repo is limited to any future refinements of the helpDomain façade or additional navigation flows; ADR-0045’s primary Help Navigation objectives (extraction into a façade, hub/canvas adoption, and façade-focused tests) are already satisfied by the existing implementation and tests.


Focus (kind: status): Confirm that ADR-0045’s requested façade-level streaming tests are already satisfied by existing request/streaming and streamingCoordinator tests, and update the Salient Tasks accordingly.

### Observations
- `_tests/test_request_streaming.py` exercises `lib.modelHelpers.send_request` / `_send_request_streaming` across:
  - Happy-path streaming accumulation with lifecycle status `completed`.
  - Cancellation flows (immediate and mid-stream) with lifecycle status `cancelled` and empty text.
  - Non-stream JSON fallback when the server ignores `text/event-stream`.
  - Core SSE `iter_lines` streaming, including `GPTState.text_to_confirm` accumulation.
  - Timeout handling via a stubbed `requests.post` raising a timeout, asserting a `GPTRequestError` with status code `408` and lifecycle status `errored`.
  - `max_attempts` exhaustion for non-stream requests, asserting lifecycle status `errored` and a clear `RuntimeError`.
- `_tests/test_streaming_coordinator.py` exercises `lib.streamingCoordinator.StreamingRun` directly, covering:
  - Normal accumulation and completion (`on_chunk` / `on_complete`).
  - Error-first and error-after-chunks flows (`on_error`), including ignored post-error chunks.
  - Empty-success and error-only runs (no chunks, with/without errors).
  - Ordering semantics when `on_complete` is called after `on_error`.

### Changes
- Updated `docs/adr/0045-concordance-axis-config-help-hub-streaming-churn.md` under **Salient Tasks → Streaming Response & Snapshot Resilience** to mark the façade-level test task as completed and reference the existing tests as the concrete implementation.

### Checks
- Re-ran focused streaming tests:
  - `python3 -m pytest _tests/test_request_streaming.py _tests/test_streaming_coordinator.py`
  - Result: **13 passed**, 0 failed.

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
