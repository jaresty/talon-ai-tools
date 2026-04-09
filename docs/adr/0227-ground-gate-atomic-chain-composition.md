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
`chain` calls it "predecessor output." `atomic` calls it "failure message." When both tokens
are co-present and `gate` governs, these terms refer to the same object: the output of the
governing artifact that opens the next implementation step. The mismatch requires mental
unification by the LLM.

**Problem 6 — No grammar mechanism for composite behavior.**
Bar has no mechanism to inject prompt text that applies only when a specific combination of
tokens is co-present. Composite behavior must live inside individual token definitions (as
integration notes), in a named preset (as additional text), or be left implicit. None of these
options produces a SSOT with clean individual token definitions.

### Why not absorb the composite into one token?

Absorbing properties (b) one-variable-per-step and (c) predecessor-reproduction into `ground`
was considered. Both are conceptually independent of ground's claim ("make the gap between
apparent and actual completion visible"). They address causal attribution and reasoning
continuity respectively — neither follows from optimizer framing. Absorbing them would make
ground semantically overloaded and would destroy the standalone value of `atomic` and `chain`
for non-craft use cases. The composite is the assembly of four tokens, not a property of any
one.

### Why not a fifth standalone method token?

A fifth method token consuming one of the three available method slots was considered. This
prevents users from adding additional method tokens alongside the composite (e.g.,
`ground gate atomic chain diagnose` would exceed the method cap). The COMPOSITION RULES
section approach (Variant G) injects outside the method axis and does not consume a slot.

---

## Decisions

### Decision 1 — COMPOSITION RULES section in rendered prompt output

The bar grammar engine gains a `compositions` configuration: a list of named compositions,
each specifying a token set and a prose block. When all tokens in a composition's set are
co-present in a `bar build` command, the engine injects a `=== COMPOSITION RULES ===` section
into the rendered prompt output, placed after `CONSTRAINTS` and before `PERSONA`.

The section is structurally labeled and distinct from individual token CONSTRAINTS. It is the
canonical location for all composite behavior.

**Canonical composition: craft**

Token set: `{ground, gate, atomic, chain}` (any axis, any position in command).

Prose block content:

```
These four tokens compose a single protocol — falsification-anchored incremental progress.
Apply them in the following dependency order: ground → gate → atomic → chain.

ground establishes the enforcement frame: derive the process, name cheap paths, identify
governing artifacts per layer. gate governs assertion coverage within that frame: every
behavior requires a governing output that currently fails before it governs. atomic governs
step scope within gate's cycle: one verification-layer change per step, scoped to the first
reported governing output. chain governs continuity within each step: reproduce the governing
output exactly before implementing — this is the step predecessor.

Governing output: the term for the artifact output (failure message, test result, compile
error) that opens the current implementation step. chain requires its reproduction; atomic
scopes the implementation to it; gate requires it to have existed and failed before the
behavior it covers was produced.

Termination: the governing artifact reporting no failures is necessary but not sufficient for
completion. When failures are exhausted, ground's completion check is the required next step:
return to the original stated intent and produce visible evidence for each item.

Dependency order rationale:
  ground  — frames the whole task; fires first (derive) and last (completion check)
  gate    — governs assertion coverage; extends ground's enforcement process
  atomic  — operationalizes gate's scope; one step per governing output
  chain   — enforces continuity within each atomic step
```

### Decision 2 — Remove distributed integration notes

Once the COMPOSITION RULES section is implemented and validated, the four integration notes
are removed from their respective token definitions:
- `ground`: remove the gate co-presence conditional
- `gate`: remove the atomic co-presence note
- `chain`: remove the gate co-presence predecessor constraint
- `atomic`: remove the ground co-presence termination note

Each token definition then describes only its standalone behavior. The composite is fully
owned by the COMPOSITION RULES section.

**Interim state**: until the grammar engine supports COMPOSITION RULES, the four integration
notes remain in the token definitions as the interim specification. The craft preset should
additionally carry the composite protocol text as a stopgap.

### Decision 3 — Tighten ground's completion check

Ground's "assertion is not evidence" clause is extended: a governing criterion must have been
verified to fail before it can count as evidence at the completion check. A criterion that has
only ever passed provides no coverage guarantee and does not satisfy ground's evidence
standard.

This is a deepening of ground's existing claim, not a change in nature. Ground's principle —
"the gap between apparent completion and actual completion must be made visible" — already
implies that a criterion incapable of detecting failure does not close that gap.

### Decision 4 — Add termination handoff trigger to ground

Ground's definition gains an explicit trigger condition for the completion check: "When a
governing artifact cycle is active, the completion check fires when the artifact reports no
failures — exhausting the artifact's failures is necessary but not sufficient for completion."

This mirrors the statement currently only in `atomic`, making the completion check's trigger
discoverable from `ground` itself.

