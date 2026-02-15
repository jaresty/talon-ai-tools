## Task: T95 — Map authentication flow boundaries

**Task description:** "How does auth propagate across our services?"
**Probability weight:** 7%
**Domain:** code
**Primary scope test:** cross vs struct discrimination

---

**Skill selection log:**
- Task token: show (explanation)  
- Completeness: full
- Scope: considered struct, cross → chose: cross
  - Reason: Auth is a concern that "propagates across otherwise distinct units" — boundary-spanning. New `cross` description emphasizes "traverses boundaries or becomes distributed across partitions." This is not about internal service structure (struct) but about auth flow across boundaries.
- Method: flow (process tracing)
- Form: diagram (visual representation)
- Channel: diagram
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build show full cross diagram flow peer_engineer_explanation
```

**Bar output preview:**
> The response explains or describes the subject for the stated audience.
> [full, cross scope, diagram channel, flow form, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 5 — `cross` captures boundary-spanning auth propagation
- Token completeness: 5 — flow+diagram appropriate for tracing auth
- Skill correctness: 5 — correctly identified cross-cutting nature
- Prompt clarity: 5 — clear auth flow visualization prompt
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
Clear discrimination. Auth is a classic cross-cutting concern. New `cross` description: "how they traverse boundaries or become distributed across partitions" makes this selection obvious.

---

*Loop-5 scope prompt validation task*
