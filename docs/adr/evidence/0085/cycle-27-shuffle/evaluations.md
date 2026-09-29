# ADR-0085 Cycle 27 — Shuffle-Driven Evaluation (stratified; seeds 225/228/230/234/239/240)

**Date:** 2026-09-29
**Evaluators:** single-evaluator (Claude, opus-5)
**Binary:** `bar version dev`, installed binary reinstalled at HEAD 72764a46 (cycles 23-26 edits present; propagation verified)
**Batch:** 6 seeds, **stratified** — first cycle under the amended sampling rule

## Sampling (amended rule applied)

Surveyed seeds 225-240 for channel draw before selecting. That pool had the inverse problem from
cycle 26: 9 of 16 seeds drew NO channel, and the 7 channel-bearing seeds were all distinct.
Selected 6 with **six distinct channels and no repeats** — codetour, formal, aloud, hunk, browse,
code — across 5 distinct tasks (pick, sort, show, fix, diff).

**Channel distribution: 6 seeds / 6 distinct channels / max 1 per channel.** Contrast cycle 26
(3 of 6 seeds = `code`), whose mean was consequently not comparable. This cycle's mean is the
first intended to be comparable across cycles.

Tokens scored for the first time this session: boom, own, facilitate, formal, aloud, hunk,
thrust, socratic, codetour.

## Calibration

Carried forward: (c23) blank-form legitimacy; (c24/25) composition when a coherent output
satisfies both, cautionary only when one starves the other; (c25) description purity —
check whether a token is mis-describing itself before filing a cross-axis entry; (c26)
supplementary content composes adjacently, a whole-response protocol cannot.

## Seed summary

| Seed | task | completeness | scope | method | form | channel | directional |
|------|------|------|------|------|------|------|------|
| 225 | pick | full | — | boom | — | codetour | fip bog |
| 228 | sort | deep | thing | own | facilitate | formal | dip bog |
| 230 | show | full | — | automate | vet | aloud | fly ong |
| 234 | sort | deep | — | — | — | hunk | — |
| 239 | fix | full | thing | thrust | socratic | browse | jog |
| 240 | diff | ration | act | — | — | code | jog |

---

## Seed 225 — pick · full · boom · codetour · fip bog

**Cross-axis:** codetour task natural `[make,fix,show,pull]`, cautionary `[sim,sort]`. `pick`
unlisted → universal rule (channel wins, task becomes content lens).

**Scores:**
- Task clarity: 5 — pick is clear.
- Constraint independence: 2 — **codetour × pick is a deliverable mismatch.** codetour emits a
  `.tour` JSON of *navigable steps through existing files*, "omitting extra prose or surrounding
  explanation". pick requires a committed selection among alternatives. A tour is a walkthrough
  structure; it has no slot for "and therefore I choose B". Under channel-wins this becomes "a
  guided tour of the options" — which never commits, so pick is not satisfied. `boom` (name a
  behavior that differs at high vs low scale, and what breaks at the transition) is a good method
  for a decision, and `fip bog` (all four compass directions) wants breadth a tour can carry.
- Category alignment: 5.
- Combination harmony: 2 — boom+full+fip-bog+pick cohere well as a scale-threshold decision; the
  codetour channel is the single member that cannot host a commitment.
  **Boundary rationale (2 not 3):** this is not attenuation — the task's success condition (a
  named selection) has no expressible location in the artifact. Same shape as cycle-23's
  `agent+diff`, where a constructor channel replaced the deliverable.
- **Overall: 2**

**Notes:** **codetour × pick** — candidate cautionary. Note codetour already cautions `sort` for
a related reason (both `sort` and `pick` produce an *ordering/selection* verdict a step-sequence
cannot express). Extending that existing cautionary to `pick` is a family extension, not a new
mechanism. The universal rule does not rescue it: a tour of options is a different deliverable,
not a reframing of the same one.

---

## Seed 228 — sort · deep · thing · own · facilitate · formal · dip bog

**Cross-axis:** formal task natural `[probe,make,ground]`, no cautionary; `sort` unlisted.
facilitate (form) — no entry.

**Scores:**
- Task clarity: 5 — sort (arrange into categories or order) is clear.
- Constraint independence: 4 — this combination is unusually well-behaved for its size.
  **`facilitate` handles the channel case in its own definition**: "Without an output-exclusive
  channel, acts as a live facilitator; with one, produces a static facilitation guide." `formal`
  IS output-exclusive-ish (separates spec from explanation), so facilitate correctly degrades to
  a static guide — no conflict, because the token anticipated it. `own` (nothing affecting shared
  artifacts) is a *safety* constraint orthogonal to everything else here. `formal`'s
  spec/explanation split suits a categorization (invariants defining each category).
