# ADR-0085 Cycle 31 — Matched-Design Evaluation (seeds 314/317/318/319/331/333)

**Date:** 2026-09-30
**Evaluator:** single-evaluator (Claude, opus-5)
**Binary:** reinstalled at HEAD 7cedd81e via `make bar-install`
**Batch:** 6 seeds, **all channel-bearing, 6 distinct channels** — design matched to c27/c28

## Pre-committed test condition

c29 (3.50) and c30 (3.67) both beat the c27/c28 baseline of 2.83, but c30 had only 4 channel-bearing
seeds and I flagged at the time that this cut against comparability — channel tokens are the most
constraining class, so a batch with two channel-free seeds has less to conflict with.

**The stated clean test was a cycle at 6 distinct channel-bearing seeds.** This is that cycle, and the
design was fixed before any seed was scored. If the mean lands near 2.83, the earlier lift was largely
sampling; if near 3.5-3.7, the improvement hypothesis holds under matched conditions.

## Sampling

Surveyed seeds 307-336, found 14 channel-bearing, selected 6 with distinct channels favouring those
never scored this session: **skill, draw, demo, video, canvas, remote**. Four of the six (demo, video,
canvas, remote) are first-time-scored, and five of six have **no cross-axis entry at all**.

First-time-scored tokens: demo, video, canvas, remote, operations, dig.

## Seed summary

| Seed | task | completeness | scope | method | form | channel | directional |
|---|---|---|---|---|---|---|---|
| 314 | check | full | — | — | ghost | skill | dig |
| 317 | diff | gist | — | — | — | draw | fly ong |
| 318 | sort | full | thing | operations | ghost | demo | bog |
| 319 | pull | narrow | jobs | — | story | video | — |
| 331 | check | zoom | — | analog | — | canvas | jog |
| 333 | plan | full | assume | adversarial | — | remote | rog |

---

## Seed 314 — check · full · ghost · skill · dig

**Cross-axis:** skill task natural=`[make]`, cautionary=`[probe, diff, show]`; `check` is **unlisted**
→ universal rule. This tests whether the constructor cautionary list I added yesterday was drawn too
narrowly.

**Scores:**
- Task clarity: 5 — check (evaluate against a condition, report pass/fail) is clear.
- Constraint independence: 2 — **`check` belongs in skill's cautionary list.** skill is a constructor
  channel: it mandates a reusable skill definition (YAML frontmatter, workflow steps, one worked
  example). Paired with check, the output is a *spec for a checking skill*, not the verdict. That is
  exactly the deliverable substitution the existing `probe`/`diff`/`show` entries describe — a check
  produces a pass/fail judgment, and the reader receives a reusable definition instead. `ghost` (a
  workflow execution trace: action taken, result observed) would suit a check well; `dig` grounds it
  in specifics.
- Category alignment: 5.
- Combination harmony: 2 — check+ghost+full+dig cohere strongly as a grounded verification trace;
  skill substitutes the deliverable. **Boundary rationale (2 not 3):** the verdict has no expressible
  location in a skill definition, the same as the cautioned cases.
- **Overall: 2**

**Notes:** **My constructor cautionary list was too narrow — the third instance of the single-seed
under-drawing lesson (c29 ledger, c30 ledger, now c31 skill/agent).** The pattern is confirmed enough
to act on differently: rather than add `check` alone, enumerate the task axis against the constructor
content unit, as c30-R1 did for ledger. Candidate covers skill, agent and image together, since all
three are constructor channels sharing one mechanism.

---

## Seed 317 — diff · gist · draw · fly ong

**Cross-axis:** **`gist` cautions `fly-ong`** (compound directional vs brief summary) — documented;
exclude from aggregation. `draw` — no entry.

**Scores:**
- Task clarity: 5 — diff is clear.
- Constraint independence: 3 — the documented **gist × fly-ong** conflict: a compound directional
  spanning abstract + acting cannot be delivered in a short summary. But **draw × diff is GOOD**: draw
  is "a spatial prose layout using ASCII arrangement, boxes, arrows, indentation, and a short legend",
  and a comparison laid out spatially — two columns, shared attributes aligned — is a natural and
  useful rendering. This is the second cycle running where draw raised rather than lowered a score
  (c29 seed 274 had draw×sort).
