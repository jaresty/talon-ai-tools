# 054 – Source-agnostic GPT presets – Work Log

## 2026-01-07 – Loop: source-agnostic preset execution (kind: behaviour+tests)

helper_version: helper:v20251223.1
focus: ADR-054 §Decision – Source-agnostic preset execution (remove cached sources and duplicated alias)
active_constraint: Preset execution still reused cached source transcripts and exposed the legacy `model preset run` alias, letting voice users trigger stale-context flows despite ADR-054 requiring explicit source selection.
expected_value:
  Impact: High – eliminates silent stale-context replays and aligns grammar with ADR contract.
  Probability: High – code path now clears cached messages and routes through explicit source resolution.
  Time Sensitivity: Medium – confusion grows as presets ship wider without the clarified command.
  Uncertainty note: Low – unit coverage already exercises preset reruns; change scope was well understood.
validation_targets:
  - python3.11 -m pytest _tests/test_gpt_actions.py _tests/test_recipe_header_lines.py

EVIDENCE
- green | 2026-01-07T08:12:30Z | exit 0 | python3.11 -m pytest _tests/test_gpt_actions.py _tests/test_recipe_header_lines.py
    helper:diff-snapshot= GPT/gpt.py | 178 ++++++++++++++++-----\n GPT/gpt.talon | 4 +--\n _tests/test_gpt_actions.py | 81 ++++++++++\n _tests/test_recipe_header_lines.py | 6 ++\n docs/adr/048-grammar-control-plane-simplification.md | 2 +-\n lib/suggestionCoordinator.py | 21 +++\n docs/adr/054-source-agnostic-gpt-presets.md | 9 ++-\n docs/adr/054-source-agnostic-gpt-presets.work-log.md | 15 +++\n 7 files changed, 263 insertions(+), 51 deletions(-)
    pointer: inline

rollback_plan: git restore --source=HEAD -- GPT/gpt.py GPT/gpt.talon _tests/test_gpt_actions.py _tests/test_recipe_header_lines.py lib/suggestionCoordinator.py docs/adr/048-grammar-control-plane-simplification.md docs/adr/054-source-agnostic-gpt-presets.md docs/adr/054-source-agnostic-gpt-presets.work-log.md

delta_summary: helper:diff-snapshot=7 files changed, 263 insertions(+), 51 deletions(-); added explicit source-aware preset action, removed the `model preset run` alias, hydrated recap metadata with source/destination, updated docs/tests to lock behaviour.

loops_remaining_forecast: 1 (confidence medium) – regenerate help/quickstart surfaces and guardrail snapshots to surface the new command wording once broader documentation refresh runs.

residual_constraints:
- severity: Medium | constraint: Help Hub / quickstart surfaces still need regeneration to mention the `model run … preset …` command; mitigation: schedule next docs refresh (`make axis-guardrails-ci`) and verify guardrail outputs; monitor trigger: after next regen PR; owning ADR: 054.

next_work:
- Behaviour: Regenerate help surfaces/docs to propagate the new preset command wording; Validation: make axis-guardrails-ci
