# ADR-0189: Orbit Closures — Type Taxonomy and Predicate Definition

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

ADR-0188's orbit analysis identified three structural attractors not addressed by the axiom
additions. Two were tractable protocol changes; one is a known structural limitation.

### Attractor B — Sentinel hollow compliance (type taxonomy gap)

A4 (Provenance) requires artifacts to be "of the correct type," but artifact type
classification was judgment-dependent: the RUNG_SEQUENCE artifact descriptions named types
informally, providing no closed classification rules. Two different models could classify
the same output differently and both claim protocol compliance. The OBR/VRO confusion
(test runner output used as live-process evidence) was the most common manifestation.

### D1 — Behavioral predicate open-endedness

The behavioral predicate scanner ended with "or similar," making thread count
non-deterministic: the same prose could yield different thread counts across invocations
depending on how the open set was interpreted. A closed enumeration was the obvious fix,
but a 35-verb closed list is not actually exhaustive — domain-specific verbs (bills,
schedules, recommends, diagnoses, etc.) fall outside any finite vocabulary. A list long
enough to appear exhaustive gives false confidence while still having gaps.

### Scale invariance (not addressed)

A trivial behavior and a complex integration both require identical seven-rung descent.
The protocol has no complexity-proportional path. This is a known structural property of
the design — not a defect. Any fix (skip mechanism, tier system) would conflict with P2
(forward-only discipline) or add a meta-protocol layer. Documented here as out of scope.

---

## Decision

### Fix 1 — Artifact type taxonomy (Attractor B)

Add a `type_label` field to each `RUNG_SEQUENCE` entry and a formal type classification
section to the prompt. Classification is by **production method, not content**:

| Rung | type_label |
|---|---|
| prose | prose-type |
| criteria | criteria-type |
| formal notation | notation-type |
| executable validation | EV-type |
| validation run observation | VRO-type |
| executable implementation | EI-type |
| observed running behavior | OBR-type |

Classification rules added to prompt:
- VRO-type: any test runner invocation, regardless of pass/fail
- OBR-type: live-process invocation only — file reads, test runs, and static analysis
  never produce OBR-type output
- EI-type: file-write tool calls at the EI rung — file-writes at the EV rung produce
  EV-type, not EI-type
- When A4 requires an artifact of the correct type, classify by production method first —
  content resembling a different type does not change the classification

### Fix 2 — Predicate definition (D1)

Replace "or similar" with a structural definition of the category. Restore the 9 canonical
verbs as examples and add:

> "or any finite verb where the subject is the system and the object is a data entity,
> user action, or external system"

**Why not a closed list:** any finite verb list has gaps for domain-specific vocabulary.
The structural definition (subject = system, object = data entity / user action / external
system) handles every domain without enumeration. The canonical verbs serve as examples
and anchor the definition; the structural rule handles everything else. Judgment is still
required at the margin, but it is *principled* judgment (check subject + object structure)
rather than list-lookup.

---

## Implementation

Changes to `lib/groundPrompt.py`:

1. Add `type_label` field to all 7 `RUNG_SEQUENCE` entries
2. Add `_type_taxonomy_block()` helper generating the classification section
3. Wire `_type_taxonomy_block()` into `GROUND_PARTS_MINIMAL["core"]` after rung table
4. Update `_rung_table()` to include `type_label` in each row
5. Replace 35-verb closed list with 9 canonical verbs + structural definition

New test file: `_tests/ground/test_ground_adr0189.py`

---

## Consequences

- **Positive**: A4's "correct type" now has a ground truth; type disputes resolve to
  production method, not content interpretation
- **Positive**: Thread count is anchored to a structural rule rather than an open
  vocabulary — deterministic for any prose that follows subject-verb-object structure
- **Positive**: Domain-specific verbs are automatically covered by the structural
  definition without requiring list updates
- **Known limitation**: Scale invariance remains — all behaviors require seven-rung
  descent regardless of complexity; no fix proposed
