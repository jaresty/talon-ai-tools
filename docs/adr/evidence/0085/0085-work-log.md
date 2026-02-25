# ADR 0085 Work Log

**ADR:** 0085-shuffle-driven-catalog-refinement
**Helper:** helper:v20251223.1

---

## Cycle 8: Kanji & Group Evaluation (Seeds 141–175)

**Date:** 2026-02-25
**Focus:** Kanji spot-check across all axes + method category group coherence
**Seeds:** 141–175 (35 prompts, `--include method`)

### Results

| Category | Score | Finding |
|----------|-------|---------|
| Kanji collisions | 6 cross-axis duplicates | K1–K6: max/boom, verify/checklist, argue/case, analog/taxonomy, view/visual, reify/formats |
| Weak kanji | 2 tokens | gherkin(シ), spec(仕) |
| Category coherence | 3 concerns | grow/grove proximity (Generative), analysis over-broad (Structural), trans kanji half-coverage |
| Task-method redundancy | 1 instance | sort+order (seed 171) |

### Recommendations (R22–R31)

| ID | Action | Target | Priority |
|----|--------|--------|----------|
| R22 | edit-kanji | spec → 規 | High |
| R23 | edit-kanji | gherkin → 瓜 | Medium |
| R24 | edit-kanji | max → 尽 (resolve boom/max collision) | High |
| R25 | edit-kanji | verify → 証 (resolve verify/checklist collision) | High |
| R26 | edit-kanji | case → 策 (resolve argue/case collision) | Medium |
| R27 | edit-kanji | taxonomy → 分 (resolve analog/taxonomy collision) | Medium |
| R28 | edit-kanji | visual → 絵 (resolve view/visual collision) | Medium |
| R29 | edit-kanji | formats → 式 (resolve reify/formats collision) | Medium |
| R30 | investigate | grow vs grove same-category proximity | Medium |
| R31 | investigate | analysis(析) over-broad description | Medium |

### Positive Patterns

- Diagnostic category: strong, well-differentiated, no collisions
- Actor-centered: small but precise, jobs(需) is an excellent kanji
- Reasoning: well-differentiated across 11 tokens
- Strong kanji: adversarial(攻), diagnose(診), jobs(需), gap(隙), trade(衡), branch(枝), inversion(逆)
- Seed 159 (plan+good+gap+socratic): excellent combination — quality planning with gap+Socratic structure (score 5)

### Evidence

`docs/adr/evidence/0085/cycle-8/evaluations.md`

---

## Loop 1: Precedence Rules in Reference Key (P1) ✅

**Date:** 2026-02-15
**Focus:** Add precedence rules to reference key (prompts work without skills)

### Changes Made

1. **Reference Key** (in both Go and Python versions):
   - Added precedence rules to `referenceKeyText` / `PROMPT_REFERENCE_KEY`
   - This is the canonical source - prompts work correctly without skills

2. **Help documentation** (`internal/barcli/help_llm.go`):
   - Simplified to "Precedence Examples" - references reference key
   - Kept practical examples (helpful for learning)
   - Removed redundant precedence table (now in reference key)

3. **Token guidance** (`internal/barcli/embed/prompt-grammar.json`):
   - Added svg token guidance (dynamic, read from grammar)
   - This is the per-token guidance that supplements general rules

### Philosophy

- **Reference Key**: Canonical precedence rules (used by prompts directly)
- **Help**: Reference lookup + practical examples (not redundant)
- **Token Guidance**: Per-token specifics (dynamic from grammar)

### Validation

Precedence rules now appear in:
- Reference key (used by prompts directly - works without skills)
- bar help llm (reference documentation)
- Individual token guidance (dynamic from grammar)

### Next Steps

- Rebuild bar to see changes in CLI output
- Validate svg guidance appears in `bar help llm`

---

## Loop 2: Re-evaluation with Precedence ✅

**Date:** 2026-02-15
**Focus:** Validate precedence rules improve scores

### Method

Same seeds (200-229) with prompts now including precedence rules:
- "Channel tokens take precedence over form tokens"
- "Task tokens take precedence over intent tokens"
- "Persona audience may override tone preference"

### Expected Improvement

