# ADR-0105: Catalog Validation and Token Refinement

## Status
Accepted

## Context

Three cycles of prompt catalog evaluation (seeds 0001–0060, ADR-0085 evidence) have identified a stable set of defects that recur across cycles because no validation or documentation fixes were applied between cycles. The dominant pattern is a 25% output-exclusive conflict rate across all three cycles — directly traceable to the absence of build-time validation. Secondary patterns involve task-affinity mismatches, semantic token conflicts, and skill documentation pointing to non-existent commands.

This ADR consolidates all actionable findings from the three evaluation cycles into a set of discrete decisions. Each decision is independently implementable.

**Evaluation evidence base:**
- Cycle 1: seeds 0001–0020 (~15% output-exclusive conflicts, 35% excellent)
- Cycle 2: seeds 0021–0040 (25% output-exclusive conflicts, 55% excellent); introduced the output-exclusive concept
- Cycle 3: seeds 0041–0060 (25% output-exclusive conflicts, 65% excellent); confirmed visual and taxonomy as output-exclusive form tokens; confirmed codetour and gherkin task-affinity failures; confirmed `bar help llm` non-existence across all four skills

---

## Decision 1: Output-Exclusive Format Validation

### Problem

Tokens whose descriptions say "ONLY output format X" or "the complete output is X" are mutually exclusive: when two appear in the same prompt, the LLM receives contradictory instructions about what the entire response should look like. This conflict is unresolvable at inference time; it cannot be reconciled by the LLM without discarding one instruction entirely.

Three cycles of evaluation confirm a persistent 25% rate of such conflicts across seeds, and this rate has not declined because no validation was implemented between cycles.

**Confirmed output-exclusive tokens by axis:**

Form axis:
- `code` — mandates "code only, no surrounding prose"
- `html` — mandates "HTML only as the complete output"
- `shellscript` — mandates "shell script only as the complete output"
- `visual` — mandates "the main answer as an abstract visual or metaphorical layout" (see Decision 2 for proposed rephrasing)
- `taxonomy` — mandates "organized as a classification system" with definitional prose (see Decision 2 for proposed rephrasing)

Channel axis (already implicitly at-most-one):
- `gherkin` — mandates "only Gherkin format as the complete output"
- `diagram` — mandates "Mermaid diagram code only"
- `adr` — mandates structured ADR document format
- `codetour` — mandates VS Code CodeTour JSON format
- `presenterm` — mandates Presenterm slide deck format
- `sync` — mandates live session/workshop plan format

**Evidence from corpus:**
- Seed 0034 (cycle 2): adr + sync
- Seed 0039 (cycle 2): shellscript + presenterm
- Seed 0033 (cycle 2): visual + presenterm
- Seed 0047 (cycle 3): visual(form) + adr(channel)
- Seed 0057 (cycle 3): taxonomy(form) + diagram(channel)

### Decision

Implement validation in `bar build` and `bar shuffle` that errors when two output-exclusive tokens appear in the same prompt combination. The channel axis already enforces "at most one channel" implicitly; this validation extends the same concept to form tokens that are output-exclusive.

Form tokens that are output-exclusive (`code`, `html`, `shellscript`, and pending Decision 2, `visual` and `taxonomy`) should be tagged `output_exclusive: true` in the token definitions. The validation rule is: at most one output-exclusive token (form or channel combined) per prompt.

The error message should name the conflicting tokens and explain the mutual exclusion:

```
Error: output-exclusive conflict — 'visual' (form) and 'adr' (channel) both prescribe
the entire response format. Use at most one output-exclusive token per prompt.
```

---

## Decision 2: Rephrase `visual` and `taxonomy` Form Tokens

### Problem

`visual` and `taxonomy` are form tokens that appear in low-scoring seeds (0047, 0052, 0057) and whose descriptions imply they mandate the entire response structure. However, unlike `code` or `html` (which genuinely produce format-only output), `visual` and `taxonomy` describe *organizational approaches* that could plausibly be applied to a portion of the response alongside other content.

Rather than flagging them permanently as output-exclusive (which would prevent many legitimate uses and is addressed in Decision 1 for `code`/`html`/`shellscript`), these two tokens should be rephrased so they are composable: their descriptions should signal "where the subject lends itself to this approach" rather than "the entire response is this format."

This is the same compositional strategy used for `table` form ("when feasible"), which scores consistently well across all three cycles without conflicts.

### Decision

