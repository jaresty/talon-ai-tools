# 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes

- Status: Accepted  
- Date: 2025-12-XX  
- Context: `talon-ai-tools` GPT `model` commands (axes: completeness, scope, method, style; static prompts; directional lenses)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 007 – Static Prompt Consolidation  
  - 008 – Pattern Picker and Recap  
  - 009 – Rerun Last Recipe Shorthand

## Context

ADR 005 introduced explicit modifier axes for:

- **Completeness** – how thoroughly to cover the territory.  
- **Scope** – what conceptual territory is in-bounds.  
- **Method** – how to approach reasoning or transformation.  
- **Style** – how to present the output (plain, bullets, code, etc.).

ADR 007 then cleaned up the static prompt surface, moving many “how”/“shape” behaviours into axes and pattern recipes, and explicitly preserving some **format/transform heavy prompts** as static prompts:

- `diagram`, `gherkin`, `shell`, `code`, `format`, `presenterm`, `recipe`, `group`, `split`, `shuffled`, `match`, `blend`, `join`, `sort`, `context`, `commit`, `ADR`, `HTML`.

Those were kept because they encoded strong output formats and safety constraints that, at the time, were seen as “beyond what a simple axis can do”.

However, as we have actually used the axes, a sub‑set of these prompts looks more and more like:

> “Take whatever this task is, but render it in this very specific shape (with guardrails).”

In other words, they are **output styles** or **methods** masquerading as static prompts:

- You could imagine rendering “any result” as:
  - a `presenterm` slide deck,  
  - a `diagram` (Mermaid graph),  
  - a semantic `HTML` fragment,  
  - an abstract `lens`‑style SVG metaphor, and so on.

Separately, some “lens” prompts like `system`, `experiment`, or `science` are really **approach/method** choices (“think in systems”, “use scientific/experimental reasoning”), not separate tasks.

The current state has drawbacks:

- **Static prompt bloat**: the surface mixes “what” (semantic tasks) with “how” (shape/method) in an ad-hoc way.
- **Axis under-use**: users cannot easily say “render this other task as a Presenterm deck” or “analyse this different problem as a system” without memorising special static prompts.
- **Redundancy and confusion**: we have both:
  - static prompts like `code`, `diagram`, `presenterm`, `HTML`, and  
  - a `style` axis that already includes `code` and can reasonably host “diagram” / “slides” / “abstract-visual” styles.

## Decision

We will:

1. **Treat several special‑purpose static prompts as primarily style or method choices** and move their semantics into the `style` and `method` axes.

2. **Remove those prompts from the static prompt surface** rather than preserving them as legacy shorthands. Users will access the behaviour via style/method axes and recipes instead of special-purpose prompt names.

3. **Extend the style axis to allow “heavier” styles** that encode strong formatting contracts and safety rules (not just “bullets vs table vs plain”).

4. **Extend the method axis to include thinking frames** (for example, systems thinking), not just local process tweaks like `steps` or `plan`.

5. **Keep truly semantic prompts as the backbone** of the static prompt surface; retire static prompts whose behaviour is better framed as a style or method.

### Static prompts to retire into style/method

The following prompts are currently implemented as static prompts but will be retired and expressed purely via axes:

- Style‑heavy / shape‑heavy:
  - `diagram` – Mermaid diagrams with safety rules.
  - `presenterm` – Presenterm slide deck Markdown with front-matter, directives, and fence/HTML safety.
  - `HTML` – semantic HTML only.
  - `gherkin` – Gherkin with Jira markup, output-only.
  - `shell` – shell scripts.
  - `code` – “code only” outputs.
  - `emoji` – emoji-only outputs.
  - `format` – context-aware formatting for Slack/Markdown/etc.
  - `recipe` – recipe-style representation with a custom language and key.
  - `lens` – abstract visual metaphor with legend and optional SVG/code.
  - `commit` – conventional commit messages.
  - `ADR` – Architecture Decision Records.

- Method‑heavy / approach‑heavy:
  - `system` – systems-thinking analysis.
  - `experiment` – experimental reasoning about possibilities and tests.
  - `science` – scientific-style reasoning about hypotheses, evidence, and models.
  - `debug` – debugging-style reasoning about failures and likely causes.

These behaviours will remain available but only through the axes:

- Style for “shape and output contract”.  
- Method for “how to think/approach”.

### Concrete style re‑mappings

Add new `styleModifier` values (single, pronounceable tokens):

