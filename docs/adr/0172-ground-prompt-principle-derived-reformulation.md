# 0172 – Ground Prompt Principle-Derived Reformulation

- Status: Proposed
- Date: 2026-03-21
- Context: The `ground` method prompt in `lib/groundPrompt.py` has grown to ~1850 words across four sections. Its rule-weight comes from enumerating every known violation pattern for a small set of underlying principles, rather than stating the principles explicitly and deriving the rules from them.

---

## Summary (for users)

- The ground prompt will be restructured around one explicit axiom (Rule 0) and four named primitives that generate all downstream rules.
- The epistemological protocol (domain-independent, stable) will be separated from the code-domain rung catalog (domain-specific) as a clean shear.
- Sentinel rules will become their own named section rather than being distributed across `derivation_structure` and `gate_validity`.
- The result is shorter, more derivation-based, and easier to maintain — load-bearing constraints are preserved, redundant restatements are eliminated.

---

## Context and Analysis

### Orbit analysis: the attractor geometry

The ground prompt, despite its volume, converges on one unspoken axiom:

> **The model's epistemic state is not evidence.**

Everything else — sentinel formats, carry-forward rules, pre-action checks, gate sequencing, the ban on retroactive labeling — is a specific enforcement mechanism for this single axiom. The prompt is long because it enumerates every form the violation can take rather than naming the axiom and deriving the rules from it.

Four attractors were identified across all sections:

1. **Conversation-event gate** — validity is grounded in conversation-state events, not model knowledge or reasoning.
2. **Anti-eagerness binding** — every gate is a delay mechanism; eagerness is the universal failure mode.
3. **Derivation chain integrity** — each rung must be traceable to I through an unbroken chain.
4. **Observation terminates** — descent ends only at tool output naming the declared behavioral gap.

### Reify/mint/shear analysis: the simpler formation

**Formal axiom set (generating set)**

Every rule in the protocol is a derived consequence of four axioms. Nothing in the document is a primitive beyond these four:

- **A1 (valid claim):** A claim about state S is valid iff there exists an event E in this conversation, produced by tool execution, that directly witnesses S.
- **A2 (chain derivation):** An artifact A_n is valid iff derived from A_{n-1} without adding unstated constraints, and A_{n-1} is valid.
- **A3 (gap license):** Forward motion from A_{n-1} to A_n is licensed iff the gap between A_{n-1} and I is witnessed by an event that names that gap specifically.
- **A4 (exact scope):** The scope of A_n is exactly the gap licensed by A_{n-1}'s observation event — neither I directly, nor any gap from a higher rung, may expand it.

| Rule | Derives from |
|---|---|
| Sentinels must precede tool | A1 |
| No retroactive sentinels | A1 (event must follow commitment) |
| Skipped rung voids artifacts below | A2 (chain validity is transitive) |
| Carry-forward required on test modification | A2 |
| Vacuous-green check | A3 (green without prior failure = gap not witnessed) |
| Gap-locality | A4 |
| Upward correction before rederivation | A2 (invalid ancestor invalidates all descendants) |

**Formal object model**

The protocol's type system has two non-comparable types: **captured events** and **composed content**. Accuracy is a property of composed content. Events do not have accuracy — they either exist at a position in the conversation or they do not. This is why "regardless of accuracy" appears repeatedly: accuracy is a property of the wrong type.

Named formal objects:

- **Event** `E`: Verbatim tool output with a conversation position. Not a summary, characterization, or anticipation.
- **Gate** `G`: Binary conversation-state condition (`open | closed`). Monotonic within a thread; non-transferable across threads.
- **Sentinel** `S`: Prospective commitment token. Valid iff `position(S) < position(E)`. A sentinel placed after E is inert — a different object from a valid sentinel, not a weaker one.
- **Rung** `R_n`: Positioned artifact. Valid iff upward-faithful (no added constraints vs. R_{n-1}) AND downward-sufficient (self-contained to evaluate R_{n+1}). These are independent failure modes.
- **Gap** `G_n`: Behavioral delta declared by R_{n-1}'s observation event. Declared, not inferred — must appear as a named entity in a captured event.
- **Thread** `T`: Directed sequence R_0...R_k. Complete iff ∃ observed running behavior event naming the declared behavioral gap.

**Rule 0 (epistemic grounding):** No claim about system state, test outcome, or artifact completeness is valid unless a tool-executed event in this conversation produced it. Model knowledge, anticipation, and reasoning cannot satisfy any gate.

**Four primitives generate the full rule set:**

- **Primitive 1 (event gate):** Sentinel declared before tool invocation; retroactive sentinels are inert.
- **Primitive 2 (derivation chain):** Artifact(n) derived from artifact(n-1); skipped rung voids all downstream artifacts.
- **Primitive 3 (observation terminates):** Thread ends at tool output naming declared gap; infrastructure events are not behavioral observations.
- **Primitive 4 (locality):** Each artifact addresses the gap declared by the prior rung's output only. Locality constrains downward motion — it bounds what a forward step may address. Upward correction governs the opposite direction and re-scopes all artifacts below the corrected rung; the two constraints do not conflict.

