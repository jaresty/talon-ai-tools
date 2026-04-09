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
- **Natural-entry validation**: For each token with `natural` entries in `CROSS_AXIS_COMPOSITION` (consult the dict — covers channel, form, completeness, and method tokens), include at least one seed combining it with a `natural`-listed pairing. These validate that `natural` assertions hold empirically — the `natural` list is a structural claim, not a tested guarantee.
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
| **Combination harmony** | Do the selected tokens work together or fight? When a channel token is present, apply the universal rule first: channel wins, task becomes a content lens. A combination is harmonious if the reframe is derivable — score it on output quality, not apparent conflict. Consult "Choosing Channel" in `bar help llm` for cautionary exceptions. |
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

**When to run:** Every 3–5 rapid evaluation cycles. Do not defer more than 5 cycles — gaps in the reference and skill documentation compound.

**Bar command for meta-analysis:**
```bash
bar build probe full domains gap \
  --addendum "Meta-evaluation of [N] representative seeds from cycles [X]-[Y] against bar help llm and bar-autopilot skill documentation. Identify where skill guidance implicitly assumes user knowledge, where bar help llm documents restrictions but they're unenforced at grammar level, and where dev-repo guidance fixes haven't propagated to the installed binary."
```
Use `gap` method token (not `rigor` or `domains` alone) — gap specifically surfaces where implicit assumptions clash with explicit treatment, which is exactly what meta-analysis tests.

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
| **Cross-axis composition coverage** | If this seed includes any token with a `CROSS_AXIS_COMPOSITION` entry (channel, form, completeness, or method — consult the dict): does the relevant section of `bar help llm` explain whether this pairing is natural, cautionary, or derivable via the universal rule? Score 1 if the section is absent or silent on this combination; 5 if it clearly explains the expected output. N/A if no token with an entry is selected. |

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

#### Phase 2d: Process Self-Evaluation

After evaluating skills and reference documentation, evaluate the evaluation process itself. This phase uses the same `gap` method — surfacing where the process implicitly assumes things are correct or complete that may not be.

**Bar command:**
```bash
bar build probe full domains gap \
  --addendum "Evaluate the ADR-0085 evaluation process itself: what does the process implicitly treat as settled that may not be? Consider: sampling strategy, release pipeline, fix closure rate, score calibration, meta-analysis cadence, blind spots in rapid evaluation."
```

**Questions to answer:**

| Criterion | Question |
|-----------|----------|
| **Sampling adequacy** | Did seed selection cover cross-axis edge cases, or only within-axis patterns? Are grammar gap patterns (channel+task, form+completeness) deliberately sampled? |
| **Release pipeline** | Are dev-repo guidance fixes visible in the installed binary? Is there a release lag between `make bar-grammar-update` and what users actually see? |
| **Fix closure rate** | Of recommendations from prior cycles, how many were implemented? How many remain open? Is the backlog growing faster than it's being resolved? |
| **Score calibration** | Was calibration run per Phase 0? If single-evaluator, was the within-evaluator consistency check completed (max delta ≤ 1) and documented in evaluation headers? An undocumented single-evaluator run is a gap; a documented single-evaluator run with boundary rationale captured is a valid path. Are the 1–5 rubric boundaries consistently applied across the cycle? |
| **Meta-analysis cadence** | How many rapid evaluation cycles since the last meta-analysis? Was deferral appropriate, or did documentation gaps compound undetected? |
| **Rapid evaluation blind spots** | Does the scoring methodology surface score-3 cases with the same rigor as score-2? Are "sparse" score-3 combos tracked for patterns, or dismissed as noise? |
| **Feedback loop closure** | After a fix is applied and released, are the original evidence seeds re-tested against the installed binary? Is there a post-release validation step? |

**Scoring rubric:**

- **5 - Tight process**: No implicit assumptions found; process is fully self-consistent
- **4 - Minor gaps**: One or two assumptions that are unlikely to cause real problems
- **3 - Meaningful gaps**: Gaps that have already caused observable drift (deferred phases, untracked release lag)
- **2 - Structural gaps**: The process has systematic blind spots that will produce wrong conclusions
- **1 - Broken**: Process cannot reliably detect the problems it was designed to find

**Feedback capture:**

