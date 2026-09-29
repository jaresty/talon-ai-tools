# ADR-0085 Cycle 28 — Stratified Evaluation (seeds 244/245/248/251/254/259)

**Date:** 2026-09-29
**Evaluator:** single-evaluator (Claude, opus-5)
**Binary:** `bar version dev`, reinstalled at HEAD 9363dec6 (cycles 23-27 edits present, incl. the
render-class sweep and the four newly documented channels)
**Batch:** 6 seeds, stratified — **second** stratified cycle, first with a comparable baseline (c27 = 2.83)

## Sampling

Surveyed seeds 241-262. `browse` appeared 3× (257, 261, 262) — the exact over-representation the
amended rule caps, and now a *documented* channel so lower-value to re-score. Selected 6 with **six
distinct channels, no repeats**, favouring undocumented ones: image, store, zettel, github, html, skill.

**Channel distribution: 6 seeds / 6 distinct channels / max 1 each.** Comparable to c27 by construction.

First-time-scored tokens: image, store, skill, authority, shear, relations, visual, story,
eliminate, ontology, lever, motifs.

## Seed summary

| Seed | task | completeness | scope | method | form | channel | directional |
|---|---|---|---|---|---|---|---|
| 244 | fix | full | lever | — | — | image | dip bog |
| 245 | check | full | authority | shear | — | store | — |
| 248 | check | full | relations | — | contextualise | zettel | fig |
| 251 | fix | skim | — | visual | story | github | fly bog |
| 254 | pull | full | motifs | eliminate | ontology | html | — |
| 259 | probe | gist | — | — | vet | skill | bog |

---

## Seed 244 — fix · full · lever · image · dip bog

**Cross-axis:** image — **no entry**. image: "consists solely of an image as the complete output —
described through subject, style, composition, lighting, and technical parameters — with no
surrounding prose".

**Scores:**
- Task clarity: 5 — fix (reformat existing content, keep meaning) is clear.
- Constraint independence: 2 — **image × fix is a deliverable mismatch.** fix transforms *given
  content* while preserving its meaning. image produces an image *specification* (subject, style,
  lighting, technical parameters). Reformatting prose into an image does not preserve meaning in
  any checkable sense — meaning-preservation is fix's success condition, and an image cannot be
  compared against the source for it. `lever` (intervention points, feedback loops, parameters
  whose change shifts equilibrium) is a systems-analysis scope with no visual carrier; `dip bog`
  wants concrete detail across structure and action.
- Category alignment: 5.
- Combination harmony: 2 — fix+lever+full+dip-bog cohere as a systems-intervention rewrite; image
  is the member that cannot carry any of it. **Boundary rationale (2 not 3):** unlike a rendering
  problem, there is no adjacent-block rescue — fix's *whole deliverable* is the transformed
  content, and an image specification is not that content in another format.
- **Overall: 2**

**Notes:** **image is a `constructor`-adjacent channel** in the three-way taxonomy sense (nn
20260717011133-2169): it does not reshape the task's output, it produces a *specification for
generating* an artifact. Same family as `agent`/`skill`. Candidate: image natural task list
(`make` — create an image) plus cautionary for content-transform tasks (fix/pull) where
meaning-preservation is unverifiable. **No entry exists at all.**

---

## Seed 245 — check · full · authority · shear · store

**Cross-axis:** store — **no entry**. store: "additionally writes output to persistent storage ...
Conversational output continues normally; storage is additive, not a replacement."

**Scores:**
- Task clarity: 5 — check (evaluate against a condition, report pass/fail) is clear.
- Constraint independence: 5 — **store is explicitly additive**, so it conflicts with nothing: the
  check verdict is produced normally *and* persisted. `authority` (explain outcomes via actors who
  can select among alternatives) is a strong scope for a check (who can act on a failure);
  `shear` (steps to separate coupled domains, reducing the seam to an explicit interface) suits a
  check that finds coupling violations. `full` sets breadth.
- Category alignment: 5.
- Combination harmony: 5 — check+authority+shear+full+store is a genuinely coherent audit: verify
  against criteria, attribute outcomes to actors with decision capacity, propose decoupling steps,
  persist the record. Nothing does displaced work.
- **Overall: 5**

**Notes:** **`store` is the cleanest channel in the catalog for composition purposes** — its
definition states "storage is additive, not a replacement", which pre-empts every conflict a
delivery channel normally creates. Same virtue as `facilitate` (c27-O1): the token anticipates its
own interaction. Candidate: store natural task list is arguably *all* tasks; more usefully, store
needs no cautionary entries at all. Positive exemplar #2.

