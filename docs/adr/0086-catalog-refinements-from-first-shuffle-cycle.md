# ADR 0086: Catalog Refinements from First Shuffle Cycle

## Status

Proposed

## Context

ADR 0085 established a shuffle-driven refinement process for systematically evaluating the prompt catalog. The first refinement cycle (Loop 4) evaluated 20 randomly generated prompts and identified several catalog quality issues:

**High-Severity Issues (2):**
1. The "infer" static task contradicts ADR 0083's principle that "task defines success"
2. Intent + persona preset combinations create ambiguity (e.g., "coach" intent + "scientist_to_analyst" preset)

**Medium-Severity Issues (6):**
3. Directional descriptions use vague language ("synthesized lens", "fused stance") without operational clarity
4. Compound directionals (fig, fog, rog, bog, dig, dip, fip) are hard to distinguish
5. Tone + audience combinations can conflict (e.g., "casually" to "CEO")

**Evidence:** See `docs/adr/evidence/0085/recommendations.yaml` with seeds demonstrating each issue.

These findings represent systematic catalog debt that reduces prompt clarity and user confidence in token selection.

---

## Decision

Apply the following catalog edits based on first refinement cycle evidence:

### 1. Retire "infer" Static Task (High Priority)

**Current:**
```python
STATIC_PROMPTS = {
    "infer": "The response infers the task without being told what to do."
}
```

**Issue:** This contradicts ADR 0083's core principle: "TASK: The primary action to perform. This defines success." If the task is to infer, that's a meta-task that should be stated explicitly.

**Decision:** **RETIRE** the "infer" token.

**Rationale:**
- Violates the prompt key's foundational contract
- Creates confusion about what "success" means
- Users selecting "infer" want the LLM to propose a task, which should be explicit: "The response proposes what task would be most valuable for this subject, then executes that task"
- Evidence: seed_1 produced ambiguous output

**Migration:**
- Remove from `lib/promptConfig.py`
- Add deprecation note if needed for backwards compatibility
- Suggest users explicitly state "propose and execute a task" in subject text instead

---

### 2. Document Intent/Preset Interaction Constraints (High Priority)

**Current behavior:** Intent can be freely combined with persona presets, leading to contradictory stances.

**Issue:** Persona presets have implicit intents. Example:
- `scientist_to_analyst` preset implies "inform/explain" intent
- Adding `coach` intent creates ambiguity: should I inform (preset) or coach (intent)?
- Evidence: seed_20 combined these, producing confused output

**Decision:** Add validation and documentation for intent + preset combinations.

**Implementation:**

```python
# lib/personaConfig.py

# Document preset implicit intents
PERSONA_PRESET_IMPLICIT_INTENTS = {
    "peer_engineer_explanation": "inform",
    "teach_junior_dev": "coach",  # coaching is inherent
    "scientist_to_analyst": "inform",
    "stakeholder_facilitator": "inform",
    "designer_to_pm": "inform",
    "product_manager_to_team": "guide",
    "executive_brief": "inform",
    "fun_mode": "entertain",  # entertainment is inherent
}

# Document compatible intent + preset combinations
INTENT_PRESET_COMPATIBILITY = {
    "coach": {
        "compatible": ["peer_engineer_explanation"],  # can add coaching flavor
        "redundant": ["teach_junior_dev"],  # already has coaching
        "conflicts": ["scientist_to_analyst", "executive_brief"],  # informational focus
    },
    "entertain": {
        "compatible": [],  # rarely compatible with professional presets
        "redundant": ["fun_mode"],  # already entertaining
        "conflicts": ["scientist_to_analyst", "executive_brief", "stakeholder_facilitator"],
    },
}
```

**User guidance:** Add to TUI2 and documentation:
> "When using a persona preset, the intent is usually implicit. Adding an explicit intent is only recommended when you want to shift the preset's default purpose. Avoid combinations like 'coach' + 'scientist_to_analyst' (informational) or 'entertain' + 'executive_brief' (serious)."

---

### 3. Clarify Directional Descriptions (Medium Priority)

**Current problem:** Many directionals use similar abstract language:
- "synthesized lens" (fig)
- "fused stance" (fog, bog)
- "unified perspective" (multiple)

Users cannot distinguish operational differences.

**Decision:** Rewrite directional descriptions with concrete, operational language.

**Proposed rewrites:**

