# ADR-0112: Prose-Form Channel Conflicts, Social-Intent Token Guidance, and Tone/Channel Register Mismatch

## Status

Completed

## Context

Cycle 6 of the shuffle-driven catalog refinement process (seeds 0101–0120, ADR-0085 evidence)
produced a mean score of 3.85/5 — an improvement from cycle 5's 3.65/5 — with 15% of seeds
still scoring ≤2. Three distinct problem categories emerged.

**Evaluation evidence base:**
- Cycle 6: seeds 0101–0120 (35% excellent, 30% good, 20% acceptable, 15% problematic)
- ADR-0107 improvements visible: interactive-form conflicts and adr channel task-affinity in place
- Persistent gap: form/channel conflict class not yet extended to prose-output forms (`questions`,
  `recipe`) — though the nature of the gap differs: some combinations are genuinely incompatible,
  others need interpretation guidance to be coherent
- New pattern: social-intent tokens (`appreciate`, `entertain`, `announce`) paired with
  analytical/structural tasks produce semantic noise at ~10% corpus frequency
- New pattern: `formally` tone paired with conversational-register channels (`slack`, `remote`,
  `sync`) produces a register mismatch

---

## Decision 1: Extend Form/Channel Conflicts to Prose-Output Forms

### Problem

ADR-0107 Decision 1 extended the form/channel conflict rule to cover interactive-dialogue forms
(`cocreate`, `quiz`, `facilitate`). However, a second category of incompatible form tokens remains
undocumented: **prose-output forms** — forms that produce plain prose structures that cannot be
expressed in non-prose output formats.

Three seeds surfaced the pattern, but they split into two sub-cases:

**Genuinely incompatible (format rigidity prevents coherent output):**

- `recipe` + `codetour` (seed 0109, score 2): `recipe` form requires a custom prose mini-language
  with an explanatory key. `codetour` channel mandates a VS Code CodeTour JSON file with specific
  semantic fields (`title`, `file`, `line`, `description`). The JSON schema has no natural slot for
  a custom mini-language; the output cannot be simultaneously a prose recipe and a valid CodeTour.
- `questions` + `gherkin` (seed 0115, score 2): `questions` form produces probing prose questions.
  `gherkin` channel mandates Given/When/Then scenario syntax. Gherkin's rigid structure cannot
  accommodate open questions without producing non-parseable output that serves neither purpose.

**Requires combination guidance (coherent with explicit interpretation):**

