# ADR-0062 – Canonicalize GPT Surface Orchestrators and History Gating

Status: In Progress — metadata orchestration + export guardrails (Loops 0001-0036)  
Date: 2025-12-24  
Owners: Talon AI tools maintainers

---

## Context

- Statement-level churn × complexity heatmap (window “90 days ago”; scope `lib/`, `GPT/`, `copilot/`, `tests/`) stored at `tmp/churn-scan/line-hotspots.json` (generated 2025-12-24T16:45Z). Matching git log fixture lives at `tmp/churn-scan/git-log-stat.txt`.
- Aggregated node scores highlight three tightly coupled clusters:
  - **GPT prompt & persona orchestration** — `GPT/gpt.py` alone carries ≈73k score across 35 hotspots, including `_suggest_prompt_text`, `_normalise_recipe`, persona canonicalization helpers, and axis catalog readers. Churn radiates into `GPT/readme.md` and Talon lists when presets or axis docs shift.
  - **Canvas & help surfaces** — `lib/modelResponseCanvas.py` (≈24k across 14 nodes), `lib/modelSuggestionGUI.py` (≈24k across 11), `lib/helpHub.py`, `lib/modelHelpCanvas.py`, and `lib/requestHistoryDrawer.py` all exhibit repeated mouse/key handlers, persona preset lookups, stance summaries, and bespoke `_reject_if_request_in_flight` guards.
  - **Request history and drop-reason actions** — `lib/requestHistoryActions.py` (≈24k across 10 nodes) and `lib/requestLog.py` (~19k) coordinate axis snapshots, persona summaries, and drop-reason notifications separately from the canvases they feed.
- These churn centers overlap with Concordance guardrails introduced in ADR-0056, but sustained scores indicate the orchestrator boundaries and canonical snapshots defined there have not yet been instantiated in code.

---

## Problem

Duplicated orchestration code keeps Concordance pressure high. GPT prompt/preset logic, canvas/help surfaces, and request history actions each maintain partial views of persona presets, axis snapshots, and in-flight gating. Contracts remain implicit: `_reject_if_request_in_flight`, persona summary builders, axis filtering, and drop-reason notifications are reimplemented per surface. As a result:

- **Visibility** is low — shared behaviours (persona/intent catalogs, axis snapshots, drop-reason workflows) are encoded in private helpers inside large modules rather than exposed as explicit facades.
- **Scope** is wide — any persona, axis, or gating tweak must touch GPT actions, multiple canvases, request history, docs, and tests simultaneously.
- **Volatility** stays high — the same helpers continue to churn across files, and no canonical abstraction anchors autocomplete or test coverage.

To lower sustained Concordance scores we must move from duplicated surface logic to explicit orchestrators with shared contracts and tests.

---

## Hidden Domains and Concordance Analysis

### 1. Prompt & Persona Orchestration Domain

- **Members (sample)**: `GPT/gpt.py::{_suggest_prompt_text,_normalise_recipe,_build_persona_intent_docs,_canonical_persona_value,axis_catalog}`, `GPT/readme.md`, Talon persona/tone/purpose lists, `lib/personaConfig.py`, `lib/suggestionCoordinator.py` stance helpers.
- **Visibility**: persona validation, axis hydration, and prompt recipe assembly live in monolithic private helpers; consuming surfaces (canvases, history summaries, docs) cannot reuse a canonical contract.
- **Scope**: adjustments ripple through GPT actions, help docs, persona lists, suggestion canvases, and tests across `_tests/` and `tests/` suites.
- **Volatility**: the heatmap shows repeated edits to persona/axis canonicalization and docs, indicating current abstractions do not stabilize behaviour.
- **Hidden tune**: *Prompt Persona Orchestrator* — a missing façade that should own persona catalogs, axis projections, and prompt recipe normalization for all consumers.

### 2. Canvas Interaction & Guidance Domain

