# ADR-0241: bar token catalog — design-system audit and recommended fixes

Status: proposed
Date: 2026-11-08

## Context

The `design-system` sequence (`lib/sequenceConfig.py`: probe motifs induce → make ontology dimension
reify → make axiom → check snag) was run inline over the bar token catalog in
`build/prompt-grammar.json`: 258 tokens on 7 axes (topology 6, completeness 14, scope 19, method 117,
form 54, channel 32, directional 16), 11 tasks, persona, 57 compositions, 27 sequences. The steps
were measured with scripts rather than executed through `bar build`; counts below are from that run.

## Findings

### Motifs
- Every definition opens "The response ..." with a fixed verb per axis (scope "focuses on", method
  "enhances the task" in 73/117, directional "additionally orients").
- 242 of 258 tokens declare `distinctions` ("X = ...; Y = ..."): 560 directed edges. The first draft
  said 257/258; that was a miscount found when the A2 validator ran. Fifteen tokens have none: channel
  adr, code, codetour, gherkin, html, jira, notebook, plain, remote, shellscript, slack, svg; form
  dialogue, wardley; method own. `jog` is the null directional and is exempt. Densest
  cross-axis seams: method<->scope 21, form<->method 13, completeness<->method 6.
- Heavy tokens carry procedure (negative clauses, named markers). Length varies from ~100 characters
  to `ground` 31.6 KB, `falsify` 15.6 KB, `shoshin` 12.5 KB, `hollow` 7.3 KB, `quiz` 6.7 KB.
- Compositions: 28 channel x form, 14 method x method, 15 other; none involve three tokens.

### Ontology
Primitives and the dimension each owns: task (verb), topology (reasoning visibility), completeness
(extent), scope (subject focus), method (procedure), form (output organization), channel (delivery),
directional (orientation), persona (register). Token names are globally unique across axes.
`directional` flattens two dimensions: its 16 tokens are vertical {none, fog, dig, fig} x
horizontal {none, rog, ong, bog}, with `jog` the null cell.

### Axioms (derived; enforcement not verified)
- A1 token names belong to exactly one axis (holds).
- A2 every token states a distinction against its nearest neighbour (violated by 15 tokens; `jog` exempt).
- A3 singleton axes take one value; soft caps scope 2, method 5, form 1, channel 3, directional 1.
- A4 conflicts resolve by priority topology > completeness > scope > method > form > channel.
- A5 same-axis conflicts are enforced through `hierarchy.axis_incompatibilities`; cross-axis conflicts are
  advisory and live in `cross_axis_composition`. Each kind has exactly one home.
- A6 a composition adds only what neither token says alone.

### Snags
- A5 (corrected): `hierarchy.axis_incompatibilities` is empty for every axis, but it is a live
  enforcement hook, not a duplicate store. `lib/talonSettings.py` uses it for last-wins eviction in
  `_canonicalise_axis_tokens`; `internal/barcli/help_llm.go` renders it under "Grammar-enforced
  restrictions" and already says cross-axis incompatibilities are advisory; `web/src/lib/incompatibilities.ts`
  consumes it. It is same-axis only, so it cannot hold the cross-axis entries. The first draft of this
  ADR called it a violation; that was wrong.
- Declared two-owner concepts: method<->scope (adversarial/fail, assume/gap/unknowns,
  authority/actors/control, bound/dam, flow/time, mapping/struct); form doing method's work
  (ontology/gloss, coupling/snag, argue/ibis/case, gate/runbook); completeness doing method's work
  (minimal/prune, narrow/redact, grow/lazy, zoom/ladder/navigate); form<->channel (axiom/formal,
  chart/diagram, plain/tight, snap/ledger/store).
- A6 violated: `ground+falsify` (~7 KB) restates Gate 1-3 and the `§ ground complete` marker.
- 289 of 560 distinctions are one-directional.
- Undeclared near-duplicates: html~svg (0.57 similarity); adversarial~unknowns (0.41).
- Eight distinctions target task names, not tokens (compare->check, sense->check, winnow->pick, ...).
- Method x topology has three declared seams (ground/live, pin/witness, falsify/audit) although
  topology constrains every method.
- Hierarchy omits directional from the priority order and persona entirely; topology and
  completeness have no soft cap.

## Decision (proposed fixes, in order)

1. Keep `hierarchy.axis_incompatibilities`; do not delete it. Document the division (same-axis
   enforced, cross-axis advisory) where the catalog describes the hierarchy. Deleting it would touch
   Python, Go and the web SPA, plus their tests, to remove a hook that is empty by design.
2. Declare the missing seams: html/svg first, then adversarial/unknowns. Check each with the
   duplication discriminator from ADR-0085.
3. Mirror the 289 one-way distinctions, or record in the guidebook that one-way is intentional.
   Prefer a generated check over hand edits.
4. Move procedure out of the `ground` and `falsify` definitions into referenced blocks, then slim
   `ground+falsify` to the interaction only.
5. Model directional as two axes (vertical, horizontal) in the grammar, keeping the 16 spoken
   tokens as aliases so existing usage does not break.
6. Add a catalog test that enforces A1 and A2, and that no cross-axis pair is registered in
   `axis_incompatibilities` (A5), so the audit does not need rerunning by hand.

## Progress (2026-11-08)

- A2 closed: distinctions authored for the 15 tokens, each stated from both sides (24 pairs); two
  existing notes (`tight`->`plain`, `demo`->`shellscript`) restated affirmatively; `dialogue` gained a
  metadata entry and heuristics. `validate_token_names_unique_across_axes` and
  `validate_distinctions_present` run in `axis-catalog-validate.py`; the A5 same-axis check is a unit
  test because reading the hierarchy imports `lib.talonSettings`, which the CLI cannot always load.
- Not done: reciprocal mirroring of the remaining one-way distinctions (~289 before this change),
  `adversarial`/`unknowns`, and the items below.

## Follow-up: deny-list phrasing in definitions

Token definitions should state what the output contains, not what it must not do (nn
`20260513141540-7254`, prior art for `blind` and `solo`). Measured on the catalog: the phrase
"does not satisfy" appears in 18 definitions (about 35 occurrences): all six topology tokens, scope
`jobs`, method `eliminate`, `falsify` (4), `gate`, `ground` (9), `mark`, `own`, `prism` (3), `redact`,
`shoshin` (2), form `quiz`, channel `zettel` (2). Many other tokens use other negations; those are
not yet classified. Each rewrite is a token-rewrite sequence run (definition rewrites), so this is its
own piece of work. Open question to settle first: some closing clauses were added deliberately to
close escape routes found by hollow audits, so each needs an allow-list restatement that keeps the
observable requirement.

## Consequences

- Fixes 1-3 are data-only and low risk. Fix 4 touches the largest definitions and needs the
  craft-pack evals rerun. Fix 5 changes grammar shape and the generated artifacts
  (`prompt-grammar.json` copies), so it should be its own ADR.
- Any edit to a token description or composition entry is governed by the bar token protocols.

## Not checked

Whether the tool enforces A3/A4 at build time; whether one-way distinctions were deliberate;
per-token behaviour of the heavy definitions.
