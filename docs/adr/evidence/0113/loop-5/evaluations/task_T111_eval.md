## Task: T111 — Plan a database migration

**Task description:** "How do we migrate from Postgres to DynamoDB?"
**Probability weight:** 10%
**Domain:** planning

---

**Skill selection log:**
- Task token: make (create plan)
- Completeness: full (comprehensive plan)
- Scope: considered time, act → chose: time
  - Why time? The new description: "when things occur and how they change over time or across stages" fits perfectly. Migration planning is about sequencing steps/phases over time. The phased nature of migration (before/during/after, cutover steps, rollback windows) is captured well by `time`.
- Method: converge (narrow to actionable plan)
- Form: scaffold (structured plan)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build make full time plain scaffold converge peer_engineer_explanation
```

---

**Coverage scores:**
- Token fitness: 5 — `time` captures phased migration sequencing
- Token completeness: 5 — all dimensions appropriate
- Skill correctness: 5 — excellent selection for phased migration plan
- Prompt clarity: 5 — clear phased plan focus
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
`time` is the right scope for migration planning. The description "how they change over time or across stages" matches migration tasks perfectly. The skill correctly identified this as a temporal sequencing task, not just action listing.

---

*Loop-5 realistic task evaluation*
