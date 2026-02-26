# ADR-0085 Cycle 19: Best Average Since Cycle 14 + Grammar Gap Pattern Confirmed
**Date:** 2026-02-25
**Seeds:** 576–615 (40 prompts)
**Bar version:** 2.64.1
**Focus:** General health check; R40 third data point; grammar gap pattern investigation

---

## Section A: Rapid Evaluation — Seeds 576–615

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 576 | check | full, assume, bug, jira, jog | scientist_to_analyst | 4 | jog+full=fine; bug+jira=form-as-lens; assumption check |
| 577 | pull | full, time, analysis | as-teacher, to-PM, formally, teach | 4 | analysis+pull+time; teacher-to-PM temporal extraction |
| 578 | trans | max, motifs, dip-ong | stakeholder_facilitator | 4 | dip-ong+max=fine; motifs+trans+max for stakeholders |
| 579 | show | full, cross, fip-ong | as-programmer, to-PM, persuade | 4 | fip-ong+full=fine; cross+show; programmer-to-PM persuasion |
| 580 | probe | deep, depends, socratic, fig | to-Kent-Beck, gently, persuade | 4 | fig+deep=fine; depends+socratic+probe; coherent |
| 581 | make | full, stable, bullets, fip-ong | designer_to_PM | 4 | fip-ong+full=fine; stable+bullets+make; coherent |
| 582 | pick | max, view | as-facilitator, to-programmer, directly, inform | 4 | max+pick+view; facilitator-to-programmer pick; coherent |
| 583 | sort | minimal, good, deduce, visual, dip-rog | designer_to_PM | 4 | dip-rog+minimal=fine (minimal≠gist/skim); visual+deduce sort |
| 584 | plan | full, stable, formats | as-prompt-engineer, casually, teach | 4 | stable+formats+plan; prompt engineer teaching; coherent |
| 585 | pick | full, cross, induce, contextualise, fly-bog | peer_engineer | 4 | fly-bog+full=fine; contextualise+pick+induce; coherent |
| 586 | probe | minimal, case | as-principal-engineer, kindly | 4 | minimal+case+probe; principal engineer; coherent |
| 587 | check | full, balance | stakeholder_facilitator | 3 | sparse |
| 588 | sort | narrow, tight, **shellscript** | as-PM | **2** | **shellscript + sort**: selection task + code channel; documented; grammar gap |
| 589 | make | full, good, domains, fly-ong | designer_to_PM | 4 | fly-ong+full=fine; domains+good+make; coherent |
| 590 | check | max, stable, svg, ong | teach_junior_dev | 3 | max+svg: exhaustive check as SVG; unusual but workable |
| 591 | trans | **gist**, flow, code, **fip-ong** | as-teacher, kindly | **2** | **R36**: gist+fip-ong; guidance in place |
| 592 | sim | gist, cross, systemic, walkthrough, remote | peer_engineer | 4 | gist+no-compound=fine; walkthrough+remote=form-as-lens; coherent |
| 593 | plan | deep, thing, deduce, taxonomy, remote, fip-bog | directly | 4 | fip-bog+deep=fine; taxonomy+remote=form-as-lens; coherent |
| 594 | make | minimal, thing, field, gherkin, dip-rog | pm_to_team | 4 | dip-rog+minimal=fine (minimal≠gist/skim); gherkin+field; coherent |
| 595 | make | full, motifs, tight | to-programmer, inform | 4 | tight+full+motifs; programmer-focused; coherent |
| 596 | make | full, time, robust, activities | pm_to_team | 4 | robust+time+activities; PM team; coherent |
| 597 | pull | full, questions, fly-ong | announce | 4 | fly-ong+full=fine; questions+pull; coherent |
| 598 | sim | full, recipe, dip-rog | to-stakeholders | 4 | dip-rog+full=fine; recipe+sim; stakeholder simulation as recipe |
| 599 | pull | max, act, balance, ladder, adr, fog | teach_junior_dev | 4 | fog+max=fine (R36=gist/skim+compound only); ladder+adr=form-as-lens |
| 600 | check | full, assume, domains, plain, rog | as-writer, to-stream-aligned-team | 4 | rog+full=fine; domains+assume+check; coherent |
| 601 | plan | full, gherkin | designer_to_PM | 4 | gherkin+plan; designer-to-PM; coherent |
| 602 | diff | full, agent, visual, diagram, dip-bog | to-stakeholders, coach | 4 | dip-bog+full=fine; visual+diagram=form-as-lens; coherent |
| 603 | trans | deep, thing, sketch, fly-ong | designer_to_PM | 4 | fly-ong+deep=fine; trans as D2; coherent |
| 604 | pick | skim, effects, presenterm | as-principal-engineer, to-principal-engineer | 4 | skim+no-compound=fine; effects+skim+presenterm; coherent |
| 605 | make | minimal, induce, log, codetour, ong | peer_engineer | 3 | log+codetour=form-as-lens (unusual); workable |
| 606 | probe | gist, assume, effects, dig | as-PM | 4 | gist+dig=fine (simple dir); effects+assume+probe; coherent |
| 607 | pick | full, cross, actions, rog | stakeholder_facilitator | 4 | rog+full=fine; actions+cross+pick; coherent |
| 608 | make | full, converge | pm_to_team | 4 | converge+make; PM team; coherent |
| 609 | plan | full, time | as-scientist, casually | 3 | sparse |
| 610 | show | full, time, product, case | teach_junior_dev | 4 | product+time+case+show; teaching juniors; coherent |
| 611 | plan | full, stable, svg, fip-bog | to-junior-engineer, directly | 3 | fip-bog+full=fine; plan as SVG unusual |
| 612 | trans | full, polar | peer_engineer | 4 | polar+trans+full; coherent |
| 613 | pull | minimal, good, branch, adr, fip-rog | to-analyst, gently | 4 | fip-rog+minimal=fine (minimal≠gist/skim); branch+adr+pull; coherent |
| 614 | sim | full, bog | pm_to_team | 4 | bog+full=fine; PM team simulation; coherent |
| 615 | probe | **max**, robust, **commit** | peer_engineer | **2** | **commit + max**: commit notes say "avoid max completeness"; documented; grammar gap |

