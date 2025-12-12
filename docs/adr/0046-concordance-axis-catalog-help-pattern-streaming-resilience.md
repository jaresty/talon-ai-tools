# ADR-0046 – Concordance – Axis Catalog, Help Navigation, Pattern GUIs, and Streaming Resilience
Status: Proposed  
Date: 2025-12-11  
Owners: Talon AI tools maintainers

## Context
- Statement-level churn × complexity heatmap generated on 2025-12-12 (refreshed via `python3 scripts/tools/churn-git-log-stat.py` and `python3 scripts/tools/line-churn-heatmap.py`):
  - `since`: 90 days ago
  - `scope`: `lib/`, `GPT/`, `copilot/`, `tests/`
  - `limit`: 200
  - JSON: `tmp/churn-scan/line-hotspots.json`
  - Git log fixture: `tmp/churn-scan/git-log-stat.txt`
- Top node-level hotspots (score = churn × complexity × coordination):
  - `lib/axisConfig.py` (File, line 1) — score **18209.3**, churn **550**, coordination **10498.0**, avgComplexity **1.73**.
  - `lib/modelHelpGUI.py` (File, line 1) — score **8067.0**, churn **784**, coordination **8067.0**, avgComplexity **1.00**.
  - `GPT/readme.md` (File, line 1) — score **6164.9**, churn **360**, coordination **4643.0**, avgComplexity **1.33**.
  - `lib/modelHelpers.py::_append_text` (Function, line 777) — score **5925.1**, churn **234**, coordination **4487.0**, avgComplexity **1.32**.
  - `tests/test_model_pattern_gui.py` (File, line 1) — score **4999.0**, churn **465**, coordination **4999.0**, avgComplexity **1.00**.
  - `lib/modelPatternGUI.py::_scroll_pattern_list` (Function, line 197) — score **4917.8**, churn **331**, coordination **4472.0**, avgComplexity **1.10**.
  - `lib/helpHub.py::_on_mouse` (Function, line 473) — score **4591.3**, churn **299**, coordination **3332.0**, avgComplexity **1.38**.
  - `lib/helpHub.py::_draw_result_row` (Function, line 237) — score **4586.7**, churn **314**, coordination **4023.0**, avgComplexity **1.14**.
  - `lib/modelResponseCanvas.py::_header_label` (Function, line 617) — score **4434.5**, churn **399**, coordination **3429.0**, avgComplexity **1.29**.
  - `tests/test_gpt_actions.py` (File, line 1) — score **4398.0**, churn **544**, coordination **4398.0**, avgComplexity **1.00**.
