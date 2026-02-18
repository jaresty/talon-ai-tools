# ADR-0113 Loop-14 Summary — Method Post-Apply + Remaining Metaphorical Tokens

**Date:** 2026-02-18
**Status:** Complete
**Focus:** Part A — Post-apply validation of loop-13 method fixes (T211, T212, T213, T218)
           Part B — Remaining metaphorical method tokens: meld, mod, field, shift (T221–T224)

---

## Part A — Post-Apply Validation: Loop-13 Method Fixes

| Task | Method | Pre-fix | Post-fix | Delta | Verdict |
|------|--------|---------|---------|-------|---------|
| T211 | boom | 2 | 4 | +2 | PASS |
| T212 | grove | 1 | 4 | +3 | PASS |
| T213 | melody | 2 | 4 | +2 | PASS |
| T218 | grow | 2 | 5 | +3 | PASS |

**Mean pre-fix:** 1.75 → **Mean post-fix:** 4.25 ✅

T218 (grow) reached 5 — three simultaneous exact-phrase triggers.
T212 (grove, was score 1) now scores 4 — the largest absolute improvement across all loops.

---

## Part B — Remaining Metaphorical Method Tokens

| Task | Token | Score | Gap? |
|------|-------|-------|------|
| T221 | meld | 2 | Yes — G-L14-01 |
| T222 | mod | 2 | Yes — G-L14-02 |
| T223 | field | 1 | Yes — G-L14-03 |
| T224 | shift | 4 | No |

**Mean (Part B):** 2.25/5

`field` scored 1 — the lowest score of any token across all 14 loops.
Physics-theory vocabulary ("shared structured medium", "structural compatibility")
is completely disconnected from software engineering terminology.

`shift` scored 4 — the most intuitive metaphorical name ("shift perspective" is a
common phrase), and users who frame tasks with explicit multi-angle structures
trigger it naturally.

### Fixes Applied

| Rec | Token | When to use added |
|-----|-------|-------------------|
| R-L14-01 | meld | "balance between", "overlap between", "navigate tensions between" |
| R-L14-02 | mod | "cyclic behavior", "periodic pattern", "repeats across cycles" |
| R-L14-03 | field | "shared infrastructure", "service mesh routing", "effects propagate through" |

Grammar regenerated. All tests pass (ok 1.688s). SSOT intact.

---

## Metaphorical Token Inventory: Complete

All metaphorical method tokens now have use_when entries:

| Token | Name metaphor | use_when added |
|-------|--------------|----------------|
| boom | onomatopoeia | loop-13 |
| grove | botanical | loop-13 |
| grow | generic growth | loop-13 |
| melody | musical | loop-13 |
| meld | blending | loop-14 |
| mod | mathematical | loop-14 |
| field | physics | loop-14 |
| shift | movement | loop-14 (not needed — score 4) |

The catalog's metaphorical method tokens are now all routing-equipped.
Remaining method tokens (compare, diagnose, explore, branch, etc.) are
description-anchored and expected to score ≥4 without use_when.

---

## Loop History (Updated)

| Loop | Focus | Mean Score |
|------|-------|------------|
| Loop-12B | Scope axis | 3.2 |
| Loop-13A | Post-apply (scope) | 4.75 |
| Loop-13B | Method axis (metaphorical) | 3.3 |
| **Loop-14A** | **Post-apply (method metaphorical)** | **4.25** ✅ |
| **Loop-14B** | **Method axis (remaining metaphorical)** | **2.25** ⚠️ → fixed |

---

## AXIS_KEY_TO_USE_WHEN Coverage (Post Loop-14)

| Axis | With use_when | Total | % |
|------|--------------|-------|---|
| completeness | 3 | 7 | 43% |
| scope | 6 | 13 | 46% |
| method | 7 | 51 | 14% |
| channel | 4 | 15 | 27% |
| form | 9 | ~32 | 28% |
| task | 0 | 11 | 0% |
| directional | 0 | 16 | 0% |

---

## Next: General Health Check

After 14 loops of targeted axis improvements, the recommended next loop is a
**cross-axis general health check**: 10 diverse tasks drawing on the full token
catalog to verify cumulative improvements hold together and no cross-axis
regressions have emerged.
