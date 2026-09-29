# Cycle 25 — Phase 2e Distinction Check

## c25-R1: tight + code — cautionary vs composition test

The decision rule from cycles 23-24: **composition** if a coherent coexisting output exists;
**cautionary** if one token structurally starves the other.

- **contextualise + code** (a composition, cycle-24 family): resolvable because contextualise's
  content is *supplementary* — the pure code artifact plus an *adjacent* prose context block
  both exist. Two artifacts coexist.
- **tight + code** (this cycle): tight is not supplementary — it is the *entire response's form*
  ("the response uses concise, dense prose ... without bullets, tables, or code"). There is no
  "adjacent block" to relocate it to: an adjacent prose block would BE the response, contradicting
  "code only." Satisfying code (code-only) leaves tight with nothing; satisfying tight (dense
  prose) violates code. No coexisting output → **cautionary**, matching the shipped faq+code and
  recipe+code entries.

**Judgment:** cautionary confirmed. This is the mirror image of the contextualise resolution and
sharpens the decision rule: a *supplementary* prose form (contextualise) composes with a
code/DSL channel via adjacency; a *whole-response* prose form (tight, and by the same logic the
already-cautioned faq/recipe) cannot, so it is cautionary.

## c25-R2: browse + fix — same as shipped browse+pull

Not a distinction/redundancy question — it is a second instance of a resolved pattern (fetch
then operate on given content). The browse+pull composition already validates the sequencing
mechanism; browse+fix reuses it. No independent check needed beyond confirming fix (like pull)
operates on given content that browse must first produce — which its definition confirms
("reformatting existing content").

**Limitation:** single evaluator, single seed per finding, compare prompts not executed by a
fresh model. c25-R1 extends an established cautionary family (faq/recipe+code) and c25-R2 extends
a shipped composition (browse+pull) — the mechanisms are already tested; only token membership is
new, which is why confidence is high/medium-high despite single-seed evidence.
