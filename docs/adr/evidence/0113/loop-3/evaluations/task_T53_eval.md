## Task: T53 — Analyze data pipeline bottlenecks (NEW — Specialized: Data Engineering)

**Domain:** Data Engineering  
**Focus:** Data flow analysis  
**Task Description:** "Find bottlenecks in our data pipeline from ingestion to warehouse"

---

### Skill Selection Log

**Task Analysis:**
- Diagnostic task (probe)
- Pipeline = flow + time
- Bottlenecks = performance limits

**Token Selection:**
- **Task:** `probe` (diagnose bottlenecks)
- **Completeness:** `full` (thorough analysis)
- **Scope:** `flow` (data movement) + `time` (latency) + `fail` (bottlenecks as failures)
- **Method:** `diagnose` (root cause) + `flow` method (not a token)
  - Chose `diagnose` only
- **Form:** (none)
- **Channel:** `plain` (prose)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build probe full flow time fail diagnose plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `flow+time+fail+diagnose` captures pipeline analysis |
| Token completeness | 4 | Good coverage; flow scope works but flow method would be nice |
| Skill correctness | 4 | Correctly routed to probe |
| Prompt clarity | 4 | Clear but could use walkthrough form |
| **Overall** | **4** | **Good — specialized domain handled.** |

---

### Gap Diagnosis

**Gap type:** minor observation  
**Observation:** `flow` scope works for data pipeline context. A `flow` method (similar to `walkthrough` but for data/process flow) could enhance but not essential. Score 4 is good coverage.

**Alternative:** `bar build probe full flow time fail diagnose walkthrough plain`

