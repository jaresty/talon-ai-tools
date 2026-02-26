# ADR-0085 Cycle 13: R36 Recurrence + New Token Discovery
**Date:** 2026-02-25
**Seeds:** 336–375 (40 prompts)
**Bar version:** 2.64.1
**Focus:** Post-cycle-12 health check, R36 recurrence tracking, R37-watch follow-up

---

## Phase 0: Calibration

**Evaluators:** single-evaluator (Claude Sonnet 4.6)
**Calibration result:** N/A (continuation of established rubric)

---

## Section A: Rapid Evaluation — Seeds 336–375

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 336 | sort | full, thing, converge, svg | scientist_to_analyst | 4 | converge+svg = sorted categories as diagram; coherent |
| 337 | probe | **gist**, activities, svg, **fip-ong** | gently | **2** | **R36: gist+fip-ong** — compound dir cannot be expressed in gist |
| 338 | make | max, act, trade, sync | stakeholder_facilitator | 3 | max+sync tension: exhaustive content vs meeting-agenda format |
| 339 | pull | deep, html, dip | stakeholder_facilitator | 4 | deep+dip+html extraction; coherent |
| 340 | pull | full, formats | audience | 3 | sparse; formats form = extract format options |
| 341 | check | full, agent, deduce, fig | executive_brief | 4 | deductive exec evaluation with fig+full=fine |
| 342 | pick | full, time, robust | formally | 4 | robust time-scope decision; minimal but clean |
| 343 | diff | full, formats | peer_engineer | 4 | compare formats; coherent |
| 344 | check | minimal, fail, unknowns, wasinawa, svg | persuade | 3 | wasinawa (What-So What-Now What) form + svg = form-as-lens required; awkward |
| 345 | probe | full, dimension, cards, adr, dip | fun_mode | 4 | probe findings as ADR with cards form; dip+full=fine |
| 346 | diff | narrow, ladder, fip-bog | teach | 3 | R37-watch confirmed: narrow+fip-bog (3rd compound) = workable but complex |
| 347 | probe | full, log, sync, rog | kindly | 4 | log form in sync; rog=primitive; coherent |
| 348 | pick | **skim**, actors, bug, **fog** | stakeholder_facilitator | **2** | **R36: skim+fog** — fog is multi-phase; listed in skim avoidance |
| 349 | plan | max, view, cards | casually, appreciate | 3 | max+appreciate+casually: exhaustive plan in casual tone is odd |
| 350 | trans | skim, agent, bullets | stakeholder_facilitator | 4 | skim+no-compound=fine; light bullets transformation |
| 351 | show | full | persuade | 3 | very sparse |
| 352 | show | full, act, explore, plain | executive_brief | 4 | exploration for executives; clean |
| 353 | diff | full | casually | 3 | very sparse |
| 354 | pull | gist, agent, canon, case, rog | fun_mode | 4 | gist+rog(primitive)=fine; canonical extraction as case |
| 355 | pull | minimal, good, inversion, direct, gherkin | fun_mode | 4 | inversion+gherkin+fun; playful inversion exercise |
| 356 | sort | full, motifs, depends | teach | 4 | dependency-sorted classification; coherent |
| 357 | trans | full, assume, gap, story, plain | scientist_to_analyst | 4 | gap-finding transformation as user story |
| 358 | check | full, fail, polar | casually | 4 | binary check of failures; clean |
| 359 | sort | full, mean, canon, faq, svg, ong | stakeholder_facilitator | 3 | svg+faq = form-as-lens required; ong=primitive=fine |
| 360 | check | skim, codetour | directly | 4 | skim+no-compound+codetour=fine; minimal check |
| 361 | probe | full, flow | fun_mode | 4 | minimal but clean |
| 362 | show | full, time, gap, faq, code | teach | 3 | code+faq = form-as-lens required; teach+code fine conceptually |
| 363 | check | deep, act, contextualise, plain | fun_mode | 4 | check+contextualise = package for downstream LLM; coherent |
| 364 | diff | full, tight | persuade | 4 | tight diff to persuade; clean |
| 365 | sort | full, operations, fly-ong | voice | 4 | fly-ong+full=fine; operations sort |
| 366 | check | full, struct, grow, ladder | stakeholder_facilitator | 4 | grow+ladder+struct check; coherent |
| 367 | show | minimal, mean, balance, contextualise, fly | coach | 4 | minimal+fly(compound)=fine(minimal≠gist/skim); contextualise+show |
| 368 | pull | full, dip | teach_junior_dev | 3 | sparse; just pull+completeness+directional |
| 369 | plan | full, shift | appreciate | 3 | sparse |
| 370 | pick | full, merge, diagram, dip | stakeholder_facilitator | 4 | merge form as decision diagram; coherent |
| 371 | check | full, time, dip | appreciate | 3 | appreciate intent odd for check task |
| 372 | show | full, agent, adversarial, diagram, fig | executive_brief | 4 | adversarial exec explanation as diagram; fig+full=fine; strong |
| 373 | check | full, recipe | peer_engineer | 4 | check as step-by-step recipe; coherent |
| 374 | pick | deep, mean, resilience, diagram, fip | coach | 4 | fip+deep=fine; resilience decision diagram |
| 375 | make | deep, time, fig | fun_mode | 4 | fig+deep=fine; time-scoped creation |

**Score distribution:**
- 4: 336, 339, 341, 342, 343, 345, 347, 350, 352, 354, 355, 356, 357, 358, 360, 361, 363, 364, 365, 366, 367, 370, 372, 373, 374, 375 (26)
- 3: 338, 340, 344, 346, 349, 351, 353, 359, 362, 368, 369, 371 (12)
- 2: 337, 348 (2)

