## Current status snapshot (this repo)

As of 2025‑12‑04, ADR 012 is effectively implemented in this repo:

- Core behaviour changes are in place:
  - Format/method-shaped static prompts have been retired into style/method axes and patterns.
  - Static prompts now form a smaller semantic backbone (domain lenses and structured tasks).
- Guardrails (tests, docs, pattern GUIs) have been updated to:
  - Keep axis vocabularies, static prompts, and patterns in sync.
  - Prevent axis-only tokens from being reintroduced as static prompts.
- Remaining work for this ADR in this repo is mostly:
  - Documentation refinements and contributor guidance.
  - Occasional new patterns or examples that showcase existing axes.

The dated slices below record the concrete steps taken to reach this state. Each slice follows the loop pattern in `docs/adr/adr-loop-execute-helper.md` (pick a small slice, implement, validate, and record it).

### 2025-12-04 – Maintenance note: axis-only list and guardrails

- When adding or removing axis-only behaviours in ADR 012’s “Axis-only prompt summary”:
  - Keep `tests/test_static_prompt_docs.py:test_axis_only_tokens_do_not_appear_as_static_prompts` in sync.
  - Update the “GPT prompts, axes, and ADRs” section in `CONTRIBUTING.md` so contributor-facing examples match the ADR and tests.

### 2025-12-04 – Maintenance note: axis-only vs semantic-backbone terminology

- In ADR 012 and this work-log:
  - “Axis-only behaviours” refers to style/method axis values that do **not** have static prompt tokens.
  - “Semantic-backbone static prompts” refers to the smaller set of static prompts that remain as primary “what” lenses.


## 2025-12-04 – Slice: tidy taxonomy bullet formatting in axis-only summary

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Fix a minor formatting issue in the axis-only style summary so the `taxonomy` style bullet is aligned with the other bullets.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Axis-only prompt summary” section:
  - Corrected the indentation for the `taxonomy` style bullet so it uses the same two-space, single-dash pattern as the surrounding bullets (previously it had an extra leading space, which could render oddly in some markdown viewers).

### Behaviour impact

- No runtime changes; this slice only cleans up formatting:
  - The axis-only style list now renders consistently, making `taxonomy` appear as a proper peer of the other style-only behaviours.

### Notes and follow-ups

- No further action needed; this was a one-off formatting fix.*** End Patch ***!


## 2025-12-04 – Slice: clarify that some axis-only tokens never had static prompts

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Avoid confusion by explicitly stating that some axis-only behaviours (for example, `slack`, `jira`, `taxonomy`) were never static prompts, so they do not appear in the retired-prompts migration table.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Migration guide for retired prompts” section:
  - After the migration table and explanatory paragraph, added a note explaining that:
    - Some newer styles/methods (such as `slack`, `jira`, `taxonomy`) were introduced directly as axis values rather than as static prompts.
    - These therefore do not appear in the retired-static-prompt table but are still accessed via the axis-based grammar and patterns described elsewhere in the ADR.

### Behaviour impact

- No runtime changes; this slice only clarifies documentation:
  - Readers are less likely to assume that every style/method value must have a corresponding retired static prompt, and understand why some axis-only tokens are missing from the migration table.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Extend this note if additional axis-only behaviours are introduced without ever being static prompts.*** End Patch !***


## 2025-12-04 – Slice: mention Slack/Jira/taxonomy in static-prompt docs axis-only note

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Keep the static-prompt docs axis-only note aligned with the current axis-only style summary, including Slack/Jira formatting and taxonomy-style outputs.

### Summary of this loop

- Updated `GPT/gpt.py` in `_build_static_prompt_docs`:
  - Expanded the introductory note so the examples now include:
    - Slack/Jira formatting and taxonomy-style outputs alongside diagrams, Presenterm decks, ADRs, shell scripts, and debugging.
  - The note still explains that these behaviours live only as style/method axis values rather than static prompts and points to ADR 012/013 and the README cheat sheet for recipes.

### Behaviour impact

- No runtime changes; this slice only enriches descriptive docs:
  - Any UI or helper that shows static-prompt docs now reflects the broader axis-only style set (including `slack`, `jira`, `taxonomy`) that users can access via axes and patterns.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Adjust this example list again if new, prominent axis-only styles are introduced.*** End Patch ***!

## 2025-12-04 – Slice: add style/method axis vocab for retired prompts

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Start wiring ADR 012 by extending the style and method axes so that behaviours from soon‑to‑be‑retired static prompts can be expressed via modifiers.

### Summary of this loop

- Extended `GPT/lists/styleModifier.talon-list` with new, single-token style modifiers that correspond to format/shape-heavy static prompts and channel-specific formatting:
  - `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`.
- Extended `GPT/lists/methodModifier.talon-list` with new method modifiers for thinking frames that currently appear as static prompts:
  - `systems`, `experimental`, `debugging`.
- Left static prompts and `STATIC_PROMPT_CONFIG` untouched in this slice; they still provide the old entrypoints, but the axis vocab now has the tokens ADR 012 expects.

### Behaviour impact

- No prompt routing or precedence changes yet:
  - `modelPrompt` already accepts style/method modifiers, so the new tokens are recognised and passed through, but no static prompt profiles have been migrated to rely on them.
  - Existing static prompts (`diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `system`, `experiment`, `science`, `debug`) remain active and unchanged.
- Users *can* start experimenting with commands like `model describe diagram` or `model describe systems`, but the deeper behaviour (for example, full Presenterm/Mermaid/Jira guardrails) is still defined by the static prompt and model-purpose instructions rather than exclusively by these new axis descriptions.

### Notes and follow-ups

- Follow-up slices for ADR 012 should:
  - Migrate the long instruction strings and safety contracts from:
    - `GPT/lists/staticPrompt.talon-list` (and `modelPurpose` where relevant) into the new style/method modifier descriptions or adjacent helpers.
  - Update `lib/staticPromptConfig.py` so that retired prompts encode their intended axes (`style`/`method`) before being removed from the static prompt list.
  - Remove the retired static prompts from `GPT/lists/staticPrompt.talon-list` once axis behaviour and docs are in place.
  - Update docs, help surfaces, and tests to reference the new axis tokens instead of the removed static prompts.

## 2025-12-04 – Slice: wire systems/experimental/debugging methods into static prompt profiles

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Align the `system`, `experiment`, `science`, and `debug` static prompt profiles with the new method axis tokens so their behaviour is expressed through `methodModifier` values.

### Summary of this loop

- Updated `lib/staticPromptConfig.py` so that:
  - `system` now has an explicit axis profile:
    - `method: "systems"`, `scope: "focus"`, `style: "plain"`.
  - `experiment` now uses `method: "experimental"` instead of `rigor`.
  - `science` now uses `method: "experimental"` instead of `rigor`.
  - `debug` now uses `method: "debugging"` instead of `rigor`.
- Left completeness/scope/style for `experiment`/`science`/`debug` unchanged (still `completeness: "full"`, `style: "plain"`, `scope: "focus"`).

### Behaviour impact

- For `model system` (and patterns that use `system` as the static prompt):
  - The effective method axis is now `systems` by default (unless overridden by a spoken method modifier).
  - `GPTState.system_prompt.method` will reflect `systems`, and the constraints block will surface `Method: systems` when appropriate.
- For `model experiment`, `model science`, and `model debug`:
  - The default method axis is now `experimental` (for `experiment`/`science`) and `debugging` (for `debug`) instead of `rigor`.
  - Any code that relies on `get_static_prompt_axes("experiment" | "science" | "debug")["method"]` will now see the new tokens.
- Existing tests that explicitly baked in `method="rigor"` for these prompts were not present in this repo, so no test updates were required for this slice; tests around generic axis mapping (for example, `tests/test_axis_mapping.py`) remain valid.

### Notes and follow-ups

- Future slices for ADR 012 should:
  - Update any pattern recipes, docs, or ADRs that describe `experiment`/`science`/`debug` in terms of `rigor` to match the new method names.
  - Remove `system`, `experiment`, `science`, and `debug` from `GPT/lists/staticPrompt.talon-list` once:
    - Method behaviour via `systems` / `experimental` / `debugging` is clearly documented, and
    - Recipes and help surfaces have been updated to use the method axis instead of these static prompts.

## 2025-12-04 – Slice: migrate Presenterm from static prompt to style axis

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Move the specialised Presenterm behaviour off the `staticPrompt` surface and into the `style` axis, then remove the `presenterm` static prompt token.

### Summary of this loop

- Updated `GPT/lists/styleModifier.talon-list`:
  - Replaced the concise `presenterm` style description with the full Presenterm contract previously stored on the `presenterm` static prompt:
    - Front-matter schema, slide structure, directives, fence safety, HTML/Markdown safety, Mermaid/LaTeX/D2/snippet handling, and encoding rules.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `presenterm` static prompt entry entirely; only `context` and `code` remain in that cluster.

### Behaviour impact

- The only way to request Presenterm formatting is now via the style axis (for example, `style presenterm`) or any recipes that incorporate that style:
  - `model describe presenterm …` instead of `model presenterm …`.
- All of the Presenterm safety and formatting guarantees are now owned by the `styleModifier` description, not by the static prompt:
  - Axis docs (`gpt_help`) will surface the Presenterm contract under “Style modifiers”.
- Removing `presenterm` from `staticPrompt.talon-list` means:
  - The `staticPrompt` grammar no longer accepts `presenterm` as a task token.
  - `tests/test_static_prompt_docs.py` remains green because `presenterm` was never in `STATIC_PROMPT_CONFIG`, and the guardrail only enforces that profiled prompts appear in the Talon list.

### Notes and follow-ups

- Future slices for ADR 012 should:
  - Update README/help text to call out Presenterm as a style rather than a static prompt.
  - Audit any remaining documentation that describes `presenterm` as a static prompt and adjust language to “use `style presenterm`”.
  - Apply the same migration pattern to other format/shape-heavy static prompts (`diagram`, `HTML`, `gherkin`, `shell`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`) before deleting their static prompt tokens.

## 2025-12-04 – Slice: migrate Diagram from static prompt to style axis

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Move the Mermaid-diagram formatting behaviour off the `diagram` static prompt and into the `diagram` style modifier, then remove the `diagram` static prompt token.

### Summary of this loop

- Updated `GPT/lists/styleModifier.talon-list`:
  - Strengthened the `diagram` style description so it clearly encodes the key Mermaid contract from the static prompt:
    - Convert input into appropriate Mermaid diagram code only.
    - Infer the most suitable diagram type for the task.
    - Respect Mermaid safety constraints: diagrams do not allow parentheses in syntax; use careful label encoding instead of raw problematic characters.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `diagram` static prompt entry and its adjacent comment; the Transformation/Reformatting section now starts with `gherkin`.

### Behaviour impact

- The intended way to ask for Mermaid diagrams is now via the style axis, e.g.:
  - `model describe diagram …`
  - rather than `model diagram …`.
- The Merlin/Mermaid safety rule that was previously only mentioned in the static prompt comment (“mermaid diagrams do not allow parentheses”) is now part of the `styleModifier` description for `diagram`, so:
  - Axis docs (`gpt_help`) surface this constraint directly under style modifiers.
- The `diagram` profile in `lib/staticPromptConfig.py` remains for now (description + axis defaults: `completeness: "gist"`, `scope: "focus"`, `style: "code"`), but there is no longer a `diagram` token in `staticPrompt.talon-list`:
  - `tests/test_static_prompt_docs.py` still characterises behaviour correctly because it only requires that profiled prompts have corresponding tokens *until* we intentionally remove them; after further slices, we may simplify or remove the `diagram` profile entirely once recipes and docs are fully axis-based.

### Notes and follow-ups

- Follow-up ADR 012 slices should:
  - Decide whether to keep a minimal `diagram` profile in `STATIC_PROMPT_CONFIG` (for help text only) or remove it once axis usage is stable.
  - Update any user-facing docs or examples that still show `model diagram` to instead use `style diagram`.
  - Apply the same pattern to the remaining format/shape-heavy prompts (`HTML`, `gherkin`, `shell`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`), shifting their contracts into styles and then deleting their static prompt tokens.

## 2025-12-04 – Slice: remove Diagram profile from STATIC_PROMPT_CONFIG

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Bring configuration and guardrails in line with the decision to retire `diagram` as a static prompt by removing its profile from `STATIC_PROMPT_CONFIG`.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `diagram` entry from `STATIC_PROMPT_CONFIG`, leaving `HTML`, `gherkin`, `shell`, `commit`, and `ADR` as the remaining format/transform prompts with profiles.

### Behaviour impact

- `get_static_prompt_profile("diagram")` and `get_static_prompt_axes("diagram")` now return `None` / `{}`:
  - This matches the fact that `diagram` is no longer a valid `staticPrompt` token and is instead represented solely by the `diagram` style modifier.
- `tests/test_static_prompt_docs.py`’s guardrail (“every profiled prompt key should appear in the Talon list”) is conceptually restored for `diagram`, because:
  - `diagram` is no longer in `STATIC_PROMPT_CONFIG`, and
  - its token has already been removed from `GPT/lists/staticPrompt.talon-list`.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Perform the same “profile removal” step for other retired static prompts once their behaviours are fully migrated to styles/methods and their tokens are removed from `staticPrompt.talon-list`.
  - Consider adding a short note to ADR 012 summarising which static prompts are now purely axis-based (for example, `diagram` and `presenterm`) and no longer appear in `STATIC_PROMPT_CONFIG`.

## 2025-12-04 – Slice: retire gherkin static prompt in favour of gherkin style

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the remaining `gherkin` static prompt profile and token so Gherkin formatting is accessed only via the `gherkin` style modifier.

### Summary of this loop

- Updated `tests/test_talon_settings_model_prompt.py`:
  - Removed `test_model_prompt_applies_code_style_for_gherkin`, which asserted that `staticPrompt="gherkin"` sets `completeness/full`, `scope/bound`, and `style/code`.
  - This frees the test suite from depending on a `gherkin` static prompt profile.
- Updated `lib/staticPromptConfig.py`:
  - Removed the `gherkin` entry from `STATIC_PROMPT_CONFIG`, leaving `HTML`, `shell`, `commit`, and `ADR` as the remaining format/transform prompts with profiles.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `gherkin` static prompt entry and its explanatory comment from the “Transformation and Reformatting” section.

### Behaviour impact

- The only representation of Gherkin formatting is now the `gherkin` style modifier in `GPT/lists/styleModifier.talon-list`:
  - Users request it via commands like `model describe gherkin …` instead of `model gherkin …`.
- `get_static_prompt_profile("gherkin")` and `get_static_prompt_axes("gherkin")` now return `None` / `{}`:
  - This aligns with the fact that `gherkin` is no longer a `staticPrompt` token.
- Static prompt docs tests:
  - No longer reference `gherkin` as a profiled static prompt, so the “profiled prompts must appear in the Talon list” guardrail remains satisfied.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Update any user-facing docs or examples (including ADR 005/007/008/012) that describe `gherkin` as a static prompt so they instead reference `style gherkin`.
  - Apply the same pattern to other format-heavy prompts (`HTML`, `shell`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`) once their contracts live fully on styles/methods and tests/docs are updated accordingly.

## 2025-12-04 – Slice: retire HTML static prompt in favour of html style

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the remaining `HTML` static prompt profile and token so semantic HTML formatting is accessed only via the `html` style modifier.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `HTML` entry from `STATIC_PROMPT_CONFIG`, so it is no longer a profiled static prompt.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `HTML: HTML` static prompt entry and its “Semantic HTML only.” comment from the Output and Formatting section.

### Behaviour impact

- The only representation of semantic-HTML output is now the `html` style modifier in `GPT/lists/styleModifier.talon-list`:
  - Users request it via commands like `model describe html …` instead of `model HTML …`.
- `get_static_prompt_profile("HTML")` and `get_static_prompt_axes("HTML")` now return `None` / `{}`:
  - This matches its removal from `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.
- Tests:
  - No tests in this repo referenced `staticPrompt="HTML"`, so no test changes were required for this slice.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Update docs/ADRs that list `HTML` as a static prompt (for example, ADR 005/007/012) so they describe it as a style-based behaviour.
  - Continue retiring other format-heavy static prompts (`shell`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`) once their style/method contracts are fully in place.

## 2025-12-04 – Slice: retire shell static prompt in favour of shellscript style

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the remaining `shell` static prompt profile and token so shell-script behaviour is accessed only via the `shellscript` style modifier.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `shell` entry from `STATIC_PROMPT_CONFIG`, so it is no longer a profiled static prompt.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `shell: shell` static prompt entry and its “Write a shell script.” comment from the planning/product section.

### Behaviour impact

- The only representation of “write a shell script” behaviour is now the `shellscript` style modifier in `GPT/lists/styleModifier.talon-list`:
  - Users request it via commands like `model describe shellscript …` instead of `model shell …`.
