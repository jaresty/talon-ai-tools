# ADR-0085: Bar Skills Feedback
**Date:** 2026-02-25
**Cycles covered:** 16–19 (seeds 456–615)
**Meta-analysis method:** `bar build probe full domains gap` — evaluating where skill guidance implicitly assumes user knowledge that isn't made explicit, and where restrictions are documented but unreachable via the normal skill workflow.

---

## Seed Evaluations

### Positive Patterns (Score-4)

#### Seed 491 — `probe full cocreate gherkin fip-rog as-writer appreciate`
**Skill alignment: 4**
- Choosing Form: `cocreate` listed. Choosing Directional: compound dir + full = fine.
- gherkin channel: Notes say "analysis tasks reframed as Gherkin scenarios" — a user following the skill to check Composition Rules would find this.
- The combination is valid but requires consulting multiple sections; no single heuristic surfaces it.
- **Gap:** No "Usage Patterns" example for form+channel both present (form-as-lens pattern).

#### Seed 492 — `plan full gherkin dip-bog teach_junior_dev`
**Skill alignment: 4**
- gherkin and compound directional straightforward. teach_junior_dev preset listed.
- **No gaps identified.**

#### Seed 563 — `make full view simulation wardley as-prompt-engineer`
**Skill alignment: 4**
- wardley in Choosing Form; simulation (method) in catalog; view in Choosing Scope.
- `simulation` (method) vs `sim` (task) distinction is noted in task catalog but not in method catalog.
- **Gap:** "Choosing Method" section doesn't disambiguate `simulation` (method) from `sim` (task). A user could confuse these.

#### Seed 599 — `pull max act balance ladder adr fog teach_junior_dev`
**Skill alignment: 4**
- adr channel guidance says "Avoid with pull" — a user checking Composition Rules would flag this.
- Actual score was 4 because `ladder` (form) + `adr` (channel) = form-as-lens that rescued the combination.
- **Gap:** Skill workflow correctly routes to Composition Rules, but the form-as-lens rescue path (ladder reframes adr from decision artifact to structural tool) is not documented. A user following the skill might over-apply the "avoid with pull" warning.

---

### Grammar Gap Seeds (Score-2)

#### Seed 533 — `plan skim grow dip-rog fun_mode` (R36)
**Skill alignment: 4**
- "Choosing Directional" section: "Avoid pairing compound directionals with `gist` or `skim`."
- skim Composition Rules note also covers dip-rog (implicitly, as multi-phase).
- A user following the skill workflow and reading Choosing Directional would catch this.
- **No skill gap** — documentation path is adequate. Gap is grammar enforcement only (R41).

#### Seed 531 — `probe minimal shellscript executive_brief` (R40, shellscript+CEO)
**Skill alignment: 4**
- Skill says to check Composition Rules before building.
- shellscript's guidance in Composition Rules: "Avoid with non-technical audiences (to-CEO, to-managers, to-stakeholders, to-team)."
- executive_brief preset = to-CEO audience.
- A user following the skill workflow would catch this.
- **No skill gap** — documentation path is adequate. Gap is grammar enforcement only (R41).

#### Seed 560 — `sim full shellscript fip-rog teach_junior_dev` (R40, shellscript+sim)
**Skill alignment: 4**
- shellscript guidance: "Avoid with narrative tasks (sim, probe)."
- Same finding as seed 531.
- **No skill gap.**

#### Seed 615 — `probe max robust commit peer_engineer` (commit+max)
**Skill alignment: 4**
- commit Composition Rules: "avoid deep or max completeness (no room to express depth)."
- A user following the skill workflow would catch this.
- **No skill gap** — documentation path is adequate. Gap is grammar enforcement only (R41).

---

### Score-3 Borderline Seeds

#### Seed 466 — `sort narrow fig as-programmer` (R37, narrow+compound dir)
**Skill alignment: 2**
- "Choosing Directional" section says compound dirs need full/deep completeness — this would guide users AWAY from narrow+fig, so they'd never accidentally hit R37.
- But if a user intentionally wants narrow+fig (focused multi-angle examination), there's no guidance explaining the score-3 tradeoff.
- `narrow` catalog entry has no Notes.
- `narrow` missing from Composition Rules completeness guidance in installed bar 2.64.1 (dev repo fix exists but not propagated — see catalog-feedback.md).
- **Gap:** The "use with awareness" quality of R37 is invisible in the skill. Either the guidance should appear in the installed binary, or "Choosing Directional" should note that narrow+compound is possible but demanding.

