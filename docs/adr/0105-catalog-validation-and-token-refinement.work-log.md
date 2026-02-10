# ADR-0105 Work Log

## Loop 1 — 2026-02-10T00:00:00Z

```
helper_version: helper:v20251223.1
focus: ADR-0105 Decisions 2, 3, 5
  - D2: Add task-affinity guidance to codetour/gherkin channel descriptions
  - D3: Add make+rewrite semantic conflict note to rewrite form description
  - D5: Populate bar help llm § Incompatibilities with documented conflict rules
  ADR sections: § Decision 2, § Decision 3, § Decision 5

active_constraint: renderCompositionRules emits no content under § Incompatibilities
  because grammar.Hierarchy.AxisIncompatibilities is empty and no code path renders
  the documented semantic conflict rules from ADR-0105; codetour and gherkin
  descriptions lack task-affinity guidance; rewrite lacks make-incompatibility note.
  This was the sole bottleneck: a user consulting § Composition Rules found an empty
  list (eval score 1/5 for composition guidance in cycle 3 Phase 2c).
  Expected value: Impact=High (fills documented gap), Probability=High (deterministic
  code change), Time Sensitivity=Low (stable catalog work).

validation_targets:
  - go test ./internal/barcli/... -run TestLLMHelpIncompatibilitiesPopulated
    (specifying: checks § Incompatibilities contains output-exclusive, codetour,
    gherkin, rewrite conflict strings)
  - go test ./internal/barcli/...
    (regression: all existing tests must continue to pass)

evidence:
  - red | 2026-02-10T00:05:00Z | exit 1 | go test ./internal/barcli/... -run TestLLMHelpIncompatibilitiesPopulated
      helper:diff-snapshot=0 files changed (before implementation)
      All four checks fail: "output-exclusive", "codetour", "gherkin", "rewrite" absent from § Incompatibilities | inline
      Excerpt: "§ Incompatibilities missing output-exclusive channel conflict rule"

  - green | 2026-02-10T00:15:00Z | exit 0 | go test ./internal/barcli/...
      helper:diff-snapshot=5 files changed, 142 insertions(+), 25 deletions(-)
      TestLLMHelpIncompatibilitiesPopulated PASS; all 13 tests pass | inline
      commit: 6acc27e

  - removal | 2026-02-10T00:12:00Z | exit 1 | git stash -- impl files && go test ./internal/barcli/... -run TestLLMHelpIncompatibilitiesPopulated
      helper:diff-snapshot=0 files changed (stashed)
      Test fails with same 4 errors after reverting implementation | inline
      git stash pop restored implementation

rollback_plan: git restore --source=HEAD~1 internal/barcli/help_llm.go internal/barcli/embed/prompt-grammar.json lib/axisConfig.py && go test ./internal/barcli/... -run TestLLMHelpIncompatibilitiesPopulated (expect exit 1)

delta_summary: helper:diff-snapshot=5 files changed, 142 insertions(+), 25 deletions(-)
  - axisConfig.py: codetour/gherkin channel descriptions extended with task-affinity
    guidance; rewrite form description extended with make-incompatibility note
  - prompt-grammar.json: same three token descriptions updated to match axisConfig.py
  - help_llm.go: renderCompositionRules now unconditionally emits three documented
    conflict categories before the grammar-enforced block (which remains conditional)
  - help_llm_test.go: added TestLLMHelpIncompatibilitiesPopulated specifying test
  - work-log: created this file
  Depth-first rung: D5 (empty § Incompatibilities) was the primary constraint;
  D2/D3 bundled as same-pass token-description updates; all three land green.

loops_remaining_forecast: 0 loops — all 6 ADR-0105 decisions implemented:
  D1 done (prior session), D2 done, D3 done, D4 done (prior session),
  D5 done, D6 done (prior session). ADR ready for Completed status.
  Confidence: high.

residual_constraints:
  - severity: Low | D1 follow-up: revised visual/taxonomy descriptions need cycle 4
    evaluation to confirm composability in practice.
    mitigation: scheduled for next ADR-0085 cycle (seeds 0061-0080)
    monitoring: if visual/taxonomy still produce low scores in cycle 4, reconsider
    owning ADR: ADR-0105 § D1 consequences

next_work:
  Behaviour: Mark ADR-0105 as Completed | validation: manual ADR status update
  Behaviour: Cycle 4 evaluation (seeds 0061-0080) to check visual/taxonomy composability
    under revised descriptions | validation: ADR-0085 evaluation rubric
```

### Adversarial Constraint Recap

**Active constraint relieved:** `renderCompositionRules` now always emits § Incompatibilities
content. The token description updates are live in both axisConfig.py and prompt-grammar.json.
The specifying test `TestLLMHelpIncompatibilitiesPopulated` guards all four expected strings
and will catch any future regression that empties the section.

**Residual gap (Low severity):** The visual/taxonomy composability fix (D1) needs a cycle 4
evaluation run before it can be declared stable. Monitoring trigger: cycle 4 Phase 1 mean score
for seeds involving visual/taxonomy; reopen condition: mean below 3.5 for those seeds.
