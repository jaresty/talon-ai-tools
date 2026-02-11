# ADR-0106: Channel Affinity, Compound Directionals, and Token Clarity

## Status
Accepted

## Context

Cycle 4 of the shuffle-driven catalog refinement process (seeds 0061–0080, ADR-0085 evidence)
produced a mean score of 3.4/5 — a regression from cycle 3's 3.9/5 — with 25% of seeds scoring
≤2 (problematic or broken). Four distinct problem categories emerged.

**Evaluation evidence base:**
- Cycle 4: seeds 0061–0080 (50% excellent, 25% acceptable, 25% problematic/broken)
- ADR-0105 improvements were visible: heuristics now accurate, § Incompatibilities now populated,
  codetour/gherkin task-affinity documented
- Regression source: form+channel conflicts reappeared in new combinations not yet documented

---

## Decision 1: Extend Code-Channel Task-Affinity Guidance

### Problem

`code`, `html`, and `shellscript` channels mandate code- or markup-only output. They work
correctly with code-producing tasks (`fix`, `make`, `pull`, `show` with code subject) but
produce incoherent results when paired with narrative tasks. ADR-0105 D2 addressed this for
`codetour` and `gherkin`, but the same issue exists for the three code-output channels:

**Evidence from cycle 4 corpus:**
- Seed 0072 (cycle 4): `sim` + `code` channel — scenario playback cannot be expressed as
  code-only output; sim produces prose narrative by definition. Scored 2/5.

`sim` and `probe` both produce prose narrative. Neither can produce valid code-only output
regardless of subject matter.

### Decision

Add task-affinity guidance to `code`, `html`, and `shellscript` channel descriptions:

**code / html / shellscript (add to description):**
> Not appropriate for narrative tasks (`sim`, `probe`) that produce prose output rather
> than code or markup.

Also add a corresponding rule to `bar help llm` § Incompatibilities § Task-affinity restrictions:
> `code`, `html`, `shellscript` channels: not appropriate for narrative tasks (`sim`, `probe`)
> that produce prose output rather than code or markup.

---

## Decision 2: Document Prose-Form / Code-Channel Conflict Class

### Problem

The `bar help llm` § Incompatibilities section (added in ADR-0105 D5) covers output-exclusive
channel conflicts, codetour/gherkin task-affinity, and the rewrite+make semantic conflict.
However, a broader conflict class is absent: **prose-producing form tokens conflict with
code/markup channels**.

Form tokens like `case`, `formats`, `walkthrough`, and `scaffold` produce structured prose.
Channels `code`, `html`, and `shellscript` mandate code or markup as the complete output.
These are incompatible — the form constrains the LLM to produce prose structure while the
channel mandates code structure.

**Evidence from cycle 4 corpus:**
- Seed 0075: `fix` + `act` + `case` + `code` — case form (structured argument) + code channel
  (code-only) → format conflict. Scored 2/5.
- Seed 0076: `sim` + `prioritize` + `formats` + `slack` — formats form (multiple output
  varieties) + slack channel (enforces Slack markdown) → single-channel/multi-format
  tension. Scored 2/5.
- Seed 0061: `diff` + `visual` + `codetour` — visual form + codetour channel → double format
  mandate. Scored 1/5 (also a task-affinity failure).

The pattern is: any form token that defines a prose output structure is incompatible with
any channel that mandates code or markup as the complete output.

### Decision

Add a prose-form conflict rule to `bar help llm` § Incompatibilities:

**Prose-form conflicts (add to § Incompatibilities):**
> Form tokens that produce structured prose (`case`, `formats`, `walkthrough`, `scaffold`,
> `recipe`, `faq`, `table`, `taxonomy`, `visual`, `variants`, `checklist`, `actions`) conflict
> with channels that mandate code or markup as the complete output (`code`, `html`, `shellscript`).
> Use prose-producing forms only with channels that support natural language (`jira`, `slack`,
> `sketch`, `plain`) or with no channel token.

Note: `test` form is an exception — it produces test case code and is compatible with code
channels. Similarly `diagram` channel produces Mermaid code and is compatible with structured
visual forms.

---

## Decision 3: Document Compound Directional Tokens

### Problem

