# 076 – Axis Token Rebucket for Method/Form/Channel Purity – Work Log

## 2026-01-12 – Loop: axis rebucket implementation (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR-076 §§Decision 1–4 – Re-home format-heavy tokens into the form axis, retire legacy method tokens, and add migration guardrails/tests.
active_constraint: Format-heavy axis tokens (`diagram`, `html`, `codetour`, `svg`) and legacy method tokens (`visual`, `samples`) still lived on channel/method lists, so prompts violated ADR-076’s contract, guardrails could not flag misuse, and user docs/tests drifted.
expected_value:
  Impact: High – restores axis orthogonality and prevents contract-breaking prompt combinations.
  Probability: High – axisConfig updates plus guardrails/tests ensure the new buckets activate.
  Time Sensitivity: Medium – the longer the drift persisted, the more recipes, docs, and users would reinforce the wrong axis semantics.
  Uncertainty note: Low – the affected code paths are covered by targeted pytest suites and prompt-grammar regeneration.
validation_targets:
  - python3.11 -m pytest _tests/test_axis_registry_drift.py _tests/test_readme_axis_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_static_prompt_docs.py _tests/test_talon_settings_model_prompt.py

EVIDENCE
- red | 2026-01-12T01:47:35Z | exit 1 | python3 -m pytest _tests/test_axis_registry_drift.py
    helper:diff-snapshot= GPT/readme.md | 15 ++++---
 _tests/test_static_prompt_docs.py | 19 +++++++-
 _tests/test_talon_settings_model_prompt.py | 8 ++--
 build/prompt-grammar.json | 71 ++++++++++++++---------------
 docs/readme-axis-cheatsheet.md | 6 +--
 internal/barcli/embed/prompt-grammar.json | 71 ++++++++++++++---------------
 lib/axisConfig.py | 45 +++++++++----------
 lib/modelHelpCanvas.py | 6 ++-
 lib/talonSettings.py | 72 +++++++++++++++++++-----------
 docs/adr/076-axis-token-rebucket-for-axis-purity.md | 78 +++++++++++++++++++++
 docs/adr/076-axis-token-rebucket-for-axis-purity.work-log.md | 53 ++++++++++++++
 11 files changed, 309 insertions(+), 135 deletions(-)
    pointer: inline (error: No module named pytest; default python3 lacks pytest module)
- green | 2026-01-12T01:47:54Z | exit 0 | python3.11 -m pytest _tests/test_axis_registry_drift.py _tests/test_readme_axis_lists.py _tests/test_generate_axis_cheatsheet.py _tests/test_static_prompt_docs.py _tests/test_talon_settings_model_prompt.py
    helper:diff-snapshot= GPT/readme.md | 15 ++++---
 _tests/test_static_prompt_docs.py | 19 +++++++-
 _tests/test_talon_settings_model_prompt.py | 8 ++--
 build/prompt-grammar.json | 71 ++++++++++++++---------------
 docs/readme-axis-cheatsheet.md | 6 +--
 internal/barcli/embed/prompt-grammar.json | 71 ++++++++++++++---------------
 lib/axisConfig.py | 45 +++++++++----------
 lib/modelHelpCanvas.py | 6 ++-
 lib/talonSettings.py | 72 +++++++++++++++++++-----------
 docs/adr/076-axis-token-rebucket-for-axis-purity.md | 78 +++++++++++++++++++++
 docs/adr/076-axis-token-rebucket-for-axis-purity.work-log.md | 53 ++++++++++++++
 11 files changed, 309 insertions(+), 135 deletions(-)
    pointer: inline

rollback_plan: git restore --source=HEAD -- GPT/readme.md _tests/test_static_prompt_docs.py _tests/test_talon_settings_model_prompt.py build/prompt-grammar.json docs/readme-axis-cheatsheet.md internal/barcli/embed/prompt-grammar.json lib/axisConfig.py lib/modelHelpCanvas.py lib/talonSettings.py docs/adr/076-axis-token-rebucket-for-axis-purity.md docs/adr/076-axis-token-rebucket-for-axis-purity.work-log.md

delta_summary: helper:diff-snapshot=11 files changed, 309 insertions(+), 135 deletions(-); moved format-constrained tokens into the form axis, renamed `method=samples` to `method=explore`, added a new `form=variants`, introduced guardrails for legacy channel/method values, refreshed docs/cheatsheets/prompt grammar, and added ADR/work-log context plus targeted test/help updates.

loops_remaining_forecast: 1 (confidence medium) – sweep remaining help/pattern surfaces for any lingering `samples`/channel diagram references and regenerate guardrail snapshots once broader doc refresh runs.

residual_constraints:
- severity: Low | constraint: Historical ADR 017 documentation still references `method=samples`, which may confuse readers until annotated; mitigation: add a follow-up doc note linking to ADR-076’s rename; monitor trigger: first doc audit post-rebucket; owning ADR: 017.
- severity: Medium | constraint: Help Hub / pattern GUI caches need regeneration to surface `form=variants` and the narrower channel list; mitigation: schedule next `make axis-guardrails-ci` run and verify UI snapshots; monitor trigger: after regeneration PR lands; owning ADR: 076.

next_work:
- Behaviour: Regenerate help/pattern snapshots to propagate `form=variants` and updated channel messaging; Validation: make axis-guardrails-ci
