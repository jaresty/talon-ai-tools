# Cycle 26 — Phase 2e Distinction Check

Decision rule (established cycles 24-25): **composition** when a coherent output satisfies both
tokens — including two coexisting artifacts (pure artifact + adjacent prose block).
**Cautionary** only when honoring one token structurally STARVES the other with no coexisting
output.

## Structural finding first: `code` never received the `svg` treatment

Shipped state (verified this cycle):

| Channel | Prose-form conflicts resolved as... |
|---|---|
| `svg` | **compositions** — ghost+svg, prep+svg, twin+svg, contextualise+svg (prose block adjacent to artifact) |
| `gherkin`, `sketch`, `shellscript`, `codetour` | **compositions** — cards+gherkin, contextualise+{gherkin,sketch,shellscript,codetour} |
| `code` | **cautionary only** — faq+code, recipe+code ("use plain or no channel"). **Zero compositions.** |

`code` ("only code or markup as the complete output, with no surrounding natural-language
explanation") is structurally the same case as `svg` ("solely SVG markup ... with no prose").
The adjacent-prose-block resolution that svg received applies identically. `code` simply never
got it — the same mis-layering cycle-24 corrected for contextualise's DSL cautions.

This is the cycle's headline: not a new mechanism, an **unpropagated one**.

## Per-finding judgments

### prep + code → COMPOSITION (confirmed)
Direct sibling of the shipped `prep+svg`. prep needs four prose sections; code forbids prose in
the artifact. Coexisting output exists: the prep write-up as a prose block before/after the code
artifact — verbatim the prep+svg resolution. Composition.

### snap + zettel → COMPOSITION (confirmed)
Coherent output exists and is *better* than either alone: decompose the snapshot's four parts
(progress / decisions / remaining / context) into one-claim notes satisfying zettel's "exactly
one claim per body", plus an entry note carrying the resume pointer that preserves snap's
"resume from here" function. Both satisfied, nothing starved. Composition.

### interactive + code → CAUTIONARY (confirmed)
Tested against the rule and it FAILS the coexistence test, unlike prep+code. interactive is not
supplementary content that can sit adjacent — it is a *turn-taking protocol*: "advance the shared
epistemic state incrementally ... names a current state and at least one available option",
which requires the counterparty to respond into the same exchange. An adjacent prose block does
not satisfy it, because the interaction must *be* the response, not accompany an artifact. This
is the `tight`-shaped case (whole-response form) — except tight was fixable by deleting a bogus
format claim, whereas interactive's turn structure is genuine and load-bearing. One token
starves the other → cautionary.

Contrast that makes the rule precise:
- **prep** = supplementary *content* (a write-up) → composes adjacently.
- **interactive** = whole-response *protocol* (an exchange) → cannot compose; cautionary.

### minimal + models → CAUTIONARY (confirmed)
Same family as shipped `skim+rigor` and `skim+orbit` (completeness floor vs method minimum).
models has a structural floor: name the operative model set, plus each absent model with why it
applies and what it surfaces. minimal licenses "the smallest answer that satisfies the request."
No coexisting output: satisfying models' enumeration floor exceeds minimal; honoring minimal
starves the enumeration. Cautionary, extending the family from `skim` to `minimal`.

### mark + code → NOT ACTED (weak isolation)
mark's '## Step N' checkpoint headers are prose structure that code-only output cannot host —
mechanically the same as prep+code. But seed 223 also contained the already-cautioned sim+code,
so mark's contribution to the low score is not isolated. Pattern-watch; revisit if mark appears
with an artifact channel in a seed without a confounding cautionary.

### models + pull → NOT ACTED (mild)
models introduces external frames; pull extracts "without altering substance". Additive-vs-verbatim
tension, same mildness as cycle-24's jobs+pull (scored 4/5 there). Pattern-watch.

**Limitation:** single evaluator; compare prompts reasoned, not executed by a fresh model. The two
composition findings extend shipped compositions (prep+svg) and the two cautionary findings extend
shipped cautionary families (skim+rigor/orbit) — mechanisms already tested, only membership new.
