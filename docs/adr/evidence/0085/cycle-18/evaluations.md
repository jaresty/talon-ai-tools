# ADR-0085 Cycle 18: Three R36 Hits + shellscript Grammar Gap Confirmed
**Date:** 2026-02-25
**Seeds:** 536–575 (40 prompts)
**Bar version:** 2.64.1
**Focus:** General health check; R40-watch follow-up (shellscript grammar gaps)

---

## Section A: Rapid Evaluation — Seeds 536–575

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 536 | pick | gist, objectivity, log, dig | as-PM, to-team, gently, inform | 3 | gist+dig=fine (simple dir); log+pick unusual |
| 537 | check | minimal, time, triage, case | peer_engineer | 4 | triage+time+case+check; rigorous peer check; coherent |
| 538 | plan | full, commit | stakeholder_facilitator | 3 | commit+plan unusual; full+commit=fine (only deep/max flagged in commit notes) |
| 539 | sim | full, motifs, sync | to-stakeholders, directly, persuade | 4 | full+sync=fine; motifs+sim+sync; persuasive simulation |
| 540 | check | full, good, sync | teach_junior_dev | 4 | full+sync=fine; quality check as sync session for juniors |
| 541 | check | **gist**, adr, **dip-rog** | as-teacher, to-XP-enthusiast, appreciate | **2** | **R36**: gist+dip-rog; guidance in place |
| 542 | diff | full, robust, fly-bog | teach_junior_dev | 4 | fly-bog+full=fine; robust diff for juniors; coherent |
| 543 | sim | gist | kindly | 3 | sparse |
| 544 | diff | full, spec, presenterm | peer_engineer | 4 | spec+diff+presenterm; criteria-based comparison as slides |
| 545 | show | skim, unknowns, code | as-programmer, kindly | 3 | skim+no-compound=fine; show+code=form-as-lens; unusual |
| 546 | show | gist, svg | pm_to_team | 3 | gist+no-compound=fine; show+svg; sparse |
| 547 | diff | full, case, adr, dip-ong | pm_to_team | 4 | dip-ong+full=fine; case+adr=form-as-lens; PM team diff as ADR |
| 548 | make | full, struct, calc, html | as-Kent-Beck, formally | 4 | calc+make+html; Kent Beck computational creation; coherent |
| 549 | sort | full, unknowns, bug, fip-bog | teach_junior_dev | 3 | fip-bog+full=fine; bug+sort unusual |
| 550 | plan | minimal, experimental, adr, fly-rog | as-designer, to-analyst, casually | 4 | fly-rog+minimal=fine (minimal≠gist/skim); experimental plan as ADR |
| 551 | plan | full, struct | executive_brief (to-CEO) | 4 | clean; structural plan for CEO; coherent |
| 552 | check | full, thing, systemic, socratic, html, bog | as-scientist, to-XP-enthusiast, announce | 4 | bog+full=fine; socratic+html=form-as-lens; systemic scientist check |
| 553 | plan | full, operations | fun_mode | 3 | sparse |
| 554 | sort | skim, unknowns, test, sketch | peer_engineer | 3 | skim+no-compound=fine; test+sketch=form-as-lens; unusual |
| 555 | pick | narrow, adr | as-teacher, to-principal-engineer, formally | 4 | narrow+no-compound=fine; pick+narrow+adr; coherent |
| 556 | probe | skim, rigor | pm_to_team | 3 | skim+rigor axis tension (light pass vs disciplined depth); workable |
| 557 | pick | max, struct | as-prompt-engineer, to-programmer, persuade | 4 | max+pick+struct; exhaustive structural decision; coherent |
| 558 | trans | **skim**, act, bias, indirect, **fog** | scientist_to_analyst | **2** | **R36**: skim+fog; guidance in place |
| 559 | plan | deep, cite, gherkin, fly-rog | persuade | 4 | fly-rog+deep=fine; plan as cited Gherkin; persuasive; coherent |
| 560 | sim | full, agent, formats, shellscript, fip-rog | teach_junior_dev | **2** | **shellscript + sim**: narrative task + code channel; documented; grammar gap |
| 561 | diff | full, actions, fip-rog | to-LLM, gently | 4 | fip-rog+full=fine; actions+diff+to-LLM; coherent |
| 562 | show | deep, cross, facilitate, fly-ong | fun_mode, casually | 4 | fly-ong+deep=fine; facilitate+show+cross; fun facilitation |
| 563 | make | full, view, simulation(method), wardley | as-prompt-engineer | 4 | simulation+make+wardley; thought experiment as Wardley Map; coherent |
| 564 | show | full, act, codetour | peer_engineer | 4 | show+act+codetour; action explanation as CodeTour; coherent |
| 565 | probe | full, fail, taxonomy, sketch | peer_engineer | 4 | taxonomy+sketch=form-as-lens; failure taxonomy as D2; coherent |
| 566 | pick | full, mean, mapping | (none) | 3 | sparse |
| 567 | pick | minimal | teach_junior_dev | 3 | sparse |
| 568 | pull | **skim**, jira, **fog** | as-facilitator, to-LLM, kindly | **2** | **R36**: skim+fog; guidance in place |
| 569 | sort | gist, act, bug | teach_junior_dev | 3 | gist+no-compound=fine; bug+sort unusual |
| 570 | make | full, presenterm | as-scientist, to-PM | 4 | make+presenterm; scientist slides for PM; clean |
| 571 | plan | max, direct, plain | designer_to_PM | 4 | max+plain=fine; direct+plain=form-as-lens (lead-first in prose); coherent |
| 572 | plan | full, slack, bog | peer_engineer | 4 | bog+full=fine; plan as Slack; coherent |
| 573 | plan | narrow, probability, adr | as-scientist | 4 | narrow+no-compound=fine; probability+plan+adr; coherent |
| 574 | check | full, actors, diagram, dig | peer_engineer | 4 | dig+full=fine; actors+diagram+check; coherent |
| 575 | sim | max, stable, argue | to-principal-engineer, directly, appreciate | 4 | max+sim=fine (no channel brevity constraint); argue+stable+sim; coherent |