**Score distribution:**
- 4: 576–586, 589, 592–604, 606–608, 610, 612–614 (32)
- 3: 587, 590, 605, 609, 611 (5)
- 2: 588, 591, 615 (3)

**Corpus average: 3.73** (best since cycle 14; 32/40 scoring 4)

---

## Section B: Key Findings

### B1 — Seed 591: R36 (gist + fip-ong)

`trans + gist + flow + code + fip-ong`. Score 2. Cycle-11 fix covers fip-ong. No new action.

### B2 — R40 third data point: shellscript + sort (seed 588)

`sort + narrow + tight + shellscript`. Score 2. shellscript guidance: "Avoid with selection tasks (pick, diff, sort) — these don't produce code." Third consecutive cycle with a shellscript grammar gap:

| Seed | Pattern | Cycle |
|------|---------|-------|
| 531 | shellscript + executive_brief (to-CEO) | 17 |
| 560 | shellscript + sim | 18 |
| 588 | shellscript + sort | 19 |

All three incompatibilities are documented in shellscript's guidance. None are grammar-enforced.

**Grammar investigation:** `_AXIS_INCOMPATIBILITIES` in `lib/talonSettings.py` is structured as `axis → token → incompatible tokens` *within* the same axis. It cannot express cross-axis incompatibilities (channel + task type, channel + audience). Grammar enforcement of shellscript task/audience incompatibilities requires a new cross-axis schema, which is non-trivial schema work.

**Current state:** Documentation correct across all three cases. Fix deferred until grammar-hardening work is scoped.

### B3 — Seed 615: commit + max (new cross-axis grammar gap)

