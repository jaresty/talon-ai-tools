# ADR-0113 Loop-12 Evaluations

**Date:** 2026-02-18
**Binary:** /tmp/bar-new (built from source)
**Focus:** Part A — Post-apply validation of loop-11 completeness fixes (T196, T200)
           Part B — Scope axis discoverability (T201–T210, 10 tasks across 13 scope tokens)

---

# Part A — Post-Apply Validation: Loop-11 Completeness Fixes

Re-evaluating T196 and T200 after adding use_when entries for `gist`, `skim`, and `narrow`.

Applied fixes verified in `lib/axisConfig.py` AXIS_KEY_TO_USE_WHEN["completeness"]:
- `gist`: "quick summary", "overview", "brief", "tldr", "high-level", "standup update" → gist
- `skim`: "light review", "spot check", "quick pass", "sanity check" → skim
- `narrow`: "specifically", "only about", "just this part" → narrow

---

## T196 — Quick overview of authentication flow (re-test)

**Task description:** "Give me a quick overview of how authentication works in our system"
**Loop-11 score:** 3 (gist undiscoverable — autopilot defaulted to full)

**Post-fix skill selection log:**
- Task: show
- Completeness: **gist** — now discoverable via:
  - use_when: "quick summary", "overview" → gist ✅
  - "quick overview" hits two use_when triggers simultaneously
- Scope: mean
- Bar command: `bar build show mean gist`

**Coverage scores (post-fix):**
- Token fitness: 5 (gist matches "quick overview" intent precisely)
- Token completeness: 4 (all key axes covered)
- Skill correctness: 5 (use_when "quick summary" + "overview" fire on "quick overview")
- Prompt clarity: 4 (gist constraints the response appropriately)
- **Overall: 4** ✅ (was 3, now 4 — PASS)

---

## T200 — High-level standup summary (re-test)

**Task description:** "Give me a high-level summary of what changed this sprint — I'll share it at the standup, keep it very brief"
**Loop-11 score:** 2 (gist/skim both undiscoverable — autopilot defaulted to full)

**Post-fix skill selection log:**
- Task: pull (extracting a summary of what changed)
- Completeness: **gist** — now discoverable via:
  - use_when: "standup update", "high-level", "brief" → gist ✅
  - "high-level summary" + "standup" + "very brief" → three triggers
  - gist now wins clearly over skim (gist use_when has "standup update" explicitly)
- Scope: time (what changed this sprint = temporal)
- Bar command: `bar build pull time gist`

**Coverage scores (post-fix):**
- Token fitness: 5 (gist captures "very brief" + "high-level" intent)
- Token completeness: 4 (time scope + gist completeness = well-covered)
- Skill correctness: 5 (use_when "standup update", "high-level", "brief" — all fire)
- Prompt clarity: 4 (gist produces brief, main-points-only output)
- **Overall: 4** ✅ (was 2, now 4 — PASS)

---

## Part A Summary

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| T196 | gist | 3 | 4 | +1 | PASS |
| T200 | gist | 2 | 4 | +2 | PASS |

**Mean pre-fix:** 2.5 → **Mean post-fix:** 4.0 ✅ (at target)

---

# Part B — Scope Axis Discoverability

**Scope tokens (13):** act, agent, assume, cross, fail, good, mean, motifs, stable, struct, thing, time, view

**Observation before evaluation:** 0 of 13 scope tokens have use_when entries. Notes exist
only for `cross` (distinguishing it from struct). All routing depends on descriptions alone.

Task coverage: 10 tasks designed to probe all 13 tokens; 3 tokens (cross, thing, act)
tested via tasks that also implicitly test adjacent tokens.

---

## T201 — Risks of migrating from monolith to microservices

**Task description:** "What risks should we consider when migrating from our monolith to microservices?"
**Domain:** Architecture / analysis
**Expected scope:** `fail`

