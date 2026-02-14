## Task: T39 — Plan capacity for growth (NEW — Domain: Planning)

**Task Description:** "Plan infrastructure capacity for 10x user growth next year"

---

### Skill Selection Log

**Task Analysis:**
- Planning task with forecasting
- make (create plan)
- Growth/scale focus

**Token Selection:**
- **Task:** `make` (create capacity plan)
- **Completeness:** `full` (comprehensive plan)
- **Scope:** `struct` (infrastructure structure) + `time` (forecasting) + `uncertainty` (growth uncertainty)
- **Method:** `steps` (planning process) + `tradeoffs` (if available) → chose `steps` + `inversion` (failure modes at scale)
- **Form:** (none)
- **Channel:** `plain` (document)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build make full struct time uncertainty steps inversion plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 4 | `inversion` (failure at scale) is creative but not obvious; `uncertainty` good for forecasting |
| Token completeness | 4 | Good coverage; could use dedicated forecasting/planning scope |
| Skill correctness | 4 | Routed correctly to make; method selection less precise |
| Prompt clarity | 4 | Clear but complex token combination |
| **Overall** | **4** | **Good — minor complexity in method selection.** |

---

### Gap Diagnosis

**Gap type:** minor complexity (not a true gap)
**Observation:** Capacity planning works but requires multiple scope tokens. This is acceptable complexity — the catalog handles it, even if not elegant.

