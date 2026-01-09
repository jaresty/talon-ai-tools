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

## 2026-01-09 — loop 005
- helper_version: helper:v20251223.1
- focus: Decision § closure — mark ADR 0070 complete now that task/method separation guardrails are in place
- active_constraint: ADR 0070 remained in `Proposed` status despite implementation landing, leaving contributors without a clear signal that the separation contract is live.
- validation_targets:
  - python3 -m pytest _tests/test_axis_description_language.py _tests/test_static_prompt_config.py
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-005.md#loop-005-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-005.md#loop-005-green--helper-rerun-python3--m-pytest-_tests-test_axis_description_language.py-_tests-test_static_prompt_config.py
- rollback_plan: `git restore --source=HEAD -- docs/adr/0070-static-prompt-task-method-separation.md docs/adr/0070-static-prompt-task-method-separation.work-log.md docs/adr/evidence/0070-static-prompt-task-method-separation/loop-005.md`
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+), 1 deletion(-) — set ADR 0070 status to Accepted now that guardrails backstop the separation.
- loops_remaining_forecast: 0 loops — ADR closed.
- residual_constraints:
  - None; both static prompt and axis guardrails run in CI via pytest.
- next_work:
  - Behaviour: None; reopen only if future guardrail coverage is needed.

## 2026-01-09 — loop 006
- helper_version: helper:v20251223.1
- focus: Decision § surfacing — align CLI completions with the What/How/Why contract while keeping Talon canvases free of shorthand syntax
- active_constraint: Build-stage completions still presented raw axis names (“static”, “completeness”, etc.) without clarifying What vs. How, making it harder to apply ADR 0070’s mental model and risking shorthand leakage into Talon help copy.
- validation_targets:
  - go test ./...
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-006.md#loop-006-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-006.md#loop-006-green--helper-rerun-go-test
- rollback_plan: `git restore --source=HEAD -- AGENTS.md internal/barcli/completion.go internal/barcli/completion_test.go docs/adr/0070-static-prompt-task-method-separation.work-log.md docs/adr/evidence/0070-static-prompt-task-method-separation/loop-006.md`
- delta_summary: helper:diff-snapshot=3 files changed, 28 insertions(+), 20 deletions(-) — retitled CLI completion categories to “What / How / Why”, appended axis keyword hints, adjusted tests, and added an AGENTS note reaffirming the CLI-vs-canvas separation.
- loops_remaining_forecast: 0 loops — surfacing now reinforces the separation without confusing Talon users.
- residual_constraints:
  - None; CLI/tests now cover the presentation contract.
- next_work:
  - Behaviour: None scheduled.

## 2026-01-09 — loop 007
- helper_version: helper:v20251223.1
- focus: Decision § surfacing — align CLI completions with the What/How/Why contract while keeping Talon canvases free of shorthand syntax
- active_constraint: Build-stage completions still presented raw axis names (“static”, “completeness”, etc.) without clarifying What vs. How, making it harder to apply ADR 0070’s mental model and risking shorthand leakage into Talon help copy.
- validation_targets:
  - go test ./...
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-007.md#loop-007-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-007.md#loop-007-green--helper-rerun-go-test
- rollback_plan: `git restore --source=HEAD -- internal/barcli/completion.go internal/barcli/completion_test.go docs/adr/0070-static-prompt-task-method-separation.work-log.md docs/adr/evidence/0070-static-prompt-task-method-separation/loop-007.md`
- delta_summary: helper:diff-snapshot=2 files changed, 8 insertions(+), 8 deletions(-) — relabeled persona categories to “Who / How (tone)” and updated the CLI tests accordingly.
- loops_remaining_forecast: 0 loops — surfacing now consistently conveys What/How/Who/Why distinction.
- residual_constraints:
  - None; CLI completions and tests encode the full framing.
- next_work:
  - Behaviour: None scheduled.

## 2026-01-09 — loop 008
- helper_version: helper:v20251223.1
- focus: Decision § surfacing — add skip navigation and reorder completion groups so Why/Who lead, What follows, and How last
- active_constraint: CLI completions still interleaved persona/axis tokens and offered voice/audience/tone even after selecting a persona preset, making it tedious to jump sections and easy to misapply ADR 0070’s What/How boundary.
- validation_targets:
  - go test ./...
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-008.md#loop-008-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-008.md#loop-008-green--helper-rerun-go-test
- rollback_plan: `git restore --source=HEAD -- internal/barcli/build.go internal/barcli/completion.go internal/barcli/completion_test.go docs/adr/0070-static-prompt-task-method-separation.work-log.md docs/adr/evidence/0070-static-prompt-task-method-separation/loop-008.md`
- delta_summary: helper:diff-snapshot=3 files changed, 154 insertions(+), 41 deletions(-) — introduced a `//next` skip sentinel, reordered completions to Why → Who → What → How, suppressed voice/audience/tone suggestions once a preset is chosen, and expanded tests accordingly.
- loops_remaining_forecast: 0 loops — CLI navigation now mirrors the mental model and provides an explicit skip affordance.
- residual_constraints:
  - None; skip token is stripped before build execution and covered by go tests.
- next_work:
  - Behaviour: None scheduled.

