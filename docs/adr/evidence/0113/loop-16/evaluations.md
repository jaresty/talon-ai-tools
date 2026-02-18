# ADR-0113 Loop-16 Evaluations

**Date:** 2026-02-18
**Binary:** /tmp/bar-new (built from source)
**Focus:** Fresh health check across uncovered token areas:
  - Scope: struct, cross, view, thing (no use_when)
  - Form: contextualise, variants, socratic (no use_when)
  - Channel: diagram, slack, jira (explicit names — high discoverability expected)

---

## GH16-T01 — Map microservice dependencies

**Task:** "Map out all the dependencies between our microservices — what depends on what?"

**Expected tokens:** probe struct full mapping

**Skill selection:**
- Task: probe (surfacing structure)
- Scope: struct ("dependencies between" → struct: "arrangement and relationships, dependencies, coordination" ✅)
- Method: mapping ("map out all" → mapping: "surface elements and relationships" ✅)
- Completeness: full

**Bar command:** `bar build probe struct full mapping`

**Scores:** fitness 5, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Notes:** struct and mapping are description-anchored — "dependencies" and "map out" appear in the
descriptions verbatim. No use_when needed; discoverability is solid.

---

## GH16-T02 — Error handling consistency across codebase

**Task:** "Where is error handling scattered across our codebase? Is it consistent?"

**Expected tokens:** probe cross full

**Skill selection:**
- Task: probe
- Scope: cross ("error handling scattered across" → cross: "cross-cutting concerns that propagate across distinct units")
- Completeness: full

**Bar command:** `bar build probe cross full`

**Risk:** Without use_when, autopilot may select `motifs` ("recurring patterns across multiple places")
instead of `cross`. Both apply to "repeated across" scenarios; the distinction is:
- cross = concerns that SPAN and PROPAGATE (error handling is a canonical cross-cutting concern)
- motifs = patterns that REPEAT at multiple sites (structural similarity, not spanning)

"Scattered across" and "inconsistent" signal spanning, not just repetition. But autopilot can't see
this distinction without routing guidance.

**Scores:** fitness 4, completeness 4, correctness 3, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: GH16-T02
token: cross
axis: scope
observation: >
  'cross' scope is appropriate for cross-cutting concern analysis ("where is X across the codebase"),
  but 'motifs' ("recurring patterns appearing in multiple places") is a near-competitor that
  description-anchored routing would plausibly select instead. The cross description does not include
  the user-natural phrases "scattered across", "spans multiple services", "cross-cutting concern",
  or "horizontal consistency", so autopilot may not distinguish it from motifs.
recommendation:
  action: edit (use_when)
  token: cross
  axis: scope
  proposed_addition: >
    Cross-cutting concerns spanning the system: user asks about a concern that appears across
    many unrelated modules (logging, error handling, auth, observability). Heuristic:
    'scattered across', 'spans multiple services', 'consistent across', 'cross-cutting',
    'appears throughout', 'horizontal concern', 'error handling across our codebase',
    'where does X live across the system' → cross scope. Distinct from motifs scope
    (motifs = structural patterns that repeat; cross = concerns that PROPAGATE and SPAN).
```

---

## GH16-T03 — CI/CD pipeline from new developer perspective

**Task:** "How does our CI/CD pipeline look from a new developer's perspective?"

**Expected tokens:** show view full

**Skill selection:**
- Task: show
- Scope: view ("from a new developer's perspective" → view: "how the subject appears from a specific
  stakeholder or positional perspective" ✅ — exact match)
- Completeness: full

**Bar command:** `bar build show view full`

**Scores:** fitness 5, completeness 4, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "from the perspective of" is such a natural anchor for view that description-anchored
routing fires reliably. No use_when needed.

---

## GH16-T04 — Bounded entities in domain model

**Task:** "What are all the bounded entities in our domain model?"

**Expected tokens:** probe thing full

**Skill selection:**
- Task: probe
- Scope: thing ("bounded entities" → thing: "entities and bounded units" ✅ — exact phrase match)
- Completeness: full

**Bar command:** `bar build probe thing full`

**Scores:** fitness 5, completeness 4, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "bounded entities" is an exact phrase match to thing's description. Very discoverable.

---

## GH16-T05 — Event sourcing decision in context

**Task:** "Put our event sourcing decision in context — why was it chosen and what are the broader
implications?"

**REVISED ASSESSMENT (post-loop):** This task was originally scored as a contextualise gap, but
the gap diagnosis was based on a misunderstanding of contextualise's intent. Contextualise is for
packaging content to be passed to another LLM operation — not for explaining a decision to a human.
The correct command for this task is `bar build show mean full` (or `show mean full time`), and
that produces a score-5 result. contextualise is NOT the right token here.

**Correct tokens:** show mean full

**Skill selection:**
- Task: show
- Scope: mean ("why was it chosen" → conceptual meaning and rationale ✅)
- Completeness: full

**Bar command:** `bar build show mean full`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Revised gap diagnosis:** None — `show mean full` is the correct and discoverable command.
The earlier gap diagnosis (G-L16-02) was a false positive caused by misidentifying contextualise's
intent. contextualise is an LLM-pipeline token; this is a human-explanation task.

**Correction applied:** contextualise form description revised (b8fee40, 1e829d8) and use_when
updated to reflect LLM-pipeline intent. GH16-T05 was a wrong-token-expected error, not a
discoverability gap.

---

## GH16-T06 — Several approaches to connection pool exhaustion

**Task:** "Give me several different approaches to solving our DB connection pool exhaustion problem."

**Expected tokens:** pick full variants

**Skill selection:**
- Task: pick (selecting from alternatives)
- Form: variants ("several different approaches" → variants: "presents several distinct,
  decision-ready options" ✅)
- Completeness: full

**Bar command:** `bar build pick full variants`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "Several different approaches" is an exact match to variants' description phrasing.
Very discoverable from description alone.

---

## GH16-T07 — GraphQL adoption with assumption-challenging

**Task:** "Help me think through whether to adopt GraphQL, but challenge my assumptions as we go."

**Expected tokens:** probe mean full socratic

**Skill selection:**
- Task: probe (thinking through a decision)
- Scope: mean (what GraphQL means, framing)
- Form: socratic ("challenge my assumptions as we go" → socratic: "question-led method that surfaces
  assumptions")
- Completeness: full

**Bar command:** `bar build probe mean full socratic`

**Risk:** "Challenge my assumptions" could route to `adversarial` METHOD (stress-testing,
constructive challenge) rather than `socratic` FORM (question-led dialogue). Key distinction:
- adversarial: challenge the design/proposal by finding weaknesses
- socratic: engage via questions to surface user's own assumptions

Without use_when, autopilot likely selects `adversarial` method (which lives in a more prominent
axis) rather than `socratic` form (which requires understanding the form token name means
question-led dialogue).

**Scores:** fitness 4, completeness 4, correctness 3, clarity 3 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: GH16-T07
token: socratic
axis: form
observation: >
  'socratic' form produces question-led dialogue that surfaces the user's own assumptions,
  but "challenge my assumptions" routes naturally to the 'adversarial' method (stress-test
  the subject). The distinction is: adversarial = challenge the design; socratic = ask the
  USER probing questions. The form name "socratic" requires familiarity with the Socratic
  method. Without use_when, autopilot selects adversarial (a method token, more prominent)
  and misses the dialogue-oriented form structure entirely.
recommendation:
  action: edit (use_when)
  token: socratic
  axis: form
  proposed_addition: >
    Question-led dialogue to surface the user's own thinking: user wants to be asked
    questions rather than given answers, or wants to reason through a topic interactively.
    Heuristic: 'ask me questions', 'help me think through', 'challenge my assumptions
    with questions', 'Socratic dialogue', 'probe my thinking', 'question me as we work
    through this', 'help me reason this out' → socratic. Distinct from adversarial
    method (adversarial = stress-test the design; socratic = question the USER's reasoning
    via dialogue).
```

