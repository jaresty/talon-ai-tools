## Task: T114 — Identify security vulnerabilities

**Task description:** "What could an attacker exploit?"
**Probability weight:** 8%
**Domain:** security

---

**Skill selection log:**
- Task token: probe (surface risks)
- Completeness: full
- Scope: considered fail, cross, struct → chose: fail
  - Why fail? The new description: "focuses on breakdowns, stress, uncertainty, or limits by examining how and under what conditions something stops working—risks, edge cases, fragility" fits well. Security vulnerabilities are failures/weaknesses in the system.
- Method: adversarial (attacker mindset)
- Form: (none)
- Channel: plain
- Persona: peer_engineer_explanation

**Bar command constructed:**
```
bar build probe full fail plain adversarial peer_engineer_explanation
```

---

**Coverage scores:**
- Token fitness: 5 — `fail` captures vulnerability/breakdown analysis
- Token completeness: 5 — adversarial method perfect for security
- Skill correctness: 5 — excellent selection
- Prompt clarity: 5 — clear vulnerability analysis focus
- **Overall: 5**

**Gap diagnosis:** none

**Notes:**
Excellent. New `fail` description worked well: "examining how and under what conditions something stops working—risks, edge cases, fragility." Security is fundamentally about finding failure modes. The skill correctly avoided `cross` (which would look for boundary-spanning patterns but not specifically vulnerabilities).

---

*Loop-5 realistic task evaluation*
