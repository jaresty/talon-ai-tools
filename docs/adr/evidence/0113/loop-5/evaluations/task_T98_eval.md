## Task: T98 — Identify recurring themes in code review feedback

**Task description:** "What issues keep coming up in our reviews?"
**Probability weight:** 5%
**Domain:** analysis
**Primary scope test:** motifs (recurring patterns)

---

**Skill selection log:**
- Task token: probe (surface patterns)
- Completeness: full
- Scope: considered fail, motifs → chose: motifs
  - Reason: Task asks about "what issues keep coming up" — recurring themes/patterns. New `motifs` description: "recurring structural or thematic forms that appear in multiple places" fits well. Not about failures specifically (fail), but about repeated observations.
- Method: induce (pattern identification)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build probe full motifs plain peer_engineer_explanation
```

**Bar output preview:**
> The response surfaces hidden assumptions, implications, dependencies, risks, or unstated context about the subject.
> [full, motifs scope, plain channel, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 5 — `motifs` captures recurring review themes
- Token completeness: 5 — appropriate for pattern identification
- Skill correctness: 5 — correctly chose motifs (recurring) over fail (breakdowns)
- Prompt clarity: 5 — clear recurring-issue focus
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
Good selection. New `motifs` description clearly positions it for identifying "repeated configurations or isomorphic patterns without analyzing their internal topology in detail."

---

*Loop-5 scope prompt validation task*
