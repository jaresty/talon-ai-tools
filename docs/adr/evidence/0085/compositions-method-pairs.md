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