- **Members (sample)**: `lib/modelResponseCanvas.py::{_on_mouse,_reject_if_request_in_flight,_lookup_intent_display}`, `lib/modelSuggestionGUI.py::{_suggestion_stance_info,_refresh_suggestions_from_state}`, `lib/modelHelpCanvas.py::{_reject_if_request_in_flight,_on_mouse}`, `lib/helpHub.py::{_draw_result_row,_persona_presets}`, `lib/requestHistoryDrawer.py::{_reject_if_request_in_flight,_on_draw}`.
- **Visibility**: each surface embeds its own event handling, persona lookup, and Concordance messaging; cross-surface behaviours (stance summaries, intent labels, drop-reason nudges) are not centralized.
- **Scope**: tweaks to persona or axis presentation require touching every canvas plus associated tests (`tests/test_model_help_gui.py`, `tests/test_model_suggestion_gui.py`, `tests/test_model_response_canvas.py`).
- **Volatility**: high churn in identical mouse/key handlers and stance formatting shows no canonical “surface coordinator” guides these UIs.
- **Hidden tune**: *Guidance Surface Coordinator* — we need a single orchestrator that broker persona summaries, axis highlights, and gating across canvases.

### 3. Request History & Drop-Reason Lifecycle Domain

- **Members (sample)**: `lib/requestHistoryActions.py::{axis_snapshot_from_axes,history_summary_lines,_reject_if_request_in_flight,_notify_with_drop_reason}`, `lib/requestLog.py::{_filter_axes_payload,latest}`, `lib/requestHistoryDrawer.py::_refresh_entries`, `lib/modelDestination.py::append_text`, `lib/modelConfirmationGUI.py::_reject_if_request_in_flight`, plus tests `tests/test_request_history_actions.py`, `tests/test_request_log.py`, `tests/test_history_axis_export_telemetry.py`.
- **Visibility**: axis snapshot shape, persona summaries, and drop-reason routing remain implicit across helpers; Concordance scoring consumers must infer semantics from multiple modules.
- **Scope**: coordinating history snapshots touches logging, canvases, GPT actions, telemetry exports, and docs.
- **Volatility**: `_reject_if_request_in_flight` and drop-reason notifications continue to churn across canvases and history modules.
- **Hidden tune**: *History Lifecycle Orchestrator* — consolidate request lifecycle gating, drop-reason messaging, and Concordance-ready history snapshots.

---

## Decision

We will introduce explicit orchestrators for the three domains above, collapsing duplicated helpers into shared contracts:

1. **Prompt Persona Orchestrator** — extract a canonical catalog that owns persona presets, axis overlays, and prompt recipe normalization, consumed by GPT actions, docs, suggestion/help canvases, and tests.
2. **Guidance Surface Coordinator** — centralize canvas/help event handling, persona/intent display logic, and Concordance messaging so each UI surface delegates rather than reimplementing.
3. **History Lifecycle Orchestrator** — unify request-in-flight gating, drop-reason notifications, and axis/persona snapshot assembly for history/log exports, aligning with Concordance expectations.

These orchestrators must reuse existing facades (e.g. `axisCatalog`, `requestLifecycle`, `suggestionCoordinator`) instead of inventing new concepts, and they must aim to measurably reduce sustained Concordance scores without weakening guardrails or tests.

---

## Tests-First Principle

> We will review existing tests before each refactor slice, add focused characterization tests only where coverage is insufficient, and guard the refactor with those tests. When current branch-focused tests already cover the behaviour, we will extend and rely on them instead of duplicating coverage.

---

## Refactor Plan (Prior Art Aligned)

### 1. Prompt Persona Orchestrator

- **Original Draft**: collapse persona canonicalization and axis hydration logic from `GPT/gpt.py` and docs into a reusable service.
- **Similar Existing Behavior**: `lib/personaConfig.py`, `lib/suggestionCoordinator.py`, and ADR-0056’s persona guidance already define catalog-like structures; `GPT/gpt.py` exposes `_build_persona_intent_docs` and `_canonical_persona_value` but keeps them private.
- **Revised Recommendation**:
  - Extract a `persona_intent_catalog` module that returns typed presets (axis keys, spoken labels, Concordance metadata) and exposes normalization APIs.
  - Have GPT actions, help docs, suggestion canvases, and Talon list generation consume the same catalog so persona changes flow from one source.
  - Add targeted tests around the catalog to cover canonicalization branches currently exercised indirectly by `_tests/test_model_suggestion_gui.py`, `tests/test_gpt_actions.py`, and related suites.

