# Cycle 24 — Phase 2e Distinction Check

## skim + orbit (c24-R2) — completeness floor vs method minimum

Not a redundancy pair (skim is completeness, orbit is method). The check here is not
"are they distinguishable" but "does the cautionary claim hold — can a skim light pass
structurally meet orbit's evidentiary minimum?"

**orbit's stated minimum (from its Description):** "Variation is sufficient only when it
includes at least one trajectory whose named initial conditions include at least one value or
parameter that does not appear in any other trajectory's named initial conditions." So orbit
requires ≥2 fully-specified trajectories with a distinguishing parameter, plus identification
of the invariant attractor across them.

**skim's stated ceiling:** "performs only a very light pass, addressing the most obvious or
critical issues without aiming for completeness."

**Judgment:** These are structurally incompatible in the same direction as the already-shipped
skim+rigor cautionary. A light pass that names and runs multiple fully-specified trajectories
and extracts their invariant is no longer a light pass — satisfying orbit violates skim, and
honoring skim starves orbit of its minimum evidence. The cautionary claim holds. This is a
**warning, not a definable composition**: there is no precedence rule that makes a light-pass
attractor analysis coherent (unlike paradox+fix, where a combined meaning existed). Confirmed:
`cautionary`.

## contextualise + sketch/svg (c24-R1) — no separate check needed

This is a mechanical extension of contextualise's existing gherkin/shellscript/codetour
cautionary entries (prose-form vs DSL-only channel). The mechanism is already validated by
those shipped entries; sketch (pure D2 source) and svg (markup only) are the same case. No
independent distinction check required — the family is established.

**Limitation:** single evaluator, seed-derived, compare prompts not executed by a fresh model.
Both recs EXTEND established cautionary families rather than asserting new mechanisms, which is
why confidence is high despite the single-seed evidence — the mechanism is already shipped and
tested; only the token membership is new.
