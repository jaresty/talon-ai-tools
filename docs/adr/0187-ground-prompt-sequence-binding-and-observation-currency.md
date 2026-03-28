# ADR-0187: Sequence-Binding Extension to P4

**Status**: Accepted
**Date**: 2026-03-28

---

## Context

ADR-0186 added P4 (Rung action discipline), which names a closed action set per rung and an
ordered sequence for the EV rung. P4 was expected to subsume L31 (pre-existence check gates
V-complete) and the OBR forward gate (live-process must precede test-suite). Both were deleted
then restored — L31 in the same ADR-0186 commit ("format-specific, not P4-derivative"), the
OBR forward gate in a follow-up fix (349e881a).

The root cause: P4 *enumerates* ordered sequences but never states the ordering is *binding
for completion*. Two gap classes remain:

1. **Sequence completion not required before sentinels.** P4 lists EV actions in order but
   doesn't say V-complete may not be emitted until the full sequence has run. L31 fills this
   gap explicitly.

2. **OBR has no explicit ordered sequence.** With no sequence to bind, the forward gate has
   no principle to derive from.

This ADR adds a sequence-binding clause to P4 and fully enumerates the OBR sequence, then
immediately deletes all rules that become derivable. The goal is maximum compression: every
rule that can be mechanically derived from a principle should be deleted, leaving only rules
that encode genuinely new information (content gates, regression guards, scope constraints)
that no principle reaches. Specific rules kept alive by inertia or caution are a maintenance
liability — they diverge from principles under future edits and become sources of confusion
about which is authoritative. High risk tolerance — the test suite is the arbiter of what
was actually subsumed; failures restore with an explanation of the gap.

---

## Full rule analysis

Every explicit rule in the OBR section (and the two cross-cutting rules that interact with
it) is assessed for derivability after the proposed amendments.

### Proposed P4 amendments

**Clause A — Sequence binding:**
> "The sequence enumerated for a rung is binding for completion — no completion sentinel
> for the rung may be emitted until the full sequence has been executed in order; no
> content other than the next step in the sequence may appear between steps."

**Clause B — OBR ordered sequence (replaces "read-only tool calls only, no writes"):**
> "OBR rung: (1) criterion re-emission, (2) provenance statement, (3) live-process
> invocation of the implementation artifact — for artifacts requiring a start step before
> querying, live-process invocation consists of process-start followed by query, both
> tool calls required — (4) exec_observed sentinel, (5) test suite run — in that order
> — read-only only, no writes."

### Rule-by-rule derivability table