### 2. Guidance Surface Coordinator

- **Original Draft**: stop duplicating mouse/key handlers, persona summary builders, and stance guidance across canvases.
- **Similar Existing Behavior**: `lib/modelSuggestionGUI.py` and `lib/modelResponseCanvas.py` already call into `suggestionCoordinator` and `modelHelpers` for portions of their logic; ADR-0046 established guidance domains for help surfaces.
- **Revised Recommendation**:
  - Introduce a `surfaceGuidance` (name TBD) module that wraps request gating, persona summary formatting, stance info, and axis highlights for canvases and drawers.
  - Replace per-surface `_reject_if_request_in_flight`, `_on_mouse`, and persona summary helpers with delegations to this coordinator, leaving surfaces to focus on drawing/layout.
  - Reinforce coverage by extending existing GUI tests (e.g. `_tests/test_model_help_gui.py`, `tests/test_model_suggestion_gui.py`) to exercise shared handlers instead of surface-specific copies.

### 3. History Lifecycle Orchestrator

- **Original Draft**: re-center history snapshot building and drop-reason routing around a single lifecycle API.
- **Similar Existing Behavior**: `lib/requestLifecycle.py`, `lib/requestState.py`, and `lib/requestBus.py` already model request phases; ADR-0055 consolidated history saves via the `file` destination.
- **Revised Recommendation**:
  - Build a `historyLifecycle` façade that:
    - Accepts the canonical persona/axis snapshot from the Prompt Persona Orchestrator.
    - Mediates `try_begin_request`, drop-reason notifications, and history snapshot persistence for canvases and actions.
    - Exposes gating telemetry (`history_validation_stats`, drop counts, sources) so guardrails and docs pull from the same lifecycle instrumentation.
    - Provides drop-reason setters/consumers so canvases and history actions stop importing `requestLog` directly.
    - Exposes persona snapshot helpers (header extraction and summary fragments) so history actions, query façades, and telemetry exports share identical normalization.
  - Migrate `requestHistoryActions`, `requestLog`, canvases, and `modelDestination.append_text` to this façade, removing bespoke `_reject_if_request_in_flight` logic.
  - Cover the façade with characterization tests that extend `tests/test_request_history_actions.py`, `tests/test_request_log.py`, and `_tests/test_history_axis_export_telemetry.py`.

---

## Consequences

- **Positive**: clearer ownership of persona catalogs, surface guidance, and history lifecycle should cut coordination width, stabilize Concordance guardrails, and reduce duplicate event-handling churn.
- **Risks**: refactors touch large, stateful modules; without strong characterization tests they could regress UI behaviour or history retention. Coordinators must avoid introducing new circular imports across Talon modules.
- **Mitigations**: follow the tests-first commitment, introduce facades incrementally (facade + adapter layers), and reuse existing orchestrators (`requestLifecycle`, `suggestionCoordinator`) to avoid rewriting business logic wholesale.

---

## Salient Tasks

- Add persona/intent catalog façade and migrate GPT actions + docs to consume it.
- Introduce shared surface guidance coordinator; delegate canvas mouse/key handlers and persona summaries.
- Implement history lifecycle façade; update request history/log modules and canvases to use it.
- Extend existing tests (history, persona, GUI suites) with necessary characterization coverage before behaviour changes.
- Completed (Loops 0034–0036): centralize help metadata summary helper, regenerate cheat sheet snapshot, and guard README coverage via `_tests/test_readme_guardrails_docs.py`.
- Completed (Loop 0099+): Help Hub buttons advertise orchestrator voice hints; metadata summaries now flag orchestrator alias coverage for downstream docs.