## 2026-01-09 — loop 009
- helper_version: helper:v20251223.1
- focus: Decision § surfacing — finish integrating //next skip handling across completion and build flows
- active_constraint: Skip sentinel logic still duplicated persona/static sections and build execution surfaced `//next` tokens, leaving navigation partially wired and untested.
- validation_targets:
  - go test ./...
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-009.md#loop-009-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-009.md#loop-009-green--helper-rerun-go-test
- rollback_plan: `git restore --source=HEAD -- internal/barcli/build.go internal/barcli/build_test.go internal/barcli/completion.go internal/barcli/completion_test.go docs/adr/0070-static-prompt-task-method-separation.work-log.md docs/adr/evidence/0070-static-prompt-task-method-separation/loop-009.md`
- delta_summary: helper:diff-snapshot=4 files changed, 317 insertions(+), 60 deletions(-) — centralized skip parsing, stripped tokens before build, and added Go coverage for persona, static, and axis skips.
- loops_remaining_forecast: 0 loops — skip navigation now behaves end-to-end.
- residual_constraints:
  - None; CLI completions and build ignore `//next:<stage>` tokens with dedicated tests.
- next_work:
  - Behaviour: None scheduled.

## 2026-01-09 — loop 010
- helper_version: helper:v20251223.1
- focus: Decision § surfacing — verify bare //next sentinel maps to persona skip and stays hidden from build
- active_constraint: Bare `//next` sentinel lacked automated coverage proving persona suggestions remain skipped, so regressions could reach operators without failing `go test ./...`.
- expected_value:
  | Factor           | Value  | Rationale                                                    |
  | Impact           | Medium | Protects persona-first navigation from regressions           |
  | Probability      | High   | Added Go tests exercise both completion and build paths      |
  | Time Sensitivity | Medium | Guard needs to land before publishing skip guidance updates |
- validation_targets:
  - go test ./...
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-010.md#loop-010-green--helper-diff-snapshot-git-diff--stat-200
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-010.md#loop-010-green--helper-rerun-go-test
- rollback_plan: `git restore --source=HEAD -- internal/barcli/completion_test.go internal/barcli/build_test.go docs/adr/evidence/0070-static-prompt-task-method-separation/loop-010.md docs/adr/0070-static-prompt-task-method-separation.work-log.md`
- delta_summary: helper:diff-snapshot=5 files changed, 410 insertions(+), 60 deletions(-) — added bare skip tests for completions/build and captured loop-010 evidence.
- loops_remaining_forecast: 0 loops — skip sentinel guardrails now cover persona/default stages (confidence: high).
- residual_constraints:
  - severity: medium — CLI docs still need skip sentinel guidance; mitigation: update help surfaces/README; monitoring: review operator feedback weekly; owner: ADR 0070.
- next_work:
  - Behaviour: Document skip sentinel usage in CLI help (validation: go test ./...) — queued for documentation loop.

## 2026-01-09 — loop 011
- helper_version: helper:v20251223.1
- focus: Decision § surfacing — publish //next skip sentinel guidance in CLI docs
- active_constraint: CLI quickstart and README lacked skip sentinel instructions, leaving operators unaware that `//next` can bypass persona/static stages when using completions.
- expected_value:
  | Factor           | Value  | Rationale                                                     |
  | Impact           | Medium | Ensures CLI users discover persona skips without trial/error  |
  | Probability      | High   | Updating README and docs quickstart fully resolves the gap    |
  | Time Sensitivity | Medium | Docs should ship with sentinel features before wider rollout |
- validation_targets:
  - go test ./...
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-011.md#loop-011-green--helper-diff-snapshot-git-diff----stat-200
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-011.md#loop-011-green--helper-rerun-go-test
- rollback_plan: `git restore --source=HEAD -- readme.md .docs/src/content/docs/guides/quickstart.mdx docs/adr/evidence/0070-static-prompt-task-method-separation/loop-011.md docs/adr/0070-static-prompt-task-method-separation.work-log.md`
- delta_summary: helper:diff-snapshot=2 files changed, 23 insertions(+), 1 deletion(-) — added CLI skip sentinel documentation to README and the docs quickstart guide.
- loops_remaining_forecast: 0 loops — CLI docs now cover skip sentinels end-to-end (confidence: high).
- residual_constraints:
  - severity: low — Monitor CLI docs for future completion changes; mitigation: keep skip guidance in release checklist; monitoring: review CLI quickstart each release; owner: ADR 0070 maintainers.
- next_work:
  - Behaviour: None scheduled; reopen if future completion features change sentinel behaviour.


## 2026-01-09 — loop 004
- helper_version: helper:v20251223.1
- focus: Decision § guardrails — ensure every axis description remains declarative as part of ADR 0070’s separation contract
- active_constraint: Axis descriptions lacked automated enforcement for the “The response …” declarative requirement, risking reintroduction of imperative language that blurs task vs. method semantics.
- validation_targets:
  - python3 -m pytest
- evidence:
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-004.md#loop-004-green--helper-diff-snapshot-git-diff----stat
  - green: docs/adr/evidence/0070-static-prompt-task-method-separation/loop-004.md#loop-004-green--helper-rerun-python3--m-pytest
- rollback_plan: `git restore --source=HEAD -- _tests/test_axis_description_language.py docs/adr/0070-static-prompt-task-method-separation.work-log.md docs/adr/evidence/0070-static-prompt-task-method-separation/loop-004.md`
- delta_summary: helper:diff-snapshot=1 file changed, 31 insertions(+) — added `_tests/test_axis_description_language.py` to guard every axis description’s declarative phrasing.
- loops_remaining_forecast: 0 loops — declarative guardrails now cover both static prompts and axes.
- residual_constraints:
  - None; declarative checks run as part of `python3 -m pytest`.
- next_work:
  - Behaviour: None scheduled; reopen if ADR scope expands beyond axes/prompts.

