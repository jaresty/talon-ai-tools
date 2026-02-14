## Task: T61 — Debug production issue (HIGH-FREQUENCY: 10%)

**Weight:** 10% — Most common task type  
**Task Description:** "The API is returning 500s, investigate"  
**Expected Challenge:** Time pressure + diagnosis + cross-system possibly

---

### Skill Selection Log

**Task Analysis:**
- Critical production issue
- Error investigation (500s)
- Time-sensitive
- May span multiple services

**Token Selection:**
- **Task:** `probe` (diagnose issue)
- **Completeness:** `full` (thorough investigation)
- **Scope:** `fail` (500 errors) + `time` (when it started) + `cross` (if distributed)
- **Method:** `diagnose` (root cause analysis) + `origin` (when did it start)
- **Form:** (none — urgent, direct)
- **Channel:** `plain` (prose)
- **Persona:** (none — ops context)

**Bar command constructed:**
```bash
bar build probe full fail time cross diagnose origin plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `fail+time+cross+diagnose+origin` perfect for prod debug |
| Token completeness | 5 | Errors, timeline, root cause all covered |
| Skill correctness | 5 | Correctly combined diagnostic scopes |
| Prompt clarity | 5 | Clear investigation framework |
| **Overall** | **5** | **Excellent — highest-frequency task covered.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Production debugging — the most common task (10% weight) — is well-covered by combining `probe` + `fail` + `diagnose` + temporal scopes. The `cross` scope handles distributed systems context.

**Bar variants output relevance:** This validates that bar can handle the most frequent user request.

