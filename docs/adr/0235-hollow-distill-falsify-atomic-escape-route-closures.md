# ADR-0235: Hollow/Distill/Falsify/Atomic Escape Route Closures and Root Criterion Encoding

**Status**: Accepted
**Date**: 2026-05-06

---

## Context

The `hollow` and `distill` method tokens were developed inductively — by observing and closing escape routes in `falsify`, `atomic`, `gate`, and `ground` — rather than being derived from an explicit principle. This created two structural problems:

1. **Inductive gaps**: each escape route required manual discovery; there was no derivation basis to predict gaps in advance.
2. **Self-certification**: `hollow` and `distill` were themselves subject to the same escape routes they were designed to close, but were not applied to their own definitions.

During a session on 2026-05-06, a systematic audit using `probe hollow`, `probe root`, `probe collapse`, and `make mint` was conducted. The audit closed ten escape routes across `falsify` and `atomic`, identified two structural gaps in `hollow` and `distill` themselves, and derived the root criterion that both tokens share.

---

## Decisions

### 1. Falsify — ten escape routes closed

Each gap was identified via `hollow`, the fix was proposed via `distill`, and changes were applied to `lib/axisConfig.py` with grammar regeneration.

**1a. Slower check consequence implicit**
*Gap*: "the slower check is not derived" left the consequence unstated — a model could write the label and continue naming a candidate.
*Fix*: added "the candidate check must not be named — choose a different candidate for which a nameable test exists."

**1b. Slower check self-refutation**
*Gap*: a model could name a test and in the same description state it does not cover the governed behavior (e.g., "covers ordering but not work_dir resolution"). The "must be capable" requirement did not invalidate self-refuting descriptions.
*Fix*: descriptions containing qualifying phrases ("but not [behavior]", "does not cover", "cannot distinguish") explicitly invalidate the nomination.

**1c. Slower check dismissal by reasoning**
*Gap*: a model could name a test, then dismiss it as incapable via reasoning rather than by citing a prior execution result.
*Fix*: a claim of incapability must be grounded in a prior execution result showing the test passing while the behavior was absent; a reasoned claim without such a quote is invalid and the slower check stands as derived.

**1d. Insufficient check irrelevance**
*Gap*: any passing test satisfied the "insufficient check" requirement, including tests that did not exercise the same triggering event as the candidate (irrelevant vs. insufficient).
*Fix*: the insufficient check must exercise the same triggering event as the candidate at coarser resolution; a check that does not share the triggering event is classified as irrelevant, not insufficient, and must not be named.

**1e. Insufficient check quote as trailing condition**
*Gap*: the quote requirement was a trailing validity condition — an entry could close without a quote and appear structurally complete.
*Fix*: "this entry is not complete until that quote appears" repositions the quote as a structural gate inside the entry.

**1f. Insufficient check quote from wrong source**
*Gap*: "prior run result" was satisfied by any result in the transcript, not specifically the named check's result.
*Fix*: the quoted output must be from a prior execution of the named insufficient check specifically; a result from a different check is invalid.

**1g. Insufficient check quote unverifiable by inspection**
*Gap*: a model could attribute any quoted result to the named check, since attribution was in prose the model controls.
*Fix*: the quoted text must contain the check's name, command, or a test identifier from it, so the source is verifiable by inspection rather than by trusting attribution.

**1h. Atomic smaller-change quote insufficiency by inference**
*Gap*: the insufficiency quote could be satisfied by a module-level FAIL (e.g., "Cannot find module") from which behavioral insufficiency was inferred rather than observed.
*Fix*: the quote must name a behavioral assertion — a test name or assertion message that fires on the governed behavior — not merely a module-level or import-level error.

**1i. Bar workflow sequence laziness**
*Gap*: the Named Sequences section in `bar help llm` listed steps by role only, with no requirement to select additional tokens per step. A model could run a sequence step with only the sequence's seed token.
*Fix*: added to `help llm`: "A sequence defines step roles and order, not the complete token set. For each step, select at least one additional token (completeness, scope, method, or form)."

**1j. Bar workflow sequence fit check**
*Gap*: no guidance on re-evaluating sequence fit between steps — a model could continue mechanically after task drift.
*Fix*: added: "Before each step after the first, emit a one-line fit check." The required string pattern makes fit evaluation transcript-visible.

---

### 2. Hollow — self-certification gap

**Gap**: hollow requires "derive the mechanism of indistinguishability before giving any example," but the mechanism derivation is itself model-evaluated prose. A mechanism derivation and a mechanism assertion produce identical transcripts.

**Decision**: hollow's definition will be updated to require that the root criterion be stated as a separately quotable claim before deriving each mechanism. The mechanism must follow from the stated criterion, not from the model's understanding of it.

**Root criterion** (to be embedded in hollow):
> "A clause is valid only if it names, within its own text, the observable that distinguishes compliance from non-compliance without requiring the evaluator to assess the model's intent."

**Status**: decided; implementation pending.

---

### 3. Distill — removed; constraints absorbed into hollow

**Gap**: distill rewrites clauses but does not require running hollow on the rewrite. Closure is self-declared.

**Structural finding** (from `probe root` and `probe collapse`):
Hollow and distill are not two independent tokens — they are two phases of one operation:
- audit: find clauses violating the root criterion
- repair: rewrite clauses to satisfy the root criterion

Distill's repair constraints (observable named before claiming closure, length constraint, gap-named-before-clause, allow-list/post-condition) belong in hollow's definition as constraints on any rewrite hollow governs — not in a separate token. Encoding them as token interactions would violate the principle that tokens do not specify behavior conditional on other tokens.

**Decision**: distill is removed. Its repair constraints are folded into hollow's definition as unconditional requirements on any rewrite hollow produces or governs. The workflow previously expressed as `hollow distill` is now expressed as `fix hollow`. Additional phases — `check hollow` (verify a rewrite satisfies the root) and `make hollow` (generate a new clause from scratch) — are naturally expressible via the task axis.

---

### 4. Surface token — rejected

**Proposed**: a `surface` token to make governing criteria explicit before evaluation, closing hollow's self-certification gap.

**Rejected**: the self-certification gap is a deficiency in hollow's own definition, not a missing capability requiring a new token. Encoding criterion-statement into hollow directly closes the gap without adding a new token. Any other token with a self-certification gap should fix its own definition, not rely on `surface` from outside.

---

## Consequences

**Positive**:
- Ten concrete escape routes in `falsify`/`atomic` are closed with specific observable properties named for each.
- The root criterion is now encoded in hollow's definition; hollow and distill no longer maintain independent definitions of the same criterion.
- `fix hollow`, `check hollow`, and `make hollow` are naturally expressible via the task axis with no additional tokens.
- Removing distill eliminates the risk of the two definitions drifting independently.

**Negative / risks**:
- Hollow's updated definition (requiring criterion statement before each mechanism) adds overhead to hollow audits; a model auditing a long instruction must state the criterion before each finding.
- The ten falsify fixes make the falsify derivation block substantially longer and more demanding; there is a tradeoff between escape-route coverage and cognitive load per derivation.

**Open**:
- Whether `check hollow` should be added to the bar-workflow skill as a recommended post-`fix hollow` step.