- Individual hotspots of note (beyond the above): `lib/staticPromptConfig.py::completeness_freeform_allowlist`, `lib/talonSettings.py::_read_axis_value_to_key_map`, `lib/requestLog.py::_filter_axes_payload`, `lib/requestHistoryActions.py::{history_axes_for,_model_source_save_dir}`, `lib/modelPromptPatternGUI.py::{__init__,_wrap,get_static_prompt_axes}`, `lib/modelHelpers.py::{call_tool,_handle_streaming_error,_handle_max_attempts_exceeded,send_request}`, Talon lists under `GPT/lists/*.talon-list`, and request/prompt orchestration functions in `GPT/gpt.py`.
- Hotspot clusters (by shared responsibility):
  - **Axis + Static Prompt Catalog + Docs/Lists**: `lib/axisConfig.py`, `lib/staticPromptConfig.py`, `GPT/gpt.py::{static_prompt_catalog,static_prompt_description_overrides,_build_static_prompt_docs}`, Talon lists (`staticPrompt.talon-list`, `methodModifier.talon-list`, `styleModifier.talon-list`), `lib/talonSettings.py` axis resolution helpers, README axis/static prompt sections, and tests (`test_static_prompt_docs.py`, `test_talon_settings_model_prompt.py`, `test_static_prompt_config.py`, `test_axis_mapping.py`, `test_readme_axis_lists.py`).
  - **Help Hub + Quick-Help Navigation**: `lib/modelHelpGUI.py`, `lib/helpHub.py::{_draw_result_row,_on_mouse,_on_key,_draw,_build_buttons,_ensure_canvas,help_hub_open}`, `lib/modelHelpCanvas.py::{_default_draw_quick_help,_draw_wrapped_commands,_on_mouse}`, and `tests/test_model_help_gui.py`.
  - **Pattern/Prompt GUIs + GPT Action Wiring**: `lib/modelPatternGUI.py::{_scroll_pattern_list,_draw_pattern_canvas,_on_mouse,_debug}`, `lib/modelPromptPatternGUI.py::{__init__,_wrap,_ensure_prompt_pattern_canvas,_register_handlers,get_static_prompt_axes}`, GPT prompt runners (`gpt_run_prompt`, `gpt_recursive_prompt`, `gpt_analyze_prompt`, `gpt_apply_prompt`), and tests (`test_model_pattern_gui.py`, `test_prompt_pattern_gui.py`, `test_model_suggestion_gui.py`, `test_integration_suggestions.py`, `test_gpt_actions.py`).
  - **Streaming/Response Resilience + History/Snapshots**: `lib/modelHelpers.py::{_append_text,call_tool,_handle_streaming_error,_handle_max_attempts_exceeded,_update_streaming_snapshot,send_request,_update_lifecycle}`, `lib/modelResponseCanvas.py::{_header_label,_format_answer_lines,_wrap_meta,_default_draw_response,_on_mouse,_wrap_text}`, `lib/requestHistoryActions.py`, `lib/requestHistoryDrawer.py`, `lib/requestState.py`, `lib/requestLog.py::_filter_axes_payload`, `lib/modelDestination.py::{append_text,insert,_slug}`, `GPT/gpt.py::_save_source_snapshot_to_file`, and related tests (`test_model_destination.py`, `test_request_history_actions.py`, `test_request_history.py`, `test_model_response_canvas.py`, `test_request_streaming.py`).

## Problem
- Axis semantics, static prompt profiles, and Talon axis tokens evolve together but live across config maps, Talon lists, README/help surfaces, and settings helpers; contributors must touch many files to make coordinated changes, creating high Concordance cost and sustained churn.
- Help hub and quick-help behaviour combine navigation logic, event handling, and rendering in large functions, obscuring contracts between navigation state, axis/static prompt docs, and UI canvases; changes ripple unpredictably.
- Pattern/prompt GUIs, GPT action wiring, and debug flows lack a shared coordinator; `_debug` and scroll/draw handlers embed orchestration details that tests also replicate, leading to duplicated logic and fragile integration points.
- Streaming response handling, canvas rendering, snapshot/log persistence, and request history summarization are coordinated through implicit helper calls rather than a visible policy layer; churn in streaming or cancellation handling cascades into UI, history drawers, and disk persistence.
- Without clearer boundaries and contracts, these clusters continue to generate high Concordance scores; reducing scores requires structural alignment and branch-focused test coverage, not weaker checks or narrower scope.

## Hidden Domains and Concordance Analysis

### Axis & Static Prompt Concordance Domain
- **Members**: `lib/axisConfig.py`, `lib/staticPromptConfig.py`, `GPT/gpt.py` static prompt/catalog helpers, Talon axis/prompt lists, README axis/static prompt sections, `lib/talonSettings.py` axis resolution, axis-related tests.
- **Visibility**: The authoritative axis/static prompt semantics are split across config maps, Talon lists, README prose, and `gpt.py` fallbacks. Contracts between axis tokens, profiles, docs, and Talon settings are implicit.
- **Scope**: Changes propagate to Talon settings (`modelPrompt`), docs (README/help hub), GPT prompt generation, and multiple test suites.
- **Volatility**: High churn and coordination show frequent edits to axis definitions, defaults, and docs. This hidden domain needs an explicit catalog boundary.

### Help Navigation & Quick-Help Domain
- **Members**: `modelHelpGUI`, `helpHub` navigation handlers (`_draw_result_row`, `_on_mouse`, `_on_key`, `_draw`, `_build_buttons`, `_ensure_canvas`, `help_hub_open`), `modelHelpCanvas` quick-help rendering, help GUI tests.
- **Visibility**: Navigation state, event handling, and rendering are interwoven; keyboard/mouse contracts are inferred from large functions. Links to axis/static prompt docs are not surfaced through a façade.
- **Scope**: Changes affect full help hub, quick-help canvases, keyboard/mouse bindings, and potentially doc fragments pulled from the axis/static prompt domain.
- **Volatility**: High churn in handlers and layout functions indicates ongoing iteration on discoverability and interaction patterns.

