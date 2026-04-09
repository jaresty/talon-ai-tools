# ADR-0227: ground/gate/atomic/chain Composition — COMPOSITION RULES Section and Token Cleanup

**Status:** Accepted
**Date:** 2026-04-09
**Related:** ADR-0220 (ground general process), ADR-0224 (ground decomposition into verify/chain/atomic)

---

## Context

The four method tokens `ground`, `gate`, `atomic`, and `chain` — used together as the craft
preset — produce an implicit composite protocol. Analysis of their co-presence revealed six
structural problems:

**Problem 1 — Distributed integration notes with no SSOT.**
Each token carries conditional text that only applies when other specific tokens are co-present:
- `ground`: "If a gate constraint is present… first step is verified assertion"
- `gate`: "When atomic is co-present: test absence blocks implementation"
- `chain`: "When gate is also present, the only valid predecessor artifact class is a failing test output"
- `atomic`: "If a ground constraint is present… exhausting failures is not termination"

These four notes form an implicit fifth protocol distributed across four locations. There is no
canonical statement of how the tokens compose; the composite behavior must be assembled by
reading all four tokens and reconciling their conditionals. Any update requires finding and
updating multiple locations.

**Problem 2 — Implicit dependency order.**
The compositional reading order `ground → gate → atomic → chain` is not declared anywhere. It
must be inferred. An LLM applying all four tokens has no structural guidance on which token's
rules govern when they conflict or intersect.

**Problem 3 — Ground's completion check trigger is stated only in atomic.**
`atomic` says: "when the artifact reports no failures, the next required step is ground's
completion check." `ground` does not name the condition under which its completion check fires.
A reader of `ground` alone cannot determine when the completion check is triggered relative to
a governing artifact cycle.

**Problem 4 — Ground's evidence quality claim is incomplete.**
`ground` says: "an assertion is not evidence." But it does not require that governing criteria
have been verified to fail before they govern. A criterion that has only ever passed provides
no coverage guarantee — this is `gate`'s primary claim — yet `ground`'s completion check
accepts any criterion as sufficient evidence. Ground's own evidence quality standard is weaker
than what the composite protocol requires.

**Problem 5 — Vocabulary mismatch for the same object.**
`chain` calls it "predecessor output" (and later "failure message"). `atomic` calls it
"failure message." When `gate` is co-present, these terms refer to the same object: the
governing artifact output that opens the current implementation step. The mismatch requires
mental unification by the LLM.

**Problem 6 — No grammar mechanism for pairwise composite behavior.**
Bar has no mechanism to inject prompt text that applies only when a specific combination of
tokens is co-present. Composite behavior must live inside individual token definitions (as
integration notes) or be left implicit.

**Important: interactions are pairwise, not all-four.**
Each integration note is conditional on exactly one other token, not on the full set of four:
- `ground` ↔ `gate` (2-token)
- `gate` ↔ `atomic` (2-token)
- `gate` ↔ `chain` (2-token)
- `atomic` ↔ `ground` (2-token)

The correct composition model is four separate 2-token compositions, each activating
independently whenever those two tokens are co-present — regardless of whether the other two
are present. A user running `ground + gate` without `atomic` and `chain` should still receive
the ground↔gate interaction rule.

### Why not absorb the composite into one token?

Absorbing properties (b) one-variable-per-step and (c) predecessor-reproduction into `ground`
was considered. Both are conceptually independent of ground's claim ("make the gap between
apparent and actual completion visible"). They address causal attribution and reasoning
continuity respectively — neither follows from optimizer framing. Absorbing them would make
ground semantically overloaded and would destroy the standalone value of `atomic` and `chain`
for non-craft use cases.

### Why not a fifth standalone method token?

A fifth method token consuming one of the three available method slots was considered. This
prevents users from adding additional method tokens alongside the composite. The COMPOSITION
RULES section approach injects outside the method axis and does not consume a slot.

