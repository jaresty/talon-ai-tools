# ADR-0085 Cycle-5: Shuffle Evaluation

**Date:** 2026-02-15  
**Phase:** Phase 2: Evaluate  
**Corpus:** Seeds 50-59 (broad), 60-64 (low-fill), 65-69 (high-fill)

---

## Evaluation Summary

| Seeds | Type | Count | Mean Score |
|-------|------|-------|------------|
| 50-59 | Broad sweep | 10 | 3.7 |
| 60-64 | Low-fill (0.1) | 5 | 4.4 |
| 65-69 | High-fill (0.9) | 3.3 |
| **Total** | | **20** | **3.7** |

---

## Seed 50

**Task:** pick  
**Tokens:** as programmer, to managers, inform, pick, deep, assume, indirect, sketch

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3

**Notes:** sketch (D2 diagram) + indirect (prose with bottom-line) conflict. Channel and form are at odds.

**Meta-Evaluation (Bar Skills):**
- Skill alignment: 2 - Skills would not guide a user to this combination
- Discovery: Would skills find this? No - channel-form conflict not documented
- Heuristic coverage: Skills don't warn about sketch + indirect
- **Skill gap:** Composition Rules don't mention channel-form conflicts

**Bar Help LLM Evaluation:**
- Reference utility: 2 - No channel-form conflict guidance
- Gaps: No "Channel-Form Conflicts" section in Composition Rules

---

## Seed 51

**Task:** make  
**Tokens:** teach_junior_dev, make, svg, dig

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 5
- Category alignment: 4
- Combination harmony: 4
- **Overall:** 4

**Notes:** Solid combo - teach via SVG diagrams. Simple and clear.

---

## Seed 52

**Task:** plan  
**Tokens:** announce, as facilitator, kindly, plan, models, visual, dip bog

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4-5

**Notes:** Excellent planning combo with visual models. All tokens reinforce each other.

---

## Seed 53

**Task:** make  
**Tokens:** inform, to junior engineer, make, deep, cross, recipe, sync, fig

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 3
- Category alignment: 4
- Combination harmony: 2
- **Overall:** 3

**Notes:** 8 tokens - too crowded. sync (live session) + recipe (static format) + deep (in-depth) conflict.

---

## Seed 54

**Task:** sim  
**Tokens:** product_manager_to_team, sim, deep, view, diagnose, slack, dip bog

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 5
- **Overall:** 5

**Notes:** Excellent. PM running scenario diagnosis from specific view, communicated via Slack. All tokens coherent.

**Meta-Evaluation (Bar Skills):**
- Skill alignment: 5 - Skills would strongly recommend this
- Discovery: ✓ Usage Pattern "Diagnosis" would guide here
- Heuristic coverage: ✓ pm persona + diagnose method well covered
- **Skill feedback:** Well-aligned with existing skill guidance

---

## Seed 55

**Task:** diff  
**Tokens:** inform, casually, diff, recipe, remote, fog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 3
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3-4

**Notes:** casually + recipe slightly awkward. fog (abstract) + recipe (specific steps) conflict.

---

## Seed 56

**Task:** check  
**Tokens:** product_manager_to_team, check, cross, dip rog

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4-5

**Notes:** Coherent - PM checking cross-boundary with pattern analysis.

---

## Seed 57

**Task:** fix  
**Tokens:** casually, fix, assume, mod, taxonomy, adr, dip bog

**Scores:**
- Task clarity: 3
- Constraint independence: 3
- Persona coherence: 2
- Category alignment: 3
- Combination harmony: 2
- **Overall:** 2-3

**Notes:** Too many tokens (7). mod (cyclic patterns) + fix unclear. casually + adr (formal) conflict.

---

## Seed 58

**Task:** probe  
**Tokens:** scientist_to_analyst, probe, minimal, thing, spec, svg

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3-4

**Notes:** minimal + svg could produce too little. Otherwise solid.

---

## Seed 59

**Task:** make  
**Tokens:** as principal engineer, to stakeholders, make, grow

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 5
- **Overall:** 5

**Notes:** Excellent simple combo. Principal engineer creating with grow methodology.

