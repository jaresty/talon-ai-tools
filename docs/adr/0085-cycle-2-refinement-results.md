# ADR 0085-Cycle-2: Shuffle-Driven Catalog Refinement Results

**Status:** Accepted  
**Date:** 2026-02-15  
**Related:** ADR 0083 (Prompt Key), ADR 0084 (Shuffle Command), ADR 0085 (Catalog Refinement Process)  
**Evidence:** `docs/adr/evidence/0085/cycle-2/`

---

## Executive Summary

**Key Decision:** Retire the `rewrite` form token entirely.

**Rationale:** Data from 3 evaluation cycles shows `rewrite` form never scores above 3/5 and has fundamental semantic conflicts with core tasks (`make`, `diff`, `pull`). It describes a transformation *activity* (method level) miscategorized as a presentation *structure* (form level).

**Alternative:** Users should use the `fix` task for transformations, which has clear semantics and consistently scores higher.

**Additional Actions:**
- Define interaction behaviors for `socratic` and `contextualise` forms instead of building constraint logic
- Clarify documentation for channel-task pairings
- Document exemplar combinations from high-scoring seeds

**Approach:** Fix the root cause (retire problematic token) rather than building validation logic to work around it.

---

## Context

Following ADR 0085's shuffle-driven refinement process, Cycle 2 evaluated 20 shuffled prompts (seeds 121-140) against ADR 0083's Prompt Key criteria and Bar Skills documentation. This ADR documents findings and recommendations for catalog improvements.

**Methodology:**
1. Generated 20 prompts with reproducible seeds (121-140)
2. Evaluated each against Prompt Key rubric (5 criteria, 1-5 scale)
3. Meta-evaluated against Bar Skills documentation (4 criteria, 1-5 scale)
4. Aggregated patterns and recommendations

---

## Findings Summary

### Score Distribution

| Overall Score | Count | Seeds | Percentage |
|---------------|-------|-------|------------|
| 5/5 (Excellent) | 10 | 121, 124, 125, 128, 130, 131, 135, 137, 139, 140 | 50% |
| 4/5 (Good) | 2 | 129, 138 | 10% |
| 3/5 (Acceptable) | 4 | 122, 123, 126, 127 | 20% |
| 2/5 (Problematic) | 3 | 132, 134, 136 | 15% |
| 1/5 (Broken) | 1 | 133 | 5% |

**Success Rate:** 60% (12/20) achieved high-quality (4-5/5) ratings

### Critical Issues Identified

1. **Documented Incompatibilities Not Enforced**
   - Seed 133: `make` + `rewrite` form (docs explicitly call this "semantically incoherent")
   - Seed 134: `sim` + `shellscript` channel (docs say "not appropriate for narrative tasks")
   - Seeds 127, 136: `probe/diff` + `gherkin` (inappropriate for non-behavioral tasks)

2. **Persona-Channel Conflicts**
   - Seed 122: `fun_mode` + `gherkin` (casual tone vs rigid structure)
   - Seed 132: `to managers` + `codetour` (wrong audience for developer tool)

3. **Intent-Method Tensions**
   - Seed 123: `appreciate` intent + `diagnose` method (contradictory approaches)

4. **Form-Channel Incompatibility**
   - Seed 122: `contextualise` form + `gherkin` channel
   - Seed 126: `table` form + `svg` channel
   - Seed 134: `socratic` form + `shellscript` channel

---

## Recommendations

### CRITICAL: Retire `rewrite` Form Token

**Evidence:** Analysis of all evaluation cycles shows `rewrite` form never scores above 3/5:

| Seed | Cycle | Score | Issue |
|------|-------|-------|-------|
| 133 | Cycle 2 | **1/5** | "Semantically incoherent" with make task |
| 53 | Seeds 41-60 | **3.0/5** | Make+rewrite semantic conflict |
| 55 | Seeds 41-60 | **2.4/5** | Rewrite+diff conflict |

**Root Cause:** "Rewrite" describes a transformation *activity* (method/task level), not a presentation *structure* (form level). It fundamentally conflicts with:
- `make` task (create from nothing vs transform existing)
- `diff` task (compare vs transform)
- `pull` task (extract vs transform)

**Decision:** Retire `rewrite` form entirely. Users needing transformation should use `fix` task instead.

**Migration Path:**
- `bar build make rewrite --subject "X"` → `bar build fix --subject "existing X"` or `bar build make --subject "new X"`
- No loss of functionality; clearer semantics

---

### HIGH: Define Form-Task Interactions

Instead of blocking combinations, define how they work together:

#### `socratic` Form Interactions

**History:** Socratic form has mixed results (5/5 with sort, 2/5 with sim+shellscript, 3/5 with fix)

**Solution:** Define interaction behavior in prompt generation:

```yaml
socratic_form_interactions:
  with_sort:
    behavior: "Ask 2-3 clarifying questions about sorting criteria, then provide sorted result"
    example: "What primary dimension should drive this categorization? [questions] → [answers] → [sorted list]"
    
  with_sim:
    behavior: "Present scenario parameters as questions before simulating"
    incompatible_with: [shellscript, code, codetour]  # Can't ask questions in code output
    
  with_fix:
    behavior: "Ask diagnostic questions before proposing transformation"
    note: "Natural fit - socratic inquiry pairs well with identifying what needs fixing"
```

#### `contextualise` Form Interactions

