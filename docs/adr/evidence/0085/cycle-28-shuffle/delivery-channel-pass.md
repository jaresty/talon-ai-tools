# Cycle 28 addendum — delivery-mechanism channel pass

Closes the last uncovered channel class identified in c28-O2. Organised by **class** rather than
one channel at a time, per the c28 process-feedback recommendation.

## The discriminating rule this pass produced

The pass began as "give the remaining delivery channels natural task lists" and found that **half of
them should have no entry at all**. The rule that separates them:

> **A delivery channel needs a cross-axis entry only if it imposes a capacity or a target
> constraint. A channel that only supplies formatting conventions, or that declares itself additive,
> constrains nothing — an entry would be vacuous or would contradict the definition.**

Evidence it was already latent in the catalog: of the delivery channels that *had* entries before
this pass, both `sync` and `presenterm` carry capacity constraints (a session plan; a 12-slide cap),
which is exactly why they needed one. `slack`, `jira`, `notion`, `store`, `zettel`, `github` had
none — and applying the rule shows three of those six were correctly empty.

## Dispositions

| Channel | Entry? | Derivation |
|---|---|---|
| `zettel` | **added** | content unit is a one-claim note → natural `[pull, probe, show]` (claim-shaped output); cautionary `make`/`fix` (a created or transformed artifact is the thing itself, not a claim about it) |
| `github` | **added** | content unit is a postable artifact in GFM needing an inferable target → natural `[make, fix, check, diff]`; cautionary `sim` (an unfolding sequence has no natural issue/comment/PR form) |
| `notion` | **added** | bidirectional target via `ntn`, same class as the shipped `browse` → natural `[make, show, pull, check]` |
| `store` | **none, deliberately** | its definition states "Conversational output continues normally; storage is additive, not a replacement." Any cautionary would **contradict the definition**; any natural list would be "all tasks" and therefore vacuous. Per the cycle-28 definition-vs-pairwise rule, the definition already governs. |
| `slack` | **none, deliberately** | pure formatting convention ("formats the answer for Slack using appropriate Markdown, mentions, and code blocks") — imposes no capacity or target constraint |
| `jira` | **none, deliberately** | pure formatting convention (Jira markup) — same |

## Why the omissions matter as much as the additions

Three cycles of this session have shown the catalog's failure mode is **entries added by analogy
with neighbours** rather than derived from the token (recipe mis-filed as prose; five cautionaries
repeating one prose premise; two pairwise entries holding single-token facts). Adding entries to
`store`/`slack`/`jira` for symmetry would have been the same error — and in `store`'s case the entry
would have actively contradicted its own definition.

Recording the omissions with their reasons means a future pass will not "complete" the coverage by
filling them in.

## Verification

- 21 channels now carry cross-axis entries.
- Falsify: `github`×`sim` flagged; `zettel`×`make` flagged; `store` has no entry as intended.
- Invariants: zero double-layered pairs, zero render-class phrasing.
- Counts: 41 compositions, 121 cautionary entries.
- go ./internal/barcli/... OK; make test 1482 OK; binary reinstalled.
