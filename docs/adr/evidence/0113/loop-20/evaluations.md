# ADR-0113 Loop-20 Evaluations

**Date:** 2026-02-17
**Binary:** /tmp/bar-new (built from source)
**Focus:** Opaque method tokens — induce, converge, branch, simulation (method), operations,
  models, systemic, unknowns, verify, trans

---

## L20-T01 — Generalize an architectural principle from three observations

**Task:** "I've seen that our three fastest microservices all avoid shared state, use in-memory
caching, and expose narrow APIs. What general architectural principle can I draw from these
observations?"

**Expected tokens:** `probe mean full induce`

**Skill selection:**
- Task: probe (analyze to surface structure/implications)
- Scope: mean (conceptual framing of what principle emerges)
- Method: induce (generalize patterns from specific observations ✅)
- Completeness: full

**Bar command:** `bar build probe mean full induce`

**Discovery risk:** `induce` means "applying inductive reasoning, generalizing patterns from
specific observations." The description is correct but academic. Users say "what general
principle can I draw from these observations," "what pattern do these cases suggest," "what
does this tell us more broadly" — none of these naturally map to the token name "induce."
Autopilot would likely select `probe mean` alone, possibly adding `analysis` (which is
auto-included in probe profiles anyway). Without use_when, the inductive reasoning framing
is invisible.

**Scores:** fitness 4, completeness 4, correctness 2, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: L20-T01
token: induce
axis: method
observation: >
  'induce' applies inductive reasoning to generalize patterns from specific observations.
  The token name is academic. Users say "what general principle can I draw from these
  examples", "what pattern do these cases suggest", "what does this tell us more broadly",
  "generalize from these observations" — none of which map to "induce". Autopilot selects
  probe+analysis instead, losing the explicit generalization and strength-assessment
  characteristic of inductive reasoning.
recommendation:
  action: edit (use_when)
  token: induce
  axis: method
  proposed_addition: >
    Inductive generalization from examples: user wants to draw a general principle, pattern,
    or rule from specific cases or observations. Heuristic: 'what general principle can I
    draw from these', 'what pattern do these examples suggest', 'what does this tell us more
    broadly', 'generalize from these observations', 'what can I conclude from these cases',
    'what rule emerges from these instances', 'extrapolate from these examples' → induce.
    Distinct from abduce (abduce = generate competing hypotheses to explain evidence;
    induce = generalize a pattern or rule from a set of examples).
