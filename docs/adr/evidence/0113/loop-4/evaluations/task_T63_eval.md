## Task: T63 — Explain code to new teammate (HIGH-FREQUENCY: 8%)

**Weight:** 8% — Common onboarding scenario  
**Task Description:** "Walk me through this module"  
**Expected Challenge:** Pedagogical + scope selection

---

### Skill Selection Log

**Task Analysis:**
- Explanation task (show)
- New teammate = pedagogical audience
- Module walkthrough

**Token Selection:**
- **Task:** `show` (explain code)
- **Completeness:** `full` (thorough explanation)
- **Scope:** `struct` (code structure) + `flow` (execution flow) + `mean` (purpose)
- **Method:** `walkthrough` (guided tour)
- **Form:** `scaffold` (building understanding)
- **Channel:** `plain` (prose)
- **Persona:** `to-junior-engineer` (learning audience)

**Bar command constructed:**
```bash
bar build show full struct flow mean walkthrough scaffold plain to-junior-engineer
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `struct+flow+mean+walkthrough+scaffold` perfect |
| Token completeness | 5 | Structure + execution + purpose + pedagogy |
| Skill correctness | 5 | Correctly applied pedagogical tokens |
| Prompt clarity | 5 | Clear learning framework |
| **Overall** | **5** | **Excellent — onboarding scenario covered.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Code explanation (8% weight) — a core use case — excellently covered. Multiple scopes (`struct+flow+mean`) + `walkthrough` method + `scaffold` form + junior persona = comprehensive pedagogical coverage.