- `get_static_prompt_profile("shell")` and `get_static_prompt_axes("shell")` now return `None` / `{}`:
  - This matches its removal from `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.
- Existing shell-related settings (for example, `user.model_shell_default`) remain valid; they control how generated shell snippets are executed or framed, independent of whether `shell` is a static prompt or a style.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Update README/help examples that mention `model shell` to instead show `style shellscript`.
  - Continue applying this pattern to other remaining format-heavy static prompts (`emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`) once their contracts are fully expressed via styles/methods.

## 2025-12-04 – Slice: retire emoji static prompt in favour of emoji style

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the `emoji` static prompt profile and token so “emoji-only” behaviour is accessed only via the `emoji` style modifier.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `emoji` entry from `STATIC_PROMPT_CONFIG` so it is no longer a profiled static prompt (leaving `format` and `LLM` as description-only prompts in that section).
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `emoji: emoji` static prompt entry from the “Output and Formatting” section.

### Behaviour impact

- The only representation of “emoji-only” output is now the `emoji` style modifier in `GPT/lists/styleModifier.talon-list`:
  - Users request it via commands like `model describe emoji …` instead of `model emoji …`.
- `get_static_prompt_profile("emoji")` and `get_static_prompt_axes("emoji")` now return `None` / `{}`:
  - This matches its removal from `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.
- No tests in this repo referenced `staticPrompt="emoji"`, so no test updates were needed.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Sweep docs (including ADR 005/007/012 and README) for any references to `emoji` as a static prompt and update them to use `style emoji`.
  - Continue retiring remaining format-heavy static prompts (`format`, `recipe`, `lens`, `commit`, `ADR`) once their style/method semantics are in place.

## 2025-12-04 – Slice: retire format static prompt in favour of style/purpose combos

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the `format` static prompt profile and token so formatting is expressed via style and purpose axes (for example, `style slack`, `style jira`, `for slack`, `for table`) rather than a generic “format” task.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `format` entry from `STATIC_PROMPT_CONFIG`, so it is no longer a profiled static prompt.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `format: format` static prompt entry from the “Output and Formatting” section, leaving `fix` and `LLM` as the remaining prompts there.

### Behaviour impact

- There is no longer a generic `model format` static prompt:
  - Users should instead combine styles and purposes that reflect the target channel or representation (for example, `style slack`, `style jira`, `style html`, `for slack`, `for table`).
- `get_static_prompt_profile("format")` and `get_static_prompt_axes("format")` now return `None` / `{}`:
  - Aligning configuration with the absence of a `format` staticPrompt token.
- No tests in this repo referenced `staticPrompt="format"`, so no test updates were required for this slice.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Update docs and examples that previously used `model format` to show concrete style/purpose combinations instead.
  - Continue focusing static prompts on semantic tasks or lenses, keeping “how/shape” concerns on the style and purpose axes.

## 2025-12-04 – Slice: retire commit static prompt in favour of commit style

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the `commit` static prompt profile and token so conventional commit messages are expressed only via the `commit` style modifier.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `commit` entry from `STATIC_PROMPT_CONFIG`, so it is no longer a profiled static prompt.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `commit: commit` static prompt entry and its “Conventional commit message for staged changes.” comment from the planning/product section.

### Behaviour impact

- The only representation of “conventional commit message” behaviour is now the `commit` style modifier in `GPT/lists/styleModifier.talon-list`:
  - Users request it via commands like `model describe commit …` (or recipes that bake in `style commit`) rather than `model commit …`.
- `get_static_prompt_profile("commit")` and `get_static_prompt_axes("commit")` now return `None` / `{}`:
  - This matches its removal from `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.
- No tests in this repo referenced `staticPrompt="commit"`, so no test updates were required for this slice.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Update README/help examples or ADRs that mention `model commit` so they instead show `style commit`.
  - Apply a similar treatment to the remaining document-shaped static prompt `ADR` once its behaviour is fully captured by the `adr` style modifier and docs are updated.

## 2025-12-04 – Slice: retire recipe static prompt in favour of recipe style

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the `recipe` static prompt profile and token so “represent as a recipe with a mini-language and key” is accessed only via the `recipe` style modifier.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `recipe` entry from `STATIC_PROMPT_CONFIG`, so it is no longer a profiled static prompt.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `recipe: recipe` static prompt entry from the “Variations and Playful” section.

### Behaviour impact

- The “recipe-like” expression is now captured solely by:
  - The `recipe` style modifier in `GPT/lists/styleModifier.talon-list`, whose description already mirrors the original static prompt (“express as a recipe with a custom mini-language plus a key”).
- `get_static_prompt_profile("recipe")` and `get_static_prompt_axes("recipe")` now return `None` / `{}`:
  - Matching its removal from `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.
- No tests in this repo referenced `staticPrompt="recipe"`, so no test updates were required in this slice.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Update any docs/ADRs that highlight `recipe` as a static prompt so they instead mention `style recipe`.
  - Consider whether `lens` should follow the same pattern (potentially via the `abstractvisual` style) once its semantics are fully captured on the style axis.

## 2025-12-04 – Slice: retire lens static prompt in favour of abstractvisual style

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the `lens` static prompt profile and token so “abstract visualization that avoids diagrams or maps” is accessed via the `abstractvisual` style modifier.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `lens` entry from `STATIC_PROMPT_CONFIG`, so it is no longer a profiled static prompt.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `lens: lens` static prompt entry from the “Variations and Playful” section.
- Left the `abstractvisual` style modifier description in `GPT/lists/styleModifier.talon-list` as the primary representation of this behaviour:
  - It already captures “abstract visual or metaphorical layout” with a legend and optional code/SVG-like hints, matching the intent of the original `lens` prompt.

### Behaviour impact

- Abstract, non-map visualizations are now requested via:
  - `style abstractvisual` (for example, `model describe abstractvisual …`) rather than `model lens …`.
- `get_static_prompt_profile("lens")` and `get_static_prompt_axes("lens")` now return `None` / `{}`:
  - Matching its removal from `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.
- No tests in this repo referenced `staticPrompt="lens"`, so no test updates were required for this slice.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Update any docs/ADRs that describe `lens` as a static prompt so they instead mention `style abstractvisual`.
  - Revisit ADR 012’s summary to list `lens` alongside `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `emoji`, `format`, `recipe`, and `commit` as prompts that are now fully axis-based.

## 2025-12-04 – Slice: retire ADR static prompt in favour of adr style

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the `ADR` static prompt profile and token so ADR-shaped documents are expressed only via the `adr` style modifier.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `ADR` entry from `STATIC_PROMPT_CONFIG`, so it is no longer a profiled static prompt.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `ADR: ADR` static prompt entry and its “Write an ADR.” comment from the planning/product section.

### Behaviour impact

- Architecture Decision Record behaviour is now represented solely by:
  - The `adr` style modifier in `GPT/lists/styleModifier.talon-list` (“Express the answer as an ADR with sections for context, decision, consequences.”).
  - Recipes and patterns that choose `style adr` on top of semantic prompts (for example, `describe`, `system`, `product`).
- `get_static_prompt_profile("ADR")` and `get_static_prompt_axes("ADR")` now return `None` / `{}`:
  - Matching its removal from both `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.
- No tests in this repo referenced `staticPrompt="ADR"`, so no test changes were required in this slice.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Update ADR 012 itself (and any other docs) to clearly list `ADR` among the now-axis-only prompts.
  - Consider adding one or two pattern recipes that showcase `style adr` combined with common semantic prompts (for example, “Architecture decision for this change” using `describe · full · focus · adr · rog`).

## 2025-12-04 – Slice: retire code static prompt in favour of code style

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the `code` static prompt profile and token so “code-only” behaviour is represented solely by the `code` style modifier.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `code` entry from `STATIC_PROMPT_CONFIG`, so it is no longer a profiled static prompt.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `code: code` static prompt entry from the “Transformation and Reformatting” section.

### Behaviour impact

- Code-only responses are now expressed via the `code` style modifier (`style code`) instead of `model code`:
  - For example, `model describe code …` to “just give code/markup, no prose.”
- `get_static_prompt_profile("code")` and `get_static_prompt_axes("code")` now return `None` / `{}`:
  - Matching its removal from both `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.
- No tests in this repo referenced `staticPrompt="code"`, so no test updates were needed.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Ensure docs and examples use `style code` (or purpose-based prompts such as `for coding`) instead of `model code`.
  - Consider a short “code-only” pattern recipe (for example, “Implement only” using `describe · full · bound · code · rog`) to make this behaviour discoverable.

## 2025-12-04 – Slice: add Current Status section to ADR 012

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Reconcile ADR 012’s narrative with the concrete work completed in this repo by adding a short “Current Status” snapshot.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added a “Current Status (this repo)” subsection under **Status**, summarising:
    - Which style-heavy prompts have been fully retired into styles (`diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`).
    - Which method-heavy prompts have moved their stance into methods (for example, `debug` → `method debugging`) and which still exist as static prompts (`system`, `experiment`, `science`).
    - The current axis vocabularies for style and method.
  - Included concrete example commands showing the new, axis-first usage (for example, `model describe diagram fog`, `model describe presenterm rog`, `model describe adr`, `model describe systemic fog`).

### Behaviour impact

- No runtime changes in this slice; it is purely documentation:
  - ADR 012 now accurately reflects the state of this repo after the preceding implementation slices.
  - Future loops (and readers) can see at a glance which prompts are still candidates for migration (for example, `system`, `experiment`, `science`) and which are already axis-only.

### Notes and follow-ups

- Future ADR 012 loops can:
  - Decide whether and when to fully retire `system`, `experiment`, and `science` as static prompts, given that their methods are already captured on the axis.
  - Further tighten docs/help so all examples and guidance consistently use the axis-based forms summarised in the new “Current Status” section.

## 2025-12-04 – Slice: mark ADR 012 as Accepted for this repo

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Update ADR 012’s metadata to reflect that its core decisions have been implemented in this repository.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Changed the header status from `Proposed` to `Accepted`.
  - Left the “Current Status (this repo)” subsection in place to indicate which parts are fully applied (style/method migrations) and which parts remain optional or future work (`system`, `experiment`, `science` retirement).

### Behaviour impact

- No runtime changes; this slice only updates ADR metadata:
  - The status now matches the fact that:
    - The targeted static prompts have been retired into style/method axes in this repo, and
    - The ADR’s implementation sketch has been followed in code, tests, and docs.

### Notes and follow-ups

- Future loops for ADR 012, if any, should:
  - Be treated as refinements or extensions (for example, possibly retiring `system`/`experiment`/`science` as static prompts), not as gating work for accepting the ADR.

## 2025-12-04 – Slice: align GPT README examples and axis list with retired static prompts

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Ensure `GPT/readme.md` no longer encourages use of retired static prompts like `diagram` as core tasks, and instead showcases axis-based usage with the new style modifiers.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Expanded the Style axis bullet to list the richer set of style modifiers now available in this repo:
    - `plain`, `tight`, `bullets`, `table`, `code`, `checklist`, `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`.
  - Adjusted example commands:
    - Replaced `model diagram gist code fog` with `model describe diagram fog` to reflect diagram as a style rather than as a static prompt.
  - Simplified the description of defaults:
    - Removed the reference to per-prompt defaults (for example, `fix`, `todo`, `diagram`) and now describe defaults solely in terms of `user.model_default_completeness/scope/method/style`.

### Behaviour impact

- No runtime behaviour changes; this slice only updates documentation:
  - New users reading the README now see axis-based usage for diagrams and other shapes, rather than relying on retired prompts like `diagram`.
  - The style axis is presented as the primary place to look for output shapes (slides, diagrams, HTML, Gherkin, shell, emoji, etc.).

### Notes and follow-ups

- Future ADR 012 documentation slices can:
  - Continue sweeping other docs (ADR 005/007/008/012 examples) for `model diagram`, `model presenterm`, `model HTML`, `model gherkin`, `model shell`, etc., and convert them to the axis-first forms.
  - Add a small set of “recipe examples” in the README that combine semantic prompts with the new styles/methods (for example, `describe · full · focus · diagram · rog` as a canonical diagram recipe).

## 2025-12-04 – Slice: update README method axis list to reflect new tokens

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure `GPT/readme.md`’s method axis description and examples reflect the current method tokens and do not reference retired static prompts.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Expanded the `methodModifier` list under “Modifier axes (advanced)” to include the newer method tokens now present in this repo:
    - `steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`, `systems`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `wasinawa`.
  - Adjusted the flow example:
    - Replaced `model flow full steps plain rog` with `model describe flow rog`, so the example now uses `flow` as a method modifier after the `describe` static prompt, rather than relying on the retired `flow` static prompt.

### Behaviour impact

- No runtime changes; this slice only updates documentation:
  - The README now accurately describes the available method modifiers in this repo (including those introduced by ADR 012/013).
  - Example usage for “explain the flow” matches the current grammar and configuration, showing `flow` as a method axis instead of a static prompt.

### Notes and follow-ups

- Future ADR 012/013 documentation slices can:
  - Add further examples that combine the new methods (`structure`, `compare`, `motifs`, `wasinawa`) with semantic prompts and styles.
  - Keep README and help UIs in sync as additional axis tokens or recipes are introduced.

## 2025-12-04 – Slice: align shell default setting docs with shellscript style

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Update shell-related configuration docs so they no longer reference the retired `model shell` static prompt and instead reflect the new `shellscript` style-based behaviour.

### Summary of this loop

- Updated `lib/talonSettings.py`:
  - Clarified the `user.model_shell_default` setting description to say:
    - “The default shell for outputting model shell commands (for example, when using the shellscript style).”
- Updated `GPT/readme.md` configuration table:
  - Changed the `user.model_shell_default` notes column from:
    - “The default shell for `model shell` commands”
  - To:
    - “The default shell used when outputting shell commands (for example, when using the `shellscript` style)”.

### Behaviour impact

- No runtime behaviour changes; this slice only updates documentation:
  - The shell default setting is now described in terms of style-based usage (`shellscript`) rather than the retired `shell` static prompt.
  - New users are less likely to look for a `model shell` static prompt that no longer exists in this repo.

### Notes and follow-ups

- Future ADR 012 documentation slices can:
  - Add a short note in README or help UIs clarifying how `shellscript` style interacts with `user.model_shell_default` (for example, which shell snippets are assumed to target).

## 2025-12-04 – Slice: add explicit axis-only prompt summary to ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make ADR 012 explicitly list which behaviours are now axis-only (styles/methods) so readers do not have to infer this solely from the work-log.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added an “Axis-only prompt summary” subsection under “Current Status (this repo)” that:
    - Lists style-only behaviours (for example, `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, `code`) that now live only on `styleModifier`.
    - Lists method-only behaviours (for example, `debugging`, `systems`, `experimental`, `structure`, `flow`, `compare`, `motifs`, `wasinawa`) that now live only on `methodModifier`.
    - Clarifies that these behaviours are intended to be combined with semantic static prompts (such as `describe`, `system`, `product`) and directional lenses.

### Behaviour impact

- No runtime behaviour changes; this slice only tightens documentation:
  - ADR 012 now has a single, explicit list of axis-only behaviours, making it easier for future maintainers and users to see which prompts have been fully migrated into styles/methods in this repo.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Keep the axis-only summary in sync as additional static prompts are demoted or retired.
  - Add a similar summary for “semantic backbone” prompts that are intentionally kept as static prompts.

## 2025-12-04 – Slice: add semantic-backbone static prompt summary to ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make ADR 012 explicitly describe which kinds of prompts are intentionally kept as static prompts, complementing the axis-only summary.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added a “Semantic-backbone static prompts” subsection under “Current Status (this repo)” that:
    - Describes the role of remaining static prompts as semantic/domain lenses and task shapes rather than axis bundles.
    - Provides example groups:
      - Analysis/perspective (`describe`, `who`/`what`/`when`/`where`/`why`/`how`, `assumption`, `objectivity`, `true`, etc.).
      - Domain/lens-heavy prompts (`knowledge`, `taste`, `system`, `tao`, `com b`, `math` family, `wardley`, `document`, `domain`, `tune`, `melody`, `constraints`, `effects`, `operations`, `facilitate`, `challenge`, `critique`, `retro`, `easier`, `unknown`, `team`, `jim`, etc.).
      - Planning/product (`todo`, `product`, `metrics`, `value`, `jobs`, `done`, `bridge`).
      - Transform/reformat operations (`group`, `split`, `shuffled`, `match`, `blend`, `join`, `sort`, `context`).
      - Variation/exercises (`problem` and similar structured workflows).
    - Notes that future ADRs may refine this backbone further, but the default bias is now towards axes and pattern recipes for new behaviours.

### Behaviour impact

- No runtime behaviour changes; this slice only clarifies documentation:
  - ADR 012 now clearly distinguishes between:
    - Axis-only behaviours (styles/methods), and
    - The smaller, intentionally kept set of semantic static prompts.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Keep the semantic-backbone description in sync as additional static prompts are demoted or consolidated.
  - Potentially add a short “cheat sheet” mapping from older static prompts to recommended axis-based recipes and backbone prompts.

## 2025-12-04 – Slice: add retired-prompts migration guide to ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Provide a concise migration table in ADR 012 that maps retired static prompts to representative axis-based equivalents.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added a “Migration guide for retired prompts” subsection listing common retired static prompts (for example, `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `code`, `debug`, `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`) alongside representative axis-based equivalents such as:
    - `model describe diagram fog`
    - `model describe presenterm rog`
    - `model describe html`
    - `model describe gherkin`
    - `model describe shellscript`
    - `model describe emoji`
    - `model describe slack` / `jira` / `html`
    - `model describe recipe`
    - `model describe abstractvisual`
    - `model describe commit`
    - `model describe adr`
    - `model describe code`
    - `model describe debugging rog`
    - `model describe structure rog`
    - `model describe flow rog`
    - `model describe compare rog`
    - `model describe taxonomy rog`
    - `model describe relations rog` (for `relation` via `scope relations`)
    - `model describe cluster rog` (plus `style table`) and `model describe motifs fog` (plus `scope relations`/`style bullets`).

