# ADR 0085: Shuffle Evaluation Corpus

This directory contains shuffled prompt evaluations following the process in ADR 0085.

## Generation Summary

- **Broad sweep**: 150 random shuffles (seeds 1-150)
- **Method deep-dive**: 11 samples (seeds 100-110)
- **Scope deep-dive**: 11 samples (seeds 111-121)
- **Directional deep-dive**: 11 samples (seeds 122-132)
- **Low-fill edge cases**: 11 samples (seeds 200-210)
- **High-fill edge cases**: 11 samples (seeds 211-221)

## Evaluation Status

| Seed | Category | Status | Overall Score |
|------|----------|--------|---------------|
| 0001 | broad | evaluated | 3 |
| 0002 | broad | evaluated | 4 |
| 0003 | broad | evaluated | 3 |
| 0005 | broad | evaluated | 2 |
| 0010 | broad | evaluated | 3 |
| 0015 | broad | evaluated | 4 |
| 0020 | broad | evaluated | 4 |
| 0100 | method | evaluated | 4 |
| 0111 | scope | evaluated | 3 |

**Average Score (so far): 3.3/5**

## Key Findings

### Issues Discovered

1. **Seed 0005** (score 2):grove token may be miscategorized - overlaps with scope=time
2. **Precedence tension**: form vs channel interaction not always clear (e.g., gherkin + presenterm)
3. **Semantic overlap**: fail (scope), grove (method), and fip rog (directional) can create redundant combinations
4. **contextualise token**: Description is complex and may confuse users

### Positive Findings

- Most combinations are coherent and well-formed
- Skills documentation provides good coverage
- Reference documentation is generally adequate
- Best-in-class: seed 0020 (plan + deep + act + adversarial) demonstrates excellent token design
