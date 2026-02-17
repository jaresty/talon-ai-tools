# Work Log — ADR-0113 Task-Gap-Driven Catalog Refinement

Sibling work-log for `0113-task-gap-driven-catalog-refinement.md`.
Evidence details under `docs/adr/evidence/0113/`.
VCS_REVERT: `git restore --source=HEAD` (file-targeted) or `git stash` (full).

---

## loop-1 | 2026-02-14 | Cycle 1: Task-gap analysis + 11 recommendations applied

```
helper_version: helper:v20251223.1
focus: ADR-0113 §Phase 1–5 (all phases); cycle 1 task-taxonomy → evaluation → gap-catalog → recommendations → implementation.
  Slice scope: run the full ADR-0113 cycle, apply all 11 recommendations, add specifying validation tests.

active_constraint: >
  The bar catalog has no `cross` scope token, so cross-cutting-concern analysis tasks
  (T07) cannot route to an appropriate scope token and score 3/5 for token fitness.
  Falsifiable: `go test ./internal/barcli/ -run TestCrossTokenExistsInGrammar` exits 1
  on the pre-change grammar.
  Expected value:
    Impact:          High  — gap blocked entire cross-cutting use-case class
    Probability:     High  — deterministic; token simply absent from grammar
    Time Sensitivity: Medium — no hard deadline, but catalog debt compounds across loops
    Uncertainty note: None; gap was directly observed and reproduced in evaluation

validation_targets:
  - go test ./internal/barcli/ -run "TestPersonaSlugNormalization|TestCrossTokenExistsInGrammar" -v
    # specifying validation — encodes two new correctness expectations introduced this loop:
    # (1) persona slug de-slugification in Build() (R-10)
    # (2) 'cross' scope token present in grammar (R-01)

evidence:
  - red | 2026-02-14T01:39:20Z | exit 1
      command: go test ./internal/barcli/ -run "TestPersonaSlugNormalization|TestCrossTokenExistsInGrammar" -v
      helper:diff-snapshot: 0 files changed (baseline; all cycle-1 changes stashed via git stash)
      wip-preserve: docs/adr/evidence/0113/loop-1-wip.patch (sha256: 5c7fda65849606c05aba22e081a10fc5b42a69260689ec3c705e62d85443125c)
      failure excerpt:
        FAIL: TestPersonaSlugNormalization — "expected slug-form audience token 'to-product-manager'
          to be accepted, got error: unrecognized token for audience: \"to-product-manager\""
        FAIL: TestCrossTokenExistsInGrammar — "expected 'cross' scope token in grammar (R-01, ADR-0113 cycle 1)"
      pointer: docs/adr/evidence/0113/loop-1.md#red-evidence

  - green | 2026-02-14T01:39:33Z | exit 0
      command: go test ./internal/barcli/ -run "TestPersonaSlugNormalization|TestCrossTokenExistsInGrammar" -v
      helper:diff-snapshot: 8 files changed, 208 insertions(+), 18 deletions(-)
        build/prompt-grammar.json | 18 +++++++++-
        cmd/bar/testdata/grammar.json | 18 +++++++++-
        docs/adr/0113-task-gap-driven-catalog-refinement.md | 38 ++++++++++++++++++
        internal/barcli/build.go | 33 ++++++++++++----
        internal/barcli/build_test.go | 31 +++++++++++++++
        internal/barcli/embed/prompt-grammar.json | 18 +++++++++-
        internal/barcli/help_llm.go | 46 +++++++++++++++++++---
        lib/axisConfig.py | 24 +++++++++++
      pointer: docs/adr/evidence/0113/loop-1.md#green-evidence

  - removal | 2026-02-14T01:39:45Z | exit 1
      command: git restore --source=HEAD -- internal/barcli/build.go internal/barcli/embed/prompt-grammar.json cmd/bar/testdata/grammar.json build/prompt-grammar.json && go test ./internal/barcli/ -run "TestPersonaSlugNormalization|TestCrossTokenExistsInGrammar" -v
      helper:diff-snapshot: 0 files changed (implementation files reverted; test file retained)
      failure excerpt:
        FAIL: TestPersonaSlugNormalization — "expected slug-form audience token 'to-product-manager'
          to be accepted, got error: unrecognized token for audience: \"to-product-manager\""
        FAIL: TestCrossTokenExistsInGrammar — "expected 'cross' scope token in grammar (R-01, ADR-0113 cycle 1)"
      pointer: docs/adr/evidence/0113/loop-1.md#removal-evidence

rollback_plan: >
  git restore --source=HEAD -- internal/barcli/build.go internal/barcli/embed/prompt-grammar.json
    cmd/bar/testdata/grammar.json build/prompt-grammar.json lib/axisConfig.py internal/barcli/help_llm.go
  Then re-run specifying validation to confirm it returns red (exit 1).

delta_summary: >
  helper:diff-snapshot: 8 files changed, 208 insertions(+), 18 deletions(-)
  Cycle 1 applied all 11 recommendations from the task-gap analysis (R-01 through R-11):
    R-01: Added 'cross' scope token to lib/axisConfig.py + regenerated grammar JSONs
    R-02: Added inversion method guidance to AXIS_KEY_TO_GUIDANCE (not description — avoids prompt injection)
    R-03: Added actors method guidance to AXIS_KEY_TO_GUIDANCE
    R-04: Split "Risk Assessment" → "Risk Analysis" + new "Risk Extraction" pattern in help_llm.go
    R-05: Updated scaffold heuristic to exclude make+design-artifact tasks
    R-06: Added "Summarisation / Extraction" usage pattern (pull gist mean)
    R-07: Added "Test Coverage Gap Analysis" and "Test Plan Creation" patterns
    R-08: Added "Pre-mortem / Inversion Exercise" pattern
    R-09: Added scope note to renderMetadata() in help_llm.go
    R-10: Fixed persona slug normalization in build.go (canonicalPersonaToken method)
    R-11: Investigated case form hang — confirmed false positive (stdin-reading behavior), closed
  Specifying validation (build_test.go): TestPersonaSlugNormalization + TestCrossTokenExistsInGrammar added.
  Depth-first rung: cycle-1 complete (all 11 recs applied and validated).

loops_remaining_forecast: >
  Estimate: 1–2 loops.
    Loop 2: Cycle 2 task-gap analysis — run taxonomy refresh, evaluate coverage improvements,
      diagnose any residual gaps. Validation: go test ./internal/barcli/
    Loop 3 (if needed): Apply cycle-2 recommendations.
  Confidence: Medium — cycle 1 addressed 7/9 diagnosed gaps; multi-turn out-of-scope gap
    (T30) and scaffold misuse (T10/T19 partially) may require further iteration.

residual_constraints:
  - id: RC-01
    constraint: >
      Scaffold form is still surfaced for make+design-artifact tasks in bar-autopilot skill.
      The help_llm.go heuristic update (R-05) reduces but does not eliminate this path; the
      skill guidance does not yet explicitly warn against scaffold when channel=code/diagram/adr.
    severity: Medium (impact: quality degradation; probability: 30–70%)
    mitigation: Skill guidance update in bar-autopilot/skill.md (both copies) to add
      explicit anti-pattern note. Monitoring trigger: if cycle-2 evaluation still shows
      scaffold misuse on make tasks.
    owning_adr: ADR-0113

  - id: RC-02
    constraint: >
      Multi-turn brainstorming task (T30) is genuinely out of scope for bar's single-turn
      prompt model. The scope note added in R-09 acknowledges this but no `cocreate` form
      entry point is documented for the iterative case.
    severity: Low (impact: minor UX; probability: <30%)
    mitigation: Acceptable deferral; R-09 scope note covers the user-facing case. If a
      future cycle introduces cocreate guidance, revisit.
    owning_adr: ADR-0113

  - id: RC-03
    constraint: >
      bar-autopilot skill.md copies (`.claude/skills/bar-autopilot/skill.md` and
      `internal/barcli/skills/bar-autopilot/skill.md`) were not updated with the new
      usage patterns added in R-04–R-08. Agents using the skill will discover new patterns
      via `bar help llm` (which was updated) but the skill's static guidance is stale.
    severity: Medium (impact: quality degradation for agents not calling bar help llm)
    mitigation: Update skill.md in both locations in loop-2 or dedicated maintenance loop.
    monitoring_trigger: if bar-autopilot generates suboptimal patterns in cycle-2 evaluation.
    owning_adr: ADR-0113

next_work:
  - Behaviour: Cycle 2 coverage verification — confirm that cycle-1 changes lift T07/T08/T10/T12/T16/T18/T19/T22 scores
    Validation: re-run ADR-0113 §Phase 2–4 on a refreshed task sample; target overall score ≥4.0
    Future-shaping: if gaps remain, proceed with R-05 extension (skill.md update for RC-03)
  - Behaviour: bar-autopilot skill.md update (RC-03)
    Validation: go test ./internal/barcli/ (no test-vector for skill content yet; manual evaluation)
    Future-shaping: add skill regression test if skill content becomes machine-checkable
```

