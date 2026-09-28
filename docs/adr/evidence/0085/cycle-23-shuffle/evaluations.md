# ADR-0085 Cycle 23 — Shuffle-Driven Evaluation (seeds 0201–0206)

**Date:** 2026-09-28
**Evaluators:** single-evaluator (Claude, opus-4-8)
**Binary version:** `bar version dev` (built from dev repo HEAD 4f635162 — no release lag)
**Batch:** 6 seeds (small rapid cycle)
**Phases run:** Phase 1 (generate), Phase 2 (score vs prompt key), Phase 2b/2c (meta-eval skills + bar help llm), Phase 2e (distinction check), Phase 2d (process self-eval)

## Calibration (single-evaluator)

Single-evaluator cycle. Boundary rationale captured inline per seed. Limitation noted in
this header per Phase 0. No 24h re-score gap available in an interactive session — scores
below carry single-evaluator uncertainty, flagged where a boundary is close (3-vs-4).

---

## Seed summary

| Seed | task | completeness | scope | method | form | channel | directional | topology |
|------|------|------|------|------|------|------|------|------|
| 201 | pick | full | struct | experimental | — | adr | — | — |
| 202 | plan | full | mean | — | template | — | — | live |
| 203 | pull | deep | — | — | — | browse | fly ong | relay |
| 204 | diff | full | struct | — | — | agent | — | — |
| 205 | plan | full | — | — | — | — | — | witness |
| 206 | fix | max | — | paradox | storyboard | github | — | — |

---

## Seed 201 — pick · full · struct · experimental · adr

**Request:** "The response chooses one or more options from a set of alternatives."

**Cross-axis composition check:**
- adr (channel) natural tasks = `['plan','probe','make']`; cautionary = `['sim']`. `pick` is
  **unlisted** (neither natural nor cautionary). Apply universal rule: channel wins, task
  becomes content lens. adr's Description says "Best suited for decision-making tasks and
  architectural tradeoffs" — `pick` IS a decision task, so the reframe is not just derivable,
  it is the token's stated sweet spot. → treat as natural-equivalent.
- adr completeness natural = `['full','deep']` — `full` is listed natural. ✓

**Scores (vs prompt key):**
- Task clarity: 5 — pick states a clear success condition (a choice is made).
- Constraint independence: 4 — `experimental` (propose runnable tests) sits oddly against a
  pure selection task: choosing an option and designing experiments to validate it are
  adjacent but not the same. It shapes HOW (justify the pick via proposed tests) without
  redefining WHAT, so it holds, but strained.
- Persona coherence: N/A (no persona preset; voice/audience/tone are separate axes here).
- Category alignment: 5 — every token in its stated axis.
- Combination harmony: 4 — pick+adr+struct+full cohere well (a decision recorded as an ADR,
  focused on structural tradeoffs, thorough). `experimental` is the one strained member:
  an ADR's "Consequences" section can absorb "how we'd validate this decision," so it's
  derivable, but a reader could reasonably expect a decision artifact not to prescribe test
  designs. **Boundary rationale (4 not 5):** the reframe is derivable but requires the reader
  to route experimental into the ADR's consequences section rather than it fitting natively.
- Method category coherence: N/A (single method token).
- **Overall: 4**

**Notes:** Coherent, useful combination. The pick→adr pairing is a genuinely good one that
adr's own description endorses but its `natural` task list omits (`pick` missing from
`['plan','probe','make']`). Candidate: add `pick` to adr's natural task list.

---

## Seed 202 — plan · full · mean · template · live

**Request:** "The response proposes steps, structure, or strategy to move toward a goal."

**Cross-axis composition check:**
- template (form) paired channel: natural=`['plain','slack','html']`, cautionary=`['shellscript','codetour','gherkin']`.
  No channel token selected → no cross-axis conflict on the channel side.
- template vs task(plan): no cautionary entry. Universal rule N/A (no channel). Evaluate on merits.

