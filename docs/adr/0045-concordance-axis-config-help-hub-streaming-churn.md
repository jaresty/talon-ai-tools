# ADR-0045 – Concordance – Axis Config, Help Surfaces, and Streaming Churn
Status: Proposed  
Date: 2025-12-11  
Owners: Talon AI tools maintainers

## Context
- Statement-level churn × complexity heatmap generated on 2025-12-11:
  - `since`: 90 days ago
  - `scope`: `lib/`, `GPT/`, `copilot/`, `tests/`
  - `limit`: 200
  - JSON: `tmp/churn-scan/line-hotspots.json`
  - Git log fixture: `tmp/churn-scan/git-log-stat.txt`
- Top **node-level hotspots** (by `score = totalChurn × avgComplexity × totalCoordination_weight`):
  - `lib/axisConfig.py` (File, line 1) — score ≈ **18209.3**, churn **550**, coordination **10498.0**, avgComplexity **1.73**.
  - `lib/modelHelpGUI.py` (File, line 1) — score **8067.0**, churn **784**, coordination **8067.0**, avgComplexity **1.0**.
  - `lib/modelPatternGUI.py::_debug` (Function, line 91) — score ≈ **7361.2**, churn **491**, coordination **6924.0**, avgComplexity **1.06**.
  - `GPT/readme.md` (File, line 1) — score ≈ **6164.9**, churn **360**, coordination **4643.0**, avgComplexity **1.33**.
  - `lib/modelHelpers.py::_append_text` (Function, line 752) — score ≈ **5018.4**, churn **181**, coordination **3857.0**, avgComplexity **1.30**.
  - `tests/test_model_pattern_gui.py` (File) — score **4999.0**, churn **465**, coordination **4999.0**, avgComplexity **1.0**.
  - `lib/helpHub.py::_draw_result_row` (Function, line 236) — score ≈ **4598.4**, churn **314**, coordination **4022.0**.
  - `lib/helpHub.py::_on_mouse` (Function, line 472) — score ≈ **4409.4**, churn **282**, coordination **3140.0**.
  - `tests/test_gpt_actions.py` (File) — score **4398.0**, churn **544**, coordination **4398.0**.
  - `lib/helpHub.py::_on_key` (Function, line 627) — score ≈ **3722.3**, churn **234**, coordination **2828.0**.
  - `GPT/gpt.py::static_prompt_catalog` (Function, line 51) — score ≈ **3560.3**, churn **284**, coordination **3267.0**.
  - `tests/test_talon_settings_model_prompt.py` (File) — score **3464.0**, churn **319**, coordination **3464.0**.
  - `lib/staticPromptConfig.py::StaticPromptProfile` (Class, line 12) — score ≈ **3431.4**, churn **453**, coordination **3036.0**.
  - `tests/test_static_prompt_docs.py` (File) — score **3388.0**, churn **304**, coordination **3388.0**.
  - `lib/modelHelpers.py::_handle_max_attempts_exceeded` (Function, line 977) — score ≈ **3083.2**, churn **135**, coordination **2256.0**.
  - `lib/modelResponseCanvas.py::_axis_join` (Function, line 675) — score ≈ **2811.2**, churn **268**, coordination **2283.0**.
  - `lib/modelHelpCanvas.py::_default_draw_quick_help` (Function, line 488) — score ≈ **2770.5**, churn **473**, coordination **2420.0**.
  - `GPT/gpt.py::_save_source_snapshot_to_file` (Function, line 445) — score ≈ **2688.2**, churn **176**, coordination **2009.0**.
  - `lib/modelHelpers.py::_handle_streaming_error` (Function, line 650) — score ≈ **2590.3**, churn **107**, coordination **2191.0**.

### Hotspot clusters
From these nodes and their neighbouring tests/callers, we infer four main hotspot clusters:

1. **Axis config + static prompt catalog + docs surfaces**
   - Code: `lib/axisConfig.py`, `lib/staticPromptConfig.py::StaticPromptProfile`, `GPT/gpt.py::static_prompt_catalog`.
   - Docs/surfaces: `GPT/readme.md` sections describing axes and static prompts.
   - Tests: `tests/test_static_prompt_docs.py`, `tests/test_talon_settings_model_prompt.py`.
   - Pattern: high churn and coordination around axis configuration, static prompt profiles, and how these are exposed in docs and Talon settings.

2. **Help hub + help canvas quick-help surfaces**
   - Code: `lib/modelHelpGUI.py` (entire file), `lib/helpHub.py::_draw_result_row`, `_on_mouse`, `_on_key`, `lib/modelHelpCanvas.py::_default_draw_quick_help`.
   - Tests: `tests/test_help_hub.py`, `tests/test_model_help_canvas.py` (by scope and prior ADRs).
   - Pattern: repeated edits to keyboard/mouse handling, row rendering, and quick-help layout for help/search; high coordination with GPT docs and axis/static prompt domains.

3. **Pattern GUI debug + GPT action orchestration**
   - Code: `lib/modelPatternGUI.py::_debug`.
   - Tests: `tests/test_model_pattern_gui.py`, `tests/test_gpt_actions.py`.
   - Pattern: frequent changes to how pattern GUIs expose state for debugging and how GPT actions drive pattern- and suggestion-related flows (recap/rerun, axis/state inspection).

4. **Streaming error handling + response canvas + file snapshots**
   - Code: `lib/modelHelpers.py::_append_text`, `_handle_streaming_error`, `_handle_max_attempts_exceeded`, `lib/modelResponseCanvas.py::_axis_join`, `GPT/gpt.py::_save_source_snapshot_to_file`.
   - Code (adjacent): `lib/modelDestination.py` save-to-file helpers, `lib/requestLog.py`, `lib/requestHistoryActions.py`.
   - Tests: `tests/test_model_response_canvas.py`, `tests/test_model_destination.py`, `tests/test_request_streaming.py`, `tests/test_request_log.py`, `tests/test_request_history_actions.py`.
   - Pattern: churn around how streaming output is accumulated, how axis information is rendered into canvases, and how snapshots/logs are written to disk.

### Concordance framing
Concordance here measures how these clusters coordinate across **visibility** (how obvious their links are), **scope** (how broadly their changes propagate), and **volatility** (how often they change). The goal is to find hidden domains where coordination is expensive and then reduce their sustained Concordance scores over time by improving structure, tests, and guardrails—not by weakening checks or narrowing coverage.

## Problem
- **Axis config and static prompt semantics are tightly coupled but spread across domains.**
  - Axis semantics and Concordance-relevant tuning live in `lib/axisConfig.py`, `lib/staticPromptConfig.py`, `GPT/gpt.py::static_prompt_catalog`, Talon lists, and README/docs.
  - High churn and coordination indicate that even small changes to axis semantics or static prompt profiles ripple through config, docs, Talon settings, and tests.
- **Help hub and quick-help surfaces embody a high-churn, low-visibility domain.**
  - Mouse/keyboard handling and row rendering for help/search are concentrated in a few large functions and files, with many edits across quick-help and hub.
  - The hidden domain that links help content, navigation behaviour, and axis/static prompt docs is not clearly bounded or named.
- **Pattern GUI debug flows and GPT action orchestration share an implicit coordination domain.**
  - The `_debug` path in `modelPatternGUI` and tests for GPT actions co-evolve, reflecting a shared but implicit domain that ties pattern state, debug surfaces, and user-facing GPT actions.
  - This domain lacks a clear coordinator/facade; patterns of use must be inferred from scattered helpers and tests.
- **Streaming error handling and response canvases coordinate across many layers.**
  - Text accumulation, error handling, axis rendering, and snapshot writes are interconnected across helpers, canvases, destinations, and logs.
  - Churn in error scenarios or partial-response handling can produce brittle behaviour across UI and persistence, with limited centralized visibility into the policies in effect.

