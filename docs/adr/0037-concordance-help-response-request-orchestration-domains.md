# ADR-0037 – Concordance Hotspots for Help, Response, and Request Orchestration Domains

Status: Proposed  
Date: 2025-12-10  
Owners: Talon AI tools maintainers

---

## Context

Over the last 90 days, a fresh statement‑level churn × complexity × coordination heatmap was run over `lib/`, `GPT/`, `copilot/`, and `tests/` using:

- `python scripts/tools/churn-git-log-stat.py` → `tmp/churn-scan/git-log-stat.txt`
- `python scripts/tools/line-churn-heatmap.py` → `tmp/churn-scan/line-hotspots.json`

This ADR builds on ADR‑010, ADR‑0011, and ADR‑0036. Those ADRs have already carved out explicit domains and refactor plans for static prompts, axis mappings, and related GUIs/docs. The latest heatmap shows that, while static‑prompt hotspots have cooled somewhat and are now governed, several **adjacent domains** continue to exhibit high, sustained Concordance scores.

From `tmp/churn-scan/line-hotspots.json` (generated 2025‑12‑10), the top node‑level hotspots by `score = churn × complexity × coordination` now include (illustrative subset):

- `lib/axisConfig.py` (File, `axisConfig.py`, line 1) — very high file‑level churn and coordination.
- `lib/modelHelpGUI.py` (File, `modelHelpGUI.py`, line 1) — high churn in the help GUI orchestration surface.
- `lib/modelPatternGUI.py::_debug` (Function, line 90) — debug/inspection path for pattern GUIs.
- `lib/modelHelpers.py::_append_text` (Function, line 675) — streaming response assembly for GUIs.
- `lib/modelHelpers.py::send_request` (Function, line 863) and `_send_request_streaming` (Function, line 547) — request orchestration and streaming helpers.
- `lib/helpHub.py::_draw_result_row`, `_on_mouse`, `_on_key` — Help Hub rendering and interaction handlers.
- `lib/modelResponseCanvas.py::_axis_join`, `_default_draw_response` — response canvas composition and axis display.
- `lib/requestHistoryActions.py::_filter_tokens` — history token filtering and search surface.
- Tests exercising these behaviours: `tests/test_model_pattern_gui.py`, `tests/test_gpt_actions.py`, `tests/test_talon_settings_model_prompt.py`, `tests/test_static_prompt_docs.py`, `tests/stubs/talon/__init__.py`, and multiple request/history/help/canvas tests.

### Individual Hotspots (nodes)

Representative high‑scoring nodes from `nodes` in `line-hotspots.json`:

- `lib/axisConfig.py :: axisConfig.py` (File, line 1) — `totalChurn ≈ 274`, `totalCoordination ≈ 6850`, `avgComplexity ≈ 1.74`, `score ≈ 11950`.
- `lib/modelHelpGUI.py :: modelHelpGUI.py` (File, line 1) — `totalChurn ≈ 784`, `totalCoordination ≈ 8067`, `avgComplexity ≈ 1.0`, `score ≈ 8067`.
- `lib/modelPatternGUI.py :: _debug` (Function, line 90) — `totalChurn ≈ 492`, `totalCoordination ≈ 6941`, `avgComplexity ≈ 1.06`, `score ≈ 7371`.
- `lib/modelHelpers.py :: _append_text` (Function, line 675) — `totalChurn ≈ 190`, `totalCoordination ≈ 4241`, `avgComplexity ≈ 1.35`, `score ≈ 5714`.
- `GPT/readme.md` (File, line 1) — `totalChurn ≈ 312`, `totalCoordination ≈ 4211`, `avgComplexity ≈ 1.32`, `score ≈ 5547`.
- `tests/test_model_pattern_gui.py` (File, line 1) — `totalChurn ≈ 465`, `totalCoordination ≈ 4999`, `avgComplexity = 1.0`, `score ≈ 4999`.
- `tests/test_gpt_actions.py` (File, line 1) — `totalChurn ≈ 544`, `totalCoordination ≈ 4398`, `avgComplexity = 1.0`, `score ≈ 4398`.
- `lib/modelHelpers.py :: send_request` (Function, line 863) — `totalChurn ≈ 157`, `totalCoordination ≈ 3293`, `avgComplexity ≈ 1.28`, `score ≈ 4216`.
- `lib/helpHub.py :: _draw_result_row` (Function, line 212) — `totalChurn ≈ 262`, `totalCoordination ≈ 3426`, `avgComplexity ≈ 1.17`, `score ≈ 4001`.
- `lib/requestHistoryActions.py :: _filter_tokens` (Function, line 33) — `totalChurn ≈ 118`, `totalCoordination ≈ 2792`, `avgComplexity ≈ 1.40`, `score ≈ 3904`.
- `lib/modelHelpers.py :: _send_request_streaming` (Function, line 547) — `totalChurn ≈ 154`, `totalCoordination ≈ 2905`, `avgComplexity ≈ 1.19`, `score ≈ 3461`.
- `lib/staticPromptConfig.py :: StaticPromptProfile` (Class, line 12) — still prominent (`totalChurn ≈ 453`, `totalCoordination ≈ 3036`, `avgComplexity ≈ 1.13`, `score ≈ 3431`), but now governed by ADR‑0011/ADR‑0036.
- `GPT/gpt.py :: gpt_apply_prompt` (Function, line 527) and `static_prompt_catalog` (Function, line 47) — `score ≈ 3352` and `≈ 3293`, coordinating CLI behaviour and static prompt catalog usage.
- `lib/helpHub.py :: _on_key`, `_on_mouse` — `score ≈ 2948` and `≈ 2861`, high‑churn interaction paths.
- `lib/modelResponseCanvas.py :: _axis_join` (Function, line 664) — `score ≈ 2799`, axis‑aware response rendering.

