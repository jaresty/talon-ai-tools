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
