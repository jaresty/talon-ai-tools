# 0064 — Canonical intent hydration and guard cleanup (work log)

## 2026-01-07 — loop 001
- helper_version: helper:v20251223.1
- focus: Step 1 hydration (system prompt + Help Hub) — restore descriptive text without aliases
- active_constraint: Canonical intent tokens still surface raw strings in request hydration (`python3 -m pytest _tests/test_gpt_suggest_context_snapshot.py::test_suggest_uses_hydrated_system_prompt_for_llm` fails red until personas hydrate descriptions)
- validation_targets:
  - python3 -m pytest _tests/test_gpt_suggest_context_snapshot.py::test_suggest_uses_hydrated_system_prompt_for_llm
  - python3 -m pytest _tests/test_prompt_session.py::PromptSessionTests::test_add_system_prompt_attaches_hydrated_persona_and_axes
  - python3 -m pytest _tests/test_help_hub.py::test_help_hub_search_intent_voice_hint_uses_orchestrator
- evidence:
  - red: docs/adr/evidence/0064/loop-001.md#loop-001-red--helper-rerun-python3---m-pytest-_tests-test_gpt_suggest_context_snapshotpytest_suggest_uses_hydrated_system_prompt_for_llm
  - red: docs/adr/evidence/0064/loop-001.md#loop-001-red--helper-rerun-python3---m-pytest-_tests-test_help_hubpytest_help_hub_search_intent_voice_hint_uses_orchestrator
  - green: docs/adr/evidence/0064/loop-001.md#loop-001-green--helper-rerun-python3---m-pytest-_tests-test_gpt_suggest_context_snapshotpytest_suggest_uses_hydrated_system_prompt_for_llm
  - green: docs/adr/evidence/0064/loop-001.md#loop-001-green--helper-rerun-python3---m-pytest-_tests-test_prompt_sessionpytestsessiontests-test_add_system_prompt_attaches_hydrated_persona_and_axes
  - green: docs/adr/evidence/0064/loop-001.md#loop-001-green--helper-rerun-python3---m-pytest-_tests-test_help_hubpytest_help_hub_search_intent_voice_hint_uses_orchestrator
- rollback_plan: `git restore --source=HEAD -- _tests/test_gpt_suggest_context_snapshot.py _tests/test_prompt_session.py lib/helpDomain.py`
- delta_summary: helper:diff-snapshot=3 files changed, 4 insertions(+), 5 deletions(-) — canonicalise hydration tests and favour orchestrator display labels in Help Hub hints
- loops_remaining_forecast: 3 loops (quick-help persona rendering, guard API shims, full-suite regression) — medium confidence pending canvas + guard validations
- residual_constraints:
  - Quick help persona grid still asserts legacy row layout (severity: medium; mitigation: update renderer/tests; monitor `_tests/test_model_help_canvas_persona_commands.py`; owning ADR 0064 Step 3)
  - Overlay guard API adjustments outstanding (severity: medium; mitigation: add exported shims + test updates; monitor `_tests/test_model_response_overlay_lifecycle.py`; owning ADR 0064 Step 2)
- next_work:
  - Behaviour: Implement quick-help persona spoken token rendering (`python3 -m pytest _tests/test_model_help_canvas_persona_commands.py::ModelHelpPersonaCommandTests::test_persona_block_shows_command_forms`)
  - Behaviour: Restore guard helper compatibility (`python3 -m pytest _tests/test_model_response_overlay_lifecycle.py` and `_tests/test_model_suggestion_gui_guard.py`)

## 2026-01-07 — loop 002
- helper_version: helper:v20251223.1
- focus: Step 3 quick-help rendering — ensure spoken persona shortcuts remain discoverable
- active_constraint: Quick-help persona section omits canonical spoken shortcuts (`python3 -m pytest _tests/test_model_help_canvas_persona_commands.py::ModelHelpPersonaCommandTests::test_persona_block_shows_command_forms` fails red because "Persona: peer" is missing)
- validation_targets:
  - python3 -m pytest _tests/test_model_help_canvas_persona_commands.py::ModelHelpPersonaCommandTests::test_persona_block_shows_command_forms
- evidence:
  - red: docs/adr/evidence/0064/loop-002.md#loop-002-red--helper-rerun-python3---m-pytest-_tests-test_model_help_canvas_persona_commandspy_modelhelpcanvaspersonacommandstests-test_persona_block_shows_command_forms
  - green: docs/adr/evidence/0064/loop-002.md#loop-002-green--helper-rerun-python3---m-pytest-_tests-test_model_help_canvas_persona_commandspy_modelhelpcanvaspersonacommandstests-test_persona_block_shows_command_forms
