# ADR 0085: Shuffle-Driven Catalog Refinement

## Status

Accepted

## Context

The prompt catalog (static prompts, axes, personas, directionals) has grown organically. While ADR 0083 established a clearer prompt key with precedence rules and boundary clarifications, we lack a systematic process to validate that individual catalog entries actually produce outputs aligned with their stated purpose.

Problems we may encounter:

- **Ambiguous tokens**: Descriptions that sound distinct but produce overlapping or indistinguishable outputs
- **Misaligned categories**: Tokens placed in wrong axes (e.g., a "method" that behaves more like "form")
- **Redundant entries**: Multiple tokens that produce effectively identical results
- **Missing coverage**: Gaps where useful combinations aren't representable
- **Conflicting combinations**: Token pairings that produce incoherent or contradictory prompts

The `bar shuffle` command (ADR 0084) provides a mechanism to generate random prompt combinations, enabling systematic exploration of the catalog's behavior.

---

## Decision

Establish a shuffle-driven refinement process that uses randomized prompt generation to evaluate catalog quality and produce actionable recommendations.

### Process Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Generate       │────▶│  Evaluate        │────▶│  Meta-Evaluate   │────▶│  Recommend      │
│  (bar shuffle)  │     │  (vs prompt key) │     │  (vs bar skills) │     │  (catalog edit) │
└─────────────────┘     └──────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │                        │
         ▼                       ▼                        ▼                        ▼
   N random prompts      Alignment score +        Skill feedback +        Retire / Edit /
   with --seed           qualitative notes        catalog gaps           Recategorize / Add
```

### Phase 1: Generation

Generate a corpus of shuffled prompts for evaluation:

```bash
# Generate 50 prompts with reproducible seeds
for seed in $(seq 1 50); do
  bar shuffle --seed $seed --json > corpus/shuffle_$seed.json
done

# Generate category-focused samples
bar shuffle --seed 100 --include static,method --exclude persona_preset
bar shuffle --seed 101 --include directional --fill 1.0
bar shuffle --seed 102 --include persona_preset --fill 0.0
```

**Sampling strategy:**
- Broad sweep: 30-50 fully random shuffles (`--fill 0.5`)
- Category deep-dives: 10-20 per axis with `--include` forcing selection
- Edge cases: Low-fill (`--fill 0.1`) and high-fill (`--fill 0.9`) extremes

### Phase 2: Evaluation

For each generated prompt, evaluate against the prompt key (ADR 0083):

| Criterion | Question |
|-----------|----------|
| **Task clarity** | Does the static prompt clearly define what success looks like? |
| **Constraint independence** | Do constraints shape HOW without redefining WHAT? |
| **Persona coherence** | Does the persona stance make sense for this task? |
| **Category alignment** | Is each token doing the job of its stated category? |
| **Combination harmony** | Do the selected tokens work together or fight? |

**Scoring rubric:**

- **5 - Excellent**: Prompt is clear, coherent, and tokens reinforce each other
- **4 - Good**: Minor rough edges but intent is clear
- **3 - Acceptable**: Usable but some tokens feel forced or redundant
- **2 - Problematic**: Confusion about intent or category overlap
- **1 - Broken**: Contradictory, nonsensical, or misleading combination

#### Phase 2b: Meta-Evaluation Against Bar Skills

After evaluating prompts against the prompt key, perform a secondary evaluation by checking them against the bar skills themselves (bar-autopilot, bar-manual, bar-workflow, bar-suggest). This meta-evaluation serves dual purposes:

**Purpose 1: Validate skill guidance quality**
- Are the skill instructions clear enough to select appropriate tokens for this prompt?
- Do the token selection heuristics in the skills lead to this combination?
- Would the skills' "Usage Patterns by Task Type" suggest this combination?
- Are there contradictions between what the skills recommend and what shuffle generated?

**Purpose 2: Discover catalog gaps/issues**
- Does this shuffle reveal tokens that aren't well-documented in the skills?
- Are there method/scope/form combinations that the skills don't cover?
- Would a user following skill guidance be able to construct this prompt?
- Does this combination highlight missing categorization in skill heuristics?

**Evaluation questions:**

| Criterion | Question |
|-----------|----------|
| **Skill discoverability** | Would the skills guide a user to select these tokens for a relevant use case? |
| **Heuristic alignment** | Do the skills' token selection heuristics explain this combination? |
| **Documentation completeness** | Are all tokens in this prompt documented in the skills' token catalog sections? |
| **Pattern coverage** | Does this combination fit any "Usage Patterns by Task Type" examples? |
| **Guidance clarity** | If the skills were updated to cover this combination, what would need to change? |

#### Phase 2c: Evaluate `bar help llm` as Reference Tool

After evaluating against skills, assess whether `bar help llm` provides adequate reference documentation for the skills to work with this prompt combination:

**Purpose:** Evaluate the utility of `bar help llm` as the primary reference that skills point to

**Evaluation questions:**

| Criterion | Question |
|-----------|----------|
| **Cheat sheet utility** | Does the Token Quick Reference cheat sheet make all tokens in this combination easily discoverable? |
| **Description clarity** | Are the token descriptions in the detailed catalog clear enough to explain this combination? |
| **Selection guidance** | Do the "Token Selection Heuristics" in `bar help llm` help explain why these tokens work together? |
| **Pattern examples** | Do the "Usage Patterns by Task Type" examples illustrate similar combinations? |
| **Reference completeness** | Would someone consulting only `bar help llm` understand what this prompt will do? |

**Scoring rubric:**

- **5 - Excellent**: `bar help llm` fully explains this combination; skills can confidently use it as reference
- **4 - Good**: Minor gaps but reference provides enough context to understand the combination
- **3 - Acceptable**: Reference provides basic info but requires external knowledge to fully understand
- **2 - Problematic**: Significant gaps in reference; skills would struggle to explain this combination
- **1 - Broken**: Reference doesn't adequately document these tokens or how they work together

**Feedback capture:**

For each shuffled prompt, document:

```markdown
### Meta-Evaluation vs Bar Skills

