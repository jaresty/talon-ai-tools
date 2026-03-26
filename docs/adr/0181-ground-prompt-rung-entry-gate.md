# ADR-0181: Ground Prompt Rung-Entry Gate — Generative Subsumption of Late Attractors

**Status:** Accepted
**Date:** 2026-03-25

---

## Context

ADR-0179 established that every rule in `GROUND_PARTS_MINIMAL["core"]` is a surface instance of four axioms (A1–A3, R2). The prompt text encodes those axioms up front, then enumerates per-rung and per-violation rules throughout the body.

A structural analysis of the prompt's attractor topology — where the model can settle into a stable compliant or non-compliant state — identified eight late-appearing correction attractors: clauses that fire after the deviation window has already opened. Six of the eight are positionally late because they are stated in the rung description where the violation *occurs*, not at rung entry *before* any content is produced.

The six late attractors and their structural cause:

| # | Attractor | Positional problem |
|---|---|---|
| 1 | VRO-only stop (R2 block) | Fires at end of rung description; model may have already emitted wrong type |
| 4 | Thread serialization gate | Stated after thread-complete mechanics; retroactive if multi-thread output already produced |
| 5 | Conjunction-splitting rule | Mid-criteria; model reads it after generating a bad criterion |
| 6 | OBR test-runner prohibition | Late in OBR section; model reads it after emitting test-runner output |
| 7 | Final report transcript gate | End of prompt; fires only at report-writing phase |
| 8 | Reconciliation loop | After HARD STOP mechanics; model may skip it before the upward return label |

The shared root cause: all six are A2 or R2 enforcement consequences stated as per-violation patches rather than as a structural gate that fires before any rung content is produced.

---

## Decision

Add a **rung-entry gate** to `GROUND_PARTS_MINIMAL["core"]`, placed immediately after the A1–A3–R2 block and before any rung-specific text.

The gate fires before the first content token of any rung (not before the rung label — the label begins the rung, but content follows it). It requires the model to confirm four preconditions before proceeding:

1. **Rung name** — state the current rung by name from the seven-rung sequence
2. **Current gap** — state the currently-false behavioral assertion being addressed
3. **Required artifact type** — state the artifact type this rung produces, as defined in RUNG_SEQUENCE
4. **Exec-observed type check** — if a `🔴 Execution observed:` sentinel exists in the current cycle, confirm its output is of the required artifact type; if none exists yet, state that explicitly

If any of (1)–(4) cannot be stated from the current-cycle transcript, produce the missing element before proceeding.

### Wording to add to `GROUND_PARTS_MINIMAL["core"]`

Placed immediately after the R2 consequence block and before the per-rung enforcement text:

```
Rung-entry gate: before producing content at any rung, state (a) the rung name,
(b) the current gap as a currently-false behavioral assertion, (c) the artifact type
this rung requires, and (d) whether a 🔴 Execution observed: sentinel exists in
the current cycle and, if so, whether its output is of type (c) —
if no exec_observed exists yet in this cycle, state that explicitly rather than
treating prior-cycle output as satisfying this check;
if any of (a)–(d) cannot be stated from the current-cycle transcript,
produce it before any other content at this rung.
```

---

## Consequences

### What the gate subsumes

The rung-entry gate is a generative A2 enforcement point. A model that executes it correctly cannot produce any of the six violations, because the gate blocks content production until the type check passes:

- **Attractor 1 (VRO-only stop):** Part (c) at VRO = validation-run-observation-type output. Part (d) confirms the exec_observed in this cycle is of that type. Test-runner output fails (d) at gate entry — before the VRO content is written.
- **Attractor 4 (thread serialization):** Part (b) requires stating the single current gap. A model attempting to produce content for a second thread cannot state a singular current gap without contradiction — the gate surfaces the violation before the content appears.
- **Attractor 5 (conjunction-splitting):** At criteria rung entry, part (b) requires stating one currently-false behavioral assertion. A conjunction cannot be stated as a single currently-false assertion without splitting — the gate enforces singularity before the criterion text is produced.
- **Attractor 6 (OBR test-runner prohibition):** Part (c) at OBR = observed-running-behavior-type output (what a non-technical observer of the running system would see). Part (d) confirms the exec_observed is of that type. Test-runner output fails (d) — gate blocks OBR content.
- **Attractor 7 (final report transcript gate):** Part (b) at the final report phase requires stating the current gap from the transcript. Recalled content that was never produced cannot be cited from the transcript — the gate surfaces this before the report section is written.
- **Attractor 8 (reconciliation loop):** At upward-return rung entry, part (d) check includes confirming the exec_observed type from the current cycle exists — the reconciliation obligation fires as a precondition of gate passage, not as a late reminder.

### What the gate does not subsume

- **Attractor 2 (HARD STOP → criteria lock):** Already correctly positioned immediately after the HARD STOP definition. The gate does not replace it.
- **Attractor 3 (prose re-emission exclusion):** Already correctly positioned. The gate does not replace it.

The per-violation clauses for attractors 1, 4, 6, 7, 8 **are removed** from the prompt. The defense-in-depth argument for retaining them does not hold: both the gate and the late clauses are prompt text enforced by the same mechanism (linear reading). If the model bypasses the gate, it can equally bypass a late clause — the two pathways are not structurally independent. Retaining the late clauses adds token cost and creates two enforcement sites for the same rule, which introduces interpretation ambiguity without adding structural protection.

Attractor 5 (conjunction-splitting) is a partial exception. The gate subsumes its enforcement (singularity check at criteria rung entry), but the current text also contains definitional content the model needs to execute the gate correctly: the specification that a conjunction is identified by the word "and" and must be split before continuing. That definitional sentence is retained; the surrounding enforcement wrapper is removed.

### Perturb findings (pre-acceptance stress test)

Three perturbations were applied to the proposed gate wording before finalizing:

**P1 — First rung, no prior exec_observed:** At the prose rung in cycle 1, no `🔴 Execution observed:` exists yet. An early draft required "confirm exec_observed type" without a nil case. Fix: part (d) explicitly requires stating "no exec_observed exists yet in this cycle" rather than treating absence as a pass or scanning prior cycles.

**P2 — HARD STOP re-entry:** After a HARD STOP, the model re-enters the criteria rung mid-session. A prior cycle's `🔴 Execution observed:` exists in the transcript. An early draft scoped the check to "the transcript" rather than "the current cycle." Fix: part (d) explicitly scopes to the current cycle, preventing a prior-cycle exec_observed from satisfying the gate (A3 compliance).

**P3 — Gate scope ambiguity:** An early draft placed the gate "before emitting the first token." The rung label itself is the first token and begins the rung. Requiring the gate preamble before the rung label would mean the gate fires before the rung is open. Fix: scope is "before producing content at any rung" — the label opens the rung; the gate fires before content follows the label.

### Efficiency impact

The gate adds a short structured preamble before every rung's content. This increases token count slightly per rung. The tradeoff is accepted because:

1. The preamble is the minimum information the model needs to correctly type-check its own output — it is not overhead, it is the A2 check made explicit and early.
2. Removing the late attractor clauses (attractors 1, 4, 6, 7, 8) recovers approximately 150–200 words from the prompt body. Net token change is negative: the gate adds ~60 words; the removals save ~180 words.

---

## Related ADRs

- ADR-0179: established the four-axiom generative basis this gate instantiates
- ADR-0178: prior drift-closure pass that added several of the late attractors now being subsumed
- ADR-0177: ground prompt collapse and behavioral rules