#### Seed 556 — `probe skim rigor pm_to_team` (skim+rigor tension)
**Skill alignment: 3**
- skim and rigor are individually well-documented.
- No note about their axis-tension (volume vs. method depth).
- A user would pick each token independently without knowing they create a score-3 combination.
- **Gap:** Cross-axis tension between completeness tokens and method tokens is undocumented. Not every tension warrants a note, but skim+rigor is the clearest case (constraining volume while demanding depth is a meaningful friction).

---

## Aggregated Skill Gaps

### Gap 1 — No "Choosing Channel" heuristics section
The skills have "Choosing Scope," "Choosing Method," "Choosing Form," and "Choosing Directional" but no "Choosing Channel." Users must scan individual channel token entries to discover task or audience restrictions. Since all cross-axis channel incompatibilities are documentation-only (R41 scope), a "Choosing Channel" section with a compatibility matrix would be the most effective mitigation short of grammar enforcement.

**Recommendation:** Add `### Choosing Channel` to `bar help llm` (help_llm.go `renderHeuristics()`):
```
- **Shell script output** → `shellscript` (only with code-producing tasks; technical audience only)
- **Conventional commit** → `commit` (form token, not channel; avoid max/deep completeness)
- **ADR format** → `adr` (decision tasks: plan, probe, make; avoid pull, diff, sort, sim)
- **Gherkin tests** → `gherkin` (make for spec, or analysis tasks reframed as scenarios)
- **Slides** → `presenterm` (supports up to ~12 slides; not for exhaustive content)
- **Session agenda** → `sync` (brief by design; avoid max completeness)
```

### Gap 2 — form-as-lens rescue path undocumented
When a form token + channel token are both present, the channel wins but form becomes a content lens. The current skill says "channel tokens take precedence over form tokens" but doesn't explain that this composability means a form like `ladder` or `wardley` can partially rescue an otherwise-incompatible task+channel pair.

**Recommendation:** Add a note to "Precedence Examples" in bar help llm:
> "When form and channel combine: the channel defines output format; the form describes conceptual organization. Example: `pull+adr+ladder` — adr channel wins, but ladder shapes what gets extracted as a hierarchical structure rather than a flat list."

### Gap 3 — `simulation` method vs `sim` task disambiguation in method selection
The "Choosing Method" section doesn't warn that `simulation` (method) is distinct from `sim` (task). These can compose: `sim` task + `simulation` method means "play out a scenario using the thought-experiment method." But a user might incorrectly use `simulation` as a task synonym for `sim`.

**Recommendation:** Add disambiguation to Choosing Method:
> "For simulations: `sim` (task) = scenario playback task; `simulation` (method) = thought-experiment reasoning method. These can compose: `sim simulation` = run a scenario via explicit counterfactual modeling."

---

## Score Summary

| Seed | Task+constraints | Prompt score | Skill alignment | Notes |
|------|-----------------|--------------|-----------------|-------|
| 491 | probe cocreate gherkin fip-rog | 4 | 4 | form-as-lens not in patterns |
| 492 | plan gherkin dip-bog | 4 | 4 | clean |
| 563 | make simulation wardley | 4 | 4 | sim vs simulation gap |
| 599 | pull balance ladder adr fog | 4 | 4 | form-as-lens rescue undocumented |
| 533 | plan skim grow dip-rog | 2 | 4 | R36 documented; grammar-only gap |
| 531 | probe shellscript executive_brief | 2 | 4 | R40 documented; grammar-only gap |
| 560 | sim shellscript | 2 | 4 | R40 documented; grammar-only gap |
| 615 | probe max commit | 2 | 4 | commit+max documented; grammar-only gap |
| 466 | sort narrow fig | 3 | 2 | narrow guidance missing from installed binary |
| 556 | probe skim rigor | 3 | 3 | cross-axis tension undocumented |

**Average skill alignment: 3.7**

---

## Recommendations for Skills

| Priority | Recommendation | Affected skill | Section |
|----------|---------------|----------------|---------|
| High | Add "Choosing Channel" section to bar help llm | bar-autopilot, bar-workflow | Token Selection Heuristics |
| Medium | Document form-as-lens rescue path in Precedence Examples | bar-autopilot | Composition Rules |
| Medium | Clarify `simulation` (method) vs `sim` (task) in method selection | bar-autopilot, bar-workflow | Choosing Method |
| Low | Add skim+rigor cross-axis tension note | bar-autopilot | Choosing Completeness |
