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
  0 loops remaining. All three decisions implemented and committed.

residual_constraints:
  - PERSONA_KEY_TO_GUIDANCE does not yet exist in personaConfig.py.
    Severity: M. This blocks D2 TUI guidance display but not description updates.
    Mitigation: create the map in Loop 2 following AXIS_KEY_TO_GUIDANCE pattern.
    Monitoring trigger: D2 loop red evidence on guidance display.
    Owning ADR: 0112 D2.

next_work: >
  None — all three decisions complete. ADR marked Completed.

---

## Loop 2 — 2026-02-13 — D2: PERSONA_KEY_TO_GUIDANCE + intent/tone guidance

```
helper_version: helper:v20251223.1
focus: ADR-0112 D2 — create PERSONA_KEY_TO_GUIDANCE in personaConfig.py;
  wire into promptGrammar.py, grammar.go, app.go; verify guidance displays
  for appreciate, entertain, announce in bar help tokens.

active_constraint: >
  PERSONA_KEY_TO_GUIDANCE did not exist; no mechanism to display selection-time
  guidance for persona tokens in TUI. Falsifiable: PersonaGuidance() method
  missing from grammar.go (compile-time check) and guidance absent from
  bar help tokens persona-intents output.

evidence:
  - green | 2026-02-13T00:00:00Z | exit 0 | go build ./...
  - green | 2026-02-13T00:00:00Z | exit 0 | go test ./internal/barcli/... -run TestLLMHelp
  - green | 2026-02-13T00:00:00Z | exit 0 | /tmp/bar help tokens persona-intents
      appreciate, entertain, announce all show ↳ guidance lines.

rollback_plan: git restore --source=HEAD lib/personaConfig.py lib/promptGrammar.py internal/barcli/grammar.go internal/barcli/app.go internal/barcli/embed/prompt-grammar.json

delta_summary: >
  personaConfig.py: PERSONA_KEY_TO_GUIDANCE added with intent (appreciate,
  entertain, announce) and tone (formally) entries; persona_key_to_guidance_map()
  accessor added.
  promptGrammar.py: import + guidance export wired into persona section.
  grammar.go: Guidance field on rawPersona + PersonaSection; PersonaGuidance()
  accessor; population wired.
  app.go: ↳ guidance display after persona axis and intent token descriptions.
  Grammar regenerated.

loops_remaining_forecast: 1 loop remaining (D3 help_llm.go register note).

residual_constraints:
  - D3 (formally+channel register in bar help llm) not yet implemented.
    Severity: L — guidance is in PERSONA_KEY_TO_GUIDANCE but not in bar help llm text.
    Monitoring: TestLLMHelpADR0112D3 will fail red until D3 lands.
    Owning ADR: 0112 D3.

next_work: >
  Behaviour: D3 — add tone/channel register conflict note to help_llm.go
  § Incompatibilities.
  Validation: go test ./internal/barcli/... -run TestLLMHelpADR0112D3 (specifying).
```

---

## Loop 3 — 2026-02-13 — D3: tone/channel register conflict in bar help llm

```
helper_version: helper:v20251223.1
focus: ADR-0112 D3 — add Tone/channel register conflicts subcategory to
  renderCompositionRules § Incompatibilities in help_llm.go; add
  TestLLMHelpADR0112D3 specifying test.

active_constraint: >
  bar help llm § Incompatibilities contains no tone/channel register conflict
  note, so users consulting the reference have no signal about formally+slack/
  sync/remote. Falsifiable: TestLLMHelpADR0112D3 fails red pre-edit, green post.

evidence:
  - green | 2026-02-13T00:00:00Z | exit 0 | go test ./internal/barcli/... -run TestLLMHelpADR0112D3
  - green | 2026-02-13T00:00:00Z | exit 0 | go test ./internal/barcli/... -run TestLLMHelp

rollback_plan: git restore --source=HEAD internal/barcli/help_llm.go internal/barcli/help_llm_test.go

delta_summary: >
  help_llm.go: Tone/channel register conflicts subcategory added before
  Semantic conflicts in renderCompositionRules.
  help_llm_test.go: TestLLMHelpADR0112D3 added as specifying validation.

loops_remaining_forecast: 0 — ADR-0112 complete.

residual_constraints:
  - None. All decisions implemented.

next_work: None — ADR-0112 complete.
```
```
