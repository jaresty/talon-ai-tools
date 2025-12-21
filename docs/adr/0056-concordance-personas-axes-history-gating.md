# ADR-0056 – Concordance Personas, Axes, and History Gating

Status: Proposed  
Date: 2025-12-17  
Owners: Talon AI tools maintainers

---

## Context

- Statement-level churn × complexity heatmap (since “90 days ago”, scope: `lib/`, `GPT/`, `copilot/`, `tests/`) read from `tmp/churn-scan/line-hotspots.json`.
- Git log fixture for the same window and scope lives at `tmp/churn-scan/git-log-stat.txt`.
- Top node-level hotspots from the latest scan highlight three strongly coupled areas (scores approximate):
  - **Axis and token configuration + docs**
    - `lib/axisConfig.py` (File, line 1) — score ≈ **28k**, very high churn and coordination.
    - `lib/talonSettings.py::{_read_axis_value_to_key_map,_read_axis_default_from_list,_axis_tokens,_resolve_axis_for_token,AxisValues}`.
    - `lib/staticPromptConfig.py::{completeness_freeform_allowlist,static_prompt_catalog,_read_static_prompt_tokens}`.
    - `lib/axisCatalog.py::{axis_catalog,axis_list_tokens}`.
    - `GPT/gpt.py::{static_prompt_catalog,_build_axis_docs,_build_static_prompt_docs,axis_catalog,_axis_drop_summary,_read_list_items}`.
    - Talon lists under `GPT/lists/*.talon-list` and docs in `GPT/readme.md`.
  - **Personas, intent presets, and Concordance-facing help/suggestion surfaces**
    - `lib/personaConfig.py` (File) and `IntentPreset`.
    - `GPT/gpt.py::{_validated_persona_value,_canonical_persona_value,_build_persona_intent_docs,_refresh_persona_intent_lists,persona_set_preset,intent_set_preset,gpt_preset_save}`.
    - `lib/helpHub.py::_persona_presets`.
    - `lib/modelSuggestionGUI.py::{_match_persona_preset,_suggestion_stance_info,_measure_suggestion_height}`.
    - Tests: `tests/test_voice_audience_tone_purpose_lists.py`, `tests/test_model_types_system_prompt.py`, `tests/test_model_suggestion_gui.py`, `tests/test_integration_suggestions.py`.
  - **Request lifecycle, history/log summaries, and “request in flight” gating**
    - `lib/requestHistoryActions.py::{requestHistoryActions.py,_request_is_in_flight,_reject_if_request_in_flight,_notify_with_drop_reason,_clear_notify_suppression,_model_source_save_dir,_filter_axis_tokens,history_axes_for,history_summary_lines,_directional_tokens_for_entry,gpt_request_history_show_latest,_save_history_prompt_to_file}`.
    - `lib/requestLog.py::{_filter_axes_payload,notify,append_entry}`.
    - `lib/historyQuery.py::history_drawer_entries_from`.
    - `lib/requestController.py::{__init__,handle}`, `lib/requestState.py::transition`, `lib/requestLifecycle.py::reduce_request_state`, `lib/requestBus.py`, `lib/requestUI.py::{_notify,_on_state_change}`.
    - `lib/modelHelpers.py::{build_system_prompt_messages,build_request,build_chatgpt_request,_build_request_context,_build_timeout_context,_send_request_streaming,_update_streaming_snapshot,build_exchange_snapshot,_warn_streaming_disabled,_handle_streaming_error,_handle_max_attempts_exceeded,_ensure_request_supported,call_tool,_build_snippet_context,chats_to_string}`.
    - GUI gating and canvas helpers: `_request_is_in_flight` / `_reject_if_request_in_flight` variants across `GPT/gpt.py`, `lib/helpHub.py`, `lib/modelHelpCanvas.py`, `lib/modelPromptPatternGUI.py`, `lib/modelSuggestionGUI.py`, `lib/requestHistoryDrawer.py`, `lib/modelConfirmationGUI.py`, `lib/providerCommands.py`.
    - Tests: `tests/test_gpt_actions.py`, `tests/test_request_history_actions.py`, `tests/test_request_history.py`, `tests/test_request_streaming.py`, `tests/test_model_help_gui.py`, `tests/test_model_help_canvas.py`, `tests/test_model_suggestion_gui.py`, `tests/test_integration_suggestions.py`.
- Recent Concordance ADRs already in this repo:
  - **ADR-0045** and **ADR-0046**: define Axis & Static Prompt, Help Navigation, Pattern Debug, and Streaming Response domains.
  - **ADR-0054**: raises code-quality expectations for axis registry, canvas overlays, and the request pipeline, with a tests-first refactor plan.
  - **ADR-0055**: retires source-only save paths in favour of the unified `file` destination.
- Despite these decisions, the latest heatmap shows sustained or newly prominent hotspots in persona/preset handling, axis token hydration into history/logs, and duplicated request-in-flight gating across canvases and helpers.

---

## Problem

High churn and coordination weight now concentrate in three overlapping Concordance domains that build on but are not fully resolved by ADR-0045/0046/0054/0055:

