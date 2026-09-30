# ledger's exclusion clause: a four-member family, not a missing axis branch

## The question asked

Seed 502 (`witness` + `walkthrough` + `ledger`) scored 2/5. My first framing was that the
form/channel axis rule needs a THIRD branch, because `ledger` neither has a construct for the form
nor merely lacks one — it actively discards the form's content. The user asked whether `ledger`'s
format is simply too constrained, and to review what its introduction solved.

## What the history shows

Commit 62416918 (2026-05-31) introduced `ledger`, stating the purpose: "enabling fire-and-forget
context management across context clears." The definition is UNCHANGED since — no drift.

The exclusion clause is not incidental; it is the token's entire differentiator. Its own distinction
says so: "store (channel) = persist whatever the response would have been; ledger (channel) = persist
only categorized facts/decisions/constraints/open-questions". Strip the exclusion and `ledger`
collapses into `store` plus four headings. Reasoning traces are discarded ON PURPOSE, because they
are the bulk and the least durable part of what survives a context clear.

**So the format is not over-constrained for its purpose.** Answer: no change to `ledger`.

## Two corrections to my own framing

1. **Exclusion is a CHANNEL property**, so a general statement would belong in the channel axis
   description — not as a third branch of the form rule.
2. **The collision in seed 502 was not the form at all.** `witness` is a TOPOLOGY token, and it is
   the one that collides. `walkthrough` (the form) does NOT collide: it narrates steps but does not
   require reasoning to appear *before a conclusion*, which is the property `ledger` discards.
   Verified — `walkthrough` correctly does not fire in the shipped entries.

## The family (enumerated, not sampled)

Criterion: the token requires intermediate reasoning to be VISIBLE IN THE OUTPUT before the
conclusion. A first pass with a loose regex returned 60 hits across five axes — it matched any
definition *mentioning* reasoning, which for the method axis is its whole job. Tightened to the
actual criterion:

| Token | Axis | Requirement |
|---|---|---|
| `witness` | topology | names each assumption and its epistemic basis before stating any conclusion |
| `audit` | topology | names each premise before stating any conclusion |
| `case` | form | lays out background, evidence, trade-offs before converging |
| `indirect` | form | begins with background and reasoning, arrives at the bottom line last |

Four members, spanning TWO axes — which is why no form-only rule would have covered it.

## Layer: cautionary, pointing at `store`

Per nn 20260929154929-2747: "Cautionary only when honoring one token structurally STARVES the other
with no coexisting output." `ledger` "writes its output to a persistent ledger file" — it REPLACES
conversational output, whereas `store` is explicitly "additive, not a replacement". So there is no
coexisting output under `ledger`, and the adjacent-block resolution is unavailable.

`store` resolves all four: the trace reaches the reader, the durable content is still persisted.
Every entry names that as the alternative.

Shipped: 4 cautionary entries under `ledger` (2 topology, 2 form). No rule change, no third branch.

## Verification

- fires for exactly {witness, audit} on topology and {case, indirect} on form
- does not fire for ten near-misses: solo, blind, relay, live, walkthrough, log, bullets, table,
  snap, commit
- every reason cites `ledger`'s exclusion clause and points at `store`
- invariants: 0 double-layered, 0 both-sides duplicates, 53 compositions, 128 cautionary pairs, 52/32
