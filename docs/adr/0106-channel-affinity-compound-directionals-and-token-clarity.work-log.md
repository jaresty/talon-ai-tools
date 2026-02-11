# ADR-0106 Work Log

## Loop 1 — 2026-02-10

```
helper_version: helper:v20251223.1
focus: ADR-0106 Decisions 1–6 (all decisions in one loop)
  - D1: code/html/shellscript task-affinity (sim+probe incompatible)
  - D2: prose-form / code-channel conflict class in bar help llm § Incompatibilities
  - D3: compound directional tokens documentation
  - D4: taxonomy/visual channel-compatibility caveats
  - D5: fix task disambiguation note
  - D6: order method disambiguation from sort task
  ADR sections: § Decision 1–6

active_constraint: None of the 6 ADR-0106 decisions are implemented. The highest-impact
  bottleneck is D1+D2: form+channel conflicts caused 4 of 5 low-scoring seeds in cycle 4
  (sim+code, case+code, formats+slack, visual+codetour) and none of these conflict patterns
  are documented in channel descriptions or bar help llm § Incompatibilities. Without D1+D2,
  LLMs generating bar commands will continue to produce invalid form+channel pairings at the
  same ~20% rate observed across cycles 1-4.
  Expected value: Impact=High (resolves #1 recurring defect class), Probability=High
  (deterministic token description + help_llm.go changes), Time Sensitivity=Low.

validation_targets:
  - go test ./internal/barcli/... -run TestLLMHelpIncompatibilitiesPopulated
    (existing; extended to check prose-form rule and sim task-affinity text)
  - go test ./internal/barcli/... -run TestLLMHelpChannelAffinityAndTokenClarity
    (new specifying test covering D3 compound directionals, D4-D6 token description content)
  - go test ./internal/barcli/...
    (regression: all existing tests must pass)

evidence:
  - red | 2026-02-10 | exit 1 | go test -run TestLLMHelpChannelAffinityAndTokenClarity
      (TBD — recorded after test written)
  - green | TBD
  - removal | TBD

rollback_plan: git restore --source=HEAD lib/axisConfig.py lib/staticPromptConfig.py
  internal/barcli/embed/prompt-grammar.json internal/barcli/help_llm.go
  internal/barcli/help_llm_test.go internal/barcli/skills/bar-manual/skill.md &&
  go test ./internal/barcli/... -run TestLLMHelpChannelAffinityAndTokenClarity (expect exit 1)

delta_summary: TBD after implementation

loops_remaining_forecast: 0 loops after this one — all 6 decisions covered in Loop 1.
  Confidence: high (all changes are token description updates + help_llm.go + skill text).

residual_constraints:
  - severity: Low | D5 fix naming: disambiguation note is the low-cost path; a full
    rename of `fix` → `reformat` or `transform` is deferred. Monitoring trigger: if user
    confusion about fix persists across cycle 5, escalate to rename ADR.
    owning ADR: ADR-0106 § D5

next_work:
  Behaviour: All 6 ADR-0106 decisions | validation: TestLLMHelpChannelAffinityAndTokenClarity
```
