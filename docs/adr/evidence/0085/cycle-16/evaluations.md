# ADR-0085 Cycle 16: R37 Confirmed (narrow+compound dir, 3rd hit) + R36 Recurrence
**Date:** 2026-02-25
**Seeds:** 456–495 (40 prompts)
**Bar version:** 2.64.1
**Focus:** General health check; R37-watch follow-up (narrow + compound directional); spike+gherkin watch

---

## Section A: Rapid Evaluation — Seeds 456–495

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 456 | trans | full, field | stakeholder_facilitator | 3 | field+trans: abstract method; sparse |
| 457 | diff | minimal, thing, actors, contextualise, svg | as-PM | 3 | contextualise+svg=form-as-lens; minimal+contextualise minor tension |
| 458 | trans | skim, afford, contextualise, shellscript | teach_junior_dev | 3 | skim+no-compound=fine; contextualise+shellscript=form-as-lens |
| 459 | pull | full, time, rigor, presenterm, fly-ong | to-principal-engineer, directly | 4 | fly-ong+full=fine; rigor+temporal extraction as slides |
| 460 | trans | gist, assume, checklist, remote | to-team, coach | 4 | gist+no-compound=fine; remote checklist coaching trans |
| 461 | trans | full, view, walkthrough, slack, fly-rog | fun_mode | 4 | fly-rog+full=fine; trans as slack walkthrough |
| 462 | probe | full, walkthrough, sync, fip-rog | to-PM | 3 | fip-rog+full=fine; fip-rog+sync complex but workable |
| 463 | probe | full, fail, mapping, bug, diagram, dip-rog | peer_engineer | 4 | dip-rog+full=fine; failures as bug-framed Mermaid |
| 464 | trans | full, view, walkthrough | to-platform-team, formally | 4 | clean; transformation walkthrough for platform team |
| 465 | check | full, depends, jira, fly-bog | fun_mode | 4 | fly-bog+full=fine; dependency check in Jira format |
| 466 | sort | **narrow**, **fig** | as-programmer, appreciate | 3 | **R37 third data point**: narrow+fig=3; guidance applied |
| 467 | pick | full | peer_engineer | 3 | sparse |
| 468 | plan | max, assume, objectivity, code, rog | teach_junior_dev | 3 | max+code plan unusual; objectivity+assume coherent |
| 469 | show | full, sketch, fly-rog | to-stakeholders, casually | 3 | fly-rog+full=fine; show as D2 unusual |
| 470 | trans | full, inversion, jira | stakeholder_facilitator | 4 | inversion+trans+jira; coherent |
| 471 | plan | full, time | to-PM, teach | 3 | sparse |
| 472 | pick | full, mean, objectivity | designer_to_PM | 4 | objectivity+pick+mean: rigorous conceptual decision |
| 473 | trans | gist, act, merge | gently, coach | 4 | gist+no-compound=fine; trans as merge with coaching tone |
| 474 | pick | **skim**, unknowns, faq, **fip-rog** | peer_engineer | **2** | **R36**: skim+fip-rog; guidance in place |
| 475 | plan | gist, models, activities, html | to-managers, appreciate | 3 | gist+no-compound=fine; activities+html=form-as-lens |
| 476 | plan | full, assume, verify, fly-ong | stakeholder_facilitator | 4 | fly-ong+full=fine; verify+assume planning; coherent |
| 477 | plan | full, motifs, triage, spike, ong | pm_to_team | 4 | spike+ong+triage; PM research spike for recurring patterns; coherent |
| 478 | plan | full, time, sync | kindly, appreciate | 4 | full+sync=fine (R38=max+sync only); time-scoped session plan |
| 479 | check | skim, cocreate, plain | teach_junior_dev | 4 | skim+no-compound=fine; cocreate+plain=content lens |
| 480 | diff | full, plain | as-Kent-Beck, to-XP-enthusiast, gently, persuade | 4 | clean; Kent Beck diff for XP enthusiasts |
| 481 | make | full, split | fun_mode | 3 | sparse |
| 482 | show | full, variants, sketch, jog | gently | 3 | variants+sketch=multiple D2 unusual; jog+full fine |
| 483 | trans | minimal, systemic, bog | fun_mode | 4 | bog+minimal=fine (minimal≠gist/skim); systemic trans |
| 484 | trans | full, assume, melody | as-PM | 3 | melody+trans: metaphorical method; sparse |
| 485 | trans | full, cross, mapping, jira | as-prompt-engineer, to-team, directly, teach | 4 | cross+mapping+jira: cross-concern mapping as Jira; coherent |
| 486 | plan | full, origin, case, dip-ong | stakeholder_facilitator | 4 | dip-ong+full=fine; origin+case+plan for stakeholders |
| 487 | trans | full, explore, variants, presenterm | to-stakeholders | 4 | explore+variants+presenterm: transformation alternatives as slides |
| 488 | trans | full, time, inversion, merge, slack | scientist_to_analyst | 4 | inversion+merge+slack=form-as-lens; coherent |
| 489 | pick | full, triage, rog | to-Kent-Beck, gently | 4 | triage+pick+rog; rog+full=fine; coherent |
| 490 | sim | minimal, fail, diagnose, fly-rog | teach_junior_dev | 4 | fly-rog+minimal=fine (minimal≠gist/skim); diagnostic failure sim |
| 491 | probe | full, cocreate, gherkin, fip-rog | as-writer, appreciate | 4 | fip-rog+full=fine; gherkin+cocreate=form-as-lens; coherent |
| 492 | plan | full, gherkin, dip-bog | teach_junior_dev | 4 | dip-bog+full=fine; plan as Gherkin |
| 493 | pick | full, gherkin | casually, coach | 3 | casually+gherkin minor tension (Gherkin is formal spec format) |
| 494 | diff | full, cluster, html, dip-rog | peer_engineer | 4 | dip-rog+full=fine; cluster+html diff |
| 495 | sort | max, analog, spike | fun_mode | 3 | max+spike tension: exhaustive spike conflicts with time-boxed nature |

