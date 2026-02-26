# ADR-0085 Cycle 14: No R36 Hits + story/gherkin Grammar Enforcement Gap
**Date:** 2026-02-25
**Seeds:** 376–415 (40 prompts)
**Bar version:** 2.64.1
**Focus:** General health check; R38-watch (max+sync) follow-up

---

## Phase 0: Calibration

**Evaluators:** single-evaluator (Claude Sonnet 4.6)
**Calibration result:** N/A

---

## Section A: Rapid Evaluation — Seeds 376–415

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 376 | show | full, jog | directly | 3 | sparse |
| 377 | show | full, time, taxonomy, gherkin, fog | pm_to_team | 3 | taxonomy+gherkin = form-as-lens; fog+full=fine |
| 378 | sort | full, agent, grove | formally | 4 | grove method; coherent |
| 379 | make | full, robust, recipe | stakeholder_facilitator | 4 | robust creation as recipe; clean |
| 380 | plan | full, assume, slack | casually | 4 | minimal but clean plan |
| 381 | pull | full, agent, dip | fun_mode | 4 | dip+full=fine; coherent |
| 382 | plan | deep, facilitate, codetour | executive_brief | 3 | facilitate+codetour = form-as-lens required; executive+codetour unusual |
| 383 | check | minimal, fail, wasinawa, adr, fog | voice, audience | 3 | wasinawa+adr form-as-lens; fog+minimal=fine (minimal≠gist/skim) |
| 384 | check | minimal, motifs, fly | fun_mode | 4 | fly+minimal=fine (minimal≠gist/skim); coherent |
| 385 | pull | full, stable, product | kindly, teach | 4 | product thinking + stable extraction; coherent |
| 386 | make | deep | scientist_to_analyst | 3 | very sparse |
| 387 | check | full, view, gap, cocreate | persuade | 4 | gap-finding check via collaborative form; coherent |
| 388 | diff | full, models, merge, fly | teach_junior_dev | 4 | fly+full=fine; models+merge diff; coherent |
| 389 | sort | gist, motifs, unknowns | announce | 4 | gist+no-directional=fine; unknowns+motifs sort |
| 390 | diff | full, balance, wardley | stakeholder_facilitator | 4 | wardley diff with balance method; coherent |
| 391 | pull | deep, time, shellscript | executive_brief | 3 | shellscript+executive_brief unusual |
| 392 | pick | full, view, cite, remote, fig | announce | 4 | cite+remote+fig+full=fine; cited decision as PR |
| 393 | pick | full, induce | fun_mode | 4 | inductive decision; coherent |
| 394 | check | skim, motifs | persuade | 3 | skim+no-directional=fine; persuade+check odd intent |
| 395 | probe | max, risks, codetour | fun_mode | 3 | probe+codetour unusual; max+codetour ok |
| 396 | probe | full, indirect, gherkin | voice, audience | 4 | gherkin+indirect = form-as-lens (background-first Gherkin); coherent |
| 397 | plan | gist, agent, sketch | pm_to_team | 4 | gist+no-directional=fine; quick stakeholder sketch plan |
| 398 | sort | full | stakeholder_facilitator | 3 | very sparse |
| 399 | probe | full, time, presenterm | casually, inform | 4 | probe findings as casual presentation; coherent |
| 400 | pull | full, stable, contextualise, remote, fip | stakeholder_facilitator | 4 | fip+full=fine; contextualise+remote = package for downstream LLM as PR |
| 401 | check | full, agent, mapping, **story**, **gherkin** | casually | **2** | **story+gherkin documented conflict** — story avoids Gherkin syntax, gherkin mandates it |
| 402 | diff | full, good, grove, bog | teach_junior_dev | 4 | bog+full=fine; grove diff for juniors |
| 403 | sim | full, codetour, ong | audience | 3 | sim+codetour unusual; ong=primitive=fine |
| 404 | check | full, product, log, ong | fun_mode | 4 | product check as log; ong=primitive=fine |
| 405 | sim | full, ladder, code, fip | gently, inform | 4 | fip+full=fine; ladder+code = abstraction-laddered code sim |
| 406 | make | full, stable, log | stakeholder_facilitator | 4 | stable creation as log; coherent |
| 407 | show | full, fail, cluster, indirect, dip | announce | 4 | dip+full=fine; cluster+indirect+fail show; coherent |
| 408 | sim | full, act, experimental, recipe, sketch, fip | teach_junior_dev | 4 | fip+full=fine; recipe+sketch teaching sim; rich combo |
| 409 | sim | full, prioritize, fig | stakeholder_facilitator | 4 | fig+full=fine; prioritized simulation |
| 410 | pick | full, view, rigor, sync, fip | persuade | 4 | fip+full=fine; rigorous sync decision |
| 411 | sim | full, depends | executive_brief | 4 | depends+sim=dependency chain simulation |
| 412 | sim | full, time, case, presenterm, dip | inform | 4 | dip+full=fine; case study slides |
| 413 | probe | deep, act, bullets, slack | peer_engineer | 4 | bullets+slack; deep act probe for peers |
| 414 | probe | full, questions, slack, dip | gently | 4 | dip+full=fine; gentle question probe |
| 415 | sort | full, case, presenterm, fip | fun_mode | 4 | fip+full=fine; fun case classification slides |

