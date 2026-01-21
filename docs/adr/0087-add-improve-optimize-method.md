# ADR 0087: Add "Improve" Method Token to Grammar Catalog

## Status

Proposed

## Date

2026-01-21

## Owners

Grammar catalog working group

## Context

The current method axis provides specialized reasoning approaches (adversarial, rewrite, debug, etc.) but lacks a general-purpose "make this better" instruction that users frequently need.

**Gap identified:** When asked how to express "improve this code" or "optimize this function," there is no direct method token that captures this intent.

**Current workarounds:**
- `method=rewrite` - Closest match, but emphasizes "preserving the original intent" and "mechanical transform" rather than enhancement
- `method=adversarial` - Stress-tests for weaknesses "aimed at improving the work" but through critique, not direct enhancement
- `method=tune` - Concordance Frame-specific, not general-purpose
- `method=bridge` - "Charts a path from current state to desired situation" but focuses on the transition, not the improvement itself

**User request patterns:**
- "Improve the performance of this code"
- "Optimize this algorithm"
- "Make this function better"
- "Enhance the readability of this class"
- "Polish this implementation"

None of these map cleanly to an existing method token. Users must either:
1. Rely on the task/subject to carry the improvement intent ("Optimize the sorting algorithm")
2. Use `rewrite` even though it doesn't emphasize enhancement
3. Leave method blank and hope the LLM infers improvement intent

**Evidence:**
- Interactive grammar Q&A (2026-01-21) revealed the gap when discussing how to express code optimization/improvement
- Method axis search for "improve|better|optimize|enhance|refine|polish" found only incidental mentions in other token descriptions

## Problem

Users lack a clear, general-purpose method token for requesting improvements, optimizations, or enhancements to existing work. This forces them to:
- Overload the task/subject with both WHAT and HOW instructions
- Use inappropriate tokens (rewrite) that don't match their intent
- Omit the method axis entirely, reducing prompt precision

The method axis should provide a direct way to say "take what exists and make it better along relevant dimensions."

## Decision

Add a new `improve` method token with the following definition:

```python
# lib/axisConfig.py - method axis

'improve': 'The response takes existing work and enhances it along relevant '
           'dimensions—such as performance, readability, maintainability, '
           'correctness, or robustness—identifying specific improvements and '
           'applying them while preserving core functionality.',
```

**Rationale for "improve" over "optimize":**
- "Improve" is broader and more general-purpose (covers readability, structure, etc.)
- "Optimize" implies performance/efficiency focus, which is narrower
- "Improve" feels more natural for diverse improvement types
- Users can still say "optimize" and it will map to "improve" via fuzzy matching/aliases if needed

**Token placement:** Add to the method axis alongside existing transformation-oriented methods (rewrite, refactor, debug).

**Semantic boundaries:**
- **improve** vs **rewrite**: "improve" emphasizes enhancement; "rewrite" emphasizes preservation
- **improve** vs **adversarial**: "improve" directly enhances; "adversarial" finds weaknesses first
- **improve** vs **debug**: "improve" is proactive enhancement; "debug" is reactive problem-solving

## Implementation Plan

### Phase 1: Add Token to Catalog

1. **Update `lib/axisConfig.py`** - Add `improve` to the `method` dictionary:
   ```python
   'improve': 'The response takes existing work and enhances it along relevant '
              'dimensions—such as performance, readability, maintainability, '
              'correctness, or robustness—identifying specific improvements and '
              'applying them while preserving core functionality.',
   ```

2. **Regenerate Talon lists** - Run `make axis-regenerate` to update voice grammar

3. **Update documentation** - Refresh README axis sections via `make axis-guardrails`

4. **Add test coverage** - Verify `improve` appears in method catalog and can be selected

### Phase 2: Validation via Shuffle

Use ADR 0085's shuffle-driven refinement process to validate the new token:

```bash
# Generate prompts using improve method
bar shuffle --seed 200 --include method --require improve
bar shuffle --seed 201 --include static,method --require improve --fill 0.7
bar shuffle --seed 202 --include improve --exclude persona_preset
```

**Evaluation criteria:**
- Does `improve` produce enhancement-focused outputs distinct from `rewrite`?
- Do combinations like `improve + form=code` yield refactored implementations?
- Are there task types where `improve` creates confusion or redundancy?

### Phase 3: Cross-Reference Updates

1. **Spoken aliases** (optional) - Consider adding "optimize", "enhance", "polish" as spoken aliases that map to "improve"

2. **Help surfaces** - Update quick-help and grammar learning overlays to mention `improve` as the enhancement method

3. **Static prompt compatibility** - Test `improve` with code-focused static prompts (refactor, review, debug) to ensure coherent combinations

## Consequences

**Positive:**
- Users gain a clear, general-purpose way to request improvements
- Reduces overloading of task/subject with HOW instructions
- Improves prompt precision for common enhancement workflows
- Fills a gap in the method axis without overlapping existing tokens

**Neutral:**
- One more method token increases catalog size (but method axis is already extensive)
- Requires documentation refresh and list regeneration

**Risks:**
- Potential overlap with `rewrite` - mitigated by clear semantic boundary (enhancement vs preservation)
- Users might expect "improve" to work on non-code tasks - addressed by broad definition covering multiple dimensions
- May expose other missing "action" methods (e.g., "simplify", "expand") - acceptable; can address in future refinement cycles

## Validation Criteria

- [ ] `improve` token added to `lib/axisConfig.py` method axis
- [ ] Talon lists regenerated (`make axis-regenerate`)
- [ ] Documentation refreshed (`make axis-guardrails`)
- [ ] Test coverage confirms `improve` appears in method catalog
- [ ] Shuffle evaluation (3+ seeds) demonstrates distinct, enhancement-focused outputs
- [ ] No conflicts with existing method tokens (rewrite, adversarial, debug)
- [ ] Help surfaces updated to reference `improve`

## Alternatives Considered

1. **Use "optimize" instead of "improve"**
   - Rejected: Too narrow (implies performance focus)
   - "Improve" is more general-purpose

2. **Use "enhance" instead of "improve"**
   - Rejected: Less common, less clear
   - "Improve" is more direct and familiar

3. **Add both "improve" and "optimize" as separate tokens**
   - Rejected: Creates unnecessary duplication
   - Use spoken aliases if performance-specific language is needed

4. **Extend "rewrite" description to include enhancement**
   - Rejected: "Rewrite" has clear established semantics (preservation)
   - Changing it would break existing user expectations

5. **Don't add any token; rely on task/subject**
   - Rejected: Reduces prompt grammar precision
   - Method axis exists to express HOW, not just WHAT

## References

- ADR 0085: Shuffle-Driven Catalog Refinement (process)
- ADR 0086: Catalog Refinements from First Shuffle Cycle (precedent)
- ADR 0083: Prompt Key Refinement (method axis semantics)
- Interactive grammar discussion (2026-01-21) identifying the gap

## Follow-up Work

- Monitor shuffle evaluations for other missing "action" methods (simplify, expand, consolidate)
- Consider spoken alias mapping ("optimize" → "improve", "enhance" → "improve")
- Evaluate whether other axes have similar gaps in common user intents
