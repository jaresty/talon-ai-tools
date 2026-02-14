## Task: T38 — Draft incident communication (NEW — Domain: Communication)

**Task Description:** "Write a status page update for the payment outage"

---

### Skill Selection Log

**Task Analysis:**
- Crisis communication
- External audience (customers)
- make (produce update)

**Token Selection:**
- **Task:** `make` (create communication)
- **Completeness:** `gist` (brief status update — not full)
- **Scope:** `fail` (what failed) + `time` (timeline) + `origin` (root cause if known)
- **Method:** (none)
- **Form:** (none)
- **Channel:** `plain` (status page prose)
- **Persona:** `to-customers` (external audience)
  - *Appropriate audience for status page*

**Bar command constructed:**
```bash
bar build make gist fail time origin plain to-customers
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `gist+fail+time+origin` captures incident update elements |
| Token completeness | 5 | What, when, why all covered; audience appropriate |
| Skill correctness | 5 | Correctly routed to make with crisis scopes |
| Prompt clarity | 5 | Clear incident communication |
| **Overall** | **5** | **Excellent.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Good coverage for incident communication. `to-customers` persona (if exists) or similar external audience token works well.

