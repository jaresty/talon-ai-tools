## Task: T85 — Handle customer escalation (RARE: 1%)

**Weight:** 1% — Support domain (edge case)  
**Task Description:** "The client is upset about downtime"  
**Expected Challenge:** Support context + communication

---

### Skill Selection Log

**Task Analysis:**
- Support/escalation task
- Customer communication
- Issue resolution

**Token Selection:**
- **Task:** `show` (explain resolution)
- **Completeness:** `gist` (concise for upset customer)
- **Scope:** `origin` (what happened) + `fail` (what went wrong) + `act` (what we did)
- **Method:** `diagnose` (explain cause)
- **Form:** (none — direct communication)
- **Channel:** `plain` (prose)
- **Persona:** `to-customer` (external audience)

**Bar command constructed:**
```bash
bar build show gist origin fail act diagnose plain to-customer
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 4 | Works for escalation; support domain niche |
| Token completeness | 4 | Good coverage; could use empathy focus |
| Skill correctness | 4 | Correctly routed to show |
| Prompt clarity | 4 | Clear explanation framework |
| **Overall** | **4** | **Good — rare support task acceptable.** |

---

### Gap Diagnosis

**Gap type:** minor observation  
**Observation:** Customer escalation (1% weight — very rare). Current approach works but support domain not a primary focus of bar. Score 4/5 acceptable for edge case.

**Note:** Bar focuses on software engineering tasks; support escalation is at the boundary. Current coverage is reasonable.

