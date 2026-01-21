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
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Generate       │────▶│  Evaluate        │────▶│  Recommend      │
│  (bar shuffle)  │     │  (vs prompt key) │     │  (catalog edit) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
   N random prompts      Alignment score +        Retire / Edit /
   with --seed           qualitative notes        Recategorize / Add
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

**Scores:**
- Task clarity: {1-5}
- Constraint independence: {1-5}
- Persona coherence: {1-5}
- Category alignment: {1-5}
- Combination harmony: {1-5}
- **Overall**: {1-5}

**Notes:**
{Qualitative observations, specific concerns, token interactions}

**Recommendations:**
- [ ] {action}: {token} - {brief reason}
```

### Output Artifacts

The refinement cycle produces:

1. **Evaluation corpus**: `docs/adr/evidence/0085/evaluations/`
2. **Recommendations list**: `docs/adr/evidence/0085/recommendations.yaml`
3. **Changelog draft**: Proposed edits to `lib/promptConfig.py` and related files
4. **Grammar regeneration**: Updated `prompt_grammar.json` after changes

---

## Implementation

### Refinement Cycle

Run this process periodically or when catalog drift is suspected:

1. **Generate**: Create 50+ shuffled prompts across sampling strategies
2. **Evaluate**: Score each against rubric, capture notes
3. **Aggregate**: Group low-scoring tokens, identify patterns
4. **Recommend**: Produce actionable list with evidence
5. **Review**: Human review of recommendations before implementing
6. **Apply**: Edit catalog files, regenerate grammar
7. **Validate**: Re-run shuffle samples to confirm improvement

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
| `lib/promptConfig.py` | Catalog edits (static prompts) |
| `lib/axisConfig.py` | Axes token edits |
| `lib/personaConfig.py` | Persona/intent edits |

---

## Consequences

### Positive

- Systematic process replaces ad-hoc catalog maintenance
- Evidence-based decisions with reproducible seeds
- Catches category misalignment before users encounter confusion
- Identifies redundancy and gaps proactively
- Builds institutional knowledge about what combinations work

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

- **LLM-assisted evaluation**: Use Claude to score prompts against rubric
- **Automated regression**: CI job that flags score drops after catalog changes
- **User feedback integration**: Correlate shuffle seeds with real usage patterns
- **Token affinity matrix**: Identify which tokens pair well/poorly
- **Coverage heatmap**: Visualize which combinations are over/under-represented
