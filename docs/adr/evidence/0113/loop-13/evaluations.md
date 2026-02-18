# ADR-0113 Loop-13 Evaluations

**Date:** 2026-02-18
**Binary:** /tmp/bar-new (built from source)
**Focus:** Part A — Post-apply validation of loop-12 scope fixes (T204, T205, T207, T210)
           Part B — Method axis discoverability (T211–T220, 10 tasks)

---

# Part A — Post-Apply Validation: Loop-12 Scope Fixes

Re-evaluating the 4 lowest-scoring scope tasks (pre-fix mean 2.25) after adding
use_when entries for `time`, `agent`, `motifs`, `stable`, `assume`, and `good`.

---

## T204 — Request flow through system (re-test)

**Task description:** "Walk me through how a request flows through the system from API gateway to database — what happens at each step?"
**Loop-12 score:** 3 (time scope missed — `flow` method preempted it)

**Post-fix skill selection:**
- Scope: **time** — now discoverable via use_when:
  - "step by step" fires on "at each step" ✅
  - "what happens when" fires on "what happens at each step" ✅
  - Two triggers → time scope selected alongside `flow` method

**Bar command (post-fix):** `bar build show time full flow walkthrough`

**Coverage scores (post-fix):**
- Token fitness: 5 (time + flow + walkthrough is the ideal combination)
- Token completeness: 4 (all key axes now covered)
- Skill correctness: 4 (two use_when triggers fire; time now selected, not just flow)
- Prompt clarity: 4 (time scope adds temporal framing; flow method adds sequencing)
- **Overall: 4** ✅ (was 3, now 4 — PASS)

---

## T205 — Who has decision-making authority (re-test)

**Task description:** "Who has decision-making authority over infrastructure changes — who can approve, block, or veto?"
**Loop-12 score:** 2 (agent scope missed — `actors` method preempted it)

**Post-fix skill selection:**
- Scope: **agent** — now discoverable via use_when:
  - "decision-making" fires ✅
  - "who has authority" fires ✅
  - "who can approve" fires ✅ (exact phrase match)
  - Triple trigger; also explicitly documents agent (scope) vs actors (method) distinction

**Bar command (post-fix):** `bar build probe agent full actors`

**Coverage scores (post-fix):**
- Token fitness: 5 (agent scope foregrounds decision-making; actors method adds actor analysis)
- Token completeness: 5 (both agent scope + actors method now selected together)
- Skill correctness: 5 (three use_when triggers fire; distinction from actors method documented)
- Prompt clarity: 5 (agent scope + actors method = explicit decision-authority framing)
- **Overall: 5** ✅ (was 2, now 5 — PASS)

---

## T207 — Recurring error-handling patterns (re-test)

**Task description:** "What recurring patterns appear in how we handle errors across different services?"
**Loop-12 score:** 2 (motifs scope missed — `mapping`/`cluster` methods preempted it)

**Post-fix skill selection:**
- Scope: **motifs** — now discoverable via use_when:
  - "recurring patterns" → exact phrase match ✅
  - "appears in multiple places" fires on "across different services" ✅

**Bar command (post-fix):** `bar build probe motifs full`

**Coverage scores (post-fix):**
- Token fitness: 5 (motifs is precisely right for recurring cross-service patterns)
- Token completeness: 4 (motifs scope captures the key dimension)
- Skill correctness: 5 ("recurring patterns" is exact — highest-confidence trigger of all fixes)
- Prompt clarity: 5 (motifs scope frames response around repeated structural forms)
- **Overall: 5** ✅ (was 2, now 5 — PASS)

---

## T210 — Stable vs. evolving API contract (re-test)

**Task description:** "Which parts of our API contract are stable and unlikely to change, and which are likely to evolve?"
**Loop-12 score:** 2 (stable scope missed — description mismatch + time scope won)

**Post-fix skill selection:**
- Scope: **stable** — now discoverable via use_when:
  - "stable" fires ✅ (exact match)
  - "unlikely to change" fires ✅ (exact phrase)
  - Double trigger; time scope also selected for "likely to evolve" half → ideal: stable + time

**Bar command (post-fix):** `bar build probe stable time full`

