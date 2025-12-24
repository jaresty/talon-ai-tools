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
  - Risk: Downstream helpers still expose spoken alias maps (e.g. `intent_synonyms`, Talon lists) and may accept multi-word inputs; mitigation: subsequent loops remove alias maps and refresh dependent tests; monitoring trigger: GPT stance setters or guardrail suites still passing with `intent decide`.
- next_work:
  - Behaviour: Update persona intent maps and GPT stance helpers to drop spoken alias dictionaries — python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_intent_set_preset_rejects_spoken_alias

## 2025-12-24 – Loop 2 (kind: behaviour/guardrail)
- helper_version: helper:v20251223.1
- focus: ADR 0061 §§Decision, Consequences — remove spoken intent alias maps and enforce canonical tokens across generator, GPT stance helpers, history summaries, and help surfaces.
- riskiest_assumption: If intent alias dictionaries remain, multi-word phrases like “for deciding” keep passing through canonicalisers (probability high given existing synonyms, impact high for ADR 015/040’s single-word contract).
- validation_targets:
  - python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_intent_set_preset_rejects_spoken_alias
  - python3 -m pytest _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_writes_axis_and_static_prompt_tokens
- evidence: docs/adr/evidence/0061/loop-0002.md
- rollback_plan: git restore --source=HEAD -- lib/personaConfig.py lib/requestHistoryActions.py lib/suggestionCoordinator.py lib/modelPatternGUI.py lib/model_responseCanvas.py scripts/tools/generate_talon_lists.py scripts/tools/history-axis-validate.py && git checkout -- GPT/gpt.py && python3 -m pytest _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_intent_set_preset_rejects_spoken_alias _tests/test_generate_talon_lists.py::GenerateTalonListsTests::test_generate_lists_writes_axis_and_static_prompt_tokens
- delta_summary: helper:diff-snapshot=21 files changed, 112 insertions(+), 149 deletions(-); persona intent maps drop spoken alias dictionaries, Talon list generation emits canonical mappings only, GPT stance helpers and history/help surfaces now display canonical tokens/labels, and associated guardrail suites enforce the behaviour.
- residual_risks:
  - Risk: Legacy docs and ADR examples still cite “for <intent>” phrasing; mitigation: follow-up loop to refresh documentation and help text; monitoring trigger: user feedback or cheat sheets referencing alias tokens.
- next_work:
  - Documentation: Update README, ADR 0061, and help cheat sheets to teach canonical intent tokens — python3 -m pytest _tests/test_help_hub.py::test_help_hub_cheat_sheet_includes_all_intent_tokens

## 2025-12-24 – Loop 3 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR 0061 §§Summary, Consequences — refresh README and ADR notes to point at canonical intent tokens and explain the alias → canonical mapping.
- riskiest_assumption: Without clarifying docs, contributors may continue speaking legacy phrases (“for deciding”), reintroducing drift when editing Talon lists or guidance (probability medium, impact medium for onboarding accuracy).
- validation_targets: (documentation-only loop)
- evidence: n/a (textual updates only; no automated validation required)
- rollback_plan: git restore --source=HEAD -- GPT/readme.md docs/adr/0061-retire-spoken-intent-aliases.work-log.md docs/adr/015-voice-audience-tone-purpose-decomposition.md docs/adr/015-voice-audience-tone-purpose-decomposition.work-log.md docs/adr/017-goal-modifier-decomposition-and-simplification.md docs/adr/040-axis-families-and-persona-contract-simplification.md docs/adr/040-axis-families-and-persona-contract-simplification.work-log.md docs/adr/042-persona-intent-presets-voice-first-commands.md
- delta_summary: helper:diff-snapshot=8 files changed, 65 insertions(+), 26 deletions(-); README + ADR notes now describe canonical intent tokens and flag legacy phrases as historical context.
- residual_risks:
  - Risk: Other legacy docs may still reference retired “for …” phrases; mitigation: continue updating ADR work logs as they are touched; trigger: future ADR loops encountering alias text.
- next_work: none queued beyond ongoing adoption.
