## Task: T90 — Analyze internal component dependencies

**Task description:** "How are the services in this codebase connected?"
**Probability weight:** 10%
**Domain:** code
**Primary scope test:** struct vs cross discrimination

---

**Skill selection log:**
- Task token: show (explanation task)
- Completeness: full (thorough explanation needed)
- Scope: considered cross, struct → chose: struct
  - Reason: Task asks about "how services are connected" — this is about internal topology/arrangement (dependencies, coordination) rather than boundary-spanning concerns. New `struct` description: "internal topology of units" fits perfectly. `cross` would be for logging/auth propagation across boundaries.
- Method: (none selected — straight explanation)
- Form: (none selected)
- Channel: plain (prose explanation)
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build show full struct plain peer_engineer_explanation
```

**Bar output preview:**
> The response explains or describes the subject for the stated audience.
> [full, struct scope, plain channel, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 5 — `struct` precisely captures internal service topology question
- Token completeness: 5 — all dimensions covered appropriately
- Skill correctness: 5 — correctly discriminated struct (internal) from cross (boundary-spanning)
- Prompt clarity: 5 — resulting prompt will produce clear dependency explanation
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
New scope prompts working excellently. The clarification that `struct` focuses on "internal topology of units without emphasizing...boundary-spanning propagation" made the selection clear. Previously this might have been ambiguous between struct/cross.

---

*Loop-5 scope prompt validation task*