---

## Decisions

### Decision 1 — COMPOSITION RULES section in rendered prompt output

The bar grammar engine gains a `compositions` configuration: a list of named compositions,
each specifying a token set (minimum 2 tokens) and a prose block. When all tokens in a
composition's set are co-present in a `bar build` command, the engine injects a
`=== COMPOSITION RULES ===` section into the rendered prompt output, placed after
`CONSTRAINTS` and before `PERSONA`. Multiple compositions may activate simultaneously; their
prose blocks are concatenated in definition order.

The section is structurally labeled and distinct from individual token CONSTRAINTS. It is the
canonical location for all pairwise composite behavior.

**Four pairwise compositions:**

**ground + gate**
Token set: `{ground, gate}`
```
ground + gate: the enforcement process derived by ground must include assertion-before-behavior
as its first step. No behavior may be produced before a governing assertion exists and has been
verified to fail when the behavior is absent. This is not an additional constraint on top of
ground's derivation — it is the required first rung of any enforcement process ground produces
when gate governs.
```

**gate + atomic**
Token set: `{gate, atomic}`
```
gate + atomic: the governing output is the artifact output (failure message, compile error,
test result) produced by the governing artifact that opens the current implementation step.
When no governing output exists for the current behavior, the scope of the current step is
undefined — the governing artifact has not been written yet. Test absence is an explicit open
gap that blocks implementation; the required action is to write and run the assertion, not to
proceed without one.
```

**gate + chain**
Token set: `{gate, chain}`
```
gate + chain: for implementation steps, the governing output is the only valid predecessor
artifact. A prior implementation artifact, compile result, or prose description does not
satisfy chain's reproduction requirement for an implementation step — only a reproduced
governing output does.
```

**atomic + ground**
Token set: `{atomic, ground}`
```
atomic + ground: exhausting the governing artifact's failures is necessary but not sufficient
for completion. When the artifact reports no failures, the required next step is ground's
completion check — return to the original stated intent and produce visible evidence for each
item. Declaring done before the completion check is a violation.
```

### Decision 2 — Remove distributed integration notes

Once the COMPOSITION RULES section is implemented and validated, the four integration notes
are removed from their respective token definitions:
- `ground`: remove the gate co-presence conditional (last sentence of current definition)
- `gate`: remove the atomic co-presence note ("When atomic is co-present…")
- `chain`: remove the gate co-presence predecessor constraint (last two sentences)
- `atomic`: remove the ground co-presence termination note (last sentence)

Each token definition then describes only its standalone behavior. Composite behavior is
fully owned by the COMPOSITION RULES section.

**Interim state**: until the grammar engine supports COMPOSITION RULES, the four integration
notes remain in the token definitions as the interim specification.

### Decision 3 — Tighten ground's completion check (prompt change)

**Current text (in `lib/groundPrompt.py`):**
> "…produce visible evidence that the behavior satisfies it — an assertion is not evidence."

**Revised text:**
> "…produce visible evidence that the behavior satisfies it — an assertion is not evidence,
> and a criterion that has only ever passed provides no coverage guarantee; only a criterion
> that has been verified to fail when the behavior is absent constitutes evidence."

This deepens ground's existing evidence quality claim. Ground's principle — "make the gap
between apparent and actual completion visible" — already implies that a criterion incapable
of detecting failure does not close that gap. This change makes that implication explicit.

### Decision 4 — Add termination handoff trigger to ground (prompt change)

**Current text:** ground's completion check description has no trigger condition.

**Add after the completion check description:**
> "When a governing artifact cycle is active, the completion check fires when the cycle
> reports no remaining failures — exhausting the artifact is necessary but not sufficient
> for completion."

This makes the trigger discoverable from `ground` itself, not only from `atomic`.

### Decision 5 — Canonicalize vocabulary: governing output (prompt changes)

**Definition:** the governing output is the artifact output (failure message, compile error,
test result) that opens the current implementation step.