```markdown
### Process Self-Evaluation

**Process health score:** {1-5}

**Gaps identified:**
- [ ] Sampling: {describe gap in seed selection strategy}
- [ ] Release pipeline: {describe lag or missing verification}
- [ ] Fix closure: {list open recommendations from prior cycles}
- [ ] Calibration: {undocumented single-evaluator run / Phase 0 skipped / boundary rationale not captured}
- [ ] Cadence: {N cycles deferred; gaps compounded}
- [ ] Blind spots: {describe systematic omissions in rapid evaluation}
- [ ] Feedback loop: {post-release validation missing or incomplete}

**Recommendations for process:**
- Add {step} to the refinement cycle to address {gap}
- Change {cadence/threshold} from {current} to {proposed} because {reason}
```

**Output artifact:**
- `docs/adr/evidence/0085/process-feedback.md` - Process health findings and improvement recommendations

#### Phase 2e: Distinction Check (compare mode)

**When to run:** Any time Phase 2 scoring surfaces a suspected redundancy between two tokens —
same-category overlap, near-identical descriptions, or qualitative notes saying "outputs felt
identical." Run before Phase 3 retire recommendations are drafted.

**Retire-candidate backlog sweep:** At the start of each cycle, check which tokens on the
retire-candidate list (open `action: retire` or `action: tracking` entries in `fix-closure-tracking.md`)
appear in the corpus. If any retire candidate appears in a shuffle seed this cycle, compare mode
is required before the cycle closes. If a retire candidate goes 5+ cycles without appearing in
the corpus at all, flag it separately — low shuffle frequency is itself a retirement signal
(low utility or high redundancy causing systematic under-selection).

**Mechanism:** Use ADR-0161 Stage 1 compare mode to generate a side-by-side Approach A prompt
for the candidate pair, then submit it to an LLM and score whether the two output sections are
empirically distinguishable.

```bash
# Example: testing whether systemic and mapping produce distinguishable outputs
bar build probe method=systemic,mapping \
  --subject "why is this codebase hard to extend"
# Submit the output to an LLM; score whether the two sections differ meaningfully
```

**Scoring:**
- **Distinguishable (outputs clearly differ in framing, emphasis, or conclusion)**: retain both;
  consider editing descriptions to make the distinction explicit if it was not apparent from
  shuffle scoring alone.
- **Indistinguishable (outputs are effectively interchangeable)**: strong retire signal —
  record as `distinction-check: failed` in the retire recommendation YAML.
- **Distinguishable but one is consistently weaker**: both tokens exist and differ, but one
  reliably produces lower-quality output for the tested task type. Record as
  `distinction-check: asymmetric` and flag the weaker token for a description edit before
  retiring. A token that is distinguishable but weak may be salvageable with a better
  description.

**Limitation:** Compare mode generates an Approach A prompt — the LLM is asked to embody
each token and respond. The quality of the distinction check depends on the LLM's ability
to correctly apply the token framing. A single task subject is not sufficient evidence;
run at least 3 different subject types before concluding indistinguishability.

**Output artifact:** append distinction check results to the retire candidate entry in
`docs/adr/evidence/0085/recommendations.yaml`.

#### Phase 2f: Sequence Signal Detection (ADR-0225)

**When to run:** During any Phase 2 evaluation cycle, after scoring individual prompts.

**What to look for:** A *sequence signal* is present when running prompt B cold (without prior
context) scores meaningfully lower than running prompt B after prompt A has already been
applied to the same subject. This is a directed quality uplift — A's output makes B more
effective, not merely compatible.

Co-occurrence (tokens appearing together in the same shuffle seed) indicates compatibility,
not sequence dependency. The sequence signal requires an explicit chained evaluation: score
B cold, score B with A's output as prior context, compare.

**Protocol:** Follow ADR-0225 §"Sequence discovery via shuffle" for the full nomination,
chained evaluation, and threshold criteria. Key threshold: mean score uplift ≥ 0.75 points
(1–5 scale) across ≥ 3 subject types, with directionality confirmed (A→B uplifts more than
B→A).

**Running the chained evaluation correctly:**

Shuffle seeds are deterministic and subject-independent — the same seed produces the same
tokens regardless of what subject is passed. This means broad shuffle sweeps across many
seeds do NOT surface co-occurrence patterns useful for sequence discovery. Use shuffle to
*explore the token space*, not to find pairings.

