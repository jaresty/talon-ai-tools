# ADR-0036 – Concordance – Static Prompt Axis SSOT and GUI Alignment
Status: Accepted  
Date: 2025-12-10  
Owners: Talon AI tools maintainers

## Context
- Churn × complexity heatmap (`tmp/churn-scan/line-hotspots.json`, generated 2025-12-03) over `lib/`, `GPT/`, `copilot/`, `tests/` with git-log fixture in `tmp/churn-scan/git-log-stat.txt`.
- Top hotspots (score = churn × complexity × coordination):
  - `lib/staticPromptConfig.py:StaticPromptProfile` (Class, line 11) — score 4070.5, churn 547, coordination 3537, complexity 1.15
  - `lib/modelPatternGUI.py:_axis_value` (Function, line 61) — 2754.2, churn 172, coordination 2707.0
  - `GPT/readme.md` (File) — 2607.9, churn 130, coordination 1813.0
  - `lib/talonSettings.py:_read_axis_value_to_key_map` (Function, line 45) — 1764.5, churn 178, coordination 1619.0
  - `lib/modelHelpGUI.py:model_help_gui` (Function, line 169) — 1623.2, churn 83, coordination 1265.0
  - `GPT/gpt.py:_build_static_prompt_docs` (Function, line 118) — 1413.4, churn 116, coordination 1123.0
  - `lib/modelPromptPatternGUI.py:prompt_pattern_gui` (Function, line 189) — 1328.5, churn 69, coordination 1153.0
  - `lib/modelPatternGUI.py:Match` (Class, line 249) — 1297.7, churn 64, coordination 1058.0
  - `lib/talonSettings.py:modelPrompt` (Function, line 160) — 1208.9, churn 80, coordination 972.0
  - `GPT/lists/staticPrompt.talon-list` (File) — 988.5, churn 393, coordination 1050.0
- Clusters from the heatmap:
  - **Static prompt catalog + docs surfaces**: `lib/staticPromptConfig.py`, `GPT/gpt.py::_build_static_prompt_docs`, `GPT/readme.md`, `GPT/lists/staticPrompt.talon-list` — high coordination between config, Talon list vocabulary, and documentation text.
  - **Axis hydration across GUIs and Talon settings**: `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`, `lib/modelHelpGUI.py`, `_load_axis_map/_axis_value` helpers, `lib/talonSettings.py` axis resolution, plus `_tests` coverage (`test_model_pattern_gui.py`, `test_talon_settings_model_prompt.py`, `test_axis_overlap_alignment.py`).
  - **Suggestion / rerun pipeline surfaces**: `GPT/gpt.py` functions around suggest/rerun (`gpt_suggest_prompt_recipes_with_source`, `gpt_rerun_last_recipe`), `lib/modelSuggestionGUI.py`, integration tests (`_tests/test_gpt_actions.py`, `_tests/test_integration_suggestions.py`).

### Concordance (hidden domains)
- **Static prompt “catalog + docs” domain**: Visibility is low because semantics are spread across `STATIC_PROMPT_CONFIG`, the Talon list, `_build_static_prompt_docs`, and README prose. Scope is broad (CLI, docs, GUIs, tests) and volatility high (547 churn; 3537 coordination), making every description tweak ripple through doc builders and tests.
- **Axis hydration + UI orchestration domain**: Visibility of axis contracts is implicit inside multiple `_load_axis_map/_axis_value` helpers and Talon settings hydrators; callers reconstruct axis text and tokens differently per GUI. Scope spans state (`GPTState`), pattern/help/suggestion canvases, and Talon settings; volatility shows in repeated churn across `_tests` for axis mapping and GUI match objects.
- **Suggestion/rerun orchestration domain**: Visibility is mixed because the orchestration between `PromptPipeline`, suggestion GUIs, and rerun commands relies on ad hoc state updates (`last_recipe`, match objects). Scope crosses async request handling and UI insertion, and volatility shows in paired churn between `GPT/gpt.py` functions and `_tests/test_gpt_actions.py`.

## Problem
- Coordination cost is high because static prompt semantics and axis docs lack a single source of truth; updates require touching configs, lists, docs, and UI builders, driving Concordance scores up.
- Axis hydration and token/state handling are duplicated across GUIs and Talon settings, so changes to axis lists or priority rules propagate unpredictably and repeatedly.
- Suggest/rerun flows mix orchestration with UI and state updates, obscuring contracts for `last_*` fields and making tests brittle when behaviour shifts.

