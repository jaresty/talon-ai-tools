# ADR-0113 Loop-14 Evaluations

**Date:** 2026-02-18
**Binary:** /tmp/bar-new (built from source)
**Focus:** Part A — Post-apply validation of loop-13 method fixes (T211, T212, T213, T218)
           Part B — Remaining metaphorical method tokens: meld, mod, field, shift (T221–T224)
           Part C — Next axis recommendation

---

# Part A — Post-Apply Validation: Loop-13 Method Fixes

Re-evaluating the 4 lowest-scoring tasks (pre-fix mean 1.75) after adding use_when
entries for `boom`, `grove`, `grow`, and `melody`.

---

## T211 — API behavior at 10x traffic spike (re-test)

**Loop-13 score:** 2 (boom missed — "boom" opaque, resilience used instead)

**Post-fix skill selection:**
- Method: **boom** — now discoverable via use_when:
  - "at 10x" → fires on "10x req/s" ✅
  - "what breaks at scale" → fires on "What breaks first if traffic suddenly spikes" ✅
  - Double trigger

**Bar command (post-fix):** `bar build probe fail full boom`

**Coverage scores (post-fix):**
- Token fitness: 5 (boom = scale-extreme exploration; user is asking exactly this)
- Token completeness: 4 (boom + fail scope covers the need well)
- Skill correctness: 4 (two use_when triggers fire; boom now selected over resilience)
- Prompt clarity: 4 (boom adds scale-extreme specificity beyond resilience alone)
- **Overall: 4** ✅ (was 2, now 4 — PASS)

---

## T212 — Compounding bottlenecks during growth (re-test)

**Loop-13 score:** 1 (grove missed — completely opaque name, systemic used)

**Post-fix skill selection:**
- Method: **grove** — now discoverable via use_when:
  - "compound" → fires on "what bottlenecks compound" ✅ (exact match)
  - "accumulates" → fires on "technical debt accumulates fastest" ✅
  - Double exact match

**Bar command (post-fix):** `bar build probe fail full grove`

**Coverage scores (post-fix):**
- Token fitness: 5 (grove = accumulation through mechanisms; user asks exactly this)
- Token completeness: 4 (grove + fail scope covers compounding failure modes)
- Skill correctness: 5 ("compound" + "accumulates" — both exact heuristic triggers)
- Prompt clarity: 4 (grove frames response around rate-of-accumulation through mechanisms)
- **Overall: 4** ✅ (was 1, now 4 — PASS, +3 delta)

---

## T213 — Cross-team database migration coordination (re-test)

**Loop-13 score:** 2 (melody missed — musical metaphor, depends used instead)

**Post-fix skill selection:**
- Method: **melody** — now discoverable via use_when:
  - "coordinate across teams" → fires on "coordinate this across the backend, data, and platform teams" ✅
  - "migration coordination" → fires on "database migration" + "coordinate" ✅
  - Double trigger

**Bar command (post-fix):** `bar build plan act full melody`

**Coverage scores (post-fix):**
- Token fitness: 5 (melody = coordination, synchronization, change alignment across teams)
- Token completeness: 4 (melody + act scope covers the coordination need)
- Skill correctness: 4 (two triggers fire; melody selected over depends)
- Prompt clarity: 4 (melody adds timing and synchronization framing beyond depends alone)
- **Overall: 4** ✅ (was 2, now 4 — PASS)

---

## T218 — Implement auth system minimal-first (re-test)

**Loop-13 score:** 2 (grow missed — opaque name, minimal completeness used instead)

**Post-fix skill selection:**
- Method: **grow** — now discoverable via use_when:
  - "add features only when required" → fires on "add features only as we actually need them" ✅
  - "minimum viable" → fires on "absolute minimum that works" ✅
  - "simplest thing that works" → fires ✅ (user says "absolute minimum that works")
  - Triple trigger

**Bar command (post-fix):** `bar build make minimal grow`

