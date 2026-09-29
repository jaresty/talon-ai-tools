# Cycle 26 — Phase 2d Process Self-Evaluation

**Process health score: 4/5.**

## What worked

- **The composition-vs-cautionary rule did discriminating work on four findings**, and this cycle
  it produced a genuinely sharper formulation: *supplementary content composes adjacently; a
  whole-response protocol cannot.* prep+code (content → composition) vs interactive+code
  (protocol → cautionary) is the clean contrast pair. That distinction did not exist before this
  cycle; it was derived by testing the rule against a case that resisted it.
- **A structural gap surfaced rather than a token defect.** The dip to 2.83 traced to three seeds
  drawing `code`, which exposed that `code` never received the adjacent-block composition
  treatment `svg` has. That is a more valuable finding than any single pair, and it was found by
  asking *why* the scores clustered rather than filing three separate entries.
- **Confounded evidence was refused, not used.** mark+code (seed 223) was mechanically identical
  to prep+code, but the seed also carried the already-cautioned sim+code, so mark's contribution
  was not isolated. It went to pattern-watch instead of becoming a fifth recommendation.

## Implicit assumptions still open

1. **Every high-confidence rec is still a family extension.** Four cycles running (c23-c26), the
   process reliably fills in known patterns. The one genuinely novel entry this cycle
   (snap+zettel) has no precedent and is rated medium-high on reasoning alone. The process has
   not been validated at discovering a new interaction *class* unaided — cycle-24's contextualise
   upgrade and cycle-25's tight root-cause fix both came from user prompts, not from the process.
   This is a real limit and should be stated, not papered over.
2. **Sampling concentration is unmanaged.** Three of six seeds drawing `code` is luck, and it both
   depressed the mean and produced the cycle's best finding. ADR-0085's sampling strategy allows
   `--include`/`--exclude` to force axis coverage, but this cycle (like 23-25) used plain
   sequential seeds. Deliberate stratification would make cycle means comparable across cycles
   instead of hostage to the draw.
3. **Single-seed evidence, five cycles deep.** Unchanged from cycle-25. Mitigated by family
   extension, not replaced.
4. **Post-apply validation ran once (cycle-25) and is not yet routine.** It caught a stale
   installed binary — a real defect invisible to the tests. It should run every cycle that ships
   edits, not once.

## Recommended process changes

- **Stratify the sample.** Use `--include`/`--exclude` to cap how many seeds in a batch draw the
  same channel, or deliberately rotate the channel under test. Comparing a 2.83 to a 3.5 across
  cycles is not meaningful when channel draw dominates the score.
- **Make post-apply validation a standing step**, not a one-off — it is the only check that
  catches propagation failures.
- **Name the process's discovery limit in the ADR.** The cycle reliably extends known families;
  novel-class discovery has so far required outside prompting. Saying so prevents over-crediting
  the method.

**Limitation:** probe gap is itself a bar prompt — an input to review, not a safeguard.
