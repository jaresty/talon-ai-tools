# ADR 0088: Adopt Universal Task Taxonomy

## Status

Proposed

## Context

The current static prompt catalog contains 46 specialized task tokens (e.g., "assumption", "who", "what", "metrics", "jobs", "wardley"). While comprehensive, this creates several issues:

1. **High cognitive load**: Users must distinguish between 46 similar-sounding tasks
2. **Overlapping semantics**: Many tasks differ only in subject matter (e.g., "assumption" vs "pain" vs "metrics" are all extraction tasks)
3. **Inconsistent granularity**: Some tasks are very specific ("connascence"), others very broad ("fix")
4. **Unclear success criteria**: Tasks like "who", "what", "when" define subject scope, not what constitutes success
5. **Difficult to extend**: Adding new tasks requires understanding how they relate to existing 46 tokens

Per ADR 0083, "TASK defines what success looks like." The current catalog conflates task types with subject-matter scopes.

### Key Insight from "Framing the idea.md"

There exist only **10 fundamental task types** that define all possible success criteria:

1. **make** - Success = something new exists
2. **fix** - Success = same content, different form
3. **pull** - Success = subset identified correctly
4. **sort** - Success = correct placement into categories
5. **diff** - Success = meaningful relationships surfaced
6. **show** - Success = understanding enabled
7. **probe** - Success = structure or insight revealed
8. **pick** - Success = justified choice made
9. **plan** - Success = actionable sequence defined
10. **check** - Success = correctness assessed

All tokens are single-syllable and pronounceable for ease of use in voice-driven workflows.

All 46 current tasks map cleanly to one of these 10 types, with subject-matter specificity better expressed through existing axes (scope, method, form).

**Test**: "If I stripped away all subject matter, could I still evaluate whether the task was completed?"
- "Extract assumptions" → pull (yes, verifiable)
- "Who is involved" → pull actors (yes, verifiable)
- "Jobs To Be Done" → probe + scope=jobs (yes, verifiable)

This test confirms that current specialized tasks combine universal task type + subject scope unnecessarily.

---

## Decision

**Replace the 46-token specialized task catalog with 10 universal task types**, expressing subject-matter specificity through new scope, method, and form axis values. All task tokens are single-syllable and pronounceable for voice-driven workflows.

### Universal Task Types to Add

```python
# lib/staticPromptConfig.py - STATIC_PROMPT_CONFIG

STATIC_PROMPT_CONFIG: dict[str, StaticPromptProfile] = {
    # Universal task types (success primitives - all single syllable)
    "make": {
        "description": "The response produces content that did not previously exist, creating something new that matches required properties.",
        "completeness": "full",
    },
    "fix": {
        "description": "The response changes the representation or form while preserving underlying meaning and semantic equivalence.",
        "completeness": "full",
    },
    "pull": {
        "description": "The response selects or isolates information already present without introducing new content.",
        "completeness": "gist",
        "method": "filter",
    },
    "sort": {
        "description": "The response assigns items to predefined or inferred categories with consistent application of category definitions.",
        "method": "cluster",
    },
    "diff": {
        "description": "The response analyzes similarities, differences, or tradeoffs along relevant dimensions with accurate relational claims.",
        "method": "compare",
    },
    "show": {
        "description": "The response makes the subject intelligible to the target audience with internal coherence and appropriate abstraction.",
    },
    "probe": {
        "description": "The response decomposes, reasons about, or interprets the subject to reveal structure or insight beyond restatement.",
        "method": "analysis",
    },
    "pick": {
        "description": "The response selects among alternatives using stated or implied criteria with clear decision and reasoned justification.",
        "method": "converge",
    },
    "plan": {
        "description": "The response produces an actionable sequence, structure, or strategy with feasible steps in logical order.",
        "method": "steps",
        "scope": "actions",
    },
    "check": {
        "description": "The response checks truth, consistency, or compliance with accurate judgment and clear pass/fail statement.",
    },
}
```

### New Axis Values Required

