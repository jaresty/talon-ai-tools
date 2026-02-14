## Task: T35 — Pre-mortem for release planning (NEW — Edge Case)

**Domain:** Planning  
**Rationale:** Test R-08 Pre-mortem / Inversion pattern  
**Task Description:** "Assume our Q4 launch has failed spectacularly — what went wrong?"

---

### Skill Selection Log (Run 1)

**Task Analysis:**
- Classic pre-mortem: assume failure, work backward
- Per R-08: Pre-mortem → `inversion` method
- Planning context

**Token Selection:**
- **Task:** `probe` (diagnostic analysis of failure causes)
- **Completeness:** `full` (thorough pre-mortem)
- **Scope:** `fail` (failure modes)
- **Method:** Considered `adversarial` (attack), `inversion` (backward reasoning) → chose `inversion`
  - *Skill correctly surfaced R-08 Pre-mortem pattern!*
- **Form:** `variants` (multiple failure scenarios)
  - *Good form selection for pre-mortem brainstorming*
- **Channel:** `plain` (prose)
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build probe full fail inversion variants plain
```

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `probe+fail+inversion+variants` perfect for pre-mortem |
| Token completeness | 5 | All dimensions covered; variants adds scenario breadth |
| Skill correctness | 5 | Correctly applied R-08 pattern |
| Prompt clarity | 5 | Clear pre-mortem instruction |
| **Overall** | **5** | **Excellent — R-08 working.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** R-08 Pre-mortem pattern successfully applied. Skill routes "assume failure..." language to `inversion` method as intended.

**Observation:** The combination of `inversion` + `variants` is particularly effective for pre-mortems — generates multiple failure scenarios via backward reasoning.

