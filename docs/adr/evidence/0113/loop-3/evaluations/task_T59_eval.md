## Task: T59 — Write incident retrospective (NEW — Communication: Post-mortem)

**Domain:** Communication  
**Audience:** Post-mortem readers  
**Focus:** Learning from failure  
**Task Description:** "Create a retrospective for last week's outage"

---

### Skill Selection Log

**Task Analysis:**
- Post-mortem document
- Root cause + lessons learned
- Forward-looking

**Token Selection:**
- **Task:** `make` (create retrospective)
- **Completeness:** `full` (comprehensive analysis)
- **Scope:** `origin` (what happened) + `fail` (what went wrong)
- **Method:** `diagnose` (root cause) + `converge` (lessons/future)
- **Form:** `checklist` (action items)
- **Channel:** `plain` (prose)
- **Persona:** (none — team context implied)

**Bar command constructed:**
```bash
bar build make full origin fail diagnose converge checklist plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `origin+fail+diagnose+converge` perfect for retrospective |
| Token completeness | 5 | Past (origin) + present (fail) + future (converge) |
| Skill correctness | 5 | Correctly combined temporal scopes |
| Prompt clarity | 5 | Clear post-mortem structure |
| **Overall** | **5** | **Excellent — post-mortem well-covered.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Good example of temporal scope combination: `origin` (what happened), `fail` (failure analysis), `converge` (lessons learned). Comprehensive retrospective coverage.

