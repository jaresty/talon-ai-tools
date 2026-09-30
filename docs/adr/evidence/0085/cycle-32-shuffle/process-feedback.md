# Cycle 32 — process self-eval (ADR-0085 step 2d)

## What the process got right

- **Stratification worked as designed.** 6/6 channel-bearing, 6 distinct channels, chosen from a
  38-seed survey. The mean (3.17) is comparable to c27/c28/c31 by construction rather than by luck.
- **Falsification caught a wrong score before it became an edit.** Seed 326 was scored 2/5 on an
  apparent bug-vs-code collision. The counterexample step found the governing rule already in config.
  Without it, cycle 32 would have shipped a redundant pairwise cautionary — the exact mis-layering
  defect the last nine cycles were about.
- **The enumerate-vs-sample rule fired correctly** (nn 20260930173923-3639). Once the decision rule
  was visible ("form + sole-output channel"), the set was bounded (5 x 52) and enumerated. The
  enumeration is what revealed 7 forms had hand-patched the same rule — invisible to sampling.
- **A uniform all-fail against known-good state was read as a harness signal, twice** (the cautionary
  greps, then the help-llm greps), rather than as a defect in the new work. Both times it was.

## What the process got wrong

- **I asserted "cautionary fired" for four seeds without observing delivered output.** What I checked
  was the config. Cross-axis cautionaries are TUI-only. This misdescription is mild here (the entries
  are correct) but it means the phrase "fired" in cycles 23-31 evidence should be read as "is present
  in config", not "was delivered to the model". Recorded in evaluations.md.
- **I misread `git diff` twice on the 135k-line grammar JSON.** First a float-only filter on a `head -20`
  window concluded the edit hadn't propagated; then `git diff -U0` reported 0 added lines for a file that
  demonstrably contained the new string. Resolution: verify JSON propagation by `grep`-ing the file and
  comparing against `git show HEAD:<path>`, not by reading the diff. The diff is unreliable at this size
  with churning embeddings.
- **One literal-match failure from concatenated string literals.** The rendered description differs from
  the source's line-wrapped form. Fix: locate with grep first and replace exact source lines, which is
  the rule already learned from the skim/gist over-match — applied here only after failing once.

## Carried forward

- O1 (cautionaries never reach a bar build agent) is the largest open question this cycle raised. It is
  a design decision, not a defect, and should not be resolved by a reflex.