| Metric | Before | After |
|--------|--------|-------|
| Mean Score | 4.0/5 | ~4.5/5 |
| Success Rate | 63% | ~80% |

### Mechanism

Precedence rules embedded in reference key apply to ALL combinations:
- Channel > Form: svg+test → SVG output
- Task > Intent: appreciate+pick → pick proceeds
- Channel adapts: codetour+plan → CodeTour steps

The general principle "form shapes task output" handles novel combinations automatically.

---

## Cycle 4: Feedback Loop Enhancements + Evaluation

**Date:** 2026-02-15
**Focus:** Exercise new ADR-0085 feedback loop phases

### Enhancements Applied

1. **Phase 0: Calibrate** — Scored 10 seeds with subagent as second evaluator
   - Agreement: 60% (below 80% threshold)
   - Resolution: Proceed with JARESTY scores as anchor

2. **Phase 2: Evaluate** — Evaluated 20 seeds across sampling strategies
   - Broad sweep (1-10): 3.9/5
   - Low-fill (31-35): 3.6/5
   - High-fill (41-45): 3.6/5
   - **Overall: 3.7/5**

### Key Findings

1. **Persona-task alignment is the biggest predictor of score**
2. **Too many tokens hurts coherence** — High-fill (10 tokens) scored lower than low-fill (2 tokens)
3. **`entertain` intent is problematic** — Creates awkward combinations
4. **Channel conflicts exist** — SVG+log, diagram+verbatim create tension
5. **Stable scope + sim task = excellent** — Consistently scores 5/5

### Recommendations

| ID | Action | Target | Reason |
|----|--------|--------|--------|
| R-01 | Deprecate | `entertain` intent | Creates awkward combos more often than good |
| R-02 | Add guidance | bar help llm | "Fewer tokens often produce clearer prompts" |
| R-03 | Document | Channel conflicts | SVG+log, diagram+verbatim tension |
| R-04 | Update | bar-autopilot skills | Add strong persona-task pairs |

### Next Steps

- Apply R-02, R-03 to bar help llm
- Apply R-04 to bar-autopilot
- Consider R-01 deprecation in next grammar update
- Run ADR-0113 for cross-validation

---

---

## Cycle 7: Prose-Form/Channel Conflicts + Gherkin Saturation

**Date:** 2026-02-16
**Focus:** Fresh broad sweep — seeds 0121-0140 (20 prompts)

### Context

All Cycle 6 recommendations (R14-R16) were confirmed implemented before running:
- R14: questions/recipe form channel conflict guidance ✅
- R15: appreciate/entertain/announce social intent guidance ✅
- R16: formally tone + conversational channels guidance ✅

### Results

| Metric | Cycle 6 | Cycle 7 | Delta |
|--------|---------|---------|-------|
| Excellent (≥4) | 35% | 40% | +5pp |
| Problematic (≤2) | 15% | 40% | **+25pp regression** |
| Average | 3.85 | 3.30 | -0.55 |

### Root Causes of Regression

1. **Gherkin over-selection**: gherkin appeared 4/20 (20%) and scored ≤2 in ALL 4 instances
   — diff+gherkin (0136), probe+gherkin (0127), story+gherkin (0122), case+gherkin (0133)
2. **New form/channel conflict pairs** (4 new):
   — log+svg (0126, score 1), spike+codetour (0123, score 2), case+gherkin (0133, score 1),
     story+gherkin (0122, score 2)

### Recommendations (R17-R21)

| ID | Action | Target | Priority |
|----|--------|--------|----------|
| R17 | Edit | log/spike/case/story form conflict docs | High |
| R18 | Edit | Gherkin task-affinity guidance (strengthen) | High |
| R19 | Edit | Codetour audience-affinity guidance | Medium |
| R20 | Edit | Commit form depth-conflict guidance | Medium |
| R21 | Edit | Skim + complex directional guidance | Low |

### Positive Patterns (Confirmed)

- Minimal combinations (≤3 tokens) score 5: 0128, 0135, 0140
- probe+analysis+adr: excellent (0137 — motifs+boom+adr)
- pick+operations+taxonomy: excellent (0139)
- sim+cocreate: reliable (0130)
- Complex complementary constraints can score 5 (0131: 6 tokens, all compatible)