To preserve the functionality of retired specialized tasks, add these axis values:

#### New Scope Values (28 total)

```python
# lib/axisConfig.py - scope axis additions

'assumptions': 'The response focuses on identifying and examining the unstated assumptions underlying the subject.',

'terminology': 'The response focuses on undefined, ambiguous, or domain-specific terms that require clarification.',

'gaps': 'The response identifies what is missing, misunderstood, or unclear in the current understanding.',

'risks': 'The response focuses on potential problems, failure modes, or negative outcomes and their likelihood or severity.',

'pain': 'The response identifies obstacles, frustrations, or inefficiencies experienced by users or stakeholders.',

'metrics': 'The response focuses on measurable indicators or key performance measures that track outcomes.',

'unknowns': 'The response identifies critical unknown unknowns and explores how they might impact outcomes.',

'actors': 'The response identifies who is involved—people, roles, stakeholders, or agents in the system.',

'timing': 'The response focuses on when things occur—schedules, sequences, durations, or temporal relationships.',

'rationale': 'The response explains why something matters, the reasoning behind it, or its purpose and motivation.',

'concurrency': 'The response examines parallel execution, race conditions, synchronization, or coordination challenges.',

'disciplines': 'The response identifies relevant academic or industry fields of knowledge and their perspectives.',

'objectivity': 'The response assesses whether claims are objective facts or subjective opinions with supporting evidence.',

'jobs': 'The response analyzes Jobs To Be Done—the outcomes users want to achieve and forces shaping their choices.',

'value': 'The response focuses on user or customer value, impact, benefits, or outcomes delivered.',

'operations': 'The response identifies Operations Research or management science concepts that frame the situation.',

'connascence': 'The response analyzes connascence (static/dynamic coupling) measuring strength, degree, locality, and remedies.',

'domains': 'The response performs domain-driven discovery by identifying bounded contexts, business capabilities, and domain boundaries.',

'taoism': 'The response examines the subject through Taoist philosophy—Dao, De, Yin/Yang, Wu Wei, Ziran, Pu, Qi, Li.',

'aesthetics': 'The response evaluates taste, style, harmony, proportion, restraint, authenticity, and appropriateness.',

'formats': 'The response focuses on document types, writing formats, or structural templates and their suitability.',

'challenges': 'The response surfaces critical questions, objections, or tests that challenge the subject.',

'failures': 'The response identifies what is wrong, why it fails, weaknesses, or areas needing correction.',

'simpler': 'The response proposes simpler approaches, shortcuts, or ways to accomplish goals with less effort or time.',

'product': 'The response examines the subject through a product lens—features, user needs, market fit, value propositions.',

'roles': 'The response focuses on team roles, responsibilities, ownership, handoffs, and collaboration patterns.',

'criteria': 'The response defines success criteria, acceptance conditions, or tests that determine when something is complete.',

'strategy': 'The response focuses on strategic positioning, competitive advantage, evolution, or long-term direction.',
```

#### New Method Values (5 total)

```python
# lib/axisConfig.py - method axis additions

'depends': 'The response traces dependency relationships, identifying what depends on what and the nature of those dependencies.',

'independent': 'The response examines how elements remain independent, decoupled, or orthogonal despite proximity.',

'cochange': 'The response applies cochange analysis to identify temporal coupling and coordinated modification patterns.',

'split': 'The response separates mixed content into distinct sections or categories with clear boundaries.',

'merge': 'The response combines multiple sources into a single coherent whole while preserving essential information.',
```

#### Retired Method Values

```python
# method=probe is retired - now a universal task type (probe)
```

#### New Form Values (2 total)

```python
# lib/axisConfig.py - form axis additions

'questions': 'The response presents the answer as a series of probing or clarifying questions rather than statements.',

'wardley': 'The response expresses the answer as a Wardley Map showing value chain evolution from genesis to commodity.',
```

---

## Migration Mapping: Current → Universal

### EXTRACT Tasks (16 retired)

