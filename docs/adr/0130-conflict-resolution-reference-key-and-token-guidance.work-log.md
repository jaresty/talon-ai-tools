# ADR-0130 Work Log

**ADR:** 0130-conflict-resolution-reference-key-and-token-guidance
**Helper:** helper:v20251223.1

---

## Loop 1 — 2026-02-16: Layer 1 reference key changes (render.go + metaPromptConfig.py + fixture)

```yaml
helper_version: helper:v20251223.1
focus: >
  ADR-0130 § Layer 1 — Reference Key Changes.
  Extend Form bullet with content-lens demotion rule (R17);
  add specification-channel reframing rule to Precedence block (R18).
  Targets: internal/barcli/render.go, lib/metaPromptConfig.py,
  cmd/bar/testdata/tui_smoke.json (snapshot update).

active_constraint: >
  render.go and metaPromptConfig.py contain updated reference key text but
  the TUI fixture snapshot still embeds the old Form bullet, causing
  TestRunTUIFixtureOutputsSnapshot to fail (exit 1).
  Falsifiable: `go test ./internal/barcli/...` exits non-zero until fixture updated.

validation_targets:
  - go test ./internal/barcli/...

evidence:
  - red  | 2026-02-16T00:00:00Z | exit 1 | go test ./internal/barcli/...
      TestRunTUIFixtureOutputsSnapshot: expected fixture run exit 0, got 1
      snapshot preview mismatch line 30: old Form bullet vs new Form bullet
      with content-lens addition | inline
  - green | 2026-02-16T00:00:01Z | exit 0 | go test ./internal/barcli/...
      All tests pass after updating cmd/bar/testdata/tui_smoke.json | inline

rollback_plan: >
  git restore internal/barcli/render.go lib/metaPromptConfig.py
  cmd/bar/testdata/tui_smoke.json
  Then replay: go test ./internal/barcli/... → expect exit 0 on old snapshot.

delta_summary: >
  helper:diff-snapshot: 4 files changed
  - internal/barcli/render.go: Form bullet extended with content-lens rule;
    new Precedence bullet for specification-channel reframing
  - lib/metaPromptConfig.py: same changes (Python SSOT path)
  - cmd/bar/testdata/tui_smoke.json: fixture snapshot updated to match new text
  - docs/adr/0130-conflict-resolution-reference-key-and-token-guidance.md: ADR created

loops_remaining_forecast: >
  2 loops remaining.
  Loop 2: Layer 2 — AXIS_KEY_TO_GUIDANCE entries in axisConfig.py (R17-R21).
  Loop 3: Layer 2 — help_llm.go prose-form conflicts + gherkin task-affinity docs.
  Confidence: high — changes are additive dict entries with clear content.

residual_constraints:
  - constraint: help_llm.go prose-form conflicts list not yet updated (R17 layer 2)
    severity: M
    mitigation: Loop 3 target
    monitoring: grep "questions.*recipe" help_llm.go; expect log/spike/case/story added
    owning_adr: ADR-0130
  - constraint: axisConfig.py AXIS_KEY_TO_GUIDANCE entries missing for R17-R21 tokens
    severity: M
    mitigation: Loop 2 target
    monitoring: grep for "log.*channel\|spike.*channel\|case.*channel" in axisConfig.py
    owning_adr: ADR-0130

next_work:
  - Behaviour: R17-R21 Layer 2 — AXIS_KEY_TO_GUIDANCE entries
    validation: python -m pytest _tests/ -x (or equivalent Python test)
    artefact: lib/axisConfig.py
  - Behaviour: R17-R18 Layer 2 — help_llm.go documentation updates
    validation: bar help llm | grep -A2 "Prose-form conflicts"
    artefact: internal/barcli/help_llm.go
```

---

## Loop 2 — 2026-02-16: Layer 2 AXIS_KEY_TO_GUIDANCE entries (axisConfig.py + grammar regen)