### Hotspot Clusters

From these nodes, we see several coherent clusters beyond the already‑governed static prompt/axis domains:

1. **Axis configuration & axis‑aware response surfaces**
   - `lib/axisConfig.py` (file‑level hotspot).
   - `lib/modelResponseCanvas.py::_axis_join`, `_default_draw_response` and nearby rendering helpers.
   - Tests such as `tests/test_model_response_canvas.py`, `tests/test_model_helpers_response_canvas.py` (and related axis alignment tests) that keep axis‑aware rendering in sync with config.

2. **Help Hub and help GUIs / canvases**
   - `lib/modelHelpGUI.py` (file).
   - `lib/helpHub.py::_draw_result_row`, `_on_key`, `_on_mouse`.
   - Help‑related canvases such as `lib/modelHelpCanvas.py` (nodes slightly lower in the list but tightly coordinated).
   - Tests: `tests/test_help_hub.py`, `tests/test_model_help_gui.py`, `tests/test_model_help_canvas.py`, `tests/test_model_helpers_response_canvas.py`.

3. **Request orchestration, streaming, and history surfaces**
   - `lib/modelHelpers.py::_append_text`, `_send_request_streaming`, `send_request`.
   - `lib/requestController.py`, `lib/requestUI.py`, `lib/requestLog.py` (coordinated via line‑level hotspots and tests).
   - `lib/requestHistoryActions.py::_filter_tokens` and related helpers.
   - Tests: `tests/test_request_async.py`, `tests/test_request_async_wrapper.py`, `tests/test_recursive_orchestrator.py`, `tests/test_request_controller.py`, `tests/test_request_state.py`, `tests/test_request_streaming.py`, `tests/test_request_ui.py`, `tests/test_request_log.py`, `tests/test_request_history.py`, `tests/test_request_history_actions.py`, `tests/test_request_history_drawer.py`, `tests/test_suggestion_coordinator.py`.

4. **Static prompt & axis SSOT follow‑through**
   - `lib/staticPromptConfig.py::StaticPromptProfile`, `GPT/gpt.py::static_prompt_catalog`, `GPT/gpt.py::gpt_apply_prompt`, `GPT/readme.md`.
   - Tests: `tests/test_static_prompt_docs.py`, `tests/test_model_pattern_gui.py`, `tests/test_gpt_actions.py`, `tests/test_talon_settings_model_prompt.py`.
   - These remain hot but are primarily within the scope of ADR‑010, ADR‑0011, and ADR‑0036; this ADR focuses on adjacent domains that continue to coordinate with them.

We treat clusters (1)–(3) as this ADR’s primary in‑scope domains.

---

## Concordance Analysis – Hidden Domains

Applying the Concordance frame (visibility, scope, volatility) to the hotspot clusters:

### 1. Axis Configuration & Axis‑Aware Response Surfaces

- **Members (illustrative):**
  - `lib/axisConfig.py` (axis/Concordance configuration and documentation metadata).
  - `lib/modelResponseCanvas.py::_axis_join`, `_default_draw_response`, and related axis‑aware drawing helpers.
  - Axis‑related response/help canvas helpers in `lib/modelHelpers.py` and `lib/modelHelpCanvas.py`.
  - Tests: `tests/test_model_response_canvas.py`, `tests/test_model_helpers_response_canvas.py`, `tests/test_axis_overlap_alignment.py`, `tests/test_readme_axis_lists.py`.
- **Visibility:**
  - Axis docs and Concordance‑facing descriptions are split between `axisConfig`, static prompt/axis ADRs, README sections, and canvas code.
  - `_axis_join` and related helpers encode UI‑specific interpretations of axis combinations that are not expressed in a shared domain façade.
- **Scope:**
  - Conceptual changes to axis docs or aggregation (e.g. how axes are grouped or surfaced in canvases) ripple across `axisConfig`, response canvases, help canvases, README, and tests.
  - The same conceptual “axis doc” tune appears in multiple domains (static prompts, Concordance docs, response GUIs) with partial overlap.
