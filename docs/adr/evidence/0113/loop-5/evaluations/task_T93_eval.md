## Task: T93 — Identify recurring architectural patterns

**Task description:** "What patterns keep appearing in our API designs?"
**Probability weight:** 8%
**Domain:** analysis
**Primary scope test:** motifs (recurring patterns)

---

**Skill selection log:**
- Task token: probe (surface patterns)
- Completeness: full
- Scope: considered struct, motifs → chose: motifs
  - Reason: Task asks about "patterns that keep appearing" — recurring forms. New `motifs` description: "recurring structural or thematic forms that appear in multiple places, identifying repeated configurations" matches perfectly. `struct` would analyze a single structure in detail.
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
- Token fitness: 5 — `motifs` directly addresses recurring pattern identification
- Token completeness: 5 — all task dimensions captured
- Skill correctness: 5 — correctly distinguished motifs (recurring) from struct (single structure)
- Prompt clarity: 5 — clear pattern-identification focus
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
New `motifs` description excellent: "recurring structural or thematic forms...without analyzing their internal topology in detail or their boundary-spanning distribution." This positions motifs clearly between struct (single structure analysis) and cross (boundary-spanning).

---

*Loop-5 scope prompt validation task*