### Pattern Debug & GPT Action Orchestration Domain
- **Members**: `modelPatternGUI` scroll/draw/debug handlers, `modelPromptPatternGUI` orchestration, GPT action runners (`gpt_run_prompt`, `gpt_recursive_prompt`, `gpt_analyze_prompt`, `gpt_apply_prompt`), suggestion/recap tests.
- **Visibility**: Debug and orchestration paths are embedded inside GUI handlers and mirrored in tests; there is no explicit coordinator to own debug state and GPT action wiring.
- **Scope**: Edits ripple from GUI rendering to GPT actions and integration tests; changes to pattern display or debug flow require adjustments in multiple modules.
- **Volatility**: Repeated edits to scroll/debug handlers and GPT action tests show an unstable coordination surface.

### Streaming Response & Snapshot Resilience Domain
- **Members**: Streaming helpers in `modelHelpers`, response canvas renderers, request history drawers/actions, request state transitions, axis filtering in request logs, snapshot/save helpers in `modelDestination` and `gpt.py`.
- **Visibility**: Streaming policies (chunk handling, cancellation, error treatment), canvas refresh rules, and snapshot/log writes are implicit across several helpers without a single policy owner.
- **Scope**: Behaviour changes affect live UI, persistence, history summaries, and Concordance scoring signals.
- **Volatility**: High churn in streaming append/error handling, canvas wrapping, and history/snapshot helpers shows frequent adjustments to cope with edge cases.

Across domains, coordination friction stems from low visibility (implicit contracts), wide scope (many dependent surfaces), and volatility (frequent edits). The refactor goals aim to increase visibility, narrow scope, and reduce volatility so Concordance scores drop for substantive reasons, not by weakening guardrails.

## Decision
- Treat the four clusters as first-class Concordance domains with explicit boundaries and orchestrators/facades that make contracts visible.
- **Axis & Static Prompt Concordance**: Establish a single catalog façade that owns axis tokens, static prompt profiles, descriptions, and Talon list bindings; route README/help hub/Talon settings through this façade.
- **Help Navigation & Quick-Help**: Extract navigation state/event handling into a dedicated helper separate from rendering; expose small hooks for axis/static prompt doc insertion and quick-help layout.
- **Pattern Debug & GPT Action Orchestration**: Introduce a coordinator for pattern inspection/debug outputs that GUI handlers and GPT actions call instead of bespoke `_debug` and scroll paths; align with existing prompt/pipeline orchestrators.
- **Streaming Response & Snapshot Resilience**: Centralize streaming policies (chunk append, cancellation, error handling, throttling) and downstream rendering/persistence hooks into a shared `StreamingSession`/policy helper that feeds response canvases, history drawers, and snapshot writers.
- For each domain, apply a tests-first approach and prefer extending existing patterns over inventing new ones. The intended long-term effect is to lower sustained Concordance scores for these hotspots by improving structure, visibility, and tests—not by relaxing scoring or hiding signals.

## Tests-First Principle
> Before modifying behaviour or boundaries, confirm the affected paths are adequately covered (true/false branches, error paths, gating conditions). Add focused characterization tests only where existing suites do not exercise the behaviour about to change; otherwise rely on and extend current tests. Do not proceed with refactors without this coverage.

## Refactor Plan (with prior art alignment)