- `diagram` – “Output an appropriate Mermaid diagram for the task; code only; apply existing Mermaid safety rules (no parentheses, label encoding, etc.).”
- `presenterm` – “Render the answer as a Presenterm slide deck (front-matter, Setext slide headers, directives, fence-safety, HTML/Markdown safety) using the existing contract.”
- `html` – “Output semantic HTML only for the answer content.”
- `gherkin` – “Output proper Gherkin using Jira markup; no surrounding explanation.”
- `shellscript` – “Express the solution as a shell script.”
- `emoji` – “Express the answer as emoji only.”
- `slack` – “Format the answer for Slack, using appropriate Markdown, mentions, and code blocks.”
- `jira` – “Format the answer using Jira markup where relevant.”
- `recipe` – “Express as a recipe with a custom language and include a key.”
- `abstractvisual` (or `lens`) – “Express the big picture as an abstract visual metaphor with a legend and optional SVG/code.”
- `commit` – “Express as a conventional commit message.”
- `adr` – “Express as an Architecture Decision Record.”

The long instruction strings and safety constraints currently attached to the static prompts (especially `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `commit`, `ADR`) will be moved to the descriptions for these style values. Using a style alone (for example, `style presenterm`) must be as powerful and safe as the old static prompt.

Concretely, instead of:

- `model diagram fog`  
- `model presenterm rog`  
- `model HTML`  
- `model gherkin`  
- `model shell`  
- `model code`  
- `model emoji`  
- `model format`  
- `model recipe`  
- `model lens`  
- `model commit`  
- `model ADR`

users will say things like:

- `model describe diagram fog`  
- `model describe presenterm rog`  
- `model describe html`  
- `model describe gherkin`  
- `model describe shellscript`  
- `model describe code`  
- `model describe emoji`  
- `model describe slack`  
- `model describe jira`  
- `model describe recipe`  
- `model describe abstractvisual`  
- `model describe commit`  
- `model describe adr`

or use pattern recipes and GUIs that bake these style values into named recipes.

### Concrete method re‑mappings

Add new `methodModifier` values that capture thinking frames, not just local process:

- `systems` – “Analyse using systems thinking: boundaries, components, flows, feedback loops, emergence, and leverage points.”
- `experimental` – “Use an experimental/scientific reasoning pattern: hypotheses, tests, observations, revisions.”
- `debugging` – “Approach as debugging: narrow hypotheses, inspect evidence, identify likely root causes.”

Wire semantic prompts to these methods via `STATIC_PROMPT_CONFIG`:

- For `system` (before it is retired as a static prompt), ensure its behaviour is expressed as:
  - `method: "systems"`  
  - `scope: "focus"`  
  - `style: "plain"` (or left to defaults).
- For `experiment` and `science`, ensure their behaviour is expressed as:
  - `method: "experimental"`  
  - with scope/style left to defaults or tuned as needed.
- For `debug`, ensure its behaviour is expressed as:
  - `method: "debugging"`  
  - with scope/style left to defaults or tuned as needed.

Once the axis behaviour is correct and documented, remove `system`, `experiment`, `science`, and `debug` as static prompts and access these approaches via the method axis:

- `model describe systems fog` – “Describe this, using a systems-thinking method, with lens `fog`.”
- `model describe experimental` – “Describe this, using an experimental/scientific method.”
- `model describe debugging` – “Describe this, using a debugging-style method.”

## Consequences

**Pros**

- **Cleaner mental model**: static prompts describe **what** we are doing (problem domain / semantic frame). Axes (style, method, completeness, scope) describe **how** and **in what shape**.
- **More composable power**:
  - Any task can be rendered as a Presenterm deck, diagram, HTML, Gherkin, shell script, commit, ADR, abstract visual, etc., without bespoke static prompts for each combination.
  - Any task can be approached with systems thinking or other methods, again without bespoke prompts.
- **Reduced redundancy**: static prompts like `code`, `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `system` no longer compete with axis semantics.
- **Better alignment with ADR 005/007**: this is the logical next step in “axes for how, prompts for what”.

**Cons / Risks**

- **Breaking change**: existing voice habits that rely on the retired static prompt names will stop working once those entries are removed from `staticPrompt.talon-list`. Users must adopt axis-style phrasing or recipes.
- **Heavier styles**: the style axis now carries non-trivial contracts (Mermaid/Presenterm/HTML/Gherkin safety, shell/commit/ADR schemas). This blurs the original “style is just presentation” intuition and needs clear documentation.
- **Migration complexity**:
  - We must carefully extract existing instructions from static prompts and Talon lists into style/method descriptions without behavioural regressions.
  - Help text and pattern pickers need to surface the new style/method values clearly.

## Implementation Sketch

1. **Extend axis vocabularies**
   - Add new entries to:
     - `GPT/lists/styleModifier.talon-list` for the style values listed above.
     - `GPT/lists/methodModifier.talon-list` for `systems`, `experimental`, and `debugging`.
   - Move the long instruction strings and safety contracts from:
     - `GPT/lists/staticPrompt.talon-list` and any `modelPurpose` entries into the corresponding style/method descriptions.

2. **Update static prompt configuration**
   - In `lib/staticPromptConfig.py`, ensure any residual profiles for the retired prompts are either:
     - Removed entirely, or
     - Simplified to transitional descriptions while code is migrated, then removed in the final clean-up.
   - For method-heavy prompts like `system`, confirm their intended axes (for example, `method: "systems"`) before removing them from the static prompt surface.

3. **Remove retired static prompts**
   - Delete the retired keys from:
     - `GPT/lists/staticPrompt.talon-list` (so they are no longer valid `staticPrompt` tokens).
     - Any help or GUI surfaces that list static prompts by name.
   - Adjust `tests/test_static_prompt_docs.py` and related tests to align with the new static prompt set.

4. **Adjust documentation and help surfaces**
   - Update `GPT/readme.md`, `_build_axis_docs`, and `_build_static_prompt_docs` to:
     - Show the new style/method values and their semantics.
     - Explain that diagram/presenterm/HTML/gherkin/shell/emoji/format/recipe/lens/commit/ADR/system behaviours are now accessed via axes, not static prompts.
   - Add examples to ADR 005/007 and pattern GUIs:
     - “Render as diagram” (`style=diagram`).
     - “Teach via slides” (`style=presenterm`).
  - “Systems sketch” (`method=systems` + `style=diagram` or `style=abstractvisual`).

5. **Guardrails and tests**
   - Extend `tests/test_axis_mapping.py` to ensure new style/method tokens round-trip.
   - Extend `tests/test_talon_settings_model_prompt.py` (and others where appropriate) to assert that:
     - Style and method axes correctly influence `GPTState.system_prompt` and the recorded recipe.
     - Using a style alone reproduces the old static prompt behaviour (for Mermaid/Presenterm/HTML/Gherkin/shell/commit/ADR).

## Status

- This ADR records the decision to migrate specific static prompts into the style and method axes with no backwards compatibility layer.
- Concrete implementation (axis list updates, static prompt removal, docs, tests) will be done in follow-up slices and recorded in a dedicated work-log (for example, `docs/adr/012-style-and-method-prompt-refactor.work-log.md`).

### Current Status (this repo)

As of 2025‑12‑04, this repository has applied the ADR 012 migration as follows:

- Fully retired into styles/methods (no `staticPrompt` token, no profile):
  - Style-heavy prompts: `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`.
  - Method-heavy prompts: `debug` (now represented by `method debugging`).
- Partially migrated / method-based but still present as static prompts:
  - `system`, `experiment`, `science` now share their thinking stance via `method systems` / `method experimental`, but still exist as static prompts with descriptions.
- Axis vocabulary:
  - `styleModifier.talon-list` includes: `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, plus generic styles (`plain`, `tight`, `bullets`, `table`, `code`, `cards`, `checklist`).
  - `methodModifier.talon-list` includes: `systems`, `experimental`, `debugging` alongside existing methods (`steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`).

In this repo, behaviours for the fully retired prompts must now be requested via the axes, for example:

- `model describe diagram fog` (instead of `model diagram fog`)
- `model describe presenterm rog` (instead of `model presenterm rog`)
- `model describe html` (instead of `model HTML`)
- `model describe gherkin` (instead of `model gherkin`)
- `model describe shellscript` (instead of `model shell`)
- `model describe emoji` (instead of `model emoji`)
- `model describe recipe` (instead of `model recipe`)
- `model describe abstractvisual` (instead of `model lens`)
- `model describe commit` (instead of `model commit`)
- `model describe adr` (instead of `model ADR`)
- `model describe code` (instead of `model code`)
- `model describe systems fog` / `model describe experimental` / `model describe debugging` (instead of relying on `system` / `experiment` / `science` / `debug` as static prompts).
