# ADR-0044 – Work Log

## 2025-12-11 – Axis join presenter slice

Focus (kind: behaviour/refactor): Centralise the `_axis_join` presenter so response recap surfaces and destinations share token joining semantics.

### Changes
- Added `lib/axisJoin.py::axis_join` to join axis tokens from snapshots/state with consistent fallback handling.
- Refactored `lib/modelResponseCanvas.py`, `lib/modelDestination.py`, and `lib/modelConfirmationGUI.py` to use the shared helper for recipe recaps and file/browser slugs.
- Added `_tests/test_axis_join_helper.py` covering list, empty, string, and missing-axis cases.

### Checks
- `python3 -m pytest _tests/test_axis_join_helper.py _tests/test_model_destination.py _tests/test_model_response_canvas.py` (22 passed).

### Removal test
- Reverting the helper/refactor would reintroduce divergent axis concatenation logic across canvases/destinations and remove the guardrail test, allowing regressions in recipe recap and snapshot slug/header output to go unguarded.

### Follow-ups
- Extend the shared helper to any additional streaming/recap presenters introduced in later ADR-0044 phases.

## 2025-12-11 – Request log axis registry slice

Focus (kind: behaviour/guardrail): Redirect request log axis filtering to the axis registry so history entries stay token-based and SSOT-backed.

### Changes
- Added `axis_registry()`/`axis_registry_tokens()` in `lib/axisMappings.py` to expose canonical axis tokens.
- Updated `lib/requestLog.py::_filter_axes_payload` to use the registry, dropping hydrated strings and unknown tokens for known axes while retaining passthrough for non-axis keys.
- Added `_tests/test_request_log_axis_filter.py` to characterise filtering of known axis tokens, hydrated strings, and passthrough keys.

### Checks
- `python3 -m pytest _tests/test_request_log_axis_filter.py _tests/test_model_destination.py _tests/test_model_response_canvas.py _tests/test_axis_join_helper.py` (passing in this loop).

### Removal test
- Reverting would reintroduce divergent axis filtering, allowing hydrated descriptions and unknown tokens into request history without guardrails or test coverage.

### Follow-ups
- Fold the registry into the planned generator/SSOT work so axis token lists and README fragments remain derivable from a single source.

## 2025-12-11 – Help UI scroll helper slice

Focus (kind: behaviour/guardrail): Introduce a shared help UI helper for scroll clamping and adopt it in Help Hub and quick-help canvas to align navigation semantics.

### Changes
- Added `lib/helpUI.py` with `clamp_scroll`, `apply_scroll_delta`, and `scroll_fraction`.
- Refactored `lib/helpHub.py` to use the shared helper for scrollbar clicks, wheel deltas, and page-up/down key handling.
- Refactored `lib/modelHelpCanvas.py` scroll handling to use the helper instead of inline clamps.
- Added `_tests/test_help_ui.py` to guard the helper’s clamp/fraction semantics.

### Checks
- `python3 -m pytest _tests/test_help_ui.py _tests/test_help_hub.py _tests/test_model_help_canvas.py` (23 passed).

### Removal test
- Reverting would reintroduce duplicated clamp logic across help surfaces and drop coverage for scroll bounds/fraction calculations, risking drift in scroll behaviour between Help Hub and quick-help.

### Follow-ups
- Extend the helper to pattern picker navigation/hover handling to finish the ADR task to unify help/pattern surfaces.

## 2025-12-11 – Pattern picker scroll helper slice

Focus (kind: behaviour/guardrail): Apply the shared help UI scroll helper to the pattern picker and characterise scroll bounds so help/pattern surfaces share navigation semantics.

### Changes
- Refactored `lib/modelPatternGUI.py` to use shared scroll helpers: added `_visible_rows`, `_max_scroll_offset`, and `_scroll_pattern_list` (clamped via `helpUI.clamp_scroll`) for both mouse and high-level scroll handlers and clamped row offsets in the renderer.
- Added `_tests/test_model_pattern_gui_scroll.py` to guard max-offset computation and clamping; adjusted `test_model_pattern_debug_name_uses_coordinator_view` patching to import modules directly.