1. **Axis tokens and history/log summaries** remain split across `axisConfig`, `axisCatalog`, `talonSettings`, `staticPromptConfig`, `requestLog`, and `requestHistoryActions`. Axis semantics feed Concordance scoring and health snapshots, but payload shapes and axis filters are duplicated and partially implicit, making it hard to reason about which axes are present where, and why.
2. **Personas, intent presets, and Concordance-facing help/suggestion flows** share an implicit domain: persona definitions in `personaConfig`, GPT actions and docs, help hub preset UIs, and suggestion canvases. Contracts between persona presets, axis tokens, and on-screen guidance are under-specified, leading to frequent edits across config, GPT actions, help hub, and GUI logic.
3. **Request-in-flight gating and streaming lifecycle** logic is repeated across GPT actions, canvases, confirmation/help/suggestion GUIs, and history drawers. Each module carries its own `_request_is_in_flight` / `_reject_if_request_in_flight` helpers, while `requestController`/`requestState`/`requestLifecycle` and `modelHelpers` already form a partial orchestrator. This duplication creates unclear ownership of concurrency policies and error handling.

These domains exhibit:

- **Low visibility**: contracts between catalogued axes, persona presets, history/log payloads, and GUI surfaces are encoded in scattered helpers and booleans rather than explicit types and facades.
- **Wide scope**: changes must touch `lib/`, `GPT/`, Talon lists, docs, and multiple test suites at once, raising coordination cost and refactor risk.
- **High volatility**: recent commits show repeated adjustments to persona presets, axis filters, history summaries, and gating conditions, with Concordance and heatmap scores staying elevated.

Reducing Concordance scores here requires clarifying these domains and boundaries, not weakening tests or Concordance checks.

---

## Hidden Domains (“Tunes”) and Concordance Analysis

### 1. Axis Tokens & History Snapshot Domain

- **Members (sample)**
  - `lib/axisConfig.py` (file), `lib/axisCatalog.py::{axis_catalog,axis_list_tokens}`.
  - `lib/talonSettings.py::{_read_axis_value_to_key_map,_read_axis_default_from_list,_axis_tokens,_resolve_axis_for_token,AxisValues}`.
  - `lib/staticPromptConfig.py::{completeness_freeform_allowlist,static_prompt_catalog,_read_static_prompt_tokens}`.
  - `lib/requestLog.py::{_filter_axes_payload,notify,append_entry}`.
  - `lib/requestHistoryActions.py::{_filter_axis_tokens,history_axes_for,history_summary_lines,_directional_tokens_for_entry,gpt_request_history_show_latest}`.
  - `lib/historyQuery.py::history_drawer_entries_from`.
  - `GPT/gpt.py::{axis_catalog,_build_axis_docs,_axis_drop_summary,static_prompt_catalog,_build_static_prompt_docs,_read_list_items}`.
  - Tests: `tests/test_axis_mapping.py`, `tests/test_static_prompt_config.py`, `tests/test_static_prompt_docs.py`, `tests/test_readme_axis_lists.py`, `tests/test_request_history_actions.py`, `tests/test_request_history.py`, `tests/test_request_log.py`.
- **Visibility**
  - Axis semantics are catalogued in `axisCatalog`/`axisConfig` and static prompt config, but history/log payloads and `history_axes_for`/`_filter_axis_tokens` reinvent axis projections per call site.
  - Concordance-relevant axis signals for history summaries and logs are not expressed as a single, typed snapshot; contributors must infer which axes matter from scattered filters.
- **Scope**
   - Changes to axis definitions or filters affect: Concordance scoring, history drawers, request logs, README/help docs, GPT help output, and multiple tests.
   - Tests and docs act as coordination fabric; drift in one place often forces brittle updates elsewhere.
   - Legacy guardrails that once allowed lens-less history entries (for example, `require_directional=False`) have been removed. A repo-wide search on 2025-12-17 found no remaining in-repo consumers, and no external macros or scripts remain; the runtime’s immediate-failure stance now holds end-to-end.
   - **Volatility**
   - Recent churn in `axisConfig`, `staticPromptConfig`, `talonSettings` axis functions, and request history/log helpers indicates an evolving story around which axes are recorded, where, and with what defaults.


**Hidden domain / tune**: *Axis Snapshot & History Concordance Domain* — the shared intent is to record and present a consistent, Concordance-relevant snapshot of axes and static prompt semantics across history summaries, logs, docs, and GUIs.

### 2. Persona & Intent Preset Concordance Domain

- **Members (sample)**
  - `lib/personaConfig.py` (file), `IntentPreset`.
  - `GPT/gpt.py::{_validated_persona_value,_canonical_persona_value,_build_persona_intent_docs,_refresh_persona_intent_lists,persona_set_preset,intent_set_preset,gpt_preset_save}`.
  - `lib/helpHub.py::_persona_presets`.
  - `lib/modelSuggestionGUI.py::{_match_persona_preset,_suggestion_stance_info,_measure_suggestion_height}`.
  - Axis-aware persona and style lists under `GPT/lists/*.talon-list`.
  - Tests: `tests/test_voice_audience_tone_purpose_lists.py`, `tests/test_model_types_system_prompt.py`, `tests/test_model_suggestion_gui.py`, `tests/test_integration_suggestions.py`, `tests/test_gpt_actions.py`.