### Decision 5 — Canonical term: governing output

"Predecessor output" (chain) and "failure message" (atomic) are unified under the term
**governing output**: the artifact output that opens the current implementation step.

- `chain` adopts "governing output" in place of "predecessor output" (for implementation steps
  when gate is co-present)
- `atomic` adopts "governing output" in place of "failure message"
- The COMPOSITION RULES section defines the term explicitly

Each token retains its own framing of *why* the governing output matters (chain: continuity;
atomic: scope), but uses the same term for the object.

### Decision 6 — Declare dependency order

The compositional reading order `ground → gate → atomic → chain` is declared explicitly in
the COMPOSITION RULES section with rationale (see Decision 1). It is not encoded in any
individual token definition.

---

## Implementation

### Python (grammar config — `lib/axisConfig.py` and new `lib/compositionConfig.py`)

A new `COMPOSITIONS` dict in `lib/compositionConfig.py`:

```python
COMPOSITIONS: dict[str, dict] = {
    "craft": {
        "tokens": {"ground", "gate", "atomic", "chain"},
        "description": "Falsification-anchored incremental progress.",
        "prose": "...",  # full block as specified in Decision 1
    }
}
```

`axisConfig.py` token definitions for `ground`, `gate`, `atomic`, `chain` are updated:
- Decision 3: tighten ground's evidence quality clause
- Decision 4: add termination handoff trigger to ground
- Decision 5: canonicalize "governing output" in chain and atomic
- Decision 2: remove integration notes (after Go implementation is complete)

### Go (grammar engine — `internal/barcli/`)

`grammar.go`:
- Add `Composition` struct: `{ Name, Tokens []string, Description, Prose string }`
- Add `Compositions []Composition` to `Grammar`
- `LoadGrammar`: populate `Compositions` from JSON

`build.go` (prompt renderer):
- After rendering `CONSTRAINTS`, check active tokens against each composition's token set
- If all tokens in a composition are present, inject `=== COMPOSITION RULES ===` section
  with the composition's prose

`promptGrammar.py` (grammar export):
- Export `compositions` array to `prompt-grammar.json`

### SPA (`web/`)

`grammar.ts`:
- Add `Composition` type and `compositions: Composition[]` field to `Grammar`

Prompt preview:
- Render `COMPOSITION RULES` section when active tokens match a composition's token set
- Section appears between CONSTRAINTS and PERSONA in the preview

`web/static/prompt-grammar.json`:
- Kept in sync with `build/prompt-grammar.json` via `make bar-grammar-update` (existing target)

### Validation

`_tests/test_composition_config.py`:
- Compositions are non-empty
- Each composition has tokens (≥2), description, prose
- All tokens in each composition reference valid grammar tokens
- craft composition contains exactly {ground, gate, atomic, chain}

`internal/barcli/composition_test.go`:
- COMPOSITION RULES section appears in output when all craft tokens are present
- Section does not appear when only a subset of craft tokens is present
- Section appears after CONSTRAINTS and before PERSONA

---

## Consequences

**Positive:**
- Single SSOT for composite behavior: one location to update, one location to read
- Individual token definitions become clean and standalone — readable without cross-referencing
- LLM receives composite rules in a labeled, structurally distinct section
- Dependency order is explicit; LLM does not need to infer it
- Vocabulary mismatch (predecessor output / failure message) eliminated
- Ground's evidence quality claim is consistent with the composite protocol's standard
- Framework generalizes: other token combinations with interaction effects can be encoded as
  additional compositions without touching individual token definitions

**Negative / risks:**
- Grammar engine change required across three layers (Python, Go, SPA) — non-trivial
- Interim state (integration notes remain + craft preset carries composite text) creates a
  period of duplication
- Token definitions without integration notes are weaker standalone — a user who applies
  `ground + gate` without the full craft set will not see the composite rules, and the
  integration notes that currently guide partial combinations will be gone after Decision 2
  is applied

**Mitigations:**
- Decision 2 (remove integration notes) is gated on Go implementation being complete and
  validated — interim duplication is explicit and bounded
- `bar help` and `bar help llm` should document the craft composition and when it activates
- For partial combinations (e.g. `ground + gate` without `atomic + chain`), consider a
  separate `partial-craft` composition or a note in each token's standalone definition that
  the full craft composition activates additional rules

---

## Open questions

1. **Partial combinations**: should `ground + gate` (without atomic + chain) have its own
   composition, or does each token's standalone definition cover that case adequately?

2. **Composition discoverability**: should `bar help tokens` or `bar help llm` list
   compositions as a first-class concept, so users know that assembling specific token sets
   activates additional behavior?

3. **Other compositions**: are there other token combinations in the current grammar that
   have undocumented interaction effects and would benefit from being encoded as compositions?
   Candidates: `sim + check` (simulate-and-review), `ground + formal` (formal verification
   framing).
