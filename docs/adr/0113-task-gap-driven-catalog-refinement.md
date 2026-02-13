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

#### Gap Type 4: Out of Scope

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
- Method: considered {options} → chose / rejected: {token} (reason)
- Form: {token or none} (reason)
- Channel: {token or none} (reason)
- Persona: {selection} (reason)

**Bar command constructed:**
bar build {tokens}

**Coverage scores:**
- Token fitness: {1-5}
- Token completeness: {1-5}
- Skill correctness: {1-5}
- Prompt clarity: {1-5}
- **Overall: {1-5}**

**Gap diagnosis:** {gap type or "none"}
{Gap YAML block if applicable}

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

---

## Implementation

### Refinement Cycle

Run this process when:
- The skill documentation (bar-autopilot, bar-manual, bar-suggest) has changed significantly
- A new domain of tasks is suspected to be underserved
- ADR-0085 shuffle cycles show consistently high scores (noise is low) but user feedback suggests gaps

Steps:
1. **Generate taxonomy** — run bar probe + variants, capture task list with weights
2. **Sample** — draw 20-30 tasks proportional to weight
3. **Apply skills** — for each task, run bar-autopilot to select tokens and build prompt
4. **Score** — evaluate coverage on four dimensions
5. **Diagnose** — classify gaps by type for all tasks scoring ≤3
6. **Aggregate** — group by gap type, identify recurring patterns
7. **Recommend** — produce actionable list with evidence
8. **Review** — human review before implementing
9. **Apply** — edit catalog, skills, or help_llm.go; regenerate grammar
10. **Validate** — re-run a sample of gapped tasks to confirm improvement

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

### Risks

- **Taxonomy staleness**: The generated task list reflects the world at generation time. Re-run
  the taxonomy generation step whenever the scope of bar usage changes significantly.
- **Conflating skill error with catalog gap**: A skill that misroutes a task (gap type 3) and a
  catalog that lacks the right token (gap type 1) can look identical from the outside. Careful
  gap diagnosis is required: check whether a token *exists* before concluding it is missing.

---

## Future Extensions

- **Telemetry-grounded taxonomy**: If usage patterns become available, replace the LLM-estimated
  probability weights with observed task frequencies
- **Cross-process correlation**: Tokens that score low in ADR-0085 coherence *and* fail to surface
  in ADR-0113 task analysis are candidates for immediate retirement
- **Automated skill testing harness**: Script the bar-autopilot skill application step using the
  Claude API to allow faster, repeatable cycle runs
- **Coverage heatmap**: Visualise which task domains are well-covered vs. gapped across cycles
