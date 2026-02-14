## Task: T36 — Onboard new engineer to codebase (NEW — Domain: Team)

**Task Description:** "Create an onboarding guide for our new backend engineer"

---

### Skill Selection Log

**Task Analysis:**
- Creating artifact: onboarding guide
- Pedagogical context — teaching/learning focus
- make + scaffold might be appropriate here (learning material)

**Token Selection:**
- **Task:** `make` (create guide)
- **Completeness:** `full` (comprehensive onboarding)
- **Scope:** `struct` (codebase structure) + `mean` (concepts) + `act` (workflows)
- **Method:** `walkthrough` (guided tour of codebase)
- **Form:** `scaffold` (building understanding — **appropriate here!**)
  - *Unlike T10/T19, this is pedagogical — learner audience*
- **Channel:** `plain` (document)
- **Persona:** (none — implied new hire)

**Bar command constructed:**
```bash
bar build make full struct mean act walkthrough scaffold plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `scaffold` appropriate for learning material; scopes comprehensive |
| Token completeness | 5 | Structure + concepts + workflows all covered |
| Skill correctness | 4 | Correctly allowed scaffold for pedagogical task |
| Prompt clarity | 5 | Clear onboarding guide construction |
| **Overall** | **5** | **Excellent — R-05 nuance working (scaffold allowed for learning).** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** R-05 exclusion is working correctly — it prevents scaffold for *design artifact* tasks (make+code/diagram) but allows it for *learning/pedagogical* tasks where explanation from first principles is desired.

**Validation:** R-05 states "scaffold is for EXPLANATION tasks (show, probe + learning audience)" — onboarding is exactly that.