## Hidden domains and Concordance analysis

### 1. Axis config + static prompt catalog + docs
- **Visibility**
  - Axis and static prompt semantics are partially visible in docs and Talon lists, but their authoritative semantics live in configuration modules and helper functions.
  - The link between `axisConfig`, `staticPromptConfig`, `static_prompt_catalog`, Talon lists, and README sections is implicit; contributors must know to update several places.
- **Scope**
  - Changes here affect: Concordance scoring and axis interpretation, static prompt choices in GUIs, docs/help text, and Talon settings flows.
  - Tests span unit, integration, and docs-level suites, so a single semantic change may require many updates.
- **Volatility**
  - High churn and coordination scores indicate frequent iteration on axis semantics, static prompts, and documentation surfaces.

**Hidden domain / tune**: *Axis & Static Prompt Concordance Domain* — governance over axis definitions, static prompt profiles, and how they are documented and exposed across GUIs, docs, and Talon settings.

### 2. Help hub + help canvas quick-help
- **Visibility**
  - Help hub behaviour (search results, navigation, keyboard/mouse interaction) is buried inside large GUI helpers with mixed responsibilities: drawing, state transitions, navigation logic.
  - Contracts between help content providers, navigation behaviour, and quick-help layout are implicit.
- **Scope**
  - Changes affect multiple surfaces: full help hub, quick-help canvas, possibly GPT docs and axis/static prompt sections.
  - Tests cover high-level behaviour but the underlying domain is not explicitly bounded.
- **Volatility**
  - High churn and coordination reflect ongoing evolution of help experiences, especially around discoverability and keyboard-driven navigation.

**Hidden domain / tune**: *Help Navigation & Quick-Help Domain* — coordination of help content, keyboard/mouse navigation, and quick-help layout across canvas and hub surfaces.

### 3. Pattern GUI debug + GPT action orchestration
- **Visibility**
  - The contract between pattern GUIs, debug flows (`_debug`), and GPT actions is implicit in spread-out helpers and tests.
  - Debug behaviour and orchestration logic mix with rendering and event-handling code, obscuring the underlying domain.
- **Scope**
  - Changes here reach across GUIs, GPT actions, request orchestration, and tests that assert behaviour of pattern-driven interactions.
- **Volatility**
  - High churn in `_debug` and associated tests suggests frequent iteration on how patterns are surfaced, debugged, and acted upon.

**Hidden domain / tune**: *Pattern Debug & GPT Action Orchestration Domain* — shared intent around exposing pattern state, wiring debug flows, and coordinating GPT actions that depend on pattern inspection.

### 4. Streaming errors + response canvas + snapshots
- **Visibility**
  - Streaming error-handling policies and text-accumulation behaviour are implemented in helper functions that are widely used but not clearly owned by a single domain.
  - The link between streaming errors, canvas rendering (including axis rendering), and snapshot file destinations is not surfaced through a coherent API.
- **Scope**
  - Changes to error handling or streaming accumulation propagate across request handling, UI canvases, persistent logs, and file destinations.
- **Volatility**
  - Repeated edits to streaming helpers, axis join logic, and snapshot functions indicate an evolving response/telemetry story.

**Hidden domain / tune**: *Streaming Response & Snapshot Resilience Domain* — coordination between streaming output accumulation, error-handling policies, axis rendering into canvases, and on-disk snapshots/logs.

## Decision
We will treat these four hidden domains as first-class Concordance domains and evolve the code to:

- **Axis & Static Prompt Concordance**
  - Consolidate axis and static prompt semantics behind clear, named facades that serve as the single home for Concordance-relevant configuration.
  - Make the relationships between configuration, docs, Talon lists, and GUIs explicit, with well-documented entrypoints for each surface.

- **Help Navigation & Quick-Help**
  - Extract help navigation and quick-help behaviour into dedicated domain helpers/facades, separating rendering from navigation logic.
  - Make keyboard/mouse contracts explicit, so help-related churn is absorbed in a small, well-tested surface.

