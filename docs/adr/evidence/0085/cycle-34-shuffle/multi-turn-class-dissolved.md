# Strip test: the multi-turn / static-artifact rule

Per nn 20260929154929-2747 corollary: strip the general half; does a form-specific remainder survive?

| Form | Its clause | General half | Form-specific remainder |
|---|---|---|---|
| facilitate | "Without an output-exclusive channel, acts as a live facilitator; with one, produces a static facilitation guide" | live-vs-static switch | "live facilitator" / "facilitation guide" — names WHAT it becomes |
| interactive | "state may be carried by ... an artifact whose format another token governs — in which case the available inputs are the points in that artifact the other side can act on" | live-vs-static switch | "available inputs are the points in the artifact" — names WHAT the inputs become |
| quiz | "An answer is permitted in the same response turn ... only when the current response is producing a static document or terminal sequence artifact" | live-vs-static switch | the Predict:-gate suspension — names WHICH requirement lifts |
| twin | (absent) | — | — (unguided; this is why quiz x svg scored 2/5 and facilitate x sketch 4/5) |

CONCLUSION: unlike the ontology/taxonomy/axiom case, the general half here is SUBSTANTIAL and
identical across three forms, while each remainder is one short phrase. So the general rule moves to
the metaprompt and each form keeps a short phrase naming what its live mode collapses INTO.

This is the same shape as cycle 32's seven-forms finding, at a different joint:
  cycle 32: 7 forms each restated "express the form through the channel's format"
  cycle 34: 3 forms each restate "collapse turn-taking into the artifact when output is static"
In both cases the duplication is the symptom of a missing axis-level rule, and the forms that did
NOT restate it are the ones that score badly.

## CORRECTION — this finding dissolved on verification

Two errors in the table above, both caught before any edit:

1. **`twin` is not a multi-turn form.** My regex matched it on the phrase "the reader", which is an
   audience reference, not turn-taking. Its actual definition: "presents two or more alternatives
   side-by-side... so the reader can compare them directly". So the class has THREE members, not
   four — and all three already state the rule. There is no unguided member.

2. **`quiz` x `svg` was scored on the wrong mechanism.** quiz DOES state the rule ("An answer is
   permitted in the same response turn ... only when the current response is producing a static
   document or terminal sequence artifact"), so the turn-taking resolves: static artifact -> answers
   inline, Predict-gate suspended. The real collision is that SVG has no text-sequence construct to
   hold question/answer pairs — an ordinary form/channel case the NARROWED axis rule already covers
   via the adjacent-block branch.

So: no missing axis-level rule here. The duplication across three forms is real but each statement
carries a form-specific remainder (what the live mode collapses INTO), and with no unguided member
there is no gap the duplication is a symptom of. Unlike cycle 32's seven forms, extracting a general
rule here would buy consistency at the cost of three short clauses — not a defect fix.

**Not acted on.** Recorded because the reasoning pattern is the trap: "N forms state the same thing"
looked identical to the cycle-32 finding, and the thing that distinguished them was checking whether
any form LACKED the clause. In cycle 32, 44 did. Here, none does.
