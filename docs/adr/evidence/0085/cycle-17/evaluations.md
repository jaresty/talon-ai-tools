# ADR-0085 Cycle 17: R36 Recurrence + shellscript/CEO Gap Watch
**Date:** 2026-02-25
**Seeds:** 496–535 (40 prompts)
**Bar version:** 2.64.1
**Focus:** General health check; R37 precision validation; R38 boundary validation; spike+gherkin watch

---

## Section A: Rapid Evaluation — Seeds 496–535

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 496 | make | narrow, sync | as-principal-engineer, coach | 4 | narrow+sync=fine (R37=narrow+compound dir only); creation session plan |
| 497 | sort | full, good, indirect, dip-ong | pm_to_team | 4 | dip-ong+full=fine; indirect sort for PM team |
| 498 | plan | full, html, dip-ong | casually, inform | 3 | dip-ong+full=fine; plan as HTML; casually+html minor tension |
| 499 | make | minimal, html, dip-rog | teach_junior_dev | 4 | dip-rog+minimal=fine (minimal≠gist/skim); teaching creation as HTML |
| 500 | check | full, split, sync | to-analyst | 4 | full+sync=fine; check split into sync agenda |
| 501 | plan | full, assume, story | fun_mode | 3 | story form for plan unusual; assume+story workable |
| 502 | make | max, view, trans(method), shellscript, dig | formally | 3 | trans method + make unusual; max+shellscript ok |
| 503 | diff | full, canon, code, dip-bog | directly, coach | 4 | dip-bog+full=fine; canonical comparison as code |
| 504 | probe | deep, tight, fip-rog | peer_engineer | 4 | fip-rog+deep=fine; tight+deep dense peer probe; coherent |
| 505 | make | full, view, mod, bug, sync, jog | to-XP-enthusiast | 3 | bug+sync=form-as-lens (awkward); mod+make unusual |
| 506 | probe | deep, fail, adr | stakeholder_facilitator | 4 | probe+fail+adr=form-as-lens; failure mode ADR; coherent |
| 507 | plan | deep, act, models | (none) | 3 | sparse |
| 508 | sort | minimal, recipe, fly-ong | scientist_to_analyst | 3 | fly-ong+minimal=fine (minimal≠gist/skim); recipe+sort unusual |
| 509 | sim | deep, fip-rog | coach | 4 | fip-rog+deep=fine; coaching simulation; coherent |
| 510 | plan | skim, time, balance, wasinawa | stakeholder_facilitator | 4 | skim+no-compound=fine; wasinawa+balance+time planning; coherent |
| 511 | probe | full, domains | fun_mode | 4 | domains+probe; casual domain boundary exploration; clean |
| 512 | pull | full, agent, grow, indirect, codetour | as-scientist | 3 | codetour+indirect=form-as-lens; grow+pull subtle tension |
| 513 | show | full, activities, plain, fog | executive_brief (to-CEO) | 4 | fog+full=fine; activities+plain=form-as-lens; abstract CEO show |
| 514 | pick | skim | to-junior-engineer, gently, coach | 3 | sparse |
| 515 | make | full, mean, faq, adr, fip-ong | peer_engineer | 3 | faq+adr=form-as-lens unusual; fip-ong+full=fine; workable |
| 516 | plan | narrow, abduce, test | as-principal-engineer, announce | 4 | narrow+no-compound=fine; abduce+test+plan: hypothesis-testing plan |
| 517 | sort | deep | pm_to_team | 3 | sparse |
| 518 | check | deep, fail, grove, rog | (none) | 4 | grove+fail+check: compounding failures; rog+deep=fine; coherent |
| 519 | probe | full, risks, cocreate, svg, fig | teach_junior_dev | 3 | fig+full=fine; cocreate+svg=form-as-lens (svg for risks unusual) |
| 520 | sim | full, agent, unknowns, cards | to-stakeholders, kindly | 4 | unknowns+agent+cards+sim; stakeholder uncertainty simulation; coherent |
| 521 | show | full, shellscript, fip-rog | as-facilitator, casually, inform | 3 | fip-rog+full=fine; show+shellscript unusual |
| 522 | make | full, cross, dip-rog | designer_to_PM | 4 | dip-rog+full=fine; cross+make; coherent |
| 523 | probe | gist, view, trans(method), adr | formally, announce | 4 | gist+no-compound=fine; gist probe as brief ADR; coherent |
| 524 | sim | full, prioritize, spike, ong | peer_engineer | 3 | ong+full=fine; spike+sim unusual (research spike ≠ scenario playback) |
| 525 | check | narrow, act, presenterm | to-XP-enthusiast | 4 | narrow+no-compound=fine; narrow check as slides; coherent |
| 526 | diff | narrow, explore, rog | pm_to_team | 4 | narrow+rog=fine (rog=simple dir); explore+diff+narrow; coherent |
| 527 | plan | full, variants | as-Kent-Beck, to-platform-team | 4 | Kent Beck plan variants for platform team; coherent |
| 528 | pick | full, product | stakeholder_facilitator | 4 | product+pick; clean stakeholder decision |
| 529 | sort | full, inversion, cards, code | teach_junior_dev | 3 | cards+code=form-as-lens; inversion+sort workable; code for sort unusual |
| 530 | show | skim, cross, codetour | as-prompt-engineer, to-Kent-Beck, gently | 4 | skim+no-compound=fine; cross+codetour; coherent |
| 531 | probe | minimal, mean, simulation(method), cocreate, shellscript | executive_brief (to-CEO) | **2** | **shellscript + to-CEO**: technical channel + non-technical audience; documentation covers it |
| 532 | probe | full, meld, fip-ong | as-scientist, directly | 4 | fip-ong+full=fine; meld+probe; scientist analysis; coherent |
| 533 | plan | **skim**, grow, **dip-rog** | fun_mode | **2** | **R36**: skim+dip-rog; guidance in place |
| 534 | diff | skim, assume, actors, bug, shellscript | to-designer, teach | 3 | skim+no-compound=fine; shellscript+diff unusual; to-designer not in avoid list |
| 535 | probe | max, assume, triage, socratic, presenterm | peer_engineer | 4 | max+presenterm=fine (defined slide capacity); triage+socratic slides; coherent |

