# Loop-24 Evaluations: Voice/Persona Axis Discoverability

**Date:** 2026-02-24
**Evaluator:** single-evaluator (Claude)
**Bar version:** 2.54.5

## Autopilot Simulation Method

For each task, the simulated autopilot follows the current heuristics in `help_llm.go`. The key
question: does autopilot *reach* the appropriate persona token? The current "Choosing Persona"
section (lines 884–889) covers:
- Known explicit audience → use `audience=` token
- Presets for technical-peer scenarios
- Non-technical audience (manager, PM, executive, CEO, stakeholder) → specific audience= tokens
- Cross-functional → stakeholder_facilitator

It does NOT cover: when to use `voice=` tokens; when to use `tone=` tokens.

---

## Group A: Voice Token Tasks

### T01 — Write a user story from PM perspective

**Task description:** "Write a user story for the CSV export feature from the PM's perspective"
**Expected persona:** voice=as-pm

**Skill selection log:**
- Task: make (creating content)
- Completeness: full (default)
- Scope: act (what activities/tasks)
- Form: story (user story format)
- Persona: heuristic checks for audience= → no explicit audience named; checks presets → no preset
  matches "PM perspective"; voice= tokens: NO GUIDANCE EXISTS → skipped

**Bar command (autopilot):** `bar build make act story`
**Bar command (with correct persona):** `bar build make act story voice=as-pm`

**Difference:** Without voice=as-pm, the story is written from a neutral generic voice. With
voice=as-pm, the prompt adds: "The response speaks as a product manager, focusing on outcomes,
scope, and stakeholders." — a meaningful framing for user story authorship.

**Coverage scores (autopilot selection):**
- Token fitness: 3 (story + act is correct; PM framing missing)
- Token completeness: 3 (voice axis uncaptured)
- Skill correctness: 2 (heuristic provides no path to voice= selection)
- Prompt clarity: 4 (prompt is usable but generic)
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: T01 — Write user story from PM perspective
dimension: persona/voice
observation: >
  voice=as-pm exists and would meaningfully shape the user story framing (PM focuses on
  outcomes, scope, stakeholders). But the "Choosing Persona" heuristic contains no guidance
  on when to use voice= tokens — it only covers audience= tokens and presets. Autopilot
  has no signal to select voice=as-pm even when the task explicitly says "from the PM's
  perspective".
recommendation:
  action: skill-update
  skill: bar-autopilot (help_llm.go)
  section: "Choosing Persona"
  proposed_addition: >
    When to use voice=: select voice= when the task asks for output FROM a specific role's
    perspective — "write as a PM", "speak as a designer", "review as a senior engineer",
    "from the facilitator's perspective". Voice= shapes the speaker identity;
    audience= shapes the target reader.