### Axis & Static Prompt Concordance
- **Original Draft**: Consolidate axis/static prompt semantics and docs into a single domain to cut churn across config maps, Talon lists, README/help surfaces, and settings.
- **Similar Existing Behavior**: Current sources of truth include `lib/axisConfig.py`, `lib/staticPromptConfig.py`, `GPT/gpt.py::{static_prompt_catalog,static_prompt_description_overrides,_build_static_prompt_docs}`, Talon lists in `GPT/lists`, and axis helpers in `lib/talonSettings.py`. ADRs 0036/030/032/034/0044/0045 established SSOT and hydration-at-boundaries patterns.
- **Revised Recommendation**:
  - Create an `axis_catalog` façade (or extend `staticPromptConfig`) that exposes typed axis definitions, static prompt profiles, and description overrides with a single export consumed by README generation, help hub, and Talon settings (`modelPrompt`, `_map_axis_tokens`, `_canonicalise_axis_tokens`).
  - Have Talon lists (`staticPrompt.talon-list`, `methodModifier.talon-list`, `styleModifier.talon-list`) generated/validated against the catalog to prevent drift; expose a small validator for tests.
  - Route `GPT/gpt.py` static prompt helpers and `axisConfig` exports through the façade so docs and runtime share the same contract; keep fallbacks minimal and logged.
  - Harden axis payload filtering (`requestLog._filter_axes_payload`) to rely on catalog metadata for visibility/scoping and ensure Concordance scoring inputs remain explicit.

### Help Navigation & Quick-Help
- **Original Draft**: Separate navigation/event handling from rendering to contain help-hub churn and make contracts visible to quick-help canvases.
- **Similar Existing Behavior**: `helpHub` implements navigation/drawing; `modelHelpGUI` and `modelHelpCanvas` render help and quick-help. ADRs 022/028/0044 define canvas separation and discoverability patterns.
- **Revised Recommendation**:
  - Extract a `help_navigation` helper owning selection state, keyboard/mouse handlers, and debounced redraw hooks; have `helpHub` and `modelHelpGUI` consume it rather than embedding logic in `_on_mouse/_on_key/_draw_result_row`.
  - Provide render adapters that accept structured rows from the navigation helper, so quick-help and full hub share layout primitives while keeping rendering isolated.
  - Surface axis/static prompt doc injection via well-named hooks instead of ad hoc string assembly, reducing scope when docs change.

### Pattern Debug & GPT Action Orchestration
- **Original Draft**: Introduce a coordinator for pattern inspection/debug data that GUI handlers and GPT actions call, replacing bespoke `_debug` and scroll/draw coupling.
- **Similar Existing Behavior**: GUI handlers live in `modelPatternGUI`/`modelPromptPatternGUI`; GPT action runners live in `GPT/gpt.py`; orchestrators include `promptPipeline`, `recursiveOrchestrator`, and `suggestionCoordinator`. ADRs 0037/023/024/025/029/043 encourage orchestrator-driven GUI wiring.
- **Revised Recommendation**:
  - Add a `pattern_debug_coordinator` that exposes: current pattern list with axis/state metadata, debug snapshots, and callbacks for scroll/selection changes. GUI handlers delegate to it; GPT actions/tests call the same API for assertions.
  - Align debug output shape with existing orchestrators (PromptPipeline/RecursiveOrchestrator) to avoid duplicating orchestration in `_scroll_pattern_list` and `_debug`.
  - Update tests (`test_model_pattern_gui.py`, `test_prompt_pattern_gui.py`, `test_model_suggestion_gui.py`, `test_gpt_actions.py`, `test_integration_suggestions.py`) to target the coordinator contract rather than GUI internals where possible.

### Streaming Response & Snapshot Resilience
- **Original Draft**: Centralize streaming chunk handling, error policies, canvas refresh, and snapshot/history writes to reduce hidden coupling between `modelHelpers`, response canvases, request history, and destinations.
- **Similar Existing Behavior**: Streaming logic in `modelHelpers` (`_append_text`, `call_tool`, `_handle_streaming_error`, `_handle_max_attempts_exceeded`, `send_request`, `_update_streaming_snapshot`), rendering in `modelResponseCanvas`, history/snapshot helpers in `requestHistoryActions`, `requestHistoryDrawer`, `requestLog`, and `modelDestination`. ADRs 027/031/038/039/044/045 discuss streaming throttles, response canvas refresh, and persistence boundaries.
- **Revised Recommendation**:
  - Introduce a `StreamingSession` (or extend existing request state) that owns chunk accumulation, cancellation, error classification, refresh throttling, and snapshot triggers; `modelHelpers` delegates rather than managing global state.
  - Define explicit hooks for response canvas updates and history/destination writes so `_append_text` and `_handle_streaming_error` no longer directly manipulate UI/logs; canvas/destination modules subscribe to session events.
  - Ensure axis metadata for requests (via `requestLog._filter_axes_payload` and history summaries) is derived from the catalog façade, keeping payload shape visible and testable.

