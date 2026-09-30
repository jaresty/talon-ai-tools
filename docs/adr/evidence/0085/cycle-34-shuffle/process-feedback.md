# Cycle 34 — process self-eval

## The near-miss worth recording

I nearly shipped a fourth axis-level rule. Three multi-turn forms (`facilitate`, `interactive`,
`quiz`) each state, in their own words, "when the output is a static artifact, collapse the
turn-taking into it; otherwise conduct it live." That is structurally IDENTICAL to cycle 32's
finding, where seven forms each restated the form/channel rule and 44 had nothing.

What stopped it: checking whether any member LACKED the clause. In cycle 32, 44 forms did — the
duplication was a symptom of a real gap. Here, **all three members already state it**, and the
fourth member I thought was unguarded (`twin`) turned out not to be a multi-turn form at all — my
regex matched it on the phrase "the reader", which is an audience reference.

So the discriminator between "duplication that signals a missing rule" and "duplication that is just
duplication" is: **does the class contain a member that lacks the clause and scores badly?** Without
one, extracting a general rule buys consistency at the cost of three short clauses, which is not a
defect fix. Added to followups as a proposed ADR check.

## Second error caught before it mattered

I scored seed 513 (`quiz`+`svg`) as 2/5 on a turn-taking collision. `quiz` already handles that case
explicitly. The real mechanism was ordinary (SVG has no text-sequence construct), which the narrowed
axis rule already covers. Rescored to 3. This is the third time this session a low score was
attributed to the wrong mechanism — cycle 32 seed 326 and cycle 33's `remote` theory were the others.
Pattern: **a real low score invites the first plausible cause, and the first plausible cause is
often the newest thing I was thinking about.** In all three cases the check that caught it was
reading the token definition rather than reasoning from the pairing.

## What worked

- Weighting toward recently-changed interactions again: 6/6 form-bearing draws directly tested the
  five commits from today, and the `aloud` gap surfaced with its second seed.
- The ADR consistency check (added today) ran BEFORE the edit this time, not after: enumerated the
  narrower entries the proposed rule would govern, found `twin+svg`, read it in full, confirmed it
  was orthogonal. That is the check `d2383ed7` skipped.
- Writing the cautionary reason from `aloud`'s own "strip long enumerations" clause rather than a
  prose-slot premise — the premise that put 15 entries in the catalog and needed retiring today.