For sequence signal detection, skip shuffle and go directly to targeted chained evaluation:

1. Identify candidate pairings intuitively (e.g., `probe → plan`, `check → fix`, `sim → make`)
2. For each pairing (A → B):
   - Run B cold on a subject; score 1–5; note what's missing
   - Run A on the same subject; execute the output fully
   - Run B primed with A's output as subject; score 1–5
   - Record cold score, primed score, uplift, and whether direction matters
3. Be honest about scores — uniform results across all pairings indicate the evaluator went
   through the motions rather than genuinely measuring. Real evaluations produce varied scores.
4. Confirm directionality: does A→B uplift more than B→A would? If not, ordering is arbitrary.

**Retrospective sweep:** Existing seeds in `docs/adr/evidence/0085/` are a candidate pool
that has never been evaluated for sequence signals. Before generating new seeds for discovery,
run the chained evaluation on any shuffle pairs that intuitively suggest ordering (e.g.,
`prep` before `vet`, `diagnose` before `fix`).

**Output artifact:** Nominated sequences go to `lib/sequenceConfig.py` via the ADR-0225
process. Record the nomination rationale and scores in `docs/adr/evidence/0085/sequences.md`.

#### Phase 2g: Systematic Sequence Coverage Audit (ADR-0226)

**When to run:** Periodically — after new sequences are added, after the usage pattern taxonomy
in `bar help llm` is updated, or when there is reason to believe workflow patterns are not
covered. Complements Phase 2f (empirical, shuffle-driven) with a systematic, taxonomy-driven
pass.

**Contrast with Phase 2f:** Phase 2f discovers sequence candidates by observing that prompt B
scores higher after prompt A — it is empirical and bottom-up. Phase 2g audits coverage by
enumerating known workflow patterns and asking whether each one has a named sequence — it is
systematic and top-down. Both are needed: Phase 2f finds sequences you didn't anticipate;
Phase 2g finds gaps in patterns you already know exist.

**Protocol:**

1. **Enumerate workflow patterns.** Run `bar help llm` and read § "Usage Patterns by Task
   Type." List each pattern. This is the audit scope.

2. **For each pattern, ask three questions:**
   - Does a named sequence exist for this pattern? (`bar sequence list`)
   - If yes: does the mode match how the workflow actually runs? A pattern that requires
     real-world action between steps should be `linear` or `cycle`, not `autonomous`.
   - If no: does this pattern naturally pause for real-world input? If yes, it is a gap.

3. **Identify gaps.** A gap is any pattern that:
   - Has no named sequence, AND involves a real-world step between LLM steps (experiment,
     deploy, interview, code execution, human review), OR
   - Has a named sequence with the wrong mode (e.g., marked `autonomous` but requires
     user results between steps).

4. **Propose candidates.** For each gap, draft:
   - Sequence name (kebab-case)
   - Mode: `autonomous` | `linear` | `cycle`
   - Step sketch: 2–3 tokens with roles and whether each requires user input
   - Rationale: what real-world action falls between steps, why the pattern recurs

5. **Validate.** For each candidate, run a subagent with a representative task and observe
   whether the pause/resume protocol triggers correctly and produces meaningful output at
   each step. Use a weak model (e.g., Haiku) to keep cost low.

**Output artifact:** Validated candidates go to `lib/sequenceConfig.py` via the ADR-0225
process. Record the audit findings (patterns surveyed, gaps found, candidates proposed,
validation results) in `docs/adr/evidence/0085/sequences.md`.

**Termination condition:** The audit is complete when every pattern in the usage taxonomy
either has a named sequence with the correct mode, or has a documented rationale for why
no sequence is warranted (e.g., the pattern is fully autonomous and well-served by ad hoc
chains).

### Phase 3: Recommendation

Based on evaluation, categorize findings into actions:

#### Retire
Token produces consistently low scores or is indistinguishable from another.

**Aggregation requirement before retiring**: Tally the token's appearances across all evaluated seeds in this cycle. Exclude any appearances flagged as known-cautionary cross-axis combinations (per the cross-axis composition check) — those scores reflect a structural channel+task incompatibility, not a token quality issue. Compute mean score and minimum score across remaining qualifying appearances. "Consistently low" means ≥3 qualifying appearances with mean ≤2.5, or any single score of 1. If fewer than 3 qualifying appearances are available, gather additional targeted seeds before proceeding to a retirement recommendation.

