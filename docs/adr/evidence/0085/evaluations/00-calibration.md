# ADR-0085 Calibration

**Date:** 2026-02-15  
**Evaluators:** jaresty (human) + claude (assistant)  
**Phase:** Phase 0: Calibrate

---

## Calibration Prompts

### Seed 1

**Task:** The response selects or extracts a subset of the given information without altering its substance.

**Tokens:** to Kent Beck, pull, minimal, mean, spike, sync, fig

---

### Seed 2

**Task:** The response changes the form or presentation of given content while keeping its intended meaning.

**Tokens:** fun_mode, fix, skim, depends, log

---

### Seed 3

**Task:** The response proposes steps, structure, or strategy to move from the current state toward a stated goal.

**Tokens:** plan, gist, act, cite, jira, fly ong

---

### Seed 4

**Task:** The response analyzes the subject to surface structure, assumptions, or implications beyond restatement.

**Tokens:** product_manager_to_team, probe, good

---

### Seed 5

**Task:** The response creates new content that did not previously exist, based on the input and constraints.

**Tokens:** directly, make, mean, simulation, sync, fip rog

---

### Seed 6

**Task:** The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.

**Tokens:** peer_engineer_explanation, sim, narrow, actions, dip ong

---

### Seed 7

**Task:** The response arranges items into categories or an order using a specified or inferred scheme.

**Tokens:** coach, formally, sort, gist, thing, mod, variants

---

### Seed 8

**Task:** The response changes the form or presentation of given content while keeping its intended meaning.

**Tokens:** product_manager_to_team, fix, full, struct, systemic, formats, bog

---

### Seed 9

**Task:** The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.

**Tokens:** designer_to_pm, sim, stable

---

### Seed 10

**Task:** The response arranges items into categories or an order using a specified or inferred scheme.

**Tokens:** entertain, as designer, casually, sort, skim, mean

---

## Scoring Rubric

For each prompt, score 1-5 on each dimension:

| Dimension | 1 | 2 | 3 | 4 | 5 |
|-----------|---|---|---|---|---|
| **Task clarity** | Unclear what success looks like | Partial clarity | Adequate but rough | Clear intent | Fully explicit |
| **Constraint independence** | Redefines the task | Heavily constrains task | Moderate constraint | Minor constraint | Shapes HOW only |
| **Persona coherence** | Contradicts task | Awkward fit | Acceptable | Good fit | Perfect match |
| **Category alignment** | Wrong axis | Mostly wrong | Mixed | Mostly correct | All correct |
| **Combination harmony** | Fighting each other | Significant friction | Some tension | Works well | Reinforces |

**Pre-flight check:** Before scoring, verify:
- Each token is in the correct axis (check axisConfig or grammar)
- Multi-token axes respect their caps (scope≤2, method≤3, channel=1, form=1, directional=1)
- If claiming "conflict" or "incompatibility," verify the grammar allows the combination first

**Overall:** Average of 5 dimensions

---

## Evaluator Scores

### JARESTY (human)

| Seed | Task clarity | Constraint ind. | Persona coherence | Category align. | Combo harmony | Overall |
|------|--------------|-----------------|-------------------|-----------------|---------------|---------|
| 1 | 4 | 3 | 4 | 3 | 3 | 3 |
| 2 | 4 | 3 | 3 | 4 | 2 | 3 |
| 3 | 5 | 4 | 3 | 5 | 4 | 4 |
| 4 | 5 | 4 | 4 | 5 | 5 | 5 |
| 5 | 4 | 3 | 4 | 4 | 2 | 3 |
| 6 | 5 | 4 | 5 | 5 | 4 | 5 |
| 7 | 4 | 4 | 4 | 5 | 3 | 4 |
| 8 | 4 | 3 | 4 | 5 | 3 | 4 |
| 9 | 5 | 5 | 5 | 5 | 5 | 5 |
| 10 | 4 | 3 | 2 | 4 | 2 | 3 |

**Mean:** 3.9/5

---

### Subagent (LLM)

| Seed | Task clarity | Constraint ind. | Persona coherence | Category align. | Combo harmony | Overall |
|------|--------------|-----------------|-------------------|-----------------|---------------|---------|
| 1 | 4 | 3 | 4 | 3 | 3 | 3 |
| 2 | 4 | 4 | 2 | 3 | 3 | 3 |
| 3 | 4 | 4 | 3 | 4 | 4 | 4 |
| 4 | 4 | 4 | 2 | 4 | 4 | 3 |
| 5 | 4 | 3 | 3 | 4 | 3 | 3 |
| 6 | 4 | 4 | 5 | 4 | 4 | 4 |
| 7 | 4 | 4 | 4 | 4 | 4 | 4 |
| 8 | 4 | 3 | 2 | 3 | 2 | 3 |
| 9 | 4 | 4 | 4 | 4 | 4 | 4 |
| 10 | 4 | 4 | 2 | 3 | 3 | 3 |

**Mean:** 3.4/5

---

## Agreement Analysis

**JARESTY scores:** 3, 3, 4, 5, 3, 5, 4, 4, 5, 3  
**Subagent scores:** 3, 3, 4, 3, 3, 4, 4, 3, 4, 3

**Agreement rate:** 6/10 = 60%  
**Score delta average:** 0.5

### Disagreements

| Seed | JARESTY | Subagent | Delta | Issue |
|------|---------|----------|-------|-------|
| 4 | 5 | 3 | -2 | Persona coherence - JARESTY saw PM_to_team + probe + good as excellent; subagent saw it differently |
| 6 | 5 | 4 | -1 | JARESTY scored higher on sim + narrow + actions combo |
| 8 | 4 | 3 | -1 | Fix + full + struct + systemic - JARESTY more generous |
| 9 | 5 | 4 | -1 | Sim + stable + designer_to_pm - both high but JARESTY perfect |

---

## Resolution

- [x] **Below 80% — discuss and re-score**
- [ ] Calibrated (agreement ≥ 80%)

### Discussion

The 60% agreement is below the 80% threshold. Key differences:

1. **Task clarity**: Both consistently scored 4-5 — high agreement
2. **Constraint independence**: JARESTY slightly more generous (3-5 vs 3-4)
3. **Persona coherence**: Main source of disagreement — subagent more critical
4. **Category alignment**: JARESTY scored higher (4-5 vs 3-4)
5. **Combination harmony**: Similar pattern to persona coherence

**Root cause**: The subagent was more conservative/critical in scoring, particularly on persona coherence and category alignment. JARESTY gave "benefit of the doubt" to ambiguous combinations.

### Rubric Clarification

For future calibrations:
- **Persona coherence**: Score based on whether persona *could* work, not whether it's the *best* choice
- **Category alignment**: If tokens are in correct axes, score 4-5 even if combination is unusual
- **Combination harmony**: Focus on whether tokens fight each other, not whether they're optimal

**Decision**: Proceed with JARESTY scores as the anchor. The subagent provides useful secondary signal but the human evaluator's context wins for borderline cases.
