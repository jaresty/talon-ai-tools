# ADR-0085 Cycle 12: R36 Validation + Broad Health Check
**Date:** 2026-02-25
**Seeds:** 296–335 (40 prompts)
**Bar version:** 2.64.1
**Focus:** Validate R36 fix (gist + compound directionals), broad health check

---

## Phase 0: Calibration

**Evaluators:** single-evaluator (Claude Sonnet 4.6)
**Calibration result:** N/A (continuation of established rubric)

---

## Section A: Rapid Evaluation — Seeds 296–335

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 296 | show | minimal, prioritize, gherkin | scientist_to_analyst | 3 | gherkin for explain is unusual; scientist+gherkin slight tension |
| 297 | make | gist, stable, risks, table, sketch | audience | 4 | gist+no-compound-dir=fine; risks+stable coherent |
| 298 | trans | full, thing, experimental, plain | stakeholder_facilitator | 4 | experimental transformation; clean |
| 299 | pick | full, time, converge, questions | none | 4 | convergent decision via questioning; coherent |
| 300 | show | full, analog, slack | executive_brief | 4 | analogy-based explanation for executives; coherent |
| 301 | probe | full, struct, cite, plain, fly-ong | audience, announce | 4 | cite+struct probe with fly-ong+full=fine; announce+probe minor tension |
| 302 | pick | full, jog | executive_brief | 4 | minimal but decisive executive pick |
| 303 | show | full | directly, coach | 3 | very sparse; functional but underspecified |
| 304 | check | gist, spike | kindly, announce | 3 | spike form + check task unusual; gist+no-compound=fine |
| 305 | sim | full, good, shift, spike, fig | scientist_to_analyst | 4 | scientific spike sim with fig+full=fine; strong combo |
| 306 | make | full, variants, dig | formally, teach | 4 | variants creation; dig+full=fine |
| 307 | pick | full, view, log, fly-ong | pm_to_team | 3 | log form for pick task awkward; fly-ong+full=fine |
| 308 | sim | full, gherkin | announce | 4 | sim expressed as Gherkin scenarios; well-handled |
| 309 | trans | skim, actions, sync | stakeholder_facilitator | 4 | skim+no-compound=fine; skim+actions+sync=light transformation for sync |
| 310 | pick | minimal, wardley, jog | gently | 3 | wardley+minimal slight tension; wardley maps detailed by nature |
| 311 | pull | full, assume, fig | executive_brief | 4 | assumption extraction with fig+full=fine |
| 312 | show | full, resilience | designer_to_pm | 3 | minimal; functional |
| 313 | sim | full, assume, meld, socratic | gently, teach | 4 | collaborative educational simulation; coherent |
| 314 | check | full, gherkin, fly-ong | fun_mode | 4 | check expressed as Gherkin; fly-ong+full=fine; fun_mode mild tension |
| 315 | check | max, merge | none | 4 | exhaustive check with merged output; clean |
| 316 | sim | full, view, cocreate | scientist_to_analyst | 4 | collaborative simulation with stakeholder view; coherent |
| 317 | diff | full, fail, fly-ong | directly | 4 | compare failures; fly-ong+full=fine |
| 318 | sort | **gist**, resilience, ladder, remote, **fip-ong** | teach_junior_dev | **2** | **R36 validated: gist+fip-ong** — compound dir cannot be expressed in gist |
| 319 | pull | skim, agent, origin, html, ong | gently, announce | 4 | skim+ong (primitive)=fine; html extraction coherent |
| 320 | show | full, rigor, walkthrough, shellscript | executive_brief | 3 | shellscript+executive_brief unusual; walkthrough in shellscript via form-as-lens |
| 321 | sim | minimal, struct, triage, test, jog | executive_brief | 3 | complex combo; test form+sim+exec_brief+minimal=slightly incoherent |
| 322 | probe | skim | casually | 3 | extremely sparse; functional |
| 323 | pull | skim | fun_mode | 3 | extremely sparse; functional |
| 324 | show | deep, quiz, presenterm | gently, persuade | 4 | deep quiz presentation; persuade+gently=coherent |
| 325 | probe | minimal, cross, canon, walkthrough, fip-ong | peer_engineer | 4 | minimal+fip-ong fine (minimal≠gist/skim); canonical cross-scope probe |
| 326 | show | narrow, spike, code, fig | appreciate | 3 | narrow completeness+fig tension (fig=full-vertical, narrow=restricted); appreciate+code unusual |
| 327 | pull | deep, visual | scientist_to_analyst | 4 | deep visual extraction; coherent |
| 328 | pick | full, struct, slack, fip-rog | persuade | 4 | fip-rog+full=fine; structural decision via persuasion |
| 329 | show | full, view | teach | 3 | minimal; functional |
| 330 | pull | full, agent | designer_to_pm | 3 | minimal; functional |
| 331 | check | max, struct, indirect, dip-ong | formally, inform | 4 | dip-ong+max=fine; exhaustive indirect check; coherent |
| 332 | trans | full, motifs, faq, sketch | designer_to_pm | 4 | motifs transformation as FAQ sketch; coherent |
| 333 | plan | minimal, order, checklist, fip-bog | gently, announce | 4 | minimal+fip-bog fine (minimal≠gist/skim); ordered plan as checklist |
| 334 | sort | full, good, fip-bog | fun_mode | 4 | fip-bog+full=fine; fun classification |
| 335 | check | full, motifs | gently | 3 | minimal; functional |