| Rule | Location | Derivable after amendments? | Path / residual |
|------|----------|-----------------------------|----------------|
| Criterion re-emission required at OBR | OBR prose | **Yes** | P4 Clause B step (1); Clause A: no content may precede step (1) at the rung |
| "Tool call is only valid next action after criterion re-emission" | OBR prose | **Yes** | P4 Clause A: no content other than next step may appear between steps; step (2) is prose, step (3) is the tool call |
| "Planning statements between criterion re-emission and tool call are violations" | OBR prose | **Yes** | Same as above — corollary of Clause A |
| Provenance statement required before tool call | OBR prose | **Yes** | P4 Clause B step (2); Clause A ordering |
| "If target is a test runner, stop" (provenance gate) | OBR prose | **Yes** | P4: OBR step (3) type is live-process invocation; invoking a test runner is wrong type — P4 closed action set |
| Thread N complete requires tool call after OBR label — condition (1) | OBR checklist | **Yes** | P4 Clause B step (3) is a tool call; Clause A: completion requires full sequence |
| OBR label after most recent impl_gate — condition (2) | OBR checklist | **Yes** | Already derivable from rung table gate column for OBR + P3 sequential descent |
| Non-empty verbatim output after OBR label — condition (3) | OBR checklist | **Yes** | P1 (evidential boundary) + exec_observed sentinel format definition |
| exec_observed directly demonstrates criterion — condition (4) | OBR checklist | **Partial** | P1 + rung table artifact definition; rung table currently says "live-process output" without "demonstrates criterion" — requires rung table amendment (see below) |
| Full test suite run required — condition (5) | OBR checklist | **No** | Genuine content gate; no principle path |
| Every failing test acknowledged with reason | OBR checklist | **No** | Scope/content requirement; not derivable from action set |
| OBR forward gate (test runner blocks completion) | OBR forward gate | **Yes** | P4 Clause B: live-process is step (3), test suite is step (5); Clause A: completion requires full sequence in order |
| "Test suite may follow but not precede/replace live-process" | OBR forward gate | **Yes** | Same — corollary of sequence ordering |
| All-criteria demonstration required | OBR prose | **Yes** | Same path as condition (4): amend OBR artifact type to "directly demonstrating all criteria declared for this thread"; P1 then subsumes it |
| Two-call sequence for server artifacts | OBR prose | **Yes** | P4 definitional amendment: fold into Clause B step (3) definition of "live-process invocation" — same mechanism as rung table amendment for condition (4) |
| "File read never satisfies OBR" | OBR prose / rung table | **Yes** | Already in rung table void condition ("file read used as evidence"); duplicate |
| "Thread N complete immediately follows exec_observed" | OBR prose | **Yes** | P4 Clause B: step (4) exec_observed precedes step (5) test suite precedes completion sentinel; Clause A binding |
| "Thread N complete may not appear until... exists in this cycle" (preamble) | OBR prose | **Yes** | P4 Clause A: completion requires full sequence — redundant wrapper around conditions (1)–(5) |
| L31 — pre-existence check gates V-complete | EV prose | **Yes** | P4: pre-existence check is step (1) of EV sequence; Clause A: V-complete requires full sequence |
| Rung-entry gate | Cross-cutting | **Yes** | P1 restatement in procedural form — "before producing content at any rung, verify valid exec_observed exists" is P1's gate condition applied forward; already derivable from P1 + rung table gate column |

### Rung table amendment required for conditions (4) and all-criteria

The OBR artifact type currently reads: "live-process output — output produced by a tool call
that starts or queries a running process."

Amend to: "live-process output — output produced by a tool call that starts or queries a
running process, directly demonstrating all criteria declared for this thread."

With this amendment:
- Condition (4) ("exec_observed directly demonstrates criterion") is P1: the gate is
  satisfied only by output classified as the rung's artifact type, which now includes
  "directly demonstrates."
