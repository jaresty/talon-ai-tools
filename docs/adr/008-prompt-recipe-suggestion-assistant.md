# 008 – Prompt Recipe Suggestion Assistant

- Status: Proposed  
- Date: 2025-12-03  
- Context: `talon-ai-tools` GPT integration (`model` commands)

## Context

The GPT integration exposes an orthogonal prompt grammar:

- Static prompts (for example, `describe`, `fix`, `todo`, and a smaller, semantic backbone set as refined by ADR 007/012/013).
- Directional lenses (for example, `fog`, `rog`, `ong`).
- Contract-style axes: completeness, scope, method, style (ADR 005/012/013).
- Pattern pickers and prompt-specific pattern menus (ADR 006).

This grammar is powerful but still requires users to *choose* a full recipe:

- Which **static prompt** to use for this subject.
- Which **axes** (completeness, scope, method, style) to apply.
- Which **directional lens** (if any) best fits the task.

Today you have:

- Curated pattern pickers (`model patterns`, `model pattern menu <prompt>`) that expose a small set of high-value recipes.
- Static prompt profiles in `STATIC_PROMPT_CONFIG` that bias axes for certain prompts.
- Axis quick help and pattern menus that make the space more discoverable.

However, in many situations you only have a rough *subject* or *task* (for example, “map dependencies across this project” or “scan this ADR for risks”) and would like the model itself to propose a few candidate **staticPrompt + axes + directional** combinations that fit that subject, without:

- Manually browsing the pattern list, or
- Keeping the entire axis and prompt vocabulary in your head.

Concretely, there is no direct way to say:

> “Given this subject and the current selection/clipboard, what are 3–5 good `staticPrompt + axes + directional` recipes, and which one should I run?”

We want a small, optional helper that:

- Uses the same selection/clipboard source model as existing `model` commands.
- Leverages the existing static prompts, axis semantics, and recipe machinery.
- Lets GPT *suggest* a few concrete recipes – including the **prompt itself** – then lets you choose which one (if any) to run.

## Decision

We will add a **Prompt Recipe Suggestion Assistant** that:

- Looks at the same text sources as other `model` commands (selection / clipboard / configured source).
- Optionally takes extra spoken text describing the subject or goal.
- Asks GPT (once) to propose several concrete recipes:
  - `staticPrompt + completeness + scope + method + style + directional`.
- Presents those recipes in a small, clickable GUI (refined by ADR 041 for stance-aware, preset-free suggestions behaviour).
- Lets the user execute a chosen recipe via the existing `model` pipeline.

This appears as:

- New voice commands such as:

  - `model suggest`  
  - `model suggest for <user.text>`

- A new, transient `imgui` modal that:
  - Lists 3–5 suggestions as buttons with names and recipes.
  - Runs the selected recipe through the same code paths as pattern execution.

The assistant is advisory only: it *suggests* prompts and axis configurations; the user decides what to run.

## Rationale

- **Leverage existing semantics**  
  ADR 005/006 already define axis meanings and the pattern/recipe machinery. This ADR reuses that work instead of inventing a new abstraction.

- **Recognition over recall**  
  Users do not have to remember static prompt names or axis tokens. They can:
  - Select some text (or rely on the clipboard / default model source),
  - Optionally add a short spoken gloss (“for dependency mapping”, “for risk scan”),
  - Then pick from a few well-structured suggestions.

- **Keep control explicit**  
  Suggestions are not auto-executed; the user inspects, selects, and runs them, keeping the workflow transparent and debuggable.

- **Single extra GPT call**  
  The helper adds at most one additional GPT request per invocation, avoiding nested orchestration complexity.

- **Align with existing UX**  
  A small, clickable GUI that shows “Name + Recipe + grammar line” is already familiar from `model patterns` and pattern menus.

## Design

### Command and flow

Introduce grammar and actions that mirror existing `model` flows:

- Talon grammar (illustrative):

  - `{user.model} suggest$: user.gpt_suggest_prompt_recipes("")`  
  - `{user.model} suggest for <user.text>$: user.gpt_suggest_prompt_recipes(text)`

- Core action:

  - `user.gpt_suggest_prompt_recipes(subject: str) -> None`

High-level flow:

