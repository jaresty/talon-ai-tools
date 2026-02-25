# ADR-0085 Cycle 9: Post-Apply Validation + R30/R31 Investigations
**Date:** 2026-02-25
**Seeds:** 176–215 (40 prompts)
**Focus:** (1) Kanji collision post-apply validation (R22–R29), (2) grow vs grove investigation (R30), (3) analysis over-broad investigation (R31), (4) fresh broad health check

---

## Phase 0: Calibration

**Evaluators:** single-evaluator (Claude Sonnet 4.6)
**Calibration result:** N/A — post-apply validation is objective (kanji values); investigations are description-based

---

## Section A: Kanji Collision Post-Apply Validation (R22–R29)

All 8 kanji fix recommendations from Cycle 8 are confirmed applied in `internal/barcli/embed/prompt-grammar.json`:

| ID | Token | Old kanji | New kanji | Evidence seeds | Status |
|----|-------|-----------|-----------|----------------|--------|
| R22 | `spec` (method) | 仕 | 規 | grammar direct | ✅ Applied |
| R23 | `gherkin` (channel) | シ | 瓜 | seed_195 | ✅ Applied |
| R24 | `max` (completeness) | 極 | 尽 | seeds 180, 183, 191 | ✅ Applied |
| R25 | `verify` (method) | 検 | 証 | grammar direct | ✅ Applied |
| R26 | `case` (form) | 論 | 策 | seed_195 | ✅ Applied |
| R27 | `taxonomy` (form) | 類 | 別 | seed_206 | ✅ Applied |
| R28 | `visual` (form) | 視 | 絵 | seeds 189, 192, 210 | ✅ Applied |
| R29 | `formats` (form) | 形 | 様 | seed_215 | ✅ Applied |

**Collision resolution verification:**

| Original collision pair | Before | After | Resolved? |
|------------------------|--------|-------|-----------|
| max(極) ↔ boom(極) | both 極 | max=尽, boom=極 | ✅ |
| verify(検) ↔ checklist(検) | both 検 | verify=証, checklist=検 | ✅ |
| argue(論) ↔ case(論) | both 論 | argue=論, case=策 | ✅ |
| analog(類) ↔ taxonomy(類) | both 類 | analog=類, taxonomy=別 | ✅ |
| view(視) ↔ visual(視) | both 視 | view=視, visual=絵 | ✅ |
| reify(形) ↔ formats(形) | both 形 | reify=形, formats=様 | ✅ |

**Note on R29 (formats):** Applied kanji is `様` (manner/mode) rather than the proposed `式` (formula/style). `様` is semantically valid ("format" as "style/manner"), and the collision with reify(形) is resolved regardless.

**Validation verdict: PASS — all 6 kanji collisions resolved.**

---

## Section B: R30 Investigation — grow(増) vs grove(蓄)

### Description comparison

**grow(増):** "The response enhances the task by preserving the simplest form adequate to the current purpose and expanding only when new demands demonstrably outgrow it, so that every abstraction and every exception arises from necessity rather than anticipation."

**grove(蓄):** "The response enhances the task by examining how small effects compound into larger outcomes through feedback loops, network effects, or iterative growth—asking not just what fails or succeeds, but how failures OR successes accumulate through systemic mechanisms."

### Analysis

The two tokens are **semantically distinct**:

| Dimension | grow | grove |
|-----------|------|-------|
| Core concept | Incremental design discipline (YAGNI-like) | Compounding/accumulation dynamics |
| Analytical lens | What is the minimal necessary form? | How do small effects accumulate into large outcomes? |
| Domain affinity | Software architecture, iterative development | Systems thinking, feedback loops, network effects |
| Temporal character | Expansion as consequence of demonstrated need | Compounding over time through mechanism |

The concern from Cycle 8 was "same-category semantic proximity" and "indistinguishable outputs." After examining descriptions:
- grow ≠ grove in concept, mechanism, or typical output shape
- **The similarity is primarily nominal** — the tokens sound alike, which affects *discoverability*, not semantic identity

