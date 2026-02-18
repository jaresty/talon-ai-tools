# ADR-0113 Loop-19 Evaluations

**Date:** 2026-02-17
**Binary:** /tmp/bar-new (built from source)
**Focus:** Task token discoverability (fix, sim, sort, check, pick) + opaque method tokens
  (abduce, analog, jobs, shift, spec)

---

## L19-T01 — Reformat a user-unfriendly error message

**Task:** "Fix this error message to be more user-friendly:
'NullPointerException at line 42 in AuthService'"

**Expected tokens:** `fix full`

**Skill selection:**
- Task: fix ("fix this error message" with the goal of making it user-friendly = change presentation
  while keeping meaning → fix is reformat, not debug)
- Completeness: full

**Bar command:** `bar build fix full`

**Bar output confirms:** "The response changes the form or presentation of given content while
keeping its intended meaning." ✅

**Key risk:** The word "fix" in the request maps to bar's `fix` token, but bar's `fix` means
reformat — NOT debug. In this case the user wants better presentation, so `fix` is correct.
The inverse risk (users saying "fix the bug" → selecting `fix` when they need `probe+diagnose`)
is documented in the notes. The notes read: "In bar's grammar, fix means reformat — not debug.
To analyze/debug: use probe with diagnose, inversion, or adversarial." This is present but
passive — the skill must actively route away from `fix` for debugging requests.

**Scores:** fitness 5, completeness 4, correctness 4, clarity 4 → **Overall: 4** ✅

**Gap diagnosis:** none for this task phrasing. Secondary observation: `fix` inverse routing
(users saying "fix the bug" or "fix this issue in the code" expect debugging, not reformatting)
needs active disambiguation in skill heuristics or use_when, not just a notes warning.

---

## L19-T02 — Scenario: deprecating the legacy API tomorrow

**Task:** "What would happen if we deprecated the legacy API tomorrow?"

**Expected tokens:** `sim full time`

**Skill selection:**
- Task: sim ("play out a scenario over time" — "what would happen if X" = hypothetical scenario
  over time ✅)
- Completeness: full
- Scope: time (events unfold over time after the deprecation)

**Bar command:** `bar build sim full time`

**Bar output confirms:** "The response plays out a concrete or hypothetical scenario over time
under stated or inferred conditions." ✅

**Discovery risk:** `sim` is not an obvious token. "What would happen if..." is one of the most
common phrasings for hypothetical reasoning, but autopilot is more likely to select `probe` (surface
implications) or `plan` (steps for deprecation). The `sim` description says "plays out a concrete
or hypothetical scenario over time" — the phrase "over time" is key and present, but the token
name `sim` is not intuitive. Without use_when, "what would happen if" phrases will route to
`probe` instead of `sim`.

**Scores:** fitness 4, completeness 4, correctness 2, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: L19-T02
token: sim
axis: task
observation: >
  'sim' task plays out hypothetical scenarios over time, but 'sim' is not intuitive vocabulary.
  "What would happen if we..." is the primary use case, but autopilot routes these to 'probe'
  (surface implications) — which gives implications rather than a time-unfolding scenario.
  The distinction matters: probe = analytical surfacing of assumptions/risks; sim = narrative
  walkthrough of what actually unfolds step by step under those conditions. Without use_when,
  "what would happen if" tasks lose the temporal-unfolding quality of sim.
recommendation:
  action: edit (use_when)
  token: sim
  axis: task
  proposed_addition: >
    Temporal scenario walkthrough: user wants to trace what unfolds over time if a condition
    occurs. Heuristic: 'what would happen if', 'play out the scenario where', 'simulate what
    happens when', 'walk me through what would occur if', 'trace the sequence of events if',
    'what unfolds after', 'hypothetically if we did X, then what' → sim. Distinct from plan
    (plan = steps to take; sim = what plays out if a condition is met) and probe (probe =
    surface assumptions analytically; sim = narrate the scenario unfolding over time).