1. **Determine text source**  
   Use the same source selection model as other `model` commands:

   - A `ModelSource` (clipboard, context, thread, style, GPT response/request/exchange, last dictation, all-text, or selection) resolved from `user.model_default_source` and the existing `create_model_source` helper.
   - In this repo, `user.model_default_source` controls whether `model`-family commands, including `model suggest`, read from clipboard vs. other sources by default; if it is set to an unknown token (for example, `"selection"`), `create_model_source` falls back to using the current selection via `SelectedText`.
   - The resolved source text is the *primary* material for suggestions; there is no extra “auto-fallback from selection to clipboard” layer beyond the shared `model_default_source` behaviour.

2. **Build a suggestion prompt**  
   Construct a single GPT request that includes:

   - A brief description of the orthogonal axes and their roles (summarised from ADR 005/006).
   - The *subject context*:
     - The resolved source text (selection/clipboard/etc.), truncated if necessary.
     - The optional `subject` string from the voice command (for example, “for clustering themes across sections”).
   - A compact table of available axis values and meanings, derived from Talon lists:
     - `completenessModifier.talon-list`
     - `scopeModifier.talon-list`
     - `methodModifier.talon-list`
     - `styleModifier.talon-list`
   - A compact list of available static prompts and their descriptions, derived from:
     - `STATIC_PROMPT_CONFIG` for profiled prompts.
     - `staticPrompt.talon-list` and associated comments/values as a fallback.
   - A strict output format specification (see below).

   The system prompt for this call can be a “prompt-designer” persona that understands the contract-style axes and must only suggest recipes, not solve the underlying domain task.

3. **Send the GPT request**  
   Use the existing prompt/session machinery to build a one-off request:

   - System: axis and static-prompt description + instructions.
   - User: subject + sample text + format requirements.

4. **Parse the GPT response into suggestions**  
   Parse the GPT response into a small list of `Suggestion` objects (see “Suggestion format”).

5. **Present a suggestion GUI**  
   Open an `imgui` modal listing the candidate recipes:

   - One button per suggestion.
   - Under each:
     - The recipe tokens (`staticPrompt · completeness · scope · method · style · directional`).
     - Optionally, a very short rationale sentence.

6. **Run the selected recipe**  
   When the user clicks a suggestion:

   - Map the recipe into the same `modelPrompt` + `ApplyPromptConfiguration` path used by patterns:
     - Use the existing recipe parser to turn tokens into:
       - `staticPrompt`, `completenessModifier`, `scopeModifier`, `methodModifier`, `styleModifier`, `directionalModifier`.
     - Build a `Match` object with those attributes.
     - Call `modelPrompt(match)` to get the user-facing Task/Constraints text.
     - Use the existing `gpt_apply_prompt` flow to run the request against the *same source text* that was used to generate suggestions.
   - Close the suggestion GUI.

If parsing fails or GPT does not respect the schema, the helper will:

- Show a simple textual fallback (the raw suggestions), or
- Notify the user that suggestions could not be parsed for execution.

### Suggestion format

To keep parsing simple and robust, the assistant will request a line-based, constrained format such as:

- Each suggestion on its own line:

  - `Name: <short human name> | Recipe: <staticPrompt> · <completeness> · <scope> · <method> · <style> · <directional>`

- Example GPT output:

  - `Name: Deep relational map | Recipe: describe · full · relations · cluster · bullets · fog`  
  - `Name: Quick dependency scan | Recipe: dependency · gist · relations · steps · plain · fog`  
  - `Name: Focused risk list | Recipe: pain · gist · focus · filter · bullets · rog`

Parsing:

- Split the response into non-empty lines.
- For each line:
  - Split on `|` into two segments (name and recipe).
  - Split `Name:` and `Recipe:` segments on `:`, trim, and validate.
  - Validate that `Recipe` contains at least:
    - A valid static prompt token, and
    - A directional lens token;
    - Any axis tokens in between are optional but must come from the enumerated lists.

Execution:

- Feed the `Recipe` string into the existing recipe parsing function used by pattern GUIs (ADR 006), which:
  - Recognises which tokens belong to completeness/scope/method/style.
  - Returns `(static_prompt, completeness, scope, method, style, directional)`.

- Map tokens through the axis maps (`*_MAP`) so that:
  - The system prompt receives full “Important: …” descriptions.
  - The GUI and recipes stay concise and human-recognizable.

### Suggestion GUI

A new `imgui` GUI (or mode on an existing one), e.g. `model_prompt_recipe_suggestions_gui`, will manage display and interaction.