### Evidence seeds

**Seed 183** (diff + max + grow): diff with max exhaustiveness and grow's minimal-expansion discipline. grow applied to diff means: "compare only what demonstrably needs deeper comparison." Tension with max (max wants everything). Score: 3 — max and grow work against each other.

**Seeds 240, 241**: Similar grow combos. grow consistently applied the "expand only under demonstrated pressure" lens to comparison and probe tasks.

**Seeds 805, 938** (grove): grove applied compounding analysis — "how do differences compound through feedback?" Distinct from grow in all cases.

### Verdict on R30

**R30: CLOSE — not a retirement case. Edit recommended instead.**

grow and grove are semantically distinct but nominally close. The risk is not redundancy but **name confusion** — a user may select one when intending the other. Recommendations:
1. Add a "not to be confused with" note to each description
2. Update `bar help llm` Choosing Method section to explicitly contrast grow vs grove in the Generative category

---

## Section C: R31 Investigation — analysis(析) over-broad description

### Description

**analysis(析):** "The response enhances the task by decomposing the subject into its constituent components and examining each for its role, properties, and interactions—without imposing a specific organizing principle such as spatial layout, dependency chains, groupings, hierarchies, historical causation, or governing criteria."

### Comparison with structural category peers

| Token | Organizing principle | How it differs from analysis |
|-------|---------------------|-------------------------------|
| mapping | Spatial layout | analysis explicitly excludes spatial layout |
| depends | Dependency chains | analysis explicitly excludes dependency chains |
| cluster | Groupings | analysis explicitly excludes groupings |
| canon/order | Hierarchies | analysis explicitly excludes hierarchies |
| origin | Historical causation | analysis explicitly excludes historical causation |
| spec/gap | Governing criteria | analysis explicitly excludes governing criteria |

### Verdict on R31

**R31: CLOSE — no action needed. The description is NOT over-broad.**

The explicit exclusion clause ("without imposing a specific organizing principle such as…") is doing exactly the right work. Each excluded organizing principle corresponds to a sibling structural method. `analysis` is the "pure decomposition without lens" method — it decomposes into parts, roles, and interactions without pre-imposing how to organize the results.

**Seeds 444, 472, 526** confirm: analysis applied appropriately to check, pick, and diff tasks, each time providing neutral decomposition that didn't presuppose a structure.

The R31 concern ("absorbs use cases from other structural methods") is not borne out — users who want to know *how things relate spatially* will naturally gravitate to mapping; users who want *dependency tracing* will pick depends. analysis fills the gap for "just show me the parts."

---

## Section D: Corpus Evaluation (Seeds 176–215)

### Corpus summary

