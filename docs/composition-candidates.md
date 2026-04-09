# Composition Candidates

Tracks method token pairs evaluated under Loop-C (ADR-0227).

**Statuses:** `pending` | `additive` | `composition`

Each entry records: pair, status, date evaluated, and a one-line summary of the emergent
requirement test result (or the composition name if one was created).

---

## Evaluated pairs

| Pair | Status | Date | Notes |
|---|---|---|---|
| ground + gate | composition | 2026-04-09 | Produces `ground+gate` composition — assertion gate must precede ground's first behavior |
| gate + atomic | composition | 2026-04-09 | Produces `gate+atomic` composition — single-failure scope rule from atomic gates implementation steps |
| gate + chain | composition | 2026-04-09 | Produces `gate+chain` composition — only failing test output is valid predecessor artifact |
| atomic + ground | composition | 2026-04-09 | Produces `atomic+ground` composition — ground completion check required when artifact reports no failures |

---

## Pending candidates

Note: candidates must be method×method pairs. `sim`, `check`, `formal` are task/channel
tokens and are not valid method token candidates.

| Pair | Priority | Rationale |
|---|---|---|
| ground + crystal | high | crystal imposes explicit structure; ground's enforcement process may interact with structure requirements |
| gate + mark | high | mark captures audit checkpoints; gate's assertion-before-behavior may require mark as co-present precondition |
| ground + reify | medium | reify makes implicit patterns explicit; ground's evidence protocol may add ordering requirement |
| chain + grain | low | grain finds latent direction; chain's predecessor-reproduction may interact with grain's direction-finding |
| gate + depends | low | depends traces relationships; gate's assertion scope may interact with dependency boundary |

---

## How to evaluate a pending pair

```bash
make composition-check PAIR="ground crystal"
```

Read the output. Apply the emergent requirement test:
- Does `ground + formal` produce a CONSTRAINTS requirement absent from `ground` alone AND `formal` alone?
- Can a response satisfy each token individually but violate the combined requirement?

If yes: draft composition prose, add to `lib/compositionConfig.py`, update status to `composition`.
If no: update status to `additive` with today's date.
