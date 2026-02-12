# ADR-0107: Interactive Form Conflicts, adr Channel Affinity, and Context-Affine Form Guidance

## Status
Completed

## Context

Cycle 5 of the shuffle-driven catalog refinement process (seeds 0081–0100, ADR-0085 evidence)
produced a mean score of 3.65/5 — an improvement from cycle 4's 3.4/5 — with 20% of seeds still
scoring ≤2. Four distinct problem categories emerged, all new patterns not yet documented.

**Evaluation evidence base:**
- Cycle 5: seeds 0081–0100 (65% excellent, 15% acceptable, 20% problematic/broken)
- ADR-0106 improvements were visible: fix task clarification confirmed implemented (seed 0099),
  prose-form / code-channel conflict rule in place
- Persistent gap: interactive/dialogue form tokens conflict with output-exclusive static channels —
  this class was absent from ADR-0106's prose-form conflict rule
- New task-affinity failure: `sort` + `adr` channel (same class as codetour/gherkin, new instance)
- Two context-affinity observations: `scaffold` form mismatched with executive personas;
  `bug` form creates semantic friction on non-debugging tasks

---

## Decision 1: Extend Form/Channel Conflicts to Interactive Forms

### Problem

ADR-0106 Decision 2 documented a prose-form / code-channel conflict rule: form tokens that produce
structured prose (`case`, `formats`, `walkthrough`, `scaffold`, etc.) conflict with code-or-markup
channels (`code`, `html`, `shellscript`). However, the rule was scoped too narrowly in two ways:

**Gap 1: Interactive forms were omitted**

`cocreate`, `quiz`, and `facilitate` are interactive/dialogue form tokens. They require
back-and-forth exchange to function — proposing moves, receiving responses, iterating.
They conflict with any output-exclusive static channel, not just code channels:

- `cocreate` + `svg` (seed 0082): cocreate requires prose dialogue; svg mandates a single static
  SVG file. Scored 2/5.
- `quiz` + `presenterm` (seed 0085): quiz requires interactive Q&A flow; presenterm requires a
  static multi-slide Markdown deck. Scored 2/5.

These are the same conflict class (interactive/dialogue form vs. static output format), but the
existing rule names only prose-structure forms, not interactive-dialogue forms.

**Gap 2: The rule only covers code channels, not presenterm/svg/sync**

`presenterm` and `svg` are also output-exclusive static channels. The existing prose-form conflict
rule lists `code`, `html`, `shellscript` but omits `presenterm`, `svg`, and other output-exclusive
channels. The rule should apply to all output-exclusive static channels.

### Decision

**1a. Add interactive-form category to the conflict rule in `bar help llm` § Incompatibilities:**

Extend the "Prose-form conflicts" entry to cover interactive forms:

> **Interactive-form conflicts:** Form tokens that require back-and-forth dialogue (`cocreate`,
> `quiz`, `facilitate`) conflict with all output-exclusive static channels (`code`, `html`,
> `shellscript`, `svg`, `presenterm`, `adr`, `codetour`, `gherkin`, `diagram`). These forms
> require a live exchange to function — they cannot be expressed as a single static artifact.
> Use interactive forms only with channels that support natural language (`jira`, `slack`,
> `sketch`, `plain`, `remote`, `sync`) or with no channel token.

**1b. Extend the existing prose-form conflict rule to list all output-exclusive channels:**

Update the existing prose-form conflict entry to replace `code`, `html`, `shellscript` with the
full list:

> Form tokens that produce structured prose (`case`, `formats`, `walkthrough`, `scaffold`,
> `recipe`, `faq`, `table`, `taxonomy`, `visual`, `variants`, `checklist`, `actions`) conflict
> with channels that mandate a fixed non-prose output format (`code`, `html`, `shellscript`,
> `svg`, `presenterm`, `adr`, `codetour`, `gherkin`, `diagram`).

**1c. Add interaction-type notes to `cocreate`, `quiz`, and `facilitate` form descriptions:**

> `cocreate` (add): "Interactive form — requires back-and-forth dialogue. Conflicts with
> output-exclusive static channels (`code`, `html`, `shellscript`, `svg`, `presenterm`,
> `adr`, `codetour`, `gherkin`, `diagram`). Use only with conversational channels or no channel."

