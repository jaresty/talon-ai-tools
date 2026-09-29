# ADR-0085 Cycle 26 — Shuffle-Driven Evaluation (seeds 0219–0224)

**Date:** 2026-09-29
**Evaluators:** single-evaluator (Claude, opus-5)
**Binary version:** `bar version dev` (installed binary refreshed at HEAD ae83f74b — includes cycles 23-25 edits; propagation verified in cycle-25 post-apply)
**Batch:** 6 seeds (small rapid cycle)
**Phases run:** Phase 1, 2, 2b/2c, 2e, 2d

## Calibration (single-evaluator)

Single-evaluator. Lessons carried forward:
- (c23) template/blank-form legitimacy; shuffle-only pairings are routing matters, not automatic defects.
- (c24/25) **composition** when a coherent output satisfies both (incl. two coexisting artifacts); **cautionary** only when one token structurally starves the other.
- (c25) **description purity** (nn 20260929154929-2747): a token description states only what the token IS — relational content routes by relationship type. Watch for tokens over-claiming format.

## Seed summary

| Seed | task | completeness | scope | method | form | channel | directional |
|------|------|------|------|------|------|------|------|
| 219 | pull | full | dam | — | interactive | code | — |
| 220 | pick | skim | — | — | table | — | — |
| 221 | pull | minimal | fail | models | — | — | fly rog |
| 222 | pick | full | good | — | snap | zettel | fip rog |
| 223 | sim | full | act | mark | — | code | rog |
| 224 | plan | prime | — | analog | prep | code | dip rog |

---

## Seed 219 — pull · full · dam · interactive · code

**Cross-axis:** code task natural includes `pull` ✓. interactive (form) — no entry.

**Scores:**
- Task clarity: 5 — pull is clear.
- Constraint independence: 2 — **interactive × code is a definitional collision.** interactive: "acts to advance the shared epistemic state incrementally rather than resolving the interaction unilaterally ... names a current state and at least one available [option/next step]" — it requires *conversational turn structure* (state + options, inviting the other side's input). code: "only code or markup as the complete output, with no surrounding natural-language explanation or narrative." An interactive exchange cannot be conducted inside a code-only artifact: the state/options prose has nowhere to live. dam (containment boundaries) + pull + full cohere fine (extract what's in/out of scope, thoroughly).
- Category alignment: 5.
- Combination harmony: 2 — pull+dam+full+code is coherent (extract scope boundaries as code/config). interactive is the sole conflicting member, and it conflicts *structurally*: its whole mechanism is a turn-taking prose exchange.
  **Boundary rationale (2 not 3):** unlike a soft affinity, interactive's core requirement (name state + offer options to the counterparty) is negated by code-only output. Not derivable by "channel wins" — the form has no residue left.
- **Overall: 2**

**Notes:** **interactive × code (and interactive × any artifact-only channel: svg, sketch, gherkin, codetour, shellscript).** Is this composition or cautionary? interactive is a *whole-response interaction protocol*, not supplementary content — closer to `tight` (whole-response) than `contextualise` (supplementary). BUT: unlike tight (which was fixed by removing a bogus format claim), interactive's requirement is genuinely structural — it needs a prose turn. Candidate: **cautionary** (one token starves the other). See distinction-check.

---

## Seed 220 — pick · skim · table

**Cross-axis:** table (form) — no entry. skim cautions are directional/method — none present here.

**Scores:**
- Task clarity: 5 — pick (LLM selects among alternatives) is clear.
- Constraint independence: 5 — table (compact Markdown table) is an excellent structure for a selection: options as rows, criteria as columns, with the pick named. skim (light pass) + pick is coherent (quick decision, obvious factors only).
- Category alignment: 5.
- Combination harmony: 5 — pick+skim+table is clean and genuinely useful: a quick comparison table ending in a choice. No token does displaced work.
- **Overall: 5**

**Notes:** Clean baseline. pick+table is a natural pairing (option/criteria grid → selection). Candidate observation: table may deserve a `task` natural list including pick/diff.

---

## Seed 221 — pull · minimal · fail · models · fly rog

**Cross-axis:** no channel/form tokens. models (method) — no entry. minimal — no entry.

