# Cycle 36 — process self-eval

## The invariant check did the work my judgement didn't

I wrote eight cautionaries and the `blind+skim` double-layering alarm is what stopped them. Not the
starvation test, which I know and had applied correctly two days earlier on `ledger`; not the layer
procedure. A mechanical check on a committed invariant.

That is the fourth time this week that a mechanical check, rather than reasoning, caught the error —
and the reviewer's question arrived in the same moment and pointed at the same thing. The lesson is
not "be more careful": it is that **the invariant check should run before writing the entries, not
after.** It costs one command and it encodes a decision I otherwise re-derive unreliably.

## The pattern that is now five instances

Writing a cautionary where a composition exists is the same error as the 15 prose-slot entries
retired two days ago, the ghost+svg confusion, the aloud/table framing, and the image/video
proposal. Every instance has the same shape: **I reach for the layer that records a problem before
checking whether a layer that resolves it already applies.** The routing procedure's order
(definition → composition → cautionary → distinctions) exists to prevent exactly this and I keep
entering it at the third step.

Concrete fix, cheaper than remembering: before writing any cautionary, run the double-layer check for
that pair. If a composition exists, the cautionary is wrong by construction.

## A note I wrote yesterday and did not apply

20261001175344-1962 says: when a token definition is rewritten, enumerate the cross-axis entries
naming that token. Cycle 35 retired one stale `solo` entry; three more were sitting there, and
enumerating took one command. I wrote the prescription and then did the partial fix anyway.

## What went right

- The axis-consistency check ran before the axis edit, found the two `witness` entries that would
  contradict the new clause, and they turned out to be the ones already slated for retirement — a
  clean confirmation rather than a surprise.
- Falsifying "prefer solo if brevity is required" produced a stronger result than a substitution: no
  topology token is brief, so the correct advice is to omit the axis. Checking every candidate instead
  of swapping one name is what produced that.
- Deliberately drawing topology against the axes cycle 35 did NOT cover (method/scope/completeness
  rather than channel again) is what surfaced the capacity class at all.
