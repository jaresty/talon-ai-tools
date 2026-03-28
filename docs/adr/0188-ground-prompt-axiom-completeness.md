# ADR-0188: Axiom Completeness — Provenance, Cycle Identity, and Convergence

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

A clash/drift/orbit analysis of the current ground prompt (executed via `bar build probe fail
clash drift` and `bar build probe fail orbit`) identified five clashes — pairs of explicitly
stated rules that cannot simultaneously be satisfied — plus seven drifts (structurally stated
constraints with no enforcement mechanism) and three structural attractors that recur across
entry conditions.

The analysis conclusion: **the clashes are not rule-writing errors; they are signals that
the axiom set is incomplete.** Each clash marks a behavioral distinction that the current
four axioms (A1, A2, A3, R2) cannot derive, forcing the prompt to special-case it. Special
cases written alongside axioms eventually contradict each other because the axiom set has no
authority over the domain the special case is trying to govern.

### Clashes identified

**C1 — Manifest once vs. mid-run revision**
"✅ Manifest declared may be emitted exactly once per invocation" contradicts "when a new gap
is discovered mid-run, return to prose and re-emit a revised manifest." No compliant path
when mid-run discovery requires a new thread.

**C2 — Carry-forward read vs. P4 EV closed action set**
Carry-forward requires a read tool call before modifying the EV artifact. P4's EV action set
is pre-check → file-writes → test runner. Read is not in the set; P4 declares "any tool call
outside it is a protocol violation." Modifying an EV artifact has no compliant path.

**C3 — EI loop trap with no exit**
If multiple EI iterations fail without closing the gap, HARD STOP is blocked (identical
criterion), returning to formal notation is blocked (spec *did* model the criterion), and
looping within EI is prescribed but failing. The protocol reaches a terminal state with no
valid next token.

**C4 — Prose re-emission with completed threads**
Prose re-emission every cycle requires [T: gap-name] markers on every behavioral predicate.
When threads are already complete, including their markers implies they are still open;
omitting them violates the bracketing rule. Neither is compliant under the once-per-invocation
manifest lock.

**C5 — OBR void condition eats its own mandatory step 5**
P4 requires a test suite run at OBR step 5. The rung table void condition reads: "test runner
output — a test-suite pass is validation-run-observation-type output, not
observed-running-behavior-type output, and voids this rung." The void condition does not
distinguish "test runner output used as OBR live-process evidence" from "test runner output
appearing after live-process evidence." A compliant step-5 run voids the rung that mandated it.

### Root cause

All five clashes trace to three missing axioms:

1. **No provenance axiom.** The current axioms define gates by artifact *type* but not by
   *causal chain*. A type-matching artifact from a prior cycle, a different thread, or a
   different gap is not distinguished from one produced in direct response to the current gap.
   This forces the prompt to special-case every "current cycle" condition individually — and
   the carry-forward rule (which is a deliberate provenance bridge) has no first-class concept
   to derive from, colliding with P4's closed action set.

2. **No cycle identity axiom.** "Current cycle" appears as a condition in impl_gate, carry-
   forward, and several gate checks. Cycle boundaries are defined only narratively (prose
   re-emission). This makes all cycle-conditioned rules depend on transcript interpretation
   rather than a formal anchor, and it makes the prose re-emission rule interact with the
   manifest in ways that produce C4.

3. **No convergence axiom.** The protocol requires forward progress but provides no bound on
   upward returns. The failure class taxonomy (impl failure → EI loop; spec failure → FN;
   observation unproducible → prose) covers three cases but leaves the case where EI loops
   without gap closure with no valid next token (C3).

---

## Decision

Add three axioms (A4, A5, P5) and fix two rule-design errors (C5 OBR void scope, manifest
once-per-invocation). Delete all rules that become derivable after the additions. The test
suite is the arbiter of what was actually subsumed.

### A4 (Provenance)

> An artifact satisfies a rung gate only if it was produced by a tool call made in direct
> response to the gap declared at the immediately prior rung in the current cycle. Evidence
> from a prior cycle, a different thread, or a different gap does not satisfy any gate
> regardless of type match.

**Derives:**
- impl_gate requires a current-cycle VRO (provenance chain: gap → VRO exec_observed →
  impl_gate, all within one cycle)
- Carry-forward is a formal provenance declaration: it bridges prior-cycle failure names into
  the current artifact explicitly. Its existence becomes mandatory precisely because A4 would
  otherwise void an artifact modified without establishing provenance to the prior failure.
  The carry-forward read of the test file is part of provenance establishment, not an
  independent tool call category — P4's EV step 1 ("pre-existence check") expands to include
  it without requiring a new action type.
- "Prior-cycle output does not satisfy any gate" (currently stated alongside A3) becomes a
  consequence of A4 rather than a separate rule.

### A5 (Cycle identity)

> A cycle for a thread is the interval bounded by the prose rung emission that opens it and
> either the Thread N complete sentinel or an upward return that closes it. The "current cycle"
> in any rule refers to the interval opened by the most recent prose emission for the current
> thread. Prose re-emission for Thread N does not affect the cycle identity of any other thread.