evidence: [L19-T02]
```

---

## L19-T03 — Categorize support tickets by recurring theme

**Task:** "Categorize these 30 support tickets by recurring theme to identify the
highest-impact areas to fix"

**Expected tokens:** `sort full cluster`

**Skill selection:**
- Task: sort ("categorize" = arrange items into categories ✅)
- Method: cluster ("group by recurring theme" = groups based on shared characteristics ✅)
- Completeness: full

**Bar command:** `bar build sort full cluster`

**Bar output confirms:** sort = "arranges items into categories", cluster = "groups or organizes
existing items into clusters based on shared characteristics." ✅

**Notes:** "Categorize" in the request maps directly to sort. "Recurring theme" maps to cluster.
Both are description-anchored. No use_when needed.

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Gap diagnosis:** none

---

## L19-T04 — OWASP compliance check on authentication

**Task:** "Does this authentication implementation meet OWASP Top 10 requirements?
Flag any violations."

**Expected tokens:** `check full fail`

**Skill selection:**
- Task: check ("does this meet requirements?" = evaluate against criteria → check ✅)
- Completeness: full
- Scope: fail (looking for violations = where it stops working / failure modes ✅)

**Bar command:** `bar build check full fail`

**Bar output confirms:** check = "evaluates the subject against a condition and reports whether
it passes or fails", fail scope = "breakdowns, stress, uncertainty, or limits." ✅

**Notes:** "Does this meet requirements?" and "Flag any violations" both map to check+fail cleanly.
The check task is well-described and discoverable. No use_when needed.

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Gap diagnosis:** none

---

## L19-T05 — Hypothesis generation for latency spike

**Task:** "What is the best explanation for why our p99 latency spiked on Tuesday afternoon —
generate ranked hypotheses from available evidence"

**Expected tokens:** `probe fail full abduce`

**Skill selection:**
- Task: probe (analyzing the incident to surface structure/assumptions)
- Scope: fail (latency spike = breakdown/failure mode)
- Method: abduce (generate hypotheses from evidence ✅)
- Completeness: full

**Bar command:** `bar build probe fail full abduce`

**Bar output confirms:** abduce = "generating explanatory hypotheses that best account for the
available evidence, explicitly comparing alternative explanations." ✅

**Discovery risk:** `abduce` is academic terminology (abductive reasoning). Most users will not
know the word. They say "what's the most likely explanation", "why did this happen — what are
the hypotheses", "generate possible causes ranked by likelihood." None of these map to "abduce"
without use_when. Autopilot would likely select `probe fail diagnose` (which is close — diagnose
narrows hypotheses through evidence) but abduce's distinctive value is explicitly generating and
comparing multiple alternative hypotheses before narrowing — this is a different reasoning mode
than diagnose's root-cause narrowing.

**Scores:** fitness 5, completeness 4, correctness 2, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: L19-T05
token: abduce
axis: method
observation: >
  'abduce' generates explanatory hypotheses from evidence, explicitly comparing alternatives.
  The token name is academic (abductive reasoning) and will not surface from natural user
  phrasing. Users say "what's the best explanation", "generate hypotheses for why",
  "what are the most likely causes", "ranked explanations for" — none of which match
  the catalog token name. Autopilot routes these to 'diagnose' (root-cause narrowing),
  which is directionally correct but loses abduce's distinctive comparative hypothesis
  generation and explicit ranking of competing explanations.
recommendation:
  action: edit (use_when)
  token: abduce
  axis: method
  proposed_addition: >
    Comparative hypothesis generation from evidence: user wants multiple candidate
    explanations ranked by how well they fit the evidence, not just a single root cause.
    Heuristic: 'what's the best explanation for', 'generate hypotheses for why',
    'what are the most likely causes ranked', 'compare possible explanations',
    'ranked hypotheses from evidence', 'abductive reasoning', 'what could explain this' →
    abduce. Distinct from diagnose (diagnose = narrow to single root cause via evidence;
    abduce = generate and compare multiple competing explanations explicitly).
evidence: [L19-T05]
```

---

## L19-T06 — Explain event sourcing by analogy

**Task:** "Use an analogy to explain event sourcing to someone from accounting who
understands debits and credits"

**Expected tokens:** `show mean full analog`

**Skill selection:**
- Task: show (explain for an audience)
- Scope: mean (conceptual framing of what event sourcing is)
- Method: analog ("use an analogy" → analog: "reasoning through analogy" ✅)
- Completeness: full

**Bar command:** `bar build show mean full analog`

**Bar output confirms:** analog = "reasoning through analogy, mapping relational structure from
a known case onto the subject and examining where the analogy holds or breaks." ✅

**Notes:** "Use an analogy" in the request exactly maps to the `analog` description. The explicit
request phrasing makes this discoverable without use_when.

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Gap diagnosis:** none

---

## L19-T07 — What job is the 'saved searches' feature doing for users?

**Task:** "What is the user actually trying to accomplish with this feature request for
a 'saved searches' capability?"

**Expected tokens:** `probe mean full jobs`

**Skill selection:**
- Task: probe (analyze the underlying need)
- Scope: mean (conceptual framing of what the user wants)
- Method: jobs (Jobs-to-be-done analysis ✅)
- Completeness: full

**Bar command:** `bar build probe mean full jobs`

**Bar output confirms:** jobs = "analyzing Jobs To Be Done — the outcomes users want to achieve
and the forces shaping their choices." ✅

**Discovery risk:** "Jobs to be done" is a specific product methodology framework. Users ask
"what is the user actually trying to accomplish", "what need does this solve", "why would
someone use this", "what outcome does the user want" — these are natural JTBD questions but
they don't map to the word "jobs" in the catalog. Autopilot would route to `probe mean` alone
or perhaps add `product` method, but not `jobs`. The `jobs` token is effectively invisible
to the skill without use_when, even though it's precisely the right method for this class of task.

**Scores:** fitness 5, completeness 4, correctness 2, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: L19-T07
token: jobs
axis: method
observation: >
  'jobs' applies the Jobs-to-be-Done (JTBD) framework — analyzing what outcomes users
  want to achieve and the forces shaping their choices. The token name 'jobs' is not
  intuitive for this concept. Users ask "what is the user actually trying to accomplish",
  "what need does this solve", "what job does this feature do", "why would someone use
  this", "what outcome does the user want" — these are the primary JTBD question patterns
  but none map to the token name 'jobs'. Autopilot would select 'probe mean' or 'product'
  method instead, missing the structured JTBD analytical framework.
