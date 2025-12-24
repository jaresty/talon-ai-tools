## 2025-12-24 – Loop 001 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (introduce shared facade + canonical tests)
- riskiest_assumption: Without a canonical orchestrator, persona/intents will continue duplicating alias logic across GPT and canvas surfaces; `python3 -m pytest _tests/test_persona_orchestrator.py` will fail to detect catalogue drift (probability medium, impact high for Concordance coordination).
- validation_targets:
  - python3 -m pytest _tests/test_persona_orchestrator.py
- evidence: docs/adr/evidence/0062/loop-0001.md
- rollback_plan: git restore --source=HEAD -- lib/personaOrchestrator.py _tests/test_persona_orchestrator.py docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md docs/adr/evidence/0062/loop-0001.md && python3 -m pytest _tests/test_persona_orchestrator.py
- delta_summary: helper:diff-snapshot=2 files added (`lib/personaOrchestrator.py`, `_tests/test_persona_orchestrator.py`) plus supporting evidence/work-log updates; establishes cached orchestrator facade fed by `persona_intent_catalog_snapshot()` and coverage for alias/display invariants.
- residual_risks:
  - Guidance surfaces still load `persona_intent_maps()` directly; mitigation: migrate GPT/help/suggestion helpers in Loop 2; monitor via the same pytest target once integrations land.
- next_work:
  - Behaviour: Migrate `GPT/gpt.py` persona helpers to `get_persona_intent_orchestrator` — python3 -m pytest _tests/test_gpt_actions.py — future-shaping: centralise canonicalisation through facade before touching canvases.

## 2025-12-24 – Loop 002 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (hydrate GPT actions + docs from canonical facade)
- riskiest_assumption: GPT actions will continue emitting stale persona/intent aliases unless they consume the orchestrator; `python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_build_persona_intent_docs_renders_snapshot_content` currently fails to surface display aliases (probability medium, impact high for Concordance visibility).
- validation_targets:
  - python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_build_persona_intent_docs_renders_snapshot_content
- evidence: docs/adr/evidence/0062/loop-0002.md
- rollback_plan: git restore --source=HEAD -- lib/personaOrchestrator.py GPT/gpt.py _tests/test_persona_orchestrator.py && python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_build_persona_intent_docs_renders_snapshot_content
- delta_summary: helper:diff-snapshot=3 files changed, 164 insertions(+), 121 deletions(-); GPT actions now call `get_persona_intent_orchestrator()` for canonical tokens, docs use shared display aliases, and orchestrator exposes axis alias map.
- residual_risks:
  - Guidance canvases still duplicate `_reject_if_request_in_flight` and stance summaries; mitigation: extract shared surface coordinator (Loop 3) and validate via `_tests/test_model_suggestion_gui.py`; monitor GPT UI churn hotspots for regressions.
- next_work:
  - Behaviour: Centralise canvas/help gating via guidance coordinator — python3 -m pytest _tests/test_model_suggestion_gui.py — future-shaping: move shared event handlers into new surface facade and align with orchestrator outputs.

## 2025-12-24 – Loop 003 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (unify request gating across canvases)
- riskiest_assumption: Without a shared guard, suggestion/help canvases continue duplicating `_reject_if_request_in_flight`, risking inconsistent Concordance messaging; `python3 -m pytest _tests/test_surface_guidance.py` fails due to missing facade (probability medium, impact high on visibility/scope).
- validation_targets:
  - python3 -m pytest _tests/test_surface_guidance.py _tests/test_model_suggestion_gui.py _tests/test_model_help_canvas_guard.py
- evidence: docs/adr/evidence/0062/loop-0003.md
- rollback_plan: git restore --source=HEAD -- lib/modelSuggestionGUI.py lib/modelHelpCanvas.py && git clean -f _tests/test_surface_guidance.py lib/surfaceGuidance.py && python3 -m pytest _tests/test_surface_guidance.py
- delta_summary: helper:diff-snapshot=4 files changed, 64 insertions(+), 139 deletions(-); introduces `lib/surfaceGuidance.py`, delegates suggestion/help canvases to shared guard, and realigns guard tests to the new facade.
- residual_risks:
  - Request history drawers still implement bespoke gating. Mitigation: fold them into the same facade in a follow-up loop and validate via `_tests/test_request_history_drawer_gating.py`.
