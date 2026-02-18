# ADR-0113 Loop-18 Evaluations

**Date:** 2026-02-18
**Binary:** /tmp/bar-new (built from source)
**Focus:** Final untested form tokens: questions, direct, cards, quiz, story, log, merge,
           checklist, table, bullets

---

## GH18-T01 — What questions to ask about a timeout

**Task:** "I'm trying to understand why our service keeps timing out — what questions should I
be asking?"

**Expected tokens:** probe fail full questions

**Skill selection:**
- Task: probe (investigating a problem)
- Scope: fail (timeouts = failure modes)
- Form: questions ("what questions should I be asking" → questions: "presents the answer as a
  series of probing or clarifying questions rather than statements")
- Completeness: full

**Bar command:** `bar build probe fail full questions`

**Risk:** `questions` form is counterintuitive — the response IS a list of questions, not answers.
Without use_when, two failure modes:
1. Autopilot selects `socratic` (also generates questions, has a use_when). Distinction:
   - socratic = LLM asks the USER questions interactively to surface their thinking
   - questions = response IS a structured list of investigation questions for the user to pursue
2. Autopilot answers directly (probe+fail) without adding questions form, producing a statement-
   based analysis instead of a question-structured diagnostic guide.

The user phrase "what questions should I be asking" is asking for the questions themselves as
content — this maps to the `questions` form, not to socratic. But the socratic use_when
('ask me questions', 'help me think through') partially overlaps with this phrasing.

**Scores:** fitness 4, completeness 4, correctness 3, clarity 3 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: GH18-T01
token: questions
axis: form
observation: >
  'questions' form structures the response as a list of probing questions (for the user
  to investigate), but competes with 'socratic' form (which interactively asks the user
  questions). The distinction is: socratic = LLM asks USER questions in dialogue;
  questions = response IS a question-list artifact the user takes away. Without use_when,
  autopilot may select socratic or omit questions entirely. User phrases like "what
  questions should I be asking" should route to questions form.
recommendation:
  action: edit (use_when)
  token: questions
  axis: form
  proposed_addition: >
    Response structured as a list of investigation or clarification questions: user wants
    the response itself to be a set of questions they can pursue, not statements or
    answers. Heuristic: 'what questions should I ask', 'give me questions to investigate',
    'what should I be asking about', 'frame this as questions', 'questions I should
    explore', 'diagnostic questions for' → questions. Distinct from socratic form
    (socratic = LLM asks the USER questions interactively to surface their thinking;
    questions = response IS a question-list artifact the user takes away).
```

---

## GH18-T02 — Bottom line on Kubernetes migration, answer first

**Task:** "What's the bottom line on whether we should migrate to Kubernetes? Give me the answer
first, then the reasoning."

**Expected tokens:** pick full direct

**Skill selection:**
- Task: pick (selecting from alternatives)
- Form: direct ("give me the answer first" → direct: "leading with the main point or
  recommendation, followed only by the most relevant supporting context" ✅)
- Completeness: full

**Bar command:** `bar build pick full direct`

**Scores:** fitness 5, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Notes:** "give me the answer first" and "bottom line" both map to direct's "leading with the
main point." Description-anchored, no use_when needed.

---

## GH18-T03 — Architecture as presentation cards

**Task:** "Break down our architecture into discrete cards I can use for a presentation."

**Expected tokens:** show struct full cards

**Skill selection:**
- Task: show
- Scope: struct (architecture = arrangement and relationships)
- Form: cards ("discrete cards... for a presentation" → cards: "discrete cards or items, each
  with a clear heading and short body" ✅ — "cards" is explicit in request)
- Completeness: full

**Bar command:** `bar build show struct full cards`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "cards" is named explicitly in the request. Trivially discoverable.

---

## GH18-T04 — Quiz on event-driven architecture

**Task:** "Test my understanding of event-driven architecture with a quiz."

**Expected tokens:** show mean full quiz

**Skill selection:**
- Task: show (explaining and testing)
- Scope: mean (conceptual understanding)
- Form: quiz ("test my understanding... with a quiz" → quiz ✅ — explicit name)
- Completeness: full

**Bar command:** `bar build show mean full quiz`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "quiz" is explicit. Trivially discoverable.

---

## GH18-T05 — User story for rate limiting

**Task:** "Write a user story for our API rate limiting feature."

**Expected tokens:** make full story

**Skill selection:**
- Task: make (creating)
- Form: story ("user story" → story: "formats the backlog item as a user story using As a/
  I want/so that" ✅ — "user story" is explicit)
- Completeness: full

**Bar command:** `bar build make full story`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "user story" is both the request phrasing and the description phrasing. Trivially
discoverable.

---

## GH18-T06 — Log entry for architecture review findings

**Task:** "Write up a brief log entry of what we discovered during the architecture review."

**Expected tokens:** make full log

**Skill selection:**
- Task: make (creating a record)
- Form: log ("log entry" → log: "work or research log entry with date or time markers...
  short bullet-style updates" ✅ — "log entry" is explicit)
- Completeness: full

**Bar command:** `bar build make full log`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "log entry" is explicit in request. Trivially discoverable.

---

## GH18-T07 — Combine three design documents

**Task:** "We have three separate design documents for the payments service — combine them into
one coherent overview."

**Expected tokens:** make full merge

**Skill selection:**
- Task: make (creating combined output)
- Form: merge ("combine them into one coherent" → merge: "combines multiple sources into a
  single coherent whole while preserving essential information" ✅ — near-exact match)
- Completeness: full

**Bar command:** `bar build make full merge`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "combine... into one coherent" maps directly to merge's description. Discoverable.

---

## GH18-T08 — Pre-deployment verification checklist

**Task:** "Give me a checklist of everything to verify before deploying to production."

**Expected tokens:** check full checklist

**Skill selection:**
- Task: check (verifying)
- Form: checklist ("checklist" → checklist: "actionable checklist whose items are clear
  imperative tasks" ✅ — explicit name in request)
- Completeness: full

**Bar command:** `bar build check full checklist`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "checklist" is explicit. Trivially discoverable.

---

## GH18-T09 — Compare caching options across dimensions

**Task:** "Compare Redis vs Memcached vs PostgreSQL for caching across key dimensions."

**Expected tokens:** diff full table

**Skill selection:**
- Task: diff (comparing subjects)
- Form: table ("compare across key dimensions" → table: "presents the main answer as a
  Markdown table" — comparison across dimensions naturally maps to tabular format)
- Completeness: full

**Bar command:** `bar build diff full table`

**Scores:** fitness 5, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Notes:** "compare across dimensions" is a strong table signal. The diff task + multiple
subjects also suggest table format. Partially description-anchored, no use_when needed.

---

## GH18-T10 — Bullet-point summary of architectural decision

**Task:** "Summarize the main points of our architectural decision — just bullet points please."

**Expected tokens:** pull gist bullets

**Skill selection:**
- Task: pull (extracting/summarizing)
- Completeness: gist (summary of main points)
- Form: bullets ("just bullet points" → bullets: "organizes ideas as concise bullet points" ✅
  — "bullet points" explicit in request)

**Bar command:** `bar build pull gist bullets`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "bullet points" is explicit. Trivially discoverable.

---

## Summary

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| GH18-T01 | questions form | 3 | Yes — G-L18-01 |
| GH18-T02 | direct form | 4 | No |
| GH18-T03 | cards form | 5 | No |
| GH18-T04 | quiz form | 5 | No |
| GH18-T05 | story form | 5 | No |
| GH18-T06 | log form | 5 | No |
| GH18-T07 | merge form | 5 | No |
| GH18-T08 | checklist form | 5 | No |
| GH18-T09 | table form | 4 | No |
| GH18-T10 | bullets form | 5 | No |

**Mean: 4.6/5** (highest single-loop mean to date)

**1 gap found** (undiscoverable-token):
- **G-L18-01**: `questions` form — counterintuitive (response IS questions, not answers);
  competes with `socratic` (which also generates questions via dialogue).

**Confirmed discoverable without use_when:** direct, cards, quiz, story, log, merge, checklist,
table, bullets — all either description-anchored or have explicit names in natural user phrasing.
