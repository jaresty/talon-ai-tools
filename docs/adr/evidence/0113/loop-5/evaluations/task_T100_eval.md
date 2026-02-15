## Task: T100 — Analyze error handling distribution

**Task description:** "Is error handling consistent across the codebase?"
**Probability weight:** 5%
**Domain:** code
**Primary scope test:** cross (boundary-spanning)

---

**Skill selection log:**
- Task token: probe (surface patterns)
- Completeness: full
- Scope: considered struct, cross → chose: cross
  - Reason: Error handling is a concern that "propagates across otherwise distinct units" — classic cross-cutting concern. New `cross` description: "examining how they traverse boundaries or become distributed across partitions" matches perfectly. Task asks about consistency "across the codebase" (boundary-spanning), not within individual modules.
- Method: verify (consistency check)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build probe full cross plain verify peer_engineer_explanation
```

**Bar output preview:**
> The response surfaces hidden assumptions, implications, dependencies, risks, or unstated context about the subject.
> [full, cross scope, plain channel, verify method, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 5 — `cross` precisely captures boundary-spanning error handling
- Token completeness: 5 — all dimensions appropriate
- Skill correctness: 5 — correctly identified cross-cutting nature
- Prompt clarity: 5 — clear consistency-check focus
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
Excellent discrimination. Error handling is a canonical cross-cutting concern. New `cross` description makes the selection clear: "concerns or forces that propagate across otherwise distinct units...examining how they traverse boundaries."

---

*Loop-5 scope prompt validation task*