> `quiz` (add): "Interactive form — requires a live Q&A exchange. Conflicts with output-exclusive
> static channels. Use only with conversational channels or no channel."

> `facilitate` (add): "Interactive form — structures a group process rather than producing a
> single document. Conflicts with output-exclusive static channels. Use only with conversational
> channels or no channel."

---

## Decision 2: Add `adr` Channel to Task-Affinity Restrictions

### Problem

`sort` + `adr` channel scored 2/5 (seed 0091). The `sort` task produces a ranked or categorized
list; the `adr` channel mandates an Architecture Decision Record structure (Context, Decision,
Consequences). These are incompatible output types — an ADR is a decision artifact, not a
list artifact.

This is the same task-affinity failure pattern established for `codetour` and `gherkin` in
ADR-0105 D2 and extended to `code`/`html`/`shellscript` in ADR-0106 D1. The `adr` channel has
implicit task-affinity for decision-making tasks and conflicts with tasks that produce
non-decision outputs:

- `sort` (ordered/categorized list) → not a decision
- `pull` (extracted subset) → not a decision
- `diff` (comparison) → not a decision; comparison is a step *toward* a decision, not the decision itself

The `adr` channel is most coherent with:
- `plan` — architectural planning decisions map directly to ADR format
- `probe` — analysis leading to a documented architectural decision
- `make` — creating an ADR as a deliverable

### Decision

Add `adr` channel to task-affinity restrictions in `bar help llm` § Incompatibilities:

> `adr` channel: task-affinity for decision-making tasks (`plan`, `probe`, `make`). The ADR
> format (Context, Decision, Consequences) is a decision artifact — it does not accommodate
> tasks that produce non-decision outputs. Avoid with `sort` (sorted list), `pull` (extraction),
> `diff` (comparison), or `sim` (scenario playback).

Also add a task-affinity note to the `adr` channel description in `lib/axisConfig.py`:

> Most appropriate with decision-making tasks (`plan`, `probe`, `make`). Produces a structured
> decision record that does not accommodate non-decision outputs — avoid with `sort`, `pull`,
> `diff`, or `sim`.

---

## Decision 3: Document `sim` + `facilitate` Combination Guidance

### Problem

`sim` + `facilitate` appeared in 2 of 20 seeds in cycle 5 (seeds 0084 and 0093), both scoring 3/5.
The tension: `sim` assumes the LLM performs scenario playback directly; `facilitate` assumes the
LLM structures a group process in which others do the work. Combined, the response's role is
ambiguous — is the LLM simulating, or designing a facilitated simulation session?

The combination is not broken: "design a facilitation structure for a simulation exercise" is
a valid and useful interpretation. But the ambiguity costs a point without explicit user intent.

This is a recurring pattern — 10% of cycle 5 corpus — and affects any combination of `sim` with
an interactive form token (`cocreate`, `quiz`, `facilitate`).

### Decision

Add a disambiguation note to the `facilitate` form description (and note in `sim` task description)
clarifying the combined interpretation:

**`facilitate` (add to description):**
> When combined with `sim`, the response should design a facilitation structure for a simulation
> exercise (who does what, in what sequence, what prompts and turn-taking the facilitator manages)
> rather than performing the simulation directly. To have the LLM play out the scenario itself,
> omit `facilitate`.

**`sim` (add to description):**
> When paired with interactive form tokens (`facilitate`, `cocreate`, `quiz`), the response
> designs a structured exercise for others to perform the simulation rather than playing it out
> directly.

---

## Decision 4: Add Audience Guidance to `scaffold` Form

### Problem

`scaffold` form + `executive_brief` persona (probe + scaffold + CEO, seed 0092) scored 3/5.
`scaffold` is explicitly defined as "starts from first principles, uses concrete examples and
analogies, so a beginner can follow." The `executive_brief` persona addresses a CEO with
business impact and crisp asks. These pull in opposite directions: scaffolding assumes low
prior knowledge; an executive brief assumes high context and low tolerance for exposition.

The `scaffold` form is correctly defined and correctly categorized — but it lacks any signal
about appropriate audience level, making it easy to pair with the wrong persona.

### Decision

Add an audience note to the `scaffold` form description:

**`scaffold` (add to description):**
> Most effective with learning-oriented audiences (`teach_junior_dev`, junior engineer,
> student). May conflict with senior executive or expert personas (`executive_brief`,
> CEO audience) where first-principles exposition contradicts expected expertise.