- **Visibility**
  - Persona/intent presets are defined in `personaConfig` and surfaced via GPT actions, help hub presets, and suggestion canvases, but the contract between axis tokens, persona presets, and Concordance scoring is implicit.
  - Validation and canonicalization helpers in `gpt.py` encode rules that are not clearly tied back to the axis catalog or persona presets.
- **Scope**
  - Changes propagate to model settings, GUI presets, suggestion tunes, voice/tone/purpose lists, docs, and tests.
  - Personas and intents influence how Concordance interprets health snapshots (e.g., “persona not set”, “tone misaligned”), so unstable semantics affect scoring.
- **Volatility**
  - High churn in persona validation, preset matching, and related tests suggests ongoing tuning of how personas/intents are represented and surfaced.

**Hidden domain / tune**: *Persona & Intent Preset Concordance Domain* — the shared intent is to provide a stable, axis-aware contract for personas and intents that spans config, GPT actions, help hub, and suggestion canvases.

### 3. Request Gating, Streaming, and History Lifecycle Domain

- **Members (sample)**
  - `lib/requestController.py::{__init__,handle}`, `lib/requestState.py::transition`, `lib/requestLifecycle.py::reduce_request_state`, `lib/requestBus.py`, `lib/requestUI.py::{requestUI.py,_notify,_on_state_change}`.
  - `lib/modelHelpers.py::{build_request,build_chatgpt_request,build_system_prompt_messages,_build_request_context,_build_timeout_context,_send_request_streaming,_update_streaming_snapshot,build_exchange_snapshot,_warn_streaming_disabled,_handle_streaming_error,_handle_max_attempts_exceeded,_ensure_request_supported,call_tool,_build_snippet_context,chats_to_string,_update_lifecycle,_send_request_streaming,_build_request_context,_build_timeout_context}`.
  - Per-surface gating helpers: `_request_is_in_flight` / `_reject_if_request_in_flight` in `GPT/gpt.py`, `lib/helpHub.py`, `lib/modelHelpCanvas.py`, `lib/modelPromptPatternGUI.py`, `lib/modelSuggestionGUI.py`, `lib/modelConfirmationGUI.py`, `lib/requestHistoryDrawer.py`, `lib/providerCommands.py`, `lib/requestHistoryActions.py`.
  - History/destination helpers: `lib/requestHistoryActions.py::{_save_history_prompt_to_file,_model_source_save_dir,gpt_request_history_show_latest}`, `lib/modelDestination.py::{append_text,insert,_slug}`, plus ADR-0055’s migration to `file` destination.
  - Tests: `tests/test_gpt_actions.py`, `tests/test_request_history_actions.py`, `tests/test_request_history.py`, `tests/test_request_streaming.py`, `tests/test_model_destination.py`, `tests/test_model_help_gui.py`, `tests/test_model_help_canvas.py`, `tests/test_model_suggestion_gui.py`, `tests/test_integration_suggestions.py`.
- **Visibility**
  - Request lifecycle policies (what it means for a request to be “in flight”, how cancellations and retries work, when history entries are written) are encoded in many small helpers rather than a single orchestrated API.
  - GUI surfaces and GPT actions implement their own gating logic instead of delegating to `requestController`/`requestState`/`requestLifecycle`.
- **Scope**
  - Behaviour changes affect GPT actions, GUI canvases, history drawers, destinations, logs, and Concordance scoring hooks that read history/streaming state.
  - Bugs or inconsistencies in gating can cause double-requests, dropped history entries, or misleading Concordance snapshots.
- **Volatility**
  - The heatmap shows repeated edits to `_request_is_in_flight` / `_reject_if_request_in_flight`, streaming helpers, and history actions, indicating an unstable coordination surface.

**Hidden domain / tune**: *Request Gating & Streaming Lifecycle Domain* — the shared intent is to centralize request concurrency, streaming, and history write policies so GUIs and GPT actions consume a single, testable lifecycle.

---

## Decision

We will treat the **Axis Snapshot & History**, **Persona & Intent Preset**, and **Request Gating & Streaming Lifecycle** domains as first-class Concordance domains, building on ADR-0045/0046/0054/0055, and evolve the code to:

1. **Axis Snapshot & History Concordance**
   - Extend the existing `axisCatalog` / axis registry façade so that **history and log payloads derive their axis views from a single, typed “axis snapshot” representation**, not bespoke filters per call site.
   - Make the relationship between `axisConfig`, `axisCatalog`, `talonSettings` axis helpers, `staticPromptConfig`, `requestLog`, `requestHistoryActions`, and README/help/doc surfaces explicit through a small set of APIs.
2. **Persona & Intent Preset Concordance**
   - Treat `personaConfig` and persona/intent helpers in `GPT/gpt.py` and `helpHub` as a single **Persona & Intent domain**, backed by axis-aware presets.
   - Expose a canonical persona/intent catalog that GUIs, GPT actions, and docs consume, aligning semantics across config, lists, and Concordance checks.