**Coverage scores (post-fix):**
- Token fitness: 5 (grow = expand only when outgrown; perfectly captures user's intent)
- Token completeness: 5 (minimal completeness + grow method = complete encoding of intent)
- Skill correctness: 5 (three use_when triggers fire simultaneously; very high confidence)
- Prompt clarity: 5 (grow + minimal = explicit evolutionary-design-from-minimum framing)
- **Overall: 5** ✅ (was 2, now 5 — PASS, +3 delta)

---

## Part A Summary

| Task | Method | Pre-fix | Post-fix | Delta | Verdict |
|------|--------|---------|---------|-------|---------|
| T211 | boom | 2 | 4 | +2 | PASS |
| T212 | grove | 1 | 4 | +3 | PASS |
| T213 | melody | 2 | 4 | +2 | PASS |
| T218 | grow | 2 | 5 | +3 | PASS |

**Mean pre-fix:** 1.75 → **Mean post-fix:** 4.25 ✅ (target ≥4.0)

T218 (grow) and T212 (grove) both reached 5 — exact-phrase triggers from user text
produce near-certain routing even for the most opaque metaphorical token names.

---

# Part B — Remaining Metaphorical Method Tokens

**Tokens:** `meld`, `mod`, `field`, `shift`

**From the reference:**
- `meld` — "reasoning about combinations, overlaps, balances, and constraints between elements"
- `mod` — "modulo-style reasoning — equivalence classes, cyclic patterns, periodic behavior"
- `field` — "interaction through a shared structured medium; effects from structural compatibility"
- `shift` — "rotating through distinct perspectives or cognitive modes"

---

## T221 — Balance consistency vs. availability in database design

**Task description:** "Help me think through the trade-offs between consistency and availability in our database design — find the right balance for our use case."
**Target method:** `meld`

**meld:** "reasoning about combinations, overlaps, balances, and constraints between elements"

**Skill selection log:**
- Task: probe or pick
- Method: **meld** — "combinations, overlaps, balances, and constraints"
  - "trade-offs between" and "right balance" → meld (balancing constraints)
  - BUT: `compare` method ("compare alternatives against criteria") competes strongly
  - `branch` (parallel reasoning paths) also applicable
  - "meld" doesn't signal "balancing constraints" in its name — opaque metaphor
  - A careful autopilot reading descriptions might find meld, but compare dominates

**Bar command (likely):** `bar build probe full compare`
**Bar command (ideal):** `bar build probe full meld`

**Coverage scores:**
- Token fitness: 2 (compare covers the analysis but misses meld's constraint-balancing frame)
- Token completeness: 3 (compare + branch covers much of the need)
- Skill correctness: 2 (no use_when; "balance" and "trade-offs" don't route to "meld")
- Prompt clarity: 3 (compare produces useful output; meld's constraint-combination frame lost)
- **Overall: 2** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T221 — Consistency vs availability balance
dimension: method
observation: >
  `meld` method (combinations, overlaps, balances, constraints between elements)
  is preempted by `compare` for any "trade-offs between X and Y" task. "Meld"
  as a name suggests blending/combining, not constraint-balancing — it's a
  partial metaphor. Users phrase balance tasks as "trade-offs", "right balance",
  "weighing X against Y" — none routing to meld. Compare and branch dominate.
recommendation:
  action: add-use-when
  axis: method
  token: meld
  proposed_use_when: >
    Constraint-balancing or tension-resolution analysis: user asks how to balance
    competing forces, find overlaps, or navigate constraints between elements.
    Heuristic: 'balance between', 'overlap between', 'constraints between',
    'combining X and Y', 'where X and Y interact', 'navigate tensions between',
    'find the combination that satisfies' → meld. Distinct from compare (compare
    = evaluate alternatives against criteria; meld = balance constraints between
    elements that must coexist).
evidence: [task_T221]
```

---

## T222 — Patterns that repeat across retry cycles

**Task description:** "Our retry logic uses exponential backoff with jitter. What patterns repeat across retry cycles — are there cyclic behaviors we should be aware of?"
**Target method:** `mod`

**mod:** "equivalence classes, cyclic patterns, quotient structures, or periodic behavior
that repeats with a defined period or wraps around boundaries"

**Skill selection log:**
- Task: probe
- Method: **mod** — "cyclic patterns, periodic behavior that repeats"
  - User explicitly says "patterns repeat across retry cycles" and "cyclic behaviors"
  - Description has "cyclic patterns" — direct match
  - BUT: "mod" as a token name means modulo arithmetic to most developers
  - Autopilot may pick `simulation`, `resilience`, or `systemic` for retry analysis
  - The description matches well; token name is the barrier

**Bar command (likely):** `bar build probe fail full simulation`
**Bar command (ideal):** `bar build probe fail full mod`

**Coverage scores:**
- Token fitness: 2 (mod adds cyclic/periodic frame; simulation/systemic miss this dimension)
- Token completeness: 3 (fail scope + systemic covers most of the need)
- Skill correctness: 2 (description matches; "mod" name interpreted as modulo not cyclic patterns; no use_when)
- Prompt clarity: 3 (simulation useful; mod's periodic-behavior frame lost)
- **Overall: 2** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T222 — Cyclic behaviors in retry logic
dimension: method
observation: >
  `mod` method (cyclic patterns, periodic behavior, equivalence classes) is
  undiscoverable because "mod" is interpreted as modulo arithmetic rather than
  as cyclic-pattern analysis. Users saying "repeats across cycles", "cyclic
  behaviors", "periodic patterns" don't have a routing path to mod. Description
  matches but name creates a false disambiguation.
recommendation:
  action: add-use-when
  axis: method
  token: mod
  proposed_use_when: >
    Cyclic or periodic pattern analysis: user asks about behavior that repeats,
    wraps around, or follows a cycle. Heuristic: 'repeats across cycles', 'cyclic
    behavior', 'periodic pattern', 'repeating structure', 'what wraps around',
    'recurs periodically', 'equivalent states' → mod. Distinct from motifs scope
    (motifs = recurring patterns across codebase; mod = cyclic/periodic reasoning
    about behavior or structure that repeats with a defined period).
evidence: [task_T222]
```

---

## T223 — How service mesh routes traffic through shared infrastructure

**Task description:** "How does our service mesh work — how do services discover and communicate through the shared mesh infrastructure, and why does traffic route the way it does?"
**Target method:** `field`

**field:** "model interaction as occurring through a shared structured medium in which effects
arise from structural compatibility rather than direct reference between actors"

**Skill selection log:**
- Task: show or probe
- Method: **field** — "shared structured medium; effects from structural compatibility"
  - "shared mesh infrastructure" → shared structured medium (close match)
  - "why traffic routes" based on "structural compatibility" (mesh routing rules) → field
  - BUT: "field" is a physics metaphor; most engineers won't connect "service mesh" to "field"
  - Autopilot more likely picks: `mapping` (surface elements/relationships), `flow` (how
    traffic moves), or `struct` scope (arrangement of services)

**Bar command (likely):** `bar build show struct full mapping`
**Bar command (ideal):** `bar build show full field`

**Coverage scores:**
- Token fitness: 2 (mapping/flow cover service discovery but miss field's "effects from
  medium compatibility" frame — the why of routing)
- Token completeness: 3 (struct + mapping covers most of the structural need)
- Skill correctness: 1 (field is a physics metaphor entirely disconnected from service mesh
  vocabulary; no routing path whatsoever)
- Prompt clarity: 3 (mapping/flow produce useful output)
- **Overall: 1** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T223 — Service mesh routing through shared infrastructure
dimension: method
observation: >
  `field` method (interaction through shared structured medium; effects from
  structural compatibility) is effectively undiscoverable. It has the most opaque
  description of any method token — "shared structured medium" and "structural
  compatibility" are physics/field-theory terms that don't map to any common
  software engineering vocabulary. Users describing service mesh, protocol
  mediation, or shared-infrastructure interactions have no routing path to field.
  Even with a description match for "shared infrastructure", the abstraction is
  too distant. Low-frequency use case.
recommendation:
  action: add-use-when
  axis: method
  token: field
  proposed_use_when: >
    Shared-medium interaction analysis: user asks how actors interact through a
    shared infrastructure or protocol layer rather than via direct references.
    Heuristic: 'shared infrastructure', 'shared medium', 'protocol mediation',
    'service mesh routing', 'why things route through', 'broadcast/multicast
    patterns', 'effects propagate through a shared layer' → field. Distinct from
    mapping (mapping = surface elements; field = model the medium through which
    they interact and why compatibility produces observed routing).
evidence: [task_T223]
```

---

## T224 — API design from three perspectives simultaneously

**Task description:** "Analyze our new API design from three angles: the developer experience of using it, the operational burden of running it, and the security attack surface it creates."
**Target method:** `shift`

**shift:** "deliberately rotating through distinct perspectives or cognitive modes,
contrasting how each frame interprets the same facts"

**Skill selection log:**
- Task: probe
- Method: **shift** — "rotating through distinct perspectives or cognitive modes"
  - User explicitly says "from three angles" and lists three distinct perspectives
  - Description says "rotating through distinct perspectives" — strong match
  - "shift" as a word does suggest "shifting perspective" — partial self-naming
  - The explicit three-perspective structure in the user request strongly signals shift

**Bar command:** `bar build probe full shift`

**Coverage scores:**
- Token fitness: 5 (shift = multi-perspective rotation; user explicitly sets up three angles)
- Token completeness: 4 (shift method covers the core well)
- Skill correctness: 4 ("from three angles" + "three distinct perspectives" → shift;
  description match is strong; "shift" name partially self-describing)
- Prompt clarity: 4 (shift frames response as structured perspective rotation)
- **Overall: 4** ✅

**Gap diagnosis:** none — `shift` is discoverable when users explicitly invoke multiple
perspectives or angles. The token name ("shift perspective") is more intuitive than
boom/grove/melody/grow.

---

## Part B Summary

| Task | Token | Score | Gap? |
|------|-------|-------|------|
| T221 | meld | 2 | Yes — G-L14-01 |
| T222 | mod | 2 | Yes — G-L14-02 |
| T223 | field | 1 | Yes — G-L14-03 |
| T224 | shift | 4 | No |

**Mean (Part B):** 2.25/5 — well below target

**Gaps:** 3 of 4 tokens gapped (meld, mod, field). `shift` is the only remaining
metaphorical method token that is sufficiently self-describing to not need a use_when.

`field` (score 1) is the most opaque token in the entire catalog — physics-theory
language completely disconnected from software engineering vocabulary.

---

# Part C — Next Axis Recommendation

## Axis Coverage Summary (Post Loop-14)

| Axis | Covered | Total | Priority |
|------|---------|-------|----------|
| form | 9 | ~32 | — (loop-8 addressed specialist forms) |
| channel | 4 | 15 | — (loop-10 addressed undiscoverable channels) |
| scope | 6 | 13 | — (loop-12 addressed gapped tokens) |
| completeness | 3 | 7 | — (loop-11 addressed gapped tokens) |
| method | 12* | 51 | Sampled — metaphorical tokens addressed; many description-anchored remain |
| task | 0 | 11 | Low — all 11 task tokens have strong descriptions + notes |
| directional | 0 | 16 | Low — directionals are intentionally abstract; users rarely select directly |

*After applying loop-14 recommendations.

## Recommendation: General Health Check Loop

After 14 loops addressing specific axis gaps, the natural next step is a **cross-axis
general health check**: sample 10 diverse tasks that draw on the full token catalog,
evaluate end-to-end coverage (including recently fixed axes), and confirm that the
cumulative improvements hold together.

This tests whether:
1. Loop-1–14 fixes coexist without conflicts or regressions
2. Cross-axis combinations (scope + method + form + channel) work as expected
3. Any new gaps emerge from token interactions not visible in single-axis tests

Rationale for health check over more axis-specific work:
- Task axis (11 tokens) — all self-describing; low expected gain from evaluation
- Directional axis (16 tokens) — intentionally non-literal; autopilot rarely selects
  directionals based on user phrasing (they're sequencing modifiers, not content-selectors)
- Remaining method tokens — ~39 tokens without use_when, but the Tier 1 tokens (compare,
  diagnose, explore, branch, etc.) are description-anchored and expected to score ≥4