evidence: [T01, T02, T03, T04, T05]
```

---

### T02 — Design feedback as a designer

**Task description:** "Give feedback on this UI mockup as a designer would"
**Expected persona:** voice=as-designer

**Skill selection log:**
- Task: probe (analyze/evaluate)
- Scope: good (quality criteria)
- Method: analysis (describe and structure)
- Persona: heuristic provides no path to voice=as-designer → skipped

**Bar command (autopilot):** `bar build probe good analysis`
**Bar command (correct):** `bar build probe good analysis voice=as-designer`

**Coverage scores:**
- Token fitness: 3 (probe good analysis is structurally sound; designer stance missing)
- Token completeness: 3 (voice axis missing)
- Skill correctness: 2 (no heuristic path)
- Prompt clarity: 4
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token (same root as T01 — see T01 YAML)

---

### T03 — Teach me about dependency injection

**Task description:** "Teach me about dependency injection"
**Expected persona:** voice=as-teacher

**Skill selection log:**
- Task: show (explain)
- Scope: mean (conceptual framing)
- Method: scaffold (build understanding gradually)
- Persona: heuristic check → no explicit audience named, no non-technical signal → no persona

Note: The heuristic does mention `persona=teach_junior_dev` for technical peer scenarios. An
astute autopilot might reach this. But "teach me" doesn't specify junior audience, and
`persona=teach_junior_dev` bundles audience=to-junior-engineer which may be wrong for the
actual requester. `voice=as-teacher` alone is the more precise selection.

**Bar command (autopilot):** `bar build show mean scaffold`
**Bar command (correct):** `bar build show mean scaffold voice=as-teacher`

**Coverage scores:**
- Token fitness: 3 (scaffold is good; teacher stance clarifies the pedagogy)
- Token completeness: 3 (voice axis missing)
- Skill correctness: 3 (preset path exists but is less precise)
- Prompt clarity: 4
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token (same root as T01)

---

### T04 — Facilitate retrospective

**Task description:** "Create a retrospective agenda for the team" (as facilitator)
**Expected persona:** voice=as-facilitator

**Skill selection log:**
- Task: make (create agenda)
- Scope: act (what activities)
- Form: facilitate (facilitation format — exists as a form token!)
- Persona: no voice= heuristic → skipped

Note: The `facilitate` form token already gets much of the way there structurally. voice=as-facilitator
adds "guiding process, balancing voices, maintaining momentum" as speaker stance, which adds
value but is secondary to the form selection.

**Bar command (autopilot):** `bar build make act facilitate`
**Bar command (correct):** `bar build make act facilitate voice=as-facilitator`

**Coverage scores:**
- Token fitness: 4 (facilitate form largely covers it)
- Token completeness: 4 (voice adds value but not critical when form is right)
- Skill correctness: 3 (voice= guidance missing, but form rescues this task)
- Prompt clarity: 4
- **Overall: 4**

**Gap diagnosis:** undiscoverable-token (lower priority — form compensates)

---

### T05 — PR review from senior engineer perspective

**Task description:** "Review this PR from a senior engineer's perspective"
**Expected persona:** voice=as-principal-engineer

**Skill selection log:**
- Task: probe (analyze/review)
- Scope: good (quality) + fail (failure modes)
- Method: adversarial (stress-test for weaknesses)
- Persona: no voice= heuristic → skipped

**Bar command (autopilot):** `bar build probe good fail adversarial`
**Bar command (correct):** `bar build probe good fail adversarial voice=as-principal-engineer`

**Coverage scores:**
- Token fitness: 3 (probe good fail adversarial is solid; senior perspective shapes authority and trade-off emphasis)
- Token completeness: 3 (voice axis missing — "principal engineer" brings systems thinking + pragmatism)
- Skill correctness: 2 (no heuristic path)
- Prompt clarity: 4
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token (same root as T01)

---

## Group B: Audience Token Tasks

### T06 — Summarize tech debt for CEO

**Task description:** "Summarize this tech debt for the CEO"
**Expected persona:** audience=to-ceo

**Skill selection log:**
- Task: pull (extract/summarize)
- Completeness: gist (brief)
- Persona: heuristic states "Non-technical audience (CEO) → audience=to-ceo" ✓

**Bar command (autopilot):** `bar build pull gist audience=to-ceo`

**Coverage scores (all 5s — heuristic works):**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

---

### T07 — Explain API to junior developer

**Task description:** "Explain this API to a junior developer"
**Expected persona:** audience=to-junior-engineer

**Skill selection log:**
- Heuristic: "junior engineer" → audience=to-junior-engineer ✓

**Bar command (autopilot):** `bar build show mean scaffold audience=to-junior-engineer`

**Coverage scores:** All 5. **Overall: 5**
**Gap diagnosis:** none

---

### T08 — Architecture decision for stakeholders

**Task description:** "Present this architecture decision to our stakeholders"
**Expected persona:** audience=to-stakeholders

**Skill selection log:**
- Heuristic: "stakeholder" → audience=to-stakeholders ✓

**Bar command (autopilot):** `bar build show struct case audience=to-stakeholders`

**Coverage scores:** All 5. **Overall: 5**
**Gap diagnosis:** none

---

### T09 — Status update to product manager

**Task description:** "Write a status update to our product manager about the delay"
**Expected persona:** audience=to-product-manager

**Skill selection log:**
- Heuristic: "PM" → audience=to-product-manager ✓

**Bar command (autopilot):** `bar build make gist audience=to-product-manager channel=slack`

**Coverage scores:** All 5. **Overall: 5**
**Gap diagnosis:** none

---

### T10 — Release communication to team

**Task description:** "Communicate this release to the whole team"
**Expected persona:** audience=to-team

**Skill selection log:**
- Heuristic lists: managers, PM, executive, CEO, stakeholders — "team" is NOT listed
- Autopilot sees "team" but finds no match in heuristic → no persona selected

**Bar command (autopilot):** `bar build make gist channel=slack`
**Bar command (correct):** `bar build make gist channel=slack audience=to-team`

**Coverage scores:**
- Token fitness: 3 (channel=slack helps; team audience shapes actionable + collaborative framing)
- Token completeness: 3 (audience=to-team missing)
- Skill correctness: 3 (heuristic list is incomplete — "team" is a common audience)
- Prompt clarity: 4
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: T10 — Release communication to team
dimension: persona/audience
observation: >
  audience=to-team exists ("addresses the team, keeping guidance actionable and collaborative")
  and is appropriate for "communicate to the whole team" tasks. But the "Choosing Persona"
  heuristic's non-technical audience list (manager, PM, executive, CEO, stakeholder) does NOT
  include "team". An autopilot following the heuristic has no trigger for audience=to-team.
recommendation:
  action: skill-update
  skill: bar-autopilot (help_llm.go)
  section: "Choosing Persona"
  proposed_addition: >
    Add "team" to the non-technical audience list: "audience=to-team" for
    "communicate to the team", "team update", "team announcement".
evidence: [T10]
```