| Current Task | Universal Replacement | Notes |
|--------------|----------------------|-------|
| assumption | pull + scope=assumptions | |
| undefined | pull + scope=terminology | |
| relevant | pull + scope=focus | Already covered by existing axes |
| misunderstood | pull + scope=gaps | |
| risky | pull + scope=risks | |
| pain | pull + scope=pain | |
| metrics | pull + scope=metrics | |
| dependency | pull + scope=relations + method=depends | |
| unknown | make + scope=unknowns | Creates hypothetical unknowns |

### EXPLAIN Tasks (10 retired)

| Current Task | Universal Replacement | Notes |
|--------------|----------------------|-------|
| describe | show | Fully covered by base task |
| who | show + scope=actors | |
| what | show + scope=focus | Already covered |
| when | show + scope=timing | |
| where | show + scope=bound | Use existing scope |
| why | show + scope=rationale | |
| interact | show + scope=relations + scope=dynamics | Already covered |
| dependent | show + scope=relations + method=depends | |
| independent | show + scope=relations + method=independent | Or use method=orthogonal |
| parallel | probe + scope=relations + scope=concurrency | |

### ANALYZE Tasks (10 retired)

| Current Task | Universal Replacement | Notes |
|--------------|----------------------|-------|
| knowledge | probe + scope=disciplines | |
| objectivity | check + scope=objectivity | |
| jobs | probe + scope=jobs | |
| value | probe + scope=value | |
| operations | sort + scope=operations | Classifies to OR category |
| cochange | probe + method=cochange | |
| jim | probe + scope=connascence | |
| domain | probe + scope=domains + method=cluster | |
| retro | probe + method=reflection | Or method=wasinawa |

### TRANSFORM Tasks (6 retired)

| Current Task | Universal Replacement | Notes |
|--------------|----------------------|-------|
| split | fix + method=split | Or method=structure |
| match | fix + method=rewrite | Already covered |
| blend | fix + method=merge | Or method=meld |
| join | fix + method=merge | Or method=meld |
| context | fix + method=contextualise | Already covered |
| todo | fix + form=checklist + scope=actions | Already covered |

### CLASSIFY Tasks (3 retired)

| Current Task | Universal Replacement | Notes |
|--------------|----------------------|-------|
| tao | sort + scope=taoism | |
| taste | check + scope=aesthetics | Evaluates quality |
| document | sort + scope=formats + method=compare | |

### COMPARE Tasks (2 retired)

| Current Task | Universal Replacement | Notes |
|--------------|----------------------|-------|
| challenge | make + form=questions + scope=challenges | Or method=adversarial |
| critique | check + scope=failures + method=adversarial | |

### RECOMMEND Tasks (2 retired)

| Current Task | Universal Replacement | Notes |
|--------------|----------------------|-------|
| easier | pick + scope=simpler | |
| product | probe + scope=product | |

### PLAN Tasks (3 retired)

| Current Task | Universal Replacement | Notes |
|--------------|----------------------|-------|
| team | plan + scope=roles + method=mapping | |
| done | make + scope=criteria + form=checklist | |
| wardley | make + form=wardley | Or probe + scope=strategy |

### VERIFY Tasks (1 retired)

| Current Task | Universal Replacement | Notes |
|--------------|----------------------|-------|
| true | check | Fully covered by base task |

**Total:** 46 retired, 10 added = **10 task tokens total** (down from 46)

---

## Implementation Plan

### Phase 1: Add Universal Tasks and New Axis Values

1. **Update lib/staticPromptConfig.py**
   - Add 10 universal task definitions
   - Keep "fix" task
   - Remove all 45 specialized tasks

2. **Update lib/axisConfig.py**
   - Add 31 new scope values
   - Add 5 new method values
   - Add 2 new form values

3. **Regenerate artifacts**
   ```bash
   make axis-regenerate
   make axis-regenerate-apply
   python3 -m prompts.export --output build/prompt-grammar.json \
     --embed-path internal/barcli/embed/prompt-grammar.json
   ```

