# ADR-0113: Task-Gap-Driven Catalog Refinement

## Status

Accepted

## Context

ADR-0085 established a shuffle-driven refinement process that generates random token combinations
and evaluates their coherence. Six cycles of this process have proven effective at surfacing
**catalog noise**: incoherent combinations, form/channel conflicts, ambiguous descriptions, and
token redundancy.

However, shuffle-driven evaluation has a structural blind spot: it tests whether *randomly selected
tokens work together*, not whether the catalog can *adequately address real user tasks*. A catalog
could pass every shuffle evaluation while still failing to represent common, important task types.
The two failure modes are different:

| Failure mode | Shuffle detects? | Task analysis detects? |
|---|---|---|
| Incoherent token combination | Yes | Incidentally |
| Token description too vague to apply | Partially | Yes |
| No token exists for a real task dimension | No | Yes |
| Skill guidance misroutes common tasks | No | Yes |
| Token exists but never surfaces via skills | No | Yes |

**The complementary question**: Given what users actually bring to bar, can the catalog and skills
construct a prompt that serves them well? Where they cannot, that gap is more urgent than a
coherence issue, because it means a real user is underserved.

This ADR establishes a **task-gap-driven refinement process** as a companion to ADR-0085's
shuffle-driven process.

---

## Decision

Establish a task-gap-driven refinement process that works from realistic user tasks inward to the
catalog, using bar skills as the selection agent and gap analysis as the recommendation driver.

### Relationship to ADR-0085

```
ADR-0085 (shuffle-driven)          ADR-0113 (task-driven)
──────────────────────────         ───────────────────────────────────
Direction:  token → evaluation     Direction:  task → token selection → evaluation
Test:       are these tokens       Test:       can the catalog + skills
            coherent together?                 address this task?
Finds:      noise, conflicts,      Finds:      gaps, missing tokens,
            redundancy                         skill misrouting, undiscoverable tokens
Output:     edit/retire/recategorize          add/edit/skill-update
```

Both processes feed the same recommendation pipeline. They should be run in alternating cycles
or triggered by different conditions: shuffle when the catalog changes, task analysis when
skill guidance or user task scope changes.

### Process Overview

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Generate        │───▶│  Apply           │───▶│  Evaluate        │───▶│  Diagnose       │
│  task taxonomy   │    │  bar skills      │    │  coverage        │    │  gap type       │
│  (variants form) │    │  (autopilot)     │    │  (vs task need)  │    │  + recommend    │
└──────────────────┘    └──────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
  Weighted task list      bar command per task    Coverage score +       Missing token /
  with probabilities      from skill selection    gap observations       skill update /
  N task types            (bar build output)      (1–5 per dimension)    description edit
```

---

### Phase 1: Generate Task Taxonomy

Produce a probability-weighted list of realistic user task types using the `variants` form token.
`variants` is designed to produce "several distinct, decision-ready options... including
approximate probabilities when helpful." Running it via a bar prompt asks an LLM to apply that
structure to the task space itself.

**Invoke bar to generate the taxonomy:**

```bash
# Build a probe prompt using variants form to enumerate realistic bar use cases
bar build probe full variants --addendum \
  "Enumerate the realistic types of tasks users bring to bar, covering software \
   engineering, analysis, writing, planning, and design contexts. Label each with \
   an approximate probability weight reflecting how frequently this task type \
   appears in practice. Avoid near-duplicates. Aim for 20-30 distinct task types."
```

Feed the resulting structured prompt to an LLM. The output is a labelled list of task types
with approximate probabilities, for example:

```markdown
## Task Taxonomy

