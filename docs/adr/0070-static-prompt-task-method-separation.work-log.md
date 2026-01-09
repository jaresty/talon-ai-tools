## 2026-01-09 — loop 001
- helper_version: helper:v20251223.1
- focus: Decision § implementation — remove method-shaped static prompts and migrate semantics onto the method axis
- active_constraint: Static prompt catalog still blended “what” tasks with “how” directions (math, bridge, COM-B, etc.), duplicating method semantics and making it impossible to reason about overrides per ADR 0070.
- validation_targets:
  - python3 -m pytest
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-001.md#loop-001-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-001.md#loop-001-green--helper-rerun-python3--m-pytest
- rollback_plan: `git restore --source=HEAD -- GPT/readme.md lib/staticPromptConfig.py lib/axisConfig.py build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json _tests/test_static_prompt_config.py _tests/test_static_prompt_docs.py _tests/test_talon_settings_model_prompt.py docs/adr/0070-static-prompt-task-method-separation.md docs/adr/0070-static-prompt-task-method-separation.work-log.md docs/adr/evidence/0070-static-prompt-task-method-separation/loop-001.md`
- delta_summary: helper:diff-snapshot=8 files changed, 381 insertions(+), 1132 deletions(-) — removed 29 procedural static prompts, refreshed axis config/grammar exports, rewrote README/help surfaces, and updated tests to reflect task-only recipes.
- loops_remaining_forecast: 1 loop (add automated lint/test to block new method-shaped static prompts) — medium confidence pending guardrail design effort.
- residual_constraints:
  - No automated lint prevents future procedural descriptions from landing in staticPromptConfig (severity: medium; mitigation: introduce a targeted test that enforces “The response …” declarative copy and fails on method language; monitoring: `python3 -m pytest _tests/test_static_prompt_config.py`).
- next_work:
  - Behaviour: Implement the guardrail test/lint to flag procedural/static prompt drift (validation via `python3 -m pytest _tests/test_static_prompt_config.py`).

## 2026-01-09 — loop 003
- helper_version: helper:v20251223.1
- focus: Decision § guardrails — enforce declarative static prompt contract via automated test coverage
- active_constraint: No automated test prevented static prompt descriptions from reintroducing procedural “how” language, so ADR 0070’s separation could silently regress.
- validation_targets:
  - python3 -m pytest
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-003.md#loop-003-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-003.md#loop-003-green--helper-rerun-python3--m-pytest
- rollback_plan: `git restore --source=HEAD -- lib/staticPromptConfig.py _tests/test_static_prompt_config.py GPT/readme.md internal/barcli/embed/prompt-grammar.json docs/adr/0070-static-prompt-task-method-separation.work-log.md docs/adr/evidence/0070-static-prompt-task-method-separation/loop-003.md`
- delta_summary: helper:diff-snapshot=4 files changed, 71 insertions(+), 36 deletions(-) — tightened declarative copy for legacy prompts, added guardrail tests for procedural phrasing and axis overlap, and refreshed docs/embeds.
- loops_remaining_forecast: 0 loops — guardrail in place, catalog fully separated.
- residual_constraints:
  - None; the declarative-language guardrail now runs with every `python3 -m pytest` invocation.
- next_work:
  - Behaviour: None scheduled; reopen if new guardrail heuristics are required.