---

## Seed 248 — check · full · relations · contextualise · zettel · fig

**Cross-axis:** contextualise natural channels `[plain, sync, jira, slack]`; zettel unlisted.
zettel — **no entry**. This is the contextualise family converted to compositions in cycle 27.

**Scores:**
- Task clarity: 5 — check is clear.
- Constraint independence: 3 — **contextualise × zettel is a real interaction with no rule.**
  contextualise "packages the subject to be passed directly to another LLM operation ... enriches
  with all context a downstream model would need"; zettel requires "one or more Zettelkasten notes
  ... each note body must contain **exactly one claim**". These pull oppositely: contextualise
  *adds* surrounding context to make content self-sufficient; zettel *decomposes* into single-claim
  atoms and forbids compound bodies. A self-contained context package is by nature multi-claim.
  Resolution exists (an index note carrying the context, one note per claim — exactly the
  `snap+zettel` pattern shipped in cycle 26), but no rule states it. `relations` (connections as the
  primary object) suits zettel well — a note graph *is* relations; `fig` spans abstract+concrete.
- Category alignment: 5.
- Combination harmony: 3 — check+relations+full+fig+zettel cohere strongly; contextualise is the
  unresolved member. **Boundary rationale (3 not 2):** the resolution is available and has a
  shipped precedent, so this is a missing rule rather than a conflict.
- **Overall: 3**

**Notes:** **contextualise+zettel is a composition candidate with a direct precedent** —
`snap+zettel` (cycle 26) resolves the identical "composite content vs one-claim-per-note" tension
by decomposing into notes plus an entry note. Strongest actionable finding this cycle.

---

## Seed 251 — fix · skim · visual · story · github · fly bog

**Cross-axis:** **`skim` cautions `fly-bog`** ✓ (compound directional vs light pass) — a DOCUMENTED
cautionary firing, so exclude from token-retirement aggregation. github — **no entry**.

**Scores:**
- Task clarity: 5 — fix is clear.
- Constraint independence: 2 — three strains. (a) The documented **skim × fly-bog**: a compound
  directional spanning abstract + structure + action cannot be delivered in a light pass. (b)
  **story × fix**: story formats the item as "As a \<persona\>, I want \<capability\>, so that
  \<value\>" — a *fixed template for a backlog item*, not a reformatting of arbitrary given
  content; applying it to fix means the source must already be a user-story-shaped requirement.
  (c) **visual × github**: visual places concepts in named positions "in a spatial arrangement,
  diagram, or map"; github delivers GitHub-Flavored Markdown via `gh`, which can host a Mermaid
  diagram, so this one is fine.
- Category alignment: 5.
- Combination harmony: 2 (flagged cautionary — **excluded from retirement aggregation**) — the
  documented skim×fly-bog plus story×fix compound.
- **Overall: 2** (cautionary excluded)

**Notes:** Confirms **skim × compound-directional** cautionary works as designed (third such
confirmation this session). Secondary finding: **story is a fixed-template form** whose subject
must already be a requirement — story+fix is odd but derivable (reformat a requirement into story
shape), so pattern-watch not action.

---

## Seed 254 — pull · full · motifs · eliminate · ontology · html

**Cross-axis:** html task natural `[make, fix, show, pulse, pull, check]` — **`pull` is natural** ✓.
ontology — no entry.

**Scores:**
- Task clarity: 5 — pull (extract a subset without altering substance) is clear.
- Constraint independence: 3 — **ontology × pull tension.** ontology "defines the concepts and
  relations that constitute the subject domain: each named concept gets a definition and a set of
  properties; each named relation gets a source concept, a target concept, and a cardinality
  constraint". That is *constructive* — it builds a formal model. pull extracts a subset "without
  altering its substance". Building an ontology from source material adds formal structure the
  source did not state (definitions, cardinalities), which strains pull's verbatim constraint —
  the same additive-vs-verbatim shape as cycle-26's `models × pull` and cycle-24's `jobs × pull`.
  `eliminate` (enumerate a closed candidate set, N as a numeral, strike or retain each) composes
  well with pull (extract, then narrow); `motifs` (recurring forms) suits ontology.