## Decision
- Establish a **static prompt catalog SSOT** that feeds Talon lists, default axis profiles, and documentation text from one module, with a generated doc block consumed by README/GUIs to increase visibility and narrow scope of edits.
- Introduce a **shared axis hydration/mapping service** (extending `lib/axisMappings.py`) as the only API for token⇄description, axis priority, and recap/rerun canonicalisation; GUIs and Talon settings consume it instead of reloading lists independently.
- Separate **suggest/rerun orchestration** from UI bindings: a thin coordinator owns `last_recipe/last_*` updates and prompt reconstruction, while GUIs call it through clear facades. This aims to reduce volatility when UI surfaces change.
- Explicitly target lower Concordance scores for the hotspots by increasing visibility of contracts, constraining scope of edits to SSOT modules, and reducing volatility through shared orchestrators rather than weakening scoring/guardrails.

## Tests-First Principle
> Before any behaviour- or boundary-changing refactor, confirm branch-level coverage of the affected paths. Add focused characterization tests only where existing suites do not cover the branches being changed; otherwise, rely on and extend current tests. Do not proceed with refactors without adequate coverage of true/false, error, and gating paths.

## Refactor Plan
- **Phase 1 – Static prompt catalog SSOT**
  - Extract a `static_prompt_catalog` helper that renders Talon list entries, axis defaults, and doc text from `STATIC_PROMPT_CONFIG`; have `_build_static_prompt_docs` and README pulls read from it.
  - Generate or validate `GPT/lists/staticPrompt.talon-list` from the catalog to prevent drift and document the generation boundary.
- **Phase 2 – Axis hydration + UI orchestrators**
  - Extend `axisMappings` with hydrated descriptions and priority rules (covering multi-token scope/method) and expose a `AxisDocs` facade consumed by pattern/help/suggestion GUIs and `talonSettings.modelPrompt`.
  - Replace GUI-local `_load_axis_map/_axis_value` with the shared service; keep canvas rendering logic only in GUI modules.
- **Phase 3 – Suggest/rerun coordination**
  - Introduce a coordinator that owns suggestion result shaping and `last_*` updates, with explicit inputs/outputs for rerun and recap; route `gpt_suggest_prompt_recipes_with_source`, `gpt_rerun_last_recipe`, and GUI callbacks through it.
  - Clarify state/hydration boundaries (token vs hydrated text) so recap/rerun do not depend on ad hoc reverse mapping.

## Revised Recommendations (with prior art)
- **Static prompt catalog SSOT**
  - Original draft: centralise static prompt descriptions and axis defaults; regenerate docs and lists from one place.
  - Similar existing behavior: `lib/staticPromptConfig.py` already defines profiles; `_build_static_prompt_docs` and README manually re-render them; ADR-030 defines token hydration boundaries.
  - Revised recommendation: wrap `STATIC_PROMPT_CONFIG` in a catalog module that emits Talon list lines, default axis tokens, and hydrated doc strings; wire `_build_static_prompt_docs` and README generation to that API; lint `staticPrompt.talon-list` against the catalog in `_tests/test_static_prompt_docs.py`.
- **Axis hydration + UI orchestration**
  - Original draft: replace GUI-local axis map loaders with a shared hydrator.
  - Similar existing behavior: `lib/axisMappings.py`/`axisConfig.py` host token maps; ADR-030 mandates token-first storage with hydration at boundaries; `GPTState` recap/rerun already canonicalise tokens.
  - Revised recommendation: extend `axisMappings` with a hydrated view and priority resolver; export a small façade (`AxisDocs`) used by `modelPatternGUI`, `modelPromptPatternGUI`, `modelHelpGUI`, `modelSuggestionGUI`, and `talonSettings.modelPrompt` for both hydration and recap token sets; keep GUI rendering and canvas layout local.
