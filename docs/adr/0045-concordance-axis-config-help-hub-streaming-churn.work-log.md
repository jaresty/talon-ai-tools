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
