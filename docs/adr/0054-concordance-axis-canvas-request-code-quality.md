# ADR-0054 – Concordance Code Quality for Axis Registry, Canvas UIs, and Request Pipeline

Status: Accepted  
Date: 2025-12-15  
Owners: Talon AI tools maintainers

## Context

- Statement-level churn × complexity heatmap (since “90 days ago”, scope: `lib/`, `GPT/`, `copilot/`, `tests/`) read from `tmp/churn-scan/line-hotspots.json`.
- Top hotspots by score (sample):

| Node | File:Line | Score | Churn | Coord | Cx |
| --- | --- | --- | --- | --- | --- |
| `axisConfig.py` (file) | `lib/axisConfig.py:1` | 18209.3 | 550 | 10498.0 | 1.73 |
| `modelHelpGUI.py` (file) | `lib/modelHelpGUI.py:1` | 8067.0 | 784 | 8067.0 | 1.00 |
| `readme.md` (file) | `GPT/readme.md:1` | 6164.9 | 360 | 4643.0 | 1.33 |
| `_append_text` | `lib/modelHelpers.py:777` | 5925.1 | 234 | 4487.0 | 1.32 |
| `test_model_pattern_gui.py` (file) | `tests/test_model_pattern_gui.py:1` | 4999.0 | 465 | 4999.0 | 1.00 |
| `_scroll_pattern_list` | `lib/modelPatternGUI.py:197` | 4917.8 | 331 | 4472.0 | 1.10 |
| `_on_mouse` | `lib/helpHub.py:473` | 4591.3 | 299 | 3332.0 | 1.38 |
| `_header_label` | `lib/modelResponseCanvas.py:617` | 4434.5 | 399 | 3429.0 | 1.29 |

- Hotspot clusters:
  - **Axis registry and static prompt assets:** `lib/axisConfig.py`, `lib/talonSettings.py` axis token readers, `lib/staticPromptConfig.py`, `GPT/gpt.py` static prompt builders, `GPT/readme.md`, tests/docs that mirror axis lists.
  - **Canvas-heavy overlays:** `lib/modelHelpGUI.py`, `lib/modelPatternGUI.py` (scroll, mouse handlers, draw routines), `lib/modelPromptPatternGUI.py` (init, debug, wrap), `lib/modelResponseCanvas.py` (header/draw/wrap), `lib/modelHelpCanvas.py` (default draw, mouse), `lib/helpHub.py` (mouse/key), `lib/modelSuggestionGUI.py`.
  - **Request pipeline and history/resilience:** `lib/modelHelpers.py` streaming/error helpers, `lib/requestHistoryActions.py` save-dir/history axes, `lib/requestState.py` transition, `lib/requestLog.py` filters, `GPT/gpt.py` apply/save helpers; tests `tests/test_gpt_actions.py`, `tests/test_integration_suggestions.py`.
  - **Test/doc guardrails with churn:** `tests/test_model_pattern_gui.py`, `tests/test_static_prompt_docs.py`, `tests/test_axis_mapping.py`, `tests/test_readme_axis_lists.py`, `tests/test_voice_audience_tone_purpose_lists.py`, `tests/test_model_state.py`.

## Problem

High coordination weight and churn sit in domains where contracts are spread across generated/static assets, multiple canvas overlays, and request lifecycle helpers. Visibility is low (implicit data shapes and duplicated axis tokens), scope is wide (UI surfaces and tests share fixtures and axes), and volatility is high (frequent edits to axis lists, canvases, and streaming helpers). This combination raises Concordance scores and makes refactors risky without clearer boundaries and branch-focused tests.

## Hidden Domains (“Tunes”) and Concordance Signals

