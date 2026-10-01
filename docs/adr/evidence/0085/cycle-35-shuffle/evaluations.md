# ADR-0085 Cycle 35 — topology×channel (the axis yesterday's ledger work opened)

**Date:** 2026-10-01 | single-evaluator | fresh build

## Stratification

Seeds 600-639 (40 surveyed, 26 channel-bearing). Weighted toward **topology+channel**, since
yesterday's last two commits (`ledger` topology+form, `aloud` form) left that interaction the
under-tested one. Six seeds, six distinct channels, **all six topology-bearing**.

| Seed | Draw | Score | Note |
|---|---|---|---|
| 600 | audit + narrow + cross + bullets + **image** | 2 → **4 (revised)** | First scored as a topology-vs-sole-output collision. Wrong: a constructor channel produces *a specification*, which is text, and `audit`'s evidence-before-claim is expressible in it. |
| 602 | blind + skim + ground + ghost + **aloud** | 2 | `blind` requires conclusions to cite assumption blocks *by label*; speech has no stable labels to refer back to. Held — one seed. |
| 605 | witness + full + thing + depends + snap + **video** | 2 → **4 (revised)** | Same correction as 600. |
| 606 | audit + deep + mean + **ledger** | 2 | **Yesterday's `ledger`×`audit` cautionary fires, drawn independently.** Post-apply confirmation. |
| 625 | audit + full + **codetour** | 4 | CodeTour step narration carries evidence-before-claim natively. |
| 629 | audit + full + fail + experimental + **github** | 4 | `github` is a delivery mechanism; PR/issue bodies are prose. |

**Mean: 3.33/5** (after revisions), 6/6 channel-bearing, 6/6 topology-bearing.

## The finding: the topology axis has no description at all

Every other axis has one — 13 of 14 keys in `AXIS_KEY_TO_AXIS_DESC`. Line 7 of the `bar build`
prompt reads a bare `- topology`. So every topology×channel interaction was unguided, and the single
shipped entry (`blind`+`code`) was one hand-patch against that absence.

This is the cycle-32 pattern on a different axis, and the discriminator from nn 20260930224858-5322
is satisfied: there ARE members lacking the clause (3 of 4 externalizing topology tokens, across 7
sole-output channels — a 4×7 matrix with exactly one entry) and they scored badly.

Added a topology axis description naming what the axis governs, plus the construct rule: the text
each token requires is carried in the channel's own constructs — comments in code, step narration in
a tour, descriptive fields in a specification — with the explicit note that **a channel producing a
specification is itself text and can carry it.**

## Second finding: a cautionary resting on a superseded definition

`solo`+`inversion` said "solo **suppresses reasoning externalization**". Current `solo` requires the
opposite — "an intermediate step only when that step names the specific prior step or derivation
dependency it closes", with a mandatory `Required because …` label.

Dates settle it: the cautionary was added 2026-05-18 (51cab054) against the old deny-list definition
("Do not proactively externalize intermediate assumptions"; recorded in nn 20260513141540-7254), and
the definition was rewritten 2026-06-15 (23ebe1fa) to the affirmative observable form. The cautionary
was never revisited. Under current `solo` the pair is compatible. **Retired.**

## Third: `blind`+`code` was mis-layered

Its own text opened with "blind+code composition" while filed as a cautionary. Converted to a
composition — which strengthens it: cautionaries render only on the token-selection paths, whereas a
composition is injected into the build prompt's COMPOSITION RULES section and so reaches the model
when `blind` and `code` are actually co-present.

## Corrections to my own scoring

Seeds 600 and 605 were scored on the wrong mechanism — I read `image`/`video` as rendered artifacts
when the catalog says "a constructor channel produces a specification for a tool or artifact".
**Fifth instance this session** of the pattern in nn 20260930224916-3769; caught by a reviewer
question, not by me. The axis rule now states the spec-is-text case explicitly so the next reader
does not repeat it.

## Verification

- bare `- topology` line: present before, absent after; guidance present after
- `solo`+`inversion`: retired, absent from output
- `blind`+`code`: resolves as a composition and is injected into a `topology:blind channel:code` build
- yesterday's work intact: 4 `ledger` cautionary reasons and the `aloud` positional reason still render
- invariants: 54 compositions, 0 double-layered, 0 both-sides duplicates, 52 forms / 32 channels
- `go test ./internal/barcli/...` ok; 85 passed in targeted catalog suites
