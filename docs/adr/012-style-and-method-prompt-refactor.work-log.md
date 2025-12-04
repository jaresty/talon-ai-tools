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
  - Included concrete example commands showing the new, axis-first usage (for example, `model describe diagram fog`, `model describe presenterm rog`, `model describe adr`, `model describe systems fog`).

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
