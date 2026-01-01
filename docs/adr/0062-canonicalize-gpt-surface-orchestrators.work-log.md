## 2025-12-24 – Loop 001 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (canonical façade) → Guidance Surface/Docs metadata alignment
- riskiest_assumption: Without continuing to codify metadata exports, downstream docs/tests diverge from Help Hub snapshots; recent loops proved we need shared helpers and doc guardrails.
- validation_targets:
  - python3 -m pytest _tests/test_help_domain.py::HelpDomainTests::test_help_metadata_summary_lines_respects_headers
  - python3 -m pytest _tests/test_help_hub.py::test_copy_adr_links_includes_metadata
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
  - python3 -m pytest _tests/test_readme_guardrails_docs.py::ReadmeGuardrailsDocsTests::test_readme_axis_cheatsheet_includes_metadata_summary
- evidence:
  - docs/adr/evidence/0062/loop-0034.md
  - docs/adr/evidence/0062/loop-0035.md
  - docs/adr/evidence/0062/loop-0036.md
- rollback_plan: git restore --source=HEAD -- lib/helpDomain.py lib/helpHub.py scripts/tools/generate-axis-cheatsheet.py docs/readme-axis-cheatsheet.md _tests/test_help_domain.py _tests/test_help_hub.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_guardrails_docs.py && rerun the validation targets
- delta_summary: Metadata helpers now centralize schema/provenance headers, Help Hub delegates to them, and documentation guardrails ensure README cheat sheet snapshots stay in sync.
- residual_risks:
  - Monitor future doc generators for metadata regressions; regenerate cheat sheet when persona/intent catalog changes.
- next_work:
  - Behaviour: keep axis/persona docs aligned with snapshot helper; audit remaining guidance surfaces when orchestrator schema evolves.

## 2025-12-26 – Loop 088 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Canvas intent presets)
- riskiest_assumption: Model Help canvas would keep hydrating intent presets via personaConfig maps instead of the persona orchestrator, leaving quick help out of sync with Concordance metadata (probability medium, impact medium-high on guidance parity).
- validation_targets:
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_presets_use_persona_orchestrator
- evidence:
  - docs/adr/evidence/0062/loop-0088.md
- rollback_plan: git stash push -- lib/modelHelpCanvas.py && python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_presets_use_persona_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 83 insertions(+), 7 deletions(-); Help canvas intent/persona helpers now delegate to the persona orchestrator before falling back to legacy maps, keeping quick help aligned with Concordance snapshots.
- residual_risks:
  - `_intent_spoken_buckets` and `_normalize_intent` still depend on personaConfig; plan future loops to route them through the orchestrator to complete the migration.
- next_work:
  - Behaviour: migrate Help canvas intent normalisation helpers to orchestrator exports — python3 -m pytest _tests/test_model_help_canvas.py — future-shaping: retire remaining personaConfig dependencies from Help canvas surfaces.


## 2025-12-25 – Loop 041 (kind: planning)
- helper_version: helper:v20251223.1
- focus: Identify additional tests needed before persona catalog façade rollout.
- riskiest_assumption: Persona/catalog refactor may lack coverage for snapshot consumers; review `_tests/test_help_hub.py`, `_tests/test_help_domain.py`, `_tests/test_generate_axis_cheatsheet.py`, and history suites to target gaps.
- summary: Documented candidate characterization tests (persona orchestrator, guidance surfaces, history lifecycle) to author prior to behavioural refactors.
- next_work:
  - Behaviour: capture open follow-up actions and risks in ADR notes — Loop 042.

## 2025-12-25 – Loop 042 (kind: planning)
- helper_version: helper:v20251223.1
- focus: Summarize follow-up actions post metadata guardrails.
- riskiest_assumption: Without explicit reminders, persona/guidance/history refactors may stall.
- summary: Noted outstanding tasks — persona catalog façade adoption, guidance coordinator extraction, history lifecycle façade implementation, plus targeted characterization tests.
- next_work:
  - Behaviour: proceed with persona catalog façade implementation in subsequent loops.

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

## 2025-12-25 – Loop 012 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (history save/export drop resets)
- riskiest_assumption: History save actions still cleared drop reasons directly; `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_actions_clear_drop_reason_helper` fails until the lifecycle façade provides the shared helper (probability medium, impact medium-high on Concordance visibility).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_actions.py
- evidence: docs/adr/evidence/0062/loop-0012.md
- rollback_plan: git stash push -- lib/historyLifecycle.py lib/requestHistoryActions.py && python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_actions_clear_drop_reason_helper && git stash pop
- delta_summary: helper:diff-snapshot=3 files changed, 28 insertions(+), 6 deletions(-); lifecycle now exposes `clear_drop_reason`, history actions re-export/use it, and tests assert façade alignment for save/export flows.
- residual_risks:
  - History save/export callers still build drop-reason messages inline; consider lifecycle helpers to centralise messaging.
- next_work:
  - Behaviour: audit remaining drop-reason consumers (requestGating) — python3 -m pytest _tests/test_request_gating.py — future-shaping: ensure request gating drop setters into the lifecycle façade where feasible.

## 2025-12-25 – Loop 015 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (Help domain axis snapshots)
- riskiest_assumption: HelpDomain continued importing `axis_snapshot_from_axes` from `requestLog`; `python3 -m pytest _tests/test_help_hub.py` fails once the guard asserts lifecycle usage (probability medium, impact medium on Concordance visibility).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py
- evidence: docs/adr/evidence/0062/loop-0015.md
- rollback_plan: git stash push -- lib/helpDomain.py && python3 -m pytest _tests/test_help_hub.py::test_help_domain_uses_lifecycle_axis_snapshot && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 10 insertions(+), 1 deletion(-); helpDomain reuses lifecycle axis snapshots and guardrails enforce façade alignment.
- residual_risks:
  - Other modules may still import axis snapshot helpers directly; audit remaining direct imports (`historyQuery`, etc.) in later loops.
- next_work:
  - Behaviour: migrate streaming coordinator drop messaging — python3 -m pytest _tests/test_streaming_coordinator.py — future-shaping: ensure telemetry consumers rely on lifecycle drop helpers.

## 2025-12-25 – Loop 018 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (HistoryQuery axis snapshots)
- riskiest_assumption: HistoryQuery continued to call `requestHistoryActions.axis_snapshot_from_axes`; `_tests/test_history_query.py` fails once the guard checks for lifecycle reuse (probability medium, impact medium on Concordance visibility/telemetry).
- validation_targets:
  - python3 - m pytest _tests/test_history_query.py
- evidence: docs/adr/evidence/0062/loop-0018.md
- rollback_plan: git stash push -- lib/historyQuery.py && python3 -m pytest _tests/test_history_query.py::HistoryQueryTests::test_history_axes_for_reuses_lifecycle_helper && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 7 insertions(+), 5 deletions(-); HistoryQuery now delegates axis snapshots to `historyLifecycle` and guardrails confirm the façade contract.
- residual_risks:
  - History drawers still reach into `requestHistoryActions` for persona fragments; future loops should migrate those helpers as the persona orchestrator consolidates metadata.
- next_work:
  - Behaviour: extract persona intent catalog façade — python3 - m pytest _tests/test_model_suggestion_gui.py _tests/test_model_response_canvas.py — future-shaping: centralise persona lookup logic for canvases and GPT docs.

## 2025-12-25 – Loop 019 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (persona orchestrator alias)
- riskiest_assumption: Suggestion coordinator still reached into `personaConfig` directly; new guard `_tests/test_suggestion_coordinator.py::test_suggestion_coordinator_uses_persona_orchestrator` fails until the facade alias exists (probability medium, impact medium on Concordance surface guidance).
- validation_targets:
  - python3 -m pytest _tests/test_suggestion_coordinator.py
- evidence: docs/adr/evidence/0062/loop-0019.md
- rollback_plan: git stash push -- lib/suggestionCoordinator.py && python3 -m pytest _tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_suggestion_coordinator_uses_persona_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 18 insertions(+); suggestion coordinator now aliases the persona orchestrator, and guardrails confirm lifecycle alignment.
- residual_risks:
  - Canonicalization still lives in suggestion coordinator; follow-up should migrate the normalization logic to the orchestrator to remove duplication.
- next_work:
  - Behaviour: migrate suggestion canonicalization to orchestrator helpers — python3 -m pytest _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py — future-shaping: ensure persona axis normalization is centralized.

## 2025-12-25 – Loop 020 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (orchestrator canonicalisation)
- riskiest_assumption: Suggestion coordinator continued to normalise via `persona_intent_maps`; `_tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_record_suggestions_uses_persona_orchestrator` fails to prove orchestrator usage (probability medium-high, impact high on Concordance guidance reuse).
- validation_targets:
  - python3 -m pytest _tests/test_suggestion_coordinator.py _tests/test_model_suggestion_gui.py
- evidence: docs/adr/evidence/0062/loop-0020.md
- rollback_plan: git stash push -- lib/suggestionCoordinator.py && python3 -m pytest _tests/test_suggestion_coordinator.py::SuggestionCoordinatorTests::test_record_suggestions_uses_persona_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 371 insertions(+), 169 deletions(-); suggestion coordinator now canonicalises persona/intent fields via the shared orchestrator, and guardrails cover the contract.
- residual_risks:
  - Orchestrator still computed locally per call; a future loop can memoize the canonical snapshot for reuse across surfaces.
- next_work:
  - Behaviour: expose orchestrator helpers to model canvases — python3 - m pytest _tests/test_model_response_canvas.py _tests/test_model_pattern_gui.py — future-shaping: ensure canvases leverage orchestrator metadata.

## 2025-12-25 – Loop 021 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (canvas persona recaps)
- riskiest_assumption: Response canvas still derived persona recaps from `persona_intent_maps`; `_tests/test_model_response_canvas.py::ModelResponseCanvasTests::test_response_canvas_uses_persona_orchestrator` demonstrates the gap (probability medium, impact medium-high on Concordance surface parity).
- validation_targets:
  - python3 -m pytest _tests/test_model_response_canvas.py _tests/test_model_pattern_gui.py
- evidence: docs/adr/evidence/0062/loop-0021.md
- rollback_plan: git stash push -- lib/modelResponseCanvas.py && python3 -m pytest _tests/test_model_response_canvas.py::ModelResponseCanvasTests::test_response_canvas_uses_persona_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 336 insertions(+), 67 deletions(-); response canvas recaps now reuse the persona orchestrator and doc tests cover the contract.
- residual_risks:
  - Model help/pattern canvases still hydrate persona labels independently; consider sharing the new orchestrator helpers across canvases next.
- next_work:
  - Behaviour: share orchestrator persona summaries with help hub — python3 -m pytest _tests/test_model_help_canvas.py _tests/test_help_hub.py — future-shaping: align help surfaces with the canonical persona orchestrator.

## 2025-12-25 – Loop 022 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (help hub presets)
- riskiest_assumption: Help Hub still hydrated persona/intent presets via `persona_intent_maps`; `_tests/test_help_hub.py::test_help_hub_uses_persona_orchestrator_for_presets` patches the orchestrator and fails without an alias (probability medium, impact medium on Concordance onboarding/search accuracy).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py _tests/test_model_response_canvas.py
- evidence: docs/adr/evidence/0062/loop-0022.md
- rollback_plan: git stash push -- lib/helpHub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_uses_persona_orchestrator_for_presets && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 174 insertions(+), 34 deletions(-); help hub now consumes the persona orchestrator for cheat sheet/search data and guardrails confirm reuse.
- residual_risks:
  - Help domain still uses personaConfig helpers directly; migrate those surfaces in a follow-up loop.
- next_work:
  - Behaviour: align help domain canonicalisation with the orchestrator — python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py — future-shaping: ensure documentation/overlay flows rely on shared persona metadata.

## 2025-12-25 – Loop 017 (kind: implementation)



- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (GPT axis snapshot usage)
- riskiest_assumption: `GPT.gpt` still reached into `requestLog` for axis snapshots; `_tests/test_gpt_readme_axis_lists.py::test_gpt_module_uses_lifecycle_axis_snapshot` fails until the module re-exports the lifecycle helper (probability medium, impact medium on Concordance docs and guidance).
- validation_targets:
  - python3 -m pytest _tests/test_gpt_readme_axis_lists.py
- evidence: docs/adr/evidence/0062/loop-0017.md
- rollback_plan: git stash push -- GPT/gpt.py && python3 -m pytest _tests/test_gpt_readme_axis_lists.py::GPTReadmeAxisListsTests::test_gpt_module_uses_lifecycle_axis_snapshot && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 55 insertions(+), 10 deletions(-); GPT module imports lifecycle axis snapshots and guardrails enforce the shared façade.
- residual_risks:
  - Other persona/prompt helpers in `GPT/gpt.py` still depend on inline catalog logic; future loops should extract them into the prompt persona orchestrator.
- next_work:
  - Behaviour: migrate GPT persona/intent docs to shared catalog — python3 -m pytest _tests/test_model_suggestion_gui.py _tests/test_model_response_canvas.py — future-shaping: centralise persona intent metadata for canvases and docs.

## 2025-12-25 – Loop 013 (kind: implementation)

- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (request gating drop helpers)
- riskiest_assumption: Request gating continued importing drop helpers from `requestLog`; `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_request_gating_uses_lifecycle_drop_helpers` fails to assert façade alignment (probability medium, impact medium-high on Concordance visibility).
- validation_targets:
  - python3 -m pytest _tests/test_request_gating.py
- evidence: docs/adr/evidence/0062/loop-0013.md
- rollback_plan: git stash push -- lib/requestGating.py && python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_request_gating_uses_lifecycle_drop_helpers && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 9 insertions(+), 1 deletion(-); requestGating now imports lifecycle drop helper, and tests enforce the shared façade.
- residual_risks:
  - requestGating still calls `drop_reason_message` directly; planned lifecycle messaging helper will consolidate message formatting.