```python
# lib/axisConfig.py - DIRECTIONAL axis

DIRECTIONAL = {
    # Simple directionals (keep as-is)
    "act": "The response provides actionable steps or procedures.",
    "dig": "The response examines concrete details and grounding examples.",

    # Compound directionals (clarify)
    "fig": {
        "old": "The response applies an abstracting-generalizing-concretizing-grounding perspective as a single synthesized lens on the preceding prompt.",
        "new": "The response alternates between abstract principles and concrete examples, using each to illuminate the other (figure-ground reversal).",
        "rationale": "Users need operational definition of how abstraction and concretization interact"
    },

    "fog": {
        "old": "The response frames the preceding prompt through one unified perspective that blends reflection, structure, acting, and extending, treating them as a single fused stance.",
        "new": "The response creates a framework (structure), demonstrates it in action (acting), reflects on what works, then extends to related applications.",
        "rationale": "Need sequential operational flow instead of 'fused stance' abstraction"
    },

    "rog": {
        "old": "The response applies a reflective-structural perspective as a single synthesized lens on the preceding prompt.",
        "new": "The response examines the structure of the subject (how it's organized), then reflects on why that structure exists and what it reveals.",
        "rationale": "Distinguish from 'analytical' method; emphasize structure-first then reflection"
    },

    "bog": {
        "old": "The response frames the preceding prompt through one unified perspective that blends acting, extending, reflection, and structure, treating them as a single fused stance.",
        "new": "The response starts with concrete action steps (bogging down into details), identifies patterns through reflection, then extends insights to related contexts.",
        "rationale": "Action-first lens distinct from fog's framework-first approach"
    },

    # Compound variants (dip/fip combinations)
    "dip bog": {
        "old": "The response frames the preceding prompt through one unified perspective that blends concreteness, grounding, acting, and extending, treating them as a single fused stance.",
        "new": "The response grounds the subject in concrete examples, works through action steps, then extends the pattern to similar cases.",
        "rationale": "Concrete → action → extend sequence"
    },

    "fip rog": {
        "old": "The response frames the preceding prompt through one unified perspective that blends abstraction, generalization, concreteness, grounding, reflection, and structure, treating them as a single fused stance.",
        "new": "The response analyzes the subject's structure at multiple levels (concrete to abstract), reflecting on how each level illuminates the others.",
        "rationale": "Multi-level structural analysis with reflection"
    },
}
```

**Key changes:**
- Replace "synthesized lens" / "fused stance" with sequential operational steps
- Use verbs describing what the response does (alternates, creates, examines, starts)
- Distinguish each directional's starting point and flow

---

### 4. Add Tone/Audience Compatibility Guidance (Medium Priority)

**Issue:** Some tone + audience combinations are contradictory.
- Evidence: seed_16 combined "casually" (tone) with "to CEO" (audience)
- Result: Tonal mismatch (CEOs expect professional communication)

**Decision:** Document tone/audience compatibility matrix.

**Implementation:**

```python
# lib/personaConfig.py or documentation

TONE_AUDIENCE_GUIDANCE = """
Tone and audience are independent axes, but some combinations create friction:

COMPATIBLE COMBINATIONS:
- "directly" works with all audiences (neutral)
- "kindly" works well with "to junior engineer", "to team"
- "formally" works well with "to CEO", "to stakeholders"
- "casually" works well with "to programmer", "to team"

POTENTIAL CONFLICTS:
- "casually" + "to CEO" → CEOs expect professional tone even if friendly
- "formally" + "to junior engineer" → May create distance that hinders learning
- "bluntly" + "to stakeholders" → May damage relationships

RECOMMENDATIONS:
- Match tone to audience expectations and context
- When in doubt, "directly" is the safe neutral choice
- Consider relationship dynamics (peer vs authority vs learner)
"""
```

**TUI2 guidance:** Show hint when conflicting tone/audience selected:
> "Note: 'casually' to 'CEO' may conflict. Consider 'directly' for professional contexts."

---

### 5. Document Constraint Combination Patterns (Low Priority)

**Issue:** Some constraint combinations work against each other:
- "gist" (short) + "max" (exhaustive) = contradiction
- "edges" (edge cases) + "narrow" (single focus) = tension
- "recipe" + "gherkin" = redundant structured formats

**Decision:** Add constraint compatibility documentation.

**Implementation:**

Create `docs/constraint-combinations.md`:

```markdown
# Constraint Combination Patterns

## Contradictory Combinations

Avoid these combinations as they create conflicting instructions:

| Constraint 1 | Constraint 2 | Conflict | Recommendation |
|--------------|--------------|----------|----------------|
| gist (short) | max (exhaustive) | Length conflict | Choose one based on priority |
| minimal | full | Coverage conflict | Choose one based on scope |
| narrow (single focus) | edges (boundary cases) | Scope conflict | Use 'bound' (specific boundaries) instead |
| recipe | gherkin | Both define format | Choose one structured format |
| tight | outline | Detail level conflict | Choose based on desired depth |

## Complementary Combinations

These combinations reinforce each other:

- **focus + narrow**: Both emphasize single-item specificity
- **edges + bound**: Both deal with boundaries (unusual vs limits)
- **skim + gist**: Both favor brevity
- **max + full**: Both favor completeness
- **dynamics + relations**: Both examine interactions

## Method + Form Synergies

Some methods pair naturally with certain forms:

- **systemic** (systems thinking) + **diagram**: Visual systems
- **cocreate** (collaborative) + **dialogue**: Back-and-forth format
- **tradeoffs** + **table**: Comparison structure
- **tune** (parameter exploration) + **matrix**: Parameter space

## Shuffle Recommendations

When `bar shuffle` generates conflicting constraints:
1. Check this compatibility guide
2. Regenerate with adjusted `--exclude` if needed
3. Manually adjust tokens for better harmony
```