**Scores:**
- Task clarity: 5 — pull is clear.
- Constraint independence: 3 — **models × minimal tension.** models requires: "enumerates named, established mental models ... first naming which models are already operative; for each absent model, names why it applies and what it would surface." That is a structurally *additive, enumerative* procedure with a floor (name operative set + each absent model + its yield). minimal is "the smallest answer that satisfies the request, avoiding work outside the core need." models' minimum output (operative set + ≥1 absent model + rationale + yield) is already more than minimal wants to license. Same family as the shipped **skim+rigor / skim+orbit** cautionaries (completeness floor vs method minimum) — but with `minimal` rather than `skim`.
  Also mild: **models × pull** — pull extracts from given source *without altering substance*; models *introduces external frames* not present in the source. That is additive interpretation over an extraction task (similar to cycle-24's jobs×pull, scored mild).
- Category alignment: 4 — all in-axis; models is an additive/generative method applied to an extraction task, so category fit to `pull` is imperfect.
- Combination harmony: 3 — pull+fail+fly-rog cohere well (extract the failure modes, abstractly/structurally framed). models is the strained member on two fronts (vs minimal, vs pull).
  **Boundary rationale (3 not 2):** each strain is individually mild and the reframe is available ("name the few highest-value absent models"), unlike seed 219's definitional collision.
- **Overall: 3**

**Notes:** Two findings: (1) **minimal + models** — completeness floor vs method enumeration minimum; the `skim+rigor/orbit` family applied to `minimal`. Candidate: extend that cautionary family to `minimal` for enumeration-floor methods (models, rigor, orbit). (2) models+pull additive-vs-verbatim — mild, pattern-watch only.

---

## Seed 222 — pick · full · good · snap · zettel

**Cross-axis:** snap (form) — no entry. zettel (channel) — no entry.

**Scores:**
- Task clarity: 5 — pick is clear.
- Constraint independence: 3 — **snap × zettel tension.** snap: "a state snapshot: current progress, key decisions made, what remains, and enough context to resume" — a *multi-part composite* artifact. zettel: "one or more Zettelkasten notes in nn format. **Each note body must contain exactly one claim** ... no coordinating conjunction joining two independent sentences — a body that does is two notes." These interact: a snapshot's four-part composite (progress/decisions/remaining/context) must be decomposed into one-claim-per-note. That is *derivable and arguably good* (the snapshot becomes a small linked note set), but it is a real structural transformation the tokens don't state — a composition-shaped interaction. good (judgment criteria) + pick + full + fip-rog cohere.
- Category alignment: 5.
- Combination harmony: 3 — pick+good+full+fip-rog is strong (choose by explicit criteria, spanning abstract/concrete, structurally framed). snap+zettel needs the decomposition rule to land well.
  **Boundary rationale (3 not 4):** without a stated rule, the likely output is either a monolithic note violating zettel's one-claim rule, or a note set that loses snap's "resume from here" coherence.
- **Overall: 3**

**Notes:** **snap + zettel is a genuine composition candidate** (not a cautionary): a coherent output exists — decompose the snapshot into one-claim notes, plus an index/entry note carrying the resume pointer. Both tokens satisfied. Strongest composition candidate this cycle.

---

## Seed 223 — sim · full · act · mark · code

**Cross-axis:** **`code` cautions `sim`** — KNOWN cautionary. Score but **exclude from retirement aggregation**.

**Scores:**
- Task clarity: 5 — sim is clear.
- Constraint independence: 2 — the documented sim×code conflict: sim plays out a scenario over time (narrative sequence of states); code is code-only with no narrative. Under channel-wins this becomes a simulation *program*, losing sim's over-time account. **mark** (checkpoints with '## Step N' headers recording observations as a process runs) *also* needs prose headers — which code-only output cannot host, so mark is a second casualty of the same channel constraint. act (tasks/operations) + full cohere with sim.
- Category alignment: 5.
- Combination harmony: 2 (flagged cautionary — **excluded from retirement aggregation**) — sim and mark both require narrative/structured-prose scaffolding that the code channel forbids.
- **Overall: 2** (cautionary — excluded)

**Notes:** Confirms the `code`→`sim` cautionary holds (third cycle it has been exercised or noted). **New sub-finding: mark × code** — mark's '## Step N' checkpoint headers are prose structure, so mark shares sim's incompatibility with code-only output. mark is not currently cautioned for code. Candidate, but entangled with the already-cautioned sim in this seed — weak isolation; flag as pattern-watch rather than act.

---

## Seed 224 — plan · prime · analog · prep · code

**Cross-axis:** prep (form) — no entry; code (channel) natural tasks exclude `plan` (unlisted, not cautioned) → universal rule.

**Scores:**
- Task clarity: 5 — plan is clear.
- Constraint independence: 2 — **prep × code.** prep: "an experiment write-up: hypothesis, method, expected outcomes, and evaluation criteria" — four prose sections. code: code-only, no prose. This is exactly the shipped **prep+svg** mechanism ("prep form requires rich prose blocks ... svg is markup-only with no prose slot") — but for the `code` channel, which has no prep entry. analog (map relational structure from a known case, examine where it holds/breaks) also needs prose to express the mapping. prime (rank by learning leverage, name the criterion, closure statement) likewise needs prose scaffolding. So *three* tokens (prep, analog, prime) each need prose the code channel forbids.
- Category alignment: 5.
- Combination harmony: 2 — plan+analog+prep+prime+dip-rog is a coherent *design-an-experiment* combination; the code channel is the single member that starves the other three.
  **Boundary rationale (2 not 1):** the reframe is nominally available (emit the experiment as a commented script / test scaffold), so not fully broken — but three tokens are simultaneously attenuated.
- **Overall: 2**

**Notes:** **prep × code** is the same prose-form-vs-artifact-channel family as the shipped `prep+svg` composition. prep+svg resolves by "the prep write-up must appear as a prose block before or after the svg artifact" — the identical resolution applies to code. Strong composition candidate (extends a shipped composition to a sibling channel).

---

## Cycle score summary

| Seed | Overall | Load-bearing issue |
|------|---------|--------------------|
| 220 | 5 | clean — pick+skim+table |
| 221 | 3 | minimal × models (enumeration floor); models × pull (mild) |
| 222 | 3 | snap × zettel — composition candidate (decompose to one-claim notes) |
| 219 | 2 | interactive × code — definitional collision (turn-taking vs artifact-only) |
| 223 | 2 | sim × code documented cautionary (excluded); mark × code sub-finding |
| 224 | 2 | prep × code — same family as shipped prep+svg composition |

**Mean (all 6): 2.83 / 5.**
**Mean excluding flagged cautionary (seed 223): 3.0 / 5** (5 qualifying seeds).

Lower than cycle-25 (3.5). Cause is identifiable, not regression: **three of six seeds drew the `code` channel** (219, 223, 224), and `code` is the most restrictive channel in the catalog (artifact-only, no prose). Every prose-bearing form or prose-needing method paired with it strains. That concentration is sampling luck, and it points at a real gap: `code` has a rich task cautionary list but almost no **form** entries, while its prose-form conflicts are the same family already resolved for `svg`.
