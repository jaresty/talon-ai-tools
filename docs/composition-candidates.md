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
| calc + chain | composition | 2026-04-09 | Each step output must be reproduced verbatim before next step constrains its conclusions |
| calc + ladder | additive | 2026-04-09 | No emergent requirement — constraints operate independently across different dimensions |
| flow + trace | additive | 2026-04-09 | No emergent requirement — stage ordering and data path narration compose additively |
| mint + root | composition | 2026-04-09 | Produces `mint+root` composition — generative model mint constructs must itself be root-compliant (single canonical generative structure) |
| chain + shoshin | composition | 2026-09-29 | Produces `chain+shoshin` — chain's reproduction of an isolated pass's output crosses the isolation boundary AFTER that context's leak check ran, so the reproduction is itself `Forwarded:`-audited before the step performing it |

---

### Backfilled from lib/compositionConfig.py (2026-09-29)

These pairs were composed without a row here, which let the generator keep reranking them
as pending. The generator now reads COMPOSITIONS directly, so this table is an index rather
than the exclusion source — but it is kept complete so the history is readable in one place.

| Pair | Status | Date | Notes |
|---|---|---|---|
| blind + skim | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `blind+skim`; see that entry for the rule |
| browse + fix | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `browse+fix`; see that entry for the rule |
| browse + pull | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `browse+pull`; see that entry for the rule |
| cards + gherkin | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `cards+gherkin`; see that entry for the rule |
| case + codetour | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `case+codetour`; see that entry for the rule |
| case + gherkin | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `case+gherkin`; see that entry for the rule |
| case + shellscript | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `case+shellscript`; see that entry for the rule |
| codetour + pick | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `codetour+pick`; see that entry for the rule |
| codetour + sort | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `codetour+sort`; see that entry for the rule |
| contextualise + codetour | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `contextualise+codetour`; see that entry for the rule |
| contextualise + gherkin | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `contextualise+gherkin`; see that entry for the rule |
| contextualise + shellscript | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `contextualise+shellscript`; see that entry for the rule |
| contextualise + sketch | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `contextualise+sketch`; see that entry for the rule |
| contextualise + svg | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `contextualise+svg`; see that entry for the rule |
| deep + commit | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `deep+commit`; see that entry for the rule |
| depends + atomic | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `depends+atomic`; see that entry for the rule |
| falsify + atomic | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `falsify+atomic`; see that entry for the rule |
| falsify + chain | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `falsify+chain`; see that entry for the rule |
| faq + code | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `faq+code`; see that entry for the rule |
| faq + codetour | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `faq+codetour`; see that entry for the rule |
| faq + shellscript | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `faq+shellscript`; see that entry for the rule |
| ghost + svg | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `ghost+svg`; see that entry for the rule |
| ground + falsify | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `ground+falsify`; see that entry for the rule |
| log + codetour | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `log+codetour`; see that entry for the rule |
| mu + fix | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `mu+fix`; see that entry for the rule |
| paradox + fix | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `paradox+fix`; see that entry for the rule |
| pick + cocreate | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `pick+cocreate`; see that entry for the rule |
| pick + indirect | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `pick+indirect`; see that entry for the rule |
| prep + code | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `prep+code`; see that entry for the rule |
| prep + svg | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `prep+svg`; see that entry for the rule |
| probe + falsify | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `probe+falsify`; see that entry for the rule |
| questions + gherkin | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `questions+gherkin`; see that entry for the rule |
| questions + shellscript | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `questions+shellscript`; see that entry for the rule |
| reset + good | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `reset+good`; see that entry for the rule |
| skim + gate | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `skim+gate`; see that entry for the rule |
| spike + codetour | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `spike+codetour`; see that entry for the rule |
| twin + svg | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `twin+svg`; see that entry for the rule |
| variants + adversarial | composition | (backfilled 2026-09-29) | Shipped in lib/compositionConfig.py as `variants+adversarial`; see that entry for the rule |

---

## Pending candidates

Generated by `make composition-candidates` — ranked by same-category membership and shared
interaction keywords. Refresh anytime: `make composition-candidates TOP=20`.

**Fixed 2026-09-29:** the generator now reads `COMPOSITIONS` in lib/compositionConfig.py as the
authoritative exclusion source, unioned with this doc's tables (so `additive` verdicts, which never
become compositions, still exclude). Previously it excluded only pairs listed here, and this index
had drifted: 38 of 42 shipped compositions had no row, so already-composed pairs kept reranking as
pending — `falsify + ground` held first place on every refresh despite shipping 2026-04-09. Coverage
reporting went from 18 to 57 pairs once it counted what is actually shipped. The generator now also
names any shipped composition missing a row here, so the drift is visible instead of silent.

| Pair | Priority | Rationale |
|---|---|---|
| atomic + chain | high | same category (Reasoning); 6 shared interaction keyword(s) |
| atomic + ladder | high | same category (Reasoning); 2 shared interaction keyword(s) |
| chain + ladder | high | same category (Reasoning); 2 shared interaction keyword(s) |
| abduce + cite | high | same category (Reasoning); 1 shared interaction keyword(s) |
| abduce + objectivity | high | same category (Reasoning); 1 shared interaction keyword(s) |
| adversarial + risks | high | same category (Diagnostic); 1 shared interaction keyword(s) |
| atomic + calc | high | same category (Reasoning); 1 shared interaction keyword(s) |
| atomic + lateral | high | same category (Reasoning); 1 shared interaction keyword(s) |
| atomic + verify | high | same category (Reasoning); 1 shared interaction keyword(s) |
| automate + shear | high | same category (Structural); 1 shared interaction keyword(s) |

---

## How to evaluate a pending pair

```bash
# Refresh the candidate list (re-run after any token additions)
make composition-candidates TOP=20

# Evaluate a specific pair
make composition-check PAIR="atomic chain"
```

Read the output. Apply the emergent requirement test:
- Does `ground + formal` produce a CONSTRAINTS requirement absent from `ground` alone AND `formal` alone?
- Can a response satisfy each token individually but violate the combined requirement?

If yes: draft composition prose, add to `lib/compositionConfig.py`, update status to `composition`.
If no: update status to `additive` with today's date.