3. **Request Gating & Streaming Lifecycle**
   - Centralize “request in flight” and streaming lifecycle policies in `requestController`/`requestState`/`requestLifecycle` and `modelHelpers`, and have canvases, GPT actions, and history drawers **call into these policies instead of carrying their own gating helpers**.
   - Complete the migration started in ADR-0055 by routing remaining history saves through the unified `file` destination and treating history writes as lifecycle events rather than bespoke helpers.

For all three domains, the intended long-term effect is to **reduce sustained Concordance scores for the relevant hotspots** by increasing visibility, narrowing scope, and reducing volatility. We explicitly will not relax Concordance thresholds, drop meaningful checks, or weaken tests to achieve lower scores.

---

## Tests-First Principle

> At each step in these domains, we will first analyze existing tests to ensure that the behaviour we intend to change is well covered. Where coverage is insufficient, we will add focused characterization tests capturing current behaviour (including relevant branches and error paths), and then proceed with the refactor guarded by those tests. Where coverage is already strong and branch-focused for the paths we are changing, we will rely on and, if needed, extend those existing tests rather than adding redundant characterization tests.
>
> Behaviour-changing refactors must not proceed without **adequate** characterization tests for the behaviour being changed. When existing tests already provide good behavioural and branch coverage for the paths being changed, prefer **reusing and extending** those tests over adding near-duplicate ones; focus tests on behavioural/contract-level assertions instead of internal implementation details.

---

## Refactor Plan (with Prior Art Alignment)

### 1. Axis Snapshot & History Concordance Domain

- **Original Draft Idea**
  - High churn and coordination around axis token readers, static prompt config, axis catalog, history axes filters, and log payloads suggest a single domain that governs **what axes we record and surface where**.
- **Similar Existing Behavior / Prior Art**
  - ADR-0045/0046/0054 already establish an **Axis & Static Prompt Concordance** domain and recommend an `axis_catalog` façade.
  - `lib/axisCatalog.py` exposes axis metadata; `lib/axisConfig.py` and `lib/axisMappings.py` define tokens and mappings.
  - `lib/staticPromptConfig.py` and `GPT/gpt.py::static_prompt_catalog` provide static prompt profiles and catalog views.
  - `lib/talonSettings.py` contains axis token readers and mappings, used by Talon settings UIs.
  - `lib/requestLog.py::_filter_axes_payload` and `lib/requestHistoryActions.py::{_filter_axis_tokens,history_axes_for,history_summary_lines}` filter and summarize axes for logs and history drawers.
  - Tests under `tests/test_axis_mapping.py`, `tests/test_static_prompt_config.py`, `tests/test_static_prompt_docs.py`, `tests/test_readme_axis_lists.py`, `tests/test_request_history_actions.py`, `tests/test_request_history.py`, and `tests/test_request_log.py` already exercise parts of this contract.
- **Revised Recommendation**
  - **Axis snapshot type**
    - Define a small `AxisSnapshot` structure (Python type or dict schema) derived from `axisCatalog` that represents the Concordance-relevant view of axes for a given request/history entry (e.g., enabled axes, key values, derived flags).
    - Ensure the snapshot drops legacy or non-catalog axes (for example, the retired `style` axis and bespoke caller metadata) so Concordance-facing surfaces only carry the agreed axis set. Legacy style handling has now been removed from request history/log code entirely; incoming data that still references the style axis now raises errors rather than emitting warnings.
    - Make `requestLog._filter_axes_payload`, `requestHistoryActions.{_filter_axis_tokens,history_axes_for,history_summary_lines,_directional_tokens_for_entry}`, and `historyQuery.history_drawer_entries_from` consume this type instead of ad hoc filters.
   - Remove duplicate axis-name/description tables from history/log modules where they overlap with the catalog and retire the legacy “extra axes” passthrough once all consumers rely on the shared snapshot.
    - (Completed 2025-12-17) Runtime guardrails now reject any request-history writes lacking a directional lens (the `require_directional` escape hatch is gone); remaining effort focuses on auditing and, when necessary, purging legacy data outside this repo that still lacks directional metadata.


   - **Phase 3 – Docs/help alignment**
      - Ensure README/help and static prompt docs that present axes do so via the catalog façade and/or a shared doc-generation helper, reusing ADR-0046/0054 patterns.
      - Clearly document that requests missing a directional lens fail immediately; there is no remediation path or compatibility shim once the guardrails are removed.


    - Ensure README/help and static prompt docs that present axes do so via the catalog façade and/or a shared doc-generation helper, reusing ADR-0046/0054 patterns.

### 2. Persona & Intent Preset Concordance Domain

- **Original Draft Idea**
  - Persona and intent presets are encoded across `personaConfig`, GPT helpers, help hub, suggestion GUIs, and Talon lists with high churn and coordination but no explicit domain boundary.
