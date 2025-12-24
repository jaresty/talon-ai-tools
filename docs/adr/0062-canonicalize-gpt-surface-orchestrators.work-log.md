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
