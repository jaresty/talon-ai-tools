# ADR-0177: Ground Prompt Collapse and Behavioral Rule Addition

**Status:** Accepted
**Date:** 2026-03-23

---

## Context

A SWE agent run executing the ground protocol revealed two systematic behavioral failures:

**Failure 1 — Prose attractor (task comprehension drift)**
The prose rung was filled with task comprehension ("The user story describes building an attributes management landing screen...") rather than a natural language description of intent and constraints. The prose rung gate ("I declared") does not require a tool call, so an agent can satisfy it by emitting prose-shaped text regardless of content. This created behavioral predicates in the prose that were never directly covered by any gap cycle, allowing `✅ Thread N complete` to be emitted with unresolved behavioral gaps.

**Failure 2 — ORB attractor (test pass substitution)**
The observed running behavior (ORB) rung was never fired with a distinct label. A test suite pass was used in place of direct implementation invocation. The ground spec did not explicitly state that test-suite output is a different artifact type from observed-running-behavior output, leaving the gate ambiguous: a passing test *implies* the implementation works, and an agent can satisfy itself with that inference.

**Root cause (both failures):** The ground spec had two implicit constraints that were not stated as explicit gates:
1. Tool output at a rung must match that rung's artifact type.
2. Before `✅ Thread N complete`, every behavioral predicate declared in the prose must have a directly-named gap cycle.

These constraints existed in spirit (the ORB rung definition says "invoke the artifact directly") but were not stated as explicit prohibitions in the positions where agents apply them.

---

## Decision

### 1. Add rung-type constraint (surgical insertion)

Insert immediately after the opening axiom sentence:

> The tool call(s) at a rung must produce output whose artifact type matches that rung's definition — output from a different rung's artifact type does not satisfy the gate regardless of what it implies (running the test suite at the observed running behavior rung produces validation-run-observation-type output, not observed-running-behavior-type output, and does not satisfy that gate).

This closes the ORB-via-test escape route by naming it explicitly.

### 2. Add ORB all-criteria rule (surgical insertion before Thread N complete)

Insert before the `✅ Thread N complete may not be emitted unless` sentence:

> For each sentence in the prose that contains a behavioral predicate (fetches, requires, displays, filters, renders, validates, authenticates, loads, saves, or any similar action verb), check that a completed gap cycle exists whose criterion directly names that behavior — implicit or incidental coverage does not satisfy this check; if any behavioral sentence has no directly-named cycle, emit a new 🔴 Gap: for it before emitting ✅ Thread N complete.

This closes the prose-gap escape route by requiring exhaustive criterion coverage before thread completion.

### 3. Establish test regression principle

Tests for the ground prompt should detect **behavioral regressions**, not lock in specific wording. A test that checks for a phrase like `"The prose rung"` is testing that the spec was not accidentally deleted; it is not testing behavior. A test that checks for `"artifact type"` is testing that the rung-type constraint is present.

Going forward:
- Tests check for the presence of behavioral markers (key phrases that would be absent only if the rule were deleted)
- Tests do not assert exact wording, sentence structure, or character counts that would break on legitimate rephrasing
- The character count test tracks growth (prompt must not grow unboundedly with each addition) but uses a sliding baseline: `ORIGINAL_CHARS + N` where N reflects the expected size of deliberate additions

### 4. Collapse the prompt text

The minimal ground prompt (`GROUND_PARTS_MINIMAL["core"]`) is currently ~14745 chars after the two additions. The same constraint is typically stated in three forms: axiom ("a rung is satisfied when..."), prohibition ("X does not satisfy..."), and example ("running tests produces VRO-type output..."). Collapse retains the canonical form and removes the restatements.

**Redundancy clusters identified:**

