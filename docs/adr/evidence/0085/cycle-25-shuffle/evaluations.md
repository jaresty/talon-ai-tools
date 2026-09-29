# ADR-0085 Cycle 25 — Shuffle-Driven Evaluation (seeds 0213–0218)

**Date:** 2026-09-29
**Evaluators:** single-evaluator (Claude, opus-4-8)
**Binary version:** `bar version dev` (rebuilt from HEAD 47ea6e76 — includes cycle-23/24 edits)
**Batch:** 6 seeds (small rapid cycle)
**Phases run:** Phase 1, 2, 2b/2c, 2e, 2d

## Calibration (single-evaluator)

Single-evaluator. Cycle-23/24 lessons applied: (a) template = legit blank form; (b) a
low score from a shuffle-only pairing no user would build is a routing/warning matter, not
automatically a catalog defect; (c) composition when two artifacts coexist, cautionary only
when one token starves the other.

## Seed summary

| Seed | task | completeness | scope | method | form | channel | directional | topology |
|------|------|------|------|------|------|------|------|------|
| 213 | check | full | thing | — | — | presenterm | — | live |
| 214 | plan | skim | — | — | coupling | html | — | — |
| 215 | fix | full | — | redact | — | browse | fip ong | — |
| 216 | check | full | — | perturb | timeline | — | bog | — |
| 217 | pull | minimal | — | winnow | tight | code | fip ong | — |
| 218 | make | full | struct | — | scorecard | notebook | — | — |

---

## Seed 213 — check · full · thing · presenterm · live

**Cross-axis:** presenterm task natural=`[make,show,plan,pull]`, caution=`[fix,probe]`. `check`
unlisted → universal rule. presenterm completeness natural=`[minimal,gist]`, caution=`[max,deep]`;
seed uses `full` — unlisted, but note presenterm prefers brevity (12-slide cap).

**Scores:**
- Task clarity: 5 — check (evaluate against a condition, report pass/fail) is clear.
- Constraint independence: 4 — presenterm (slide deck) as the delivery of a check verdict is
  coherent (a pass/fail review presented as slides). `full` sits mildly against presenterm's
  brevity preference (natural=minimal/gist, 12-slide cap) but isn't cautioned. live topology
  (externalize states per-segment) maps onto slides reasonably.
- Category alignment: 5.
- Combination harmony: 4 — check+thing (evaluate the entities in scope) + presenterm + full +
  live cohere: a slide deck auditing each entity against criteria. **Boundary rationale (4 not
  5):** full vs presenterm's brevity is a mild pull (a 12-slide cap fights "every named element
  at one depth"), derivable but slightly strained.
- **Overall: 4**

**Notes:** Coherent. Mild finding: **presenterm + full** — presenterm's completeness natural is
minimal/gist and it caps at 12 slides, so full is in mild tension though not currently cautioned.
Not strong enough to act on from one seed; note for pattern-watch. check is a reasonable
presenterm task (verdict deck) — arguably belongs in presenterm's natural task list alongside
show/plan.

---

## Seed 214 — plan · skim · coupling · html

**Cross-axis:** html task natural=`[make,fix,show,pulse,pull,check]`, caution=`[sim,probe]`.
`plan` unlisted → universal rule (channel wins, task = content lens). coupling (form) — no entry.

**Scores:**
- Task clarity: 5 — plan is clear.
- Constraint independence: 4 — html (semantic HTML only, no prose) as the delivery of a plan is
  fine (a plan rendered as an HTML page). coupling form (a coupling map — domains joined at a
  seam, what crosses the boundary) over a plan is a slightly unusual but valid structure: a plan
  organized as the couplings between workstreams. skim (light pass) + plan is coherent (a quick
  high-level plan).
