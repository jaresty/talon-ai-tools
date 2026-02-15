## Task: T92 — Understand conceptual framing before evaluation

**Task description:** "What does 'eventual consistency' actually mean in this context?"
**Probability weight:** 8%
**Domain:** analysis
**Primary scope test:** mean (conceptual framing)

---

**Skill selection log:**
- Task token: show (explanation)
- Completeness: full
- Scope: considered mean, assume → chose: mean
  - Reason: Task asks for conceptual understanding — "how something is conceptually framed or understood prior to evaluation" — exactly the new `mean` description. Not asking what must be true (assume), but what the concept means.
- Method: (none)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build show full mean plain peer_engineer_explanation
```

**Bar output preview:**
> The response explains or describes the subject for the stated audience.
> [full, mean scope, plain channel, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 5 — `mean` precisely addresses conceptual framing question
- Token completeness: 5 — no missing dimensions for definition task
- Skill correctness: 5 — correctly chose mean (conceptual) over assume (premises)
- Prompt clarity: 5 — clear focus on conceptual understanding
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
New `mean` description clarifies: "how something is conceptually framed or understood prior to evaluation or action...without asserting required premises." This makes the mean/assume distinction crisp. Previously these might have been conflated.

---

*Loop-5 scope prompt validation task*
