# Work log – 053 Retire the “purpose” axis label; make “intent” the single Why axis

## 2026-01-09
- kind: status
- focus: cutover plan and sequencing
- change: recorded initial plan and execution checklist for retiring purpose and moving to intent-only.
- artefacts: docs/adr/053-retire-purpose-axis-use-intent.md, docs/adr/053-retire-purpose-axis-use-intent.work-log.md.
- tests: not run (doc-only).

## 2026-01-09
- kind: status
- focus: execution touchpoints and open tasks
- change: added execution checklist, definition of done, risks, and open tasks to ADR 053.
- artefacts: docs/adr/053-retire-purpose-axis-use-intent.md, docs/adr/053-retire-purpose-axis-use-intent.work-log.md.
- tests: not run (doc-only).

## 2026-01-09
- kind: behaviour
- focus: codemod helper
- change: added `scripts/tools/codemod_intent_axis.py` to support purpose→intent mechanical updates.
- artefacts: scripts/tools/codemod_intent_axis.py.
- tests: not run (utility addition).

## 2026-01-09
- kind: behaviour
- focus: intent-only cutover
- change: migrated purpose→intent across SSOT, grammar/runtime list (`modelIntent`), stance validation, suggest pipeline, docs/tests; ran pytest.
- artefacts: lib/personaConfig.py, lib/modelTypes.py, lib/stanceValidation.py, GPT/gpt.py, GPT/gpt.talon, GPT/lists/modelIntent.talon-list, multiple tests/docs, docs/adr/053-retire-purpose-axis-use-intent.md.
- tests: `python3 -m pytest` (pass).

## 2026-01-09
- kind: status
- focus: ADR acceptance
- change: marked ADR 053 accepted after the cutover and passing tests.
- artefacts: docs/adr/053-retire-purpose-axis-use-intent.md, docs/adr/053-retire-purpose-axis-use-intent.work-log.md.
- tests: none (state/doc update).

## 2026-01-09
- kind: behaviour
- focus: wording/verification cleanup
- change: cleaned intent-only wording and added a verification note (pytest) in ADR 053.
- artefacts: docs/adr/053-retire-purpose-axis-use-intent.md, docs/adr/053-retire-purpose-axis-use-intent.work-log.md.
- tests: not rerun (doc cleanup).

## 2026-01-09
- kind: behaviour
- focus: new intent token
- change: added intent token `for resolving` to intent axis and Talon list; updated guardrail test.
- artefacts: lib/personaConfig.py, GPT/lists/modelIntent.talon-list, _tests/test_voice_audience_tone_purpose_lists.py.
- tests: `python3 -m pytest` (pass).

## 2026-01-09
- kind: status
- focus: intent surfacing requirements
- change: reopened ADR to In Progress; added open tasks to surface all intent tokens in presets/quick help and to rename intent tokens to single-word, speakable keys.
- artefacts: docs/adr/053-retire-purpose-axis-use-intent.md, docs/adr/053-retire-purpose-axis-use-intent.work-log.md.
- tests: none (doc/state update).

## 2026-01-09
- kind: behaviour
- focus: doc corrections
- change: restored ADR/work-log titles and references to “purpose”→“intent” after accidental codemod edits.
- artefacts: docs/adr/053-retire-purpose-axis-use-intent.md, docs/adr/053-retire-purpose-axis-use-intent.work-log.md.
- tests: not run (doc fix).

## 2026-01-09
- kind: behaviour
- focus: intent token canonicalisation and validation
- change: converted intent tokens to single-word canonicals (with spoken→canonical map), added `resolve`, updated Talon list values, stance validation (spoken + canonical), and list guardrail tests. Ran full pytest.
- artefacts: lib/personaConfig.py, lib/modelTypes.py, lib/stanceValidation.py, GPT/lists/modelIntent.talon-list, _tests/test_voice_audience_tone_purpose_lists.py, _tests/test_gpt_actions.py, _tests/test_gpt_suggest_context_snapshot.py, _tests/test_gpt_suggest_validation.py, _tests/test_prompt_session.py, _tests/test_suggestion_stance_validation.py.
- tests: `python3 -m pytest` (pass).

## 2026-01-09
- kind: behaviour
- focus: intent token surfacing and bucket coverage
- change: quick help now shows all intent tokens bucketed (task/relational) via spoken→canonical maps; added bucket parity tests and cheat-sheet coverage; expanded intent buckets to cover all canonical tokens including inform/triage/announce/learn; ensured list values remain single-word.
- artefacts: lib/helpHub.py, lib/personaConfig.py, _tests/test_help_hub.py, _tests/test_voice_audience_tone_purpose_lists.py.
- tests: `python3 -m pytest` (pass).

## 2026-01-09
- kind: status
- focus: mark ADR 053 accepted
- change: all open tasks completed (intent surfacing, single-word tokens, bucket coverage); ADR status set to Accepted.
- artefacts: docs/adr/053-retire-purpose-axis-use-intent.md, docs/adr/053-retire-purpose-axis-use-intent.work-log.md.
- tests: not rerun (state/doc update).

## 2026-01-09
- kind: status
- focus: adversarial check for remaining in-repo work
- change: re-reviewed ADR 053 scope after acceptance; scanned intent surfacing/bucket tests (lib/helpHub.py, lib/personaConfig.py, _tests/test_help_hub.py, _tests/test_voice_audience_tone_purpose_lists.py) and full pytest run to confirm no missing in-repo tasks. No additional work identified.
- artefacts: docs/adr/053-retire-purpose-axis-use-intent.md, docs/adr/053-retire-purpose-axis-use-intent.work-log.md; references inspected code/tests above.
- tests: not rerun (full pytest already green this loop).
