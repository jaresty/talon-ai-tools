# Tasks T16 + T18 — Task misclassification for extraction and quality tasks

---

## Task T16 — Summarise complex technical content

**Task description:** "Summarise this 50-page RFC for the engineering team"
**Probability weight:** 3%
**Domain:** writing

### Skill selection log

Bar-autopilot sees this as an explanation/description task:
- Task: `show` (explains or describes the subject for the stated audience)
- Completeness: `gist` (short, touches main points)
- Scope: `mean` (conceptual understanding, purpose, framing)
- No method or form selected

**Bar command (autopilot):** `bar build show gist mean`

**Better command:** `bar build pull gist mean`

### Why pull is better

- `show` = "explains or describes the subject for the stated audience" — explains TO someone
- `pull` = "extracts a targeted subset of the input for inspection, filtering, or reuse" — extracts FROM a source

Summarisation is extraction: given a long document (the SUBJECT), pull out the key points.
`pull` more precisely instructs the LLM to perform extraction rather than explanation.
The distinction matters: `show` risks rephrasing the subject, while `pull` instructs the
LLM to compress and extract.

### Coverage scores
- Token fitness: 3 (show functional but pull is more precise)
- Token completeness: 3 (missing a method for "focus on the most important aspects")
- Skill correctness: 3 (skill routes summarisation to show task, not pull)
- Prompt clarity: 3 (show+gist+mean produces a reasonable but imprecise prompt)
- **Overall: 3**

### Gap diagnosis

```yaml
gap_type: skill-guidance-wrong
task: T16 — Summarise complex content
dimension: task selection
observation: >
  Bar-autopilot routes summarisation tasks to 'show' because summarisation is
  "explaining" the content at a high level. But summarisation is semantically
  an extraction operation: given a long source document, extract a shorter version.

  'pull' task ("extracts a targeted subset for inspection, filtering, or reuse")
  better describes what summarisation does. pull+gist+mean says:
  "extract [pull] a short [gist] conceptual overview [mean] from this source."

  The skill guidance doesn't distinguish explanation ("show what this means") from
  extraction ("pull out the key points from this document"). Both feel like show-style
  tasks but they differ: explanation can work without a source document; extraction
  requires one. When a SUBJECT is provided and the task is to compress it, 'pull' is
  more appropriate than 'show'.

recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    Add a "Summarisation / Extraction" pattern:
    - When the task is to summarise an existing document/RFC/article: use 'pull + gist'
    - When the task is to explain a concept without a specific source: use 'show + mean'
    - Heuristic: if a SUBJECT is long content to be compressed, 'pull' is likely correct;
      if a SUBJECT is a topic name or concept to explain, 'show' is likely correct
    Example: bar build pull gist mean --subject "[long RFC content]"
evidence: [T16]
```

---

## Task T18 — Create test plan / identify test coverage gaps

**Task description:** "What tests are missing for this feature?" / "Create a test plan for the payment integration"
**Probability weight:** 3%
**Domain:** code

### Skill selection log

Bar-autopilot routes to quality evaluation:
- Task: `check` (evaluates or assesses the subject against criteria)
- Scope: `good` (quality/success criteria) + `fail` (failure cases, gaps)
- Form: `checklist`

**Bar command (autopilot):** `bar build check full good fail checklist`

**Problem:** The task taxonomy entry covers two distinct sub-tasks:
1. "What tests are missing?" → evaluate coverage gaps → `check+fail checklist`
2. "Create a test plan" → produce a test plan artifact → `make+act+fail checklist`

These are different tasks requiring different bar commands.

### Coverage scores
- Token fitness: 3 (check works for gap analysis but not for creating a test plan)
- Token completeness: 3 (ambiguous task means no single command can serve both)
- Skill correctness: 3 (skill can't distinguish the two sub-tasks without user clarification)
- Prompt clarity: 3 (check+good+fail checklist is functionally reasonable for gap analysis only)
- **Overall: 3**

### Gap diagnosis

```yaml
gap_type: skill-guidance-wrong
task: T18 — Create test plan / identify coverage gaps
dimension: task disambiguation
observation: >
  "Test plan" tasks split into two distinct operations that need different bar tasks:

  1. COVERAGE GAP ANALYSIS ("what's missing?"): check + good + fail checklist
     - check = evaluate/assess
     - good = quality/coverage standards
     - fail = what falls short
     - Produces: list of missing test cases

  2. TEST PLAN CREATION ("create a test plan"): make + act + fail checklist
     - make = create an artifact
     - act = behavioral actions/scenarios
     - fail = failure cases and edge cases to cover
     - Produces: a test plan document

  Bar-autopilot routes both to check-based quality evaluation because "testing" is
  associated with checking/evaluation. But creating a test plan is an artifact
  production task (make), not an evaluation task (check).

  The skill needs to ask: is the user evaluating existing coverage OR creating a
  new test plan? The question "what tests are missing?" is check-based; "write a
  test plan" is make-based.

recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    Add disambiguation for test-related tasks:
    - Test coverage gap analysis ("what tests are missing?", "where are gaps?"):
      bar build check full good fail checklist
    - Test plan creation ("write a test plan", "create test cases"):
      bar build make full act fail checklist
    Heuristic: if the user is asking what's missing = check; if creating = make.
evidence: [T18]
```
