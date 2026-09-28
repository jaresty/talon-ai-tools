# ADR-0085 Cycle 24 — Shuffle-Driven Evaluation (seeds 0207–0212)

**Date:** 2026-09-28
**Evaluators:** single-evaluator (Claude, opus-4-8)
**Binary version:** `bar version dev` (rebuilt from HEAD e36b327a — includes cycle-23 edits; no release lag)
**Batch:** 6 seeds (small rapid cycle)
**Phases run:** Phase 1, Phase 2, Phase 2b/2c (meta-eval), Phase 2e (distinction check), Phase 2d (process self-eval)

## Calibration (single-evaluator)

Single-evaluator. Boundary rationale inline. Cycle-23 calibration lesson applied: `template`
paired with a task legitimately produces a *blank form* — do not score that as a defect (this
was the miscalibration that produced the dropped R2 last cycle).

## Seed summary

| Seed | task | completeness | scope | method | form | channel | directional |
|------|------|------|------|------|------|------|------|
| 207 | pull | full | jobs | cite | bullets | — | — |
| 208 | plan | full | — | — | contextualise | sketch | rog |
| 209 | show | ration | stable | — | template | — | fig |
| 210 | fix | skim | — | orbit | — | store | ong |
| 211 | sim | full | assume | automate | code | — | — |
| 212 | pick | grow | motifs | — | — | ledger | fip ong |

---

## Seed 207 — pull · full · jobs · cite · bullets

**Request:** "select or extract a subset of the given information without altering its substance."

**Cross-axis check:** bullets — no entry. No channel token. Evaluate on merits.

**Scores (vs prompt key):**
- Task clarity: 5 — pull is clear.
- Constraint independence: 5 — cite (anchor claims to sources), bullets (concise points), jobs
  (focus on outcomes/pressures), full (breadth) all shape HOW without redefining the extraction.
- Category alignment: 5.
- Combination harmony: 4 — coherent: extract the jobs-to-be-done from source material, cited,
  as bullets. One mild tension: `pull` extracts *given* material "without altering substance,"
  while `jobs` (scope) reframes toward *outcomes the subject is trying to achieve* — a slightly
  interpretive lens over a verbatim-extraction task. Derivable (extract the passages that reveal
  the jobs), so not a defect. **Boundary rationale (4 not 5):** jobs adds an interpretive angle
  that sits a half-step from pull's "without altering substance," but stays within it.
- Method category coherence: N/A (single method).
- **Overall: 4**

**Notes:** Clean, useful. cite+pull is a natural pairing (extract with provenance). No action.

---

## Seed 208 — plan · full · contextualise · sketch · rog

**Request:** "propose steps, structure, or strategy to move toward a goal."

**Cross-axis check:** sketch (channel) natural tasks = `['make','plan','show','probe']` — **plan is
natural.** ✓ contextualise (form) channel cautions are gherkin/shellscript/codetour — sketch not
among them, but sketch IS a channel and contextualise IS a form → the two interact (see below).

**Scores (vs prompt key):**
- Task clarity: 5 — plan is clear.
- Constraint independence: 3 — **contextualise + sketch tension.** contextualise (form) packages
  content *for a downstream LLM* — "enriches with all context a downstream model would need...
  The main content is not rewritten." sketch (channel) emits *only pure D2 diagram source, no
  surrounding natural language.* These fight: contextualise wants added prose context; sketch
  forbids prose entirely ("Do not include any surrounding natural language"). Under the universal
  rule (channel wins), sketch wins → output is D2 source only → contextualise's "enrich with
  background/assumptions/constraints" has nowhere to live. This is the same **prose-form-meets-
  DSL-only-channel** mechanism as the existing ghost+svg, prep+svg, twin+svg, cards+gherkin
  composition entries.
- Category alignment: 5.
- Combination harmony: 3 — plan+full render fine into a D2 diagram (a plan as a diagram). rog
  (structural/reflective) suits a diagram well. The lone conflict is contextualise×sketch.
  **Boundary rationale (3 not 2):** only one pairing conflicts and it has a known resolution
  pattern (prose block before/after the DSL artifact); the rest cohere.
- **Overall: 3**

**Notes:** **contextualise + sketch (and contextualise + any DSL-only channel: svg, gherkin,
sketch/D2, codetour)** is the same prose-form-vs-DSL-channel family already covered for ghost/
prep/twin/cards. contextualise belongs in that family but has no entry. Candidate: composition
entry `contextualise+sketch` (or generalize the existing SVG-family entries to name
contextualise). Strong compare-mode/composition candidate.

