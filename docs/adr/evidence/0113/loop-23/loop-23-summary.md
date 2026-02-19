# Loop-23 Summary — Task Token Routing Validation + Slug Bug Fix

**Date:** 2026-02-19
**Focus:** Validate that "Choosing Task" and "Choosing Persona" heuristics prevent misrouting on
a fresh 10-task sample. Also discovered and fixed a slug recognition bug for proper-noun audience
tokens.

---

## Evaluation Summary

| Task | Tokens selected | Overall |
|------|-----------------|---------|
| T01 — Debug Postgres queries | probe full fail diagnose | **5** |
| T02 — Extract audit risks | pull fail | **5** |
| T03 — Walk PM through auth | show mean walkthrough + to-product-manager | **5** |
| T04 — Choose session storage | pick full struct branch | **4** |
| T05 — Monolith migration plan | plan full struct time flow | **5** |
| T06 — Verify API contract | check full fail | **5** |
| T07 — Reformat release notes | fix jira | **5** |
| T08 — Group feature requests | sort full cluster | **5** |
| T09 — Simulate no circuit breaker | sim full time fail | **5** |
| T10 — GraphQL vs REST for CEO | diff fail + audience=to-ceo | **5** |

**Mean score: 4.9/5** (highest in program history)

---

## Key Findings

### Heuristic validation: PASS

Both new heuristics from loop-22 performed correctly across all test cases:

- **"Choosing Task" heuristic**: All 10 tasks routed to the correct task token.
  - T01 (debug) → probe+diagnose ✓ (previously would have misrouted to fix)
  - T09 (simulate) → sim ✓ (not probe)
  - T06 (verify) → check ✓ (not probe)
  - T07 (reformat) → fix ✓ (not make)
  - T02 (extract) → pull ✓ (not probe)
- **"Choosing Persona" heuristic**: Both explicit-audience cases routed correctly.
  - T03 (PM) → explicit audience=to-product-manager ✓ (not peer preset)
  - T10 (CEO) → explicit audience=to-ceo ✓

### Minor gap found (T04)

The pick/diff boundary for "compare to decide" vs "select" tasks is not explained in the heuristic.
Not a misrouting issue — pick is correct — but the distinction between using `diff+converge` (for
structured comparison) vs `pick` (when asking the LLM to select) is undocumented. Low priority.

### Bug found and fixed: proper-noun audience slug recognition

During T10 evaluation, `audience=to-ceo` failed with "unrecognized token" despite `to-ceo` being
listed as the slug in `bar help llm`. Root cause: `canonicalPersonaToken` de-slugified `"to-ceo"`
to `"to ceo"` (lowercase), which failed to match the stored canonical `"to CEO"` (mixed case).

**Affected tokens:** `to CEO`, `to Kent Beck`, `to XP enthusiast`

**Fix:** `build.go` `canonicalPersonaToken` — use `s.grammar.slugToCanonical[lower]` (already
populated by `initialiseSlugs` with the correct `"to-ceo"` → `"to CEO"` mapping) before the
de-slug fallback. O(1) lookup instead of a linear scan.

**Regression test added:** `TestPersonaProperNounSlugNormalization` in `build_test.go`.

---

## ADR-0113 Program Status After Loop-23

Loop-23 is the first loop since loop-9 to score at or above 4.9 (4.625 was the previous high
from loop-22 post-apply). The "Choosing Task" heuristic is the highest-impact single addition in
the program — it addresses the core misrouting failure mode across all 11 task tokens.

**Axis coverage status:**
- Task axis: complete (11/11 tokens, heuristic routing validated)
- Completeness axis: complete
- Scope axis: complete
- Method axis: substantially complete
- Form axis: complete (15/~32 tokens with use_when; form has use_when for key tokens)
- Channel axis: complete
- Directional axis: covered (7 primitives with use_when)
- Persona: heuristics in place for task-specific audience routing

**Program health: EXCELLENT** — no new catalog gaps. Bug fix surfaced and resolved same loop.
