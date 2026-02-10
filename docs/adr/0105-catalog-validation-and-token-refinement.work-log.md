# ADR-0105 Work Log

## Loop 1 — 2026-02-10T00:00:00Z

```
helper_version: helper:v20251223.1
focus: ADR-0105 Decisions 2, 3, 5
  - D2: Add task-affinity guidance to codetour/gherkin channel descriptions
  - D3: Add make+rewrite semantic conflict note to rewrite form description
  - D5: Populate bar help llm § Incompatibilities with documented conflict rules

active_constraint: renderCompositionRules emits no content under § Incompatibilities
  because grammar.Hierarchy.AxisIncompatibilities is empty and no code path renders
  the documented semantic conflict rules; codetour and gherkin descriptions lack
  task-affinity guidance; rewrite lacks make-incompatibility note.
  This is the sole bottleneck: a user consulting § Composition Rules finds an empty
  list, defeating the purpose of the section (eval score 1/5 for composition guidance).

validation_targets:
  - go test ./internal/barcli/... -run TestLLMHelpIncompatibilitiesPopulated
    (specifying: checks § Incompatibilities contains codetour, gherkin, rewrite rules)
  - go test ./internal/barcli/...
    (regression: existing tests must continue to pass)

evidence:
  - red | 2026-02-10T00:00:00Z | exit 1 | go test ./internal/barcli/... -run TestLLMHelpIncompatibilitiesPopulated
      test function does not exist yet — will record after test is written
  - (green and removal TBD after implementation)

rollback_plan: git restore --source=HEAD internal/barcli/help_llm.go internal/barcli/help_llm_test.go lib/axisConfig.py internal/barcli/embed/prompt-grammar.json && go test ./internal/barcli/... -run TestLLMHelpIncompatibilitiesPopulated

delta_summary: helper:diff-snapshot=0 files changed (before edit)

loops_remaining_forecast: 1 loop (this one closes D2/D3/D5; no further open decisions)

residual_constraints:
  - severity: Low | D1 follow-up: revised visual/taxonomy descriptions need cycle 4
    evaluation to confirm composability in practice.
    mitigation: scheduled for next ADR-0085 cycle (seeds 0061-0080)
    monitoring: if visual/taxonomy still produce low scores in cycle 4, reconsider
    owning ADR: ADR-0105 § D1 consequences

next_work:
  Behaviour: D5 Incompatibilities populated | validation: TestLLMHelpIncompatibilitiesPopulated
  Behaviour: D2/D3 token descriptions updated | validation: go test ./internal/barcli/...
```
