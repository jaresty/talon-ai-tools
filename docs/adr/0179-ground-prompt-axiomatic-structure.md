# ADR-0179: Ground Prompt Axiomatic Structure — Generative Basis and Redundancy Taxonomy

**Status:** Informational
**Date:** 2026-03-24

---

## Context

The ground prompt (`groundPrompt.py`, `GROUND_PARTS_MINIMAL["core"]`) has grown through iterated failure-mode closure — each paragraph was added when a model was observed to exploit a gap not covered by existing text. The result is a ~3000-word prompt that is robust but opaque: the relationship between individual rules and any underlying principle is not stated.

This ADR records a structural analysis of that prompt using `bar build show collapse mint fly-rog`. The analysis addresses two questions:

1. Is there a more general formulation that achieves the same behavioral constraints?
2. What does the current structure reveal about the design tradeoff embedded in it?

---

## Finding 1: The Prompt Is Derivable From Four Axioms

Every rule in the current prompt is a surface instance of one of four generative axioms:

**A1 (Epistemic authority):** Only tool-executed events have evidential standing. Model recall, inference, and prediction have none, regardless of accuracy.

**A2 (Type discipline):** Each rung defines an artifact type. A tool-executed event satisfies a rung gate only if its output is of that rung's artifact type. Cross-type output — however correct — does not satisfy the gate.

**A3 (Cycle isolation):** Each descent through the ladder is a new evidential context. Artifacts from prior cycles have no standing in the current cycle. Carry-forward must be explicitly established within the current cycle.

**R2 (Minimal derivation):** Each artifact is the minimal transformation of the prior artifact that satisfies the current rung's type — form changes, intent does not.

### Derivation table

| Rule in current prompt | Derives from |
|---|---|
| Verbatim output, no elision inside triple-backtick block | A1: editorial alteration introduces model output into the evidential record |
| Prose descriptions do not satisfy exec_observed | A1 |
| Rung-type mismatch example (VRO output ≠ OBS satisfaction) | A2 |
| Criterion 'and' split rule | R2: a conjunction is not minimal |
| Behavioral-vs-structural criterion requirement | R2: a structural criterion is not of the behavioral artifact type |
| Carry-forward rows must cite current-cycle read results | A3 + A1: prior-cycle names have no standing; model recall cannot establish them |
| Per-cycle V-complete requirement | A3: prior-cycle artifacts have no standing |
| Prose re-emission at start of every cycle | A3: prior-cycle prose has no standing as a derivation basis |
| Sentinel-is-a-gate rule (outputting the label begins the rung) | A2: a sentinel names a rung type; emitting it outside the rung violates type |
| Sentinel-as-summary prohibition | A2 |
| OBR "direct demonstration" requirement | A2: test-runner output is not of the observed-running-behavior type |
| impl_gate does not complete the thread | A2: licensing an edit is not of the thread-complete artifact type |
| Provenance statement before OBR tool calls | A1 + A3: only a citable tool-executed event in the current cycle establishes provenance |

---

## Finding 2: Redundancy Is Structural, Not Accidental

The current prompt states the same underlying constraint in multiple surface forms across different rung contexts. This is not authorial redundancy — it is deliberate hardening.

### Five repeated constraint clusters

| Constraint | Surface instances |
|---|---|
| Tool output verbatim, complete | exec_observed definition; triple-backtick rule; elision prohibition; no-editorial-closing rule |
| Gates cannot be satisfied by inference | Attractor sentence; rung-type mismatch example; "prose descriptions do not satisfy" clause |
| One artifact per rung, minimal scope | "addresses only the gap"; "nothing beyond it"; criterion 'and' split; conjunction split; "not all known requirements" |
| Sentinel is a gate, not a label | "outputting a label begins the rung"; sentinel-outside-rung violation; sentinel-as-summary prohibition |
| Prior-cycle artifacts have no standing | Per-cycle V-complete; per-cycle impl-gate; carry-forward citable-read requirement |

Each cluster is one rule (derivable from A1–A3 + R2) stated at every rung where a model has been observed to violate it. The repetition is not compression failure — it is the record of where models actually escape.

---

## Finding 3: The Design Tradeoff

The prompt sits deliberately at the robust end of a generative-vs-hardened spectrum:

**Axiom-first formulation (~200 words):** State A1–A3 + R2, then derive rules on demand. Shorter and more principled. Fragile: relies on the model correctly deriving specific surface rules it has not been shown. A model that understands the axiom may still fail to apply it correctly in a novel context.

**Surface-instance enumeration (~3000 words, current):** State the axiom implicitly and enumerate every known attack surface explicitly. Longer and less elegant. Robust: each rule closes a specific escape route that has been observed to fire. A model that fails to derive a rule from the axiom is told the rule directly.

The prompt is long because it is a catalog of previously closed escape routes, not because the underlying principle is complex. Its structure is analogous to a test suite written to cover every bug ever found: not the specification, but the history of violations of the specification.

---

## Decision

This ADR is **informational** — it records the analysis without mandating changes to the current prompt.

The findings support three potential follow-on decisions, each of which would require its own ADR:

1. **Axiom header (non-breaking):** Prepend A1–A3 + R2 as a stated derivation basis before the current rule text. No rules removed. Adds derivability without reducing robustness. Low risk.

2. **Collapse to derivation categories (breaking):** Replace surface-instance enumeration with category-level rules (e.g., "no editorial alteration of tool output" instead of four specific elision prohibitions). Shorter. Requires validation that novel escape routes not covered by surface instances are blocked by the category rule alone.

3. **Axiom-first rewrite (high risk):** Replace the current prompt with a statement of A1–A3 + R2 plus category-level consequences. Would require extensive live-session validation before adoption.

---

## Methodology

Analysis used `bar build show collapse mint fly-rog` with the rendered prompt text as subject:

- **Collapse:** Identified five repeated constraint clusters and reduced them to single underlying rules
- **Mint:** Constructed A1–A3 + R2 as the explicit generative basis from which all rules follow as direct products
- **Fly-rog:** Oriented toward abstract structure and what the organization of the prompt reveals — the design tradeoff between derivability and robustness

The derivation table above is the canonical artifact of this analysis. Each row maps a surface rule to its generating axiom; a row that cannot be completed indicates a rule that is not derivable from the four axioms and may require a fifth.