**Score distribution:**
- 4: 378–381, 384–385, 387–390, 392–393, 396–397, 399–400, 402, 404–415 (29)
- 3: 376–377, 382–383, 386, 391, 394–395, 398, 403 (10)
- 2: 401 (1)

**Corpus average: 3.70** (improvement from 3.60; zero R36 hits this cycle)

---

## Section B: Key Findings

### B1 — No R36 hits (zero gist/skim + compound directional)

Seeds with gist/skim: 389 (gist, no dir), 394 (skim, no dir), 397 (gist, no dir). None paired with compound directionals. First clean cycle since R36 was introduced.

### B2 — Seed 401: story + gherkin = score 2 (documentation gap vs grammar gap)

`check + full + agent + mapping + story + gherkin`. Score 2. `story` form notes: "Explicitly avoids Gherkin or test-case syntax — conflicts with gherkin channel." `gherkin` channel mandates gherkin-only output. Direct contradiction.

**Critical distinction:** The conflict IS fully documented:
- `story` guidance in `AXIS_KEY_TO_GUIDANCE` → renders in Token Guidance section of `bar help llm` Composition Rules
- `gherkin` `use_when` also notes: "Avoid with prose-structure forms (story, case, log, questions, recipe)"

**What's missing:** Grammar-level enforcement. `AxisIncompatibilities` does not include story↔gherkin, so the grammar allows the combination and shuffle can produce it. Users building commands manually have documentation to avoid it; the grammar doesn't prevent it.

**Low priority for now** — documentation is correct and complete. Grammar enforcement would eliminate the combination from shuffle output entirely but requires schema work. Flag for future grammar hardening pass.

### B3 — R38-watch: max + sync not confirmed

No max+sync combination appeared this cycle. Still only 1 data point (seed 338). Remain on watch.

### B4 — max + codetour (seed 395): score 3

`probe + max + risks + codetour + fun_mode`. Score 3. Different pattern from R38 (max+sync), but similar theme: max completeness + a constrained-format channel (codetour = code navigation structure). Not blocking; just note that max completeness often scores 3 with channel tokens that have inherent structural constraints.

### B5 — Positive patterns

| Pattern | Seed | Score | Value |
|---------|------|-------|-------|
| sim + act + experimental + recipe + sketch + fip | 408 | 4 | Rich teaching simulation |
| pull + stable + contextualise + remote + fip | 400 | 4 | Contextualised extraction packaged as PR |
| pick + view + cite + remote + fig | 392 | 4 | Cited decision with full-vertical directional |
| probe + full + indirect + gherkin | 396 | 4 | form-as-lens working correctly: background-first Gherkin |
| sim + full + ladder + code + fip | 405 | 4 | Abstraction-laddered code simulation |

---

## Section C: Trend Summary (Cycles 11–14)

| Cycle | Seeds | R36 hits | Score-2s | Avg | Change |
|-------|-------|----------|----------|-----|--------|
| 11 | 256–295 | 1 (fly-ong) | 1 | 3.73 | Fix applied |
| 12 | 296–335 | 1 (fip-ong) | 1 | 3.60 | Validation |
| 13 | 336–375 | 2 (fip-ong, fog) | 2 | 3.60 | No change |
| 14 | 376–415 | 0 | 1 (story+gherkin) | 3.70 | No change |

The R36 floor appears to be ~0-2 hits per 40-seed cycle; zero this cycle is a better-than-average draw. The stable floor around 3.60–3.73 is driven by sparse combos (structural, not catalog) and occasional documented-but-unenforced conflicts.

---

## Recommendations (Cycle 14)

```yaml
- id: R39
  action: define-behavior (not block)
  finding: story form + gherkin channel = score 2 (seed 401)
  root_cause: >
    story notes said "explicitly avoids Gherkin syntax — conflicts with gherkin channel."
    But by the channel-wins precedence rule, story+gherkin is NOT a conflict — it is a
    defined composition: Gherkin scenarios shaped by user-value framing. The old note
    was written for the no-channel case; it incorrectly implied a hard conflict.
  fix_applied: >
    Updated story guidance in axisConfig.py to describe both cases:
    (1) no channel → prose user stories; (2) gherkin channel → BDD scenarios shaped
    by user capabilities and value (As a → Given; I want → When; So that → Then).
    Updated gherkin use_when to remove story from avoid list, adding exception note.
  status: ✅ Applied
  evidence: [seed_401]

- id: R38-watch
  status: unconfirmed (0 hits cycle 14)
  pattern: max completeness + constrained-format channel (sync, codetour)
  evidence: [seed_338 (max+sync=3, cycle-13), seed_395 (max+codetour=3, cycle-14)]
  note: >
    Two data points now but different channels. Pattern may be: max completeness
    + any channel with inherent structural constraints scores 3.
    Generalise watch to: max + [sync, codetour, adr, presenterm, gherkin].
```