4. **Update documentation**
   - Update GPT/readme.md with new tokens (alphabetically)
   - Create migration guide in docs/MIGRATION-0088.md
   - Update examples to use universal tasks

5. **Rebuild bar CLI**
   ```bash
   cd cmd/bar && go build && cd ../..
   ```

### Phase 2: Testing and Validation

1. **Shuffle validation**
   ```bash
   # Test all universal tasks appear
   for task in make fix pull sort diff show probe pick plan check; do
     ./bar shuffle --include static --fill 1.0 --seed $(shuf -i 1-1000 -n 1) | grep -q "$task" && echo "✓ $task" || echo "✗ $task MISSING"
   done

   # Test new scope values appear
   for scope in assumptions risks metrics jobs value; do
     ./bar shuffle --include scope --fill 1.0 --seed $(shuf -i 1-1000 -n 1) | grep -q "$scope" && echo "✓ $scope" || echo "✗ $scope MISSING"
   done
   ```

2. **Run ci-guardrails**
   ```bash
   make ci-guardrails
   ```

3. **Manual testing of equivalences**
   ```bash
   # Old: assumption
   echo "What assumptions underlie microservices?" | ./bar build assumption

   # New: pull + scope=assumptions
   echo "What assumptions underlie microservices?" | ./bar build pull scope=assumptions

   # Old: jobs
   echo "JTBD for project management tools" | ./bar build jobs

   # New: probe + scope=jobs
   echo "JTBD for project management tools" | ./bar build probe scope=jobs

   # Old: wardley
   echo "Value chain for SaaS analytics" | ./bar build wardley

   # New: make + form=wardley
   echo "Value chain for SaaS analytics" | ./bar build make form=wardley
   ```

4. **Test coverage**
   - Update _tests/test_talon_settings_model_prompt.py for new task catalog
   - Add tests for new scope/method/form values
   - Verify migration mappings in tests

### Phase 3: Documentation and Migration Support

1. **Create migration guide**
   - Document each old task → new combination mapping
   - Provide examples for common use cases
   - Explain the universal task model

2. **Update README examples**
   - Replace specialized tasks with universal equivalents
   - Show how to combine task + scope + method
   - Add "Common Patterns" section

3. **Add deprecation warnings** (optional)
   - If we want a transition period, detect old tokens and suggest new ones
   - Could be implemented in bar CLI or as a linting tool

---

## Consequences

### Positive

1. **Dramatically reduced cognitive load**: 10 tasks vs 46 (78% reduction)
2. **Voice-optimized**: All task tokens are single-syllable and pronounceable
3. **Clearer success criteria**: Each task type has unambiguous evaluation test
4. **Better composability**: Task type + scope + method = precise intent
5. **Easier to extend**: Adding new scopes doesn't require new tasks
6. **Consistent granularity**: All tasks are universal primitives
7. **Separation of concerns**: Task (what success is) vs scope (subject matter) vs method (how to think)
8. **Self-documenting**: "pull scope=assumptions" is clearer than "assumption"

### Tradeoffs

1. **Multi-token expressions**: `pull scope=assumptions` vs single `assumption` token
   - **Mitigation**: More explicit, easier to understand once learned
   - **Benefit**: Composition reveals structure (pull vs probe)
   - **Voice advantage**: Single-syllable tasks are faster to say

2. **Breaking change**: All 46 specialized tasks retired
   - **Mitigation**: Comprehensive migration guide with 1:1 mappings
   - **Benefit**: Clean break prevents accumulation of legacy tokens

3. **More axis values**: +36 new values across scope/method/form (28 scope, 5 method, 2 form, 1 retired method)
   - **Mitigation**: Well-organized, discoverable through categories
   - **Benefit**: Axis values are reusable across tasks

4. **User re-learning**: Existing users must learn new patterns
   - **Mitigation**: Migration guide, examples, deprecation warnings
   - **Benefit**: Simpler mental model in long run

### Risks

