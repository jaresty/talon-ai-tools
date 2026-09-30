# Method-pair composition audit (ADR-0227 Loop-C) — 2026-09-29

First pass at the method×method backlog, untouched during cycles 23-28 because
`make composition-candidates` covers only method pairs — a different axis pair from the
form/channel work those cycles addressed.

## Generator caveat found immediately

`make composition-candidates` does **not** filter against already-shipped compositions.
`falsify + ground` ranks **first** on every refresh (10 shared keywords) despite being shipped
since 2026-04-09. Of the top 12 candidates, 1 was already shipped and 11 were genuinely pending.
Recorded in `docs/composition-candidates.md` so the next pass cross-checks
`COMPOSITIONS` before evaluating.

## Evaluated: chain + shoshin → COMPOSITION

Selected as the highest-signal pending pair (3 shared interaction keywords; same Reasoning category).

**The emergent requirement.** chain requires a step to reproduce its predecessor's actual output
before new reasoning. shoshin, in `delegate`/`parallel`/`dialogue` orchestration, runs passes in
isolated contexts whose inadmissible frames are withheld, auditing every item that *enters* a
context with a `Forwarded:` line and closing with a leak check. Neither token governs the moment
chain reproduces an *isolated* pass's output — which crosses the isolation boundary in the
**outbound** direction, after that context's leak check has already run.

**Falsification case** (required by Loop-C before recording a verdict):

> A response emits `Orchestration: delegate`, a disposition block marking the inherited
> architecture frame `inadmissible`, and spawns a subagent that returns a finding. The next
> implementation step opens by quoting that subagent's result block verbatim and citing a specific
> string from it, then proceeds. **chain is satisfied** — the predecessor output was reproduced and
> a string cited. **shoshin is satisfied** — disposition emitted, inbound items `Forwarded:`-audited,
> `Leak: not found` guaranteed by construction. **The combined requirement is violated**: the
> reproduction re-admits into the main thread the very frame shoshin withheld, because the quoted
> text carries the delegate's framing back across the boundary — and shoshin's leak check has
> already run, so nothing re-audits it.

Constructible ⇒ **composition, not additive.**

**Strip-one-token test** (cycle-28 rule — does this belong in a definition instead?):
- Remove shoshin → "reproduce the predecessor's output" is chain alone.
- Remove chain → "audit items crossing the isolation boundary" is shoshin alone.

The rule exists only under co-presence, and concerns *which predecessor chain may reproduce when
isolation is in play*. **Passes** — a genuine interaction, not a definition clause in disguise.

**Resolution shipped:** the reproduced output is itself `Forwarded:`-audited before the step that
performs it, one line per item, with an inadmissible-frame item appearing only as an explicit
question; or name a predecessor produced under a disposition where that frame was admissible.
Gate clause rejects both a missing audit and an audit that omits a carried item.

## Remaining pending (10)

abduce+eliminate, abduce+rigor, adversarial+inversion, atomic+shoshin, automate+enforce,
automate+mint, cite+eliminate, cite+objectivity, cite+rigor, depends+enforce.

Each needs its own falsification case. `atomic+shoshin` looks likeliest to be a real composition
(same isolation-boundary family as chain+shoshin); the three `cite+*` pairs look likeliest additive
(citing sources composes independently with most reasoning constraints), but that is a guess, not an
evaluation — do not record verdicts without constructing the case.

## Coverage

18 → 19 of 5778 pairs evaluated (0.3%). The backlog is genuinely large; this pass establishes the
method and the generator caveat rather than clearing it.

---

# Second pass (2026-09-29, later) — two additive verdicts

## atomic + shoshin → ADDITIVE

I had predicted this the likeliest remaining composition ("same isolation family as chain+shoshin").
That prediction was wrong, and the way it was wrong is worth recording.

No falsification case is constructible. atomic governs **step granularity** (one observable change
per step) and **turn discipline** (do not return control to the user between steps). shoshin governs
**frame selection** and **context isolation**. A subagent invocation is a tool call, not a user turn,
so shoshin's delegate/parallel/dialogue orchestration never trips atomic's clause; and atomic's
observability requirement is already met by an isolated context's result.

What made chain+shoshin real was chain **reproducing** an isolated pass's output — content crossing
the boundary outbound, after that context's leak check had run. atomic reproduces nothing.

