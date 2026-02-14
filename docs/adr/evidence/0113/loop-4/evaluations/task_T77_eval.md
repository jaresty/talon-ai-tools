## Task: T77 — Deprecate old API (LOWER-FREQUENCY: 3%)

**Weight:** 3% — Planning task  
**Task Description:** "Plan the sunset of v1 endpoints"  
**Expected Challenge:** Migration planning + communication

---

### Skill Selection Log

**Task Analysis:**
- Deprecation planning
- Migration coordination
- Timeline + communication

**Token Selection:**
- **Task:** `make` (create deprecation plan)
- **Completeness:** `full` (comprehensive plan)
- **Scope:** `delta` (changes) + `time` (timeline) + `act` (migration steps)
- **Method:** `steps` (phased approach)
- **Form:** `checklist` (deprecation checklist)
- **Channel:** `plain` (prose)
- **Persona:** `to-engineering-lead` (affected teams)

**Bar command constructed:**
```bash
bar build make full delta time act steps checklist plain to-engineering-lead
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 4 | `delta+time+act+steps` works but verbose |
| Token completeness | 4 | Good coverage; no dedicated migrate/deprecate token |
| Skill correctness | 4 | Correctly routed to make |
| Prompt clarity | 4 | Clear but could be sharper |
| **Overall** | **4** | **Good — works but multiple tokens needed.** |

---

### Gap Diagnosis

**Gap type:** minor observation (same as T51 in Loop 3)  
**Observation:** Deprecation/migration tasks require 3+ scope tokens (`delta+time+act`). No single `migrate` or `deprecate` token exists. Current score 4/5 is acceptable; not urgent.

**Workaround:** Current multi-token approach works fine.