- next_work:
  - Behaviour: consolidate drop reason message formatting — python3 -m pytest _tests/test_request_gating.py _tests/test_request_history_actions.py — future-shaping: expose lifecycle helper for drop reason messages so modules no longer depend on `requestLog` formatting.

## 2025-12-25 – Loop 014 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (drop reason message façade)
- riskiest_assumption: Modules still format drop messages via `requestLog`; `python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_request_gating_uses_lifecycle_drop_helpers` fails after extending the guardrail to message helpers (probability medium, impact medium-high on Concordance visibility).
- validation_targets:
  - python3 -m pytest _tests/test_request_gating.py
- evidence: docs/adr/evidence/0062/loop-0014.md
- rollback_plan: git stash push -- lib/historyLifecycle.py lib/requestGating.py lib/dropReasonUtils.py && python3 -m pytest _tests/test_request_gating.py::RequestGatingTests::test_request_gating_uses_lifecycle_drop_helpers && git stash pop
- delta_summary: helper:diff-snapshot=4 files changed, 16 insertions(+), 3 deletions(-); lifecycle now exposes `drop_reason_message`, requestGating and dropReasonUtils delegate to it, and tests enforce the shared façade.
- residual_risks:
  - Future work may expose lifecycle helpers for additional drop metadata (e.g., source summaries) to simplify streaming coordinator integrations.
- next_work:
  - Behaviour: audit remaining direct `requestLog` imports for drop messaging — python3 -m pytest _tests/test_streaming_coordinator.py — future-shaping: ensure streaming coordinator also consumes lifecycle helpers before refactoring telemetry outputs.

## 2025-12-25 – Loop 023 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (help domain persona/intent orchestration)
- riskiest_assumption: Help domain would keep hydrating persona/intent entries from `persona_intent_maps`, so `_tests/test_help_domain.py::HelpDomainTests::test_help_index_uses_persona_orchestrator` fails to prove orchestrator reuse (probability medium, impact medium-high on Concordance visibility/search parity).
- validation_targets:
  - python3 -m pytest _tests/test_help_domain.py
- evidence: docs/adr/evidence/0062/loop-0023.md
- rollback_plan: git restore --source=HEAD -- lib/helpDomain.py && python3 -m pytest _tests/test_help_domain.py::HelpDomainTests::test_help_index_uses_persona_orchestrator
- delta_summary: helper:diff-snapshot=2 files changed, 299 insertions(+), 65 deletions(-); `help_index` now pulls persona/intent presets through the orchestrator with map fallbacks, normalises axis tokens, and updates guardrails covering voice hints.
- residual_risks:
  - Help domain still derives spoken casing from catalog displays; loop 24 will tighten shared alias casing across help hub/search results, monitoring via `_tests/test_help_domain.py`.
- next_work:
  - Behaviour: extend fallback alias casing across help hub and docs — python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py — future-shaping: centralise spoken alias formatting alongside the orchestrator so all surfaces share the same casing rules.

## 2025-12-25 – Loop 024 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (help hub/help domain metadata alias casing)
- riskiest_assumption: Help Hub and help index would keep inferring persona/intent aliases without shared metadata, so `python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py` keeps failing with missing metadata (probability medium, impact medium-high on Concordance visibility/search parity).
- validation_targets:
  - python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py
- evidence: docs/adr/evidence/0062/loop-0024.md
- rollback_plan: git restore --source=HEAD -- lib/helpDomain.py lib/helpHub.py _tests/test_help_domain.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py
- delta_summary: helper:diff-snapshot=4 files changed, 207 insertions(+), 13 deletions(-); help index now emits canonical persona/intent metadata, labels/voice hints keep orchestrator casing, and Help Hub propagates metadata through its search index.
- residual_risks:
  - Help Hub cheat sheet/clipboard flows still build alias strings manually; plan to reuse the new metadata snapshot for copy/export surfaces and guard via `_tests/test_help_hub.py`.
- next_work:
  - Behaviour: reuse persona/intent metadata for cheat sheet copy/export — python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py _tests/test_help_hub_guardrails.py — future-shaping: ensure documentation/export paths consume the canonical metadata so Concordance guardrails stay aligned.

## 2025-12-25 – Loop 025 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (reuse persona/intent metadata for Help Hub cheat sheet copy/export)
- riskiest_assumption: Without redirecting Help Hub cheat sheet/export flows to the metadata snapshot, patched orchestrator casing would keep drifting; `python3 -m pytest _tests/test_help_hub.py` failed because the cheat sheet still emitted the legacy strings (probability medium, impact medium-high on Concordance visibility/export parity).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py _tests/test_help_hub_guardrails.py
- evidence: docs/adr/evidence/0062/loop-0025.md
- rollback_plan: git restore --source=HEAD -- lib/helpDomain.py lib/helpHub.py _tests/test_help_domain.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py _tests/test_help_hub_guardrails.py
- delta_summary: helper:diff-snapshot=4 files changed, 422 insertions(+), 20 deletions(-); introduces the metadata snapshot helper in `helpDomain`, refactors `helpHub` cheat sheet copy/export to consume it, and extends help hub/domain guardrails to assert canonical persona/intent metadata.
- residual_risks:
  - Help Hub ADR/clipboard exports still assemble metadata ad hoc; mitigation: migrate the remaining exports to `help_metadata_snapshot`; monitor via `_tests/test_help_hub.py` copy/export guardrails.
- next_work:
  - Behaviour: migrate Help Hub ADR link/clipboard exports to metadata snapshot — python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py — future-shaping: keep documentation/export paths aligned with canonical persona/intent metadata.

## 2025-12-25 – Loop 026 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (reuse persona/intent metadata for Help Hub ADR exports)
- riskiest_assumption: Help Hub ADR clipboard exports would continue omitting canonical persona/intent summaries unless we piped in the shared metadata snapshot; `python3 -m pytest _tests/test_help_hub.py::test_copy_adr_links_includes_metadata -q` remained red under the previous implementation (probability medium, impact medium on Concordance documentation parity).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py _tests/test_help_hub_guard.py
- evidence: docs/adr/evidence/0062/loop-0026.md
- rollback_plan: git restore --source=HEAD -- lib/helpHub.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py _tests/test_help_hub_guard.py
- delta_summary: helper:diff-snapshot=2 files changed, 91 insertions(+); adds `_metadata_snapshot_summary_lines()` so `_adr_links_text()` (and clipboard copy) reuse canonical persona/intent metadata, and extends Help Hub guardrails to cover the richer export content.
- residual_risks:
  - Metadata summary remains text-only; follow-up loop may expose structured JSON exports for automation consumers.
- next_work:
  - Behaviour: expose structured metadata export for automation (JSON) — python3 -m pytest _tests/test_help_hub.py — future-shaping: keep downstream tooling aligned with canonical metadata formats.

## 2025-12-25 – Loop 027 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (structured JSON metadata export)
- riskiest_assumption: Automation consumers would continue scraping text-only metadata summaries without a structured export; `python3 -m pytest _tests/test_help_hub.py::test_copy_metadata_snapshot_json -q` failed against the previous implementation (probability medium, impact medium on Concordance automation coverage).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py _tests/test_help_hub_guard.py
- evidence: docs/adr/evidence/0062/loop-0027.md
- rollback_plan: git restore --source=HEAD -- lib/helpHub.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py _tests/test_help_hub_guard.py
- delta_summary: helper:diff-snapshot=2 files changed, 126 insertions(+), 22 deletions(-); factors metadata extraction into `_metadata_snapshot_records()`, adds JSON export helpers plus a Help Hub button/action, and extends guardrails with JSON-focused tests.
- residual_risks:
  - JSON payload currently lacks schema versioning or provenance metadata; schedule a follow-up loop to embed schema fields for automation clients.
- next_work:
  - Behaviour: add schema version + provenance fields to metadata payload — python3 -m pytest _tests/test_help_hub.py — future-shaping: keep automation clients resilient to future changes.

## 2025-12-25 – Loop 028 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (metadata schema provenance)
- riskiest_assumption: Without explicit schema + provenance fields, automation clients cannot observe metadata evolution; `python3 -m pytest _tests/test_help_hub.py::test_copy_metadata_snapshot_json` remains red when the JSON payload omits version identifiers (probability medium, impact medium-high on Concordance automation resilience).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_copy_metadata_snapshot_json
- evidence: docs/adr/evidence/0062/loop-0028.md
- rollback_plan: git restore --source=HEAD -- lib/helpHub.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_copy_metadata_snapshot_json
- delta_summary: helper:diff-snapshot=2 files changed, 26 insertions(+), 1 deletion(-); `_metadata_snapshot_json()` now embeds schema version + provenance metadata and guardrails assert the canonical payload structure.
- residual_risks:
  - Text-based metadata exports still omit schema/provenance cues; mitigation: extend summary/ADR copy helpers in the next loop and monitor via the same pytest target.
- next_work:
  - Behaviour: propagate schema/provenance metadata into Help Hub summary copy — python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py — future-shaping: keep textual exports aligned with the canonical JSON schema for automation consumers.

## 2025-12-25 – Loop 029 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (metadata schema provenance in summaries)
- riskiest_assumption: Help Hub ADR summaries still omit schema + provenance headers, so automation clients scraping text cannot detect schema evolution; `python3 -m pytest _tests/test_help_hub.py::test_copy_adr_links_includes_metadata` stays red when headers are missing (probability medium, impact medium-high on Concordance automation visibility).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_copy_adr_links_includes_metadata
- evidence: docs/adr/evidence/0062/loop-0029.md
- rollback_plan: git restore --source=HEAD -- lib/helpHub.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_copy_adr_links_includes_metadata
- delta_summary: helper:diff-snapshot=2 files changed, 57 insertions(+), 13 deletions(-); `_metadata_snapshot_summary_lines()` now emits schema version, timestamp, and provenance headers while JSON export reuses the shared payload helper.
- residual_risks:
  - Metadata consumers outside Help Hub still lack the headers; mitigation: extend help domain exports in the next loop and observe via `_tests/test_help_hub.py` and `_tests/test_help_domain.py` guardrails.
- next_work:
  - Behaviour: expose schema/provenance headers to help domain exports — python3 -m pytest _tests/test_help_hub.py _tests/test_help_domain.py — future-shaping: keep downstream documentation aligned with canonical metadata cues.

## 2025-12-25 – Loop 030 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (help domain metadata headers)
- riskiest_assumption: HelpDomain exports still lacked schema/provenance headers, leaving documentation unable to track metadata evolution; `python3 -m pytest _tests/test_help_domain.py::HelpDomainTests::test_help_metadata_snapshot_aggregates_index_metadata` stays red when the snapshot omits these fields (probability medium, impact medium on Concordance documentation parity).
- validation_targets:
  - python3 -m pytest _tests/test_help_domain.py::HelpDomainTests::test_help_metadata_snapshot_aggregates_index_metadata
- evidence: docs/adr/evidence/0062/loop-0030.md
- rollback_plan: git restore --source=HEAD -- lib/helpDomain.py _tests/test_help_domain.py && python3 -m pytest _tests/test_help_domain.py::HelpDomainTests::test_help_metadata_snapshot_aggregates_index_metadata
- delta_summary: helper:diff-snapshot=2 files changed, 69 insertions(+), 1 deletion(-); `help_metadata_snapshot` now emits schema version, timestamp, and provenance headers, and guardrails assert the augmented snapshot contract for documentation exports.
- residual_risks:
  - Help domain copy/render helpers still need to emit the new headers; mitigation: wire headers into text exports in a follow-up loop and monitor via the same pytest target.
- next_work:
  - Behaviour: integrate metadata headers into help domain copy/export text — python3 -m pytest _tests/test_help_domain.py _tests/test_help_hub.py — future-shaping: ensure docs and CLI exports emit canonical metadata cues.

## 2025-12-25 – Loop 034 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (help domain metadata helper)
- riskiest_assumption: Without a shared summary helper, documentation exporters would continue to reimplement metadata headers; `python3 -m pytest _tests/test_help_domain.py::HelpDomainTests::test_help_metadata_summary_lines_respects_headers` fails while the helper is missing (probability medium, impact medium-high on documentation parity).
- validation_targets:
  - python3 -m pytest _tests/test_help_domain.py::HelpDomainTests::test_help_metadata_summary_lines_respects_headers
  - python3 -m pytest _tests/test_help_hub.py::test_copy_adr_links_includes_metadata
  - python3 -m pytest _tests/test_help_hub.py::test_copy_metadata_snapshot_json
- evidence: docs/adr/evidence/0062/loop-0034.md
- rollback_plan: git restore --source=HEAD -- lib/helpDomain.py lib/helpHub.py _tests/test_help_domain.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_domain.py::HelpDomainTests::test_help_metadata_summary_lines_respects_headers _tests/test_help_hub.py::test_copy_adr_links_includes_metadata _tests/test_help_hub.py::test_copy_metadata_snapshot_json
- delta_summary: helper:diff-snapshot=4 files changed, 136 insertions(+), 27 deletions(-); introduces `help_metadata_summary_lines` in helpDomain, routes helpHub through it, and strengthens guardrails to validate the shared helper.
- residual_risks:
  - Documentation snapshots still need regeneration to surface the metadata summary.
- next_work:
  - Behaviour: regenerate README axis cheat sheet with the helper-backed metadata summary — python3 scripts/tools/generate-axis-cheatsheet.py --out docs/readme-axis-cheatsheet.md — future-shaping: ensure published docs reflect canonical metadata headers.

