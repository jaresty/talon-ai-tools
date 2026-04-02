# ADR-0221: Canonical Essence Reduction for Ground Protocol

## Status

**Accepted**

## Context

The current ground protocol (`lib/groundPrompt.py`) contains 22 principles (P0–P22) and 40+ checklist items totaling ~200 lines of prompt text. While comprehensive, this verbose form presents several challenges:

1. **Token cost**: Every invocation incurs the full prompt cost, even when a compressed form would suffice
2. **Adherence friction**: The checklist density creates multiple potential failure points; missing any item triggers enforcement consequence
3. **Maintenance burden**: Changing a single principle requires navigating the full text to ensure consistency
4. **Canonical ambiguity**: The "essence" of the protocol is implicit rather than explicit—the core invariant is buried in 40 items

The canonical derivation (via `bar build sort split cluster mint`) identified:
- **5 foundational sentences** that capture the protocol's irreducible essence
- **4 structural principles** (Evidence, Gap, Derivation, Guard) that all P0–P22 derive from
- **2 hard gates** (Protocol derived, Ladder derived) that enforce the invariant

## Decision

Reduce the ground protocol to a **canonical essence** form that preserves the original's behavior: the model must derive the protocol from first principles, articulate consequences of failure ("what GOES WRONG"), and state enforcement rules for each item.

### Core Invariant

> Every assertion requires visible, externally validated proof. A model's description of completed work is indistinguishable from actually completing it—the protocol enforces the distinction by requiring a piece of reality before any claim about reality.

### Four Structural Principles (derive each: rule → consequence → enforcement)

1. **Evidence Primacy** — Trust comes from enforced evidence, not narrative claims. WHAT GOES WRONG: false completion. RULE: evidence before claims.
2. **One Gap At A Time** — Refinement addresses exactly one demonstrated failure. WHAT GOES WRONG: root causes obscured. RULE: one gap per refinement.
3. **Visible Derivation** — Every artifact cites its source; drift cannot hide. WHAT GOES WRONG: evidence of derivation lost. RULE: cite source before proceeding.
4. **Guard Integrity** — Evaluation mechanisms cannot change in same phase as artifacts. WHAT GOES WRONG: evaluation becomes circular. RULE: separate rungs.

### Meta-Loop Enforcement

> After every verification, re-run challenge; proceed only when zero-gap evidence appears. WHAT GOES WRONG: gaps remain undetected. RULE: loop until zero-gap.

### Hard Gates (must be emitted verbatim)

- 🔵 Protocol derived — emitted when protocol rules are derived
- 🔵 Ladder derived — emitted when ladder structure is derived for the domain
- No descent before both sentinels (hard gate blocks progress until both appear)

### Rung Structure (must be emitted at each rung)

- Emit rung label at BEGINNING: "=== Intent ===", "=== Criteria ===", etc.
- Emit completion sentinel at END: ✅ [Rung] complete

### Derivation Checklist (generative form — no P-number crutches)

Instead of enumerating items, the model derives the protocol from first principles and makes visible for each:

