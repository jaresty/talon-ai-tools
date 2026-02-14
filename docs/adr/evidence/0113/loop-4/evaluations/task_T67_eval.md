## Task: T67 — Analyze error patterns (HIGH-FREQUENCY: 6%)

**Weight:** 6% — Analysis domain  
**Task Description:** "Why do we keep seeing these timeouts?"  
**Expected Challenge:** Pattern analysis + root cause

---

### Skill Selection Log

**Task Analysis:**
- Pattern analysis (probe)
- Recurring issue (why keep seeing)
- Root cause investigation

**Token Selection:**
- **Task:** `probe` (analyze patterns)
- **Completeness:** `full` (thorough analysis)
- **Scope:** `fail` (timeouts as failures) + `time` (when they occur) + `origin` (root cause)
- **Method:** `diagnose` (root cause) + `induce` (pattern from examples)
- **Form:** (none)
- **Channel:** `plain` (prose)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build probe full fail time origin diagnose induce plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `fail+time+origin+diagnose+induce` excellent |
| Token completeness | 5 | Pattern analysis + root cause |
| Skill correctness | 5 | Correctly combined analysis methods |
| Prompt clarity | 5 | Clear pattern investigation |
| **Overall** | **5** | **Excellent — analysis domain covered.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** Error pattern analysis (6% weight) — `induce` method (pattern generalization) + `diagnose` (root cause) + temporal scopes = comprehensive analysis coverage.

