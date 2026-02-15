## Task: T124 — Trace request flow

**Task description:** "Follow a request through the system"
**Probability weight:** 3%
**Domain:** system understanding

---

**Skill selection log:**
- Task token: show (explanation)
- Completeness: full
- Scope: considered flow, cross, time → chose: flow
  - Why flow? This is about process/procedure sequence—request path through components. `flow` is the right token for this.
  - **Consideration:** `cross` could also work since the request traverses boundaries, but `flow` is more specific to process tracing.
- Method: (none)
- Form: diagram (visual trace)
- Channel: diagram
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build show full flow diagram peer_engineer_explanation
```

---

**Coverage scores:**
- Token fitness: 5 — `flow` captures process sequence perfectly
- Token completeness: 5 — diagram channel good for visual trace
- Skill correctness: 5 — excellent selection
- Prompt clarity: 5 — clear request flow visualization
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
Good selection. `flow` (process/procedure) is distinct from `time` (general temporal) and `cross` (boundary-spanning concerns). The new scope descriptions for other tokens didn't interfere with this clear choice. The skill correctly identified this as process tracing, not structural analysis or concern distribution.

---

*Loop-5 realistic task evaluation*
