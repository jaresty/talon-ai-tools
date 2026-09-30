# ADR-0085 Cycle 29 — Stratified Evaluation (seeds 263/269/274/276/281/283)

**Date:** 2026-09-29
**Evaluator:** single-evaluator (Claude, opus-5)
**Binary:** reinstalled at HEAD d2326f5b via `make bar-install` — includes every cycle 23-28 edit plus
today's constructor/delivery channel entries, so this cycle doubles as post-apply validation of them.
**Batch:** 6 seeds, stratified — **third** stratified cycle (c27 = 2.83, c28 = 2.83 baseline)

## Sampling

Surveyed seeds 263-284. `jira` appeared 3×, `code`/`html`/`image` 2× each — stratification mattered.
Selected 6 with **5 distinct channels plus 1 channel-free**, favouring channels this session had not
scored: agent, draw, ledger, notion, jira. Six distinct tasks (sim, probe, sort, diff, pick, plan).

First-time-scored tokens: fourfold, cluster, draw, axiom, slides, zoom, time.

## Seed summary

| Seed | task | completeness | scope | method | form | channel | directional |
|---|---|---|---|---|---|---|---|
| 263 | sim | deep | — | fourfold | facilitate | — | ong |
| 269 | probe | grow | lever | cluster | cards | agent | — |
| 274 | sort | gist | thing | — | — | draw | dip bog |
| 276 | diff | full | mean | — | — | ledger | — |
| 281 | pick | full | — | adversarial | axiom | notion | — |
| 283 | plan | zoom | time | — | slides | jira | dip ong |

---

## Seed 263 — sim · deep · fourfold · facilitate · ong

**Cross-axis:** no channel. facilitate — no entry (and needs none; see below).