**Coverage scores (post-fix):**
- Token fitness: 5 (stable + time covers both halves of the question)
- Token completeness: 5 (stable for persistence, time for evolution — complete coverage)
- Skill correctness: 5 ("stable" + "unlikely to change" — two exact phrase matches)
- Prompt clarity: 5 (stable + time scopes frame the response around the contrast)
- **Overall: 5** ✅ (was 2, now 5 — PASS)

---

## Part A Summary

| Task | Scope | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| T204 | time | 3 | 4 | +1 | PASS |
| T205 | agent | 2 | 5 | +3 | PASS |
| T207 | motifs | 2 | 5 | +3 | PASS |
| T210 | stable | 2 | 5 | +3 | PASS |

**Mean pre-fix:** 2.25 → **Mean post-fix:** 4.75 ✅

Three tasks went straight to 5 — these were the cleanest fixes in any loop so far.
Exact phrase matches ("recurring patterns", "unlikely to change", "who can approve")
are far stronger routing signals than synonym matching.

---

# Part B — Method Axis Discoverability

**Method tokens (51):** abduce, actors, adversarial, analog, analysis, argue, bias, boom,
branch, calc, cite, cluster, compare, converge, deduce, depends, diagnose, dimension,
domains, effects, experimental, explore, field, flow, grove, grow, induce, inversion,
jobs, mapping, meld, melody, mod, models, objectivity, operations, order, origin,
prioritize, probability, product, resilience, rigor, risks, robust, shift, simulation,
spec, split, systemic, unknowns, verify

**Observation:** 0 of 51 method tokens have use_when entries. All routing is description-only.

**Sampling strategy:** Focus on metaphorical/opaque names (boom, grove, melody, grow)
and tokens that compete with similar tokens (resilience vs robust, systemic vs mapping,
inversion vs adversarial). Skip tokens that are clearly self-describing (compare, diagnose,
flow, risks, prioritize, verify, explore, depends, cite, branch, adversarial).

---

## T211 — Behavior at extreme traffic load

**Task description:** "Our API handles 10k req/s normally. What breaks first if traffic suddenly spikes to 10x — 100k req/s?"
**Domain:** Architecture / resilience
**Target method:** `boom`

**boom:** "explore behaviour toward extremes of scale or intensity, examining what breaks,
dominates, or vanishes"

**Skill selection log:**
- Task: probe
- Scope: fail (breakdowns), struct (where things break)
- Method: **boom** ideally — but: "boom" doesn't signal "scale extremes" at all
  - Autopilot more likely picks: `risks` (what could go wrong), `adversarial` (stress test),
    `resilience` (behaviour under stress), or `simulation` (what-if scenario)
  - `boom` description has "extremes of scale" but token name provides zero routing signal
  - No user would type "let's do a boom analysis" — it's not an industry term

**Bar command (likely):** `bar build probe fail full resilience`
**Bar command (ideal):** `bar build probe fail full boom`

**Coverage scores:**
- Token fitness: 2 (resilience/adversarial capture similar intent; boom's scale-extreme
  specificity is lost)
- Token completeness: 3 (fail scope + resilience covers most of the need)
- Skill correctness: 2 (no routing path — "boom" is an opaque metaphor; not discoverable
  from any common user phrasing)
- Prompt clarity: 3 (resilience/adversarial still produce useful output)
- **Overall: 2** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T211 — API behavior at 10x traffic spike
dimension: method
observation: >
  `boom` method (behaviour at extremes of scale) is systematically missed because
  the token name "boom" provides no routing signal. Users asking about scale extremes
  say "what breaks at 10x", "extreme load", "scale to limits" — none of which map
  to "boom". Autopilot picks resilience, adversarial, or simulation instead. The
  boom token is unique (scale-extreme exploration) but invisible without a heuristic.
recommendation:
  action: add-use-when
  axis: method
  token: boom
  proposed_use_when: >
    Scale extreme analysis: user asks what happens at 10x, 100x, or at the limits
    of the system. Heuristic: 'at 10x', 'at extreme load', 'what breaks at scale',
    'pushed to the limit', 'at maximum load', 'what dominates at scale',
    'scale extremes' → boom. Distinct from resilience (resilience = behavior under
    stress at normal extremes; boom = behavior at mathematical extremes of scale).