- Category alignment: 5.
- Combination harmony: 3 (flagged cautionary) — diff+draw is a strong pairing; gist+fly-ong is the
  documented conflict.
- **Overall: 3** (cautionary — excluded)

**Notes:** **`draw` × `diff` is now the second good draw pairing across two cycles** (draw×sort in c29).
draw still has no cross-axis entry. Two independent seeds is past the single-seed bar that c29/c30
established as insufficient — this is now actionable rather than pattern-watch.

---

## Seed 318 — sort · full · thing · operations · ghost · demo · bog

**Cross-axis:** `demo` — no entry. demo: "produces a pull request evidence artifact. The output must
contain, as literal text: (1) the action taken, and (2) the result as it appeared when captured."

**Scores:**
- Task clarity: 5 — sort is clear.
- Constraint independence: 4 — **`ghost` + `demo` is a strong, almost redundant pairing**: ghost
  structures output as "a sequence of autonomous actions with their observed results — action taken,
  result observed"; demo requires "as literal text: (1) the action taken, and (2) the result as it
  appeared when captured." These are nearly the same requirement, with demo adding the
  evidence-artifact framing and the no-reviewer-execution constraint. `operations` (name the objective
  optimized, the constraints bounding it, the tradeoffs) suits a sort well — sorting *by* a named
  objective. `thing` gives it entities; `bog` covers structure and action.
- Category alignment: 5.
- Combination harmony: 4 — everything composes; the mild issue is ghost/demo overlap, where ghost adds
  little demo does not already require. **Boundary rationale (4 not 5):** a redundant token is not a
  conflict but it does occupy a slot without earning it.
- **Overall: 4**

**Notes:** **`ghost` and `demo` overlap substantially** — both require action-plus-observed-result as
literal text. Same shape as the cite/objectivity subsumption found yesterday: neither token's
distinctions mentions the other, so a chooser cannot see it. Candidate for reciprocal distinctions,
routing to the distinctions layer rather than compositions (nothing produces bad output).

---

## Seed 319 — pull · narrow · jobs · story · video

**Cross-axis:** `video` — no entry. video: "consists solely of a video as the complete output —
described through scene, camera motion, subject actions, style, and temporal progression — with no
surrounding prose."

