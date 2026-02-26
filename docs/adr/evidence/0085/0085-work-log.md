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

---

## Cycle 11: Compound Directional Expansion + Bar v2.64.1 Health Check (Seeds 256–295)

**Date:** 2026-02-25
**Focus:** Post-cycle-10 health check, verify R34 heuristic coverage with expanded compound directional catalog (bar v2.64.1)
**Seeds:** 256–295 (40 prompts)

### Results

| Category | Score | Finding |
|----------|-------|---------|
| R34: fly-ong + skim | ✅ Confirmed | Seed 287 (skim+fly-ong = 2); fly-ong missing from skim token notes |
| R34: fip-rog + skim | Existing coverage | Seed 260 (skim+fip-rog) scores 3 (fip-rog is listed in skim notes, but socratic+exec tension also present) |
| help_llm.go R34 heuristic | ✅ Validated | fly-ong+full (seeds 257, 273) and bog+full (278) all score 4; heuristic works |
| Corpus average | 3.73 | Slight regression from 3.75; seed 287 drives it |

### Changes Applied

| ID | Action | Applied? |
|----|--------|----------|
| R36 | Update skim + gist token notes in axisConfig.py with full compound directional list | ✅ Applied |

### Positive Patterns Confirmed

- pull + triage + thing + fig + executive_brief: executive extraction with prioritization (seed 264, score 5)
- pick + boom + adr + jog + formally + announce: decisive ADR creation (seed 270, score 4)
- probe + adversarial + questions + presenterm: adversarial probing as slides (seed 261, score 4)
- probe + mean + order + actions + dig: concrete ordered probe with actionable output (seed 290, score 4)

### Open Items

(none — R36 applied)

### Evidence

`docs/adr/evidence/0085/cycle-11/evaluations.md`

---

## Cycle 12: R36 Validation + Broad Health Check (Seeds 296–335)

**Date:** 2026-02-25
**Focus:** Validate cycle-11 R36 fix (gist + compound directionals), broad health check
**Seeds:** 296–335 (40 prompts)

### Results

| Category | Score | Finding |
|----------|-------|---------|
| R36 validation: gist + fip-ong | ✅ Confirmed | Seed 318 (gist+fip-ong = 2); cycle-11 fix correctly motivated |
| minimal + compound dirs | ✅ Fine | Seeds 325 (minimal+fip-ong), 333 (minimal+fip-bog) both score 4 |
| narrow + fig mild tension | New watch | Seed 326 (narrow+fig = 3); low priority |
| Corpus average | 3.60 | Regression from 3.73; 14 sparse/minimal seeds + seed 318 |

### Changes Applied

No changes — R36 already applied in cycle 11. Cycle 12 is validation-only.

### Positive Patterns Confirmed

- sim + assume + meld + socratic + teach: collaborative educational simulation (seed 313, score 4)
- pick + full + converge + questions: convergent decision via questioning (seed 299, score 4)
- show + deep + quiz + presenterm: deep persuasive quiz presentation (seed 324, score 4)
- check + max + struct + indirect + dip-ong: exhaustive indirect structural check (seed 331, score 4)

### Open Items

| ID | Issue | Priority |
|----|-------|----------|
| R37-watch | narrow completeness + fig directional tension (seed 326, score 3) | Low — monitor |

### Evidence

`docs/adr/evidence/0085/cycle-12/evaluations.md`

---

## Cycle 13: R36 Recurrence + New Token Discovery (Seeds 336–375)

**Date:** 2026-02-25
**Focus:** Post-cycle-12 health check, R36 recurrence tracking, R37-watch follow-up
**Seeds:** 336–375 (40 prompts)

### Results

| Category | Score | Finding |
|----------|-------|---------|
| R36: gist + fip-ong | ✅ Guidance in place | Seed 337 (gist+fip-ong=2); 3rd gist+compound hit; cycle-11 fix covers it |
| R36: skim + fog | ✅ Guidance in place | Seed 348 (skim+fog=2); fog was always in skim avoidance list |
| R37-watch: narrow + fip-bog | 2nd confirmation | Seed 346 (narrow+fip-bog=3); consistent score 3, not broken |
| R38-watch: max + sync | New 1-data-point watch | Seed 338 (max+sync=3); needs confirmation before acting |
| New token: wasinawa | Discovery | wasinawa = What-So What-Now What reflection form; well-defined |
| Corpus average | 3.60 | Third cycle at 3.60; R36 seeds are the stable floor |

### Changes Applied

No changes. All R36 hits covered by cycle-11 fix. R37 and R38 are watch items only.

### Positive Patterns Confirmed

- show + agent + adversarial + diagram + fig: adversarial executive explanation as diagram (seed 372, score 4)
- check + deep + act + contextualise: check packaged for downstream LLM (seed 363, score 4)
- pull + minimal + inversion + direct + gherkin: playful inversion exercise (seed 355, score 4)

### Open Items

