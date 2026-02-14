## Task: T62 — Review pull request (HIGH-FREQUENCY: 10%)

**Weight:** 10% — Second most common  
**Task Description:** "Review this PR for the auth service"  
**Expected Challenge:** Evaluation + feedback + quality check

---

### Skill Selection Log

**Task Analysis:**
- Code review task
- Evaluation (check) vs explanation (show)
- Quality assessment

**Token Selection:**
- **Task:** `check` (evaluate code)
- **Completeness:** `full` (thorough review)
- **Scope:** `good` (quality criteria) + `fail` (issues to fix)
- **Method:** `rigor` (code quality focus)
- **Form:** `checklist` (review items)
- **Channel:** `plain` (prose)
- **Persona:** Considered `to-author` → chose none (peer review)

**Bar command constructed:**
```bash
bar build check full good fail rigor checklist plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `check+good+fail+rigor` excellent for code review |
| Token completeness | 5 | Quality + issues covered |
| Skill correctness | 5 | Correctly chose check (evaluate) over show |
| Prompt clarity | 5 | Clear review framework |
| **Overall** | **5** | **Excellent — second highest-frequency covered.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Code review (10% weight) well-covered. `check` task differentiates from `show` (explanation). `rigor` method adds code quality focus.

**Note on persona:** Could use `to-author` persona but peer review context works without it.