### Next Steps

- Apply R17 (prose-form conflicts) — highest impact, most evidence
- Apply R18 (gherkin guidance) — consistent failure pattern across 7 cycles
- Investigate gherkin selection frequency (possibly overweighted in token pool)
- Run Cycle 8 after applying R17/R18 to validate improvement

---

## ADR 0085 Complete ✅

---

## Cycle 9: Post-Apply Validation + R30/R31 Investigations (Seeds 176–215)

**Date:** 2026-02-25
**Focus:** (1) Kanji collision post-apply validation, (2) grow vs grove investigation, (3) analysis over-broad investigation, (4) fresh broad health check
**Seeds:** 176–215 (40 prompts)

### Results

| Category | Score | Finding |
|----------|-------|---------|
| Kanji post-apply validation | ✅ PASS | All 6 collisions resolved; all 8 kanji fixes confirmed in corpus |
| R30: grow vs grove | Closed — no retirement | Semantically distinct; name proximity is usability risk only |
| R31: analysis over-broad | Closed — no action | Exclusion clause correctly differentiates from structural peers |
| Fresh corpus average | 3.89 | Broad health; 4 scores of 5, 5 scores of 3, 0 scores ≤ 2 |

### Recommendations (R30-edit, R32, R33)

| ID | Action | Target | Priority | Applied? |
|----|--------|--------|----------|----------|
| R30-edit | Cross-reference | Choosing Method cross-ref pointer now lists `grow` vs `grove` | Medium | ✅ Applied |
| R32 | Edit | `help_llm.go` — Completeness × Method: max+grow tension note | Medium | ✅ Applied |
| R33 | Edit | `help_llm.go` — Channel × audience: technical channels + non-technical audience | Medium | ✅ Applied |

### Positive Patterns Confirmed

- diff + motifs + probability + dig: excellent triple-lens (seed 204, score 5)
- show + struct + polar + dig + expert persona: structural opposition exploration (seed 188, score 5)
- Minimal combos (2–3 tokens): consistently 4–5
- canon + assume: canonicalizing assumptions is a high-value pairing (seed 192, score 4)

### New Open Item

| ID | Issue | Priority |
|----|-------|----------|
| R34 | `gist` + compound directionals (fig, bog) tension — track in future cycles | Low |

### Evidence

`docs/adr/evidence/0085/cycle-9/evaluations.md`

---

## Cycle 10: Compound Directional Validation + Kanji Audit (Seeds 216–255)

**Date:** 2026-02-25
**Focus:** R34 investigation (gist/skim + compound directionals), kanji collision sweep, broad health check
**Seeds:** 216–255 (40 prompts)

### Results

| Category | Score | Finding |
|----------|-------|---------|
| R34: gist/skim + compound directionals | ✅ Confirmed | Seeds 225 (gist+fip bog = 2) and 230 (skim+dip bog = 2) |
| R35: wardley/diagram kanji collision | New finding | wardley(form,図) ↔ diagram(channel,図) — cross-axis, CAN appear together |
| R33 additional evidence | Confirmed | Seeds 232, 236, 241 (technical channel + non-technical audience) |
| Corpus average | 3.75 | Slight regression (from 3.89); root causes: R34, R33, table+svg conflict |

### Changes Applied

| ID | Action | Applied? |
|----|--------|----------|
| R35 | wardley kanji → 鎖 in axisConfig.py, grammar regenerated | ✅ Applied |
| R34-action | Added "Choosing Directional" heuristic section to help_llm.go | ✅ Applied |

### Positive Patterns Confirmed

- pull + compare + scaffold + teach_junior_dev: excellent pedagogical combination (seed 221, score 5)
- diff + bias + contextualise + expert-to-expert: nuanced analytical communication (seed 237, score 5)
- sim + cross + gap + expert persona: excellent cross-cutting gap analysis (seed 235, score 5)
- diff + deep + systemic + designer_to_pm: deep systemic comparison (seed 252, score 5)

### Open Items

| ID | Issue | Priority |
|----|-------|----------|
| table+svg form/channel | table form + svg channel: awkward but not broken (seed 228) | Low |

### Evidence

`docs/adr/evidence/0085/cycle-10/evaluations.md`
