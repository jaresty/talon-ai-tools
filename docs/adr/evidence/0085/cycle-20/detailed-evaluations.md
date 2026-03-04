# ADR-0085 Cycle 20: Detailed Phase 2 Evaluations

**Date:** 2026-03-03
**Bar version:** 2.67.0
**Dev repo ahead of binary:** Unknown (need to check)

---

## Seed 616: sort + full + fip rog

**Tokens selected:**
- task: sort
- completeness: full
- directional: fip rog
- form: null
- channel: null
- scope: null
- method: null
- persona: none

**Generated prompt preview:**
> TASK: sort / full completeness / fip rog directional

**Cross-axis composition check:**
- No CROSS_AXIS_COMPOSITION entries for sort task, full completeness, or fip rog directional
- No cautionary or natural pairings to check

**Scores (vs Prompt Key):**
- Task clarity: 5 — sort clearly defined
- Constraint independence: 5 — fip rog shapes HOW without redefining WHAT
- Persona coherence: N/A — no persona
- Category alignment: 5 — all tokens correct
- Combination harmony: 5 — full + compound directional works well
- Method category coherence: N/A — no method token
- **Overall: 5**

**Meta-Evaluation (vs Bar Skills):**
- Skill alignment: 5 — simple combination well-covered
- Skill discoverability: 5 — sort task + directional obvious
- Heuristic coverage: 5 — covered
- Documentation completeness: 5 — all tokens documented
- **Meta overall: 5**

**Bar Help LLM Reference Evaluation:**
- Cheat sheet utility: 5
- Description clarity: 5
- Selection guidance: 5
- Pattern examples: 5
- Cross-axis composition coverage: N/A — no cross-axis tokens
- **Reference overall: 5**

**Notes:** Clean, simple combination. No issues.

**Recommendations:** None

---

## Seed 626: make + deep + story + presenterm

**Tokens selected:**
- task: make
- completeness: deep
- form: story
- channel: presenterm

**Generated prompt preview:**
> TASK: make / deep completeness / story form / presenterm channel

**Cross-axis composition check:**
- channel=presenterm has entry in CROSS_AXIS_COMPOSITION
  - task: natural [make, show, plan, pull] — make is natural ✓
  - completeness: natural [minimal, gist]; cautionary [max, deep] — deep is cautionary!
- Checking presenterm + deep: "same constraint as max — slide format cannot accommodate deep analysis; use minimal or gist instead"

**Scores (vs Prompt Key):**
- Task clarity: 4 — make is clear
- Constraint independence: 4 — constraints shape how
- Persona coherence: N/A
- Category alignment: 4 — tokens correct
- Combination harmony: 3 — deep + presenterm is cautionary per CROSS_AXIS_COMPOSITION
- Method category coherence: N/A
- **Overall: 3**

**Meta-Evaluation (vs Bar Skills):**
- Skill alignment: 4 — make task is well-documented
- Skill discoverability: 4 — presenterm + story available
- Heuristic coverage: 4
- Documentation completeness: 4 — guidance exists but may not surface in skills
- **Meta overall: 4**

**Bar Help LLM Reference Evaluation:**
- Cheat sheet utility: 4
- Description clarity: 4
- Selection guidance: 3 — deep + presenterm tradeoff not prominently surfaced
- Pattern examples: 4
- Cross-axis composition coverage: 3 — presenterm + deep is cautionary but buried
- **Reference overall: 4**

**Cautionary combination detected:**
- Axis / token: channel/presenterm
- Paired: completeness/deep
- Warning: "same constraint as max — slide format cannot accommodate deep analysis; use minimal or gist instead"
- Exclude from token retirement aggregation: ✓

**Notes:** This is a new finding - presenterm + deep was not documented as problematic in prior cycles. The CROSS_AXIS_COMPOSITION has this as cautionary but it's not surfaced prominently.

**Skill Feedback:**
- bar-autopilot § Usage Patterns should warn against presenterm + deep combo

**Help LLM Feedback:**
- presenterm Composition Rules section should prominently warn about deep/max completeness

**Recommendations:**
- [ ] edit: presenterm - add prominent warning about deep/max completeness incompatibility

---

## Seed 632: pull + skim + fly bog + scaffold (R36)

**Tokens selected:**
- task: pull
- completeness: skim
- directional: fly bog
- form: scaffold

**Generated prompt preview:**
> TASK: pull / skim completeness / fly bog directional / scaffold form

**Cross-axis composition check:**
- completeness=skim has entry in CROSS_AXIS_COMPOSITION
  - directional: cautionary [fig, bog, fly-ong, fly-rog, fly-bog, fip-ong, fip-rog, fip-bog, dip-ong, dip-rog, dip-bog]
- fly bog is in the cautionary list ✓

**Cautionary combination detected:**
- Axis / token: completeness/skim
- Paired: directional/fly bog
- Warning: "compound directional requires sustained examination skim cannot provide; use full or deep instead"
- Exclude from token retirement aggregation: ✓

