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

## Decision 5: Bar Skills Reference `bar help llm` (Non-Existent)

### Problem

All four bar skills (bar-autopilot, bar-manual, bar-workflow, bar-suggest) reference `bar help llm` as the "preferred" command for discovering tokens and understanding composition rules. This command does not exist in the current bar binary.

The skills label `bar help tokens` as "legacy / older versions" — but `bar help tokens` is the only working command. The fiction inverts the actual state: the "preferred" path fails with command-not-found, the "legacy" path succeeds.

Additionally, skills reference sections that only exist in `bar help llm` (non-existent):
- § "Usage Patterns by Task Type"
- § "Choosing Method"
- § "Token Selection Heuristics"
- § "Composition Rules"

None of these sections exist in `bar help tokens`. Users following skills will encounter dead links to documentation that does not exist.

This was confirmed across all 20 seeds in cycle 3's Phase 2b evaluation. Mean discoverability score under current skills: 2.9/5.

### Decision

Choose one of the following two remediation paths:

**Path A (preferred):** Implement `bar help llm` as a richer version of `bar help tokens` that includes:
- The sections skills already reference (Usage Patterns by Task Type, Choosing Method, Token Selection Heuristics, Composition Rules)
- Output-exclusive conflict documentation
- Task-affinity guidance for codetour and gherkin
- Updated scope token coverage (assume, motifs, stable, view)

This path makes skills accurate and adds the composition guidance missing from `bar help tokens` (Decision 7 below).

**Path B (fallback):** Update all four skills to treat `bar help tokens` as the current command (removing "legacy" label) and remove all references to sections that don't exist. Acknowledge that composition guidance is not yet available in the reference tool.

Path B requires fewer implementation resources but leaves the composition guidance gap in place.

---

## Decision 6: Skills Missing Guidance for New Scope Tokens

### Problem

ADR-0104 added four new scope tokens: `assume`, `motifs`, `stable`, and `view`. None of the four bar skills have been updated to include these tokens in their guidance.

In cycle 3, four of the five scope tokens that appear in seeds are ADR-0104 additions: `thing`, `mean`, `fail`, `good`, `time`, `view` — of which `view`, `mean`, `fail`, `good`, `time` are new or recently added. The mean discoverability for seeds with new scope tokens was 2.3/5 (see Phase 2b).

A user following current skills would have no path to discover:
- `view` (seed 0047): stakeholder or role perspective scope
- `mean` (seed 0054): interpretation or framing scope
- `fail` (seed 0058): failure-mode and breakdown scope
- `good` (seed 0056): quality criteria scope
- `time` (seed 0053): temporal scope

These scope tokens contributed to some of the highest-quality prompts in the corpus (seeds 0056 and 0058 both scored 5.0) and their absence from skills guidance is a significant discoverability gap.

### Decision

Update all four skills to include the new scope tokens with brief selection heuristics. At minimum, each skill should include:

- `assume` — use when the response should surface and interrogate preconditions and assumptions
- `motifs` — use when the response should identify recurring patterns and structural themes
- `stable` — use when the response should focus on invariants and what does not change
- `view` — use when the response should take a specific stakeholder or role perspective
- Updated entries for `time`, `fail`, `good`, `mean`, `thing` if not already present

This update should be applied in tandem with Decision 5 (fixing the `bar help llm` reference) since both require touching all four skill files.

---

## Decision 7: No Composition Guidance in `bar help tokens`

### Problem

Skills reference composition-guidance sections (§ "Composition Rules", § "Token Selection Heuristics") that only exist in `bar help llm` (non-existent). `bar help tokens` has no guidance on:

- Incompatible combinations (output-exclusive conflicts)
- Token interaction (how form and channel tokens relate)
- Task affinity (which channels work with which tasks)
- Positive patterns (combinations that work well together)

This gap was confirmed by the Phase 2c evaluation, where `bar help tokens` scored 1/5 on both output-exclusive concept coverage and composition guidance (overall mean: 2.6/5).

For the 5–8 token combinations characteristic of this corpus, users have the ingredients but no recipe and no warning labels.

### Decision

Either implement `bar help llm` (Decision 5, Path A) or add a short composition section to `bar help tokens` output. The composition section should include:

**Output-exclusive conflicts:**
> Some tokens mandate the complete output format. At most one such token (form or channel) may appear per prompt. Output-exclusive form tokens: code, html, shellscript. All channel tokens are output-exclusive. Combining two output-exclusive tokens produces contradictory instructions.

**Task affinity:**
> codetour and gherkin channels have task affinity restrictions. See `bar help tokens codetour` and `bar help tokens gherkin` for details.

**Semantic conflicts:**
> rewrite(form) implies existing content to transform. Combining with make(task) is semantically incoherent.

**Positive composition guidance:**
> For strong combination patterns, see [link or reference to documentation].

This section need not be exhaustive. Even a short "known conflicts" notice at the end of `bar help tokens` output would raise the composition guidance score from 1/5 to 3/5.

---

## Consequences

### Positive

- **Validation eliminates 25% defect rate:** Decision 1 (output-exclusive validation in `bar build` / `bar shuffle`) directly addresses the primary defect class that persisted across all three evaluation cycles. Expected cycle 4 output-exclusive conflict rate: ≤5%.

- **Token descriptions become self-documenting:** Decisions 2, 3, and 4 add task-affinity and semantic-conflict guidance directly to token descriptions, making misuse visible at token selection time rather than requiring external documentation.

- **Skills become reliable:** Decisions 5 and 6 eliminate the non-existent command reference and add new scope token guidance, raising mean skill discoverability from 2.9/5 toward ≥4.0.

- **Reference tool becomes composition-capable:** Decision 7 adds the meta-guidance layer that `bar help tokens` currently lacks, reducing dependence on implicit knowledge for multi-token prompt construction.

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

### Decision 5: Fix Skills `bar help llm` Reference
**Files to change (Path B, minimum):**
- `bar-autopilot` skill: replace all `bar help llm` references with `bar help tokens`; remove "legacy" label; remove references to non-existent sections
- `bar-manual` skill: same
- `bar-workflow` skill: same
- `bar-suggest` skill: same

**Additional files to change (Path A, full):**
- `bar` binary: implement `bar help llm` command with the sections referenced in skills

### Decision 6: Update Skills for New Scope Tokens
**Files to change:**
- `bar-autopilot` skill: add assume, motifs, stable, view scope token heuristics; verify time, fail, good, mean, thing are present
- `bar-manual` skill: same
- `bar-workflow` skill: same
- `bar-suggest` skill: same

### Decision 7: Add Composition Guidance to `bar help tokens`
**Files to change:**
- `bar` binary: add composition section to `bar help tokens` output (or implement `bar help llm` per Decision 5 Path A)
- If adding to `bar help tokens`: add output-exclusive conflict notice, codetour/gherkin task-affinity cross-reference, and rewrite semantic conflict note