| # | Task type | Example | Approx. weight |
|---|-----------|---------|----------------|
| T01 | Explain a code system to a non-technical stakeholder | "explain our auth flow to the PM" | 12% |
| T02 | Analyse failure modes in a design or implementation | "what could go wrong with this approach?" | 9% |
| T03 | Plan a refactor with structural constraints | "plan migrating from REST to GraphQL" | 8% |
| T04 | Generate Gherkin acceptance criteria from a story | "write BDD tests for this feature" | 7% |
| T05 | Draft a Slack message summarising a technical decision | "tell the team we're delaying the release" | 6% |
...
```

**Sampling strategy:**

- Select tasks proportional to weight: higher-weight tasks appear more often in the evaluation corpus
- Include at least one task from each broad domain (code, analysis, writing, planning, design)
- Add edge-case tasks: cross-domain tasks, very brief tasks, tasks with strong format requirements

**Output artifact:** `docs/adr/evidence/0113/task-taxonomy.md`

**Secondary pass — method category stratification:**

After generating the main probability-weighted list, run a secondary pass to surface task types that may be underrepresented in a flat probability-weighted sample:

```bash
bar build probe full variants --addendum \
  "For each method category — Decision Methods, Understanding Methods, \
   Exploration Methods, Diagnostic Methods — list 5 realistic bar task types \
   where that category's methods would be the primary analytical tool. \
   Label each with the category and an example bar command."
```

Use the output to ensure each method category has at least 3-5 representative tasks in the evaluation corpus. This prevents systematic under-sampling of Diagnostic or Exploration tasks, which users may describe with lower-frequency vocabulary but are no less important.

---

### Phase 2: Apply Bar Skills

For each sampled task, run bar-autopilot to select tokens and construct the bar command. This
mirrors how an LLM using bar in practice would approach the task — making the skill the selection
agent tests both the catalog and the skill simultaneously.

**For each task in the corpus:**

1. Present the task description to an LLM running bar-autopilot
2. Let the skill consult `bar help llm`, select tokens, and run `bar build`
3. Capture the full selection: which tokens were chosen, which were considered and rejected, and
   the resulting bar output

**Capture format:**

```markdown
## Task: T01 — Explain code system to non-technical stakeholder

**Task description:** "Explain our authentication flow to the product manager"

**Skill selection log:**
- Considered: show, probe → chose: show (explanation task, not analysis)
- Completeness: full (thorough explanation needed)
- Scope: considered struct, mean → chose: mean (conceptual understanding is the goal)
- **Method category targeted:** Understanding (explanation task requires structural mapping, not root-cause or decision)
  - **Category rationale:** goal is to convey how the system works, not diagnose problems or evaluate options
- Method: considered melody → rejected (coordination analysis is secondary)
- Form: (none selected)
- Channel: plain (prose for PM audience)
- Persona: designer_to_pm or custom → chose: peer_engineer_explanation

**Bar command constructed:**
bar build show full mean plain peer_engineer_explanation