---

## Seed 209 — show · ration · stable · template · fig

**Request:** "explain or describe the subject for the stated audience."

**Cross-axis check:** template — no channel token, so channel-cautions don't fire. Applying
cycle-23 lesson: template legitimately yields a blank form.

**Scores (vs prompt key):**
- Task clarity: 5 — show is clear.
- Constraint independence: 3 — **template + show tension (same family as cycle-23 template+plan).**
  show (explain/describe for an audience) is generative prose; template mandates empty labeled
  slots. Under form precedence, output becomes a *blank explanation template* ([Concept],
  [Audience-relevant analogy], [Example]…) rather than an actual explanation. Per cycle-23, this
  is template doing its job, not a defect — but it *does* mean show, ration, stable, and fig all
  do displaced work (they shape what slots exist, not filled content). ration (allocate depth by
  a named score) over an empty template is nearly inert — there is no depth to allocate when no
  slot is filled. fig (abstract+concrete) likewise shapes slot *selection*, not content.
- Category alignment: 5.
- Combination harmony: 3 — coherent as "a template for explaining this subject," but four of the
  five modifiers (show's prose intent, ration, fig, and stable's lens) are attenuated by
  template's emptiness. **Boundary rationale (3 not 2):** the reframe is fully recoverable (a
  thorough explanation template) and cycle-23 established this is legitimate; but the attenuation
  of ration+fig is real, so not a 4.
- **Overall: 3**

**Notes:** Confirms the cycle-23 finding that **template attenuates depth/directional modifiers**
because it produces empty slots. This is now the *second* seed (after 202) showing template +
generative task + a depth/directional token. Not a composition defect — but a candidate
**guidebook** note: "template pairs weakly with depth (ration/deep/grow) and directional tokens
because empty slots carry no depth to allocate; template governs slot structure, not content
depth." This is discovery-layer guidance, not a co-presence rule. Corroborates, does not
duplicate, cycle-23.

---

## Seed 210 — fix · skim · orbit · store · ong

**Request:** "change the form or presentation of given content while keeping its meaning."

**Cross-axis check:** store (channel) — no entry (additive persistence; composes with anything).
skim completeness directional cautions do NOT include `ong` (primitive, not compound) → OK.
skim method cautions = `['rigor']` — orbit not listed, but see tension below.

**Scores (vs prompt key):**
- Task clarity: 5 — fix is clear.
- Constraint independence: 2 — **skim + orbit conflict, and orbit + fix conflict.**
  (a) orbit (method) requires "varying initial conditions across multiple trajectories... at
  least one trajectory whose named initial conditions include at least one value not in any
  other" — a structurally heavy, multi-run analysis. skim (completeness) is "only a very light
  pass... without aiming for completeness." orbit's minimum evidentiary bar (multiple distinct
  trajectories) cannot be met by a skim light pass. Same mechanism as the cautioned skim+rigor.
  (b) orbit (find the attractor across trajectories) applied to fix (reformat existing content)
  has almost no purchase — reformatting has no "trajectories" or "sensitive dependence on
  initial conditions." orbit is an analysis method forced onto a transformation task (the
  cycle-23 paradox+fix category — a tension-holding/analysis method on a convergent task).
- Category alignment: 4 — all in-axis, but orbit (an Exploration/Diagnostic-style method) is
  category-mismatched to fix (transformation).
- Combination harmony: 2 — store+ong+fix cohere (reformat, persist it, orient toward next
  actions). orbit is the disruptive member on two fronts (vs skim, vs fix). **Boundary rationale
  (2 not 1):** no single hard contradiction, but orbit conflicts with *two* other tokens
  simultaneously; the response can technically emit something, but orbit is doing no real work.
- Method category coherence: N/A (single method).
- **Overall: 2**

**Notes:** Two findings:
1. **skim + orbit** — completeness floor vs method's multi-trajectory minimum. Same family as
   the existing **skim+rigor** cautionary (completeness/skim/method). Candidate: add `orbit` (and
   likely other high-evidence methods) to skim's method cautionary list. This is a genuine
   cautionary (no precedence rescues a light pass that structurally can't meet orbit's minimum).
