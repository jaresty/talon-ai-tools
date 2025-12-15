# 012 – Retire Special‑Intent Static Prompts into Style/Method (Form/Channel) Axes

- Status: Accepted  
- Date: 2025-12-04  
- Context: `talon-ai-tools` GPT `model` commands (axes: completeness, scope, method, form, channel; static prompts; directional lenses)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 006 – Pattern Picker and Recap  
  - 007 – Static Prompt Consolidation  
  - 008 – Prompt Recipe Suggestion Assistant  
  - 009 – Rerun Last Recipe Shorthand  
  - 013 – Static Prompt Axis Refinement and Streamlining
  - Work-log: `docs/adr/012-style-and-method-prompt-refactor.work-log.md`

## Summary (for users)

This ADR retires many format- and method-shaped static prompts (for example, `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, and `debug`) and re-expresses them as **form/channel** (formerly style) and **method** axis values. In practice, that means:

- You keep using short, semantic prompts for “what” (for example, `describe`, `todo`, `product`, `wardley`).
- You use **axes** to say “how” and “in what shape”:
- Form/Channel values like `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, `code`, `taxonomy` (form = container/shape, channel = medium bias).
  - Methods like `systems`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `wasinawa` (replacing older static prompts such as `system`, `experiment`, `science`, `debug`).
- Common behaviours that used to be static prompts now look like:
  - `model describe diagram fog` (instead of `model diagram fog`),
  - `model describe presenterm rog` (instead of `model presenterm rog`),
  - `model describe adr rog` (instead of `model ADR`),
  - `model describe shellscript rog` (instead of `model shell`),
  - `model describe debugging rog` (instead of `model debug`).
  - Structural/relational prompts like `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, and `motifs` are now expressed via method/scope/style axes (see the migration guide below for representative recipes).

Static prompts are now reserved for semantic/domain lenses and structured tasks that cannot be cleanly expressed as axis combinations; everything else should use form/channel, methods, scopes, and patterns.

This is a deliberate, breaking change: commands like `model diagram` / `model presenterm` / `model ADR` / `model shell` no longer exist in this repo; use the axis-based forms (for example, `model describe diagram …`, `model describe presenterm …`, `model describe adr …`, `model describe shellscript …`) instead.

For contributors: when adding or changing prompts/axes, also see the “GPT prompts, axes, and ADRs” section in `CONTRIBUTING.md` for concrete design rules and required guardrail tests.

For day-to-day use, many of these axis combinations are also available as named patterns in the model pattern GUI (for example, “Sketch diagram”, “Architecture decision”, “Present slides”, “Slack summary”, “Jira ticket”, “Motif scan”).

## Context

ADR 005 introduced explicit modifier axes for:

- **Completeness** – how thoroughly to cover the territory.  
- **Scope** – what conceptual territory is in-bounds.  
- **Method** – how to approach reasoning or transformation.  
- **Form** – how to present the output (plain, bullets, code, etc.).  
- **Channel** – medium bias (slack, jira, presenterm, etc.).

In this repo, the concrete axis vocabularies live in:

- `GPT/lists/completenessModifier.talon-list`
- `GPT/lists/scopeModifier.talon-list`
- `GPT/lists/methodModifier.talon-list`
- `GPT/lists/formModifier.talon-list`
- `GPT/lists/channelModifier.talon-list`
- `GPT/lists/directionalModifier.talon-list`

ADR 007 then cleaned up the static prompt surface, moving many “how”/“shape” behaviours into axes and pattern recipes, and explicitly preserving some **format/transform heavy prompts** as static prompts:

- `diagram`, `gherkin`, `shell`, `code`, `format`, `presenterm`, `recipe`, `group`, `split`, `shuffled`, `match`, `blend`, `join`, `sort`, `context`, `commit`, `ADR`, `HTML`.

In this repo, the current static prompt tokens live in:

- `GPT/lists/staticPrompt.talon-list`

ADR 006 and ADR 008 build on this grammar by:

- ADR 006 – introducing the pattern picker and quick-help UIs for axis-based recipes.
- ADR 008 – adding a prompt recipe suggestion assistant that proposes concrete `staticPrompt · completeness · scope · method · style · directional` combinations.

Some of ADR 005’s original “Still TODO” ideas around per-prompt completeness/scope/method/style profiles for format-heavy prompts are now effectively addressed by ADR 012/013’s richer style/method axes plus `lib/staticPromptConfig.py` profiles for the remaining semantic prompts.

Implementation touchpoints (this repo) include:

- `lib/talonSettings.py` – composes `modelPrompt` from static prompts and axes.
- `lib/staticPromptConfig.py` – defines semantic static prompt profiles and default axes.
- `GPT/lists/*.talon-list` – Talon lists for static prompts and axis vocabularies.
- `lib/modelPatternGUI.py` – pattern picker and axis-based recipes.
- `lib/modelHelpGUI.py` – quick-help axis summaries and example recipes.
- `GPT/gpt.py` – builds axis/static-prompt docs and wires prompts into the GPT pipeline.

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

1. **Treat several special‑intent static prompts as primarily style or method choices** and move their semantics into the `style` and `method` axes.

2. **Remove those prompts from the static prompt surface** rather than preserving them as legacy shorthands. Users will access the behaviour via style/method axes and recipes instead of special-intent prompt names.

3. **Extend the form/channel axes to allow “heavier” styles** that encode strong formatting contracts and safety rules (not just “bullets vs table vs plain”).

4. **Extend the method axis to include thinking frames** (for example, systems thinking), not just local process tweaks like `steps` or `plan`.

5. **Keep truly semantic prompts as the backbone** of the static prompt surface; retire static prompts whose behaviour is better framed as a style or method.

### Relation to ADR 007

ADR 007 explicitly chose *not* to consolidate several format/transform-heavy prompts (`diagram`, `gherkin`, `shell`, `code`, `format`, `presenterm`, `recipe`, `commit`, `ADR`, `HTML`, etc.) and a broad set of domain/lens prompts, treating them as part of the “semantic backbone”.

ADR 012 refines that stance for this repo:

- It reinterprets many of the format/transform prompts as **styles** and migrates them into the `styleModifier` axis (for example, `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `recipe`, `abstractvisual`, `commit`, `adr`, `code`).
- It treats some prompts that are largely about **method** or **scope** as better expressed via axes and, together with ADR 013, moves them into `methodModifier`/`scopeModifier` (for example, `debug` via `debugging`, `relation` via `scope relations`).

The underlying intent of ADR 007 still holds—semantic/domain prompts remain the backbone—but the concrete list of “kept” static prompts in this repository is now smaller and more axis-centric as a result of ADR 012 (and ADR 013).

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

Concretely, where users previously said:

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

they should now use axis-based forms such as:

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

- `systemic` – “Analyse using systems thinking: boundaries, components, flows, feedback loops, emergence, and leverage points.”
- `experimental` – “Use an experimental/scientific reasoning pattern: hypotheses, tests, observations, revisions.”
- `debugging` – “Approach as debugging: narrow hypotheses, inspect evidence, identify likely root causes.”

Wire semantic prompts to these methods via `STATIC_PROMPT_CONFIG`:

- For `system` (before it is retired as a static prompt), ensure its behaviour is expressed as:
  - `method: "systemic"`  
  - `scope: "focus"`  
  - `style: "plain"` (or left to defaults).
- For `experiment` and `science`, ensure their behaviour is expressed as:
  - `method: "experimental"`  
  - with scope/style left to defaults or tuned as needed.
- For `debug`, ensure its behaviour is expressed as:
  - `method: "debugging"`  
  - with scope/style left to defaults or tuned as needed.

Once the axis behaviour is correct and documented, remove `system`, `experiment`, `science`, and `debug` as static prompts and access these approaches via the method axis:

- `model describe systemic fog` – “Describe this, using a systems-thinking method, with lens `fog`.”
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
- **Heavier styles**: the form/channel split now carries non-trivial contracts (Mermaid/Presenterm/HTML/Gherkin safety, shell/commit/ADR schemas). This blurs the original “style is just presentation” intuition and needs clear documentation.
- **Migration complexity**:
  - We must carefully extract existing instructions from static prompts and Talon lists into style/method descriptions without behavioural regressions.
  - Help text and pattern pickers need to surface the new style/method values clearly.

## Implementation Sketch

1. **Extend axis vocabularies**
   - Add new entries to:
     - `GPT/lists/styleModifier.talon-list` for the style values listed above.
     - `GPT/lists/methodModifier.talon-list` for `systems`, `experimental`, and `debugging`.
   - Move the long instruction strings and safety contracts from:
     - `GPT/lists/staticPrompt.talon-list` and any `modelIntent` entries into the corresponding style/method descriptions.

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
    - In this repo, axis-based patterns have already been added in `lib/modelPatternGUI.py`, for example:
      - `Sketch diagram` – `describe · gist · focus · diagram · fog`.
      - `Architecture decision` – `describe · full · focus · adr · rog`.
      - `Present slides` – `describe · full · focus · presenterm · rog`.
      - `Slack summary` – `describe · gist · focus · slack · fog`.
      - `Jira ticket` – `describe · full · focus · steps · jira · fog`.
      - `Motif scan` – `describe · gist · relations · motifs · bullets · fog`.

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
- `model describe systemic fog` / `model describe experimental` / `model describe debugging` (instead of relying on `system` / `experiment` / `science` / `debug` as static prompts).

#### Axis-only prompt summary

For quick reference, the following behaviours are **axis-only** in this repo (no static prompt token or profile):

- **Style-only behaviours** (via `styleModifier`):
  - `diagram` – Mermaid diagrams (code-only, with safety rules).
  - `presenterm` – Presenterm slide decks.
  - `html` – semantic HTML only.
  - `gherkin` – Jira-flavoured Gherkin, no surrounding prose.
  - `shellscript` – shell scripts.
  - `emoji` – emoji-only.
  - `slack` / `jira` – channel-specific formatting.
  - `recipe` – mini-language recipes with a key.
  - `abstractvisual` – abstract SVG/visual metaphors.
  - `commit` – conventional commits.
  - `adr` – Architecture Decision Records.
  - `taxonomy` – type/taxonomy-style outputs (categories, subtypes, relationships).
  - `code` – code/markup-only output.

- **Method-only behaviours** (via `methodModifier`):
  - `debugging` – debugging-style scientific method.
  - `systemic` – systems-thinking stance.
  - `experimental` – experimental/scientific stance.
  - `structure` – structural focus method.
  - `flow` – flow/sequence focus method.
  - `compare` – comparison/contrast method.
  - `motifs` – motif/pattern scan method.
  - `wasinawa` – What–So What–Now What reflection.

These behaviours should be combined with semantic static prompts (for example, `describe`, `product`) and directional lenses rather than invoked as standalone static prompts.

If this axis-only list changes, update the corresponding guardrails and contributor docs:
- `tests/test_static_prompt_docs.py:test_axis_only_tokens_do_not_appear_as_static_prompts`
- The “GPT prompts, axes, and ADRs” section in `CONTRIBUTING.md`.

In this ADR and its work-log, “axis-only behaviours” refers to these style/method values that **only** exist on the axes, whereas “semantic-backbone static prompts” refers to the remaining static prompts that still act as primary “what” lenses.

#### Semantic-backbone static prompts

Complementing the axis-only behaviours, this repo intentionally keeps a smaller set of **semantic backbone** static prompts. These encode domains, lenses, or task shapes that are not naturally recoverable from axes alone. Examples include:

- Analysis and perspective:
  - `describe`, `who`, `what`, `when`, `where`, `why`, `how`, `undefined`, `assumption`, `objectivity`, `true`.
- Domain / lens heavy:
  - `knowledge`, `taste`, `tao`, `com b`, `math`, `orthogonal`, `map`, `graph`, `document`, `wardley`, `domain`, `tune`, `melody`, `constraints`, `effects`, `operations`, `facilitate`, `challenge`, `critique`, `retro`, `easier`, `unknown`, `team`, `jim`.
- Planning and product:
  - `todo`, `product`, `metrics`, `value`, `jobs`, `done`, `bridge`.
- Transformations / reformatting:
  - `group`, `split`, `shuffled`, `match`, `blend`, `join`, `sort`, `context`.
- Variation and exercises:
  - `problem` and similar prompts that encode specific structured workflows.

Future ADRs may refine this backbone further, but the intent is that new behaviours should prefer axes and pattern recipes over adding more static prompts.

### Migration guide for retired prompts

For users accustomed to the earlier static prompt set, the table below summarizes how to express retired prompts using the new axis-first grammar:

| Retired static prompt | Axis-based equivalent (representative)                                   |
| --------------------- | ------------------------------------------------------------------------- |
| `diagram`             | `model describe diagram fog`                                              |
| `presenterm`          | `model describe presenterm rog`                                           |
| `HTML`                | `model describe html`                                                     |
| `gherkin`             | `model describe gherkin`                                                  |
| `shell`               | `model describe shellscript`                                              |
| `emoji`               | `model describe emoji`                                                    |
| `format`              | `model describe slack` / `model describe jira` / `model describe html`   |
| `recipe`              | `model describe recipe`                                                   |
| `lens`                | `model describe abstractvisual`                                           |
| `commit`              | `model describe commit`                                                   |
| `ADR`                 | `model describe adr`                                                      |
| `code`                | `model describe code`                                                     |
| `debug`               | `model describe debugging rog`                                            |
| `structure`           | `model describe structure rog`                                            |
| `flow`                | `model describe flow rog`                                                 |
| `compare`             | `model describe compare rog`                                              |
| `type`                | `model describe taxonomy rog`                                             |
| `relation`            | `model describe relations rog` (using `scope relations`)                 |
| `clusters`            | `model describe cluster rog` (plus `style table` when appropriate)       |
| `motifs`              | `model describe motifs fog` (plus `scope relations` and `style bullets`) |

These examples are illustrative; in practice you can combine:

- A semantic static prompt (for example, `describe`, `system`, `product`),
- One or more axis tokens (scope, method, style), and
- A directional lens,

to reconstruct or refine the behaviours previously covered by the retired static prompts.

Some newer styles and methods (for example, `slack`, `jira`, `taxonomy`) were introduced directly as axis values and therefore do not appear in this retired-static-prompt table; they are still accessed via the axis-based grammar and patterns described elsewhere in this ADR.

Structural and relational retirements (`structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`) are further characterised in ADR 013, which focuses on static-prompt/axis refinement and streamlining.

### Design rule for new behaviours

When adding new GPT behaviours in this repo:

- **Prefer axes and patterns first**:
  - Ask: “Is this primarily a way of thinking (method), a slice of territory (scope), or an output shape (style)?”.
  - If so, add or reuse an axis token and, if helpful, a pattern recipe rather than a new static prompt.
- **Name axis tokens for speech**:
  - Use short, single, pronounceable words without hyphens (for example, `shellscript` instead of `shell-script`); avoid punctuation or multi-word phrases in axis keys so they remain easy to speak and remember.
- **Expose high-value recipes as patterns**:
  - For axis combinations you expect to use frequently, add or update named patterns in `lib/modelPatternGUI.py` (see ADR 006) so users can access them via the pattern GUI as well as by speaking the full grammar.
- **Add new static prompts sparingly**:
  - Only when the behaviour encodes a clearly semantic/domain lens or a structured task that is not recoverable from axes alone (for example, `system`, `wardley`, `problem`).
- **Keep docs and tests in sync**:
  - For any new axis/static-prompt combination, ensure:
    - Axis lists (`GPT/lists/*Modifier.talon-list`) are updated.
    - Patterns/help surfaces show at least one example (for example, update `lib/modelPatternGUI.py` and quick-help fallbacks in `lib/modelHelpGUI.py`).
    - Relevant tests are added or updated so regressions are visible.
  - When you change prompts or axes, run at least the focused tests that encode ADR 012’s guardrails:
    - `tests/test_axis_mapping.py`
    - `tests/test_talon_settings_model_prompt.py`
    - `tests/test_static_prompt_docs.py`
    - `tests/test_model_pattern_gui.py`
    - `tests/test_model_help_gui.py`

#### Mini-checklist: deprecating a static prompt

When retiring or demoting an existing static prompt in this repo:

- Decide the axis-based replacement:
  - Identify the semantic static prompt to use instead (often `describe` or an existing lens).
  - Decide the intended completeness/scope/method/style and directional lens.
- Ensure axis vocabularies support it:
  - Add or reuse method/style tokens in the Talon lists if needed.
- Update configuration and lists:
  - Reflect the axes in `lib/staticPromptConfig.py` (if a transitional profile is still needed).
  - Remove the static prompt key from `GPT/lists/staticPrompt.talon-list` once axis recipes are in place.
- Update UX surfaces:
  - Add or adjust patterns in `lib/modelPatternGUI.py`.
  - Update quick-help examples in `lib/modelHelpGUI.py` if appropriate.
- Update docs and tests:
  - Adjust ADRs/README/migration tables to show the axis-based form.
  - Keep `tests/test_static_prompt_docs.py` and other guardrail tests passing.

### Tests and guardrails (this repo)

The following tests and helpers in this repo exercise the behaviour described in ADR 012:

- `tests/test_axis_mapping.py`:
  - Verifies that axis tokens (including style and method modifiers) round-trip through the value→key maps used by recipes and GUIs.
- `tests/test_talon_settings_model_prompt.py`:
  - Checks `modelPrompt`’s composition logic for completeness/scope/method/style and ensures the effective axes are pushed into `GPTState.system_prompt` and `last_recipe`.
- `tests/test_static_prompt_docs.py`:
  - Asserts that all profiled static prompts are present in `staticPrompt.talon-list`.
  - Ensures that pattern recipes’ static prompts are documented in the static prompt help text.
   - Includes guardrails that:
     - Axis-only tokens from ADR 012 (for example, `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `debug`, `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`, `taxonomy`) never reappear as `staticPrompt` keys.
     - Static-prompt docs themselves continue to mention that some behaviours are axis-only and point to ADR 012/013 and the README cheat sheet for axis-based recipes.
- `tests/test_model_pattern_gui.py`, `tests/test_model_help_gui.py`:
  - Characterise how patterns and quick-help present recipes and axis tokens (including the newer diagram/adr/debugging-style patterns).
   - Cover axis-based patterns for diagrams, ADRs, Presenterm slides, Slack/Jira formatting, and motif scans, ensuring their recipes parse into the expected axis combinations.
 - For contributor-focused guidance on when and how to change prompts/axes (including a checklist of guardrail tests to run), see the “GPT prompts, axes, and ADRs” section in `CONTRIBUTING.md`.
 - When making incremental changes under this ADR, you can follow the loop pattern in `docs/adr/adr-loop-execute-helper.md` (pick a small slice, implement, validate, and record it in this work-log).

Together, these tests provide guardrails so that:

- Axis vocabularies remain consistent between Talon lists, recipes, GUIs, and docs.
- Static prompt retirements and axis migrations remain in sync with help surfaces and pattern UIs.

### Practical usage tips

In this repo, a good mental model for using the new grammar is:

- Treat **static prompts** as “what lens or domain?” (for example, `describe`, `system`, `product`, `wardley`, `math`).
- Treat **axes** as “how and in what shape?”:
  - Completeness (how deep), scope (what territory), method (how to think), style (how to present).
- Use **patterns** for common bundles:
  - For example, run “Sketch diagram” instead of remembering `describe · gist · focus · diagram · fog`.
  - Run “Architecture decision” instead of remembering `describe · full · focus · adr · rog`.
  - Run “Present slides” instead of remembering `describe · full · focus · presenterm · rog`.
  - Run “Slack summary” / “Jira ticket” instead of remembering `describe · gist · focus · slack · fog` or `describe · full · focus · steps · jira · fog`.
  - Run “Motif scan” instead of remembering `describe · gist · relations · motifs · bullets · fog`.
  - Use taxonomy-style recipes (for example, `describe · full · focus · taxonomy · rog` or the “Type outline” pattern) when you need type/taxonomy outputs (categories, subtypes, relationships).
  - Discover and run these bundles via:
    - `model patterns` / `model coding patterns` / `model writing patterns` (pattern GUI; see ADR 006).
    - `model quick help` / `model show grammar` to inspect axis combinations and get speakable recipes.
- Use **suggestion helpers** when you’re not sure which axes to pick:
  - `model suggest` / `model suggest for <subject>` (ADR 008) can propose concrete `staticPrompt · completeness · scope · method · style · directional` recipes for the current context, which you can then run or adapt.
- When in doubt:
  - Start with `model describe fog`.
  - Add one or two axes as needed (for example, `structure`, `flow`, `diagram`, `adr`, `systems`, `debugging`, `motifs`).
  - For more examples of concrete, speakable recipes, see the “Common axis recipes (cheat sheet)” section in `GPT/readme.md`.
  - To iterate on a good combination without re-speaking everything, use `model again` / `model again [<staticPrompt>] [axis tokens…]` (ADR 009) to rerun and tweak the last recipe.

### Status snapshot vs Implementation Sketch

In this repo, all of ADR 012’s implementation steps are complete; remaining work under this ADR is primarily maintenance, documentation, and occasional new patterns/examples built on the existing axes.

For a dated, slice-by-slice record of how this ADR was applied here, see `docs/adr/012-style-and-method-prompt-refactor.work-log.md`.

Mapping the “Implementation Sketch and Next Steps” section to this repo’s current state:

- **Step 1 – Extend axis vocabularies**: implemented.
  - Style: `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, `taxonomy`, etc.
  - Method: `systemic`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `wasinawa`, alongside existing `steps`, `plan`, `rigor`, `filter`, `cluster`, etc.
- **Step 2 – Update static prompt configuration**: implemented for all targeted prompts.
  - Format/transform prompts and several axis-shaped prompts have had their profiles removed or simplified in `lib/staticPromptConfig.py`.
- **Step 3 – Remove retired static prompts**: implemented for all prompts listed in this ADR for this repo.
  - `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, and others have been removed from `staticPrompt.talon-list`.
- **Step 4 – Adjust documentation and help surfaces**: implemented.
  - README, quick-help, static prompt docs, ADRs 005/007/008/012/013, and pattern GUIs have been updated to emphasise axis-based usage.
  - Axis-based patterns such as “Sketch diagram”, “Architecture decision”, “Present slides”, “Slack summary”, “Jira ticket”, “Motif scan”, and “Type outline” are present in `lib/modelPatternGUI.py`.
- **Step 5 – Guardrails and tests**: implemented for this repo’s scope.
  - Axis mapping tests, `modelPrompt` composition tests, static prompt docs tests, and pattern/help GUI tests cover the new behaviour.

Future work related to this ADR in this repo is now mostly optional/refinement:

- Decide if and when to fully retire certain remaining method-heavy static prompts (for example, `experiment`, `science`) in favour of pure axis-based recipes. If/when that happens, representative axis-first replacements would be:
  - `model experiment` / `model science` → `model describe experimental fog` (or `model describe experimental rog` for more exhaustive plans and hypotheses).
- Continue evolving patterns and docs to highlight high-value axis combinations rather than adding new static prompts.
- When considering further static-prompt/axis refinements beyond what is already implemented here, treat ADR 013 as the primary home for those decisions and keep this ADR focused on the style/method refactor it records.