**Bar output preview:**
> The response explains or describes the subject for the stated audience.
> [full, mean scope, plain channel, peer_engineer_explanation]
```

**Output artifact:** `docs/adr/evidence/0113/selections/task_T01.md` (one file per task)

---

### Phase 3: Evaluate Coverage

Score each skill-constructed prompt against the original task need. Unlike ADR-0085's coherence
rubric (do these tokens work together?), the coverage rubric asks whether the tokens *adequately
serve the task*.

**Coverage rubric (1–5 per dimension):**

| Dimension | Question |
|-----------|----------|
| **Token fitness** | Do the selected tokens accurately describe how this task should be done? |
| **Token completeness** | Are there important dimensions of the task that no selected token captures? |
| **Skill correctness** | Did the skill guidance lead to the right selection, or did it misroute? |
| **Prompt clarity** | Would the resulting bar output produce a response that genuinely serves the task? |
| **Overall** | Does this combination represent the best the catalog can offer for this task? |

**Scoring:**

- **5 - Full coverage**: Tokens precisely address all meaningful dimensions of the task
- **4 - Good coverage**: Minor dimensions uncaptured but core is well served
- **3 - Partial coverage**: Key aspects of the task are not represented by any token
- **2 - Poor coverage**: The combination misrepresents the task or skill misrouted badly
- **1 - No coverage**: No adequate token combination exists for this task type

**Starter pack check (secondary):**

After scoring the skill-selected combination, check whether a starter pack covers this task type:

- Is there a starter pack that maps to this task type? If yes, name it and score its coverage: {1-5}
- Pack vs autopilot: [Pack better / Autopilot better / Equivalent]
- If pack is better: what does it provide that autopilot missed? (candidate for skill-guidance-wrong diagnosis)
- If no relevant pack exists: does this task type warrant a new starter pack? (candidate for `starter-pack-add` recommendation)

**Output artifact:** `docs/adr/evidence/0113/evaluations/task_T01_eval.md`

---

### Phase 4: Diagnose Gap Type

For every task scoring ≤3, diagnose *why* the coverage is insufficient. Gap type determines
the recommendation action.

#### Gap Type 1: Missing Token

No token in the catalog represents this task dimension. The concept is absent.

```yaml
gap_type: missing-token
task: T07 — Identify cross-cutting concerns in a codebase
dimension: scope
observation: >
  No scope token focuses on cross-cutting concerns (logging, auth, error handling,
  observability) as a distinct structural lens. The user wants to identify where
  these concerns are handled, duplicated, or missing. 'struct' (arrangements/dependencies)
  is the closest but doesn't foreground the cross-cutting nature.
recommendation:
  action: add
  axis: scope
  proposed_token: "cross"
  proposed_description: >
    The response focuses on concerns that span multiple modules or components —
    patterns applied repeatedly across the codebase (logging, error handling,
    auth, observability) — examining their consistency, distribution, and
    coupling characteristics.
evidence: [task_T07, task_T14]
```

#### Gap Type 2: Undiscoverable Token

A token exists that would serve the task, but the skill failed to surface it. The token's
description or the skill's heuristics don't connect this task type to that token.

```yaml
gap_type: undiscoverable-token
task: T12 — Evaluate a proposed architecture against known failure patterns
dimension: method
observation: >
  'inversion' method (work backward from catastrophic outcomes) is well-suited here,
  but bar-autopilot selected 'adversarial' instead. The inversion description doesn't
  mention architecture evaluation as a use case, so the skill's heuristics don't
  surface it for this pattern.
recommendation:
  action: edit
  token: inversion
  axis: method
  proposed_addition: >
    Well-suited for architecture evaluation: starting from known failure modes
    (cascade failures, split-brain, thundering herd) and working backward to
    identify which design choices create or prevent them.
evidence: [task_T12]
```

#### Gap Type 3: Skill Guidance Wrong

A good token combination exists and the tokens are discoverable, but the skill's heuristics
actively misrouted selection — either toward weaker tokens or away from the right ones.

```yaml
gap_type: skill-guidance-wrong
task: T19 — Produce a risk summary for a release decision
dimension: task + method
observation: >
  The skill selected 'probe' (surface assumptions/implications) but this task is
  more naturally 'pull' (extract a subset — the risk subset) paired with 'fail'
  scope. The skill's "Usage Patterns by Task Type" section lists probe as the
  default for analysis tasks, which is too broad — it overrides the more specific
  pull+fail pattern for extraction-from-risk tasks.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    For risk extraction tasks ("what are the risks", "failure modes", "what could go wrong"):
    prefer 'pull' + 'fail' scope over 'probe'. Reserve 'probe' for open-ended analysis
    where the structure of the analysis itself is the deliverable.