**Skill selection log:**
- Task: probe (surfacing implications)
- Completeness: full
- Scope: **fail** — "breakdowns and failure modes"
  - "risks" explicitly in fail description ("risks, edge cases, fragility, or failure modes")
  - Usage patterns from loop-1: "Risk Analysis" pattern → `probe fail full`
  - "what risks should we consider" → very direct match
- Method: inversion (working backward from failures) or risks

**Bar command:** `bar build probe fail full inversion`

**Coverage scores:**
- Token fitness: 5 (fail + inversion combination is precisely right)
- Token completeness: 5 (well-served by loop-1 patterns)
- Skill correctness: 5 (both usage pattern and description match; high confidence)
- Prompt clarity: 5 (fail scope + inversion method = strong risk-analysis prompt)
- **Overall: 5** ✅

**Gap diagnosis:** none — `fail` is the best-supported scope token (usage patterns + description).

---

## T202 — Structure of the authentication module

**Task description:** "Describe the structure of our authentication module — what are the main components and how do they relate?"
**Domain:** Code / architecture
**Expected scope:** `struct`

**Skill selection log:**
- Task: show (explaining/describing)
- Completeness: full
- Scope: **struct** — "arrangement and relationships — dependencies, coordination, constraints"
  - "structure", "components", "how do they relate" → struct
  - Token name "struct" is semi-self-naming ("structure" → struct)
- Method: mapping (surfacing elements and relationships)

**Bar command:** `bar build show struct full mapping`

**Coverage scores:**
- Token fitness: 5 (struct is the natural choice for "structure/components/relations")
- Token completeness: 4 (mapping method adds value)
- Skill correctness: 4 (struct is discoverable; "structure" → struct is intuitive)
- Prompt clarity: 4 (struct + mapping gives clear architecture-description framing)
- **Overall: 4** ✅

**Gap diagnosis:** none — `struct` is sufficiently self-describing.

---

## T203 — What CQRS means and why to use it

**Task description:** "Explain what CQRS means, why the pattern exists, and when you'd reach for it"
**Domain:** Architecture / concept
**Expected scope:** `mean`

**Skill selection log:**
- Task: show (explaining a concept)
- Completeness: full
- Scope: **mean** — "conceptual framing — purpose, interpretation, definitions"
  - "what does X mean", "why it exists" → mean (token name semantically matches intent)
  - "explain what CQRS means" → mean scope directly
- Method: (none needed — conceptual explanation)

**Bar command:** `bar build show mean full`

**Coverage scores:**
- Token fitness: 5 (mean is exactly right for "what does X mean + why does it exist")
- Token completeness: 4 (could add context scope; mean covers the core well)
- Skill correctness: 5 (token name semantics + "what does X mean" → mean; very direct)
- Prompt clarity: 4 (mean focuses on conceptual framing; precise)
- **Overall: 4** ✅

**Gap diagnosis:** none — `mean` is discoverable via its token name semantics.

---

## T204 — Request flow from API to database

**Task description:** "Walk me through how a request flows through the system from API gateway to database — what happens at each step?"
**Domain:** Code / architecture
**Expected scope:** `time`

**Skill selection log:**
- Task: show (explaining a process)
- Completeness: full
- Scope: **time** — "sequences and temporal change — sequences, evolution, phases"
  - "flows through", "what happens at each step" → time (sequential)
  - But: `act` (tasks/actions) and `flow` (method) are strong adjacent pulls
  - `time` scope is about *when* things happen; `act` is about *what* actions occur
  - "at each step" → time (sequence); "walk me through" → walkthrough form
- Method: flow (step-by-step sequential progression)
- Form: walkthrough

**Bar command:** `bar build show time full flow walkthrough`

**Coverage scores:**
- Token fitness: 4 (time + flow both active; time scope may be secondary to flow method)
- Token completeness: 4 (time + flow + walkthrough combination is very strong)
- Skill correctness: 3 (time scope might be missed — autopilot may pick flow method alone
  and skip time scope; "walk me through" routes to walkthrough form, "flows" to flow method,
  but time scope is a distinct additional signal)