**Scores (vs Prompt Key):**
- Task clarity: 4
- Constraint independence: 3 — skim + compound directional is in tension
- Persona coherence: 4 — fun_mode + scaffold is coherent
- Category alignment: 5
- Combination harmony: 2 — skim + fly bog is known cautionary
- Method category coherence: N/A
- **Overall: 2**

**Meta-Evaluation (vs Bar Skills):**
- Skill alignment: 4 — R36 guidance exists
- Skill discoverability: 4
- Heuristic coverage: 4
- Documentation completeness: 4
- **Meta overall: 4**

**Bar Help LLM Reference Evaluation:**
- Cheat sheet utility: 4
- Description clarity: 5
- Selection guidance: 4
- Pattern examples: 4
- Cross-axis composition coverage: 5 — skim + compound directional covered
- **Reference overall: 4**

**Notes:** R36 hit - documented in cycle 11. No new action.

**Recommendations:** None — R36 documented

---

## Seed 635: sort + skim + diagnose + dip ong + wardley (R36)

**Tokens selected:**
- task: sort
- completeness: skim
- method: diagnose (Diagnostic category)
- directional: dip ong
- form: wardley

**Cross-axis composition check:**
- completeness=skim has entry (see seed 632)
- dip ong is in skim's cautionary directional list ✓

**Cautionary combination detected:**
- Axis / token: completeness/skim
- Paired: directional/dip ong
- Warning: from CROSS_AXIS_COMPOSITION
- Exclude from token retirement aggregation: ✓

**Scores (vs Prompt Key):**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: N/A
- Category alignment: 4
- Combination harmony: 2 — skim + compound directional
- Method category coherence: 5 — single Diagnostic method
- **Overall: 2**

**Notes:** R36 second hit this cycle. Documented, no new action.

**Recommendations:** None — R36 documented

---

## Seed 639: pick + full + shellscript (R40)

**Tokens selected:**
- task: pick
- completeness: full
- channel: shellscript
- persona: designer_to_pm

**Cross-axis composition check:**
- channel=shellscript has entry in CROSS_AXIS_COMPOSITION
  - task: natural [make, fix, show, trans, pull]; cautionary [sim, probe]
  - pick is NOT in natural or cautionary — so it's unlisted
  - Per ADR guidance: check AXIS_KEY_TO_GUIDANCE prose for form-as-lens rescues
- shellscript guidance says: "Avoid with selection tasks (pick, diff, sort) — these don't produce code"

**Scores (vs Prompt Key):**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 4 — designer_to_pm reasonable
- Category alignment: 5
- Combination harmony: 2 — shellscript + pick is known problematic
- Method category coherence: N/A
- **Overall: 2**

**Meta-Evaluation (vs Bar Skills):**
- Skill alignment: 3 — shellscript + pick not prominently warned against in skills
- Skill discoverability: 3
- Heuristic coverage: 3 — skills don't surface this incompatibility
- Documentation completeness: 4
- **Meta overall: 3**

**Bar Help LLM Reference Evaluation:**
- Cheat sheet utility: 4
- Description clarity: 4
- Selection guidance: 3 — shellscript task compatibility not prominent
- Pattern examples: 3
- Cross-axis composition coverage: 4 — documented but could be more prominent
- **Reference overall: 4**

**Notes:** R40 fourth data point. shellscript + pick is a grammar gap - documented but not enforced.

**Skill Feedback:**
- bar-autopilot § shell script guidance should warn about pick/diff/sort tasks

**Recommendations:**
- [ ] tracking: R41-grammar-hardening — cross-axis incompatibility enforcement deferred

---

## Seed 646: pick + deep + struct + dig + recipe

**Tokens selected:**
- task: pick
- completeness: deep
- scope: struct
- method: dig
- form: recipe

**Cross-axis composition check:**
- No CROSS_AXIS_COMPOSITION entries for these tokens

**Scores (vs Prompt Key):**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: N/A
- Category alignment: 5
- Combination harmony: 4
- Method category coherence: 5 — single Diagnostic method
- **Overall: 4**

**Meta-Evaluation (vs Bar Skills):**
- Skill alignment: 5
- Skill discoverability: 5
- Heuristic coverage: 5
- Documentation completeness: 5
- **Meta overall: 5**

**Bar Help LLM Reference Evaluation:**
- Cheat sheet utility: 5
- Description clarity: 5
- Selection guidance: 5
- Pattern examples: 5
- Cross-axis composition coverage: N/A
- **Reference overall: 5**

**Notes:** Excellent combination. No issues.

**Recommendations:** None

---

## Summary of Detailed Evaluations

| Seed | Score | Key Finding |
|------|-------|-------------|
| 616 | 5 | Clean |
| 626 | 3 | **New:** presenterm + deep is cautionary (not previously surfaced) |
| 632 | 2 | R36 (documented) |
| 635 | 2 | R36 (documented) |
| 639 | 2 | R40 fourth data point |
| 646 | 4 | Clean |

**New findings:**
- presenterm channel + deep completeness produces suboptimal output per CROSS_AXIS_COMPOSITION but not prominently surfaced in skills or help

**R36/R40 status:** Documented, no new action

**Recommendations:**
- [ ] edit: presenterm - add prominent warning about deep/max completeness incompatibility to help llm
