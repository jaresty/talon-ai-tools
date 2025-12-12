# ADR-0044 – Concordance Axis SSOT and Help/Pattern UI Streamlining
Status: Proposed  
Date: 2025-12-11  
Owners: talon-ai-tools maintainers

## Context
- Statement-level churn × complexity scan run with `python scripts/tools/churn-git-log-stat.py` and `python scripts/tools/line-churn-heatmap.py`; artifacts live in `tmp/churn-scan/git-log-stat.txt` and `tmp/churn-scan/line-hotspots.json`.
- Top node-level hotspots (score = churn × complexity × coordination):  
  | Node | Score | Churn | Coordination | Complexity |
  | --- | ---: | ---: | ---: | ---: |
  | lib/axisConfig.py (file) | 18209.26 | 550 | 10498 | 1.73 |
  | lib/modelHelpGUI.py (file) | 8067.00 | 784 | 8067 | 1.00 |
  | lib/modelPatternGUI.py::_debug | 7361.16 | 491 | 6924 | 1.06 |
  | GPT/readme.md (file) | 6164.87 | 360 | 4643 | 1.33 |
  | lib/modelHelpers.py::_append_text | 6003.12 | 233 | 4571 | 1.31 |
  | tests/test_model_pattern_gui.py (historical; now `_tests/`) | 4999.00 | 465 | 4999 | 1.00 |
  | lib/helpHub.py::_draw_result_row | 4598.40 | 314 | 4022 | 1.14 |
  | lib/helpHub.py::_on_mouse | 4409.36 | 282 | 3140 | 1.40 |
  | tests/test_gpt_actions.py (historical; now `_tests/`) | 4398.00 | 544 | 4398 | 1.00 |
  | lib/helpHub.py::_on_key | 3722.32 | 234 | 2828 | 1.32 |
- Hotspot clusters:
  - Axis lexicon + docs SSOT: `lib/axisConfig.py`, `lib/staticPromptConfig.py::completeness_freeform_allowlist`, `GPT/readme.md`, `GPT/gpt.py::static_prompt_description_overrides`, `lib/requestLog.py::_filter_axes_payload`, axis-facing tests (`_tests/test_axis_mapping.py`, `_tests/test_static_prompt_docs.py`, `_tests/test_talon_settings_model_prompt.py`, `_tests/test_readme_axis_lists.py`), stubs.
  - Help / Quick Help / Hub surfaces: `lib/modelHelpGUI.py`, `lib/modelHelpCanvas.py::_default_draw_quick_help`, `lib/helpHub.py::_draw_result_row/_on_mouse/_on_key`, plus navigation/search tests (`_tests/test_help_domain.py`, `_tests/test_model_help_canvas.py`, `_tests/test_model_help_gui.py`, `_tests/test_gpt_actions.py`).
  - Pattern picker + streaming/response assembly: `lib/modelPatternGUI.py::_debug/_draw_pattern_canvas/_on_mouse`, `lib/modelHelpers.py::_append_text/_handle_streaming_error`, `lib/modelResponseCanvas.py::_axis_join`, `lib/modelConfirmationGUI.py::_axis_join`, `lib/modelDestination.py::_slug/_axis_join`, related UI/tests (`_tests/test_model_pattern_gui.py`, `_tests/test_model_response_canvas.py`, `_tests/test_model_destination.py`, `_tests/test_model_helpers_response_canvas.py`).

## Hidden Domains (Concordance)
- Axis lexicon + hydration SSOT: coordination links across static axis lists, prompt metadata, request logging, docs, and tests are implicit; when tokens shift, the blast radius spans UI, prompts, and telemetry. Visibility is low (duplicated copies), scope is repo-wide, volatility is high (550 churn, 10k coordination for `axisConfig.py`).
- Help/pattern discovery surfaces: help hub, quick help canvas, and pattern picker all manage their own state, bounds, and keyboard/mouse semantics with parallel code paths. Visibility of shared contracts is low (per-surface helpers), scope spans multiple canvases, and volatility is high through frequent UI refinements.
- Streaming response & recap composition: response canvas, confirmation GUI, destinations, and streaming helpers each re-implement axis joins and streaming lifecycle hooks. Visibility is medium (helpers exist but scattered), scope spans streaming, rendering, and persistence, and volatility is elevated through cancel/error handling tweaks.

## Problem
Fragmented SSOTs and parallel UI/streaming implementations drive high coordination cost: axis token updates require multi-surface edits; help/pattern UIs drift in focus/scroll semantics; response recap logic diverges across canvases/destinations. These misaligned boundaries inflate Concordance scores by keeping visibility low, scope broad, and volatility high for hotspots that already change often.

## Decision
- Establish a single axis lexicon/hydration SSOT that feeds prompts, docs, telemetry filters, and UI surfaces; regenerate readme/help copies from that source and fail fast when drift appears.  
- Consolidate help/quick-help/pattern canvases behind shared navigation and rendering helpers so pointer/key semantics, hover/focus, and onboarding hints live in one orchestrator; reuse existing `helpDomain` focus/search helpers rather than duplicating event handling.  
- Extract shared response recap/axis-join + streaming lifecycle helpers used by response canvas, confirmation GUI, and destinations, tightening around current `modelResponseCanvas`/`modelDestination` patterns to reduce duplication.  
- Explicitly target reduced Concordance scores by increasing visibility (single SSOT + shared helpers), narrowing scope (central orchestrators reduce blast radius), and lowering volatility (auto-generated docs/tests for axis data) without relaxing guardrails.