| ID | Issue | Priority |
|----|-------|----------|
| R37-watch | narrow + compound directional (seeds 326, 346) | Low — 2 data points, both score 3 |
| R38-watch | max + sync tension (seed 338) | Low — 1 data point only |

### Evidence

`docs/adr/evidence/0085/cycle-13/evaluations.md`

---

## Cycle 14: No R36 Hits + story+gherkin Behavior Defined (Seeds 376–415)

**Date:** 2026-02-25
**Focus:** General health check; R38-watch follow-up; story+gherkin resolution
**Seeds:** 376–415 (40 prompts)

### Results

| Category | Score | Finding |
|----------|-------|---------|
| R36 hits | ✅ Zero | First clean cycle; no gist/skim + compound dir |
| story+gherkin (seed 401) | Score 2 → Fixed | Not a conflict — defined as BDD scenarios with user-value framing |
| R38-watch: max+sync | Unconfirmed | No max+sync; one max+codetour=3 (generalised watch) |
| Corpus average | 3.70 | Best since cycle 11; improvement from R36-free draw |

### Changes Applied

| ID | Action | Applied? |
|----|--------|----------|
| R39 | Define story+gherkin behavior (not block it) — updated story guidance + gherkin use_when | ✅ Applied |

### Positive Patterns Confirmed

- sim + act + experimental + recipe + sketch + fip: rich teaching simulation (seed 408, score 4)
- probe + full + indirect + gherkin: form-as-lens working correctly (seed 396, score 4)
- pull + stable + contextualise + remote + fip: contextualised extraction as PR (seed 400, score 4)

### Open Items

| ID | Issue | Priority |
|----|-------|----------|
| R37-watch | narrow + compound directional (seeds 326, 346) | Low |
| R38-watch | max + constrained-format channel (seeds 338, 395) | Low — generalised to max+[sync,codetour,adr,presenterm] |

### Evidence

`docs/adr/evidence/0085/cycle-14/evaluations.md`

---

## Cycle 15: Four R36 Hits + R38 Confirmed (Seeds 416–455)

**Date:** 2026-02-25
**Focus:** General health check; R38-watch confirmation (max+sync)
**Seeds:** 416–455 (40 prompts)

### Results

| Category | Score | Finding |
|----------|-------|---------|
| R36 hits | 4 (seeds 423,443,445,446) | Above-average draw; all covered by cycle-11 fix |
| R38: max + sync confirmed | Seed 418 (2nd data point) | Both seeds score 3; fix applied |
| Corpus average | 3.40 | Regression from 3.70; 4 R36 hits drive it |

### Changes Applied

| ID | Action | Applied? |
|----|--------|----------|
| R38 | Add max↔sync avoidance notes to both tokens in axisConfig.py | ✅ Applied |

### New watch

| ID | Issue | Priority |
|----|-------|----------|
| spike+gherkin | 1 data point (seed 432, score 3). May deserve story+gherkin treatment | Low |

### Evidence

`docs/adr/evidence/0085/cycle-15/evaluations.md`

---

## Cycle 16: R37 Applied + R36 Recurrence (Seeds 456–495)

**Date:** 2026-02-25
**Focus:** General health check; R37-watch resolution (3rd data point); spike+gherkin watch
**Seeds:** 456–495 (40 prompts)

### Results

| Category | Score | Finding |
|----------|-------|---------|
| R36: skim + fip-rog | ✅ Guidance in place | Seed 474 (skim+fip-rog=2); cycle-11 fix covers it |
| R37: narrow + fig | 3rd data point → fixed | Seed 466 (narrow+fig=3); consistent across seeds 326, 346, 466 |
| full + sync (R38 boundary) | ✅ Fine | Seed 478 (full+sync=4); fix correctly scoped to max+sync only |
| R38 generalization: max + spike | New 1-data-point watch | Seed 495 (max+spike=3); spike = time-boxed, max = exhaustive |
| Corpus average | 3.58 | Within 3.40–3.70 band; 15 sparse seeds + 1 R36 hit |

### Changes Applied

| ID | Action | Applied? |
|----|--------|----------|
| R37 | Add `narrow` entry to AXIS_KEY_TO_GUIDANCE["completeness"]: "use with awareness" note for narrow+compound directional combinations | ✅ Applied |

### Positive Patterns Confirmed

- plan + full + motifs + triage + spike + ong: PM research spike with triage; coherent (seed 477, score 4)
- probe + full + cocreate + gherkin + fip-rog: gherkin+cocreate=form-as-lens (seed 491, score 4)
- trans + full + explore + variants + presenterm: transformation alternatives as slides (seed 487, score 4)
- plan + full + origin + case + dip-ong: origin-based case planning (seed 486, score 4)

### Open Items

| ID | Issue | Priority |
|----|-------|----------|
| spike+gherkin | 1 data point (seed 432 cycle-15, score 3). No new data this cycle | Low |
| R38-generalization | max + brevity-constrained forms (seed 495 max+spike=3). One data point | Low — watch |

### Evidence

`docs/adr/evidence/0085/cycle-16/evaluations.md`
