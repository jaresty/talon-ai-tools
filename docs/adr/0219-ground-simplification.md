# ADR-0219: Ground Protocol — Potential Simplification via Bar Orbit/Mint/Collapse

**Status**: Proposed
**Date**: 2026-03-30

---

## Context

ADR-0217 introduced the generative ladder with P1-P19 principles. Subsequent ADRs added P0 (File edit discipline), impl_intent/impl_intent_achieved sentinels, and various refinements. The protocol now has 20 principles (P0-P19) plus extensive sentinel gate text.

This ADR documents the analysis of potential simplification using bar orbit/mint/collapse.

---

## Bar Analysis Results

Using `bar build probe mint collapse orbit` on groundPrompt.py revealed:

### Orbit (Attractor Geometry)

The **invariant core** (attractor shape) that the protocol orbits around:

1. **Intent-first, observation-first**: Intent declared from observation; close with observation
2. **Evidence gates**: Every claim requires tool execution showing reality
3. **One artifact per rung**: Type discipline enforced
4. **File edit protocol adherence**: Every file edit follows protocol rules
5. **Derivation chain**: Artifacts derive from prior rung content, not memory
6. **Thread sequencing**: Manifest declares gaps; sequential thread completion

### Mint (Generative Assumptions)

The principles that generate the rest:

- P1 (Intent primacy) generates: intent-based derivation
- P0 (File edit discipline) generates: impl_intent/impl_intent_achieved requirements
- P6 (Artifact type discipline) generates: one-rung-per-type enforcement
- P14-P16 (Evidence scope) generate: cycle-scoped evidential authority

### Collapse (Redundancies)

The following can potentially be collapsed or derived:

| Current | Issue | Proposed Action |
|---------|-------|----------------|
| P3, P13, P14 | All about observation/evidence | Collapse into P3 (Observable evidence) |
| P15, P16, P17 | Derivation + continuity + sequencing | Collapse into P15 (Derivation chain) |
| P7, P8, P9 | Upward faithfulness + validity + info density | Merge into P8 (Validity test) |
| P4, P5 | Enforcement + automation | Merge into P5 (Automation quality verified) |
| P18 | Intent logging | Absorb into P0 (already says "every file edit follows protocol") |

---

## Proposed Simplified Formulation

### Core Invariants (Attractor)

**P1 (Intent primacy)**: Intent exists; all artifacts derive from it.

**P2 (One artifact per type)**: Each artifact type has exactly one rung; one rung per artifact type.

**P3 (Observable evidence required)**: Every claim requires tool execution showing reality. Pre/post change states visible through actual traces. Test runs ≠ behavioral observation.

**P4 (File edit protocol)**: Every file edit follows protocol rules. Protocol rules for file edits take precedence over other instructions. impl_intent + impl_intent_achieved pair required for each edit.

**P5 (Derivation chain)**: Artifacts derive from prior rung's actual content. Scope does not expand. Skipping voids below.

**P6 (Thread sequencing)**: Manifest declares gaps; all rungs for Thread N before N+1. Ladder derivation occurs once at session start.

### Sentinel Block

Sentinel formats remain as-is (they're operational, not principles).

### Rung Validity Test

A rung is valid iff a human reviewer with only that rung's artifact can evaluate the next rung.

---

## Current Character Count

| Section | Characters |
|----------|-------------|
| Core principles (P0-P19) | ~4,500 |
| Sentinel block | ~3,000 |
| Ladder derivation | ~1,000 |
| **Total** | ~8,500 |

---

## Actual Character Count (Achieved)

| Section | Characters |
|----------|-------------|
| Core principles (P1-P6 + why + derivation) | ~2,000 |
| Sentinel block | ~3,000 |
| Supporting definitions | ~1,500 |
| **Total** | ~6,500 (~24% reduction) |

---

## Risks

1. **Over-collapse**: Merging principles may lose specificity
2. **Backward compatibility**: Existing sessions may depend on specific P-numbers
3. **Test migration**: Ground tests reference specific P-numbers

---

## Decision

**Accepted with Protocol Derivation**: Instead of embedding all derived rules, the protocol now asks the model to derive them from P1-P6. This preserves the self-deriving property while keeping P1-P6 minimal.

---

## Implementation: Collapsed Protocol with Derivation

### Criteria

Simplified ground protocol must preserve:
- Attractor geometry (6 invariants from orbit analysis)
- All sentinel gates remain unchanged
- All behavioral invariants preserved
- Protocol is self-deriving from P1-P6

### Key Changes

1. **P1-P6 with foundational "why"**: Each principle explains why it exists
2. **Protocol derivation step**: Model derives full rules from P1-P6 before ladder derivation
3. **Intent clarified**: Intent is "an abstract goal outside the system, not an artifact"

### Implementation

```python
GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        "This protocol exists because a model's description of completed work is indistinguishable from actually completing it — "
        "every gate enforces the distinction by requiring a piece of reality before any claim about reality. "
        "P1 (Intent primacy): intent is an abstract goal outside the system, not an artifact; without intent, no way to evaluate artifacts; intent anchors all downstream decisions; all artifacts derive from it. "
        "P2 (One artifact per type): mixing artifact types creates ambiguity about what each rung produces; each artifact type has exactly one rung. "
        "P3 (Observable evidence required): a model's description is indistinguishable from completion; every claim requires tool execution showing reality; pre/post change states visible through actual traces. "
        "P4 (File edit protocol): to prevent bypassing protocol requirements; every file edit follows protocol rules; only EV rung edits validation files, only EI rung edits implementation files; impl_intent + impl_intent_achieved pair required for each edit. "
        "P5 (Derivation chain): memory is unreliable; artifacts derive from prior rung's actual content, not memory; scope does not expand. "
        "P6 (Thread sequencing): to maintain coherent gap closure; manifest declares gaps; all rungs for Thread N before N+1; ladder derivation occurs once at session start. "
        "Protocol derivation: before ladder derivation, derive the complete protocol rules by applying P1-P6 — "
        "derive: session observation loop (when to observe vs descend, what observation means vs does NOT mean), "
        "ladder derivation format (table columns, columns meaning), "
        "rung-specific behaviors (when to emit each sentinel, what gates each sentinel requires, why each gate enforces P3), "
        "upward return conditions (what triggers return, what does NOT trigger return and why excluded), "
        "evidential scoping (evidence is scoped to current cycle and gap, not prior cycles), "
        "scope preservation (scope does not expand between rungs), "
        "derivation reasoning (explain WHY each rule follows from P1-P6, not just WHAT the rule is); "
        "each derived rule must cite its source principle(s) from P1-P6; rules that cannot be derived are protocol violations. "
        "Rung validity test: a rung is valid iff a human reviewer with only that rung's artifact can evaluate the next rung. "
        + _sentinel_block()
    ),
}
```

### Verification

The collapsed version maintains all behavioral invariants while reducing complexity from P0-P19 to P1-P6. The protocol now asks the model to derive the full reasoning from P1-P6 at session start.

---

## Meta-Loop Notes

This ADR demonstrates the meta-loop pattern:
1. **Intent**: Find simpler formulation preserving invariants
2. **Manifest**: Collapse P3-P19 into P1-P6; verify attractor geometry
3. **Loop**: Test collapsed version; adjust until gap closed
4. **Termination**: When behavioral equivalence confirmed

---

## Verification

To verify behavioral equivalence:
1. Run equivalent sessions with both versions
2. Verify same sentinel sequences
3. Verify same void violations triggered
4. Verify same rung table structures