- **Suggest/rerun coordination**
  - Original draft: split suggestion result shaping and rerun prep into a dedicated coordinator.
  - Similar existing behavior: `PromptPipeline`/`RecursiveOrchestrator` (lib/modelPatternGUI.py, GPT/gpt.py) already centralise request flow; `_tests/test_prompt_pipeline.py` and `_tests/test_recursive_orchestrator.py` cover orchestration.
  - Revised recommendation: add a coordinator (module or class) that takes prompt inputs, applies axis/static prompt catalog hydration, returns both model-facing and recap-friendly state, and updates `GPTState`. Reuse `PromptPipeline` for execution and `GPTState` for storage; GUIs call the coordinator instead of mutating state directly.

## Tests-First Refactor Plan
- **Static prompt catalog SSOT**
  - Existing coverage: `_tests/test_static_prompt_config.py`, `_tests/test_static_prompt_docs.py`, `_tests/test_readme_axis_lists.py` validate profiles and doc rendering.
  - Plan: add a characterization test that asserts the catalog renders both Talon list lines and doc strings identically for a sampled prompt (including axis defaults). Use existing tests for regression after wiring `_build_static_prompt_docs` and README to the catalog.
- **Axis hydration + UI orchestration**
  - Existing coverage: `_tests/test_model_pattern_gui.py`, `_tests/test_prompt_pattern_gui.py`, `_tests/test_model_help_gui.py`, `_tests/test_model_suggestion_gui.py`, `_tests/test_talon_settings_model_prompt.py`, `_tests/test_axis_overlap_alignment.py`.
  - Plan: before refactor, assert current hydration/recap outputs for one GUI flow and `modelPrompt` (including multi-token scope and prefixed tokens). After introducing the shared hydrator, reuse these tests plus a new small test on the façade to guard priority/description mapping; avoid duplicating GUI rendering checks.
- **Suggest/rerun coordination**
  - Existing coverage: `_tests/test_gpt_actions.py` (rerun and suggest behaviours), `_tests/test_integration_suggestions.py`, `_tests/test_prompt_pipeline.py`, `_tests/test_recursive_orchestrator.py`, `_tests/test_prompt_session.py`.
  - Plan: add a focused characterization test for the new coordinator to confirm `last_recipe/last_*` updates and rerun input formation stay stable; rely on existing integration tests for behavioural verification post-refactor.

## Consequences
- Positive: Higher visibility through SSOT catalog and shared hydrator should reduce coordination blasts when prompts or axis lists evolve, lowering sustained Concordance scores for the identified hotspots. Rerun/suggestion flows gain clearer contracts, reducing brittleness across UI and async paths.
- Risks: Introducing a catalog generator and hydrator façade could regress Talon list parsing or GUI rendering if boundaries are misdrawn; mitigate with characterization tests and incremental wiring. Coordination modules add indirection; keep APIs small and documented.
- Mitigations: Phase work so existing tests stay green before and after each wiring step; keep token-vs-hydrated boundaries explicit per ADR-030 to avoid state drift.

## Salient Tasks
- [x] Add `static_prompt_catalog` helper and unit test that round-trips to Talon list lines and doc text.
- [x] Wire `_build_static_prompt_docs` and README static prompt section to the catalog; add drift check in `_tests/test_static_prompt_docs.py`.
- [x] Extend `axisMappings` with hydrated views and priority resolver; expose façade consumed by pattern/help/suggestion GUIs and `modelPrompt`.
- [x] Replace GUI-local axis loaders with façade calls; keep rendering logic local and covered by existing GUI tests.
- [x] Introduce suggestion/rerun coordinator that owns `last_*` updates; route `gpt_suggest_prompt_recipes_with_source`/`gpt_rerun_last_recipe` through it and add a focused characterization test.

## Current Status
- Phase 1: catalog SSOT implemented and tests added; static prompt docs consume the catalog.
- Phase 2: axis hydration routed through `axisMappings` façade across pattern/prompt/help/suggestion GUIs; response/help hubs read snapshots.
- Phase 3: suggestion/rerun/recap state consolidated via `suggestionCoordinator` (`record/entries/source`, grammar hints, snapshots, clear helpers); `gpt` actions and canvases consume the coordinator; targeted suites are green (`python3 -m pytest _tests/test_static_prompt_docs.py _tests/test_axis_mappings.py _tests/test_model_pattern_gui.py _tests/test_prompt_pattern_gui.py _tests/test_model_help_canvas.py _tests/test_model_suggestion_gui.py _tests/test_model_response_canvas.py _tests/test_gpt_actions.py _tests/test_suggestion_coordinator.py`).
