## Shuffle Seeds 21-30 — Batch Evaluation

**Evaluation Summary:**

| Seed | Task | Completeness | Scope/Method | Form/Channel | Directional | Persona | Score | Notes |
|------|------|--------------|--------------|--------------|-------------|---------|-------|-------|
| 21 | probe | skim | operations | sync | fig | Kent Beck | 4 | Light ops analysis via sync — slight mismatch |
| 22 | show | minimal | mod | table | — | programmer | 5 | Modulo reasoning as table — interesting |
| 23 | show | full | — | — | — | stakeholders | 4 | Basic but valid |
| 24 | show | full | order | wardley | fly ong | team | 5 | Wardley Map for team |
| 25 | probe | max | good | — | ong | — | 4 | Max + good slight tension |
| 26 | make | full | — | recipe | dip ong | programmer | 5 | Recipe for programmers — good combo |
| 27 | show | max | origin | — | jog | junior | 5 | Deep historical analysis |
| 28 | probe | full | time+resilience | log | fip bog | platform | 5 | Operational resilience log |
| 29 | show | max | good+boom | quiz | fip rog | PM | 3 | Quiz + presenterm potential conflict ⚠️ |
| 30 | show | deep | thing+analysis | faq | shellscript | junior | 2 | **CONFLICT:** faq + shellscript incompatible ❌ |

---

### Critical Conflict Identified

**Seed 30 — Score 2:**
- Form: faq (question/answer format)
- Channel: shellscript (executable code output)
- **Conflict:** Incompatible output formats
  - faq = Q&A prose structure
  - shellscript = executable bash code
- **Severity:** High — These cannot be combined meaningfully
- **Recommendation:** Add incompatibility rule: `faq` form conflicts with `shellscript`, `code`, `codetour` channels

### Moderate Conflict

**Seed 29 — Score 3:**
- Form: quiz (questions before answers)
- Channel: presenterm (slide deck)
- **Conflict:** Quiz is interactive; presenterm is static output
- **Note:** Quiz form description says "without output-exclusive channel, conducts as interactive exchange" — presenterm IS output-exclusive
- **Severity:** Moderate — Might work as static quiz in slides

---

### Overall Statistics (Seeds 21-30)

| Score | Count | Percentage |
|-------|-------|------------|
| 5 | 5 | 50% |
| 4 | 3 | 30% |
| 3 | 1 | 10% |
| 2 | 1 | 10% |
| 1 | 0 | 0% |

**Mean:** 4.1/5.0

---

### Key Findings

1. **One broken combination (Seed 30):** faq + shellscript
2. **One moderate conflict (Seed 29):** quiz + presenterm
3. **No other critical issues:** 90% of combinations score ≥ 3
4. **Wardley Map working:** Seed 24 (form + team persona)
5. **Resilience method appearing:** Seed 28 (time + resilience + log)

