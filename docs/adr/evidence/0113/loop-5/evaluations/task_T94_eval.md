## Task: T94 — Analyze system stability under load

**Task description:** "Will this configuration remain stable during traffic spikes?"
**Probability weight:** 7%
**Domain:** analysis
**Primary scope test:** stable (equilibrium/persistence)

---

**Skill selection log:**
- Task token: probe (surface implications)
- Completeness: full
- Scope: considered fail, stable → chose: stable
  - Reason: Task asks about stability under perturbation (traffic spikes). New `stable` description: "equilibrium, persistence, and self-reinforcing states...analyzing how perturbations affect their continuity" matches perfectly. `fail` would focus on breakdowns; `stable` focuses on persistence.
- Method: adversarial (stress-test the configuration)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build probe full stable plain peer_engineer_explanation
```

**Bar output preview:**
> The response surfaces hidden assumptions, implications, dependencies, risks, or unstated context about the subject.
> [full, stable scope, plain channel, peer_engineer_explanation]

---

**Coverage scores:**
- Token fitness: 5 — `stable` precisely addresses equilibrium/persistence question
- Token completeness: 5 — all dimensions appropriate
- Skill correctness: 5 — correctly chose stable (persistence) over fail (breakdown)
- Prompt clarity: 5 — clear stability analysis focus
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
New `stable` description is cleaner: "equilibrium, persistence, and self-reinforcing states...analyzing how perturbations affect their continuity." Previous description was more verbose but similar meaning. Good clarity improvement.

---

*Loop-5 scope prompt validation task*