evidence: [L20-T01]
```

---

## L20-T02 — Narrow three architecture options to one recommendation

**Task:** "We have explored event-driven, CQRS, and monolith-first approaches for the new
billing system. Help me narrow this to a single recommendation with explicit tradeoff reasoning."

**Expected tokens:** `pick full converge`

**Skill selection:**
- Task: pick (select from alternatives)
- Method: converge (systematically narrow from broad to focused ✅)
- Completeness: full

**Bar command:** `bar build pick full converge`

**Discovery notes:** User says "narrow this to a single recommendation with explicit tradeoff
reasoning" — converge's description says "systematically narrowing from broad exploration to
focused recommendations, weighing trade-offs explicitly." The word "narrow" appears in both.
Autopilot would select `pick` alone (already sounds like the answer), potentially missing the
tradeoff-weighing process that converge adds. Partially anchored — not a scored gap, but the
"narrow... explicit tradeoff reasoning" signal should increase converge selection reliability.

**Scores:** fitness 4, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Gap diagnosis:** none (borderline — converge is partially anchored via "narrow" vocabulary)

---

## L20-T03 — Compare two architectures by branching on key assumptions

**Task:** "Explore whether we should adopt event-driven architecture or stay with
request-response, branching on the key assumptions: team size, consistency requirements,
and operational maturity."

**Expected tokens:** `probe struct full branch`

**Skill selection:**
- Task: probe (analyze the architectural choice)
- Scope: struct (how components are arranged and related)
- Method: branch (explore multiple reasoning paths, branching on key assumptions ✅)
- Completeness: full

**Bar command:** `bar build probe struct full branch`

**Discovery notes:** User literally says "branching on the key assumptions" — branch description:
"exploring multiple reasoning paths in parallel, branching on key assumptions or choices." The
vocabulary is almost directly mirrored. Description-anchored.

**Scores:** fitness 4, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Gap diagnosis:** none

---

## L20-T04 — Thought experiment on tripling ingestion rate

**Task:** "Run a thought experiment: what happens to our event pipeline if we triple ingestion
rate? Walk through feedback loops, bottlenecks, and tipping points that would emerge."

**Expected tokens:** `probe fail full simulation`

**Skill selection:**
- Task: probe (analyze — the thought experiment enriches the analysis)
- Scope: fail (focusing on what breaks at scale)
- Method: simulation ("focusing on explicit thought experiments or scenario walkthroughs
  that project evolution over time, highlighting feedback loops, bottlenecks, tipping
  points, and emergent effects" ✅)
- Completeness: full

**Bar command:** `bar build probe fail full simulation`

**Critical distinction:** `simulation` (method) vs `sim` (task) are easily confused:
- `sim` task: standalone scenario walkthrough — "what unfolds over time if X"
- `simulation` method: enriches another task (probe, plan) with thought-experiment
  reasoning focusing on feedback loops, tipping points, and emergent effects

Without use_when for `simulation` method, two failure modes:
1. Autopilot selects `sim full fail` (task sim instead of method simulation) — loses the
   analytical probe framing; produces a narrative instead of an analysis enriched with
   thought-experiment reasoning
2. Autopilot selects `probe fail boom` (scale extremes) — directionally correct but
   misses simulation's specific focus on feedback loops and emergent effects over time

The method is also undiscoverable from its name: users say "run a thought experiment,"
"project what would happen," "trace feedback loops and tipping points" — none obviously
route to "simulation" as a method enrichment token.

**Scores:** fitness 4, completeness 3, correctness 2, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: L20-T04
token: simulation
axis: method
observation: >
  'simulation' as a METHOD enriches another task (probe, plan) with thought-experiment
  reasoning: feedback loops, bottlenecks, tipping points, emergent effects over time.
  Two failure modes without use_when: (1) autopilot selects sim TASK instead — sim is a
  standalone scenario task, not a method enrichment; (2) autopilot selects boom (scale
  extremes) which is related but distinct. The key differentiator for simulation method is
  the feedback-loop/tipping-point/emergent-effect framing. Also easily confused with the
  sim task: sim = narrative walkthrough of what unfolds; simulation method = analytical
  enrichment with thought-experiment reasoning about systemic dynamics.
recommendation:
  action: edit (use_when)
  token: simulation
  axis: method
  proposed_addition: >
    Thought-experiment enrichment for feedback loop and emergent effect analysis: user
    wants to project systemic dynamics through an analytical lens, not just narrate
    what happens. Heuristic: 'run a thought experiment', 'trace feedback loops',
    'where would bottlenecks emerge', 'tipping point analysis', 'what emergent effects
    would arise', 'project systemic dynamics', 'model how effects compound over time' →
    simulation method. Distinct from sim task (sim = standalone scenario narrative of
    what unfolds; simulation method = enriches probe/plan with thought-experiment
    reasoning about feedback loops, tipping points, and emergent system behaviour).
    Distinct from boom (boom = scale extremes; simulation = systemic feedback dynamics).
evidence: [L20-T04]
```

---

## L20-T05 — Model on-call scheduling as an operations research problem

**Task:** "We have 12 engineers, 4 services, and 3 on-call rotations to schedule for next
quarter. Model this as an operations research problem and identify the binding constraints."

**Expected tokens:** `probe struct full operations`

**Skill selection:**
- Task: probe (surface structure/constraints)
- Scope: struct (arrangements and dependencies of the scheduling problem)
- Method: operations (OR/management science framing ✅)
- Completeness: full

**Bar command:** `bar build probe struct full operations`

**Discovery notes:** User says "model this as an operations research problem" — trivially
discoverable because the user explicitly names the framework. No use_when needed.

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Gap diagnosis:** none

---

## L20-T06 — Mental models for service extraction decision

**Task:** "What named mental models are most useful for thinking through whether to extract
a service from a monolith?"

**Expected tokens:** `probe mean full models`

**Skill selection:**
- Task: probe (analyze the decision space)
- Scope: mean (conceptual framing of when extraction is right)
- Method: models ("explicitly identifying and naming relevant mental models" ✅)
- Completeness: full

**Bar command:** `bar build probe mean full models`

**Discovery notes:** User says "named mental models" — models description: "explicitly
identifying and naming relevant mental models, explaining why they apply (or fail)."
"Named mental models" appears in both user request and description. Largely description-anchored.

**Scores:** fitness 5, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Gap diagnosis:** none

---

## L20-T07 — CI/CD pipeline as an interacting system

**Task:** "How do the components of our CI/CD pipeline interact as a whole system?
Where do feedback loops and emergent bottlenecks form?"

**Expected tokens:** `probe struct full systemic`