---

### 6. Investigation: Consolidate Compound Directionals (Future Work)

**Issue:** 7+ compound directionals (fig, fog, rog, bog, dig, dip, fip variants) are hard to distinguish.

**Decision:** **Defer to ADR 0087** pending deeper investigation.

**Investigation plan:**
1. Generate 20 shuffles with `--include directional --fill 1.0`
2. Compare outputs for fig vs fog vs rog vs bog
3. Measure user comprehension (survey or user testing)
4. Decide which directionals to retire/merge

**Hypothesis:** Can consolidate to 3-4 core patterns:
- **act** (action-oriented)
- **dig** (concrete details)
- **fig** (abstract ↔ concrete alternation)
- **rog** (structure + reflection)

Evidence requirement: 3+ evaluators agreeing outputs are indistinguishable before retiring.

---

## Implementation

### Phase 1: High Priority (Immediate)

1. **Retire "infer"**
   - Remove from `lib/promptConfig.py`
   - Regenerate grammar: `python scripts/export_prompt_grammar.py`
   - Update tests
   - Add migration note in CHANGELOG

2. **Add intent/preset validation**
   - Add compatibility matrix to `lib/personaConfig.py`
   - Update TUI2 to show warnings
   - Document in help text

### Phase 2: Medium Priority (Next Sprint)

3. **Rewrite directional descriptions**
   - Update `lib/axisConfig.py` with new operational descriptions
   - Regenerate grammar
   - Update documentation

4. **Add tone/audience guidance**
   - Document compatibility in `lib/personaConfig.py`
   - Add TUI2 hints for conflicting combinations

### Phase 3: Low Priority (Background)

5. **Document constraint patterns**
   - Create `docs/constraint-combinations.md`
   - Link from main README
   - Reference in shuffle documentation

6. **Plan directional consolidation investigation**
   - Create ADR 0087 for investigation plan
   - Execute investigation cycle per ADR 0085 process

---

## Consequences

### Positive

- Catalog quality improves systematically
- User confidence in token selection increases
- Contradictory combinations prevented
- Clearer operational guidance for complex tokens
- Evidence-based changes (not arbitrary)

### Tradeoffs

- "infer" retirement may break existing workflows (mitigation: document migration)
- Intent/preset validation adds complexity (mitigation: make warnings, not errors)
- Directional rewrites require user re-learning (mitigation: keep old descriptions in CHANGELOG)

### Risks

- Users may disagree with specific descriptions (mitigation: iterate based on feedback)
- Validation logic may be too restrictive (mitigation: warnings not blocking errors)
- Consolidating directionals may remove nuance (mitigation: require strong evidence)

---

## Validation

### Phase 1 Validation

```bash
# Verify "infer" removed
grep -r "infer" lib/promptConfig.py && echo "ERROR: infer still present" || echo "OK: infer retired"

# Verify grammar regenerated
python scripts/export_prompt_grammar.py
jq '.static_prompts.profiles | has("infer")' prompt_grammar.json
# Should output: false

# Test intent/preset validation
go test ./internal/barcli/... -run TestPersonaIntentValidation
```

### Phase 2 Validation

```bash
# Generate test shuffles with new directionals
for seed in 1 5 9 14 20; do
  echo "=== Seed $seed with new descriptions ==="
  ./bar shuffle --seed $seed | grep -A10 "DIRECTIONAL"
done

# Compare clarity vs old descriptions
diff -u <(git show HEAD~1:lib/axisConfig.py | grep -A5 '"fig":') \
        <(cat lib/axisConfig.py | grep -A5 '"fig":')
```

### Regression Testing

```bash
# Re-run original problematic seeds
./bar shuffle --seed 1   # Should no longer use "infer"
./bar shuffle --seed 16  # Should show tone/audience hint
./bar shuffle --seed 20  # Should show intent/preset hint

# Verify improvements via second refinement cycle
./scripts/shuffle_corpus.sh --count 20 --seed-start 100
# Evaluate seeds 100-119 and compare issue rate vs original 40%
```

---

## References

- ADR 0083: Prompt Key Refinement (defines TASK precedence)
- ADR 0085: Shuffle-Driven Catalog Refinement (established process)
- Evidence: `docs/adr/evidence/0085/recommendations.yaml`
- Seeds demonstrating issues: 1, 5, 7, 9, 14, 16, 18, 20

---

## Success Metrics

**Target after implementation:**
- Issue rate in shuffle evaluations drops from 40% (8/20 seeds) to <20%
- User-reported catalog confusion issues decrease
- Persona preset + intent combinations have clear guidance
- Directional descriptions score >4.0 on clarity (1-5 scale)

**Measurement:**
- Run second refinement cycle (ADR 0085 Loop 5+)
- Compare issue rates and severity distributions
- Track user feedback on directional clarity
