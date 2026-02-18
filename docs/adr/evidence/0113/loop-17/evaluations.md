# ADR-0113 Loop-17 Evaluations

**Date:** 2026-02-18
**Binary:** /tmp/bar-new (built from source)
**Focus:** Fresh health check — uncovered scope (act, mean) and form tokens
  (indirect, case, activities, scaffold, tight, formats) + channel tokens (adr, gherkin)

---

## GH17-T01 — Tasks performed during a code review

**Task:** "What are the actual tasks being performed during a code review?"

**Expected tokens:** probe act full

**Skill selection:**
- Task: probe (surfacing what's happening)
- Scope: act ("actual tasks being performed" → act: "focuses on what is being done or intended—
  tasks, activities, operations, or work to be performed" ✅ — near-exact match)
- Completeness: full

**Bar command:** `bar build probe act full`

**Scores:** fitness 5, completeness 4, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "tasks being performed" matches act's description verbatim. Description-anchored,
no use_when needed.

---

## GH17-T02 — What does eventual consistency mean

**Task:** "What does eventual consistency actually mean?"

**Expected tokens:** show mean gist

**Skill selection:**
- Task: show (explaining a concept)
- Scope: mean ("what does X actually mean" → mean: "conceptual meaning and framing" ✅)
- Completeness: gist ("brief" — one-phrase question)

**Bar command:** `bar build show mean gist`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "what does X mean" is the canonical phrasing for mean scope. Highly discoverable.

---

## GH17-T03 — Make the case for microservices, reasoning first

**Task:** "Make the case for moving to a microservices architecture — but walk me through the
reasoning before you give me your recommendation."

**Expected tokens:** plan full indirect

**Skill selection:**
- Task: plan (proposing a strategy)
- Form: indirect ("walk me through the reasoning before giving the recommendation" → indirect:
  "begins with brief background, reasoning, and trade-offs and finishes with a clear bottom-line
  point")

**Bar command:** `bar build plan full indirect`

**Risk:** Two discoverability problems:
1. The name "indirect" is opaque — it means "background-first, conclusion-last" but that
   interpretation requires prior knowledge of the token. A user phrasing "walk me through the
   reasoning first" would not naturally reach for a token called "indirect."
2. Competes with `case` form, which also builds reasoning before a recommendation. The distinction
   is subtle: case = builds an argument/case (more explicit evidence-and-objection structure);
   indirect = background and reasoning lead to a bottom-line point (softer build-up).
   Without use_when, autopilot likely selects `case` (which is more self-descriptive) and misses
   `indirect`.

**Scores:** fitness 4, completeness 4, correctness 3, clarity 3 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: GH17-T03
token: indirect
axis: form
observation: >
  'indirect' form (background and reasoning first, conclusion last) has an opaque name and
  competes with 'case' form (argument structure, evidence before conclusion). The name
  "indirect" does not surface the pattern "build up before the conclusion". Without use_when,
  autopilot selects 'case' (more self-descriptive name for build-before-conclude pattern)
  and misses the softer, narrative-reasoning structure that 'indirect' provides.
recommendation:
  action: edit (use_when)
  token: indirect
  axis: form
  proposed_addition: >
    Reasoning-first, conclusion-last narrative: user asks for explanation or recommendation
    that builds up context before landing the point. Heuristic: 'walk me through the
    reasoning first', 'build up to the recommendation', 'show your thinking before the
    conclusion', 'give me the context before the answer', 'reasoning before conclusion'
    → indirect. Distinct from case form (case = structured argument with evidence and
    objections; indirect = softer narrative reasoning that converges on a bottom-line point).
```

---

## GH17-T04 — Build the argument for GraphQL over REST

**Task:** "Build the argument for why we should adopt GraphQL over REST."

**Expected tokens:** pick full case

**Skill selection:**
- Task: pick (choosing between alternatives)
- Form: case ("build the argument" → case: "building the case before the conclusion, laying out
  background, evidence, trade-offs" ✅ — "build the case/argument" maps directly)
- Completeness: full

**Bar command:** `bar build pick full case`

**Scores:** fitness 5, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Notes:** "build the case" and "build the argument" are near-exact matches to the case description.
Description-anchored, no use_when needed.

---

## GH17-T05 — Design sprint session activities

**Task:** "Design the agenda activities for a 2-hour design sprint session."

**Expected tokens:** plan act full activities

**Skill selection:**
- Task: plan (proposing structure)
- Scope: act (what will be done)
- Form: activities ("agenda activities for a design sprint session" → activities: "concrete session
  activities or segments—what to do, by whom, and in what order")

**Bar command:** `bar build plan act full activities`

**Risk:** Three-way competition without use_when:
1. `facilitate` form — "design sprint" is a collaborative session, matching facilitate's
   "workshop planning" heuristic. Autopilot likely selects facilitate.
2. `actions` form — "activities" in the task description sounds like actions (general to-do list).
3. `activities` form — correct choice, but requires knowing the distinction: activities =
   session-segment format (what to do by whom, in order, within a session); facilitate =
   facilitation plan (goals, participation cues, session structure as a whole).

The distinction between activities and facilitate is that activities produces the segment-level
content ("what happens in each block") while facilitate produces the facilitation plan (session
goals, participation mechanics, agenda structure). Both are plausible; autopilot will likely
select facilitate over activities due to facilitate's explicit use_when.

**Scores:** fitness 4, completeness 3, correctness 3, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: GH17-T05
token: activities
axis: form
observation: >
  'activities' form produces concrete session segments (what to do, by whom, in what order)
  but competes with 'facilitate' form (which has a use_when) and 'actions' form (general
  to-do tasks). User phrasing "agenda activities for a session" triggers facilitate's
  use_when ("workshop planning"), preempting activities. Distinct from facilitate (facilitate
  = overall facilitation plan with participation mechanics; activities = segment-level content
  of each session block).
recommendation:
  action: edit (use_when)
  token: activities
  axis: form
  proposed_addition: >
    Segment-level session content: user wants the concrete activities within a session,
    not the overall facilitation structure. Heuristic: 'what activities should we do',
    'activities for each block', 'session activities', 'design sprint activities',
    'what happens in each segment', 'activities list for the workshop' → activities.
    Distinct from facilitate form (facilitate = overall facilitation plan with session
    goals and participation mechanics; activities = segment-by-segment content of what
    to do and when). Often combined with facilitate: facilitate handles the structure,
    activities handles the content.
```

---

## GH17-T06 — Explain distributed consensus to a junior

**Task:** "Explain distributed consensus (Raft/Paxos) to a junior developer who has never seen it."

**Expected tokens:** show mean full scaffold

**Skill selection:**
- Task: show (explaining for an audience)
- Scope: mean (conceptual understanding)
- Form: scaffold ("to a junior developer who has never seen it" → scaffold: "starts from first
  principles, introduces ideas gradually... Most effective with learning-oriented audiences" ✅)
- Completeness: full

**Bar command:** `bar build show mean full scaffold`

**Scores:** fitness 5, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Notes:** "junior developer who has never seen it" maps to scaffold's "learning-oriented audiences"
note. The description "starts from first principles" connects to "has never seen it". Discoverable.

---

## GH17-T07 — Dense architecture summary, no bullets

**Task:** "Give me a dense summary of our system architecture — no bullets or tables, just packed
prose."

**Expected tokens:** show struct gist tight

**Skill selection:**
- Task: show
- Scope: struct (system architecture = arrangement and relationships)
- Completeness: gist (summary)
- Form: tight ("dense... no bullets or tables, just packed prose" → tight: "concise, dense prose,
  remaining freeform without bullets, tables, or code" ✅ — near-exact match)

**Bar command:** `bar build show struct gist tight`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "dense", "no bullets or tables", and "packed prose" all appear verbatim or near-verbatim
in tight's description. Very discoverable.

---

## GH17-T08 — Document ADR for event sourcing decision

**Task:** "Document our decision to adopt event sourcing for our orders domain."

**Expected tokens:** make full adr

**Skill selection:**
- Task: make (creating a document)
- Channel: adr ("document our decision" → Architecture Decision Record ✅ — explicit format)
- Completeness: full

**Bar command:** `bar build make full adr`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "document our decision" maps to ADR format. Channel name is well-known in engineering
contexts.

---

## GH17-T09 — BDD scenarios for authentication flow

**Task:** "Write BDD scenarios for our user authentication flow."

**Expected tokens:** make full gherkin

**Skill selection:**
- Task: make (creating test scenarios)
- Channel: gherkin ("BDD scenarios" → gherkin ✅ — explicit format name)
- Completeness: full

**Bar command:** `bar build make full gherkin`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "BDD" and "Gherkin" are synonymous in engineering parlance. Explicit and trivially
discoverable.

---

## GH17-T10 — What format for API design presentation

**Task:** "What document format should I use to present our API design to different stakeholders?"

**Expected tokens:** show full formats

**Skill selection:**
- Task: show (explaining options)
- Form: formats ("what document format should I use" → formats: "document types, writing formats,
  or structural templates and their suitability" ✅ — "format" in request maps to formats token)
- Completeness: full

**Bar command:** `bar build show full formats`

**Scores:** fitness 5, completeness 4, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** "format" in the user phrase maps directly to the formats token. Discoverable.

---

## Summary

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| GH17-T01 | act scope | 5 | No |
| GH17-T02 | mean scope | 5 | No |
| GH17-T03 | indirect form | 3 | Yes — G-L17-01 |
| GH17-T04 | case form | 4 | No |
| GH17-T05 | activities form | 3 | Yes — G-L17-02 |
| GH17-T06 | scaffold form | 4 | No |
| GH17-T07 | tight form | 5 | No |
| GH17-T08 | adr channel | 5 | No |
| GH17-T09 | gherkin channel | 5 | No |
| GH17-T10 | formats form | 5 | No |

**Mean: 4.4/5** (above 4.0 target)

**2 gaps found** (both undiscoverable-token type):
1. **G-L17-01**: `indirect` form — opaque name, competes with `case`
2. **G-L17-02**: `activities` form — preempted by `facilitate` use_when; segement vs. plan distinction unclear

**Confirmed discoverable without use_when:** act, mean (scope); case, scaffold, tight, formats (form);
adr, gherkin (channel).
