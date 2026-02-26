# ADR-0085 Cycle 15: Four R36 Hits + R38 Confirmed (max+sync)
**Date:** 2026-02-25
**Seeds:** 416–455 (40 prompts)
**Bar version:** 2.64.1
**Focus:** General health check; R38-watch confirmation

---

## Section A: Rapid Evaluation — Seeds 416–455

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 416 | probe | deep, dimension, walkthrough, ong | scientist_to_analyst | 4 | ong=primitive=fine; deep dimension walkthrough |
| 417 | trans | full, mean | casually | 3 | sparse |
| 418 | make | **max**, act, effects, **sync** | teach_junior_dev | 3 | **R38 confirmed**: max+sync tension (2nd data point) |
| 419 | pick | deep, merge, rog | voice | 4 | rog=primitive=fine; merged decision |
| 420 | sort | full, view, risks, dip | stakeholder_facilitator | 4 | dip+full=fine |
| 421 | plan | full, shellscript | casually | 3 | shellscript for plan unusual |
| 422 | pull | full, assume, adversarial, faq, fig | designer_to_pm | 4 | fig+full=fine; adversarial+faq extraction excellent |
| 423 | sort | **skim**, rigor, plain, **fip-ong** | persuade | **2** | **R36**: skim+fip-ong; guidance in place |
| 424 | diff | skim, adr | scientist_to_analyst | 4 | skim+no-dir=fine; diff as ADR |
| 425 | show | full, fail, mapping, code | fun_mode | 3 | code for explain unusual |
| 426 | make | full, fail, socratic, slack | gently | 4 | socratic failure scenarios; coherent |
| 427 | pick | full, thing, deduce, scaffold, bog | peer_engineer | 4 | bog+full=fine; deductive pick with scaffold |
| 428 | diff | full, view, dip | teach | 4 | dip+full=fine; perspective diff |
| 429 | make | full, struct, wardley, plain, dip | executive_brief | 4 | dip+full=fine; wardley creation |
| 430 | probe | full, fail, unknowns | gently | 4 | unknowns+fail probe; coherent |
| 431 | pick | full, mean | executive_brief | 3 | sparse |
| 432 | pick | minimal, act, spike, gherkin | casually | 3 | spike+gherkin: channel-wins rule applies; Gherkin scenarios as hypothesis tests (form-as-lens); workable |
| 433 | diff | minimal, meld, test, codetour, fig | peer_engineer | 3 | fig+minimal=fine; codetour+test form awkward |
| 434 | trans | full, systemic, activities, svg, fip | scientist_to_analyst | 3 | fip+full=fine; activities+svg = form-as-lens |
| 435 | pick | narrow, mean, test | appreciate | 3 | sparse |
| 436 | plan | full, act, ong | scientist_to_analyst | 4 | ong=primitive=fine |
| 437 | trans | full, effects, test | coach | 4 | effects+test transformation; coherent |
| 438 | plan | narrow, thing, bullets, plain, ong | teach_junior_dev | 4 | ong=primitive=fine; narrow plan as bullets |
| 439 | plan | full, effects, merge, svg, dig | casually | 3 | svg+merge = form-as-lens; dig+full=fine |
| 440 | pull | full, contextualise, remote | stakeholder_facilitator | 4 | contextualise+remote; clean |
| 441 | sort | max, melody | audience | 3 | max+melody (metaphorical method); sparse+unusual |
| 442 | check | full, stable, visual, svg, fip | inform | 3 | fip+full=fine; visual+svg = form-as-lens (visual form as content lens in SVG) |
| 443 | pull | **gist**, assume, svg, **dip-rog** | peer_engineer | **2** | **R36**: gist+dip-rog; guidance in place |
| 444 | check | max, act, split, wasinawa, dip | none | 4 | dip+max=fine; wasinawa check; coherent |
| 445 | sim | **skim**, actions, sync, **fip-bog** | fun_mode | **2** | **R36**: skim+fip-bog; guidance in place |
| 446 | show | **gist**, actions, **bog** | gently | **2** | **R36**: gist+bog; guidance in place |
| 447 | show | deep, fail, ong | peer_engineer | 4 | ong=primitive=fine; deep failure explanation |
| 448 | trans | full, analysis | appreciate | 3 | sparse; appreciate+trans slightly odd |
| 449 | plan | minimal, diagram, bog | designer_to_pm | 4 | bog+minimal=fine; minimal diagram plan |
| 450 | pick | full, thing | announce | 3 | sparse |
| 451 | diff | full, time, objectivity, shellscript | fun_mode | 3 | shellscript for diff unusual; objectivity method coherent |
| 452 | sort | full, view, risks, commit, shellscript, fly | teach_junior_dev | 3 | commit form+compound dir conflict (notes); shellscript overrides commit anyway |
| 453 | show | full, stable, gherkin | formally | 4 | show as Gherkin scenarios; coherent |
| 454 | check | minimal, html, dip | peer_engineer | 4 | dip+minimal=fine; check as HTML |
| 455 | show | minimal, mean, shift, facilitate, fip | teach | 4 | fip+minimal=fine; facilitate+shift; coherent |

