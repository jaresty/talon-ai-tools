# ADR-0085 Phase 2h — Composition Signal Detection Evidence

<!-- Template for each entry:
### <A> + <B> — COMPOSITION | ADDITIVE (<date>)
**Surfaced via:** <how the pair was identified>
**<A> alone:** <one-line constraint>
**<B> alone:** <one-line constraint>
**Emergent requirement:** <what A+B requires that neither alone imposes>
**Falsification case:** <one paragraph: response that satisfies A and B individually but violates A+B>
**Verdict:** composition | additive
-->

---

## Session 2026-04-09

**Seeds evaluated:** 1–10 with `bar shuffle --include method --fill 1.0`
**Pre-cycle candidates:** top 10 from `make composition-candidates`

---

### calc + chain — COMPOSITION (2026-04-09)

**Surfaced via:** seed 3 surfaced `chain`; matched to top candidate `calc+chain` from generator.

**calc alone:** Conclusions must be constrained by executable or quasi-executable step outputs — no requirement about reproducing predecessor text.

**chain alone:** Each step must reproduce its predecessor's actual output verbatim before proceeding — no requirement about executable steps or constrained conclusions.

**Emergent requirement:** Each calculation output must be quoted exactly (not paraphrased) before the reasoning that depends on it may proceed. calc requires conclusions be constrained by step outputs; chain requires exact predecessor reproduction; together they require the exact step output to appear in the response before the next step constrains its conclusions from it.

**Falsification case:** A response that lists three calculation steps (step 1: X = 3; step 2: Y = X + 2 = 5; step 3: Z = Y × 4 = 20) satisfies calc (conclusions constrained by formal steps) and satisfies chain individually (each step references the prior result). However, if step 3 writes "building on the previous result of 5" rather than quoting "step 2: Y = X + 2 = 5" verbatim, it violates calc+chain — the predecessor output was paraphrased, not reproduced, so the causal link between the calculation and the conclusion is unverifiable.

**Verdict:** composition

---

### calc + ladder — ADDITIVE (2026-04-09)

**Surfaced via:** top candidate from `make composition-candidates` (same category: Reasoning).

**calc alone:** Conclusions must be constrained by executable or quasi-executable step outputs — no requirement about abstraction level.

**ladder alone:** Move deliberately between abstraction levels ordered by importance — no requirement about step outputs or formal procedures.

**Emergent requirement:** None identified. The constraints operate on orthogonal dimensions — calc governs how conclusions relate to steps; ladder governs the ordering of abstraction levels. Neither imposes requirements on the other.

**Falsification case:** Attempted but not constructable. A response that runs formal calculations at the abstract level and at the concrete level satisfies both calc and ladder and cannot violate any combined constraint that neither alone imposes.

**Verdict:** additive

---

### flow + trace — ADDITIVE (2026-04-09)

**Surfaced via:** top candidate from `make composition-candidates` (same category: Temporal/Dynamic).

**flow alone:** Describes linear ordering of stages — no requirement about making data/control path explicit.

**trace alone:** Narrates sequential control/data progression from input to outcome — no requirement about stage structure.

**Emergent requirement:** None identified. Stage ordering (flow) and path narration (trace) compose additively — each constraint is satisfiable without reference to the other.

**Falsification case:** Not constructable. A response that lists stages and narrates the data path through them satisfies both independently; no combined violation is achievable that neither alone would catch.

**Verdict:** additive

---

### mint + root — COMPOSITION (2026-04-09)

**Surfaced via:** top candidate from `make composition-candidates` (same category: Structural).

**mint alone:** Generative assumptions must be made explicit; conclusions follow as direct products of the stated model — no requirement that the generative model itself have a single authoritative form.

**root alone:** Each proposition has a single authoritative locus; parallel accounts must be mapped or unified — no requirement about what generates the propositions.

**Emergent requirement:** The generative model mint constructs must itself be root-compliant — there may be only one canonical generative structure per domain. mint creates a structured derivation; root prohibits unresolved parallel accounts. Together: two independent generative models for the same phenomenon cannot coexist; the generative layer is not exempt from root's single-source requirement.

**Falsification case:** A response that presents two structural models for the same system (Model A: treat as a pipeline; Model B: treat as a state machine) and derives conclusions from each separately satisfies mint (each model has explicit generative assumptions with conclusions following from them) and satisfies root within each model (no internal duplication). However, it violates mint+root because the two models are parallel explanatory accounts of the same phenomenon without a specified dependency relationship or canonical unification — root's requirement applies to the generative layer, which mint+root makes explicit.

**Verdict:** composition