**`atomic` changes (`lib/axisConfig.py`):**
- Replace "exact failure message" → "governing output" throughout
- Replace "failure message read literally" → "governing output read literally"
- Replace "one failure message" → "one governing output"
- Add definition on first use: "the governing output — the first reported failure from the
  governing artifact"

**`chain` changes (`lib/axisConfig.py`):**
- Replace "the failure message produced by the governing artifact is the predecessor artifact
  for the implementation step" → "the governing output is the predecessor artifact for the
  implementation step"
- Replace "only a reproduced failure message does" → "only a reproduced governing output does"
- Retain "predecessor output" for the general (non-gate) case — it is the correct term when
  gate is not present

### Decision 6 — Declare dependency order in COMPOSITION RULES

When all four tokens are co-present, the gate+atomic and atomic+ground compositions both
activate. The dependency order `ground → gate → atomic → chain` is declared in the
`atomic + ground` composition prose as context, not as a separate fifth composition:

Add to the **atomic + ground** composition prose:
```
When all four tokens ground/gate/atomic/chain are co-present, the dependency order is:
ground (frame and close) → gate (assertion coverage) → atomic (step scope) → chain (step
continuity). Each token's rules operate at a different level; they do not conflict.
```

---

## Prompt change summary

### `lib/groundPrompt.py` — GROUND_PARTS_MINIMAL["core"]

Three changes:

1. **Evidence quality** (Decision 3): after "an assertion is not evidence", add:
   ", and a criterion that has only ever passed provides no coverage guarantee; only a
   criterion that has been verified to fail when the behavior is absent constitutes evidence."

2. **Termination trigger** (Decision 4): after the completion check description, add:
   "When a governing artifact cycle is active, the completion check fires when the cycle
   reports no remaining failures — exhausting the artifact is necessary but not sufficient
   for completion."

3. **Remove gate co-presence note** (Decision 2, deferred): remove the final sentence
   "If a gate constraint is present in this prompt…" — deferred until COMPOSITION RULES
   infrastructure exists.

### `lib/axisConfig.py` — atomic

Four changes:

1. **Canonical term** (Decision 5): first use of "failure message" → "governing output (the
   first reported failure from the governing artifact)"
2. **Canonical term** (Decision 5): subsequent "failure message" → "governing output"
   throughout
3. **Remove ground co-presence note** (Decision 2, deferred): remove final sentence
   "If a ground constraint is present…" — deferred until COMPOSITION RULES infrastructure
   exists.

### `lib/axisConfig.py` — chain

Two changes:

1. **Canonical term** (Decision 5): "the failure message produced by the governing artifact
   is the predecessor artifact for the implementation step that follows it; reproduce it
   exactly before implementing" → "the governing output is the predecessor artifact for the
   implementation step that follows it; reproduce it exactly before implementing"
2. **Remove gate co-presence note** (Decision 2, deferred): remove the final two sentences
   "Predecessor type constraint for implementation steps: when gate is also present…" —
   deferred until COMPOSITION RULES infrastructure exists.

### `lib/axisConfig.py` — gate

One change (deferred):

1. **Remove atomic co-presence note** (Decision 2, deferred): remove "When atomic is
   co-present: if no failure message exists…" paragraph — deferred until COMPOSITION RULES
   infrastructure exists.

---

## Implementation

### Python (`lib/`)

**New file: `lib/compositionConfig.py`**
```python
COMPOSITIONS: list[dict] = [
    {
        "name": "ground+gate",
        "tokens": ["ground", "gate"],
        "prose": "...",  # Decision 1 ground+gate block
    },
    {
        "name": "gate+atomic",
        "tokens": ["gate", "atomic"],
        "prose": "...",  # Decision 1 gate+atomic block
    },
    {
        "name": "gate+chain",
        "tokens": ["gate", "chain"],
        "prose": "...",  # Decision 1 gate+chain block
    },
    {
        "name": "atomic+ground",
        "tokens": ["atomic", "ground"],
        "prose": "...",  # Decision 1 atomic+ground block (with dependency order note)
    },
]
```