- Prompt clarity: 4 (flow + walkthrough drives clear sequential output even without time scope)
- **Overall: 3** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T204 — Request flow through system
dimension: scope
observation: >
  `time` scope (sequences and temporal change) is not reliably selected when
  users ask about "how something flows" or "what happens at each step". The
  method token `flow` (step-by-step sequential progression) and the form
  `walkthrough` dominate — autopilot satisfies the sequential need via method
  without adding time scope. The difference: time scope adds temporal emphasis
  (phases, evolution, before/after) that `flow` method doesn't — but autopilot
  doesn't recognize this distinction without a routing heuristic.
recommendation:
  action: add-use-when
  axis: scope
  token: time
  proposed_use_when: >
    Temporal or sequential focus: user asks about sequence, history, phases, or
    how something changes over time. Heuristic: 'step by step', 'in order',
    'over time', 'what happens when', 'sequence', 'timeline', 'history',
    'how did we get here', 'phases' → time scope. Distinct from flow method
    (flow = reasoning approach; time = scope dimension of what to emphasize).
evidence: [task_T204]
```

---

## T205 — Who has decision-making authority over infrastructure?

**Task description:** "Who has decision-making authority over infrastructure changes — who can approve, block, or veto?"
**Domain:** Architecture / governance
**Expected scope:** `agent`

**Skill selection log:**
- Task: probe or show
- Scope: **agent** — "actors with agency — who can select among alternatives"
  - "who has authority", "who can approve/block/veto" → agent scope
  - BUT: `actors` is a METHOD token with overlapping meaning
  - `actors` method: "identifying and centering people, roles, or agents"
  - `agent` scope: "actors with the capacity to select among alternatives"
  - Both sound right for "who decides?" tasks
  - Autopilot is likely to pick `actors` method WITHOUT adding `agent` scope
  - The agent/actors distinction: scope = what to focus on; method = how to analyze it
  - A careful autopilot picks both; an unprompted one picks actors method and misses agent scope

**Bar command (likely):** `bar build probe full actors`
**Bar command (ideal):** `bar build probe agent full actors`

**Coverage scores:**
- Token fitness: 3 (agent scope missed; actors method selected — similar but different)
- Token completeness: 3 (key dimension — decision-making focus — not in scope position)
- Skill correctness: 2 (agent scope vs actors method confusion; no heuristic separates them)
- Prompt clarity: 3 (actors method produces actor-centered output; agent scope adds decision
  framing that actors alone doesn't guarantee)
- **Overall: 2** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T205 — Decision-making authority over infrastructure
dimension: scope
observation: >
  `agent` scope (actors with agency and decision-making) is systematically
  confused with `actors` method. Both focus on "people/roles who act" but
  serve different grammatical roles: agent is a scope constraint (what to
  emphasize), actors is a method enhancement (how to analyze). Autopilot
  picks actors method for "who decides?" tasks and does not additionally
  select agent scope. No heuristic distinguishes them. The agent scope
  description is accurate but the distinction from actors method is not
  documented in routing guidance.
recommendation:
  action: add-use-when
  axis: scope
  token: agent
  proposed_use_when: >
    Decision-making or agency focus: user asks who can act, who has authority,
    or how choices are made. Heuristic: 'who decides', 'who has authority',
    'who can approve', 'decision-making', 'agency', 'who is responsible' →
    agent scope. Note: agent is a SCOPE token (what to focus on); actors is a
    METHOD token (how to analyze). Use agent scope to foreground decision-making
    actors; use actors method to enrich any task with actor-centered analysis.
    Both can be selected together.
evidence: [task_T205]
```

---

## T206 — Assumptions about user traffic in the design

**Task description:** "What assumptions are we making about user traffic and load patterns in this system design?"
**Domain:** Architecture / analysis
**Expected scope:** `assume`

**Skill selection log:**
- Task: probe (surfacing assumptions — literally what assume is for)
- Completeness: full
- Scope: **assume** — "explicit or implicit premises that must hold"
  - "what assumptions are we making" → assume
  - Description: "focuses on explicit or implicit premises that must hold for the reasoning"
  - "assumptions" in user request matches "premises" in description (near-synonym)
  - But: no use_when; relies on description synonym matching