### Behaviour impact

- No runtime changes; this slice only improves documentation:
  - ADR 012 now contains a direct “cheat sheet” for users migrating from the older static prompt surface to the new axis-first grammar.

### Notes and follow-ups

- Future ADR 012/013 documentation slices can:
  - Keep this table in sync if additional static prompts are retired or if recommended recipes change.

## 2025-12-04 – Slice: note axis-only behaviours in staticPrompt list header

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the staticPrompt Talon list itself hint that some behaviours are axis-only, in line with ADR 012/013 and the README.

### Summary of this loop

- Updated `GPT/lists/staticPrompt.talon-list`:
  - Added a brief header comment after the `list: user.staticPrompt` line:
    - “Static prompts cover the semantic ‘what’ (lenses and domains); many format and method behaviours now live only as style/method axes (see ADR 012/013).”

### Behaviour impact

- No runtime changes; this slice only updates comments:
  - Developers editing `staticPrompt.talon-list` are reminded that:
    - Static prompts are for semantic lenses/domains.
    - Format/method behaviours should generally be expressed via axes, not new static prompts.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Refine this header if the static prompt surface or axis design changes again.

## 2025-12-04 – Slice: add practical usage tips to ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Provide a brief, concrete “how to think about and use this grammar” section so ADR 012 feels more actionable.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added a “Practical usage tips” subsection that:
    - Encourages treating static prompts as “what lens/domain?” and axes as “how/shape?”.
    - Suggests starting from simple forms like `model describe fog` and then adding a small number of axis tokens (for example, `structure`, `flow`, `diagram`, `adr`).
    - Points to patterns such as “Sketch diagram” and “Architecture decision” as easy entry points for axis-heavy recipes without memorising full token strings.

### Behaviour impact

- No runtime changes; this slice only improves ADR 012’s usability:
  - Readers now get a short, opinionated guide on how to approach the new axis-based grammar in everyday use.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Extend this section with additional concrete recipes or shortcuts as more patterns and axes are introduced.

## 2025-12-04 – Slice: document tests and guardrails for ADR 012 behaviour

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Capture in ADR 012 which tests and helpers in this repo exercise the style/method refactor and static prompt streamlining.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added a “Tests and guardrails (this repo)” subsection under the Status/Current Status area that:
    - Lists key tests:
      - `tests/test_axis_mapping.py` – axis token/value mapping and round-trips.
      - `tests/test_talon_settings_model_prompt.py` – `modelPrompt` composition of completeness/scope/method/style into `GPTState.system_prompt` and `last_recipe`.
      - `tests/test_static_prompt_docs.py` – static prompt docs coverage and pattern static prompt documentation.
      - `tests/test_model_pattern_gui.py` / `tests/test_model_help_gui.py` – patterns and quick-help examples using the new axis-based recipes.
    - Summarises how these tests keep axis vocabularies, static prompt profiles, and help/pattern UIs in sync.

### Behaviour impact

- No runtime changes; this slice only improves ADR 012’s documentation:
  - Future maintainers can see at a glance which tests support the ADR 012 behaviour and where to look when making further changes.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Extend this section if additional tests are added specifically for new axis tokens or static prompt migrations.

## 2025-12-04 – Slice: add status snapshot vs Implementation Sketch to ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Summarise which parts of ADR 012’s Implementation Sketch have been carried out in this repo and which remain as optional refinements.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added a “Status snapshot vs Implementation Sketch” subsection that:
    - Maps each Implementation Sketch step (axis vocab, static prompt config, static prompt removal, docs/help updates, tests/guardrails) to this repo’s current state (all implemented).
    - Highlights that remaining work is now mostly optional:
      - For example, deciding if/when to fully retire `system`/`experiment`/`science` as static prompts in favour of pure axis-based recipes.

### Behaviour impact

- No runtime behaviour changes; this slice only clarifies where ADR 012 stands in this repo:
  - Future maintainers can quickly see that ADR 012 is effectively implemented here and that further work is refinement rather than core implementation.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Update this status snapshot if new axis tokens, patterns, or static prompt retirements are added.

## 2025-12-04 – Slice: cross-reference ADR 005’s TODOs with ADR 012/013

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Capture that some of ADR 005’s “Still TODO” ideas around per-prompt profiles have been refined or superseded by ADR 012/013 in this repo.

### Summary of this loop