recommendation:
  action: edit (use_when)
  token: jobs
  axis: method
  proposed_addition: >
    Jobs-to-be-done (JTBD) analysis: user wants to understand what outcome users are
    trying to achieve, what need the feature serves, or what forces shape their adoption
    choices. Heuristic: 'what is the user actually trying to accomplish', 'what job does
    this feature do', 'what need does this solve', 'why would someone use this',
    'what outcome does the user want', 'what drives adoption', 'user motivation behind',
    'JTBD', 'jobs to be done' → jobs. Distinct from product method (product = features,
    user needs, value propositions broadly; jobs = specifically the outcome/progress users
    seek and the forces blocking or enabling it).
evidence: [L19-T07]
```

---

## L19-T08 — Microservices decision from three stakeholder perspectives

**Task:** "Look at this architectural decision to move to microservices from the perspective
of security, operations, and product — rotate through each"

**Expected tokens:** `probe struct full shift`

**Skill selection:**
- Task: probe (analyze the architectural decision)
- Scope: struct (how services will be arranged and related)
- Method: shift ("rotate through distinct perspectives" → shift ✅)
- Completeness: full

**Bar command:** `bar build probe struct full shift`

**Bar output confirms:** shift = "deliberately rotating through distinct perspectives or cognitive
modes, contrasting how each frame interprets the same facts." ✅

**Discovery risk:** "From the perspective of X, Y, and Z — rotate through each" maps to shift's
description with reasonable confidence. The description uses "rotating through distinct
perspectives" which mirrors the user's phrasing "rotate through each perspective." This is
partially anchored. No strong gap, but slightly opaque token name.

**Scores:** fitness 4, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Gap diagnosis:** none (borderline — shift is partially anchored to "perspective of X, Y, Z"
phrasing; adding use_when would improve routing reliability but is not urgent)

---

## L19-T09 — Define "done" before implementing the payment flow

**Task:** "Before we implement this payment flow, define what done looks like and what
tests would need to pass"

**Expected tokens:** `plan full spec`

**Skill selection:**
- Task: plan (propose strategy/structure moving toward a goal)
- Method: spec (define correctness criteria before implementation ✅)
- Completeness: full

**Bar command:** `bar build plan full spec`

**Bar output confirms:** spec = "defines explicit criteria of correctness before proposing
implementations and treats those criteria as fixed and authoritative." ✅

**Notes:** "Define what done looks like" and "what tests would need to pass" map well to spec's
description. The spec method has a TDD-adjacent framing that connects to this request. Partially
anchored.

**Scores:** fitness 4, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Gap diagnosis:** none

---

## L19-T10 — Rank feature proposals by strategic value

**Task:** "Rank these 8 feature proposals by strategic value for next quarter"

**Expected tokens:** `sort full prioritize`

**Skill selection:**
- Task: sort ("rank" = arrange in order ✅)
- Method: prioritize ("by strategic value" = rank by importance making rationale explicit ✅)
- Completeness: full

**Bar command:** `bar build sort full prioritize`

**Bar output confirms:** sort = "arranges items into categories or an order", prioritize =
"assessing and ordering items by importance or impact, making the ranking and rationale
explicit." ✅

**Notes:** "Rank" maps to sort (ordering scheme). "By strategic value" maps to prioritize.
Both are description-anchored. No use_when needed.

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Gap diagnosis:** none

---

## Summary

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| L19-T01 | fix (reformat) | 4 | No (secondary note on inverse routing) |
| L19-T02 | sim | 3 | Yes — G-L19-01 |
| L19-T03 | sort + cluster | 5 | No |
| L19-T04 | check + fail | 5 | No |
| L19-T05 | abduce | 3 | Yes — G-L19-02 |
| L19-T06 | analog | 5 | No |
| L19-T07 | jobs | 3 | Yes — G-L19-03 |
| L19-T08 | shift | 4 | No |
| L19-T09 | plan + spec | 4 | No |
| L19-T10 | sort + prioritize | 5 | No |

**Mean: 4.1/5**

**3 gaps found** (all undiscoverable-token):
- **G-L19-01**: `sim` task — "what would happen if" does not route to sim without use_when
- **G-L19-02**: `abduce` method — academic terminology; "best explanation / ranked hypotheses"
  does not route to abduce without use_when
- **G-L19-03**: `jobs` method — JTBD phrasing; "what is the user trying to accomplish" does
  not route to jobs without use_when

**Secondary observation (not a scored gap):**
`fix` inverse routing — users saying "fix the bug / fix this code" may mistakenly select `fix`
(reformat) instead of `probe+diagnose`. The notes warn against this but the skill heuristics
may not actively route away. Worth monitoring.

**Confirmed description-anchored (no use_when needed):**
sort, check, cluster, prioritize, analog — all score 5 from description or explicit user phrasing.