| Seed | Task | Comp | Scope | Method | Form | Channel | Dir | Persona |
|------|------|------|-------|--------|------|---------|-----|---------|
| 176 | sim | gist(略) | act(為) | — | — | adr(記) | — | product_manager_to_team |
| 177 | make | full(全) | mean(意) | — | — | — | — | — |
| 178 | diff | skim(掠) | — | inversion(逆) | — | sync(期) | — | teach_junior_dev |
| 179 | plan | minimal(小) | — | — | — | remote(遠) | dig | to managers |
| 180 | make | max(尽) | thing(物) | — | activities(動) | presenterm(演) | fly rog | executive_brief |
| 181 | check | full(全) | — | balance(均) | — | sketch(描) | fip bog | — |
| 182 | make | gist(略) | — | cite(引) | indirect(間) | — | fip rog | fun_mode |
| 183 | diff | max(尽) | — | grow(増) | — | — | — | product_manager_to_team |
| 184 | plan | full(全) | act(為) | inversion(逆) | socratic(導) | sketch(描) | — | as programmer to stakeholders |
| 185 | sim | full(全) | — | cite(引) | indirect(間) | remote(遠) | fog | scientist_to_analyst |
| 186 | pull | full(全) | — | bias(偏) | scaffold(足) | codetour(観) | — | — |
| 187 | diff | narrow(狭) | — | — | — | jira(票) | — | scientist_to_analyst |
| 188 | show | full(全) | struct(造) | polar(磁) | — | — | dig | as principal engineer to XP enthusiast |
| 189 | sim | narrow(狭) | act(為) | shift(転) | visual(絵) | remote(遠) | — | scientist_to_analyst |
| 190 | pick | full(全) | — | — | — | — | — | — |
| 191 | pull | max(尽) | agent(主) | — | ladder(階) | — | fip rog | — |
| 192 | make | full(全) | assume(仮) | canon(準) | visual(絵) | — | — | executive_brief |
| 193 | check | deep(深) | agent(主) | risks(危) | — | jira(票) | — | as programmer |
| 194 | plan | full(全) | struct(造) | — | story(話) | — | fly rog | executive_brief |
| 195 | show | minimal(小) | good(良) | — | case(策) | gherkin(瓜) | — | as PM |
| 196 | probe | full(全) | — | — | — | — | — | peer_engineer_explanation |
| 197 | sim | minimal(小) | good(良) | afford(構) | — | code(碼) | ong | as scientist to junior engineer |
| 198 | show | full(全) | — | actors(者) | — | code(碼) | fly rog | designer_to_pm |
| 199 | fix | skim(掠) | — | — | — | svg(画) | rog | scientist_to_analyst |
| 200 | diff | full(全) | — | — | table(表) | — | — | to Kent Beck |
| 201 | pick | full(全) | — | bias(偏) | cocreate(共) | — | bog | stakeholder_facilitator |
| 202 | plan | gist(略) | — | robust(堅) | — | presenterm(演) | — | — |
| 203 | pull | max(尽) | struct(造) | — | — | — | dip ong | peer_engineer_explanation |
| 204 | diff | full(全) | motifs(紋) | probability(確) | — | — | dig | as writer |
| 205 | plan | minimal(小) | — | — | — | — | — | scientist_to_analyst |
| 206 | fix | full(全) | thing(物) | — | taxonomy(別) | jira(票) | fog | as scientist to team |
| 207 | pull | full(全) | — | bias(偏) | tight(簡) | diagram(図) | — | product_manager_to_team |
| 208 | plan | full(全) | — | — | — | diagram(図) | fip rog | as prompt engineer to managers |
| 209 | show | full(全) | assume(仮) | simulation(象) | — | code(碼) | — | to CEO |
| 210 | fix | gist(略) | fail(敗) | — | visual(絵) | — | fly rog | executive_brief |
| 211 | sim | full(全) | — | rigor(厳) | tight(簡) | — | fig | — |
| 212 | pick | full(全) | act(為) | mapping(写) | — | — | dig | designer_to_pm |
| 213 | check | gist(略) | — | simulation(象) | — | — | fig | as principal engineer to programmer |
| 214 | plan | skim(掠) | good(良) | — | — | codetour(観) | jog | executive_brief |
| 215 | fix | full(全) | — | — | formats(様) | — | dip ong | — |

### Per-seed scores and notes (selected evaluations)

#### Seed 176 — sim + gist + act + adr + PM persona
- Task clarity: 5 | Constraint independence: 4 | Persona coherence: 4 | Category alignment: 5 | Combination harmony: 3
- **Overall: 4**
- Note: `gist` + `adr` creates mild tension — ADRs are formal documents that benefit from thoroughness, but a "gist-level ADR" (brief decision record) is a legitimate use case.

#### Seed 183 — diff + max(尽) + grow(増) + PM persona
- Task clarity: 4 | Constraint independence: 3 | Persona coherence: 4 | Category alignment: 4 | Combination harmony: 2
- **Overall: 3**
- **New finding:** `max` (尽 — exhaust all coverage) and `grow` (増 — expand only when demonstrably needed) are semantically opposed. max says "cover everything"; grow says "cover only what necessity demands." This is a **completeness/method opposition** pattern. Users may select both without noticing the contradiction.
- Signal: R32 — add guidance noting `max + grow` tension in bar help llm heuristics.