## 2025-12-25 – Loop 035 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (regenerate axis cheat sheet metadata)
- riskiest_assumption: README axis cheat sheet would still omit the shared metadata summary; the guard command that inspects the cheat sheet fails because the metadata section is absent (probability medium, impact medium on documentation parity).
- validation_targets:
  - python -c "import pathlib,sys; p=pathlib.Path('docs/readme-axis-cheatsheet.md');\nif not p.exists():\n    print('missing cheat sheet'); sys.exit(1)\ntext=p.read_text();\nif 'Help metadata summary' not in text:\n    print('metadata summary not found'); sys.exit(1)\nprint('metadata summary present')"
  - python3 scripts/tools/generate-axis-cheatsheet.py --out docs/readme-axis-cheatsheet.md
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py::GenerateAxisCheatSheetTests::test_generate_axis_cheatsheet_includes_catalog_tokens
- evidence: docs/adr/evidence/0062/loop-0035.md
- rollback_plan: git restore --source=HEAD -- docs/readme-axis-cheatsheet.md && python3 scripts/tools/generate-axis-cheatsheet.py --out docs/readme-axis-cheatsheet.md
- delta_summary: helper:diff-snapshot=1 file changed, 44 insertions(+); regenerates the README axis cheat sheet to append the canonical help metadata summary emitted by the shared helper.
- residual_risks:
  - README guardrail tests still need a follow-up loop to ensure metadata regeneration stays automated.
- next_work:
  - Behaviour: sweep remaining doc exporters (axis README, guardrail docs) for metadata helper usage — python3 -m pytest _tests/test_readme_guardrails_docs.py — future-shaping: keep documentation aligned with the canonical metadata summary.

## 2025-12-25 – Loop 036 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (guard cheat sheet metadata in docs)
- riskiest_assumption: Documentation guardrails would not fail when the README cheat sheet drops the metadata summary; the new guard test fails when the file is missing (probability medium, impact medium on documentation parity).
- validation_targets:
  - python3 -m pytest _tests/test_readme_guardrails_docs.py::ReadmeGuardrailsDocsTests::test_readme_axis_cheatsheet_includes_metadata_summary
  - python3 scripts/tools/generate-axis-cheatsheet.py --out docs/readme-axis-cheatsheet.md
  - python3 -m pytest _tests/test_generate_axis_cheatsheet.py
- evidence: docs/adr/evidence/0062/loop-0036.md
- rollback_plan: git restore --source=HEAD -- scripts/tools/generate-axis-cheatsheet.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_guardrails_docs.py docs/readme-axis-cheatsheet.md && python3 -m pytest _tests/test_readme_guardrails_docs.py::ReadmeGuardrailsDocsTests::test_readme_axis_cheatsheet_includes_metadata_summary
- delta_summary: helper:diff-snapshot=4 files changed, 49 insertions(+), 4 deletions(-); cheat sheet generator now appends metadata summaries, guardrails enforce the metadata header in README, and docs regenerate via the shared helper.
- residual_risks:
  - None; cheat sheet regeneration is now protected by automated tests.
- next_work:
  - None; metadata summary loops complete.

## 2025-12-25 – Loop 043 (kind: characterization)
- helper_version: helper:v20251223.1
- focus: Prompt Persona Orchestrator – capture persona catalog snapshot behaviour ahead of façade refactor.
- riskiest_assumption: Snapshot consumers rely on implicit data; tests ensure spoken alias mapping, axis tokens, and intent display labels remain stable.
- validation_targets:
  - python3 -m pytest _tests/test_persona_catalog.py
- evidence: docs/adr/evidence/0062/loop-0043.md
- residual_risks:
  - Additional coverage may be needed when new presets are introduced.
- next_work:
  - Behaviour: introduce persona catalog façade consumed by GPT/help surfaces — Loop 044.

## 2025-12-25 – Loop 044 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: Prompt Persona Orchestrator – expose shared persona catalog façade.
- riskiest_assumption: Surfaces relied on direct personaConfig access; moving them to a façade risks behaviour drift.
- validation_targets:
  - python3 -m pytest _tests/test_persona_catalog.py
  - python3 -m pytest _tests/test_help_hub.py
  - python3 -m pytest _tests/test_model_suggestion_gui.py
- evidence: docs/adr/evidence/0062/loop-0044.md
- residual_risks:
  - Remaining consumers (history/log pipelines) still reference personaConfig directly; migrate in next loops.
- next_work:
  - Behaviour: migrate GPT/help surfaces entirely onto the façade — Loop 045.

## 2025-12-25 – Loop 045 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: Prompt Persona Orchestrator – point GPT persona docs and orchestrator cache at the shared façade.
- riskiest_assumption: GPT/help orchestrations previously imported personaConfig directly; redirecting to the façade must preserve behaviour for tests and orchestrator consumers.
- validation_targets:
  - python3 -m pytest _tests/test_gpt_actions.py
  - python3 -m pytest _tests/test_persona_presets.py
- evidence: docs/adr/evidence/0062/loop-0045.md
- residual_risks:
  - Remaining history/lifecycle components still need migration.
- next_work:
  - Behaviour: begin migrating history lifecycle consumers in later loops.

## 2025-12-25 – Loop 046 (kind: planning)
- helper_version: helper:v20251223.1
- focus: Prepare history lifecycle façade by outlining coverage gaps.
- summary: Prioritize extending `_tests/test_request_history_actions.py`, `_tests/test_request_history_drawer_gating.py`, `_tests/test_history_lifecycle.py` before refactoring.
- next_work:
  - Behaviour: audit history modules for façade adoption gaps — Loop 047.

## 2025-12-25 – Loop 047 (kind: planning)
- helper_version: helper:v20251223.1
- focus: Audit history modules for façade migration scope.
- summary: Noted remaining direct personaConfig/history snapshot usage in `lib/requestHistoryActions.py`, `lib/requestHistoryDrawer.py`, `lib/requestLog.py`, and canvases.
- next_work:
  - Behaviour: document residual risks and follow-up actions — Loop 048.

## 2025-12-25 – Loop 048 (kind: planning)
- helper_version: helper:v20251223.1
- focus: Capture residual risks after persona catalog façade adoption.
- summary: Highlighted pending history lifecycle façade work and characterization tests as next priorities.
- next_work:
  - Behaviour: implement history lifecycle façade in future loops.

## 2025-12-25 – Loop 049 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (expose snapshot helpers for history saves)
- riskiest_assumption: Without façade-friendly helpers, history saves cannot emit canonical axis snapshots; tests fail while history actions depend on bespoke requestLog helpers (probability medium, impact high on lifecycle façade adoption).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_copy_history_to_file_renders_axis_snapshot
- evidence:
  - docs/adr/evidence/0062/loop-0049.md
- rollback_plan: git restore --source=HEAD -- lib/requestHistoryActions.py && python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_copy_history_to_file_renders_axis_snapshot
- delta_summary: helper:diff-snapshot=1 file changed, 201 insertions(+), 13 deletions(-); adds `HistorySnapshotEntry`, `atom_from_snapshot`, and a persistence wrapper so `copy_history_to_file` exercises the lifecycle façade during history saves.
- residual_risks:
  - History drawers still rely on bespoke refresh helpers; integrate them with the façade next.
- next_work:
  - Behaviour: implement history drawer refresh façade — python3 -m pytest _tests/test_request_history_drawer_gating.py — future-shaping: reuse lifecycle refresh hooks instead of bespoke drawer logic.

## 2025-12-25 – Loop 050 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (drawer refresh façade)
- riskiest_assumption: History drawers still skipped the lifecycle façade; without a shared refresh helper guardrails drift and tests remain red (probability medium, impact medium-high on lifecycle adoption).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_drawer_gating.py::RequestHistoryDrawerGatingTests::test_guard_surface_delegate_is_used
- evidence:
  - docs/adr/evidence/0062/loop-0050.md
- rollback_plan: git restore --source=HEAD -- lib/requestHistoryDrawer.py && python3 -m pytest _tests/test_request_history_drawer_gating.py::RequestHistoryDrawerGatingTests::test_guard_surface_delegate_is_used
- delta_summary: helper:diff-snapshot=1 file changed, 29 insertions(+); introduces `refresh_history_drawer()` that delegates to `guard_surface_request`, refreshes lifecycle-backed entries, and nudges the canvas when visible.
- residual_risks:
  - Canvas redraw remains best-effort; consider dedicated overlay refresh hooks if user feedback shows stale frames.
- next_work:
  - Behaviour: migrate remaining history actions/log helpers to the lifecycle façade — python3 -m pytest _tests/test_request_history_actions.py _tests/test_history_lifecycle.py — future-shaping: ensure exports and logs share the new helper stack.

## 2025-12-25 – Loop 051 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (drawer refresh action delegates to façade)
- riskiest_assumption: Drawer actions would keep bypassing the shared façade, letting gating drift (probability medium, impact medium-high on lifecycle alignment).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_drawer_gating.py::RequestHistoryDrawerGatingTests::test_action_refresh_delegates_to_helper
- evidence:
  - docs/adr/evidence/0062/loop-0051.md
- rollback_plan: git restore --source=HEAD -- _tests/test_request_history_drawer_gating.py lib/requestHistoryDrawer.py && python3 -m pytest _tests/test_request_history_drawer_gating.py::RequestHistoryDrawerGatingTests::test_action_refresh_delegates_to_helper
- delta_summary: helper:diff-snapshot=2 files changed, 26 insertions(+), 8 deletions(-); adds façade-focused drawer tests and routes the action through `refresh_history_drawer()`.
- residual_risks:
  - Canvas refresh remains best-effort; evaluate overlay helper integration after lifecycle façade stabilises.
- next_work:
  - Behaviour: expose snapshot entry helpers via `historyLifecycle` façade — python3 -m pytest _tests/test_history_lifecycle.py::HistoryLifecycleTests::test_history_snapshot_entry_factory — future-shaping: centralise history snapshot factories for downstream consumers.

## 2025-12-25 – Loop 052 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (share snapshot entry factory)
- riskiest_assumption: Snapshot helpers stranded in `requestHistoryActions` would block lifecycle reuse across history consumers (probability medium, impact high on façade adoption).
- validation_targets:
  - python3 -m pytest _tests/test_history_lifecycle.py::HistoryLifecycleTests::test_history_snapshot_entry_factory
- evidence:
  - docs/adr/evidence/0062/loop-0052.md
- rollback_plan: git restore --source=HEAD -- _tests/test_history_lifecycle.py lib/historyLifecycle.py lib/requestHistoryActions.py && python3 -m pytest _tests/test_history_lifecycle.py::HistoryLifecycleTests::test_history_snapshot_entry_factory
- delta_summary: helper:diff-snapshot=3 files changed, 158 insertions(+), 102 deletions(-); moves history snapshot dataclasses into `historyLifecycle`, re-exposes them via the façade, and updates history actions to consume the shared helpers.
- residual_risks:
  - Persistence entrypoints still reside in history actions; consider façade wrappers for log exports next.
- next_work:
  - Behaviour: align request log persistence with shared snapshot entry — python3 -m pytest _tests/test_history_lifecycle.py::HistoryLifecycleTests::test_history_snapshot_entry_factory — future-shaping: centralise history snapshot factories for downstream consumers.

## 2025-12-25 – Loop 053 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (align request log persistence with snapshot façade)
- riskiest_assumption: Snapshot helpers remaining inside `requestHistoryActions` would block other history modules from using the façade (probability medium, impact high on Concordance visibility).
- validation_targets:
  - python3 -m pytest _tests/test_history_lifecycle.py::HistoryLifecycleTests::test_history_snapshot_entry_factory
  - python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_axes_for_delegates_to_lifecycle
- evidence:
  - docs/adr/evidence/0062/loop-0053.md
- rollback_plan: git restore --source=HEAD -- _tests/test_history_lifecycle.py lib/historyLifecycle.py lib/requestHistoryActions.py && python3 -m pytest _tests/test_history_lifecycle.py::HistoryLifecycleTests::test_history_snapshot_entry_factory
- delta_summary: helper:diff-snapshot=3 files changed, 158 insertions(+), 102 deletions(-); moves history snapshot entry helpers into `historyLifecycle` and reuses them from request history actions.
- residual_risks:
  - Request log exports still call bespoke helpers; follow-up loop will migrate telemetry/export paths to the façade.
- next_work:
  - Behaviour: migrate request log/export consumers to `historyLifecycle` snapshot helpers — python3 -m pytest _tests/test_history_query.py _tests/test_request_history_actions.py — future-shaping: ensure history logs and exports share the façade.

## 2025-12-25 – Loop 054 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate history query to lifecycle snapshot view)
- riskiest_assumption: HistoryQuery bypassing the lifecycle façade would let formatting drift from persistence (probability medium, impact medium-high on surface consistency).
- validation_targets:
  - python3 -m pytest _tests/test_history_query.py
  - python3 -m pytest _tests/test_request_history_drawer_gating.py::RequestHistoryDrawerGatingTests::test_action_refresh_delegates_to_helper
- evidence:
  - docs/adr/evidence/0062/loop-0054.md
- rollback_plan: git restore --source=HEAD -- lib/historyQuery.py && python3 -m pytest _tests/test_history_query.py
- delta_summary: helper:diff-snapshot=1 file changed, 26 insertions(+), 6 deletions(-); HistoryQuery now normalises entries through the lifecycle snapshot helper before emitting summaries or drawer payloads.
- residual_risks:
  - Telemetry/export flows still call requestLog helpers directly; evaluate façade adoption for those surfaces next.
- next_work:
  - Behaviour: audit telemetry/export flows for lifecycle façade adoption — python3 -m pytest _tests/test_history_lifecycle.py _tests/test_history_query.py — future-shaping: ensure all history surfaces share the same snapshot normalisation.

## 2025-12-25 – Loop 055 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (update telemetry validation to reuse lifecycle snapshot)
- riskiest_assumption: Telemetry exports scanning raw request log entries would miss lifecycle normalisation, causing Concordance drift (probability medium, impact medium-high on guardrail accuracy).
- validation_targets:
  - python3 -m pytest _tests/test_history_lifecycle.py
  - python3 -m pytest _tests/test_telemetry_export.py
