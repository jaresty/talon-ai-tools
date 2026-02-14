## Task: T43 — Select tech stack for new project (NEW — Test `compare` with constraints)

**Domain:** Planning  
**Focus:** Test `compare` in constrained decision context  
**Task Description:** "We need to choose a database: Postgres, MongoDB, or DynamoDB. Consider team expertise, cost, and scalability."

---

### Skill Selection Log

**Task Analysis:**
- Constrained comparison (explicit criteria mentioned)
- Infrastructure decision
- Team/cost factors suggest persona or directional

**Token Selection:**
- **Task:** `probe` (evaluate options)
- **Completeness:** `full` (thorough evaluation)
- **Scope:** `good` (quality criteria: expertise, cost, scalability)
- **Method:** `compare` (compare options)
- **Form:** `checklist` (criteria-based evaluation)
- **Channel:** `plain` (prose)
- **Persona:** `to-engineering-lead` (decision audience)

**Bar command constructed:**
```bash
bar build probe full good compare checklist plain to-engineering-lead
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `compare+checklist` excellent for criteria-based selection |
| Token completeness | 5 | Audience persona adds decision context |
| Skill correctness | 5 | Correctly applied compare to constrained decision |
| Prompt clarity | 5 | Clear evaluation framework |
| **Overall** | **5** | **Excellent.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** `compare` works well with explicit constraints/criteria. Could potentially use `robust` method for uncertainty, but `compare` is more direct for this use case.