- **Volatility:**
  - High churn in `axisConfig` and response canvases indicates ongoing tuning of axis semantics, Concordance presentation, and UX.
  - Tests track these shifts but often at the level of specific rendered strings or layouts rather than explicit domain contracts.

**Hidden domain / tune:** a **“Concordance axis documentation and response surfaces”** domain that owns how axes and Concordance‑relevant flags are explained, grouped, and rendered across canvases and docs.

### 2. Help Hub and Help GUIs / Canvases

- **Members (illustrative):**
  - `lib/modelHelpGUI.py` (help GUI entrypoint and layout/orchestration).
  - `lib/helpHub.py::_draw_result_row`, `_on_key`, `_on_mouse`.
  - `lib/modelHelpCanvas.py` and any helper functions that render or scroll help results.
  - Tests: `tests/test_help_hub.py`, `tests/test_model_help_gui.py`, `tests/test_model_help_canvas.py`.
- **Visibility:**
  - Help search/index logic, keyboard/mouse interaction semantics, and rendering rules are interleaved in large functions.
  - Contracts for what is searchable, how results are ordered, and what keyboard shortcuts guarantee are encoded implicitly in code and tests.
- **Scope:**
  - Changes to help indexing or result layout affect `helpHub`, help GUIs, canvases, and sometimes README/ADR references; small tweaks can cause broad churn.
  - Help interactions also coordinate with request history and suggestion surfaces (e.g. jumping from help to a recipe or action).
- **Volatility:**
  - The heatmap shows sustained churn in `_draw_result_row`, `_on_key`, and `_on_mouse`, matching ongoing UX refinement and Concordance guardrail tuning.

**Hidden domain / tune:** a **“Help discovery and interaction”** domain that owns help indexing, ranking, and input handling across Hub + GUIs, separate from canvas drawing mechanics.

### 3. Request Orchestration, Streaming, and History Surfaces

- **Members (illustrative):**
  - `lib/modelHelpers.py::_append_text`, `_send_request_streaming`, `send_request` (request/stream orchestration and GUI updates).
  - `lib/requestController.py`, `lib/requestAsync.py`, `lib/requestBus.py`, `lib/requestUI.py`, `lib/requestLog.py`.
  - `lib/requestHistoryActions.py::_filter_tokens` and related helpers underlying history drawers.
  - `lib/suggestionCoordinator.py` and `lib/recursiveOrchestrator.py` as higher‑level orchestrators.
  - Tests: the `tests/test_request_*` suite, `tests/test_recursive_orchestrator.py`, `tests/test_suggestion_coordinator.py`, `tests/test_request_history_actions.py`, `tests/test_request_history_drawer.py`, `tests/test_request_ui.py`.
- **Visibility:**
  - The lifecycle of a request (from Talon command / GUI action through async execution, streaming, logging, and history) is scattered across many modules.
  - `_append_text` couples streaming protocol details (chunks, deltas) with canvas‑specific updates and history metadata updates.
  - History token filters encode implicit contracts for how entries are grouped and surfaced but are not captured in a named domain.
- **Scope:**
  - Behavioural changes to streaming (e.g. new partial‑render rules) can ripple through model helpers, response canvases, request UI, logs, and history drawers.
  - Filters and logging semantics influence Help Hub and Concordance surfaces as well (e.g. which runs show up where, with which tags).
- **Volatility:**
  - High churn in `send_request`, `_send_request_streaming`, `_append_text`, and `_filter_tokens` reflects ongoing adjustments to UX, performance, and guardrails.
  - Tests track this evolution across many files, with coordinated edits in request and suggestion suites.

**Hidden domain / tune:** a **“Request lifecycle + history orchestration”** domain that owns end‑to‑end request execution, streaming, logging, and history/query behaviour, with clear boundaries between transport, orchestration, and UI.

### 4. Static Prompt & Axis SSOT Follow‑through

- **Members (illustrative):**
  - `lib/staticPromptConfig.py::StaticPromptProfile` and helpers.
  - `GPT/gpt.py::static_prompt_catalog`, `gpt_apply_prompt`.
  - `GPT/readme.md` static‑prompt sections.
  - Tests: `tests/test_static_prompt_docs.py`, `tests/test_model_pattern_gui.py`, `tests/test_gpt_actions.py`, `tests/test_talon_settings_model_prompt.py`.
- **Visibility, scope, volatility:**
  - These nodes remain hot but are explicitly governed by ADR‑010, ADR‑0011, and ADR‑0036, which have already introduced SSOT façades and refactor plans.
  - The current ADR’s role is to ensure adjacent help/response/request domains integrate with those façades rather than reinventing or bypassing them.