---

## loop-10 | 2026-02-17 | Cycle 10: Output channel discoverability + SSOT fix

```
focus: Output channel token discoverability — whether bar-autopilot selects output channels
  correctly for 13 tasks spanning code, docs, visual output, and collaboration.

active_constraint: >
  AXIS_KEY_TO_USE_WHEN in lib/axisConfig.py was empty (SSOT regression, same as loop-9).
  Must be restored before grammar regeneration or use_when data is lost.
  The following channel tokens had no routing heuristic: plain, sync, sketch, remote.

validation_targets:
  - go test ./internal/barcli/ -v (all tests including TestLLMHelpUsagePatternsTokensExist)
  - /tmp/bar-new help llm | grep -E "When to use" (channel use_when visible)

evidence:
  - red | 2026-02-17 | pre-change
      AXIS_KEY_TO_USE_WHEN = {} in working tree despite HEAD having form entries
      No usage patterns for plain or sync channels
      Tasks T188, T189, T190, T193 scored 3/5

  - green | 2026-02-17 | post-change
      command: go test ./internal/barcli/ -v
      result: ok (1.565s)
      changes: 3 files (axisConfig.py, help_llm.go, help_llm_test.go) + grammar regen

delta_summary: >
  5 files changed (lib/axisConfig.py, internal/barcli/help_llm.go,
  internal/barcli/help_llm_test.go + grammar JSONs regenerated):
    R-L10-05: Restored 9 form use_when entries to AXIS_KEY_TO_USE_WHEN (SSOT regression fix)
    R-L10-01: Added plain channel use_when + "Plain Prose Output" usage pattern
    R-L10-02: Added sync channel use_when + "Synchronous Session Plan" usage pattern
    R-L10-03: Added sketch channel use_when (D2 vs Mermaid disambiguation)
    R-L10-04: Added remote channel use_when (delivery-optimization clarification)
  Test list updated: plain, sync added to patternTokens validation list.
  Mean score: 4.15/5 (9 tasks at 5, 4 tasks at 3 pre-fix).

residual_constraints:
  - id: RC-L10-01
    constraint: >
      AXIS_KEY_TO_USE_WHEN has now regressed twice (loop-9 fix, loop-10 same regression).
      The make bar-grammar-update pipeline does not preserve the Python SSOT contents —
      some step (possibly axis-regenerate-apply) zeros the variable. Risk of future regression.
    severity: Medium
    mitigation: Investigate make axis-regenerate-apply target to understand if it overwrites
      axisConfig.py and add a check to prevent zeroing AXIS_KEY_TO_USE_WHEN.

loops_remaining_forecast: >
  Estimate: 1-3 loops.
  Post-apply validation of loop-10 changes (verify channel use_when renders for target tasks).
  Potential future focus: completeness axis (brief/outline/full selection), cross-domain tasks,
  or general health check after all loop 1-10 fixes.
```

---
