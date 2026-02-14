## Task: T08 — Risk assessment / risk extraction (RE-TEST)

**Loop 1 Score:** 3  
**Loop 1 Gap:** skill-guidance-wrong — used `probe` instead of `pull` for extraction  
**Fix Applied:** R-04 — Split Risk Assessment into Risk Extraction (`pull`) and Risk Analysis (`probe`)  
**Task Description:** "What are the risks of deploying the payment service on Friday?"

---

### Skill Selection Log (Run 1)

**Task Analysis:**
- User wants a risk *list/extraction* — "what are the risks?"
- This is targeted subset extraction, not open-ended analysis
- Per R-04 heuristic: "what are the risks?" → pull (extraction)

**Token Selection:**
- **Task:** `pull` (extraction task) — *correctly chose extraction over analysis!*
- **Completeness:** `full` (comprehensive risk list)
- **Scope:** `fail` (focus on failure modes/risks)
- **Method:** Considered `adversarial` (attack surface), `inversion` (backward reasoning) → chose `risks` (direct risk enumeration)
- **Form:** `checklist` (produce a structured risk list)
- **Channel:** `plain` (prose checklist)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build pull full fail risks checklist plain
```

**Bar output preview:**
```
The response extracts a specific subset or view of the subject.
[full completeness, fail scope (failure/risk focus), risks method, checklist form, plain channel]
```

---

### Skill Selection Log (Run 2 — Variance Check)

**Token Selection:**
- **Task:** `pull` (same — consistent extraction routing)
- **Completeness:** `full` (same)
- **Scope:** `fail` (same)
- **Method:** `risks` (same)
- **Form:** `checklist` (same)
- **Channel:** `plain`
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build pull full fail risks checklist plain
```

**Variance:** None — skill consistently applies R-04 Risk Extraction pattern. ✅

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `pull+fail+risks+checklist` precisely matches risk extraction |
| Token completeness | 5 | All dimensions captured; form adds useful structure |
| Skill correctness | 5 | Correctly applied R-04 pattern: extraction vs analysis distinction |
| Prompt clarity | 5 | Output clearly describes risk list extraction |
| **Overall** | **5** | **Fixed! Loop 1 gap resolved.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** R-04 fix successfully resolves the risk extraction gap. Skill now correctly distinguishes:
- Risk extraction: "what are the risks?" → `pull+fail+risks`
- Risk analysis: "how risky is this?" → `probe+fail+adversarial`