**Hidden domain / tune:** a **“Static prompt and axis SSOT continuation”** domain whose main concern here is boundary alignment with the new domains above.

---

## Problem

Despite earlier Concordance work on static prompts and axis mapping, the latest heatmap shows that:

- **Axis documentation and response surfaces** remain structurally ambiguous:
  - `axisConfig` combines Concordance configuration, axis docs, and UI‑driven groupings in one large file.
  - Response canvases and help canvases re‑express axis semantics locally, leading to duplicated churn and fragile tests.
- **Help discovery and interaction** logic is tightly coupled to canvas rendering and request history:
  - Keyboard and mouse handlers in `helpHub` directly manipulate search state, selection, and canvas layouts.
  - Contracts for what appears in help and how it is navigated are not expressed as a domain façade.
- **Request lifecycle & history orchestration** spreads responsibilities across `modelHelpers`, request controller/async modules, canvases, and history drawers:
  - `_append_text` and `_send_request_streaming` conflate low‑level stream handling, UI updates, and history tagging.
  - History filters and logs are tuned in tandem with these helpers but without a single “request lifecycle” home.
- **Concordance scores stay high** around these domains because visibility is low (implicit contracts), scope is wide (many files move together), and volatility is high (ongoing UX/perf tuning).

We want to **reduce sustained Concordance scores** for these hotspots by tightening their domain boundaries and aligning them with existing SSOT façades, without weakening Concordance checks or test guardrails.

---

## Decision

For the in‑scope hotspots, we adopt the following structural decisions:

1. **Introduce an explicit “axis docs & response surfaces” domain façade**
   - Treat `lib/axisConfig.py` as the primary home for Concordance axis documentation and grouping metadata, with a **small, explicit API** that:
     - Exposes axis descriptors and groupings used by response/help canvases and README/ADR docs.
     - Encodes Concordance‑relevant flags (e.g. “tune”, “surface”, “guardrail”) in a structured way.
   - Update `lib/modelResponseCanvas.py`, `lib/modelHelpCanvas.py`, and related helpers to:
     - Consume this façade for axis/group information rather than hard‑coding local join logic.
     - Focus on layout/rendering concerns, not axis doc semantics.

2. **Separate help discovery/interaction from canvas rendering**
   - Define a **Help domain module** (or clearly separated section within `helpHub`) that:
     - Owns help index construction, search, ranking, and keyboard/mouse navigation semantics.
     - Provides pure functions for “given a query and current selection, compute next selection and visible rows”.
   - Have `modelHelpGUI`, `modelHelpCanvas`, and `helpHub` treat this domain as their source of truth, limiting them to presentation and wiring.

3. **Consolidate request lifecycle + history orchestration behind a façade**
   - Introduce a **RequestLifecycle** façade over `modelHelpers.send_request`, `_send_request_streaming`, `_append_text`, `requestController`, `requestHistoryActions`, and `requestLog` that:
     - Separates transport concerns (HTTP/streaming) from orchestration (states, retries, cancellation) and UI updates.
     - Provides a stable API for emitting high‑level events (e.g. “chunk received”, “stream ended”, “error”) to canvases and history/log surfaces.
   - Move history token filtering semantics (`_filter_tokens`) into this domain or a sibling “history query” module so that drawers and help surfaces consume a single contract.

4. **Align all three domains with existing SSOT façades**
   - Axis docs and response surfaces must consume the **axis and static prompt façades** defined by ADR‑0011 and ADR‑0036 rather than introducing new representations.
   - Help/Request domains should reuse existing orchestrators such as `RecursiveOrchestrator`, `PromptPipeline`, and `suggestionCoordinator` where applicable rather than duplicating orchestration logic inside GUI helpers.

For all these decisions, the intended long‑term effect is to **lower Concordance scores** for the in‑scope hotspots by:

- Increasing visibility of domain contracts (axis docs, help semantics, request lifecycle).
- Narrowing scope of changes (local edits per domain façade).
- Reducing volatility in core orchestrators through clearer separation of concerns and stronger tests.

We explicitly do **not** relax Concordance scoring or weaken tests; improvements must come from genuine structural and behavioural changes.

---

## Tests‑First Principle

We reaffirm the existing tests‑first characterization principle from ADR‑0011 and ADR‑010 and apply it specifically to the new domains:

> At each step, we will first analyze existing tests to ensure that the behavior we intend to change is well covered. Where coverage is insufficient, we will add focused characterization tests capturing current behavior (including relevant branches and error paths), and then proceed with the refactor guarded by those tests. Where coverage is already strong and branch‑focused for the paths we are changing, we will rely on and, if needed, extend those existing tests rather than adding redundant characterization tests.

In particular:

