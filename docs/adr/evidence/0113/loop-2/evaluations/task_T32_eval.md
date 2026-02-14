## Task: T32 — Security risk extraction (NEW — Edge Case)

**Domain:** Security  
**Rationale:** Test R-04 Risk Extraction pattern in security context  
**Task Description:** "List all security risks in the authentication flow"

---

### Skill Selection Log (Run 1)

**Task Analysis:**
- "List" = extraction (pull), not analysis (probe)
- Security context, but extraction pattern same as T08
- Per R-04: "what are the risks?" → pull

**Token Selection:**
- **Task:** `pull` (extraction — "list risks")
  - *Correctly applied R-04 pattern!*
- **Completeness:** `full` (comprehensive list)
- **Scope:** `fail` (risks/vulnerabilities)
- **Method:** `risks` (risk enumeration) + `adversarial` (attack surface)
- **Form:** `checklist` (structured risk list)
- **Channel:** `plain` (prose)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build pull full fail risks adversarial checklist plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `pull+fail+risks+adversarial` precise for security risk extraction |
| Token completeness | 5 | Comprehensive coverage |
| Skill correctness | 5 | R-04 pattern generalizes to security domain |
| Prompt clarity | 5 | Clear extraction instruction |
| **Overall** | **5** | **Excellent — pattern generalizes.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** R-04 Risk Extraction pattern successfully applies across domains:
- T08: General risk extraction (deployment)
- T32: Security risk extraction (auth flow)

Pattern is domain-agnostic and skill applies it correctly.