**The shear:** Two concerns are currently coupled:
- **Concern A — epistemological protocol:** What counts as valid evidence; how gates open. Domain-independent, stable.
- **Concern B — code-domain rung sequence:** The specific R4 rungs for code contexts. Domain-specific.

Separating these at a clean interface reduces the protocol section to ~200 words and makes the code-domain section independently maintainable.

---

## Decision

Restructure `GROUND_PARTS` in `lib/groundPrompt.py` from four keys to four keys with different boundaries:

| Current key | New key | Change |
|---|---|---|
| `derivation_structure` | `epistemological_protocol` | Replaced by Rule 0 + 4 primitives |
| `gate_validity` | `sentinel_rules` | Sentinel enforcement extracted as own section |
| *(distributed)* | `rung_sequence_code` | Code-domain rung catalog as standalone section |
| `reconciliation_and_completion` | `reconciliation_and_completion` | Unchanged |

### Proposed `GROUND_PARTS` structure

```python
GROUND_PARTS: dict[str, str] = {
    "epistemological_protocol": (
        "Rule 0 (epistemic grounding): no claim about system state, test outcome, or artifact "
        "completeness is valid unless a tool-executed event in this conversation produced it; "
        "model knowledge, anticipation, and reasoning cannot satisfy any gate regardless of accuracy. "
        "Four primitives govern every thread and derive all downstream rules: "
        "Primitive 1 (event gate): declare the sentinel before running the tool — "
        "a sentinel not immediately followed by verbatim tool output is inert and carries no gate function; "
        "retroactive sentinels do not open gates; the tool must be re-run with the sentinel appearing immediately before it. "
        "Primitive 2 (derivation chain): each artifact derives from the prior artifact — "
        "form changes, intent does not (R1); "
        "a skipped rung voids all artifacts below it; "
        "an artifact is a rung iff upward-faithful and downward-sufficient (R2); "
        "stopping mid-thread is only permitted when the next rung is not achievable. "
        "Primitive 3 (observation terminates): every thread ends at tool output naming the declared behavioral gap; "
        "infrastructure events — build success, server running, HTTP 200, URL response — "
        "are not behavioral observations regardless of label; "
        "the specific behavior named in the gap must appear as a verifiable event in the tool output. "
        "Primitive 4 (locality): each artifact addresses the gap declared by the prior rung's output and nothing more; "
        "implementing beyond the declared gap is a violation; "
        "modifying a behavioral assertion's predicate requires upward correction through criteria. "
        "Eagerness to implement is the primary failure mode — "
        "the shortest path to a valid artifact is strict primitive adherence; "
        "every skipped rung produces output that must be discarded and rederived."
    ),
    "sentinel_rules": (
        "Sentinels are the primary enforcement mechanism for Primitive 1. "
        "For executable rungs, emit "
        "\U0001F534 Execution observed: [verbatim tool output \u2014 triple-backtick delimited, complete, nothing omitted] "
        "then \U0001F534 Gap: [what the verbatim output reveals] "
        "on their own lines before any implementation artifact; "
        "a prose description of tool output is always composed content and never satisfies this sentinel. "
        "The \U0001F534 Execution observed sentinel body must be consistent with what the validation artifact as written could produce \u2014 "
        "output naming symbols not present in the validation artifact is fabricated. "
        "The \U0001F7E2 Implementation gate cleared sentinel must appear in this response before any tool call "
        "that creates or modifies an implementation source file; "
        "emit '\U0001F7E2 Implementation gate cleared \u2014 gap cited: [verbatim from \U0001F534 Execution observed]'. "
        "A \u2705 completion sentinel attests prior completion \u2014 it does not constitute it; "
        "a \u2705 token in manifest entries or planning text is inert and carries no phase-completion function. "
        "The validation run observation rung is only satisfied by an observed failure; "
        "a green run without a prior recorded failure for each test is a gap signal \u2014 "
        "either the behavior is already implemented (verify) or the validation artifact is vacuous. "
        "When the validation artifact is modified, emit a carry-forward statement before any implementation artifact: "
        "'Carry-forward: [which original failures cover which current tests]'; "
        "modification without carry-forward is a traversal violation."
    ),
    "rung_sequence_code": (
        "For code contexts, R4 instantiates as: "
        "prose (natural language description of intent and constraints) \u2192 "
        "criteria (acceptance conditions as plain statements) \u2192 "
        "formal notation (non-executable specification with behavioral invariants; must satisfy R2 \u2014 "
        "produce the R2 audit as a separate named section: one row per criterion, "
        "'\u20181. criterion \u2192 behavioral invariant\u2019 or '\u20181. criterion \u2192 UNENCODED\u2019'; "
        "emit '\u2705 Formal notation R2 audit complete \u2014 N/N criteria encoded' before advancing) \u2192 "
        "executable validation (a file artifact invocable by go test, pytest, or equivalent, "
        "targeting the declared gap; implementation code is not permitted at this rung) \u2192 "
        "validation run observation (only satisfied by an observed failure; "
        "emit '\u2705 Validation artifact V complete' after declaring the gap) \u2192 "
        "executable implementation (blocked until V-complete and \U0001F7E2 Implementation gate cleared "
        "have both appeared in this order) \u2192 "
        "observed running behavior (observation rung \u2014 no new files; "
        "invoke artifacts already produced and record their output; "
        "creating infrastructure to enable observation is production regardless of characterization). "
        "ground is a Process method \u2014 the manifest, rung sequence, and execution gates are mandatory "
        "regardless of task complexity or scope; "
        "there is no complexity threshold below which the ladder becomes optional. "
        "When I-formation is required: read-only exploration before the manifest; "
        "any file creation or modification before the manifest-complete sentinel is a boundary violation; "
        "emit '\u2705 I-formation complete' before the manifest."
    ),
    "reconciliation_and_completion": (
        "Every artifact documenting the governing intent of this invocation "
        "must be consistent with I before the invocation closes. "
        "The invocation close must include a reconciliation report: "
        "either 'all representations reconciled' or named failures with reasons. "
        "\u2705 Thread N complete may only appear after observed running behavior for that thread has been produced. "
        "\u2705 Manifest exhausted \u2014 N/N threads complete may only appear after all threads "
        "have emitted their completion sentinels and the reconciliation report has been produced; "
        "the N must equal the exact count of threads declared in the manifest."
    ),
}
```

