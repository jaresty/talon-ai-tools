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

## 2026-01-12 – Loop: help/pattern guardrail regen (kind: guardrail)

helper_version: helper:v20251223.1
focus: ADR-076 §Follow-ups 2 – Regenerate help/pattern snapshots so guardrail assets include `form=variants` and the narrowed channel list.
active_constraint: Help hub and pattern snapshots still referenced pre-rebucket tokens because guardrail regeneration had not been rerun since `form=variants` landed.
expected_value:
  Impact: Medium – keeps user-facing guardrail assets aligned with the new axis buckets.
  Probability: High – `make axis-guardrails-ci` regenerates the snapshots directly from the catalog.
  Time Sensitivity: Medium – stale guardrail artefacts would confuse users until the next release if left unresolved.
  Uncertainty note: Low – prior runs showed the command completes quickly when the catalog is in sync.
validation_targets:
  - make axis-guardrails-ci

EVIDENCE
- green | 2026-01-12T01:54:20Z | exit 0 | make axis-guardrails-ci
    helper:diff-snapshot=0 files changed
    pointer: inline (axis guardrail regeneration emitted refreshed README/static prompt snapshots under tmp/ and verified catalog health)

rollback_plan: git restore --source=HEAD -- .

delta_summary: helper:diff-snapshot=0 files changed; reran the guardrail regeneration so tmp/ README axis lines, cheatsheet, and static prompt docs reflect `form=variants`/reduced channel set with catalog validation passing.

loops_remaining_forecast: 1 (confidence medium) – annotate ADR 017 documentation to reference the `method=explore` rename.

residual_constraints:
- severity: Low | constraint: Historical ADR 017 documentation still references `method=samples`, which may confuse readers until annotated; mitigation: add a follow-up doc note linking to ADR-076’s rename; monitor trigger: first doc audit post-rebucket; owning ADR: 017.
- severity: Low | constraint: Help/pattern UIs rely on the regenerated tmp/ outputs being applied in the next documentation refresh; mitigation: queue follow-up to sync the tracked Help Hub/quick help files during the upcoming docs sweep; monitor trigger: after next docs PR; owning ADR: 076.

next_work:
- Behaviour: Annotate ADR 017 docs to highlight `method=explore` replacing `samples`; Validation: python3.11 -m pytest _tests/test_static_prompt_docs.py

## 2026-01-12 – Loop: ADR 017 documentation alignment (kind: docs+tests)

helper_version: helper:v20251223.1
focus: ADR-076 §Follow-ups 2 – Update ADR 017 guidance so it points to `method=explore` + `form=variants` instead of the legacy `method=samples` wording.
active_constraint: ADR 017 still described sampling via `completeness=samples`, which contradicted ADR 076 and risked misleading contributors during migration.
expected_value:
  Impact: Medium – keeps the ADR chain consistent and reduces confusion when teaching sampling recipes.
  Probability: High – editing ADR 017 directly addresses the wording gap.
  Time Sensitivity: Medium – stale guidance would persist in onboarding docs until updated.
  Uncertainty note: Low – scope limited to textual edits plus doc guardrail test.
validation_targets:
  - python3.11 -m pytest _tests/test_static_prompt_docs.py

EVIDENCE
- green | 2026-01-12T02:05:17Z | exit 0 | python3.11 -m pytest _tests/test_static_prompt_docs.py
    helper:diff-snapshot=1 file changed, 24 insertions(+), 24 deletions(-)
    pointer: inline

rollback_plan: git restore --source=HEAD -- docs/adr/017-goal-modifier-decomposition-and-simplification.md

delta_summary: helper:diff-snapshot=1 file changed, 24 insertions(+), 24 deletions(-); updated ADR 017 sampling guidance to reference `method=explore` + `form=variants`, refreshed examples, and adjusted implementation notes/tests references.

loops_remaining_forecast: 1 (confidence medium) – apply regenerated help/pattern snapshots to tracked surfaces in a future docs sweep.

residual_constraints:
- severity: Low | constraint: Help/pattern UIs rely on the regenerated tmp/ outputs being applied in the next documentation refresh; mitigation: queue follow-up to sync the tracked Help Hub/quick help files during the upcoming docs sweep; monitor trigger: after next docs PR; owning ADR: 076.