- **Pattern Debug & GPT Action Orchestration**
  - Introduce a coordinator for pattern-debug flows that clarifies contracts between pattern GUIs, debug outputs, and GPT actions.
  - Route tests and GUIs through this coordinator rather than custom `_debug` paths.

- **Streaming Response & Snapshot Resilience**
  - Centralize streaming error-handling and text accumulation policies, and clarify how axis rendering and snapshots participate in those policies.
  - Provide clear, testable APIs for writing snapshots and logs so downstream behaviour is easier to reason about.

For each domain, our intent is to **lower sustained Concordance scores** for the associated hotspots by:

- Increasing **visibility** of contracts and boundaries (fewer hidden cross-module links).
- Narrowing **scope** of coordination (more work contained within domain facades and helpers).
- Reducing **volatility** at high-impact boundaries by making them easier to extend safely.

We will not lower scores by weakening Concordance checks, hiding signals, or removing meaningful tests.

## Tests-First Principle
> Before modifying behaviour or boundaries in these domains, first confirm that the affected paths are adequately covered by existing tests (with emphasis on true/false branches, error paths, and gating conditions). Add focused characterization tests only where existing suites do not exercise the behaviour about to change; otherwise, rely on and extend current tests. Do not proceed with refactors without this coverage.

## Refactor Plan

### 1. Axis & Static Prompt Concordance Domain
- **Original draft idea**
  - High churn and coordination in `axisConfig`, `staticPromptConfig`, `static_prompt_catalog`, and associated docs/tests indicate a single domain mixing configuration, docs, and UI-facing semantics.
- **Prior art / existing patterns**
  - `lib/axisConfig.py` and `lib/axisMappings.py` define axis tokens, mappings, and boundaries for Concordance.
  - `lib/staticPromptConfig.py` defines `StaticPromptProfile` and related profiles.
  - `GPT/gpt.py::static_prompt_catalog` acts as a catalog façade consumed by docs and GUIs.
  - ADRs: static prompt SSOT and axis-token ADRs (e.g., ADR-0036, ADR-030, ADR-032, ADR-034) already define token-first storage and hydration-at-boundaries guidance.
- **Revised recommendation**
  - Treat `static_prompt_catalog` and `axisConfig` as part of a single **Axis & Static Prompt Concordance** domain with the following properties:
    - Axis semantics and static prompt profiles are defined in one cohesive configuration layer.
    - Docs (README, GPT/help surfaces), Talon lists, and Talon settings consume this layer through explicit, small APIs.
  - Align `axisConfig` and `static_prompt_catalog` naming and responsibilities so it is clear which module owns:
    - Token definitions and Concordance scoring input.
    - Human-readable descriptions for docs and help.
    - Default selections for static prompts and axis profiles.
  - Reduce duplication between README sections, help surfaces, and tests by leaning on a shared catalog API.

### 2. Help Navigation & Quick-Help Domain
- **Original draft idea**
  - Help hub and quick-help logic appear in large, mixed-responsibility functions with frequent churn, indicating a hidden domain for help navigation and layout.
- **Prior art / existing patterns**
  - `lib/helpHub.py` provides search and navigation logic for help.
  - `lib/modelHelpGUI.py` and `lib/modelHelpCanvas.py` render help and quick-help canvases.
  - ADRs around help/discoverability (e.g., ADR-028) and canvas layouts define patterns for separating rendering from orchestration.
- **Revised recommendation**
  - Introduce a **Help Navigation & Quick-Help** façade that:
    - Encapsulates navigation state and keyboard/mouse contracts (next/prev result, open, focus handling) separate from rendering.
    - Provides small, well-documented hooks for `helpHub` and help canvases to render and update UI based on domain-level state.
  - Move repeated row-rendering and event-handling patterns into reusable helpers that can be consumed by both full help hub and quick-help canvases.
  - Ensure the façade exposes clear points to integrate axis/static prompt docs (from the Axis & Static Prompt domain) so help churn doesnt require bespoke wiring each time.

