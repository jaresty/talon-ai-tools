## Task: T110 — Debug why production is slow

**Task description:** "The API latency spiked, find the bottleneck"
**Probability weight:** 12%
**Domain:** debugging

---

**Skill selection log:**
- Task token: probe (investigation)
- Completeness: full (thorough diagnosis)
- Scope: considered fail, time, cross → chose: cross
  - Why cross? The new description: "concerns or forces that propagate across otherwise distinct units" fits well. Latency bottlenecks often involve cross-cutting concerns: logging overhead, auth checks, tracing, caching layers. The skill correctly identified this as likely a boundary-spanning issue.
- Method: diagnose (systematic cause-finding)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build probe full cross plain diagnose peer_engineer_explanation
```

---

**Coverage scores:**
- Token fitness: 5 — `cross` captures boundary-spanning nature of perf issues
- Token completeness: 5 — diagnose method + cross scope good for debugging
- Skill correctness: 5 — skill made appropriate selection
- Prompt clarity: 5 — clear debugging focus
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
New `cross` description worked well here. Performance issues often involve cross-cutting concerns (logging, auth, tracing) that "propagate across distinct units." The skill correctly avoided `fail` (which would focus on error conditions) and `time` (sequence) in favor of `cross` (distributed concern).

---

*Loop-5 realistic task evaluation*