evidence: [task_T19, task_T23]
```

#### Gap Type 4: Category Misrouting

A method token was selected from the correct axis, but its semantic category (Decision/Understanding/Exploration/Diagnostic) doesn't match the task's analytical need. The token is discoverable and the skill guidance isn't grossly wrong — the selection fails at category granularity.

```yaml
gap_type: category-misrouting
task: T31 — Identify the root cause of a recurring production failure
dimension: method
observation: >
  bar-autopilot selected 'mapping' (Understanding category) to analyze
  the failure's structure. The task calls for root-cause work, which belongs
  to the Diagnostic category ('diagnose', 'inversion', 'adversarial').
  'mapping' is discoverable and technically valid, but the wrong analytical
  stance for this task type.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Choosing Method"
  proposed_addition: >
    For root-cause and failure-mode tasks, target Diagnostic-category methods
    (diagnose, inversion, adversarial) before Understanding-category methods.
    Understanding methods (mapping, systemic, flow) describe structure;
    Diagnostic methods find what's broken.
evidence: [task_T31]
```

#### Gap Type 5: Out of Scope

The task is not appropriate for bar — bar's grammar cannot represent it well and should not
try to. This is a valid finding: knowing the catalog's boundary is as useful as knowing its coverage.

```yaml
gap_type: out-of-scope
task: T28 — Real-time collaborative brainstorming session
observation: >
  Bar constructs single-turn structured prompts. Real-time collaborative brainstorming
  requires multi-turn, stateful interaction that bar's grammar cannot represent.
  The 'cocreate' form gets closest but is still a single-prompt artifact.
recommendation:
  action: none
  note: >
    Document as a known out-of-scope task type. Consider adding to bar help llm
    § Scope note: "Bar produces single-turn structured prompts; it does not model
    multi-turn interactive sessions."
evidence: [task_T28]
```

---

### Phase 5: Recommend

Aggregate gap diagnoses into actionable recommendations following the same taxonomy as ADR-0085:

| Gap type | Recommendation action |
|----------|-----------------------|
| `missing-token` | **Add** — propose new token with description |
| `undiscoverable-token` | **Edit** — clarify token description to surface for this task type; or update skill heuristics |
| `skill-guidance-wrong` | **Skill-update** — revise skill section (Usage Patterns, Heuristics) |
| `category-misrouting` | **Skill-update** — revise "Choosing Method" section to clarify category selection for this task type |
| `out-of-scope` | **Document** — note as known boundary in bar help llm |

---

### Evaluation Template

```markdown
## Task: {ID} — {Task type name}

**Task description:** {Concrete example phrasing}
**Probability weight:** {from taxonomy}
**Domain:** {code / analysis / writing / planning / design}