- **Axis Registry SSOT:** Axis token maps, list files, static prompt docs, and GPT entrypoints drift across `axisConfig`, `talonSettings`, static prompt config, and README/list fixtures. Visibility is low because generation steps are implicit; scope is repo-wide (axis usage surfaces everywhere); volatility is high due to list edits.
- **Canvas Overlay Orchestration:** Help hub, help canvas, pattern/prompt canvases, response/suggestion canvases each own event handling and layout math, closing/activation, and scroll logic. Visibility is scattered across handlers; scope is cross-surface (each closes others); volatility is high from iterative UI tweaks and test churn.
- **Request Pipeline and Resilience:** Streaming append, tool calls, request/log history, and error handling are split across `modelHelpers`, `requestHistoryActions`, `requestState`, `requestLog`, and GPT save/apply helpers. Visibility is implicit via shared mutable state; scope touches UI overlays, history, and persistence; volatility is high because failures and new flows get patched locally.
- **Tests/Docs as Coordination Fabric:** High-churn tests and docs mirror axis lists and canvas behaviors but rely on implicit fixtures. Visibility into what they guard is low; scope is broad because they gate releases; volatility reflects upstream instability.

## Decision

- Treat **axis registry data** as a single published contract and align generation/consumption (code + docs + lists) to it, reducing hidden drift and coordination cost.
- Extract **shared canvas overlay patterns** (event handling, scroll/clamp, close/activation, text wrapping) into a thin façade that existing canvases can compose, clarifying responsibilities and reducing volatility.
- Pull **request pipeline resilience** into a clearer orchestration path that reuses the existing `requestController`/`requestBus` shape, so streaming, retries, and history integrations stop leaking across helpers and canvases.
- For each slice, tighten or reuse existing branch-focused tests before refactors, aiming to **lower sustained Concordance scores** by raising visibility, narrowing scope, and reducing volatility—not by weakening checks or coverage.

## Tests-First Principle

> Before changing behavior or structure, ensure the affected paths have adequate branch-level characterization. Reuse existing tests when they already cover the branches being touched; add focused characterization only where gaps exist. Prefer behavioral/contract assertions over implementation details, and keep the suite lean.

## Refactor Plan (with prior art reuse)

### Axis Registry SSOT
- **Original Draft:** Introduce a new axis-registry generator and have talon settings, static prompts, and README/list assets pull from it.
- **Similar Existing Behavior:** `lib/axisCatalog.py` already centralizes axis metadata; `lib/axisConfig.py` is generated from registry; `lib/staticPromptConfig.py` and `GPT/gpt.py` static prompt builders consume axis data; tests `tests/test_axis_mapping.py`, `tests/test_readme_axis_lists.py`, `tests/test_static_prompt_docs.py` assert parts of the contract.
- **Revised Recommendation:** Extend `axisCatalog` as the single SSOT and make `axisConfig`, static prompt docs, and GPT static prompt builders consume a shared serialization routine. Add a small regen helper (script or Makefile target) that also refreshes README/list fixtures. Keep regeneration idempotent and document it near `axisCatalog`. Align with ADRs 0044–0046 scope on axis config/help streaming to avoid divergent pipelines.
- **Phasing:** 1) Introduce shared serializer + regen command; 2) Switch `talonSettings`/static prompt builders to the serializer; 3) Update README/list fixtures via regen; 4) Trim redundant per-module maps.

### Canvas Overlay Orchestration
- **Original Draft:** Create a new canvas base and rewrite all overlays to use it.
- **Similar Existing Behavior:** `lib/helpUI.py` provides shared scroll/wheel helpers; canvases already close each other via `_close_overlapping_surfaces`; `modelPatternGUI`/`modelPromptPatternGUI` share debug/wrap patterns; `modelResponseCanvas` and `modelHelpCanvas` share layout idioms; tests `tests/test_model_pattern_gui.py`, `tests/test_model_state.py` cover core flows.
- **Revised Recommendation:** Extract a light “overlay behaviors” module that wraps `helpUI` primitives for scroll, key/mouse routing, close/activation, and text wrapping. Refactor canvases incrementally to use these hooks without changing visual layout. Co-locate shared constants (padding, clamp rules) and rely on existing close semantics. Keep event handler signatures consistent to reduce branching in tests.
- **Phasing:** 1) Add shared overlay helper layer atop `helpUI`; 2) Migrate `modelPatternGUI` and `modelPromptPatternGUI` handlers; 3) Migrate help hub/help canvas and response/suggestion canvases; 4) Consolidate duplicated constants; 5) Update tests to target shared hooks instead of per-canvas branches.

