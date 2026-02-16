# ADR-0113 Loop-6 Summary — Token Guidance Validation

**Date:** 2026-02-15  
**Status:** Complete  
**Focus:** Validate token guidance added in ADR-0128  

---

## Summary

Loop-6 tested the token guidance added in ADR-0128 by evaluating tasks that target the new guidance:

- **Tasks evaluated:** 13
- **Mean score:** 4.5/5
- **Target:** ≥ 4.0 ✅

---

## Task Scores

| Task | Description | Selected Tokens | Score | Guidance Validated |
|------|-------------|------------------|-------|-------------------|
| T130 | Summarise RFC | pull + gist | 5 | ✅ show → pull |
| T131 | Security risks | pull + gist | 5 | ✅ probe → pull |
| T132 | Test plan | make + act | 5 | ✅ make for creation |
| T133 | Test gaps | check + good + fail | 5 | ✅ check for evaluation |
| T134 | Explain to exec | show + mean | 4 | ✅ No scaffold |
| T135 | Design API | make + scaffold | 3 | ⚠️ Scaffold conflict |
| T136 | Extract decisions | pull + gist | 5 | ✅ pull guidance |
| T137 | Risk assessment | pull + fail | 4 | ✅ probe → pull |
| T138 | Generate options | probe + variants | 5 | ✅ probe correct |
| T139 | Document patterns | show + struct | 4 | ✅ No pull needed |
| T140 | Code quality | check + good | 5 | ✅ check correct |
| T141 | Compare tools | diff + thing | 5 | ✅ diff correct |
| T142 | Explain to junior | show + scaffold | 3 | ⚠️ Scaffold conflict |

---

## Findings

### Working Well

1. **Pull guidance working**: Tasks T130, T131, T136, T137 correctly use pull for extraction
2. **Make/Check distinction working**: T132 (test plan) uses make, T133 (test gaps) uses check
3. **Guidance visible**: `bar help llm` shows the new guidance for scaffold, probe, show, pull

### Issues Found

| Task | Issue | Severity |
|------|-------|----------|
| T135 | scaffold + make used despite guidance | Medium - guidance visible but not followed |
| T142 | scaffold + show for junior (borderline) | Low - may be valid use case |

### Analysis

The scaffold guidance is present and visible in `bar help llm`, but users (or skills) may still select it for design tasks. This is a **guidance vs. enforcement** issue - the guidance tells users to avoid, but doesn't prevent selection.

The key question: Should scaffold + make be **blocked** at grammar level, or is guidance sufficient?

---

## Comparison to Prior Loops

| Loop | Focus | Mean Score |
|------|-------|-------------|
| Loop-4 | Taxonomy generation | 4.87 |
| Loop-5 | Scope validation | 4.875 |
| **Loop-6** | **Token guidance** | **4.5** |

Slightly lower due to scaffold conflicts. This is expected - guidance doesn't force behavior.

---

## Recommendations

### No Critical Issues

The token guidance is working as designed - visible at point of selection. Whether users follow it depends on:
1. How prominently the guidance is displayed in TUI
2. Whether skills enforce or suggest
3. User attention to guidance

### Future Consideration

If scaffold + make conflicts remain problematic:
- Option A: Add to grammar incompatibilities (block at parse time)
- Option B: Keep as guidance and accept some misuse
- Option C: Add TUI warning when conflicting combo selected

---

## Conclusion

✅ ADR-0128 token guidance is implemented and visible  
✅ Task selection improved for probe/pull and make/check  
⚠️ Scaffold guidance visible but not always followed  

The guidance approach is working - users can see the recommendation. Enforcement would require grammar changes.

---

*Loop-6 complete - token guidance validated*