**Skill alignment score:** {1-5}
- 5: Skills would clearly recommend this combination
- 4: Skills provide hints but not explicit guidance
- 3: Skills are neutral/silent on this combination
- 2: Skills guidance contradicts this combination
- 1: Skills would actively discourage this combination

**Skill gaps identified:**
- [ ] Token {X} not documented in skill catalog sections
- [ ] Method category {Y} missing from skill heuristics
- [ ] Combination pattern not covered in "Usage Patterns"
- [ ] Skill guidance contradicts shuffle result (explain why)

**Recommendations for skills:**
- Update bar-{skill-name} § "{section}" to include {specific guidance}
- Add new usage pattern example for {task type}
- Clarify token selection heuristics for {axis}

**Recommendations for catalog:**
- Token {X} description unclear (skills can't explain it)
- Category misalignment detected (skills categorize differently)
- Combination produces incoherent result (skills should warn against it)
```

**Feedback for `bar help llm`:**

```markdown
### Bar Help LLM Reference Evaluation

**Reference utility score:** {1-5}
- 5: Reference fully supports skills for this combination
- 4: Reference mostly adequate with minor gaps
- 3: Reference provides basics but limited guidance
- 2: Reference has significant gaps for this combination
- 1: Reference inadequate for understanding this combination

**Help documentation gaps identified:**
- [ ] Token {X} description too vague in detailed catalog
- [ ] Cheat sheet hard to scan for {axis} tokens
- [ ] Heuristics section missing guidance for {method category} + {scope category}
- [ ] Usage patterns lack examples for {task type}
- [ ] Composition rules don't explain {incompatibility or constraint}

**Recommendations for bar help llm:**
- Update § "Token Catalog" § "{axis}" to clarify {token} description
- Add example to § "Usage Patterns by Task Type" for {scenario}
- Expand § "Token Selection Heuristics" § "{section}" to cover {case}
- Improve § "Composition Rules" to explain {constraint}
```

**Output artifacts:**
- `docs/adr/evidence/0085/skill-feedback.md` - Aggregated skill improvement recommendations
- `docs/adr/evidence/0085/catalog-feedback.md` - Catalog issues discovered via skill validation
- `docs/adr/evidence/0085/help-llm-feedback.md` - `bar help llm` documentation gaps and improvements

### Phase 3: Recommendation

Based on evaluation, categorize findings into actions:

#### Retire
Token produces consistently low scores or is indistinguishable from another.

```yaml
action: retire
token: "systemic"
axis: method
reason: "Overlaps significantly with 'analytical'; users can't distinguish output"
evidence: [seed_12, seed_34, seed_45]
```

#### Edit
Token concept is valuable but description needs refinement.

```yaml
action: edit
token: "focus"
axis: scope
current: "The response stays within the selected target."
proposed: "The response addresses only the specific item named, excluding related items."
reason: "Current description too vague; users unsure what 'target' means"
evidence: [seed_7, seed_22]
```

#### Recategorize
Token is in wrong axis.

```yaml
action: recategorize
token: "tight"
from_axis: form
to_axis: completeness
reason: "'Tight' controls depth/verbosity more than structure"
evidence: [seed_15, seed_31]
```

#### Add
Gap identified where no token covers a needed concept.

```yaml
action: add
axis: directional
proposed_token: "contrarian"
proposed_description: "The response challenges assumptions and argues against the obvious interpretation."
reason: "No existing directional for critical/skeptical lens"
evidence: [seed_8, seed_19]  # prompts where this would have helped
```

### Evaluation Template

For each shuffled prompt, capture:

```markdown
## Seed: {N}

**Tokens selected:**
- static: {token}
- completeness: {token}
- scope: {token}
- method: {token}
- directional: {token}
- persona: {preset or axes}

**Generated prompt preview:**
> {first 200 chars of rendered prompt}

**Scores (vs Prompt Key):**
- Task clarity: {1-5}
- Constraint independence: {1-5}
- Persona coherence: {1-5}
- Category alignment: {1-5}
- Combination harmony: {1-5}
- **Overall**: {1-5}

**Meta-Evaluation (vs Bar Skills):**
- Skill alignment: {1-5}
- Skill discoverability: {1-5}
- Heuristic coverage: {1-5}
- Documentation completeness: {1-5}
- **Meta overall**: {1-5}

**Bar Help LLM Reference Evaluation:**
- Cheat sheet utility: {1-5}
- Description clarity: {1-5}
- Selection guidance: {1-5}
- Pattern examples: {1-5}
- **Reference overall**: {1-5}

**Notes:**
{Qualitative observations, specific concerns, token interactions}

**Skill Feedback:**
- [ ] Skill gap: {which skill} § {section} needs {what}
- [ ] Catalog issue: {token} description unclear to skills

**Help LLM Feedback:**
- [ ] Help gap: bar help llm § {section} needs {what}
- [ ] Reference issue: {token or combination} inadequately documented

**Recommendations:**
- [ ] {action}: {token} - {brief reason}
```

### Output Artifacts

The refinement cycle produces:

1. **Evaluation corpus**: `docs/adr/evidence/0085/evaluations/`
2. **Recommendations list**: `docs/adr/evidence/0085/recommendations.yaml`
3. **Skill feedback**: `docs/adr/evidence/0085/skill-feedback.md` - Aggregated improvements for bar skills
4. **Help LLM feedback**: `docs/adr/evidence/0085/help-llm-feedback.md` - `bar help llm` documentation gaps
5. **Catalog feedback**: `docs/adr/evidence/0085/catalog-feedback.md` - Catalog issues discovered via skill validation
6. **Changelog draft**: Proposed edits to `lib/promptConfig.py` and related files
7. **Grammar regeneration**: Updated `prompt_grammar.json` after changes

---

## Implementation

### Refinement Cycle

Run this process periodically or when catalog drift is suspected:

1. **Generate**: Create 50+ shuffled prompts across sampling strategies
2. **Evaluate**: Score each against prompt key rubric, capture notes
3. **Meta-Evaluate Skills**: Score each against bar skills, identify skill gaps and catalog issues
4. **Meta-Evaluate Reference**: Score `bar help llm` utility for each prompt, identify documentation gaps
5. **Aggregate**: Group low-scoring tokens, identify patterns, collect feedback for skills/catalog/help
6. **Recommend**: Produce actionable list with evidence for catalog, skills, and help documentation
7. **Review**: Human review of recommendations before implementing
8. **Apply**: Edit catalog files, skill documentation, and/or help_llm.go, regenerate grammar
9. **Validate**: Re-run shuffle samples to confirm improvement

### Automation Opportunities

```bash
# Generate evaluation corpus
./scripts/shuffle_corpus.sh --count 50 --output docs/adr/evidence/0085/corpus/

# (Future) LLM-assisted evaluation
./scripts/evaluate_corpus.sh --corpus docs/adr/evidence/0085/corpus/ \
  --prompt-key docs/adr/0083-prompt-key-refinement.md \
  --output docs/adr/evidence/0085/evaluations/
```

### Files to Create/Modify

| File | Purpose |
|------|---------|
| `scripts/shuffle_corpus.sh` | Generate reproducible corpus |
| `docs/adr/evidence/0085/` | Evidence directory |
| `docs/adr/evidence/0085/skill-feedback.md` | Aggregated skill improvement recommendations |
| `docs/adr/evidence/0085/help-llm-feedback.md` | `bar help llm` documentation improvement recommendations |
| `docs/adr/evidence/0085/catalog-feedback.md` | Catalog issues discovered via skill validation |
| `lib/promptConfig.py` | Catalog edits (static prompts) |
| `lib/axisConfig.py` | Axes token edits |
| `lib/personaConfig.py` | Persona/intent edits |
| `internal/barcli/skills/bar-autopilot/skill.md` | Skill documentation updates |
| `internal/barcli/skills/bar-manual/skill.md` | Skill documentation updates |
| `internal/barcli/skills/bar-workflow/skill.md` | Skill documentation updates |
| `internal/barcli/skills/bar-suggest/skill.md` | Skill documentation updates |
| `.claude/skills/*/skill.md` | User-facing skill copies (sync after updates) |
| `internal/barcli/help_llm.go` | `bar help llm` reference documentation improvements |

---

## Consequences

### Positive

- Systematic process replaces ad-hoc catalog maintenance
- Evidence-based decisions with reproducible seeds
- Catches category misalignment before users encounter confusion
- Identifies redundancy and gaps proactively
- Builds institutional knowledge about what combinations work
- **Meta-evaluation creates feedback loop**: Skills improve as catalog evolves, and catalog issues surface when skills can't explain them
- **Bidirectional validation**: Catalog validates skills, skills validate catalog
- **Documentation stays synchronized**: Skill guidance stays current with catalog capabilities
- **Reference quality assurance**: `bar help llm` quality is continuously evaluated as the primary reference for skills

### Tradeoffs

- Requires human judgment for evaluation (can't fully automate)
- Initial corpus generation and evaluation is time-intensive
- May surface uncomfortable truths about beloved tokens
- Recommendations still require careful human review

### Risks

- Over-pruning: Removing tokens that are valuable in rare contexts
- Churn: Frequent changes destabilize user muscle memory
- Subjectivity: Different evaluators may score differently

**Mitigations:**
- Require multiple low scores before recommending retirement
- Batch changes into quarterly refinement cycles
- Use multiple evaluators for ambiguous cases

---

## Validation

```bash
# Verify shuffle generates diverse outputs
for i in $(seq 1 10); do
  bar shuffle --seed $i --json | jq -r '.axes.static'
done | sort | uniq -c | sort -rn
# Should show variety, not clustering on few tokens

# Verify reproducibility for evidence tracking
bar shuffle --seed 42 > /tmp/a.txt
bar shuffle --seed 42 > /tmp/b.txt
diff /tmp/a.txt /tmp/b.txt  # should be empty

# Spot-check a generated prompt against prompt key
bar shuffle --seed 123
# Manually evaluate: does output match ADR 0083 expectations?
```

---

## Future Extensions

- **LLM-assisted evaluation**: Use Claude to score prompts against rubric automatically
- **Automated skill checking**: Script that validates shuffle output against skill documentation programmatically
- **Automated regression**: CI job that flags score drops after catalog changes
- **User feedback integration**: Correlate shuffle seeds with real usage patterns
- **Token affinity matrix**: Identify which tokens pair well/poorly
- **Coverage heatmap**: Visualize which combinations are over/under-represented
- **Skill improvement tracking**: Monitor how skill feedback impacts subsequent shuffle evaluations
