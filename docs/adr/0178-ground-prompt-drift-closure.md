# ADR-0178: Ground Prompt Drift Closure — Self-Attestation, Gate Sequencing, and Upstream Coverage

**Status:** Accepted
**Date:** 2026-03-24

---

## Fix Pattern Key

Each fix in this ADR is expressed using a three-field recipe notation:

```
ROOT    — the generative assumption that makes the fix load-bearing
COLLAPSE — the minimal canonical rule that subsumes all surface instances
ENTER   — how the fix attaches to existing structure without replacing it
```

A fix that cannot be expressed in all three fields is not structural — it is additional prose, and additional prose cannot close drift.

---

## Context

An orbit/drift analysis of the ground prompt (`groundPrompt.py`) was conducted across its four parts: `epistemological_protocol`, `sentinel_rules`, `rung_sequence_code`, and `reconciliation_and_completion`.

**Orbit findings** — the prompt converges on four attractors regardless of which part is consulted:
1. Tool-executed event as the only valid epistemic atom
2. The ladder is mandatory with zero complexity threshold
3. Upward correction as the primary repair mechanism
4. Behavioral gaps (not implementation decisions) as the unit of work

**Drift findings** — seven points where conclusions are treated as necessary but are not structurally enforced:

| # | Location | Drift description |
|---|---|---|
| D1 | `sentinel_rules` | Verbatim-ness is asserted but unverifiable — a model can truncate and label it verbatim |
| D2 | `sentinel_rules` | "Immediately before" is a proximity claim, not a gate-sequence rule — prose can appear between sentinel and invocation |
| D3 | `rung_sequence_code` | Behavioral vs structural criterion distinction requires semantic judgment — R2 audit is model-generated |
| D4 | `epistemological_protocol` | Downward-sufficiency is a semantic property with no executable test — models assert it without verifying |
| D5 | `reconciliation_and_completion` | Behavioral sentence enumeration at `Thread N complete` is model-generated — undercounting is undetectable |
| D6 | `sentinel_rules` | Carry-forward is a named licensed exception — content accuracy is unverifiable |
| D7 | `rung_sequence_code` | New-file prohibition at OBR is enforced only by characterization — file creation can be relabeled as invocation |

**Root cause analysis** — the seven drift points reduce to three root failure modes:

| Root failure | Covers |
|---|---|
| Self-attestation of output properties | D1, D4 |
| Temporal/positional rules without structural anchors | D2, D7 |
| Model-generated coverage claims produced retrospectively | D3, D5, D6 |

---

## Decision

### Fix A — Replace self-attestation with structural derivability

```
ROOT    The protocol already prohibits satisfying gates with anticipated content (the
        prospective-commitment principle). The same logic applies to content properties:
        asserting "this is verbatim" or "this is downward-sufficient" is the same
        epistemological error the sentinel was designed to prevent.

COLLAPSE Any property claim about a produced artifact that requires the model to
         introspect the artifact's internal adequacy is invalid as a gate-opener.
         Gate-opening claims must be derivable from named structural features.

ENTER   Attach to the existing sentinel_rules prospective-commitment paragraph.
        Add after "the sentinel's purpose is not accuracy but prior-to-interpretation
        capture":
```

**D1 insertion** (into `sentinel_rules`, after the prospective-commitment paragraph):

> The triple-backtick block constitutes the sentinel body. No content may appear inside the block that was not produced by the tool call. Elision markers (`...`, `[truncated]`, `[output continues]`, `[remaining output omitted]`), reformatted text, and paraphrase are prohibited inside the block. If tool output is too long to include in full, the block must end at a natural output boundary with the last character the tool produced — no editorial closing.

**D4 insertion** (into `epistemological_protocol`, after the downward-sufficiency definition in Primitive 2):

> Before closing a rung artifact, identify every decision the next rung must make that is not fully determined by this artifact's explicit content. State each such decision as an open constraint in the artifact. An artifact with no stated open constraints claims to be fully downward-sufficient; an artifact with stated open constraints is partially downward-sufficient and gates descent to the extent those constraints are resolved at the next rung.

---

### Fix B — Replace temporal/positional rules with action-sequence gate rules

```
ROOT    The protocol already has a strong pattern for gate-sequence rules: the 🟢
        sentinel is defined as "must appear before any tool call that creates or
        modifies an implementation source file" — a next-action constraint, not a
        proximity claim. "Immediately before" and "no new files" are weaker forms
        of the same constraint type.

COLLAPSE A positional rule is only enforceable when: the gated action is a named
         class AND the gate is a named sentinel AND the only valid next action after
         the sentinel is the gated action.

ENTER   Retire "immediately before" in sentinel_rules. Replace with the same
        next-action pattern used by 🟢. For OBR, attach to the existing
        "no new files may be created at this rung" sentence.
```

**D2 replacement** (in `sentinel_rules`, replacing all uses of "immediately before"):

> `🔴 Execution observed:` gates the tool invocation — the only valid next action after emitting this sentinel is the tool call it names. Any response content between this sentinel and the tool call converts the sentinel to retroactive regardless of sequence. A sentinel-to-tool sequence with intervening content must be treated as if the sentinel was not emitted; re-emit and re-run.

**D7 insertion** (into `rung_sequence_code`, after "no new files may be created at this rung" in the OBR section):

> Before any tool call touching the filesystem at this rung, emit a provenance statement: "Invoking [artifact] produced at [rung name] in this thread." The cited rung must be quotable from this conversation. A tool call with no citable provenance is creating a new artifact regardless of characterization and is prohibited at this rung.

---

### Fix C — Move coverage claims upstream to production time

