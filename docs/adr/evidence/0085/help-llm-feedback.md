# ADR-0085: Bar Help LLM Reference Feedback
**Date:** 2026-02-25
**Cycles covered:** 16–19 (seeds 456–615)
**Meta-analysis method:** `bar build probe full domains gap`

---

## Seed Evaluations

### Positive Patterns (Score-4)

#### Seed 491 — `probe full cocreate gherkin fip-rog as-writer appreciate`
**Reference utility: 4**
- gherkin channel notes explain the analysis→Gherkin reframe well.
- cocreate form listed in Choosing Form.
- fip-rog with full completeness: Choosing Directional correctly permits this.
- **Gap:** No usage pattern example showing form+channel both present (form-as-lens pattern). A user would need to reason the interaction independently.

#### Seed 492 — `plan full gherkin dip-bog teach_junior_dev`
**Reference utility: 5**
- All tokens well-documented. gherkin with plan task = clean.
- **No gaps identified.**

#### Seed 563 — `make full view simulation wardley as-prompt-engineer`
**Reference utility: 4**
- wardley: "Conceptual mapping of component evolution and strategic positioning." Sufficient.
- simulation (method): Token catalog has it. The `sim` task notes reference the distinction, but the `simulation` method entry doesn't cross-link to `sim`.
- **Gap:** `simulation` method catalog entry doesn't say "Distinct from sim task (sim = scenario playback task; simulation = thought-experiment reasoning method)." A user reading only the method entry could conflate these.

#### Seed 599 — `pull max act balance ladder adr fog teach_junior_dev`
**Reference utility: 4**
- adr channel notes: "Avoid with pull" — the warning is there. But scored 4 because ladder+adr forms a lens.
- The reference correctly flags the potential conflict (pull+adr); the actual good result came from the form-as-lens interaction.
- **Gap:** "Composition Rules → Incompatibilities → Precedence Examples" doesn't illustrate this form-as-lens rescue. The reference helps users avoid the bad pattern but doesn't explain when the combination is valid.

---

### Grammar Gap Seeds (Score-2)

#### Seed 533 — `plan skim grow dip-rog fun_mode` (R36)
**Reference utility: 4**
- "Choosing Directional" section correctly warns: "Avoid pairing compound directionals with `gist` or `skim` completeness."
- skim's Composition Rules note: "Avoid pairing with multi-phase directionals (bog, fip rog, fly rog, fog)" — partially covers it; dip-rog is a multi-phase directional but isn't listed explicitly.
- **Gap:** skim's Composition Rules note has an incomplete list (see catalog-feedback.md Issue 2). "Choosing Directional" saves this case, but the skim-specific note is misleading.

#### Seed 531 — `probe minimal shellscript executive_brief` (R40, shellscript+CEO)
**Reference utility: 5**
- shellscript Composition Rules guidance: "Avoid with non-technical audiences (to-CEO, to-managers, to-stakeholders, to-team)." Complete and correct.
- All documentation in place. Gap is grammar enforcement only (R41).

#### Seed 560 — `sim full shellscript fip-rog teach_junior_dev` (R40, shellscript+sim)
**Reference utility: 5**
- shellscript Composition Rules guidance: "Avoid with narrative tasks (sim, probe)." Complete and correct.
- Same as seed 531.

#### Seed 615 — `probe max robust commit peer_engineer` (commit+max)
**Reference utility: 5**
- commit Composition Rules guidance: "avoid deep or max completeness (no room to express depth)." Complete and correct.
- Gap is grammar enforcement only (R41).

---

### Score-3 Borderline Seeds

#### Seed 466 — `sort narrow fig as-programmer` (R37)
**Reference utility: 2**
- `narrow` token catalog entry: Notes column empty; no compatibility guidance.
- Composition Rules Completeness section: only `max` and `skim` listed; `narrow` absent from installed bar 2.64.1.
- `fig` compound directional listed and described.
- "Choosing Directional" says "compound directionals require full/deep completeness" — implicitly warns against narrow+fig, but doesn't explain the score-3 tradeoff for users who intentionally want narrow+fig.
- **Gap:** narrow guidance exists in dev grammar but is absent from the installed binary. This is the clearest reference gap from cycles 16–19.

#### Seed 556 — `probe skim rigor pm_to_team` (skim+rigor tension)
**Reference utility: 3**
- skim and rigor individually documented.
- rigor: "disciplined, well-justified reasoning." skim: "light pass." These are on different axes but semantically conflict.
- Neither token's notes address the volume-vs-depth tension.
- **Gap:** No cross-axis tension documentation between completeness and method tokens. Score-3 result is inherent to the combination but reference provides no signal.

---

## Aggregated Documentation Gaps

### Gap 1 — No "Choosing Channel" section in bar help llm