### 3. Pattern Debug & GPT Action Orchestration Domain
- **Original draft idea**
  - `_debug` in `modelPatternGUI` and coupled tests in `test_model_pattern_gui.py` and `test_gpt_actions.py` highlight a shared but implicit domain around pattern debugging and GPT actions.
- **Prior art / existing patterns**
  - `lib/promptPipeline.py` and `lib/recursiveOrchestrator.py` orchestrate prompt flows.
  - `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`, and related canvases implement pattern displays and interactions.
  - ADRs for pattern GUI and suggestion/rerun coordination (e.g., ADR-0037, ADR-029, ADR-043) already discuss orchestrator-based patterns.
- **Revised recommendation**
  - Define a **Pattern Debug & GPT Action** coordinator that:
    - Exposes a clear API for pattern inspection and debug output generation (e.g., structured view of active patterns, axis state, and last actions).
    - Is called by `modelPatternGUI`, GPT actions, and tests, replacing ad hoc `_debug` entrypoints.
    - Integrates with existing orchestrators (`promptPipeline`, `recursiveOrchestrator`) rather than duplicating orchestration logic.
  - Update tests to target the coordinator where appropriate, keeping GUI-specific tests focused on rendering and layout rather than replicating orchestration logic.

### 4. Streaming Response & Snapshot Resilience Domain
- **Original draft idea**
  - Churn in `modelHelpers` streaming helpers, response canvas axis join logic, and snapshot functions points to a coordinated domain managing streaming response behaviour and persistence.
- **Prior art / existing patterns**
  - `lib/modelHelpers.py` provides streaming and error-handling helpers.
  - `lib/modelResponseCanvas.py` renders streamed responses and axis information.
  - `lib/modelDestination.py` and `GPT/gpt.py::_save_source_snapshot_to_file` implement save-to-file paths.
  - `lib/requestLog.py` and `lib/requestHistoryActions.py` track logs and history.
  - ADRs around file destinations and logging (e.g., ADR-0038, ADR-0039) already define some persistence patterns.
- **Revised recommendation**
  - Create a small **Streaming Response & Snapshot** façade that:
    - Defines streaming accumulation policies (e.g., how partial responses are buffered, how errors truncate or annotate output).
    - Owns the contract for when and how snapshots/logs are written to disk, integrating with existing destination modules.
    - Exposes a consistent interface used by canvases, destinations, and logs so that changing streaming behaviour is localised.
  - Align axis-related rendering (`_axis_join`) with this façade so that axis display behaviour is clearly coupled to streaming state when necessary but not hard-wired into individual canvases.

## Tests-First Refactor Plan
For each domain, we will:

1. Identify the **affected modules/functions** and existing tests.
2. Assess **branch-level coverage** (true/false paths, error/exception paths, gating conditions, early returns).
3. Define a **tests-first plan** that lists required characterization tests (where coverage is insufficient) and the tests that will guard new behaviour.
4. Prefer extending existing tests over adding near-duplicates; focus on behavioural/contract-level assertions.

### Axis & Static Prompt Concordance
- **Existing coverage (non-exhaustive)**
  - `tests/test_static_prompt_docs.py` — static prompt docs and list alignment.
  - `tests/test_talon_settings_model_prompt.py` — Talon settings model prompt behaviour.
  - `tests/test_readme_axis_lists.py` — README axis list rendering.
- **Plan**
  - Before refactors, add focused characterization tests where needed to assert:
    - Axis definitions and descriptions for a sample of axes round-trip consistently through `axisConfig`, `static_prompt_catalog`, README, and help/docs surfaces.
    - Static prompt profiles used in GUIs and Talon settings match catalog definitions.
  - After introducing or tightening facades:
    - Reuse these tests and add small façade-specific tests that validate inputs/outputs (e.g., catalog API returns expected structures for docs and help).

