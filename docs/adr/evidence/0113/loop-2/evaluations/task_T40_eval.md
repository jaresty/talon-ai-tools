## Task: T40 — Review accessibility compliance (NEW — Domain: Compliance)

**Task Description:** "Check if our web app meets WCAG 2.1 AA standards"

---

### Skill Selection Log

**Task Analysis:**
- Compliance evaluation task
- check (evaluate against criteria), not make or probe
- WCAG = specific standard/criteria

**Token Selection:**
- **Task:** `check` (evaluate compliance)
- **Completeness:** `full` (thorough compliance check)
- **Scope:** `good` (standards/criteria) + `fail` (violations)
- **Method:** `checklist` (structured compliance verification)
- **Form:** `checklist` (form matches method — good)
- **Channel:** `plain` (report format)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build check full good fail checklist plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `check+good+fail+checklist` precise for compliance review |
| Token completeness | 5 | Standards + violations + structured format |
| Skill correctness | 5 | Correctly routed to check (evaluation) |
| Prompt clarity | 5 | Clear compliance verification |
| **Overall** | **5** | **Excellent.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Compliance review well-covered. `check` task with `good` (criteria) + `fail` (gaps) is effective pattern.

