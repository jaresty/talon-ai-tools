# ADR-0085 Cycle-6: Shuffle Evaluation

**Date:** 2026-02-15  
**Phase:** Phase 2: Evaluate  
**Corpus:** Seeds 70-79 (broad), 80-84 (low-fill), 85-89 (high-fill)

---

## Evaluation Summary

| Seeds | Type | Count | Mean Score |
|-------|------|-------|------------|
| 70-79 | Broad sweep | 10 | TBD |
| 80-84 | Low-fill (0.1) | 5 | TBD |
| 85-89 | High-fill (0.9) | 5 | TBD |
| **Total** | | **20** | **TBD** |

---

## Seed 70

**Tokens:** appreciate, to junior engineer, formally, make, skim, fail, boom, fly rog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 4

**Notes:** appreciate intent + make task is awkward. "Appreciation" + "create new content" don't blend well. Otherwise reasonable.

---

## Seed 71

**Tokens:** fix, full, time, spike, dip ong

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** fix + time + spike - all code-related. Works.

---

## Seed 72

**Tokens:** fun_mode, sim, struct, code, rog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 3
- Category alignment: 4
- Combination harmony: 2
- **Overall:** 3

**Notes:** sim + code - narrative task with code channel. Conflict.

---

## Seed 73

**Tokens:** inform, as writer, kindly, pull, narrow, inversion, socratic

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** Good combo - writer persona with extraction + socratic.

---

## Seed 74

**Tokens:** fun_mode, show, fip rog

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 3
- Category alignment: 4
- Combination harmony: 4
- **Overall:** 4

**Notes:** Simple. fun_mode might override persona tone.

---

## Seed 75

**Tokens:** announce, as facilitator, to team, directly, fix, narrow, motifs, test, code, dip bog

**Scores:**
- Task clarity: 3
- Constraint independence: 2
- Persona coherence: 3
- Category alignment: 3
- Combination harmony: 2
- **Overall:** 2-3

**Notes:** 10 tokens - way too many. fix task + test form + code channel all code-focused but messy.

---

## Seed 76

**Tokens:** peer_engineer_explanation, sim, mapping, merge, slack

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 5
- **Overall:** 5

**Notes:** Excellent - PM simulating with mapping + merge + slack channel.

---

## Seed 77

**Tokens:** as designer, to team, check, deep, fail, sketch, fip ong

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 4

**Notes:** check + fail + sketch - check with failure mode analysis + D2 diagram.

---

## Seed 78

**Tokens:** scientist_to_analyst, fix, stable, robust, dig

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 4
- **Overall:** 4

**Notes:** fix task with stable/robust scope + dig directional. Works.

---

## Seed 79

**Tokens:** stakeholder_facilitator, pull, skim, good, socratic, fip ong

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 4
- **Overall:** 4

**Notes:** Good extraction combo with socratic + fip.

---

## Seed 80 (Low-fill)

**Tokens:** inform, as prompt engineer, pick, minimal

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 4
- **Overall:** 4

**Notes:** Simple and clear.

---

## Seed 81 (Low-fill)

**Tokens:** gently, plan

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 4
- **Overall:** 4

**Notes:** Very simple. Missing task token though.

---

## Seed 82 (Low-fill)

**Tokens:** as facilitator, pull, cross, mapping

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 5
- **Overall:** 5

**Notes:** Excellent - cross-cutting concerns mapping.

---

## Seed 83 (Low-fill)

**Tokens:** make

**Scores:**
- Task clarity: 4
- Constraint independence: 5
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** Minimal. Works.

---

## Seed 84 (Low-fill)

**Tokens:** show, fly rog

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 4
- **Overall:** 4

**Notes:** Simple with directional.

---

## Seed 85 (High-fill)

**Tokens:** product_manager_to_team, plan, narrow, fail, prioritize, test, slack

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3-4

**Notes:** 7 tokens - a bit many. prioritize + test both actions.

---

## Seed 86 (High-fill)

**Tokens:** product_manager_to_team, diff, skim, good, dimension, activities, adr, jog

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3-4

**Notes:** 8 tokens. adr channel with diff - good combo.

---

## Seed 87 (High-fill)

**Tokens:** stakeholder_facilitator, check, gist, assume, compare, taxonomy, fip bog

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 4

**Notes:** 7 tokens but coherent.

---

## Seed 88 (High-fill)

**Tokens:** product_manager_to_team, sim, minimal, motifs, explore, story, fig

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3-4

**Notes:** 7 tokens. story form + motifs scope.

---

## Seed 89 (High-fill)

**Tokens:** stakeholder_facilitator, diff, deep, thing, inversion, bullets, sync, fog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3-4

**Notes:** 8 tokens. deep + inversion + fog - lots of analytical.

---

## Summary

Mean: **3.9/5**

- Broad (70-79): 3.7
- Low-fill (80-84): 4.2
- High-fill (85-89): 3.5

## Key Findings

**Working well:**
- Persona + task combos generally coherent
- Low-fill still performs best
- Directionals (fip rog, dip ong) working

**Issues:**
- Token count still impacts scores (high-fill lower)
- Seed 72: sim + code conflict
- Seed 75: too many tokens (10) - lowest score

## Recommendations

1. No new catalog changes needed
2. Token count guidance (from ADR-0127) still relevant
3. sim + code channel is still problematic (documented in guidance)