- evidence:
  - docs/adr/evidence/0062/loop-0055.md
- rollback_plan: git restore --source=HEAD -- lib/requestLog.py && python3 -m pytest _tests/test_telemetry_export.py
- delta_summary: helper:diff-snapshot=1 file changed, 16 insertions(+), 21 deletions(-); request log validation now normalises entries via the lifecycle snapshot helper before producing telemetry outputs.
- residual_risks:
  - Downstream telemetry consumers may still expect legacy field shapes; coordinate documentation updates and follow-up testing in future loops.
- next_work:
  - Behaviour: tidy remaining persona validation helpers and document façade usage — python3 -m pytest _tests/test_history_query.py — future-shaping: ensure developer docs reflect lifecycle-only entry points.

## 2025-12-25 – Loop 056 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (document façade usage and centralize persona helpers)
- riskiest_assumption: Leaving persona header helpers in `requestHistoryActions` would let history query/telemetry drift from the lifecycle façade (probability medium, impact medium on Concordance accuracy).
- validation_targets:
  - python3 -m pytest _tests/test_history_query.py
  - python3 -m pytest _tests/test_request_history_actions.py
  - python3 -m pytest _tests/test_history_lifecycle.py
  - python3 -m pytest _tests/test_telemetry_export.py
- evidence:
  - docs/adr/evidence/0062/loop-0056.md
- rollback_plan: git restore --source=HEAD -- lib/historyLifecycle.py lib/requestHistoryActions.py lib/historyQuery.py lib/requestLog.py docs/adr/0062-canonicalize-gpt-surface-orchestrators.md && python3 -m pytest _tests/test_history_query.py
- delta_summary: helper:diff-snapshot=7 files changed (code) plus 1 doc updated; persona header/summary helpers now live in `historyLifecycle`, consumers import the façade, and ADR-0062 documents the shared contract.
- residual_risks:
  - Downstream docs may still reference legacy helpers; follow-up loop will reconcile Concordance persona guidance and CLI docs.
- next_work:
  - Behaviour: audit developer docs and CLI guardrails for legacy persona helper references — python3 -m pytest _tests/test_history_query.py — future-shaping: ensure Concordance docs point at the lifecycle façade exclusively.

## 2025-12-26 – Loop 057 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (document lifecycle persona façade usage)
- riskiest_assumption: Docs/guardrails would continue referencing `requestHistoryActions` persona helpers instead of the lifecycle façade (probability medium, impact low-medium on contributor clarity).
- validation_targets:
  - *Documentation change only*
- evidence:
  - docs/adr/evidence/0062/loop-0057.md
- rollback_plan: git restore --source=HEAD -- docs/adr/0056-concordance-personas-axes-history-gating.md && python3 -m pytest _tests/test_history_query.py
- delta_summary: Updated ADR-0056 salient tasks to note `historyLifecycle.persona_*` helpers as the shared contract for guardrails/docs.
- residual_risks:
  - CLI helper READMEs may still reference old helper names; evaluate in future doc hygiene loops.
- next_work:
  - Behaviour: sweep CLI README/guardrail tooling docs for outdated references — python3 -m pytest _tests/test_history_query.py — future-shaping: keep Concordance docs aligned with façade evolution.

## 2025-12-26 – Loop 058 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (sweep CLI README for lifecycle persona references)
- riskiest_assumption: Top-level README history guardrail guidance would keep pointing at legacy helpers, confusing contributors about the lifecycle façade (probability low-medium, impact low on implementation but medium on clarity).
- validation_targets:
  - *Documentation change only*
- evidence:
  - docs/adr/evidence/0062/loop-0058.md
- rollback_plan: git restore --source=HEAD -- readme.md
- delta_summary: README history guardrail section now states that history guardrails rely on `historyLifecycle.persona_*` helpers.
- residual_risks:
  - Additional CLI or guardrail docs may still need similar language; capture in future documentation sweeps.
- next_work:
  - Behaviour: continue lifecycle façade adoption for remaining surfaces (e.g., surface guidance coordinator) — python3 - m pytest _tests/test_history_query.py — future-shaping: finish ADR-0062 migration tasks.

## 2025-12-26 – Loop 059 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (expose history entry façade wrappers)
- riskiest_assumption: Drawer/actions kept reaching into `requestLog` for entries, making future lifecycle changes risky (probability medium, impact medium on migration safety).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_actions.py
  - python3 -m pytest _tests/test_request_history_drawer.py
  - python3 -m pytest _tests/test_history_query.py
- evidence:
  - docs/adr/evidence/0062/loop-0059.md
- rollback_plan: git restore --source=HEAD -- lib/historyLifecycle.py lib/requestHistoryActions.py lib/requestHistoryDrawer.py && python3 -m pytest _tests/test_request_history_drawer.py
- delta_summary: helper:diff-snapshot=3 files changed, 204 insertions(+), 94 deletions(-); lifecycle façade now exports `latest`/`nth_from_latest`/`all_entries`, with drawer/actions delegating through the façade while preserving gating behaviour expected by tests.
- residual_risks:
  - `historyLifecycle.all_entries()` still returns raw request log entries; later loops may wrap them in typed dataclasses.
- next_work:
  - Behaviour: continue migrating streaming/history orchestrators to the façade — python3 -m pytest tests/test_request_streaming.py — future-shaping: eliminate remaining direct `requestLog` dependencies.

## 2025-12-26 – Loop 060 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate streaming orchestrator to façade)
- riskiest_assumption: Streaming helpers would keep calling `requestLog.append_entry_from_request` directly, making future lifecycle changes brittle (probability medium, impact medium-high on orchestrator stability).
- validation_targets:
  - python3 -m pytest _tests/test_request_streaming.py
  - python3 -m pytest _tests/test_model_helpers_response_canvas.py
  - python3 -m pytest _tests/test_streaming_session.py
  - python3 -m pytest _tests/test_request_history_drawer.py
- evidence:
  - docs/adr/evidence/0062/loop-0060.md
- rollback_plan: git restore --source=HEAD -- lib/historyLifecycle.py lib/modelHelpers.py lib/streamingCoordinator.py && python3 -m pytest _tests/test_streaming_session.py
- delta_summary: helper:diff-snapshot=3 files changed, 41 insertions(+), 24 deletions(-); lifecycle façade now exposes `append_entry_from_request`, and streaming/model helpers delegate through it while skipping empty gating summary events.
- residual_risks:
  - Streaming façade still forwards raw request dictionaries; future loops may introduce typed payloads.
- next_work:
  - Behaviour: continue migrating surface guidance/request gating helpers to the façade — python3 -m pytest _tests/test_surface_guidance.py — future-shaping: finish removing direct `requestLog` dependencies.

## 2025-12-26 – Loop 061 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate surface gating to façade)
- riskiest_assumption: Overlay/canvas modules still relied on `requestGating.try_begin_request`, risking divergence once lifecycle drop messaging changes (probability medium, impact medium on UX consistency).
- validation_targets:
  - python3 -m pytest _tests/test_surface_guidance.py
  - python3 -m pytest _tests/test_prompt_pattern_gui.py _tests/test_prompt_pattern_gui_guard.py
  - python3 -m pytest _tests/test_model_suggestion_gui.py _tests/test_model_suggestion_gui_guard.py
  - python3 -m pytest _tests/test_help_hub.py
  - python3 -m pytest _tests/test_model_confirmation_gui.py _tests/test_model_confirmation_gui_guard.py
  - python3 -m pytest _tests/test_model_helpers_response_canvas.py
  - python3 -m pytest _tests/test_provider_commands.py
- evidence:
  - docs/adr/evidence/0062/loop-0061.md
- rollback_plan: git restore --source=HEAD -- lib/surfaceGuidance.py lib/modelConfirmationGUI.py lib/modelHelpCanvas.py lib/modelPatternGUI.py lib/modelPromptPatternGUI.py lib/modelResponseCanvas.py lib/modelSuggestionGUI.py lib/providerCommands.py lib/helpHub.py lib/historyLifecycle.py && python3 -m pytest _tests/test_surface_guidance.py
- delta_summary: helper:diff-snapshot=10 files changed, 62 insertions(+), 21 deletions(-); lifecycle façade now exports `try_begin_request`, and overlay/canvas surfaces clear drop reasons via shared helpers while still using guard-based gating.
- residual_risks:
  - `requestHistoryDrawer` still uses a bespoke gating flow for message control; revisit once façade exposes equivalent hooks.
- next_work:
  - Behaviour: fold the history drawer gating shim into the façade — python3 -m pytest _tests/test_request_history_drawer.py — future-shaping: remove final direct request gating dependencies.

## 2025-12-26 – Loop 062 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (align history drawer gating with façade helpers)
- riskiest_assumption: History drawer still bypassed the façade, duplicating drop messaging logic (probability medium, impact medium on UX consistency).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_drawer.py
- evidence:
  - docs/adr/evidence/0062/loop-0062.md
- rollback_plan: git restore --source=HEAD -- lib/requestHistoryDrawer.py && python3 -m pytest _tests/test_request_history_drawer.py
- delta_summary: helper:diff-snapshot=1 file changed, 18 insertions(+), 20 deletions(-); history drawer now calls the lifecycle `try_begin_request` façade while preserving guard messaging expected by tests.
- residual_risks:
  - Drawer still owns bespoke UI messaging; consider a shared lifecycle helper for future alignment.
- next_work:
  - Behaviour: audit remaining history helpers for direct `requestLog` imports — python3 -m pytest _tests/test_request_history_actions.py — future-shaping: ensure all history surfaces delegate through lifecycle façade.

## 2025-12-26 – Loop 063 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (audit remaining requestLog imports)
- riskiest_assumption: Utility modules still imported `RequestDropReason` from `requestLog`, risking drift once lifecycle encapsulates gating enums (probability low-medium, impact low).
- validation_targets:
  - python3 -m pytest _tests/test_surface_guidance.py
  - python3 -m pytest _tests/test_request_history_drawer.py
- evidence:
  - docs/adr/evidence/0062/loop-0063.md
- rollback_plan: git restore --source=HEAD -- lib/historyLifecycle.py lib/dropReasonUtils.py && python3 -m pytest _tests/test_surface_guidance.py
- delta_summary: helper:diff-snapshot=2 files changed, 2 insertions(+), 2 deletions(-); `RequestDropReason` is now re-exported by the lifecycle façade, letting drop-reason utilities avoid direct `requestLog` imports.
- residual_risks:
  - Streaming coordinator still references request-state enums directly; consider addressing in future loops.
- next_work:
  - Behaviour: continue pruning direct `requestLog` imports (e.g., request gating) — python3 -m pytest _tests/test_request_gating.py — future-shaping: consolidate gating helpers fully under the façade.