- Category alignment: 5.
- Combination harmony: 4 — sort+thing+deep+formal is strong: categorize the entities, deeply,
  with formal criteria per category. facilitate adds a session structure around it; dip-bog
  grounds it concretely.
  **Boundary rationale (4 not 5):** five modifiers on one task is a lot of simultaneous shaping,
  and `own` does little visible work in a categorization task (nothing here would touch shared
  artifacts) — it is inert rather than conflicting.
- **Overall: 4**

**Notes:** **`facilitate` is a model case for this session's principle** — a form token whose
description states its own channel interaction ("with an output-exclusive channel, produces a
static guide") instead of leaving a latent conflict for a cross-axis entry to patch. Worth citing
as the positive exemplar of format-neutral definition. No action.

---

## Seed 230 — show · full · automate · vet · aloud · fly ong

**Cross-axis:** aloud (channel) — no entry. vet (form) — no entry.

**Scores:**
- Task clarity: 5 — show is clear.
- Constraint independence: 3 — **vet × aloud tension.** vet structures output as a
  post-experiment review with four analytic parts (what the transcript showed, comparison to
  prior prediction, what can be derived, what follows) — and explicitly requires "naming null
  results as gaps, not as disconfirmation", a precise distinction. aloud delivers via TTS and
  mandates condensing to "spoken-word density — strip code blocks, raw URLs, and long
  enumerations; summarize rather than truncate". vet's four-part analytic structure with its
  careful null-result distinction is exactly the kind of precision that spoken condensation
  erodes. Not a hard collision — a spoken review is possible — but the form's discriminations are
  at risk. `automate` (prefer repeatable operations) over a spoken explanation is mildly odd but
  fine.
- Category alignment: 5.
- Combination harmony: 3 — show+full+fly-ong+vet cohere; aloud is the pressure. **Boundary
  rationale (3 not 4):** `full` (every named element at one depth) and aloud's condensation
  requirement pull in opposite directions too — that is a *second* strain on the same channel, so
  not a clean 4.
- **Overall: 3**

**Notes:** Two candidates, both pattern-watch (single seed): (1) **aloud × analytic multi-part
forms** (vet, prep) — spoken density erodes fine distinctions; (2) **aloud × full/max
completeness** — a spoken response cannot carry exhaustive coverage. The second is the same
*completeness-floor-vs-channel* shape as the shipped `presenterm+max/deep` cautionary, so aloud
plausibly warrants a completeness cautionary. Flagged, not acted (one seed).

---

## Seed 234 — sort · deep · hunk

**Cross-axis:** hunk (channel) — no entry. Minimal seed: one task, one completeness, one channel.

**Scores:**
- Task clarity: 5 — sort is clear.
- Constraint independence: 3 — **hunk × sort.** hunk delivers "via a live Hunk diff review
  session", requiring the agent to run `hunk skill path`, read the embedded skill, and follow its
  workflow; if no session exists, ask the user to launch one. It is a *diff review* medium — its
  content unit is a change hunk. `sort` arranges items into categories or order. Sorting is not a
  diff, so the medium supplies no natural carrier for a categorization; under channel-wins this
  becomes "review a diff, arranged by category", which is derivable (group the hunks) but reframes
  sort's subject from arbitrary items to diff hunks. `deep` composes fine.
- Category alignment: 5.
- Combination harmony: 3 — with only three tokens there is little to conflict; the strain is the
  single channel/task pairing. **Boundary rationale (3 not 2):** the reframe ("group the hunks by
  category") is genuinely available and useful, unlike seed 225's codetour+pick where no
  expressible location existed for the verdict.
- **Overall: 3**

**Notes:** hunk is a **delivery-mechanism channel** (per the three-way taxonomy in nn
20260717011133-2169: format / delivery-mechanism / constructor) with no cross-axis entry at all.
Its content unit (a diff hunk) constrains which tasks fit naturally — make/fix/check/pull suit it;
sort/pick/sim do not. Candidate: a hunk cross-axis entry with a natural task list. Single seed;
deferred consistent with how ledger+pick and table+pick were handled.

---

## Seed 239 — fix · full · thing · thrust · socratic · browse · jog

**Cross-axis:** **`browse+fix` composition FIRES** (shipped cycle-25). socratic cautions
`shellscript`/`codetour`, not `browse`. thrust (method) — no entry.

**Scores:**
- Task clarity: 5 — fix is clear.
- Constraint independence: 2 — **socratic × browse is the load-bearing conflict.** socratic
  "interrogates the user's stated or implied position", and before any question must "name the
  specific claim, belief, or reasoning step from the user's input that will be examined — if no
  such claim is identifiable, state this before proceeding". That is a *dialogue with the user*.
  browse is "enacted by driving a browser ... rather than displayed inline" — the response acts on
  an external target, not on the user's claims. These operate on different objects: socratic needs
  the user's asserted position; browse produces browser actions. This is the `interactive`-shaped
  case — a whole-response dialogue protocol vs an enacted channel — except socratic is *not*
  rescued by artifact-carries-the-state, because its subject is the user's reasoning, not an
  artifact. `thrust` (catalog competing structural forces) suits `fix` well; `thing` scopes it.
- Category alignment: 5.
- Combination harmony: 2 — fix+thrust+thing+full+browse cohere (fetch, then reformat around the
  competing forces — and the shipped `browse+fix` composition supplies the sequencing). socratic
  is the member with no coherent place.
  **Boundary rationale (2 not 3):** socratic's precondition (name a claim from the user's input)
  cannot be satisfied by a browser-driving response; it is not attenuated but unsatisfiable.
- **Overall: 2**

**POST-APPLY VALIDATION (ADR step 12, standing):** the shipped `browse+fix` composition fired
correctly on this seed — confirming a cycle-25 edit is live and active in the installed binary.
This is the intended use of a later cycle to validate an earlier one's edits.

**Notes:** **socratic × enacted channels (browse, and by the same logic github/store/zettel).**
socratic already cautions shellscript/codetour on format grounds; the deeper issue is that
socratic requires a *user position to interrogate*, which an enacted/delivery channel does not
provide. Candidate: extend socratic's channel cautionary to enacted channels — a family extension
with a sharper stated reason than the existing format-based entries.

---

## Seed 240 — diff · ration · act · code · jog

**Cross-axis:** code task natural `[make,fix,show,pulse,pull,check]`, caut `[sim,probe]`; `diff`
unlisted → universal rule.

**Scores:**
- Task clarity: 5 — diff (compare for the reader to decide) is clear.
- Constraint independence: 3 — **diff × code.** code emits only code/markup. A comparison for a
  reader to weigh is prose-shaped reasoning; under channel-wins this becomes "express the
  comparison as code" — e.g. parallel implementations, or a table in a comment block. Derivable
  and sometimes genuinely good (comparing two approaches by showing both), so not a hard
  collision. **`ration`** (allocate depth by a named situational score, naming the score, and
  naming why each shallow part is shallow) requires *prose justification* — "for each part left at
  minimal or zero depth, the response names its low score as the reason" — which code-only output
  cannot host. Per this session's finding, the mandated derivation/interpretation scaffold gives
  that prose a home, so it is not fatal.
- Category alignment: 5.
- Combination harmony: 3 — diff+act+jog is coherent (compare what is being done); ration and code
  each pull mildly. **Boundary rationale (3 not 2):** both strains have available resolutions (show
  both implementations; put ration's score justification in the scaffold), unlike seeds 225/239.
- **Overall: 3**

**Notes:** `diff` is absent from code's natural AND cautionary lists. Given `code` naturally hosts
`make/fix/show/pull/check`, and a two-implementation comparison is a real use, `diff` is arguably
natural for code. Single seed — pattern-watch. Also mild: **ration × artifact-only channels** need
the scaffold for their score justification; covered by the scaffold finding, no action.

---

## Cycle score summary

| Seed | Channel | Overall | Load-bearing issue |
|------|------|---------|--------------------|
| 228 | formal | **4** | clean — facilitate anticipates the channel case in its own definition |
| 230 | aloud | 3 | vet's analytic distinctions vs spoken density; full vs condensation |
| 234 | hunk | 3 | hunk's content unit is a diff hunk; sort has no natural carrier |
| 240 | code | 3 | diff×code derivable; ration's justification needs the scaffold |
| 225 | codetour | 2 | pick's verdict has no expressible location in a `.tour` |
| 239 | browse | 2 | socratic needs a user position; browse acts on an external target |

**Mean: 2.83 / 5** across 6 distinct channels.

**On comparability:** this is the first stratified cycle, so it is also the first mean intended to
be compared. It happens to equal cycle 26's 2.83 — but cycle 26's was produced by one channel
appearing 3 times, while this one spans six distinct channels at one seed each. The equality is
coincidence; only this cycle's figure is a meaningful baseline.

**What stratification bought:** six channels scored instead of effectively three, and it surfaced
that **four channels have no cross-axis entry at all** (aloud, hunk, browse, and previously
ledger/notebook) — a coverage gap that sequential sampling had been hiding by repeatedly drawing
the same well-documented channels.
