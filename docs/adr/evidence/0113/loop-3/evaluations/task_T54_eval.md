## Task: T54 — Create runbook for on-call scenarios (NEW — Specialized: Operations)

**Domain:** Operations  
**Focus:** Incident response procedures  
**Task Description:** "Write a runbook for handling database outages during on-call"

---

### Skill Selection Log

**Task Analysis:**
- Documentation task (make)
- Runbook = step-by-step procedures
- Incident response context

**Token Selection:**
- **Task:** `make` (create runbook)
- **Completeness:** `full` (comprehensive procedures)
- **Scope:** `fail` (outages) + `act` (response actions)
- **Method:** `steps` (procedural)
- **Form:** `walkthrough` (step-by-step guide) + `checklist` (verification)
- **Channel:** `plain` (document)
- **Persona:** `to-on-call-engineer` (operations audience)

**Bar command constructed:**
```bash
bar build make full fail act steps walkthrough plain to-on-call-engineer
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `fail+act+steps+walkthrough` perfect for runbook |
| Token completeness | 5 | All dimensions covered |
| Skill correctness | 5 | Correctly combined operational tokens |
| Prompt clarity | 5 | Clear incident response guide |
| **Overall** | **5** | **Excellent — operations domain well-covered.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Good example of how `steps` method + `walkthrough` form create effective operational documentation. `fail+act` scope combination addresses incident context.