- Category alignment: 4 — ontology is a constructive form applied to an extraction task.
- Combination harmony: 3 — pull+motifs+eliminate+full+html cohere; ontology is the strained member.
  **Boundary rationale (3 not 2):** extracting *the domain's stated* concepts and relations is a
  legitimate reading, so derivable.
- **Overall: 3**

**Notes:** **Third instance of additive-form/method × pull** (jobs c24, models c26, ontology c28).
Three independent seeds across three cycles is now a pattern, not a one-off. Candidate: a general
treatment — pull's completeness/method/form interaction is that modifiers select *within* the
source rather than adding to it. The shipped `pull+deep` composition already states exactly this
("deep governs how much of the selected subset to carry across ... not a licence to unpack,
elaborate, or add reasoning beyond what the source states"). Extending that principle beyond
`deep` is the actionable move.

---

## Seed 259 — probe · gist · vet · skill · bog

**Cross-axis:** **`gist` cautions `bog`** ✓ — DOCUMENTED cautionary firing (compound directional vs
brief summary); exclude from retirement aggregation. skill — no entry. vet — no entry.

**Scores:**
- Task clarity: 5 — probe (analyze to surface structure, assumptions, implications) is clear.
- Constraint independence: 2 — two strains. (a) Documented **gist × bog**: a compound directional
  covering structure *and* action cannot fit a short summary. (b) **skill × probe**: skill is a
  *constructor* channel — "structured as a reusable agent skill definition — YAML frontmatter
  (name, description, when_to_use, requires) followed by a markdown body with usage instructions,
  workflow steps, and one real worked example". Paired with probe, the output is a *skill spec for
  a probing agent*, not the analysis. Exactly cycle-23's `agent × diff` finding, which established
  the constructor-channel class. `vet` (post-experiment review) also needs analytic prose the
  frontmatter-plus-body structure can host, so vet is fine.
- Category alignment: 5.
- Combination harmony: 2 (cautionary excluded) — the documented gist×bog plus the constructor
  substitution.
- **Overall: 2** (cautionary excluded)

**Notes:** **`skill` confirms the constructor-channel class** first identified for `agent` in cycle
23 and recorded in the channel taxonomy note (nn 20260717011133-2169: format / delivery-mechanism /
**constructor**). Both `agent` and `skill` replace the deliverable with a spec for a tool that would
perform it. Neither has a cross-axis entry. Candidate: constructor channels (agent, skill, image)
need natural task lists centred on `make`, with cautionaries for analysis tasks (probe/diff/show)
where the analysis itself is the deliverable.

---

## Cycle score summary

| Seed | Channel | Overall | Load-bearing issue |
|---|---|---|---|
| 245 | store | **5** | clean — store is additive by definition, conflicts with nothing |
| 248 | zettel | 3 | contextualise×zettel — composition candidate (snap+zettel precedent) |
| 254 | html | 3 | ontology×pull — third additive-form×pull instance |
| 244 | image | 2 | image×fix — constructor channel, meaning-preservation unverifiable |
| 251 | github | 2 | documented skim×fly-bog (excluded) + story×fix |
| 259 | skill | 2 | documented gist×bog (excluded) + skill×probe constructor substitution |

**Mean (all 6): 2.83 / 5.**
**Mean excluding the two flagged cautionaries (251, 259): 3.25 / 5** (4 qualifying seeds).

## Comparison to cycle 27 — the first meaningful cross-cycle comparison

| | c27 | c28 |
|---|---|---|
| Channels | 6 distinct | 6 distinct |
| Mean (all) | 2.83 | 2.83 |
| Mean (excl. flagged cautionaries) | 3.0 (1 excluded) | 3.25 (2 excluded) |
| Documented cautionaries fired | 1 (sim×code) | **2** (skim×fly-bog, gist×bog) |

**Interpretation:** the all-seed means are identical and the excluding-flagged means are close, which
under matched stratification suggests the ~2.8–3.3 band is the catalog's actual score against random
combinations rather than an artifact of sampling. That is the first time this session a mean has been
interpretable. Two documented cautionaries fired versus one — the caution layer is doing visible work.

**The finding that matters more than the mean:** five of six channels in this batch have **no
cross-axis entry** (image, store, zettel, github, skill). Cycle 27 closed four such gaps (aloud,
hunk, browse, notebook) and this batch immediately surfaced five more. The undocumented-channel
backlog is substantially larger than c27-O2 estimated, and it clusters on the **constructor** and
**delivery-mechanism** classes rather than format channels.