- `questions` + `diagram` (seed 0120, score 2): the low score was caused by the LLM lacking a
  default interpretation, not by fundamental incompatibility. A question-tree or decision-map
  Mermaid diagram — where nodes are probing questions and edges are branching paths — is a real,
  useful artifact. The existing REFERENCE KEY rule ("channel defines output format when both
  present") gives a coherent reading: `diagram` wins and the output is Mermaid code, while
  `questions` form shapes the *content* of that diagram toward a question structure. An LLM can
  produce this reliably with an explicit hint. This is the same pattern as `sim + facilitate`
  (ADR-0107 D3): not incompatible, just ambiguous without guidance.

The distinction matters for what to prescribe. Genuinely incompatible combinations need a
constraint note ("avoid"). Ambiguous-but-coherent combinations need an interpretation note
("when combined with X, this means Y").

**Summary:**

| Combination | Class | Treatment |
|---|---|---|
| `recipe` + `codetour` | Incompatible — schema rigidity | Conflict note |
| `questions` + `gherkin` | Incompatible — syntax rigidity | Conflict note |
| `questions` + `diagram` | Coherent with guidance | Combination guidance |

### Decision

**1a. Add prose-output form conflict note to `bar help llm` § Incompatibilities:**

Extend the "Form/channel conflicts" entry with a subcategory for incompatible prose-output forms,
covering only the genuinely incompatible combinations:

> **Prose-output-form conflicts:** `recipe` form (custom prose mini-language + key) conflicts with
> channels whose schema leaves no slot for a prose document (`codetour`, `code`, `html`,
> `shellscript`, `svg`, `presenterm`). `questions` form (probing prose questions) conflicts with
> channels whose syntax cannot accommodate open questions (`gherkin`). Use both tokens with
> prose-compatible channels (`plain`, `slack`, `jira`, `remote`, `sync`) or no channel.
> Note: `questions` + `diagram` is not in this list — see combination guidance below.

**1b. Add combination guidance for `questions` + `diagram` in `bar help llm`:**

Add a note in the combination guidance section (alongside `sim + facilitate`):

> **`questions` + `diagram`:** Channel wins — output is Mermaid code. `questions` form shapes the
> content: the diagram should represent a question structure (decision tree, question map, inquiry
> flow) rather than a structural diagram of the subject. Useful for Socratic maps, branching
> decision guides, and exploratory question hierarchies.

**1c. Add conflict notes to `questions` and `recipe` form descriptions in `lib/axisConfig.py`:**

> `questions` (add): "Conflicts with channels whose syntax cannot accommodate open questions
> (`gherkin`). When combined with `diagram`, channel wins — the output is Mermaid code structured
> as a question tree or decision map (see combination guidance). Use with prose-compatible channels
> (`plain`, `slack`, `jira`, `remote`, `sync`), `diagram`, or no channel."

> `recipe` (add): "Prose-output form — produces a prose mini-language document and conflicts with
> channels whose schema has no slot for a prose document (`codetour`, `code`, `html`, `shellscript`,
> `svg`, `presenterm`). Use with prose channels or no channel."

**1d. Add AXIS_KEY_TO_GUIDANCE entries for `questions` and `recipe`:**

Add guidance entries in `lib/axisConfig.py` so the TUI surfaces the right signal at token-selection
time:

> `questions` guidance: "Conflicts with gherkin (syntax rigidity). With diagram: produces a
> question-tree Mermaid diagram. Use with plain, slack, diagram, or no channel."

> `recipe` guidance: "Conflicts with codetour, code, shellscript, svg (schema has no prose slot).
> Use with plain, slack, or no channel."

---

## Decision 2: Add Guidance for Social-Intent Tokens to Prevent Task Mismatch

### Problem

Two seeds in cycle 6 (0111 and 0113, both scoring 3/5) paired the `appreciate` intent with
analytical planning tasks. In both cases, "appreciate" (express thanks or recognition) introduced
semantic noise — the LLM receives an intent to express gratitude while simultaneously being asked
to produce a structural plan or architectural analysis. The intent either gets ignored or awkwardly
injects thanks into an otherwise analytical response.

This is not a defect in the `appreciate` token's definition — it is correctly defined as "express
thanks, recognition, or positive regard." The problem is that the token lacks any signal about
*when not to use it*: it can be randomly selected alongside any task, and its description gives
no indication that it requires the *entire response's purpose* to be gratitude.

The same structural issue applies to two related intents:

- **`entertain`** ("engage or amuse the audience"): meaningful only when amusement is the
  response's primary function; creates confusion when the task is analytical
- **`announce`** ("deliver news or a formal announcement"): meaningful only when delivering
  a specific announcement; creates friction when the task is analysis or planning

These three tokens form a class of **social-purpose intents** — communicative acts whose meaning
depends on the response *being that act*. They differ from *modulating intents* like `teach`,
`persuade`, or `coach`, which can naturally shape how an analytical task is communicated. A plan
can be delivered in a teaching register; a plan cannot be simultaneously a gratitude expression.

At the observed corpus frequency (~10%), users who include intent tokens in their prompts will
hit this mismatch regularly when selecting intents without careful consideration.

### Decision

**2a. Add usage-context guidance to `appreciate`, `entertain`, and `announce` intent descriptions
in `lib/personaConfig.py`:**

> `appreciate` (add): "Use only when the response's primary purpose is to thank or recognize the
> audience — not as a modifier for analytical or task-driven prompts. Pairing `appreciate` with
> planning, analysis, or evaluation tasks (`plan`, `probe`, `check`, `diff`) creates semantic
> noise: the LLM will either ignore it or awkwardly inject gratitude into an otherwise analytical
> response. For an appreciative register in informational responses, prefer `tone: kindly` instead."

> `entertain` (add): "Use only when engagement or amusement is the response's primary purpose.
> Not a substitute for casual tone — use `tone: casually` for an informal register. Pairing with
> analytical tasks (`plan`, `probe`, `check`) produces a tonally confused response that is neither
> fully analytical nor genuinely entertaining."

> `announce` (add): "Use only when delivering a specific piece of news or a formal announcement
> is the response's purpose. Pairing with analytical or planning tasks creates friction — the
> response will attempt to analyze and announce simultaneously, weakening both."

**2b. Add PERSONA_KEY_TO_GUIDANCE entries for `appreciate`, `entertain`, and `announce`:**

If `personaConfig.py` supports a guidance map (parallel to `AXIS_KEY_TO_GUIDANCE` from ADR-0110),
add TUI guidance for these tokens so users see the warning at selection time. If the guidance map
does not yet exist for persona tokens, create it following the same pattern as ADR-0110.

> `appreciate` guidance: "Social-purpose intent: use only when the whole response is an expression
> of thanks. Does not modify analytical tasks."

> `entertain` guidance: "Social-purpose intent: use only when amusement is the primary goal.
> Use `tone: casually` for informal register instead."

> `announce` guidance: "Social-purpose intent: use only when delivering a specific announcement.
> Not a task modifier."

---

## Decision 3: Add Register Guidance to `formally` Tone for Conversational Channels

### Problem

Seed 0118 (fix + slack + formally, score 3) exposed a register mismatch: `formally` tone (elevated
language, professional structure) paired with `slack` channel (Slack markdown, mentions,
conversational fragments). Slack is an informal-register platform by design — the formatting
conventions (short messages, reactions, mentions) assume conversational language. A formal tone
instruction produces Slack messages that read as bureaucratic memos, defeating the purpose of
Slack formatting.

The same mismatch applies to other real-time or conversational channels:

- `sync` — live session plans and agendas; formal tone produces stilted facilitation scripts
- `remote` — video call scripts and talking points; formal tone contradicts the spoken register

The `formally` token has no guidance about channel register compatibility. A user who wants a
professional-but-accessible Slack message will not know to avoid `formally` without this guidance.

### Decision

**3a. Add register note to `formally` tone description or PERSONA_KEY_TO_GUIDANCE in
`lib/personaConfig.py`:**

> `formally` (add to description or guidance): "May conflict with conversational-register channels.
> `slack`, `sync`, and `remote` have informal or spoken registers — formal elevated language will
> feel mismatched and bureaucratic in these contexts. For professional-but-accessible output in
> conversational channels, use no tone token or `directly` instead."

**3b. Add to `bar help llm` § Incompatibilities as a tone/channel register note:**

> **Tone/channel register conflicts:** `formally` tone conflicts with conversational-register
> channels that assume informal or spoken language (`slack`, `sync`, `remote`). Use `directly`
> or no tone token when a professional register is needed in these channels.

---

## Consequences

### Positive

- **Decision 1 closes the remaining prose-output-form gap in the form/channel conflict rule:**
  ADR-0105, ADR-0106, and ADR-0107 progressively extended the conflict rule from prose-structure
  forms to code channels, to all output-exclusive channels, to interactive forms. Decision 1 adds
  genuinely incompatible prose-output combinations (`recipe + codetour`, `questions + gherkin`)
  while rescuing `questions + diagram` as a coherent combination via interpretation guidance.

- **`questions + diagram` combination guidance adds a new useful pattern:** A question-tree or
  decision-map Mermaid diagram is a recognisable and useful artifact. Documenting the combination
  interpretation rather than prohibiting the pairing increases catalog expressiveness rather than
  reducing it.

- **Decision 2 prevents social-intent/task mismatches without removing useful tokens:** The
  `appreciate`, `entertain`, and `announce` tokens are genuinely useful in their correct context.
  Adding usage-context guidance preserves them while reducing the noise they introduce when
  randomly combined with analytical tasks.

- **Decision 3 adds the first tone/channel interaction guidance:** Previous incompatibility
  documentation focused on form/channel and task/channel conflicts. Decision 3 introduces a
  tone/channel dimension, capturing the register-mismatch class.

### Negative / Tradeoffs

- **Decision 1 (AXIS_KEY_TO_GUIDANCE for form tokens):** Adding guidance entries for `questions`
  and `recipe` increases the number of tokens with guidance, which is the desired direction
  (ADR-0110). The `questions + diagram` combination guidance adds a second entry to the combination
  guidance section (alongside `sim + facilitate`) — this section may need a canonical home in
  `bar help llm` if it grows further.

- **Decision 2 (PERSONA_KEY_TO_GUIDANCE) may require creating the map:** If
  `PERSONA_KEY_TO_GUIDANCE` does not yet exist in `personaConfig.py`, it needs to be created
  following ADR-0110's pattern, adding moderate implementation scope. The description-only path
  is available as a fallback without the TUI guidance.

- **Decision 3 is guidance, not prohibition:** `formally` + `slack` is not blocked, only
  documented as problematic. The combination will continue to appear in shuffle evaluations.
  If it recurs at high frequency, a stronger note should be considered.

---

## Follow-up Work

### Decision 1: Prose-output form conflicts + questions/diagram combination guidance

**Files to change:**
- `lib/axisConfig.py`: add conflict notes to `questions` and `recipe` form descriptions; add
  `AXIS_KEY_TO_GUIDANCE` entries for both tokens
- `internal/barcli/help_llm.go`: extend `renderCompositionRules` — add prose-output-form
  conflict subcategory; add `questions + diagram` combination guidance entry alongside
  `sim + facilitate`
- `internal/barcli/embed/prompt-grammar.json`: regenerate after `axisConfig.py` changes

### Decision 2: Social-intent token guidance

**Files to change:**
- `lib/personaConfig.py`: add usage-context notes to `appreciate`, `entertain`, `announce`
  intent descriptions; add `PERSONA_KEY_TO_GUIDANCE` entries (creating the map if not present)
- `internal/barcli/embed/prompt-grammar.json`: regenerate after `personaConfig.py` changes

### Decision 3: Tone/channel register guidance

**Files to change:**
- `lib/personaConfig.py`: add register note to `formally` tone description or
  `PERSONA_KEY_TO_GUIDANCE`
- `internal/barcli/help_llm.go`: add tone/channel register entry to `renderCompositionRules`
  § Incompatibilities
- `internal/barcli/embed/prompt-grammar.json`: regenerate after `personaConfig.py` changes

### Test coverage

- Extend `TestLLMHelpIncompatibilitiesPopulated` (or equivalent) to verify:
  - The prose-output-form conflict rule text is present
  - The tone/channel register conflict note is present