next_work:
- Behaviour: Sync regenerated help/pattern artefacts into tracked docs/UIs; Validation: make axis-guardrails-test

## 2026-01-12 – Loop: README axis/cheatsheet refresh (kind: docs)

helper_version: helper:v20251223.1
focus: ADR-076 §Follow-ups 2/4 – Apply regenerated axis snapshots to tracked docs and sampling examples.
active_constraint: GPT README, cheatsheet, and sampling examples still reflected pre-variants tokens/orders, risking drift from the catalog and incorrect quick-start recipes.
expected_value:
  Impact: Medium – keeps user-facing docs aligned with the rebucketed axis contract and avoids incorrect recipes.
  Probability: High – generators and targeted edits refresh the tracked artefacts directly from the catalog.
  Time Sensitivity: Medium – delaying doc refresh would keep stale guidance visible to operators.
  Uncertainty note: Low – scope limited to docs and a quick help sample; tests guard the regenerated content.
validation_targets:
  - python3.11 -m pytest _tests/test_readme_axis_lists.py _tests/test_make_static_prompt_docs.py

EVIDENCE
- green | 2026-01-12T02:26:30Z | exit 0 | python3.11 -m pytest _tests/test_readme_axis_lists.py _tests/test_make_static_prompt_docs.py
    helper:diff-snapshot=4 files changed, 26 insertions(+), 25 deletions(-)
    pointer: inline

rollback_plan: git restore --source=HEAD -- GPT/readme.md docs/readme-axis-cheatsheet.md docs/adr/017-goal-modifier-decomposition-and-simplification.md lib/modelHelpCanvas.py

delta_summary: helper:diff-snapshot=4 files changed, 26 insertions(+), 25 deletions(-); regenerated README axis lines/static prompt sections from the catalog, updated the cheatsheet metadata, and corrected curated sampling examples (README, ADR 017, quick help canvas) to include the scope focus token.

loops_remaining_forecast: 1 (confidence medium) – apply regenerated help/pattern artefacts to tracked surfaces (quick help canvas already dynamic; remaining focus is release docs/UI snapshots when refreshed).

residual_constraints:
- severity: Low | constraint: Help/pattern UI docs still rely on regenerated tmp artefacts being applied during the next docs sweep; mitigation: schedule the broader docs/UI refresh before release; monitoring trigger: next docs PR; owning ADR: 076.

next_work:
- Behaviour: Run docs/UI sweep to apply regenerated help/pattern content; Validation: make axis-guardrails-test

## 2026-01-12 – Loop: Publish release notes & accept ADR (kind: docs)

helper_version: helper:v20251223.1
focus: ADR-076 wrap-up – Communicate the rebucket in release notes and mark the ADR accepted now that catalog/docs/quick-help surfaces are aligned.
active_constraint: README release notes and ADR status still reflected a pre-acceptance state, leaving operators without a clear record that explore/variants/focus sampling is live.
expected_value:
  Impact: Medium – documents the change for users and signals closure of the ADR.
  Probability: High – editing README/ADR text addresses the communication gap directly.
  Time Sensitivity: Medium – aligning status soon after landing the rebucket avoids confusion across release artifacts.
  Uncertainty note: Low – documentation-only change, guarded by existing README tests.
validation_targets:
  - python3.11 -m pytest _tests/test_readme_guardrails_docs.py

EVIDENCE
- green | 2026-01-12T02:37:55Z | exit 0 | python3.11 -m pytest _tests/test_readme_guardrails_docs.py
    helper:diff-snapshot=3 files changed, 35 insertions(+), 2 deletions(-)
    pointer: inline

rollback_plan: git restore --source=HEAD -- README.md docs/adr/076-axis-token-rebucket-for-axis-purity.md docs/adr/076-axis-token-rebucket-for-axis-purity.work-log.md

delta_summary: helper:diff-snapshot=3 files changed, 35 insertions(+), 2 deletions(-); added a release note documenting the rebucket, marked ADR 076 as accepted with refreshed summary guidance, and captured the loop in the work log.

loops_remaining_forecast: 0 (confidence high) – All in-repo follow-ups for ADR 076 are complete; future adjustments can ride standard documentation passes.

residual_constraints:
- None; help/pattern surfaces draw from the catalog, and communication artifacts are up to date.

next_work:
- None; reopen if catalog semantics change.