evidence: [task_T211]
```

---

## T212 — Compounding bottlenecks as user base grows

**Task description:** "As our user base grows from 10k to 1M users, what bottlenecks compound and what technical debt accumulates fastest?"
**Domain:** Architecture / planning
**Target method:** `grove`

**grove:** "examine how small effects compound into larger outcomes through feedback loops,
network effects, or iterative growth — asking not just what fails or succeeds, but HOW
failures OR successes accumulate through systemic mechanisms"

**Skill selection log:**
- Task: probe
- Method: **grove** ideally — but: "grove" is a completely opaque metaphor
  - "compound", "accumulate", "feedback loops" are the grove triggers — but none of them
    appear in the token name
  - Autopilot picks: `simulation` (how things evolve over time), `systemic` (feedback loops),
    `effects` (second-order effects), or `risks` (what goes wrong)
  - "grove" as a method name would only be discovered by someone who has read the full catalog

**Bar command (likely):** `bar build probe fail full systemic`
**Bar command (ideal):** `bar build probe fail full grove`

**Coverage scores:**
- Token fitness: 2 (systemic captures feedback loops but not the accumulation/compounding
  framing that is grove's specific contribution)
- Token completeness: 3 (systemic or effects cover parts of the need)
- Skill correctness: 1 (no routing path — "grove" is opaque; "compound" and "accumulate"
  don't link to any known token name)
- Prompt clarity: 3 (systemic/effects still useful)
- **Overall: 1** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T212 — Compounding bottlenecks during growth
dimension: method
observation: >
  `grove` method (how small effects compound through feedback loops and iterative
  growth) is completely undiscoverable. The token name "grove" is a metaphor with
  no relationship to accumulation, compounding, or growth dynamics. Users say
  "compound", "accumulate", "technical debt grows", "feedback loops" — none
  routing to "grove". Autopilot picks systemic or effects instead. Grove is
  distinct from both: systemic = interacting whole; effects = second/third-order
  consequences; grove = HOW things accumulate over iterations.
recommendation:
  action: add-use-when
  axis: method
  token: grove
  proposed_use_when: >
    Accumulation and compounding analysis: user asks how small effects build up
    over time, how debt or improvement compounds, or how feedback loops amplify
    outcomes. Heuristic: 'compound', 'accumulates over time', 'feedback loop',
    'network effect', 'technical debt grows', 'exponential growth', 'how things
    build up', 'rate of change' → grove. Distinct from systemic (systemic =
    interacting whole; grove = rate of accumulation through mechanisms) and
    effects (effects = trace consequences; grove = examine HOW they compound).
evidence: [task_T212]
```

---

## T213 — Coordinate database migration across teams

**Task description:** "We need to migrate our database schema without downtime. How do we coordinate this across the backend, data, and platform teams?"
**Domain:** Architecture / coordination
**Target method:** `melody`

**melody:** "analyze coordination across components, time, or teams, including coupling,
synchronization, and change alignment"

**Skill selection log:**
- Task: plan
- Method: **melody** ideally — but: "melody" doesn't signal "cross-team coordination"
  - "coordinate" could route to: `actors` (center the teams involved), `depends` (dependencies),
    `systemic` (interactions), or `flow` (sequence)
  - "melody" as a metaphor for coordination is evocative but completely non-literal
  - A user saying "help me coordinate this migration" has no path to "melody"

**Bar command (likely):** `bar build plan act full depends`
**Bar command (ideal):** `bar build plan act full melody`

**Coverage scores:**
- Token fitness: 2 (depends covers coupling; melody's synchronization and change-alignment
  framing is lost)
- Token completeness: 3 (depends + actors captures most of the multi-team need)
- Skill correctness: 2 (no routing path — "melody" requires knowing the token exists)
- Prompt clarity: 3 (depends/actors useful but misses coordination-timing dimension)
- **Overall: 2** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T213 — Cross-team database migration coordination
dimension: method
observation: >
  `melody` method (coordination across components, time, or teams — coupling,
  synchronization, change alignment) is systematically missed because "melody"
  is a musical metaphor with no literal relationship to coordination. Users asking
  "how do we coordinate across teams" route to actors, depends, or systemic instead.
  Melody's specific value (synchronization timing, coupling analysis, change alignment)
  is distinct from depends (what relies on what) but invisible without a heuristic.