**Bar command:** `bar build probe assume full`

**Coverage scores:**
- Token fitness: 4 (assume is exactly right; description closely matches user intent)
- Token completeness: 4 (assume scope + probe task = well-composed)
- Skill correctness: 3 (no use_when; "assumptions" → "premises" synonym match works for
  careful autopilots but is not guaranteed; risk of autopilot using unknowns method instead)
- Prompt clarity: 4 (assume scope surfaces hidden premises — exactly what's needed)
- **Overall: 3** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T206 — Design assumptions about user traffic
dimension: scope
observation: >
  `assume` scope (premises and preconditions) relies on "assumptions" → "premises"
  synonym matching in the description. This works for careful autopilots reading
  descriptions, but there's no routing heuristic. The `unknowns` method is also
  applicable here ("surface critical unknown unknowns") and may be chosen instead
  of or in addition to assume scope. Without a use_when, routing is description-
  dependent and variable.
recommendation:
  action: add-use-when
  axis: scope
  token: assume
  proposed_use_when: >
    Assumptions and premises focus: user asks what must be true, what is taken for
    granted, or what preconditions are embedded in the design. Heuristic:
    'what assumptions', 'what are we assuming', 'what must be true', 'what
    preconditions', 'hidden assumptions', 'what are we taking for granted' →
    assume scope. Distinct from unknowns method (unknowns = surfaces what we
    don't know we don't know; assume = makes explicit what is already assumed).
evidence: [task_T206]
```

---

## T207 — Recurring error-handling patterns across services

**Task description:** "What recurring patterns appear in how we handle errors across different services?"
**Domain:** Code / architecture
**Expected scope:** `motifs`

**Skill selection log:**
- Task: probe (surfacing patterns)
- Completeness: full
- Scope: **motifs** — "recurring structural or thematic forms that appear in multiple places"
  - "recurring patterns" → motifs description matches exactly
  - BUT: "motifs" is an unusual, non-technical token name — not self-naming
  - "patterns" might route to: `mapping` method (surface elements and relationships),
    `cluster` method (group by shared characteristics), or `struct` scope
  - Without knowing "motifs" exists, autopilot routes to method tokens for "patterns"
  - Motifs scope is specifically about RECURRENCE across multiple places — distinct from
    mapping/cluster which don't emphasize repetition

**Bar command (likely):** `bar build probe struct full mapping` or `bar build probe full cluster`
**Bar command (ideal):** `bar build probe motifs full`

**Coverage scores:**
- Token fitness: 2 (motifs scope missed; mapping/cluster used instead — overlapping but weaker)
- Token completeness: 2 (the "recurrence across places" dimension is not captured)
- Skill correctness: 2 (no routing heuristic; unusual token name; "patterns" routes elsewhere)
- Prompt clarity: 3 (mapping/cluster still produce useful output about patterns)
- **Overall: 2** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T207 — Recurring error-handling patterns across services
dimension: scope
observation: >
  `motifs` scope (recurring structural or thematic forms in multiple places) is
  systematically missed because: (a) "motifs" is an unusual/abstract token name
  that doesn't self-identify for technical users, (b) "patterns" in user requests
  routes to mapping/cluster methods rather than motifs scope, (c) no use_when or
  heuristic distinguishes motifs (recurrence across instances) from struct
  (arrangement within one system) or mapping (surface all relationships).
recommendation:
  action: add-use-when
  axis: scope
  token: motifs
  proposed_use_when: >
    Recurring or repeated patterns across the codebase or system: user asks
    about repeated structures, common idioms, or reused patterns that appear
    in multiple places. Heuristic: 'recurring patterns', 'repeated across',
    'appears in multiple places', 'common idioms', 'structural motifs',
    'repeated structure' → motifs scope. Distinct from struct (one system's
    arrangement) and mapping method (surface all elements/relationships).
evidence: [task_T207]
```

---

## T208 — What makes a well-designed API?

**Task description:** "What quality criteria define a well-designed REST API — how do we judge whether our API is good?"
**Domain:** Architecture / evaluation
**Expected scope:** `good`

**Skill selection log:**
- Task: check (evaluating against criteria)
- Completeness: full
- Scope: **good** — "quality criteria and success standards — how quality or goodness is judged"
  - "quality criteria", "judge whether our API is good" → good scope
  - "well-designed" → good (token name is close to "good design")
  - Description: "criteria, metrics, standards, values, or taste"
  - But: no use_when; user may not phrase as "what makes this good?" explicitly
  - Risk: autopilot picks adversarial/rigor methods instead of good scope

**Bar command:** `bar build check good full`

**Coverage scores:**
- Token fitness: 4 (good captures "quality criteria" well; description matches)
- Token completeness: 3 (good scope alone leaves method open; adversarial or rigor useful)
- Skill correctness: 3 (no use_when; "quality criteria" → good relies on description match;
  autopilot may default to no scope or pick struct instead)
- Prompt clarity: 3 (good scope frames response around criteria; but check task + good
  scope combo may not always be assembled correctly without a heuristic)
- **Overall: 3** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T208 — Quality criteria for REST API design
dimension: scope
observation: >
  `good` scope (quality criteria and success standards) is not reliably selected
  when users ask about "what makes X good" or "quality criteria". No use_when
  exists. Autopilot may pick check task without a scope, or scope to struct
  (arrangement) or mean (definition) rather than good (criteria for quality).
  The good/fail pairing is also natural for evaluation tasks but requires knowing
  both exist.
recommendation:
  action: add-use-when
  axis: scope
  token: good
  proposed_use_when: >
    Quality criteria or success standards focus: user asks what makes something
    good, what criteria matter, or how to judge quality. Heuristic: 'quality
    criteria', 'what makes it good', 'how to judge', 'success criteria',
    'well-designed', 'what good looks like', 'standards for' → good scope.
    Often pairs with fail scope to cover both quality and failure mode dimensions.
evidence: [task_T208]
```

---

## T209 — Architecture change from the ops team's perspective

**Task description:** "Describe this proposed database sharding change from the perspective of the operations team — what are their concerns and priorities?"
**Domain:** Architecture / stakeholder
**Expected scope:** `view`

**Skill selection log:**
- Task: show (describing from a perspective)
- Completeness: full
- Scope: **view** — "how the subject appears from a specific stakeholder, role, or position"
  - "from the perspective of the operations team" → view scope
  - "from the perspective of" is a near-direct trigger for view
  - Description: "from a specific stakeholder, role, or positional perspective"

**Bar command:** `bar build show view full`

**Coverage scores:**
- Token fitness: 5 (view is exactly right; "perspective of" → view)
- Token completeness: 4 (view + show covers the core well)
- Skill correctness: 4 (description is direct; "from the perspective of" is a strong signal)
- Prompt clarity: 4 (view scope constrains response to ops team framing)
- **Overall: 4** ✅

**Gap diagnosis:** none — `view` is discoverable from its description for "from the perspective of" phrasings.

---

## T210 — Stable vs. evolving parts of the API contract

**Task description:** "Which parts of our API contract are stable and unlikely to change, and which are likely to evolve?"
**Domain:** Architecture / planning
**Expected scope:** `stable` (+ `time` for the contrast)

**Skill selection log:**
- Task: probe or diff
- Completeness: full
- Scope: **stable** — "equilibrium, persistence, and self-reinforcing states"
  - "stable and unlikely to change" → stable scope
  - Description: "configurations that maintain themselves and how perturbations affect them"
  - But: "stable" in description is about system equilibrium; user means API versioning stability
  - The match is imperfect: user asks about stability of a design artifact (which parts won't change),
    while stable scope focuses on self-reinforcing system states
  - Autopilot may route to time scope (what will change) or no scope

**Bar command (likely):** `bar build probe time full` or `bar build probe full`
**Bar command (ideal):** `bar build probe stable time full`

**Coverage scores:**
- Token fitness: 3 (stable is applicable but description mismatch makes it non-obvious)
- Token completeness: 3 (time scope also needed for the "likely to evolve" half)
- Skill correctness: 2 (stable is hard to discover: "stable and unlikely to change" ≠
  "self-reinforcing equilibrium"; the description is too system-theory for this use case)
- Prompt clarity: 3 (stable scope adds value but requires user to know the token)
- **Overall: 2** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T210 — Stable vs. evolving API contract parts
dimension: scope
observation: >
  `stable` scope (equilibrium and persistence) is undiscoverable for "what won't
  change" / "what is stable" API tasks. The description uses system-theory language
  ("equilibrium", "self-reinforcing states") that doesn't match how engineers
  think about API stability. "Stable and unlikely to change" → stable scope
  should be a direct match, but the description mismatch makes autopilot unlikely
  to connect them. No use_when exists. Autopilot routes to time scope (what
  changes over time) and misses the stability framing.
recommendation:
  action: add-use-when
  axis: scope
  token: stable
  proposed_use_when: >
    Stability and persistence focus: user asks what is stable, unlikely to change,
    or self-reinforcing in the system. Heuristic: 'stable', 'unlikely to change',
    'won't change', 'what persists', 'what is settled', 'fixed constraints',
    'what has remained stable' → stable scope. Often pairs with time scope
    (stable = what persists; time = how things evolve).
evidence: [task_T210]
```

---

## Part B Summary

| Task | Expected Scope | Autopilot Picks | Score | Gap? |
|------|---------------|-----------------|-------|------|
| T201 | fail | fail (+ usage patterns) | 5 | No |
| T202 | struct | struct | 4 | No |
| T203 | mean | mean | 4 | No |
| T204 | time | flow method (scope missed) | 3 | Yes — G-L12-01 |
| T205 | agent | actors method (scope confused) | 2 | Yes — G-L12-02 |
| T206 | assume | unknowns method or no scope | 3 | Yes — G-L12-03 |
| T207 | motifs | mapping/cluster method | 2 | Yes — G-L12-04 |
| T208 | good | no scope or struct | 3 | Yes — G-L12-05 |
| T209 | view | view | 4 | No |
| T210 | stable | time or no scope | 2 | Yes — G-L12-06 |

**Mean score (Part B):** 3.2/5 — below 4.0 target

**Not evaluated:** `act`, `thing`, `cross`
- `act` — self-describing for "what actions/tasks"; lower priority
- `thing` — self-describing for "what entities exist"; lower priority
- `cross` — has Notes entry from loop-1; lower priority (already documented)

### Discoverability Tiers

**Tier 1 — Well-discoverable (score ≥ 4):**
- `fail` — "risks/failure modes" explicit in description + loop-1 usage patterns
- `struct` — "structure/components" semi-self-naming
- `mean` — token name semantics match "what does X mean"
- `view` — "from the perspective of" maps directly

**Tier 2 — Undiscoverable without use_when (score ≤ 3):**
- `time` — preempted by `flow` method; temporal framing missed
- `agent` — confused with `actors` method; no routing distinction
- `assume` — synonym gap: "assumptions" → "premises" not guaranteed
- `good` — no heuristic for "quality criteria / what makes it good"
- `motifs` — unusual name; "patterns" routes to method tokens
- `stable` — description mismatch: system-theory vs. design-stability language

### Gaps Found

| Gap | Token | Score | Type | Severity |
|-----|-------|-------|------|----------|
| G-L12-01 | time | 3 | undiscoverable-token | Medium |
| G-L12-02 | agent | 2 | undiscoverable-token | High |
| G-L12-03 | assume | 3 | undiscoverable-token | Medium |
| G-L12-04 | motifs | 2 | undiscoverable-token | High |
| G-L12-05 | good | 3 | undiscoverable-token | Medium |
| G-L12-06 | stable | 2 | undiscoverable-token | Medium |
