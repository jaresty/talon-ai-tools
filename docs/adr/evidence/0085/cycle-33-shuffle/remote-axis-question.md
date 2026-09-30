# Cycle 33 followup — is `remote` on the right axis? (No: the defect was elsewhere)

## The proposal, and why it dissolved

After seeds 333 and 410 both drew `remote` and scored well but oddly, I proposed a
"delivery-mechanism sub-class" for `remote` and `aloud`. Two things were wrong with it.

**1. The sub-class already exists.** Note 20260717011133-2169 records a three-way channel
taxonomy — format (reshape) / delivery-mechanism (redirect) / constructor (replace-with-spec) —
with delivery-mechanism defined as "the LLM must invoke a CLI or tool to deposit the output rather
than emitting it inline" and members `zettel`, `hunk`, `github`. I had referenced this taxonomy
earlier in the same session and still proposed re-inventing part of it.

**2. The two tokens do not belong to the same category.**
- `aloud` IS a delivery-mechanism channel (it invokes `say -r 250` / `espeak`) and is missing from
  the note's member list.
- `remote` is NOT. It names a platform context and constrains content for it; no CLI, no deposit.

## The "wrong axis" claim also failed

I then proposed that `remote` does not belong on the channel axis at all. Falsified:
- The axis is "Delivery format — the artifact type **or platform** the response targets." `remote`
  names a platform context, which is inside that.
- `sync` does the same kind of work (a live session plan rather than static text — a delivery
  context, not a markup format) and is well-established, with cautionaries written against it.
  If `remote` is misfiled, so is `sync`.

So `remote` stays. Two proposals, both dissolved on inspection.

## The actual defect (enumerated, then fixed)

What seed 410 really showed: `ontology`'s description said "Output adapts to channel: diagram
channel → entity-relation graph; code channel → formal schema; no channel → prose concept entries."
`remote` matches neither named branch, so it fell through to the **no-channel** branch while a
channel was active.

This is a defect in the enumerating form's branch structure, not in `remote`. Enumerated the class:
**4 forms** have a channel-branch enumeration with a no-channel fallback.

| Form | Named channels | Branch structure |
|---|---|---|
| ontology | code, diagram, formal | member list — 29 of 32 channels fall through |
| axiom | code, formal | member list — 30 fall through |
| taxonomy | code | member list — 31 fall through |
| facilitate | *(none)* | **property partition** ("output-exclusive channel or not") — covers all 32 |

`facilitate` already had the robust pattern. Converted the other three to partition by CONSTRUCT
PROPERTY rather than by named member, keeping each one's specific mappings (predicates, ER graph,
type system) since those are what the general axis rule cannot derive:

- ontology → "a graph channel renders them as nodes and labelled edges, a code or notation channel
  as a formal schema..., and a channel with no such construct as named concept entries"
- taxonomy → "a code or notation channel... a channel with nesting as nested structure, and a
  channel with neither as named sections ordered by level"
- axiom → "a formal, code or notation channel renders them as predicates..., and a channel without
  a notation construct as named axiom entries"

`remote` now reaches a defined branch AS a channel lacking the construct, rather than as an absent
channel. Same output shape, correct reason, and it generalises to all 29 previously-unmatched channels.

## Guard updated

`TestLLMHelpChannelAffinityAndTokenClarity` D4 asserted the literal "Output adapts to channel"
appeared **anywhere** in the catalog — so any of the three enumerating forms satisfied it, despite
the comment saying it checked taxonomy. Re-anchored to taxonomy's own table row and shown to
discriminate: perturbing taxonomy's clause makes it fail and print the offending row.

## Process note

I concluded three times that the rewritten guard was "vacuous" because perturbation did not make it
fail. All three were wrong: the guard lives in `TestLLMHelpChannelAffinityAndTokenClarity` (line 414)
and I was running `TestLLMHelpADR0107TokenDescriptions` (line 490). The original failure message cited
`help_llm_test.go:450`, which is inside the former. **When a perturbation does not produce the
expected RED, check that the test being run is the test that was changed before concluding anything
about the guard.**
