## Task: T49 — Onboarding guide with hands-on exercises (NEW — Cross-domain: Team + Learning)

**Domains:** Team, Learning  
**Focus:** Test pedagogical tasks with practical components  
**Task Description:** "Create an onboarding guide for new engineers that includes hands-on exercises"

---

### Skill Selection Log

**Task Analysis:**
- Learning material (scaffold appropriate)
- Hands-on exercises (act scope)
- Guide creation (make)

**Token Selection:**
- **Task:** `make` (create guide)
- **Completeness:** `full` (comprehensive)
- **Scope:** `act` (hands-on exercises) + `mean` (concepts)
- **Method:** Considered `scaffold` (learning) → but task is make + exercises
  - **Chose no method** — scaffold not needed when act scope present
- **Form:** `scaffold` (pedagogical structure) + `checklist` (exercise list)
- **Channel:** `plain` (document)
- **Persona:** (none — new hire implied)

**Bar command constructed:**
```bash
bar build make full act mean scaffold checklist plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 4 | Good but complex (scaffold + checklist) |
| Token completeness | 4 | Covers learning + practical; could use walkthrough |
| Skill correctness | 4 | Scaffold used appropriately for learning |
| Prompt clarity | 4 | Clear but slightly complex combination |
| **Overall** | **4** | **Good — minor complexity with form selection.** |

---

### Gap Diagnosis

**Gap type:** minor complexity  
**Observation:** Task combines pedagogical (scaffold) with practical (act) elements. Current selection works but `walkthrough` method might better guide hands-on exercises.

**Alternative:** `bar build make full act mean walkthrough plain`