Rephrase the `visual` and `taxonomy` form token descriptions to be composable rather than mandatory:

**visual (revised description):**
> The response presents the main answer as an abstract visual or metaphorical layout with a short legend where the subject lends itself to visual representation, emphasising big-picture structure over dense prose.

**taxonomy (revised description):**
> The response organizes the main content as a classification system, type hierarchy, or category taxonomy, defining types, their relationships, and distinguishing attributes clearly, where the subject admits classification.

The key addition in both cases is the conditional clause ("where the subject lends itself to" / "where the subject admits classification"). This signals that these forms are applied when appropriate rather than overriding all other constraints, making them composable with channels and other form tokens.

After rephrasing, `visual` and `taxonomy` should **not** be tagged `output_exclusive: true`. Their new descriptions will naturally avoid the whole-response-override problem. If future evaluation cycles show they still conflict in practice, reconsider.

---

## Decision 3: Codetour and Gherkin Task Affinity

### Problem

`codetour` and `gherkin` channels are output-exclusive (they mandate complete output format) but their primary problem is not just format conflict — it is task-affinity mismatch. They produce outputs that are only meaningful in specific task contexts:

- `codetour` requires references to actual code files and line numbers; it is meaningless for non-code tasks
- `gherkin` is designed for behavior specification (Given/When/Then); it is inappropriate for tasks that do not map to system behaviors

**Evidence from corpus:**
- Seed 0054 (cycle 3): sim + codetour — scenario simulation cannot be expressed as a valid CodeTour JSON file
- Seed 0055 (cycle 3): diff + codetour — persuasive comparison cannot be expressed through VS Code navigation format
- Seed 0060 (cycle 3): sort + gherkin — categorization/ordering cannot be expressed as BDD test scenarios

All three seeds scored ≤3.2, and skills provide no guidance that would prevent these mismatches.

### Decision

Add task affinity guidance to `codetour` and `gherkin` channel descriptions:

**codetour (add to description):**
> Appropriate for tasks that produce or reference navigable code artifacts: `fix`, `make` when creating code, `show` when exposing code structure, `pull` when extracting from code. Not appropriate for non-code tasks such as `sim`, `sort`, `probe`, `diff` (without code subject), or `plan`.

**gherkin (add to description):**
> Appropriate for tasks that map naturally to scenario-based behavior specification: `check` for acceptance criteria, `plan` for BDD-style feature planning, `make` when defining system behavior. Not appropriate for tasks that don't involve system behavior: `sort`, `sim`, `probe`, `diff` (without behavioral subject).

Additionally, consider adding a soft warning in `bar build` / `bar shuffle` when codetour or gherkin is combined with a task outside their affinity set. This would be a warning (not an error) since the task might have a code or behavioral subject that makes the combination valid.

---

## Decision 4: `make` + `rewrite` Form Semantic Conflict

### Problem

`rewrite` form implies transforming existing content while preserving intent. `make` task implies creating new content that does not previously exist. These are semantically incompatible: a prompt cannot simultaneously require creating content from nothing and rewriting existing content.

**Evidence from corpus:**
- Seed 0053 (cycle 3): make + rewrite(form) + plain — scored 3.0
- Seed 0055 (cycle 3): diff + rewrite(form) + codetour — scored 2.4 (rewrite/diff conflict among multiple conflicts)

This pattern was not observed in cycles 1 or 2, suggesting `rewrite` is a newer form token whose semantic boundary with tasks has not been documented.

### Decision

Add a compatibility note to the `rewrite` form token description:

**rewrite (add to description):**
> Best paired with `fix`, `pull`, `diff`, or `show` tasks that supply existing content to transform. Pairing with `make` is semantically incoherent: `make` implies creating from nothing while `rewrite` implies transforming existing content.

Consider adding `make` + `rewrite(form)` to the validation rules as a soft conflict (warning, not error) since there may be edge cases where a user intends "create something that functions as a rewrite of a given document" — an unusual but not impossible scenario.

---

## Decision 5: `bar help llm` Token Selection Heuristics Contains Stale Content

### Problem

`bar help llm` exists and the skills are correct to reference it — the § "Usage Patterns by Task Type", § "Token Selection Heuristics", and § "Composition Rules" sections all exist. However, the **content** of the Token Selection Heuristics section is significantly out of date.

