# ADR-0113 Loop-8 Summary — Specialist Form Token Coverage

**Date:** 2026-02-17
**Status:** Complete
**Focus:** Validate whether specialist/exotic form tokens are discoverable by bar-autopilot

---

## Summary

Loop-8 tested specialist form tokens — forms with specific structural purposes that haven't
been systematically evaluated in prior loops.

- **Tasks evaluated:** 13 (T170–T182)
- **Mean score:** 3.38/5
- **Target:** ≥ 4.0 ❌ (significantly below target)
- **Root cause:** Systematic skill guidance gap — specialist forms have no usage patterns

This is the lowest mean score across all loops, confirming the central hypothesis:
**bar-autopilot defaults to generic forms and cannot discover specialist forms without usage patterns.**

---

## Central Finding

**All 13 specialist form tokens produce good prompts when manually selected.**
The prompts are well-described, semantically correct, and clearly rendered.

**The failure is entirely in discoverability.**

bar help llm contains 36 usage patterns, but none cover the 8 specialist forms that scored ≤3:
- wardley, wasinawa, spike (artifact), cocreate, taxonomy, facilitate, recipe, visual

Without a usage pattern, bar-autopilot defaults to:
- `walkthrough` for step-by-step tasks
- `checklist` for structured outputs
- `table` for classification/comparison
- `variants` for options
- `diagram` channel for visual/relational tasks

The specialist forms are systematically invisible to autopilot unless the user explicitly names them.

---

## Task Scores

| Task | Form | Overall | Notes |
|------|------|---------|-------|
| T170 | wardley | 3 | No usage pattern; autopilot → diagram or table |
| T171 | wasinawa | 3 | No usage pattern; autopilot → walkthrough |
| T172 | spike | 3 | No usage pattern + task token mismatch (plan → make) |
| T173 | cocreate | 3 | No usage pattern; autopilot → make+variants |
| T174 | ladder | 4 | Somewhat discoverable from explicit "abstraction levels" cue |
| T175 | taxonomy | 3 | No usage pattern + scope mismatch (struct → thing) |
| T176 | facilitate | 3 | No usage pattern; autopilot → plan+walkthrough |
| T177 | recipe | 3 | No usage pattern; most unusual form; autopilot → walkthrough |
| T178 | socratic | 4 | Discoverable from "through questions, not explanation" |
| T179 | merge | 4 | Reasonably discoverable from "combine multiple sources" |
| T180 | codetour | 5 | User-directed; channel name is self-describing |
| T181 | quiz | 4 | Discoverable from explicit "quiz" request |
| T182 | visual | 3 | No usage pattern; autopilot → diagram channel |

---

## Discoverability Analysis

### High discoverability (user-directed or self-describing):
- `codetour` — user names it explicitly (score 5)
- `quiz` — user says "through a quiz" (score 4)
- `socratic` — user says "through questions" (score 4)
- `merge` — "combine multiple sources" maps naturally (score 4)

### Medium discoverability (discoverable with strong cues):
- `ladder` — "step up and down abstraction levels" is a reasonable hint (score 4)

### Low discoverability (requires usage patterns):
- `wardley` — no cue in "map components"; autopilot picks diagram
- `wasinawa` — "reflect on what happened" doesn't surface wasinawa
- `spike` — "should we adopt X?" maps to diff or probe, not spike
- `cocreate` — "iterative design" maps to make+variants, not cocreate
- `taxonomy` — "classify all types" maps to table, not taxonomy
- `facilitate` — "plan a retrospective" maps to plan+walkthrough
- `recipe` — "document setup" maps to show+walkthrough
- `visual` — "show relationships" maps to diagram channel

---

## Gaps Found

### G-L8-01 — wardley: No usage pattern for strategic landscape mapping
**Gap type:** undiscoverable-token
**Severity:** Medium — Wardley maps are a standard strategy tool
**Fix:** Add "Strategic Landscape / Wardley Mapping" usage pattern

### G-L8-02 — wasinawa: No usage pattern for post-incident reflection
**Gap type:** undiscoverable-token
**Severity:** Medium — Post-incident retrospectives are common engineering tasks
**Fix:** Add "Post-Incident Reflection" usage pattern

### G-L8-03 — spike: No usage pattern + wrong task token in guidance
**Gap type:** skill-guidance-wrong
**Severity:** Medium — Research spikes are a common agile artifact
**Fix:** Add "Research Spike" usage pattern with `make` (not `plan`) task token

### G-L8-04 — cocreate: No usage pattern for collaborative/iterative design
**Gap type:** undiscoverable-token
**Severity:** Low-medium — Iterative design requests are common
**Fix:** Add "Collaborative / Iterative Design" usage pattern

### G-L8-05 — taxonomy + scope: No usage pattern; struct scope misfit
**Gap type:** skill-guidance-wrong
**Severity:** Low — Classification tasks are moderately common
**Fix:** Add "Classification / Type Taxonomy" usage pattern with `thing` scope

### G-L8-06 — facilitate: No usage pattern for facilitation planning
**Gap type:** undiscoverable-token
**Severity:** Medium — Facilitation planning is a distinct task type
**Fix:** Add "Facilitation Planning" usage pattern

### G-L8-07 — recipe: No usage pattern; most unusual form in catalog
**Gap type:** undiscoverable-token
**Severity:** Low — Recipe format is niche but distinctive
**Fix:** Add "Process-as-Recipe Documentation" usage pattern with walkthrough distinction

### G-L8-08 — visual vs diagram: No guidance distinguishing form from channel
**Gap type:** skill-guidance-wrong
**Severity:** Medium — visual form is always overridden by diagram channel default
**Fix:** Add visual vs diagram heuristic to Token Selection Heuristics

---

## Comparison to Prior Loops

| Loop | Focus | Mean Score |
|------|-------|------------|
| Loop-4 | Taxonomy generation | 4.87 |
| Loop-5 | Scope validation | 4.875 |
| Loop-6 | Token guidance (ADR-0128) | 4.5 |
| Loop-7 | Directionals + persona | 4.75 |
| **Loop-8** | **Specialist forms** | **3.38** |

Loop-8 is intentionally targeting a gap, not measuring overall catalog health.
The low score reflects a genuine systemic issue: form tokens are undercovered in skill guidance.

---

## Recommendation Priority

| Priority | Gap | Fix |
|----------|-----|-----|
| High | G-L8-01, G-L8-02, G-L8-06 | wardley, wasinawa, facilitate patterns |
| Medium | G-L8-03, G-L8-04, G-L8-08 | spike pattern + make fix, cocreate pattern, visual/diagram heuristic |
| Low | G-L8-05, G-L8-07 | taxonomy scope fix, recipe pattern |

---

## Conclusion

Specialist form tokens are well-designed and produce good prompts. The catalog is not broken.
The **skill guidance is the bottleneck**: 8 specialist forms have no usage patterns, making
them invisible to bar-autopilot without explicit user direction.

**Action needed:** Add 7 usage patterns and 1 heuristic to bar help llm (in bar-autopilot skill).

This is a concentrated, actionable finding. All 8 patterns follow the same structure:
- Task type description
- Pattern (bar command)
- Heuristic (when to select this vs. default alternatives)