---

## Group C: Tone Token Tasks

### T11 — Formal incident report

**Task description:** "Draft a formal incident report for compliance"
**Expected persona:** tone=formally

**Skill selection log:**
- Task: make (create document)
- Scope: act (what happened)
- Form: log (incident log format)
- Persona: heuristic says nothing about tone= → skipped

**Bar command (autopilot):** `bar build make act log`
**Bar command (correct):** `bar build make act log tone=formally`

**Coverage scores:**
- Token fitness: 3 (make act log is structurally correct; formal register uncaptured)
- Token completeness: 3 (tone axis completely absent from heuristic)
- Skill correctness: 2 (no heuristic path to tone=)
- Prompt clarity: 4
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: T11 — Formal incident report
dimension: persona/tone
observation: >
  tone=formally ("formal, professional tone") is clearly the right selection for a compliance
  incident report. But the "Choosing Persona" heuristic in help_llm.go contains zero guidance
  on tone= tokens. The entire tone axis (casually, directly, formally, gently, kindly) is
  invisible to autopilot. There is no signal that would lead it to select tone=formally.
recommendation:
  action: skill-update
  skill: bar-autopilot (help_llm.go)
  section: "Choosing Persona"
  proposed_addition: >
    When to use tone=: select tone= when the task specifies an emotional register or
    communication style:
    - "formal", "official", "compliance", "professional" → tone=formally
    - "casual", "informal", "friendly", "quick Slack" → tone=casually
    - "gentle", "sensitive", "supportive", "careful" → tone=gently
    - "direct", "blunt", "concise", "no-fluff" → tone=directly
    - "kind", "encouraging", "warm" → tone=kindly