**§ Choosing Method** references many tokens that do not exist or were deprecated:
- `compare`, `tradeoff` — do not exist as method tokens
- `constraints` — deprecated per ADR-0104 (removed from methods)
- `structure` — does not exist (this is a scope concept, not a method)
- `sequence` — does not exist
- `impacts`, `diverge`, `survey` — do not exist
- `failure`, `stress`, `vulnerabilities` — do not exist
- `variants`, `options` — form tokens, not method tokens

**§ Choosing Form** references non-existent tokens:
- `matrix`, `tasks`, `options`, `log` — do not exist as form tokens
- `adr` is a channel token, not a form token

**§ Choosing Scope** is missing `assume`, `motifs`, and `stable` — all added in ADR-0104.

The phantom tokens in the heuristics mean that a user following skill guidance to consult § "Choosing Method" would be directed to use tokens that `bar build` will reject with `error: unrecognized token`.

This was the primary source of the 2.9/5 mean discoverability score in cycle 3's Phase 2b evaluation — not the command's existence, which is correct.

### Decision

Regenerate or rewrite the Token Selection Heuristics section in `bar help llm` to use only tokens that exist in the current grammar. The corrected heuristics should:

- Remove all phantom/deprecated tokens from § Choosing Method
- Replace with real tokens drawn from the actual method axis (see `bar help tokens method`)
- Add `assume`, `motifs`, `stable` to § Choosing Scope
- Correct § Choosing Form to use only real form tokens
- Ensure category groupings reflect the actual ADR-0104 token set

---

## Decision 6: `bar help llm` Composition Rules Section is Empty

### Problem

`bar help llm` includes a § "Composition Rules" section with an § "Incompatibilities" subsection. This subsection exists but contains no content — the heading "Certain token combinations are not allowed:" is followed immediately by the next section with no entries listed.

This is where output-exclusive conflict rules, task-affinity warnings, and semantic conflict notes should appear. The section is structurally present but functionally empty.

Skills (bar-autopilot, bar-manual, bar-workflow, bar-suggest) correctly direct users to consult § "Composition Rules" for valid combinations. A user who follows this guidance and reads the section will find nothing, with no indication that conflicts exist.

This gap was confirmed in the Phase 2c evaluation: Composition Guidance scored 1/5 and Output-Exclusive Concept Coverage scored 1/5 (overall mean: 2.6/5).

### Decision

Populate § "Incompatibilities" in `bar help llm` with documented conflict rules, drawing from findings across evaluation cycles 1–3:

**Output-exclusive conflicts:**
> Some tokens mandate the entire response format. At most one output-exclusive token (form or channel) may appear per prompt. Output-exclusive form tokens: `code`, `html`, `shellscript`. All channel tokens are output-exclusive. Combining two output-exclusive tokens produces contradictory instructions the LLM cannot reconcile.

**Task-affinity restrictions:**
> `codetour` channel: appropriate for tasks producing navigable code artifacts (`fix`, `make` with code, `show` with code structure). Not appropriate for `sim`, `sort`, `probe`, `diff` without code subject.
> `gherkin` channel: appropriate for tasks mapping to scenario-based behavior specification (`check`, `plan` with BDD context, `make` with behavior definition). Not appropriate for `sort`, `sim`, `probe`.

**Semantic conflicts:**
> `rewrite` form implies existing content to transform. Pairing with `make` (creates new content) is semantically incoherent.

This section also serves as the long-term home for future conflict rules as the catalog evolves.

---

## Decision 7: `bar help llm` Scope Heuristics Missing ADR-0104 Tokens

### Problem

ADR-0104 added four new scope tokens: `assume`, `motifs`, `stable`, and `view`. The § "Choosing Scope" section in `bar help llm` Token Selection Heuristics includes `view` but is missing `assume`, `motifs`, and `stable`.

These three tokens appeared in high-scoring seeds in cycle 3:
- `fail` and `good` (both present in heuristics) contributed to seeds 0056 and 0058 scoring 5.0
- `assume`, `motifs`, `stable` would similarly drive high-quality prompts if discoverable

Current § Choosing Scope entries: `thing`, `struct`, `time`, `mean`, `act`, `good`, `fail`, `view`.

Missing: `assume`, `motifs`, `stable`.

### Decision

Add the three missing tokens to § "Choosing Scope" in `bar help llm`:

- **Premises/preconditions** → `assume`
- **Recurring patterns/themes** → `motifs`
- **Invariants/persistent states** → `stable`

This update is low-cost (three lines) and should be combined with Decision 5 (heuristics rewrite) since both affect the same section.

