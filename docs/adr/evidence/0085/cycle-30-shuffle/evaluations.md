# ADR-0085 Cycle 30 — Stratified Evaluation (seeds 289/293/296/301/305/306)

**Date:** 2026-09-30
**Evaluator:** single-evaluator (Claude, opus-5)
**Binary:** reinstalled at HEAD 7acaea5a via `make bar-install`
**Batch:** 6 seeds, stratified — **fourth** stratified cycle (c27 2.83, c28 2.83, c29 3.50)

## This cycle's specific job

c29 scored 3.50 against a matched baseline of 2.83 and I could not separate catalog improvement from
draw luck. A fourth stratified cycle is the cheapest way to start distinguishing them: if the mean
sits near 2.83, c29 was variance; if it sits near 3.50, the improvement hypothesis gains support.
Stated in advance so the reading is not retrofitted to whatever comes out.

## Sampling

Surveyed seeds 285-306. The pool was channel-light — 14 of 22 drew none, `formal` appeared twice.
Selected **4 distinct channels + 2 channel-free** (adr, formal, presenterm, ledger), deliberately
keeping the channel-free seeds because form×form and method×method interactions are the least covered
part of the catalog and channel-heavy batches crowd them out.

First-time-scored tokens: narrow, test, wardley, reset, wasinawa, relations.

## Seed summary

| Seed | task | completeness | scope | method | form | channel | directional |
|---|---|---|---|---|---|---|---|
| 289 | probe | narrow | time | adversarial | test | adr | — |
| 293 | plan | full | motifs | reset | wardley | — | — |
| 296 | show | full | relations | — | wasinawa | — | jog |
| 301 | probe | minimal | assume | — | case | formal | — |
| 305 | sim | ration | thing | visual | — | presenterm | — |
| 306 | make | full | — | models | — | ledger | — |

---

## Seed 289 — probe · narrow · time · adversarial · test · adr

**Cross-axis:** adr task natural includes `probe` ✓; adr completeness natural = `[full, deep]`,
cautionary `skim` — this seed uses `narrow`, which is **unlisted**.

**Scores:**
- Task clarity: 5 — probe is clear.
- Constraint independence: 3 — **`narrow` × `adr` is an unlisted capacity tension.** adr requires
  context / decision / consequences sections and its completeness natural list is `[full, deep]` with
  `skim` cautioned as producing "incomplete decisions". `narrow` — "restricts the discussion to a very
  small slice of the topic, avoiding broad context" — is the same *shape* of conflict as the cautioned
  `skim`: an ADR whose context section explicitly avoids broad context undercuts the artifact's
  purpose. `test` form (structured test cases by scenario type) inside an ADR is odd but derivable —
  the consequences section can carry verification cases. `adversarial` + `time` scope suit a probe.
- Category alignment: 5.
- Combination harmony: 3 — probe+adversarial+time+adr cohere; narrow fights adr, and test sits
  awkwardly. **Boundary rationale (3 not 2):** both strains are derivable (a narrowly scoped ADR about
  one decision; verification cases in consequences), so not a conflict.
- **Overall: 3**

**Notes:** **`adr` × `narrow` is a capacity-family candidate** — same mechanism as the shipped
`adr`×`skim` ("ADRs need full context and consequences to be actionable"). narrow restricts scope
rather than depth, which is a *different* axis of reduction, but the consequence for adr is identical.
Candidate cautionary; single seed, so recorded not acted.

---

## Seed 293 — plan · full · motifs · reset · wardley

**Cross-axis:** no channel. wardley, reset — no entries.

**Scores:**
- Task clarity: 5 — plan is clear.
- Constraint independence: 4 — **`reset` + `plan` is a genuinely strong pairing**: reset "discards
  compatibility constraints and reconstructs the structure as if no prior commitments existed", which
  for a planning task produces a greenfield plan — a recognisable and useful mode. `wardley` (value
  chain evolution from genesis to commodity) is a *planning-native* form. `motifs` (recurring
  structural forms) gives reset something to notice across the map.
