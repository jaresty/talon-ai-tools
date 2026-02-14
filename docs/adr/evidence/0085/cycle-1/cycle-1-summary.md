# ADR-0085 Cycle-1 Evidence — Shuffle-Driven Catalog Refinement

**Date:** 2026-02-14  
**Status:** Complete  
**Method:** 30 random shuffles (seeds 1-30) with systematic evaluation

---

## Summary

Cycle 1 used `bar shuffle` to generate 30 random token combinations and evaluated them for coherence, conflicts, and category alignment.

**Key Results:**
- **Total combinations:** 30
- **Mean score:** 4.37/5.0
- **Excellent (5):** 15 (50%)
- **Good (4):** 12 (40%)
- **Acceptable (3):** 2 (7%)
- **Problematic (2):** 1 (3%)
- **Broken (1):** 0 (0%)

---

## Overall Statistics

| Score | Count | Percentage | Description |
|-------|-------|------------|-------------|
| 5 | 15 | 50% | Excellent — Clear, coherent, tokens reinforce |
| 4 | 12 | 40% | Good — Minor rough edges |
| 3 | 2 | 7% | Acceptable — Some tension |
| 2 | 1 | 3% | Problematic — Conflict |
| 1 | 0 | 0% | Broken — Contradictory |

**Mean:** 4.37/5.0 ✅

---

## Findings

### ✅ Strengths

1. **50% of combinations score 5/5** — Catalog produces excellent results half the time
2. **90% score ≥ 4** — Only 10% have noticeable issues
3. **No completely broken combinations** — No score 1
4. **New tokens working:**
   - `cross` (R-01) appeared naturally in 3 combinations
   - Combines well with method tokens (melody, time)
5. **Persona system diverse:** CEO, Kent Beck, junior, team, stakeholders all appearing

### ⚠️ Conflicts Identified

| Seed | Score | Conflict | Severity | Recommendation |
|------|-------|----------|----------|----------------|
| 13 | 3 | log form + diagram channel | Moderate | Document channel precedence |
| 29 | 3 | quiz form + presenterm channel | Moderate | Quiz interactivity vs static output |
| 30 | 2 | **faq form + shellscript channel** | **High** | **Add incompatibility rule** |

**Critical Recommendation:**
- Add incompatibility: `faq` conflicts with `shellscript`, `code`, `codetour`
- Rationale: FAQ format (Q&A prose) cannot be expressed as executable code

### Minor Observations

1. **log + diagram (Seed 13):** Log (prose with timestamps) + diagram (Mermaid) — channel likely takes precedence
2. **quiz + presenterm (Seed 29):** Quiz form says "interactive exchange" without output-exclusive channel; presenterm IS output-exclusive
3. **Minimal + comprehensive scopes:** Seeds with `minimal`/`skim` + `cross`/`domains` show slight tension (expected, not problematic)

---

## New Token Validation

### `cross` Scope (R-01, Loop 1)

**Appeared in:** Seeds 1, 5, 9
**Combinations:**
- cross + minimal + spike (Seed 1)
- cross + melody + sync (Seed 5)
- cross + time (Seed 9)

**Assessment:** ✅ Working correctly — combines naturally with methods

---

## Recommendations

### R-0085-01: Add Form-Channel Incompatibility

```yaml
action: add-incompatibility
tokens:
  - form: faq
  - channel: [shellscript, code, codetour]
reason: FAQ format (Q&A prose structure) incompatible with executable code output
severity: high
evidence: [seed_30]
```

### R-0085-02: Document Quiz-Presenterm Interaction

```yaml
action: document
tokens:
  - form: quiz
  - channel: presenterm
note: >
  Quiz form conducts "interactive exchange" without output-exclusive channel.
  Presenterm IS output-exclusive, so quiz becomes static (question headings
  with revealed answers) rather than interactive. This is acceptable behavior
  but should be documented.
severity: low
evidence: [seed_29]
```

### R-0085-03: Log-Diagram Precedence

```yaml
action: document
tokens:
  - form: log
  - channel: diagram
note: >
  When log form (prose with timestamps) combines with diagram channel
  (Mermaid code), channel takes precedence. Form organization within
  diagram may be limited.
severity: low
evidence: [seed_13]
```

---

## Comparison to ADR-0113

| Metric | ADR-0113 (Task-Gap) | ADR-0085 (Shuffle) |
|--------|---------------------|-------------------|
| Method | Realistic tasks | Random combinations |
| Focus | Coverage | Coherence |
| Mean score | 4.7-4.87 | 4.37 |
| Gaps found | 0 critical | 1 conflict |
| New tokens | compare added | cross validated |

**Insight:**
- Task-gap analysis (ADR-0113) shows catalog covers realistic tasks excellently
- Shuffle analysis (ADR-0085) shows random combinations are mostly coherent
- Together: Catalog is both comprehensive AND internally consistent

---

## Conclusion

**Cycle 1 demonstrates:**
1. ✅ **Catalog is internally consistent** — 90% of random combinations score ≥ 4
2. ✅ **New tokens integrate well** — `cross` appears naturally in shuffles
3. ⚠️ **One conflict to fix** — faq + shellscript incompatibility
4. ✅ **No urgent issues** — Only 3% problematic, 0% broken

**Recommendation:**
- Fix R-0085-01 (faq-shellscript incompatibility) — high priority
- Document R-0085-02 and R-0085-03 — low priority
- Run Cycle 2 after fix to validate improvement

---

## Artifacts

| File | Description |
|------|-------------|
| `corpus/shuffle_*.json` | 30 generated prompts |
| `evaluations/seed_*_eval.md` | Per-seed evaluations |
| `cycle-1-summary.md` | This complete analysis |
| `work-log.md` | Progress tracker |

