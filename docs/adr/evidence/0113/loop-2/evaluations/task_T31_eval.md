## Task: T31 — Refactor with cross-cutting impact (NEW — Edge Case)

**Domain:** Code  
**Rationale:** Test `cross` token in practice (different from T07's analysis focus)  
**Task Description:** "Plan a refactor to centralize error handling across all microservices"

---

### Skill Selection Log (Run 1)

**Task Analysis:**
- Planning task with cross-service impact
- Error handling is a cross-cutting concern (spans all services)
- Task is `make` (create plan), not `show` or `probe`

**Token Selection:**
- **Task:** `make` (create refactor plan)
- **Completeness:** `full` (thorough plan)
- **Scope:** Considered `struct` (dependencies), `delta` (changes) → chose `cross` (error handling spans services) + `delta` (refactor changes)
  - *Skill correctly applied `cross` to cross-cutting concern!*
- **Method:** `steps` (refactor process)
- **Form:** (none — plan, not explanation)
- **Channel:** `plain` (document)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build make full cross delta steps plain
```

---

### Skill Selection Log (Run 2 — Variance Check)

**Token Selection:**
- **Task:** `make` (same)
- **Completeness:** `full` (same)
- **Scope:** `cross` + `delta` (same — good combination)
- **Method:** `steps` (same)
- **Form:** (none)
- **Channel:** `plain`
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build make full cross delta steps plain
```

**Variance:** None — consistent selection of `cross` for cross-cutting refactor. ✅

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `cross+delta` captures cross-service + change aspects |
| Token completeness | 5 | All dimensions covered; steps method appropriate |
| Skill correctness | 5 | Correctly surfaced `cross` in different context (make vs show) |
| Prompt clarity | 5 | Clear refactor plan with cross-cutting focus |
| **Overall** | **5** | **Excellent — `cross` token generalizes well.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** `cross` token successfully applies to both:
- T07: `show` (analysis of existing cross-cutting concerns)
- T31: `make` (planning refactor of cross-cutting concerns)

Token is versatile and skill surfaces it consistently.