recommendation:
  action: add-use-when
  axis: method
  token: melody
  proposed_use_when: >
    Cross-component or cross-team coordination analysis: user asks how to synchronize
    work, manage coupling, or align changes across teams or components. Heuristic:
    'coordinate across teams', 'synchronize changes', 'change alignment', 'coupling
    between components', 'parallel work streams', 'avoid conflicts between teams',
    'migration coordination' → melody. Distinct from depends (depends = what relies
    on what; melody = how coordination, timing, and coupling should be managed).
evidence: [task_T213]
```

---

## T214 — Cognitive biases in architectural decision

**Task description:** "We're deciding between a message queue and a REST API for async processing. What cognitive biases might affect our decision?"
**Domain:** Decision-making
**Target method:** `bias`

**bias:** "identify likely cognitive biases, heuristics, or systematic errors that might
distort judgment or conclusions"

**Skill selection log:**
- Task: probe
- Method: **bias** — "cognitive biases" is in the description; user says "cognitive biases"
  - Near-self-naming: token name "bias" + user phrase "cognitive biases" = direct match
  - High confidence routing

**Bar command:** `bar build probe full bias`

**Coverage scores:**
- Token fitness: 5 (bias is exactly right; token name + user phrase align)
- Token completeness: 4 (bias method well-specified for this task)
- Skill correctness: 5 ("cognitive biases" in user request → bias description says "cognitive
  biases, heuristics, or systematic errors")
- Prompt clarity: 4 (bias method produces cognitive-bias-focused analysis)
- **Overall: 4** ✅

**Gap diagnosis:** none — `bias` is discoverable from its description for "cognitive biases" phrasings.

---

## T215 — How our codebase ended up in its current state

**Task description:** "Our authentication service is a mess of patches and workarounds. How did we get here — what decisions led to this?"
**Domain:** Code / archaeology
**Target method:** `origin`

**origin:** "uncover how the subject arose, why it looks this way now, and how past decisions
shaped the present state"

**Skill selection log:**
- Task: probe or show
- Method: **origin** — description has "how the subject arose" and "past decisions shaped
  the present state"
  - User says "how did we get here", "what decisions led to this" → origin
  - Description maps well; "origin" is a clear enough metaphor

**Bar command:** `bar build probe time full origin`

**Coverage scores:**
- Token fitness: 5 (origin perfectly captures "how did we get here" intent)
- Token completeness: 4 (time scope + origin method covers history-of-decisions framing)
- Skill correctness: 4 ("how did we get here" → origin; description match is strong)
- Prompt clarity: 4 (origin + time = clear historical-archaeology framing)
- **Overall: 4** ✅

**Gap diagnosis:** none — `origin` is sufficiently discoverable for "how did we get here" phrasings.

---

## T216 — What happens if we remove the cache entirely

**Task description:** "What would happen if we removed the Redis caching layer entirely — walk through the scenario step by step."
**Domain:** Architecture / analysis
**Target method:** `simulation`

**simulation:** "explicit thought experiments or scenario walkthroughs that project evolution
over time, highlighting feedback loops, bottlenecks, tipping points, and emergent effects"

**Skill selection log:**
- Task: sim or probe
- Method: **simulation** — "what would happen if" is a thought experiment
  - Task token `sim` also covers this: "play out a scenario over time"
  - sim task + simulation method is potentially redundant but complementary
  - "walk through the scenario step by step" → simulation or walkthrough form

**Bar command:** `bar build sim fail full simulation`

**Coverage scores:**
- Token fitness: 4 (sim task + simulation method; combined they provide strong scenario framing)
- Token completeness: 4 (fail scope adds "what breaks" dimension)
- Skill correctness: 4 ("what would happen if" → sim task; "walk through scenario" → simulation method)
- Prompt clarity: 4 (sim + simulation = explicit scenario walkthrough)
- **Overall: 4** ✅

**Gap diagnosis:** none — `simulation` is discoverable via its description for "what would happen if" phrasings.

---

## T217 — Jobs to be done for internal platform engineers

**Task description:** "Analyze our internal developer platform from a jobs-to-be-done perspective — what are engineers trying to accomplish and what forces shape their tool choices?"
**Domain:** Product / platform
**Target method:** `jobs`

**jobs:** "analyzing Jobs To Be Done — the outcomes users want to achieve and the forces
shaping their choices"

**Skill selection log:**
- Task: probe
- Method: **jobs** — user explicitly says "jobs-to-be-done" and "forces shape their choices"
  - "jobs-to-be-done" is a known product framework; token name matches the framework name
  - Self-naming for users who know the framework; "forces shaping choices" also in description

**Bar command:** `bar build probe full jobs`

**Coverage scores:**
- Token fitness: 5 (jobs is exactly the framework the user invoked)
- Token completeness: 4 (jobs method well-specified)
- Skill correctness: 5 ("jobs-to-be-done" → jobs; framework name match)
- Prompt clarity: 4 (jobs method frames response around outcomes and forces)
- **Overall: 4** ✅

**Gap diagnosis:** none for explicit JTBD users. Minor: users who don't know the framework
name ("what do engineers actually need?") might not route to `jobs`. Lower severity —
framework-aware users who invoke JTBD know to use the term.

---

## T218 — Build simplest auth system first, expand later

**Task description:** "Let's implement the authentication system by starting with the absolute minimum that works, then add features only as we actually need them."
**Domain:** Software design
**Target method:** `grow`

**grow:** "preserve the simplest form adequate to the current purpose and expanding only
when new demands demonstrably outgrow it, so that every abstraction and exception arises
from necessity rather than anticipation"

**Skill selection log:**
- Task: make or plan
- Method: **grow** — "simplest minimum, add only as needed" matches grow description exactly
  - BUT: "grow" as a token name doesn't signal "start simple and expand"
  - User says "minimum that works, add features only as needed" — description match is very
    strong but token name is opaque
  - Autopilot might pick: `spec` (define criteria first), `converge` (narrow to focus),
    or no method (just make + minimal completeness)

**Bar command (likely):** `bar build make minimal`
**Bar command (ideal):** `bar build make minimal grow`

**Coverage scores:**
- Token fitness: 2 (minimal completeness captures "minimum" but misses grow's "expand only
  when outgrown" contract — the evolutionary stance)
- Token completeness: 3 (make + minimal covers the artifact; grow's design philosophy lost)
- Skill correctness: 2 ("start simple and expand" → grow requires knowing the token exists;
  no routing heuristic; description is perfect match but name is misleading)
- Prompt clarity: 3 (minimal produces a minimal result; grow would add the expansion framing)
- **Overall: 2** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T218 — Implement auth system starting minimal, expand as needed
dimension: method
observation: >
  `grow` method (preserve simplest form, expand only when outgrown — YAGNI/evolutionary
  design philosophy) is undiscoverable because "grow" doesn't signal "start simple".
  Users expressing this intent say "minimum viable", "start with the simplest thing",
  "YAGNI", "add only what's needed" — none routing to "grow". Autopilot picks minimal
  completeness (correctly for the artifact) but misses the evolutionary-design method
  that grow encodes (expand only when demonstrably outgrown).
recommendation:
  action: add-use-when
  axis: method
  token: grow
  proposed_use_when: >
    Evolutionary or incremental design approach: user wants to start minimal and
    expand only as needed. Heuristic: 'start simple and expand', 'minimum viable',
    'YAGNI', 'add only what you need', 'simplest thing that works', 'evolve as
    needed', 'don't over-engineer', 'add features only when required' → grow.
    Distinct from minimal completeness (minimal = brevity of output; grow = design
    philosophy of evolutionary expansion from minimum).
evidence: [task_T218]
```