**Priority signal — same-category redundancy**: If the redundant token shares a semantic category (Decision/Understanding/Exploration/Diagnostic) with the token it overlaps, retirement is higher priority than cross-category overlap. Tokens in the same category are explicitly positioned as peers; indistinguishable outputs within a category are unambiguous redundancy, not a framing difference.

**Distinction check required**: Before finalizing any retire recommendation based on redundancy,
run Phase 2e compare mode on the candidate pair. A retire recommendation without a
`distinction-check` result is incomplete. Record the result in the YAML as shown below.

```yaml
action: retire
token: "systemic"
axis: method
category: "Understanding"  # include when retiring a method token
reason: "Overlaps significantly with 'mapping' (same Understanding category); outputs indistinguishable"
evidence: [seed_12, seed_34, seed_45]
distinction-check: failed  # failed | asymmetric | distinguishable — required before retire is finalized
distinction-check-subjects: ["why is this codebase hard to extend", "explain the payment system", "what does this module do"]
```

#### Edit
Token concept is valuable but description needs refinement.

For **tokens with `CROSS_AXIS_COMPOSITION` entries** (channel, form, completeness, or method tokens — consult the dict), add `ssot_target` to route the edit to the correct SSOT:
- `description` — token's short description string (default for all non-channel tokens)
- `guidance_prose` — `AXIS_KEY_TO_GUIDANCE` narrative (human-facing; TUI2/SPA meta panel)
- `cautionary_entry` — `CROSS_AXIS_COMPOSITION` warning text (structured; rendered in `bar help llm` cross-axis composition sections)
- `use_when` — `AXIS_KEY_TO_USE_WHEN` selection guidance

```yaml
action: edit
token: "focus"
axis: scope
ssot_target: description  # required for tokens with CROSS_AXIS_COMPOSITION entries; optional but encouraged for others
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

#### Add Cautionary Entry
Cross-axis combination produces structurally poor output that cannot be resolved by the pairing tokens' individual descriptions. The structural incompatibility may be any of:
- **Format incompatibility**: the task's inherent modality (narrative, non-executable) conflicts with the channel's output format (e.g., `shellscript+sim`)
- **Capacity incompatibility**: one token constrains output volume in a way that prevents another token from doing its job (e.g., `gist+fig`, `skim+rigor`, `commit+max`)
- **Directional range incompatibility**: output format cannot accommodate multi-dimensional directional range (e.g., `commit+fog`, `gist+bog`)

**Before adding**: verify the combination cannot be rescued by the universal rule or form-as-lens mechanism. Only combinations that produce poor output *even after applying those rescues* belong here.

```yaml
action: cautionary-entry
axis: "channel"        # top-level axis in CROSS_AXIS_COMPOSITION ("channel", "form", "completeness", or "method")
token: "shellscript"   # token within that axis
paired_axis: "task"    # the axis being paired with
paired_token: "sim"    # the specific token that produces poor output
warning: "tends to produce thin output — simulation is inherently narrative, not executable"
reason: "Simulation tasks require narrative flow that cannot be expressed as executable shell commands"
evidence: [seed_12, seed_34]
```

#### Reclassify Natural Entry
A combination listed as `natural` in `CROSS_AXIS_COMPOSITION` consistently produces poor output in practice — the `natural` assertion was a structural hypothesis that empirical evaluation has falsified.

```yaml
action: reclassify-natural
axis: "channel"
token: "adr"
paired_axis: "task"
paired_token: "probe"
from: natural
to: cautionary
proposed_warning: "tends to produce shallow decisions — probe's open-ended analysis resists ADR's conclusion-first structure"
reason: "Natural assertion not borne out: 3/3 evaluated seeds scored ≤3"
evidence: [seed_51, seed_62, seed_78]
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
| Token: {X} | retire (redundancy) | absent from all tasks | **Corroborated** | Proceed |
| Token: {Y} | edit (description) | gap: undiscoverable | **Aligned** | Priority |
| Skill: {S} | n/a | gap: skill-guidance-wrong | **Single-signal** | Validate with shuffle |
| Token: {Z} | score 5 (coherent) | gap: missing-token | **Contradictory** | Skill fix, not catalog |

