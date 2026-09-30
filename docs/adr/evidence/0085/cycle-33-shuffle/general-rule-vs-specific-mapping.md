# Strip test per nn 20260929154929-2747 corollary

Test: remove the general frame (Half A). Does the remainder still say something true and
specific that the axis rule cannot derive?

| Form | Half B remainder | Derivable from axis rule? |
|---|---|---|
| ontology | graph channel -> nodes and labelled edges; code/notation -> formal schema (types, fields, constraints) | NO — "construct that can carry concepts+relations" does not yield "labelled edges" |
| taxonomy | code/notation -> type system (interfaces, enums, hierarchies); nesting -> nested structure | NO — does not yield "interfaces, enums" |
| axiom | formal/code/notation -> predicates or type-system constraints | NO — does not yield "predicates" |
| facilitate | "acts as a live facilitator" vs "static facilitation guide" | NO — CORRECTED. This is a MODE switch (does the response conduct a live session), not a rendering rule. The axis rule governs WHERE the form's content goes, never whether the response acts live. Kept. |

Conclusion: keep Half B as a short mapping; delete Half A from the three mapping forms
(ontology, taxonomy, axiom) — the axis rule carries it. facilitate is KEPT: on closer reading its
clause is a behavioral mode switch, not a rendering frame, so the axis rule does not subsume it.
My first pass on this row was wrong.

## What moved to the metaprompt and what could not

The general frame — "where the channel has a construct that can carry the form, express it through
that construct; where it has none, place the form's content adjacent to the artifact" — is now
stated ONCE, in the form axis description (`AXIS_KEY_TO_AXIS_DESC["form"]`, delivered on the
`bar build` path since d2383ed7). Every form inherits it.

The specific mappings cannot move there, because they are facts about the FORM, not about channels:
no general rule derives "ontology → nodes and labelled edges" from "ontology defines concepts and
relations". They stay as one short clause per form.

## The defect this found in my own prior edit

Commit 1eb6d3d4 (an hour earlier) converted three member-list enumerations to construct partitions.
That fixed the fallthrough — but it wrote the general frame into all three descriptions, reproducing
the exact surplus that cycle 32 had deleted from `ghost`. Both the axis line and each form's clause
then said "construct that can carry", verified in one rendered result (`bar help token ontology`
contained both phrasings).

Removed the frame from ontology, taxonomy and axiom; kept each mapping.

- ontology: "A graph channel renders the concepts and relations as nodes and labelled edges; a code
  or notation channel as a formal schema of types, fields and constraints."
- taxonomy: "A code or notation channel renders the hierarchy as a type system of interfaces, enums
  and hierarchies; a channel with a nesting construct as nested structure."
- axiom: "A formal, code or notation channel renders the axioms as predicates or type-system
  constraints."

## A correction to this document's own first pass

The table above initially recorded `facilitate` as pure surplus, fully derivable from the axis rule.
That was wrong. Its clause — "Without an output-exclusive channel, acts as a live facilitator; with
one, produces a static facilitation guide" — is a BEHAVIORAL MODE switch: whether the response
conducts a live session. The axis rule governs where the form's content goes, never whether the
response acts live. Kept, and the row corrected in place.

## Guard

D4 in `TestLLMHelpChannelAffinityAndTokenClarity` had been anchored (earlier this session) to
"active channel's constructs can carry" — the general frame. Once that frame moved to the axis line,
the assertion would have passed on any form's text and said nothing about taxonomy. Re-anchored to
"type system of interfaces", which only taxonomy can state. Shown to discriminate: perturbing that
phrase produces RED naming the row; restoring produces GREEN.

## Standing rule this suggests

When a general rule is added at the axis level, the per-token clauses it now covers must be
RE-READ and split: delete the half the axis rule carries, keep the half only that token can state.
Adding the general rule without doing the split leaves the duplication that the general rule was
meant to remove — which is what 1eb6d3d4 did.
