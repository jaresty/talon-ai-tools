## Task: T51 — Document API deprecation strategy (NEW — Specialized: Documentation)

**Domain:** Documentation  
**Focus:** Deprecation-specific task  
**Task Description:** "Create a deprecation strategy for our v1 API"

---

### Skill Selection Log

**Task Analysis:**
- Documentation task (make)
- Deprecation = migration + communication + timeline
- Need to cover migration path, timeline, communication

**Token Selection:**
- **Task:** `make` (create strategy doc)
- **Completeness:** `full` (comprehensive deprecation plan)
- **Scope:** `delta` (changes) + `time` (timeline) + `act` (migration actions)
- **Method:** `steps` (process) + `communicate` (not a token)
  - Chose `steps` only
- **Form:** `checklist` (deprecation checklist)
- **Channel:** `plain` (document)
- **Persona:** `to-engineering-lead` (affected teams)

**Bar command constructed:**
```bash
bar build make full delta time act steps checklist plain to-engineering-lead
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 4 | `delta+time+act+steps` captures deprecation well |
| Token completeness | 4 | Missing explicit "deprecation" or "migration" scope |
| Skill correctness | 4 | Routed correctly to make |
| Prompt clarity | 4 | Clear but could be sharper with dedicated token |
| **Overall** | **4** | **Good — works but verbose.** |

---

### Gap Diagnosis

**Gap type:** minor observation  
**Observation:** Deprecation/migration tasks require multiple tokens (`delta+time+act`) to express the concept. No single token targets "migration" or "deprecation" explicitly. Current coverage works (score 4) but is verbose.

**Potential addition:** `migrate` scope or `deprecate` method for migration/deprecation tasks. Score 4 is acceptable; not urgent.