- Behaviour‑changing refactors in axis docs/response surfaces, help discovery/interaction, or request lifecycle/history must not proceed without adequate tests for the behaviours being changed.
- When existing tests already exercise the relevant branches and contracts, we will **reuse and extend** those tests rather than adding near‑duplicate suites.
- Tests should prefer behavioural contracts (e.g. “this key chord moves selection in this way”, “this request status transition emits these events”) over incidental static text (e.g. full help prose), unless that text itself encodes a behaviour‑level contract.

---

## Refactor Recommendations (Draft → Revised with Prior Art)

### 1. Axis Docs & Response Surfaces Domain

**Original draft idea**

- Split axis documentation and response canvas axis logic into a dedicated domain: a single module owns axis descriptions, Concordance flags, and groupings; canvases simply render a supplied structured model.

**Similar existing behaviour and patterns (prior art)**

- ADR‑0011 and ADR‑0036 already treat static prompt/axis configuration and GUIs as domains, with `lib/staticPromptConfig.py`, `lib/axisMappings.py`, and `lib/talonSettings.py` acting as façades.
- ADR‑031 and ADR‑023 (response canvas and viewer ADRs) already govern parts of the response canvas layout and throttling behaviour.
- `tests/test_readme_axis_lists.py` and `tests/test_axis_overlap_alignment.py` validate relationships between axis docs, list files, and rendered views.

**Revised recommendation**

- Evolve `lib/axisConfig.py` into an explicit **AxisDocs façade** for Concordance and response surfaces:
  - Define clear, typed data structures for axis groups, descriptions, and Concordance annotations (e.g. “tune hotspot”, “guardrail axis”).
  - Provide query helpers consumed by:
    - `modelResponseCanvas` (for `_axis_join` and related axis renderings).
    - `modelHelpCanvas` and help/interpreter views that surface axis docs.
    - Axis‑related README/ADR doc builders.
- Update `modelResponseCanvas` and `modelHelpCanvas` to:
  - Replace local ad‑hoc axis joining and selection logic with calls to `AxisDocs` helpers.
  - Keep only drawing/layout code and small formatting decisions in canvas modules.
- Keep alignment with static prompt/axis façades by:
  - Using axis identifiers and tokens from `axisMappings` / `staticPromptConfig` rather than inventing new keys.
  - Having tests confirm that `AxisDocs` remains consistent with these existing façades.

### 2. Help Discovery & Interaction Domain

**Original draft idea**

- Extract search, ranking, and navigation semantics from `helpHub` and help GUIs into a separate “help domain” module, leaving canvas code purely presentational.

**Similar existing behaviour and patterns (prior art)**

- `lib/helpHub.py` already centralises help indexing and result shaping, but intermixes it with event handlers.
- ADR‑028 (“Help Hub and Discoverability”) and ADR‑021 (“Browser meta and answer layout”) document earlier UX and layout decisions for help surfaces.
- Tests `tests/test_help_hub.py`, `tests/test_model_help_gui.py`, and `tests/test_model_help_canvas.py` already capture many help behaviours.

**Revised recommendation**

- Introduce a small **HelpDomain** façade (either as a new module or carved out of `helpHub`) that:
  - Owns:
    - Index construction from commands, prompts, and docs.
    - Query → ranked results mapping.
    - Navigation semantics: given current selection, key/mouse event, and result list, compute next selection and scroll window.
  - Exposes pure, easily testable functions for these behaviours.
- Have `modelHelpGUI`, `modelHelpCanvas`, and `helpHub`:
  - Call into `HelpDomain` for search and navigation decisions.
  - Restrict themselves to drawing, binding events, and wiring results to canvases.
- Align with ADR‑028/ADR‑021 by:
  - Reusing existing notions of “help sources”, “result kinds”, and layout hints.
  - Avoiding new result types when existing categories (recipes, commands, docs) suffice.

### 3. Request Lifecycle & History Orchestration Domain

**Original draft idea**

- Move stream protocol handling, logging, and history updates out of `_append_text` / `_send_request_streaming` into a dedicated RequestLifecycle module; treat GUIs and histories as subscribers to lifecycle events.

**Similar existing behaviour and patterns (prior art)**

- `lib/requestController.py`, `lib/requestAsync.py`, `lib/requestBus.py`, and `lib/recursiveOrchestrator.py` already provide orchestrator patterns for async request handling.
- `lib/suggestionCoordinator.py` functions as a focused coordinator for suggestion flows.
- ADR‑027 (“Request state machine and progress surfaces”) and related request ADRs define state machine expectations and progress surfaces.
- The `tests/test_request_*` suite, `tests/test_recursive_orchestrator.py`, `tests/test_request_history_actions.py`, `tests/test_request_history_drawer.py`, and `tests/test_request_ui.py` already characterize many lifecycle and history behaviours.

**Revised recommendation**

