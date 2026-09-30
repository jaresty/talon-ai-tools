# Cycle 33 — process self-eval

## The failure worth recording

**I shipped a rule that contradicted 10 existing entries, and my own falsification step did not
catch it.** In cycle 32 I constructed a counterexample for "is the rule delivered?" and confirmed
it. I never asked "does the rule agree with what is already shipped?" The ground properties I
declared were all about the delivery path; none was about consistency with the composition layer.

Concretely: property [5] was "adding the clause does not change the Talon path." A property like
"the clause does not contradict a shipped composition" would have caught it, and was just as
available.

**Generalisation for the layer procedure:** when an edit adds a rule at the AXIS level, the
falsification case must include the entries at narrower levels that the new rule now governs.
A rule that is correct in isolation can still be wrong because something more specific already
answers the same question differently. Broad rules need a consistency check against the specific
ones, not just a delivery check.

## Second instance of the same meta-pattern

This is now the fourth claim this session that asserted a gap was TOTAL when it was PARTIAL:
1. "cautionaries are TUI-only" — refuted; they render in `help llm --section heuristics`.
2. "the TOKENS block is unguarded" — partially guarded, by six source-reading tests.
3. "ghost+svg was retired" — only its cautionary half was.
4. "zero prose-slot reasons remain in the catalog" (note 20260527210320-3898) — 15 remained.

All four were refuted by enumeration or execution. None was refuted by reasoning. The pattern is
strong enough to state as a rule: **a claim that a category is empty should not be recorded without
the enumeration that establishes it**, and the enumeration should be re-run before the claim is
relied on — the catalog changes under it.

## What worked

- Weighting the draw toward form+channel co-occurrence found the contradiction within six seeds.
  Stratifying by what a recent change affects is more productive than stratifying for comparability
  alone.
- The user's choice to narrow rather than retire preserved a three-cycle convergence I would have
  been willing to discard. Worth noting that my recommendation was the conservative one here only
  because the conflict was surfaced first.
- Three literal-match failures, all resolved by locating source lines with grep before editing. The
  pre-commit autofix re-wraps long strings, so a literal copied from rendered output will not match
  source. This is now a reliable expectation rather than a surprise.
