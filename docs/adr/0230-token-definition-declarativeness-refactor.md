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

## Retest Results (2026-04-10)

7-agent stress test run against updated definitions. Same task types as ADR-0229.

### SSOT issue: ground binary was stale for first retest run

During the retest, `lib/groundPrompt.py` had not yet been updated — only `lib/axisConfig.py` had been edited, which the pre-commit hook (`make bar-grammar-update`) silently reverted by regenerating `axisConfig.py` from `groundPrompt.py`. All 7 agents received the old ground text ("name at least one cheap path"). The ground fix was committed separately (commit e4809b90) after the retest was already underway. **Probe question 4 (cheap-path removal) results are invalidated — a targeted ground-only retest is required.**

Gate and atomic changes were correctly committed (they live directly in `axisConfig.py`, not generated from a separate SSOT).

### Agent scores

| Agent | Task type | Self-score | Key finding |
|-------|-----------|-----------|-------------|
| Refactor | Rename function | 5/5 | Compiler-as-assertion; cited old cheap-path prescription (stale ground) |
| Delete | Remove function + call sites | 4/5 | Correctly planned; gap: behavioral isolation of new writeSectionWithContract behavior |
| Prose | Write CONTRIBUTING.md section | 5/5 | Floor assertions AND full manual verification protocol declared (who/procedure/pass-fail) |
| Performance | Buffer pool benchmark | 4/5 | Set explicit threshold prospectively before implementation; simulated (not executed) benchmarks |
| Multi-layer | token_version through 5 layers | 4.5/5 | Surfaced DAG, identified Layer 2 pressure point, noted epistemic independence |
| Prioritization | Non-code evaluation task | 5/5 | Derived visible rubric mechanism from principle without 🔴 format |
| Process design | Non-code design task | 5/5 | Gate assertions written before each component; completion check executed |

### Probe question findings

**1. Sentinel removal (gate rewrite)** ✅ VALIDATED

Agents derived equivalent visible-signal mechanisms from the principle without being told the 🔴 format. The prioritization agent produced rubric-output blocks before each evaluation; the process design agent produced assertion-before-step blocks. The principle ("assertion precedes behavior; assertion must be verified to fail before implementation") is format-agnostic — agents select appropriate visible signal forms for the domain.

**2. "No natural assertion" floor/ceiling principle (gate rewrite)** ✅ VALIDATED

Prose agent obtained both: (a) structural floor assertions (file exists, headings present, cited paths resolve), and (b) a fully declared manual verification protocol specifying who verifies, what they do, and a binary pass/fail condition. The new declarative principle produced complete behavior without the old "do not proceed" instruction.

**3. Atomic reproduction removal** ✅ VALIDATED

Chain owned the reproduction requirement cleanly. Atomic's sizing concern (causal isolation, one change per step) was distinct and unambiguous. No agents reported confusion between the two. The overlap noted in ADR-0230 gap analysis was real but resolved by moving the reproduction requirement to chain exclusively.

**4. Ground cheap-path removal** ❌ INVALIDATED (stale binary)

Agents did enumerate cheap paths, but the ground binary contained the old prescription ("name at least one cheap path"). Cannot determine whether this resulted from the new principle or the old prescription. **Targeted ground-only retest required** after confirming the new binary is in use.

**5. Composition prompt declarativeness** ✅ VALIDATED

Multi-layer agent found the composition prompt non-redundant: it provided parallel-branch DAG guidance and the impossibility/pressure distinction that individual tokens did not cover. The constraint framing ("gate's principle is a required constraint on whatever ground derives") was correctly interpreted — no agents confused it with a procedural ordering requirement.

### Additional findings

**Threshold provenance (performance):** The performance agent set the threshold prospectively — baseline measurement first, then `baseline × 0.75 = threshold` declared before implementation, then benchmark run. This is the correct pattern: threshold commits to a binary pass/fail before results are known, preventing post-hoc rationalization.

**Behavioral isolation gap (delete):** The delete agent (4/5) correctly planned the deletion but noted a gap: the behavioral side effect of `writeSectionWithContract` (new inline contract support) was not isolated in a separate assertion. The scope-creep decision-gate from ADR-0229 was applied nominally but not executed as a hard gate.

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

**Status:** Probes 1, 2, 3, 5 validated (2026-04-10). Probe 4 invalidated by stale binary — targeted ground-only retest pending.

---

## Open Items

- [x] Retest: run 7-agent stress test against updated definitions
- [ ] Ground-only retest: confirm cheap-path enumeration results from new principle (not old prescription) — binary must show "appearance-reality gap costly to maintain" in ground text
- [ ] Evaluate: does gate need an explicit call to produce visible failing output before implementation, or is this derivable from "verified to fail" + chain's reproduction requirement?
- [ ] Evaluate: chain's "predecessor" ambiguity — should "specific predecessor output" be made more precise for multi-step nested tasks?
- [ ] Evaluate: atomic's "any verification" ambiguity in multi-layer systems — should this be specified as "the verification layer this step operates in"?
