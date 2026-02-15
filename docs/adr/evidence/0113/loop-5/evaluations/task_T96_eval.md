## Task: T96 — Surface implicit assumptions in reasoning

**Task description:** "What must be true for this rollback plan to work?"
**Probability weight:** 6%
**Domain:** analysis
**Primary scope test:** assume (premises that must hold)

---

**Skill selection log:**
- Task token: probe (surface hidden factors)
- Completeness: full
- Scope: considered mean, assume → chose: assume
  - Reason: Task asks what "must be true" — explicit/implicit premises. New `assume` description: "explicit or implicit premises that must hold for the reasoning, system, or argument to function" matches exactly. Not asking for conceptual understanding (mean), but for required conditions.
- Method: inversion (work backward from failure)
- Form: checklist
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build probe full assume plain checklist peer_engineer_explanation
```

**Bar output preview:**
> The response surfaces hidden assumptions, implications, dependencies, risks, or unstated context about the subject.
> [full, assume scope, plain channel, checklist form, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 5 — `assume` precisely addresses premise identification
- Token completeness: 5 — checklist form appropriate for assumptions
- Skill correctness: 5 — correctly chose assume (premises) over mean (framing)
- Prompt clarity: 5 — clear premise-surfacing focus
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
New `assume` description is clearer: "explicit or implicit premises that must hold for the reasoning, system, or argument to function." Previous was "premises that must already hold for the reasoning or system to function" — similar but new phrasing is crisper.

---

*Loop-5 scope prompt validation task*