**Score distribution:**
- 4: seeds 297–302, 305–306, 308–309, 311, 313–317, 319, 324–325, 327–328, 331–334 (25)
- 3: seeds 296, 303–304, 307, 310, 312, 320–323, 326, 329–330, 335 (14)
- 2: seed 318 (1)

**Corpus average: 3.60** (regression from 3.73; driven by 14 sparse/minimal seeds scoring 3, plus R36 seed 318)

---

## Section B: Key Findings

### B1 — R36 Validated: gist + fip-ong (Seed 318)

Seed 318 = `sort + gist + resilience + ladder + remote + fip-ong + teach_junior_dev`. Score 2.

`fip-ong` (fip ong 現) is a compound directional: "alternate between abstract principles and concrete examples, then identify actions and extend to related situations." This multi-phase depth cannot be expressed in a gist (brief but complete summary).

The cycle-11 R36 fix added to `gist` notes: "Avoid pairing with compound directionals (fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog)" — `fip-ong` is now explicitly listed. **Fix was correctly motivated and applied.**

Note: Seeds 325 (minimal+fip-ong) and 333 (minimal+fip-bog) both score 4 — `minimal` completeness is NOT in the avoidance list and correctly so. Minimal = smallest satisfying answer; it doesn't truncate to a brief summary.

### B2 — Seed 326: narrow + fig mild tension

`narrow` completeness (restricted to a small slice) + `fig` directional (full vertical: abstract AND concrete) is semantically in tension — fig wants to span the full vertical axis, narrow wants to restrict. However this is weaker than R36 because fig is one compound (not multi-phase sequential), and narrow is about topic scope not output brevity. Score 3, monitor.

### B3 — Sparse combos (seeds 303, 312, 322, 323, 329, 330, 335)

Seven seeds in this batch are very sparse (1-2 constraint tokens). Scores 3 are appropriate (functional but underspecified). This is natural variation from shuffling; no catalog action needed.

### B4 — Positive patterns

| Pattern | Seeds | Score | Value |
|---------|-------|-------|-------|
| sim + assume + meld + socratic + teach | 313 | 4 | Collaborative educational simulation |
| pick + full + converge + questions | 299 | 4 | Convergent decision via questioning |
| show + deep + quiz + presenterm | 324 | 4 | Deep persuasive quiz presentation |
| check + max + struct + indirect + dip-ong | 331 | 4 | Exhaustive indirect structural check |
| probe + full + struct + cite + plain | 301 | 4 | Citation-grounded structural probe |

---

## Section C: Recurring Patterns

| Pattern | Cycle 12 | Cycle-to-date | Action |
|---------|----------|---------------|--------|
| Compound dir + gist/skim | 1 seed (318: gist+fip-ong) | R36 applied in cycle 11 | Fixed; seed 318 is post-apply evidence |
| Sparse/minimal combos scoring 3 | 7 seeds | Consistent 20-35% of corpus | No action; shuffle naturally underspecifies |
| narrow + fig tension | 1 seed (326) | New | Track next cycle (low priority) |

---

## Recommendations (Cycle 12)

No new catalog changes needed. Cycle-11 R36 fix validated.

```yaml
- id: R36-validation
  type: post-apply-evidence
  finding: gist + fip-ong (seed 318) scores 2
  fix_applied: cycle-11 (gist notes now list fip-ong in compound avoidance list)
  status: confirmed-fixed

- id: R37-watch
  type: watch
  pattern: narrow completeness + fig directional
  seeds: [seed_326]
  score: 3
  reason: >
    narrow (restrict to small slice) + fig (span full vertical axis) are
    semantically in tension. One seed, low priority. Monitor next cycle.
  action: none-yet
```
