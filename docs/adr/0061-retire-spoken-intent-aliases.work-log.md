# 0061 – Retire Spoken Intent Aliases – Work Log

## 2025-12-24 – Loop 1 (kind: guardrail/tests)
- helper_version: helper:v20251223.1
- focus: ADR 0061 §Decision — canonical intent normalisation rejects spoken alias tokens in `personaConfig`.
- riskiest_assumption: Without tightening the canonicaliser, multi-word spoken aliases continue to resolve via `canonical_persona_token`, keeping ADR 015/040 violations hidden (probability high, impact high for maintaining single-word intent contract).
- validation_targets:
  - python3 -m pytest _tests/test_persona_presets.py::PersonaPresetTests::test_canonical_persona_token_rejects_spoken_intent_aliases
- evidence: docs/adr/evidence/0061/loop-0001.md
- rollback_plan: git restore --source=HEAD -- lib/personaConfig.py _tests/test_persona_presets.py && python3 -m pytest _tests/test_persona_presets.py::PersonaPresetTests::test_canonical_persona_token_rejects_spoken_intent_aliases
- delta_summary: helper:diff-snapshot=2 files changed, 8 insertions(+), 5 deletions(-); `normalize_intent_token` now returns canonical tokens only and the new guardrail test fails on spoken aliases.
- residual_risks:
  - Risk: Downstream helpers still expose spoken alias maps (e.g. `intent_synonyms`, Talon lists) and may accept multi-word inputs; mitigation: subsequent loops remove alias maps and refresh dependent tests; monitoring trigger: GPT stance setters or guardrail suites still passing with `intent for deciding`.
- next_work:
  - Behaviour: Update persona intent maps and GPT stance helpers to drop spoken alias dictionaries — python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_intent_set_preset_rejects_spoken_alias