### Help Navigation & Quick-Help
- **Existing coverage (non-exhaustive)**
  - `tests/test_help_hub.py` — help hub behaviour and navigation.
  - `tests/test_model_help_canvas.py` — quick-help canvas interactions.
- **Plan**
  - Characterize current navigation behaviour for:
    - Keyboard-only navigation across results.
    - Mouse-based selection and focus transitions.
    - Interaction between quick-help and full help hub.
  - After extracting the navigation façade:
    - Add small unit tests on the façade for navigation state transitions.
    - Keep existing canvas tests to validate rendering and integration, adjusting them to use the façade.

### Pattern Debug & GPT Action Orchestration
- **Existing coverage (non-exhaustive)**
  - `tests/test_model_pattern_gui.py` — pattern GUI behaviour.
  - `tests/test_gpt_actions.py` — GPT actions (including debug-related flows).
  - `tests/test_prompt_pipeline.py`, `tests/test_recursive_orchestrator.py` — prompt orchestration.
- **Plan**
  - Characterize current `_debug` output and how GPT actions consume or expose it.
  - Add focused tests for the new coordinator that:
    - Verify debug output shape and key fields.
    - Confirm that GPT actions call the coordinator as expected.
  - Rely on existing integration tests for end-to-end behaviour, updating them only where behaviour changes are intended.

### Streaming Response & Snapshot Resilience
- **Existing coverage (non-exhaustive)**
  - `tests/test_model_response_canvas.py` — response canvas behaviours.
  - `tests/test_model_destination.py` — save-to-file destinations.
  - `tests/test_request_streaming.py` — streaming request behaviour.
  - `tests/test_request_log.py`, `tests/test_request_history_actions.py` — logging and history.
- **Plan**
  - Characterize current behaviour for:
    - Normal streaming (no errors): how text is appended, how axes are rendered, when snapshots are written.
    - Error scenarios: partial responses, max-attempts exceeded, streaming errors.
  - Add façade-level tests that:
    - Verify streaming accumulation policies and error-handling decisions.
    - Assert snapshot/log write contracts (e.g., when a snapshot should be present and what metadata it includes).
  - Keep existing tests as end-to-end guards and extend them with cases that exercise new façade behaviours where appropriate.

## Current Status (2025-12-11)

- **Axis & Static Prompt Concordance**
  - In-repo guardrails and facades in place:
    - Guardrail tests enforce that profiled static prompt axes (scope/method/style/directional) use valid `axisConfig` tokens.
    - `modelPrompt` behaviour is characterised so that static prompt profile axes flow into `GPTState.last_axes` when no spoken modifiers override them.
    - `static_prompt_description_overrides()` and `static_prompt_catalog()` now act as the primary docs/README-facing facades for static prompt descriptions and catalog structure.
  - Remaining work for this repo:
    - Introduce a slightly higher-level catalog/facade API (built on the current helpers) and tighten Talon settings / GUI consumers to use it consistently.
    - Decide how completeness hints that are not present in `axisConfig` should be handled (pure hints vs. promoted axis tokens) and update tests/docs accordingly.

- **Help Navigation & Quick-Help**
  - In-repo behaviour/guardrails:
    - Help Hub navigation already delegates search/focus to `helpDomain` helpers, with tests characterising keyboard navigation and result focus.
    - Hub buttons that open other overlays (Quick help, Patterns, History, HTML docs, Suggestions) now close the hub before opening the target surface, with tests guarding this close-before-open behaviour.
  - Remaining work for this repo:
    - Decide whether quick-help should share a small navigation façade with Help Hub (for example, for focus movement), or remain a separate, focused surface with its own state.