evidence: [T11, T12, T13]
```

---

### T12 — Casual Slack check-in

**Task description:** "Send a casual check-in Slack message to the team"
**Expected persona:** tone=casually (+ channel=slack + audience=to-team)

**Skill selection log:**
- Task: make; Channel: slack (heuristic should surface this)
- Audience: to-team — missing from heuristic (T10 gap)
- Tone: casually — no heuristic path

**Bar command (autopilot):** `bar build make gist channel=slack`
**Bar command (correct):** `bar build make gist channel=slack tone=casually audience=to-team`

**Coverage scores:**
- Token fitness: 3 (channel=slack is correct; casual register missing)
- Token completeness: 3 (tone + audience both missing)
- Skill correctness: 2 (two persona dimensions missed)
- Prompt clarity: 4
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token (tone=casually; audience=to-team — same roots as T10, T11)

---

### T13 — Sensitive code feedback

**Task description:** "Give sensitive, supportive feedback on a colleague's code"
**Expected persona:** tone=gently; method should NOT be adversarial

**Skill selection log:**
- Task: probe (analyze/evaluate)
- Scope: good (quality criteria)
- Method: adversarial — autopilot sees "find weaknesses/feedback" and reaches for adversarial.
  This is wrong: adversarial ("constructive stress-test, searching for weaknesses") directly
  contradicts the "sensitive, supportive" framing.
- Tone: gently — no heuristic path → skipped

**Bar command (autopilot):** `bar build probe good adversarial`
**Bar command (correct):** `bar build probe good analysis tone=gently`

**Coverage scores:**
- Token fitness: 2 (adversarial actively contradicts the task's emotional requirement)
- Token completeness: 2 (tone=gently entirely missing; wrong method chosen)
- Skill correctness: 1 (heuristic misroutes on method AND provides no tone path)
- Prompt clarity: 2 (adversarial framing would produce harsh, non-supportive feedback)
- **Overall: 2**

**Gap diagnosis:** undiscoverable-token (tone=gently) + skill-guidance-wrong (adversarial method)
```yaml
gap_type: skill-guidance-wrong
task: T13 — Sensitive code feedback
dimension: method + persona/tone
observation: >
  Autopilot selects adversarial method for "feedback" tasks because the "Finding problems"
  heuristic routes to adversarial. But adversarial ("constructive stress-test, searching for
  weaknesses") is the wrong method when the task explicitly requires sensitivity. Additionally,
  tone=gently is completely absent from any heuristic — the tone axis has no guidance at all.
  The combination produces a prompt that would generate aggressive rather than supportive feedback.
recommendation:
  action: skill-update
  skill: bar-autopilot (help_llm.go)
  section: "Choosing Method"
  proposed_addition: >
    For feedback tasks with emotional framing ("sensitive", "supportive", "gentle",
    "constructive" in the collegial sense): prefer analysis method over adversarial.
    Reserve adversarial for technical stress-testing (code, designs, arguments) where
    the goal is finding failure modes, not interpersonal communication.
    Pair with tone=gently when the task's framing signals sensitivity.
evidence: [T13]
```

---

## Group D: No-Persona Controls

### T14 — Performance bottleneck analysis

**Task description:** "Analyze the performance bottleneck in this query"
**Expected persona:** none

**Bar command (autopilot):** `bar build probe struct fail diagnose`
**Coverage scores:** All 5. **Overall: 5**
**Gap diagnosis:** none — control case passes.

---

### T15 — List API endpoints

**Task description:** "List all the API endpoints in this service"
**Expected persona:** none

**Bar command (autopilot):** `bar build pull thing gist`
**Coverage scores:** All 5. **Overall: 5**
**Gap diagnosis:** none — control case passes.

---

## Coverage Summary

| Task | Autopilot overall | Gap type |
|------|-------------------|----------|
| T01 | 3 | undiscoverable-token (voice=as-pm) |
| T02 | 3 | undiscoverable-token (voice=as-designer) |
| T03 | 3 | undiscoverable-token (voice=as-teacher) |
| T04 | 4 | undiscoverable-token (voice=as-facilitator — low priority, form compensates) |
| T05 | 3 | undiscoverable-token (voice=as-principal-engineer) |
| T06 | 5 | none |
| T07 | 5 | none |
| T08 | 5 | none |
| T09 | 5 | none |
| T10 | 3 | undiscoverable-token (audience=to-team not in heuristic) |
| T11 | 3 | undiscoverable-token (tone=formally — tone axis has zero heuristic) |
| T12 | 3 | undiscoverable-token (tone=casually + audience=to-team) |
| T13 | 2 | undiscoverable-token (tone=gently) + skill-guidance-wrong (adversarial method) |
| T14 | 5 | none |
| T15 | 5 | none |

**Mean coverage: 3.60** (vs loop-23: 4.9/5)

Tasks scoring ≤3: 9/15 (T01–T03, T05, T10–T13)

**Root cause pattern**: Three structural gaps, all in "Choosing Persona" heuristic:
1. voice= axis: no heuristic guidance at all (5 tasks affected: T01–T05)
2. tone= axis: no heuristic guidance at all (3 tasks affected: T11–T13)
3. audience=to-team: missing from the non-technical audience list (2 tasks affected: T10, T12)

**Secondary**: skill-guidance-wrong on method selection for sensitive feedback (T13).