- **Similar Existing Behavior / Prior Art**
  - `lib/personaConfig.py` defines personas/intents used by GPT flows.
  - `GPT/gpt.py` implements persona validation, canonicalization, and preset actions; ADR-0037 and ADR-0046 already encourage orchestrator-based designs for GPT actions.
  - `lib/helpHub.py::_persona_presets` and `lib/modelSuggestionGUI.py::{_match_persona_preset,_suggestion_stance_info}` surface presets and stance info to users.
  - Axis and static prompt domains (ADRs 0036/0044/0045/0046/0054) treat axes as first-class Concordance inputs but do not yet fully align persona/intents with those axes.
  - Tests under `tests/test_voice_audience_tone_purpose_lists.py`, `tests/test_model_types_system_prompt.py`, `tests/test_model_suggestion_gui.py`, `tests/test_integration_suggestions.py`, and `tests/test_gpt_actions.py` exercise persona/intent behaviours from different angles.
- **Revised Recommendation**
  - **Persona/intent catalog**
    - Introduce or extend a `persona_catalog` / `intent_catalog` helper, backed by `personaConfig`, that:
      - Exposes typed persona/intent presets, including associated axis tokens (voice, tone, purpose) and defaults.
      - Provides a single API used by GPT actions (`persona_set_preset`, `intent_set_preset`, `gpt_preset_save`), help hub (`_persona_presets`), suggestion GUIs, and docs.
  - **Canonicalization and validation alignment**
    - Refactor `_validated_persona_value`, `_canonical_persona_value`, and `_build_persona_intent_docs` in `GPT/gpt.py` to operate entirely in terms of the persona/intent catalog and axis catalog, rather than bespoke string logic.
    - Ensure persona/intent lists under `GPT/lists/*.talon-list` are generated or validated against this catalog, similar to axis list validation in ADR-0046.
  - **Concordance visibility**
    - Make Concordance scoring and health snapshots consume persona/intent state explicitly (via the catalog), so that missing or conflicting persona/intent assignments are visible and testable rather than inferred from scattered strings.
- **Phasing**
  - **Phase 1 – Persona/intent catalog and tests**
    - Define the catalog shape and add tests that assert round-tripping between `personaConfig`, GPT actions, help hub presets, suggestion GUIs, and list files for a representative subset.
  - **Phase 2 – GPT and GUI refactor**
    - Route GPT persona/intent commands and help hub/suggestion GUIs through the catalog, trimming redundant preset/stance logic.
  - **Phase 3 – Concordance integration**
    - Update Concordance-related code to read persona/intent state from the catalog and surface it in axis/history snapshots where appropriate.

### 3. Request Gating & Streaming Lifecycle Domain

- **Original Draft Idea**
  - High churn in `_request_is_in_flight` / `_reject_if_request_in_flight` helpers, streaming functions in `modelHelpers`, and history actions suggests that request gating and streaming lifecycle should be owned by a single orchestrated domain rather than duplicated per surface.
- **Similar Existing Behavior / Prior Art**
  - ADR-0045/0046/0054 already designate **Request Pipeline and Resilience** as a Concordance domain and recommend a `StreamingSession`-style façade.
  - `lib/requestController.py`, `lib/requestState.py`, `lib/requestLifecycle.py`, and `lib/requestBus.py` form an implicit orchestrator for request state transitions.
  - `lib/modelHelpers.py` centralizes streaming and error-handling helpers but callers still interpret “in flight” and retries locally.
  - `lib/requestHistoryActions.py` and `lib/requestHistoryDrawer.py` control when history entries appear and how they’re summarized.
  - ADR-0055 migrates source-only saves toward the unified `file` destination but remaining helpers like `_save_history_prompt_to_file` and `_model_source_save_dir` still appear as hotspots.
- **Revised Recommendation**
  - **Central request gating API**
    - Extend `requestController`/`requestState`/`requestLifecycle` with explicit helpers for:
      - Asking whether a request is in flight (`is_in_flight`),
      - Attempting to start a new request (`try_start_request` with structured drop reasons), and
      - Handling cancellations and retries.
    - Replace duplicated `_request_is_in_flight` / `_reject_if_request_in_flight` helpers in GPT actions and canvases with calls into this API.
  - **StreamingSession and history hooks**
    - Implement a `StreamingSession` (as sketched in ADR-0046/0054) that:
      - Owns chunk accumulation, error classification, and refresh throttling.
      - Emits structured events for “history/write snapshot”, “log entry”, and “UI refresh”, consumed by `requestHistoryActions`, `requestLog`, `modelResponseCanvas`, and GUIs.
    - Retire or narrow `_save_history_prompt_to_file` and `_model_source_save_dir` to thin adapters over the `file` destination and history events, in line with ADR-0055.
  - **Concordance-aware gating**
    - Make drop reasons and gating outcomes visible in logs/history (`_notify_with_drop_reason`, `history_summary_lines`) using a small, typed schema. Concordance checks should be able to distinguish “blocked for good reason” from “dropped silently”.
