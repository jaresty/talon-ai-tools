# ADR-0198: Ground Prompt Minimum-Viable Refactor

**Status**: Proposed
**Date**: 2026-03-28

---

## Context

The current `groundPrompt.py` has accumulated ~90% corollary prose — restatements of rules that are directly derivable from two axioms: (1) only tool-executed events have evidential standing (proof-of-work chain), and (2) a rung's gate is satisfied only by output classified as that rung's artifact type, where type is determined by production method, not content. Every "no inference," "no prior-cycle output," "no cross-type output" sentence follows from axiom 1; every "test runner output is VRO-type," "file read is not OBR-type" sentence follows from axiom 2. The prompt grew rule-by-rule without the axioms ever being stated, so each derivable corollary was added defensively. The result is a prompt that is hard to reason about, brittle to extend, and risks over-specifying behavior a capable model should derive rather than pattern-match.

Why-sentences at type edge cases are not corollaries — they are defection-closing. A model that understands "test runner output is VRO-type" can still rationalize that comprehensive tests effectively demonstrate live behavior. The why-sentence closes that specific escape: *a passing test proves the harness's assertions pass, not that the behavior exists as a running system.* This cannot be derived from the axioms alone — it names a specific tempting substitution and explains why it doesn't count. Why-sentences belong in the refactored prompt; mechanical rule restatements do not.

---

## Decision

Refactor `GROUND_PARTS_MINIMAL["core"]` to state only what cannot be derived:

**Keep (non-derivable — must be stated):**
- The two axioms explicitly, as the generative root of all rules
- The rung table: 7 rung names, type labels, artifact definitions, gate conditions, void conditions
- The sentinel format strings (arbitrary conventions)
- Type edge-case classifications where production method is ambiguous: test runner output → VRO-type (not OBR-type); file reads → not OBR-type; **plus a why-sentence for each** — these close specific defection paths a model may rationalize even after understanding the axioms
- The OBR rung action sequence (criterion re-emission → provenance → live-process → exec_observed → test suite run) — a design decision among valid options
- Thread sequencing policy: complete all seven rungs for Thread N before any content for Thread N+1

**Remove (derivable from the two axioms):**
- All restatements that a model can produce by applying the axioms: "no inference," "no prior-cycle output," "no cross-rung output within same cycle," "skipped rung voids all below," "one edit per re-run," "sentinel is not a summary," etc.
- Redundant gate reminders restating what the rung table already encodes
- Criteria-rung specifics that restate falsifiability and conjunction rules derivable from "one behavioral criterion per thread per cycle"

The refactored prompt opens with the two axioms, then the rung table, then sentinel formats, then type edge cases with why-sentences, then the OBR sequence, then thread policy — and nothing else.

---

## Implementation

- `lib/groundPrompt.py`: rewrite `GROUND_PARTS_MINIMAL["core"]` — state axioms first, then rung table, then sentinel formats, then type edge cases, then OBR sequence, then thread policy; remove all derivable corollary prose
- Size-cap baselines in `_tests/ground/` will need updating
- Run full ground test suite to verify no behavioral regression

---

## Consequences

- **Positive**: Prompt is shorter, more readable, and easier to extend — new rungs or types require only a table row and edge-case classification, not a paragraph of corollaries
- **Positive**: A model that understands the axioms can reason about novel situations rather than pattern-matching rules; this generalizes the protocol beyond software to any domain where work must be distinguished from claims about work
- **Risk**: Models that need explicit corollary restatement to comply may regress; ADR-0113 loop testing should be run post-refactor to detect any routing or compliance failures introduced by removing the defensive prose
