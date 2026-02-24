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
- **Method category samples**: 5-10 shuffles per method semantic category (Decision/Understanding/Exploration/Diagnostic) with `--include method` to evaluate whether tokens within each category produce distinguishable, coherent outputs. Tokens in the same category that produce indistinguishable results are a stronger retirement signal than cross-category redundancy.
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
| **Method category coherence** | When multiple method tokens are selected, do their semantic categories (Decision/Understanding/Exploration/Diagnostic) make complementary analytical sense together? |

**Scoring rubric:**

- **5 - Excellent**: Prompt is clear, coherent, and tokens reinforce each other
- **4 - Good**: Minor rough edges but intent is clear
- **3 - Acceptable**: Usable but some tokens feel forced or redundant
- **2 - Problematic**: Confusion about intent or category overlap
- **1 - Broken**: Contradictory, nonsensical, or misleading combination

**Evaluation principle — Channel × Form composition**:

Channel defines output medium (code, prose, diagram), form defines structure within that medium.
They compose additively, not in conflict. Evaluate whether the combination makes semantic sense,
not whether tokens seem redundant.

For example: `test + code` = "test structure in code format" (valid, not redundant).
`sim + code` = "simulation expressed as code" (valid, not narrative conflict).

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
| **Method category legibility** | Do the method category headings (Decision/Understanding/Exploration/Diagnostic) in the "Choosing Method" section clearly guide selection toward the methods in this combination? Score 1 if the category labels misdirected selection, 5 if they immediately surfaced the right methods. |

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
- [ ] Method category label {X} in "Choosing Method" section misdirected selection (explain)
- [ ] Method category grouping missing tokens that belong in category {X}

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

#### Starter Pack Update
Shuffle combination is coherent and corresponds to or should be represented by a starter pack.

```yaml
action: starter-pack-update
pack: "investigation"  # existing pack name
current_tokens: [probe, struct, mean, mapping]
proposed_tokens: [probe, struct, mean, mapping, adversarial]
reason: "Shuffle evidence shows adversarial method consistently improves investigation prompts; pack should include it"
evidence: [seed_18, seed_29, seed_44]
```

#### Starter Pack Add
No starter pack covers a coherent combination that shuffle evidence repeatedly surfaces.

```yaml
action: starter-pack-add
proposed_pack: "risk-audit"
proposed_tokens: [probe, fail, adversarial, inversion]
reason: "Shuffle repeatedly surfaces this Diagnostic-method combination for risk tasks; no pack represents it"
evidence: [seed_22, seed_37]
```

#### Recategorize Method
Method token is assigned to the wrong semantic category (Decision/Understanding/Exploration/Diagnostic).

```yaml
action: recategorize-method
token: "systemic"
from_category: "Understanding"
to_category: "Diagnostic"
reason: "Token examines system-level failure patterns, not structural mapping"
evidence: [seed_12, seed_34]
```

#### Phase 3b: Cross-Validate with ADR-0113

If ADR-0113 (task-driven refinement) has been run, compare findings before finalizing recommendations:

```markdown
## Cross-Validation: ADR-0085 ↔ ADR-0113

**ADR-0085 run:** {date / seed range}
**ADR-0113 run:** {date / task sample}

### Correlation Table

| Finding | ADR-0085 | ADR-0113 | Correlation | Action |
|---------|----------|----------|-------------|--------|
| Token: {X} | retire (redundancy) | absent from all tasks | **Confirmed** | Proceed |
| Token: {Y} | edit (description) | gap: undiscoverable | **Aligned** | Priority |
| Skill: {S} | n/a | gap: skill-guidance-wrong | **Single-signal** | Validate with shuffle |
| Token: {Z} | score 5 (coherent) | gap: missing-token | **Contradictory** | Skill fix, not catalog |

### Findings Summary

- **Confirmed:** {both processes agree}
- **Aligned:** {related issues, same root cause}
- **Contradictory:** {one process found, other missed — investigate}
- **ADR-0113-only:** {task gaps not in shuffle — validate with next shuffle run}
```

Store: `docs/adr/evidence/cross-validation/{date}.md`

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

**LLM Execution Outcome:**
- [ ] Executed successfully
- [ ] Refusal or safety filter triggered
- [ ] Output malformed / unparseable
- [ ] Quality degraded (valid tokens, off-prompt output)

**If degraded/failure:**
- Failure mode: {refusal / hallucination / format / quality / context}
- Root cause: {static prompt / token combo / token description / model limitation}
- Signal: {catalog / skill / model issue to flag}

**Scores (vs Prompt Key):**
- Task clarity: {1-5}
- Constraint independence: {1-5}
- Persona coherence: {1-5}
- Category alignment: {1-5}
- Combination harmony: {1-5}
- Method category coherence: {1-5}
  - 5: All methods from compatible categories (e.g., two Diagnostic methods, or Exploration→Understanding progression)
  - 3: Mix of categories with plausible rationale
  - 1: Category clash (e.g., Exploration + Decision methods without a bridging task)
  - N/A: Only one method token selected
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

**Kanji spot-check (optional):**
- [ ] Kanji for selected tokens are semantically reinforcing (e.g., 隙 for `gap` = gap/crack ✓)
- [ ] No kanji appear duplicated across displayed tokens in this combination
- Flag any that feel misleading or arbitrary; record in `category-feedback.md`

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
6. **Category feedback**: `docs/adr/evidence/0085/category-feedback.md` - Method tokens miscategorized; category label clarity issues; mismatches between `AXIS_KEY_TO_CATEGORY` and skill heuristics
7. **Changelog draft**: Proposed edits to `lib/promptConfig.py` and related files
8. **Grammar regeneration**: Updated `prompt_grammar.json` after changes