| Cluster | Current statements | Collapse target |
|---|---|---|
| Rung satisfaction axiom + artifact type | 4 statements (axiom, tool-type constraint, VRO-test example, OBS section restatement) | 2: axiom + type constraint with one example |
| ORB output type | 4 statements ("not the test suite", "test pass/fail not valid OBS", "tests are never a valid consumer", rung-type constraint) | 1: rung-type constraint at axiom covers all |
| Implementation gate | 3 statements (🟢 licenses first edit, 🟢 does not complete thread, next action after 🟢 must be tool call) | 1 compound sentence |
| Validation rung prohibitions | ~8 prohibition sentences (no implementation notes, no planning prose, no file reads, no "let me fix"...) | 1: "only validation artifacts may be produced; no other content before V complete" |
| Criterion atomicity | 3 statements (one criterion, "and" check, split instruction) | 1 sentence with the "and" check as the operative test |
| Pre-existing artifact check | 3 sentences (read the path, emit result, pre-existing must be confirmed failing) | 1: "before V-complete, confirm path contents via tool call; if pre-existing, confirm failing" |
| Vacuity check | 3 sentences (static vs runtime, perturb, restore if red) | 1 conditional: "if static, run before edit; if runtime, perturb; red-then-restore required" |
| Implicit-coverage prohibition | appears twice ("implicit or incidental coverage does not satisfy this check") | 1 instance at prose predicate check; remove from ORB all-criteria |
| Prose re-emission | 3 statements (every cycle, upward returns, criterion must derive from re-emitted prose) | 1 |
| Gap phrasing rules | 3 statements (currently-false, no artifact naming, manifest exhausted condition) | 1 compound |
| Upward return taxonomy | verbose; repeats "if X return to Y" three times | 1 compact table-form sentence |

**Target:** ~7500 chars (≈49% reduction). Each collapsed rule retains its behavioral marker phrase so existing behavioral tests continue to pass.

**Collapse approach:**
1. For each cluster, identify the single canonical sentence that an agent would apply at the decision point
2. Remove all restatements of that sentence that appear elsewhere in the text
3. Retain examples only where the rule contains a term that could be ambiguous without one (the VRO-type/ORB-type example is necessary; the "useFoo hook calls /bar" criterion example is necessary; most prohibition lists are not)
4. Update tests in parallel: any test checking a phrase that disappears in the collapse must be replaced with a test checking the canonical marker phrase

**Test update plan:**

Tests in `test_ground_prompt_minimal.py` that assert specific phrases will need updating when those phrases are rephrased during collapse. The replacement test for each should check:
- The behavioral rule is present (a key phrase that is present iff the rule exists)
- The character count ceiling is updated to `≤ 7500 + 500` buffer

Tests in `test_ground_rewrite_thread1.py` check behavioral markers (`"artifact type"`, `"each criterion"`) and will not need updating — these are the canonical marker phrases.

---

## Consequences

**Immediate:**
- `GROUND_PARTS_MINIMAL["core"]` grows by ~709 chars (from 14036 to ~14745)
- The char limit test in `test_ground_prompt_minimal.py` (`test_total_chars_under_3000`, actual limit 14500) will fail and must be updated to reflect the new baseline
- Two new behavioral tests added in `_tests/test_ground_rewrite_thread1.py`:
  - `test_rung_type_constraint_present` — checks `"artifact type"` is present
  - `test_orb_all_criteria_present` — checks `"each criterion"` or `"every criterion"` is present
  - `test_prompt_does_not_grow_beyond_additions` — checks `len(prompt) < ORIGINAL_CHARS + 800`

**Completed (this ADR):**
- Redundancy removal pass: 11 clusters collapsed, 14745 → 12994 chars (−1751, ~12% reduction)
- 15 tests updated from exact-phrase assertions to behavioral-marker assertions
- 5 new tests added (2 rung-type constraint, 2 ORB all-criteria, 1 growth guard)

**Next step — deeper collapse (~12994 → ~7500 chars):**
The redundancy removal pass eliminated restatements within clusters. The remaining ~5500 chars require more aggressive restructuring: collapsing entire paragraphs by rewriting them at higher abstraction, not just removing duplicate sentences. This will break more tests and requires the same cluster-by-cluster approach with test rewrites in parallel. The key constraint: every behavioral rule must retain a canonical marker phrase that a test can assert.

**Deferred:**
- Apply equivalent rules to `GROUND_PARTS` (the full 4-section dict) once the minimal version is validated

**Non-goals:**
- Changing `GROUND_PARTS` code structure (sections, keys, build function branching) — code structure is not the target
- Changing the Python structure of `groundPrompt.py` itself

---

## Methodology

Analysis used bar methods:
- **Orbit**: Identified what shape agent behavior converges to — task comprehension prose and test-pass ORB are attractors because the spec allows them
- **Reify**: Made the implicit artifact-type constraint and all-criteria exhaustion constraint explicit as formal gate sentences
- **Mint**: Derived the minimal gate text from the behavioral failure — what is the shortest sentence that closes this escape route?
- **Collapse**: Identified that the existing spec restates the same rules ~3× each; the two new rules add text that could be recovered by removing redundant restatements elsewhere
