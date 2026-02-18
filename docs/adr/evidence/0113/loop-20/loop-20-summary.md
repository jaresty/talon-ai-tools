# ADR-0113 Loop-20 Summary — Opaque Method Tokens Set 3

**Date:** 2026-02-17
**Status:** Complete
**Focus:** induce, converge, branch, simulation (method), operations, models, systemic,
           unknowns, verify, trans

---

## Results

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| L20-T01 | induce | 3 | Yes — G-L20-01 |
| L20-T02 | converge | 4 | No |
| L20-T03 | branch | 4 | No |
| L20-T04 | simulation (method) | 3 | Yes — G-L20-02 |
| L20-T05 | operations | 5 | No |
| L20-T06 | models | 4 | No |
| L20-T07 | systemic | 4 | No |
| L20-T08 | unknowns | 5 | No |
| L20-T09 | verify | 5 | No |
| L20-T10 | trans | 3 | Yes — G-L20-03 |

**Mean: 4.0/5**

---

## Gaps Found and Fixed

| ID | Token | Axis | Root cause | Fix |
|----|-------|------|-----------|-----|
| G-L20-01 | induce | method | Academic term; "generalize from observations" does not route to induce | use_when: 'what general principle can I draw from these', 'what pattern do these examples suggest', 'extrapolate from these examples' |
| G-L20-02 | simulation | method | Confused with sim task; "thought experiment / feedback loops / tipping points" not discoverable as method enrichment | use_when: 'run a thought experiment', 'trace feedback loops', 'tipping point analysis', 'what emergent effects would arise' + distinction from sim task |
| G-L20-03 | trans | method | Completely opaque name; "signal degrades / gets lost" does not route to trans | use_when: 'where does signal get lost', 'where does data degrade', 'signal fidelity', 'where does noise enter' |

## Post-Apply Validation

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| L20-T01 | induce | 3 | 4 | +1 | PASS — 'generalize from observations / what pattern do these suggest' now anchored |
| L20-T04 | simulation | 3 | 4 | +1 | PASS — 'run a thought experiment / trace feedback loops' now anchored; sim vs simulation distinction explicit |
| L20-T10 | trans | 3 | 4 | +1 | PASS — 'where does signal get lost / signal fidelity' now anchored |

Grammar regenerated. All tests pass. SSOT intact.

---

## Key sim vs simulation Distinction Clarified

A critical semantic overlap now explicitly documented:
- **`sim` (task):** Standalone scenario walkthrough — use as the task when the whole
  response IS a scenario narrative unfolding over time ("what would happen if we deprecated X")
- **`simulation` (method):** Thought-experiment enrichment — use with another task (probe, plan)
  when the analysis should be structured around feedback loops, tipping points, and emergent
  effects ("probe + simulation" = analyze the system using thought-experiment projection)

---

## Tokens Confirmed Description-Anchored (No use_when Needed)

| Token | Axis | Reason |
|-------|------|--------|
| converge | method | "narrow to a recommendation" maps to "systematically narrowing from broad to focused" |
| branch | method | User says "branching on key assumptions" — mirrors description exactly |
| operations | method | User says "operations research problem" — explicit framework name |
| models | method | User says "named mental models" — mirrors description exactly |
| systemic | method | "as a whole system / feedback loops" maps to "interacting whole / feedback loops" |
| unknowns | method | User says "unknown unknowns" — phrase appears in both request and description |
| verify | method | User says "apply falsification pressure" — mirrors description exactly |

---

## Method Axis Coverage (Post Loop-20)

Tokens with use_when: abduce, boom, field, grove, grow, induce, jobs, meld, melody, mod,
simulation, trans (12 method tokens)

Confirmed description-anchored (no use_when needed): actors, adversarial, analog, analysis,
argue, bias, branch, calc, cite, cluster, compare, converge, deduce, depends, diagnose,
dimension, domains, effects, experimental, explore, flow, induce (via description rescue),
inversion, mapping, models, objectivity, operations, order, origin, prioritize, probability,
product, resilience, rigor, risks, robust, shift, spec, split, systemic, unknowns, verify

Remaining without use_when (likely low-risk — description-anchored or explicit phrase):
calc, cite, domains, experimental, objectivity, order, origin, probability, product, rigor,
risks, robust — all have clear enough descriptions or rely on user saying the exact term.

**Method axis systematic check: Substantially complete.** High-risk opaque tokens now covered.
Re-trigger only on new tokens or failure reports.