1. **Some nuance may be lost**: Highly specialized tasks (connascence, JTBD, Wardley) become combinations
   - **Mitigation**: Scope values preserve specificity (scope=connascence, scope=jtbd)
   - **Response**: Combination is more honest (analyze connascence vs "jim" which obscures operation)

2. **Longer token strings**: Multiple tokens vs single specialized token
   - **Mitigation**: Bar CLI supports multi-token expressions naturally
   - **Response**: Explicitness aids understanding and debugging

3. **Migration friction**: Users must update existing workflows
   - **Mitigation**: Provide automated migration script
   - **Response**: One-time cost for long-term simplicity

---

## Validation Criteria

### Success Metrics

- [ ] All 10 universal tasks defined and documented (all single-syllable)
- [ ] All 36 new axis values added (28 scope, 5 method, 2 form, 1 method retired)
- [ ] All 46 specialized tasks removed from catalog
- [ ] Migration guide covers all 46 retired tasks
- [ ] README updated with universal task examples
- [ ] All tests pass (make ci-guardrails)
- [ ] Shuffle generates valid combinations for all universal tasks
- [ ] Manual equivalence testing confirms migrations work

### Acceptance Tests

1. Generate a prompt using each universal task type
2. Generate a prompt using each new scope value
3. Verify each retired task has a documented migration path
4. Confirm no regression in existing test suite
5. User testing: Can new users understand universal tasks without seeing old catalog?

---

## References

- "Framing the idea.md" - 10 universal task types proposal
- ADR 0083: Prompt Key Refinement (task defines success principle)
- ADR 0086: Catalog Refinements (retired "infer" for similar reasons)
- ADR 0087: Add improve/optimize method (token addition pattern)
- tmp/task-taxonomy-rehoming.md - detailed migration analysis

---

## Appendices

### Appendix A: Why Not Keep Specialized Tasks?

**Option considered**: Keep specialized tasks like "jobs", "wardley", "jim" as convenience shortcuts.

**Rejected because**:
1. Creates two parallel systems (universal + specialized) increasing cognitive load
2. Unclear when to use shortcut vs composition ("jobs" vs "analyze scope=jtbd")
3. Precedent for unbounded growth (every framework becomes a task)
4. Obscures the universal structure (users don't learn composition)
5. Conflicts with "task defines success" principle (JTBD is a scope, not a success type)

**Better solution**: Document common patterns in README:
```bash
# Jobs To Be Done analysis
bar build probe scope=jobs method=analysis form=bullets

# Wardley mapping
bar build make form=wardley scope=strategy

# Connascence analysis
bar build probe scope=connascence method=rigor
```

### Appendix B: Full Token Count Comparison

**Before ADR 0088:**
- Tasks: 46
- Scope: 10
- Method: 53 (including method=probe)
- Form: 24
- Total combinatorial space: ~290,640 combinations

**After ADR 0088:**
- Tasks: 10 (all single-syllable universal)
- Scope: 38 (10 existing + 28 new)
- Method: 57 (53 - 1 retired probe + 5 new)
- Form: 26 (24 + 2 new)
- Total combinatorial space: ~564,564 combinations

**Analysis**: 78% fewer top-level tasks, but vastly more expressive power through composition. All task tokens are single-syllable and voice-optimized. The increase in scope/method/form values preserves specialized functionality while maintaining universal task structure.

### Appendix C: Open Questions

1. Should form=wardley exist or is form=diagram + scope=strategy sufficient?
   - **Current decision**: Include form=wardley for specificity (Wardley has unique structure)
   - **Alternative**: Use form=diagram; but may lose Wardley-specific conventions

2. Should method=probe be fully retired or kept as a method alongside task=probe?
   - **Current decision**: Retire method=probe to avoid confusion (probe is now exclusively a task)
   - **Alternative**: Keep both; but creates ambiguity in "probe scope=foo" (task) vs "show method=probe scope=foo"

**Resolution approach**: Implement as proposed, gather usage data in next shuffle cycle (ADR 0085 process), refine based on evidence.