**Skill selection log:**
- Task token considered: {options} → chose: {token} (reason)
- Completeness: {token} (reason)
- Scope: considered {options} → chose: {token} (reason)
- **Method category targeted:** [Decision / Understanding / Exploration / Diagnostic / mixed]
  - **Category rationale:** {why this category fits the task's analytical need}
- Method: considered {options} → chose / rejected: {token} (reason)
- Form: {token or none} (reason)
- Channel: {token or none} (reason)
- Persona: {selection} (reason)

**Bar command constructed:**
bar build {tokens}

**Bar output preview:**
> {first 200 chars of rendered prompt}

**LLM Execution Outcome:**
- [ ] Executed successfully
- [ ] Refusal or safety filter triggered
- [ ] Output malformed / unparseable
- [ ] Quality degraded (valid tokens, off-prompt output)

**If degraded/failure:**
- Failure mode: {refusal / hallucination / format / quality / context}
- Root cause: {static prompt / token combo / skill selection / model limitation}
- Signal: {catalog / skill / model issue to flag}

**Coverage scores:**
- Token fitness: {1-5}
- Token completeness: {1-5}
- Skill correctness: {1-5}
- Prompt clarity: {1-5}
- **Overall: {1-5}**

**Gap diagnosis:** {gap type or "none"} — [missing-token / undiscoverable-token / skill-guidance-wrong / category-misrouting / out-of-scope]
{Gap YAML block if applicable}

**Starter pack check:**
- Relevant pack: {pack name or "none"}
- Pack coverage score: {1-5 or N/A}
- Pack vs autopilot: [Pack better / Autopilot better / Equivalent / N/A]
- Notes: {what pack adds or misses vs autopilot selection}

**Notes:**
{Observations on what worked, what was missing, what the skill did well or poorly}
```

---

### Output Artifacts

| Artifact | Purpose |
|----------|---------|
| `docs/adr/evidence/0113/task-taxonomy.md` | Probability-weighted task list |
| `docs/adr/evidence/0113/selections/` | Per-task skill application logs |
| `docs/adr/evidence/0113/evaluations/` | Per-task coverage scores and gap diagnoses |
| `docs/adr/evidence/0113/gap-catalog.md` | Aggregated gap findings grouped by type |
| `docs/adr/evidence/0113/recommendations.yaml` | Actionable recommendations (same format as ADR-0085) |
| `docs/adr/evidence/0113/category-feedback.md` | Method token categorization issues and category label clarity gaps |

---

## Implementation

### Refinement Cycle

Run this process when:
- The skill documentation (bar-autopilot, bar-manual, bar-suggest) has changed significantly
- A new domain of tasks is suspected to be underserved
- ADR-0085 shuffle cycles show consistently high scores (noise is low) but user feedback suggests gaps

Steps:
1. **Calibrate** — run calibration check with multiple evaluators to establish scoring consistency
2. **Generate taxonomy** — run bar probe + variants, capture task list with weights
3. **Sample** — draw 20-30 tasks proportional to weight
4. **Apply skills** — for each task, run bar-autopilot to select tokens and build prompt
5. **Score** — evaluate coverage on four dimensions, capture LLM execution outcome
6. **Diagnose** — classify gaps by type for all tasks scoring ≤3
7. **Aggregate** — group by gap type, identify recurring patterns
8. **Recommend** — produce actionable list with evidence
9. **Cross-Validate** — if ADR-0085 (shuffle-driven) has been run, correlate findings between processes
10. **Process Health Check** — run `probe gap` on aggregated findings to surface implicit assumptions in the evaluation cycle itself before review
11. **Review** — human review before implementing
12. **Apply** — edit catalog, skills, or help_llm.go; regenerate grammar
13. **Post-Apply Validate** — re-test original evidence cases against new catalog state
14. **Validate** — re-run a sample of gapped tasks to confirm improvement

### Automation Note

Phase 2 (skill application) requires an LLM in the loop and cannot be run as a pure CLI
pipeline. The bar command is constructed *by* the skill, not passed to it. A future automation
could use the Claude API to script the skill application step, but initial cycles are expected
to be human-driven with Claude assistance.

### Interaction with ADR-0085

- **ADR-0085 should be run first** when the catalog has recently changed — catch coherence
  issues before testing coverage with real tasks
- **ADR-0113 should be run** when skill guidance changes or when gap coverage is suspected
- Recommendations from both processes feed the same YAML format and review pipeline
- A finding in ADR-0113 (undiscoverable token) may surface a token description that ADR-0085
  later validates or invalidates in combination
- **Cross-validate findings**: Before applying recommendations, compare what each process found

#### Phase 0: Calibrate

Before evaluating any tasks, establish evaluator consistency:

```markdown
## Calibration (this run)

**Date:** {YYYY-MM-DD}
**Evaluators:** {names or "single-evaluator"}

### Procedure

Both evaluators independently scored the same 10 tasks without consulting each other.

### Results

**Agreement rate:** {X}/10 = {Y}%
**Score delta average:** {Z} (mean absolute difference)

### Resolution

- [ ] **Calibrated (agreement ≥ 80%):** Proceed with full evaluation
- [ ] **Discuss and re-score:** Below threshold — resolve discrepancies, clarify rubric
```

Store: `docs/adr/evidence/0113/evaluations/00-calibration.md`

#### Phase 5b: Cross-Validate with ADR-0085

If ADR-0085 (shuffle-driven) has been run, compare findings before finalizing recommendations:

```markdown
## Cross-Validation: ADR-0113 ↔ ADR-0085

**ADR-0113 run:** {date / task sample}
**ADR-0085 run:** {date / seed range}

### Correlation Table

| Finding | ADR-0113 | ADR-0085 | Correlation | Action |
|---------|----------|----------|-------------|--------|
| Token: {X} | gap: missing-token | score 5 (coherent) | **Task-only signal** | Validate with next shuffle |
| Token: {Y} | gap: undiscoverable | edit recommended | **Aligned** | Proceed with priority |
| Skill: {S} | gap: skill-guidance-wrong | n/a | **Single-signal** | Validate with shuffle |
| Method: {M} | gap: missing-token | no issues | **Confirmed gap** | Add to recommendations |

### Findings Summary

- **Confirmed:** {both processes agree on gap}
- **Aligned:** {related issues, same root cause}
- **Task-only:** {gaps found only in task analysis — validate with shuffle}
- **Shuffle-only:** {coherence issues not affecting real tasks — lower priority}
```

Store: `docs/adr/evidence/cross-validation/{date}.md`

#### Process Health Check

After cross-validation (or after aggregating recommendations if ADR-0085 has not been run), run a `probe gap` pass on the cycle's aggregated findings. This is not a diagnostic for any specific gap type — it surfaces implicit assumptions in the evaluation process itself before human review.

```bash
bar build probe gap \
  --subject "$(cat docs/adr/evidence/0113/gap-catalog.md)" \
  --addendum "Surface implicit assumptions in this refinement cycle: what is this process treating as settled that may not be? Consider: task taxonomy scope, gap type boundaries, coverage rubric definitions, the separation between skill error and catalog gap, what counts as sufficient evidence."
```

Questions this step is designed to surface:

- Does the gap taxonomy treat `undiscoverable-token` and `skill-guidance-wrong` as cleanly separable when the root cause is often shared?
- Does the task taxonomy's probability weighting treat LLM-estimated frequency as a reliable proxy for actual usage?
- Are coverage scores treating the five rubric dimensions as independent when they are entangled?
- Does the process assume that fixing skill guidance is sufficient when the catalog description is also contributing?

Capture output as a brief note appended to `gap-catalog.md` before handing off to human review.

#### Post-Apply Validation

After applying changes, re-test original evidence cases to confirm the fix worked:

```markdown
## Post-Apply Validation

**Applied changes:** {list from recommendations.yaml}
**Validation date:** {YYYY-MM-DD}

### Regression Check

| Recommendation | Original evidence | Re-test result | Status |
|----------------|-------------------|----------------|--------|
| add: token X | task_T07, task_T14 | New token available | ✓ Pass |
| edit: token Y | task_T12 | Re-evaluated with new description | ✓ Pass |
| skill-update: {S} | task_T19 | Re-ran task with updated skill | ✗ Fail |

### Failed Validations

- {list any failures with likely cause and action}
```

Store: `docs/adr/evidence/0113/post-apply/{date}.md`

### Skill Update Impact Tracking

If the applied changes include skill updates (heuristics, Usage Patterns), track whether they improved outcomes:

```markdown
## Skill Update Impact: {skill name}

**Original recommendation:** {date from recommendations.yaml}
**Update applied:** {date}
**File modified:** {path to skill file}

### Pre-Update Baseline

Original task sample used for gap detection:
- Tasks: {T01, T07, T12}
- Pre-update coverage scores: {list}

### Post-Update: Original Evidence Re-Test

| Task | Pre-update score | Post-update score | Delta |
|------|------------------|-------------------|-------|
| T01  | 2                | 4                 | +2    |
| T07  | 3                | 3                 | 0     |
| T12  | 1                | 2                 | +1    |

### Post-Update: Fresh Task Sample

To avoid overfitting to original sample, generate 5 new tasks from the same domain:

| Task | Coverage score | Notes |
|------|----------------|-------|
| T_new_01 | 4 | Good coverage |
| T_new_02 | 3 | Similar gap to original |
| T_new_03 | 5 | Full coverage |
| T_new_04 | 3 | Gap persists: {reason} |
| T_new_05 | 4 | Good coverage |

### Analysis

- Original tasks improved: {X}/3
- Fresh sample average: {Y}/5
- Fresh sample vs pre-update average: {comparison}

### Verdict

- [ ] **Effective:** Fresh sample average ≥ pre-update average AND original tasks improved
- [ ] **Partial:** Some improvement but gaps remain
- [ ] **Ineffective:** No meaningful improvement or regressions

**Next steps:**
- {for effective: document improvement, close tracking}
- {for partial: iterate on skill update}
- {for ineffective: revert or try catalog-level fix instead}
```

Store: `docs/adr/evidence/0113/skill-updates/{skill-name}-{date}.md`

---

## Consequences

### Positive

- **Closes the coverage blind spot in ADR-0085**: Random shuffles cannot reveal that a task
  type is unrepresentable — only starting from the task can surface that gap.
- **Makes skills a first-class test subject**: Bar skills are tested against realistic tasks,
  not described in the abstract. Skill guidance issues become empirically visible.
- **Gap taxonomy creates actionable signal**: The four gap types map directly to recommendation
  actions (add / edit / skill-update / document), avoiding the ambiguity of "something is wrong."
- **`variants` form generates taxonomy naturally**: Using bar's own `variants` form to enumerate
  task types is self-consistent — it tests the catalog tool with the catalog itself, and the
  form's built-in probability framing is exactly what the taxonomy requires.

### Tradeoffs

- **Requires LLM in the loop**: Unlike `bar shuffle`, task-gap evaluation cannot be scripted
  without an LLM performing the skill application step. Each cycle requires active Claude
  participation.
- **Task taxonomy depends on LLM judgment**: The probability weights are estimated, not measured
  from telemetry. They reflect what Claude believes is common, which may differ from actual usage.
  If real usage data becomes available, it should replace the generated taxonomy.
- **Skill evaluation is noisy**: Different LLM runs may select different tokens for the same task.
  Run each task through the skill at least twice and note selection variance as part of the
  evaluation.
- **Calibration phase adds upfront time**: But improves score quality and inter-evaluator reliability
- **Cross-validation requires ADR-0085**: Both processes need to run for full correlation

### Risks

- **Taxonomy staleness**: The generated task list reflects the world at generation time. Re-run
  the taxonomy generation step whenever the scope of bar usage changes significantly.
- **Conflating skill error with catalog gap**: A skill that misroutes a task (gap type 3) and a
  catalog that lacks the right token (gap type 1) can look identical from the outside. Careful
  gap diagnosis is required: check whether a token *exists* before concluding it is missing.
- **LLM quality gaps**: Catalog and skill fixes don't address model execution failures
- **Cross-validation contradiction**: Processes may disagree on findings, unclear which to trust

---

## Future Extensions

- **Telemetry-grounded taxonomy**: If usage patterns become available, replace the LLM-estimated
  probability weights with observed task frequencies
- **Cross-process correlation**: Tokens that score low in ADR-0085 coherence *and* fail to surface
  in ADR-0113 task analysis are candidates for immediate retirement
- **Automated skill testing harness**: Script the bar-autopilot skill application step using the
  Claude API to allow faster, repeatable cycle runs
- **Coverage heatmap**: Visualise which task domains are well-covered vs. gapped across cycles
- **LLM execution quality tracking**: Aggregate failure modes across cycles to identify systematic model issues
- **Skill update impact tracking**: Measure whether skill changes improve coverage on new task samples

---

*In-flight loop progress is tracked in the sibling work-log file:
`0113-task-gap-driven-catalog-refinement.work-log.md`.
Detailed evidence is under `docs/adr/evidence/0113/`.*