- Updated `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.work-log.md`:
  - In one of the “Still TODO for ADR 005” sections, added a note that:
    - Format/transform behaviour that might have been encoded as per-prompt completeness profiles is now handled by:
      - `styleModifier` values (for example, `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `recipe`, `abstractvisual`, `commit`, `adr`, `code`), and
      - `methodModifier` values (for example, `debugging`, `systems`, `experimental`) rather than per-static-prompt completeness hints.
    - Remaining per-prompt axis profiles now live in `lib/staticPromptConfig.py` and focus on semantic prompts that genuinely need them.

### Behaviour impact

- No runtime changes; this slice only clarifies how ADR 012/013 relate to earlier ADR 005 TODOs:
  - Readers of ADR 005’s work-log can now see that some of the originally envisioned per-prompt completeness tuning has been re-expressed as axis values and styles rather than as static-prompt-specific hacks.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Further prune or update ADR 005’s TODO notes if additional areas are clearly superseded by the axis-first design.

## 2025-12-04 – Slice: align ADR 008 context with refined static prompt/axis model

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Update ADR 008’s context so it refers to the current semantic-backbone static prompt set and axis design from ADR 012/013.

### Summary of this loop

- Updated `docs/adr/008-prompt-recipe-suggestion-assistant.md`:
  - In the “Context” section, changed the brief grammar description from:
    - “Static prompts (for example, `describe`, `fix`, `todo`, `gherkin`). Contract-style axes: completeness, scope, method, style (ADR 005).”
  - To:
    - “Static prompts (for example, `describe`, `fix`, `todo`, and a smaller, semantic backbone set as refined by ADR 007/012/013). Contract-style axes: completeness, scope, method, style (ADR 005/012/013).”
  - This clarifies that:
    - The suggestion assistant operates over the **current** static prompt surface (narrowed by ADR 012/013), and
    - Axes now include the richer style/method tokens introduced by ADR 012/013.

### Behaviour impact

- No runtime changes; this slice only aligns ADR 008’s narrative with the current design:
  - Readers of ADR 008 are now explicitly pointed at ADR 007/012/013 for the up-to-date static prompt and axis model.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Further enrich ADR 008 with explicit examples that feature axis-based recipes instead of older static-prompt-heavy ones.


## 2025-12-04 – Slice: ensure patterns apply new style axis tokens

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Make sure model patterns that are meant to use heavy styles (for example, `diagram`, `presenterm`, `adr`) actually set the style axis when executed, and guard this with a focused test.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Extended `STYLE_TOKENS` so the pattern parser recognises all current style modifiers from `styleModifier.talon-list`, including:
    - `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, `taxonomy` (alongside `plain`, `tight`, `bullets`, `table`, `code`, `cards`, `checklist`).
  - This means patterns like:
    - `Sketch diagram` (`describe · gist · focus · diagram · fog`),
    - `Architecture decision` (`describe · full · focus · adr · rog`), and
    - `Present slides` (`describe · full · focus · presenterm · rog`)
    now apply their intended style axis when run, instead of silently dropping the style token.
- Updated `tests/test_model_pattern_gui.py`:
  - Added `test_pattern_with_style_token_sets_style_axis`, which runs the `Sketch diagram` pattern and asserts that:
    - `GPTState.last_static_prompt == "describe"`,
    - `last_completeness == "gist"`, `last_scope == "focus"`,
    - `last_method == ""`, and
    - `last_style == "diagram"` with `last_directional == "fog"`.

### Behaviour impact

- Model patterns that include style tokens from ADR 012 now:
  - Correctly set the style axis via `styleModifier`, so `modelPrompt` and downstream prompts see the same “heavy style” semantics as when users speak those styles directly.
  - Produce `GPTState.last_recipe` and axis fields that accurately reflect the pattern’s intent, improving quick-help recaps and `model again` behaviour.
- Existing patterns without explicit style tokens (for example, `Debug bug`) behave unchanged; the new style tokens are additive.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add dedicated patterns for channel-specific styles (for example, `slack`, `jira`) now that `STYLE_TOKENS` understands them.
  - Extend tests to cover additional style-heavy patterns (for example, `Architecture decision` and `Present slides`) if their behaviour becomes more complex.


## 2025-12-04 – Slice: surface Slack/Jira styles in quick-help examples

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Make the replacements for the old `format` static prompt (`slack`, `jira`, `html`) more discoverable by adding Slack/Jira style recipes to the model quick-help examples.

### Summary of this loop

- Updated `lib/modelHelpGUI.py` in `_show_examples`:
  - Added two example axis recipes that showcase channel-specific formatting styles:
    - `Format for Slack: describe · gist · focus · slack · fog`
    - `Format for Jira: describe · gist · focus · jira · fog`
  - Left existing examples for debugging, ADRs, diagrams, and Presenterm slides unchanged.

### Behaviour impact

- When users open the `model` quick-help GUI, they now see concrete examples for:
  - Requesting Slack-formatted output via `style slack`.
  - Requesting Jira-markup-formatted output via `style jira`.
- This makes it clearer how to express “format this for Slack/Jira” after retiring the `format` static prompt, in line with ADR 012’s migration guide.

### Notes and follow-ups

- Future ADR 012/013 slices could:
  - Add a short note in ADR 012 summarising Slack/Jira as the primary replacements for channel-specific formatting that previously went through `model format`.
  - Introduce optional model patterns that bake in these styles for common workflows (for example, “Review for Slack” or “Ticket description”).


## 2025-12-04 – Slice: align README cheat sheet with Slack/Jira styles

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Make the Slack/Jira formatting styles visible in the main GPT README’s axis recipe cheat sheet so users see them alongside diagrams, ADRs, and shell scripts.

### Summary of this loop

- Updated `GPT/readme.md` in the “Common axis recipes (cheat sheet)” section:
  - Added a “Channel formatting” group with two example commands:
    - `model describe slack fog` – format for Slack (Markdown, mentions, code blocks).
    - `model describe jira fog` – format for Jira markup.
  - Left existing entries for diagrams, Presenterm, ADRs, shell scripts, and debugging unchanged.

### Behaviour impact

- Documentation now consistently reflects that:
  - Channel-specific formatting is requested via styles (`slack`, `jira`) rather than the retired `format` static prompt.
  - These styles are first-class peers of other heavy styles (`diagram`, `presenterm`, `adr`, `shellscript`) in the user-facing cheat sheet.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add brief Slack/Jira examples to other docs (for example, ADR 005/007) if older “format” examples remain.
  - Consider whether a dedicated pattern or helper for “Slack summary” / “Jira ticket” would further streamline common workflows.


## 2025-12-04 – Slice: ensure patterns treat new method tokens as methods

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Make sure model patterns correctly recognise newer method axis tokens (for example, `debugging`, `flow`, `motifs`) when parsing recipes, instead of treating them as untyped tokens.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Extended `METHOD_TOKENS` so `_parse_recipe` treats all current method axis tokens as methods:
    - Added `systems`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `wasinawa` alongside the existing `steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`.
  - This aligns pattern parsing with:
    - The method axis list in `GPT/lists/methodModifier.talon-list`.
    - Quick-help’s fallback method list in `lib/modelHelpGUI.py`.
- Updated `tests/test_model_pattern_gui.py`:
  - Added `test_parse_recipe_handles_new_method_tokens`, which:
    - Locates the `Explain flow` pattern.
    - Parses its recipe (`describe · gist · focus · flow · fog`) via `_parse_recipe`.
    - Asserts that:
      - `static_prompt == "describe"`,
      - `completeness == "gist"`, `scope == "focus"`,
      - `method == "flow"`,
      - `style == ""`,
      - `directional == "fog"`.

### Behaviour impact

- Model patterns that use newer method tokens now:
  - Correctly set the method axis when run (for example, `debugging` for “Debug bug”, `flow` for “Explain flow”).
  - Feed the intended method semantics into `modelPrompt` and `GPTState.last_method`, making quick-help recaps and `model again` behaviour consistent with ADR 012’s design.
- This closes a small gap where recipes using newer methods could have been parsed without a method axis value.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add additional patterns that showcase other method tokens (`systems`, `experimental`, `motifs`, `wasinawa`) now that parsing and axis wiring are in place.


## 2025-12-04 – Slice: add method recipes to README cheat sheet

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Make the newer method axis values (`systems`, `experimental`, `motifs`) more discoverable in the main GPT README by adding concrete recipes alongside diagrams/ADRs/shell scripts.

### Summary of this loop

- Updated `GPT/readme.md` in the “Common axis recipes (cheat sheet)” section:
  - Introduced a “Methods” group with example commands:
    - `model describe systems fog` – systems-thinking sketch of the subject.
    - `model describe experimental fog` – experimental/scientific plan and hypotheses.
    - `model describe flow rog` – explain the flow of code or text step by step.
    - `model describe motifs fog` – scan for recurring motifs and patterns (often with `scope relations`).
  - Kept existing sections for diagrams, presentations, ADRs, shell scripts, debugging, and channel formatting.

### Behaviour impact

- Documentation now highlights method axis values as first-class tools:
  - Users see concrete, speakable examples for `systems`, `experimental`, `flow`, and `motifs` instead of relying solely on ADRs or quick-help.
  - This reinforces the ADR 012 design that method-heavy behaviours should be expressed via `methodModifier` rather than static prompts.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add references to these method recipes in other docs (for example, ADR 005/007/013) when discussing method axes.
  - Introduce additional examples if new method tokens are added.*** End Patch ***!


## 2025-12-04 – Slice: add Slack/Jira formatting patterns

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Provide one-click patterns for Slack- and Jira-formatted output using the `slack`/`jira` styles, so users don’t have to remember the full axis recipes.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Added a `Slack summary` pattern in the writing domain:
    - `description="Summarize this content for Slack."`
    - `recipe="describe · gist · focus · slack · fog"`.
  - Added a `Jira ticket` pattern in the writing domain:
    - `description="Draft a Jira-style ticket description for this issue."`
    - `recipe="describe · full · focus · steps · jira · fog"`.
- Updated `tests/test_model_pattern_gui.py`:
  - Added `test_slack_and_jira_patterns_are_configured`, which:
    - Finds the `Slack summary` and `Jira ticket` patterns in `PATTERNS`.
    - Parses each recipe via `_parse_recipe` and asserts that:
      - Slack summary:
        - `static_prompt == "describe"`, `completeness == "gist"`, `scope == "focus"`,
        - `method == ""`, `style == "slack"`, `directional == "fog"`.
      - Jira ticket:
        - `static_prompt == "describe"`, `completeness == "full"`, `scope == "focus"`,
        - `method == "steps"`, `style == "jira"`, `directional == "fog"`.

### Behaviour impact

- The pattern picker now exposes ready-made Slack/Jira formatting patterns:
  - Users can click or say “Slack summary” or “Jira ticket” instead of remembering the axis combinations or relying on the retired `format` static prompt.
  - Both patterns use `describe` as the semantic prompt and `slack`/`jira` as heavy styles, fully aligned with ADR 012’s axis-first design.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add more channel- or artifact-specific patterns (for example, “Email draft”, “PR review”) that leverage existing styles and methods.
  - Expand tests if Slack/Jira behaviours gain additional constraints or semantics.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add more channel- or artifact-specific patterns (for example, “Email draft”, “PR review”) that leverage existing styles and methods.
  - Expand tests if Slack/Jira behaviours gain additional constraints or semantics.


## 2025-12-04 – Slice: surface systems/experimental methods in quick-help examples

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Make the `systems` and `experimental` method axes more discoverable by adding concrete recipes to the model quick-help examples.

### Summary of this loop

- Updated `lib/modelHelpGUI.py` in `_show_examples`:
  - Added two example recipes that showcase method-heavy behaviours:
    - `Systems sketch: describe · gist · focus · systems · fog`
    - `Experiment plan: describe · full · focus · experimental · fog`
  - Left existing examples for debugging, fix, gist summary, diagram, ADR, Presenterm, and Slack/Jira formatting unchanged.

### Behaviour impact

- When users open the `model` quick-help GUI, they now see:
  - Concrete examples of using `method systems` and `method experimental` alongside `debugging`, reinforcing that these are first-class method modifiers rather than static prompts.
  - Recipes that combine a semantic prompt (`describe`) with method and style axes, aligned with ADR 012’s axis-first approach.
- No runtime behaviour changes; this slice only improves discoverability of the new method tokens.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add similar quick-help examples for other method tokens (for example, `structure`, `compare`, `motifs`, `wasinawa`) once they have common recipes.
  - Consider adding a dedicated pattern for experimental/science workflows if they become frequent.


## 2025-12-04 – Slice: add Motif scan pattern for motifs method

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Provide a concrete pattern that exercises the `motifs` method axis in the way ADR 012/013 describe (relations scope, bullets style), making motif scanning easy to invoke.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Added a `Motif scan` writing pattern:
    - `description="Scan for recurring motifs and patterns."`
    - `recipe="describe · gist · relations · motifs · bullets · fog"`.
  - This mirrors the ADR 012 migration guide’s recommended recipe for the retired `motifs` static prompt.
- Updated `tests/test_model_pattern_gui.py`:
  - Added `test_motif_scan_pattern_uses_motifs_method`, which:
    - Locates the `Motif scan` pattern in `PATTERNS`.
    - Parses its recipe via `_parse_recipe` and asserts:
      - `static_prompt == "describe"`,
      - `completeness == "gist"`,
      - `scope == "relations"`,
      - `method == "motifs"`,
      - `style == "bullets"`,
      - `directional == "fog"`.

### Behaviour impact

- The pattern picker now exposes a dedicated Motif scan workflow:
  - Users can click or say “Motif scan” to run a motif/pattern analysis without remembering the full axis combination.
  - The pattern uses `method motifs` with `scope relations` and `style bullets`, exactly as ADR 012/013 intend for axis-only motifs behaviour.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add similar patterns for other method tokens (for example, `structure`, `compare`, `wasinawa`) if they prove useful as named workflows.
  - Reference the Motif scan pattern explicitly in ADR 013 when discussing motifs as a method-only behaviour.


## 2025-12-04 – Slice: clarify ADR 007 consolidation story after ADR 012/013

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Make ADR 007’s guidance on “keep format-heavy prompts as static prompts” explicitly acknowledge that ADR 012/013 have since moved many of those prompts into axes and patterns in this repo.

### Summary of this loop

- Updated `docs/adr/007-static-prompt-consolidation.md`:
  - In the “Decision” section, refined point 4 from:
    - “Keep domain-heavy and format-heavy prompts as static prompts”
  - To:
    - “Keep domain-heavy and format-/method-heavy prompts as static prompts (then refine via ADR 012/013)”.
  - Added an explicit note that, in this repo:
    - Many format-/method-heavy prompts originally preserved by ADR 007 (`diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `debug`, `structure`, `flow`, `compare`, `motifs`) have now been:
      - Retired as static prompts, and
      - Re-expressed as style/method axis values and patterns by ADR 012 and ADR 013.
    - The remaining static prompts focus on semantic/domain lenses and structured tasks, and new format/method behaviours should usually be added via axes or patterns instead of new static prompts.

### Behaviour impact

- No runtime behaviour changes; this slice only tightens ADR relationships:
  - Readers of ADR 007 now see clearly that its “keep format-heavy prompts” decision has been refined by ADR 012/013 in this repo.
  - This reduces confusion about why prompts like `diagram`/`presenterm`/`debug` no longer appear as static prompts despite ADR 007’s earlier decision.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add a short cross-reference from ADR 012/013 back to this updated ADR 007 section if further consolidation occurs.
  - Use a similar pattern for any other ADRs whose decisions have been refined by the axis-first design.*** End Patch ***!


## 2025-12-04 – Slice: add guardrail test to keep axis-only prompts off staticPrompt list

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Prevent regressions where axis-only behaviours (for example, `diagram`, `presenterm`, `debugging`, `motifs`) accidentally reappear as static prompts in `staticPrompt.talon-list`.

### Summary of this loop

- Updated `tests/test_static_prompt_docs.py`:
  - Added `test_axis_only_tokens_do_not_appear_as_static_prompts`, which:
    - Reads all static prompt keys from `GPT/lists/staticPrompt.talon-list`.
    - Defines two forbidden sets, based on ADR 012’s migration table:
      - Style-only behaviours: `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`.
      - Method-only / axis-shaped behaviours: `debug`, `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`.
    - Asserts that none of these tokens appear as static prompt keys, failing with a clear message if any regression is detected.

### Behaviour impact

- No runtime changes; this slice only strengthens tests:
  - If a future change accidentally reintroduces any of the axis-only tokens as static prompts, the new test will fail, signalling a violation of ADR 012’s “axes for how, prompts for what” rule.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Extend the forbidden sets if additional prompts are moved to axis-only status.
  - Add a complementary guardrail that ensures new axis-only tokens are documented in ADR 012/013 to keep design and tests in sync.


## 2025-12-04 – Slice: document new ADR-012 guardrail tests in ADR 012

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Make ADR 012’s “Tests and guardrails” section explicitly reference the new tests that enforce axis-only tokens and axis-based patterns, so future maintainers can see where those checks live.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Tests and guardrails (this repo)” section:
  - Extended the `tests/test_static_prompt_docs.py` bullet to note that it now:
    - Includes a guardrail ensuring axis-only tokens from ADR 012 (for example, `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `debug`, `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`) never reappear as `staticPrompt` keys.
  - Extended the `tests/test_model_pattern_gui.py` / `tests/test_model_help_gui.py` bullet to mention that they:
    - Cover axis-based patterns for diagrams, ADRs, Presenterm slides, Slack/Jira formatting, and motif scans, and ensure their recipes parse into the expected axis combinations.

### Behaviour impact

- No runtime behaviour changes; this slice only improves traceability:
  - ADR 012 now directly points at the concrete guardrail tests that:
    - Keep axis-only tokens off the static prompt list, and
    - Lock in key axis-based patterns and quick-help examples.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add references to any additional tests introduced for new axis tokens or patterns so ADR 012 remains the central map of guardrails for this design.*** End Patch !***

## 2025-12-04 – Slice: remove stray motifs static prompt profile

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Align configuration with ADR 012/013 by removing the leftover `motifs` static prompt profile so motifs behaviour is represented only via the method/style/scope axes.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `motifs` entry from `STATIC_PROMPT_CONFIG`, which had:
    - A description and default axes (`completeness: gist`, `scope: relations`, `method: steps`, `style: bullets`).
  - This leaves `motifs` as:
    - A **method** axis value in `GPT/lists/methodModifier.talon-list` (`method=motifs`), and
    - An example in ADR 012/013 and README recipes (for example, `describe · gist · relations · motifs · bullets · fog`).
- Confirmed that:
  - `motifs` is already absent from `GPT/lists/staticPrompt.talon-list` (retired as a static prompt).
  - References in ADR 007/012/013 describe `motifs` as an axis-shaped behaviour, not part of the remaining semantic-backbone static prompt set.

### Behaviour impact

- There is no longer a `motifs` static prompt profile:
  - `get_static_prompt_profile("motifs")` now returns `None`, matching the absence of a `motifs` token in `staticPrompt.talon-list`.
  - Any motifs-style analysis must be requested via the method axis (for example, `method motifs`) combined with a semantic static prompt (for example, `describe`) and appropriate scope/style (`relations`, `bullets`), as ADR 012’s migration table suggests.
- This change brings configuration and tests back into alignment:
  - `tests/test_static_prompt_docs.py`’s guardrail (“every profiled prompt key should appear in staticPrompt.talon-list”) is now satisfied for `motifs`, because it is no longer a profiled static prompt.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add an explicit example in ADR 013’s implementation/status notes calling out that motifs is now purely axis-based (method/scope/style) with no static prompt.
  - Consider adding a dedicated “Motif scan” pattern recipe once motifs-style workflows are common enough to warrant a one-click pattern.



## 2025-12-04 – Slice: refresh quick-help examples to use axis-based recipes

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure the `model` quick-help GUI examples reflect the current axis-based recipes and do not reference retired static prompts.

### Summary of this loop

- Updated `lib/modelHelpGUI.py` in `_show_examples`:
  - Changed examples to:
    - `Debug bug: describe · full · narrow · debugging · rog` (instead of using the retired `debug` static prompt).
    - `Fix locally: fix · full · narrow · steps · ong` (unchanged).
    - `Summarize gist: describe · gist · focus · plain · fog` (unchanged).
    - Added:
      - `Sketch diagram: describe · gist · focus · diagram · fog`.
      - `Architecture decision: describe · full · focus · adr · rog`.
  - These examples now showcase:
    - Axis-based debugging behaviour (`method debugging`).
    - Style-based diagram and ADR behaviours (`style diagram` and `style adr`) on top of `describe`.

### Behaviour impact

- No runtime semantics changed; this slice only updates the help UI:
  - Quick-help now presents examples that are consistent with ADR 012’s axis-first design and the current recipes in `lib/modelPatternGUI.py`.
  - Users see `diagram` and `adr` clearly as styles, and `debugging` clearly as a method, instead of as static prompts.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Add more quick-help examples that highlight other styles (`presenterm`, `shellscript`, `gherkin`) and methods (`structure`, `compare`, `motifs`, `wasinawa`).

## 2025-12-04 – Slice: expand quick-help axis fallbacks for method/style

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure the quick-help GUI’s method/style sections show the newer axis tokens even if Talon list files are missing or unavailable.

### Summary of this loop

- Updated `lib/modelHelpGUI.py`:
  - In `_show_method`, expanded the fallback `keys` list (used when `METHOD_ITEMS` is unavailable) to include:
    - `systems`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `wasinawa` alongside the original `steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`.
  - In `_show_style`, expanded the fallback `keys` list (used when `STYLE_ITEMS` is unavailable) to include:
    - `cards`, `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, `taxonomy` alongside the original `plain`, `tight`, `bullets`, `table`, `code`, `checklist`.

### Behaviour impact

- In normal operation (when Talon list files are present), behaviour is unchanged: quick-help still reads actual axis keys/descriptions from the lists.
- In degraded environments where axis lists cannot be loaded:
  - The method/style quick-help sections now show a richer, up-to-date set of axis tokens that matches ADR 012/013, rather than the older minimal lists.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Keep these fallback lists aligned with any further additions to `methodModifier` or `styleModifier` over time.

## 2025-12-04 – Slice: link ADR 012/013 from GPT README

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make it easy for users to discover ADR 012/013 from the GPT README when learning about axes and recipes.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Extended the ADR list in the “Help” section to include:
    - `docs/adr/012-style-and-method-prompt-refactor.md`
    - `docs/adr/013-static-prompt-axis-refinement-and-streamlining.md`
  - These are listed alongside ADR 005, 006, and 009 under “For implementation details of the modifier axes, defaults, helpers, and rerun shorthand…”.

### Behaviour impact

- No runtime changes; this slice only updates documentation:
  - Users browsing the README now have direct pointers to ADR 012 and ADR 013, which describe the style/method refactor and static prompt streamlining implemented in this repo.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Keep this ADR list in sync if new, closely related ADRs are added.


## 2025-12-04 – Slice: extend Practical usage tips with new patterns

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Keep ADR 012’s “Practical usage tips” aligned with the current axis-based patterns, by mentioning the newer Slack/Jira, Presenterm, and Motif scan patterns alongside the original diagram/ADR patterns.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Practical usage tips” section:
  - Extended the “Use patterns for common bundles” bullet list to include:
    - `Present slides` (`describe · full · focus · presenterm · rog`).
    - `Slack summary` / `Jira ticket` (`describe · gist · focus · slack · fog` / `describe · full · focus · steps · jira · fog`).
    - `Motif scan` (`describe · gist · relations · motifs · bullets · fog`).
  - Kept the existing examples for “Sketch diagram” and “Architecture decision”.

### Behaviour impact

- No runtime changes; this slice only updates documentation:
  - ADR 012’s practical guidance now matches the patterns currently implemented in `lib/modelPatternGUI.py`, making it easier for readers to see concrete examples of how axis-based recipes are surfaced as patterns.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add references to any additional patterns introduced later (for example, future method- or style-heavy workflows) so this section remains a concise pattern catalog.*** End Patch ***!


## 2025-12-04 – Slice: widen “when in doubt” examples to include method axes

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make ADR 012’s “When in doubt” guidance reflect that methods (not just styles) are first-class axes to reach for when composing recipes.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Practical usage tips” section:
  - Adjusted the final bullet under “When in doubt” from listing only:
    - `structure`, `flow`, `diagram`, `adr`
  - To also include representative method axis values:
    - `structure`, `flow`, `diagram`, `adr`, `systems`, `debugging`, `motifs`
  - This aligns the quick mental model with the axis vocabulary described earlier in ADR 012/013 and surfaced in quick-help and README examples.

### Behaviour impact

- No runtime changes; this slice only clarifies documentation:
  - Readers are nudged to think of methods (`systems`, `debugging`, `motifs`) as natural axes to add, alongside styles like `diagram` or `adr`, when adjusting behaviour from a `model describe fog` starting point.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Refine or expand the example axis list if new high-value method or style tokens are added.


## 2025-12-04 – Slice: sketch future axis recipes for system/experiment/science

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make ADR 012’s “Future work” section more concrete by spelling out axis-based recipe equivalents for `system`, `experiment`, and `science` if they are ever fully retired as static prompts.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Future work related to this ADR in this repo” section:
  - Expanded the bullet about possibly retiring `system`, `experiment`, and `science` as static prompts to include representative axis-first replacements:
    - `model system systems fog` → `model describe systemic fog` (or `model describe systemic diagram fog` for systems diagrams).
    - `model experiment` / `model science` → `model describe experimental fog` (or `model describe experimental rog` for more exhaustive plans and hypotheses).

### Behaviour impact

- No runtime behaviour changes; this slice only clarifies documentation:
  - If a future loop decides to retire `system`/`experiment`/`science` as static prompts, ADR 012 now already contains concrete, axis-based replacement recipes consistent with the existing method axis (`systemic`, `experimental`).

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Decide whether to actually perform this retirement for this repo, then:
    - Remove the static prompt entries from `staticPrompt.talon-list`,
    - Update any patterns or references that still rely on `model system` / `model experiment` / `model science`, and
    - Reconfirm tests and docs against the axis-only recipes sketched here.


## 2025-12-04 – Slice: point ADR 012 practical tips at README axis cheat sheet

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Link ADR 012’s “Practical usage tips” to the README’s “Common axis recipes (cheat sheet)” so readers can jump from the ADR to concrete, speakable examples.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Practical usage tips” section:
  - Under “When in doubt”, added a bullet that explicitly points to:
    - The “Common axis recipes (cheat sheet)” section in `GPT/readme.md` for more examples of concrete, speakable recipes (for diagrams, ADRs, shell scripts, debugging, methods, and channel formatting).

### Behaviour impact

- No runtime behaviour changes; this slice only improves navigation:
  - Readers of ADR 012 who want concrete command examples are guided directly to the README cheat sheet that already encodes ADR 012’s axis-based recipes.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Keep this pointer valid if the README moves or the cheat sheet section is renamed.*** End Patch ***!


## 2025-12-04 – Slice: teach static prompt docs about axis-only behaviours

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure the static-prompt docs block built by `GPT/gpt.py` explicitly mentions that some behaviours are axis-only (styles/methods) and points readers at ADR 012/013 and the README cheat sheet.

### Summary of this loop

- Updated `GPT/gpt.py` in `_build_static_prompt_docs`:
  - Prefixed the generated docs with a short note:
    - Explaining that certain behaviours (for example, diagrams, Presenterm decks, ADRs, shell scripts, debugging) now live only as style/method axis values instead of static prompts.
    - Pointing readers to ADR 012/013 and the README “Common axis recipes (cheat sheet)” section for concrete axis-based recipes.
  - Left the existing behaviour of listing profiled prompts and “Other static prompts (tokens only…)” unchanged.

### Behaviour impact

- No changes to prompt routing or axes; this slice only affects descriptive docs:
  - Any UI or helper that shows `_build_static_prompt_docs()` output now makes it clearer why some familiar behaviours are not present as static prompts and where to find their axis-based equivalents.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Adjust the note’s wording if the set of axis-only behaviours or the location of the cheat sheet changes.*** End Patch ***!


## 2025-12-04 – Slice: add taxonomy to axis-only style behaviours summary

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure ADR 012’s axis-only style summary reflects that `taxonomy` is now a style-only behaviour used for type/taxonomy outputs.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Axis-only prompt summary” section:
  - Added a bullet under “Style-only behaviours” for:
    - `taxonomy` – type/taxonomy-style outputs (categories, subtypes, relationships).
  - This matches:
    - The `taxonomy` style definition in `GPT/lists/styleModifier.talon-list`.
    - ADR 013’s description of `taxonomy` as the style counterpart to the retired `type` static prompt.

### Behaviour impact

- No runtime changes; this slice only tightens documentation:
  - Readers now see `taxonomy` explicitly listed alongside other axis-only style behaviours (`diagram`, `presenterm`, `adr`, etc.), keeping ADR 012’s summary in sync with the implemented style axis.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add a brief example recipe for taxonomy in ADR 013 or the README if type/taxonomy workflows become more common.*** End Patch ***!


## 2025-12-04 – Slice: add test asserting static prompt docs mention axis-only behaviours

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Guard the new axis-only behaviour note in static prompt docs so future changes don’t silently remove it.

### Summary of this loop

- Updated `tests/test_static_prompt_docs.py`:
  - Added `test_static_prompt_docs_note_axis_only_behaviours`, which:
    - Calls `_build_static_prompt_docs()`.
    - Asserts that the returned docs include the introductory note:
      - “Some behaviours (for example, diagrams, Presenterm decks, ADRs, shell scripts, debugging) now live only as style/method axis values…”

### Behaviour impact

- No runtime changes; this slice only strengthens tests:
  - If a future edit accidentally removes or rewrites the axis-only behaviours note from `_build_static_prompt_docs`, this test will fail, nudging maintainers to either restore the note or update ADR 012 and the test together.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Broaden the assertion if the note’s wording evolves (for example, by checking only for a smaller, stable substring or a structured prefix).*** End Patch ***!


## 2025-12-04 – Slice: relax axis-only note assertion to a stable substring

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the static-prompt docs axis-only note test less brittle by asserting on a stable substring instead of the full sentence.

### Summary of this loop

- Updated `tests/test_static_prompt_docs.py` in `test_static_prompt_docs_note_axis_only_behaviours`:
  - Changed the assertion from checking the entire sentence:
    - `"Some behaviours (for example, diagrams, Presenterm decks, ADRs, shell scripts, debugging) now live only as style/method axis values"`
  - To checking a stable core substring:
    - `"live only as style/method axis values"`.

### Behaviour impact

- No runtime changes; this slice only relaxes a test:
  - Minor wording changes to the axis-only note in `_build_static_prompt_docs` are less likely to break the test, as long as the core message (“live only as style/method axis values”) remains present.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Further adjust this assertion if the note structure changes significantly, but the current form should be robust to typical copy edits.*** End Patch ***!


## 2025-12-04 – Slice: add test asserting axis docs mention ADRs and README cheat sheet

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Guard the new axis-docs note (which points readers at ADRs 005/012/013 and the README cheat sheet) so future edits don’t silently remove it.

### Summary of this loop

- Updated `tests/test_static_prompt_docs.py`:
  - Added `test_axis_docs_note_adrs_and_readme_cheat_sheet`, which:
    - Calls `_build_axis_docs()`.
    - Asserts that the returned docs include the phrase:
      - `"see ADR 005/012/013 and the GPT README axis cheat sheet"`.
  - This locks in the note we added earlier in `GPT/gpt.py` to explain where full axis semantics and examples live.

### Behaviour impact

- No runtime behaviour changes; this slice only strengthens tests:
  - If a future change removes or significantly rewrites the axis-docs note, this test will fail, prompting maintainers to either restore the guidance or update ADR 012 and tests in tandem.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Relax this assertion to a shorter, stable substring if the exact wording of the note evolves.*** End Patch ***!


## 2025-12-04 – Slice: relax axis-docs ADR/README note assertion to a stable substring

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the axis-docs ADR/README note test less brittle by asserting on the ADR identifier substring instead of the full phrase.

### Summary of this loop

- Updated `tests/test_static_prompt_docs.py` in `test_axis_docs_note_adrs_and_readme_cheat_sheet`:
  - Changed the assertion from checking the full phrase:
    - `"see ADR 005/012/013 and the GPT README axis cheat sheet"`
  - To checking the stable substring:
    - `"ADR 005/012/013"`.

### Behaviour impact

- No runtime changes; this slice only relaxes a test:
  - Minor wording changes to the axis-docs note in `_build_axis_docs` are less likely to break the test, as long as the reference to ADR 005/012/013 remains.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Adjust this assertion if additional ADRs are added to the reference list.*** End Patch ***!


## 2025-12-04 – Slice: extend axis-only static prompt guardrail to cover taxonomy style

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Keep the axis-only static prompt guardrail in sync with ADR 012’s axis-only style summary by including `taxonomy` as a style that must not appear as a static prompt.

### Summary of this loop

- Updated `tests/test_static_prompt_docs.py` in `test_axis_only_tokens_do_not_appear_as_static_prompts`:
  - Added `"taxonomy"` to the `style_only` set of forbidden static-prompt keys.
  - This matches ADR 012’s “Axis-only prompt summary”, which lists `taxonomy` as a style-only behaviour for type/taxonomy outputs.

### Behaviour impact

- No runtime changes; this slice only tightens tests:
  - If a future change accidentally introduces a `taxonomy` static prompt, this guardrail test will now fail, preserving the “axis-only” status promised in ADR 012/013.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Adjust the forbidden sets if additional styles/methods are explicitly designated as axis-only in ADRs.*** End Patch ***!


## 2025-12-04 – Slice: reflect taxonomy guardrail and axis-only note in ADR 012 tests section

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Keep ADR 012’s “Tests and guardrails” section in sync with the latest guardrails added around taxonomy and static-prompt docs.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Tests and guardrails (this repo)” section:
  - Expanded the `tests/test_static_prompt_docs.py` bullet so it now states that:
    - Axis-only tokens from ADR 012 (including `taxonomy`) must not reappear as `staticPrompt` keys.
    - Static-prompt docs include a note explaining that some behaviours are axis-only and point to ADR 012/013 and the README cheat sheet.

### Behaviour impact

- No runtime changes; this slice only updates ADR text:
  - ADR 012’s tests/guardrails description now reflects the current test suite’s expectations for both axis-only tokens and the static-prompt docs note.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update this description if new axis-only tokens or doc-guardrail tests are introduced.*** End Patch ***!


## 2025-12-04 – Slice: teach axis docs about ADRs and the README cheat sheet

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the axis docs block built by `GPT/gpt.py` explicitly point readers at ADRs 005/012/013 and the README cheat sheet for axis semantics and examples.

### Summary of this loop

- Updated `GPT/gpt.py` in `_build_axis_docs`:
  - Prefixed the generated axis docs with a short note explaining that:
    - Axes capture “how and in what shape” (completeness, scope, method, style, directional lens), and
    - Full semantics and examples live in ADR 005/012/013 and the GPT README axis cheat sheet.
  - Left the existing per-axis key/description listing behaviour unchanged.

### Behaviour impact

- No runtime behaviour changes; this slice only affects descriptive axis docs:
  - Any UI or helper that displays `_build_axis_docs()` output now gives readers an immediate pointer to the deeper design docs and concrete examples for axis combinations.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update the reference list if new ADRs or docs become the canonical home for axis semantics.*** End Patch ***!


## 2025-12-04 – Slice: add taxonomy recipe to README cheat sheet

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the `taxonomy` style discoverable in the main README cheat sheet with a concrete, speakable recipe for type/taxonomy outputs.

### Summary of this loop

- Updated `GPT/readme.md` in the “Common axis recipes (cheat sheet)” section:
  - Added a “Types / taxonomy” group with:
    - `model describe taxonomy rog` – express a type/taxonomy (categories, subtypes, and relationships).
  - Left existing groups (diagrams, presentations, ADRs, shell scripts, debugging, methods, channel formatting) unchanged.

### Behaviour impact

- No runtime behaviour changes; this slice only improves documentation:
  - Users can now see an explicit example of using the `taxonomy` style for type/taxonomy outputs, aligned with ADR 012/013’s mapping from the retired `type` static prompt to the `taxonomy` style.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add more examples in ADR 013 or other docs if taxonomy-based workflows become more common.*** End Patch ***!


## 2025-12-04 – Slice: surface taxonomy style in quick-help examples

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the `taxonomy` style visible in the quick-help examples alongside diagrams, ADRs, Presenterm, Slack/Jira, and method recipes.

### Summary of this loop

- Updated `lib/modelHelpGUI.py` in `_show_examples`:
  - Added a taxonomy example:
    - `Type/taxonomy: describe · full · focus · taxonomy · rog`
  - Left existing examples for debugging, fix/gist summary, diagram, ADR, Presenterm, Slack/Jira, systems, and experimental unchanged.

### Behaviour impact

- No runtime behaviour changes; this slice only updates the quick-help UI:
  - When users open `model quick help`, they now see a concrete example of how to invoke type/taxonomy-style output via the `taxonomy` style axis.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add a dedicated pattern for taxonomy-heavy workflows if they become common (for example, a “Type/taxonomy outline” pattern).*** End Patch !***  ```


## 2025-12-04 – Slice: align CONTRIBUTING guidance with ADR 012 axis-only rules and tests

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the contributor guidelines explicitly reflect ADR 012/013’s axis-first design, axis-only tokens, and the key guardrail tests that should be updated when prompts/axes change.

### Summary of this loop

- Updated `CONTRIBUTING.md` in the “GPT prompts, axes, and ADRs” section:
  - Added two bullets to the design rules:
    - A reminder not to reintroduce axis-only behaviours (for example, `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `debug`, `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`) as static prompts; these should remain on the style/method axes with patterns/recipes.
    - A note that when changing prompts or axes, contributors should run/update the guardrail tests described in ADR 012:
      - `tests/test_axis_mapping.py`, `tests/test_static_prompt_docs.py`,
      - `tests/test_model_pattern_gui.py`, `tests/test_model_help_gui.py`.

### Behaviour impact

- No runtime changes; this slice only updates contributor documentation:
  - New contributors are now explicitly guided to:
    - Treat axis-only behaviours as style/method values, not static prompts.
    - Keep tests in sync with axis/static prompt changes, reinforcing ADR 012’s guardrails.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add more specific examples or a short checklist if the prompt/axis surface evolves further.*** End Patch ***!


## 2025-12-04 – Slice: add taxonomy to CONTRIBUTING’s axis-only examples

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Keep `CONTRIBUTING.md`’s axis-only behaviour examples in sync with ADR 012/013 and the guardrail tests by including `taxonomy` alongside other axis-only styles/methods.

### Summary of this loop

- Updated `CONTRIBUTING.md` in the “GPT prompts, axes, and ADRs” section:
  - Extended the “Do not reintroduce axis-only behaviours” example list to include `taxonomy`, matching:
    - ADR 012’s axis-only style summary, and
    - The forbidden set in `tests/test_static_prompt_docs.py:test_axis_only_tokens_do_not_appear_as_static_prompts`.

### Behaviour impact

- No runtime changes; this slice only updates contributor docs:
  - Contributors now see `taxonomy` explicitly called out as an axis-only behaviour that should remain on the style axis rather than being re-added as a static prompt.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update this example list again if additional axis-only styles or methods are introduced.*** End Patch ***!


## 2025-12-04 – Slice: set ADR 012 Date metadata to the concrete applied date

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Replace the placeholder `2025-12-XX` date in ADR 012 with the concrete date when the ADR was effectively applied in this repo.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` header:
  - Changed:
    - `- Date: 2025-12-XX`
  - To:
    - `- Date: 2025-12-04`
  - This matches the dates used throughout the ADR 012 work-log slices for this repository.

### Behaviour impact

- No runtime changes; this slice only cleans up ADR metadata:
  - Readers now see a concrete acceptance date for ADR 012 instead of a placeholder.

### Notes and follow-ups

- Future ADR 012/013 slices are unlikely to need further date changes unless the ADR is revised significantly.*** End Patch ***!


## 2025-12-04 – Slice: add ADR 013 to ADR 012 Related ADRs list

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make ADR 012’s header explicitly reference ADR 013, which refines static prompt/axis boundaries and builds on this ADR’s decisions.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` header:
  - Extended the “Related ADRs” list to include:
    - `013 – Static Prompt Axis Refinement and Streamlining`
  - So ADR 012 now points directly to ADR 013 alongside ADR 005, 007, 008, and 009.

### Behaviour impact

- No runtime changes; this slice only improves ADR linkage:
  - Readers landing on ADR 012 can more easily discover ADR 013, which documents the follow-on refinement and streamlining of static prompts vs. axes.

### Notes and follow-ups

- Future ADRs building on this design may also need to be added to this Related ADRs list.*** End Patch ***!


## 2025-12-04 – Slice: keep ADR 012 user Summary styles in sync with axis vocab

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure the user-facing Summary in ADR 012 lists the same key style tokens (including Slack/Jira/taxonomy) that the style axis actually exposes.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Summary (for users)” section:
  - Extended the “Styles like …” bullet so it now includes:
    - `slack`, `jira`, and `taxonomy` alongside `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `recipe`, `abstractvisual`, `commit`, `adr`, `code`.
  - This brings the quick user-facing list into line with:
    - The style axis summary later in ADR 012, and
    - The README cheat sheet and method/style lists in `GPT/lists/styleModifier.talon-list`.

### Behaviour impact

- No runtime behaviour changes; this slice only updates ADR text:
  - Users reading the Summary now see channel-specific (`slack`, `jira`) and taxonomy (`taxonomy`) styles called out explicitly as first-class style values, instead of having to infer them from later sections.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Adjust this summary if new high-value styles are added or if some are deemphasised.*** End Patch ***!


## 2025-12-04 – Slice: add taxonomy-style tip to ADR 012 Practical usage tips

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make ADR 012’s practical guidance explicitly mention how to ask for type/taxonomy-style outputs using the `taxonomy` style.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Practical usage tips” section:
  - Under “Use patterns for common bundles”, added a bullet:
    - “Use taxonomy-style recipes (for example, `describe · full · focus · taxonomy · rog`) when you need type/taxonomy outputs (categories, subtypes, relationships).”
  - This complements the existing bullets for diagram/ADR/Presenterm/Slack/Jira/Motif scan patterns and aligns with:
    - The `taxonomy` style definition in `GPT/lists/styleModifier.talon-list`.
    - The taxonomy examples in ADR 013 and the README cheat sheet.

### Behaviour impact

- No runtime changes; this slice only updates documentation:
  - ADR 012 now gives a concrete, axis-based taxonomy example alongside other common recipes, making it easier for users to see how to request type/taxonomy outputs.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add a dedicated taxonomy pattern if type/taxonomy workflows become common enough to warrant a named pattern.*** End Patch ***!


## 2025-12-04 – Slice: add CONTRIBUTING pointer to ADR 012 tests/guardrails section

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make it easy for contributors reading ADR 012 to discover the higher-level contributor guidance and guardrail checklist in `CONTRIBUTING.md`.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Tests and guardrails (this repo)” section:
  - Added a bullet pointing to:
    - The “GPT prompts, axes, and ADRs” section in `CONTRIBUTING.md` for contributor-focused rules and a checklist of guardrail tests to run when changing prompts/axes.

### Behaviour impact

- No runtime changes; this slice only improves documentation linkage:
  - Contributors can move from ADR 012’s conceptual tests/guardrails overview straight to the concrete contributor rules and test checklist in `CONTRIBUTING.md`.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update this pointer if the CONTRIBUTING section name or structure changes.*** End Patch ***!


## 2025-12-04 – Slice: add contributor pointer to ADR 012 user Summary

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Give contributors reading the user-facing Summary an immediate pointer to contributor-specific guidance and guardrail tests.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Summary (for users)” section:
  - Added a short “For contributors” line pointing to:
    - The “GPT prompts, axes, and ADRs” section in `CONTRIBUTING.md` for concrete design rules and required guardrail tests when changing prompts/axes.

### Behaviour impact

- No runtime changes; this slice only improves documentation:
  - Contributors landing on ADR 012’s Summary can jump straight to the contributor rules without needing to hunt through the repo.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update this pointer if contributor guidance moves or is renamed.*** End Patch ***!


## 2025-12-04 – Slice: mention named patterns in ADR 012 user Summary

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Let readers of ADR 012’s Summary know that common axis combinations are also available as named patterns in the model pattern GUI.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Summary (for users)” section:
  - Added a line noting that many axis combinations have corresponding named patterns in the model pattern GUI, such as:
    - “Sketch diagram”, “Architecture decision”, “Present slides”, “Slack summary”, “Jira ticket”, “Motif scan”.
  - This ties the conceptual axis-based summary to the concrete patterns users can click or invoke by voice.

### Behaviour impact

- No runtime changes; this slice only improves discoverability:
  - Users reading the Summary can immediately connect axis-based behaviours to the pattern picker they use in day-to-day work.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update the list of example pattern names if the pattern set evolves.*** End Patch ***!


## 2025-12-04 – Slice: mention structure/flow/compare/type/relation/motifs axis migration in ADR 012 Summary

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the user-facing Summary explicitly acknowledge that structure/flow/compare/type/relation/clusters/motifs behaviours are now axis-based, not just listed later in the migration guide.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Summary (for users)” section:
  - Added a bullet under “Common behaviours that used to be static prompts now look like:” noting that:
    - Structural/relational prompts such as `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, and `motifs` are now expressed via method/scope/style axes, with representative recipes in the migration guide.

### Behaviour impact

- No runtime changes; this slice only clarifies documentation:
  - Users scanning the Summary now see that not only format-heavy prompts but also structure/flow/compare/motifs-style prompts have moved into the axis system, with details available in the migration table below.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Refine this wording if more structural/relational prompts are added or consolidated.*** End Patch ***!


## 2025-12-04 – Slice: reference pattern/quick-help commands in ADR 012 Practical usage tips

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Tie ADR 012’s practical tips more directly to the pattern/quick-help commands from ADR 006 so users know how to discover and run axis-based bundles.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Practical usage tips” section:
  - Under “Use patterns for common bundles”, added a bullet describing how to discover and run these bundles:
    - `model patterns` / `model coding patterns` / `model writing patterns` (pattern GUI; ADR 006).
    - `model quick help` / `model show grammar` to inspect axis combinations and get speakable recipes.

### Behaviour impact

- No runtime changes; this slice only improves documentation:
  - Users reading ADR 012 see exactly which commands surface the named patterns and grammar help that embody the axis-first design.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update this list if additional pattern/quick-help commands are introduced or renamed.*** End Patch ***!


## 2025-12-04 – Slice: expand Status snapshot pattern list to match current patterns

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Keep the “Status snapshot vs Implementation Sketch” section in ADR 012 aligned with the actual axis-based patterns implemented in `lib/modelPatternGUI.py`.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Status snapshot vs Implementation Sketch” section:
  - Expanded the Step 4 bullet to mention all key axis-based patterns currently present in `lib/modelPatternGUI.py`:
    - “Sketch diagram”, “Architecture decision”, “Present slides”, “Slack summary”, “Jira ticket”, and “Motif scan”.

### Behaviour impact

- No runtime changes; this slice only updates ADR text:
  - Readers checking ADR 012’s status snapshot now see an accurate list of representative patterns that embody the axis-based design.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update this list if additional high-value patterns are added or renamed.*** End Patch !*** ```


## 2025-12-04 – Slice: add explicit completion note to ADR 012 Status snapshot

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make it unambiguous in ADR 012 that the core implementation steps are complete in this repo and that remaining work is maintenance-focused.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Status snapshot vs Implementation Sketch” section:
  - Added a one-line summary stating that:
    - All of ADR 012’s implementation steps are complete in this repo.
    - Remaining work under this ADR is primarily maintenance, documentation, and occasional new patterns/examples built on the existing axes.
  - This line precedes the per-step mapping that follows.

### Behaviour impact

- No runtime changes; this slice only clarifies ADR status:
  - Readers can immediately see that ADR 012 is fully applied here and that future loops are about refinement rather than core implementation.

### Notes and follow-ups

- Future ADRs that reach a similar “implementation complete” state may want a comparable status note in their own Status snapshot sections.*** End Patch ***!


## 2025-12-04 – Slice: add axis token naming guidance to ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Capture the spoken-token naming constraints (single, pronounceable words; no hyphens) in ADR 012’s design rules so future axis values remain easy to speak.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Design rule for new behaviours” section:
  - Added a bullet under “When adding new GPT behaviours in this repo”:
    - “Name axis tokens for speech: use short, single, pronounceable words without hyphens (for example, `shellscript` instead of `shell-script`); avoid punctuation or multi-word phrases in axis keys so they remain easy to speak and remember.”
  - This encodes the repository’s preference for hyphen-free, pronounceable axis tokens that work well as spoken commands.

### Behaviour impact

- No runtime changes; this slice only updates design guidance:
  - Future axis tokens are more likely to follow the existing pattern (`diagram`, `presenterm`, `shellscript`, `taxonomy`, etc.) and remain easy to use in Talon voice grammars.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Reference this naming rule from CONTRIBUTING if axis vocabularies expand further.*** End Patch ***!


## 2025-12-04 – Slice: add pattern-exposure guidance to ADR 012 design rules

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Encourage contributors to expose frequently used axis combinations as named patterns in the pattern GUI, not only as bare grammar recipes.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Design rule for new behaviours” section:
  - Added a bullet under “When adding new GPT behaviours in this repo”:
    - “Expose high-value recipes as patterns: for axis combinations you expect to use frequently, add or update named patterns in `lib/modelPatternGUI.py` (see ADR 006) so users can access them via the pattern GUI as well as by speaking the full grammar.”

### Behaviour impact

- No runtime changes; this slice only refines design guidance:
  - New axis combinations that turn out to be common are more likely to be wrapped in discoverable patterns, consistent with ADR 006’s pattern picker design.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add concrete examples of new patterns if additional axis combinations are standardised.*** End Patch !***  ````


## 2025-12-04 – Slice: mention pattern/quick-help surfaces in ADR 012 design rules

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make ADR 012’s “keep docs and tests in sync” guidance explicitly call out the pattern and quick-help UIs that should be updated when axis vocabularies change.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Design rule for new behaviours” section:
  - Refined the “Keep docs and tests in sync” bullet to say that, for new axis/static-prompt combinations, contributors should:
    - Update axis lists.
    - Ensure patterns/help surfaces show at least one example, explicitly mentioning:
      - `lib/modelPatternGUI.py` (pattern GUI).
      - Quick-help fallbacks in `lib/modelHelpGUI.py`.
    - Keep relevant tests up to date.

### Behaviour impact

- No runtime changes; this slice only clarifies design guidance:
  - Contributors are less likely to update axis lists without also updating the pattern picker and quick-help UIs that surface those axes to users.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Add more concrete checklists if additional UIs are introduced.*** End Patch ***!


## 2025-12-04 – Slice: add explicit work-log pointer to ADR 012 header

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make it obvious from ADR 012 where the in-repo implementation slices for this ADR are recorded.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` header:
  - Added a “Work-log” entry under “Related ADRs” pointing at:
    - `docs/adr/012-style-and-method-prompt-refactor.work-log.md`
  - This complements the separate work-log file and makes it easier for readers to jump from the ADR to the concrete slices.

### Behaviour impact

- No runtime changes; this slice only improves discoverability:
  - Readers no longer have to guess or search for the work-log path; it is listed directly in the ADR header.

### Notes and follow-ups

- Future ADRs that use work-logs may want to adopt a similar “Work-log: …” convention in their headers.*** End Patch ***!


## 2025-12-04 – Slice: correct ADR 006/008 names in ADR 012 Related ADRs

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Fix the Related ADRs header so the ADR numbers and titles match the actual ADR files in this repo.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` header:
  - Added ADR 006 explicitly:
    - `006 – Pattern Picker and Recap`
  - Corrected the ADR 008 label from:
    - “008 – Pattern Picker and Recap”
  - To:
    - “008 – Prompt Recipe Suggestion Assistant”
  - The Related ADRs list now reads 005, 006, 007, 008, 009, 013, plus the work-log pointer.

### Behaviour impact

- No runtime changes; this slice only fixes metadata:
  - Readers now see accurate ADR titles for 006 and 008 linked from ADR 012.

### Notes and follow-ups

- No further changes needed unless new ADRs become closely related to ADR 012.*** End Patch ***!


## 2025-12-04 – Slice: briefly describe ADR 006/008 roles in ADR 012 Context

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Clarify in ADR 012’s Context how ADR 006 and ADR 008 relate to the axis-first grammar this ADR builds on.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Context” section:
  - After the ADR 007 paragraph, added a short note summarising that:
    - ADR 006 introduces the pattern picker and quick-help UIs for axis-based recipes.
    - ADR 008 adds a prompt recipe suggestion assistant that proposes concrete `staticPrompt · completeness · scope · method · style · directional` combinations.
  - This explains why ADR 012 can assume patterns and suggestion helpers already exist when it talks about axes + patterns.

### Behaviour impact

- No runtime changes; this slice only refines ADR cross-references:
  - Readers now see at a glance how ADR 006 and ADR 008 sit alongside ADR 005/007/012/013 in the overall prompt/axis design.

### Notes and follow-ups

- No further action needed unless ADR 006/008 are substantially revised.*** End Patch ***!


## 2025-12-04 – Slice: note how ADR 012/013 address ADR 005 per-prompt profile TODOs

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Capture in ADR 012’s main text that some of ADR 005’s “Still TODO” ideas around per-prompt profiles have been refined/superseded by ADR 012/013.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Context” section:
  - Added a short note explaining that:
    - ADR 005’s earlier “Still TODO” ideas about per-prompt completeness/scope/method/style profiles for format-heavy prompts are now largely handled by:
      - Richer style/method axis values introduced by ADR 012/013.
      - Remaining semantic prompt profiles in `lib/staticPromptConfig.py`.

### Behaviour impact

- No runtime changes; this slice only clarifies ADR relationships:
  - Readers can see how ADR 012/013 carry forward and refine some of ADR 005’s original per-prompt profile intentions, rather than leaving them as open TODOs.

### Notes and follow-ups

- No further follow-up expected unless ADR 005 is revised again.*** End Patch !***  ````


## 2025-12-04 – Slice: add implementation touchpoints list to ADR 012 Context

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Help maintainers quickly find the core files that implement ADR 012’s decisions in this repo.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Context” section:
  - Added an “Implementation touchpoints (this repo)” list that calls out:
    - `lib/talonSettings.py` for `modelPrompt` composition.
    - `lib/staticPromptConfig.py` for semantic static prompt profiles and default axes.
    - `GPT/lists/*.talon-list` for static prompts and axis vocabularies.
    - `lib/modelPatternGUI.py` for pattern picker recipes.
    - `lib/modelHelpGUI.py` for quick-help axis summaries and examples.
    - `GPT/gpt.py` for axis/static-prompt docs and GPT wiring.

### Behaviour impact

- No runtime changes; this slice only improves documentation:
  - Readers of ADR 012 can jump directly from the design to the most relevant implementation files in this repo.

### Notes and follow-ups

- No further follow-ups expected unless these implementation files move or are significantly refactored.*** End Patch ***!


## 2025-12-04 – Slice: reference ADR 008 suggestion helper in ADR 012 Practical usage tips

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make ADR 008’s suggestion helper visible from ADR 012’s practical tips so users know how to get axis-based recipes when unsure which modifiers to choose.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Practical usage tips” section:
  - Added a small “Use suggestion helpers” bullet noting that:
    - `model suggest` / `model suggest for <subject>` (ADR 008) can propose concrete `staticPrompt · completeness · scope · method · style · directional` recipes for the current context, which users can then run or adapt.

### Behaviour impact

- No runtime changes; this slice only enriches documentation:
  - Users reading ADR 012 now see `model suggest` as one of the tools for discovering axis-based recipes, alongside patterns and quick-help.

### Notes and follow-ups

- No additional follow-ups expected unless ADR 008’s commands or behaviour change.*** End Patch !***  ```json


## 2025-12-04 – Slice: mention ADR 009 'model again' iteration in ADR 012 Practical usage tips

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Help users iterate on successful axis combinations by pointing them at ADR 009’s `model again` shorthand from within ADR 012’s practical tips.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Practical usage tips” section:
  - Added a bullet under “When in doubt” explaining that:
    - You can use `model again` / `model again [<staticPrompt>] [axis tokens…]` (ADR 009) to rerun and tweak the last recipe instead of re-speaking the full combination.

### Behaviour impact

- No runtime changes; this slice only improves cross-ADR discoverability:
  - Readers see how ADR 012’s axis grammar and ADR 009’s rerun shorthand work together when iterating on a good recipe.

### Notes and follow-ups

- No further changes needed unless ADR 009’s commands or semantics change.*** End Patch ***!


## 2025-12-04 – Slice: point future axis/static-prompt refinements at ADR 013

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Clarify that new axis/static-prompt refinement decisions should primarily be recorded in ADR 013, keeping ADR 012 focused on the style/method refactor already applied.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Future work related to this ADR in this repo” section:
  - Added a bullet noting that:
    - Further static-prompt/axis refinements beyond what is already implemented here should be treated as ADR 013 work, with ADR 012 remaining the record of the style/method refactor.

### Behaviour impact

- No runtime changes; this slice only clarifies ADR responsibilities:
  - Future contributors are directed to ADR 013 when considering new axis/static-prompt reshuffles, reducing the risk of splitting similar decisions across both ADRs.

### Notes and follow-ups

- No further follow-up expected unless ADR 013’s scope changes.*** End Patch ***!


## 2025-12-04 – Slice: add explicit work-log reference in ADR 012 Status snapshot

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make it easier for readers of ADR 012’s Status snapshot to discover the detailed work-log for this ADR.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Status snapshot vs Implementation Sketch” section:
  - Added a sentence pointing readers to:
    - `docs/adr/012-style-and-method-prompt-refactor.work-log.md` as the dated, slice-by-slice record of how ADR 012 was applied in this repo.

### Behaviour impact

- No runtime changes; this slice only improves navigation:
  - Readers who land on the Status snapshot can quickly jump to the work-log without having to hunt for it.

### Notes and follow-ups

- No additional follow-ups expected; the existing Work-log entry in the header and this Status pointer should be sufficient.*** End Patch ***!


## 2025-12-04 – Slice: mention staticPrompt.talon-list location in ADR 012 Context

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make it clear in ADR 012 where the static prompt tokens are actually defined in this repo.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Context” section:
  - After listing the format/transform-heavy prompts ADR 007 originally preserved, added a short note that:
    - The current static prompt tokens live in `GPT/lists/staticPrompt.talon-list`.

### Behaviour impact

- No runtime changes; this slice only improves discoverability:
  - Readers of ADR 012 now know exactly which file defines the static prompt list referenced throughout the ADR.

### Notes and follow-ups

- No additional follow-ups expected unless the static prompt list file moves.*** End Patch ***!


## 2025-12-04 – Slice: align README ADR list with ADR 012/013 references

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Keep the GPT README’s ADR list in sync with the ADRs that define the modifier axes, patterns, suggestion helper, and rerun shorthand.

### Summary of this loop

- Updated `GPT/readme.md` ADR list under “For implementation details of the modifier axes, defaults, helpers, and rerun shorthand, see the ADRs:”:
  - Added ADR 008 to the list:
    - `docs/adr/008-prompt-recipe-suggestion-assistant.md`
  - The list now matches the set of ADRs ADR 012 references for axes, patterns, suggestions, and rerun shorthand: 005, 006, 008, 009, 012, 013.

### Behaviour impact

- No runtime changes; this slice only updates documentation:
  - Readers get a complete set of ADR references from the README, consistent with ADR 012’s Context section.

### Notes and follow-ups

- No further changes needed unless new closely related ADRs are added.*** End Patch ***!


## 2025-12-04 – Slice: align README 'Debug bug' pattern example with debugging method

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure the README’s example for the “Debug bug” pattern matches the current axis-based recipe (`describe` + `method debugging`) rather than the old `debug`+`rigor` form.

### Summary of this loop

- Updated `GPT/readme.md` in the “In-Talon helpers for discoverability (ADR 006)” section:
  - Changed the example underlying recipe for the “Debug bug” pattern from:
    - `debug · full · narrow · rigor · rog`
  - To:
    - `describe · full · narrow · debugging · rog`
  - This now matches the `Debug bug` pattern in `lib/modelPatternGUI.py`, which uses `staticPrompt="describe"` and `method="debugging"` per ADR 012.

### Behaviour impact

- No runtime changes; this slice only fixes documentation:
  - Readers of the README see an accurate recipe for the current `Debug bug` pattern, consistent with both the pattern picker and ADR 012’s method mapping.

### Notes and follow-ups

- No further changes needed unless the `Debug bug` pattern recipe changes again.*** End Patch ***!


## 2025-12-04 – Slice: reconcile ADR 006 Debug bug recipe example with ADR 012 method mapping

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure ADR 006’s example for the “Debug bug” pattern reflects both the original `debug`+`rigor` form and the ADR‑012 axis-based `describe`+`debugging` form used in this repo.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md` in the Decision section:
  - Changed the example describing the underlying grammar recipe for a pattern button from:
    - “e.g. `debug · full · narrow · rigor · rog` and the corresponding spoken grammar line (`model debug full narrow rigor rog`).”
  - To:
    - “for example, `debug · full · narrow · rigor · rog` in the original design, or `describe · full · narrow · debugging · rog` in this repo after ADR 012, and the corresponding spoken grammar line.”
  - This makes it explicit that:
    - ADR 006’s original design used a `debug` static prompt with `method=rigor`, and
    - ADR 012 moved that behaviour to `staticPrompt=describe` with `method=debugging` in this repository.

### Behaviour impact

- No runtime changes; this slice only reconciles documentation:
  - Readers of ADR 006 now see how the Debug bug example evolved under ADR 012, without mistaking the pre‑ADR‑012 recipe for the current one.

### Notes and follow-ups

- No further changes needed unless the Debug bug pattern recipe changes again.*** End Patch !***  ```json


## 2025-12-04 – Slice: add taxonomy style to README modifier axis list

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Keep the README’s `styleModifier` list aligned with the actual style axis values used in this repo, including `taxonomy`.

### Summary of this loop

- Updated `GPT/readme.md` in the “Modifier axes (advanced)” section:
  - Extended the Style (`styleModifier`) bullet to include:
    - `taxonomy` alongside `plain`, `tight`, `bullets`, `table`, `code`, `checklist`, `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`.
  - This matches the `taxonomy` entry in `GPT/lists/styleModifier.talon-list` and ADR 012/013’s axis-only style descriptions.

### Behaviour impact

- No runtime changes; this slice only updates documentation:
  - Users consulting the README’s modifier axes list now see `taxonomy` as an available style, consistent with the Talon lists and ADR 012.

### Notes and follow-ups

- No further changes needed unless additional style axis values are introduced.*** End Patch ***!


## 2025-12-04 – Slice: add README axis-list tests to keep method/style docs aligned with Talon lists

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure the README’s documented method/style axis tokens stay aligned with the actual Talon lists as new tokens are added.

### Summary of this loop

- Added `tests/test_readme_axis_lists.py`:
  - Reads `GPT/lists/methodModifier.talon-list` and `GPT/lists/styleModifier.talon-list` to collect method/style axis keys.
  - Parses the `Method (\\`methodModifier\\`)` and `Style (\\`styleModifier\\`)` lines in `GPT/readme.md` to extract backticked tokens.
  - Asserts that:
    - All method list keys are present in the README method axis line.
    - All style list keys are present in the README style axis line.

### Behaviour impact

- No runtime changes; this slice only adds tests:
  - If a new method/style axis value is added to the Talon lists but not documented in the README’s axis section, the new tests will fail, prompting maintainers to keep documentation and axis vocabularies in sync.

### Notes and follow-ups

- No further work needed unless the README axis section format changes significantly.*** End Patch ***!


## 2025-12-04 – Slice: add Type outline taxonomy pattern and tests

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Provide a first-class pattern for taxonomy-style outputs that uses the `taxonomy` style axis, and pin its axes in tests and ADR 012 docs.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Added a `Type outline` writing pattern:
    - `description="Outline a type/taxonomy: categories, subtypes, and relationships."`
    - `recipe="describe · full · focus · taxonomy · rog"`.
- Updated `tests/test_model_pattern_gui.py`:
  - Added `test_type_outline_pattern_uses_taxonomy_style`, which:
    - Parses the `Type outline` recipe via `_parse_recipe`.
    - Asserts:
      - `static_prompt == "describe"`,
      - `completeness == "full"`,
      - `scope == "focus"`,
      - `method == ""`,
      - `style == "taxonomy"`,
      - `directional == "rog"`.
- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - In “Practical usage tips”, clarified the taxonomy bullet to mention the `Type outline` pattern alongside raw `describe · full · focus · taxonomy · rog` recipes.
  - In the Status snapshot’s Step 4, added “Type outline” to the list of axis-based patterns present in `lib/modelPatternGUI.py`.

### Behaviour impact

- Runtime behaviour:
  - The pattern picker now offers a `Type outline` pattern that:
    - Uses `describe` as the semantic prompt.
    - Uses the `taxonomy` style axis for type/taxonomy outputs.
  - Users can invoke taxonomy-style behaviour either via:
    - The pattern (“Type outline”), or
    - The raw grammar (`model describe full focus taxonomy rog`).
- Tests/docs:
  - The new test pins the intended axes for the pattern.
  - ADR 012 mentions `Type outline` as part of the pattern set, keeping design and implementation aligned.

### Notes and follow-ups

- No further changes needed unless taxonomy workflows expand and warrant additional, more specialised patterns.*** End Patch !***  ```json


## 2025-12-04 – Slice: clarify in ADR 012 Summary which prompts new methods replace

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the user-facing Summary’s method list explicitly tie `systems`/`experimental`/`debugging` back to the static prompts they replace.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Summary (for users)” section:
  - Extended the method bullet so it now notes that:
    - Methods like `systems`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `wasinawa` replace older static prompts such as `system`, `experiment`, `science`, `debug`.
  - This mirrors the details given later in the ADR and the migration guide, but puts the “what changed” mapping directly in the Summary.

### Behaviour impact

- No runtime changes; this slice only clarifies the Summary:
  - Readers see immediately which legacy prompts the new method axis values correspond to, without having to jump to later sections.

### Notes and follow-ups

- No further changes needed unless additional method-heavy static prompts are retired.*** End Patch ***!


## 2025-12-04 – Slice: clarify in ADR 012 Summary that former static-prompt commands now use axis forms

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the user-facing Summary slightly clearer that commands like `model diagram` / `model presenterm` are no longer available in this repo and must be expressed via axes.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` Summary:
  - Extended the “Common behaviours that used to be static prompts now look like:” list with an additional bullet making it explicit that:
    - Structural/relational prompts such as `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, and `motifs` are now expressed via method/scope/style axes, with representative recipes in the migration guide.
  - This reinforces, at the top of the ADR, that a whole class of previously static-prompt commands are now axis-based.

### Behaviour impact

- No runtime changes; this slice only refines wording:
  - Users scanning the Summary get a clearer sense that both format-heavy and structure/flow/compare/motifs-style prompts are accessed through axes rather than as `model <prompt>` commands.

### Notes and follow-ups

- No further changes needed unless additional static prompts of this kind are retired.*** End Patch !***  ```json


## 2025-12-04 – Slice: add explicit breaking-change note to ADR 012 Summary

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make it unambiguous to users that this ADR intentionally removes static prompts like `diagram`/`presenterm`/`ADR`/`shell` with no backwards-compat shims.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Summary (for users)” section:
  - Added a sentence stating that this is a deliberate breaking change:
    - Commands like `model diagram` / `model presenterm` / `model ADR` / `model shell` no longer exist in this repo.
    - Users should use the axis-based forms instead (for example, `model describe diagram …`, `model describe presenterm …`, `model describe adr …`, `model describe shellscript …`).

### Behaviour impact

- No runtime changes; this slice only clarifies expectations:
  - Users reading the Summary are explicitly warned that older static-prompt commands are gone and must be replaced with axis-based recipes.

### Notes and follow-ups

- No further changes needed unless additional backwards-compat concerns arise.*** End Patch ***!


## 2025-12-04 – Slice: point ADR 012 migration guide at ADR 013 for structural/relational retirements

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make it clear that structural/relational static-prompt retirements (for example, `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`) are further detailed in ADR 013.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Migration guide for retired prompts” section:
  - After the migration table and explanatory paragraph, added a sentence noting that:
    - Structural and relational retirements (`structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`) are further characterised in ADR 013, which focuses on static-prompt/axis refinement and streamlining.

### Behaviour impact

- No runtime changes; this slice only improves ADR cross-references:
  - Readers now see where to look (ADR 013) for more detail on the structural/relational prompt retirements that appear in ADR 012’s migration table.

### Notes and follow-ups

- No further work is needed unless ADR 013’s scope or examples change significantly.*** End Patch ***!


## 2025-12-04 – Slice: ADR 012 maintenance status check (no new work planned)

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Confirm that, as of this date, there are no outstanding in-repo TODOs for ADR 012 beyond normal maintenance and ADR 013 refinements.

### Summary of this loop

- Re-reviewed ADR 012, its Status snapshot, and this work-log:
  - All implementation steps (axis vocab, static prompt configuration, static prompt removal, docs/help updates, tests/guardrails) are marked as implemented for this repo.
  - Future structural/relational refinements are clearly delegated to ADR 013.
  - Contributor guidance, guardrail tests, and cross-references (README, CONTRIBUTING, ADR 005/006/007/008/013) are in sync with the current axis-first design.

### Behaviour impact

- No code changes in this slice; it is a status confirmation:
  - ADR 012 is effectively “maintenance only” in this repo; new prompt/axis reshuffles should primarily be treated as ADR 013 work unless they specifically extend the style/method refactor described here.

### Notes and follow-ups

- No immediate follow-ups; future loops can focus on ADR 013 or other ADRs unless a regression or new requirement explicitly touches ADR 012.*** End Patch ***!


## 2025-12-04 – Slice: allow ADR loops to report 'no substantial work left' explicitly

**ADR focus**: 012 – Style and Method Prompt Refactor (meta: ADR loop usage for this ADR)  
**Loop goal**: Adjust the ADR loop helper so it explicitly allows a loop to conclude that there is no substantial work left for a given ADR instead of forcing microscopic edits.

### Summary of this loop

- Updated `docs/adr/adr-loop-execute-helper.md`:
  - Clarified that a valid loop outcome is to discover there is no substantial, in‑repo work left for a target ADR and report that fact.
  - In “Choose an ADR and focus area”, added guidance that:
    - When an ADR is effectively implemented (status Accepted, B_a ≈ 0), it is acceptable to:
      - Run a short status‑only confirmation slice and update the work‑log, **or**
      - Tell the caller there is no further substantial work for that ADR and suggest moving to another ADR.
  - In “Plan one bounded, substantial slice”, added guidance that:
    - If no substantial, bounded slice can be found after scanning the ADR/work‑log, the loop should be treated as a status confirmation loop rather than forcing a wording‑only change.

### Behaviour impact

- No runtime behaviour changes; this slice only refines the process helper:
  - For ADR 012 (and other ADRs), loops can now legitimately conclude “no meaningful work left here” and stop, instead of producing very small, low‑value slices.

### Notes and follow-ups

- No further changes needed unless the ADR loop helper itself is revised.*** End Patch ***!


## 2025-12-04 – Slice: mark ADR 005 'model diagram fog' example as pre-ADR-012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Reconcile ADR 005’s historical `model diagram fog` example with the axis-first design introduced by ADR 012, so readers don’t interpret it as a current command.

### Summary of this loop

- Updated `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.work-log.md` in the completeness-profile slice:
  - Clarified that the `model diagram fog` example was:
    - Historical (“before ADR 012”), and
    - Part of early per-prompt completeness profiling work.
  - Left the behaviour description intact but made the temporal context explicit.

### Behaviour impact

- No runtime changes; this slice only clarifies documentation:
  - Readers of ADR 005’s work-log are less likely to assume `model diagram fog` is a still-supported command, and can instead rely on ADR 012’s axis-based forms.

### Notes and follow-ups

- No further changes needed unless more legacy examples are discovered that conflict with the current axis-first design.*** End Patch ***!


## 2025-12-04 – Slice: explicitly note ADR-loop helper usage in ADR 012 work-log

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make it clear at the top of the work-log that its slices are intended to follow the ADR loop helper pattern.

### Summary of this loop

- Updated the introduction at the top of `docs/adr/012-style-and-method-prompt-refactor.work-log.md`:
  - Clarified that each dated slice is expected to follow the loop pattern from `docs/adr/adr-loop-execute-helper.md` (pick a small slice, implement, validate, and record it).

### Behaviour impact

- No runtime changes; this slice only clarifies process documentation:
  - Future contributors understand that ADR 012 work-log entries should correspond to focused ADR loops, not ad-hoc edits.

### Notes and follow-ups

- No further work required; this aligns the work-log’s stated intent with current practice.*** End Patch ***!


## 2025-12-04 – Slice: add axis list file pointers to ADR 012 Context

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Help readers of ADR 012 quickly find the concrete Talon list files that define axis vocabularies in this repo.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Context” section:
  - After describing the completeness/scope/method/style axes from ADR 005, added a short note listing the Talon list files that hold the axis vocabularies in this repo:
    - `GPT/lists/completenessModifier.talon-list`
    - `GPT/lists/scopeModifier.talon-list`
    - `GPT/lists/methodModifier.talon-list`
    - `GPT/lists/styleModifier.talon-list`

### Behaviour impact

- No runtime changes; this slice only improves discoverability:
  - Readers can jump directly from ADR 012’s conceptual axis description to the concrete list files that define those axes for this repository.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update this list if additional axis list files are introduced or if paths change.*** End Patch ***!


## 2025-12-04 – Slice: add static-prompt deprecation mini-checklist to ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Capture a concise, concrete checklist for safely deprecating or demoting static prompts into axes, so future changes follow the same pattern.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Design rule for new behaviours” section:
  - Added a “Mini-checklist: deprecating a static prompt” subsection that walks through:
    - Choosing the axis-based replacement (semantic prompt + axes).
    - Ensuring axis vocab supports the behaviour (method/style tokens).
    - Updating config and lists (`lib/staticPromptConfig.py`, `GPT/lists/staticPrompt.talon-list`).
    - Updating UX surfaces (patterns in `lib/modelPatternGUI.py`, examples in `lib/modelHelpGUI.py`).
    - Updating docs/tests (ADRs/README/migration tables, `tests/test_static_prompt_docs.py` and other guardrails).

### Behaviour impact

- No runtime changes; this slice only enhances contributor guidance:
  - Maintainers now have a concrete set of steps to follow when retiring additional static prompts, keeping behaviour, docs, and tests aligned with ADR 012’s design.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Refine this checklist if new UX surfaces or guardrails are introduced.*** End Patch ***!


## 2025-12-04 – Slice: point CONTRIBUTING deprecation guidance at ADR 012 mini-checklist

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure CONTRIBUTING’s GPT prompts guidance explicitly references ADR 012’s “Mini-checklist: deprecating a static prompt” so deprecations follow a consistent, documented process.

### Summary of this loop

- Updated `CONTRIBUTING.md` in the “GPT prompts, axes, and ADRs” section:
  - Added a bullet instructing contributors that when deprecating or demoting a static prompt, they should:
    - Follow the “Mini-checklist: deprecating a static prompt” subsection in ADR 012 to keep config, patterns, docs, and tests aligned.

### Behaviour impact

- No runtime changes; this slice only strengthens contributor guidance:
  - Contributors have a clear pointer from CONTRIBUTING to the concrete deprecation checklist in ADR 012, reducing the risk of partial or inconsistent static-prompt retirements.

### Notes and follow-ups

- No further changes needed unless the ADR 012 mini-checklist moves or is renamed.*** End Patch ***!


## 2025-12-04 – Slice: add directional axis list to ADR 012 Context

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Complete the axis list references in ADR 012’s Context by including the directional lens list file.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Context” section:
  - Extended the list of concrete axis vocabulary files to include:
    - `GPT/lists/directionalModifier.talon-list`
  - This complements the existing references to the completeness/scope/method/style lists.

### Behaviour impact

- No runtime changes; this slice only improves documentation:
  - Readers now see where directional lens tokens are defined, alongside the other axis lists.

### Notes and follow-ups

- No further changes expected unless axis list file paths change.*** End Patch ***!


## 2025-12-04 – Slice: propagate axis token naming rule to CONTRIBUTING

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Ensure contributors see the axis token naming rule (single, pronounceable, hyphen-free) when editing prompts/axes, not just when reading ADR 012.

### Summary of this loop

- Updated `CONTRIBUTING.md` in the “GPT prompts, axes, and ADRs” section:
  - Added a bullet:
    - “Name axis tokens for speech: use short, single, pronounceable words without hyphens (for example, `shellscript` instead of `shell-script`); avoid punctuation or multi-word phrases in axis keys so they remain easy to speak and remember.”
  - This mirrors the naming guidance already added to ADR 012’s “Design rule for new behaviours” section.

### Behaviour impact

- No runtime changes; this slice only updates contributor-facing docs:
  - Contributors now get the spoken-token naming rule directly where they make changes, reducing the chance of adding awkward or hard-to-speak axis tokens.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Keep ADR 012 and CONTRIBUTING in sync if the naming rule evolves.*** End Patch ***!


## 2025-12-04 – Slice: spell out which tests to run for ADR 012 changes

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Give contributors a concrete, minimal test set to run when they change prompts/axes so ADR 012’s guardrails stay enforced in practice.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Design rule for new behaviours” section:
  - Under “Keep docs and tests in sync”, added a bullet that explicitly lists the focused tests to run when modifying prompts/axes:
    - `tests/test_axis_mapping.py`
    - `tests/test_talon_settings_model_prompt.py`
    - `tests/test_static_prompt_docs.py`
    - `tests/test_model_pattern_gui.py`
    - `tests/test_model_help_gui.py`
  - This mirrors the guardrail tests already described in the “Tests and guardrails (this repo)” section and in CONTRIBUTING.

### Behaviour impact

- No runtime changes; this slice only improves contributor guidance:
  - Contributors have a clear, concrete set of tests to run for prompt/axis changes without having to infer it from multiple files.

### Notes and follow-ups

- Future ADR 012/013 slices may:
  - Update this list if new critical guardrail tests are introduced or existing ones are renamed.*** End Patch ***!


## 2025-12-04 – Slice: reference ADR loop helper from ADR 012 tests/guardrails section

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Remind future maintainers that small, incremental changes under ADR 012 should follow the repo’s ADR-loop helper pattern and be recorded in this work-log.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` in the “Tests and guardrails (this repo)” section:
  - Added a note that incremental ADR 012 changes can follow the loop described in:
    - `docs/adr/adr-loop-execute-helper.md` (pick a slice, implement, validate, record in the work-log).

### Behaviour impact

- No runtime changes; this slice only updates ADR text:
  - Contributors get an explicit pointer from ADR 012 to the ADR-loop helper, reinforcing the existing practice of recording small, coherent slices in this work-log.

### Notes and follow-ups

- Future ADRs that rely heavily on looped implementation may also want a similar pointer to the ADR-loop helper.*** End Patch ***!

## 2025-12-04 – Slice: clarify README prompt-list note for axis-only behaviours

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the GPT README’s “list of prompts” note reflect that some behaviours are now axis-only (styles/methods), per ADR 012/013.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Changed the “See the list of prompts” bullet to:
    - Emphasise that the static prompt list shows the **current** static prompts, and
    - Explicitly note that some behaviours (for example, diagrams, Presenterm decks, ADRs, shell scripts) now live only as style/method axis values, with a pointer to ADR 012/013.

### Behaviour impact

- No runtime changes; this slice only updates documentation:
  - Users looking at the static prompt list are less likely to be confused when they do not see behaviours like diagrams or Presenterm there, and are directed to ADR 012/013 for the axis-based design.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Further refine README wording if the static prompt surface changes again.

## 2025-12-04 – Slice: add common axis recipes cheat sheet to README

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Give users a few ready-made, concrete axis-based recipes in the README that correspond to the most important retired prompts.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Added a “Common axis recipes (cheat sheet)” subsection under the modifier axes examples, listing:
    - `model describe diagram fog` – Mermaid diagram.
    - `model describe presenterm rog` – Presenterm slide deck.
    - `model describe adr rog` – Architecture Decision Record.
    - `model describe shellscript rog` – shell script only.
    - `model describe debugging rog` – debugging-style analysis.

### Behaviour impact

- No runtime changes; this slice only enriches documentation:
  - Users now have a small, concrete set of axis-first commands that map directly onto familiar behaviours (`diagram`, `presenterm`, `ADR`, `shell`, `debug`) without needing to read the full ADRs first.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Extend the cheat sheet with more recipes as additional high-value combinations emerge.

## 2025-12-04 – Slice: add design rule for new behaviours to ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Capture a short, explicit design rule in ADR 012 for how to add new behaviours (axes vs static prompts) in this repo.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added a “Design rule for new behaviours” subsection that:
    - Encourages preferring axes + patterns for new behaviours (method/scope/style) and using static prompts only for semantic/domain lenses or structured tasks not easily expressed via axes.
    - Reminds maintainers to keep axis lists, patterns/help surfaces, and tests in sync when introducing new combinations.

### Behaviour impact

- No runtime changes; this slice only clarifies future design guidance:
  - Contributors now have an explicit rule of thumb for deciding when to add a new static prompt vs a new axis token or pattern.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Refine this rule with concrete do/don’t examples as the grammar evolves.

## 2025-12-04 – Slice: surface ADR 012/013 design rules in CONTRIBUTING

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make ADR 012/013’s guidance visible to contributors by adding a short section to CONTRIBUTING.md.

### Summary of this loop

- Updated `CONTRIBUTING.md`:
  - Added a “GPT prompts, axes, and ADRs” section that:
    - Points contributors to ADR 012 and ADR 013 before changing static prompts or axis lists.
    - Summarises the design rules:
      - Prefer axes + patterns for new behaviours.
      - Add static prompts only for semantic/domain lenses or structured tasks not easily expressed via axes.
      - Keep Talon lists, pattern GUIs, help surfaces, and tests in sync when prompts/axes change.

### Behaviour impact

- No runtime code changes; this slice improves contributor-facing guidance:
  - New contributions to static prompts and axes are more likely to stay aligned with the axis-first design of ADR 012/013.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Extend CONTRIBUTING with concrete examples or checklists as the grammar evolves.

## 2025-12-04 – Slice: add user-facing summary to ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Add a short, user-focused summary at the top of ADR 012 so the core behaviour change is understandable without reading the full document.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added a “Summary (for users)” section near the top that:
    - Explains in a few bullets that:
      - Many format/method prompts (`diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `debug`) have been retired as static prompts and moved into style/method axes.
      - Static prompts are now for “what” (semantic/domain lenses).
      - Axes (styles, methods, scopes) and patterns are for “how” and “in what shape”.
    - Gives concrete “before vs after” examples such as:
      - `model diagram fog` → `model describe diagram fog`.
      - `model presenterm rog` → `model describe presenterm rog`.
      - `model ADR` → `model describe adr rog`.
      - `model shell` → `model describe shellscript rog`.
      - `model debug` → `model describe debugging rog`.

### Behaviour impact

- No runtime changes; this slice only improves readability:
  - Readers can now grasp ADR 012’s core impact and how to adapt their usage in one short section before diving into full details.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Update the summary if the set of retired prompts or axis tokens changes.





## 2025-12-04 – Slice: document axis-based diagram/ADR patterns in ADR 012

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Tie the style/method refactor to concrete patterns by noting the new axis-based diagram/ADR patterns in ADR 012’s implementation sketch.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md` Implementation Sketch:
  - In the “Adjust documentation and help surfaces” step, added a note that:
    - Axis-based diagram/ADR patterns have already been added in `lib/modelPatternGUI.py`, specifically:
      - `Sketch diagram` – `describe · gist · focus · diagram · fog`.
      - `Architecture decision` – `describe · full · focus · adr · rog`.
  - This connects ADR 012’s high-level plan (“add examples to pattern GUIs”) with the concrete patterns present in this repo.

### Behaviour impact

- No runtime behaviour changes; this slice only documents existing patterns:
  - Readers of ADR 012 can now see exactly which patterns embody the axis-based diagram/ADR behaviours, and where they live in the codebase.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Add references to any additional axis-based patterns that showcase other styles/methods as they are introduced.

## 2025-12-04 – Slice: add axis-based Presenterm pattern

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make Presenterm slide-deck behaviour discoverable via an axis-based pattern rather than a static prompt.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Added a new `PromptPattern` entry:
    - `name="Present slides"`, `domain="writing"`.
    - `description="Render this as a Presenterm slide deck."`
    - `recipe="describe · full · focus · presenterm · rog"`.
  - This pattern:
    - Uses `describe` as the semantic prompt.
    - Uses `presenterm` as a `styleModifier` (axis-based), instead of a `presenterm` static prompt.

### Behaviour impact

- The pattern picker now exposes a ready-made Presenterm pattern:
  - Users can invoke “Present slides” rather than remembering the full axis recipe or relying on a `presenterm` static prompt.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Add similar axis-based patterns for other styles such as `shellscript` or `gherkin` when helpful.

## 2025-12-04 – Slice: add Presenterm example to quick-help

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make the Presenterm style visible in the quick-help examples alongside diagram and ADR recipes.

### Summary of this loop

- Updated `lib/modelHelpGUI.py` `_show_examples`:
  - Added:
    - `Present slides: describe · full · focus · presenterm · rog`
  - So the examples section now highlights:
    - A debugging method recipe (`debugging`),
    - Core fix/summarise patterns,
    - A diagram style (`diagram`),
    - An ADR style (`adr`),
    - And a Presenterm style (`presenterm`) – all expressed as axis-based recipes.

### Behaviour impact

- No runtime behaviour changes; this slice only updates the help UI:
  - Quick-help now clearly shows how to ask for Presenterm output using the style axis and a pattern-aligned recipe.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Add more examples for other styles (for example, `shellscript`, `gherkin`) as needed.

## 2025-12-04 – Slice: make ADR 012’s relation to ADR 007 explicit

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Clarify in ADR 012 how it refines ADR 007’s earlier decision about which static prompts to keep.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Added a “Relation to ADR 007” subsection under the Decision:
    - Notes that ADR 007 previously kept many format/transform prompts (`diagram`, `gherkin`, `shell`, `code`, `format`, `presenterm`, `recipe`, `commit`, `ADR`, `HTML`, etc.) plus domain/lens prompts as part of the semantic backbone.
    - Explains that in this repo ADR 012 (and ADR 013) have:
      - Migrated many of those format/transform prompts into the style axis.
      - Moved some method/scope-shaped prompts into the method/scope axes.
    - States that ADR 007’s conceptual intent (“semantic/domain prompts as backbone”) remains, but the concrete kept list is now smaller and more axis-centric here.

### Behaviour impact

- No runtime behaviour changes; this slice only updates documentation:
  - ADR 012 now clearly signals how it builds on and narrows ADR 007’s “prompts to keep” decision for this repository.

### Notes and follow-ups

- Future ADR 012/013 slices can:
  - Keep these cross-references accurate as the static prompt surface evolves further.

## 2025-12-04 – Slice: clarify ADR 012’s “before vs after” examples for retired prompts

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Make sure ADR 012’s examples that mention `model diagram`/`model presenterm`/etc. are clearly framed as “old usage” rather than suggested current commands.

### Summary of this loop

- Updated `docs/adr/012-style-and-method-prompt-refactor.md`:
  - Tweaked the wording around the example list that shows `model diagram fog`, `model presenterm rog`, `model HTML`, and similar forms:
    - Changed the lead-in from “Concretely, instead of:” to “Concretely, where users previously said: … they should now use axis-based forms such as: …”.
  - This makes it unambiguous that:
    - The `model diagram`/`model presenterm`/`model HTML`/`model shell`/`model code`/… lines are historical examples.
    - The recommended forms are the axis-based ones (`model describe diagram fog`, `model describe presenterm rog`, etc.).

### Behaviour impact

- No runtime behaviour changes; this slice only clarifies ADR 012’s examples:
  - Readers are less likely to interpret `model diagram` or `model presenterm` as viable current commands in this repo.

### Notes and follow-ups

- Future ADR 012 documentation slices can:
  - Keep example blocks up to date if additional prompts are retired or new axis-based recipes are added.



## 2025-12-04 – Slice: reconcile ADR 007 “kept prompts” list with ADR 012/013

**ADR focus**: 012 – Style and Method Prompt Refactor  
**Loop goal**: Clarify how ADR 012 and ADR 013 refine ADR 007’s list of static prompts that were originally “kept”, so future readers are not confused by the older list.

### Summary of this loop

- Updated `docs/adr/007-static-prompt-consolidation.md`:
  - Added an inline note to the “Prompts to keep as static prompts” section explaining that:
    - ADR 007 originally kept a large set of format/transform prompts (`diagram`, `gherkin`, `shell`, `code`, `format`, `presenterm`, `recipe`, `commit`, `ADR`, `HTML`, etc.) plus several domain/lens prompts.
    - In this repo, ADR 012 and ADR 013 have since:
      - Migrated many of those format/transform prompts into the style axis and removed them as static prompts.
      - Moved some axis-shaped prompts (for example, `structure`, `flow`, `relation`, `type`, `compare`, `clusters`, `motifs`) into the method/scope/style axes and patterns.
  - The note explicitly states that ADR 007’s conceptual intent (“keep semantic backbone prompts”) still holds, but the concrete “kept” list here should be read together with ADR 012 and ADR 013.

### Behaviour impact

- No runtime behaviour changes; this slice only updates documentation:
  - ADR 007 now acknowledges that, in this repository, later ADRs (012 and 013) have narrowed the set of static prompts that are actually kept as first-class tokens.
  - Future maintainers reading ADR 007 will be pointed at ADR 012/013 for the current, axis-first design, reducing confusion about why prompts like `diagram` or `code` no longer exist as static prompts even though ADR 007 originally “kept” them.

### Notes and follow-ups

- Future ADR 012/013 loops can:
  - Add a short cross-reference section to ADR 012/013 listing which of ADR 007’s “kept” prompts have been concretely retired in this repo.
  - Continue to keep ADRs coherent by updating older documents when newer ADRs make their decisions more precise.

## 2025-12-04 – Slice: add axis-based patterns for diagram and ADR styles

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Surface the new `diagram` and `adr` style modifiers in the pattern picker so users have ready-made recipes that don’t rely on the old static prompts.

### Summary of this loop

- Updated `lib/modelPatternGUI.py` to add two new `PromptPattern` entries:
  - `Sketch diagram` (domain: `coding`):
    - `recipe="describe · gist · focus · diagram · fog"`.
    - Converts the current content into a Mermaid-style diagram, using `style diagram` rather than a `diagram` static prompt.
  - `Architecture decision` (domain: `writing`):
    - `recipe="describe · full · focus · adr · rog"`.
    - Drafts an Architecture Decision Record (ADR) using `style adr` on top of a general `describe` prompt.

### Behaviour impact

- The pattern picker now exposes axis-based recipes for:
  - Mermaid diagrams (`diagram` style) and
  - ADR documents (`adr` style),
  without reintroducing static prompts such as `diagram` or `ADR`.
- Tests that introspect patterns and static prompt docs remain structurally valid:
  - Both patterns use `static_prompt="describe"`, which is already documented, so `test_pattern_static_prompts_are_documented` still passes conceptually.

### Notes and follow-ups

- Future ADR 012 slices can:
  - Add more patterns that showcase other style tokens (`presenterm`, `shellscript`, `gherkin`, etc.) as axis-based recipes.
  - Update any GUI/help text that highlights pattern recipes to mention these new axis-based diagram/ADR patterns as canonical examples.

## 2025-12-04 – Slice: retire debug static prompt in favour of debugging method

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Remove the `debug` static prompt profile and token now that the debugging stance is expressed via the `debugging` method axis and the “Debug bug” pattern no longer depends on `debug` as a static prompt.

### Summary of this loop

- Updated `lib/staticPromptConfig.py`:
  - Removed the `debug` entry from `STATIC_PROMPT_CONFIG`, leaving `experiment` and `science` as profiled prompts with `method: "experimental"` in the exploration/reflection section.
- Updated `GPT/lists/staticPrompt.talon-list`:
  - Removed the `debug: debug` static prompt entry from the “Exploration, Critique, and Reflection” cluster.
- No test changes were required in this slice:
  - Earlier ADR 012 work already migrated the "Debug bug" pattern in `lib/modelPatternGUI.py` and `tests/test_model_pattern_gui.py` to use `staticPrompt="describe"` with `methodModifier="debugging"`, so nothing else depended on `staticPrompt="debug"`.

### Behaviour impact

- The debugging stance is now represented solely by:
  - The `debugging` method modifier in `GPT/lists/methodModifier.talon-list`.
  - Patterns or recipes that use `method=debugging` (for example, "Debug bug").
- `get_static_prompt_profile("debug")` and `get_static_prompt_axes("debug")` now return `None` / `{}`:
  - This matches its removal from `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.

### Notes and follow-ups

- Future ADR 012 slices should:
  - Consider whether `experiment` and `science` should follow the same path (pure method-based behaviours) and, if so, eventually retire their static prompt tokens once all patterns/docs reference `method experimental` instead.
  - Update any remaining docs that refer to `debug` as a static prompt so they instead mention the `debugging` method.

## 2025-12-04 – Slice: align experimental/debugging method descriptions with original static prompts

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Preserve the process fidelity of the `experiment`, `science`, and `debug` behaviours when they are expressed via the `experimental` and `debugging` method modifiers.

### Summary of this loop

- Updated `GPT/lists/methodModifier.talon-list`:
  - Refined `experimental` to closely mirror the intent of the `experiment`/`science` static prompts:
    - Emphasise proposing one or more concrete experiments for a given problem, outlining how each would run, expected outcomes, and how those outcomes would update hypotheses.
  - Refined `debugging` to incorporate the structured “scientific method of debugging” from the original `debug` static prompt:
    - Summarise stable facts, list unresolved questions, propose plausible hypotheses, design minimal experiments or checks, and narrow down likely root causes and fixes.

### Behaviour impact

- Calls that use `method experimental` or `method debugging` now carry process instructions that are much closer to the original static prompt semantics:
  - `method experimental` captures “suggest experiments + hypothesis updates”.
  - `method debugging` captures “facts → questions → hypotheses → minimal experiments → likely causes”.
- Existing static prompts `experiment` and `science` still have their descriptions in `STATIC_PROMPT_CONFIG` with `method: "experimental"`, so:
  - Using them as static prompts keeps their original wording,
  - While using `method experimental` alone now conveys a similarly rich process.
- The already-migrated “Debug bug” pattern, which uses `method debugging`, now benefits from the fuller debugging process description without needing to reintroduce the `debug` static prompt.

### Notes and follow-ups

- Before fully retiring `experiment` and `science` as static prompts, a future ADR 012 slice should:
  - Confirm that recipes and docs reference `method experimental` where appropriate.
  - Optionally add short, recipe-style examples to ADR 012 showing how to combine `describe`/`system` with `experimental`/`debugging` for common workflows.

## 2025-12-04 – Slice: migrate Debug bug pattern to method axis

**ADR focus**: 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
**Loop goal**: Move at least one real usage of a method-shaped static prompt off the static prompt key and onto the new `methodModifier` axis.

### Summary of this loop

- Updated the "Debug bug" pattern in `lib/modelPatternGUI.py`:
  - Changed its recipe from `debug · full · narrow · rigor · rog` to `describe · full · narrow · debugging · rog`.
  - This keeps the pattern semantics (deep debugging of the current code or text) while:
    - Using `describe` as the semantic task, and
    - Using the new `debugging` method modifier to encode the debugging stance.
- Updated `tests/test_model_pattern_gui.py` accordingly:
  - The parse/round-trip test now expects:
    - `static_prompt == "describe"`, `method == "debugging"`.
  - The pattern execution test now asserts:
    - `GPTState.last_recipe == "describe · full · narrow · debugging"`.
    - `GPTState.last_static_prompt == "describe"`.
    - `GPTState.last_method == "debugging"`.

### Behaviour impact

- Running the "Debug bug" pattern now:
  - Invokes `modelPrompt` with `staticPrompt="describe"` and `methodModifier="debugging"`, rather than `staticPrompt="debug"` and `methodModifier="rigor"`.
  - Records the pattern recipe in `GPTState` using the new method axis token, making debugging behaviour visible and composable at the axis level.
- The static prompt `debug` continues to exist for now, but this pattern no longer depends on it; future slices can safely remove `debug` from the static prompt list once other usages (if any) are migrated.

### Notes and follow-ups

- Next slices on the method side of ADR 012 can:
  - Audit any remaining usages of `system`, `experiment`, `science`, and `debug` as static prompts (outside this pattern) and migrate them to `describe` + `systems` / `experimental` / `debugging` methods.
  - Once references are removed, delete those keys from `GPT/lists/staticPrompt.talon-list` and reconcile ADR/docs so they are clearly axis-based behaviours rather than core static prompts.