**Score distribution:**
- 4: 459, 460, 461, 463, 464, 465, 470, 472, 473, 476, 477, 478, 479, 480, 483, 485, 486, 487, 488, 489, 490, 491, 492, 494 (24)
- 3: 456, 457, 458, 462, 466, 467, 468, 469, 471, 475, 481, 482, 484, 493, 495 (15)
- 2: 474 (1)

**Corpus average: 3.58** (slight regression from 3.70; one R36 hit + 15 sparse/3-scoring seeds)

---

## Section B: Key Findings

### B1 — Seed 474: R36 (skim + fip-rog)

`pick + skim + unknowns + faq + fip-rog`. Score 2. `fip-rog` = compound directional requiring multi-phase traversal (abstract → concrete → structural). skim cannot express this range. Fix from cycle-11 covers fip-rog explicitly. No new action.

### B2 — R37 Confirmed: narrow + compound directional (third data point → fix applied)

Seed 466 = `sort + narrow + fig + as-programmer + appreciate`. Score 3. Third hit:

| Seed | Pattern | Cycle | Score |
|------|---------|-------|-------|
| 326 | narrow + fig | 12 | 3 |
| 346 | narrow + fip-bog | 13 | 3 |
| 466 | narrow + fig | 16 | 3 |

Three consistent data points all at score 3. Pattern is clear: narrow restricts topic scope; compound directionals span multiple analytical dimensions within that restricted scope — cognitively demanding but not broken (unlike R36 where gist/skim = score 2 because brevity prevents expressing the full directional range).

**Root cause:** narrow = "restrict to a small slice" (topic scope modifier); compound directionals = "examine along multiple axes" (analytical range modifier). Pairing them produces a constrained-topic multi-angle examination that is valid but expensive to execute. Score 3 is appropriate.

**Fix applied:** Added `narrow` entry to `AXIS_KEY_TO_GUIDANCE["completeness"]`:
> "Restricts discussion to a small topic slice. Compound directionals work with narrow but the combination examines the slice from multiple analytical dimensions simultaneously — cognitively demanding. If multi-dimensional analysis is the goal, prefer full or deep completeness so the directional can range freely."

