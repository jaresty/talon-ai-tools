# Cycle 27 — Phase 2d Process Self-Evaluation

**Process health score: 4/5.**

## The two amendments made this session both paid off immediately

1. **Stratified sampling worked, and its value was not the one I predicted.** I expected it to
   make the mean comparable (it does). The larger payoff was *coverage*: scoring six distinct
   channels in one batch surfaced that **four channels have no cross-axis entry at all** (aloud,
   hunk, browse, notebook). Sequential sampling had been hiding this for four cycles by repeatedly
   drawing the well-documented format channels. A sampling rule intended to fix comparability
   turned out to fix a blind spot.

2. **Post-apply validation happened organically.** Seed 239 co-presented `browse+fix`, and the
   cycle-25 composition fired correctly. Previous cycles required a separate deliberate check;
   here a later cycle validated an earlier cycle's edit as a side effect of normal scoring. That
   is the cheapest possible form of the standing step, and it argues for *deliberately* seeding
   combinations that exercise recent edits.

## The stated discovery limit held again — with one qualification

Both acted recommendations (c27-R1, c27-R2) are one-member extensions of shipped cautionary
families. Five cycles, same pattern: the method reliably fills in known families. Consistent with
the limit now written into ADR-0085 Risks.

The qualification: c27-R2 is not a pure extension. socratic's existing entries give *format*
reasons; the seed exposed that the real constraint is *subject*-based (socratic needs a user
position to interrogate, which no artifact supplies). That is a better reason than the shipped
entries carry — so the cycle produced a small conceptual sharpening, not only a new member. It
also produced c27-O1, identifying `facilitate` as the positive exemplar of a format-neutral
definition, which is a genuinely new observation class (previous cycles found violations of the
description-purity principle; this is the first cycle to find a token that *exemplifies* it).

## Gaps

1. **Single-seed evidence, five cycles deep.** Unchanged. Both acted findings rest on one seed
   each, mitigated by family extension. The deferred items (aloud, hunk, diff+code) are correctly
   held rather than acted.
2. **New-entry creation keeps being deferred, and the backlog is now visible as a class.** Four
   channels lack any entry; individually each is "single seed, defer", but collectively that is a
   documented coverage gap (c27-O2). The deferral rule is individually right and cumulatively
   wrong. A targeted pass over the undocumented channels would be higher-yield than another
   random cycle — worth stating as the recommended next action rather than another cycle.
3. **Cycle means still not really comparable across cycles.** This is the first stratified cycle,
   so there is nothing yet to compare it *to*. Comparability begins with cycle 28.

## Recommended next action

Not another random cycle. **A targeted pass giving natural task lists to the undocumented channels
(aloud, hunk, browse, notebook)** — the gap this cycle's stratification surfaced. Random sampling
will keep rediscovering it one seed at a time.

**Limitation:** probe gap is itself a bar prompt — an input to review, not a safeguard.