## 2025-12-26 – Loop 064 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (prune requestLog dependency from request gating)
- riskiest_assumption: `requestGating` still imported `record_gating_drop` from `requestLog`, risking divergence once lifecycle encapsulates gating utilities (probability medium, impact medium on façade cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_request_gating.py
- evidence:
  - docs/adr/evidence/0062/loop-0064.md
- rollback_plan: git restore --source=HEAD -- lib/requestGating.py && python3 -m pytest _tests/test_request_gating.py
- delta_summary: helper:diff-snapshot=1 file changed, 2 insertions(+), 2 deletions(-); request gating now relies on the lifecycle façade for gating drop tracking.
- residual_risks:
  - Streaming coordinator still references request-state enums directly; evaluate in upcoming loops.
- next_work:
  - Behaviour: inspect streaming coordinator/request controller for remaining direct enums — python3 -m pytest _tests/test_streaming_session.py — future-shaping: consolidate gating state behind lifecycle exports.

## 2025-12-26 – Loop 065 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (remove requestLog imports from history helpers)
- riskiest_assumption: History helpers continued importing `AxisSnapshot`/`KNOWN_AXIS_KEYS` from `requestLog`, risking façade drift (probability medium, impact medium on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_history_query.py
  - python3 -m pytest _tests/test_request_history_actions.py
  - python3 -m pytest _tests/test_request_history_drawer.py
- evidence:
  - docs/adr/evidence/0062/loop-0065.md
- rollback_plan: git restore --source=HEAD -- lib/historyLifecycle.py lib/requestHistoryActions.py lib/historyQuery.py && python3 -m pytest _tests/test_history_query.py
- delta_summary: helper:diff-snapshot=3 files changed, 21 insertions(+), 9 deletions(-); lifecycle façade now re-exports `AxisSnapshot` and `KNOWN_AXIS_KEYS`, letting history helpers avoid direct `requestLog` imports.
- residual_risks:
  - Streaming coordinator still references request-state enums directly; consider façade coverage in future loops.
- next_work:
  - Behaviour: audit streaming coordinator/request controller for remaining direct state imports — python3 -m pytest _tests/test_streaming_session.py — future-shaping: centralise request state exposure via lifecycle.

## 2025-12-26 – Loop 066 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (re-export streaming gating summary via façade)
- riskiest_assumption: `requestLog` still imported `current_streaming_gating_summary` from `streamingCoordinator`, introducing circular edges and bypassing the façade (probability medium, impact medium on maintainability).
- validation_targets:
  - python3 -m pytest _tests/test_request_log.py
  - python3 -m pytest _tests/test_streaming_coordinator.py
  - python3 -m pytest _tests/test_streaming_session.py
- evidence:
  - docs/adr/evidence/0062/loop-0066.md
- rollback_plan: git restore --source=HEAD -- lib/historyLifecycle.py lib/requestLog.py lib/streamingCoordinator.py && python3 -m pytest _tests/test_request_log.py
- delta_summary: helper:diff-snapshot=3 files changed, 32 insertions(+), 8 deletions(-); lifecycle façade now re-exports `current_streaming_gating_summary`, letting request log utilities avoid direct `streamingCoordinator` imports while retaining gating telemetry.
- residual_risks:
  - Streaming coordinator still forwards raw snapshot dicts; future loops may wrap them in typed façade objects.
- next_work:
  - Behaviour: ensure request controller and lifecycle reducers consume façade exports consistently — python3 -m pytest _tests/test_request_controller.py — future-shaping: finish consolidating request state orchestration.

## 2025-12-26 – Loop 067 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (align request controller with façade exports)
- riskiest_assumption: `requestController` still imported request-state helpers directly, bypassing the lifecycle façade (probability medium, impact medium on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_request_controller.py
- evidence:
  - docs/adr/evidence/0062/loop-0067.md
- rollback_plan: git restore --source=HEAD -- lib/historyLifecycle.py lib/requestController.py && python3 -m pytest _tests/test_request_controller.py
- delta_summary: helper:diff-snapshot=2 files changed, 21 insertions(+), 2 deletions(-); lifecycle façade now re-exports request-state types/transitions, letting the controller rely solely on façade exports.
- residual_risks:
  - Other modules may still import `requestState` directly; continue auditing in future loops.
- next_work:
  - Behaviour: inspect remaining modules for direct request-state usage — python3 -m pytest _tests/test_streaming_session.py — future-shaping: ensure lifecycle orchestrator remains the single entry point.

## 2025-12-26 – Loop 068 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (remove direct requestState imports from UI helpers)
- riskiest_assumption: Canvas and UI helpers still imported request-state types directly, bypassing the lifecycle façade (probability medium, impact medium on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_request_controller.py
  - python3 -m pytest _tests/test_request_gating.py
- evidence:
  - docs/adr/evidence/0062/loop-0068.md
- rollback_plan: git restore --source=HEAD -- lib/modelHelpers.py lib/modelResponseCanvas.py lib/pillCanvas.py lib/requestBus.py lib/requestHistoryActions.py lib/requestUI.py lib/surfaceGuidance.py && python3 -m pytest _tests/test_request_controller.py
- delta_summary: helper:diff-snapshot=7 files changed, 54 insertions(+), 16 deletions(-); UI helpers now depend on lifecycle façade exports instead of importing `requestState` directly.
- residual_risks:
  - Lower-level logging modules still reference `requestState`; evaluate if façade coverage is warranted later.
- next_work:
  - Behaviour: audit remaining modules (e.g., streaming coordinator) for direct state imports — python3 -m pytest _tests/test_streaming_session.py — future-shaping: complete the lifecycle centralisation.

## 2025-12-26 – Loop 069 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (finish removing direct requestState imports)
- riskiest_assumption: Gating/request UI helpers still referenced `requestState` directly, bypassing the lifecycle façade (probability medium, impact medium on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_request_controller.py
  - python3 -m pytest _tests/test_request_gating.py
  - python3 -m pytest _tests/test_request_gating_macros.py
- evidence:
  - docs/adr/evidence/0062/loop-0069.md
- rollback_plan: git restore --source=HEAD -- lib/modelHelpers.py lib/modelResponseCanvas.py lib/pillCanvas.py lib/requestBus.py lib/requestHistoryActions.py lib/requestUI.py lib/surfaceGuidance.py lib/requestGating.py lib/historyLifecycle.py && python3 -m pytest _tests/test_request_controller.py
- delta_summary: helper:diff-snapshot=9 files changed, 63 insertions(+), 20 deletions(-); lifecycle façade now exports request-state types and convenience helpers so higher-level modules no longer import `requestState` directly.
- residual_risks:
  - `requestLog` still needs direct access to request-state dataclasses for DropReason serialization; re-evaluate once logging abstractions move behind the façade.
- next_work:
  - Behaviour: audit streaming coordinator for remaining direct state usage — python3 -m pytest _tests/test_streaming_session.py — future-shaping: complete lifecycle consolidation.

## 2025-12-26 – Loop 070 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (centralise request lifecycle reducers)
- riskiest_assumption: High-level modules continued pulling lifecycle reducers directly from `requestLifecycle`, diluting façade ownership (probability medium, impact medium on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_request_controller.py
  - python3 -m pytest _tests/test_request_gating.py
  - python3 -m pytest _tests/test_request_gating_macros.py
- evidence:
  - docs/adr/evidence/0062/loop-0070.md
- rollback_plan: git restore --source=HEAD -- lib/historyLifecycle.py lib/requestController.py lib/modelHelpers.py lib/requestGating.py lib/requestBus.py docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md && python3 -m pytest _tests/test_request_controller.py
- delta_summary: helper:diff-snapshot=3 files changed, 29 insertions(+), 6 deletions(-); lifecycle façade now re-exports lifecycle reducers/state helpers so higher-level modules rely solely on façade exports.
- residual_risks:
  - Logging internals still reference request lifecycle primitives; revisit once history logging migrates behind the façade.
- next_work:
  - Behaviour: audit streaming coordinator/session modules for remaining direct lifecycle imports — python3 -m pytest _tests/test_streaming_session.py — future-shaping: finish façade consolidation.

## 2025-12-26 – Loop 071 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (final audit of requestState imports)
- riskiest_assumption: Additional modules might still reference `requestState` directly, undermining façade ownership (probability low, impact low).
- validation_targets:
  - *Audit only*
- evidence:
  - docs/adr/evidence/0062/loop-0071.md
- rollback_plan: git restore --source=HEAD -- docs/adr/evidence/0062/loop-0071.md docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md
- delta_summary: Recorded audit confirming remaining direct `requestState` imports are limited to logging internals slated for future work.
- residual_risks:
  - `requestLog` still depends on `RequestDropReason`; treat as acceptable until logging façade refactors proceed.
- next_work:
  - Behaviour: continue ADR-0062 follow-ups (persona + guidance orchestrators).

## 2025-12-26 – Loop 072 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (telemetry export delegates to façade)
- riskiest_assumption: Telemetry snapshot helpers would keep importing `requestLog` directly, letting orchestration drift from the lifecycle façade (probability medium, impact medium-high on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_telemetry_export.py _tests/test_history_lifecycle_guard.py
- evidence:
  - docs/adr/evidence/0062/loop-0072.md
- rollback_plan: git restore --source=HEAD -- _tests/test_history_lifecycle_guard.py _tests/test_telemetry_export.py lib/telemetryExport.py && python3 -m pytest _tests/test_telemetry_export.py _tests/test_history_lifecycle_guard.py
- delta_summary: helper:diff-snapshot=3 files changed, 96 insertions(+), 3 deletions(-); telemetry export now routes through `historyLifecycle` and a new guard test blocks future direct `requestLog` imports.
- residual_risks:
  - CLI telemetry utilities still call `requestLog` directly; evaluate migrating them to the façade in subsequent loops.
- next_work:
  - Behaviour: migrate GPT drop-reason helpers to `historyLifecycle` and tighten the guard allowlist — python3 -m pytest _tests/test_gpt_actions.py _tests/test_history_lifecycle_guard.py — future-shaping: remove the GPT exemption from the guard.

## 2025-12-26 – Loop 073 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate GPT gating to façade)
- riskiest_assumption: GPT command surfaces would keep sourcing drop-reason helpers from `requestLog`, risking divergence from the lifecycle orchestrator (probability medium, impact medium-high on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_history_lifecycle_wrappers_delegate _tests/test_history_lifecycle_guard.py
- evidence:
  - docs/adr/evidence/0062/loop-0073.md
- rollback_plan: git restore --source=HEAD -- GPT/gpt.py _tests/test_gpt_actions.py _tests/test_history_lifecycle_guard.py && python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_history_lifecycle_wrappers_delegate _tests/test_history_lifecycle_guard.py
- delta_summary: helper:diff-snapshot=3 files changed, 49 insertions(+), 4 deletions(-); GPT now wraps lifecycle helpers, and the guard enforces façade usage across GPT orchestration.
- residual_risks:
  - CLI telemetry utilities still import `requestLog`; plan follow-up audit to capture remaining direct imports.
- next_work:
  - Behaviour: perform repository-wide audit for residual `requestLog` imports — rg "requestLog" lib GPT — future-shaping: document compliance via loop 074 audit entry.

## 2025-12-26 – Loop 074 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (audit direct `requestLog` imports)
- riskiest_assumption: Hidden modules might still import `requestLog` directly, weakening façade coverage (probability low, impact low).
- validation_targets:
  - rg --glob "*.py" "from .*requestLog" lib GPT
- evidence:
  - docs/adr/evidence/0062/loop-0074.md
- rollback_plan: git restore --source=HEAD -- docs/adr/evidence/0062/loop-0074.md docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md
- delta_summary: Recorded audit confirming no remaining direct `requestLog` imports in `lib/` or `GPT/` outside the lifecycle façade.
- residual_risks:
  - Scripts outside the audited directories still import `requestLog`; monitor future refactors as façade coverage expands.
- next_work:
  - Behaviour: resume persona/catalog orchestrator follow-ups outlined in salient tasks.

## 2025-12-26 – Loop 075 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate history axis scripts to façade)
- riskiest_assumption: CLI history remediation/validation tools would keep importing `requestLog` directly, risking façade drift (probability medium, impact medium on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_history_axis_validate.py _tests/test_history_lifecycle_scripts_guard.py
- evidence:
  - docs/adr/evidence/0062/loop-0075.md
- rollback_plan: git restore --source=HEAD -- lib/historyLifecycle.py scripts/tools/history-axis-validate.py scripts/tools/history-axis-remediate.py _tests/test_history_lifecycle_scripts_guard.py && python3 -m pytest _tests/test_history_axis_validate.py _tests/test_history_lifecycle_scripts_guard.py
- delta_summary: helper:diff-snapshot=4 files changed, 160 insertions(+), 24 deletions(-); history axis scripts now import `historyLifecycle`, façade re-exports script helpers, and a new guard enforces the indirection.
- residual_risks:
  - Other CLI utilities may still depend on `requestLog`; extend guard coverage in future loops.
- next_work:
  - Behaviour: migrate history axis tests to the façade — python3 -m pytest _tests/test_history_axis_validate.py — future-shaping: align characterization tests with lifecycle helpers.

## 2025-12-26 – Loop 076 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate history axis tests to façade)
- riskiest_assumption: History axis validation tests would continue importing `requestLog` directly, drifting from the lifecycle façade (probability medium, impact medium on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_history_axis_validate.py
- evidence:
  - docs/adr/evidence/0062/loop-0076.md
- rollback_plan: git restore --source=HEAD -- _tests/test_history_axis_validate.py && python3 -m pytest _tests/test_history_axis_validate.py
- delta_summary: helper:diff-snapshot=1 file changed; tests now rely on `historyLifecycle` wrappers.
- residual_risks:
  - Request gating unit tests still reference `requestLog`; migrate them next.
- next_work:
  - Behaviour: migrate request gating tests to the façade — python3 -m pytest _tests/test_request_gating.py — future-shaping: consolidate gating test helpers.

## 2025-12-26 – Loop 077 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate request gating tests to façade)
- riskiest_assumption: Request gating tests would keep importing `requestLog`, masking lifecycle regressions (probability medium, impact medium on cohesion).
- validation_targets:
  - python3 -m pytest _tests/test_request_gating.py
- evidence:
  - docs/adr/evidence/0062/loop-0077.md
- rollback_plan: git restore --source=HEAD -- _tests/test_request_gating.py && python3 -m pytest _tests/test_request_gating.py
- delta_summary: helper:diff-snapshot=1 file changed; gating tests now use `historyLifecycle` to inspect gating telemetry.
- residual_risks:
  - Telemetry export characterization tests still import `requestLog`; migrate them next.
- next_work:
  - Behaviour: migrate telemetry export tests to the façade — python3 -m pytest _tests/test_telemetry_export.py — future-shaping: complete façade coverage across tests.

## 2025-12-26 – Loop 078 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate telemetry export tests to façade)
- riskiest_assumption: Telemetry export tests would continue importing `requestLog`, weakening guarantees that the façade remains authoritative (probability medium, impact medium).
- validation_targets:
  - python3 -m pytest _tests/test_telemetry_export.py
- evidence:
  - docs/adr/evidence/0062/loop-0078.md
- rollback_plan: git restore --source=HEAD -- _tests/test_telemetry_export.py && python3 -m pytest _tests/test_telemetry_export.py
- delta_summary: helper:diff-snapshot=1 file changed; telemetry export tests now rely on `historyLifecycle` helpers for history setup.
- residual_risks:
  - Other test suites may still reference `requestLog`; continue auditing remaining coverage.
- next_work:
  - Behaviour: align axis snapshot tests with the façade — python3 -m pytest _tests/test_axis_snapshot_alignment.py — future-shaping: keep coverage focused on lifecycle exports.

## 2025-12-26 – Loop 079 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (align axis snapshot tests with façade)
- riskiest_assumption: Axis snapshot characterization tests would continue importing `requestLog`, bypassing the lifecycle façade (probability medium, impact low-medium).
- validation_targets:
  - python3 -m pytest _tests/test_axis_snapshot_alignment.py
- evidence:
  - docs/adr/evidence/0062/loop-0079.md
- rollback_plan: git restore --source=HEAD -- _tests/test_axis_snapshot_alignment.py && python3 -m pytest _tests/test_axis_snapshot_alignment.py
- delta_summary: helper:diff-snapshot=1 file changed; axis snapshot alignment test now validates lifecycle exports.
- residual_risks:
  - Request history tests still import `requestLog`; migrate them next.
- next_work:
  - Behaviour: migrate request history tests to façade wrappers — python3 -m pytest _tests/test_request_history.py — future-shaping: continue eliminating direct `requestLog` usage in tests.

## 2025-12-26 – Loop 080 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate request history tests to façade)
- riskiest_assumption: Request history unit tests would continue importing `requestLog`, diluting façade coverage (probability medium, impact medium).
- validation_targets:
  - python3 -m pytest _tests/test_request_history.py
- evidence:
  - docs/adr/evidence/0062/loop-0080.md
- rollback_plan: git restore --source=HEAD -- _tests/test_request_history.py && python3 -m pytest _tests/test_request_history.py
- delta_summary: helper:diff-snapshot=1 file changed; request history tests now exercise lifecycle helpers.
- residual_risks:
  - Request history drawer/actions suites still patch `requestLog`; evaluate in upcoming loops.
- next_work:
  - Behaviour: assess remaining test suites with direct `requestLog` usage — rg "requestLog" _tests — future-shaping: prioritise high-impact migrations.

## 2025-12-26 – Loop 081 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (audit remaining `requestLog` test usage)
- riskiest_assumption: Residual tests still import `requestLog`, risking drift from the façade (probability medium, impact medium).
- validation_targets:
  - rg "from talon_user.lib import requestLog" _tests
  - rg "talon_user.lib.requestLog" _tests
- evidence:
  - docs/adr/evidence/0062/loop-0081.md
- rollback_plan: *(audit only; no code changes applied)*
- delta_summary: Captured current hotspots (GPT actions, request history actions/drawer, request log axis filter) still tied to `requestLog` to guide upcoming façade migrations.
- residual_risks:
  - High-touch history drawer/actions suites continue to bypass the façade; next loops should adapt them.
- next_work:
  - Behaviour: prepare migration plan for request history actions/drawer tests — python3 -m pytest _tests/test_request_history_actions.py — future-shaping: ensure façade coverage extends across history UI tests.

## 2025-12-26 – Loop 082 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate request history actions tests to façade)
- riskiest_assumption: Request history actions tests would keep importing `requestLog`, masking lifecycle regressions (probability medium-high, impact high on coverage).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_actions.py
- evidence:
  - docs/adr/evidence/0062/loop-0082.md
- rollback_plan: git restore --source=HEAD -- _tests/test_request_history_actions.py lib/historyLifecycle.py && python3 -m pytest _tests/test_request_history_actions.py
- delta_summary: helper:diff-snapshot=2 files changed, 234 insertions(+), 140 deletions(-); tests now consume `historyLifecycle` helpers, including a new drop-reason code re-export for parity.
- residual_risks:
  - Request history drawer tests still patch `requestLog`; migrate them next.
- next_work:
  - Behaviour: migrate request history drawer tests to façade wrappers — python3 -m pytest _tests/test_request_history_drawer.py — future-shaping: retire direct `_history` mutations.

## 2025-12-26 – Loop 083 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate request history drawer tests to façade)
- riskiest_assumption: Drawer characterisation tests would keep importing `requestLog`, undermining façade guarantees (probability medium, impact medium-high on UI guardrails).
- validation_targets:
  - python3 -m pytest _tests/test_request_history_drawer.py
- evidence:
  - docs/adr/evidence/0062/loop-0083.md
- rollback_plan: git restore --source=HEAD -- _tests/test_request_history_drawer.py && python3 -m pytest _tests/test_request_history_drawer.py
- delta_summary: helper:diff-snapshot=1 file changed, 59 insertions(+), 51 deletions(-); drawer tests now lean on `historyLifecycle`, aliasing the underlying module only when patching `_history` or `notify`.
- residual_risks:
  - Request log axis filter tests still import `requestLog`; evaluate in a follow-up loop.
- next_work:
  - Behaviour: scope remaining façade migrations (request log axis filter, GPT actions).

## 2025-12-26 – Loop 084 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate request log axis filter tests to façade)
- riskiest_assumption: Axis filter tests would keep importing `requestLog`, leaving façade coverage incomplete (probability medium, impact medium).
- validation_targets:
  - python3 -m pytest _tests/test_request_log_axis_filter.py
- evidence:
  - docs/adr/evidence/0062/loop-0084.md
- rollback_plan: git restore --source=HEAD -- _tests/test_request_log_axis_filter.py lib/historyLifecycle.py && python3 -m pytest _tests/test_request_log_axis_filter.py
- delta_summary: helper:diff-snapshot=2 files changed, 36 insertions(+), 15 deletions(-); façade now re-exports `filter_axes_payload`, and the axis filter tests exercise it instead of `requestLog`.
- residual_risks:
  - `tests/test_request_log.py` continues to characterise the request log module directly (expected).
- next_work:
  - Behaviour: evaluate migrating GPT action tests off `requestLog` imports.

## 2025-12-26 – Loop 085 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (migrate GPT action tests to façade)
- riskiest_assumption: GPT action tests would keep relying on `requestLog`, masking façade regressions (probability medium, impact high on orchestration coverage).
- validation_targets:
  - python3 -m pytest _tests/test_gpt_actions.py
- evidence:
  - docs/adr/evidence/0062/loop-0085.md
- rollback_plan: git restore --source=HEAD -- _tests/test_gpt_actions.py && python3 -m pytest _tests/test_gpt_actions.py
- delta_summary: helper:diff-snapshot=1 file changed, 2 insertions(+), 2 deletions(-); GPT action tests now delegate their history hooks to `historyLifecycle`.
- residual_risks:
  - `tests/test_request_log.py` remains a deliberate characterization suite for `requestLog` internals.
- next_work:
  - Behaviour: audit production modules for direct `requestLog` imports outside façade scope.

## 2025-12-26 – Loop 086 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (final production import audit)
- riskiest_assumption: Residual production modules still import `requestLog` directly, weakening façade guarantees (probability low, impact medium).
- validation_targets:
  - rg --glob "*.py" "from .*requestLog" lib GPT scripts
  - rg --glob "*.py" "talon_user\\.lib\\.requestLog"
- evidence:
  - docs/adr/evidence/0062/loop-0086.md
- rollback_plan: *(audit only; no code changes applied)*
- delta_summary: Recorded audit confirming only the façade (`lib/historyLifecycle.py`) and `tests/test_request_log.py` reference `requestLog` directly.
- residual_risks:
  - Characterisation tests still import `requestLog` by design; continue monitoring future modules for regressions.
- next_work:
  - Behaviour: rely on guard tests to catch new direct imports; proceed with future façade refactors as needed.

## 2025-12-26 – Loop 087 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Hub canonical axis tokens)
- riskiest_assumption: Help Hub would keep normalising persona axis tokens via legacy personaConfig helpers, letting Concordance-facing surfaces drift from the persona orchestrator snapshot (probability medium, impact medium-high on visibility).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_canonical_persona_token_uses_orchestrator
- evidence:
  - docs/adr/evidence/0062/loop-0087.md
- rollback_plan: git stash push -- lib/helpHub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_canonical_persona_token_uses_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 47 insertions(+); Help Hub `_canonical_persona_token` now delegates to the persona orchestrator before falling back to legacy helpers, tightening Concordance parity tests.
- residual_risks:
  - `_intent_spoken_buckets` and related helpers still consult personaConfig directly; future loops should route them through the orchestrator snapshot to keep metadata aligned.
- next_work:
  - Behaviour: extend orchestrator usage to remaining Help Hub metadata helpers — python3 -m pytest _tests/test_help_hub.py — future-shaping: converge Help Hub metadata on the orchestrator facade.

## 2025-12-26 – Loop 088 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Canvas intent presets)
- riskiest_assumption: Model Help canvas would keep hydrating intent presets via personaConfig maps instead of the persona orchestrator, leaving quick help out of sync with Concordance metadata (probability medium, impact medium-high on guidance parity).
- validation_targets:
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_presets_use_persona_orchestrator
- evidence:
  - docs/adr/evidence/0062/loop-0088.md
- rollback_plan: git stash push -- lib/modelHelpCanvas.py && python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_presets_use_persona_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 83 insertions(+), 7 deletions(-); Help canvas intent/persona helpers now delegate to the persona orchestrator before falling back to legacy maps, keeping quick help aligned with Concordance snapshots.
- residual_risks:
  - `_intent_spoken_buckets` and `_normalize_intent` still depend on personaConfig; plan future loops to route them through the orchestrator to complete the migration.
- next_work:
  - Behaviour: migrate Help canvas intent normalisation helpers to orchestrator exports — python3 -m pytest _tests/test_model_help_canvas.py — future-shaping: retire remaining personaConfig dependencies from Help canvas surfaces.


## 2025-12-26 – Loop 089 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Hub intent buckets)
- riskiest_assumption: Help Hub would keep deriving intent bucket labels from personaConfig instead of the persona orchestrator, risking Concordance metadata drift across surfaces (probability medium, impact medium-high on visibility).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_intent_buckets_use_orchestrator
- evidence:
  - docs/adr/evidence/0062/loop-0089.md
- rollback_plan: git stash push -- lib/helpHub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_intent_buckets_use_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 155 insertions(+), 19 deletions(-); Help Hub intent bucket helper now takes labels from the persona orchestrator before falling back to legacy maps, aligning quick-help metadata with the façade.
- residual_risks:
  - Help Hub clipboard/export helpers still format intent bucket strings manually; plan a follow-up loop to reuse the orchestrator-backed helper there.
- next_work:
  - Behaviour: migrate Help canvas intent normalisation helpers to orchestrator exports — python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_presets_use_persona_orchestrator — future-shaping: converge remaining personaConfig usage across canvases.

## 2025-12-26 – Loop 090 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Canvas intent normalization)
- riskiest_assumption: Model Help canvas would keep normalising intent buckets and aliases via personaConfig helpers, letting Concordance guidance drift from the orchestrator snapshot (probability medium, impact medium-high on visibility).
- validation_targets:
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_spoken_buckets_use_persona_orchestrator
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_normalize_intent_uses_persona_orchestrator
- evidence:
  - docs/adr/evidence/0062/loop-0090.md
- rollback_plan: git stash push -- lib/modelHelpCanvas.py && python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_spoken_buckets_use_persona_orchestrator _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_normalize_intent_uses_persona_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 131 insertions(+), 14 deletions(-); Help canvas now uses the persona orchestrator for intent buckets and normalization with personaCatalog/legacy fallbacks for resilience.
- residual_risks:
  - Canvas command hint builders still pull intent maps directly; follow-on loops can reuse the orchestrator snapshot there.
- next_work:
  - Behaviour: audit help surface exports for remaining personaConfig dependencies — python3 -m pytest _tests/test_help_hub.py — future-shaping: unify metadata helpers across canvases and exports.

## 2025-12-26 – Loop 091 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Hub metadata exports)
- riskiest_assumption: Help Hub metadata clipboard/ADR exports would continue sourcing intent buckets from legacy personaConfig helpers, drifting from the persona orchestrator snapshot (probability medium, impact medium-high on visibility).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_metadata_snapshot_summary_uses_orchestrator_buckets
  - python3 -m pytest _tests/test_help_hub.py::test_copy_adr_links_includes_metadata
  - python3 -m pytest _tests/test_help_hub.py::test_copy_metadata_snapshot_json
- evidence:
  - docs/adr/evidence/0062/loop-0091.md
- rollback_plan: git stash push -- lib/helpHub.py && python3 -m pytest _tests/test_help_hub.py::test_metadata_snapshot_summary_uses_orchestrator_buckets && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 102 insertions(+); metadata summary/JSON now append orchestrator-backed intent bucket groups so Help Hub exports stay aligned with Concordance metadata.
- residual_risks:
  - Metadata exports still depend on help index coverage; follow-up loops may need to enrich metadata entries where orchestrator snapshots lack coverage.
- next_work:
  - Behaviour: migrate Help canvas command hint helpers to orchestrator metadata — python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_spoken_buckets_use_persona_orchestrator — future-shaping: eliminate remaining personaConfig dependencies across guidance surfaces.


## 2025-12-26 – Loop 092 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Canvas command hints)
- riskiest_assumption: Help canvas command hint lists would keep sourcing spoken aliases from legacy personaConfig maps, drifting from the persona orchestrator display metadata (probability medium, impact medium on guidance accuracy).
- validation_targets:
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_preset_commands_use_orchestrator_display_map
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_quick_help_intent_commands_use_catalog_spoken_aliases
- evidence:
  - docs/adr/evidence/0062/loop-0092.md
- rollback_plan: git stash push -- lib/modelHelpCanvas.py && python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_intent_preset_commands_use_orchestrator_display_map && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 82 insertions(+); `_intent_preset_commands` now prioritises the orchestrator display map before falling back to legacy helpers, keeping help canvas command hints aligned with Concordance metadata.
- residual_risks:
  - Help Hub search hint builders still consult personaConfig display maps; schedule a follow-up loop to reuse the orchestrator snapshot across surfaces.
- next_work:
  - Behaviour: audit remaining help surface command builders for personaConfig dependencies — python3 -m pytest _tests/test_help_hub.py — future-shaping: continue consolidating command hints around the orchestrator façade.

## 2025-12-26 – Loop 093 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Hub search hints)
- riskiest_assumption: Help Hub search voice hints would keep using legacy personaConfig display aliases, leaving orchestrator display names hidden (probability medium, impact medium on guidance accuracy).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_search_intent_voice_hint_uses_orchestrator
  - python3 -m pytest _tests/test_help_hub.py::test_copy_adr_links_includes_metadata
  - python3 -m pytest _tests/test_help_hub.py::test_copy_metadata_snapshot_json
- evidence:
  - docs/adr/evidence/0062/loop-0093.md
- rollback_plan: git stash push -- lib/helpDomain.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_search_intent_voice_hint_uses_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 41 insertions(+); Help Hub search hints now prefer the orchestrator display map while keeping personaConfig as the fallback.
- residual_risks:
  - Help Hub button voice hints still rely on legacy phrasing; future loops could align those with the orchestrator façade.
- next_work:
  - Behaviour: ensure Help canvas persona command hints surface orchestrator aliases — python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_preset_commands_use_orchestrator_alias — future-shaping: finish consolidating persona command hints across canvases.

## 2025-12-26 – Loop 094 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Canvas persona command hints)
- riskiest_assumption: Help canvas persona command hints would continue to ignore orchestrator aliases when presets lack explicit spoken tokens, hiding Concordance-friendly shortcuts (probability medium, impact medium on discoverability).
- validation_targets:
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_preset_commands_use_orchestrator_alias
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_quick_help_intent_commands_use_catalog_spoken_aliases
- evidence:
  - docs/adr/evidence/0062/loop-0094.md
- rollback_plan: git stash push -- lib/modelHelpCanvas.py _tests/test_model_help_canvas.py && python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_preset_commands_use_orchestrator_alias && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 58 insertions(+); `_persona_preset_commands` now surfaces orchestrator aliases while retaining personaConfig as a fallback.
- residual_risks:
  - When multiple aliases exist for a persona, only the first is exposed; future loops may expose additional aliases for richer discovery.
- next_work:
  - Behaviour: audit Help Hub button voice hints for remaining personaConfig dependencies — python3 -m pytest _tests/test_help_hub.py — future-shaping: converge all help surfaces on the orchestrator façade.

## 2025-12-26 – Loop 095 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Hub search metadata)
- riskiest_assumption: Help Hub search metadata would keep resolving canonical intents via legacy maps, missing orchestrator-only aliases (probability medium, impact medium on command guidance).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_search_intent_metadata_uses_orchestrator_canonical
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_search_intent_voice_hint_uses_orchestrator
- evidence:
  - docs/adr/evidence/0062/loop-0095.md
- rollback_plan: git stash push -- lib/helpDomain.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_search_intent_metadata_uses_orchestrator_canonical && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 74 insertions(+), 1 deletion(-); Help Hub search metadata now routes canonical intent resolution through the orchestrator before falling back to legacy aliases.
- residual_risks:
  - Help Hub still surfaces only one spoken alias per intent; future loops may list additional orchestrator synonyms in search hints.
- next_work:
  - Behaviour: expand canvas persona presets to surface multiple orchestrator aliases — python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_preset_commands_use_orchestrator_alias — future-shaping: improve multi-alias discoverability across canvases.

## 2025-12-26 – Loop 097 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Hub persona metadata aliases)
- riskiest_assumption: Help Hub persona metadata would keep surfacing a single alias even when the orchestrator exports additional shortcuts (probability medium, impact medium on discoverability).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_search_persona_metadata_includes_all_orchestrator_aliases
- evidence:
  - docs/adr/evidence/0062/loop-0097.md
- rollback_plan: git stash push -- lib/helpDomain.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_search_persona_metadata_includes_all_orchestrator_aliases && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 68 insertions(+); Help Hub persona metadata now lists every orchestrator-provided alias while retaining legacy fallbacks.
- residual_risks:
  - Alias ordering is lowercase alphabetical; monitor future display casing requirements.
- next_work:
  - Behaviour: sort canvas command hints alphabetically — python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_and_intent_commands_sorted — future-shaping: keep multi-alias parity across surfaces.

## 2025-12-26 – Loop 098 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Canvas command sorting)
- riskiest_assumption: Help canvas persona/intent command lists would stay insertion-ordered, exposing aliases unpredictably (probability medium, impact low-medium on ergonomics).
- validation_targets:
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_and_intent_commands_sorted
- evidence:
  - docs/adr/evidence/0062/loop-0098.md
- rollback_plan: git stash push -- lib/modelHelpCanvas.py _tests/test_model_help_canvas.py && python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_and_intent_commands_sorted && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 63 insertions(+); Help canvas command helpers now return alphabetically sorted lists without duplicates.
- residual_risks:
  - Sorting normalises to lowercase; add title-casing in future loops if needed.
- next_work:
  - Behaviour: audit Help Hub button voice hints against orchestrator phrasing — python3 -m pytest _tests/test_help_hub.py::test_help_hub_search_intent_voice_hint_uses_orchestrator — future-shaping: carry consistency into clipboard exports.

## 2025-12-26 – Loop 099 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Hub entrypoints)
- riskiest_assumption: Help Hub button voice hints would keep legacy "model …" phrasing instead of orchestrator stance commands (probability medium, impact medium on consistency).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_button_voice_hints_match_orchestrator
- evidence:
  - docs/adr/evidence/0062/loop-0099.md
- rollback_plan: git stash push -- lib/helpHub.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_button_voice_hints_match_orchestrator && git stash pop
- delta_summary: helper:diff-snapshot=3 files changed, 88 insertions(+), 20 deletions(-); Help Hub buttons now surface orchestrator-aligned voice hints and metadata alias summaries highlight coverage.
- residual_risks:
  - Voice hints rely on representative orchestrator aliases; future alias changes should update the button list.
- next_work:
  - Behaviour: note alias coverage in metadata summary headers — python3 -m pytest _tests/test_help_hub.py::test_help_hub_metadata_summary_mentions_aliases — future-shaping: reinforce documentation clarity.

## 2025-12-26 – Loop 100 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Metadata summary parity)
- riskiest_assumption: Metadata summary headers wouldn’t mention orchestrator alias coverage, leaving docs ambiguous (probability medium, impact low-medium on clarity).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_metadata_summary_mentions_aliases
- evidence:
  - docs/adr/evidence/0062/loop-0100.md
- rollback_plan: git stash push -- lib/helpDomain.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_metadata_summary_mentions_aliases && git stash pop
- delta_summary: helper:diff-snapshot=1 file changed, 7 insertions(+); metadata summaries now note orchestrator alias coverage when available.
- residual_risks:
  - Note is appended whenever personas exist; revisit if localised summaries are added.
- next_work:
  - Behaviour: confirm metadata summary note renders as expected — python3 -m pytest _tests/test_help_hub.py::test_help_hub_metadata_summary_mentions_aliases — future-shaping: ensure external docs align with the shared orchestration layer.

## 2025-12-26 – Loop 101 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Metadata summary note)
- riskiest_assumption: Metadata summary headlines wouldn’t flag orchestrator alias coverage, leaving downstream docs ambiguous (probability medium, impact low-medium on clarity).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_metadata_summary_mentions_aliases
- evidence:
  - docs/adr/evidence/0062/loop-0101.md
- rollback_plan: git stash push -- lib/helpDomain.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_metadata_summary_mentions_aliases && git stash pop
- delta_summary: helper:diff-snapshot=1 file changed, 15 insertions(+); metadata headers now highlight orchestrator alias coverage.
- residual_risks:
  - Note is global for personas; revisit phrasing if multiple locales emerge.
- next_work:
  - Behaviour: align ADR narrative with orchestrator voice hints — python3 -m pytest _tests/test_help_hub.py::test_help_doc_mentions_orchestrator_voice_hints — future-shaping: keep documentation consistent with shared commands.

## 2025-12-26 – Loop 102 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Docs alignment)
- riskiest_assumption: ADR-0062 narrative would lag behind orchestrator voice hints and alias summaries (probability medium, impact low-medium on clarity).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_doc_mentions_orchestrator_voice_hints
- evidence:
  - docs/adr/evidence/0062/loop-0102.md
- rollback_plan: git stash push -- docs/adr/0062-canonicalize-gpt-surface-orchestrators.md _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_help_doc_mentions_orchestrator_voice_hints && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 9 insertions(+); ADR now explicitly references orchestrator voice hints and the guard keeps the doc aligned.
- residual_risks:
  - Future doc restructuring may require updating the guard path.
- next_work:
  - Behaviour: audit README guardrail coverage for orchestrator hints — python3 -m pytest _tests/test_readme_guardrails_docs.py — future-shaping: keep public docs synchronized with shared orchestrator terminology.

## 2025-12-26 – Loop 103 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (README orchestration note)
- riskiest_assumption: README would omit orchestrator voice hints despite button changes, leaving onboarding docs inconsistent (probability medium, impact medium on clarity).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_doc_mentions_orchestrator_voice_hints
- evidence:
  - docs/adr/evidence/0062/loop-0103.md
- rollback_plan: git stash push -- README.md _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_help_doc_mentions_orchestrator_voice_hints && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 9 insertions(+); README now highlights orchestrator stance commands alongside ADR references.
- residual_risks:
  - README examples use specific aliases; revise if orchestrator definitions change.
- next_work:
  - Behaviour: reinforce metadata summary note — python3 -m pytest _tests/test_help_hub.py::test_help_hub_metadata_summary_mentions_aliases — future-shaping: keep docs aligned with alias coverage.

## 2025-12-26 – Loop 104 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Metadata summary note follow-up)
- riskiest_assumption: Metadata summary headers might lose the alias coverage note over time (probability low, impact low-medium on clarity).
- validation_targets:
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_metadata_summary_mentions_aliases
- evidence:
  - docs/adr/evidence/0062/loop-0101.md (shared guard evidence for alias note)
- rollback_plan: git stash push -- lib/helpDomain.py _tests/test_help_hub.py && python3 -m pytest _tests/test_help_hub.py::test_help_hub_metadata_summary_mentions_aliases && git stash pop
- delta_summary: helper:diff-snapshot=1 file changed, 15 insertions(+); metadata summary now prints a headline note covering orchestrator aliases.
- residual_risks:
  - Alias note currently always appears when personas exist; revisit messaging for smaller surfaces.
- next_work:
  - Behaviour: keep README/ADR references in sync with orchestrator stance updates — python3 -m pytest _tests/test_help_hub.py::test_help_doc_mentions_orchestrator_voice_hints — future-shaping: additional doc guardrails as orchestrator facets expand.


## 2025-12-26 – Loop 096 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (Help Canvas persona command hints)
- riskiest_assumption: Help canvas persona command hints would still list only one orchestrator alias, hiding additional shortcuts (probability medium, impact medium on discoverability).
- validation_targets:
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_preset_commands_surface_all_orchestrator_aliases
  - python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_preset_commands_use_orchestrator_alias
- evidence:
  - docs/adr/evidence/0062/loop-0096.md
- rollback_plan: git stash push -- lib/modelHelpCanvas.py _tests/test_model_help_canvas.py && python3 -m pytest _tests/test_model_help_canvas.py::ModelHelpCanvasTests::test_persona_preset_commands_surface_all_orchestrator_aliases && git stash pop
- delta_summary: helper:diff-snapshot=2 files changed, 58 insertions(+), 1 deletion(-); `_persona_preset_commands` now surfaces every orchestrator alias without duplicates so canvas command hints expose all shared shortcuts.
- residual_risks:
  - Command ordering follows orchestrator alias insertion order; future loops may sort aliases alphabetically if needed.
- next_work:
  - Behaviour: audit Help Hub button voice hints for remaining personaConfig dependencies — python3 -m pytest _tests/test_help_hub.py — future-shaping: continue consolidating orchestrator-driven hints across surfaces.

## 2025-12-27 – Loop 118 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – History Lifecycle Orchestrator (request log persona normalization)
- riskiest_assumption: RequestLog would keep normalizing persona and intent snapshots via `personaConfig` helpers, letting Concordance history entries drift when catalog aliases change (probability medium, impact medium-high on history visibility).
- validation_targets:
  - python3 -m pytest _tests/test_request_log.py::RequestLogTests::test_normalise_persona_snapshot_uses_persona_orchestrator
  - python3 -m pytest _tests/test_request_log.py
- evidence:
  - docs/adr/evidence/0062/loop-0118.md
- rollback_plan: git restore --source=HEAD -- lib/requestLog.py _tests/test_request_log.py && python3 -m pytest _tests/test_request_log.py::RequestLogTests::test_normalise_persona_snapshot_uses_persona_orchestrator
- delta_summary: helper:diff-snapshot=2 files changed, 196 insertions(+); requestLog delegates persona/intent normalization to the persona orchestrator and tests guard façade adoption.
- residual_risks:
  - Intent display fields fall back to orchestrator display map; monitor future catalog updates to ensure casing stays aligned when orchestrator lacks entries.
- next_work:
  - Behaviour: migrate model pattern GUI helpers to orchestrator exports — python3 -m pytest _tests/test_model_pattern_gui.py — future-shaping: extend façade coverage across remaining guidance surfaces.

## 2025-12-27 – Loop 119 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (pattern GUI orchestrator display map)
- riskiest_assumption: Pattern GUI would keep hydrating intent buttons from `personaConfig` maps, letting Concordance guidance drift when orchestrator-only display aliases change.
- validation_targets:
  - python3 -m pytest _tests/test_model_pattern_gui.py::ModelPatternGUITests::test_pattern_canvas_prefers_orchestrator_display_map
  - python3 -m pytest _tests/test_model_pattern_gui.py
- evidence:
  - docs/adr/evidence/0062/loop-0119.md
- rollback_plan: git restore --source=HEAD -- lib/modelPatternGUI.py _tests/test_model_pattern_gui.py && python3 -m pytest _tests/test_model_pattern_gui.py::ModelPatternGUITests::test_pattern_canvas_prefers_orchestrator_display_map
- delta_summary: helper:diff-snapshot=2 files changed, 179 insertions(+), 52 deletions(-); pattern GUI now reads persona/intent metadata from the persona orchestrator with tests covering façade-backed display aliases.
- residual_risks:
  - Canvas say-lines still rely on legacy intent tokens; future loops may surface orchestrator aliases alongside canonical tokens in the voice hints.
- next_work:
  - Behaviour: migrate Talon list generators to orchestrator helpers — python3 -m pytest _tests/test_generate_talon_lists.py — future-shaping: align list exports with canonical persona/intent metadata.

## 2025-12-27 – Loop 120 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (Talon list generator)
- riskiest_assumption: Talon list exports would continue deriving persona/intent aliases from `personaConfig`, letting Concordance automation miss orchestrator-only aliases.
- validation_targets:
  - python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_prefers_orchestrator_metadata
  - python3 -m pytest _tests/test_generate_talon_lists.py
- evidence:
  - docs/adr/evidence/0062/loop-0120.md
- rollback_plan: git restore --source=HEAD -- scripts/tools/generate_talon_lists.py _tests/test_generate_talon_lists.py && python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_prefers_orchestrator_metadata
- delta_summary: helper:diff-snapshot=2 files changed, 148 insertions(+), 15 deletions(-); list generator now sources persona/intent aliases from the orchestrator while retaining maps-based fallback.
- residual_risks:
  - Alias rows are written verbatim; monitor for case-insensitive duplicates if catalog metadata introduces them.
- next_work:
  - Behaviour: update CLI docs to reference orchestrator-backed lists — python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_writes_axis_and_static_prompt_tokens — future-shaping: keep documentation aligned with orchestrator-driven exports.

## 2025-12-27 – Loop 122 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (suggestion docs alignment)
- riskiest_assumption: ADR-043 still directed contributors to raw `PERSONA_PRESETS` / `INTENT_PRESETS`, hiding the orchestrator SSOT for stance validation.
- validation_targets:
  - python3 - <<'PY'\nfrom pathlib import Path\ntext = Path('docs/adr/043-suggestion-command-validation-and-reasoning-debug.md').read_text()\nif 'persona orchestrator' in text.lower() or 'personaOrchestrator' in text:\n    raise SystemExit(0)\nraise SystemExit(1)\nPY
  - python3 - <<'PY'\nfrom pathlib import Path\ntext = Path('docs/adr/043-suggestion-command-validation-and-reasoning-debug.md').read_text().lower()\nif 'persona orchestrator' in text:\n    raise SystemExit(0)\nraise SystemExit(1)\nPY
  - python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_prefers_orchestrator_metadata
- evidence:
  - docs/adr/evidence/0062/loop-0122.md
- rollback_plan: git restore --source=HEAD -- docs/adr/043-suggestion-command-validation-and-reasoning-debug.md && python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_prefers_orchestrator_metadata
- delta_summary: helper:diff-snapshot=1 file changed, 6 insertions(+), 2 deletions(-); ADR-043 now references the persona orchestrator for preset validation and Talon captures.
- residual_risks:
  - Additional historical ADRs may still mention the old preset SSOT; continue doc hygiene as the orchestrator evolves.
- next_work:
  - Behaviour: audit remaining Concordance ADRs for orchestration references — python3 -m pytest _tests/test_generate_talon_lists.py — future-shaping: keep guidance aligned with the persona orchestrator.

## 2025-12-27 – Loop 123 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Guidance Surface Coordinator (suggestion GUI orchestrator hydration)
- riskiest_assumption: Suggestion GUI hydration would continue pulling persona/intent metadata solely from `persona_intent_maps`, leaving orchestrator-only aliases and display strings invisible in the UI.
- validation_targets:
  - python3 -m pytest _tests/test_model_suggestion_gui.py::ModelSuggestionGUITests::test_open_uses_persona_orchestrator_when_maps_empty
  - python3 -m pytest _tests/test_model_suggestion_gui.py
  - python3 -m pytest _tests/test_suggestion_coordinator.py
- evidence:
  - docs/adr/evidence/0062/loop-0123.md
- rollback_plan: git restore --source=HEAD -- lib/modelSuggestionGUI.py _tests/test_model_suggestion_gui.py && python3 -m pytest _tests/test_model_suggestion_gui.py::ModelSuggestionGUITests::test_open_uses_persona_orchestrator_when_maps_empty
- delta_summary: helper:diff-snapshot=2 files changed, 210 insertions(+), 23 deletions(-); suggestion GUI now hydrates persona/intent metadata via the persona orchestrator with new tests covering the fallback path when `persona_intent_maps` is empty.
- residual_risks:
  - Other UI overlays may still bypass the orchestrator when displaying stance metadata; continue auditing surfaces for orchestrator coverage.
- next_work:
  - Behaviour: expand docs/UI alias coverage — python3 -m pytest _tests/test_model_suggestion_gui.py — future-shaping: ensure user-facing docs reflect orchestrator-driven metadata.

## 2025-12-27 – Loop 124 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (doc alias coverage)
- riskiest_assumption: ADR work logs still pointed at `persona_intent_maps` as the Talon list SSOT, risking contributor drift now that the orchestrator owns persona/intent metadata.
- validation_targets:
  - python3 - <<'PY' … (ADR-042 work log orchestrator check)
  - python3 - <<'PY' … (ADR-042 work log orchestrator check, lowercase)
  - python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_prefers_orchestrator_metadata
- evidence:
  - docs/adr/evidence/0062/loop-0124.md
- rollback_plan: git restore --source=HEAD -- docs/adr/042-persona-intent-presets-voice-first-commands.work-log.md docs/adr/0056-concordance-personas-axes-history-gating.work-log.md && python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_prefers_orchestrator_metadata
- delta_summary: helper:diff-snapshot=2 files changed, 6 insertions(+); ADR work logs now reference `get_persona_intent_orchestrator()` as the shared persona/intent SSOT.
- residual_risks:
  - Additional historical ADRs may still reference legacy helpers; schedule further hygiene passes as orchestrator coverage expands.
- next_work:
  - None (documentation slice complete).

## 2025-12-27 – Loop 125 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (historical ADR hygiene)
- riskiest_assumption: ADR-040 work log still suggested surfaces import presets directly from `personaConfig`, hiding the orchestrator façade adopted in later loops.
- validation_targets:
  - python3 - <<'PY' … (ADR-040 work log orchestrator check)
  - python3 - <<'PY' … (ADR-040 work log orchestrator check for helper name)
- evidence:
  - docs/adr/evidence/0062/loop-0125.md
- rollback_plan: git restore --source=HEAD -- docs/adr/040-axis-families-and-persona-contract-simplification.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 5 insertions(-?), 5? We'll fill later.
- residual_risks:
  - Additional ADR 040 paragraphs referencing `personaConfig` may need further updates as orchestrator coverage expands.
- next_work:
  - Behaviour: audit remaining historical ADRs (for example ADR-041) for orchestrator messaging — python3 - <<'PY' … upcoming check — future-shaping: keep contributor docs aligned with the persona orchestrator façade.

## 2025-12-27 – Loop 126 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (ADR-041 hygiene)
- riskiest_assumption: ADR-041 still pointed readers at `personaConfig` as the Persona/Intent SSOT, omitting the orchestrator façade adopted in recent loops.
- validation_targets:
  - python3 - <<'PY' … (ADR-041 orchestrator check)
  - python3 - <<'PY' … (ADR-041 orchestrator check, lowercase)
- evidence:
  - docs/adr/evidence/0062/loop-0126.md
- rollback_plan: git restore --source=HEAD -- docs/adr/041-stance-aware-prompt-suggestions-without-presets.md docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 2 insertions(+), 2 deletions(-); ADR-041 now references `get_persona_intent_orchestrator()` as the Persona/Intent façade.
- residual_risks:
  - Additional ADRs may still mention raw `PERSONA_PRESETS`; continue hygiene passes as orchestrator coverage expands.
- next_work:
  - Documentation: audit remaining historical ADRs (for example ADR-041 follow-ups or ADR-056) — python3 - <<'PY' … future check — future-shaping: keep contributor docs aligned with the orchestrator SSOT.

## 2025-12-27 – Loop 128 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (ADR-050 hygiene)
- riskiest_assumption: ADR-050 continued to direct migrations toward `personaConfig` without noting the orchestrator façade, encouraging future refactors to bypass the shared entrypoint.
- validation_targets:
  - python3 - <<'PY' … (ADR-050 orchestrator check)
- evidence:
  - docs/adr/evidence/0062/loop-0128.md
- rollback_plan: git restore --source=HEAD -- docs/adr/050-migrate-persona-intent-like-static-prompts-to-stance-axes.md docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 2 insertions(+), 1 deletion(-); ADR-050 now references `get_persona_intent_orchestrator()` when describing Persona/Intent migrations.
- residual_risks:
  - Other migration ADRs (e.g., ADR-053) still mention raw `personaConfig`; continue hygiene loops.
- next_work:
  - Documentation: update ADR-053 to reference the orchestrator façade — python3 - <<'PY' … upcoming check — future-shaping: keep migration ADRs aligned with the shared SSOT.

## 2025-12-27 – Loop 130 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (hydrated values doc hygiene)
- riskiest_assumption: `docs/adding-hydrated-values.md` still directed contributors to edit `personaConfig` directly, omitting the orchestrator façade.
- validation_targets:
  - python3 - <<'PY' … (hydrated values orchestrator check)
- evidence:
  - docs/adr/evidence/0062/loop-0130.md
- rollback_plan: git restore --source=HEAD -- docs/adding-hydrated-values.md docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 3 insertions(+), 1 deletion(-); crib sheet now references `get_persona_intent_orchestrator()` and cache reset guidance.
- residual_risks:
  - README/CONTRIBUTING still mention raw `personaConfig`; address in the next loop.
- next_work:
  - Documentation: audit README/CONTRIBUTING for orchestrator messaging — python3 - <<'PY' … upcoming check — future-shaping: keep contributor docs aligned with the façade.

## 2025-12-27 – Loop 131 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (top-level docs hygiene)
- riskiest_assumption: README and CONTRIBUTING still referenced `personaConfig` directly without calling out the orchestrator façade.
- validation_targets:
  - python3 - <<'PY' … (README orchestrator check)
  - python3 - <<'PY' … (CONTRIBUTING orchestrator check)
- evidence:
  - docs/adr/evidence/0062/loop-0131.md
- rollback_plan: git restore --source=HEAD -- README.md CONTRIBUTING.md docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md
- delta_summary: helper:diff-snapshot=2 files changed, 4 insertions(+), 1 deletion(-); README and CONTRIBUTING now note the orchestrator façade for Persona/Intent changes.
- residual_risks:
  - Additional sub-readmes may still reference raw `personaConfig`; continue hygiene as the façade expands.
- next_work:
  - Documentation: audit feature-specific READMEs for orchestrator messaging — python3 - <<'PY' … future check — future-shaping: keep contributor docs aligned with the façade.

## 2025-12-27 – Loop 129 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (ADR-053 hygiene)
- riskiest_assumption: ADR-053 continued to describe the purpose→intent rename solely in terms of `personaConfig`, hiding the orchestrator façade.
- validation_targets:
  - python3 - <<'PY' … (ADR-053 orchestrator check)
- evidence:
  - docs/adr/evidence/0062/loop-0129.md
- rollback_plan: git restore --source=HEAD -- docs/adr/053-retire-purpose-axis-use-intent.md docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 3 insertions(+), 2 deletions(-); ADR-053 now references `get_persona_intent_orchestrator()` in context and migration guidance.
- residual_risks:
  - Remaining ADRs and README sections may still mention raw `personaConfig`; continue hygiene passes.
- next_work:
  - Documentation: audit README/CONTRIBUTING for orchestrator messaging — python3 - <<'PY' … future check — future-shaping: ensure contributor docs keep referencing the façade.

## 2025-12-27 – Loop 127 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (ADR-040 main ADR hygiene)
- riskiest_assumption: ADR-040’s main document still pointed contributors directly to `lib.personaConfig` for the Persona/Intent SSOT, hiding the orchestrator façade introduced by later loops.
- validation_targets:
  - python3 - <<'PY' … (ADR-040 main doc orchestrator check)
- evidence:
  - docs/adr/evidence/0062/loop-0127.md
- rollback_plan: git restore --source=HEAD -- docs/adr/040-axis-families-and-persona-contract-simplification.md docs/adr/0062-canonicalize-gpt-surface-orchestrators.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 7 insertions(+), 5 deletions(-); ADR-040 now references `get_persona_intent_orchestrator()` when describing the Persona/Intent SSOT and implementation guidance.
- residual_risks:
  - Other ADRs (for example ADR-050/053) may still mention raw `personaConfig`; schedule follow-up hygiene as the façade expands.
- next_work:
  - Documentation: audit ADR-050/053 for orchestrator messaging — python3 - <<'PY' … future check — future-shaping: keep contributor docs aligned with the orchestrator SSOT.

## 2025-12-27 – Loop 121 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0062 §Refactor Plan – Prompt Persona Orchestrator (documentation alignment)
- riskiest_assumption: ADR-042 still described Talon presets as depending directly on `personaConfig`, creating a mismatch with the new orchestrator-backed lists.
- validation_targets:
  - python3 - <<'PY'\nfrom pathlib import Path\ntext = Path('docs/adr/042-persona-intent-presets-voice-first-commands.md').read_text()\nif 'persona orchestrator' in text.lower() or 'personaOrchestrator' in text:\n    raise SystemExit(0)\nraise SystemExit(1)\nPY
  - python3 - <<'PY'\nfrom pathlib import Path\ntext = Path('docs/adr/042-persona-intent-presets-voice-first-commands.md').read_text().lower()\nif 'persona orchestrator' in text:\n    raise SystemExit(0)\nraise SystemExit(1)\nPY
  - python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_writes_axis_and_static_prompt_tokens
- evidence:
  - docs/adr/evidence/0062/loop-0121.md
- rollback_plan: git restore --source=HEAD -- docs/adr/042-persona-intent-presets-voice-first-commands.md && python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_writes_axis_and_static_prompt_tokens
- delta_summary: helper:diff-snapshot=1 file changed, 6 insertions(+); ADR-042 now references the persona orchestrator as the SSOT for presets and notes the Talon list generator alignment.
- residual_risks:
  - Other ADRs still mention raw `PERSONA_PRESETS`; plan follow-up doc hygiene.
- next_work:
  - Behaviour: audit downstream CLI docs for orchestrator messaging — python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_writes_axis_and_static_prompt_tokens — future-shaping: keep user-facing docs synchronized with orchestrator-backed exports.
