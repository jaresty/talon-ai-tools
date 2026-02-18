# ADR-0113 Loop-21 Evaluations

**Date:** 2026-02-18
**Binary:** /tmp/bar-new (built from source)
**Focus:** Directional token discoverability — all 16 directionals had empty use_when.
  Tested primitives: jog, dig, fog, rog, ong, bog, fig + compounds: fly-rog, fly-ong, dip-rog

---

## L21-T01 — Just pick a logging framework, no questions

**Task:** "Just tell me which logging framework to use for a Node.js microservice —
don't ask me clarifying questions, make a call"

**Expected tokens:** `pick gist jog`

**Skill selection:**
- Task: pick (select from alternatives)
- Completeness: gist (short answer)
- Directional: jog ("don't ask clarifying questions, make a call" → execute directly ✅)

**Discovery risk:** `jog` is the most practically useful directional — users frequently want
an immediate decision without back-and-forth. But without use_when, autopilot would omit the
directional entirely. "Don't ask me questions" / "make a call" don't route to any token in
the grammar without an explicit hint. The token name "jog" gives no information.

**Scores:** fitness 4, completeness 4, correctness 2, clarity 5 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token (G-L21-01: jog)

---

## L21-T02 — Concrete examples of eventual consistency failures

**Task:** "Be concrete — give me specific real examples of where eventual consistency
has caused data corruption in production systems, not abstract analysis"

**Expected tokens:** `probe fail full dig`

**Skill selection:**
- Task: probe (analyze failure modes)
- Scope: fail (failure modes/breakdowns)
- Completeness: full
- Directional: dig ("be concrete... specific real examples... not abstract analysis" ✅)

**Discovery risk:** "be concrete" / "specific examples" / "not abstract" → dig description
says "concrete details and grounding examples, focusing on specifics rather than abstractions."
Description is anchored to "concrete" and "specifics" vocabulary. But token name "dig" is
completely opaque. Without use_when, autopilot omits the directional axis entirely.

**Scores:** fitness 4, completeness 4, correctness 2, clarity 5 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token (G-L21-02: dig)

---

## L21-T03 — Step back to the abstract principle

**Task:** "I can see these three patterns in our codebase: everything uses polling, timeouts
are all magic numbers, and retries are inconsistent. Step back — what general principle
does this reveal?"

**Expected tokens:** `probe mean gist fog`

**Skill selection:**
- Task: probe
- Scope: mean (conceptual framing)
- Completeness: gist
- Directional: fog ("step back — what general principle does this reveal?" → surface abstract
  principles from specifics ✅)

**Discovery risk:** "step back," "general principle," "what does this reveal" → fog description:
"identify general patterns and abstract principles from the specifics, moving from particular
cases to broader insights." Partially anchored via "general principle" and "broader insights."
But "fog" sounds counterproductive (foggy?). Without use_when, directional axis is omitted.

**Scores:** fitness 4, completeness 4, correctness 2, clarity 5 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token (G-L21-03: fog)

---

## L21-T04 — Describe architecture structure then reflect on what it reveals

**Task:** "Describe how this event-driven architecture is structured, then tell me
what that structure reveals about the team's priorities and design philosophy"

**Expected tokens:** `show struct full rog`

**Skill selection:**
- Task: show (explain/describe for audience)
- Scope: struct (arrangement and relationships)
- Completeness: full
- Directional: rog ("structure... then what it reveals" → rog: examine structure, reflect ✅)

**Discovery risk:** User says "describe how it's structured, then tell me what that structure
reveals" — rog description: "examine the structure of the subject, then reflects on why that
structure exists and what it reveals." The vocabulary "structure... reveals" appears in both.
Partially description-anchored. But directionals are rarely selected by autopilot since the
axis isn't part of the standard selection flow.

**Scores:** fitness 4, completeness 4, correctness 3, clarity 5 → **Overall: 4** ⚠️

**Gap diagnosis:** partially discoverable — rog description mirrors user phrasing, but
directional axis is systematically under-selected. Scored as gap given the axis-level issue.

---

## L21-T05 — Actions with follow-on steps

**Task:** "What concrete actions should I take to reduce our p99 latency, and for each
action, what is the natural follow-on step?"

**Expected tokens:** `plan full ong`

**Skill selection:**
- Task: plan (propose steps)
- Completeness: full
- Directional: ong ("actions... for each action, what is the natural follow-on step" ✅)

**Discovery risk:** "actions... follow-on step" → ong: "identify concrete actions to take,
then extends those actions to related situations or next steps." "Follow-on step" maps to
"next steps." Partially anchored. But directional axis systematically under-selected.

**Scores:** fitness 4, completeness 4, correctness 3, clarity 5 → **Overall: 4** ⚠️

**Gap diagnosis:** partially discoverable — same directional axis issue as rog.

---

## L21-T06 — Structure, reflect, then act

**Task:** "Look at the structure of this microservices design, reflect on what it means
internally, then tell me what actions that reflection demands"

**Expected tokens:** `probe struct full bog`

**Skill selection:**
- Task: probe
- Scope: struct
- Completeness: full
- Directional: bog (three-phase: structure → reflect inward → actions ✅)

**Discovery risk:** bog is the hardest primitive to discover. Even knowing rog and ong, the
inward reflection + action sequence of bog is not obvious. The user says "structure... reflect
on what it means... what actions that demands" — which maps to bog's three-phase description,
but the description is dense. The bog vs rog distinction (inward reflection → acts vs outward
reflection, no action) is subtle. Completely undiscoverable without use_when.

