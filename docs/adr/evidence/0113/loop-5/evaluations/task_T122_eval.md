## Task: T122 — Assess technical debt

**Task description:** "How bad is this module?"
**Probability weight:** 4%
**Domain:** assessment

---

**Skill selection log:**
- Task token: check (evaluation)
- Completeness: full
- Scope: considered good, fail, struct → chose: good
  - Why good? The new description focuses on "quality, success, or goodness is judged—criteria, metrics, standards." Technical debt assessment is about quality judgment. However, `fail` could also work (what's broken/fragile).
- Method: (none)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build check full good plain peer_engineer_explanation
```

---

**Coverage scores:**
- Token fitness: 4 — `good` covers quality assessment, but technical debt is also about `fail` (what's fragile)
- Token completeness: 4 — might benefit from both perspectives
- Skill correctness: 4 — reasonable choice but narrow
- Prompt clarity: 4 — will assess quality but may miss failure modes
- **Overall: 4**

**Gap diagnosis:** undiscoverable-pattern

**Notes:**
Technical debt assessment spans multiple scopes: `good` (quality criteria), `fail` (fragility/breakdowns), `struct` (coupling/complexity). The skill chose `good` which covers one dimension. This isn't wrong, but the new scope descriptions don't suggest combining scopes for multi-faceted assessments. Consider guidance for when to use multiple scopes or sequence them.

---

*Loop-5 realistic task evaluation*