**Scores (vs prompt key):**
- Task clarity: 5 — plan has a clear success condition.
- Constraint independence: 3 — **template + plan is in tension.** template's Description:
  "every content position is a labeled slot ... no slot is pre-filled ... prose content
  outside slot positions is not [permitted]." A plan (steps/strategy toward a goal) is
  inherently prose-and-sequence content. Forcing plan output into an empty fill-in-the-blank
  artifact means the LLM produces a *plan template* (labeled empty slots like [Milestone],
  [Owner], [Risk]) rather than an actual plan. That is a legitimate output ("give me a
  planning template") but template here *redefines WHAT* from "produce a plan" to "produce a
  blank planning form." This is the classic form-overrides-task tension.
- Category alignment: 5.
- Combination harmony: 3 — plan+full+mean+template: `full` (thorough) and `template` (empty
  slots) also pull against each other — a template is defined by *absence* of filled content,
  so "thorough coverage" applies to slot enumeration, not content. Derivable (a thorough
  template names every slot a plan would need) but strained. `live` topology (externalize
  states per-segment) over an empty template is nearly inert — there's little live reasoning
  to externalize when the output is blank slots.
  **Boundary rationale (3 not 2):** the reframe *is* recoverable (a comprehensive planning
  template), so it's not broken; but multiple tokens (full, live) do reduced work under
  template's emptiness constraint, so it's not a clean 4.
- Method category coherence: N/A.
- **Overall: 3**

**Notes:** This surfaces a real form-as-lens question: **does template override task the way a
channel does?** template is a form token, and forms are supposed to organize *within* the
task's content, not empty it out. template is unusual — it's the one form token whose
definition mandates *absence* of content. That makes it behave more like a channel (it
dictates the artifact type) than a form. Candidate finding for help-llm / cross-axis docs:
template + generative-task (plan/make/show) needs a form-as-lens note.

---

## Seed 203 — pull · deep · browse · fly-ong · relay

**Request:** "The response selects or extracts a subset of the given information without altering its substance."

**Cross-axis composition check:**
- browse (channel): no CROSS_AXIS entry. browse Description: "The response is enacted by
  driving a browser through the `agent-browser` CLI ... a bidirectional target the response
  may read from or act on." Universal rule: channel wins.
- pull (task) = "Extracting a subset of information from source material."

**Scores (vs prompt key):**
- Task clarity: 5 — pull is clear.
- Constraint independence: 2 — **browse + pull conflict.** pull operates on *given* source
  material ("selects or extracts a subset of the given information"). browse *fetches* content
  by driving a live browser. Under the universal rule (channel wins), this reframes to "drive
  a browser to fetch pages, then extract a subset" — which is coherent as a *fetch-then-extract*
  task, BUT pull's definition specifically says "without altering its substance" applied to
  "the given information." browse supplies no given information; it goes and gets it. The
  reframe changes pull from "extract from what I gave you" to "go find, then extract," which
  is closer to a research/probe task than pull.
- Category alignment: 5.
- Combination harmony: 2 — `deep` (substantial depth, unpack reasoning layers) fights `pull`
  (extract subset without altering substance — a *compression* operation, not a depth
  operation). deep wants to unpack; pull wants to select and compress. `fly-ong` (abstract +
  acting) over an extraction task pushes toward "principles + what to do," but pull is neither
  abstracting nor acting — it's selecting. `relay` topology (another party continues
  mid-stream) over a browser-driven extraction is plausible (hand off the fetched subset) but
  adds little.
  **Boundary rationale (2 not 3):** three tokens (deep, fly-ong, and arguably relay) each pull
  against pull's core "select and compress verbatim" operation. The reframe requires
  overriding pull's "given information" and "without altering substance" clauses. That's more
  than "one token feels forced" (a 3) — it's a combination where the task's defining
  constraints are contradicted by the modifiers.
- **Overall: 2**

**Notes:** Two independent tensions worth recording:
1. **pull + deep** — completeness `deep` (unpack layers) vs task `pull` (compress a subset).
   These are near-opposite operations. Compare-mode candidate.
2. **pull + browse** — task assumes *given* material; channel *fetches* material. Candidate
   cautionary or a note that browse reframes pull into fetch-then-extract.

---

## Seed 204 — diff · full · struct · agent

**Request:** "The response compares two or more subjects by naming similarities, differences, or tradeoffs."

**Cross-axis composition check:**
- agent (channel): no CROSS_AXIS entry. agent Description: "The response is structured as an
  agent definition — a persistent autonomous subprocess specification with YAML frontmatter
  ... Formatted for direct use as an agent configuration." Universal rule: channel wins.

**Scores (vs prompt key):**
- Task clarity: 5 — diff is clear.
- Constraint independence: 1 — **agent + diff is a hard conflict.** agent (channel) mandates
  the output BE an agent-definition file (YAML frontmatter: name, tools, trigger; body of
  behavior; ends with "Write to disk"). diff (task) asks for a comparison of subjects for the
  reader to decide. Under the universal rule, channel wins → the output must be an agent
  definition, and diff becomes the *content lens*: "define an agent whose job is to compare
  subjects." That IS derivable (an agent spec for a comparison agent), but it completely
  transforms the request: the user asked to compare X and Y and instead gets a subprocess
  spec for a comparison-bot. The comparison itself is never delivered — only a spec for a
  thing that would do comparisons.
- Category alignment: 5.
- Combination harmony: 2 — under the universal rule the reframe is *technically* derivable
  (an agent that performs diffs), so it is not a 1 on harmony; but `full` and `struct` then
  apply to the agent spec, not to any actual comparison, so they do displaced work.
  **Boundary rationale (constraint independence = 1):** unlike template (which produces a
  usable planning artifact), agent+diff produces an artifact of a *categorically different
  kind* than the task requested — the reader who wanted a comparison gets an agent config.
  The channel doesn't just reshape the comparison; it replaces the deliverable.
- **Overall: 2**