2. **orbit + fix** — analysis method on transformation task. Same shape as cycle-23 paradox+fix.
   Could extend the "analysis-method + transformation-task" treatment, but unlike paradox+fix
   there's no coherent combined meaning to define (orbit needs trajectories; a reformat has
   none) → this is a *warning* (cautionary/guidebook), not a definable composition.

---

## Seed 211 — sim · full · assume · automate · code

**Request:** "play out a concrete or hypothetical scenario over time under stated conditions."

**Cross-axis check:** **code (channel) cautions `sim`!** code caution task = `['sim','probe']`.
This is a KNOWN cautionary pairing → score but **exclude from retirement aggregation**; verify
the warning holds.

**Scores (vs prompt key):**
- Task clarity: 5 — sim is clear.
- Constraint independence: 2 — **sim + code is the documented cautionary.** sim plays out a
  scenario over time (inherently narrative — a sequence of states and consequences); code emits
  "only code or markup... no surrounding natural-language explanation." A time-evolving scenario
  narrative cannot be expressed as code-only output. The existing cautionary text captures this.
  automate (prefer repeatable operations) actually *pulls toward* code (coherent), and assume
  (surface premises) suits sim well — but the code channel caps sim's narrative.
- Category alignment: 5.
- Combination harmony: 2 (flagged cautionary — **excluded from retirement aggregation**) — under
  the universal rule, code wins → sim becomes "express the scenario as executable code" (a
  simulation *program*), which is derivable but loses sim's over-time narrative. The cautionary
  warning is empirically supported here.
- Method category coherence: N/A.
- **Overall: 2** (cautionary — excluded from token-retirement aggregation)

**Notes:** Confirms the existing `code` caution for `sim` holds. No new action — this is the
cross-axis check working as designed. automate+sim+assume (minus the code cap) would be a strong
combination: model the scenario's premises and what could be automated.

---

## Seed 212 — pick · grow · motifs · ledger · fip ong

**Request:** "choose one or more options from a set of alternatives."

**Cross-axis check:** ledger (channel) — no entry (categorized persistence: Facts/Decisions/
Constraints/Open Questions; composes with anything). grow completeness — no entry. fip-ong is a
compound directional; grow (not skim) → no directional caution.

**Scores (vs prompt key):**
- Task clarity: 5 — pick is clear.
- Constraint independence: 4 — grow (start minimal, expand only where justified), motifs (recurring
  patterns), fip-ong (span abstract+concrete, oriented to action) all shape HOW. ledger writes the
  decision under Facts/Decisions/Constraints/Open Questions — a genuinely apt channel for a `pick`
  (a decision *is* the ledger's "Decisions" content). **Boundary rationale (4 not 5):** motifs
  (recurring patterns across the option set) is a slightly unusual scope for a selection task —
  it fits (pick by identifying which option instantiates a recurring winning pattern) but is a
  half-step interpretive.
- Category alignment: 5.
- Combination harmony: 5 — pick + ledger is a strong, coherent pairing (a decision recorded to a
  Decisions ledger). grow suits a disciplined selection rationale; fip-ong orients the choice
  toward action. This is one of the cleaner combinations this cycle.
- **Overall: 4**

**Notes:** pick + ledger is a natural pairing — a decision written to the ledger's Decisions
heading. Parallels the cycle-23 R1 finding (pick+adr): pick composes naturally with
decision-recording channels (adr, ledger). Candidate: consider whether ledger's cross-axis entry
should list pick/plan as natural tasks (ledger currently has no CROSS_AXIS entry at all).

---

## Cycle score summary

| Seed | Overall | Load-bearing issue |
|------|---------|--------------------|
| 207 | 4 | clean; jobs slightly interpretive over pull |
| 208 | 3 | contextualise (prose form) × sketch (DSL-only channel) — SVG-family gap |
| 209 | 3 | template attenuates ration/fig (empty slots) — corroborates cycle-23 |
| 210 | 2 | skim × orbit (light pass vs multi-trajectory min); orbit × fix (analysis on transform) |
| 211 | 2 | sim × code — documented cautionary, excluded from aggregation |
| 212 | 4 | clean; pick + ledger natural pairing |

**Mean (all 6): 3.0 / 5.**
**Mean excluding the flagged cautionary (seed 211): 3.2 / 5** (5 qualifying seeds).

Consistent with cycle-23 (3.0): this batch again drew several form/channel edge cases
(contextualise+sketch, template+show) plus one documented cautionary (sim+code) and one
completeness×method floor conflict (skim+orbit). Exactly the edges ADR-0085 is built to surface.