---

## T219 — Work backward from authentication failure modes

**Task description:** "Our auth system has had three outages this quarter. Work backward from the worst possible failure — total authentication unavailability — to find the design choices that create this risk."
**Domain:** Architecture / reliability
**Target method:** `inversion`

**inversion:** "begin from undesirable or catastrophic outcomes, working backward to avoid,
mitigate, or design around those paths"

**Skill selection log:**
- Task: probe
- Method: **inversion** — description is "begin from catastrophic outcomes, work backward"
  - User says "work backward from the worst possible failure" → inversion (near-exact)
  - Notes explicitly say "well-suited for architecture evaluation: start from named failure
    modes and ask which design choices create or amplify them"
  - User phrase matches both description and notes

**Bar command:** `bar build probe fail full inversion`

**Coverage scores:**
- Token fitness: 5 (inversion is exactly right; description + notes match user intent)
- Token completeness: 4 (fail scope + inversion method = strong)
- Skill correctness: 5 ("work backward from worst failure" → inversion; description + notes
  both provide routing signal)
- Prompt clarity: 5 (inversion method structures analysis around catastrophic-outcome-first)
- **Overall: 5** ✅

**Gap diagnosis:** none — `inversion` is well-described and the notes add an explicit
architecture-evaluation routing signal.

