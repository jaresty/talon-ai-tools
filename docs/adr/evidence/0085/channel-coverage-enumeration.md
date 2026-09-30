# Systematic channel-coverage enumeration (2026-09-30)

Closes the rediscovery loop that three separate passes kept reopening. Cycles 27, 28 and 31 each
reported "five more channels have no entry", because each found them one seed at a time. Enumerating
the axis directly shows the set was always bounded.

## The set is closed

**32 channel tokens. 27 have entries. 5 do not, and all five are deliberate.**

| Channel | Disposition | Reason |
|---|---|---|
| `plain` | **omission (new)** | "imposing no additional structural conventions" — the null format. It is the *absence* of a constraint, so an entry would be vacuous. |
| `slack` | omission (recorded earlier) | pure formatting convention (Markdown, mentions) |
| `jira` | omission (recorded earlier) | pure formatting convention (Jira markup); confirmed by c30 seed 283, which put it in a five-token combination without friction |
| `store` | omission (recorded earlier) | declares itself additive — "storage is additive, not a replacement"; an entry would contradict the definition |
| `remote` | omission (recorded earlier) | additive delivery-context requirement; c31 seed 333 scored it 5/5 |

## Four entries added, each enumerated against the 11-task axis

The axis is `check diff fix make pick plan probe pull show sim sort`. Each list was derived by asking
of every task whether the channel's **content unit** can carry its deliverable — not by generalising
from a drawn seed, which is the method that produced three consecutive under-drawn lists (c29 ledger,
c30 ledger, c31 skill).

| Channel | Content unit (quoted) | natural | cautionary |
|---|---|---|---|
| `svg` | "solely SVG markup ... with no surrounding prose" | make, show | — (four prose-form compositions already shipped) |
| `diagram` | "Mermaid diagram code only" | show, sort, plan, diff | `sim` — a scenario unfolding over time is narrative; diagram syntax renders structure and sequence, not an account of what happens as conditions change |
| `canvas` | "named shapes and connections rather than prose alone" | show, sort, diff, plan | — (spatial, following the draw/sketch precedent) |
| `demo` | "as literal text: (1) the action taken, and (2) the result as it appeared when captured" | check, fix, make | `probe`, `show` — an analysis or explanation is neither an action nor a captured result, so there is nothing to evidence |

## Why enumeration beat sampling here

Three shuffle cycles reported the same finding with different membership. The reason is structural:
shuffle draws channels in proportion to nothing in particular, so an uncovered channel is found only
when drawn, and each discovery looks like a new gap rather than a member of a known set. The axis is 32
items long and the decision rule already existed (capacity or target constraint → entry; additive or
pure-format → recorded omission), so the whole set could be settled in one pass.

**The generalisable point:** when a sampling process reports the same class of gap in three consecutive
runs, the gap is enumerable and sampling is the wrong instrument. Enumerate the axis instead.

## Also in this pass — ghost/demo reciprocal distinctions

`ghost` (form) requires "a sequence of autonomous actions with their observed results"; `demo`
(channel) requires "as literal text: (1) the action taken, and (2) the result as it appeared". demo
subsumes ghost's requirement, and **neither token's distinctions mentioned the other** — ghost
distinguished itself from log/walkthrough/mark, demo from witness/code/shellscript/plain/sync.

Second instance of this subsumption pattern after cite/objectivity. Routed to the **distinctions**
layer: nothing produces bad output, so it is neither composition nor cautionary — the defect is
discoverability at selection time.

## Verification

- 27/32 covered; the 5 uncovered are all recorded omissions with reasons, so a later pass cannot
  mistake them for gaps.
- Falsify: `diagram`×`sim` flagged; `demo`×`probe` flagged; `plain` correctly has no entry.
- Invariants: 0 double-layered pairs. 45 compositions, 135 cautionary entries.
- go ./internal/barcli/... OK; axis metadata + catalog validate 85 passed, 237 subtests.
