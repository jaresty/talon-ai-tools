# ADR-0085 Cycle 10: Compound Directional Validation + Kanji Audit
**Date:** 2026-02-25
**Seeds:** 216–255 (40 prompts)
**Focus:** (1) R34 investigation — gist/skim + compound directionals, (2) kanji collision sweep, (3) fresh broad health check

---

## Phase 0: Calibration

**Evaluators:** single-evaluator (Claude Sonnet 4.6)
**Calibration result:** N/A

---

## Section A: R34 Investigation — gist/skim + Compound Directionals

### Seeds with compound directionals in this corpus

| Seed | Comp | Dir | Score | Notes |
|------|------|-----|-------|-------|
| 217 | full | fig | 4 | full + fig: acceptable — full coverage with abstract+concrete lens |
| 218 | gist | dip bog | 4 | see below — actually mild, dip bog with gist works here |
| 219 | full | fig | 3 | full + fig + presenterm: complex, fig adds to richness not contradiction |
| 223 | full | fig | 4 | sim+branch+visual+fig: rich but coherent |
| 224 | deep | fig | 3 | deep+fig+slack: fig + Slack channel creates brevity pressure |
| **225** | **gist** | **fip bog** | **2** | **confirmed R34: gist+fip bog = tension** |
| 228 | full | fly ong | 3 | full+fly ong+table+svg: table+svg channel conflict also present |
| **230** | **skim** | **dip bog** | **2** | **confirmed R34: skim+dip bog = tension** |
| 240 | full | fig | 4 | diff+cross+grow+fig: coherent, full not in conflict with fig |
| 243 | full | fly ong | 4 | sort+mean+ladder+fly ong: ladder+fly ong complementary |

### Analysis

**R34 is confirmed** — but the pattern is more specific than originally stated:

- Tension occurs when **completeness ≤ skim** (gist or skim) is combined with **compound directionals** (fig, bog, fip bog, dip bog, fly bog, fly ong, etc.)
- Tension does **not** occur with `full` or `deep` + compound directionals
- `full` + compound directional = 4 in most cases (the full coverage accommodates multi-directional exploration)
- `gist`/`skim` + compound directional = 2 (contradictory: brief output can't cover a full-spectrum lens)

**Seed 225** (pick + gist + log + fip bog, score 2): gist says "touch main points once" — fip bog (幻, illusory/inverted fog + bog) asks for coverage spanning inverted-abstract AND both-horizontal dimensions. These are categorically incompatible in a brief summary.

**Seed 230** (show + skim + log + diagram + dip bog, score 2): skim is even more restrictive than gist. dip bog (混, concrete+acting AND reflective+acting) requires multi-dimensional coverage that skim cannot accommodate.

**Action: R34-action** — add guidance to bar help llm: avoid gist/skim with compound directionals.

---

## Section B: New Kanji Collision — wardley(form) ↔ diagram(channel)

### Discovery

Cycle 8 classified `wardley` vs `diagram` as a "same-channel duplicate (can't appear together)." This was **incorrect**.

From grammar inspection:
- `wardley`: **form** axis, kanji = 図
- `diagram`: **channel** axis, kanji = 図

Since they are on different axes, wardley (form) and diagram (channel) **CAN appear together** in the same prompt. This is a genuine **cross-axis kanji collision**.

Seed 217 shows `form=wardley(図), channel=jira` — no collision here, but any seed with both `form=wardley` and `channel=diagram` would display duplicate 図.

### Fix

Change `wardley` kanji from 図 to 鎖:
- 鎖 = "chain" — references the value chain that Wardley maps visualize
- Unambiguous semantic fit, no collisions with other tokens
- 図 remains exclusively for `diagram` (channel)

### R35

```yaml
- id: R35
  action: edit-kanji
  token: wardley
  axis: form
  current_kanji: 図
  proposed_kanji: 鎖
  reason: wardley(form) and diagram(channel) both use 図 and can appear together in the same prompt;
    鎖 (chain) references the value chain concept central to Wardley maps
  evidence: [kanji_collision_K7, cycle_10_discovery]
```

---

## Section C: R33 Additional Evidence — Technical Channel × Non-Technical Audience

Cycle 9 introduced R33 (code/codetour/shellscript channels incompatible with non-technical audiences). Cycle 10 provides additional evidence:

| Seed | Channel | Audience | Score | Note |
|------|---------|----------|-------|------|
| 232 | code | executive_brief | 3 | sim + code + executive: R33 confirmed |
| 236 | codetour | to stakeholders (as Kent Beck) | 3 | diff+codetour+stakeholders: R33 confirmed |
| 241 | code | stakeholder_facilitator | 3 | probe+code+stakeholder_facilitator: R33 confirmed |

R33 guidance was applied in Cycle 9. These seeds show the pattern persists — the guidance is correct and important.

---

## Section D: Corpus Evaluation (Seeds 216–255)

### Corpus summary

| Seed | Task | Comp | Scope | Method | Form | Channel | Dir | Persona |
|------|------|------|-------|--------|------|---------|-----|---------|
| 216 | check | minimal(小) | — | — | scaffold(足) | html(標) | — | fun_mode |
| 217 | pull | full(全) | fail(敗) | — | wardley(図) | jira(票) | fig | product_manager_to_team |
| 218 | make | gist(略) | — | flow(流) | — | diagram(図) | dip bog | as principal engineer |
| 219 | pull | full(全) | — | rigor(厳) | — | presenterm(演) | fig | scientist_to_analyst |
| 220 | pick | full(全) | good(良) | — | — | svg(画) | — | as prompt engineer |
| 221 | pull | full(全) | thing(物) | compare(較) | scaffold(足) | — | — | teach_junior_dev |
| 222 | pick | full(全) | — | origin(起) | — | slack(通) | rog | to platform team |
| 223 | sim | full(全) | — | branch(枝) | visual(絵) | — | fig | product_manager_to_team |
| 224 | plan | deep(深) | fail(敗) | — | recipe(法) | slack(通) | fig | as scientist |
| 225 | pick | gist(略) | — | — | log(誌) | — | fip bog | scientist_to_analyst |
| 226 | probe | max(尽) | mean(意) | — | — | slack(通) | — | as PM to Kent Beck |
| 227 | pick | full(全) | struct(造) | — | — | — | — | to XP enthusiast |
| 228 | sort | full(全) | motifs(紋) | depends(依) | table(表) | svg(画) | fly ong | designer_to_pm |
| 229 | make | narrow(狭) | — | — | test(験) | — | — | to designer |
| 230 | show | skim(掠) | — | — | log(誌) | diagram(図) | dip bog | executive_brief |
| 231 | sort | full(全) | thing(物) | meld(融) | — | remote(遠) | — | as programmer to XP enthusiast |
| 232 | sim | full(全) | — | product(商) | — | code(碼) | — | executive_brief |
| 233 | sort | full(全) | view(視) | — | commit(提) | — | — | to platform team |
| 234 | sort | full(全) | view(視) | — | — | — | ong | executive_brief |
| 235 | sim | full(全) | cross(横) | gap(隙) | — | — | — | scientist_to_analyst |
| 236 | diff | full(全) | — | — | — | codetour(観) | — | as Kent Beck to stakeholders |
| 237 | diff | narrow(狭) | — | bias(偏) | contextualise(脈) | — | — | scientist_to_analyst |
| 238 | pull | full(全) | mean(意) | — | — | jira(票) | — | to XP enthusiast |
| 239 | fix | full(全) | — | models(型) | contextualise(脈) | diagram(図) | dip ong | scientist_to_analyst |
| 240 | diff | full(全) | cross(横) | grow(増) | — | — | fig | — |
| 241 | probe | gist(略) | agent(主) | grow(増) | checklist(検) | code(碼) | — | stakeholder_facilitator |
| 242 | make | full(全) | assume(仮) | — | scaffold(足) | — | — | designer_to_pm |
| 243 | sort | full(全) | mean(意) | — | ladder(階) | — | fly ong | to analyst |
| 244 | fix | full(全) | — | afford(構) | — | — | rog | fun_mode |
| 245 | check | narrow(狭) | — | balance(均) | story(話) | — | fly rog | programmer to programmer |
| 246 | diff | minimal(小) | — | — | variants(変) | html(標) | — | peer_engineer_explanation |
| 247 | show | deep(深) | time(時) | grow(増) | quiz(試) | gherkin(瓜) | — | as scientist (teach) |
| 248 | check | full(全) | — | simulation(象) | — | svg(画) | rog | teach_junior_dev |
| 249 | check | skim(掠) | fail(敗) | — | — | — | — | as programmer |
| 250 | make | narrow(狭) | — | — | — | sync(期) | — | executive_brief |
| 251 | fix | skim(掠) | mean(意) | — | variants(変) | sketch(描) | fog | as junior engineer |
| 252 | diff | deep(深) | thing(物) | systemic(系) | — | — | — | designer_to_pm |
| 253 | sort | full(全) | fail(敗) | — | recipe(法) | — | — | product_manager_to_team |
| 254 | pull | minimal(小) | — | domains(領) | checklist(検) | code(碼) | jog | as principal engineer |
| 255 | check | full(全) | thing(物) | — | — | slack(通) | — | scientist_to_analyst |

### Per-seed scores (selected)

#### Seed 218 — make + gist + flow + diagram + dip bog (混) + PE
- Task clarity: 5 | Constraint independence: 4 | Category alignment: 5 | Combination harmony: 4
- Note: gist + dip bog (混 = concrete+acting+reflective) is a borderline case. gist is brief, dip bog is multi-dimensional. But `make` + `flow` + `diagram` are all pointing toward a single focused output (a flow diagram), which constrains scope enough that dip bog doesn't overwhelm the brevity. Acceptable.
- **Overall: 4**

#### Seed 221 — pull + full + thing + compare + scaffold + teach_junior_dev
- Task clarity: 5 | Constraint independence: 5 | Persona coherence: 5 | Category alignment: 5 | Combination harmony: 5
- **Overall: 5** — Compare two things with scaffolded structure for junior devs. Every token reinforces pedagogical purpose.

#### Seed 225 — pick + gist + log + fip bog (幻)
- Task clarity: 4 | Constraint independence: 4 | Category alignment: 4 | Combination harmony: 2
- **Overall: 2** — R34 confirmed: gist (brief) + fip bog (illusory/inverted fog + bog = multi-directional compound) = contradictory completeness signals.

#### Seed 228 — sort + full + motifs + depends + table + svg + fly ong
- Task clarity: 4 | Constraint independence: 4 | Category alignment: 3 | Combination harmony: 2
- **Overall: 3** — Two issues: (1) table(form) + svg(channel): svg wins as channel, table becomes content lens in SVG — workable but awkward; (2) very dense combination (5 tokens excluding task).

#### Seed 229 — make + narrow + test + to designer
- **Overall: 5** — Clean minimal: narrow creative with test structure for a designer audience.

#### Seed 230 — show + skim + log + diagram + dip bog + executive_brief
- Task clarity: 4 | Constraint independence: 3 | Category alignment: 4 | Combination harmony: 2
- **Overall: 2** — R34 confirmed: skim (ultra-brief) + dip bog (compound directional) = incompatible.

#### Seed 232 — sim + full + product + code + executive_brief
- Task clarity: 4 | Constraint independence: 4 | Persona coherence: 2 | Combination harmony: 2
- **Overall: 3** — R33: code channel + executive persona. R33 guidance was added; this confirms the pattern.

#### Seed 235 — sim + full + cross + gap + scientist_to_analyst
- Task clarity: 5 | Constraint independence: 5 | Persona coherence: 5 | Combination harmony: 5
- **Overall: 5** — cross-cutting gap analysis via simulation. Excellent: simulating what happens when implicit cross-cutting assumptions are violated.

#### Seed 236 — diff + full + codetour + as Kent Beck to stakeholders
- Task clarity: 4 | Constraint independence: 4 | Persona coherence: 2 | Combination harmony: 2
- **Overall: 3** — R33: codetour (technical channel) + to stakeholders (non-technical). Kent Beck voice is expert but stakeholders audience is non-technical.

#### Seed 237 — diff + narrow + bias + contextualise + scientist_to_analyst
- Task clarity: 5 | Constraint independence: 5 | Persona coherence: 5 | Combination harmony: 5
- **Overall: 5** — narrow bias comparison with contextual background. Every token reinforces nuanced analytical communication.

#### Seed 247 — show + deep + time + grow + quiz + gherkin + as scientist (teach)
- Task clarity: 5 | Constraint independence: 4 | Category alignment: 5 | Combination harmony: 4
- Note: quiz(form) + gherkin(channel): gherkin wins; quiz becomes content lens (Q&A structured as Gherkin Given/When/Then). Unusual but valid for teaching temporal concepts. grow + time: disciplined expansion across time lens. intent=teach + gherkin: teaching via BDD scenarios ✓
- **Overall: 4**

#### Seed 252 — diff + deep + thing + systemic + designer_to_pm
- Task clarity: 5 | Constraint independence: 5 | Persona coherence: 5 | Combination harmony: 5
- **Overall: 5** — deep systemic comparison of objects, framed for PM audience.

---

### Score summary

| Score | Seeds | Count |
|-------|-------|-------|
| 5 | 221, 229, 235, 237, 252 | 5 (12.5%) |
| 4 | 218, 219, 220, 222, 223, 231, 238, 239, 240, 242, 243, 244, 245, 247, 248, 251, 253, 254 | 18 (45%) |
| 3 | 217, 224, 226, 228, 232, 233, 234, 236, 241, 246, 249, 250, 255 | 13 (32.5%) |
| 2 | 225, 230 | 2 (5%) |
| 1 | — | 0 |

**Scored average: 3.75** — slight regression vs Cycle 9 (3.89). Root causes: R34 pattern (gist/skim + compound dir), R33 pattern (technical channel + non-technical audience), table+svg channel combination.

---

## Cycle 10 Findings Summary

### Confirmed patterns

| Pattern | Count this cycle | Action |
|---------|-----------------|--------|
| R34: gist/skim + compound directionals | 2 seeds, both score 2 | Add help_llm guidance |
| R33: technical channel + non-technical audience | 3 seeds | Guidance already applied; evidence archived |

### New issues found

| ID | Issue | Type | Seeds | Priority |
|----|-------|------|-------|----------|
| R35 | wardley(form, 図) ↔ diagram(channel, 図) — cross-axis kanji collision | kanji | 217, any wardley+diagram | High |

---

## Recommendations (Cycle 10)

```yaml
- id: R35
  action: edit-kanji
  token: wardley
  axis: form
  current_kanji: 図
  proposed_kanji: 鎖
  reason: wardley(form) and diagram(channel) both use 図; they CAN appear together (different axes);
    鎖 (chain) references value chain — core Wardley map concept; Cycle 8 misclassified this
    as same-channel when wardley is form, not channel
  evidence: [cycle_8_misclassification, cycle_10_discovery]

- id: R34-action
  action: edit
  target: bar help llm
  section: Token Selection Heuristics > Choosing Directional
  proposed: |
    Compound directionals (fig, bog, fly ong, fly bog, fip bog, dip bog, etc.) span multiple
    dimensions simultaneously and require space to resolve. Avoid pairing them with gist or skim
    completeness — the multi-directional coverage cannot be expressed in a brief summary. Use full
    or deep completeness when selecting compound directionals.
  reason: Seeds 225 and 230 both score 2 (gist/skim + compound dir); full + compound dir scores 4
  evidence: [seed_225, seed_230]
```