- **Pattern Debug & GPT Action Orchestration**
  - In-repo behaviour/guardrails:
    - `pattern_debug_snapshot()` in `modelPatternGUI` provides a structured, tested view of pattern recipes and axes plus current `GPTState` axes.
    - `pattern_debug_catalog()` in `patternDebugCoordinator` exposes a coordinator-style catalog of pattern debug snapshots (optionally filtered by domain), built on `pattern_debug_snapshot`.
    - `UserActions.gpt_show_pattern_debug` surfaces a concise, user-facing pattern debug view by querying the coordinator and rendering a short recipe line plus last-axes payload.
    - GPT action tests around async blocking and meta notifications now directly guard the `actions.app.notify` contract.
  - Remaining work for this repo:
    - Decide how far to extend the Pattern Debug coordinator (for example, adding a "last run" view or richer filters) and whether any GUI flows should consume it directly instead of relying on local helpers like `_debug`.

- **Streaming Response & Snapshot Resilience**
  - In-repo behaviour/guardrails:
    - Streaming request behaviour (happy path, cancellation, JSON fallback, SSE, and timeout) is characterised and guarded by tests, including lifecycle status transitions.
    - Source and destination snapshots have tests for headers and slugs that encode axis/static-prompt context and source type, built on the shared `last_recipe_snapshot()` / `recipe_header_lines_from_snapshot()` façade in `suggestionCoordinator`.
    - The `max_attempts` non-streaming failure path in `send_request` is explicitly tested to mark the lifecycle as `errored` and raise a clear error.
    - Request history entries in `requestLog` now store token-only axis state filtered through `axisMappings`, dropping obviously hydrated axis descriptions before logging, with tests guarding this behaviour.
    - A small `streamingCoordinator` façade (`StreamingRun` plus helpers) now exists as a test-backed accumulator for per-request streaming state, and `_send_request_streaming` uses `StreamingRun` as its in-memory accumulator while preserving existing canvas and lifecycle behaviour.
  - Remaining work for this repo:
    - Thread response canvas updates and snapshot/log writes through the streaming façade behind an explicit policy surface, keeping existing tests green.

## Consequences
- **Positive outcomes**
  - **Lower coordination cost** for axis/static prompt changes by consolidating semantics and exposing clear, reusable facades for docs, help, and Talon settings.
  - **More stable help experiences** by centralizing navigation and quick-help behaviour, reducing brittle coupling between canvases and raw event handlers.
  - **Clearer orchestration for pattern debug and GPT actions**, making it easier to evolve debug flows without scattering changes across GUIs and tests.
  - **More robust streaming and snapshot behaviour**, with explicit policies and APIs that localize complexity and reduce surprises across UI and persistence.
  - Over time, these changes should **reduce sustained Concordance scores** for the identified hotspots, as coordination becomes more obvious, scoped, and resilient.

- **Risks**
  - Extracting new facades and coordinators may introduce temporary indirection and learning curve for contributors.
  - Misaligned boundaries could centralize too much responsibility, reintroducing monolith-like hotspots.
  - Behavioural changes in streaming or help navigation may surprise users if not carefully characterized and tested.

- **Mitigations**
  - Apply the **tests-first refactor plan** for each domain; ensure existing behaviours are characterized before refactors.
  - Phase changes so that each new façade or coordinator is introduced behind existing APIs where possible, then adopted incrementally.
  - Use ADR work-logs or follow-up ADRs only where necessary to document material behavioural shifts; prefer closing loops within this ADRs salient tasks.

## Salient Tasks
- **Axis & Static Prompt Concordance**
  - [x] Map current uses of `axisConfig`, `axisMappings`, `staticPromptConfig`, and `static_prompt_catalog` across libs, GUIs, Talon lists, and docs.
  - [x] Introduce or tighten small catalog/facade APIs that expose axis and static prompt semantics to docs, help, and Talon settings (for example, `static_prompt_catalog`, `static_prompt_description_overrides`, and `static_prompt_settings_catalog`).
  - [x] Adopt these facades in Talon settings and GUI/help surfaces where appropriate, and add/extend tests to characterise cross-surface behaviour and consistency (for example, `modelPrompt` / `GPTState.last_axes` alignment with `static_prompt_settings_catalog`, and quick-help static prompt focus using the shared catalog).

