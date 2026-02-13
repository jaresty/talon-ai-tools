# ADR-0110: Token Guidance Field — Separate Selection Hints from Execution Instructions

## Status

Accepted — Implementation complete (D1–D5). All 7 audit token descriptions trimmed of
selection guidance; guidance content lives exclusively in the guidance field.

## Context

Token `description` fields currently serve two distinct purposes simultaneously:

1. **Execution instruction** — prose injected into the bar prompt that tells the executing LLM
   how to generate the response ("The response focuses on...", "The response consists only of...")

2. **Selection guidance** — meta-commentary that helps a human or selecting LLM decide *whether*
   to reach for this token ("Note: `fix` is a reformat task, not a debug task", "Not appropriate
   for narrative tasks")

These audiences are different, the content is different, and the timing is different. Execution
instruction is consumed at response-generation time. Selection guidance is consumed at
token-selection time, *before* the command is built.

### Concrete Examples of Mixed Descriptions

**`task:fix`** (clearest case):
> "The response changes the form or presentation of given content while keeping its intended
> meaning. **Note: in bar's grammar, `fix` is a reformat task, not a debugging task. For work
> that involves correcting defects or errors, use `make` or `show` paired with diagnostic method
> tokens (`diagnose`, `inversion`, `adversarial`).**"

The sentence from "Note:" onward has no effect on the executing LLM. Its only purpose is to
redirect a selector who mis-reaches for `fix`. Injecting it into the prompt adds noise.

**`channel:code`**:
> "The response consists only of code or markup as the complete output, with no surrounding
> natural-language explanation or narrative. **Not appropriate for narrative tasks (`sim`, `probe`)
> that produce prose output rather than code.**"

The second sentence is a selection warning. The executing LLM does not need it; it already
has its instruction. It exists only to steer the person (or agent) building the command.

**`channel:html`**, **`channel:shellscript`**, **`channel:gherkin`**, **`channel:codetour`**:
All share the same "Not appropriate for narrative tasks..." pattern — selection warnings appended
to execution instructions.

**`form:facilitate`**:
> "... When combined with `sim`, designs a facilitation structure for a simulation exercise
> rather than performing the simulation directly."

This is affinity guidance: it describes a specific token combination's behavior for the benefit
of a selector, not a behavioral constraint for the executing LLM.

### Why This Matters

- **Prompt purity**: Execution instructions should be minimal and unambiguous. Selection noise
  can cause an executing LLM to second-guess the instruction or over-apply caveats.
- **ADR-0108 precedent**: `quiz`, `cocreate`, `facilitate` had incompatibility claims embedded
  in their descriptions that turned out to be incorrect assumptions. Mixing guidance into
  descriptions makes it easy to encode assumptions that become stale.
- **ADR-0109 context**: The label field (ADR-0109) addresses the very-short case (3-8 words).
  `guidance` addresses the medium case: 1-3 sentences of selection-oriented prose that doesn't
  fit in a label but doesn't belong in the injection text.

### What Guidance Is Not

- **Hard incompatibilities**: Already handled by `hierarchy.incompatibilities` (machine-readable,
  validation-enforced). Guidance is *soft* — advisory, not enforced.
- **Channel-adaptive behavior**: "Without an output-exclusive channel, does X; with one, does Y"
  is *execution* instruction — the executing LLM needs it to behave correctly. This stays in
  `description`.
- **The label**: The label (ADR-0109) is a 3-8 word selection summary. Guidance is longer-form
  selection prose that can't be reduced to a label.

---

## Decision 1: Add Optional `guidance` Field to Grammar Schema

Add a `guidance` section parallel to `definitions` under `axes`, and a `guidance` field under
`tasks`:

```json
{
  "axes": {
    "definitions": { "channel": { "code": "The response consists only of code…" } },
    "labels":      { "channel": { "code": "Code-only output" } },
    "guidance":    { "channel": { "code": "Avoid with narrative tasks (sim, probe) that produce prose rather than code." } },
    "list_tokens": { ... }
  },
  "tasks": {
    "catalog": { ... },
    "labels":   { "fix": "Reformat existing content" },
    "guidance": { "fix": "In bar's grammar, fix means reformat — not debug. To correct defects, use make or show with diagnose, inversion, or adversarial." }
  }
}
```

`guidance` is **optional per token**. Most tokens need no guidance — only those with genuine
selection ambiguity, naming gotchas, or meaningful soft affinities.

---

## Decision 2: Audit Existing Descriptions and Extract Guidance Content

The following tokens have identifiable guidance content mixed into their current descriptions.
Each should have that content moved to `guidance` and the `description` trimmed to pure
execution instruction:

| Token | Guidance to extract |
|-------|-------------------|
| `task:fix` | "Note: `fix` is a reformat task, not a debugging task. For defect correction, use `make` or `show` with `diagnose`, `inversion`, or `adversarial`." |
| `channel:code` | "Not appropriate for narrative tasks (`sim`, `probe`) that produce prose output." |
| `channel:html` | "Not appropriate for narrative tasks (`sim`, `probe`) that produce prose output." |
| `channel:shellscript` | "Not appropriate for narrative tasks (`sim`, `probe`) that produce prose output." |
| `channel:gherkin` | "Appropriate for tasks that map naturally to scenario-based behavior." *(currently phrased as selection guidance inline)* |
| `channel:codetour` | "Appropriate for tasks involving code navigation or explanation." *(same pattern)* |
| `form:facilitate` | "When combined with `sim`, designs a facilitation structure for a simulation exercise rather than performing the simulation directly." |

Additional tokens may surface during a full audit of all descriptions.

---

## Decision 3: Expose `AxisGuidance()` and `TaskGuidance()` on Grammar

```go
// AxisGuidance returns the optional selection-guidance text for the given axis token.
// Returns empty string if no guidance is defined.
func (g *Grammar) AxisGuidance(axis, token string) string

// TaskGuidance returns the optional selection-guidance text for the given task token.
// Returns empty string if no guidance is defined.
func (g *Grammar) TaskGuidance(name string) string
```

---

## Decision 4: Surface Guidance in Help and Reference Outputs

**`bar help tokens` (non-plain):** Show guidance after the description, indented and prefixed:

```
  channel:
    • code: Code-only output
      The response consists only of code or markup as the complete output…
      ↳ Avoid with narrative tasks (sim, probe) that produce prose rather than code.
```

Tokens without guidance show nothing extra.

**`bar help tokens --plain`:** Guidance is omitted. The plain format is for programmatic
consumption; guidance is too verbose for that use case and the tab-separated label (ADR-0109)
already provides selection signal there.

**`bar help llm` Token Catalog:** Add a `Notes` column to the three-column table established
in ADR-0109:

```markdown
| Token | Label | Description | Notes |
|-------|-------|-------------|-------|
| `fix` | Reformat existing content | The response changes the form… | fix means reformat, not debug. For defect correction use make or show + diagnose. |
| `code` | Code-only output | The response consists only of code… | Avoid with narrative tasks (sim, probe). |
```

Tokens without guidance have an empty `Notes` cell.

**TUI (`bar tui2`):** Show guidance text on demand (e.g., expanded view or help panel) —
not in the primary token list alongside the label.

---

## Decision 5: Update `lib/promptGrammar.py` to Pass Guidance Through

Following the pattern of ADR-0109 Decision 6, add two new catalog keys:

| New catalog key | Shape | Consumed by |
|----------------|-------|-------------|
| `axis_guidance` | `{axis: {token: guidance_text}}` | `_build_axis_section` → `axes.guidance` in JSON |
| `static_prompt_guidance` | `{task: guidance_text}` | `_build_static_section` → `tasks.guidance` in JSON |

---

## Consequences

### Positive

- **Cleaner execution instructions.** Descriptions become tighter behavioral contracts with
  no meta-commentary noise.
- **Formal home for selection hints.** Authors have an obvious place to put gotchas, naming
  traps, and soft affinities without polluting the prompt.
- **Reduces ADR-0108-class errors.** Guidance that proves wrong can be corrected without
  touching the execution instruction. The two concerns no longer constrain each other.
- **Discoverable in reference outputs.** `bar help llm` and `bar help tokens` surface guidance
  where it's useful; `--plain` omits it where it's noise.
- **Complements ADR-0109.** label (3-8 words) + guidance (1-3 sentences) + description (full
  instruction) gives three distinct fields for three distinct audiences.

### Negative

- **Audit cost.** Existing descriptions must be reviewed to identify and extract mixed content.
  Some cases are unambiguous (`task:fix`); others require judgment.
- **Schema version bump.** Adding `guidance` alongside `labels` (ADR-0109) can be batched
  into a single bump if the two ADRs are implemented together.
- **Not every token benefits.** Most tokens have clean descriptions already. The field risks
  being underused or unevenly applied. Authoring guidelines should clarify the bar for adding
  guidance (genuine selection ambiguity or naming trap — not general commentary).

### Neutral

- These two ADRs (0109 and 0110) share implementation surface: both add optional fields to
  the grammar schema, both require Python and Go changes, both affect the same help outputs.
  Implementing them together reduces total overhead.