```yaml
helper_version: helper:v20251223.1
focus: >
  ADR-0130 § Layer 2 — Token Documentation Guidance.
  Add AXIS_KEY_TO_GUIDANCE entries for R17 (log, spike, case, story forms),
  R18 (gherkin channel — strengthened), R19 (codetour channel — audience),
  R20 (commit form — depth conflict), R21 (skim completeness — directional depth).
  Targets: lib/axisConfig.py, internal/barcli/embed/prompt-grammar.json (regen).

active_constraint: >
  AXIS_KEY_TO_GUIDANCE in lib/axisConfig.py lacks entries for log, spike, case,
  story (R17), and strengthened gherkin (R18), codetour audience (R19), commit
  depth (R20), skim directional (R21). These tokens will surface in TUI without
  selection-time warnings, increasing frequency of documented conflict patterns.
  Falsifiable: python3 -m pytest _tests/ exits non-zero if generated axisConfig
  drifts from tracked (regen script enforces canonical format).

validation_targets:
  - python3 -m pytest _tests/ -x -q
  - go test ./internal/barcli/...

evidence:
  - red  | 2026-02-16T00:00:10Z | exit 1 | python3 -m pytest _tests/ -x -q
      test_generated_axis_config_matches_tracked: string line-break formatting
      mismatch — manual edits used different wrapping than regen script | inline
  - green | 2026-02-16T00:00:20Z | exit 0 | python3 -m pytest _tests/ -x -q
      All 1233 tests pass after replacing axisConfig.py with regen-canonical
      output (tmp/axisConfig.generated.py) | inline
  - green | 2026-02-16T00:00:21Z | exit 0 | go test ./internal/barcli/...
      All barcli tests pass (cached) | inline

rollback_plan: >
  git restore lib/axisConfig.py internal/barcli/embed/prompt-grammar.json
  Then replay: python3 -m pytest _tests/ -x -q → expect exit 0 on old axisConfig.

delta_summary: >
  helper:diff-snapshot: 3 files changed
  - lib/axisConfig.py: AXIS_KEY_TO_GUIDANCE additions for R17-R21 (regenerated
    canonical format via scripts/tools/axis_regen_all.py)
  - internal/barcli/embed/prompt-grammar.json: regenerated via python3 -m prompts.export
  - docs/adr/0130 work-log: this entry
  New guidance entries: channel.codetour (audience-affinity), channel.gherkin
  (strengthened task-affinity + R18 reframing note), form.case, form.log,
  form.spike, form.story, form.commit (depth conflict), completeness.skim
  (directional depth tension).

loops_remaining_forecast: >
  1 loop remaining.
  Loop 3: help_llm.go — update § Composition Rules § Prose-form conflicts list
  and § Incompatibilities § Channel task-affinity section.
  Confidence: high.

residual_constraints:
  - constraint: help_llm.go prose-form conflicts list not yet updated
    severity: M
    mitigation: Loop 3 target
    monitoring: bar help llm | grep -A5 "Prose-form conflicts" — expect log/spike/case/story
    owning_adr: ADR-0130

next_work:
  - Behaviour: R17-R18 Layer 2 — help_llm.go documentation updates
    validation: go build ./cmd/bar && bar help llm | grep -c "log\|spike\|case\|story"
    artefact: internal/barcli/help_llm.go
```

---

## Loop 3 — 2026-02-16: Layer 2 help_llm.go documentation (R17-R19)

```yaml
helper_version: helper:v20251223.1
focus: >
  ADR-0130 § Layer 2 — help_llm.go documentation.
  Update § Composition Rules § Task-affinity restrictions: codetour audience-
  affinity (R19), gherkin reframing rule (R18).
  Update § Composition Rules § Prose-output-form conflicts: add log, spike,
  case, story (R17) with individual conflict descriptions.
  Target: internal/barcli/help_llm.go.

active_constraint: >
  help_llm.go prose-output-form conflicts section lists only faq, recipe,
  questions. It lacks log, spike, case, story — the four new conflict forms
  identified in ADR-0085 Cycle 7. Task-affinity section for gherkin does not
  reflect the reframing rule. codetour entry lacks audience-affinity warning.
  Falsifiable: go test ./internal/barcli/... exits non-zero if help_llm tests
  break; /tmp/bar_new help llm | grep "log form" returns empty until fixed.

validation_targets:
  - go test ./internal/barcli/...
  - /tmp/bar_new help llm | grep -c "log form"

evidence:
  - red  | 2026-02-16T00:00:30Z | exit 1 (empty output) | /tmp/bar_new help llm | grep "log form"
      Old binary returns empty — log form not in help output | inline
  - green | 2026-02-16T00:00:40Z | exit 0 | go test ./internal/barcli/...
      All barcli tests pass after help_llm.go edits | inline
  - green | 2026-02-16T00:00:41Z | exit 0 | /tmp/bar_new help llm | grep "log form"
      "- `log` form: work/research log entry..." present in output | inline

rollback_plan: >
  git restore internal/barcli/help_llm.go
  Then replay: go test ./internal/barcli/... → expect exit 0 on old content.

delta_summary: >
  helper:diff-snapshot: 2 files changed
  - internal/barcli/help_llm.go:
    * Task-affinity: codetour gains audience-affinity note (developer only)
    * Task-affinity: gherkin rewritten to reflect reframing rule for analysis tasks
    * Prose-output-form conflicts: section rewritten as bulleted list; adds log,
      spike, case, story alongside existing faq, recipe, questions
  - docs/adr/0130 work-log: this entry

loops_remaining_forecast: >
  0 loops remaining. All ADR-0130 behaviours landed green.
  ADR status should be updated to Accepted.

residual_constraints:
  - constraint: ADR-0131 (reference_key as grammar export field) not yet implemented
    severity: L
    mitigation: Separate ADR; sync risk managed by convention (edit metaPromptConfig.py first)
    monitoring: grep for referenceKeyText in render.go; should eventually be removed
    owning_adr: ADR-0131

next_work:
  - Behaviour: ADR-0130 completion — update ADR status to Accepted
    validation: n/a (documentation-only)
    artefact: docs/adr/0130-conflict-resolution-reference-key-and-token-guidance.md
```