- **Phasing**
  - **Phase 1 – Gating helpers on controller/state**
    - Introduce `is_in_flight`/`try_start_request` on `requestController`/`requestState` and update a small, well-tested subset of callers (`GPT/gpt.py`, `modelConfirmationGUI`) to use them.
  - **Phase 2 – StreamingSession and history writes**
    - Introduce `StreamingSession` and move streaming helpers in `modelHelpers` to delegate lifecycle decisions to it.
    - Route history/log writes via StreamingSession events and the `file` destination; deprecate direct prompt-only writers.
  - **Phase 3 – Canvas and GUI migration**
    - Update help/suggestion/history canvases and provider GUIs to rely on the centralized gating API and StreamingSession events, trimming local `_request_is_in_flight` / `_reject_if_request_in_flight` clones.

---

## Tests-First Refactor Plan

For each domain, we will align with the existing test suites and add characterization only where necessary.

### Axis Snapshot & History Concordance

- **Existing coverage (non-exhaustive)**
  - `tests/test_axis_mapping.py` — axis token and mapping behaviour.
  - `tests/test_static_prompt_config.py` — static prompt config profiles.
  - `tests/test_static_prompt_docs.py` — static prompt docs/list alignment.
  - `tests/test_readme_axis_lists.py` — README axis list rendering.
  - `tests/test_request_history_actions.py`, `tests/test_request_history.py`, `tests/test_request_log.py` — history/log axis behaviour and summaries.
- **Plan**
  - Before introducing `AxisSnapshot`:
    - Add focused tests that characterize current axis content for a representative history/log entry (which axes appear, how missing/extra axes are handled).
  - After wiring `AxisSnapshot`:
    - Reuse and, where needed, extend these tests to assert that history/log outputs derive from the catalog and that Concordance-relevant axes are preserved.
    - Add a regression test (or CI assertion) that fails when a history append omits directional axes, proving the guardrail remains enforced.
  - Keep guardrail suites (e.g., `_tests/test_run_guardrails_ci.py`, `_tests/test_history_axis_validate.py`, `_tests/test_history_axis_export_telemetry.py`, `_tests/test_make_axis_guardrails_ci.py`) and `scripts/tools/run_guardrails_ci.sh` catching axis/catalog drift, directionality guardrails, and telemetry exports before refactors land.
  - Ensure doc-generation helpers (`scripts/tools/generate_readme_axis_lists.py`, `scripts/tools/generate-axis-cheatsheet.py`, `GPT/gpt.py::_build_axis_docs`) stay tied to the same snapshot so README/help/cheatsheet artefacts fail CI when catalog tokens diverge.

### Persona & Intent Preset Concordance

- **Existing coverage (non-exhaustive)**
  - `tests/test_voice_audience_tone_purpose_lists.py` — persona/voice/tone/purpose lists.
  - `tests/test_model_types_system_prompt.py` — model/system prompt type handling.
  - `tests/test_model_suggestion_gui.py` — suggestion canvas behaviour including stance presets.
  - `tests/test_integration_suggestions.py`, `tests/test_gpt_actions.py` — end-to-end GPT flows involving personas/intents.
- **Plan**
  - Characterize the current mapping between persona/intent presets, axis tokens, and GUI/help surfaces for a small set of presets.
  - Add tests around the persona/intent catalog API (once introduced) that assert round-tripping between config, GPT actions, help hub presets, suggestion GUIs, and lists.
  - Add integration coverage (for example, extending `tests/test_integration_suggestions.py`) that fails when catalog alignment regresses so GUI/help/doc flows stay in sync.
    - Add a persona/intent CI guardrail (lint/test) that rejects bypasses of the catalog API before landing.
    - When refactoring `_validated_persona_value`, `_canonical_persona_value`, and related helpers, ensure existing integration tests remain the primary guardrails; only add new tests where behaviour is currently untested.
  - Keep guardrail and regression suites (e.g., `_tests/test_persona_presets.py`, `_tests/test_model_suggestion_gui.py`, `_tests/test_history_axis_validate.py`) asserting that persona/intents surfaced through GUIs, history summaries, and telemetry snapshots match the catalog façade.
  - Ensure `scripts/tools/history-axis-validate.py` and related guardrail targets continue reporting persona alias/tone tables so operations can detect drift across catalog, history, and suggestion outputs.
 
  - Before resetting counters, run `python3 scripts/tools/history-axis-validate.py --summary-path artifacts/history-axis-summaries/history-validation-summary.json` (and optional `--summarize-json` variants) locally if you want to keep a snapshot. Skip CI artifact uploads unless the workflow expands beyond a solo maintainer.



### Request Gating & Streaming Lifecycle


- **Existing coverage (non-exhaustive)**
  - `tests/test_gpt_actions.py` — GPT action request flows and gating.
  - `tests/test_request_history_actions.py`, `tests/test_request_history.py` — history entries and summaries.
  - `tests/test_request_streaming.py` — streaming behaviour and basic error handling.
  - `tests/test_model_destination.py` — file destination semantics (per ADR-0039/0055).
  - `tests/test_model_help_gui.py`, `tests/test_model_help_canvas.py`, `tests/test_model_suggestion_gui.py`, `tests/test_integration_suggestions.py` — GUI-level behaviour for help/suggestion/history overlays.