---

## T220 — Systemic analysis of why incidents keep recurring

**Task description:** "We've had the same class of production incidents three times this year. Help me analyze the system as an interconnected whole — what feedback loops are keeping this problem alive?"
**Domain:** Reliability / system analysis
**Target method:** `systemic`

**systemic:** "reasoning about the subject as an interacting whole, identifying components,
boundaries, flows, feedback loops, and emergent behaviour that arise from their interactions"

**Skill selection log:**
- Task: probe
- Method: **systemic** — description is "interacting whole, feedback loops, emergent behaviour"
  - User explicitly says "system as an interconnected whole" and "feedback loops"
  - Phrase-level match: "feedback loops" appears in both user request and systemic description
  - Likely well-discoverable

**Bar command:** `bar build probe fail full systemic`

**Coverage scores:**
- Token fitness: 5 (systemic is precisely right; user explicitly invokes the systemic framing)
- Token completeness: 4 (fail scope adds the incident/breakdown lens)
- Skill correctness: 5 ("interconnected whole" + "feedback loops" → systemic; both phrases
  appear in the description)
- Prompt clarity: 5 (systemic method structures response around whole-system interactions)
- **Overall: 5** ✅

**Gap diagnosis:** none — `systemic` is discoverable for "interconnected whole / feedback loops" phrasings.

---

## Part B Summary

| Task | Target Method | Score | Gap? |
|------|--------------|-------|------|
| T211 | boom | 2 | Yes — G-L13-01 |
| T212 | grove | 1 | Yes — G-L13-02 |
| T213 | melody | 2 | Yes — G-L13-03 |
| T214 | bias | 4 | No |
| T215 | origin | 4 | No |
| T216 | simulation | 4 | No |
| T217 | jobs | 4 | No |
| T218 | grow | 2 | Yes — G-L13-04 |
| T219 | inversion | 5 | No |
| T220 | systemic | 5 | No |

**Mean score (Part B):** 3.3/5 — below 4.0 target

### Discoverability Tiers (Method Axis, sampled)

**Tier 1 — Well-discoverable (no use_when needed):**
- `bias` (4) — "cognitive biases" in description; user phrase matches
- `origin` (4) — "how did we get here" in description
- `simulation` (4) — "what would happen if" → sim task/simulation method
- `jobs` (4) — JTBD framework name; self-naming for framework users
- `inversion` (5) — "work backward from failures"; notes add explicit routing
- `systemic` (5) — "feedback loops" + "interconnected whole" in description

**Tier 2 — Undiscoverable (opaque names):**
- `boom` (2) — musical/onomatopoeia metaphor; no routing path
- `grove` (1) — botanical metaphor; completely opaque
- `melody` (2) — musical metaphor; coordination context lost
- `grow` (2) — describes evolutionary design but name signals generic growth

### Pattern: Metaphorical Method Names

The method axis uses several evocative metaphorical names that are memorable but
not self-describing: `boom`, `grove`, `melody`, `grow`, `meld`, `mod`, `field`.
These tokens provide powerful reasoning frames but are completely invisible to
bar-autopilot without use_when entries.

Unsampled tokens likely also undiscoverable: `meld` (combinations/overlaps),
`mod` (cyclic reasoning), `field` (shared structured medium).

### Gaps Found

| Gap | Token | Score | Severity |
|-----|-------|-------|----------|
| G-L13-01 | boom | 2 | Medium — scale-extreme analysis is a real use case |
| G-L13-02 | grove | 1 | High — compounding/accumulation tasks have no routing path at all |
| G-L13-03 | melody | 2 | Medium — cross-team coordination tasks use actors/depends instead |
| G-L13-04 | grow | 2 | Medium — YAGNI/evolutionary design has no routing path |