Directional tokens in bar can be combined into compound tokens: `fly rog`, `fip rog`, `dip ong`,
`dip bog`, `fip ong`, etc. These render as single tokens with merged descriptions and are
legitimate grammar constructs (not axis violations — the directional axis accepts one compound
token). However, they are completely absent from:

- `bar help llm` § Token Catalog § Directional
- `bar help llm` § Token Selection Heuristics
- All skill documentation (`bar-manual`, `bar-autopilot`, `bar-workflow`)

A user building a bar command manually by consulting `bar help tokens directional` or
`bar help llm` would see only the primitive tokens (`fly`, `rog`, `fip`, `bog`, `dip`, `ong`,
`dig`, `fog`). They would have no indication that these can be combined or that the compounds
have their own merged descriptions.

**Evidence from cycle 4 corpus:**
Compound directionals appeared in 6 of 20 seeds (0070, 0071, 0074, 0075, 0077, 0079),
all rendering correctly but all invisible to manual prompt construction.

### Decision

Add compound directional documentation to `bar help llm` and `bar-manual` skill:

**`bar help llm` § Token Catalog § Directional (add subsection):**
> Compound directionals: primitive directional tokens can be combined into compound tokens
> (e.g., `fly rog`, `fip rog`, `dip ong`, `dip bog`). Compounds produce a merged description
> that applies both directional pressures simultaneously. Compound forms are discoverable via
> `bar shuffle` — observe the directional axis in shuffled JSON output to see which compounds
> exist. Compounds count as a single directional token and do not exceed the axis cap.

**`bar-manual` skill (add note):**
> Compound directionals exist but are not listed by `bar help tokens directional`. Run
> `bar shuffle --json` and examine the `directional` field to discover available compound forms.

---

## Decision 4: Add Composability Caveat to `taxonomy` and `visual` Forms

### Problem

