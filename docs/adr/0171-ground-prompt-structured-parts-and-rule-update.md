# ADR-0171: Ground Prompt — Structured Parts and Rule Update

**Status**: Proposed
**Date**: 2026-03-20

---

## Context

The `ground` method prompt in `lib/axisConfig.py` is stored as a single concatenated string of approximately 70 lines. Four distinct concerns are intermixed with no structural separation:

1. **Derivation structure** — what I, V, O mean; what makes a rung; rung completeness
2. **Gate validity** — what constitutes a valid gate; sentinel mechanics; observation requirements
3. **Derivation discipline** — gap-locality; minimal scope; upward revision
4. **Reconciliation and completion** — durable artifact reconciliation; thread and manifest close

The consequences of this structure are:
- Editing one concern requires reading the entire prompt to locate it
- Diffs conflate unrelated changes across concerns
- The prompt cannot be extended or reasoned about concern by concern

### Gaps identified via `snag` + `gap` analysis (2026-03-20)

A seam analysis against requirements derived from observed failure patterns surfaced five gaps in the current rule content:

| Gap | Current state | Required state |
|-----|--------------|----------------|
| Upward revision | Framed as error recovery only ("when a rung reveals the rung above needs correction") | Always permitted when a gap is observed vs. reality/code/stakeholder; requires signposting |
| Durable artifact reconciliation | Entirely absent | Every pre-existing artifact documenting the same intent must be reconciled before invocation close; failure reported as named process failure |
| Over-implementation | Not named as a failure mode | Implementing beyond the declared gap is a violation; minimal scope is the rule |
| Executable-vs-prose verification | Implicit (inferable from "inline labeled log entries") | Explicit: executable verification required only for executable artifacts |
| Rung achievability criteria | Implicit; stated only as escape hatch | Must be declared with explicit justification; convenience and anticipated outcome are not valid grounds |

---

## Decision

### 1. Refactor storage: structured parts with a serializer

Replace the monolithic string with a `GROUND_PARTS` dict of four named string parts in `lib/axisConfig.py`. A `build_ground_prompt()` function joins them in canonical order. The `"ground"` key in the method dict references the function call result.

```python
GROUND_PARTS = {
    "derivation_structure": "...",
    "gate_validity": "...",
    "derivation_discipline": "...",
    "reconciliation_and_completion": "...",
}

def build_ground_prompt() -> str:
    return " ".join([
        GROUND_PARTS["derivation_structure"],
        GROUND_PARTS["gate_validity"],
        GROUND_PARTS["derivation_discipline"],
        GROUND_PARTS["reconciliation_and_completion"],
    ])
```

The serializer is the single authoritative place where part ordering is enforced. Individual parts are the single authoritative place where each concern's rules live. Neither duplicates the other.

### 2. Update rule content to close identified gaps

The four parts below are the canonical rule content. They supersede the current monolithic string entirely.

---

#### Part: `derivation_structure`

> I is the declared intent governing the invocation. I precedes and is not itself an artifact. Every artifact derives from I through the prior rung — form changes, intent does not. V is a constraint artifact self-contained to evaluate the next artifact without consulting I. O is the output evaluated against V.
>
> A rung is complete when and only when its artifact has been produced — not when it has been listed, planned, or described. A rung is not achievable when the domain provides no standard artifact type for it; this must be stated explicitly with justification — convenience, anticipated outcome, or prior knowledge do not make a rung not achievable. Completeness governs the depth of each rung's artifact; it does not affect whether a rung must be produced. Executable verification is required only for executable artifacts; prose artifacts do not require execution to be complete. Formal notation must satisfy R2: every behavioral constraint from the criteria rung must be re-expressed in the notation — not just interface shape; type signatures or schemas that capture structure without encoding invariants do not satisfy this rung.

---

#### Part: `gate_validity`

> A gate is a conversation-state condition: open when and only when the required event has occurred in this conversation for this thread. Prior knowledge, anticipation, and model reasoning cannot satisfy any gate regardless of accuracy.
>
> For executable rungs, emit `🔴 Execution observed: [verbatim tool output — content composed without running the tool is invalid]` then `🔴 Gap: [what the verbatim output reveals]` on their own lines before any implementation artifact. Before producing implementation code, emit `🟢 Implementation gate cleared — gap cited: [verbatim from 🔴 Execution observed]`. The quote must be verbatim from the `🔴 Execution observed` sentinel of this thread; quoting anticipated output or a prior thread's observation is invalid.
>
> The `🔴` sentinel format is reserved exclusively for executable rung gates. For non-executable rungs, observation appears inline as labeled prose. No implementation artifact may appear before the `🔴` sentinels for the current thread.

---

#### Part: `derivation_discipline`

> Gap-locality: the gap gating rung N is the output of executing rung N-1. No gap from any higher rung, and no element of I directly, may serve as the gating gap for the current rung.
>
> Minimal scope: the current rung's artifact addresses the declared gap and nothing more. Implementing beyond the declared gap is a violation — not a benefit.
>
> Upward revision is always permitted when a gap is observed between prior understanding of I and something encountered via direct interaction with reality, code, or a stakeholder. Upward revision must be signposted with: what was observed, which rung is being revised, and why. It is never permitted to change I without first observing a gap in V that derived it. Changing I requires revising every artifact derived from it to restore chain consistency before descent continues.

---

#### Part: `reconciliation_and_completion`

> Intent precedes its representations. Every artifact that documents the governing intent of this invocation — whether produced in this invocation or pre-existing in the codebase — must be consistent with I before the invocation closes. If reconciliation is feasible, return up the chain to prose and rederive. If not feasible, report as a named process failure: which artifact diverges, what the divergence is, and why reconciliation could not occur. The invocation close must include a reconciliation report: either "all representations reconciled" or the list of named failures with reasons.
>
> `✅ Thread N complete` may only appear after observed running behavior for that thread has been produced and recorded. `✅ Manifest exhausted — N/N threads complete` may only appear after all threads have emitted their completion sentinels and the reconciliation report has been produced.

---

## Consequences

### Positive

- Each concern is independently readable and editable without touching adjacent parts
- Git diffs isolate changes to a single concern
- The serializer enforces part ordering as a single explicit dependency
- The rule content now covers all five identified gaps; failure modes (over-implementation, skipping reconciliation) are named rather than implied
- Adding a new concern in the future is a two-step operation: add a part to `GROUND_PARTS`, add the key to `build_ground_prompt()`

### Negative / watch points

- `build_ground_prompt()` must be called at module load time (or its result cached) — callers that reference the method dict should not need to change, but the value is now a function call result rather than a literal string
- The four-part boundary is a structural choice: if a future rule spans two concerns, the boundary may need revision
- The reconciliation requirement in Part 4 applies to this ADR itself: upon acceptance, the `ground` entry in `axisConfig.py` is the artifact that must be reconciled

## Implementation notes

The implementation is mechanical once this ADR is accepted:

1. Extract the four blocks from the current monolithic string
2. Replace each block with the updated rule content from this ADR
3. Add `GROUND_PARTS` dict and `build_ground_prompt()` to `lib/axisConfig.py`
4. Replace `"ground": "..."` in the method dict with `"ground": build_ground_prompt()`
5. Run the grammar export pipeline and verify the serialized prompt matches the concatenation of the four parts
6. Update `build/prompt-grammar.json` and `web/static/prompt-grammar.json`