- Category alignment: 5.
- Combination harmony: 4 — plan+reset+wardley+motifs+full cohere well: map the value chain as if
  unconstrained, noting recurring patterns. **Boundary rationale (4 not 5):** `reset`'s discard of
  prior commitments sits in mild tension with a Wardley map's *evolution* axis, which is inherently
  historical — you cannot show genesis→commodity movement while disclaiming prior commitments. The
  reframe (map the evolution as it *would* run unconstrained) is available.
- **Overall: 4**

**Notes:** **reset × historically-grounded forms** (wardley, timeline, log) is a candidate tension
worth watching: reset disclaims prior commitments while those forms are *about* what came before.
Single seed, and the reframe is available, so pattern-watch only.

---

## Seed 296 — show · full · relations · wasinawa · jog

**Cross-axis:** no channel. wasinawa — no entry. `jog` is the null directional.

**Scores:**
- Task clarity: 5 — show is clear.
- Constraint independence: 5 — `wasinawa` (What–So What–Now What reflection) is a natural structure
  for an explanation: describe the relationships, interpret why they matter, propose next steps.
  `relations` scope — "treats the connections between entities as the primary object of study, names
  each relationship type present, characterizes what each type asserts" — gives wasinawa's three
  movements exactly one subject each. `full` sets breadth; `jog` applies no push.
- Category alignment: 5.
- Combination harmony: 5 — show+relations+wasinawa+full is clean and mutually reinforcing. Nothing
  does displaced work. The null directional is the right choice here rather than a wasted slot.
- **Overall: 5**

**Notes:** Clean baseline. **wasinawa+show and wasinawa+relations both read as natural pairings.**
wasinawa has no cross-axis entry. Consistent with the c29 lesson (single-seed natural lists draw too
tight), recorded as a candidate rather than acted on.

---

## Seed 301 — probe · minimal · assume · case · formal

**Cross-axis:** formal task natural includes `probe` ✓. case channel natural = `[plain, slack, jira,
sync]`, cautionary `html`; `formal` is **unlisted**.

