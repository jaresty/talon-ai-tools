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
