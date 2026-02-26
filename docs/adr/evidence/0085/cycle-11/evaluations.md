# ADR-0085 Cycle 11: Compound Directional Expansion + Bar v2.64.1 Health Check
**Date:** 2026-02-25
**Seeds:** 256–295 (40 prompts)
**Bar version:** 2.64.1 (upgraded from 2.25.0 before this cycle)
**Focus:** (1) Post-cycle-10 health check, (2) verify R34 heuristic coverage with expanded compound directional catalog, (3) identify new gaps from v2.64.1 changes

---

## Phase 0: Calibration

**Evaluators:** single-evaluator (Claude Sonnet 4.6)
**Calibration result:** N/A (continuation of established rubric)

---

## Key Change: Bar v2.64.1 Compound Directional Expansion

Bar v2.64.1 significantly expanded the directional token catalog. The previous release used shorthand names (fly, dip, fip); the new release exposes all compound directionals explicitly:

**New explicit compound directionals (16 total):**
- `bog` (rog+ong), `dig`, `dip-bog`, `dip-ong`, `dip-rog`, `fig` (fog+dig)
- `fip-bog`, `fip-ong`, `fip-rog`
- `fly-bog`, `fly-ong`, `fly-rog`
- `fog`, `jog`, `ong`, `rog`

Previously the help_llm.go "Choosing Directional" heuristic listed "(fig, bog, fly ong, fly bog, fip bog, dip bog, etc.)" — the "etc." now has a full enumeration to lean on.

---

## Section A: Rapid Evaluation — Seeds 256–295