**Important distinction from R36:** This is NOT an avoidance rule — it's a "use with awareness" note. Users may intentionally want narrow+compound for focused multi-angle examination.

### B3 — Seed 495: max + spike (R38 generalization watch)

`sort + max + analog + spike`. Score 3. `max` = exhaustive; `spike` = research spike (time-boxed inquiry with focused questions). Spike form has inherent brevity implied by its purpose (scoped investigation, not comprehensive survey). Like max+sync, max+spike pull in opposite directions.

**Note:** This is a form token (spike), not a channel token. R38 fix covered max+sync (channel). This suggests a broader pattern: max + any brevity-constrained output type. One data point for now.

### B4 — Seed 478: full + sync validated (R38 fix working correctly)

`plan + full + time + sync`. Score 4. R38 fix correctly targets only max+sync, not full+sync. full+sync = fine (practical session plan with normal coverage). The fix is narrowly scoped as intended.

### B5 — Positive patterns

| Pattern | Seed | Score | Value |
|---------|------|-------|-------|
| probe + full + cocreate + gherkin + fip-rog | 491 | 4 | gherkin+cocreate = form-as-lens; fip-rog+full fine |
| plan + full + motifs + triage + spike + ong | 477 | 4 | PM research spike with triage; rich coherent combo |
| trans + full + explore + variants + presenterm | 487 | 4 | Transformation alternatives survey as slides |
| plan + full + origin + case + dip-ong | 486 | 4 | Origin-based case planning with compound dir |
| diff + full + plain + as-Kent-Beck + to-XP-enthusiast | 480 | 4 | Expert-to-expert diff with strong persona alignment |

---

## Section C: Trend Summary (Cycles 12–16)

| Cycle | Seeds | R36 hits | Score-2s | Avg | Change |
|-------|-------|----------|----------|-----|--------|
| 12 | 296–335 | 1 (gist+fip-ong) | 1 | 3.60 | Validation |
| 13 | 336–375 | 2 (fip-ong, fog) | 2 | 3.60 | No change |
| 14 | 376–415 | 0 | 1 (story+gherkin) | 3.70 | R39 fix applied |
| 15 | 416–455 | 4 (above-average) | 4 | 3.40 | R38 fix applied |
| 16 | 456–495 | 1 (skim+fip-rog) | 1 | 3.58 | R37 fix applied |

R36 floor is 0–4 hits per 40 seeds; 1 this cycle is normal. Average 3.58 continues the 3.40–3.70 band. Sparse combos (15 this cycle) drive the floor.

---

## Recommendations (Cycle 16)

```yaml
- id: R37
  action: edit-notes
  tokens: [narrow]
  target: lib/axisConfig.py
  status: ✅ Applied
  evidence: [seed_326 (cycle-12), seed_346 (cycle-13), seed_466 (cycle-16)]
  note: >
    Three data points, consistent score 3. narrow + compound directional = valid
    but cognitively demanding (narrow restricts topic; compound spans analytical
    dimensions within it). "Use with awareness" note added — not a mandatory
    avoidance rule. Full/deep completeness recommended when multi-dimensional
    analysis is the primary goal.

- id: R36-cycle16
  type: post-apply-evidence
  findings: [seed_474 (skim+fip-rog=2)]
  status: confirmed-working

- id: R38-generalization-watch
  type: watch
  pattern: max completeness + brevity-constrained form tokens (not just channels)
  seeds: [seed_495 (max+spike=3)]
  note: >
    R38 fix covered max+sync (channel). Seed 495 suggests max+spike (form) follows
    the same logic: spike = time-boxed inquiry; max = exhaustive. One data point.
    Watch for max + [spike, commit] combinations. If confirmed, add note to spike
    and max guidance.

- id: spike-gherkin-watch
  type: watch
  pattern: spike form + gherkin channel
  seeds: [seed_432 (cycle-15, score 3)]
  status: no new data this cycle
```
