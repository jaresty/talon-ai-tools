## Task: T66 — Plan feature rollout (HIGH-FREQUENCY: 6%)

**Weight:** 6% — Planning + risk  
**Task Description:** "Plan the gradual rollout of v2"  
**Expected Challenge:** Planning + risk + coordination

---

### Skill Selection Log

**Task Analysis:**
- Planning task (make plan)
- Gradual rollout = phases + risk
- Coordination likely needed

**Token Selection:**
- **Task:** `make` (create rollout plan)
- **Completeness:** `full` (comprehensive plan)
- **Scope:** `time` (phased rollout) + `act` (actions per phase) + `fail` (risk mitigation)
- **Method:** `steps` (rollout phases) + `risks` (per R-04)
- **Form:** `checklist` (phase checklist)
- **Channel:** `plain` (prose)
- **Persona:** Considered `to-engineering-lead` → chose none

**Bar command constructed:**
```bash
bar build make full time act fail steps risks checklist plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `time+act+fail+steps+risks` perfect for rollout |
| Token completeness | 5 | Phases, actions, risks all covered |
| Skill correctness | 5 | Correctly applied R-04 Risk pattern |
| Prompt clarity | 5 | Clear rollout planning |
| **Overall** | **5** | **Excellent — planning + risk combined.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Feature rollout (6% weight) — combines planning (`make+steps`) with risk (`fail+risks`) per Loop 2 R-04. Complex real-world scenario handled well.

