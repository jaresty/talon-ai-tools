# ADR-0085 Phase 2h — Composition Signal Detection Evidence

## Session 2026-04-09

**Seeds evaluated:** 1–10 with `--include method --fill 1.0`
**Method tokens surfaced:** paradox, automate, induce, domains, ladder, dimension, migrate, melody, ground, diagnose

**Candidates evaluated this session:**

### calc + chain — COMPOSITION (2026-04-09)

Surfaced via: seed 3 (`chain`), matched against top candidate `calc+chain` from `make composition-candidates`.

Emergent requirement test:
- **calc alone**: conclusions must be constrained by executable step outputs — no predecessor-reproduction requirement
- **chain alone**: each step must reproduce predecessor's actual output — no requirement about executable steps
- **calc + chain combined**: the two requirements interact — each calculation output must be quoted exactly before the reasoning that depends on it can proceed. Neither token alone imposes this combined constraint.

**Verdict:** composition warranted. Prose added to `lib/compositionConfig.py`. Grammar regenerated. Tests pass.
