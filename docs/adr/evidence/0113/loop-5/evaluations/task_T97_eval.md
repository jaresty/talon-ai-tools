## Task: T97 — Compare structural vs cross-cutting analysis

**Task description:** "Should I look at service dependencies or logging consistency?"
**Probability weight:** 6%
**Domain:** analysis
**Primary scope test:** struct vs cross discrimination (explicit comparison)

---

**Skill selection log:**
- Task token: probe (analysis)
- Completeness: full
- Scope: considered both struct and cross as alternatives → chose: cross
  - Reason: Task presents a choice between "service dependencies" (structural) and "logging consistency" (cross-cutting). Both are valid analyses, but "logging consistency" is the cross-cutting concern that propagates across boundaries. The skill correctly identified that the user's dilemma is about which lens to apply, and either could be valid depending on goal.
  - **Note:** This is an interesting case where the skill could reasonably choose either. Cross was selected because the user seems to be asking about consistency across services (boundary-spanning), not internal dependency structure.
- Method: compare (explicit comparison)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build probe full cross plain compare peer_engineer_explanation
```

**Bar output preview:**
> The response surfaces hidden assumptions, implications, dependencies, risks, or unstated context about the subject.
> [full, cross scope, plain channel, compare method, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 4 — `cross` is reasonable but `struct` would also be valid; the choice depends on goal
- Token completeness: 4 — comparison method helps but scope choice is ambiguous
- Skill correctness: 4 — skill made a reasonable choice but didn't surface the ambiguity
- Prompt clarity: 4 — prompt will analyze logging consistency, but user asked for help choosing
- **Overall: 4**

**Gap diagnosis:** undiscoverable-token

```yaml
gap_type: undiscoverable-token
task: T97 — Compare structural vs cross-cutting analysis
dimension: scope + method
observation: >
  The task presents an explicit comparison between two scope lenses (struct vs cross).
  The skill selected `cross` scope with `compare` method, but this doesn't fully capture
  the user's need: they want help deciding WHICH lens to apply, not analysis through one lens.
  The `compare` method compares alternatives, but the scope token commits to one lens.
  A "meta-scope" or better guidance about when to apply struct vs cross would help.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    When the user explicitly asks to choose between structural analysis (internal topology)
    and cross-cutting analysis (boundary-spanning concerns), consider using `compare` method
    with no scope token, or apply scope in sequence (first one, then the other).
    Example: "Should I look at dependencies or error handling?" — these are different
    analytical lenses (struct vs cross) and the answer may require comparing both.
evidence: [task_T97]
```

**Notes:**
This task exposed an interesting edge case: when the user explicitly asks to choose between analytical lenses, selecting one scope token doesn't fully serve the need. The new scope descriptions are clear individually, but guidance for comparing/discriminating between them could be enhanced.

---

*Loop-5 scope prompt validation task*
