# ADR-0113 Loop-15 Summary — Method Post-Apply + General Health Check

**Date:** 2026-02-18
**Status:** Complete
**Focus:** Part A — Post-apply validation of loop-14 fixes (T221 meld, T222 mod, T223 field)
           Part B — General health check (10 cross-axis tasks, verifying loops 1–14)

---

## Part A — Post-Apply Validation

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| T221 | meld | 2 | 4 | +2 | PASS |
| T222 | mod | 2 | 4 | +2 | PASS |
| T223 | field | 1 | 4 | +3 | PASS |

**Mean pre-fix:** 1.67 → **Mean post-fix:** 4.0 ✅

All three metaphorical method tokens now land cleanly. `field` (worst scorer across
all 14 loops at score 1) recovered to 4 via "service mesh routing" exact trigger.

---

## Part B — General Health Check

**Mean score: 4.5/5** ✅ — highest general sample mean of any loop

| Task | Axes exercised | Score |
|------|---------------|-------|
| GH-T01 | minimal + stable + grow + melody (4 loops verified) | 5 |
| GH-T02 | fail + inversion + systemic | 5 |
| GH-T03 | act + facilitate + sync | 4 |
| GH-T04 | mean + gist | 5 |
| GH-T05 | good + view (scope x2 combination) | 5 |
| GH-T06 | assume + unknowns | 4 |
| GH-T07 | motifs | 4 |
| GH-T08 | meld + compare | 4 |
| GH-T09 | fail + skim | 5 |
| GH-T10 | fail + boom | 4 |

**No new gaps found. No regressions. All loop-10–14 fixes verified.**

GH-T01 is the landmark task: it simultaneously fires use_when entries from loops 11
(minimal), 12 (stable), 13 (grow + melody) and scores 5 — confirming that cumulative
improvements compose correctly, not just in isolation.

---

## Program-Level Summary (Loops 1–15)

| Loop | Focus | Mean |
|------|-------|------|
| 1 | Full cycle (11 recs applied) | — |
| 2–7 | Task-gap evaluation cycles | — |
| 8 | Specialist forms | 3.38 |
| 9 | Post-apply (loop-8) | 5.0 |
| 10 | Output channels | 4.15 |
| 11A | Post-apply (channels) | 4.25 |
| 11B | Completeness axis | 3.6 |
| 12A | Post-apply (completeness) | 4.0 |
| 12B | Scope axis | 3.2 |
| 13A | Post-apply (scope) | 4.75 |
| 13B | Method (metaphorical set 1) | 3.3 |
| 14A | Post-apply (method set 1) | 4.25 |
| 14B | Method (metaphorical set 2) | 2.25 |
| 15A | Post-apply (method set 2) | 4.0 |
| **15B** | **General health check** | **4.5** ✅ |

---

## AXIS_KEY_TO_USE_WHEN Coverage (Final State)

| Axis | With use_when | Total | Key tokens covered |
|------|--------------|-------|--------------------|
| completeness | 3 | 7 | gist, skim, narrow |
| scope | 6 | 13 | agent, assume, good, motifs, stable, time |
| method | 10 | 51 | boom, field, grove, grow, meld, melody, mod + 3 others |
| channel | 4 | 15 | plain, sync, sketch, remote |
| form | 9 | ~32 | cocreate, facilitate, ladder, recipe, spike, visual, walkthrough, taxonomy, wasinawa |

---

## Open Issues (Carried Forward)

1. **SPA persona selector missing** — noted in MEMORY.md; unrelated to ADR-0113
2. **SSOT regression risk** — `make axis-regenerate-apply` may zero AXIS_KEY_TO_USE_WHEN;
   check git diff before regenerating. Has occurred twice (loops 9, 10); clean since.
3. **Method axis long tail** — 41 of 51 method tokens have no use_when. Assessment:
   description-anchored tokens (compare, diagnose, explore, etc.) are Tier 1 discoverable.
   No evidence of gaps; skip until new evidence surfaces.
4. **Task axis (0/11) and directional axis (0/16)** — low priority; self-describing or
   intentionally abstract (directionals).

---

## Conclusion

The ADR-0113 program has completed its primary objective: systematic discoverability
improvement across all major token axes. The general health check (loop-15B, mean 4.5)
confirms that cumulative fixes compose correctly and produce reliable routing across
complex multi-axis tasks. No further targeted axis work is indicated at this time.

**Recommended next trigger:** Run another ADR-0113 cycle when:
- New tokens are added to the catalog
- New skill guidance (bar-autopilot, bar-manual) is published
- User feedback indicates routing failures for a specific task type