- **Plan**
  - Before centralizing gating:
    - Identify representative true/false branches for “request in flight” across GPT actions and one or two canvases; add characterization tests where missing.
    - Ensure error/cancellation branches in `modelHelpers` streaming helpers and history writers are covered.
    - As `StreamingSession` and gating APIs are introduced:
      - Add small, focused tests for the new APIs (e.g., `try_start_request` drop reasons, StreamingSession event ordering) while keeping integration tests as the main behavioural guardrails.
      - Avoid duplicating GUI behaviour tests; instead, validate that GUIs respond correctly to lifecycle events.
      - Keep guardrail and telemetry suites (e.g., `_tests/test_run_guardrails_ci.py`, `_tests/test_history_axis_validate.py`, `_tests/test_history_axis_export_telemetry.py`) asserting streaming status, last-drop messages/codes, and gating reason/source tables so CLI summaries and machine-readable payloads fail when those fields regress.
      - Ensure local guardrail targets continue surfacing the same last-drop bullets as CI (`_tests/test_make_request_history_guardrails.py`) so operator workflows stay aligned with automation output.

Across all domains, we will continue to run `python3 -m pytest` from the repo root during each slice, relying on existing suites as primary regression protection.


---

## Consequences

- **Positive**
  - Clearer **Axis Snapshot & History** boundaries reduce coordination cost when axis semantics change, making Concordance scoring inputs more visible and easier to evolve.
  - A unified **Persona & Intent** catalog stabilizes presets across GPT actions, help hub, and suggestion GUIs, reducing churn and surprises when tuning personas/intents.
  - Centralized **Request Gating & Streaming Lifecycle** semantics reduce duplicated gating logic, make error/cancellation handling more predictable, and simplify reasoning about when history/log entries are written.
  - Concordance scores for the identified hotspots should decrease over time as visibility increases, scope narrows, and volatility is absorbed by focused facades and types.
  - CI guardrails that fail on lens-less history writes keep the directional requirement non-negotiable, providing an automated early warning before regressions reach production.
  - Guardrail automation archives `history-axis-validate.py --summary-path` output before applying `--reset-gating`, so local runs can capture drop telemetry prior to clearing counters.
- Guardrail runs export `history-validation-summary.telemetry.json` (top gating reasons, totals, artifact link) so the same machine-readable snapshot is available if you need to inspect trends manually.
- Guardrail telemetry now includes the last-drop message/code and the streaming last-drop message/code so you can surface actionable gating context without parsing raw logs.
- Local `make request-history-guardrails(-fast)` runs print the `Last gating drop` and `Streaming last drop` lines alongside the JSON summaries, giving you quick visibility into history vs streaming rejections without digging through logs.
- CLI guardrail commands operate in standalone Python processes; they validate repository logic but do not snapshot Talon’s live in-memory history. Capturing runtime history still requires a Talon-side command or manual export.
- **Risks**
  - Introducing new catalogs and lifecycle APIs can temporarily increase complexity and surface hidden inconsistencies.
  - Misaligned migrations (e.g., partially adopted `AxisSnapshot` or persona catalog) could create confusing states where some surfaces see new behaviour and others see old.
  - As the solo maintainer, I might forget to archive the streaming/persona telemetry summaries before resetting guardrails, losing the very signals this ADR depends on.
- **Mitigations**
  - Land changes in small, test-backed slices following the Tests-First Refactor Plan.
  - Keep new facades thin, documented, and aligned with ADR-0045/0046/0054/0055 patterns.
  - Monitor statement-level churn × complexity heatmaps and Concordance scores after each slice to confirm improvements come from structural gains, not weakened checks.
  - Enforce CI guardrails and integration coverage that fail when directional lenses or persona/intent catalog alignment regress, so violations surface before landing.
  - Keep a lightweight personal note of the guardrail commands you care about (for example, `make request-history-guardrails`, `python3 scripts/tools/history-axis-validate.py --summary-path …`, `run_guardrails_ci.sh request-history-guardrails`) and run them before resetting counters when you want fresh telemetry snapshots.

---

## Salient Tasks

