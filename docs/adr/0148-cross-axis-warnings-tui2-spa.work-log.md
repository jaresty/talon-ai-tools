# ADR-0148 Work Log: Cross-Axis Composition Warnings in TUI2 and SPA

EVIDENCE_ROOT: docs/adr/evidence/0148
ARTEFACT_LOG: docs/adr/evidence/0148/loop-N.md
VCS_REVERT: git restore --source=HEAD

---

## Loop 1 — Phase 1a: Coverage expansion data (2026-02-27)

```yaml
helper_version: helper:v20251223.1
focus: >
  ADR-0148 Phase 1a — Add Tier 1 + Tier 2 entries to CROSS_AXIS_COMPOSITION in
  lib/axisConfig.py; run make bar-grammar-update; verify renderCrossAxisComposition
  picks up new entries via dev binary.
active_constraint: >
  CROSS_AXIS_COMPOSITION has no entries for presenterm, html.task, adr.completeness,
  codetour.audience, gherkin.completeness, or sync.task — the Tier 1/2 tokens required
  by ADR-0148 Part D. The constraint is falsifiable: `go build -o /tmp/bar-new
  ./cmd/bar/main.go && /tmp/bar-new help llm | grep presenterm` exits 0 but produces no
  output. Alternative candidate: implement TUI2 display first (Phase 1b) — lower
  expected value because display code is only useful once data exists; data is a strict
  prerequisite. EV: Impact=H (all three surfaces need the data), Probability=H
  (deterministic add), TimeSensitivity=H (blocks Phases 1b, 1c, 2). Product=27.
validation_targets:
  - T-1a: go build -o /tmp/bar-new ./cmd/bar/main.go && /tmp/bar-new help llm | grep -A5 presenterm
  - T-1b: go test ./internal/barcli/ -run TestLLMHelp (regression guard)
evidence:
  - red   | 2026-02-27T00:00:00Z | exit 0 but empty output | /tmp/bar-new help llm | grep presenterm
      helper:diff-snapshot=0 files changed
      presenterm not in CROSS_AXIS_COMPOSITION; grep returns empty | inline
  - green | see evidence/0148/loop-1.md
rollback_plan: git restore --source=HEAD lib/axisConfig.py; go build -o /tmp/bar-new ./cmd/bar/main.go && /tmp/bar-new help llm | grep presenterm  (should return empty again)
delta_summary: >
  Added adr.task.cautionary(sim), adr.completeness, codetour.audience,
  gherkin.completeness, sync.task (Tier 1) and presenterm.task, presenterm.completeness,
  html.task (Tier 2) to CROSS_AXIS_COMPOSITION. make bar-grammar-update regenerated
  all grammar JSON artefacts. Rung: data added → grammar regenerated → dev binary
  verified.
loops_remaining_forecast: >
  4 loops remaining: 1b (TUI2 meta sections), 1c (TUI2 chip prefix),
  2 (SPA + prose cleanup). Confidence: high — each loop has clear scope and
  established validation paths.
residual_constraints:
  - TUI2 display (Phase 1b): not started; data now available. Severity: M.
      Monitoring: addressed in Loop 2.
  - SPA display (Phase 2): not started; blocked on Phase 1b. Severity: M.
  - Prose cleanup (Part C): not started; blocked on Phase 2 meta panel rendering
      being verified. Severity: L. Monitoring: addressed in Loop 4.
next_work:
  - Behaviour T-1b: TUI2 always-on meta sections for channel/form tokens (Phase 1b).
      Validation: extend TUI2 smoke fixture and run go test ./internal/barcli/ -run TestTUI2Smoke.
```
