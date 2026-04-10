# ADR-0230 — Token Definition Declarativeness Refactor

**Date:** 2026-04-10
**Status:** Active — retest required

---

## Context

Following ADR-0229 (stress test), the ground+gate+chain+atomic protocol was retested across 7 agents and scored 4–5/5. Three secondary gaps emerged. A `check-and-rewrite` bar-workflow (`orbit gap drift split` → `collapse root mint`) was applied to the four token definitions to evaluate factoring and declarativeness.

The core finding: **prescriptive procedure is worse than principle.** A definition that encodes *how* to satisfy a principle is fragile — it accumulates corollaries that become domain-specific, miscounted, and harder for agents to internalize. A definition that states *what* the principle requires allows agents to derive appropriate process for each domain.

---

## Findings from the bar-workflow Analysis

### orbit: attractor structure

Varying task context (code TDD, prose, process design, multi-layer, organizational) and finding invariants:

- **ground**: attractor = optimizer assumption + mandatory completion check. Stable.
- **gate**: attractor = unverified assertion provides no coverage. Stable. But gate's prompt text had accumulated domain-specific accretion (sentinel format, layer boundary rules, governing tool corollary) that varies by trajectory — not part of the attractor.
- **chain**: attractor = anchor to actual predecessor output, not interpretation. Stable.
- **atomic**: attractor = observable causal isolation, one change per step. Stable.

### gap: implicit/explicit mismatches

1. **gate miscounted requirements**: gate said "Three requirements follow from this principle" but had four enumerated requirements — the fourth (type-matching) was added via ADR-0229 remediation without updating the count.
2. **gate embedded prescriptive procedure**: the 🔴 sentinel format, the layer boundary requirement, the governing tool corollary — all derivable from the core principle, not invariant across domains.
3. **"no natural assertion" handler underspecified**: gate said "state that explicitly and do not proceed" but didn't say what to do instead; the floor/ceiling structure was in ADR-0229 findings, not in gate's definition.
4. **reproduction requirement overlap**: atomic's per-step reproduction gate ("before any implementation, reproduce the exact governing output") overlaps with chain's reproduction requirement. Both stated it with slightly different scope.
5. **ground's cheap-path prescription**: "A valid derivation must name at least one cheap path" prescribes the form of ground's derivation, not just the principle it must satisfy.

### drift: underenforced conclusions

1. **gate vs. ground relationship unstable**: gate's text was fully self-contained, reading as a complete enforcement protocol — making its relationship to ground's derivation ambiguous when both are co-present.
2. **"predecessor" in chain underspecified**: "the specific predecessor output" could mean immediately prior step or the specific output this step builds on — these can differ in nested multi-step tasks.
3. **atomic's "step" definition ambiguous**: "any verification" is ambiguous in multi-layer systems — different verification layers may not agree on step boundaries.
4. **gate's governing-tool escape hatch applied liberally**: the test for "structurally enforced" (no behavioral difference possible) is difficult for agents to evaluate precisely; they may apply it liberally to avoid writing assertions.

### split: factoring verdict

| Token | Level | Core principle | Factoring |
|-------|-------|---------------|-----------|
| ground | Task (meta) | Appearance ≠ reality; completion check mandatory | ✅ single concern |
| gate | Step (precondition) | Unverified assertion = no coverage | ⚠️ accumulated procedure |
| chain | Step (continuity) | Anchor to actual predecessor output | ✅ single concern |
| atomic | Step (sizing) | Causal isolation; one change per step | ✅ single concern |

**Verdict:** The four tokens are genuinely orthogonal. They should not be merged or split. Only gate needs significant revision; ground and atomic need minor trims.

---

## Changes Applied

### gate (full rewrite)

**Before:** Enumerated numbered list (Three/Four requirements), 🔴 sentinel format, layer boundary requirement, governing tool corollary, "do not proceed" handler for "no natural assertion" with no guidance on what to do instead.

**After:** Core principle stated first. Three named conditions derived from it (assertion precedes behavior; one assertion per behavior; assertion type must match behavior type). Each condition is the minimum that cannot be derived without further specification. The governing tool corollary is collapsed into the type-matching condition (derivable from "type must match"). The "no natural assertion" case is given a floor/ceiling principle: structural floor assertions are required but insufficient; a manual verification protocol must be declared.

