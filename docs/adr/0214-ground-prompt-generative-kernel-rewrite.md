# ADR-0214: Ground Prompt — Generative Kernel Rewrite

**Status**: Proposed
**Date**: 2026-03-28

---

## Context

ADR-0198 pruned derivable corollaries from the ground prompt, reducing it to axioms + rung table + type edge cases. Since then, ADRs 0199–0213 re-accumulated ~15 additional rule paragraphs — all from transcript analysis of escape routes. The prompt is again growing under escape-route pressure.

The root cause is structural: escape routes are being closed at the **behavioral level** (enumerating prohibited actions at each rung) rather than at the **type definition level** (making the type definitions precise enough that the prohibited actions are type errors). When a rule must be added to prohibit X, it means the type definition of that rung's artifact doesn't yet make X obviously wrong. The prohibition is a patch on an underspecified type.

**Abductive hypothesis**: If each rung's artifact type were defined with enough precision that "test renderer produces VRO-type," "stub is not implementation-type," "import failure is not a red run," and "file read produces read-type not OBR-type" all follow from the type definition alone, the enumerated prohibitions in P4 and the escape-route-closer block would become redundant. The prompt could be stated once, generatively, and not need patching.

**Alternative hypothesis**: Some escape routes require explicit closure because they involve tempting substitutions a model will rationalize even after understanding the type definitions — the "why-sentence" class identified in ADR-0198. These are not type errors; they are epistemically seductive misclassifications.

The ADR-0198 analysis was correct about which-sentences are non-derivable. What it did not do was audit *which specific escape-route closers* fall into which category — and thus could not determine whether the rung type definitions were the proximate fix.

---

## Decision

Rewrite `GROUND_PARTS_MINIMAL["core"]` as a **generative kernel** in five sections, replacing the current mixture of axioms, prose principles, P4 enumerations, and escape-route closers.

### Section 1 — Protocol Invariant (one sentence)

> A model's description of completed work is indistinguishable from actually completing it — every gate enforces the distinction by requiring a piece of reality before any claim about reality.

This is the single generative root. Every other rule either follows from it or is a convention (sentinel formats, OBR sequence design).

### Section 2 — Gate Formula (four axioms)

State A1, A2, A4, R2 compactly as a single gate formula:

> **Gate formula**: A rung gate is cleared if and only if a tool call appears in the current cycle whose output (a) was produced by the tool call as a direct response to the gap declared at the prior rung (A4/provenance), (b) has the artifact type defined for this rung in the rung table (A2/type discipline), and (c) was produced in this cycle — not in a prior cycle, a different thread, or a different gap (A1/A5). Type is determined by production method, not content.

A3 (cycle identity) and A5 (cycle boundary) are definitions, not rules — they belong inline in the rung table's gate column.

P1 (evidential boundary), P3 (scope discipline), P5 (convergence), and P6 (cross-thread convergence) are all derivable from this formula and the rung table. They need not appear as named principles.

### Section 3 — Typed Rung Table (seven rows + precise type definitions)

The rung table already exists but its type definitions are too coarse. The audit below (see Classification Audit) shows that most escape routes that required ADR patches are cases where the type definition failed to exclude a plausible-but-wrong production method.

Proposed type definitions, replacing the current artifact-column descriptions:

| Rung | Type label | Artifact type definition (production method) |
|---|---|---|
| prose | prose-type | Natural language produced by the model — no tool calls permitted at this rung |
| criteria | criteria-type | Natural language produced by the model asserting a single falsifiable behavioral property — no tool calls permitted |
| formal notation | notation-type | Structured specification produced by the model (type signatures, interfaces, invariants, pseudocode) — no tool calls permitted; content is non-executable by definition: any content that can be run without modification is implementation-type, not notation-type |
| executable validation | EV-type | A test file produced by a file-write tool call and confirmed runnable by a test-runner tool call at the EV rung; the test runner invocation at this rung produces VRO-type output, not EV-type; EV-type is the *file artifact*, not the runner output |
| validation run observation | VRO-type | Output produced by a test-runner tool call — any test runner invocation produces VRO-type output regardless of pass/fail, environment, or browser mode; this includes test renderers, headless browser runners, and integration runners |
| executable implementation | EI-type | Output produced by a file-write tool call that targets an implementation file — a file-write at the EV rung produces EV-type; a file-write at the EI rung targeting the test file produces neither EI-type nor EV-type unless the meta-test pattern is in effect |
| observed running behavior | OBR-type | Output produced by a tool call that performs a live-process invocation — an HTTP request or browser navigation to a running server's URL; reading a file, running tests (any runner, any mode), or querying static state produces read-type or VRO-type, not OBR-type; OBR-type requires a running process that was started in this session |

**Key change**: VRO-type and OBR-type are now exhaustively defined by production method. The why-sentences that ADR-0198 preserved ("a passing test proves the harness's assertions pass, not that the behavior exists as a running system") are incorporated inline into the type definition rather than stated as separate sentences. A model reading the OBR-type definition cannot claim a test runner satisfies the OBR gate — the type definition excludes it by production method.

### Section 4 — Rung Sequence Table (replaces P4 prose enumerations)

P4 currently enumerates permitted/prohibited actions per rung as prose paragraphs. Replace with a compact sequence table. The table's closed action sets make violations type errors against the table rather than named prohibitions.

| Rung | Permitted tool calls | Order required? | Completion gate |
|---|---|---|---|
| prose | none | — | `✅ I declared` appears in output |
| criteria | none | — | criterion written; `🔴 Gap:` precedes criterion |
| formal notation | none | — | R2 audit section present; all criteria encoded |
| EV | (1) pre-existence check, (2a) import-check run, [stub write + re-run if import fails], (2b) test file write, (3) test runner | yes — (2a) must pass before (2b) | `✅ Validation artifact V complete`; file-write result in transcript; test block content in transcript |
| VRO | test runner only | — | `🔴 Execution observed:` with verbatim output; `🔴 Gap:` citing failing assertion |
| EI | implementation file-write(s) only | — | file-write result in transcript; `🟢 Implementation gate cleared` |
| OBR | (1) criterion re-emission, (2) provenance statement, (3) process-start [if required] + HTTP/browser query, (4) `🔴 Execution observed:`, (5) test suite run | yes | `✅ Thread N complete` |

Any tool call not listed for a rung is a type violation — the sequence table's closed sets replace all of P4's per-rung prohibition prose.

### Section 5 — Non-Derivable Rules (compact, audited)

After applying the precise type definitions and sequence table, the following rules remain because they are *not* type errors or gate formula violations — they are policy decisions or epistemically seductive substitutions:

**Harness error routing** (non-derivable: defines what "red run" means):
> A harness error (import failure, syntax error, missing dependency) is not a red run. The test must have been loadable and its assertions must have run. Fix the harness before treating any output as VRO-type evidence. When EV shows an import failure, repair re-enters at step (2a) — not at (2b) or as a freeform stub write.

**Green-without-red vacuity** (non-derivable: closes specific rationalization):
> A green VRO is only valid as a post-implementation green if a prior red VRO for the same criterion exists in this cycle after the most recent `🟢 Implementation gate cleared`. A green run without a prior red run means the test is vacuous — rewrite it.

**HARD STOP scope** (non-derivable: names the one valid upward return):
> `🛑 HARD STOP` is valid in exactly one case: the current criterion is identical to the criterion from the most recent prior cycle for this thread (P5 — criterion underspecified). All other failure classes route forward: harness error → EV repair; missing implementation → EI; test-interaction failure → EV repair; spec gap → formal notation. HARD STOP does not re-emit `✅ Ground entered` or `✅ Manifest declared`.