> **For each derived rule, state three things:**
> 1. **THE RULE** — what must be done
> 2. **WHAT GOES WRONG** — consequence of failure (making future costs paid now)
> 3. **THE ENFORCEMENT** — how the protocol catches/blocks violation
>
> The model must derive at minimum:
> - The invariant (claim vs reality) — what GOES WRONG if you claim without evidence: false completion; RULE: evidence before claims
> - Optimization pressure — what GOES WRONG if unaddressed: steps skipped, unverifiable results; RULE: make compliance easier than deviation
> - Ladder structure — what GOES WRONG if skipped: gaps disappear, completion becomes false; RULE: one rung at a time
> - Challenge mechanism — instantiate mechanism that detects gaps, APPLY it, SHOW failure; WHAT GOES WRONG if skipped: gaps remain undetected; RULE: mechanism must visibly fail
> - Single gap rule — one observed failure as active gap; WHAT GOES WRONG: multiple hidden fixes accumulate; RULE: one gap per refinement
> - Minimal refinement — smallest observable behavior that closes active gap; WHAT GOES WRONG: over-reaching weakens causal trust; RULE: minimal only
> - Meta-loop — after EVERY Verification, Challenge runs again; WHAT GOES WRONG: gaps undetected on subsequent rounds; RULE: loop until zero-gap
> - Zero-gap evidence — absence must be evidenced, not asserted; WHAT GOES WRONG: false confidence; RULE: evidence of no failure required
> - Full intent coverage — every criterion evaluated at least once; WHAT GOES WRONG: unevaluated criteria silently fail; RULE: all criteria must be evaluated
> - Gap authorization — no implementation until failing check exists; WHAT GOES WRONG: implementation inferred from intent; RULE: failing check precedes implementation
> - Enforcement validity — every guard must fail visibly before pass; WHAT GOES WRONG: unverified passes; RULE: fail-first then pass
> - Guard-implementation separation — guards and implementation change in separate rungs; WHAT GOES WRONG: causality obscured; RULE: separate rungs
> - Consequence materialization — every "what GOES WRONG" creates visible consequence; WHAT GOES WRONG: violations costless; RULE: immediate visible consequence
> - Preservation verification — pre/post characterization tests for behavior changes; WHAT GOES WRONG: changes unverified; RULE: green→change→green required
> - Hard gate — no rung until sentinels visible; WHAT GOES WRONG: protocol not derived; RULE: sentinels required before descent

⚠️ HARD GATE: Do not start the ladder until derivation is complete with consequences and enforcement rules visible for each rule.

### Domain Adaptation

- Writing: Intent → Criteria → Challenge → Minimal Artifact → Verification → Meta-loop
- Decision-making: Intent → Criteria → Analysis → Challenge → Minimal Artifact → Verification → Meta-loop
- The model must derive the appropriate ladder for the domain.

### Transition Checkpoint

BEFORE transitioning to next rung, verify and declare: [artifact completed?], [evidence visible?], [gaps remaining?], [intent aligned?], [guards unchanged?], [next rung requires?]. If any condition fails, do NOT proceed.

### Sentinel Derivation

The model derives sentinels from principles on each session. Template: declare intent → derive criteria → structure → challenge → refine → verify.

## Consequences

### Positive

- **Reduced token cost**: ~8x compression (200 lines → ~25 lines with derivation preserved)
- **Behavioral equivalence**: Derive → consequence → rule pattern preserved; model still derives protocol itself
- **Explicit derivation mechanism**: The technique is now visible, not buried in checklist format
- **Easier maintenance**: Core principles in one place, derivation rules reference them

### Trade-offs

- **Loss of exhaustive enumeration**: 40 items condensed to ~15 minimum derivation points
- **Model re-derives from principles**: This is intentional — the derivation process is the mechanism, not just the output
- **P-numbers eliminated**: The protocol is now derived from first principles, not enumerated from P0-P22

## Proposed Protocol Verbatim