---

## GH16-T08 — Auth middleware flow diagram

**Task:** "Draw a flow diagram showing how requests pass through our auth middleware."

**Expected tokens:** show struct full diagram

**Skill selection:**
- Task: show
- Scope: struct ("how requests pass through" → struct: arrangement and relationships between components)
  OR time ("flow" = sequence over time)
- Channel: diagram ("flow diagram", "draw" → explicit diagram channel ✅)
- Completeness: full

**Bar command:** `bar build show struct full diagram`

**Scores:** fitness 5, completeness 4, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "diagram", "flow diagram", and "draw" all trigger the diagram channel reliably.
The explicit channel name makes this trivially discoverable.

---

## GH16-T09 — Incident summary for Slack

**Task:** "Summarize this incident for our team Slack channel — brief and clear."

**Expected tokens:** pull gist slack

**Skill selection:**
- Task: pull (extracting/summarizing)
- Completeness: gist ("brief" → gist ✅)
- Channel: slack ("Slack channel" → explicit ✅)

**Bar command:** `bar build pull gist slack`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "Slack" is named explicitly. "Brief" triggers gist use_when. Pull+gist+slack is
an excellent fit. Channel name discoverability is highest tier.

---

## GH16-T10 — Jira ticket for rate limiting feature

**Task:** "Write a Jira ticket for the API rate limiting feature we need to build."

**Expected tokens:** make full jira

**Skill selection:**
- Task: make (creating new content)
- Channel: jira ("Jira ticket" → explicit ✅)
- Completeness: full

**Bar command:** `bar build make full jira`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "Jira ticket" is explicit. Highest tier discoverability.

---

## Summary

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| GH16-T01 | struct + mapping | 4 | No |
| GH16-T02 | cross scope | 3 | Yes — G-L16-01 |
| GH16-T03 | view scope | 5 | No |
| GH16-T04 | thing scope | 5 | No |
| GH16-T05 | contextualise form | 3 | Yes — G-L16-02 |
| GH16-T06 | variants form | 5 | No |
| GH16-T07 | socratic form | 3 | Yes — G-L16-03 |
| GH16-T08 | diagram channel | 5 | No |
| GH16-T09 | slack channel | 5 | No |
| GH16-T10 | jira channel | 5 | No |

**Mean: 4.3/5** (above 4.0 target)

**3 gaps found** (all score 3, all undiscoverable-token type):
1. **G-L16-01**: `cross` scope — competes with `motifs`; needs user-phrasing use_when
2. **G-L16-02**: `contextualise` form — description targets LLM-to-LLM use; needs user-phrasing use_when
3. **G-L16-03**: `socratic` form — competes with `adversarial` method; needs dialogue-oriented use_when

**No regressions** — tokens covered in loops 11–15 all remain at score 4–5.

### New Gap Inventory: Loop 16

| ID | Token | Axis | Gap type | Rec action |
|----|-------|------|----------|-----------|
| G-L16-01 | cross | scope | undiscoverable-token | add use_when |
| G-L16-02 | contextualise | form | undiscoverable-token | add use_when |
| G-L16-03 | socratic | form | undiscoverable-token | add use_when |
