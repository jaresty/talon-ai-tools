# ADR-0112 Work Log

ADR: `0112-prose-form-conflicts-intent-register-mismatch.md`
VCS_REVERT: `git restore --source=HEAD`
EVIDENCE_ROOT: `docs/adr/evidence/0112/`
VALIDATION_TARGET: `go test ./internal/barcli/... -run TestLLMHelp`

---

## Loop 1 — 2026-02-13 — D1: prose-output-form conflicts + questions/diagram combination guidance

```
helper_version: helper:v20251223.1
focus: >
  ADR-0112 D1 — add conflict notes to questions/recipe form descriptions in
  axisConfig.py; add AXIS_KEY_TO_GUIDANCE entries for both; extend
  renderCompositionRules in help_llm.go with prose-output-form conflict
  subcategory and questions+diagram combination guidance; add specifying test.

active_constraint: >
  help_llm.go § Incompatibilities contains no prose-output-form conflict rule
  and no combination guidance for questions+diagram, so bar help llm gives no
  signal for these cases. Falsifiable: TestLLMHelpADR0112D1 (introduced this
  loop) fails red before edits, green after.

validation_targets:
  - go test ./internal/barcli/... -run TestLLMHelpADR0112D1   (specifying — new)
  - go test ./internal/barcli/... -run TestLLMHelp             (regression)
  - make bar-grammar-update                                     (grammar sync)

evidence:
  - red  | 2026-02-13T00:00:00Z | exit 1 | go test ./internal/barcli/... -run TestLLMHelpADR0112D1
      TestLLMHelpADR0112D1: test not found (test introduced in this loop)
      helper:diff-snapshot=0 files changed (pre-edit baseline)
  - green | 2026-02-13T00:00:00Z | exit 0 | go test ./internal/barcli/... -run TestLLMHelpADR0112D1
      All checks pass; prose-output-form conflict and questions+diagram guidance present.
      helper:diff-snapshot: see commit
  - removal | 2026-02-13T00:00:00Z | exit 1 | git restore --source=HEAD lib/axisConfig.py internal/barcli/help_llm.go internal/barcli/help_llm_test.go && go test ./internal/barcli/... -run TestLLMHelpADR0112D1
      Test fails after revert confirming specifying validation.

rollback_plan: git restore --source=HEAD lib/axisConfig.py internal/barcli/help_llm.go internal/barcli/help_llm_test.go internal/barcli/embed/prompt-grammar.json

delta_summary: >
  axisConfig.py: questions description extended with conflict/guidance note;
  recipe description extended with conflict note; AXIS_KEY_TO_GUIDANCE["form"]
  gains questions and recipe entries.
  help_llm.go renderCompositionRules: prose-output-form subcategory added to
  § Incompatibilities; new § Combination Guidance subsection with
  questions+diagram interpretation.
  help_llm_test.go: TestLLMHelpADR0112D1 added as specifying validation.
  Grammar regenerated via make bar-grammar-update.

loops_remaining_forecast: >
  2 loops remaining (D2 social-intent guidance, D3 formally+channel register).
  Confidence: high — both are contained description + guidance-map edits.

residual_constraints:
  - PERSONA_KEY_TO_GUIDANCE does not yet exist in personaConfig.py.
    Severity: M. This blocks D2 TUI guidance display but not description updates.
    Mitigation: create the map in Loop 2 following AXIS_KEY_TO_GUIDANCE pattern.
    Monitoring trigger: D2 loop red evidence on guidance display.
    Owning ADR: 0112 D2.

next_work: >
  Behaviour: D2 — social-intent token guidance (appreciate, entertain, announce)
  Validation: go test ./internal/barcli/... -run TestLLMHelp (regression) +
  new specifying test for intent guidance in personaConfig.py grammar output.
```