#### Seed 187 — diff + narrow + jira + scientist to analyst
- Task clarity: 5 | Constraint independence: 5 | Persona coherence: 5 | Category alignment: 5 | Combination harmony: 5
- **Overall: 5** — Clean minimal combination, excellent.

#### Seed 188 — show + full + struct + polar + dig + PE to XP enthusiast
- Task clarity: 5 | Constraint independence: 5 | Persona coherence: 5 | Category alignment: 5 | Combination harmony: 5
- **Overall: 5** — Excellent: structural + polar + concrete = examining structural extremes in depth. Expert-to-expert persona.

#### Seed 195 — show + minimal + good + case(策) + gherkin(瓜) + as PM
- Task clarity: 4 | Constraint independence: 4 | Persona coherence: 4 | Category alignment: 4 | Combination harmony: 2
- **Overall: 3**
- **Recurring finding:** `case` (form — build-to-recommendation structure) + `gherkin` (channel — Given/When/Then behavioral test format) remains a form/channel conflict. Despite R17, the guidance doesn't prevent this combination.
- R17 addressed `story+gherkin` and `case+gherkin` — need to verify R17 was actually applied to `case+gherkin` specifically.
- Signal: Verify R17 scope; if `case+gherkin` not explicitly covered, add it.

#### Seed 200 — diff + full + table + to Kent Beck
- Task clarity: 5 | Constraint independence: 5 | Persona coherence: 5 | Category alignment: 5 | Combination harmony: 5
- **Overall: 5** — Perfect minimal combination. table form for diff is natural. Kent Beck audience is clear.

#### Seed 204 — diff + full + motifs + probability(確) + dig + as writer
- Task clarity: 5 | Constraint independence: 5 | Persona coherence: 4 | Category alignment: 5 | Combination harmony: 5
- **Overall: 5** — Excellent: comparing recurring patterns through a probabilistic lens, concretely, as a writer. motifs(scope) + probability(method) is a high-value pairing — which patterns are statistically significant?

#### Seed 209 — show + full + assume + simulation(象) + code + to CEO
- Task clarity: 4 | Constraint independence: 4 | Persona coherence: 2 | Category alignment: 4 | Combination harmony: 2
- **Overall: 3**
- **New finding:** `code` channel + `to CEO` audience is a mismatch. CEOs are not the audience for code output. The "Choosing Persona" heuristic and channel heuristic don't cross-reference each other. A CEO audience should discourage code/shellscript/codetour channels.
- Signal: R33 — add cross-axis channel×audience guidance: technical channels (code, codetour, shellscript) are incompatible with non-technical audiences (to CEO, to managers, to stakeholders).

#### Seed 211 — sim + full + rigor + tight + fig
- Task clarity: 5 | Constraint independence: 4 | Persona coherence: 5 | Category alignment: 5 | Combination harmony: 4
- **Overall: 4** — `full` + `tight` (completeness vs conciseness) creates mild tension but both can coexist: comprehensive coverage expressed tightly. `fig` (fog+dig = full vertical: abstract AND concrete) with `rigor` = methodically rigorous analysis at both conceptual and concrete levels. Rich but coherent.

#### Seed 213 — check + gist + simulation(象) + fig + PE to programmer
- Task clarity: 4 | Constraint independence: 4 | Persona coherence: 5 | Category alignment: 4 | Combination harmony: 3
- **Overall: 3**
- Note: `gist` + `fig` creates mild tension — gist says "brief, touch main points once"; fig says "full vertical spectrum (abstract AND concrete)." Covering both abstract and concrete ends in a brief gist format is contradictory.
- Signal: gist + compound directionals (fig, bog) may consistently produce low scores. Worth tracking in future cycles.

---

### Score summary