```
This protocol exists because a model's description of completed work is
indistinguishable from actually completing it — every gate enforces the
distinction by requiring a piece of reality before any claim about reality.

The system assumes optimization pressure: the model will attempt the most
expedient path, including skipping steps. Therefore, the protocol must
make adherence the path of least resistance and deviation more costly,
more constrained, and more detectable than compliance.

CORE INVARIANT: Every assertion requires visible, externally validated proof.
WHAT GOES WRONG: false completion becomes indistinguishable from real.
RULE: evidence before claims.

FOUR STRUCTURAL PRINCIPLES (derive each: rule → consequence → enforcement):
1. Evidence Primacy — Trust comes from enforced evidence, not narrative claims.
   WHAT GOES WRONG: false completion. RULE: evidence before claims.
2. One Gap At A Time — Refinement addresses exactly one demonstrated failure.
   WHAT GOES WRONG: root causes obscured. RULE: one gap per refinement.
3. Visible Derivation — Every artifact cites its source; drift cannot hide.
   WHAT GOES WRONG: evidence of derivation lost. RULE: cite source before proceeding.
4. Guard Integrity — Evaluation mechanisms cannot change in same phase as artifacts.
   WHAT GOES WRONG: evaluation becomes circular. RULE: separate rungs.

META-LOOP: After every verification, re-run challenge; proceed only when
zero-gap evidence appears. WHAT GOES WRONG: gaps remain undetected. RULE: loop until zero-gap.

HARD GATES (must be emitted verbatim in chat):
- 🔵 Protocol derived — emitted when protocol rules are derived
- 🔵 Ladder derived — emitted when ladder structure is derived for the domain
- No descent before both sentinels (hard gate blocks progress until both appear)

RUNG STRUCTURE (must be emitted at each rung):
- Emit rung label at BEGINNING: "=== Intent ===", "=== Criteria ===", etc.
- Emit completion sentinel at END: ✅ [Rung] complete

DERIVATION CHECKLIST (generative form — derive protocol from first principles):

For each rule, state three things:
1. THE RULE — what must be done
2. WHAT GOES WRONG — consequence of failure (making future costs paid now)
3. THE ENFORCEMENT — how the protocol catches/blocks violation

The model must derive at minimum:
- The invariant (claim vs reality) — what GOES WRONG: false completion; RULE: evidence before claims
- Optimization pressure — what GOES WRONG: steps skipped, unverifiable results; RULE: make compliance easier than deviation
- Ladder structure — what GOES WRONG: gaps disappear, completion becomes false; RULE: one rung at a time
- Challenge mechanism — instantiate mechanism that detects gaps, APPLY it, SHOW failure; RULE: mechanism must visibly fail
- Single gap rule — one observed failure as active gap; RULE: one gap per refinement
- Minimal refinement — smallest observable behavior that closes active gap; RULE: minimal only
- Meta-loop — after EVERY Verification, Challenge runs again; RULE: loop until zero-gap
- Zero-gap evidence — absence must be evidenced; RULE: evidence of no failure required
- Full intent coverage — every criterion evaluated at least once; RULE: all criteria evaluated
- Gap authorization — no implementation until failing check exists; RULE: failing check precedes implementation
- Enforcement validity — every guard must fail visibly before pass; RULE: fail-first then pass
- Guard-implementation separation — guards and implementation change in separate rungs; RULE: separate rungs
- Consequence materialization — every "what GOES WRONG" creates visible consequence; RULE: immediate visible consequence
- Preservation verification — pre/post characterization tests; RULE: green→change→green required
- Hard gate — no rung until sentinels visible; RULE: sentinels required before descent

⚠️ HARD GATE: Do not start the ladder until derivation is complete with consequences
and enforcement rules visible for each rule.

TRANSITION CHECKPOINT: Before next rung, verify: [artifact completed?], [evidence visible?],
[gaps remaining?], [intent aligned?], [guards unchanged?], [next rung requires?].
If any fails, do NOT proceed.

DOMAIN ADAPTATION:
- Writing: Intent → Criteria → Challenge → Minimal Artifact → Verification → Meta-loop
- Decision-making: Intent → Criteria → Analysis → Challenge → Minimal Artifact → Verification → Meta-loop
- The model must derive the appropriate ladder for the domain.

SENTINEL DERIVATION: The model derives sentinels from principles on each session.
Template: declare intent → derive criteria → structure → challenge → refine → verify.
```

## Implementation Path

1. Create `lib/groundPromptCanonical.py` with the essence form above
2. Run A/B test: full prompt vs canonical form on equivalent tasks
3. Measure: token cost, adherence rate, task completion quality
4. If canonical performs equivalently, adopt as default; keep full form as reference

## References

- Original protocol: `lib/groundPrompt.py` (P0–P22, ~200 lines)
- Canonical derivation: `bar build sort split cluster mint deep --subject groundPrompt.py`
- ADR-0220: generalized ground protocol (original context)