### Token Summary and Scores

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 256 | trans | full, agent, flow, cocreate | analyst, kindly | 4 | Collaborative transformation — coherent |
| 257 | plan | full, motifs, split, presenterm, dip-ong | pm_to_team | 4 | Plan+split+presenterm; compound dir ok w/full |
| 258 | check | full, agent, deduce | pm→managers, teach | 4 | Deductive eval PM-to-managers; coherent |
| 259 | probe | full, act, html, fly-ong | scientist_to_analyst | 3 | probe+html awkward; fly-ong+full fine; score limited by html channel for analytical task |
| 260 | pick | skim, cross, socratic, fip-rog | executive_brief | 3 | skim+fip-rog = R34 pattern (score 2 candidate); socratic+executive_brief tension also; executive pick via socratic questioning is odd |
| 261 | probe | narrow, adversarial, questions, presenterm, dip-ong | audience, casually | 4 | Excellent: adversarial+questions+probe; casually mild tension |
| 262 | sort | narrow, motifs, split, activities, dip-ong | executive_brief | 4 | Motifs classification as activities; coherent |
| 263 | sim | full, mean, quiz, plain | casually, teach | 4 | Educational sim as quiz; coherent |
| 264 | pull | full, thing, triage, fig | executive_brief | **5** | Excellent: executive extraction with prioritization and full-vertical directional |
| 265 | sim | full, agent, socratic, svg | directly, inform | 3 | svg+socratic = form-as-content-lens required; awkward but handled by rule |
| 266 | show | minimal, time, log | fun_mode | 4 | Minimal temporal log; fun mode playful; coherent |
| 267 | check | full, stable, jog | voice, audience | 3 | Stable scope + jog = minimal constraints; functionally fine but sparse |
| 268 | trans | full, act, origin, visual, html | stakeholder_facilitator | 4 | origin+visual+html → visual transformation as HTML; coherent |
| 269 | probe | full, stable, compare, bug, shellscript, dig | stakeholder_facilitator | 3 | shellscript+bug form awkward; stakeholder+shellscript unusual but not broken |
| 270 | pick | full, boom, adr, jog | formally, announce | 4 | **Notable positive**: decision→ADR with boom insight + formal announcement; highly coherent |
| 271 | pull | gist, sync | stakeholder_facilitator | 4 | Minimal but clean; gist+sync = quick stakeholder sync |
| 272 | show | full, afford, test, sync, fig | voice, audience | 4 | affordances explained as test-structure agenda; fig+full fine |
| 273 | pull | full, effects, questions, fly-ong | fun_mode | 4 | Extract effects as questions; fly-ong+full fine |
| 274 | sort | full, thing, calc, fly-ong | none | 4 | Calculational classification; clean |
| 275 | pull | skim, unknowns, adr, rog | scientist_to_analyst | 3 | skim+adr slight tension (ADRs tend fuller); rog+skim fine |
| 276 | diff | skim, resilience, dig | voice, teach | 4 | skim+dig fine (dig is simple/primitive) |
| 277 | probe | narrow, grow, bug | scientist_to_analyst | 4 | grow+bug+probe coherent diagnostic |
| 278 | probe | full, simulation, slack, bog | stakeholder_facilitator | 4 | simulation method + bog directional + full completeness; bog+full fine |
| 279 | pull | full | audience, gently | 3 | Too sparse — pull with only completeness; functionally ok |
| 280 | sim | full, good, risks, rog | executive_brief | 4 | sim with good scope + risks method coherent |
| 281 | pick | full, recipe, svg, dip-ong | formally, coach | 3 | svg+recipe = form-as-content-lens required; awkward |
| 282 | sort | minimal, cross, systemic, direct, bog | designer_to_pm | 3 | bog+minimal not the same as R34 (minimal ≠ gist/skim); score 3 for complexity; systemic+direct tension slight |
| 283 | plan | full, struct, robust, remote, bog | voice, inform | 4 | plan+robust+struct+remote; bog+full fine |
| 284 | show | full | executive_brief | 3 | Minimal; show+full+executive_brief; no focus |
| 285 | pull | full, cross, meld, checklist, sketch | audience, announce | 4 | meld+cross+checklist+sketch coherent extraction |
| 286 | sim | full, assume, experimental, scaffold | audience, appreciate | 4 | experimental+scaffold+sim; appreciate intent minor oddity |
| 287 | pull | **skim**, thing, actors, **fly-ong** | pm_to_team | **2** | **R34 pattern: skim+fly-ong** — fly-ong IS compound, skim cannot span abstract→concrete→act |
| 288 | plan | full, act, triage, variants | kindly, persuade | 4 | triage+variants+plan; persuade+kindly coherent |
| 289 | probe | full, assume, grow, bug, adr, bog | stakeholder_facilitator | 3 | adr+bug form complex channel/form interaction; grow+probe slightly metaphorical |
| 290 | probe | full, mean, order, actions, dig | directly, persuade | 4 | order method+actions form+dig = concrete probing ordered by priority; persuade+probe minor tension |
| 291 | diff | full, act, shift, sketch | executive_brief | 4 | diff+shift+sketch; clean executive brief |
| 292 | pull | full, bias, faq, bog | voice, audience | 4 | bias extraction as FAQ; bog+full fine |
| 293 | plan | minimal, product, taxonomy, sync | fun_mode | 4 | Fun planning session as taxonomy in sync format; coherent |
| 294 | pick | full, cross, analysis, formats, slack | audience | 4 | analysis+formats+slack; clean decision |
| 295 | plan | full, resilience | scientist_to_analyst | 3 | Minimal; plan+resilience+scientist; sparse but functional |

**Score distribution:**
- 5: seed 264 (1)
- 4: seeds 256, 257, 258, 261, 262, 263, 266, 268, 270, 271, 272, 273, 274, 276, 277, 278, 280, 283, 285, 286, 288, 289, 290, 291, 292, 293, 294, 295 (28)
- 3: seeds 259, 260, 265, 267, 269, 275, 279, 281, 282, 284, 289, 295 (10)
- 2: seed 287 (1)