**Scores:** fitness 4, completeness 3, correctness 2, clarity 4 → **Overall: 2** ⚠️

**Gap diagnosis:** undiscoverable-token (G-L21-06: bog)

---

## L21-T07 — Abstract first, then structural reflection

**Task:** "Start from the abstract architectural principle of bounded contexts, then examine
how it manifests structurally and what the structure reveals"

**Expected tokens:** `probe mean full fly-rog`

**Skill selection:**
- Task: probe
- Scope: mean
- Completeness: full
- Directional: fly-rog (abstract first → structural examination → reflection ✅)

**Discovery risk:** Compound token — requires knowing both fly (abstract first) and rog
(examine structure then reflect). Without knowing the primitives, completely undiscoverable.
Even with primitives known, compounds must be discovered via bar shuffle. User phrasing
"abstract principle... then manifests structurally... what the structure reveals" maps to
fly-rog but only if the user already knows the directional system.

**Scores:** fitness 4, completeness 3, correctness 2, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token (compound — lower priority than primitives)

---

## L21-T08 — Big picture first, then concrete action plan

**Task:** "Give me the big picture principle behind zero-downtime deployments, then turn
that into a concrete action plan with follow-on steps"

**Expected tokens:** `plan full fly-ong`

**Skill selection:**
- Task: plan
- Completeness: full
- Directional: fly-ong (abstract first → concrete actions → extensions ✅)

**Discovery risk:** Compound — fly (abstract first) + ong (actions and extensions). User
says "big picture first, then concrete action plan with follow-on steps" which maps well,
but only if the primitives are known. Without directional use_when, autopilot omits entirely.

**Scores:** fitness 4, completeness 3, correctness 2, clarity 5 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token (compound — lower priority than primitives)

---

## L21-T09 — Alternate between abstract and concrete

**Task:** "Explain idempotency — keep alternating between the abstract definition and
concrete examples from HTTP APIs, using each to sharpen the other"

**Expected tokens:** `show mean full fig`

**Skill selection:**
- Task: show
- Scope: mean (conceptual framing)
- Completeness: full
- Directional: fig ("alternating between abstract... and concrete examples, using each
  to sharpen the other" → fig: "alternate between abstract principles and concrete examples,
  using each to illuminate the other" ✅)

**Discovery notes:** User says "alternating between the abstract... and concrete examples,
using each to sharpen the other" — fig description: "alternate between abstract principles
and concrete examples, using each to illuminate the other (figure-ground reversal)."
The vocabulary is almost exactly mirrored. Description-anchored. Still needs use_when
because the directional axis is systematically under-selected.

**Scores:** fitness 5, completeness 4, correctness 3, clarity 5 → **Overall: 4** ✅

**Gap diagnosis:** partially discoverable — description mirrors phrasing closely. Fixed
via directional use_when to ensure axis is consulted.

---

## L21-T10 — Concrete examples first, then structural reflection

**Task:** "Start with concrete failure examples from our Kafka consumer lag incidents,
then step back to examine the structural pattern they reveal"

**Expected tokens:** `probe fail full dip-rog`

**Skill selection:**
- Task: probe
- Scope: fail
- Completeness: full
- Directional: dip-rog (concrete first → structural examination → reflection ✅)

**Discovery risk:** Compound token (dig + rog). User phrasing "concrete examples first,
then examine the structural pattern" maps to dip (concrete first) + rog (examine structure
then reflect). But compound tokens are only discoverable via bar shuffle. Without knowing
the primitives, impossible to select.

**Scores:** fitness 4, completeness 3, correctness 2, clarity 4 → **Overall: 3** ⚠️

**Gap diagnosis:** undiscoverable-token (compound — addressed indirectly by fixing dig
and rog primitives with use_when, enabling discovery of the compound)

---

## Summary

| Task | Key token | Score | Gap? |
|------|----------|-------|------|
| L21-T01 | jog | 3 | Yes — G-L21-01 |
| L21-T02 | dig | 3 | Yes — G-L21-02 |
| L21-T03 | fog | 3 | Yes — G-L21-03 |
| L21-T04 | rog | 4 | Yes (axis-level) |
| L21-T05 | ong | 4 | Yes (axis-level) |
| L21-T06 | bog | 2 | Yes — G-L21-06 |
| L21-T07 | fly-rog | 3 | Yes (compound) |
| L21-T08 | fly-ong | 3 | Yes (compound) |
| L21-T09 | fig | 4 | Partial (fixed via axis-level use_when) |
| L21-T10 | dip-rog | 3 | Yes (compound, addressed indirectly) |

**Mean: 3.2/5** — lowest since loops 12–14. Directional axis had zero use_when coverage.

**Root cause:** Directional tokens are never consulted by autopilot because the axis had no
`AXIS_KEY_TO_USE_WHEN` section at all. The fix adds the entire directional section.

**Applied fix:** Added `"directional"` key to `AXIS_KEY_TO_USE_WHEN` in `lib/axisConfig.py`
with use_when for: jog, dig, fog, rog, ong, bog, fig (all 6 primitives + fig).

**Compound tokens** (fly-rog, fly-ong, fip-rog, fip-ong, dip-rog, dip-bog, dip-ong, fly-bog,
fip-bog): addressed indirectly — compounds are discovered from bar shuffle + knowing the
primitives. Now that primitives have use_when, compounds become reachable via composition.