```
ROOT    A coverage claim C about artifact A is structurally grounded iff C is
        derivable from A's content at the moment A is closed. Claims produced
        after A is used downstream are retrospective and cannot be verified
        against A's state at closure time.

COLLAPSE Move all coverage claims to co-production: emit the claim at the same
         rung as the artifact it covers, not at a downstream rung that consumes it.

ENTER   At criteria rung: add inline falsifying condition as required format.
        At prose rung: add inline thread markers as required format.
        At carry-forward: strengthen existing format to require verbatim test-name
        quotation from prior 🔴 Execution observed output.
```

**D3 replacement** (in `rung_sequence_code`, at the criteria rung definition):

> Each criterion must be written in two parts: (a) observable behavior — what a non-technical observer of the running system would see; (b) falsifying condition — what system behavior would cause this criterion to fail. A criterion without an explicit falsifying condition is incomplete at time of production and must not be advanced from. If the falsifying condition requires knowledge of implementation internals, the criterion is structural, not behavioral, and must be rewritten.

**D5 replacement** (in `rung_sequence_code`, at the prose rung definition):

> Each sentence in the prose that contains a behavioral predicate (fetches, requires, displays, filters, renders, validates, authenticates, loads, saves, or any similar action verb attributing behavior to the system) must be followed inline by a bracketed thread marker: `[T: gap-name]`. These markers become the authoritative enumeration for the manifest and for the Thread N complete check. The manifest thread list must correspond 1:1 with the inline thread markers in prose. The Thread N complete check verifies thread markers, not untagged sentences.

**D6 strengthening** (in `sentinel_rules`, replacing the carry-forward format sentence):

> Carry-forward format: `Carry-forward: prior failure [verbatim test name as it appeared in 🔴 Execution observed:] covers current test [verbatim test name as written in the artifact]`. One row per current test. Each prior-failure name must be quotable verbatim from a `🔴 Execution observed:` sentinel in this conversation. Any current test whose name does not appear in a carry-forward row is unconditionally uncovered and triggers the vacuous-green check.

---

## Implementation notes

The seven insertions target five locations in `GROUND_PARTS` and the corresponding locations in `GROUND_PARTS_MINIMAL`:

| Fix | Dict key | Position |
|---|---|---|
| D1 | `sentinel_rules` | After prospective-commitment paragraph |
| D2 | `sentinel_rules` | Replace "immediately before" occurrences (all 3) |
| D3 | `rung_sequence_code` | Replace criteria rung format sentence |
| D4 | `epistemological_protocol` | After Primitive 2 downward-sufficiency clause |
| D5 | `rung_sequence_code` | Replace prose rung behavioral-predicate sentence |
| D6 | `sentinel_rules` | Replace carry-forward format sentence |
| D7 | `rung_sequence_code` | After OBR "no new files" sentence |

D2 retires the phrase "immediately before" from `sentinel_rules`. Verify no test asserts this phrase.

---

## Consequences

**Structural:**
- The three root fixes are load-bearing: they derive from the protocol's own epistemic principles rather than adding new axioms. Any model that accepts the prospective-commitment principle (Fix A), the 🟢 gate-sequence pattern (Fix B), or the existing coverage-claim structure (Fix C) cannot reject these fixes without also rejecting the principle it already accepts.
- Fix C (D5 specifically) changes the manifest-generation model: manifests are now derived from inline prose markers rather than independently declared. This is a structural dependency change — prose must precede manifest declaration with markers present.

**Prompt size:**
- `GROUND_PARTS` grew from 31000 to 33411 chars (+2411). Baselines updated in:
  - `test_ground_prompt_redundancy_audit.py`: `POST_THREAD2_BASELINE` 31000 → 34000
  - `test_ground_prompt_rung_table.py`: `BASELINE_RUNG_SEQUENCE_CODE_CHARS` 11600 → 13000

**Completed (this ADR):**
- All 7 insertions applied to `GROUND_PARTS` in `lib/groundPrompt.py`
- `_tests/test_ground_adr0178.py` created with 8 behavioral-marker tests (all passing)
- Two pre-existing tests required text adjustments to keep behavioral markers within their context windows:
  - `test_sentinel_is_prospective_commitment_not_label`: fixed by adding `"interpreted"` to D2 gate sentence
  - `test_criteria_rung_falsifiability_is_a_gate`: fixed by moving `"before advancing"` and `"behavioral"` within the 600-char criteria window
- D2 note: `"immediately before"` confirmed absent from `sentinel_rules`; existing tests did not assert that phrase
- 1609 tests pass, 0 fail

**Deferred:**
- Applying D1–D7 equivalents to `GROUND_PARTS_MINIMAL` (pending validation of `GROUND_PARTS` in live sessions)

**Non-goals:**
- Changing the four-part structure of `GROUND_PARTS` or the build function
- Applying these changes to `GROUND_PARTS_MINIMAL` until validated against `GROUND_PARTS`
- Fixing drift points not listed here (the analysis identified these seven as structurally closable; others may require axiom-level changes)

---

## Methodology

Analysis used bar methods:
- **Orbit**: Identified invariant attractor geometry across all four prompt parts — four structural attractors found
- **Drift**: Identified seven underenforced conclusions where model divergence is possible without formal rule violation
- **Enter**: Fixes join the existing protocol's own logic and redirect from within — no axiom replacements
- **Collapse**: Seven surface instances reduced to three root failure modes; fixes target roots
- **Mint**: Each fix constructed from a generative assumption explicit enough that the fix follows as a direct product

Bar command: `bar build fix thing enter collapse mint recipe fly-rog`
