## Task: T41 — Choose between microservices vs monolith (NEW — Test `compare` token)

**Domain:** Architecture  
**Focus:** Test new `compare` method token  
**Task Description:** "Should we use microservices or a monolith for our new platform?"

---

### Skill Selection Log (Run 1)

**Task Analysis:**
- Classic comparison/decision task
- Two clear alternatives presented
- Need to evaluate against criteria
- `compare` token should surface here

**Token Selection:**
- **Task:** `probe` (analysis to inform decision)
- **Completeness:** `full` (thorough comparison)
- **Scope:** `struct` (architectural structure) + `good` (quality criteria)
- **Method:** Considered `adversarial` (stress-test), `tradeoffs` (not a token), `compare` → **chose `compare`**
  - *Skill correctly surfaced the new `compare` token!*
- **Form:** `checklist` (decision criteria)
- **Channel:** `plain` (prose comparison)
- **Persona:** (none — technical audience implied)

**Bar command constructed:**
```bash
bar build probe full struct good compare checklist plain
```

**Bar output preview:**
```
The response diagnoses or analyzes the subject to surface assumptions.
[full completeness, struct scope (arrangements), good scope (quality), compare method, checklist form, plain channel]
```

---

### Skill Selection Log (Run 2 — Variance Check)

**Token Selection:**
- **Task:** `probe` (same)
- **Completeness:** `full` (same)
- **Scope:** `struct` + `good` (same)
- **Method:** `compare` (same — consistent!)
- **Form:** `checklist` (same)
- **Channel:** `plain`
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build probe full struct good compare checklist plain
```

**Variance:** None — skill consistently selects `compare` for comparison tasks. ✅

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `compare` precisely matches "evaluate alternatives" task |
| Token completeness | 5 | All dimensions captured; checklist adds structure |
| Skill correctness | 5 | Correctly surfaced new `compare` token |
| Prompt clarity | 5 | Clear architectural comparison instruction |
| **Overall** | **5** | **Excellent — `compare` token working perfectly.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** The `compare` token addition successfully handles comparison/decision tasks. Skill surfaces it naturally when alternatives are presented. This replaces the verbose workaround from T37 in Loop 2 (`probe+delta+good+adversarial`) with a cleaner, more precise command.

**Comparison to Loop 2 T37:**
- Loop 2 (without compare): `probe full delta good adversarial checklist` — works but verbose
- Loop 3 (with compare): `probe full struct good compare checklist` — precise and clean

