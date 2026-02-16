# ADR-0085 Cycle-5 Recommendations

**Date:** 2026-02-15  
**Source:** Cycle-5 shuffle evaluation (seeds 50-69)

---

## Findings Summary

- **Mean score:** 3.7/5
- **Broad sweep:** 3.7/5
- **Low-fill:** 4.4/5
- **High-fill:** 3.3/5
- **Evaluated:** 20 seeds (broad + edge cases)

---

## Recommendations

### R-05: Add Channel-Form Conflict Detection

```yaml
action: edit
target: "bar help llm - Composition Rules"
section: "Channel-Form Conflicts"
proposed_addition: >
  "Channel and form tokens can conflict. Avoid these combinations:
   
   - sketch (D2) + indirect/prose forms → Choose diagram OR prose, not both
   - shellscript + pick/diff/sort → Shell script output doesn't fit selection tasks
   - gherkin + sort/fix/make → Gherkin is BDD format, not suitable for sorting/creation"
recommendation: "Add to Composition Rules section"
```

**Rationale:** Multiple seeds showed channel-form conflicts (50, 53, 67, 68). Users need guidance. Seed 50 meta-eval confirmed skills can't guide away from this.

---

### R-06: Document Strong Task-Channel Pairs

```yaml
action: edit
target: "bar help llm - Token Selection Heuristics"
section: "Task-Channel Combinations"
proposed_addition: >
  "Effective combinations:
   
   - diff + jira → Comparison in Jira format
   - make + svg → Create SVG diagrams
   - check + log → Validation output in log format
   - plan + adr → Planning as Architecture Decision Records
   - sim + diagram → Scenarios as Mermaid diagrams"
recommendation: "Add as guidance in Token Selection Heuristics"
```

**Rationale:** Seeds 51, 54, 65 showed good task-channel synergy. Seed 54 meta-eval confirmed skills already guide this well via Usage Patterns.

---

### R-07: Add Token Count Guidance

```yaml
action: edit
target: "bar help llm - Composition Rules"
section: "General Guidance"
proposed_addition: >
  "More tokens does not equal better prompts. Low-fill prompts (1-2 tokens) scored 4.4/5 
   vs high-fill (7+ tokens) at 3.3/5. Prefer:
   
   - 2-4 tokens for most tasks
   - 5+ tokens only when task genuinely requires multiple dimensions"
recommendation: "Add to Composition Rules (reinforces R-02 from Cycle-4)"
```

**Rationale:** Cycle-4 R-02 is still valid. Low-fill continues to outperform.

---

### R-08: Add Task-Channel Incompatibility Documentation

```yaml
action: edit
target: "bar help llm - Composition Rules"
section: "Task-Channel Incompatibilities"
proposed_addition: >
  "Task and channel tokens can be semantically incompatible. Avoid:
   
   - shellscript + pick/diff/sort → Shellscript is code execution, not selection/sorting
   - gherkin + sort/fix/make → Gherkin is BDD behavior specification, not for creation/sorting"
recommendation: "Add to Composition Rules section"
```

**Rationale:** Seeds 67, 68 had very low scores due to task-channel mismatch. Seed 67 meta-eval confirmed skills can't warn users away from this.

---

## Not Recommended

### No Individual Token Removals

While certain combinations scored low, no single token was consistently problematic across seeds. The issues are combination-specific, not token-specific.

---

## Next Steps

1. **Apply R-05** to `bar help llm` (Composition Rules - Channel conflicts)
2. **Apply R-06** to `bar help llm` (Token Selection Heuristics - Task-Channel pairs)
3. **Apply R-07** to `bar help llm` (reinforces Cycle-4 R-02)
4. **Investigate R-08** - Consider deprecating or removing shellscript/gherkin for incompatible tasks
5. **Validate** in Cycle-6

---

*Recommendations derived from ADR-0085 shuffle-driven refinement, Cycle-5*
