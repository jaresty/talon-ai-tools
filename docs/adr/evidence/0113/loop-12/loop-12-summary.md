# ADR-0113 Loop-12 Summary — Completeness Post-Apply + Scope Axis Discoverability

**Date:** 2026-02-18
**Status:** Complete
**Focus:** Part A — Post-apply validation of loop-11 completeness fixes (T196, T200)
           Part B — Scope axis discoverability (10 tasks, T201–T210)

---

## Part A — Post-Apply Validation: Loop-11 Completeness Fixes

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| T196 | gist | 3 | 4 | +1 | PASS |
| T200 | gist | 2 | 4 | +2 | PASS |

**Mean pre-fix:** 2.5 → **Mean post-fix:** 4.0 ✅

Both tasks now route correctly. "quick overview" hits "quick summary" + "overview"
triggers simultaneously; "standup" + "high-level" + "brief" → gist via use_when.

---

## Part B — Scope Axis Discoverability

### Task Scores

| Task | Expected Scope | Score | Gap? |
|------|---------------|-------|------|
| T201 | fail | 5 | No |
| T202 | struct | 4 | No |
| T203 | mean | 4 | No |
| T204 | time | 3 | Yes — G-L12-01 |
| T205 | agent | 2 | Yes — G-L12-02 |
| T206 | assume | 3 | Yes — G-L12-03 |
| T207 | motifs | 2 | Yes — G-L12-04 |
| T208 | good | 3 | Yes — G-L12-05 |
| T209 | view | 4 | No |
| T210 | stable | 2 | Yes — G-L12-06 |

**Mean score (Part B):** 3.2/5 — below 4.0 target

### Discoverability Tiers

**Tier 1 — Well-discoverable (no use_when needed):**
- `fail` (5) — "risks" in description + loop-1 usage patterns
- `struct` (4) — "structure/components" semi-self-naming
- `mean` (4) — token name semantics match "what does X mean"
- `view` (4) — "from the perspective of" maps directly

**Tier 2 — Gapped — now fixed:**
- `time` (3) — preempted by `flow` method; temporal framing missed
- `agent` (2) — confused with `actors` method; no routing distinction
- `assume` (3) — synonym gap: "assumptions" → "premises" not guaranteed
- `good` (3) — no heuristic for "quality criteria / what makes it good"
- `motifs` (2) — unusual name; "patterns" routes to method tokens
- `stable` (2) — description mismatch: system-theory vs. design-stability language

### Central Pattern

**Method tokens preempt scope tokens.** The most common failure mode in the scope axis
is not a missing token — it's a method token absorbing the user intent before scope is
consulted:
- "recurring patterns" → `mapping` or `cluster` method instead of `motifs` scope
- "flows through" → `flow` method instead of `time` scope
- "who decides" → `actors` method instead of `agent` scope

This is distinct from form/channel gaps (where the issue is obscure token names). Scope
tokens are conceptually clear but lose to methods in salience during selection.

### Fixes Applied (loop-12 apply step)

| Rec | Token | What was added |
|-----|-------|----------------|
| R-L12-01 | time | use_when: "step by step", "timeline", "sequence", "phases", "history" |
| R-L12-02 | agent | use_when: "who decides", "decision-making", "who has authority"; distinguishes from actors method |
| R-L12-03 | assume | use_when: "what assumptions", "what must be true", "hidden assumptions" |
| R-L12-04 | motifs | use_when: "recurring patterns", "appears in multiple places", "same pattern in different places" |
| R-L12-05 | good | use_when: "quality criteria", "what makes it good", "success criteria", "well-designed" |
| R-L12-06 | stable | use_when: "stable", "unlikely to change", "won't change", "what persists" |

Grammar regenerated. All tests pass (ok 1.434s).

---

## Loop History (Updated)

| Loop | Focus | Mean Score |
|------|-------|------------|
| Loop-8 | Specialist forms | 3.38 |
| Loop-9 | Post-apply (loop-8) | 5.0 |
| Loop-10 | Output channels | 4.15 |
| Loop-11A | Post-apply (loop-10) | 4.25 |
| Loop-11B | Completeness axis | 3.6 |
| **Loop-12A** | **Post-apply (loop-11)** | **4.0** ✅ |
| **Loop-12B** | **Scope axis** | **3.2** ⚠️ |

---

## SSOT Status

`AXIS_KEY_TO_USE_WHEN` now covers:

| Axis | Tokens with use_when | Total tokens |
|------|---------------------|--------------|
| completeness | 3 (gist, skim, narrow) | 7 |
| scope | 6 (agent, assume, good, motifs, stable, time) | 13 |
| channel | 4 (plain, sync, sketch, remote) | 15 |
| form | 9 (cocreate, facilitate, ladder, recipe, spike, visual, walkthrough, taxonomy, wasinawa) | ~32 |
| method | 0 | 51 |
| directional | 0 | 16 |
| task | 0 | 11 |

---

## Next Actions

Post-apply validation of loop-12 scope fixes should be loop-13.
After validation: method axis has 51 tokens with 0 use_when entries — largest remaining gap.
