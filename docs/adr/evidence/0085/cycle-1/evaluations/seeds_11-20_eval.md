## Shuffle Seeds 11-20 — Batch Evaluation

**Evaluation Summary:**

| Seed | Task | Completeness | Scope/Method | Form/Channel | Directional | Persona | Score | Notes |
|------|------|--------------|--------------|--------------|-------------|---------|-------|-------|
| 11 | probe | full | diagnose | diagram | dig | junior | 4 | Diagnosis as diagram — unusual but valid |
| 12 | show | full | mean | — | dip rog | XP | 4 | Conceptual understanding for XP audience |
| 13 | show | full | — | log+diagram | — | CEO | 3 | log + diagram channel conflict ⚠️ |
| 14 | show | full | struct+prioritize | activities | fip rog | junior | 5 | Structured prioritization activity |
| 15 | probe | full | mean+grove | — | — | team | 5 | Compounding effects analysis |
| 16 | show | minimal | — | plain | dip ong | CEO | 4 | Minimal for CEO — slight mismatch |
| 17 | show | full | — | codetour | — | — | 5 | Code explanation via tour |
| 18 | show | skim | — | merge+plain | — | team | 4 | Skim + merge slight tension |
| 19 | show | deep | cluster | scaffold | — | — | 5 | Deep clustering with scaffolding |
| 20 | sim | full | simulation | questions | — | PM | 5 | Scenario sim via questions for PM |

---

### Potential Conflict Identified

**Seed 13 — Score 3:**
- Form: log (work log entry)
- Channel: diagram (Mermaid diagram)
- **Conflict:** These appear incompatible
  - log = prose with date/time markers
  - diagram = Mermaid code only
- **Severity:** Moderate — channels define output format, forms organize within format
- **Resolution:** Form might be ignored or channel takes precedence

**Recommendation:** Document that channel takes precedence over form when incompatible

---

### Overall Statistics (Seeds 11-20)

| Score | Count | Percentage |
|-------|-------|------------|
| 5 | 5 | 50% |
| 4 | 4 | 40% |
| 3 | 1 | 10% |
| 2 | 0 | 0% |
| 1 | 0 | 0% |

**Mean:** 4.4/5.0

---

### Key Findings

1. **One potential conflict:** log form + diagram channel (Seed 13)
2. **No broken combinations:** All scores ≥ 3
3. **CEO persona appearing:** Seeds 13, 16 — business context coverage
4. **Simulation working:** Seed 20 (sim + simulation + questions) for PM

