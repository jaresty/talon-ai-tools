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

## 2025-12-25 – Loop 007 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate actions/drawer to façade)
- riskiest_assumption: History actions/query still rely on local axis filters; `_tests/test_history_query.py` and `_tests/test_request_history_actions.py` fail when expecting lifecycle delegation (probability medium, impact medium-high on Concordance scope/visibility).
- validation_targets:
  - python3 -m pytest _tests/test_history_lifecycle.py _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_history_drawer_gating.py
- evidence: docs/adr/evidence/0062/loop-0007.md
- rollback_plan: git stash push -- lib/historyQuery.py lib/requestHistoryActions.py && python3 -m pytest _tests/test_history_query.py _tests/test_request_history_actions.py && git stash pop
- delta_summary: helper:diff-snapshot=4 files changed, 82 insertions(+), 24 deletions(-); history actions/query now delegate to `historyLifecycle`, with dedicated lifecycle tests and updated guardrail coverage.
- residual_risks:
  - History log save helpers still handle persona/drop-reason flows inline; Loop 008 will instrument and document lifecycle responsibilities before refactoring saves.
- next_work:
  - Behaviour: instrument history log + docs — python3 -m pytest _tests/test_history_lifecycle.py _tests/test_history_query.py _tests/test_request_history_actions.py — future-shaping: document lifecycle responsibilities and wire telemetry for lifecycle stats before orchestrator integration.

## 2025-12-25 – Loop 008 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (instrument telemetry + docs)
- riskiest_assumption: Lifecycle telemetry remains fragmented unless the façade exports shared gating stats; `python3 -m pytest _tests/test_history_lifecycle.py _tests/test_history_query.py _tests/test_request_history_actions.py` currently fails to validate the shared instrumentation (probability medium, impact high on Concordance visibility).
- validation_targets:
  - python3 -m pytest _tests/test_history_lifecycle.py _tests/test_history_query.py _tests/test_request_history_actions.py
- evidence: docs/adr/evidence/0062/loop-0008.md
- rollback_plan: git stash push -- lib/historyLifecycle.py lib/historyQuery.py lib/requestLog.py && python3 -m pytest _tests/test_history_lifecycle.py _tests/test_history_query.py _tests/test_request_history_actions.py && git stash pop
- delta_summary: helper:diff-snapshot=5 files changed, 73 insertions(+), 7 deletions(-); lifecycle façade exports gating telemetry wrappers, historyQuery reuses them, and ADR text highlights the shared instrumentation.
- residual_risks:
  - Drop-reason helpers still live in requestLog/requestHistoryActions; mitigation: migrate them into `historyLifecycle` next and validate via `_tests/test_request_history_actions.py`.
- next_work:
  - Behaviour: consolidate drop-reason helpers through lifecycle façade — python3 -m pytest _tests/test_request_history_actions.py — future-shaping: align history saves and notifications with the shared lifecycle entrypoints.

## 2025-12-25 – Loop 009 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (centralise drop reasons)
- riskiest_assumption: Request history surfaces would keep importing `requestLog` drop helpers unless the lifecycle façade exposed them; `python3 -m pytest _tests/test_history_lifecycle.py _tests/test_history_query.py _tests/test_request_history_actions.py` fails to observe the shared contract (probability medium, impact high on Concordance scope/visibility).
- validation_targets:
  - python3 -m pytest _tests/test_history_lifecycle.py _tests/test_history_query.py _tests/test_request_history_actions.py
- evidence: docs/adr/evidence/0062/loop-0009.md
- rollback_plan: git stash push -- lib/historyLifecycle.py lib/requestHistoryActions.py && python3 -m pytest _tests/test_history_lifecycle.py _tests/test_history_query.py _tests/test_request_history_actions.py && git stash pop
- delta_summary: helper:diff-snapshot=3 files changed, 53 insertions(+), 3 deletions(-); lifecycle façade exports drop-reason setters/consumers, history actions import them, and lifecycle tests cover the contract.
- residual_risks:
  - Surface guidance and confirmation/pattern GUIs still import `requestLog` drop helpers; mitigation: reroute those surfaces through `historyLifecycle` in the next loop and validate via `_tests/test_surface_guidance.py` and related GUI suites.
- next_work:
  - Behaviour: migrate remaining UI surfaces to lifecycle drop helpers — python3 -m pytest _tests/test_surface_guidance.py _tests/test_model_help_canvas_guard.py — future-shaping: ensure all canvases use shared drop-reason orchestration before refactoring history saves.

## 2025-12-25 – Loop 010 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (reuse drop helpers in surface guidance + GUIs)
- riskiest_assumption: UI surfaces would keep setting drop reasons via `requestLog`; `_tests/test_surface_guidance.py _tests/test_model_help_canvas_guard.py` fails until the façade owns the helpers (probability medium, impact medium-high on Concordance visibility).
- validation_targets:
  - python3 -m pytest _tests/test_surface_guidance.py _tests/test_model_help_canvas_guard.py
- evidence: docs/adr/evidence/0062/loop-0010.md
- rollback_plan: git stash push -- lib/surfaceGuidance.py lib/modelConfirmationGUI.py lib/modelPatternGUI.py lib/modelPromptPatternGUI.py lib/helpHub.py lib/providerCommands.py && python3 -m pytest _tests/test_surface_guidance.py _tests/test_model_help_canvas_guard.py && git stash pop
- delta_summary: helper:diff-snapshot=7 files changed, 15 insertions(+), 6 deletions(-); surface guidance and related GUIs now import lifecycle drop helpers, and tests assert lifecycle equivalence.
- residual_risks:
  - History save/export helpers still call `set_drop_reason` directly; mitigation: migrate save/export flows to lifecycle façade next and validate via `_tests/test_request_history_actions.py`.
- next_work:
  - Behaviour: align history save/export drop handling with lifecycle — python3 -m pytest _tests/test_request_history_actions.py — future-shaping: ensure persistence paths reuse the shared drop-reason orchestration before refactoring history saves.

## 2025-12-25 – Loop 011 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (history drawer + response canvas drop helpers)
- riskiest_assumption: Drawer/response canvases would keep calling `requestLog` helpers; `python3 -m pytest _tests/test_request_history_drawer_gating.py _tests/test_model_response_canvas.py` fails until the lifecycle façade owns those imports (probability medium, impact high on Concordance visibility).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_drawer_gating.py _tests/test_model_response_canvas.py
- evidence: docs/adr/evidence/0062/loop-0011.md
- rollback_plan: git stash push -- lib/requestHistoryDrawer.py lib/modelResponseCanvas.py && python3 -m pytest _tests/test_request_history_drawer_gating.py _tests/test_model_response_canvas.py && git stash pop
- delta_summary: helper:diff-snapshot=4 files changed, 27 insertions(+), 3 deletions(-); request history drawer/response canvas now import lifecycle drop helpers, and tests assert façade equivalence.
- residual_risks:
  - History save/export flows still set drop reasons directly; next loop aligns those pathways with the façade.
- next_work:
  - Behaviour: migrate history save/export drop handling — python3 -m pytest _tests/test_request_history_actions.py — future-shaping: ensure persistence and exports delegate to lifecycle helpers before refactoring saves.