**`lib/groundPrompt.py`**: apply Decisions 3 and 4 prompt changes.

**`lib/axisConfig.py`**: apply Decision 5 vocabulary changes to `atomic` and `chain`.

**`lib/promptGrammar.py`**: export `compositions` array to `prompt-grammar.json`.

### Go (`internal/barcli/`)

**`grammar.go`**:
- Add `Composition` struct: `{ Name string; Tokens []string; Prose string }`
- Add `Compositions []Composition` to `Grammar`
- `LoadGrammar`: populate from JSON

**`build.go`** (prompt renderer):
- After rendering `CONSTRAINTS`, iterate compositions
- For each composition whose token set is a subset of the active tokens, append its prose
  to a `COMPOSITION RULES` buffer
- If buffer non-empty, emit `=== COMPOSITION RULES ===` section

**`promptGrammar.py`** (grammar export): include `compositions` in JSON export.

### SPA (`web/`)

**`grammar.ts`**: add `Composition` type and `compositions: Composition[]` to `Grammar`.

**Prompt preview**: render `COMPOSITION RULES` section between CONSTRAINTS and PERSONA when
active tokens match one or more compositions. Section only appears when at least one
composition activates.

**`web/static/prompt-grammar.json`**: kept in sync via `make bar-grammar-update`.

### Validation

**`_tests/test_composition_config.py`** (new):
- Compositions list is non-empty
- Each composition has name, tokens (≥2 valid grammar tokens), prose (non-empty)
- The four named compositions exist: ground+gate, gate+atomic, gate+chain, atomic+ground
- All token references resolve to known method tokens

**`internal/barcli/composition_test.go`** (new):
- COMPOSITION RULES section appears when both tokens of a 2-token composition are present
- Section does not appear when only one token of a composition is present
- Multiple compositions activate and concatenate when all four tokens are present
- Section appears after CONSTRAINTS and before PERSONA
- Each of the four compositions activates independently

---

## Consequences

**Positive:**
- SSOT for each pairwise interaction: one location per composition, not distributed across
  two token definitions
- Individual token definitions become clean and standalone after Decision 2 is applied
- LLM receives composite rules in a labeled, structurally distinct section
- Pairwise model correctly handles partial combinations (e.g. `ground + gate` alone)
- Framework generalizes: other token pairs with interaction effects can be encoded as
  additional compositions without touching token definitions
- Ground's standalone evidence quality claim is tightened and self-consistent

**Negative / risks:**
- Grammar engine change required across three layers (Python, Go, SPA)
- Interim state (integration notes remain until infrastructure exists) creates a period of
  duplication between integration notes and compositions
- Token definitions without integration notes (after Decision 2) are weaker for standalone
  use — but the COMPOSITION RULES section covers co-presence cases correctly

**Mitigations:**
- Decision 2 (remove integration notes) is gated on Go/SPA implementation being complete
  and validated — interim duplication is explicit and bounded
- `bar help llm` should document that compositions activate automatically on token
  co-presence, so users know to expect the COMPOSITION RULES section

---

## Open questions

1. **`bar help llm` discoverability**: should compositions be listed as a first-class concept
   in `bar help llm`, so users know that specific token pairs activate additional behavior?

2. **Other compositions**: are there other token pairs with undocumented interaction effects
   that warrant compositions? Candidates to evaluate: `ground + formal` (formal verification
   framing), `sim + check` (simulate-then-review interaction).

3. **Ordering of composition prose blocks**: when multiple compositions activate
   simultaneously (e.g. all four tokens present activates all four compositions), should the
   prose blocks be ordered by dependency (ground+gate first, atomic+ground last) or by
   definition order in `compositionConfig.py`?
