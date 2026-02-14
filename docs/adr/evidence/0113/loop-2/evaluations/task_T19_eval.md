## Task: T19 — Write system design document (RE-TEST)

**Loop 1 Score:** 3  
**Loop 1 Gap:** skill-guidance-wrong — `scaffold` used for `make` + design artifact  
**Fix Applied:** R-05 — Exclude `scaffold` when `make` produces design artifacts  
**Task Description:** "Write a system design document for the authentication service"

---

### Skill Selection Log (Run 1)

**Task Analysis:**
- User wants to *create* a design document (make)
- Design artifact: architecture/design specification
- Per R-05: omit form tokens for make+design tasks

**Token Selection:**
- **Task:** `make` (create document)
- **Completeness:** `full` (comprehensive design doc)
- **Scope:** `struct` (structural/architectural focus)
- **Method:** Considered `diagram` (visual), `adr` (decision record style) → chose none (plain design doc)
- **Form:** Considered `scaffold` → **rejected per R-05** — design artifact, not explanation
  - *Skill correctly excluded scaffold!*
- **Channel:** `plain` (document format)
- **Persona:** Considered `to-product-manager`, `to-engineering-lead` → chose `to-engineering-lead` (technical design review audience)

**Bar command constructed:**
```bash
bar build make full struct plain to-engineering-lead
```

**Bar output preview:**
```
The response produces or generates the subject as output.
[full completeness, struct scope, plain channel, to-engineering-lead audience]
```

---

### Skill Selection Log (Run 2 — Variance Check)

**Token Selection:**
- **Task:** `make` (same)
- **Completeness:** `full` (same)
- **Scope:** `struct` (same)
- **Method:** (none — same)
- **Form:** **None** — correctly omitted (same)
- **Channel:** `plain`
- **Persona:** `to-engineering-lead` (same)

**Bar command constructed:**
```bash
bar build make full struct plain to-engineering-lead
```

**Variance:** None — consistent exclusion of scaffold. ✅

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `make+struct` precisely targets design document creation |
| Token completeness | 5 | Audience persona adds appropriate framing for design review |
| Skill correctness | 5 | Correctly applied R-05 exclusion rule |
| Prompt clarity | 5 | Clear artifact production instruction |
| **Overall** | **5** | **Fixed! Loop 1 gap resolved.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** R-05 fix working correctly. T10 and T19 both show scaffold is now properly excluded for make+design artifact tasks.