**Notes:** `agent` is a "constructor" channel — like `skill`, it turns the task into a *spec
for a tool that would perform the task*, not the task's output. This is a general pattern:
constructor channels (agent, skill) applied to analysis/comparison tasks (diff, probe, show)
produce a spec, not an analysis. Candidate: cross-axis note for agent+analysis-tasks, or a
general "constructor channel" note in help-llm's Choosing Channel section.

---

## Seed 205 — plan · full · witness

**Request:** "The response proposes steps, structure, or strategy to move toward a goal."

**Cross-axis composition check:** no channel/form tokens; topology only. No cross-axis entry.

**Scores (vs prompt key):**
- Task clarity: 5 — plan is clear.
- Constraint independence: 5 — witness (name each assumption + its epistemic basis before any
  dependent conclusion) shapes HOW a plan is presented (each step names its assumption) without
  redefining WHAT. `full` sets breadth. Clean.
- Category alignment: 5.
- Combination harmony: 5 — plan+full+witness is a genuinely strong combination: a thorough
  plan where every step surfaces its assumptions before committing. This is exactly the
  "long-horizon planning" use case witness's heuristics name.
- Method category coherence: N/A.
- **Overall: 5**

**Notes:** Clean baseline. witness+plan is a natural, high-value pairing. No action.

---

## Seed 206 — fix · max · paradox · storyboard · github

**Request:** "The response changes the form or presentation of given content while keeping its intended meaning."

**Cross-axis composition check:**
- github (channel): no CROSS_AXIS entry. Description: "delivered to GitHub via `gh` CLI ...
  format output as GitHub Flavored Markdown." Universal rule: channel wins (delivery medium).
- storyboard (form): no entry. paradox (method): no entry. max (completeness): no entry.

**Scores (vs prompt key):**
- Task clarity: 5 — fix (reformat existing content, keep meaning) is clear.
- Constraint independence: 2 — **paradox + fix is a category conflict.** paradox (method):
  "holds the subject as an unresolved generative tension ... Synthesis, resolution, and
  explanation are not valid closing moves." fix (task): reformat content while *keeping its
  intended meaning*. Reformatting is a convergent, meaning-preserving operation; paradox is a
  divergent, meaning-*problematizing* stance. Applying paradox to a reformat task means:
  reformat the content while refusing to resolve its tensions — but a reformat by definition
  preserves meaning and doesn't introduce or hold tensions. The two operate on different
  objects. Derivable only by straining ("reformat in a way that preserves the content's
  internal contradictions") — weak.
- Category alignment: 4 — all tokens in their axes, but paradox is a Diagnostic/Exploration-
  flavored method applied to a mechanical transformation task (fix), so its *category* is
  mismatched to the task even though its *axis* is correct.
- Combination harmony: 2 — storyboard (numbered Scene/Narration panels) as the form for a
  *reformat* is plausible (reformat content INTO a storyboard). But storyboard + paradox
  fight: storyboard demands a resolved, sequential narrative arc ("No panel references an
  entity ... not introduced in an earlier panel" — a coherent progression); paradox forbids
  resolution. A storyboard that holds unresolved tension across its panels is possible but the
  form's "designed presentational sequence" pushes toward closure that paradox forbids.
  `max` (exhaustive, omissions are errors) over a reformat is odd — reformatting has no
  "elements to exhaustively cover"; it transforms whatever is given.
  **Boundary rationale (2 not 1):** each pair is individually *just barely* derivable, so no
  single hard contradiction (which would be a 1) — but three separate strained pairings
  (paradox×fix, storyboard×paradox, max×fix) compound into a combination that fights itself.
- Method category coherence: N/A (single method).
- **Overall: 2**

**Notes:** The load-bearing tension is **paradox × fix (and paradox × any transformation
task).** paradox is a method for sitting with irresolvable tension; fix/make/reformat are
convergent production tasks. Compare-mode candidate: does paradox produce distinguishable,
useful output on a transformation task, or is it inert/incoherent there? Also **max × fix**:
completeness `max` presupposes a subject with enumerable elements; a reformat task has no such
element set. Minor.

---

## Cycle score summary

| Seed | Overall | Load-bearing issue |
|------|---------|--------------------|
| 201 | 4 | experimental strained against pick (minor); adr natural-list omits pick |
| 202 | 3 | template empties a generative task (plan); form-as-channel behavior |
| 203 | 2 | pull+deep opposite operations; browse fetches vs pull's "given" material |
| 204 | 2 | agent is a constructor channel — replaces diff's deliverable with a spec |
| 205 | 5 | clean (witness+plan baseline) |
| 206 | 2 | paradox×fix category conflict; storyboard×paradox; max×fix |

**Mean: 3.0 / 5** (single-evaluator)

Lower than recent cycles (cycle-22 ~4.04, cycle-23-topology ~4.125) — expected, because these
seeds happened to draw several channel/form tokens that override or transform their tasks
(adr, browse, agent, template, github), plus one method×task category conflict (paradox×fix).
That is the sampling drawing the exact edge cases ADR-0085 exists to surface, not a regression.
