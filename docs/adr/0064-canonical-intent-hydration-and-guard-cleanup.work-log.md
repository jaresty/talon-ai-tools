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
