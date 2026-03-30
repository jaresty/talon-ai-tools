# ADR-0218: Ground Prompt — Collapsed Formulation via Orbit-Mint-Collapse

**Status**: Proposed
**Date**: 2026-03-30
**Updated**: 2026-03-30 (incorporates ADR-0227 through ADR-0237)

---

## Context

ADR-0217 introduced the generative ladder with 19 principles (P1-P19, later P20-P21) replacing the fixed rung enumeration. Subsequent ADRs (0219-0237) added specificity to close escape routes discovered in real sessions. The resulting groundPrompt.py has grown from ~8,500 to ~21,246 characters:

- **Duplicate void language**: Multiple principles describe what "voids" a rung
- **Scattered evidence concerns**: P14 (Evidential authority), P15 (Cycle identity), P16 (Provenance), P17 (Derivation chain) each address related but fragmented concerns
- **Verbose gate conditions**: Sentinel gates repeat similar patterns across 18 entries
- **Accumulated escape-route closures**: ADR-0227 through ADR-0237 added critical specificity that must be preserved in any collapse

This ADR proposes a collapsed formulation that reduces complexity while preserving the **invariant attractor** — including all escape-route closures landed since ADR-0219.

---

## Hypothesis

The ground protocol has an underlying **attractor geometry**: a minimal set of invariants that define the protocol's identity. Using `bar orbit` to find the invariant structure, `bar mint` to derive explicit generative assumptions, and `bar collapse` to reduce to canonical form should produce a shorter prompt that behaves identically to the original.

---

## Collapsed Formulation

The following principles replace the current P1-P21. P15 (Cycle identity) and P16 (Provenance) are merged into P14 (Evidential authority). P20 (Write authorization) and P21 (Upward return) are renumbered as P18 and P19.

### Core Invariants (Collapsed from P1-P21 + ADR-0227–0237)

1. **Intent primacy**: Intent exists; all artifacts derive from it. When intent changes, refine affected rungs top-down.
2. **Behavioral change isolation**: One rung per artifact type; changes only at dedicated rung.
3. **Observable evidence required**: Pre/post change states visible through actual tool output.
4. **Enforced and persistent**: Behavioral changes require verification automation.
5. **Automation quality verified**: Automation must fail before passing; the failure output is part of the verification artifact, not a separate rung.
6. **Artifact type discipline**: One rung per type; text rungs produce no files. An executable validation artifact is a file whose sole purpose is to assert behavioral properties of another artifact — it contains no behavior of its own; validation files may not be imported by implementation files. An executable implementation artifact is a file that produces behavior directly — it contains no assertions; implementation files may not contain assertions. A file that both asserts and implements voids the rung; classification is by content, not path.
7. **Upward faithfulness**: Lower rungs narrow what upper rungs permit.
8. **Rung validity test**: Human reviewer with only this rung's artifact can evaluate next rung; ladder is minimal — remove any rung that does not affect faithfulness evaluation.
9. **Information density preservation**: Each rung encodes same/higher quality than above.
10. **Three-part completeness**: Observation + automation + implementation.
11. **Immediate lowest-rung observation**: Observe at lowest feasible rung.
12. **Completeness slice**: One independently testable behavior per thread per cycle; criterion is a falsifiable behavioral assertion, not a feature name.
13. **Observation-first, observation-last**: Open and close with tool-executed observation of live running code. Observing running behavior means invoking the system directly in a manner that exercises the behavior named in the intent — the output must be produced by the behavior itself; reading files, grepping source, inspecting static artifacts, and running test suites do not satisfy this requirement. The gap between observed behavior and declared intent must be derived from the tool output, not assumed or inferred. ✅ Ground complete may only be emitted as the outcome of the observation loop — emitting it outside the loop is a protocol violation regardless of whether 🔵 Closing observation is present. 🔵 Closing observation must appear after ✅ Manifest exhausted and before ✅ Ground complete; its gate requires a tool call that directly invokes the behavior named in the session intent.
14. **Evidential authority**: Only tool-executed events have standing; evidence scoped to the cycle and gap in which it was produced; a prior cycle, different thread, or different gap does not satisfy any gate. The impl_gate requires at least one assertion-level failure string in verbatim exec_observed output — infrastructure failure, import error, process crash, or model-described summary does not satisfy this gate. For implementation code: before each file write, log the intention (target one specific assertion) and include the red observation showing that assertion currently fails; after the change, verify the target assertion is green and confirm no other assertions flipped unexpectedly — if more than that assertion flips from red to green, revert and try a different approach. Test code is not subject to this requirement.
15. **Derivation chain**: Artifacts derive from prior rung's actual content, not memory; scope does not expand between rungs.
16. **Continuous descent**: No pausing between rungs; response length is not a valid stop reason.
17. **Thread sequencing**: Manifest declares gaps; all rungs for Thread N before N+1. The ladder derivation (producing the rung table and manifest) occurs once when ground protocol begins — not per thread.
18. **Write authorization**: Every file write immediately preceded by 🔵 Write authorized citing open rung name, artifact type, and file path. The cited artifact type must match the artifact type of the named file as determined by the rung table — a type mismatch voids the write and the rung.
19. **Upward return**: Return to revise when derivation error discovered at or above the revised rung — lower-rung pressure is not a valid trigger; violation voids the revised rung and all below. Returning to the session observation loop is valid when a tool-executed observation reveals the declared gap is incorrect; the entire current ladder is void on such return; a new observation must precede any new gap declaration.