`probe + max + robust + commit`. Score 2. commit form guidance: "avoid deep or max completeness — no room to express depth." Documentation correct; grammar can't enforce cross-axis (form ↔ completeness) incompatibilities with current schema.

This is the same structural gap as R40 but affecting form ↔ completeness instead of channel ↔ task. The pattern is now clear: **any documented cross-axis incompatibility in AXIS_KEY_TO_GUIDANCE is unenforced at grammar level** because `_AXIS_INCOMPATIBILITIES` only handles same-axis conflicts.

**Consolidation:** R40 and this finding are symptoms of the same root cause — the grammar schema doesn't support cross-axis incompatibilities. Flag as R41-grammar-hardening: a dedicated session to design and implement cross-axis incompatibility enforcement.

### B4 — Excellent overall corpus (32/40 scoring 4)

No new guidance failures. Highlights:
- Seeds 599 (fog+max=4): confirms R36 correctly targets gist/skim+compound, not all completeness+fog
- Seeds 583, 594, 613 (minimal+compound-dir=4): confirms minimal≠gist/skim boundary is precise
- Seeds 578, 582 (max+compound-dir/max+pick=4): max completeness works fine with compound dirs and non-constrained tasks

### B5 — Positive patterns

| Pattern | Seed | Score | Value |
|---------|------|-------|-------|
| probe + deep + depends + socratic + fig | 580 | 4 | Dependency probe via Socratic questioning |
| sim + gist + cross + systemic + walkthrough + remote | 592 | 4 | Gist simulation as remote step-by-step walkthrough |
| plan + deep + thing + deduce + taxonomy + remote + fip-bog | 593 | 4 | Deductive taxonomy plan for remote delivery |
| pull + max + act + balance + ladder + adr + fog | 599 | 4 | Rich 6-token pull combo — all compatible |
| diff + full + agent + visual + diagram + dip-bog | 602 | 4 | Visual diff as Mermaid via form-as-lens |

---

## Section C: Grammar Gap Summary (All Cycles)

Cross-axis incompatibilities that are documented but grammar-unenforced:

| Finding | Axis pair | Seeds | Status |
|---------|-----------|-------|--------|
| shellscript + non-tech audience | channel ↔ persona-audience | 531 | R40 |
| shellscript + narrative tasks (sim, probe) | channel ↔ task | 560 | R40 |
| shellscript + selection tasks (sort, pick, diff) | channel ↔ task | 588 | R40 |
| commit + deep/max completeness | form ↔ completeness | 615 | New |

All four are caused by the same root: `_AXIS_INCOMPATIBILITIES` is single-axis only. A cross-axis incompatibility schema would eliminate all of them.

---

## Recommendations (Cycle 19)

```yaml
- id: R36-cycle19
  type: post-apply-evidence
  findings: [seed_591 (gist+fip-ong=2)]
  status: confirmed-working

- id: R40
  status: confirmed (3 data points, 3 consecutive cycles)
  action: defer to R41-grammar-hardening
  evidence: [seed_531, seed_560, seed_588]

- id: R41-grammar-hardening
  type: architectural
  description: >
    Design and implement cross-axis incompatibility enforcement.
    _AXIS_INCOMPATIBILITIES in lib/talonSettings.py only supports same-axis
    conflicts. Cross-axis incompatibilities (channel↔task, form↔completeness,
    channel↔audience) are documented in AXIS_KEY_TO_GUIDANCE but not enforced.
    Affected cases: shellscript+[sim/probe/pick/diff/sort/to-CEO/...] and
    commit/gist/skim+[max/deep/compound-dirs].
    Note: gist/skim+compound-dirs ARE enforced via guidance notes (R36), which
    works through LLM reading rather than grammar blocking. The question is
    whether grammar blocking is needed for the remaining cases.
  priority: medium (score-2 seeds appear in ~7% of shuffle draws)
  action: none-yet; needs design session
```
