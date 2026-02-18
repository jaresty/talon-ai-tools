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

## loop-11 | 2026-02-18 | Cycle 11: Channel post-apply validation + completeness axis discoverability

```
focus: Part A — post-apply validation of loop-10 channel discoverability fixes (T188 sync,
  T189 sketch, T190 plain, T193 remote). Part B — completeness axis discoverability
  (gist, max, minimal, deep, skim — 5 tasks T196-T200).

active_constraint: >
  AXIS_KEY_TO_USE_WHEN has no completeness axis entries (0 of 7 tokens covered).
  gist and skim are undiscoverable for common "brief/quick/overview" and "light review"
  phrasings — autopilot defaults to full. No SSOT regression observed this loop.

validation_targets:
  - Part A: mean post-fix score ≥ 4.0 (target: all 4 gapped tasks ≥ 4)
  - Part B: completeness axis mean score (3.6 observed — below 4.0 target)

evidence:
  - Part A | 2026-02-18 | post-apply validation
      T188 sync: 3 → 4 (+1) PASS — "session plan" heuristic fires
      T189 sketch: 3 → 4 (+1) PASS — "D2 diagram" heuristic fires
      T190 plain: 3 → 5 (+2) PASS — "no bullets/plain prose" fires (strongest fix)
      T193 remote: 3 → 4 (+1) BORDERLINE PASS — "distributed session" fires; note preserved
      Mean: 3.0 → 4.25 ✅
  - Part B | 2026-02-18 | completeness axis evaluation
      T196 (gist/quick overview): score 3 — gapped (no use_when, autopilot defaults to full)
      T197 (max/exhaustive docs): score 4 — "exhaustive" word-for-word in description
      T198 (minimal/smallest change): score 4 — semi-self-naming
      T199 (deep/deep dive): score 5 — self-naming
      T200 (gist vs skim/standup brief): score 2 — gapped (ambiguous; full as default)
      Mean: 3.6/5 ⚠️ (below 4.0 target)

delta_summary: >
  Evaluation only — no catalog changes applied this loop.
  Loop-10 fixes confirmed landing (Part A).
  Completeness axis gaps identified (Part B): gist, skim, narrow (3 recs).
  Evidence files created:
    docs/adr/evidence/0113/loop-11/evaluations.md
    docs/adr/evidence/0113/loop-11/recommendations.yaml
    docs/adr/evidence/0113/loop-11/loop-11-summary.md

residual_constraints:
  - id: RC-L11-01
    constraint: >
      AXIS_KEY_TO_USE_WHEN has no completeness axis entries. gist and skim are
      undiscoverable for "quick/brief/overview" and "light review/spot check" phrasings.
      narrow has no known routing path at all.
    severity: Medium (gist/skim), Low (narrow)
    mitigation: Apply R-L11-01 (gist use_when), R-L11-02 (skim use_when), R-L11-03 (narrow use_when)
  - id: RC-L11-02
    constraint: >
      T193 (remote + retrospective) is a borderline pass. A second usage pattern
      (remote + facilitate) would strengthen the routing signal beyond the use_when alone.
    severity: Low
    mitigation: Add usage pattern in loop-12 apply step

next_work:
  - Apply R-L11-01, R-L11-02, R-L11-03: add completeness use_when entries to axisConfig.py
    (check git diff before running make bar-grammar-update — SSOT regression risk)
  - Post-apply validate: re-test T196 and T200 after completeness use_when added
  - Scope axis discoverability (0 of 13 tokens have use_when) — candidate for loop-13

apply:
  date: 2026-02-18
  changes:
    - R-L11-01: Added gist use_when to AXIS_KEY_TO_USE_WHEN["completeness"] in lib/axisConfig.py
    - R-L11-02: Added skim use_when to AXIS_KEY_TO_USE_WHEN["completeness"] in lib/axisConfig.py
    - R-L11-03: Added narrow use_when to AXIS_KEY_TO_USE_WHEN["completeness"] in lib/axisConfig.py
  grammar_regen: make bar-grammar-update (exit 0)
  ssot_check: AXIS_KEY_TO_USE_WHEN intact after regen (no regression)
  tests: go test ./internal/barcli/ — ok (1.446s)
  verification: /tmp/bar-new help llm | grep gist/skim/narrow → When to use columns render correctly
```

---

## loop-12 | 2026-02-18 | Cycle 12: Completeness post-apply + scope axis discoverability + apply