## Tests-First Refactor Plan
- **General approach**: Before each slice, inventory existing tests; add characterization only for uncovered behaviour. Use `python3 -m pytest` from repo root.
- **Axis & Static Prompt Concordance**:
  - Existing coverage: `tests/test_axis_mapping.py`, `tests/test_talon_settings_model_prompt.py`, `tests/test_static_prompt_config.py`, `tests/test_static_prompt_docs.py`, `tests/test_readme_axis_lists.py`.
  - Add/extend tests only where gaps exist:
    - Catalog façade contract: talon list tokens vs catalog profiles, doc/description overrides, fallback handling for missing profiles.
    - Axis payload filtering (`requestLog._filter_axes_payload`) branch coverage for missing/extra axes.
    - README/help generation path uses the same catalog data (avoid snapshot-only assertions; assert structured data used by docs).
- **Help Navigation & Quick-Help**:
  - Existing coverage: `tests/test_model_help_gui.py` (plus prior help ADR suites).
  - Add characterization for navigation helper: keyboard vs mouse selection, empty results, debounce behaviour; branch tests before moving handlers out of `_on_mouse/_on_key`.
- **Pattern Debug & GPT Action Orchestration**:
  - Existing coverage: `tests/test_model_pattern_gui.py`, `tests/test_prompt_pattern_gui.py`, `tests/test_model_suggestion_gui.py`, `tests/test_gpt_actions.py`, `tests/test_integration_suggestions.py`.
  - Characterize coordinator API: debug snapshot shape, selection/scroll events, integration with GPT actions. Keep GUI rendering tests for layout-only aspects.
- **Streaming Response & Snapshot Resilience**:
  - Existing coverage: `tests/test_model_response_canvas.py`, `tests/test_model_destination.py`, `tests/test_request_history_actions.py`, `tests/test_request_history.py`, `tests/test_request_streaming.py`.
  - Add/extend tests where missing:
    - Cancellation and timeout branches in streaming session vs current `_append_text` path.
    - Snapshot/log hooks triggered on stream end/error; ensure history summaries stay consistent when axes are missing or malformed.
    - Canvas refresh throttling behaviour (branch tests for forced vs deferred refresh).
- Behaviour-changing refactors must not proceed until branch-focused coverage exists for the affected path; prefer extending these suites over adding redundant tests.

## Consequences
- **Positive**: Clear domain facades reduce coordination cost, lower sustained Concordance scores, and make README/help/Talon surfaces reuse the same catalog; navigation/pattern/debug/streaming flows become easier to evolve with predictable blast radius.
- **Risks**: Introducing new coordinators can temporarily increase complexity; migration must be phased with tests to avoid regressions. Catalog consolidation risks breaking legacy Talon/runtime fallbacks if not guarded.
- **Mitigations**: Keep facades small and typed; provide transitional adapters; land changes in slices aligned with the Tests-First plan; measure Concordance scores after each slice to ensure reductions come from structural gains rather than weakened checks.

## Salient Tasks (sliceable)
- Establish `axis_catalog` façade and update `GPT/gpt.py`, `lib/axisConfig.py`, `lib/talonSettings.py`, and README/help consumers to use it; add validator tying catalog to Talon lists.
- Extract `help_navigation` helper and route `modelHelpGUI`/`helpHub`/`modelHelpCanvas` handlers through it; backfill navigation branch tests.
- Introduce `pattern_debug_coordinator` and migrate `_scroll_pattern_list`/`_debug`/prompt pattern handlers plus GPT actions/tests to its API.
- Wrap streaming lifecycle in a `StreamingSession` with explicit hooks for response canvas and history/snapshot writers; update `modelHelpers`, `modelResponseCanvas`, and `requestHistoryActions` to consume events; add cancellation/error branch tests.
- After each slice, run `python3 -m pytest` to confirm coverage and use Concordance outputs to verify sustained score reductions for the in-scope hotspots.