State:

- A small list of `Suggestion` objects, each with:
  - `name: str`
  - `recipe_tokens: str` (e.g. `"describe · full · relations · cluster · bullets · fog"`)
  - Parsed fields: `static_prompt`, `completeness`, `scope`, `method`, `style`, `directional`.

Rendering:

- Title: “Prompt recipe suggestions”.
- For each suggestion:
  - A clickable button labeled with `name`.
  - A line showing `Recipe: <recipe_tokens>`.
  - Optionally a short (one-line) rationale text if included in the format later.
- A “Close” button to dismiss without taking action.

Interaction:

- Clicking a suggestion button:
  - Calls a helper such as `user.model_prompt_recipe_suggestions_run(recipe_tokens)`:
    - Uses the parsed fields (or re-parses from `recipe_tokens`).
    - Builds a `Match` object similar to `modelPatternGUI._run_pattern`.
    - Invokes `modelPrompt(match)` and `gpt_apply_prompt` using the same source/destination model as normal `model` calls.
  - Closes the suggestions GUI.

- Saying “close suggestions” (optional future addition) can map to `user.model_prompt_recipe_suggestions_close()`.

### Axis and static-prompt metadata source

To keep semantics centralized and consistent:

- Use the same `.talon-list` readers as `modelHelpGUI` and pattern GUIs:
  - For each axis list file, derive:
    - The set of valid *tokens* (keys).
    - A short description for each token (values).
- For static prompts:
  - Use `STATIC_PROMPT_CONFIG` as the primary source of descriptions and any profile axes.
  - Fall back to `staticPrompt.talon-list` keys and comments/values for prompts without profiles.
- When building the suggestion prompt:
  - Enumerate available tokens per axis and a small set of representative static prompts with descriptions.
  - Explicitly instruct GPT to only use static prompts and tokens from these sets.
- When executing a suggestion:
  - Treat tokens as authoritative; if a token is not in the allowed sets, reject that suggestion.

This ADR does **not** change the semantics of default axes or profiles; it only introduces a new way to *select* static prompts and axis combinations.

## Consequences

### Benefits

- **Makes the grammar more approachable**  
  Users can work from a natural “subject + selection/clipboard” instead of memorizing static prompts and recipes. Suggested recipes are:

  - Concrete and explicit.
  - Re-usable (you can copy the recipe and use it directly later via `model`).

- **Reuses existing infrastructure**  
  `STATIC_PROMPT_CONFIG`, axis lists, recipe parsing, and the `model` pipeline all stay in one place. The assistant is a thin layer over these pieces.

- **Keeps control visible**  
  No automatic execution. Suggestions are visible and must be explicitly chosen. This matches the explicit, inspectable style of ADR 004/005/006.

- **Fits existing workflow**  
  Works with the same sources as other `model` commands:

  - Selection or clipboard (depending on `model_default_source` and captures).
  - Optional extra spoken “for …” text for additional nuance.

### Trade-offs / Risks

- **Adds another GPT call**  
  Each invocation costs latency and tokens, though usage is strictly opt-in.

- **Requires careful prompt design**  
  The suggestion meta-prompt must be robust, so GPT stays within the static prompt and axis vocabularies and output format. Poorly constrained prompts could produce invalid recipes.

- **UX complexity**  
  Adds another GUI surface. It must be:

  - Clearly named and scoped (“prompt recipe suggestions”), and
  - Clearly differentiated from `model patterns` and `model pattern menu`.

## Alternatives considered

- **Rely solely on pattern pickers and prompt menus (ADR 006)**  
  Pros:
  - No new code paths.
  - Users browse curated recipes.

  Cons:
  - Still requires users to choose prompts and recipes manually.
  - Less adaptive to arbitrary subjects or domains.
  - Does not provide a shorthand for iterating on the last recipe once chosen; for that, see ADR 009’s `model again` rerun shorthand.

- **Auto-run a “best guess” recipe with no GUI**  
  Pros:
  - Fewer clicks.

  Cons:
  - Hides important choices.
  - Makes debugging and trust harder.
  - Conflicts with the explicit/inspectable ethos of ADR 004/005/006.

- **Full “builder” wizard for every request**  
  Pros:
  - Complete coverage and explicit control.

  Cons:
  - Too high-friction for frequent use.
  - Better treated as a separate, advanced feature (as noted in ADR 006).

