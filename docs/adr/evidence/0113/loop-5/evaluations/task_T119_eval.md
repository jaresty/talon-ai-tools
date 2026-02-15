## Task: T119 — Investigate error handling consistency

**Task description:** "Are we handling errors consistently?"
**Probability weight:** 5%
**Domain:** code analysis

---

**Skill selection log:**
- Task token: probe (surface patterns)
- Completeness: full
- Scope: considered cross, motifs, fail → chose: cross
  - Why cross? The new description: "concerns or forces that propagate across otherwise distinct units" fits perfectly. Error handling is a cross-cutting concern that should be consistent across boundaries.
  - **Alternative:** `motifs` could also work (recurring patterns).
- Method: verify (consistency check)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build probe full cross plain verify peer_engineer_explanation
```

---

**Coverage scores:**
- Token fitness: 5 — `cross` captures boundary-spanning error handling
- Token completeness: 5 — verify method good for consistency
- Skill correctness: 5 — good selection
- Prompt clarity: 5 — clear consistency check
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
Good fit. New `cross` description: "how they traverse boundaries or become distributed across partitions" is exactly what error handling consistency analysis needs. The skill could have chosen `motifs` (recurring patterns), but `cross` is more precise for boundary-spanning concerns.

---

*Loop-5 realistic task evaluation*
