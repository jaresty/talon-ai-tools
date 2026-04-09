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

| Pair | Priority | Rationale |
|---|---|---|
| ground + formal | high | Both reference governing artifacts; formal may impose structure ground doesn't specify alone |
| sim + check | medium | simulate-then-review interaction may add ordering requirement absent from each alone |
| gate + sim | medium | Gate's assertion-before-behavior may conflict with sim's hypothetical output |
| chain + atomic | low | Already covered as gate+chain + gate+atomic; direct chain+atomic may be additive |

---

## How to evaluate a pending pair

```bash
make composition-check PAIR="ground formal"
```

Read the output. Apply the emergent requirement test:
- Does `ground + formal` produce a CONSTRAINTS requirement absent from `ground` alone AND `formal` alone?
- Can a response satisfy each token individually but violate the combined requirement?

If yes: draft composition prose, add to `lib/compositionConfig.py`, update status to `composition`.
If no: update status to `additive` with today's date.