- **Help Navigation & Quick-Help**
  - [x] Extract navigation state and keyboard/mouse contracts into a dedicated help navigation façade (via `helpDomain` helpers such as `help_focusable_items`, `help_next_focus_label`, `help_activation_target`, and `help_edit_filter_text`).
  - [x] Update help hub and help canvas to use the façade for navigation while keeping rendering logic local (for example, `helpHub.focusable_items_for`, `_next_focus_label`, `_focus_step`, and `_activate_focus` delegating into `helpDomain`).
  - [x] Add façade-focused tests and extend existing help/canvas tests to cover key navigation flows (for example, `_tests/test_help_hub.py` focus/activation and filter/edit tests, plus `_tests/test_model_help_canvas.py` quick-help behaviours).

- **Pattern Debug & GPT Action Orchestration**
  - [x] Design and implement a pattern debug coordinator that replaces ad hoc `_debug` entrypoints for non-GUI flows (via `pattern_debug_snapshot` and `pattern_debug_catalog`).
  - [x] Route GPT actions that depend on pattern inspection through this coordinator (for example, `gpt_show_pattern_debug`).
  - [ ] Decide whether and how GUI debug flows should consume the coordinator and extend tests to target those paths where appropriate, via a small subproject that:
    - [x] Maps the concrete GUI debug flows and entrypoints that currently rely on `_debug`-style helpers (for example, the `modelPatternGUI._debug` path exercised by `_tests/test_model_pattern_gui.py`).
    - [ ] Defines the minimal coordinator-facing API needed by those flows (for example, which snapshot fields they consume and how results are rendered).
    - [ ] Migrates at least one representative GUI debug flow to call the coordinator instead of a local `_debug` helper, with focused tests characterising that integration.
    - [ ] Extends or adds tests around remaining GUI debug flows as they are migrated in follow-up loops, until they either use the coordinator or are explicitly documented as out-of-scope.

- **Streaming Response & Snapshot Resilience**
  - [x] Design a small streaming/snapshot façade (for example, a `streamingCoordinator`) around `_send_request_streaming` that owns accumulation and error-handling policies for a single request, without rewiring call sites yet.
  - [x] Add façade-level characterization tests that cover normal streaming, cancellation, JSON fallback, SSE, timeout, and max-attempts behaviour, reusing existing request/streaming tests where possible (primarily `_tests/test_request_streaming.py` and `_tests/test_streaming_coordinator.py`).
  - [ ] Rewire `modelResponseCanvas` to use the streaming façade (or a thin wrapper over `StreamingRun.snapshot()`) for any streaming-specific state it needs, while keeping existing layout and axis rendering semantics unchanged and extending tests to cover the integration, via a small subproject that:
    - [ ] Identifies which `modelResponseCanvas` behaviours actually depend on streaming-specific state (for example, incremental text accumulation vs. final snapshot fields).
    - [x] Introduces a thin adapter or helper that exposes `StreamingRun.snapshot()` data in the shape `modelResponseCanvas` needs, without changing canvas layout or axis rendering semantics (for example, `canvas_view_from_snapshot` in `streamingCoordinator`).
    - [ ] Updates at least one focussed response-canvas test to exercise this adapter path in a happy-path streaming scenario while keeping existing expectations green.
    - [ ] Extends tests (for example, `_tests/test_model_response_canvas.py` and streaming-related tests) to cover any new error or partial-response behaviours introduced by the façade wiring in follow-up loops.
  - [x] Thread snapshot/file/log writes (`_save_source_snapshot_to_file`, `modelDestination`, `requestLog`/`requestHistoryActions`) through the axis/recipe façade (`last_recipe_snapshot` / `recipe_header_lines_from_snapshot`) and axis filtering helpers, with existing tests in `_tests/test_gpt_source_snapshot.py`, `_tests/test_model_destination.py`, `_tests/test_request_log.py`, and `_tests/test_request_history_actions.py` guarding the contracts.
