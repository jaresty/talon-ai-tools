# ADR-0196: Why-Framing — Purpose Statements to Reduce Meta-Ambiguity

**Status**: Proposed
**Date**: 2026-03-28

---

## Context

Repeated protocol violations share a common root: models treat rules as constraints to navigate rather than as consequences of a single underlying purpose. A model that understands *why* a rule exists applies better judgment at margins; a model that only sees rules finds workarounds.

Analysis using `bar probe mean struct gap` identified four levels of missing "why":

### Level 1 — Why this protocol exists at all

No sentence in the prompt explains why the ground protocol needs to exist. A model without this framing cannot distinguish "the protocol requires me to pause here" from "the protocol is a bureaucratic obstacle." The underlying reason: **a model's description of completed work is structurally indistinguishable from actually completing it**. Text about an implementation, text about its tests, and text about their results are all equally valid outputs of a language model — none require the described thing to exist. The protocol's purpose is to enforce the distinction.

### Level 2 — Why rung gates are gated on tool-executed events (already partially added)

ADR-0196 partially addresses this: "every rung gate exists to prevent one class of error: claiming evidence without producing it." This is the mechanical consequence of Level 1, not the motivation. It was added as a preamble before A3 in a prior session but size cap tests were not yet updated.

### Level 3 — Why the descent has seven specific rungs

No sentence explains why each rung exists or why skipping one is wrong. The rule "each rung may not be skipped or combined" exists but has no motivating sentence. The underlying reason: **each rung forces a kind of specificity the prior rung cannot enforce** — prose makes intent legible, criteria makes it falsifiable, formal notation makes it precise, EV makes it executable, VRO confirms it fails, EI produces the fix, OBR confirms it runs live. Skipping a rung leaves open the escape route that rung closes.

### Level 4 — Three local why-sentences for structurally distinct violations

Three rules are violated because the model misunderstands the *category* of the artifact, not just the rule:

**Criteria batch-collect:** Models treat the criteria rung as a planning phase — collect all thread criteria, then descend. The missing why: "writing criteria for all threads before any descent treats the rung as a planning step; it is an evidential gate — each thread's criterion is only valid in the context of that thread's descent, not as a batch plan."

**R2 audit sentinel ordering:** Models emit the `✅ Formal notation R2 audit complete` sentinel immediately after the notation body, treating it as a closing header. The missing why: "the sentinel closes an audit that already exists in the transcript; emitting it first inverts causality — you are claiming completion before the evidence exists."

**Gap-before-criterion:** Models write the criterion first, then the Gap. The missing why: "the Gap names the currently-false assertion that the criterion will make true — writing the criterion before the Gap proposes a repair before naming what is broken."

---

## Decision

Add four why-sentences to `lib/groundPrompt.py` in order of scope:

### Addition 1 — Protocol-level purpose (before all existing text)

> "This protocol exists because a model's description of completed work is indistinguishable from actually completing it — every gate enforces the distinction by requiring a piece of reality before any claim about reality."

### Addition 2 — Gate mechanism purpose (already present as of prior session, update size caps)

> "Every rung gate exists to prevent one class of error: claiming evidence without producing it. A sentinel is not a summary of what you believe happened — it is a claim that a specific tool-executed event exists in this transcript; if that event is absent, the sentinel is false regardless of prediction or prior knowledge."

### Addition 3 — Descent structure purpose (before the seven-rung list)

> "Each rung forces a kind of specificity the prior rung cannot enforce: prose makes intent legible, criteria makes it falsifiable, formal notation makes it precise, EV makes it executable, VRO confirms it fails, EI produces the fix, OBR confirms it runs; skipping a rung leaves open the escape route that rung closes."

### Addition 4 — Three local why-sentences

- At the criteria batch-collect rule: "each thread's criterion is only valid in the context of that thread's descent — writing criteria for all threads before descending any treats the rung as a planning step, which it is not"
- At the R2 audit sentinel rule: "the sentinel closes an audit that already exists in the transcript; emitting it before the audit section inverts causality — you are claiming completion before the evidence exists"
- At the Gap-before-criterion rule: "the Gap names the currently-false assertion that the criterion will make true; writing the criterion first proposes a repair before naming what is broken"

---

## Implementation

Changes to `lib/groundPrompt.py`:
1. Addition 1 before existing text (new first sentence)
2. Addition 2 already present — verify position
3. Addition 3 before "Seven rungs in order:" line
4. Addition 4a at criteria batch-collect block
5. Addition 4b at R2 audit sentinel rule
6. Addition 4c at Gap-before-criterion rule

Update size caps in affected tests.

New test file: `_tests/ground/test_ground_adr0196_why_framing.py`

---

## Consequences

- **Positive**: models can apply principled judgment at rule margins rather than pattern-matching on prohibitions
- **Positive**: the three local why-sentences address category errors (planning-vs-gate, causality inversion, repair-before-defect) not covered by the global preamble
- **Known limitation**: a model that has already decided to violate a rule will not be corrected by knowing why the rule exists — why-framing helps at margins, not for adversarial non-compliance
- **Size**: four additions will increase prompt size; net effect must be measured against size caps