**Thread sequencing** (non-derivable: design decision):
> All seven rungs for Thread N must complete before any content for Thread N+1. After `✅ Manifest declared`, the only valid next token is the criteria rung label for Thread 1.

**Integration thread** (non-derivable: design decision):
> When the prose contains two or more behavioral threads, one additional integration thread must be declared as the final manifest entry, asserting composed behavior across at least two threads in a single end-to-end invocation.

**Session persistence** (non-derivable: policy):
> Once `✅ Ground entered` has been emitted, ground protocol remains active until the session ends or the user explicitly exits. Each response must begin by identifying the current rung and current gap.

**Sentinel formats** (arbitrary conventions — keep as registry, not prose).

---

## Classification Audit: Escape-Route Closers → Type Errors vs. Non-Derivable

This audit traces each major escape-route closure (ADRs 0199–0213) to its category:

| Rule | Source ADR | Category | Disposition |
|---|---|---|---|
| Test renderer produces VRO-type, not OBR-type | 0197 | Type error | Absorbed into OBR-type definition |
| File read produces read-type, not OBR-type | 0197 | Type error | Absorbed into OBR-type definition |
| Import failure is not a red run | 0207 | Non-derivable (defines "red run") | Keep in Section 5 |
| Stub-write at EV must go through import-check gate | 0207/0212/0213 | Sequence error | Absorbed into EV sequence table |
| Stub is not implementation | 0209 | Type error (stub-type ≠ EI-type) | Absorbed into EI-type definition |
| OBR cannot use test runner as query | 0208 | Type error | Absorbed into OBR-type definition |
| EV may not write implementation files | 0206 | Sequence error | Absorbed into EV sequence table (closed action set) |
| EI may not modify test files | 0211 | Sequence error | Absorbed into EI sequence table |
| VRO re-run without EI edit | 0202/0208 | Sequence error | Absorbed into sequence table ordering |
| Green-without-red vacuity | 0195 | Non-derivable (closes rationalization) | Keep in Section 5 |
| HARD STOP scope | 0199 | Non-derivable (policy) | Keep in Section 5 |
| Criteria anchored to manifest verbatim | 0194 | Gate formula (A4/provenance) | Derivable from gate formula |
| One criterion per thread per cycle | 0193 | Gate formula (A4/scope) | Derivable from gate formula |
| Harness error routes to EV, not HARD STOP | 0195/0213 | Non-derivable (names specific route) | Keep in Section 5 |
| exec_observed verbatim requirement | multiple | Non-derivable (format convention) | Keep in sentinel registry |

**Result**: ~10 of the 15 rule blocks added in ADRs 0199–0213 are type errors or sequence errors that the revised type definitions and sequence table absorb. ~5 are genuinely non-derivable and belong in Section 5.

---

## Consequences

**Expected reduction**: The prompt's `core` block should shrink from ~450 lines to approximately:
- Section 1: 2 sentences
- Section 2: 6 sentences (gate formula)
- Section 3: rung table (7 rows × 5 columns)
- Section 4: sequence table (7 rows × 4 columns)
- Section 5: ~6 compact named rules
- Sentinel registry: unchanged

**Escape-route closure durability**: Future escape routes that require new ADRs should be diagnosable as one of three kinds: (a) type definition gap → extend the type definition, (b) sequence table gap → extend the sequence table, (c) genuinely non-derivable → add to Section 5. If a rule doesn't fit any category, it is a signal the type definitions are still underspecified.

**Risk**: The sequence table's closed action sets are more restrictive than P4's current prose. P4 uses "only" language but does not enumerate every valid action. The sequence table must be validated against known-good transcripts to confirm it doesn't over-constrain.

**Implementation**: Rewrite `GROUND_PARTS_MINIMAL["core"]` directly. The Python helper functions `_rung_table()`, `_type_taxonomy_block()`, `_sentinel_block()` may be simplified or merged once the new structure is validated. Run `make axis-regenerate-apply` to propagate.