```
focus: Part A — post-apply validation of loop-11 completeness fixes (T196 gist, T200 gist).
  Part B — scope axis discoverability (10 tasks T201-T210, 13 scope tokens).
  Apply — 6 scope use_when entries added immediately after evaluation.

active_constraint: >
  AXIS_KEY_TO_USE_WHEN had 0 of 13 scope tokens covered. Method tokens preempt scope
  tokens during selection — "recurring patterns" → mapping/cluster instead of motifs,
  "flows through" → flow method instead of time scope, "who decides" → actors method
  instead of agent scope. No SSOT regression observed this loop.

evidence:
  - Part A: T196 gist 3→4 PASS; T200 gist 2→4 PASS. Mean 2.5→4.0 ✅
  - Part B scope axis: T201(fail)=5, T202(struct)=4, T203(mean)=4, T204(time)=3,
      T205(agent)=2, T206(assume)=3, T207(motifs)=2, T208(good)=3, T209(view)=4,
      T210(stable)=2. Mean 3.2/5 ⚠️

delta_summary: >
  6 scope use_when entries added to AXIS_KEY_TO_USE_WHEN["scope"] in lib/axisConfig.py:
    R-L12-01: time — "step by step", "timeline", "sequence", "phases"
    R-L12-02: agent — "who decides", "who has authority"; distinguishes from actors method
    R-L12-03: assume — "what assumptions", "what must be true"
    R-L12-04: motifs — "recurring patterns", "appears in multiple places"
    R-L12-05: good — "quality criteria", "what makes it good", "success criteria"
    R-L12-06: stable — "stable", "unlikely to change", "what persists"
  Grammar regenerated. Tests: ok (1.434s). SSOT intact.

residual_constraints:
  - id: RC-L12-01
    constraint: Method axis 51 tokens, 0 use_when entries — largest remaining gap.
    severity: High (volume), Medium (per-token)
    mitigation: Candidate for loop-14+ after scope post-apply validation (loop-13).

next_work:
  - Post-apply validate loop-12 scope fixes: re-test T204, T205, T207, T210
  - Method axis use_when coverage — 51 tokens, 0 covered; needs sampling strategy
```

---

## loop-13 | 2026-02-18 | Cycle 13: Scope post-apply + method axis (metaphorical tokens) + apply

```
focus: Part A — post-apply validation of loop-12 scope fixes (T204 time, T205 agent,
  T207 motifs, T210 stable). Part B — method axis discoverability sampling (10 tasks
  T211-T220), focusing on metaphorical token names (boom, grove, melody, grow).
  Apply — 4 method use_when entries added same loop.

active_constraint: >
  Method axis: 0 of 51 tokens had use_when entries. Metaphorical names (boom, grove,
  melody, grow, meld, mod, field, shift) have no routing path — unlike scope tokens
  (which were preempted by methods), these have no competing token absorbing them;
  they're simply invisible. No SSOT regression observed this loop.

evidence:
  - Part A: T204(time) 3→4 PASS; T205(agent) 2→5 PASS; T207(motifs) 2→5 PASS;
      T210(stable) 2→5 PASS. Mean 2.25→4.75 ✅ (strongest post-apply result yet)
  - Part B: T211(boom)=2, T212(grove)=1, T213(melody)=2, T214(bias)=4, T215(origin)=4,
      T216(simulation)=4, T217(jobs)=4, T218(grow)=2, T219(inversion)=5, T220(systemic)=5.
      Mean 3.3/5 ⚠️ Pattern: metaphorical names invisible; description-anchored discoverable.

delta_summary: >
  4 method use_when entries added to AXIS_KEY_TO_USE_WHEN["method"] in lib/axisConfig.py:
    R-L13-01: boom — "at 10x", "extreme load", "what breaks at scale", "at the limit"
    R-L13-02: grove — "compound", "feedback loop", "snowball", "network effect"
    R-L13-03: melody — "coordinate across teams", "synchronize changes", "coupling"
    R-L13-04: grow — "YAGNI", "start simple and expand", "minimum viable"
  Grammar regenerated. Tests: ok (1.638s). SSOT intact.

residual_constraints:
  - id: RC-L13-01
    constraint: >
      47 of 51 method tokens still have no use_when. Remaining metaphorical tokens
      that likely need use_when: meld, mod, field, shift. Description-anchored tokens
      (compare, diagnose, explore, branch, etc.) are likely fine without.
    severity: Medium (meld/mod/field/shift), Low (description-anchored tokens)

next_work:
  - Post-apply validate T211, T212, T213, T218 (all scored ≤2 pre-fix)
  - Continue method axis: meld, mod, field, shift (remaining metaphorical tokens)
  - Or pivot: task axis (11 tokens, 0 use_when) — smaller scope
```

---

## loop-14 | 2026-02-18 | Cycle 14: Method post-apply + remaining metaphorical tokens + apply

