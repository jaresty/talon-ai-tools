## Task: T99 — Distinguish meaning from premises

**Task description:** "What's the difference between understanding X and assuming X?"
**Probability weight:** 5%
**Domain:** analysis
**Primary scope test:** mean vs assume discrimination (explicit)

---

**Skill selection log:**
- Task token: show (explanation)
- Completeness: full
- Scope: considered mean, assume → chose: mean
  - Reason: Task is meta-cognitive — asking to distinguish conceptual understanding from premises. New `mean` description: "how something is conceptually framed or understood prior to evaluation" fits because this is about distinguishing conceptual operations. However, the task is explicitly ABOUT assumptions vs meaning, so this is an edge case.
  - **Alternative interpretation:** Could also use no scope and let the task description carry the full weight, or use `compare` method.
- Method: compare (distinguishing concepts)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build show full mean plain compare peer_engineer_explanation
```

**Bar output preview:**
> The response explains or describes the subject for the stated audience.
> [full, mean scope, plain channel, compare method, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 4 — `mean` is reasonable but the task is about both mean AND assume; selecting one is incomplete
- Token completeness: 3 — selecting only one scope when the task is explicitly about the distinction is limiting
- Skill correctness: 4 — skill made a reasonable choice but didn't surface that this task spans both scopes
- Prompt clarity: 4 — prompt will work but doesn't fully capture the meta-distinction
- **Overall: 4**

**Gap diagnosis:** undiscoverable-token

```yaml
gap_type: undiscoverable-token
task: T99 — Distinguish meaning from premises
dimension: scope
observation: >
  The task explicitly asks to distinguish between conceptual understanding (mean)
  and premises (assume). Selecting either scope token alone is incomplete because
  the task is ABOUT the relationship/distinction between these two scopes.
  The skill selected `mean` with `compare` method, which is reasonable but
  doesn't fully capture that the comparison is between two scope lenses.
  Consider whether scope tokens should be combinable for meta-analytical tasks,
  or if the skill should recognize when the task IS about scope distinctions.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    For meta-analytical tasks that ask to distinguish between scope concepts
    (e.g., "difference between understanding and assuming", "structure vs pattern"):
    consider using `compare` method with no scope token, allowing the task
    description to define the comparison without committing to one scope.
    Alternatively, analyze through each scope sequentially.
evidence: [task_T99]
```

**Notes:**
Similar to T97, this task is about comparing/discriminating scope concepts rather than applying one scope. The new scope descriptions are clear individually, but meta-analytical tasks about scope distinctions may need special handling.

---

*Loop-5 scope prompt validation task*