- Category alignment: 5.
- Combination harmony: 3 — the mild tension is **coupling (form) × html (channel)**: coupling's
  description says it "pairs naturally with diagram/sketch channels" — a coupling *map* is
  inherently diagrammatic (seams, boundaries, what crosses). html (semantic HTML) can render a
  coupling map (as a structured page / embedded SVG), so it's derivable under channel-wins, but
  coupling's natural home is a diagram channel, not html. Not a hard conflict.
  **Boundary rationale (3 not 4):** coupling wants a visual/diagram target; html is prose-markup;
  the map becomes a described/tabular structure rather than a true coupling diagram — derivable
  but the form is doing attenuated work, similar to the "form wants a diagram channel" family.
- **Overall: 3**

**Notes:** **coupling (and timeline — see seed 216) are "diagram-affinity forms":** their own
descriptions say they "pair naturally with diagram/sketch channels." When paired with a
non-diagram channel (html here), the form renders in an attenuated way. This is a *soft* affinity
(html CAN host a coupling map), not the hard prose-form-vs-DSL-channel conflict from cycle-24.
Pattern-watch: diagram-affinity forms (coupling, timeline) + non-diagram channels. Not
actionable from one seed.

---

## Seed 215 — fix · full · redact · browse · fip ong

**Cross-axis:** browse (channel) — no entry. redact (method) — no entry.

**Scores:**
- Task clarity: 5 — fix (reformat, keep meaning) is clear.
- Constraint independence: 3 — **redact + fix compose well** (reformat while removing named
  categories for a general audience — coherent, both are content transforms). The tension is
  **browse × fix**: browse drives a live browser to fetch/act; fix reformats *given* content.
  Like cycle-23's browse+pull, browse supplies no given content — it fetches. Under channel-wins
  this becomes "drive the browser, then reformat what's fetched," derivable but fix's "given
  content" premise is overridden. fip-ong (abstract+concrete, action-oriented) over a
  fix/reformat is mild.
- Category alignment: 5.
- Combination harmony: 3 — redact+fix+full cohere; browse is the disruptive member (same shape
  as cycle-23 browse+pull). **Boundary rationale (3 not 2):** only one token (browse) conflicts,
  and it's the same fetch-vs-given pattern already understood; redact+fix is genuinely good.
- **Overall: 3**

**Notes:** **browse × transformation/extraction tasks (fix, pull)** recurs — cycle-23 flagged
browse+pull (now a composition: fetch-then-extract). browse+fix is the same family: fetch first,
then reformat the fetched content. Candidate: a browse+fix composition (sequencing), OR generalize
the browse+pull composition to "browse + given-content tasks (pull/fix): browse fetches first."
Corroborates cycle-23; this is the *second* browse-vs-given-content instance.

---

## Seed 216 — check · full · perturb · timeline · bog

**Cross-axis:** timeline (form) — no entry. No channel; bog directional with `full` (not skim) →
no caution.

**Scores:**
- Task clarity: 5 — check is clear.
- Constraint independence: 5 — perturb (introduce controlled faults, observe response) is an
  excellent method for check (verify safeguards against criteria — perturb tests them). timeline
  (temporal sequence) suits a perturbation check (what happens over time as faults are injected).
  bog (structure + action) fits. full = breadth.
- Category alignment: 5.
- Combination harmony: 5 — check+perturb+timeline+bog is a genuinely strong, coherent
  combination: a fault-injection audit whose results are laid out on a timeline, covering both
  what it means structurally and what to do. This is the cleanest seed this cycle.
- **Overall: 5**

**Notes:** Strong baseline. perturb+check is a natural, high-value pairing (stress-test as
verification). timeline suits sequential fault injection. No action.

---

## Seed 217 — pull · minimal · winnow · tight · code · fip ong

**Cross-axis:** code task natural=`[make,fix,show,pulse,pull,check]` — **pull is natural.** ✓
tight (form) — no entry. minimal completeness — no entry; fip-ong compound directional but
completeness is `minimal` (not skim) → no directional caution.