**Score distribution:**
- 4: 537, 539, 540, 542, 544, 547, 548, 550, 551, 552, 555, 557, 559, 561, 562, 563, 564, 565, 570, 571, 572, 573, 574, 575 (24)
- 3: 536, 538, 543, 545, 546, 549, 553, 554, 556, 566, 567, 569 (12)
- 2: 541, 558, 560, 568 (4)

**Corpus average: 3.50** (regression from 3.53; three R36 hits + shellscript/sim drive it)

---

## Section B: Key Findings

### B1 — Three R36 hits (seeds 541, 558, 568) — above-average draw

| Seed | Pattern | Fix in place? |
|------|---------|---------------|
| 541 | gist + dip-rog | ✅ Yes — R36 cycle-11 |
| 558 | skim + fog | ✅ Yes — R36 cycle-11 |
| 568 | skim + fog | ✅ Yes — R36 cycle-11 |

Two skim+fog hits in one cycle. All three covered. Above-average draw; no action needed.

**Running skim+fog totals:** seed 348 (cycle-13), seed 558, seed 568 (cycle-18) = 4 total across the program. All covered; this is a statistically common pattern because fog appears in ~10–15% of shuffles and skim is common.

### B2 — Seed 560: shellscript + sim = score 2 (R40 confirmed, second data point)

`sim + full + agent + formats + shellscript + fip-rog + teach_junior_dev`. Score 2.

shellscript guidance: "Avoid with narrative tasks (sim, probe) and selection tasks (pick, diff, sort) — these don't produce code."

Documentation IS correct. Grammar does not enforce it. This is the second shellscript grammar gap data point:

| Seed | Pattern | Documentation correct? | Grammar enforces? |
|------|---------|----------------------|-------------------|
| 531 (cycle-17) | shellscript + executive_brief (to-CEO) | ✅ Yes | ❌ No |
| 560 (cycle-18) | shellscript + sim | ✅ Yes | ❌ No |