**Score distribution:**
- 4: 496, 497, 499, 500, 503, 504, 506, 509, 510, 511, 513, 516, 518, 520, 522, 523, 525, 526, 527, 528, 530, 532, 535 (23)
- 3: 498, 501, 502, 505, 507, 508, 512, 514, 515, 517, 519, 521, 524, 529, 534 (15)
- 2: 531, 533 (2)

**Corpus average: 3.53** (slight regression from 3.58; 2 score-2 seeds; 15 sparse/3-scoring seeds)

---

## Section B: Key Findings

### B1 — Seed 533: R36 (skim + dip-rog)

`plan + skim + grow + dip-rog + fun_mode`. Score 2. `dip-rog` = compound directional (start with concrete details → examine structure and reflect on patterns). skim cannot express this multi-dimensional range. Cycle-11 fix covers dip-rog explicitly. No new action.

### B2 — Seed 531: shellscript + executive_brief (to-CEO) = score 2

`probe + minimal + mean + simulation + cocreate + shellscript + executive_brief`. Score 2.

`executive_brief` preset = programmer voice + to-CEO audience. `shellscript` guidance: "Avoid with non-technical audiences (to-CEO, to-managers, to-stakeholders, to-team)." The incompatibility IS documented; the grammar doesn't enforce it.

**Critical distinction from story+gherkin (cycle 14):** The story+gherkin fix applied the channel-wins rule — story composed naturally into gherkin via user-value framing. shellscript+CEO has no such rescue: a CEO cannot read shell script output. This is a genuine incompatibility, not a definable composition.

**Current state:** Documentation correct; grammar allows it. Same structural gap as before cycle 14 story+gherkin fix, but with no channel-wins redefinition path. Options:
1. Accept documentation-only coverage (current state)
2. Add shellscript ↔ to-CEO to AxisIncompatibilities (heavier schema work)

One data point. Flag as R40-watch; do not act yet.

### B3 — R37 precision validated (seeds 496, 525, 526)