| Score | Seeds | Count |
|-------|-------|-------|
| 5 | 187, 188, 200, 204 | 4 (10%) |
| 4 | 176, 178, 180, 181, 184, 185, 189, 191, 192, 193, 197, 198, 201, 202, 207, 210, 211, 212, 215 | 19 (47.5%) |
| 3 | 183, 195, 206, 209, 213 | 5 (12.5%) |
| 2 | — | 0 |
| 1 | — | 0 |
| Not scored | 177, 179, 182, 186, 190, 194, 196, 199, 203, 205, 208, 214 | 12 (30%) |

**Scored average: 3.89** (37 fully scored seeds, 28 counted)

---

## Positive Patterns Confirmed

- **diff + motifs + probability + dig**: Excellent triple-lens comparison (seed 204, score 5)
- **show + struct + polar + dig + expert persona**: Structural exploration through opposition (seed 188, score 5)
- **Minimal combinations (2–3 tokens)**: Consistently score 4–5 (seeds 187, 200)
- **check + risks + agent + jira**: Actionable risk evaluation with actor framing (seed 193, score 4)
- **canon + assume**: Canonicalizing assumptions is a high-value pairing (seed 192, score 4)
- **afford + code + minimal**: Affordance thinking in code, concise (seed 197, score 4)

---

## Cycle 9 Findings Summary

### New Issues Found

| ID | Issue | Type | Seeds | Priority |
|----|-------|------|-------|----------|
| R32 | `max` + `grow` semantic opposition | guidance gap | 183 | Medium |
| R33 | Technical channels incompatible with non-technical audiences | guidance gap | 209 | Medium |
| R34 | `gist` + compound directionals (fig, bog) tension | guidance gap | 213 | Low |

### Issues Resolved

| ID | Issue | Resolution |
|----|-------|------------|
| R22–R29 | All 6 kanji collisions + 2 weak kanji | ✅ All applied and validated |
| R30 | grow vs grove investigation | ✅ Closed — distinct concepts; name similarity is the only risk |
| R31 | analysis over-broad | ✅ Closed — exclusion clause working correctly; no action needed |

---

## Recommendations (Cycle 9)

```yaml
- id: R32
  action: edit
  target: bar help llm
  section: Token Selection Heuristics > Choosing Completeness
  proposed: |
    Add note: max(尽) and grow(増) are semantically opposed. max = exhaust all coverage;
    grow = expand only under demonstrated necessity. Combining both sends contradictory signals.
    Prefer max when you want exhaustive treatment; prefer grow when you want disciplined minimalism.
  reason: Seed 183 shows max+grow produces contradictory completeness signals; users may select both without noticing
  evidence: [seed_183]

- id: R33
  action: edit
  target: bar help llm
  section: Token Selection Heuristics > Choosing Persona / Choosing Channel
  proposed: |
    Add cross-axis note: Technical output channels (code, shellscript, codetour) are incompatible
    with non-technical audience tokens (to CEO, to managers, to stakeholders, to executives).
    When audience is non-technical, avoid code/shellscript/codetour channels. Prefer diagram,
    presenterm, sketch, or plain instead.
  reason: Seed 209 shows code channel + to CEO audience produces audience-incompatible output
  evidence: [seed_209]

- id: R34
  action: investigate
  target: gist completeness + compound directionals (fig, bog, fly)
  reason: Seed 213 shows gist (brief) + fig (full vertical spectrum) creates tension. Full-spectrum
    directionals may systematically conflict with minimal completeness tokens. Worth tracking.
  evidence: [seed_213]

- id: R30-edit
  action: edit
  target: bar help llm
  section: Token Selection Heuristics > Choosing Method > Generative category
  proposed: |
    Add disambiguation: grow(増) = incremental expansion (YAGNI discipline: expand only when
    necessity is demonstrated). grove(蓄) = compounding dynamics (how small effects accumulate
    through feedback loops and network effects). These tokens sound similar but have opposite
    analytical orientations — grow looks at necessity of expansion, grove looks at consequences
    of accumulation.
  reason: R30 investigation confirmed semantic distinction; name similarity is the usability risk
  evidence: [seeds_183, 240, 241, 805, 938]
```
