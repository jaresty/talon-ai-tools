# Shuffle-Driven Catalog Refinement

This directory contains tools and templates for systematically evaluating and refining the prompt catalog (static prompts, axes, personas, directionals) using randomized prompt generation.

## Overview

The refinement process follows three phases:

1. **Generation**: Create a corpus of shuffled prompts with reproducible seeds
2. **Evaluation**: Score each prompt against the ADR 0083 prompt key rubric
3. **Recommendation**: Aggregate findings into actionable catalog edits

See [ADR 0085](../../0085-shuffle-driven-catalog-refinement.md) for full rationale and specification.

---

## Workflow

### Phase 1: Generate Corpus

Use `scripts/shuffle_corpus.sh` to create a reproducible set of shuffled prompts:

```bash
# Build bar if needed
go build ./cmd/bar

# Generate default corpus (50 prompts)
./scripts/shuffle_corpus.sh

# Generate smaller test corpus
./scripts/shuffle_corpus.sh --count 10 --output /tmp/test_corpus

# Generate with high fill probability (more constraints/personas)
./scripts/shuffle_corpus.sh --count 20 --fill 0.9 --output corpus/high_fill

# Generate with specific seed range
./scripts/shuffle_corpus.sh --count 25 --seed-start 100
```

**Output**: JSON files at `docs/adr/evidence/0085/corpus/shuffle_NNNN.json`

**Sampling strategies** (from ADR 0085):
- Broad sweep: 30-50 prompts with `--fill 0.5` (default)
- Category deep-dives: 10-20 per axis with targeted generation
- Edge cases: Low fill (`--fill 0.1`) and high fill (`--fill 0.9`)

### Phase 2: Evaluate Prompts

For each generated prompt:

1. Copy `evaluation-template.md` to `evaluations/eval_SEED.md`
2. Fill in the template fields:
   - Extract tokens from the JSON's `.tokens` array
   - Copy prompt text from `.preview` or render from `.axes`
   - Score each of the 5 criteria (1-5)
   - Document notes and observations
   - Draft recommendations (retire/edit/recategorize/add)

**Example evaluation workflow**:

```bash
# Create evaluations directory
mkdir -p docs/adr/evidence/0085/evaluations

# Copy template for seed 1
cp docs/adr/evidence/0085/evaluation-template.md \
   docs/adr/evidence/0085/evaluations/eval_0001.md

# View the shuffled prompt
cat docs/adr/evidence/0085/corpus/shuffle_0001.json | jq -r '.preview'

# View selected tokens
cat docs/adr/evidence/0085/corpus/shuffle_0001.json | jq '.tokens'

# Edit evaluation file
vim docs/adr/evidence/0085/evaluations/eval_0001.md
```

**Scoring rubric** (see template for full details):

| Score | Meaning |
|-------|---------|
| 5 | Excellent - exemplary quality |
| 4 | Good - minor issues only |
| 3 | Acceptable - usable but improvable |
| 2 | Problematic - significant concerns |
| 1 | Broken - incoherent or contradictory |

**Five evaluation criteria**:
1. **Task Clarity**: Does the static prompt define success clearly?
2. **Constraint Independence**: Do constraints shape HOW not WHAT?
3. **Persona Coherence**: Does persona stance fit the task?
4. **Category Alignment**: Are tokens in the right categories?
5. **Combination Harmony**: Do tokens work together or fight?

### Phase 3: Aggregate Recommendations

After evaluating 20-50 prompts, aggregate recommendations:

1. Extract all recommendation YAML blocks from evaluations
2. Group by action type (retire/edit/recategorize/add)
3. Identify patterns (same token getting multiple low scores)
4. Prioritize high-confidence recommendations with multiple evidence seeds
5. Create `recommendations.yaml` with aggregated actions

**Recommendation schema**:

```yaml
# Retire: Token is redundant or indistinguishable
- action: retire
  token: "systemic"
  axis: method
  reason: "Overlaps significantly with 'analytical'"
  evidence: [seed_12, seed_34, seed_45]
  evaluator_consensus: 3  # number of evaluators agreeing

# Edit: Concept good, description needs work
- action: edit
  token: "focus"
  axis: scope
  current: "The response stays within the selected target."
  proposed: "The response addresses only the specific item named, excluding related items."
  reason: "Current description too vague"
  evidence: [seed_7, seed_22]
  evaluator_consensus: 2

# Recategorize: Token in wrong axis
- action: recategorize
  token: "tight"
  from_axis: form
  to_axis: completeness
  reason: "Controls depth/verbosity more than structure"
  evidence: [seed_15, seed_31]
  evaluator_consensus: 2

# Add: Gap identified
- action: add
  axis: directional
  proposed_token: "contrarian"
  proposed_description: "The response challenges assumptions and argues against the obvious interpretation."
  reason: "No existing directional for critical/skeptical lens"
  evidence: [seed_8, seed_19]
  evaluator_consensus: 3
```

