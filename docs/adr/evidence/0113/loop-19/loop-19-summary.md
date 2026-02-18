# ADR-0113 Loop-19 Summary — Task Token Discoverability + Opaque Method Tokens

**Date:** 2026-02-17
**Status:** Complete
**Focus:** Task token discoverability (fix, sim, sort, check, pick) + opaque method tokens
           (abduce, analog, jobs, shift, spec)

---

## Results

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| L19-T01 | fix (reformat) | 4 | No |
| L19-T02 | sim | 3 | Yes — G-L19-01 |
| L19-T03 | sort + cluster | 5 | No |
| L19-T04 | check + fail | 5 | No |
| L19-T05 | abduce | 3 | Yes — G-L19-02 |
| L19-T06 | analog | 5 | No |
| L19-T07 | jobs | 3 | Yes — G-L19-03 |
| L19-T08 | shift | 4 | No |
| L19-T09 | plan + spec | 4 | No |
| L19-T10 | sort + prioritize | 5 | No |

**Mean: 4.1/5**

---

## Gaps Found and Fixed

| ID | Token | Axis | Root cause | Fix |
|----|-------|------|-----------|-----|
| G-L19-01 | sim | task | "what would happen if" does not map to sim; routes to probe | use_when in staticPromptConfig.py: 'what would happen if', 'play out the scenario where', 'simulate what happens when' |
| G-L19-02 | abduce | method | Academic term; "best explanation / ranked hypotheses" does not route to abduce | use_when in AXIS_KEY_TO_USE_WHEN: 'what's the best explanation for', 'generate hypotheses for why', 'ranked hypotheses from evidence' |
| G-L19-03 | jobs | method | JTBD terminology; "what is the user trying to accomplish" does not route to jobs | use_when in AXIS_KEY_TO_USE_WHEN: 'what is the user actually trying to accomplish', 'what job does this feature do', 'JTBD' |

## Post-Apply Validation

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| L19-T02 | sim | 3 | 4 | +1 | PASS — 'what would happen if' now anchored in catalog |
| L19-T05 | abduce | 3 | 4 | +1 | PASS — 'best explanation', 'ranked hypotheses' now anchored |
| L19-T07 | jobs | 3 | 4 | +1 | PASS — 'what is the user trying to accomplish' now anchored |

Grammar regenerated. All tests pass. SSOT intact.

---

## Tokens Confirmed Discoverable (no use_when needed)

| Token | Axis | Reason |
|-------|------|--------|
| fix | task | "change form/presentation" maps to user requests for reformatting (note: inverse routing risk documented in existing Notes) |
| sort | task | "arrange into categories / rank" maps directly |
| check | task | "does this meet requirements?" maps directly |
| cluster | method | "group by shared characteristics" maps to "categorize by theme" |
| analog | method | "use an analogy" maps explicitly |
| shift | method | "rotate through distinct perspectives" maps to "from the perspective of X, Y, Z" |
| spec | method | "define correctness criteria before implementation" maps to "define done before building" |
| prioritize | method | "rank by importance or impact" maps to "rank by strategic value" |

---

## Secondary Observation: `fix` Inverse Routing

The existing Notes for `fix` warn: "fix means reformat — not debug." This is present in the
catalog Notes column but passive. A user saying "fix this bug" or "fix this broken code" may
still select the `fix` task when they need `probe + diagnose`. The existing notes handle this
partially — no use_when needed now, but if reports emerge of `fix` being misused for debugging
tasks, the Notes entry should be strengthened with a disambiguation hint.

---

## Program-Level Task Axis Coverage (Post Loop-19)

| Axis | Tokens systematically tested | With routing guidance |
|------|-----------------------------|-----------------------|
| task | make, fix, pull, sort, diff, show, probe, pick, plan, sim, check (11/11) | sim (L19), fix (prior Notes), probe/pull/show (prior Notes) |

The task axis is now systematically covered. All 11 tokens have been tested against realistic
task scenarios. The only discovered gap was `sim` — now fixed.

---

## Key Finding: Method Axis Has Many Remaining Opaque Tokens

Post loop-19, the method axis has use_when for: boom, field, grove, grow, meld, melody, mod
(prior loops), plus abduce, jobs (this loop). Confirmed description-anchored: analog, shift,
spec, cluster, prioritize, diagnose, adversarial, explore. Still without use_when and potentially
undiscoverable: induce, converge, branch, simulation, spec (partially), operations, models.

**Recommendation for loop-20:** Continue method axis opaque token check —
induce, converge, branch, simulation, operations, models as next candidates.