**Scores:**
- Task clarity: 5 — sim (play out a scenario over time) is clear.
- Constraint independence: 5 — **facilitate handles the channel case in its own definition**
  ("Without an output-exclusive channel, acts as a live facilitator; with one, produces a static
  facilitation guide"), and with no channel present it correctly takes the live-facilitator reading.
  `fourfold` (exhaust the logical stance space — affirmative, negation, both, neither) suits a
  simulation well: four stance branches of how a scenario could play out. `deep` unpacks each; `ong`
  orients toward what to do next.
- Category alignment: 5.
- Combination harmony: 5 — sim+fourfold+facilitate+deep+ong is genuinely strong: facilitate a session
  that plays the scenario out across all four stance positions, in depth, ending in actions.
- **Overall: 5**

**Notes:** Second cycle in which `facilitate` scored at the top (c27 seed 228 was 4/5). Its
self-describing channel clause keeps paying — it is the positive exemplar for format-neutral
definitions (c27-O1). No action.

---

## Seed 269 — probe · grow · lever · cluster · cards · agent

**Cross-axis:** **`agent` cautions `probe`** — the constructor-channel entry added earlier TODAY,
firing on a fresh random draw. Score but **exclude from retirement aggregation**.

**Scores:**
- Task clarity: 5 — probe is clear.
- Constraint independence: 2 — the documented constructor substitution: `agent` mandates an agent
  definition (YAML frontmatter, tools, trigger, "Write to disk"), so probe's analysis is replaced by
  a *spec for a probing agent*. The reader asked for analysis and receives a subprocess
  configuration. `cluster` (group existing items by shared characteristics without altering them) and
  `cards` (discrete headed items) would both suit a probe well; `lever` (intervention points) is a
  strong probe scope; `grow` expands only where justified.
- Category alignment: 5.
- Combination harmony: 2 (flagged cautionary — **excluded from aggregation**) — five tokens cohere as
  a clustered intervention-point analysis in cards; `agent` is the single member that replaces the
  deliverable.
- **Overall: 2** (cautionary — excluded)

**POST-APPLY VALIDATION:** the `agent`×`probe` cautionary shipped hours earlier in this session fired
correctly on an independent random draw. This is the third organic post-apply confirmation (c27
validated browse+fix, c28 validated skim/gist directional entries).

---

## Seed 274 — sort · gist · thing · draw · dip bog

**Cross-axis:** **`gist` cautions `dip-bog`** (compound directional vs brief summary) — documented;
exclude from aggregation. `draw` — **no entry**.

**Scores:**
- Task clarity: 5 — sort (arrange into categories or order) is clear.
- Constraint independence: 3 — two interactions. (a) The documented **gist × dip-bog**: a compound
  directional spanning concrete + structural + acting cannot fit a short summary. (b) **draw × sort
  is actually GOOD**: draw is "a spatial prose layout using ASCII arrangement, boxes, arrows,
  indentation, and a short legend" — a categorization is naturally expressible as a spatial grouping,
  and `thing` (what entities are in view) gives draw exactly the nodes to lay out. That pairing
  raises the score rather than lowering it.
- Category alignment: 5.
- Combination harmony: 3 (flagged cautionary) — sort+thing+draw is a strong core; gist+dip-bog is the
  documented conflict.
- **Overall: 3** (cautionary — excluded)

**Notes:** **`draw` is a candidate natural pairing for sort/diff/show** — spatial ASCII layout suits
categorization, comparison, and structural explanation. draw has no cross-axis entry. Single seed, so
recorded as a candidate rather than acted on, consistent with how ledger/table/notebook were handled.

---

## Seed 276 — diff · full · mean · ledger

**Cross-axis:** ledger natural = `[pick, plan]` (added earlier today); `diff` is **unlisted** →
universal rule. This directly tests whether that natural list was drawn too narrowly.

**Scores:**
- Task clarity: 5 — diff (compare for the reader to decide) is clear.
- Constraint independence: 4 — ledger writes under four fixed headings (Facts, Decisions,
  Constraints, Open Questions) and emits only content fitting them. A comparison maps on well:
  the compared attributes are Facts, the tradeoffs are Constraints, what the comparison cannot settle
  is Open Questions. What it lacks is a *Decisions* entry — `diff` deliberately leaves the choice to
  the reader, so that heading stays empty. Coherent, with one structurally vacant heading.
  `mean` (conceptual framing) and `full` fit.
- Category alignment: 5.
- Combination harmony: 4 — **Boundary rationale (4 not 5):** everything composes, but one of
  ledger's four fixed headings has nothing to receive, which is a mild structural idle.
- **Overall: 4**

**Notes:** **My `[pick, plan]` natural list for ledger was too narrow.** `diff` scores 4/5 — it
populates three of four headings and its only gap is the *deliberate* one (diff withholds the
decision). Candidate: add `diff` to ledger's natural task list; consider `check` too (verdicts are
Facts + Open Questions). Recorded as a correction to today's own entry, not a new defect.

---

## Seed 281 — pick · full · adversarial · axiom · notion

**Cross-axis:** notion natural = `[make, show, pull, check]` (added today); `pick` unlisted →
universal rule. axiom — no entry.

**Scores:**
- Task clarity: 5 — pick is clear.
- Constraint independence: 4 — `notion` is a bidirectional delivery target, so it constrains where
  output goes rather than what it is: a decision posts to Notion fine. **`axiom` + `pick` is the
  interesting pairing**: axiom structures content as "a named set of axioms over a given vocabulary:
  each axiom stated as a constraint, paired with a brief note naming the class of interpretation it
  rules out." For a selection task that reads as: state the constraints the choice must satisfy, each
  ruling out a class of candidate — which is a *genuinely strong* way to justify a pick.
  `adversarial` (name failure categories, then instances) pressure-tests the choice.
- Category alignment: 5.
- Combination harmony: 4 — pick+axiom+adversarial+full+notion cohere: constrain the decision space
  axiomatically, adversarially test it, commit, post it. **Boundary rationale (4 not 5):** axiom's
  vocabulary requirement means the pick must be expressible over a named vocabulary, which is a real
  precondition the combination does not guarantee.