**Scores:**
- Task clarity: 5 — pull (extract a subset without altering substance) is clear.
- Constraint independence: 2 — **`video` × `pull` is a constructor-class deliverable substitution.**
  video produces a *video specification* (scene, camera motion, style, temporal progression). pull
  extracts a subset of given source material without altering it. A video spec is a new artifact, not
  the extracted material — the same mechanism as the `image`×`pull` cautionary added yesterday ("an
  image is a new artifact rather than the extracted material, so the subset is not delivered").
  `story` form (As a persona, I want... so that...) is a fixed backlog template that also does not
  survive as video; `jobs` scope and `narrow` compose fine with pull.
- Category alignment: 5.
- Combination harmony: 2 — pull+jobs+narrow cohere; video and story both fail to carry an extraction.
  **Boundary rationale (2 not 3):** same as image×pull — the deliverable is categorically wrong, not
  merely unrenderable.
- **Overall: 2**

**Notes:** **`video` is a constructor channel with no entry** — it produces a spec for generating an
artifact, exactly like `image`, `agent` and `skill`. Yesterday's constructor pass covered agent, skill
and image but **missed video**. This is a coverage gap in a pass I did, not a new mechanism. Candidate:
give video the same constructor treatment (natural `[make]`, cautionary for transform/extract tasks).

---

## Seed 331 — check · zoom · analog · canvas · jog

**Cross-axis:** `canvas` — no entry. canvas: "structured as input to a canvas rendering agent. The
subject is represented as named shapes and connections rather than prose alone."

**Scores:**
- Task clarity: 5 — check is clear.
- Constraint independence: 3 — **`zoom` × `canvas` is a capacity interaction.** zoom "treats the
  subject as exponentially-spaced buckets from smallest natural unit to largest. Each bucket receives
  substantive coverage." canvas represents the subject as named shapes and connections. Spatially,
  exponentially-spaced buckets are *renderable* (nested regions), so this composes better than it
  might — but "substantive coverage" per bucket across an exponential range pushes shape count, the
  same capacity shape as the c30 observation about zoom × slide-like channels. `analog` (map relational
  structure from a known case) suits canvas well — analogies are naturally spatial. `check`+canvas is
  reasonable: a verdict rendered as annotated shapes.
- Category alignment: 5.
- Combination harmony: 3 — check+analog+canvas is a good core; zoom adds bucket-count pressure.
  **Boundary rationale (3 not 4):** zoom's per-bucket substantive coverage is mandatory, so the
  pressure is structural rather than optional.
- **Overall: 3**

**Notes:** **Second instance of `zoom` × spatially-capped channels** (c30 seed 305 had zoom×presenterm).
Two independent seeds now; this moves past the single-seed bar. Candidate: a zoom completeness
cautionary for capped-unit channels, or — per the c30 `minimal` lesson — first check whether `zoom` is
request-relative or absolute before writing any warning.

---

## Seed 333 — plan · full · assume · adversarial · remote · rog

**Cross-axis:** `remote` — no entry. remote: "optimised for remote delivery, ensuring instructions work
in distributed or online contexts and surfacing tooling or interaction hints suitable for video, voice,
or screen sharing."

**Scores:**
- Task clarity: 5 — plan is clear.
- Constraint independence: 5 — **`remote` is an additive channel**, like `store`: it does not replace
  or reshape the deliverable, it adds a delivery-context requirement ("surfacing tooling or interaction
  hints"). A plan optimised for remote delivery is still a plan. `assume` (premises that must hold)
  and `adversarial` (name failure categories then instances) are both strong for planning; `rog`
  orients toward structure and implications; `full` sets breadth.
- Category alignment: 5.
- Combination harmony: 5 — plan+assume+adversarial+remote+full+rog is genuinely strong: a thorough plan
  whose premises are named, whose failure modes are enumerated by category, optimised for distributed
  delivery. Nothing does displaced work.
- **Overall: 5**

**Notes:** **`remote` is a third additive channel** after `store` and `facilitate`'s self-describing
clause. It constrains nothing about the deliverable, so per the channel-entry-necessity rule
(ADR-0085) it needs **no cross-axis entry** — and this seed is evidence for that judgment rather than
a gap. Worth recording explicitly so a later coverage pass does not "complete" it.

---

## Cycle score summary

| Seed | Channel | Overall | Load-bearing issue |
|---|---|---|---|
| 333 | remote | **5** | clean — remote is additive, needs no entry |
| 318 | demo | **4** | ghost/demo overlap (subsumption, not conflict) |
| 317 | draw | 3 | documented gist×fly-ong (excluded); **draw×diff is good** |
| 331 | canvas | 3 | zoom×canvas bucket pressure (second instance) |
| 314 | skill | 2 | check belongs in skill's constructor cautionary list |
| 319 | video | 2 | video is an uncovered constructor channel |

**Mean (all 6): 3.17 / 5.**
**Mean excluding the one flagged cautionary (317): 3.20 / 5** (5 qualifying seeds).

## The matched comparison — what it actually shows

| | c27 | c28 | c29 | c30 | **c31** |
|---|---|---|---|---|---|
| Channel-bearing seeds | 6 | 6 | 5 | 4 | **6** |
| Distinct channels | 6 | 6 | 5 | 4 | **6** |
| Mean (all) | 2.83 | 2.83 | 3.50 | 3.67 | **3.17** |

**The improvement hypothesis is weakened, not confirmed.** Under the matched 6-channel design that
c27/c28 used, the mean fell back to 3.17 — above the 2.83 baseline but well below c29's 3.50 and c30's
3.67. That is consistent with my own stated qualification: part of c29/c30's lift came from having
fewer channel-bearing seeds, which is exactly what I flagged and what this cycle was run to test.

Best current read across five stratified cycles: **the catalog scores somewhere around 2.8-3.7 against
random combinations, and the variance between cycles exceeds any improvement signal I can demonstrate.**
Five cycles is not enough to establish a trend, and I should stop treating individual cycle means as
evidence of progress.

**What this cycle DID establish, which matters more than the mean:** five of six channels drawn had no
cross-axis entry, and three findings reached the two-independent-seed threshold that c29/c30 set as the
bar for action — draw (good pairings in c29 and c31), zoom × capped channels (c30 and c31), and the
single-seed under-drawing pattern (ledger twice, now skill). The coverage gap is the reliable finding;
the score is not.