---

## Consequences

### Positive

- **Validation eliminates 25% defect rate:** Decision 1 (output-exclusive validation in `bar build` / `bar shuffle`) directly addresses the primary defect class that persisted across all three evaluation cycles. Expected cycle 4 output-exclusive conflict rate: ≤5%.

- **Token descriptions become self-documenting:** Decisions 2, 3, and 4 add task-affinity and semantic-conflict guidance directly to token descriptions, making misuse visible at token selection time rather than requiring external documentation.

- **`bar help llm` heuristics become trustworthy:** Decision 5 removes phantom tokens from § Choosing Method and § Choosing Form that currently cause `error: unrecognized token` when followed literally, raising mean skill discoverability from 2.9/5 toward ≥4.0.

- **Composition rules become populated:** Decision 6 fills the empty § Incompatibilities section, giving users the conflict guidance the section promises but currently withholds.

- **Scope token coverage complete:** Decision 7 adds `assume`, `motifs`, `stable` to § Choosing Scope, making all 11 current scope tokens discoverable via heuristics.

### Negative / Tradeoffs

- **Flexibility reduced:** Output-exclusive validation (Decision 1) will error on combinations that were previously permitted. Some combinations that a creative user might have found productive (e.g., using visual form alongside an ADR channel for a mixed-format response) will be blocked. The tradeoff is acceptable given the 25% defect rate.

- **Implementation work required:** Decisions 1, 5, and 7 require binary and/or skill implementation work. Decisions 2, 3, 4, and 6 require documentation-only changes and are lower cost.

- **Decision 2 rephrasing requires evaluation:** The revised `visual` and `taxonomy` descriptions will need a follow-up evaluation cycle to confirm they perform as composable tokens without introducing new ambiguities. A cycle 4 evaluation should track whether these tokens still produce conflicts under the new descriptions.

---

## Follow-up Work

### Decision 1: Output-Exclusive Validation
**Files to change:**
- `bar` binary: add `output_exclusive: true` tag to form tokens (`code`, `html`, `shellscript`) in token definitions
- `bar` binary: add validation rule in `bar build` / `bar shuffle` that rejects combinations with two or more output-exclusive tokens (form or channel)
- Token definition file (wherever form tokens are defined): tag code, html, shellscript as output_exclusive
- Error message copy: write the conflict error message as specified in Decision 1

### Decision 2: Rephrase `visual` and `taxonomy`
**Files to change:**
- Token definition file: update `visual` form token description to add conditional clause ("where the subject lends itself to visual representation")
- Token definition file: update `taxonomy` form token description to add conditional clause ("where the subject admits classification")
- Do NOT tag these as output_exclusive after rephrasing

### Decision 3: Codetour and Gherkin Task Affinity
**Files to change:**
- Token definition file: update `codetour` channel description to add task-affinity guidance
- Token definition file: update `gherkin` channel description to add task-affinity guidance
- `bar` binary (optional): add soft warning when codetour or gherkin is combined with an out-of-affinity task

### Decision 4: `make` + `rewrite` Semantic Conflict
**Files to change:**
- Token definition file: update `rewrite` form token description to add note about task compatibility
- `bar` binary (optional): add soft warning when make + rewrite(form) appear together

### Decision 5: Fix `bar help llm` Token Selection Heuristics
**Files to change:**
- `internal/barcli/help_llm.go` (or wherever the heuristics content is generated): rewrite § Choosing Method to use only real method tokens; rewrite § Choosing Form to use only real form tokens; remove deprecated `constraints` token reference
- Verify against `bar help tokens method` and `bar help tokens form` output after change

### Decision 6: Populate `bar help llm` § Composition Rules § Incompatibilities
**Files to change:**
- `internal/barcli/help_llm.go`: add output-exclusive conflict rules, codetour/gherkin task-affinity rules, and rewrite+make semantic conflict to § Incompatibilities

### Decision 7: Add Missing Scope Tokens to `bar help llm` § Choosing Scope
**Files to change:**
- `internal/barcli/help_llm.go`: add `assume`, `motifs`, `stable` entries to § Choosing Scope in Token Selection Heuristics

### Ongoing: Test Coverage for `bar help llm` Examples
**Files to create/change:**
- Add a test that validates all tokens mentioned in `bar help llm` heuristics exist in the current grammar, preventing phantom token regression
- Test should run `bar help tokens` and cross-reference every token name cited in § Token Selection Heuristics