**Corpus average: 3.60** (identical to cycle 12; 2 R36 seeds pull it down)

---

## Section B: Key Findings

### B1 — Seed 337: gist + fip-ong (R36, third occurrence)

`probe + gist + activities + svg + fip-ong`. Score 2. `fip-ong` = "alternate between abstract and concrete, then identify actions and extend." gist cannot span this multi-phase range. Third R36 gist-hit (cycle-11: fly-ong, cycle-12: fip-ong, cycle-13: fip-ong again). R36 fix in place — guidance documented correctly.

### B2 — Seed 348: skim + fog (R36, fog variant)

`pick + skim + actors + bug + fog`. Score 2. `fog` = "surface abstract patterns and principles." Skim avoidance list explicitly includes fog (carried over from original skim notes, also in updated R36 list). R36 fix correctly covers this. Second skim+fog hit.

### B3 — R37-watch: narrow + compound directional (second confirmation)

Seed 346 = `diff + narrow + ladder + fip-bog`. Score 3. `fip-bog` spans abstract+concrete+reflect+act (4 dimensions). With narrow completeness (restrict to a small slice), the 4-dimensional span is achievable within the restricted slice — not broken, but complex. **Two data points now: seed 326 (narrow+fig=3), seed 346 (narrow+fip-bog=3).** Consistent score 3 pattern.

This is different from R36 (gist/skim+compound = score 2). Narrow restricts topic scope, not output brevity; you can examine a narrow slice from all angles. Low priority but worth adding a note.

**Proposed note for `narrow` in axisConfig.py notes:** Add brief guidance that compound directionals work with narrow but the combination is cognitively demanding — prefer full/deep completeness if multi-dimensional analysis is needed.

Actually: on reflection, this is a "use with awareness" situation, not a "avoid" situation. A user may intentionally want to examine a narrow slice from all angles. Score 3 is appropriate; no mandatory avoidance needed. Keep as R37-watch.

### B4 — New token: `wasinawa`

`wasinawa` (振) = "What–So What–Now What reflection: describes what happened, interprets why it matters, proposes concrete next steps." A structured reflection framework form token. Appears in seed 344 paired with svg channel — requires form-as-content-lens treatment (can't render prose reflection in SVG). Score 3 for the channel mismatch, not the token itself.

Token appears well-defined and coherent. No catalog issue; discovery note only.

### B5 — max + sync tension (seed 338)

`make + max + trade + sync`. Score 3. `max` = "exhaustive, treat omissions as errors." `sync` = "synchronous session plan (agenda, steps, cues)." These pull in opposite directions: sync wants actionable brevity, max demands exhaustive coverage. Neither token's notes warn about this pairing.

**Low-priority recommendation:** Add brief note to `sync` or `max` about this tension. Score 3 (usable but awkward) means low priority.

### B6 — Positive patterns

| Pattern | Seed | Score | Value |
|---------|------|-------|-------|
| show + agent + adversarial + diagram + fig | 372 | 4 | Adversarial executive explanation as diagram |
| check + deep + act + contextualise | 363 | 4 | Check result packaged for downstream LLM |
| pull + gist + agent + canon + case + rog | 354 | 4 | Gist+primitive dir = fine; canonical case extraction |
| pull + minimal + inversion + direct + gherkin | 355 | 4 | Inversion + gherkin = playful structural inversion |
| check + full + struct + grow + ladder | 366 | 4 | Growth check via abstraction laddering |

---

## Section C: Recurring Patterns (Cycle-to-Date)

| Pattern | Cycle 11 | Cycle 12 | Cycle 13 | Action |
|---------|----------|----------|----------|--------|
| gist/skim + compound dir (R36) | 2 hits | 1 hit | 2 hits | Fixed in cycle 11; guidance in place |
| narrow + compound dir (R37-watch) | 1 (seed 326) | — | 1 (seed 346) | Watch; no action yet |
| SVG + structured form | — | — | 2 (344, 359) | Form-as-lens rule handles; no action |
| max + sync tension | — | — | 1 (seed 338) | R38-watch; low priority |
| Sparse/minimal combos | 10 seeds | 14 seeds | 12 seeds | No action; shuffle natural |

---

## Recommendations (Cycle 13)

No immediate catalog changes. R36 guidance is working. Two new watch items.

```yaml
- id: R36-cycle13
  type: post-apply-evidence
  findings:
    - seed_337: gist + fip-ong = 2 (third gist+compound hit)
    - seed_348: skim + fog = 2 (second skim+fog hit)
  fix_applied: cycle-11 (both fip-ong and fog in avoidance lists)
  status: confirmed-working

- id: R37-watch
  type: watch
  pattern: narrow completeness + compound directional
  seeds: [seed_326 (cycle-12, narrow+fig=3), seed_346 (cycle-13, narrow+fip-bog=3)]
  score: 3 (consistently; not score 2)
  reason: >
    narrow restricts topic scope; compound dir spans analytical dimensions within that
    scope. Combination is cognitively demanding but not broken — a user may intentionally
    examine a narrow slice from all angles. Not a mandatory avoidance; keep watching.
  action: none-yet

- id: R38-watch
  type: watch
  pattern: max completeness + sync channel
  seeds: [seed_338 (cycle-13, max+sync=3)]
  score: 3
  reason: >
    max = exhaustive coverage (omissions are errors); sync = meeting-agenda format
    (brevity implied). These pull in opposite directions. One data point only.
  action: none-yet; needs second confirming seed before adding notes
```
