## Task: T46 — Plan migration with risk analysis (NEW — Cross-domain: Planning + Risk)

**Domains:** Planning, Risk  
**Focus:** Test complex multi-domain task  
**Task Description:** "Plan our database migration and identify all the things that could go wrong"

---

### Skill Selection Log

**Task Analysis:**
- Dual task: create plan AND identify risks
- Could be split or combined
- Migration = delta + time; risks = fail + risks

**Token Selection:**
- **Task:** `make` (create plan) — primary task
- **Completeness:** `full` (comprehensive)
- **Scope:** `delta` (migration changes) + `time` (timeline) + `fail` (risks)
- **Method:** `risks` (risk identification) + `steps` (planning process)
  - *Combined planning + risk analysis effectively*
- **Form:** `checklist` (structured plan with risks)
- **Channel:** `plain` (prose)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build make full delta time fail risks steps checklist plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `make+delta+time+fail+risks+steps` covers both domains |
| Token completeness | 5 | Plan creation + risk identification both represented |
| Skill correctness | 5 | Correctly combined planning and risk scopes/methods |
| Prompt clarity | 4 | Slightly verbose but clear (6 tokens) |
| **Overall** | **5** | **Excellent — complex cross-domain handled well.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Bar handles cross-domain tasks by allowing multiple scope and method tokens. The command is slightly long (6 tokens) but precisely captures both aspects of the request.

**Alternative split approach:**
- Plan: `bar build make full delta time steps checklist`
- Risks: `bar build pull full fail risks checklist`

But the combined approach works well for integrated deliverables.