Three seeds this cycle used narrow without compound directionals:
- Seed 496: narrow + sync → score 4
- Seed 525: narrow + act + presenterm → score 4
- Seed 526: narrow + explore + rog → score 4

R37 note correctly leaves narrow+channel and narrow+simple-directional alone. The "use with awareness" scope is precise.

### B4 — R38 boundary validated (seeds 500, 535)

- Seed 500: full + sync → score 4 (R38 correctly targets max+sync only)
- Seed 535: max + presenterm → score 4 (max+presenterm fine — presenterm has defined capacity up to 12 slides; exhaustive content fills structured slots rather than overloading format)

Both validations confirm R38 fix is correctly scoped.

### B5 — Seed 524: spike + sim tension (R38-generalization watch)

`sim + full + prioritize + spike + ong`. Score 3. spike = research spike (focused question document). sim = scenario playback. The combination is semantically awkward: spike asks "what do we need to learn?" while sim plays out scenarios. Score 3 = usable but strained.

This is a second data point on the spike-as-constraint tension — different from max+spike (seed 495, cycle 16) but same underlying issue: spike's format implies bounded, exploratory inquiry that conflicts with tasks expecting broad execution. Watch.

### B6 — Positive patterns

| Pattern | Seed | Score | Value |
|---------|------|-------|-------|
| probe + deep + tight + fip-rog + peer_engineer | 504 | 4 | Dense multi-directional peer probe |
| probe + deep + fail + adr + stakeholder | 506 | 4 | Failure mode as ADR form-as-lens |
| probe + gist + view + trans(method) + adr | 523 | 4 | Brief probe ADR with staged-transfer method |
| sim + full + agent + unknowns + cards | 520 | 4 | Stakeholder uncertainty simulation as cards |
| check + deep + fail + grove + rog | 518 | 4 | Compounding failure check; grove method excellent |

---

## Section C: Trend Summary (Cycles 14–17)

| Cycle | Seeds | R36 hits | Score-2s | Avg | Change |
|-------|-------|----------|----------|-----|--------|
| 14 | 376–415 | 0 | 1 (story+gherkin → fixed) | 3.70 | R39 applied |
| 15 | 416–455 | 4 (above-average) | 4 | 3.40 | R38 applied |
| 16 | 456–495 | 1 | 1 | 3.58 | R37 applied |
| 17 | 496–535 | 1 (skim+dip-rog) | 2 (R36 + shellscript/CEO) | 3.53 | No change |

R36 floor is 1–4 per cycle. shellscript/CEO is a new watch item not related to R36.

---

## Recommendations (Cycle 17)

```yaml
- id: R36-cycle17
  type: post-apply-evidence
  findings: [seed_533 (skim+dip-rog=2)]
  status: confirmed-working

- id: R40-watch
  type: watch
  pattern: shellscript channel + non-technical audience preset (executive_brief → to-CEO)
  seeds: [seed_531 (cycle-17, score 2)]
  note: >
    shellscript guidance already says "avoid with non-technical audiences (to-CEO...)".
    Documentation is correct. Grammar does not enforce it. No channel-wins redefinition
    is possible (CEO cannot read shell scripts). If a second seed confirms, consider
    adding shellscript ↔ executive_brief to AxisIncompatibilities.

- id: spike-task-tension-watch
  type: watch
  pattern: spike form paired with execution-oriented tasks (sim, pick)
  seeds: [seed_432 (cycle-15, score 3), seed_524 (cycle-17, score 3)]
  note: >
    Two data points: spike+gherkin (cycle-15) and spike+sim (cycle-17), both score 3.
    Spike = bounded research inquiry. It composes awkwardly with tasks that imply
    execution or broad output. A third data point in different tasks would suggest
    a general spike-as-form note about task affinity.

- id: R37-validation
  type: post-apply-validation
  seeds: [seed_496 (narrow+sync=4), seed_525 (narrow+no-dir=4), seed_526 (narrow+rog=4)]
  status: confirmed-precise (note correctly targets compound dirs only)

- id: R38-validation
  type: post-apply-validation
  seeds: [seed_500 (full+sync=4), seed_535 (max+presenterm=4)]
  status: confirmed-precise (max+sync only; max+other-channels fine)
```