- Introduce a **RequestLifecycle façade** that:
  - Owns the **logical request state machine** (pending, running, streaming, completed, errored, cancelled) and associated metadata (source, tags, axis/static‑prompt context).
  - Emits clearly defined events (`on_chunk`, `on_complete`, `on_error`, `on_cancel`, `on_retry`) consumed by:
    - `modelResponseCanvas` and friends for incremental rendering.
    - `requestHistoryActions` and drawers for entry creation and updates.
    - `requestLog` for durable logging.
  - Encapsulates stream protocol details (chunk framing, deltas) so `_append_text` becomes a thin adapter from stream events to canvas operations.
- Refactor `modelHelpers.send_request` and `_send_request_streaming` to:
  - Delegate lifecycle responsibilities to `RequestLifecycle` rather than owning state transitions directly.
  - Treat the underlying transport (HTTP/Talon RPC) as a pluggable dependency.
- Normalize history filtering and token semantics by:
  - Moving `_filter_tokens` logic into a small “HistoryQuery” helper within the same domain.
  - Documenting filter categories (e.g. by source, tags, outcome, Concordance tune) so help and drawers share them.

### 4. Static Prompt & Axis SSOT Follow‑through

**Original draft idea**

- Further reduce duplication between `staticPromptConfig`, `static_prompt_catalog`, `gpt_apply_prompt`, and axis/response surfaces.

**Similar existing behaviour and patterns (prior art)**

- ADR‑010, ADR‑0011, and ADR‑0036 already define SSOT façades and refactor plans for static prompts and axis mappings, much of which has been implemented in this repo.
- `static_prompt_catalog` and `gpt_apply_prompt` already consume `STATIC_PROMPT_CONFIG` and axis façades.

**Revised recommendation**

- Treat remaining churn in these nodes as **governed follow‑through** under existing ADRs.
- For this ADR, the only new recommendation is:
  - Ensure the AxisDocs and RequestLifecycle/HelpDomain façades **consume** static prompt/axis façades rather than re‑encoding prompt/axis semantics.
  - Extend existing tests only where new boundaries (e.g. new façades) touch static‑prompt/axis behaviour.

---

## Tests‑First Refactor Plan

For each revised recommendation, we map affected modules to existing tests and any required new characterization coverage.

### 1. Axis Docs & Response Surfaces

- **Affected modules/functions:**
  - `lib/axisConfig.py`.
  - `lib/modelResponseCanvas.py::_axis_join`, `_default_draw_response`, and nearby helpers.
  - `lib/modelHelpCanvas.py` where it surfaces axis docs.
- **Existing tests to rely on:**
  - `tests/test_model_response_canvas.py`.
  - `tests/test_model_helpers_response_canvas.py`.
  - `tests/test_axis_overlap_alignment.py`.
  - `tests/test_readme_axis_lists.py`.
- **Characterization focus:**
  - Branches in `_axis_join` and related helpers (e.g. missing axes, multiple axes, ordering rules).
  - Behaviour when axis config changes (new axis, renamed axis, hidden axis).
- **New tests (where needed) before refactor:**
  - A small **AxisDocs** unit test suite that:
    - Confirms round‑trip between `axisConfig` data and the structures consumed by canvases.
    - Verifies that axis groupings and descriptions match expectations from existing tests/README slices.
- **Mapping refactor steps to tests:**
  - Step 1 (introduce AxisDocs façade): guarded by new AxisDocs tests + existing `test_axis_overlap_alignment.py`.
  - Step 2 (wire `modelResponseCanvas`/`modelHelpCanvas` to façade): guarded by `test_model_response_canvas.py` and `test_model_helpers_response_canvas.py`.
  - Step 3 (remove duplicated axis logic from canvases): rerun the full set above plus `test_readme_axis_lists.py`.

### 2. Help Discovery & Interaction

- **Affected modules/functions:**
  - `lib/helpHub.py::_draw_result_row`, `_on_key`, `_on_mouse`.
  - `lib/modelHelpGUI.py`.
  - `lib/modelHelpCanvas.py`.
- **Existing tests to rely on:**
  - `tests/test_help_hub.py`.
  - `tests/test_model_help_gui.py`.
  - `tests/test_model_help_canvas.py`.
- **Characterization focus:**
  - Keyboard navigation branches (up/down/page, open/close, focus changes).
  - Mouse interaction (click/hover) vs. keyboard equivalence.
  - Ranking and grouping behaviour for diverse help items (actions, prompts, docs).
- **New tests (where needed) before refactor:**
  - Focused tests over the new **HelpDomain** façade to:
    - Assert that given a query and selection, the next selection and visible window match current behaviour for representative scenarios.
    - Encode any invariants about which items must always be reachable via certain key chords.
- **Mapping refactor steps to tests:**
  - Step 1 (extract HelpDomain pure functions): guarded by new HelpDomain tests.
  - Step 2 (wire `helpHub`/GUIs/canvases to HelpDomain): guarded by `test_help_hub.py` + GUI/canvas tests.
  - Step 3 (clean up legacy event‑driven logic): rerun the full help test set and adjacent integration tests that cross help → request flows.