- **Overall: 4**

**Notes:** `pick` is arguably natural for notion (a recorded decision is a normal Notion artifact) —
same correction shape as seed 276's ledger finding. Also **axiom+pick reads as a good pairing**
(constraints-that-rule-out as decision justification); axiom has no entry.

---

## Seed 283 — plan · zoom · time · slides · jira

**Cross-axis:** `jira` — **no entry, deliberately** (today's delivery-channel pass classified it as a
pure formatting convention imposing no capacity or target constraint). This tests that judgment.
`slides` and `zoom` — no entries.

**Scores:**
- Task clarity: 5 — plan is clear.
- Constraint independence: 3 — **`zoom` × `slides` is a real capacity interaction.** zoom "covers the
  full range of the subject by treating it as exponentially-spaced buckets from smallest natural unit
  to largest. Each bucket receives substantive coverage." slides organizes as discrete self-contained
  units. These actually compose *well* structurally (one bucket per slide is a natural mapping) — but
  zoom's "substantive coverage" per bucket across an exponential range pushes toward many slides,
  which is the capacity tension `presenterm` already cautions for max/deep. `jira`'s formatting
  convention composes with everything, confirming today's no-entry judgment. `time` scope suits both
  plan and zoom (temporal buckets).
- Category alignment: 5.
- Combination harmony: 3 — plan+time+zoom+slides is coherent (a plan laid out over exponentially
  spaced time horizons, one per slide) with `dip ong` grounding it in concrete next actions.
  **Boundary rationale (3 not 4):** the bucket-count pressure is real but derivable — the response can
  choose fewer buckets — so it is a strain, not a conflict.
- **Overall: 3**

**Notes:** Two findings. (1) **`jira` needing no entry is CONFIRMED** — it composed with a
five-token combination without friction, validating today's deliberate omission. (2) **`zoom` ×
slide-like channels** is a capacity-family candidate (same shape as presenterm×max/deep): an
exponential bucket range pushes unit count. Single seed; pattern-watch.

---

## Cycle score summary

| Seed | Channel | Overall | Load-bearing issue |
|---|---|---|---|
| 263 | — | **5** | clean — facilitate's self-describing clause again |
| 276 | ledger | 4 | diff populates 3 of 4 ledger headings — my natural list was too narrow |
| 281 | notion | 4 | axiom+pick reads as a good pairing; pick arguably natural for notion |
| 274 | draw | 3 | documented gist×dip-bog (excluded); draw×sort is GOOD |
| 283 | jira | 3 | zoom×slides bucket-count pressure; jira no-entry confirmed |
| 269 | agent | 2 | documented agent×probe constructor substitution (excluded) |

**Mean (all 6): 3.50 / 5.**
**Mean excluding the two flagged cautionaries (269, 274): 4.00 / 5** (4 qualifying seeds).

## Comparison across the three stratified cycles

| | c27 | c28 | c29 |
|---|---|---|---|
| Distinct channels | 6 | 6 | 5 + 1 channel-free |
| Mean (all) | 2.83 | 2.83 | **3.50** |
| Mean (excl. flagged) | 3.0 | 3.25 | **4.00** |
| Documented cautionaries fired | 1 | 2 | 2 |

**This is the first cycle to move the baseline.** c27 and c28 both sat at 2.83; c29 is 3.50, and 4.00
excluding flagged pairs. Two candidate explanations, and I cannot separate them from one cycle:
(a) the catalog genuinely improved — ~30 entries were added or corrected today, including the
constructor and delivery-channel coverage that two of these seeds exercised; (b) draw luck, since this
batch included a channel-free seed and two channels (`draw`, `jira`) that impose little.

The honest read is that a single cycle cannot distinguish improvement from variance, and c27/c28
agreeing at 2.83 was itself partly coincidence. One data point above baseline is a hypothesis, not a
trend.
