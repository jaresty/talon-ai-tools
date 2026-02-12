# ADR-0108: Channel-Adaptive Interactive Forms

## Status
Completed

## Context

ADR-0107 D1 classified `cocreate`, `quiz`, and `facilitate` as "interactive forms" — incompatible
with output-exclusive channels — and added a conflict warning to both the token descriptions and
the `bar help llm § Incompatibilities` section.

On reflection, the incompatibility is an artifact of how the descriptions were written, not a
fundamental constraint. The form descriptions defined the behavior as requiring back-and-forth
interaction, but the **organizing principle** of each form is distinct from its interaction mode:

- `quiz` organizes content as question-before-explanation sequences
- `cocreate` organizes content as small-move proposals with explicit decision points
- `facilitate` organizes content as a session structure with goal-framing and participation design

These organizing principles are fully expressible in static artifacts. A `quiz + presenterm`
combination naturally produces a quiz-formatted slide deck — questions as slide headers, answers
beneath, knowledge checks before reveals. A `facilitate + sync` combination produces a session
agenda. Neither requires interaction to be coherent; interaction is the *default mode* when no
output format constrains it.

The channel-adaptive pattern — already established for `taxonomy` and `visual` in ADR-0106 D4 —
provides the correct model: a form applies its organizing principle to the output structure; when
an output-exclusive channel is present, that channel determines the format while the form shapes
the rhetorical structure within it.

**Evidence:** Cycle 5 seeds 0082 (cocreate+svg=2) and 0085 (quiz+presenterm=2) were scored as
conflicts. Under channel-adaptive semantics, quiz+presenterm would produce a coherent quiz deck
and would score ≥4.

---

## Decision 1: Rewrite `quiz`, `cocreate`, `facilitate` as Channel-Adaptive Forms

Replace the "Interactive form — requires back-and-forth dialogue" framing with channel-adaptive
descriptions that explicitly describe both modes:

**`quiz` (new description):**
> Organizes the response as a quiz structure — questions posed before explanations, testing
> understanding through active recall before providing answers. Without an output-exclusive
> channel, conducts this as an interactive exchange: poses questions, waits for responses,
> then clarifies or deepens. With an output-exclusive channel (`presenterm`, `code`, `diagram`,
> etc.), structures the output itself as a quiz — question headings with revealed answers,
> test sections, knowledge checks — without requiring live interaction.

**`cocreate` (new description):**
> Structures the response as a collaborative process — small moves, explicit decision points,
> and alignment checks rather than a one-shot answer. Without an output-exclusive channel,
> conducts this interactively: proposes, pauses for feedback, and iterates. With an
> output-exclusive channel, formats the artifact to expose decision points, show alternative
> moves, and make the response-inviting structure visible within the output.

**`facilitate` (new description):**
> Structures the response as a facilitation plan — framing the goal, proposing session
> structure, managing participation and turn-taking rather than doing the work solo. Without
> an output-exclusive channel, acts as a live facilitator: proposes structure and invites
> participation interactively. With an output-exclusive channel, produces a static facilitation
> guide: agenda, goals, cues, and session structure as a deliverable artifact.

---

## Decision 2: Remove the Interactive-Form Conflict Rule from `bar help llm`

The "Interactive-form conflicts" section added in ADR-0107 D1 listed `cocreate`, `quiz`, and
`facilitate` as incompatible with all output-exclusive channels. This section should be removed
now that those forms are channel-adaptive.

The remaining incompatibility content (output-exclusive conflicts, task-affinity restrictions,
prose-form conflicts, semantic conflicts) remains unchanged.

---

## Consequences

### Positive

- `quiz + presenterm`, `quiz + code`, `facilitate + presenterm`, `cocreate + svg` are now valid
  combinations — the channel constrains the output format and the form shapes the rhetorical
  structure within it.
- Fewer catalog entries carry incompatibility warnings, making the catalog more approachable.
- Consistent with the channel-adaptive pattern established for `taxonomy` and `visual`.
- The ADR-0107 D3 guidance on `sim + facilitate` remains valid and useful: without a channel,
  `sim + facilitate` still creates the same role ambiguity (simulate vs. facilitate a simulation).
  With an output-exclusive channel (e.g., `sync`), the combination is unambiguous: it produces
  a session plan for a simulation exercise.

### Negative / Tradeoffs

- `cocreate + svg` is now permitted. The combination is coherent (an SVG exposing decision
  points or alternative moves), but the usefulness is narrow. It will no longer be flagged
  as a conflict; users should understand it produces a design-proposal SVG, not a dialogue.
- Partially supersedes ADR-0107 D1 (interactive-form conflicts). ADR-0107 D2–D5 remain
  unchanged.

---

## Follow-up Work

**Files to change:**
- `lib/axisConfig.py`: rewrite `cocreate`, `quiz`, `facilitate` form descriptions (D1)
- `internal/barcli/embed/prompt-grammar.json`: regenerated from axisConfig.py
- `internal/barcli/help_llm.go`: remove Interactive-form conflicts section (D2)
- `internal/barcli/help_llm_test.go`: update ADR-0107 test assertions; add ADR-0108 test