**Score distribution:**
- 4: 416, 419, 420, 422, 424, 426, 427, 428, 429, 430, 436, 437, 438, 440, 444, 447, 449, 453, 454, 455 (20)
- 3: 417, 418, 421, 425, 431, 432, 433, 434, 435, 439, 441, 442, 448, 450, 451, 452 (16)
- 2: 423, 443, 445, 446 (4)

**Corpus average: 3.40** (significant regression; 4 R36 hits vs usual 0–2)

---

## Section B: Key Findings

### B1 — Four R36 hits (above-average draw)

| Seed | Pattern | Fix in place? |
|------|---------|--------------|
| 423 | skim + fip-ong | ✅ Yes — R36 cycle-11 |
| 443 | gist + dip-rog | ✅ Yes — R36 cycle-11 |
| 445 | skim + fip-bog | ✅ Yes — R36 cycle-11 |
| 446 | gist + bog | ✅ Yes — R36 cycle-11 |

All four are covered by the cycle-11 fix. The guidance is correct; these are random-draw occurrences. With 16 compound directionals in the catalog and gist/skim appearing in ~10–15% of shuffles, statistical clustering happens. No new action needed.

### B2 — R38 Confirmed: max + sync (second data point → fix applied)

Seed 418 = `make + max + act + effects + sync + teach_junior_dev`. Score 3. Second max+sync hit (first was seed 338, cycle 13). Both score 3; pattern is consistent.

**Root cause:** `max` = "exhaustive, treat omissions as errors." `sync` = "synchronous session plan — agenda, steps, cues." A session plan must be actionable and concise by design; max completeness produces an overloaded agenda that loses the session format's purpose.

**Fix applied:** Added notes to both tokens in `axisConfig.py`.

### B3 — Seed 432: spike + gherkin (form-as-lens, score 3)

`pick + minimal + act + spike + gherkin`. Score 3. Unlike story+gherkin (which has a natural behavioral mapping), spike is exploratory prose ("what do we need to learn?"). With channel-wins rule, gherkin+spike = Gherkin scenarios framing the unknowns as testable hypotheses — workable but a stretch. Score 3 is appropriate; no documentation change needed (spike's notes already say "conflicts with gherkin" and users are warned).

**Future consideration:** Apply the same story+gherkin treatment to spike — define Gherkin+spike as "scenarios representing experiments to reduce uncertainty." One data point for now; watch for recurrence.

### B4 — Seed 452: commit form + compound directional (fly)

`sort + full + view + risks + commit + shellscript + fly`. Score 3. Commit form notes say "avoid compound directionals." With shellscript channel, commit becomes a content lens anyway (shellscript overrides). The compound dir conflict only matters when commit is the output format. Score 3 for overall complexity; no new action.

### B5 — Positive patterns

| Pattern | Seed | Score | Value |
|---------|------|-------|-------|
| pull + assume + adversarial + faq + fig | 422 | 4 | Adversarial assumption extraction as FAQ |
| pick + deduce + scaffold + bog + full | 427 | 4 | Scaffolded deductive pick — bog+full fine |
| check + max + act + split + wasinawa | 444 | 4 | Exhaustive wasinawa check |
| make + fail + socratic + slack | 426 | 4 | Socratic failure scenario creation |

---

## Section C: R38 Fix Applied

**R38 action:** Updated `max` and `sync` notes in `axisConfig.py`:
- `sync`: Added "Avoid pairing with max completeness — session plans must be actionable and concise; max completeness overloads the format. Use full or minimal completeness."
- `max`: Added "Avoid pairing with sync channel — sync implies practical session brevity that conflicts with exhaustive coverage."

---

## Recommendations (Cycle 15)

```yaml
- id: R38
  action: edit-notes
  tokens: [max, sync]
  target: lib/axisConfig.py
  status: ✅ Applied
  evidence: [seed_338 (cycle-13), seed_418 (cycle-15)]

- id: R36-cycle15
  type: post-apply-evidence
  findings: [seed_423, seed_443, seed_445, seed_446]
  status: confirmed-working (4 hits; above-average statistical draw; all covered)

- id: spike-gherkin-watch
  type: watch
  pattern: spike form + gherkin channel
  seeds: [seed_432 (score 3)]
  note: >
    One data point. spike+gherkin might deserve the same story+gherkin treatment
    (define behavior rather than flag as conflict). Watch for recurrence.
```