**Removed:** Sentinel format (🔴) — prescriptive procedure; agents derive how to make failing output visible. Layer boundary requirement — derivable from "one assertion per behavior" applied to multi-layer contexts. Numbered list structure — principle generates conditions without counting them. "Verified before first use" as a separate numbered requirement — collapsed into "assertion precedes behavior" (observing it fail is the verification).

### atomic (targeted trim)

**Removed:**
- "the per-step gate enforces it: before any implementation, reproduce the exact governing output" — reproduction requirement belongs to chain; atomic's concern is step sizing, not continuity
- "When deriving this token, establish the cycle protocol explicitly: what the governing artifact is, how failures will be observed, how scope will be determined. A derivation that omits this is incomplete." — prescribes the form of derivation rather than the principle; agents derive the cycle structure from "observable causal isolation requires establishing what will be observed"

### ground (targeted trim)

**Removed:** "A valid derivation must name at least one cheap path that would produce the appearance of completion without satisfying the intent, and for each, specify what visible evidence would distinguish genuine compliance from that path." — prescribes the form of the enforcement derivation rather than the principle; the optimizer assumption already implies the agent reasons about how their process closes the appearance-reality gap.

**Changed:** "derive an enforcement process from the intent of this task" → "derive an enforcement process from the intent of this task whose constraints make the appearance-reality gap costly to maintain" — states the principle the enforcement process must satisfy rather than leaving "from the intent" vague.

### Composition prompts (declarativeness pass)

**ground+gate:** Changed from "must include assertion-before-behavior as its first step" (prescribes ordering of ground's derivation) to: gate's principle is a required constraint on whatever ground derives — any enforcement process that permits behavior without a verified assertion violates gate.

**atomic+ground:** Removed the procedural dependency order (`ground → gate → atomic → chain`). Replaced with a level-of-abstraction description: each token governs a different level (task process / step precondition / step scope / step continuity); violations at one level are independent of the others.

**ground+gate+atomic+chain:** Removed "fix:" labels (prescriptive). Retained the impossibility vs. pressure distinction as a declarative observation: they are distinct failure modes with different causes and are not resolved by the same intervention.

### Test updates

Two tests in `composition_test.go` locked in the previous definition structure and were updated:
- `TestGateDefinition_NoGroundVocabulary`: changed assertion from checking for "structural scope violation" to checking for "independently-failing" (same intent: gate uses assertion-appropriate vocabulary for coverage violations)
- `TestGateDefinition_FourthRequirement` → `TestGateDefinition_TypeMatchingRequirement`: changed from checking for "Fourth, assertion type must match behavior type" / "executable and automated" to checking for "Assertion type must match behavior type" / "static check cannot govern executable behavior"

---

## Retest Required

The definition changes are significant enough to warrant a new stress test. Key questions for the retest:

1. **gate rewrite — "no natural assertion" floor principle**: does the declarative floor/ceiling principle produce the correct behavior (structural floor + manual verification protocol declared) without the explicit "do not proceed" instruction?
2. **gate rewrite — sentinel removal**: does removing the 🔴 sentinel format cause agents to skip making failing output visible, or do they derive an equivalent mechanism from the principle?
3. **atomic reproduction removal**: when using atomic without chain, do agents still anchor to the governing output before implementing — or does removing the reproduction gate cause drift?
4. **ground cheap-path removal**: does removing the prescribed derivation form cause ground to produce weaker enforcement processes, or do agents derive equivalent structure from the principle?
5. **composition prompt declarativeness**: does the new ground+gate composition (constraint framing vs. first-step framing) produce equivalent behavior?

### Suggested retest task coverage

Same 7 tasks from ADR-0229 retest, same scoring rubric. Focus questions on:
- Can the agent reconstruct the sentinel behavior from first principles without being told?
- Can the agent reconstruct the cheap-path analysis from first principles without being told?
- Does the "no natural assertion" floor/ceiling principle produce complete behavior?
- Does the atomic definition (without reproduction gate) still produce anchored step execution when chain is absent?

---

## Open Items

- [ ] Retest: run 7-agent stress test against updated definitions
- [ ] Evaluate: does gate need an explicit call to produce visible failing output before implementation, or is this derivable from "verified to fail" + chain's reproduction requirement?
- [ ] Evaluate: chain's "predecessor" ambiguity — should "specific predecessor output" be made more precise for multi-step nested tasks?
- [ ] Evaluate: atomic's "any verification" ambiguity in multi-layer systems — should this be specified as "the verification layer this step operates in"?