**Derives:**
- Prose re-emission scope: re-emitting prose for a thread is scoped to that thread's current
  cycle. [T: gap-name] markers are required only for the gap being addressed in this cycle,
  not for all threads in the session. This resolves C4: already-complete threads are in
  closed cycles; the re-emitted prose opens a new cycle for the current thread only.
- All cycle-conditioned rules (impl_gate, carry-forward applicability, "current cycle's VRO")
  are now formally anchored to the A5 cycle boundary rather than to transcript interpretation.

### P5 (Convergence)

> A thread converges only when its gap closes. If a thread has executed EI without gap
> closure and the criterion has not changed since the most recent prior HARD STOP cycle for
> this thread, the criterion is underspecified — return to the criteria rung. This is the
> convergence exit; it is not optional.

**Derives:**
- The EI loop trap (C3) has a defined exit: repeated EI failure with an unchanged criterion
  triggers P5, which mandates return to criteria.
- The HARD STOP identical-criterion prohibition becomes a consequence of P5: an identical
  criterion would immediately re-trigger P5, making the HARD STOP accomplish nothing. P5
  subsumes the prohibition as a forward-derivable corollary rather than a backward-looking
  special case.
- The HARD STOP failure-class taxonomy (impl failure → EI loop; spec failure → FN; criterion
  underspecified → criteria rung) is now complete: all three branches have a defined exit.

### Rule-design fixes

**Fix 1 — OBR void condition scope (C5)**

The void condition "test runner output voids this rung" is currently categorical. Scope it:

> voids_if: "... test runner output *used as OBR live-process evidence* voids this rung;
> test runner output at OBR step 5 does not void this rung"

P4 Clause B already establishes that the test suite run is step 5 (after live-process
invocation); with this scope restriction, step 5 output is classified as fulfilling the P4
sequence requirement rather than as a void-triggering artifact-type mismatch.

**Fix 2 — Manifest revision semantics (C1)**

Drop "✅ Manifest declared may be emitted exactly once per invocation."

Replace with:

> ✅ Manifest declared opens the thread manifest for the session. A revised manifest may be
> emitted when a new gap is discovered mid-run — return to prose, re-emit prose for all
> incomplete threads with the new gap included, then emit ✅ Manifest declared with the
> revised thread list. Completed threads are closed and may not be re-opened by a revision.
> The N in ✅ Manifest declared must reflect the current incomplete thread count at the time
> of emission.

---

## Full derivability table

| Rule / special case | Currently in prompt | Derivable after A4/A5/P5? | Path |
|---|---|---|---|
| impl_gate requires current-cycle VRO | Yes | **Yes** | A4: impl_gate artifact must have current-cycle provenance; VRO exec_observed is the causal predecessor |
| Prior-cycle output doesn't satisfy any gate | Yes (alongside A3) | **Yes** | A4: prior-cycle evidence lacks current-cycle provenance |
| Carry-forward read is required at EV | Yes | **Yes** | A4: carry-forward establishes provenance; P4 EV step 1 "pre-existence check" expands to include it |
| Prose re-emission requires [T:] markers only for current thread | Not stated; current rule creates C4 | **Yes** | A5: prose re-emission scope is per-thread; completed threads are in closed cycles |
| Current-cycle VRO must be for the current criterion | Yes (impl_gate rule) | **Yes** | A4: provenance chain includes the gap identity |
| HARD STOP identical-criterion prohibition | Yes | **Yes** | P5: identical criterion → P5 fires → return to criteria; HARD STOP would not advance past it |
| EI loop trap exit | Missing (C3) | **Yes** | P5: repeated EI failure + unchanged criterion = criteria rung return |
| HARD STOP failure-class taxonomy complete | Partial (C3 missing) | **Yes** | P5 provides the third branch |
| Manifest once-per-invocation | Yes | **No — design error** | Fix 2: replace with revision semantics |
| OBR void eats step 5 | Yes | **No — design error** | Fix 1: scope void condition |
| Carry-forward format / verbatim naming | Yes | **No** | Content gate; A4 requires provenance declaration but doesn't specify format |
| "Behavioral predicate" definition + "or similar" | Yes | **No** | Open-ended; closed enumeration desirable but not derivable from axioms |

### Rules to delete after additions

The following phrases become derivable and should be removed. Where noted, both sides of a
clash are removed — the axiom now owns the domain both sides were trying to govern.

**From C1 (manifest once vs. revision) — Fix 2 removes the "once" side:**
- "✅ Manifest declared may be emitted exactly once per invocation"
  — replaced by Fix 2 revision semantics; "when a new gap is discovered mid-run, return to
  prose and re-emit a revised manifest" becomes the surviving canonical positive statement

**From C2 (carry-forward read vs. P4 EV action set) — A4 derives the read requirement:**
- "when the artifact is modified, invoke a tool call to read the current test file before
  emitting carry-forward rows"
  — derivable from A4 (provenance establishment) + P4 EV step 1 expanded to include
  "read of existing test file for carry-forward"; the carry-forward *format* rule (verbatim
  failure name citation) stays — it is a content gate A4 does not reach