---

## Decision 5: Add Context-Affinity Note to `bug` Form

### Problem

`bug` form + `sync` channel scored 2/5 (seed 0099). `bug` form structures output as a static
bug report (Steps to Reproduce, Expected Behavior, Actual Behavior, Environment); `sync` channel
requires a live session plan or agenda. These are incompatible output structures.

Additionally, `bug` form has strong debugging semantic associations — even when paired with the
correctly-clarified `fix` task (now a reformat task per ADR-0106 D5), the bug-report structure
creates semantic friction with non-debugging tasks. The form's debugging context is inherent in
its template structure, not just its name.

### Decision

Add a context-affinity note to the `bug` form description:

**`bug` (add to description):**
> Strongest with diagnostic and debugging tasks (`probe`, or `make`/`show` paired with diagnostic
> methods: `diagnose`, `inversion`, `adversarial`). Creates semantic friction with non-debugging
> tasks (e.g., `fix`, which is a reformat task in bar's grammar). Conflicts with session-plan
> channels (`sync`) — a bug report is a static artifact, not a live session agenda.

---

## Consequences

### Positive

- **Interactive-form conflict rule closes the remaining gap in ADR-0106 D2:** The existing
  prose-form rule covered structural prose forms but missed interactive/dialogue forms entirely.
  Decision 1 closes this gap and ensures cocreate, quiz, and facilitate are correctly documented
  as incompatible with any output-exclusive static channel.

- **adr task-affinity extends the pattern established by ADR-0105/0106:** sort+adr is the same
  failure class as sort+gherkin and sim+codetour. Adding adr to the task-affinity list makes the
  pattern coverage systematic.

- **sim+facilitate guidance prevents ambiguous compositions:** The combination is valid but
  requires user intent to be stated. The guidance disambiguates without prohibiting the combination.

- **scaffold and bug audience/context notes prevent persona mismatches:** These are lower-urgency
  but catch real friction patterns that recur across corpus seeds.

### Negative / Tradeoffs

- **Decision 1 (channel list expansion) increases maintenance surface:** The list of
  output-exclusive channels is now named in three places: the prose-form rule, the interactive-form
  rule, and individual token descriptions. If a new channel is added, all three locations need
  updating. A future ADR may introduce a single canonical list.

- **Decision 3 (sim+facilitate) deferred from prohibition to guidance:** The combination is
  not blocked, only explained. Users who don't read the note will still encounter the ambiguity.
  If the pattern continues to score 3/5 in subsequent cycles, a stronger note or soft prohibition
  should be considered.

---

## Follow-up Work

### Decision 1: Interactive form / static channel conflicts
**Files to change:**
- `internal/barcli/help_llm.go`: update `renderCompositionRules` — extend prose-form conflict
  rule to name all output-exclusive channels; add new interactive-form conflict rule
- `lib/axisConfig.py`: add interaction-type notes to `cocreate`, `quiz`, `facilitate` form
  descriptions
- `internal/barcli/embed/prompt-grammar.json`: same updates for cocreate, quiz, facilitate

### Decision 2: adr channel task-affinity
**Files to change:**
- `internal/barcli/help_llm.go`: add `adr` to § Task-affinity restrictions in
  `renderCompositionRules`
- `lib/axisConfig.py`: add task-affinity note to `adr` channel description
- `internal/barcli/embed/prompt-grammar.json`: same update

### Decision 3: sim + facilitate guidance
**Files to change:**
- `lib/axisConfig.py`: add disambiguation note to `facilitate` form description and `sim` task
  description
- `internal/barcli/embed/prompt-grammar.json`: same updates

### Decision 4: scaffold audience guidance
**Files to change:**
- `lib/axisConfig.py`: add audience note to `scaffold` form description
- `internal/barcli/embed/prompt-grammar.json`: same update

### Decision 5: bug form context-affinity
**Files to change:**
- `lib/axisConfig.py`: add context-affinity note to `bug` form description
- `internal/barcli/embed/prompt-grammar.json`: same update

### Ongoing: Test coverage
- `TestLLMHelpIncompatibilitiesPopulated` should be extended to verify:
  - The interactive-form conflict rule text is present
  - The `adr` task-affinity entry is present