### Checks
- `python3 -m pytest _tests/test_help_ui.py _tests/test_help_hub.py _tests/test_model_help_canvas.py _tests/test_model_pattern_gui_scroll.py _tests/test_model_pattern_gui.py` (52 passed).

### Removal test
- Reverting would drop shared clamping in the pattern picker and the new scroll guardrails, allowing hover/scroll behaviour to drift from Help Hub/quick help and reintroducing unbounded row offsets.

### Follow-ups
- None for scroll; next slices can reuse the shared helper for hover/focus orchestration if pattern navigation is expanded.

## 2025-12-11 – Axis registry drift guardrail slice

Focus (kind: guardrail/tests): Add a drift guardrail for the axis registry so the SSOT stays aligned with axisConfig and Talon list tokens.

### Changes
- Added `_tests/test_axis_registry_drift.py` asserting `axis_registry()` matches `AXIS_KEY_TO_VALUE` keys and GPT list tokens for completeness/scope/method/style/directional axes.

### Checks
- `python3 -m pytest _tests/test_axis_registry_drift.py _tests/test_axis_mapping.py` (18 passed).

### Removal test
- Reverting would drop the registry drift guardrail, allowing axis registry tokens to diverge from axisConfig or Talon lists without detection.

### Follow-ups
- Still need the generator step to produce `axisConfig.py`/README fragments from the registry; this guardrail sets the baseline for that work.

## 2025-12-11 – Axis registry generator slice

Focus (kind: guardrail/tests): Add a generator for axisConfig content derived from the registry and guard against drift.

### Changes
- Added `scripts/tools/generate_axis_config.py` with `render_axis_config()` to emit `AXIS_KEY_TO_VALUE` (and supporting dataclasses) from the axis registry and `render_axis_markdown()` to generate README-ready token fragments.
- Extended `_tests/test_axis_config_generator.py` to assert generated maps match axisConfig and markdown output includes all axes/tokens.

### Checks
- `python3 -m pytest _tests/test_axis_config_generator.py _tests/test_axis_registry_drift.py _tests/test_axis_mapping.py` (19 passed).

### Removal test
- Reverting would drop the generator/markdown helpers and guardrails, allowing axisConfig/registry and README fragments to drift undetected.

### Follow-ups
- Wire the generator into a make target and use the markdown output to refresh README snippets so docs stay synced with the registry.

## 2025-12-11 – Streaming snapshot presenter slice

Focus (kind: guardrail/refactor): Introduce a shared streaming snapshot presenter so streaming snapshot updates are single-sourced and covered by tests.

### Changes
- Added `record_streaming_snapshot` to `lib/streamingCoordinator.py` to persist `StreamingRun` snapshots to `GPTState` and return a copy.
- Updated `lib/modelHelpers.py` to use the shared helper for all streaming snapshot updates instead of ad hoc assignment.
- Extended `_tests/test_streaming_coordinator.py` to cover the new helper and reran streaming tests to ensure behaviour is unchanged.

### Checks
- `python3 -m pytest _tests/test_streaming_coordinator.py _tests/test_request_streaming.py` (20 passed).

### Removal test
- Reverting would restore inline snapshot updates and drop the guardrail, risking inconsistent snapshot writes across streaming code paths.

### Follow-ups
- Expand the presenter to cover lifecycle events/notifications if further streaming refactors are needed.

## 2025-12-11 – Streaming lifecycle helper slice

Focus (kind: guardrail/refactor): Centralise streaming lifecycle events (chunk/error/complete) behind streamingCoordinator helpers to keep snapshot writes consistent.

### Changes
- Added `record_streaming_chunk`, `record_streaming_error`, and `record_streaming_complete` in `lib/streamingCoordinator.py` to pair lifecycle events with snapshot persistence.
- Refactored `lib/modelHelpers.py` streaming path to use the new helpers for all chunk/error/complete updates.
- Extended `_tests/test_streaming_coordinator.py` to cover `record_streaming_snapshot`; reran streaming guardrail suite.

### Checks
- `python3 -m pytest _tests/test_streaming_coordinator.py _tests/test_request_streaming.py` (20 passed).

### Removal test
- Reverting would reintroduce ad hoc snapshot writes for streaming lifecycle events, risking divergence across happy-path, buffered, timeout, and cancel/error flows.

