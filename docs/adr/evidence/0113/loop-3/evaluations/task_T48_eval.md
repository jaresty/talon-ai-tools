## Task: T48 — Debug performance across services (NEW — Cross-domain: Debugging + System)

**Domains:** Debugging, System  
**Focus:** Test `cross` token with debugging context  
**Task Description:** "Our API is slow — trace the performance bottlenecks across all microservices"

---

### Skill Selection Log

**Task Analysis:**
- Debugging task (diagnose)
- Cross-service (cross-cutting concern)
- Performance focus (time + resource)

**Token Selection:**
- **Task:** `probe` (diagnostic)
- **Completeness:** `full` (thorough investigation)
- **Scope:** `cross` (spans services) + `time` (latency/timing) + `fail` (bottlenecks as failures)
- **Method:** `diagnose` (root cause analysis)
- **Form:** `walkthrough` (trace through system)
- **Channel:** `plain` (prose)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build probe full cross time fail diagnose walkthrough plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `cross+time+fail+diagnose` perfect for distributed debugging |
| Token completeness | 5 | Cross-service, timing, bottlenecks all covered |
| Skill correctness | 5 | Correctly surfaced cross for microservices context |
| Prompt clarity | 5 | Clear distributed debugging instruction |
| **Overall** | **5** | **Excellent — `cross` token working in new context.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** `cross` token from Loop 1 continues to work well — now in debugging context (T48) vs analysis (T07) or refactoring (T31). Token is versatile across domains.