**The error in my prediction:** I reasoned by analogy from the shared token (`shoshin`), when the
emergent requirement in chain+shoshin came from `chain`'s specific mechanic. That is the same
by-analogy reasoning this session repeatedly found in the catalog itself (recipe mis-filed as prose;
five cautionaries repeating one premise). Sharing a token does not put two pairs in the same family.

## cite + objectivity → ADDITIVE, but surfaced a real defect

The emergent-requirement test fails — there is no behavioral requirement the combination creates.
But the reason is not independence: `objectivity` requires "supporting cited-evidence claims with
named sources", which **subsumes** `cite` entirely. Selecting both adds nothing.

Neither token's Distinctions field mentions the other (cite distinguishes only from `verify`,
objectivity only from `rigor`), so a chooser cannot see the redundancy from either description.

**Layer:** not a composition, and not a cautionary either — nothing produces bad output. It is a
selection-time discoverability defect, which routes to the distinctions/guidebook layer. Captured as
nn 20260929220006-4931 with a candidate reciprocal-distinction fix. Deliberately not fixed here:
editing token distinctions is outside a composition audit's scope.

**Note on the shuffle blind spot:** no shuffle cycle would find this. A cite+objectivity seed scores
fine because the output is correct. Only reading two definitions against each other reveals that one
is inert.

## Coverage after this pass

59 / 5778 pairs (1.0%); 25 / 743 same-category (3.4%). Remaining from the original top 12:
abduce+eliminate, abduce+rigor, adversarial+inversion, automate+enforce, automate+mint,
cite+eliminate, cite+rigor, depends+enforce.

---

# Third pass (2026-09-29) — the remaining 8 candidates cleared

All eight remaining candidates from the original top-12 evaluated. **Three compositions, five
additive.** Coverage 59 → 67 / 5778 (1.2%); same-category 25 → 33 / 743 (4.4%).

## Three compositions — one shape, three different joining relations

All three close the same class of gap: **two token-generated sets that nothing joins.** Each token
produces a set and passes on its own terms, so a response can satisfy both while the sets never meet.
Critically, the joining relation differs in each, which is why they are three entries rather than one
general rule:

| Pair | The gap | Joining relation |
|---|---|---|
| `abduce+eliminate` | eliminate never constrains WHERE its candidate set comes from, so abduce's hypotheses and eliminate's candidates can be disjoint lists — the response's own hypotheses go untested | **set identity**: the closed candidate set IS the hypothesis set, N equal |
| `adversarial+inversion` | adversarial only FINDS failures; inversion BLOCKS one outcome. Nothing requires the inverted outcome to be among the found instances, so every failure identified can go un-blocked | **membership**: the inverted outcome is one of the named instances |
| `depends+enforce` | enforce creates gates; depends traces dependency order. Nothing requires the gate order to follow the traced order, so a response can gate against its own analysis | **ordering**: gate order follows traced order, and each precondition names which dependency it enforces |

I flagged the pattern-matching risk explicitly before writing these — three pairs sharing a shape is
exactly the by-analogy reasoning that mis-filed `recipe` and that produced my failed `atomic+shoshin`
prediction. Each therefore got its own strip-one-token test, and each passed independently.

## Five additive, with reasons

- `abduce+rigor` — a hypothesis IS a claim, so rigor's premise-naming already reaches abduce's output.
- `cite+eliminate` — a defeater is a claim, so cite already reaches it.
- `cite+rigor` — premise-naming and source-anchoring are independent dimensions of one claim.
- `automate+enforce` — **different objects**: automate operates on the SUBJECT's workflow, enforce on
  the RESPONSE's step structure.
- `automate+mint` — different objects again: subject's operations vs the response's derivation.

The "different objects" reason is worth naming as its own additive pattern: two tokens can share
vocabulary (ordering, structure, automation) while acting on entirely different things. Vocabulary
overlap is not interaction.

## Verification

All three fire on co-presence; invariants hold (45 compositions, 121 cautionary, 0 double-layered).

**Harness note, second occurrence:** the fire-check loop returned a false 3/3 MISSING due to nested
command substitution in the probe — the same shell pattern that produced a false 12/12 MISSING in the
render-sweep validation. Caught because a uniform all-fail against known-good state is a harness
signal, not a regression signal. Checking one pair directly confirmed it fired. Worth remembering:
validate the validator against one known-good case before trusting a sweep of results.