Two consecutive cycles, two different shellscript incompatibilities, both score 2. The documentation is correct for both; the grammar allows both. This pattern suggests grammar-level enforcement of shellscript incompatibilities would eliminate these score-2 seeds entirely.

**Root cause pattern:** shellscript channel has documented incompatibilities for (a) narrative tasks (sim, probe), (b) selection tasks (pick, diff, sort), (c) non-technical audiences. None of these are enforced at grammar level. R40 is now confirmed (2 data points across 2 incompatibility types).

**Recommendation:** Flag for grammar schema work to add shellscript task/audience incompatibilities to AxisIncompatibilities. This is a heavier change than an axisConfig.py note edit — defer to a dedicated grammar-hardening session.

### B3 — Seed 556: skim + rigor cross-axis tension (score 3)

`probe + skim + rigor + pm_to_team`. Score 3. `skim` = completeness (light pass, surface only). `rigor` = method (disciplined, well-justified reasoning). These are on different axes but semantically conflict: a rigorous light pass is an oxymoron. However, skim constrains output VOLUME while rigor shapes the METHOD within that constraint — you can be rigorous about the subset you do cover. Score 3 is appropriate. One data point; no action.

### B4 — Seed 575: max + sim validated as fine

`sim + max + stable + argue`. Score 4. Unlike max+sync (R38), max+sim has no brevity constraint — simulations can be exhaustive. R38 is correctly scoped to max+sync (session plan channel) only.

### B5 — Positive patterns

| Pattern | Seed | Score | Value |
|---------|------|-------|-------|
| sim + full + motifs + sync + persuade | 539 | 4 | Persuasive motif simulation as session plan |
| check + full + systemic + socratic + html + bog | 552 | 4 | Socratic HTML systemic check |
| make + full + view + simulation(method) + wardley | 563 | 4 | Thought experiment Wardley creation |
| probe + full + fail + taxonomy + sketch | 565 | 4 | Failure taxonomy as D2 diagram |
| plan + deep + cite + gherkin + fly-rog | 559 | 4 | Cited persuasive Gherkin plan |

---

## Section C: Trend Summary (Cycles 15–18)

| Cycle | Seeds | R36 hits | Score-2s | Avg | Change |
|-------|-------|----------|----------|-----|--------|
| 15 | 416–455 | 4 | 4 | 3.40 | R38 applied |
| 16 | 456–495 | 1 | 1 | 3.58 | R37 applied |
| 17 | 496–535 | 1 | 2 | 3.53 | No change |
| 18 | 536–575 | 3 | 4 | 3.50 | No change |

Score-2 seeds are running at 1–4 per cycle. The stable source of non-R36 score-2s is shellscript grammar gaps (2 in 2 cycles). Grammar enforcement of shellscript incompatibilities would eliminate these.

---

## Recommendations (Cycle 18)

```yaml
- id: R36-cycle18
  type: post-apply-evidence
  findings: [seed_541 (gist+dip-rog=2), seed_558 (skim+fog=2), seed_568 (skim+fog=2)]
  status: confirmed-working

- id: R40
  status: confirmed (2 data points)
  pattern: shellscript channel + documented-but-unenforced incompatibilities
  data_points:
    - seed_531 (cycle-17): shellscript + executive_brief (to-CEO audience)
    - seed_560 (cycle-18): shellscript + sim (narrative task)
  documentation: correct (shellscript guidance notes both incompatibilities)
  grammar: not enforced
  recommendation: >
    Grammar-level enforcement would eliminate these score-2 seeds permanently.
    Add to AxisIncompatibilities: shellscript ↔ [sim, probe] tasks;
    shellscript ↔ [to-CEO, to-managers, to-stakeholders, to-team] audiences.
    Defer to a dedicated grammar-hardening session (heavier schema work).

- id: spike-task-tension-watch
  type: watch
  status: no new data this cycle
  note: spike+gherkin (432), spike+sim (524) — 2 data points; still watching
```