### Follow-ups
- Consider a small lifecycle wrapper for request state transitions if additional streaming refactors land.

## 2025-12-11 – Streaming lifecycle presenter tests slice

Focus (kind: guardrail/tests): Characterise the streaming lifecycle presenter helpers so chunk/error/complete paths stay aligned with canvas views.

### Changes
- Added `_tests/test_streaming_lifecycle_presenter.py` covering `record_streaming_chunk/error/complete` and their canvas-view projections.
- Reran streaming coordinator and request streaming suites to ensure behaviour remains unchanged with the new helpers.

### Checks
- `python3 -m pytest _tests/test_streaming_lifecycle_presenter.py _tests/test_streaming_coordinator.py _tests/test_request_streaming.py` (22 passed).

### Removal test
- Reverting would drop lifecycle presenter coverage, allowing snapshot/view regressions to slip into chunk/error/complete paths unnoticed.

### Follow-ups
- None identified for lifecycle coverage; further streaming refactors can build on the presenter helpers.

## 2025-12-11 – ADR-0044 completion check (status)

Focus (kind: status/completion): Confirm ADR-0044 tasks are complete in-repo with fresh evidence.

### Findings
- All Salient Tasks are checked: axis registry/generator + drift guardrails; requestLog/static prompt allowlist redirected; help/pattern navigation helpers shared; `_axis_join` centralised; streaming lifecycle presenter + tests landed; pytest runs accompany each slice.
- Generated axis artifacts (`tmp/axisConfig.generated.py`, `tmp/readme-axis-tokens.md`) available via `make axis-regenerate`.

### Evidence
- Command: `python3 -m pytest _tests/test_axis_config_generator.py _tests/test_readme_axis_lists.py _tests/test_streaming_lifecycle_presenter.py _tests/test_streaming_coordinator.py _tests/test_request_streaming.py` (pass).
- Artefacts reviewed: `docs/adr/0044-concordance-axis-ssot-help-hub-streamlining.md` (status set to Accepted), generator outputs in `tmp/`.

### Adversarial check
- Plausible gaps: future README integration of generated markdown; optional lifecycle wrapper for request state transitions. Both would be new scope/feature work; no failing tests or regressions.

### Decision
- ADR-0044 is complete for this repo; parked unless new tasks/regressions are recorded.

## 2025-12-11 – Axis generator make target slice

Focus (kind: tooling/guardrail): Wire the axis registry generator into tooling to produce axisConfig and README fragments for drift checks.

### Changes
- Fixed `scripts/tools/generate_axis_config.py` import path so it can run via `PYTHONPATH=.` from the repo root.
- Added `axis-regenerate` Makefile target to emit `tmp/axisConfig.generated.py` and `tmp/readme-axis-tokens.md` from the registry.
- Regenerated the artifacts via `make axis-regenerate` as a reference output.

### Checks
- `make axis-regenerate`
- `python3 -m pytest _tests/test_axis_config_generator.py _tests/test_readme_axis_lists.py` (5 passed).

### Removal test
- Reverting would drop the reproducible generation path and make it harder to detect drift between the registry, axisConfig, and README snippets.

### Follow-ups
- Consider plugging the generated README fragment into the README update process or CI drift checks.

## 2025-12-11 – Axis registry generator slice

Focus (kind: guardrail/tests): Add a generator for axisConfig content derived from the registry and guard against drift.

### Changes
- Added `scripts/tools/generate_axis_config.py` with `render_axis_config()` to emit `AXIS_KEY_TO_VALUE` (and supporting dataclasses) from the axis registry.
- Added `_tests/test_axis_config_generator.py` that execs the rendered module and asserts the generated `AXIS_KEY_TO_VALUE` matches the current axisConfig mapping.

### Checks
- `python3 -m pytest _tests/test_axis_config_generator.py _tests/test_axis_registry_drift.py _tests/test_axis_mapping.py` (19 passed).

### Removal test
- Reverting would drop the generator and its guardrail, allowing axisConfig/registry drift to go undetected and blocking future README regeneration from the SSOT.

### Follow-ups
- Wire the generator into a make target and use it to emit README snippets so docs stay in sync with the registry.