**Scores:**
- Task clarity: 5 — pull is clear.
- Constraint independence: 3 — **tight (form) × code (channel).** tight = "concise dense prose,
  remaining freeform without bullets, tables, or code." code = "only code or markup, no prose."
  These directly conflict: tight mandates *prose without code*; code mandates *code without
  prose*. Under channel-wins, code wins → output is code-only → tight's "dense prose" has nowhere
  to exist. tight is a prose-form meeting a code channel — the same prose-form-vs-code-channel
  family. winnow (resize candidates, select by value/cost) + pull (extract subset) compose well
  (winnow the extraction to the highest-value subset). minimal + pull + winnow all reinforce
  (smallest valuable subset).
- Category alignment: 5.
- Combination harmony: 2 — pull+minimal+winnow+fip-ong cohere strongly (a minimal, value-selected
  extraction). But tight×code is a direct form-vs-channel contradiction: tight is defined by
  *prose, no code*; code is defined by *code, no prose*. **Boundary rationale (2 not 3):** unlike
  coupling×html (soft affinity), this is a definitional collision — tight's core ("without ...
  code") is negated by the code channel. The form can't do its job at all.
- **Overall: 2**

**Notes:** **tight × code is a hard prose-form-vs-code-channel conflict** — tight explicitly
excludes code, code excludes prose. Unlike contextualise+DSL (resolvable by adjacent block,
because contextualise's content is *supplementary*), tight IS the whole response's prose form —
there's no "adjacent block" that satisfies "the response uses dense prose" when the channel says
"code only." This is a **cautionary** (one token starves the other; no coexisting output), not a
composition. Candidate: tight+code cautionary (and likely tight+other code-like channels:
shellscript, svg, sketch, gherkin). Strongest actionable finding this cycle.

---

## Seed 218 — make · full · struct · scorecard · notebook

**Cross-axis:** scorecard (form) — no entry. notebook (channel) — no entry.

**Scores:**
- Task clarity: 5 — make (create new content) is clear.
- Constraint independence: 3 — **scorecard (form) × notebook (channel).** scorecard = quantitative
  metrics with baseline/target/current/RAG status. notebook = valid Jupyter .ipynb (markdown +
  code cells). These actually compose reasonably: a notebook whose cells build/compute a scorecard
  (code cells computing metrics, markdown cells showing RAG status) is coherent — arguably a
  *natural* pairing (notebooks are made for computed metrics dashboards). make+struct (create,
  focused on arrangement) + full fit. The mild tension: scorecard is a fairly rigid tabular form;
  notebook wants cells — the scorecard has to be expressed across notebook cells rather than as
  one table.
- Category alignment: 5.
- Combination harmony: 4 — make+full+struct+scorecard+notebook cohere well: build a metrics
  scorecard as a runnable notebook. **Boundary rationale (4 not 5):** scorecard's rigid
  baseline/target/current/RAG structure spread across notebook cells is slightly awkward but
  entirely workable — arguably a good pairing. (3 on independence reflects the form/channel
  needing coordination; 4 on harmony reflects that they genuinely reinforce.)
- **Overall: 4**

**Notes:** scorecard + notebook is actually a *good* pairing (computed metrics in a runnable
notebook) — candidate natural-pairing, not a conflict. No negative action; possible future
natural-list entry (notebook natural form: scorecard).

---

## Cycle score summary

| Seed | Overall | Load-bearing issue |
|------|---------|--------------------|
| 216 | 5 | clean — perturb+check+timeline+bog |
| 213 | 4 | mild presenterm+full brevity tension |
| 218 | 4 | scorecard×notebook actually good (natural candidate) |
| 214 | 3 | coupling (diagram-affinity form) × html (non-diagram channel) — soft |
| 215 | 3 | browse × fix (fetch-vs-given, same family as cycle-23 browse+pull) |
| 217 | 2 | tight (prose form) × code (code channel) — hard definitional conflict |

**Mean: 3.5 / 5** — highest of the three cycles (23: 3.0, 24: 3.0/3.2, 25: 3.5). No documented
cautionary fired this cycle (unlike cycle-24's sim+code). The draw was gentler; the one hard
conflict (tight×code) is a clean new cautionary candidate.
