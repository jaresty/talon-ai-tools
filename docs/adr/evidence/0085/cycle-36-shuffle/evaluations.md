# ADR-0085 Cycle 36 — topology × method/scope/completeness

**Date:** 2026-10-01 | single-evaluator | fresh build

## Stratification

Seeds 700-739. Cycle 35 covered topology×channel, so this cycle deliberately paired topology with the
axes it had NOT been drawn against — method, scope, completeness. Six topology-bearing seeds; two
channel-bearing (down from 6/6 last cycle, by design).

| Seed | Draw | Score | Note |
|---|---|---|---|
| 702 | witness + full + jobs + sever + wasinawa + html | 4 | `wasinawa` and `witness` both want reasoning visible; `full` gives room. Coherent. |
| 704 | audit + **skim** + good + gherkin + fip-rog | 2 | `audit` needs an evidence-naming string before every conclusion; `skim` is a light pass. Uncovered — and the seed that opened the finding. |
| 713 | audit + grow + assume + sever + diagram + fly-ong | 4 | `grow` expands where analysis demands; compatible with per-claim evidence. |
| 720 | blind + full + thing + falsify + elicit + presenterm | 3 | Crowded (falsify records + blind blocks + a 12-slide cap with `full` active) but each is satisfiable. |
| 723 | blind + deep + thing + lateral | 4 | `deep` gives `blind`'s assumption blocks room. Arguably natural. |
| 734 | witness + **gist** + test + notebook + rog | 2 | Shipped `witness`+`gist` cautionary fires. |

**Mean: 3.17/5**, 6/6 topology-bearing, 2/6 channel-bearing.

## What I got wrong first, and what the reviewer's question fixed

My first move was to enumerate a 4×2 matrix (four externalizing topology tokens × two absolute caps)
and fill the six empty cells with **cautionaries**. I wrote all eight, and the invariant check caught
`blind+skim` as **double-layered** — because a `blind+skim` COMPOSITION already ships:

> "assumption and constraint reconstruction … is compressed to one-line headers rather than full
> blocks. Each header names the assumption or constraint explicitly so the conclusion can be traced to
> it, but elaboration is suppressed."

That composition is the answer to the reviewer's question ("could we resolve with a definition change
or composition rule instead of cautionary?"): **the tension compresses, it does not starve.** A
cautionary is correct only when honoring one token structurally starves the other with no coexisting
output — and `blind+skim` demonstrates a coexisting output exists. All eight of my cautionaries were
the wrong layer, reverted before commit.

## What shipped instead

The compression rule is identical across all four tokens, so it went to the **axis description**, not
to eight entries:

> "Where a completeness token caps depth absolutely, the required text compresses to its shortest
> labelled form rather than being dropped — the label and the reference from each conclusion to it
> survive, and only the elaboration is suppressed."

- **Kept** `blind+skim` as the specific case: "one-line headers" is not derivable from a general clause.
- **Retired** the two `witness` × {skim, gist} cautionaries, which asserted the opposite ("undermine
  witness's purpose") and are now covered.
- Only `skim` and `gist` cap absolutely. `minimal` is request-relative, `narrow` limits breadth, and
  `ration`/`grow`/`zoom`/`prime` are distributive — an earlier classifier swept all of these in, the
  fourth over-broad regex of the session.

## Second finding: three more entries falsified by the June `solo` rewrite

Cycle 35 retired `solo`+`inversion` as resting on a superseded definition. It was **one of four**.
Enumerating every entry referencing `solo` found three more:

- `witness`×`skim` and `witness`×`gist` — both said "prefer solo if brevity is required"
- `solo`×`stakeholder_facilitator` — "solo externalizes **minimal** reasoning state"

All three describe the pre-rewrite `solo` ("Do not proactively externalize… Present only the final
artifact"). Under current `solo` the advice is false: it mandates a `Required because …` label on
**every** intermediate step. Falsification established something stronger — **no topology token is the
brief option**; every one imposes a per-step textual requirement, so the correct alternative is to
omit the topology token entirely. The two `witness` entries were retired; the `solo` persona entry was
rewritten to describe the current definition.

Note 20261001175344-1962 prescribes exactly this enumeration ("when rewriting a token definition,
enumerate the cross-axis entries naming that token"). I wrote that note yesterday and did not run it.

## Verification

- capacity clause delivered in a `topology:audit completeness:skim` build; absent before
- `witness` cautionaries and stale `solo` advice: absent from `help llm --section heuristics`
- `blind+skim` composition intact
- guard: C22-R2's location assumption replaced by `TestTopologyCapacityGuidanceDelivered`, asserted
  against the axis description and shown to discriminate (perturb → RED, restore → GREEN)
- invariants: 54 compositions, 124 cautionary pairs, 0 double-layered, 0 both-sides duplicates, 52/32
- `go test ./internal/barcli/...` ok; 85 passed
