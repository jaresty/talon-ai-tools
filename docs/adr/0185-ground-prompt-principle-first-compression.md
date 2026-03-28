# ADR-0185: Ground Prompt Principle-First Compression

**Status:** Proposed
**Date:** 2026-03-28
**Follows:** ADR-0184 (lean rewrite — A1/A2/P2 removal, rung-entry gate trim)

---

## Context

The ground prompt currently sits at ~26 KB. ADR-0184 removed ~1.2 KB of redundancy
(A1, A2, P2, rung-entry gate items a–c). Further compression is possible: the ~18 KB
"protocol mechanics" section consists almost entirely of per-rung instantiations of four
named principles (P1, P3, A3, R2). These instantiations were added reactively across
L1–L30 escape-route closures and earlier ADRs to force compliance where the principles
alone were not being applied locally.

### Depends analysis result

A test-suite audit (`python3 -c "import ast…"` across `_tests/ground/*.py`) surfaces
~150 specific prose phrases pinned via `assertIn`. Critically, most rules previously
identified as "redundant P1/P3/A3/R2 instantiations" are themselves test-pinned. This
creates a hard dependency:

```
prose rule X
    ↑ assertIn("fragment of X", self.core)  ← test_ground_*.py
```

Deleting prose without updating the pinning test breaks the test suite even when the
rule is semantically subsumed by a principle. Compression therefore has **two coupled
dependencies**:

1. Prose rewrite (sharpen principles → delete instantiations)
2. Test migration (literal-phrase anchors → behavioral-effect anchors)

These cannot be done independently: if you delete prose first, tests break; if you
migrate tests first, you are writing tests for a prompt that has not changed yet.

### Ten genuine per-rung exceptions

The mapping analysis (bar `probe full mapping adversarial`) identified rules that are
**not** inferrable from any of the four principles regardless of how precisely they are
stated. These must remain in prose:

1. **exec_observed verbatim format** — triple-backtick, omission marker with count
2. **Conjunction-splitting rule** (criteria rung) — "if criterion contains 'and', split"
3. **Carry-forward format** (EV modification) — quote prior failure verbatim from exec_observed
4. **Harness error handling** (EV rung) — fix harness, not HARD STOP
5. **HARD STOP conditions** — valid only after exec_observed + Gap at VRO rung
6. **Provenance statement at OBR** — name invocation target before tool call
7. **impl_gate is first token** — no tool call, no prose before it in the response
8. **[T: gap-name] markers in prose** — count must match manifest thread list
9. **Manifest declared exactly once per invocation** — invocation-level singleton
10. **Test vacuity checks** — static: run before edit; runtime: perturbation required

---

## Decision

Adopt **principle-first flattening** in three sequenced phases:

### Phase 1 — Sharpen the four principles

Add precision clauses to P1, P3, A3, and R2 so that each subsumes its instantiations
without ambiguity:

| Principle | Current gap | Precision addition |
|---|---|---|
| P1 | Doesn't cover intra-cycle cross-rung type mismatch | "…including cross-rung output within the same cycle — a tool call at rung X does not satisfy the gate at rung Y even if both are in the current cycle." |
| P3 | Doesn't cover sentinel singletons | "…and each sentinel defined in the sentinel block is valid exactly once at its defining rung per invocation unless noted." |
| A3 | Doesn't define when evidential context resets within a thread | "…the evidential context resets at every re-emission of the prose rung label." |
| R2 | Doesn't state the void-propagation rule explicitly | "…if the prior rung's artifact is absent or void, no artifact below it is valid regardless of content." |

### Phase 2 — Classify and migrate tests

For each `assertIn` anchor, classify as one of:

- **`principle-derivative`**: the rule is a direct instantiation of a sharpened principle
  → replace the literal-phrase assertIn with a behavioral-effect assertion (e.g., assert
  that a correctly-described protocol state satisfies the rule, rather than that a
  specific substring is present in the prompt)
- **`rung-specific-exception`**: one of the ten genuine exceptions
  → keep the assertIn; the prose it anchors is not deleted
- **`boundary-case`**: rule sits at the boundary — principle subsumes the general case
  but the specific phrasing captures a nuance not in the table
  → evaluate individually; default to keeping unless the rung table voids_if already
  names it explicitly

**Migration pattern for principle-derivative anchors:**

Before (literal-phrase anchor):
```python
self.assertIn("all seven rungs must complete for Thread N before any rung content for Thread N+1 may appear", self.core)
```

After (behavioral-effect anchor):
```python
# P3 sequential-thread constraint: any content for thread N+1 is blocked until thread N is complete
self.assertIn("Thread N", self.core)
self.assertIn("Thread N+1", self.core)
# The operative rule must exist in some form — P3 or prose — that names the sequential constraint
has_sequential_rule = (
    "all seven rungs must complete for Thread N before any rung content for Thread N+1" in self.core
    or ("Thread N complete" in self.core and "before any rung content for Thread N+1" in self.core)
)
self.assertTrue(has_sequential_rule, "P3 sequential-thread constraint must exist in some form")
```

### Phase 3 — Delete principle-derivative prose

With tests migrated to behavioral-effect anchors, delete each principle-derivative prose
block. The rung table's `gate` and `voids_if` columns already encode many of these; the
sharpened principles encode the rest.

**Expected size reduction:** ~8–12 KB from the ~18 KB protocol mechanics section,
leaving the 10 genuine exceptions + sharpened principles + rung table.

---

## Sequencing constraint

```
Phase 1 (sharpen principles)
    → Phase 2 (classify + migrate tests — tests still pass on current prompt)
        → Phase 3 (delete prose — tests pass on compressed prompt)
```

Phase 2 must produce a test suite that passes against both the current (pre-deletion)
prompt and the target (post-deletion) prompt. This is the gate condition for Phase 3.

---

## Consequences

**Benefits:**
- Prompt size reduction of ~30–45% from current 26 KB
- Principles become the single authoritative source — future escape-route fixes sharpen
  principles rather than adding new prose paragraphs
- Test suite anchors behavioral effects rather than prose wording, making prompt
  rewording safe without test churn

**Risks:**
- Phase 2 test migration is the critical path: migrating a test incorrectly (making it
  too weak) could allow a behavioral regression to pass undetected
- Some boundary-case rules may need individual judgment; default to keeping
- The rung table `voids_if` column must be verified as verbatim-rendered in the prompt
  (it is, via `_rung_table()`) before treating it as a safe replacement for prose

**Out of scope:**
- The ten genuine per-rung exceptions are not touched
- Sentinel formats (`SENTINEL_TEMPLATES`) are not touched
- Rung table structure is not changed (only the principle text changes)

---

## Acceptance criteria

- [ ] Four principles sharpened with precision clauses; all current tests pass
- [ ] Each `assertIn` anchor classified as `principle-derivative`, `rung-specific-exception`, or `boundary-case`
- [ ] All `principle-derivative` tests migrated to behavioral-effect anchors; suite passes on current prompt
- [ ] Prose deletion applied; suite passes on compressed prompt
- [ ] Ground prompt size ≤ 16 KB (from 26 KB)
- [ ] No escape-route regression: run the L1–L30 test files and confirm all pass