**History:** Scores 3/5 with fix+gherkin, 4/5 with pull+sync

**Solution:** Define channel compatibility:

```yaml
contextualise_form:
  description: "Adds framing context without changing core content"
  compatible_channels: [plain, sync, jira, slack]
  incompatible_channels: [gherkin, shellscript, code, codetour]  # Pure output channels
  
  with_pull:
    behavior: "Extract information with added framing context"
    example: "Pull + contextualise = extraction with context preservation"
```

---

### HIGH: Clarify Channel-Task Documentation

Current issue: Documentation warns about inappropriate pairings but doesn't define what happens:

**Current (ambiguous):**
> "gherkin channel: not appropriate for non-behavioral tasks (sort, sim, probe)"

**Proposed (clear):**
> "gherkin channel: produces Gherkin syntax output. When combined with non-behavioral tasks, the task directive shapes the scenario content while gherkin shapes the output format. Example: `bar build sort gherkin --subject "features"` produces Gherkin scenarios that categorize features."

Apply this pattern to all channel-task warnings.

---

### MEDIUM: Document Intent-Method Interactions

Instead of forbidding combinations, document the interaction:

```yaml
intent_method_interactions:
  appreciate_intent:
    with_diagnose: "Begin by acknowledging what works well, then diagnose gaps"
    with_risks: "Frame risks as appreciation for what could go wrong"
    note: "Appreciation doesn't exclude diagnostic methods; it changes their framing"
    
  teach_intent:
    with_diagnose: "Use diagnostic examples as teaching moments"
    note: "Teaching can include showing what NOT to do (diagnose errors)"
```

---

### MEDIUM: Exemplar Documentation

From high-scoring seeds, create reference patterns:

**Exemplar 1: Rigorous Creation** (Seed 121)
```
bar build make good verify test --subject "..."
Persona: designer_to_pm
Directional: fip rog
```
Use case: Creating quality-focused artifacts with falsification validation

**Exemplar 2: Planning with Assumptions** (Seed 131)
```
bar build plan assume simulation variants --subject "..."
Persona: designer_to_pm
Directional: dip ong
```
Use case: Scenario-based planning exploring multiple paths

**Exemplar 3: Decision Support** (Seed 139)
```
bar build pick spec recipe --subject "..."
Persona: scientist_to_analyst
```
Use case: Structured decision-making with specification

---

### LOW: Catalog Documentation Enhancements

1. **Add "Compatibility" section** to each token documentation:
   - Compatible with: [list]
   - Conflicts with: [list]
   - Works best with: [list]

2. **Add "Anti-patterns" section** documenting problematic combinations found in shuffle evaluation

3. **Update shuffle algorithm** to implement compatibility scoring, avoiding known problematic combinations

---

## Implementation Plan

### Phase 1: Retire `rewrite` Form (Immediate)
- [ ] Remove `rewrite` from axisConfig.py form axis
- [ ] Update help_llm.go to remove rewrite references
- [ ] Add migration note: "Use `fix` task for transformations"
- [ ] Regenerate grammar

### Phase 2: Define Interactions (Next Sprint)
- [ ] Add interaction definitions to promptConfig.py
- [ ] Update help_llm.go with form-task interaction documentation
- [ ] Update bar help llm --section tokens to show interaction guidance

### Phase 3: Documentation (Following Sprint)
- [ ] Create exemplar pattern documentation
- [ ] Add "Interactions" section to token docs
- [ ] Document anti-patterns from evaluation

### Phase 4: Quality Improvements
- [ ] Track shuffle statistics to identify problematic tokens
- [ ] Consider adding `--quality` flag to shuffle for filtering

---

## Validation

After implementation, validate by:

1. Re-running seeds 121-140 to confirm improvements
2. Expecting 70%+ success rate (up from 60%)
3. Zero occurrences of `rewrite` form in shuffle output
4. Clear interaction documentation for `socratic` and `contextualise`

---

## Files to Modify

| File | Change |
|------|--------|
| `lib/axisConfig.py` | Remove `rewrite` from form axis |
| `internal/barcli/help_llm.go` | Remove rewrite references; add interaction docs |
| `lib/promptConfig.py` | Add form-task interaction definitions |
| `.claude/skills/bar-workflow/skill.md` | Document rewrite→fix migration |
| Grammar files | Regenerate after rewrite removal |

---

## Consequences

### Positive
- Eliminates semantically incoherent `rewrite` form entirely
- Reduces catalog complexity (fewer tokens to maintain)
- Improves clarity: `fix` task for transformations is unambiguous
- Maintains full flexibility for valid edge cases
- Lower implementation cost (no validation logic)

### Tradeoffs
- Breaking change: users of `rewrite` form need to migrate
- `socratic` and `contextualise` still need careful documentation

### Risks
- **User confusion:** Users accustomed to `rewrite` need migration guidance
- **Edge case loss:** Some `rewrite` combinations might have been working

**Mitigations:**
- Provide clear error message: "`rewrite` form retired. Use `fix` task for transformations."
- Document migration examples in help
- Include in release notes

---

## Related Evidence

- Full evaluation: `docs/adr/evidence/0085/cycle-2/evaluations-complete.md`
- Raw corpus: `docs/adr/evidence/0085/cycle-2/corpus/`
- Previous cycles: `docs/adr/evidence/0085/cycle-1/`

---

*This ADR was produced using the ADR 0085 shuffle-driven refinement process.*
