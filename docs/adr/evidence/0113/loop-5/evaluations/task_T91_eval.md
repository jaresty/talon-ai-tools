## Task: T91 — Trace logging across microservices

**Task description:** "Where does our request logging happen in the distributed system?"
**Probability weight:** 9%
**Domain:** code
**Primary scope test:** cross (boundary-spanning)

---

**Skill selection log:**
- Task token: probe (surface patterns)
- Completeness: full (comprehensive trace)
- Scope: considered struct, cross → chose: cross
  - Reason: Logging is a concern that "propagates across otherwise distinct units, layers, or domains" — exactly matching new `cross` description. This examines how logging traverses service boundaries, not internal service structure.
- Method: induce (pattern identification)
- Form: (none selected)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build probe full cross plain peer_engineer_explanation
```

**Bar output preview:**
> The response surfaces hidden assumptions, implications, dependencies, risks, or unstated context about the subject.
> [full, cross scope, plain channel, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 5 — `cross` perfectly captures boundary-spanning logging concern
- Token completeness: 5 — appropriate for distributed tracing task
- Skill correctness: 5 — correctly identified cross-cutting nature vs structural analysis
- Prompt clarity: 5 — prompt clearly targets distributed logging patterns
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
Excellent discrimination. New `cross` description: "concerns or forces that propagate across otherwise distinct units, layers, or domains" makes the boundary-spanning nature explicit. Contrast with T90 shows clear struct/cross distinction working.

---

*Loop-5 scope prompt validation task*