> **Note on corroboration**: Because both processes share an evaluator, skill set, and reference document, agreement between them is corroboration, not independent confirmation. Corroborated findings warrant higher confidence but should be treated as confirmed only when tested by a structurally independent observer or method.

### Findings Summary

- **Corroborated:** {both processes agree — note shared evaluator limitation}
- **Aligned:** {related issues, same root cause}
- **Contradictory:** {one process found, other missed — investigate}
- **ADR-0113-only:** {task gaps not in shuffle — validate with next shuffle run}
```

Store: `docs/adr/evidence/cross-validation/{date}.md`

### Evaluation Template

For each shuffled prompt, capture:

```markdown
## Seed: {N}

**Evaluation session:**
- Binary version: {bar --version output}
- Dev repo ahead of binary: {yes/no}
- If yes: Phase 2c (bar help llm) findings are potentially stale — note in help-llm-feedback.md

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

**Cross-axis composition check (complete before scoring):**
- [ ] Check each token in this combination against `bar help llm` cross-axis composition sections (covers channel, form, completeness, and method tokens). If binary version is ahead of dev repo (per evaluation session header), fall back to `CROSS_AXIS_COMPOSITION` in `lib/axisConfig.py` as the authoritative source.
- [ ] No entry found for any token in this combination → skip; proceed to scoring
- [ ] Entry found → evaluate against the rendered guidance:
  - [ ] **Natural**: pairing listed as natural → expected good output; score per normal rubric
  - [ ] **Cautionary**: pairing listed as cautionary → known structural issue; score per normal rubric but exclude from token retirement aggregation; add note below
  - [ ] **Unlisted pairing for a token that has an entry**: check `AXIS_KEY_TO_GUIDANCE` prose for form-as-lens rescues; apply universal rule (channel wins, task = content lens)

**If cautionary combination detected:**
- Axis / token: {e.g., channel/shellscript, form/commit, completeness/skim, method/grow}
- Cautionary pairing: {paired axis + token, e.g., task/sim, directional/fig, method/rigor}
- Warning (from CROSS_AXIS_COMPOSITION): {text}
- Exclude from token retirement aggregation: ✓

**Scores (vs Prompt Key):**
- Task clarity: {1-5}
- Constraint independence: {1-5}
- Persona coherence: {1-5}
- Category alignment: {1-5}
- Combination harmony: {1-5}
  - 5: Tokens reinforce each other naturally; or channel+task reframe is derivable under universal rule and produces coherent output
  - 3: Reframe is derivable but strained; or one token feels redundant
  - 1: Tokens actively contradict; or combination is in CROSS_AXIS_COMPOSITION cautionary list (flag as cautionary; exclude from token retirement aggregation)
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
- Cross-axis composition coverage: {1-5 or N/A}
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
6. **Process feedback**: `docs/adr/evidence/0085/process-feedback.md` - Evaluation process health findings and improvement recommendations (Phase 2d)
7. **Category feedback**: `docs/adr/evidence/0085/category-feedback.md` - Method tokens miscategorized; category label clarity issues; mismatches between `AXIS_KEY_TO_CATEGORY` and skill heuristics
8. **Changelog draft**: Proposed edits to `lib/promptConfig.py` and related files
9. **Grammar regeneration**: Updated `prompt_grammar.json` after changes

---

## Implementation

### Refinement Cycle

Run this process periodically or when catalog drift is suspected:

1. **Calibrate**: Run calibration check with multiple evaluators to establish scoring consistency
1a. **Version check**: Record `bar --version` (installed binary) and compare to dev repo HEAD. Document in each evaluation header. If binary is behind dev repo, flag all Phase 2c (bar help llm) findings as potentially stale.
2. **Generate**: Create 50+ shuffled prompts across sampling strategies
3. **Evaluate**: Score each against prompt key rubric, capture notes, record LLM execution outcome
4. **Meta-Evaluate Skills**: Score each against bar skills, identify skill gaps and catalog issues (Phase 2b)
5. **Meta-Evaluate Reference**: Score `bar help llm` utility for each prompt, identify documentation gaps (Phase 2c)
5a. **Meta-Evaluate Process**: Run `probe full domains gap` on the process itself — sampling adequacy, release pipeline, fix closure rate, score calibration, cadence, blind spots (Phase 2d); capture in `process-feedback.md`
5b. **Distinction Check**: For any suspected redundancy pair surfaced in steps 3–5, run compare mode (Phase 2e) to empirically test whether the tokens produce distinguishable outputs; record `distinction-check` result before drafting retire recommendations
6. **Aggregate**: Group low-scoring tokens, identify patterns, collect feedback for skills/catalog/help/process
7. **Recommend**: Produce actionable list with evidence for catalog, skills, and help documentation
8. **Cross-Validate**: If ADR-0113 (task-driven) has been run, correlate findings between processes
9. **Process Health Check**: Run `probe gap` on the aggregated findings to surface implicit assumptions in the evaluation cycle itself before review
10. **Review**: Human review of recommendations before implementing
11. **Apply**: Edit catalog files, skill documentation, and/or help_llm.go, regenerate grammar
11a. **Release Lag Check**: After running `make bar-grammar-update`, verify that guidance changes are visible in `bar help llm` output from the installed binary. Dev-repo changes update JSON files but NOT the installed binary — a Homebrew/Nix release is required. Check with: `bar help llm | grep -A3 "<token-name>"`. If the guidance is absent, note it in `catalog-feedback.md` under "Release Lag Tracking" and request a release.
12. **Post-Apply Validate**: Re-test original evidence cases against new catalog state
13. **Validate**: Re-run shuffle samples to confirm improvement

#### Phase 0: Calibrate

Before evaluating any prompts, establish evaluator consistency:

```markdown
## Calibration (this run)

**Date:** {YYYY-MM-DD}
**Evaluators:** {names or "single-evaluator"}

### Procedure

**Multi-evaluator:** Both evaluators independently scored the same 10 prompts without consulting each other.

**Single-evaluator (when multi-evaluator is unavailable):** Score the same 5 prompts twice with at least a 24-hour gap between rounds. Flag any dimension where delta > 1 as a calibration concern. Note this limitation in all evaluation headers for this cycle.

### Boundary Rationale

For each score boundary where evaluators (or rounds) disagreed, write one sentence explaining why the example is a 3 and not a 2, or a 4 and not a 3. This rationale becomes the calibration artifact for subsequent rounds — agreement on scores alone does not establish shared criteria across unseen cases.

### Results

**Agreement rate:** {X}/10 = {Y}% (multi-evaluator) or within-evaluator max delta: {Z} (single-evaluator)
**Score delta average:** {Z} (mean absolute difference)
**Boundary rationale captured:** {yes/no}

### Resolution

- [ ] **Calibrated (agreement ≥ 80%):** Proceed with full evaluation
- [ ] **Single-evaluator consistent (max delta ≤ 1):** Proceed, noting single-evaluator limitation in evaluation headers
- [ ] **Discuss and re-score:** Below threshold — resolve discrepancies, clarify rubric
```

Store: `docs/adr/evidence/0085/evaluations/00-calibration.md`

### Process Health Check

After cross-validation (or after aggregating recommendations if ADR-0113 has not been run), run a `probe gap` pass on the cycle's aggregated findings. This is not a diagnostic for any specific token failure — it surfaces implicit assumptions in the evaluation process itself before human review.

```bash
bar build probe gap \
  --subject "$(cat docs/adr/evidence/0085/recommendations.yaml)" \
  --addendum "Surface implicit assumptions in this refinement cycle: what is this process treating as settled that may not be? Consider: scoring rubric boundaries, category definitions, retirement thresholds, cross-validation logic, what counts as sufficient evidence."
```

Questions this step is designed to surface:

- Does the scoring rubric treat "category alignment" as separable from "combination harmony" when they share root causes?
- Are retirement thresholds ("multiple low scores") treating a quantitative bar as self-evident when it isn't?
- Does the cross-validation assume ADR-0085 and ADR-0113 measure independent things when they may share blind spots?
- Are any recommendation actions (retire/edit/recategorize) treating their own scope as obvious?

**Limitation**: `probe gap` is itself a bar prompt — LLM-evaluated, non-deterministic, and subject to the same implicit assumption tendencies the process is trying to detect. Treat its output as an input signal for human review, not as a structural safeguard. It cannot validate its own output. If the probe returns findings that suggest the process is broken, escalate to human judgment — there is no automated resolution path.

Capture output as a brief note appended to `recommendations.yaml` before handing off to human review.

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