1. **Axis Snapshot & History**
   - (Completed 2025-12-18) Define an `AxisSnapshot` type driven by `axisCatalog` and add adapters in `lib/requestLog.py:61` and `lib/requestHistoryActions.py:34` so history/log surfaces share the normalisation contract.
   - (Completed 2025-12-18) Update `history_axes_for`, `history_summary_lines`, and `lib/requestLog._filter_axes_payload` to consume `AxisSnapshot`, keeping Talon-side filtering via `talonSettings._filter_axis_tokens` only for live settings.
   - Ensure README/help/static prompt docs that present axes reuse the same catalog and snapshot helpers, building on ADR-0046/0054.
     - (Completed 2025-12-18) Static prompt docs (`GPT/gpt.py::_build_static_prompt_docs`) now derive axis defaults via `AxisSnapshot`, keeping doc output aligned with history/log canonicalisation.
     - (Completed 2025-12-18) README axis list generation (`scripts/tools/generate_readme_axis_lists.py`) now normalises tokens via `AxisSnapshot`, dropping hydrated artefacts while preserving catalog/list drift visibility.
      - (Completed 2025-12-18) Axis cheat sheet export (`scripts/tools/generate-axis-cheatsheet.py`) now consumes `AxisSnapshot`, so help surfaces display the canonical, lower-cased tokens used across history/log/docs.
      - (Completed 2025-12-18) `GPT/readme.md` now embeds the refreshed `make readme-axis-refresh` snapshot so the tracked README shows AxisSnapshot-normalised tokens.
      - (Completed 2025-12-18) Help Hub quick help (`lib/helpDomain.py`) now sources axis tokens via `AxisSnapshot`, aligning in-Talon guidance with the shared façade.
      - (Completed 2025-12-18) History axis validator messaging now reports that docs/help share the AxisSnapshot façade, keeping guardrail output in sync with doc surfaces.
       - (Completed 2025-12-18) Axis docs generation (`GPT/gpt.py::_build_axis_docs`) now canonicalises tokens via `AxisSnapshot`, so long-form help mirrors README/help surfaces.
       - (Completed 2025-12-18) ADR-005 quick reference now points at the AxisSnapshot façade/regeneration helpers so documentation stays aligned with the SSOT.
       - (Completed 2025-12-18) ADR-006 command quick reference now instructs maintainers to regenerate AxisSnapshot-backed helpers before editing.
       - (Completed 2025-12-18) GPT README quick reference now carries the same regeneration note so user-facing docs stay in sync with AxisSnapshot helpers.
 



    - (Completed 2025-12-17) Audit of this repo’s Talon overlays, CLI scripts, and automation confirmed no residual `require_directional=False` usage, and no external automation paths remain.
    - (Completed 2025-12-17) Added a CI/guardrail check by invoking `scripts/tools/history-axis-validate.py` from `make request-history-guardrails`, failing when new code paths attempt to append history entries without directional lenses.

2. **Persona & Intent Presets**
   - (Completed 2025-12-19) Introduced a persona/intent catalog backed by `personaConfig.persona_intent_catalog_snapshot`, with GPT persona/intent actions, help hub presets, suggestion GUIs, and list files consuming the shared façade.
   - (Completed 2025-12-19) Refactored `_validated_persona_value`, `_canonical_persona_value`, and `_build_persona_intent_docs` to rely on catalog-backed `persona_intent_maps`, keeping persona/intents aligned with axis metadata.
   - (Completed 2025-12-19) Added integration coverage (e.g., `_tests/test_persona_presets.py`, `_tests/test_integration_suggestions.py::SuggestionIntegrationTests::test_suggest_alias_only_metadata_round_trip`) that fails when persona/intent catalog alignment regresses, keeping GUIs, docs, and help flows in sync.
3. **Request Gating & Streaming Lifecycle**
    - (Completed 2025-12-21) Added `is_in_flight`/`try_start_request` helpers on `requestController`, `requestState`, and `requestLifecycle`, migrated request bus/controller/GUI gating wrappers to the shared façade, and kept telemetry routing through `requestGating`.
    - (Completed 2025-12-21) Implemented `StreamingSession` aligned with ADR-0046/0054 and moved streaming/error helpers plus history/log writers onto its events so gating summaries, snapshots, and telemetry stay in sync.
    - (Completed 2025-12-19) Completed ADR-0055 by delegating request history saves to the shared `modelDestination` file helper so prompt-only helpers remain thin adapters covered by existing history tests.
    - (Completed 2025-12-21) Added focused regression tests for gating/streaming paths (e.g., `tests/test_request_gating.py`, `tests/test_streaming_coordinator.py`, guardrail CLI helpers) that fail when the centralized lifecycle or telemetry guardrails regress.
    - (In progress 2025-12-21) GUI gating migration status:
      - `lib/modelHelpCanvas` and `lib/modelSuggestionGUI` now delegate `_request_is_in_flight` / `_reject_if_request_in_flight` to `requestGating`, with guard tests locking drop-message fallback and drop-reason clearing.
      - Remaining surfaces (pattern/prompt pattern GUIs, help hub, provider commands, history overlays) still carry bespoke wrappers; keep the shared facade migration plan open until they delegate to `requestGating` with matching guard rails.
    - For solo workflows, capture any history snapshot you care about by running `python3 scripts/tools/history-axis-validate.py --summary-path artifacts/history-axis-summaries/history-validation-summary.json` before invoking `--reset-gating`; skip CI artifact archiving unless you reintroduce shared automation.


The execution of these tasks should be coordinated with existing Concordance ADRs so that this ADR serves as a focused completion path for persona, axis snapshot, and request gating hotspots revealed by the latest churn × complexity analysis.

## Monitoring & Next Steps
- Optional guardrail: run `make request-history-guardrails` when you want fresh JSON summaries (`history-validation-summary.json`, `.streaming.json`, `.telemetry.json`) before a reset.
- Optional spot-check: `python3 scripts/tools/history-axis-validate.py --summary-path artifacts/history-axis-summaries/history-validation-summary.json --reset-gating` still enforces directional axes; use `--summarize-json` variants when you want to inspect streaming/persona tables.
- When telemetry fields expand, add or extend targeted tests so the new data stays covered without relying on manual guardrails.
