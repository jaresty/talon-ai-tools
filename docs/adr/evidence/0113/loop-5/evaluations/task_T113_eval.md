## Task: T113 — Explain code to new team member

**Task description:** "Walk me through the auth flow"
**Probability weight:** 8%
**Domain:** explanation

---

**Skill selection log:**
- Task token: show (explanation)
- Completeness: full
- Scope: considered flow, struct, mean → chose: flow
  - Why flow? The task asks to "walk through" the auth flow—temporal sequence. New scope descriptions don't include `flow`, but `flow` is about process/procedure sequence. This is different from `time` (general temporal) or `struct` (arrangement).
  - **Alternative:** Could also use `mean` (conceptual understanding) for a newcomer.
- Method: (none)
- Form: scaffold (structured walkthrough)
- Channel: plain
- Persona: onboarding_new_hire

**Bar command constructed:**
```
bar build show full flow plain scaffold onboarding_new_hire
```

---

**Coverage scores:**
- Token fitness: 5 — `flow` captures process sequence well
- Token completeness: 5 — appropriate for walkthrough task
- Skill correctness: 5 — good selection for sequential explanation
- Prompt clarity: 5 — clear process walkthrough
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
Good selection. `flow` isn't one of the scopes with updated descriptions, but it's working well for process explanation. The skill correctly avoided `struct` (static arrangement) in favor of `flow` (dynamic sequence). New descriptions for other scopes didn't cause confusion here.

---

*Loop-5 realistic task evaluation*