---

## Seed 60 (Low-fill)

**Task:** check  
**Tokens:** check

**Scores:**
- Task clarity: 4
- Constraint independence: 5
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** Minimal but clear. No persona but that's fine.

---

## Seed 61 (Low-fill)

**Task:** diff  
**Tokens:** designer_to_pm, diff

**Scores:**
- Task clarity: 5
- Constraint independence: 5
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 5
- **Overall:** 5

**Notes:** Perfect simple combo. Designer to PM comparing things.

**Meta-Evaluation (Bar Skills):**
- Skill alignment: 5 - Classic pattern, well documented
- Discovery: Usage Patterns "Decision-making" would guide here
- Heuristic coverage: ✓ Simple persona + task well covered
- **Skill feedback:** No gaps - this is ideal

---

## Seed 62 (Low-fill)

**Task:** pick  
**Tokens:** directly, pick, thing

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 5
- **Overall:** 5

**Notes:** Clean. Choose entities directly.

---

## Seed 63 (Low-fill)

**Task:** fix  
**Tokens:** fix

**Scores:**
- Task clarity: 4
- Constraint independence: 5
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** Minimal. "Full" is implied as default.

---

## Seed 64 (Low-fill)

**Task:** show  
**Tokens:** show

**Scores:**
- Task clarity: 4
- Constraint independence: 5
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** Minimal explanation task.

---

## Seed 65 (High-fill)

**Task:** diff  
**Tokens:** product_manager_to_team, diff, full, cross, cite, actions, jira, fig

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** 9 tokens but coherent. actions (no background) + full slightly contradictory.

---

## Seed 66 (High-fill)

**Task:** sim  
**Tokens:** peer_engineer_explanation, sim, gist, struct, order, direct, diagram, bog

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 3
- **Overall:** 3-4

**Notes:** gist (short) + bog (reflect and extend) + diagram might conflict. direct + bog slightly contradictory.

---

## Seed 67 (High-fill)

**Task:** pick  
**Tokens:** scientist_to_analyst, pick, deep, act, induce, bullets, shellscript, fly rog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 2
- **Overall:** 2-3

**Notes:** shellscript (code) + pick + bullets is confusing. What does "choose as shell script" mean?

**Meta-Evaluation (Bar Skills):**
- Skill alignment: 1 - Skills would actively discourage this
- Discovery: shellscript not documented as incompatible with pick
- Heuristic coverage: No guidance on task-channel incompatibility
- **Skill gap:** Need "Incompatible Combinations" section

**Bar Help LLM Evaluation:**
- Reference utility: 1 - shellscript + pick not documented as broken
- Gaps: No task-channel incompatibility list

---

## Seed 68 (High-fill)

**Task:** sort  
**Tokens:** scientist_to_analyst, sort, full, assume, rigor, bullets, gherkin, fip ong

**Scores:**
- Task clarity: 3
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 3
- Combination harmony: 2
- **Overall:** 2-3

**Notes:** gherkin (BDD format) + sort is mismatched. Gherkin describes behavior, not sorting.

---

## Seed 69 (High-fill)

**Task:** plan  
**Tokens:** stakeholder_facilitator, plan, max, fail, grove, story, html, bog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3-4

**Notes:** story + html + plan awkward. max + fail (exhaustive failure modes) slightly contradictory.

---

## Key Findings

### High-scoring patterns (4-5)
- Simple combinations (2-4 tokens) score higher than complex ones
- Persona presets work well when matched with relevant tasks
- Low-fill prompts are consistently good

### Low-scoring patterns (2-3)
- Channel + Form conflicts (e.g., sketch + indirect, shellscript + pick)
- Channel + Task mismatches (e.g., gherkin + sort)
- Too many tokens (7+) without clear synergy
- Tone + Format conflicts (e.g., casually + adr)

### Recommendations for Cycle-6

1. **R-05: Add channel-form conflict detection** to guide users away from conflicting combinations
2. **R-06: Document strong task-channel pairs** (e.g., diff + jira, make + svg)
3. **R-07: Consider deprecating certain channel-task combos** that don't compose well (gherkin + sort, shellscript + pick)