ADR-0105 D1 rephrased `taxonomy` and `visual` form tokens to be composable ("where the subject
admits classification" / "where the subject lends itself to visual representation"). The intent
was to signal conditional application rather than whole-response mandate.

However, cycle 4 seed 0069 (`plan` + `verify` + `taxonomy` + `gherkin` = 2/5) shows the
rephrasing is insufficient when paired with an output-exclusive channel. Both `taxonomy` (when
applied) and `gherkin` (always) attempt to define the complete output structure. The conditional
clause in the description doesn't prevent this conflict because the channel is output-exclusive
regardless of the form's conditionality.

The same issue applies to `visual`: pairing it with any output-exclusive channel still produces
two competing output mandates.

### Decision

Add an explicit channel-compatibility caveat to both `taxonomy` and `visual` form descriptions:

**taxonomy (add to description):**
> Composable with non-exclusive channels (`jira`, `slack`, `sketch`, `plain`) or with no
> channel token. Avoid pairing with output-exclusive channels (`gherkin`, `codetour`, `code`,
> `adr`, `html`, `shellscript`, `diagram`, `presenterm`, `sync`) — both would attempt to
> define the complete output structure.

**visual (add to description):**
> Composable with non-exclusive channels (`jira`, `slack`, `sketch`, `plain`) or with no
> channel token. Avoid pairing with output-exclusive channels — both would attempt to define
> the complete output structure.

---

## Decision 5: Clarify `fix` Task Semantics

### Problem

The `fix` task description reads: "The response changes the form or presentation of given
content while keeping its intended meaning." This describes a reformat/rewrite operation, not
the conventional meaning of "fix" (correct a defect or error). Users encountering `fix` in
`bar help tokens` or `bar help llm` may expect it to be the task for debugging or error
correction, and use it for bug-fix or repair scenarios where it does not apply.

**Evidence from cycle 4 corpus:**
Seeds 0066, 0071, 0075, and 0078 all use `fix` with this reformat meaning. The task is
coherent but the name creates a discoverability mismatch — "find the task for fixing a bug"
leads a user to `fix`, which actually means "reformat while preserving intent."

The task for debugging/error-correction work is typically composed as `show` or `make` with
diagnostic method tokens (`diagnose`, `inversion`, `adversarial`). No task token currently
means "correct a defect."

### Decision

Add a disambiguation note to the `fix` task description:

**fix (add to description):**
> Note: in bar's grammar, `fix` means "transform form or presentation while preserving
> meaning" — it is a reformatting task, not a debugging task. For work that involves
> correcting defects or errors, use `make` or `show` paired with diagnostic method tokens
> (`diagnose`, `inversion`, `adversarial`).

---

## Decision 6: Disambiguate `order` Method from `sort` Task

### Problem

The `sort` task description reads: "The response arranges items into categories or an order
using a specified or inferred scheme." The `order` method description adds "ordering"
reasoning to any task. When combined, `sort` + `order` reads as tautological — both describe
arranging things in order, and the method does not visibly differentiate from the task.

**Evidence from cycle 4 corpus:**
Seed 0068 (`sort` + `order` method + `direct` form) scored 3/5. The evaluator note: "order
method doesn't add clear differentiation beyond what sort already states."

### Decision

Add a disambiguation note to the `order` method description:

**order (add to description):**
> When paired with `sort` task, `order` adds emphasis on the *criteria and scheme* driving
> the sequencing — making explicit the ranking logic rather than merely producing the sorted
> result. The distinction is subtle; consider whether it is needed before including both.

---

## Consequences

### Positive

- **Code-channel task-affinity complete:** Decision 1 extends the ADR-0105 D2 pattern to
  cover `code`/`html`/`shellscript` channels, closing the sim+code gap.

- **Prose-form conflict rule fills the biggest gap:** Decision 2 adds the broadest missing
  rule — any prose-producing form conflicts with code/markup-only channels. This single rule
  would have prevented the 3 low-scoring form+channel seeds in cycle 4.

- **Compound directionals become discoverable:** Decision 3 makes compound directionals
  visible to manual prompt builders for the first time. Currently invisible to anyone not
  running `bar shuffle`.

- **taxonomy/visual channel caveats prevent repeat failures:** Decision 4 prevents the
  taxonomy+gherkin and visual+codetour patterns that recurred across cycles 3 and 4.

- **fix disambiguation prevents task misuse:** Decision 5 prevents users from reaching
  for `fix` when they mean "correct a defect."

### Negative / Tradeoffs

- **Decision 3 (compound directionals) requires investigation:** Compound directional tokens
  need to be enumerated from the grammar before they can be documented. The set may change
  as the grammar evolves, making the documentation a maintenance surface.

- **Decision 5 (fix naming) deferred full rename:** The low-cost path (disambiguation note)
  is chosen over renaming `fix` to `reformat` or `transform`, which would be a breaking
  change for existing users. A future ADR may revisit the rename if user confusion remains
  common.

---

## Follow-up Work

### Decision 1: Code-channel task-affinity
**Files to change:**
- `lib/axisConfig.py`: add task-affinity note to `code`, `html`, `shellscript` descriptions
- `internal/barcli/embed/prompt-grammar.json`: same updates
- `internal/barcli/help_llm.go`: add sim/probe note to § Task-affinity restrictions

### Decision 2: Prose-form / code-channel conflict
**Files to change:**
- `internal/barcli/help_llm.go`: add prose-form conflict rule to `renderCompositionRules`

### Decision 3: Compound directional documentation
**Files to change:**
- `internal/barcli/help_llm.go`: add compound directionals subsection to § Token Catalog
- `internal/barcli/skills/bar-manual/skill.md`: add note about `bar shuffle` for discovery

### Decision 4: taxonomy/visual channel caveats
**Files to change:**
- `lib/axisConfig.py`: update `taxonomy` and `visual` form descriptions
- `internal/barcli/embed/prompt-grammar.json`: same updates

### Decision 5: fix task disambiguation
**Files to change:**
- `lib/axisConfig.py` (or wherever task tokens are defined): add note to `fix`
- `internal/barcli/embed/prompt-grammar.json`: same update

### Decision 6: order method disambiguation
**Files to change:**
- `lib/axisConfig.py`: add disambiguation note to `order` method
- `internal/barcli/embed/prompt-grammar.json`: same update

### Ongoing: Test coverage
- Existing `TestLLMHelpIncompatibilitiesPopulated` should be extended to check for the
  new prose-form conflict rule text once Decision 2 is implemented.
