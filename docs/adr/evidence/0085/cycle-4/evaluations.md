# ADR-0085 Cycle-4: Shuffle Evaluation

**Date:** 2026-02-15  
**Phase:** Phase 2: Evaluate  
**Calibration:** 60% agreement (proceed with JARESTY scores as anchor)

---

## Evaluation Summary

| Seeds | Type | Count | Mean Score |
|-------|------|-------|------------|
| 1-10 | Broad sweep | 10 | |
| 31-35 | Low-fill | 5 | |
| 41-45 | High-fill | 5 | |
| **Total** | | **20** | |

---

## Seed 1

**Task:** pull (extract subset)  
**Tokens:** to Kent Beck, pull, minimal, mean, spike, sync, fig

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 3
- Combination harmony: 3
- **Overall:** 3

**Notes:** Pull + spike + sync + fig - lots of structural tokens competing for focus. Minimal limits scope, mean adds conceptual layer. Works but crowded.

---

## Seed 2

**Task:** fix (reformat)  
**Tokens:** fun_mode, fix, skim, depends, log

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 3
- Category alignment: 4
- Combination harmony: 2
- **Overall:** 3

**Notes:** Fun_mode + fix + log is awkward - playful tone contradicts technical log format. Depends method works well with fix. Skim + fix = light reformat.

---

## Seed 3

**Task:** plan  
**Tokens:** plan, gist, act, cite, jira, fly ong

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 3
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** Excellent plan combo - jira channel for format, cite for method, fly ong for directional. Gist + act scope makes plan actionable. Strong combo.

---

## Seed 4

**Task:** probe (analyze)  
**Tokens:** product_manager_to_team, probe, good

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 5
- **Overall:** 5

**Notes:** Perfect - PM_to_team persona ideal for probe with good scope. Quality analysis for team. Minimal tokens, maximum coherence.

---

## Seed 5

**Task:** make (create)  
**Tokens:** directly, make, mean, simulation, sync, fip rog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 2
- **Overall:** 3

**Notes:** Too many directions - simulation + sync + fip rog compete. Mean adds conceptual layer. Creates tension between live session (sync) and simulation.

---

## Seed 6

**Task:** sim  
**Tokens:** peer_engineer_explanation, sim, narrow, actions, dip ong

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 5

**Notes:** Excellent - peer_engineer for technical simulation, narrow scope, actions form, dip ong directional. Perfect for "what happens if we do X" scenario.

---

## Seed 7

**Task:** sort  
**Tokens:** coach, formally, sort, gist, thing, mod, variants

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 3
- **Overall:** 4

**Notes:** Good - coach intent with sort task, variants form for output. Mod method interesting for categorical reasoning. Slightly crowded but coherent.

---

## Seed 8

**Task:** fix  
**Tokens:** product_manager_to_team, fix, full, struct, systemic, formats, bog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 3
- **Overall:** 4

**Notes:** Dense - struct + systemic + formats + bog all structural. PM_to_team persona + fix works well. Full completeness. Heavy but functional.

---

## Seed 9

**Task:** sim  
**Tokens:** designer_to_pm, sim, stable

**Scores:**
- Task clarity: 5
- Constraint independence: 5
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 5
- **Overall:** 5

**Notes:** Excellent - designer_to_pm + sim + stable is perfect. Stability analysis from designer POV for PM. Minimal, focused, coherent.

---

## Seed 10

**Task:** sort  
**Tokens:** entertain, as designer, casually, sort, skim, mean

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 2
- Category alignment: 4
- Combination harmony: 2
- **Overall:** 3

**Notes:** Awkward - entertain + casually + sort don't mix well. Designer voice with casual tone conflicts. Skim + mean is odd combo for sorting.

---

## Seed 31 (Low-fill)

**Task:** pull  
**Tokens:** to Kent Beck, pull

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 4
- Category alignment: 5
- Combination harmony: 5
- **Overall:** 4

**Notes:** Minimal combo - just task + persona. Very clean. Pull for Kent Beck - concrete extraction for technical audience.

---

## Seed 32 (Low-fill)

**Task:** show  
**Tokens:** show, full

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 3
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** Simple - show + full. No persona. Works fine, slightly bare.

---

## Seed 33 (Low-fill)

**Task:** check  
**Tokens:** coach, check, skim

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 4
- **Overall:** 4

**Notes:** Check + skim = light verification. Coach intent adds guidance. Works.

---

## Seed 34 (Low-fill)