```
focus: Part A — post-apply validation of loop-13 method fixes (T211 boom, T212 grove,
  T213 melody, T218 grow). Part B — remaining metaphorical method tokens: meld, mod,
  field, shift (T221-T224). Apply — 3 use_when entries added (meld, mod, field).

active_constraint: >
  `field` scored 1 (lowest in all 14 loops) — physics-theory vocabulary entirely
  disconnected from software engineering. `shift` scored 4 without use_when —
  "shift perspective" is intuitive enough to self-route. No SSOT regression.

evidence:
  - Part A: T211(boom) 2→4 PASS; T212(grove) 1→4 PASS (+3, largest delta yet);
      T213(melody) 2→4 PASS; T218(grow) 2→5 PASS (+3). Mean 1.75→4.25 ✅
  - Part B: T221(meld)=2, T222(mod)=2, T223(field)=1, T224(shift)=4. Mean 2.25.
      All metaphorical tokens now inventoried and addressed.

delta_summary: >
  3 method use_when entries added to AXIS_KEY_TO_USE_WHEN["method"]:
    R-L14-01: meld — "balance between", "overlap between", "navigate tensions between"
    R-L14-02: mod — "cyclic behavior", "periodic pattern", "repeats across cycles"
    R-L14-03: field — "shared infrastructure", "service mesh routing", "effects propagate"
  Grammar regenerated. Tests: ok (1.688s). SSOT intact.
  All 8 metaphorical method tokens now have use_when (boom, grove, grow, melody,
  meld, mod, field covered; shift scored 4 without needing one).

next_work:
  - Post-apply validate T221, T222, T223 (loop-14 gaps)
  - General health check: 10 diverse cross-axis tasks to verify cumulative improvements
  - Task axis (0/11) and directional axis (0/16) are low priority — self-describing
```

---

## loop-15 | 2026-02-18 | Cycle 15: Method post-apply + general health check

```
focus: Part A — post-apply validation of loop-14 fixes (T221 meld, T222 mod, T223 field).
  Part B — general health check: 10 diverse cross-axis tasks (GH-T01 through GH-T10)
  verifying that cumulative loop-1–14 improvements compose correctly.

evidence:
  - Part A: T221(meld) 2→4 PASS; T222(mod) 2→4 PASS; T223(field) 1→4 PASS (+3).
      Mean 1.67→4.0 ✅. All metaphorical method tokens now routing correctly.
  - Part B: GH-T01=5, GH-T02=5, GH-T03=4, GH-T04=5, GH-T05=5,
      GH-T06=4, GH-T07=4, GH-T08=4, GH-T09=5, GH-T10=4. Mean 4.5/5 ✅
      No new gaps. No regressions. All loop-10–14 fixes verified in combination.
      GH-T01 fires use_when from loops 11+12+13 simultaneously → scores 5.

delta_summary: >
  Evaluation only — no catalog changes this loop. All loop-14 fixes confirmed.
  Program-level conclusion: ADR-0113 primary objective complete. AXIS_KEY_TO_USE_WHEN
  now covers the most impactful undiscoverable tokens across all axes.

residual_constraints:
  - id: RC-L15-01
    constraint: 41 of 51 method tokens have no use_when (Tier 1 / description-anchored).
    severity: Low — no evidence of routing failures for these tokens.
  - id: RC-L15-02
    constraint: SSOT regression risk persists (make axis-regenerate-apply may zero
      AXIS_KEY_TO_USE_WHEN). Last regression: loop-10. Clean since.
    severity: Medium — monitor on every grammar regen.

next_trigger: >
  Re-run ADR-0113 cycle when: new tokens added to catalog, new skill guidance published,
  or user feedback indicates routing failures for a specific task type.
```

---

---

## Loop-16 — 2026-02-18

**Focus:** Fresh health check across uncovered token areas (scope: cross/view/struct/thing; form: contextualise/socratic/variants; channel: diagram/slack/jira)

**Health check (GH16-T01–T10):** Mean 4.3/5. 3 gaps at score 3: cross scope (competes with motifs), contextualise form (LLM-to-LLM description), socratic form (competes with adversarial method).

**Confirmed discoverable without use_when:** struct, view, thing (description-anchored); diagram, slack, jira (explicit channel names).

**Fixes applied:**
- R-L16-01: cross scope use_when — "scattered across", "cross-cutting concern", "appears throughout"
- R-L16-02: contextualise form use_when — "put X in context", "explain why this was chosen"
- R-L16-03: socratic form use_when — "challenge my assumptions with questions", "Socratic dialogue"

**Post-apply:** T02→4, T05→4, T07→4. Mean 3.0→4.0 ✅. Grammar regenerated, tests pass.

**Coverage update:** scope 7/13, form 12/~32.


---

## Loop-17 — 2026-02-18

**Focus:** Form token health check (indirect, case, activities, scaffold, tight, formats) + scope (act, mean) + channel (adr, gherkin)

**Results (mean 4.4/5):** 2 gaps at score 3: indirect form (opaque name, competes with case), activities form (preempted by facilitate use_when).

**Confirmed discoverable without use_when:** act, mean scope; case, scaffold, tight, formats form; adr, gherkin channel.

**Fixes applied:**
- G-L17-01: indirect form use_when — 'walk me through the reasoning first', 'reasoning before conclusion'
- G-L17-02: activities form use_when — 'session activities', 'what happens in each segment', 'design sprint activities'

**Post-apply:** T03→4, T05→4. Coverage: form 14/~32.