### Sentinel Block (Unchanged)

The sentinel formats and gates remain as-is to preserve protocol auditability. The collapse targets the principle text, not the operational sentinels.

---

## Verification

### Original vs Collapsed Metrics

| Metric | Current (P1-P21 + ADRs) | Collapsed | Reduction |
|--------|------------------------|-----------|-----------|
| Principles | 21 (P1-P19 + P20 + P21) | 19 | 9.5% |
| Core text characters | ~21,246 | ~TBD | ~TBD |
| Sentinel gates | 18 entries | 18 entries | 0% |

### Invariant Preservation Check

The collapsed version preserves all closures from ADR-0219 through ADR-0237:
- ✅ Intent-first ordering (P1, P13)
- ✅ Evidence gates require tool execution (P14)
- ✅ One artifact type per rung; validation/implementation mutually exclusive (P6)
- ✅ Thread/cycle/gap scoping (P12, P14, P17)
- ✅ Write authorization with type cross-check (P18)
- ✅ Rung validity test and minimality (P8)
- ✅ Manifest + observation loop structure with live-code requirement (P13)
- ✅ impl_gate assertion-level failure requirement (P14)
- ✅ Intention logging before implementation file writes; target one assertion; revert if more than target flips (P14)
- ✅ Closing observation sentinel and observation-loop termination authority (P13)
- ✅ Upward return with lower-rung-pressure prohibition and observation-loop return (P19)

### Behavioral Equivalence Test

Run equivalent sessions with both versions and verify:
1. Same sentinel sequence emitted
2. Same void violations triggered
3. Same rung table structure derived
4. Test runs, file reads, and static inspection rejected as observations
5. impl_gate blocked when exec_observed lacks assertion-level failure strings

---

## Implementation

If approved, the collapsed formulation replaces `lib/groundPrompt.py` and requires:
1. `make axis-regenerate-apply` to propagate to axisConfig.py
2. All existing ground tests pass against collapsed version
3. Char-count ceiling tests updated to reflect new size

---

## Alternatives Considered

1. **Keep original**: Accept redundancy for explicitness; rejected for maintenance burden
2. **Collapse further**: Merge more principles; risks losing externally verifiable formulations
3. **Automated collapse**: Use bar mint without orbit; rejected because attractor geometry must be preserved

---

## Risks

- **Over-collapse**: Removing too much redundancy may make principles ambiguous; every escape-route closure from ADR-0219–0237 must survive the collapse
- **Verification burden**: Must demonstrate behavioral equivalence including all recent additions
- **Migration cost**: Existing ground sessions may need adaptation

---

## Decision

**Proposed**: Adopt collapsed formulation (ADR-0218) pending behavioral equivalence verification against all existing ground tests.

---

## Meta-Loop Notes

This ADR demonstrates the meta-loop pattern:
1. **Intent**: Shorter ground prompt preserving all invariants including ADR-0219–0237 closures
2. **Manifest**: Collapse P1-P21 → P1-P19; preserve sentinels; incorporate all escape-route text
3. **Loop**: Verify equivalence → adjust → repeat until gap closed
4. **Termination**: When all 203 existing ground tests pass against collapsed version