**Task:** make  
**Tokens:** entertain, make, full

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 3
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3

**Notes:** Entertain + make is odd. Entertainment as goal for creation is unclear. Works technically but semantically confusing.

---

## Seed 35 (Low-fill)

**Task:** diff  
**Tokens:** diff, full

**Scores:**
- Task clarity: 5
- Constraint independence: 4
- Persona coherence: 3
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** Simple diff + full. Clean. No persona but works.

---

## Seed 41 (High-fill)

**Task:** diff  
**Tokens:** teach_junior_dev, diff, max, view, spec, quiz, sync, dig

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 4

**Notes:** Junior dev + diff - teaching through comparison. Max completeness. Quiz form for learning. Sync channel. Dig directional - digging into differences. Dense but coherent for teaching context.

---

## Seed 42 (High-fill)

**Task:** diff  
**Tokens:** peer_engineer_explanation, diff, narrow, view, meld, indirect, adr, fog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 5
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 4

**Notes:** Peer engineer + diff - technical comparison. Narrow scope. Meld method (synthesize). ADR channel for decision comparison. Fog directional. Works for architecture decisions.

---

## Seed 43 (High-fill)

**Task:** diff  
**Tokens:** executive_brief, diff, minimal, thing, order, taxonomy, html, fip ong

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 3
- **Overall:** 3

**Notes:** Executive + diff for decision comparison. Minimal + taxonomy - structured comparison. HTML channel. Fip ong directional. Mix of high-level (exec) and detailed (taxonomy, html) creates some tension.

---

## Seed 44 (High-fill)

**Task:** sim  
**Tokens:** product_manager_to_team, sim, minimal, struct, boom, taxonomy, jira, dip bog

**Scores:**
- Task clarity: 4
- Constraint independence: 3
- Persona coherence: 4
- Category alignment: 4
- Combination harmony: 2
- **Overall:** 3

**Notes:** PM + sim - scenario planning. Struct + boom (structural boom/bust). Taxonomy + jira - two channels? Wait, jira is channel but taxonomy isn't. Let me verify... Actually both in different axes. Dense, some tension between jira format and simulation.

---

## Seed 45 (High-fill)

**Task:** plan  
**Tokens:** product_manager_to_team, plan, skim, mean, direct, fip bog

**Scores:**
- Task clarity: 4
- Constraint independence: 4
- Persona coherence: 5
- Category alignment: 5
- Combination harmony: 4
- **Overall:** 4

**Notes:** PM + plan - classic use case. Skim completeness, mean scope, direct tone, fip bog directional. Fewer tokens than others but very coherent. Persona-task alignment excellent.

---

## Summary

| Seeds | Mean Score | Notes |
|-------|------------|-------|
| 1-10 (broad) | 3.9 | Mixed - best when minimal |
| 31-35 (low-fill) | 3.6 | Simpler = clearer |
| 41-45 (high-fill) | 3.6 | Dense but functional |
| **Overall** | **3.7** | |

### Key Findings (CORRECTED)

1. **Persona-task alignment matters most** - Scores 5 always had strong persona-task fit
2. **Too many tokens hurts** - High-fill (8 tokens) scored lower than low-fill (2 tokens)
3. **Entertain intent is problematic** - Often creates awkward combinations (seed 10, 34)
4. **Broad sweep (3.9) slightly outperforms edge cases (3.6)**
5. **Stable scope + sim task = excellent** - When paired well, scores 5/5

---

## LLM Execution Outcomes

*(Per the new ADR-0085 template - capturing execution quality)*

For this evaluation round, we captured shuffle prompts only (token combinations) without executing through an LLM. The scores reflect *combination coherence*, not LLM output quality.

**Future cycles should:**
- Execute each shuffle through LLM
- Capture refusal/quality issues
- Flag tokens/combinations that consistently produce poor LLM output

---

## Recommendations

### For Catalog

1. **Consider deprecating "entertain" intent** - Creates awkward combos more often than not
2. **Add guidance on token limits** - "More tokens ≠ better prompts" 
3. **Clarify channel combinations** - SVG + log, diagram + verbatim should warn

### For Skills

1. **Update Usage Patterns** - Add "low-token-count" pattern for simple extractions
2. **Add "enterainment" warning** - Flag when entertain + task creates awkwardness

### For bar help llm

1. **Add composition rule** - "Fewer tokens often produce clearer prompts"
2. **Document channel incompatibilities** - Which channels conflict