**From C3 (EI loop trap) — P5 subsumes both sides of the clash:**
- "if the implementation did not close the gap, loop within executable implementation" as a
  standalone rule — absorbed as the first branch of the P5 failure-class taxonomy; delete
  the standalone form
- "Before emitting 🛑 HARD STOP, locate the criterion written in the most recent prior HARD
  STOP cycle for this thread — if it is textually identical to the current criterion, HARD
  STOP is a protocol violation: an identical criterion means the upward return accomplished
  nothing; if the implementation did not close the gap, loop within executable implementation;
  if the spec did not model the criterion, return to formal notation before issuing HARD STOP."
  — entire block deleted; P5 provides the complete taxonomy with the convergence exit; the
  HARD STOP identity prohibition is a P5 corollary (identical criterion → P5 fires immediately)

**From A4 (provenance):**
- "🟢 Implementation gate cleared requires a 🔴 Execution observed from the current cycle's
  validation run observation rung — not from a prior cycle"
  — A4 corollary: prior-cycle evidence lacks current-cycle provenance
- "artifacts, test results, and artifact names from prior cycles have no standing in the
  current cycle" (the corollary restatement alongside A3)
  — A4 subsumes it; the A3 boundary definition is still needed, this corollary is redundant

**C4 (prose re-emission with completed threads) — A5 scopes, rules are updated not deleted:**
- The prose re-emission rule is **reworded** (not deleted): replace "at the start of every
  cycle" with "at the start of every cycle for the current thread, covering only the gap
  being addressed in that cycle"
- The [T: gap-name] counting rule before ✅ Manifest declared is **reworded**: count markers
  in the re-emitted prose for the current thread only, not all prose in the session

---

## Implementation

### Step 1 — Add A4, A5, P5 to `lib/groundPrompt.py`

Insert after R2, before P1:

**A4:**
```
A4 (Provenance): an artifact satisfies a rung gate only if it was produced by a tool call
made in direct response to the gap declared at the immediately prior rung in the current cycle;
evidence from a prior cycle, a different thread, or a different gap does not satisfy any gate
regardless of type match.
```

**A5:**
```
A5 (Cycle identity): a cycle for a thread is the interval bounded by the prose rung emission
that opens it and either ✅ Thread N complete or an upward return that closes it;
the current cycle is the interval opened by the most recent prose emission for the current
thread; prose re-emission for one thread does not affect the cycle identity of any other thread.
```

**P5:**
```
P5 (Convergence): a thread converges only when its gap closes; if EI has executed without
gap closure and the criterion has not changed since the most recent prior HARD STOP cycle
for this thread, the criterion is underspecified — return to the criteria rung;
this is mandatory, not optional.
```

### Step 2 — Apply rule-design fixes

- Replace void condition in `RUNG_SEQUENCE` OBR entry as specified in Fix 1.
- Replace manifest once-per-invocation rule with revision semantics as specified in Fix 2.

### Step 3 — Delete derivable rules

Per the derivability table above. The test suite is the arbiter.

### Step 4 — Run full test suite

```bash
python3 -m pytest _tests/ground/ -x
```

For each failure: restore the deleted prose, add a row to this ADR's "not subsumed" table
with an explanation of why A4/A5/P5 don't reach it.

---

## Not addressed

The orbit analysis identified three additional structural properties that are not fixed here:

- **Attractor B (sentinel hollow compliance)**: artifact type classification is judgment-
  dependent; A4 and A5 tighten when evidence qualifies but don't formalize the type taxonomy.
  A formal type registry would be required. Not proposed here.
- **Scale invariance**: a trivial behavior and a complex integration both require identical
  seven-rung descent. The protocol has no complexity-proportional path. Not proposed here.
- **"Behavioral predicate" open-endedness (D1)**: thread count depends on an enumerable but
  undefined set. Closing "or similar" requires either a closed verb list or a different
  threading mechanism. Not proposed here.

---

## Consequences

- **Positive**: five clashes eliminated; each previously conflicting rule either becomes a
  derivable corollary or is replaced by a consistent revision
- **Positive**: HARD STOP failure-class taxonomy is complete; no terminal states without a
  valid next token
- **Positive**: prose re-emission is no longer in tension with the manifest; each thread's
  re-emitted prose is scoped to its own open cycle
- **Positive**: carry-forward's purpose is grounded in A4 provenance; its requirement is
  derivable, only its format is a content gate
- **Risk**: A5's cycle-per-thread model may interact with the manifest counting rule in edge
  cases where two threads are in overlapping prose emissions — verify no test regression on
  multi-thread session tests
- **Risk**: P5's convergence trigger ("criterion has not changed") inherits D5's semantic
  gap-identity problem; verify whether the identical-criterion check needs a formal definition
  of "changed" to be operationalizable
- **Risk**: Fix 2 (manifest revision semantics) changes observable behavior — manifests can
  now be revised mid-run; existing tests that assert manifest-once behavior will need updating
  to assert the revised semantics instead
