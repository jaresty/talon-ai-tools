# ADR-0113 Loop-5 Evidence — Scope Prompt Validation (Realistic Tasks)

**Date:** 2026-02-14  
**Status:** Complete  
**Focus:** Validating new scope descriptions against realistic user tasks  
**Method:** Task-gap analysis starting from real tasks, not scope distinctions

---

## Summary

Loop 5 evaluated the new scope prompt descriptions (commit 4be88cb) against realistic user tasks to see if they improve catalog coverage. Unlike previous loops that tested scope discrimination artificially, this loop started from actual software engineering workflows.

**Key Results:**
- **Tasks evaluated:** 8 representative tasks (of 15 in taxonomy)
- **Mean score:** 4.875/5.0
- **All tasks score ≥ 4** — No critical gaps
- **7 of 8 tasks scored 5/5** — Excellent coverage
- **New scope descriptions working well** — Clear guidance for realistic tasks

---

## Task Scores Summary

| Task | Weight | Description | Score | Primary Scope Used |
|------|--------|-------------|-------|-------------------|
| T110 | 12% | Debug production latency | **5** | cross |
| T111 | 10% | Database migration planning | **5** | time |
| T112 | 9% | Architecture decision review | **5** | good |
| T113 | 8% | Code explanation | **5** | flow |
| T114 | 8% | Security vulnerability identification | **5** | fail |
| T119 | 5% | Error handling consistency | **5** | cross |
| T122 | 4% | Technical debt assessment | **4** | good |
| T124 | 3% | Request flow tracing | **5** | flow |

**Mean:** 4.875/5.0  
**Target:** ≥ 4.5 ✅

---

## New Scope Descriptions Performance

### Working Excellently

| Scope | Tasks | Performance |
|-------|-------|-------------|
| **cross** | T110, T119 | New description: "concerns or forces that propagate across otherwise distinct units" clearly guides selection for boundary-spanning concerns (performance, error handling) |
| **fail** | T114 | New description: "breakdowns, stress, uncertainty, or limits...risks, edge cases, fragility" perfect for security vulnerability analysis |
| **good** | T112, T122 | New description: "quality, success, or goodness is judged—criteria, metrics, standards" clear for evaluation tasks |

### Observations

**T122 — Technical Debt (Score: 4)**
- Scope selected: `good` (quality assessment)
- Gap: Technical debt spans multiple scopes (good, fail, struct)
- **Insight:** New scope descriptions are clear individually, but don't guide when to combine scopes for multi-faceted assessments

---

## Findings

### Strengths

1. **Clear scope boundaries** — New descriptions make struct/cross/mean/assume distinctions crisp
2. **Realistic task coverage** — 7 of 8 tasks scored 5/5 with clear scope selection
3. **No confusion between similar scopes** — Skill correctly discriminated in all cases
4. **Consistent with previous loops** — R-01 (cross token) continues working well

### Minor Observations (Not Critical Gaps)

| Task | Observation | Priority |
|------|-------------|----------|
| T122 | Multi-faceted assessments may benefit from scope combination guidance | Low |

---

## Comparison to Previous Loops

| Loop | Focus | Mean Score | Key Finding |
|------|-------|------------|-------------|
| Loop-1 | Initial gap analysis | N/A | Added cross token, fixed persona normalization |
| Loop-2 | Verify loop-1 fixes | 4.5+ | All recommendations working |
| Loop-3 | Extended coverage | 4.7 | Excellent coverage across domains |
| Loop-4 | Bar variants taxonomy | 4.87 | High-frequency tasks all perfect |
| **Loop-5** | **Scope prompt validation** | **4.875** | **New descriptions working well** |

---

## Recommendations

### Implemented: R-L5-01 Multi-Scope Assessment Guidance

**Added to `internal/barcli/help_llm.go` in Usage Patterns section:**

```go
{
    title:   "Comprehensive Assessment (Multi-Scope)",
    command: "bar build check <scope> full <method> --subject \"...\"",
    example: "bar build check good full analysis --subject \"Assess codebase quality\"",
    desc:    "Use for multi-faceted assessments that span quality (good), fragility (fail), and structure (struct). When the task requires multiple analytical lenses, prioritize by primary concern or analyze sequentially: quality-first (good), risk-first (fail), or architecture-first (struct).",
},
```

This addresses the T122 finding where technical debt assessment spans multiple scopes. Now `bar help llm` provides guidance for handling multi-faceted assessments.

### No Critical Recommendations

Loop 5 achieved target mean (4.875 ≥ 4.5) with 7 of 8 tasks scoring 5/5. The only observation has been addressed.

---

## Conclusion

**Loop 5 validates the new scope prompt descriptions:**

1. ✅ **New descriptions are clear and actionable** — 7/8 tasks scored perfectly
2. ✅ **Scope discrimination working** — No confusion between similar scopes
3. ✅ **Mean 4.875 exceeds 4.5 target** — Excellent coverage maintained
4. ✅ **Consistent with loop-4 high-frequency success** — New descriptions don't regress previous fixes

**The scope prompt update (commit 4be88cb) is successful.**

---

## Artifacts

| File | Description |
|------|-------------|
| `task-taxonomy.md` | 15 realistic user tasks |
| `evaluations/task_T*_eval.md` | Per-task evaluations |
| `loop-5-summary.md` | This analysis |

---

*Validation complete — scope prompts working as intended*