---

## Implementation

### Refinement Cycle

Run this process periodically or when catalog drift is suspected:

1. **Calibrate**: Run calibration check with multiple evaluators to establish scoring consistency
2. **Generate**: Create 50+ shuffled prompts across sampling strategies
3. **Evaluate**: Score each against prompt key rubric, capture notes, record LLM execution outcome
4. **Meta-Evaluate Skills**: Score each against bar skills, identify skill gaps and catalog issues
5. **Meta-Evaluate Reference**: Score `bar help llm` utility for each prompt, identify documentation gaps
6. **Aggregate**: Group low-scoring tokens, identify patterns, collect feedback for skills/catalog/help
7. **Recommend**: Produce actionable list with evidence for catalog, skills, and help documentation
8. **Cross-Validate**: If ADR-0113 (task-driven) has been run, correlate findings between processes
9. **Review**: Human review of recommendations before implementing
10. **Apply**: Edit catalog files, skill documentation, and/or help_llm.go, regenerate grammar
11. **Post-Apply Validate**: Re-test original evidence cases against new catalog state
12. **Validate**: Re-run shuffle samples to confirm improvement

#### Phase 0: Calibrate

Before evaluating any prompts, establish evaluator consistency:

```markdown
## Calibration (this run)

**Date:** {YYYY-MM-DD}
**Evaluators:** {names or "single-evaluator"}

### Procedure

Both evaluators independently scored the same 10 prompts without consulting each other.

### Results

**Agreement rate:** {X}/10 = {Y}%
**Score delta average:** {Z} (mean absolute difference)

### Resolution

- [ ] **Calibrated (agreement ≥ 80%):** Proceed with full evaluation
- [ ] **Discuss and re-score:** Below threshold — resolve discrepancies, clarify rubric
```

Store: `docs/adr/evidence/0085/evaluations/00-calibration.md`

### Post-Apply Validation

After applying changes, re-test original evidence cases to confirm the fix worked:

```markdown
## Post-Apply Validation

**Applied changes:** {list from recommendations.yaml}
**Validation date:** {YYYY-MM-DD}

### Regression Check

| Recommendation | Original evidence | Re-test result | Status |
|----------------|-------------------|----------------|--------|
| retire: token X | seed_12, seed_34 | Token X no longer appears | ✓ Pass |
| edit: token Y | seed_7, seed_22 | Re-evaluated with new description | ✓ Pass |
| skill-update: {S} | task_T19 | Re-ran task with updated skill | ✓ Pass |
| add: token Z | seed_8 | New token available and selected | ✗ Fail |

### Failed Validations

- {list any failures with likely cause and action}
```

Store: `docs/adr/evidence/0085/post-apply/{date}.md`

### Skill Update Impact Tracking

If the applied changes include skill updates (heuristics, Usage Patterns), track whether they improved outcomes:

```markdown
## Skill Update Impact: {skill name}

**Original recommendation:** {date from recommendations.yaml}
**Update applied:** {date}
**File modified:** {path to skill file}

### Pre-Update Baseline

Original evidence used for gap detection:
- Seeds: {seed_12, seed_34}
- Pre-update scores: {list average}

### Post-Update: Original Evidence Re-Test

| Seed | Pre-update score | Post-update score | Delta |
|------|------------------|-------------------|-------|
| seed_12 | 2 | 4 | +2 |
| seed_34 | 3 | 3 | 0 |

### Post-Update: Fresh Sample

To avoid overfitting to original evidence, generate 5 new seeds and re-evaluate:

| Seed | Coverage score | Notes |
|------|----------------|-------|
| seed_100 | 4 | Good coverage |
| seed_101 | 3 | Similar gap to original |
| seed_102 | 5 | Full coverage |
| seed_103 | 3 | Gap persists: {reason} |
| seed_104 | 4 | Good coverage |

### Analysis

- Original evidence improved: {X}/2
- Fresh sample average: {Y}/5
- Fresh sample vs pre-update average: {comparison}

### Verdict

- [ ] **Effective:** Fresh sample average ≥ pre-update average AND original evidence improved
- [ ] **Partial:** Some improvement but gaps remain
- [ ] **Ineffective:** No meaningful improvement

**Next steps:**
- {for effective: document improvement, close tracking}
- {for partial: iterate on skill update}
- {for ineffective: revert or try catalog-level fix instead}
```

Store: `docs/adr/evidence/0085/skill-updates/{skill-name}-{date}.md`

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
| `docs/adr/evidence/0085/category-feedback.md` | Method token categorization issues and category label clarity gaps |
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
- Calibration phase adds upfront time but improves score quality
- Cross-validation requires ADR-0113 to also be run

### Risks

- Over-pruning: Removing tokens that are valuable in rare contexts
- Churn: Frequent changes destabilize user muscle memory
- Subjectivity: Different evaluators may score differently
- LLM quality gaps: Catalog fixes don't address model execution failures
- Cross-validation contradiction: Processes disagree, unclear which to trust

**Mitigations:**
- Require multiple low scores before recommending retirement
- Batch changes into quarterly refinement cycles
- Use multiple evaluators for ambiguous cases
- Run calibration before each evaluation cycle
- Capture LLM execution outcomes as separate signal from token selection
- Investigate contradictory cross-validation findings before applying fixes

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
- **LLM execution quality tracking**: Aggregate failure modes across cycles to identify systematic model issues
- **Cross-process automation**: Script the correlation between ADR-0085 and ADR-0113 findings