## Prior Art and Revised Recommendations
- Axis lexicon + hydration  
  - Original draft: create new axis registry and regenerate all consumers.  
  - Similar existing behavior: `lib/axisMappings.py` already wraps `axisConfig`; `_tests/test_static_prompt_docs.py`, `_tests/test_readme_axis_lists.py`, and `_tests/test_axis_mapping.py` validate mappings and docs; `axis_docs_map` provides SSOT access.  
  - Revised recommendation: extend `axisMappings` to expose a canonical axis registry (tokens, descriptions, aliases) and drive `axisConfig`, `staticPromptConfig`, GPT README snippets, and `requestLog` filtering from that registry; add a guarded generator (make target) plus checks that fail when generated artifacts drift.
- Help / quick-help / pattern surfaces  
  - Original draft: rewrite canvases with a new UI abstraction.  
  - Similar existing behavior: `helpDomain` centralizes search/focus logic; `modelHelpCanvas` and `modelHelpGUI` already share `apply_canvas_typeface` and `_wrap_text`; pattern picker shares axis hydration helpers.  
  - Revised recommendation: factor shared canvas orchestration (layout, bounds, hover/focus, scroll, onboarding text) into a `help_ui` helper used by help hub, quick help, and pattern picker; wire event handling through `helpDomain` navigation helpers; keep surface-specific rendering (buttons/results/pattern tiles) modular.
- Streaming response & recap composition  
  - Original draft: invent a new streaming controller and recap builder.  
  - Similar existing behavior: `_axis_join` variants in `modelResponseCanvas`, `modelConfirmationGUI`, and `modelDestination` already normalize axis tokens; streaming lifecycle hooks live in `modelHelpers` and `requestState`.  
  - Revised recommendation: lift `_axis_join` into a shared presenter in `modelResponseCanvas` (or a small utility module) and reuse it in confirmation/destination code; wrap streaming lifecycle (open/refresh/cancel/error) into a `streaming_presenter` that `modelHelpers` and canvas refresh paths share, honoring existing throttle/meta update patterns.

## Tests-First Refactor Plan
- Axis SSOT alignment  
  - Reuse: `_tests/test_axis_mapping.py`, `_tests/test_static_prompt_docs.py`, `_tests/test_static_prompt_config.py`, `_tests/test_readme_axis_lists.py`, `_tests/test_talon_settings_model_prompt.py`, `_tests/test_axis_docs.py`.  
  - Add: generator drift test that compares emitted `axisConfig.py`/README fragments to the registry; characterization for `requestLog._filter_axes_payload` to ensure axis filtering stays stable.  
  - Branch focus: token additions/removals, alias handling, missing-axis fallbacks.
- Help/pattern surfaces  
  - Reuse: `_tests/test_help_domain.py` (focus/search semantics), `_tests/test_model_help_gui.py`, `_tests/test_model_help_canvas.py`, `_tests/test_model_pattern_gui.py`, `_tests/test_gpt_actions.py`.  
  - Add: characterization for shared hover/focus state transitions (mouse + keyboard) across hub/quick help/pattern surfaces; scroll boundary tests to guard max-scroll clamps.  
  - Branch focus: filter empty vs non-empty paths, hover/drag vs scroll, onboarding toggle.
- Streaming & recap  
  - Reuse: `_tests/test_model_helpers_response_canvas.py`, `_tests/test_model_helpers_meta_throttle.py`, `_tests/test_model_response_canvas.py`, `_tests/test_model_confirmation_gui.py`, `_tests/test_model_destination.py`, `_tests/test_request_streaming.py`, `_tests/test_request_cancel.py`.  
  - Add: shared `_axis_join` utility coverage (tokens missing/empty, multi-axis composites); streaming presenter characterization for cancel/error vs happy path and for buffered vs SSE content-type.  
  - Branch focus: cancel mid-stream, non-stream responses, error propagation to UI refresh.

## Refactor Plan
- Phase 0: introduce an axis registry in `axisMappings` with a generate/check step; regenerate `axisConfig.py` and README snippets; wire `requestLog._filter_axes_payload` and static prompt completeness allowlist to consume the registry.
- Phase 1: extract a `help_ui` canvas helper (layout + input orchestration) used by help hub, quick help, and pattern picker; migrate `helpHub` mouse/key handling to `helpDomain` helpers; keep rendering components thin.
- Phase 2: hoist `_axis_join` into a shared utility and adopt it in response canvas, confirmation GUI, and destinations; wrap streaming lifecycle calls in `modelHelpers` with a small presenter shared with canvas refreshers, preserving existing throttle intervals.
- Phase 3: tighten tests per the Tests-First plan, then iterate small slices (one surface/consumer at a time) with existing suite + new characterization before code moves.

## Consequences
- Positive: axis token changes become single-sourced with clear generation/checks; help/pattern surfaces share consistent navigation semantics; streaming/recap paths align, reducing duplication and Concordance friction.  
- Risks: generator drift or helper extraction may break Talon runtime assumptions; UI refactors can regress hover/scroll handling; streaming presenter may surface latent cancel/timeout bugs.  
- Mitigations: enforce generator checks in CI, land in thin slices with existing + new characterization tests, keep fallback rendering/logging paths intact during migration. Expected effect: lower sustained Concordance scores for axis and help/response hotspots through higher visibility, narrower scope, and lower volatility rather than weakened guardrails.

## Salient Tasks
- [ ] Add axis registry + generator, regenerate `axisConfig.py`/README fragments, and add drift test.  
- [ ] Redirect `requestLog` axis filtering and static prompt allowlist to the registry.  
- [ ] Extract `help_ui` helper and migrate help hub, quick help canvas, and pattern picker to shared navigation/scroll/hover handling.  
- [ ] Centralize `_axis_join` and adopt across response/confirmation/destination code paths.  
- [ ] Wrap streaming lifecycle into a shared presenter and cover cancel/error/buffered paths with characterization tests.  
- [ ] Run `python3 -m pytest` to confirm coverage after each slice.
