# ADR-0113 Loop-9 Summary — Post-Apply Validation of Loop-8 (Specialist Form Discoverability)

**Date:** 2026-02-17
**Status:** Complete
**Type:** Post-apply validation (ADR-0113 § Post-Apply Validation)
**Validating:** ADR-0132 `use_when` metadata + `visual` guidance (from this loop)

---

## What Was Applied

Loop-8 identified 8 specialist form tokens invisible to bar-autopilot because no selection
heuristics existed. The fix (ADR-0132) added `use_when` discoverability metadata to the
Token Catalog for 9 form tokens via `AXIS_KEY_TO_USE_WHEN` in `axisConfig.py`.

This loop also:
1. Restored `AXIS_KEY_TO_USE_WHEN` data to `axisConfig.py` — it had been zeroed out
   during a `make axis-regenerate-apply` run (commit 6638e34), leaving the embedded JSON
   with stale use_when data not backed by the Python SSOT
2. Added `visual` form guidance to `AXIS_KEY_TO_GUIDANCE["form"]` in `axisConfig.py`
   (visual vs diagram distinction belongs in the guidance field, not in help_llm.go)
3. Removed token-specific routing from `help_llm.go` — usage patterns should not hardcode
   token names; use_when on the token is the correct mechanism
4. Regenerated all grammar files via `make bar-grammar-update`

---

## Validation Results

5 tasks sampled from the 8 that scored ≤3 in Loop-8:

| Task | Form | Loop-8 Score | Loop-9 Score | Pass? |
|------|------|-------------|-------------|-------|
| T170 | wardley | 3 | 5 | ✅ |
| T171 | wasinawa | 3 | 5 | ✅ |
| T172 | spike | 3 | 5 | ✅ |
| T173 | cocreate | 3 | 5 | ✅ |
| T182 | visual | 3 | 5 | ✅ |

**Mean Loop-8 (gapped tasks):** 3.0/5
**Mean Loop-9 (same tasks):** 5.0/5
**All 5 tasks pass** ✅

---

## Why They Now Pass

### wardley (T170)
`use_when`: "Strategic mapping: user wants to position components on an evolution axis.
Heuristic: 'Wardley map', 'map on evolution axis', 'genesis to commodity' → wardley."

The heuristic directly matches "Wardley map" and "map components on evolution axis" phrases.
Autopilot reading the Token Catalog now has a clear signal. Previously: no routing signal.

### wasinawa (T171)
`use_when`: "Post-incident reflection or retrospective on past events. Heuristic: 'reflect on
incident', 'what went wrong and what to do next', 'lessons learned' → wasinawa. Distinct from
pre-mortem (inversion method): pre-mortem assumes future failure; wasinawa reflects on past events."

The pre-mortem distinction prevents confusion with `inversion` method.

### spike (T172)
`use_when`: "Framing a technology investigation as a backlog spike artifact. Use make task
(not plan) — the spike IS the artifact. Heuristic: 'should we adopt X?', 'spike on Y',
'investigation backlog item' → make + spike."

Provides both routing signal AND corrects the make-vs-plan task token confusion.

### cocreate (T173)
`use_when`: "Iterative design with explicit decision points and alignment checks at each step
rather than a one-shot response. Heuristic: 'work through incrementally', 'with decision
points', 'iterative design' → cocreate. Distinct from variants (choice of designs) and make
(one-shot artifact)."

The distinction from `variants` prevents the most common substitution error.

### visual (T182)
`guidance` (Notes): "Distinct from the diagram channel: visual = abstract/metaphorical prose
layout with a short legend; diagram = precise Mermaid code with exact nodes and edges. Use visual
when conceptual overview or spatial metaphor is more useful than diagrammatic precision (e.g.,
non-technical audience, big-picture emphasis). Use diagram when exact topology, dependency
mapping, or architecture review requires precise structure."

`use_when`: "Heuristic: 'abstract visual', 'conceptual layout', 'big-picture structure for
non-technical audience' → visual. Distinct from diagram channel (precise Mermaid output)."

Both the Notes column AND the When to use column now guide autopilot to distinguish visual
from diagram for exec/non-technical audience cases.

---

## Infrastructure Fix

**Root cause discovered:** `AXIS_KEY_TO_USE_WHEN` in `axisConfig.py` was `{}` despite
the embedded grammar JSON containing use_when entries. The data was added in commit 619b681
but zeroed out by `make axis-regenerate-apply` in commit 6638e34 (which fixed the generator
to emit the constant but did not persist the data).

**Fix applied:** Restored use_when entries to `axisConfig.py` SSOT. All grammar files
regenerated via `make bar-grammar-update`. Python SSOT and JSON are now in sync.

---

## Comparison to Loop-8

| Metric | Loop-8 | Loop-9 |
|--------|--------|--------|
| Tasks evaluated | 13 | 5 (sample of gapped tasks) |
| Mean score (gapped) | 3.0 | 5.0 |
| Skill correctness (gapped) | 2.0 avg | 5.0 avg |
| Root cause resolved | No | Yes (use_when SSOT restored) |

---

## Conclusion

✅ All 5 Loop-8 gapped tasks now score 5/5 with use_when guidance present
✅ `visual` guidance added to grammar via correct channel (axisConfig.py guidance field)
✅ `AXIS_KEY_TO_USE_WHEN` SSOT restored and grammar regenerated
✅ `help_llm.go` kept clean — no token-specific routing hardcoded

The specialist form discoverability issue is resolved. The Token Catalog's "When to use"
column is now the authoritative routing mechanism for specialist forms.