**Aggregation workflow**:

```bash
# Extract all recommendations
grep -h "^- action:" evaluations/*.md > recommendations_raw.yaml

# Manual review and consolidation
vim recommendations.yaml

# Prioritize by evidence count and consensus
# - High confidence: 3+ evaluators or 5+ seeds
# - Medium confidence: 2 evaluators or 3+ seeds
# - Low confidence: Single evaluator, 1-2 seeds
```

---

## Files

- `evaluation-template.md` - Template for scoring individual prompts
- `corpus/` - Generated shuffle JSON files (`.gitignore`d)
- `evaluations/` - Completed evaluation markdown files
- `recommendations.yaml` - Aggregated catalog edit actions
- `README.md` - This file

---

## Example: Complete Refinement Cycle

```bash
# 1. Generate corpus
./scripts/shuffle_corpus.sh --count 30

# 2. Evaluate each prompt
for seed in $(seq -f "%04g" 1 30); do
  cp docs/adr/evidence/0085/evaluation-template.md \
     docs/adr/evidence/0085/evaluations/eval_$seed.md

  echo "Evaluate seed $seed:"
  cat docs/adr/evidence/0085/corpus/shuffle_$seed.json | jq -r '.preview'
  echo ""
  read -p "Press enter to edit evaluation..."
  vim docs/adr/evidence/0085/evaluations/eval_$seed.md
done

# 3. Aggregate recommendations
grep -h "^- action:" docs/adr/evidence/0085/evaluations/*.md \
  > docs/adr/evidence/0085/recommendations_raw.yaml

vim docs/adr/evidence/0085/recommendations.yaml
# (consolidate, prioritize, add consensus counts)

# 4. Apply recommendations
# Edit lib/promptConfig.py, lib/axisConfig.py, lib/personaConfig.py
# based on recommendations.yaml

# 5. Regenerate grammar
python scripts/export_prompt_grammar.py

# 6. Validate
go build ./cmd/bar
go test ./internal/barcli/...

# 7. Re-run sample seeds to verify improvement
for seed in 12 34 45; do
  echo "Seed $seed after changes:"
  ./bar shuffle --seed $seed
  echo ""
done
```

---

## Tips

**Efficient evaluation**:
- Evaluate in batches of 5-10 prompts per session
- Focus on medium-score prompts (2-4) where issues are clearest
- Skip obvious excellent (5) or broken (1) prompts after noting the score

**Pattern recognition**:
- Track which tokens appear in low-scoring prompts repeatedly
- Note which combinations consistently cause confusion
- Identify missing token coverage when writing improvised descriptions

**Prioritization**:
- Retire: High confidence needed (3+ evaluators)
- Edit: Medium confidence acceptable (2+ evaluators)
- Recategorize: High confidence needed (significant change)
- Add: Medium confidence (validates perceived gap)

---

## Validation

Verify the process is working:

```bash
# Corpus reproducibility
./bar shuffle --seed 42 > /tmp/a.txt
./bar shuffle --seed 42 > /tmp/b.txt
diff /tmp/a.txt /tmp/b.txt  # should be empty

# Corpus diversity
for i in $(seq 1 10); do
  ./bar shuffle --seed $i --json | jq -r '.axes.static'
done | sort | uniq -c | sort -rn
# Should show variety, not clustering on few tokens

# Evaluation completeness
grep "^**Score:** [1-5]" evaluations/eval_0001.md | wc -l
# Should output 5 (one per criterion)

# Recommendation format
yamllint recommendations.yaml  # if yamllint installed
# Should parse as valid YAML
```

---

## Future Enhancements

- **LLM-assisted scoring**: Use Claude to evaluate prompts automatically
- **Automated aggregation**: Script to consolidate recommendations
- **Coverage heatmap**: Visualize which token combinations are tested
- **Regression testing**: CI job that flags score drops after catalog changes
- **User feedback loop**: Correlate shuffle seeds with real usage patterns