### 3. Request Lifecycle & History Orchestration

- **Affected modules/functions:**
  - `lib/modelHelpers.py::_append_text`, `_send_request_streaming`, `send_request`.
  - `lib/requestController.py`, `lib/requestAsync.py`, `lib/requestBus.py`, `lib/requestUI.py`, `lib/requestLog.py`.
  - `lib/requestHistoryActions.py::_filter_tokens` and related helpers.
- **Existing tests to rely on:**
  - `tests/test_request_async.py` and `tests/test_request_async_wrapper.py`.
  - `tests/test_recursive_orchestrator.py`.
  - `tests/test_request_controller.py`, `tests/test_request_state.py`, `tests/test_request_streaming.py`.
  - `tests/test_request_ui.py`, `tests/test_request_log.py`.
  - `tests/test_request_history.py`, `tests/test_request_history_actions.py`, `tests/test_request_history_drawer.py`.
  - `tests/test_suggestion_coordinator.py`, `tests/test_gpt_actions.py` (for end‑to‑end flows).
- **Characterization focus:**
  - True/false and error branches in streaming (`_send_request_streaming`), including cancellation and retry paths.
  - History filter behaviour for representative combinations of tags, outcomes, and sources.
  - State transitions in the request state machine as exercised by controller/async/bus modules.
- **New tests (where needed) before refactor:**
  - A minimal **RequestLifecycle** test suite that:
    - Drives the state machine through happy, error, and cancellation paths, asserting emitted events.
    - Exercises `_filter_tokens` in isolation with a small fixture of history entries.
- **Mapping refactor steps to tests:**
  - Step 1 (introduce RequestLifecycle façade and HistoryQuery helper with adapters from existing code): guarded by new RequestLifecycle tests + streaming/state tests.
  - Step 2 (migrate `modelHelpers` and history drawers to consume the façade): guarded by request streaming/UI/history tests.
  - Step 3 (simplify/remove duplicated lifecycle logic from `modelHelpers` and drawers): rerun the full `tests/test_request_*` suite plus suggestion/Concordance‑relevant tests.

### 4. Static Prompt & Axis SSOT Follow‑through

- **Affected modules/functions:**
  - Integration points where AxisDocs/HelpDomain/RequestLifecycle façades consume static prompt/axis data.
- **Existing tests to rely on:**
  - `tests/test_static_prompt_docs.py`, `tests/test_model_pattern_gui.py`, `tests/test_gpt_actions.py`, `tests/test_talon_settings_model_prompt.py`, `tests/test_axis_mapping.py`.
- **Characterization focus:**
  - Ensuring that new façades do not change static prompt or axis semantics at their boundaries.
- **New tests (where needed) before refactor:**
  - Only where new façades add behaviour that meaningfully interacts with static prompts/axes; otherwise, rely on existing tests as guardrails.

---

## Refactor Plan

We propose a phased plan that can be executed in small, test‑guarded slices.

1. **Phase 1 – Characterize current behaviour and introduce façades**
   - Add focused characterization tests for AxisDocs, HelpDomain, RequestLifecycle, and HistoryQuery units as described above.
   - Introduce minimal façade modules/sections that initially wrap existing helpers (`_axis_join`, `_append_text`, `_filter_tokens`, etc.) without changing behaviour.

2. **Phase 2 – Migrate canvases and GUIs to façades**
   - Wire `modelResponseCanvas`, `modelHelpCanvas`, `modelHelpGUI`, `helpHub`, and history drawers to consume the new façades.
   - Keep legacy helpers as thin adapters until migration is complete.

3. **Phase 3 – Simplify and consolidate legacy logic**
   - Remove duplicated axis doc logic from canvases in favour of AxisDocs.
   - Remove embedded search/navigation logic from `helpHub` in favour of HelpDomain.
   - Fold stream and history update logic from `modelHelpers`/drawers into RequestLifecycle/HistoryQuery.

4. **Phase 4 – Concordance follow‑up**
   - After major slices land, re‑run `scripts/tools/line-churn-heatmap.py` and compare hotspots for:
     - `lib/axisConfig.py`.
     - `lib/modelResponseCanvas.py` and `lib/modelHelpCanvas.py`.
     - `lib/helpHub.py` and `lib/modelHelpGUI.py`.
     - `lib/modelHelpers.py` and `lib/request*` modules.
   - Confirm that sustained Concordance scores for these nodes decrease or at least stabilize with more interpretable coordination patterns.

---

## Consequences

- **Positive outcomes:**
  - Clearer domain boundaries for axis docs/response surfaces, help discovery, and request lifecycle/history should lower coordination cost and make Concordance scores easier to interpret.
  - GUIs and canvases become thinner, focusing on presentation while delegating semantics to testable façades.
  - Request streaming and history behaviour becomes safer to evolve, with a single state machine and event surface instead of scattered ad‑hoc logic.