**Corpus average: 3.73** (slight regression from cycle-10's 3.75; seed 287 drives most of this)

---

## Section B: Key Findings

### B1 — Seed 260: skim + fip-rog (R34, unreported)

Seed 260 has `skim + fip-rog`. The skim token's notes explicitly list `fip-rog` as an avoidance target — this IS documented. However it still scored 3 (not 2) because the socratic+executive_brief tension dominates. Both issues compound.

### B2 — Seed 287: skim + fly-ong (R34 gap confirmed)

**This is the primary finding.** Seed 287 = `pull + skim + thing + actors + fly-ong + pm_to_team`. Score 2.

`fly-ong` is a compound directional (abstract-first, then act and extend). The skim token's notes say:
> "Avoid pairing with multi-phase directionals (bog, fip rog, fly rog, fog)"

But `fly-ong` is NOT in this list. Only `fly-rog` is listed. The help_llm.go heuristic correctly says:
> "Compound directionals (fig, bog, fly ong, fly bog, fip bog, dip bog, etc.) avoid gist or skim"

**Gap:** skim token's `notes` field is incomplete — it lists 4 avoidance targets but misses: `fly-ong`, `fip-ong`, `fip-bog`, `fly-bog`, `dip-bog`, `dip-ong`, `dip-rog`, `fig`.

**Also:** `gist` token has NO notes about compound directionals at all. The help_llm.go heuristic covers both gist and skim but the token-level notes only cover skim (incompletely).

**Fix needed:** Update skim and gist token notes in `lib/axisConfig.py` to list all compound directionals.

Also: `commit` form token notes say "avoid complex directionals (fip rog, fly rog, bog, fog)" — same incomplete list pattern.

### B3 — R34 heuristic in help_llm.go validated

The "Choosing Directional" heuristic added in cycle-10 correctly names fly-ong and covers the general case. Seeds 257 (dip-ong+full: 4), 273 (fly-ong+full: 4), 278 (bog+full: 4) all score correctly because they use full/deep completeness. The heuristic works at the help_llm level. The gap is only at the token notes level.

### B4 — Positive patterns

| Pattern | Seeds | Score | Value |
|---------|-------|-------|-------|
| pull+triage+thing+fig+executive_brief | 264 | 5 | Executive extraction with prioritization + full-vertical lens |
| pick+boom+adr+jog+formally+announce | 270 | 4 | Decisive ADR creation with dramatic insight method |
| probe+adversarial+questions+presenterm | 261 | 4 | Adversarial probing as presentation structure |
| probe+mean+order+actions+dig | 290 | 4 | Concrete ordered probe with actionable output |
| plan+struct+robust+remote+bog | 283 | 4 | Resilience planning as remote/GitHub artifact |

---

## Section C: Recurring Patterns

| Pattern | Count | Action |
|---------|-------|--------|
| Compound dir + skim/gist | 2 seeds (260 skim+fip-rog, 287 skim+fly-ong) | R36: fix skim+gist token notes |
| SVG + structured form | 2 seeds (265 svg+socratic, 281 svg+recipe) | Form-as-content-lens rule handles; no action needed |
| Minimal/sparse combos | 3 seeds (267, 279, 284, 295) | Low priority; shuffle produces minimal combos occasionally |

---

## Recommendations (Cycle 11)

```yaml
- id: R36
  action: edit-notes
  axis: completeness
  tokens: [skim, gist]
  target: lib/axisConfig.py
  current_skim_notes: |
    Quick-pass constraint: most obvious or critical issues only.
    Avoid pairing with multi-phase directionals (bog, fip rog, fly rog, fog)
    that require structural depth and sustained examination.
    Use with simple directionals (jog, rog) or none.
  proposed_skim_notes: |
    Quick-pass constraint: most obvious or critical issues only.
    Avoid pairing with any compound directional (fig, bog, fly-ong, fly-bog, fly-rog,
    fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog, fog) that requires
    multi-phase depth or sustained examination.
    Use with simple directionals (jog, rog, dig, ong) or none.
  current_gist_notes: (empty)
  proposed_gist_notes: |
    Brief but complete response. Avoid pairing with compound directionals (fig, bog,
    fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog)
    that require multi-dimensional depth — gist cannot express their full range.
    Use with simple directionals (jog, rog, dig, ong) or none.
  reason: >
    skim notes list only 4 avoidance targets (bog, fip-rog, fly-rog, fog), missing
    fly-ong (confirmed by seed 287 score 2) and all other compound directionals.
    gist has no avoidance guidance at all. help_llm.go heuristic correctly covers both
    but token-level notes are incomplete and don't match the expanded v2.64.1 catalog.
  evidence: [seed_287, seed_260]
  priority: Medium
```