## Status and future work

- **Status in this repo**: Implemented (core behaviour); optional refinements remain.
  - Implemented slices:
    - `model suggest` / `model suggest for <user.text>` grammar.
    - `user.gpt_suggest_prompt_recipes(subject: str)` action that:
      - Reads from the same default source model as other `model` commands.
      - Sends a single GPT request with a constrained `Name: … | Recipe: …` format.
      - Embeds axis + directional semantics from the Talon lists and static prompt semantics from `STATIC_PROMPT_CONFIG` / `staticPrompt.talon-list`.
      - Returns the suggestions as plain text via the existing insertion pipeline.
    - Parsing and state caching:
      - Parses `Name: … | Recipe: …` lines into structured `{name, recipe}` dictionaries.
      - Stores them in `GPTState.last_suggested_recipes` for later reuse.
    - Suggestion GUI:
      - `model_prompt_recipe_suggestions_gui_open` / `…_close` actions and a small `imgui` window (`model_suggestion_gui`) that:
        - Reads from `GPTState.last_suggested_recipes` and shows each suggestion as a button with name and recipe.
        - Runs the chosen recipe via `modelPrompt` / `gpt_apply_prompt` using the same source/destination model as other `model` commands.
        - **Closes itself whenever a suggestion is executed**, mirroring the pattern picker behaviour.
    - Convenience aliases:
      - `model suggestions` grammar to reopen the last suggestion window without re-running `model suggest`.
      - `run suggestion <number>` (while the suggestion window is open) to execute the Nth suggestion by index using the cached recipes.
  - Remaining slices (optional/polish for this repo):
    - Add higher-level tests that exercise the full suggest → GUI → execute path end-to-end.

### Initial implementation slice (planning)

1. **Prompt recipe suggestion action and grammar**
   - Add `user.gpt_suggest_prompt_recipes(subject: str)` wired to the existing prompt/session machinery.
   - Add grammar for:
     - `model suggest`
     - `model suggest for <user.text>`

2. **Suggestion prompt and parser**
   - Implement a dedicated suggestion meta-prompt that:
     - Describes axes and static prompts succinctly.
     - Lists valid tokens and their meanings.
     - Specifies the `Name: … | Recipe: …` output format.
   - Implement a parser that:
     - Extracts `name` and `recipe_tokens` per line.
     - Validates static prompt and axis tokens against the vocabularies.
     - Produces `Suggestion` objects ready for display and execution.

3. **Suggestion GUI**
   - Add a small `imgui` modal that:
     - Displays suggestions as clickable recipes.
     - Runs a recipe via the existing `model` pipeline when clicked.
     - Closes cleanly and does not interfere with pattern pickers or confirmation GUIs.

### Possible future refinements

- Bias suggestions using:
  - The active static prompt, if any.
  - Recent successful recipes (`GPTState.last_recipe`) as examples.
- Provide a “copy recipe” button to paste a suggestion into the editor.
- Add a “run by index” command:
  - E.g. `model run suggested one` for keyboard/voice-only workflows, mapping to the last suggestion set.

## Everyday usage examples

Once ADR 008’s slices implemented in this repo are loaded in Talon, typical flows look like:

- **Get prompt recipes for the current text**
  - Select some text (or rely on the configured `user.model_default_source`, often clipboard).
  - Say `model suggest` or `model suggest for dependency mapping`.
  - The model:
    - Reads from the same source you use for other `model` commands.
    - Asks GPT for 3–5 `Name: … | Recipe: …` lines.
    - Inserts those lines as plain text.
    - Parses and caches them in `GPTState.last_suggested_recipes`.
    - Opens the “Prompt recipe suggestions” window with one button per suggestion.

- **Run one of the suggested recipes**
  - In the suggestions window:
    - Click a suggestion button (for example, “Deep relational map”).
    - The recipe is parsed into `staticPrompt + completeness + scope + method + style + directional`.
    - A normal `model` request is executed with those axes over the same source/destination.
    - The suggestion window closes automatically once the prompt runs.

- **Reopen the last suggestion set without another GPT call**
  - Say `model suggestions`.
  - The suggestion window reopens using the cached `GPTState.last_suggested_recipes` from the last `model suggest` call.
  - You can click a different recipe, or say `close suggestions` to dismiss the window.