- next_work:
  - Behaviour: Extend surface guidance to request history drawers — python3 -m pytest _tests/test_request_history_drawer_gating.py — future-shaping: collapse remaining `_reject_if_request_in_flight` helpers into the new facade.

## 2025-12-24 – Loop 004 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (request history drawer gating)
- riskiest_assumption: History drawer continues to duplicate `_reject_if_request_in_flight`, leading to inconsistent Concordance messaging; `python3 -m pytest _tests/test_request_history_drawer_gating.py` fails under the updated guard expectations (probability medium, impact medium-high on history visibility).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_drawer_gating.py
- evidence: docs/adr/evidence/0062/loop-0004.md
- rollback_plan: git restore --source=HEAD -- lib/requestHistoryDrawer.py && python3 -m pytest _tests/test_request_history_drawer_gating.py
- delta_summary: helper:diff-snapshot=2 files changed, 67 insertions(+), 74 deletions(-); request history drawer now delegates gating to `guard_surface_request`, and tests assert the shared facade contract.
- residual_risks:
  - Request history actions/log modules still duplicate gating logic. Mitigation: migrate them to the shared facade in the next loop and validate via `_tests/test_request_history_actions.py`.
- next_work:
  - Behaviour: Adopt surface guidance in `requestHistoryActions` and related log helpers — python3 -m pytest _tests/test_request_history_actions.py — future-shaping: remove remaining bespoke gating before introducing the history lifecycle orchestrator.

## 2025-12-24 – Loop 005 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (request history actions)
- riskiest_assumption: History actions still duplicate `_reject_if_request_in_flight`, leading to inconsistent saves; `python3 -m pytest _tests/test_request_history_actions.py` fails when tests expect the shared guard (probability medium, impact high on history volatility).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_actions.py
- evidence: docs/adr/evidence/0062/loop-0005.md
- rollback_plan: git restore --source=HEAD -- lib/requestHistoryActions.py && python3 -m pytest _tests/test_request_history_actions.py
- delta_summary: helper:diff-snapshot=2 files changed, 33 insertions(+), 90 deletions(-); history actions now delegate gating to `guard_surface_request`, and save workflows respect shared guard semantics.
- residual_risks:
  - Downstream history log/save helpers may still assume local drop-reason messaging. Mitigation: audit `_notify_with_drop_reason` flows alongside the planned history lifecycle orchestrator.
- next_work:
  - Behaviour: Prepare history lifecycle façade — gather coverage around request log snapshots via python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_writes_axes_headers — future-shaping: consolidate axis snapshot assembly before introducing the lifecycle orchestrator.

## 2025-12-24 – Loop 006 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (introduce axis snapshot façade)
- riskiest_assumption: History modules still filter axes ad hoc; `_tests/test_history_lifecycle.py` fails without a shared facade (probability medium, impact high on Concordance visibility/scope).
- validation_targets:
  - python3 -m pytest _tests/test_history_lifecycle.py _tests/test_request_history_actions.py _tests/test_request_history_drawer_gating.py
- evidence: docs/adr/evidence/0062/loop-0006.md
- rollback_plan: git stash push -- lib/historyLifecycle.py _tests/test_history_lifecycle.py lib/requestHistoryActions.py && python3 -m pytest _tests/test_history_lifecycle.py && git stash pop
- delta_summary: helper:diff-snapshot=3 files changed, 107 insertions(+), 23 deletions(-); adds `lib/historyLifecycle.py`, lifecycle characterization tests, and re-routes history axis helpers through the facade.
- residual_risks:
  - History drawer/actions still duplicate drop-reason notifications and history saves lack lifecycle orchestration. Mitigation: Loop 007 will migrate history drawers/actions to the lifecycle façade.
- next_work:
  - Behaviour: Migrate history drawer/actions to `historyLifecycle` façade — python3 -m pytest _tests/test_request_history_drawer_gating.py _tests/test_request_history_actions.py — future-shaping: expose lifecycle entry point before unifying request log saves.
