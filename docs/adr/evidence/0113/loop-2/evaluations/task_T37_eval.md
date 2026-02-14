## Task: T37 — Compare two technical approaches (NEW — Domain: Analysis)

**Task Description:** "Should we use Kafka or RabbitMQ for our event streaming?"

---

### Skill Selection Log

**Task Analysis:**
- Decision support task
- Comparing two alternatives
- probe (analysis) vs show (explanation) — this is evaluative

**Token Selection:**
- **Task:** `probe` (analyze tradeoffs)
- **Completeness:** `full` (comprehensive comparison)
- **Scope:** `delta` (differences between options) + `good` (evaluation criteria)
- **Method:** `tradeoffs` (if available) → considered `adversarial` (stress-test each) → chose `adversarial` + `walkthrough` (explore each option)
- **Form:** `checklist` (decision criteria checklist)
- **Channel:** `plain` (prose comparison)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build probe full delta good adversarial checklist plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 4 | `adversarial` works but `tradeoffs` would be more precise; no tradeoffs token exists |
| Token completeness | 4 | Good coverage; missing explicit comparison structure |
| Skill correctness | 5 | Correctly routed to probe (analysis) |
| Prompt clarity | 4 | Clear but could be sharper with dedicated comparison tokens |
| **Overall** | **4** | **Good — minor gap: no dedicated comparison/decision token.** |

---

### Gap Diagnosis

**Gap type:** missing-token (minor)
**Observation:** No token specifically targets "compare alternatives" or "decision support" tasks. Current workaround (`probe+delta+good+adversarial`) works but is verbose.

**Potential addition:** A `compare` method or `versus` scope for alternative comparison tasks. However, current coverage is acceptable (score 4) — not urgent.

**Evidence:** T37 (this task)