**Skill selection:**
- Task: probe (analyze the system)
- Scope: struct (component arrangements and relationships)
- Method: systemic ("reasoning about the subject as an interacting whole, identifying
  components, boundaries, flows, feedback loops, and emergent behaviour" ✅)
- Completeness: full

**Bar command:** `bar build probe struct full systemic`

**Discovery notes:** User says "as a whole system" and "feedback loops and emergent bottlenecks"
— systemic description: "interacting whole... feedback loops... emergent behaviour." Both
"whole system" and "feedback loops" map directly. Largely description-anchored. Token name
`systemic` is not the most obvious but description rescues it.

**Scores:** fitness 4, completeness 4, correctness 4, clarity 5 → **Overall: 4** ✅

**Gap diagnosis:** none

---

## L20-T08 — Unknown unknowns in a database migration plan

**Task:** "What are the critical unknown unknowns in our plan to migrate from Postgres
to Cassandra?"

**Expected tokens:** `probe fail full unknowns`

**Skill selection:**
- Task: probe (surface implications)
- Scope: fail (what could go wrong)
- Method: unknowns ("identifying critical unknown unknowns" ✅)
- Completeness: full

**Bar command:** `bar build probe fail full unknowns`

**Discovery notes:** User says "unknown unknowns" — trivially discoverable from the
explicit phrase in the description and the token name itself.

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Gap diagnosis:** none

---

## L20-T09 — Falsification pressure on a performance assumption

**Task:** "Apply falsification pressure to our assumption that GraphQL will reduce
over-fetching in our mobile clients by 40%"

**Expected tokens:** `probe mean full verify`

**Skill selection:**
- Task: probe (analyze the assumption)
- Scope: mean (the conceptual framing of what the assumption claims)
- Method: verify ("applying falsification pressure to claims" ✅)
- Completeness: full

**Bar command:** `bar build probe mean full verify`

**Discovery notes:** User says "apply falsification pressure" — verify description: "applying
falsification pressure to claims." The user's exact phrasing matches. Trivially discoverable.

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Gap diagnosis:** none

---

## L20-T10 — Information flow model for observability pipeline

**Task:** "Model the information flow in our observability pipeline from metric emission
to alerting — where does signal degrade, get delayed, or get lost?"

**Expected tokens:** `probe struct full trans`

**Skill selection:**
- Task: probe (analyze the flow)
- Scope: struct (pipeline stages and their relationships)
- Method: trans ("information transfer model with source, encoding, channel, decoding,
  destination, and feedback... account for noise or distortion" ✅)
- Completeness: full

**Bar command:** `bar build probe struct full trans`

**Discovery risk:** `trans` is completely opaque. The token name gives no hint. Even the
label "Information transfer model with noise and feedback" is academic (Shannon channel
model). Users asking "where does signal degrade / get lost / get delayed" are asking the
right question for `trans`, but they won't say "apply an information transfer model" —
they'll say "trace the signal path" or "where does data get lost." Without use_when,
autopilot routes to `probe struct fail` (what breaks) or `probe struct flow` (step-by-step)
— both miss the noise/distortion/fidelity framing that makes `trans` distinctive.

**Scores:** fitness 4, completeness 3, correctness 2, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token
```yaml
gap_type: undiscoverable-token
task: L20-T10
token: trans
axis: method
observation: >
  'trans' models information transfer as a staged process (source → encoding → channel
  → decoding → destination → feedback), accounting for noise and distortion. The token
  name and academic framing are completely opaque. Users asking "where does signal
  degrade / get lost / get delayed" are asking the core trans question, but they won't
  say "information transfer model" or "Shannon channel analysis." Autopilot routes to
  probe+fail (what breaks) or probe+flow (step-by-step), missing the signal-fidelity
  and noise-accounting framing.
recommendation:
  action: edit (use_when)
  token: trans
  axis: method
  proposed_addition: >
    Information fidelity and signal degradation analysis: user asks where data or signal
    is lost, distorted, delayed, or degraded as it passes through a system. Heuristic:
    'where does signal get lost', 'where does data degrade', 'signal fidelity', 'where
    is information lost in transmission', 'where does the message get distorted',
    'trace signal path through the system', 'where does noise enter', 'signal-to-noise',
    'observability pipeline fidelity' → trans. Distinct from flow method (flow = narrate
    step-by-step sequence; trans = model noise, distortion, and fidelity across stages).
evidence: [L20-T10]
```

---

## Summary

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| L20-T01 | induce | 3 | Yes — G-L20-01 |
| L20-T02 | converge | 4 | No |
| L20-T03 | branch | 4 | No |
| L20-T04 | simulation (method) | 3 | Yes — G-L20-02 |
| L20-T05 | operations | 5 | No |
| L20-T06 | models | 4 | No |
| L20-T07 | systemic | 4 | No |
| L20-T08 | unknowns | 5 | No |
| L20-T09 | verify | 5 | No |
| L20-T10 | trans | 3 | Yes — G-L20-03 |

**Mean: 4.0/5**

**3 gaps found** (all undiscoverable-token):
- **G-L20-01**: `induce` — "generalize from observations" does not route to induce without use_when
- **G-L20-02**: `simulation` method — confused with `sim` task; "thought experiment" is key
  differentiator; feedback loops / tipping points don't route to simulation method
- **G-L20-03**: `trans` — completely opaque token name; "signal degrades / gets lost" doesn't route there

**Confirmed description-anchored (no use_when needed):**
converge, branch, operations, models, systemic, unknowns, verify — all score 4–5 from
description vocabulary or explicit user phrasing.