- **Risks:**
  - Introducing new façade layers can temporarily increase complexity and churn.
  - Misaligned boundaries could duplicate work already governed by ADR‑010/ADR‑0011/ADR‑0036 or request/response ADRs.
- **Mitigations:**
  - Keep façade APIs minimal and driven by existing tests and use‑cases.
  - Align with prior ADRs (010, 0011, 0036, 023, 027, 028, 031) and reuse their domain homes.
  - Land changes in small, tests‑first slices with Concordance follow‑up scans.

---

## Current Status (2025-12-10)

- AxisDocs façade: `AxisDoc` structures, AxisDocs helpers, and canvas wiring are in place; response and help canvases now source axis documentation exclusively via this façade, and the axis/readme tests are green, so there is no remaining in-repo work for this domain in this repo.
- HelpDomain façade: index, search, focusable-items, navigation, filter-editing, and activation helpers now live in `lib/helpDomain.py`; Help Hub’s key and mouse handlers are thin adapters over this façade under the existing help tests.
- RequestLifecycle & HistoryQuery façade: `lib/requestLifecycle.py`, `lib/historyQuery.py`, and adapters in `lib/requestState.py`/`lib/requestBus.py` exist with tests; history drawers and request-history listing now consume the HistoryQuery façade for labels/bodies/axes/summaries, and `lib/modelHelpers.send_request` together with `_send_request_streaming`/`_append_text` now track a logical RequestLifecycle state (pending/running/streaming/completed) via this façade. The full `tests/test_request_*`, `tests/test_request_history_*`, `tests/test_suggestion_coordinator.py`, and `tests/test_gpt_actions.py` suites are green under this setup, so duplicated lifecycle/history logic in `modelHelpers` is now considered retired for this repo.
- Concordance follow‑up: hotspot scans were re‑run on 2025-12-10 using `scripts/tools/churn-git-log-stat.py` and `scripts/tools/line-churn-heatmap.py`; results confirm that the in-scope hotspots (AxisDocs, HelpDomain, RequestLifecycle/history) remain prominent but are now governed by the new façades and tests.

## Salient Tasks

- [x] **AxisDocs façade**
  - [x] Introduce an `AxisDocs` façade in or beside `lib/axisConfig.py` with typed axis/group/flag structures.
  - [x] Add AxisDocs unit tests and wire `modelResponseCanvas`/`modelHelpCanvas` to consume it.
  - [x] Remove duplicated axis doc logic from canvases and keep `tests/test_model_response_canvas.py`, `tests/test_model_helpers_response_canvas.py`, and `tests/test_axis_overlap_alignment.py` green.

- [x] **HelpDomain façade**
  - [x] Extract help index, ranking, and navigation into a HelpDomain façade consumed by `helpHub`, `modelHelpGUI`, and `modelHelpCanvas`.
  - [x] Add focused HelpDomain tests for search and navigation behaviour.
  - [x] Simplify help event handlers to thin adapters while keeping `tests/test_help_hub.py`, `tests/test_model_help_gui.py`, and `tests/test_model_help_canvas.py` green.

- [x] **RequestLifecycle & HistoryQuery façade**
  - [x] Introduce a RequestLifecycle façade and HistoryQuery helper that own request state transitions, stream events, and history filters, with unit tests.
  - [x] Migrate `modelHelpers.send_request` to use the RequestLifecycle façade (logical status via `RequestLifecycleState` and `reduce_request_state`).
  - [x] Migrate `_send_request_streaming`, `_append_text` to use the RequestLifecycle façade.
  - [x] Migrate history drawers to use the HistoryQuery façade.
  - [x] Deduplicate cancel-handling lifecycle/history logic in `modelHelpers.send_request`.
  - [x] Deduplicate non-stream error-handling logic in `modelHelpers.send_request` behind a shared helper.
  - [x] Centralise "max attempts exceeded" handling in `modelHelpers.send_request` behind a shared helper.
  - [x] Centralise streaming error lifecycle/history behaviour in `_send_request_streaming` using the RequestLifecycle façade.
  - [x] Centralise history append semantics for completed requests behind a small helper (for example in `requestLog`/`historyQuery`), and confirm drawers/listing consume it.
  - [x] Once the above subtasks are complete and `tests/test_request_*`, `tests/test_request_history_*`, `tests/test_suggestion_coordinator.py`, and `tests/test_gpt_actions.py` remain green, mark duplicated lifecycle/history logic as retired for this repo.

- [x] **Concordance follow‑up**
  - [x] Re‑run `scripts/tools/line-churn-heatmap.py` after at least one major façade phase to confirm that sustained scores for the in‑scope hotspots decrease or stabilize.
  - [x] Record significant slices and outcomes in an ADR‑0037 work‑log when Concordance scans are re-run.