### Request Pipeline and Resilience
- **Original Draft:** Introduce a new request façade to own streaming/error handling/history saves.
- **Similar Existing Behavior:** `lib/requestController.py`/`lib/requestBus.py`/`lib/requestState.py` already form an orchestrator; `lib/modelHelpers.py` implements streaming append/error handling; `lib/requestHistoryActions.py` and `lib/requestLog.py` manage persistence; tests `tests/test_gpt_actions.py`, `tests/test_integration_suggestions.py`, `tests/test_recursive_orchestrator.py` exercise request flows.
- **Revised Recommendation:** Align streaming/error helpers with `requestController` by exposing explicit lifecycle hooks (`on_append`, `on_retry`, `on_history_save`) and routing UI refresh through the controller rather than per-canvas helpers. Normalize history/save-dir logic in `requestHistoryActions` behind a small interface consumed by GPT entrypoints. Keep telemetry/notifications in `modelHelpers.notify` but minimize cross-module state.
- **Phasing:** 1) Define lifecycle hooks in `requestController` and thread through `modelHelpers` streaming functions; 2) Swap request history/save-dir calls to the normalized interface; 3) Update GPT entrypoints to use the hooks; 4) Trim duplicate append/error branches in canvases.

### Tests-First Refactor Plan

- **Axis Registry SSOT:** Rely on `tests/test_axis_mapping.py` and `tests/test_readme_axis_lists.py` for existing branch coverage; extend with a regen smoke test that asserts generated `axisConfig`/README/list artifacts stay in sync. Add characterization only if serializer changes token ordering or filters.
- **Canvas Overlay Orchestration:** Use `tests/test_model_pattern_gui.py` and `tests/test_model_state.py` to cover scroll/key/mouse flows; add focused tests for shared overlay helper hooks (scroll clamp, close ordering, wrap sizing). Avoid duplicating per-canvas snapshots; prefer table-driven cases across canvases.
- **Request Pipeline and Resilience:** Use `tests/test_gpt_actions.py`, `tests/test_integration_suggestions.py`, `tests/test_recursive_orchestrator.py` for pipeline coverage; add characterization for streaming error/retry paths and history save-dir resolution before refactors. Ensure error branches and cancel cases are exercised.
- **Docs/List Fixtures:** Keep `tests/test_static_prompt_docs.py` and `tests/test_voice_audience_tone_purpose_lists.py` as guardrails; add a single fixture-alignment test if regen flow changes formatting.

## Consequences

- **Positive:** Clearer domain boundaries reduce coordination cost; shared serializers and overlay helpers cut duplicate branching; Concordance scores for axis/canvas/request hotspots should fall as visibility increases and scope/volatility narrow; regen flow reduces doc/list drift.
- **Risks:** Shared helpers can introduce regressions if contracts are implicit; regen may reorder tokens unexpectedly; canvas refactors risk input handling regressions. Mitigate via branch-focused tests and phased rollout.
- **Concordance Effect:** Expected to lower sustained scores for the identified hotspots by improving structure and tests rather than weakening checks. Monitor heatmap/Concordance after each phase; do not relax scoring thresholds.

## Salient Tasks

- Add axis serializer + regen command; wire `axisConfig`, static prompt builders, and README/list regen to it; refresh fixtures.
- Introduce overlay helper layer atop `helpUI`; migrate pattern/prompt canvases first, then help hub/help canvas/response/suggestion canvases; align constants.
- Define request lifecycle hooks in `requestController`; route `modelHelpers` streaming/error handling and history saves through them; update GPT entrypoints.
- Expand/extend tests as outlined in the Tests-First plan before each refactor slice; keep runs via `python3 -m pytest`.