- rollback_plan: `git restore --source=HEAD -- lib/modelHelpCanvas.py`
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+), 2 deletions(-) — preserve persona preset order so canonical spoken shortcut appears with header prefix
- loops_remaining_forecast: 2 loops (guard API shims, full-suite regression) — medium confidence with guard work outstanding
- residual_constraints:
  - Overlay guard API adjustments outstanding (severity: medium; mitigation: add exported shims + test updates; monitor `_tests/test_model_response_overlay_lifecycle.py`; owning ADR 0064 Step 2)
- next_work:
  - Behaviour: Restore guard helper compatibility (`python3 -m pytest _tests/test_model_response_overlay_lifecycle.py` and `_tests/test_model_suggestion_gui_guard.py`)
  - Behaviour: Reconfirm regression suite once guard path is green (`python3 -m pytest`)

## 2026-01-07 — loop 003
- helper_version: helper:v20251223.1
- focus: Step 2 guard utilities — restore module-level shims and tolerate new gating kwargs
- active_constraint: Overlay/test harness cannot patch guard helpers because module-level shims went missing (`python3 -m pytest _tests/test_model_response_overlay_lifecycle.py` fails red due to `passive` kwarg; `_tests/test_model_suggestion_gui_guard.py` and `_tests/test_request_history_drawer_gating.py` fail on missing exports)
- validation_targets:
  - python3 -m pytest _tests/test_model_response_overlay_lifecycle.py
  - python3 -m pytest _tests/test_model_suggestion_gui_guard.py::ModelSuggestionGUIGuardTests::test_reject_if_request_in_flight_preserves_drop_reason_on_success
  - python3 -m pytest _tests/test_request_history_drawer_gating.py
- evidence:
  - red: docs/adr/evidence/0064/loop-003.md#loop-003-red--helper-rerun-python3---m-pytest-_tests-test_model_response_overlay_lifecyclepy
  - red: docs/adr/evidence/0064/loop-003.md#loop-003-red--helper-rerun-python3---m-pytest-_tests-test_model_suggestion_gui_guardpy_modelsuggestionguiguardtests-test_reject_if_request_in_flight_preserves_drop_reason_on_success
  - red: docs/adr/evidence/0064/loop-003.md#loop-003-red--helper-rerun-python3---m-pytest-_tests-test_request_history_drawer_gatingpy
  - green: docs/adr/evidence/0064/loop-003.md#loop-003-green--helper-rerun-python3---m-pytest-_tests-test_model_response_overlay_lifecyclepy
  - green: docs/adr/evidence/0064/loop-003.md#loop-003-green--helper-rerun-python3---m-pytest-_tests-test_model_suggestion_gui_guardpy_modelsuggestionguiguardtests-test_reject_if_request_in_flight_preserves_drop_reason_on_success
  - green: docs/adr/evidence/0064/loop-003.md#loop-003-green--helper-rerun-python3---m-pytest-_tests-test_request_history_drawer_gatingpy
- rollback_plan: `git restore --source=HEAD -- lib/modelResponseCanvas.py lib/modelSuggestionGUI.py lib/requestHistoryDrawer.py _tests/test_model_response_overlay_lifecycle.py _tests/test_model_suggestion_gui_guard.py _tests/test_request_history_drawer_gating.py`
- delta_summary: helper:diff-snapshot=6 files changed, 92 insertions(+), 24 deletions(-) — add compatibility shims for guard helpers, re-export drop helpers, and update tests for new kwargs
- loops_remaining_forecast: 1 loop (full-suite regression sweep) — medium confidence pending end-to-end run after guard updates
- residual_constraints:
  - Full regression sweep outstanding (severity: medium; mitigation: run `python3 -m pytest`; owning ADR 0064 Step 4)
- next_work:
  - Behaviour: Execute full regression suite and record results (`python3 -m pytest`)

## 2026-01-07 — loop 004
- helper_version: helper:v20251223.1
- focus: Step 4 regression sweep — ensure full suite passes under hydration + guard adjustments
- active_constraint: Guardrail make targets fail with new passive handling (`python3 -m pytest` exits red across overlay guard tests)
- validation_targets:
  - python3 -m pytest
- evidence:
  - red: docs/adr/evidence/0064/loop-004.md#loop-004-red--helper-rerun-python3---m-pytest
  - green: docs/adr/evidence/0064/loop-004.md#loop-004-green--helper-rerun-python3---m-pytest
- rollback_plan: `git restore --source=HEAD -- lib/modelHelpCanvas.py lib/modelSuggestionGUI.py lib/overlayLifecycle.py lib/surfaceGuidance.py`
- delta_summary: helper:diff-snapshot=4 files changed, 48 insertions(+), 14 deletions(-) — sort persona commands while preserving primary spoken token display, add passive-compatible overlays shim, and skip gating when suppression flags are active
- loops_remaining_forecast: 0 loops — ADR behaviours complete pending review
- residual_constraints: None (all guard behaviours green)
- next_work: None
