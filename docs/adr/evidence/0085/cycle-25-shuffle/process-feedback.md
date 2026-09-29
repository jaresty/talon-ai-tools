# Cycle 25 — Phase 2d Process Self-Evaluation

**Process health score: 4/5** — steady. The cautionary-vs-composition decision rule (built
over cycles 23-24) did real classifying work this cycle and sharpened.

## What the decision rule caught this cycle

- **tight+code → cautionary, not composition.** The rule "composition if a coexisting output
  exists" distinguished tight (whole-response prose form → starves) from contextualise
  (supplementary prose → composes adjacently). Without the rule, the cycle-24 momentum toward
  "make everything a composition" would have mis-filed tight+code as a composition it cannot be.
- **coupling×html classified as soft affinity (no action), not a conflict.** Resisted the
  reflex to file every form/channel friction as a cautionary — coupling's own description says
  it merely "pairs naturally" with diagram channels; html attenuates but does not break it.
- **scorecard×notebook flagged as a GOOD pairing, not a defect.** A 4/5 with genuine
  reinforcement — recorded as a natural-list candidate, not a warning.

## Implicit assumptions still open

1. **"Extends an established family" keeps being the justification** (tight+code ~ faq/recipe+code;
   browse+fix ~ browse+pull). Three cycles running, the highest-confidence recs are all family
   extensions. This is legitimately lower-risk, but it means the process is good at *filling in*
   known patterns and has NOT been tested at discovering a genuinely novel interaction class.
   The one novel move (cycle-24 contextualise upgrade) came from a user prompt, not the process.
2. **Single-seed evidence, three cycles deep.** Each rec still rests on one appearance. The
   family-extension argument mitigates but does not replace corroboration. None have been
   re-tested against a fresh seed post-application (the ADR's own post-apply validation step has
   been skipped all three cycles).
3. **Deferred natural-list candidates are accumulating** (adr+pick landed; ledger+pick landed;
   now presenterm+check, notebook+scorecard pending). Natural-list *additions* are low-risk and
   cheap — the process may be over-deferring them relative to their cost.

## Recommended process change

- Run the ADR's **Post-Apply Validation** step at least once: re-draw a seed that would exercise
  one of the shipped edits (e.g. a browse+pull or contextualise+sketch seed) and confirm the
  composition now fires and improves the score. Three cycles of edits with zero post-apply
  re-tests is the biggest open gap.

**Limitation:** probe gap is itself a bar prompt — input to review, not a safeguard.