**Impact:** Channel selection requires scanning individual token entries. There's no quick-reference guide for channel selection analogous to "Choosing Scope," "Choosing Method," "Choosing Form," or "Choosing Directional."

All cross-axis channel incompatibilities are advisory-only (R41 scope), making the "Choosing Channel" section the most valuable near-term improvement: it would surface shellscript, commit, adr, and sync task/audience restrictions in one place.

**Recommendation for `help_llm.go renderHeuristics()`:**
```
### Choosing Channel

- **Shell script** → `shellscript`: code-producing tasks only (make, fix, show, trans, pull). Avoid with narrative tasks (sim, probe) and selection tasks (pick, diff, sort). Technical audience only — avoid with to-CEO, to-managers, to-stakeholders, to-team.
- **ADR** → `adr`: decision artifact — best with plan, probe, make. Avoid with pull, diff, sort, sim.
- **Gherkin tests** → `gherkin`: acceptance tests or analysis reframed as behavioral scenarios. Avoid prose-structure forms (story, case, log, questions, recipe).
- **Slides** → `presenterm`: structured delivery; supports ~12 slides. Avoid exhaustive content (max completeness); use full or minimal.
- **Session plan** → `sync`: agenda with timing and cues. Brief by design — avoid max completeness.
- **Commit message** → `commit`: Note — commit is a FORM token, not a channel. Avoid deep/max completeness.
```

### Gap 2 — "Grammar-enforced restrictions" section is empty

The `## Composition Rules` section ends with:
```
**Grammar-enforced restrictions:**
```
...then nothing. This misleads readers into thinking either (a) there are no restrictions, or (b) all listed restrictions are grammar-enforced.

**Recommendation:** Fill with honest content (see catalog-feedback.md Issue 4).

### Gap 3 — `narrow` guidance absent from installed binary

R37 fix exists in dev grammar but not in bar 2.64.1. Token catalog entry has empty Notes. Composition Rules completeness guidance doesn't include `narrow`. This is the highest-impact reference gap — it means R37's "use with awareness" signal is invisible to users.

### Gap 4 — `skim` Composition Rules note has incomplete compound directional list

Current: "Avoid pairing with multi-phase directionals (bog, fip rog, fly rog, fog)"
Should be: "Avoid pairing with any compound directional (fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog) or fog"

Inconsistency between skim's Composition Rules note (partial list) and "Choosing Directional" section (correct complete guidance) creates confusion.

### Gap 5 — No cross-axis tension documentation for completeness×method

skim+rigor (seed 556, score 3) represents a class of combinations where completeness and method pull in opposite directions. Currently undocumented. This is a low-priority gap since the score-3 is appropriate (usable but strained) and users would be unlikely to avoid it regardless.

---

## Score Summary

| Seed | Prompt score | Reference utility | Primary gap |
|------|-------------|------------------|-------------|
| 491 (probe+cocreate+gherkin+fip-rog) | 4 | 4 | form-as-lens pattern not in usage examples |
| 492 (plan+gherkin+dip-bog) | 4 | 5 | none |
| 563 (make+simulation+wardley) | 4 | 4 | simulation vs sim disambiguation |
| 599 (pull+balance+ladder+adr+fog) | 4 | 4 | form-as-lens rescue not in precedence examples |
| 533 (plan+skim+grow+dip-rog) | 2 | 4 | skim note incomplete; Choosing Directional saves it |
| 531 (probe+shellscript+executive_brief) | 2 | 5 | none — fully documented; grammar-only gap |
| 560 (sim+shellscript) | 2 | 5 | none — fully documented; grammar-only gap |
| 615 (probe+max+commit) | 2 | 5 | none — fully documented; grammar-only gap |
| 466 (sort+narrow+fig) | 3 | 2 | narrow guidance absent from installed binary |
| 556 (probe+skim+rigor) | 3 | 3 | cross-axis tension undocumented |

**Average reference utility: 4.1**

---

## Recommendations for `bar help llm`

| Priority | Section | Recommendation |
|----------|---------|----------------|
| High | `### Choosing Channel` | Add new section in `renderHeuristics()` — cross-axis channel restrictions in one place |
| High | `**Grammar-enforced restrictions:**` | Fill with honest statement: all cross-axis incompatibilities are advisory-only |
| High | `narrow` Completeness guidance | Propagate R37 dev-grammar guidance to installed binary via new bar release |
| Medium | `skim` Completeness guidance | Replace partial list with "all compound directionals + fog" |
| Medium | Usage Patterns | Add form-as-lens example showing form+channel composability |
| Low | `simulation` method catalog entry | Add "Distinct from sim task" disambiguation |
| Low | (none — may not be worth adding) | skim+rigor cross-axis tension note |