---

## Consequences

**Positive:**
- Rule 0 is now a named, citable primitive — violation diagnosis becomes "which primitive does this break?" rather than "which enumerated rule applies?"
- Epistemological protocol is domain-independent and can be reused for non-code contexts by swapping `rung_sequence_code` for a different domain section.
- Sentinel rules as a standalone section makes the enforcement mechanism legible as a unit.
- Material reduction in word count (~40% estimate) without removing any load-bearing constraint.

**Risks / open questions:**
- The current prompt has been battle-tested; the reformulation has not. Behavioral equivalence should be validated against known failure modes (retroactive sentinels, vacuous-green, eagerness violations) before replacing.
- Some nuance in the current `gate_validity` section (e.g., the upward-correction observation record requirement, the I-formation permitted-criterion detail) may need to be reintegrated if omitted from the sketch above.
- Requires `make axis-regenerate-apply` after editing `groundPrompt.py` to propagate downstream.

**Structural shear planes (enforcement-model divergences):**
- **SP1 — Top-rung softness:** The axiomatic model (A2, A3) applies uniformly across all rungs, but the prose and criteria rungs have no mechanical gate — violations here surface only at validation run observation, not at the point of production. Mitigation: explicit self-check guidance at criteria rung (falsifiability requirement before advancing).
- **SP2 — Carry-forward as A1 exception:** Carry-forward is the one deliberate exception to A1 in the protocol — it is a composed claim, not a captured event, because no tool invocation can produce it. The strictness of its format requirement (explicit, named, traceable) derives directly from this exception status. This trade is necessary but should be made explicit in the prompt text so the model understands why the requirement is strict.
- **SP3 — Locality/upward-correction directionality:** A4 (locality) and upward correction appear to pull against each other but govern opposite directions of chain traversal. The protocol is consistent but the directional asymmetry is implicit; making it explicit ("locality constrains downward motion only") prevents misreading the two constraints as contradictory.
- **SP4 — Flat artifact section boundary:** The clean shear between epistemological protocol and code-domain rung catalog exists structurally in the `GROUND_PARTS` Python dict but is represented in the delivered artifact only by visual separators embedded in continuous prose. A model receiving the prompt cannot syntactically distinguish section boundaries. This is inherent to the medium; the mitigation is the source-level dict structure, which this ADR preserves.
- **SP5 — EI rung interior dead zone (addressed 2026-03-21):** Orbit analysis identified that the `executable implementation` rung had a single entry gate (quote 🔴 + emit 🟢) but no internal loop invariant. Once the gate opened, the rung interior was uncontrolled — a model could write a full implementation in one pass before re-running the validation artifact, and the vacuous-green check was discharged at rung entry rather than re-armed at each cycle iteration. Both behaviors are direct violations of Primitive 1 applied to mid-rung state transitions. Mitigation applied: the EI rung description in `rung_sequence_code` now states the rung proceeds as a minimal-step cycle (each edit bounded by the current observed failure; re-run required after each edit; single-pass is a traversal violation; vacuous-green check re-arms on every green result within the cycle). Three behavioral tests added to `_tests/test_ground_prompt.py` to enforce this at the text level.

---

## Prior art

- ADR-0171 (referenced in `groundPrompt.py` module docstring) — the four-part structured decomposition this ADR proposes to revise.