- All-criteria demonstration ("live-process must demonstrate every criterion, not only the
  primary one") is P1: output that demonstrates only a subset is not classified as the
  rung's artifact type.

---

## Decision

1. **Add Clause A (sequence binding) to P4.**
2. **Replace OBR "read-only" entry with explicit ordered sequence (Clause B), folding the two-call server definition into step (3).**
3. **Amend OBR artifact type in rung table to "directly demonstrating all criteria declared for this thread."**
4. **Delete all rules in the derivable rows of the table above.**
5. **Keep**: condition (5) test suite gate, failing-test acknowledgement, and the continuous transition rule.

Phases 3 and 4 of ADR-0186's migration pattern (migrate literal pins, then delete) are
**collapsed into one step**. The test suite is the arbiter. If a test fails after deletion,
the rule was not subsumed and is restored with an explanation of why the principle doesn't
reach it.

---

## Implementation

### Step 1 — Amend `lib/groundPrompt.py`

Three edits:

**P4 — add Clause A after the type-not-count clause:**
```
the sequence enumerated for a rung is binding for completion —
no completion sentinel for the rung may be emitted until the full sequence
has been executed in order; no content other than the next step in the
sequence may appear between steps;
```

**P4 — replace OBR entry:**
```
OBR rung: (1) criterion re-emission, (2) provenance statement,
(3) live-process invocation of the implementation artifact — for artifacts
requiring a start step before querying, live-process invocation consists of
process-start followed by query, both tool calls required —
(4) exec_observed sentinel with verbatim output,
(5) test suite run — in that order — read-only only, no writes;
```

**Rung table — OBR artifact type:**
```
artifact="live-process output — output produced by a tool call that starts
or queries a running process, directly demonstrating all criteria declared
for this thread"
```

### Step 2 — Delete derivable rules from `lib/groundPrompt.py`

Delete all prose covered by the "Yes" rows in the derivability table:

- Criterion re-emission required + no-planning-between rule (OBR prose block 1)
- Provenance statement rule and its test-runner stop clause
- Thread N complete preamble ("may not appear until a tool call exists...") — conditions (1)–(4)
- OBR forward gate ("if the most recent tool call at this rung is a test runner...")
- "Thread N complete immediately follows exec_observed" rule
- L31 explicit forward gate ("if that tool call has not been made... only valid next action is that tool call")
- Rung-entry gate (entire block — P1 procedural restatement)

Keep:
- Condition (5) and failing-test acknowledgement requirement
- "File read never satisfies OBR" can be removed as it duplicates the rung table void condition — low risk

### Step 3 — Write tests

New test file: `_tests/ground/test_ground_adr0187.py`

Behavioral-effect anchors (not literal-phrase pins):

1. P4 contains a sequence-binding clause referencing completion sentinels and step ordering
2. OBR action list contains criterion re-emission as a named step
3. OBR action list contains provenance statement as a named step
4. OBR action list contains live-process invocation as a named step
5. OBR action list contains test suite run as a named step, after live-process
6. OBR rung table artifact type references "directly demonstrates"
7. L31 gate behavior: V-complete blocked without pre-existence check (behavioral, not phrase)
8. OBR forward gate behavior: test-suite-only OBR blocks Thread N complete (behavioral, not phrase)
9. Criterion re-emission behavior: OBR label requires criterion text before tool call (behavioral)

Deletion-guard file: `_tests/ground/test_ground_adr0187_deletions.py`

Guards verifying the deleted phrases are absent (prevents re-introduction):
- L31 explicit gate phrase
- OBR forward gate phrase
- Rung-entry gate phrase
- Criterion re-emission explicit prohibition phrase

### Step 4 — Run full test suite

```bash
python3 -m pytest _tests/ground/ -x
```

Any failure identifies a rule that was not subsumed. For each failure: restore the deleted
prose, add a row to the "not subsumed" table in this ADR explaining why the principle doesn't
reach it.

---

## Expected size impact

| Change | Delta |
|--------|-------|
| P4 Clause A (sequence-binding) | +~120 chars |
| P4 OBR sequence (replaces "read-only") | +~50 chars |
| Rung table OBR artifact amendment | +~30 chars |
| Deletions (derivable rules + two-call + all-criteria) | −~700 chars |
| **Net** | **−~450 chars** |

---

## Consequences

- **Positive**: new OBR escape routes that respect action type and sequence are immediately
  named as P4 violations; no new principle required
- **Positive**: the OBR section becomes structurally parallel to EV — both have numbered
  sequences that P4's binding clause governs
- **Positive**: rung-entry gate deletion removes a procedural restatement of P1 that has been
  a source of confusion about when it applies
- **Risk**: the sequence-binding clause "no content other than the next step may appear between
  steps" is strict — verify it doesn't block legitimate prose that currently appears between
  OBR steps (e.g., "A file read never satisfies this rung" explanatory text)
- **Risk**: deleting conditions (1)–(4) of the Thread N complete checklist removes an
  explicit enumeration that the model may rely on for self-checking; if tests show regressions
  in Thread N complete discipline, restore as a P4 corollary note rather than independent rules
- **Not addressed**: condition (5) test suite gate and failing-test acknowledgement — these
  are regression guards, not criterion-demonstration requirements; no existing or proposed
  principle covers "no other behavior was broken"; a new principle would be required to
  subsume them and is not proposed here