**Scores:**
- Task clarity: 5 — probe is clear.
- Constraint independence: 3 — **`case` × `formal` is an unlisted form/channel interaction.** case
  "structures reasoning by building the case before the conclusion — background, evidence, trade-offs,
  alternatives before converging on a recommendation." formal "separates behavioral specification from
  explanation: formal notation encodes what must be true; natural language labels and explains." Both
  want the prose *and* both impose an ordering on it — case wants argument-then-conclusion, formal
  wants spec-separated-from-explanation. They compose (the explanation half can carry the case), but
  nothing states how. `minimal` + `case` is the sharper tension: case requires background, evidence,
  trade-offs AND alternatives before converging — a four-part minimum that `minimal` ("the smallest
  answer that satisfies the request") does not license. Same completeness-floor shape as the shipped
  `minimal`×`models`.
- Category alignment: 5.
- Combination harmony: 3 — probe+assume+formal cohere strongly (surface the premises, specify them
  formally); case+minimal is the strain. **Boundary rationale (3 not 2):** a terse case is
  constructible, so a strain not a conflict.
- **Overall: 3**

**Notes:** Two candidates. (1) **`minimal` × `case`** — completeness floor vs a four-part structural
minimum; extends the shipped `minimal`×`models` family, which is the same mechanism. (2) **`case` ×
`formal`** — both impose prose ordering; composable but unstated. The first is the stronger of the two
and is a family extension rather than a new mechanism.

---

## Seed 305 — sim · ration · thing · visual · presenterm

**Cross-axis:** presenterm task natural = `[make, show, plan, pull]`, cautionary `[fix, probe]`; `sim`
is **unlisted** → universal rule. presenterm completeness natural = `[minimal, gist]`, cautionary
`[max, deep]`; `ration` **unlisted**.

**Scores:**
- Task clarity: 5 — sim (play out a scenario over time) is clear.
- Constraint independence: 3 — **`sim` + `presenterm` is actually good**: a scenario playing out over
  time maps naturally onto a slide sequence, one state per slide. That is a better fit than
  presenterm's cautioned `fix`/`probe`. The real tension is **`ration` × `presenterm`**: ration
  "allocates coverage depth in proportion to a situational score that the response must name" and for
  each shallow part "names its low score as the reason" — that naming is prose overhead, and
  presenterm's completeness natural list is `[minimal, gist]` with a 12-slide cap. The score-naming
  machinery costs slides. `visual` (concepts in named positions encoding relationships) suits slides
  well; `thing` scope gives it entities to place.
- Category alignment: 5.
- Combination harmony: 3 — sim+visual+thing+presenterm is a strong core; ration adds bookkeeping the
  format must carry. **Boundary rationale (3 not 4):** ration's per-part justification is mandatory,
  not optional, so the overhead is structural.
- **Overall: 3**

**Notes:** **`sim` is arguably natural for presenterm** — a scenario over time is a slide sequence.
Presenterm cautions `fix` and `probe` but says nothing about `sim`, and this seed suggests it belongs
in the natural list. Also **`ration` × brevity-capped channels** (presenterm, commit, aloud) is a
capacity candidate: ration's mandatory score-naming is prose overhead a capped format must absorb.

---

## Seed 306 — make · full · models · ledger

**Cross-axis:** ledger task natural = `[pick, plan, diff]` — **widened one hour earlier this session**;
`make` is **unlisted**. This directly re-tests that list. `minimal`×`models` cautionary exists but this
seed uses `full`, so it does not fire.

**Scores:**
- Task clarity: 5 — make (create new content) is clear.
- Constraint independence: 4 — `make` + `ledger` works: a newly created artifact's facts, decisions
  taken while creating it, constraints discovered, and open questions all populate ledger's four
  headings. `models` (enumerate absent named mental models, naming what each would surface) fits a
  make task well — it broadens the construction before committing. `full` sets breadth.
- Category alignment: 5.
- Combination harmony: 4 — make+models+full+ledger cohere. **Boundary rationale (4 not 5):** ledger
  records *about* work; a `make` deliverable is the artifact itself, so the ledger captures the
  decisions around the artifact rather than the artifact — one indirection the combination does not
  state.
- **Overall: 4**

**Notes:** **ledger's natural list is STILL too narrow** — `make` scores 4/5 one hour after I widened
the list from `[pick, plan]` to `[pick, plan, diff]`. This is the second consecutive correction to the
same entry, which is stronger evidence for the c29 lesson than c29 itself provided: deriving a natural
list from one or two seeds keeps under-drawing it. Candidate: add `make`; and the real lesson is that
this list should be enumerated against the whole task axis rather than widened one seed at a time.

---

## Cycle score summary

| Seed | Channel | Overall | Load-bearing issue |
|---|---|---|---|
| 296 | — | **5** | clean — wasinawa+relations+show |
| 293 | — | **4** | reset+plan+wardley strong; reset×historical forms mild |
| 306 | ledger | **4** | make fits ledger — list still too narrow after yesterday's widening |
| 289 | adr | 3 | narrow×adr capacity tension (unlisted, same shape as cautioned skim) |
| 301 | formal | 3 | minimal×case completeness floor; case×formal both order prose |
| 305 | presenterm | 3 | ration×presenterm score-naming overhead; sim fits presenterm |

**Mean (all 6): 3.67 / 5.** No flagged cautionary fired this cycle, so there is no exclusion figure —
every seed counts.

## The comparison this cycle was run to make

| | c27 | c28 | c29 | c30 |
|---|---|---|---|---|
| Distinct channels | 6 | 6 | 5 + 1 free | 4 + 2 free |
| Mean (all) | 2.83 | 2.83 | 3.50 | **3.67** |
| Documented cautionaries fired | 1 | 2 | 2 | **0** |

**The improvement hypothesis gains support.** Two cycles now sit well above the 2.83 baseline (3.50,
3.67), and c30 reached its figure with **zero flagged cautionaries** — the previous above-baseline
cycle had two exclusions inflating its adjusted number, while this one needed no adjustment at all.

Two honest qualifications:
1. **Zero cautionaries firing is itself a signal I cannot cleanly read.** It could mean the catalog now
   steers away from known-bad pairings, or simply that this draw missed them. Four cycles is not enough
   to distinguish.
2. **c30 had only 4 channel-bearing seeds** versus 6 in c27/c28, and channel tokens are the most
   constraining class. Part of the lift may be that two seeds had no channel to conflict with. This is
   a sampling difference I introduced deliberately (to reach form/method interactions) and it cuts
   against strict comparability with c27/c28.

So: supported, not established. A fifth cycle at 6 distinct channels would be the clean test.
