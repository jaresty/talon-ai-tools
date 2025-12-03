# 008 – Prompt Recipe Suggestion Assistant – Work-log

This work-log tracks concrete changes made in this repo under ADR 008.

## 2025-12-03 – Initial ADR and naming alignment (assistant-authored)

- **Focus area**: Capture the design for a prompt-recipe suggestion helper (`model suggest`) that proposes full `staticPrompt + axes + directional` recipes over the current selection/clipboard, and align terminology so it no longer sounds “axes-only”.
- **Changes made (docs):**
  - Added ADR 008 at `docs/adr/008-prompt-recipe-suggestion-assistant.md` describing:
    - A “Prompt Recipe Suggestion Assistant” that:
      - Reads from the same sources as other `model` commands (selection / clipboard / configured source).
      - Optionally takes extra spoken text (`model suggest for <user.text>`).
      - Asks GPT to propose a small set of candidate recipes of the form `staticPrompt · completeness · scope · method · style · directional`.
      - Shows those recipes in a small `imgui` GUI, where clicking a suggestion runs it via the existing `model` pipeline.
    - A constrained output format (`Name: … | Recipe: …`) for the suggestion call, and a plan to reuse the existing recipe parser and axis maps.
    - The axis and static-prompt metadata sources (axis `.talon-list` files and `STATIC_PROMPT_CONFIG` / `staticPrompt.talon-list`).
  - Iterated the ADR text so that:
    - It clearly states that suggestions include the **static prompt** as well as axes and directional lens.
    - Naming is consistent with the full behaviour:
      - Title: “Prompt Recipe Suggestion Assistant”.
      - Commands: `model suggest` / `model suggest for <user.text>`.
      - Core action: `user.gpt_suggest_prompt_recipes(subject: str)`.
      - GUI: `model_prompt_recipe_suggestions_gui` with “Prompt recipe suggestions” as the title, plus helpers named `model_prompt_recipe_suggestions_run/close`.
- **ADR 008 impact:**
  - Establishes a clear, repo-local specification for how prompt-recipe suggestions should work (entrypoints, data flow, parsing contract, and GUI shape) without yet committing to an implementation.
  - Removes residual “axis-only” naming from the design so future loops can implement behaviour without renaming or clarifying intent first.

## 2025-12-03 – Minimal `model suggest` action wiring (assistant-authored)

- **Focus area**: Land a first, usable slice of ADR 008 by wiring a `model suggest` action that calls the existing prompt pipeline to ask GPT for prompt recipes over the current selection/clipboard, returning the suggestions as plain text. The full clickable GUI and structured parsing remain for later loops.
- **Changes made (actions and grammar):**
  - Added a new user action `gpt_suggest_prompt_recipes(subject: str)` in `GPT/gpt.py` that:
    - Resolves the source text via `create_model_source(settings.get("user.model_default_source"))`, matching other `model` commands (selection, clipboard, etc.).
    - Builds a single user message instructing GPT to act as a “prompt recipe assistant” and to emit 3–5 lines in the form `Name: … | Recipe: staticPrompt · completeness · scope · method · style · directional`.
    - Calls `PromptSession` + `_prompt_pipeline.complete(session)` to run this request, then routes the resulting text through `actions.user.gpt_insert_response` using a `Default()` destination.
    - Notifies the user if no source text is available, reusing existing error signalling from `ModelSource` where possible.
  - Extended `GPT/gpt.talon` with:
    - `{user.model} suggest for <user.text>$: user.gpt_suggest_prompt_recipes(text)`
    - `{user.model} suggest$: user.gpt_suggest_prompt_recipes("")`
    so the feature can be invoked as `model suggest` or `model suggest for <extra description>`.
- **Changes made (tests):**
  - Added `test_gpt_suggest_prompt_recipes_uses_prompt_session` in `tests/test_gpt_actions.py` to assert that:
    - `gpt_suggest_prompt_recipes` calls `create_model_source` and `source.get_text()`.
    - A `PromptSession` is constructed, `begin(reuse_existing=True)` is called, and exactly one `add_messages` call is made.
    - `_prompt_pipeline.complete` is invoked with that session, and `actions.user.gpt_insert_response` is called once with the pipeline result and the session’s destination.
  - **ADR 008 impact:**
  - Delivers a minimal but functional version of `model suggest` that:
    - Reads from the same sources as other `model` commands.
    - Produces GPT-suggested prompt recipes as plain text that the user can inspect and copy.
  - Defers structured parsing of suggestions and the dedicated “prompt recipe suggestions” GUI to future loops, which can now build on a concrete, exercised entrypoint and test.

## 2025-12-03 – Enrich `model suggest` with full axis and prompt semantics (assistant-authored)

- **Focus area**: Make `model suggest`’s meta-prompt see essentially the same vocabulary and semantics as the human-facing help (axes, directional lenses, and static prompts), so suggested recipes are grounded in the actual token space.
- **Changes made (actions):**
  - Refactored `gpt_suggest_prompt_recipes` in `GPT/gpt.py` to no longer rely on a hard-coded subset of axis tokens:
    - Added `_read_list_items(filename)` to read `(key, description)` pairs from any `GPT/lists/*.talon-list` file.
    - Added `_build_axis_docs()` to assemble a text block for:
      - Completeness, scope, method, style modifiers, and directional modifiers (`directionalModifier.talon-list`).
      - Each entry is listed as `- key: <full “Important: …” description>`, so GPT sees the complete semantics for all axis and lens tokens.
    - Replaced the previous manual `axis_tokens` block in `gpt_suggest_prompt_recipes` with `axis_docs = _build_axis_docs()`, injected under “Axis semantics and available tokens”.
  - Enriched static prompt documentation for the suggestion call:
    - Added `_build_static_prompt_docs()` that:
      - Walks `STATIC_PROMPT_CONFIG` first, emitting lines of the form:
        - `- <name>: <description> (defaults: completeness=…, scope=…, method=…, style=…)` when profile axes are present.
      - Reads `GPT/lists/staticPrompt.talon-list` to collect any remaining static prompt tokens not in `STATIC_PROMPT_CONFIG`, and appends a final bullet:
        - `- Other static prompts (tokens only; see docs for semantics): <comma-separated list>`
      - This ensures GPT sees the full static prompt token vocabulary while keeping rich semantics centralized in `STATIC_PROMPT_CONFIG`.
    - `gpt_suggest_prompt_recipes` now calls `_build_static_prompt_docs()` and includes the result under “Static prompts and their semantics”.
- **ADR 008 impact:**
  - Brings the suggestion meta-prompt much closer to the human-facing help:
    - All axis and directional tokens are described using their canonical “Important: …” text from the Talon lists.
    - All profiled static prompts are documented with both descriptions and default axes, and every other static prompt token is at least surfaced by name.
  - Lays a firmer semantic foundation for future loops that will parse and execute suggested recipes, since both the LLM and the code are now working from the same axis and prompt vocabularies.

## 2025-12-03 – Clarify source semantics for `model suggest` (assistant-authored)

- **Focus area**: Reconcile ADR 008’s description of how `model suggest` chooses its input text with the actual implementation, and make explicit that it shares the same `user.model_default_source` semantics as other `model` commands (no hidden “selection then clipboard” fallback).
- **Changes made (docs):**
  - Updated the “Determine text source” subsection in `docs/adr/008-prompt-recipe-suggestion-assistant.md` to:
    - Spell out that sources are resolved via `create_model_source(user.model_default_source)`, with the same mapping as other `model` flows (clipboard, context, thread, style, GPT response/request/exchange, last dictation, all-text, or selection via the fallback `SelectedText`).
    - Note that:
      - `user.model_default_source` governs whether commands like `model` / `model suggest` read from clipboard vs. other sources.
      - If `user.model_default_source` is set to an unknown token (for example, `"selection"`), `create_model_source` falls back to using the current selection via `SelectedText`.
      - There is **no additional, special “auto-fallback from selection to clipboard” layer** for `model suggest` beyond this shared behaviour.
- **ADR 008 impact:**
  - The ADR now accurately describes how input is chosen for suggestions in this repo, avoiding confusion between:
    - The configurable default source (`user.model_default_source`), and
    - Any imagined, extra fallback logic that does not exist in code.
  - Future loops can safely build GUI and execution behaviour on top of a clearly documented, shared source-selection model.

## 2025-12-03 – Parse and persist suggested recipes for later GUI use (assistant-authored)

- **Focus area**: Move ADR 008 closer to the planned suggestion GUI by parsing `model suggest` output into structured recipes and storing them in shared state, while still returning plain-text suggestions as today.
- **Changes made (state and actions):**
  - Extended `lib/modelState.GPTState` with:
    - `last_suggested_recipes: ClassVar[List[Dict[str, str]]] = []`, plus resets in both `clear_all` and `reset_all`.
    - This provides a central place to cache the most recent set of suggested recipes.
  - Updated `GPT/gpt.py:gpt_suggest_prompt_recipes` to:
    - After `_prompt_pipeline.complete(session)`, parse `result.text` line by line, looking for lines of the form:
      - `Name: <short name> | Recipe: <recipe tokens>`
    - For each well-formed line, extract:
      - `name` (the short human label).
      - `recipe` (the full `staticPrompt · completeness · scope · method · style · directional` string).
    - Store the parsed list as:
      - `GPTState.last_suggested_recipes = [{"name": ..., "recipe": ...}, …]`.
    - Keep existing behaviour of inserting the full text result via `actions.user.gpt_insert_response(result, destination)`, so current usage is unchanged.
- **Changes made (tests):**
  - Added `test_gpt_suggest_prompt_recipes_parses_suggestions` to `tests/test_gpt_actions.py`:
    - Mocks `PromptSession` and `create_model_source` as in other tests.
    - Sets `self.pipeline.complete.return_value` to a `PromptResult` whose `text` contains two suggestion lines:
      - `Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog`
      - `Name: Quick scan | Recipe: dependency · gist · relations · steps · plain · fog`
    - Calls `gpt_suggest_prompt_recipes("subject")` and asserts that:
      - `GPTState.last_suggested_recipes` contains exactly two entries with the expected `name` and `recipe` fields.
- **ADR 008 impact:**
  - Provides the structured data that the future `model_prompt_recipe_suggestions_gui` can use without re-calling the model:
    - The GUI slice can focus on rendering and execution, reading from `GPTState.last_suggested_recipes` and closing on selection, as specified in ADR 008.
  - Keeps the current user-facing behaviour intact (plain-text suggestions), making this a low-risk, incremental step toward the full design.

## 2025-12-03 – Current status snapshot for ADR 008 (assistant-authored)

- **Completed in this repo so far:**
  - ADR 008 and its work-log are written and wired to this implementation.
  - `model suggest` / `model suggest for <user.text>` grammar is available.
  - `user.gpt_suggest_prompt_recipes(subject: str)`:
    - Uses the same `user.model_default_source` + `create_model_source` model as other `model` commands.
    - Builds a rich suggestion meta-prompt that includes:
      - Full axis and directional semantics and tokens from the Talon lists.
      - Static prompt semantics and default axes from `STATIC_PROMPT_CONFIG`, plus a token list for other prompts.
    - Calls the existing prompt pipeline once to obtain suggestions in a constrained `Name: … | Recipe: …` format.
    - Inserts the full suggestion text via `gpt_insert_response`.
    - Parses `Name: … | Recipe: …` lines and caches structured recipes in `GPTState.last_suggested_recipes`.
  - Tests cover:
    - Wiring of `gpt_suggest_prompt_recipes` through `PromptSession` / `_prompt_pipeline.complete`.
    - Parsing and state update of `GPTState.last_suggested_recipes`.
  - **Still in-repo and incomplete:**
  - Suggestion GUI (partially implemented in this loop; see below for details).
  - Optional follow-ups:
    - Voice command to reopen the last suggestion set or “run suggestion <n>” by index.
    - Higher-level tests that exercise the full suggest → GUI → execute flow once the GUI exists.
  - **Out-of-repo or explicitly deferred:**
  - Any generic, cross-repo tooling for prompt-recipe suggestion beyond this Talon integration.
  - Complex multi-step builders that go beyond the single-call `model suggest` flow described in ADR 008.

## 2025-12-03 – First suggestion GUI slice with close-on-execute behaviour (assistant-authored)

- **Focus area**: Implement a minimal but functional suggestion GUI for ADR 008 that:
  - Reads from `GPTState.last_suggested_recipes`.
  - Lets you click a suggestion to run the corresponding recipe via the normal `model` pipeline.
  - Closes itself when a suggestion is executed, matching the pattern picker behaviour.
- **Changes made (GUI and actions):**
  - Added `lib/modelSuggestionGUI.py`:
    - Defines a new tag `user.model_suggestion_window_open`.
    - Defines a `Suggestion` dataclass (`name`, `recipe`) and `SuggestionGUIState` holding a list of suggestions.
    - `_refresh_suggestions_from_state()`:
      - Copies `GPTState.last_suggested_recipes` into `SuggestionGUIState.suggestions`, skipping incomplete entries.
    - `_run_suggestion(suggestion)`:
      - Uses `_parse_recipe` and the same axis maps from `lib/modelPatternGUI` to split the suggestion’s `recipe` into:
        - `static_prompt`, `completeness`, `scope`, `method`, `style`, `directional`.
      - Builds a `Match`-style object with `staticPrompt` and any axis modifiers mapped through `_axis_value` + `COMPLETENESS_MAP` / `SCOPE_MAP` / `METHOD_MAP` / `STYLE_MAP` / `DIRECTIONAL_MAP`.
      - Calls `modelPrompt(match)` to construct the Task/Constraints text.
      - Creates an `ApplyPromptConfiguration` using:
        - `model_source=create_model_source(user.model_default_source)`.
        - `model_destination=create_model_destination(user.model_default_destination)`.
      - Executes the recipe with `actions.user.gpt_apply_prompt(config)`.
      - Updates `GPTState.last_recipe` to a concise token-based recipe (`staticPrompt · completeness · scope · method · style` where present).
      - Calls `actions.user.model_prompt_recipe_suggestions_gui_close()` so the GUI closes after execution.
    - `@imgui.open() model_suggestion_gui(gui)`:
      - Renders a “Prompt recipe suggestions” window.
      - If there are no suggestions, shows a hint to run `model suggest`.
      - Otherwise, for each suggestion:
        - Renders a button labeled with the suggestion’s name; clicking it calls `_run_suggestion` and returns.
        - Shows the recipe tokens and an example `model …` grammar line for that recipe.
      - Provides a “Close” button that calls `model_prompt_recipe_suggestions_gui_close()`.
    - `@mod.action_class`:
      - `model_prompt_recipe_suggestions_gui_open()`:
        - Refreshes suggestions from `GPTState.last_suggested_recipes`.
        - If empty, notifies the user.
        - Closes related menus (pattern picker, prompt pattern picker, help) to avoid overlap.
        - Shows the suggestion GUI.
      - `model_prompt_recipe_suggestions_gui_close()`:
        - Hides the suggestion GUI.
- **Changes made (wiring and voice grammar):**
  - `GPT/gpt.py`:
    - After parsing suggestions in `gpt_suggest_prompt_recipes`, now:
      - Sets `GPTState.last_suggested_recipes = suggestions`.
      - If `suggestions` is non-empty, attempts to call `actions.user.model_prompt_recipe_suggestions_gui_open()`, catching exceptions so the raw text insert still works even if the GUI is unavailable.
  - `GPT/gpt-suggestions-gui.talon`:
    - Added a tag-scoped grammar:
      - `tag: user.model_suggestion_window_open`
      - `^close suggestions$: user.model_prompt_recipe_suggestions_gui_close()`
    - This mirrors the pattern picker’s “close patterns” voice command for the suggestion window.
- **ADR 008 impact:**
  - Delivers the core UX promised in ADR 008 for this repo:
    - `model suggest` now:
      - Calls GPT once to generate suggestions.
      - Parses and caches them.
      - Automatically opens a suggestion window listing them.
    - Clicking a suggestion:
      - Runs the corresponding `staticPrompt + axes + directional` recipe via the same machinery as patterns and prompt patterns.
      - Closes the suggestion window after execution.
  - Remaining GUI-related work is now incremental polish (additional voice commands, styling, and broader tests), rather than core behaviour.

## 2025-12-03 – Add `model suggestions` to reopen the last suggestion window (assistant-authored)

- **Focus area**: Provide a simple voice entrypoint to reopen the prompt recipe suggestion window without re-running `model suggest`, using the cached `GPTState.last_suggested_recipes`.
- **Changes made (grammar):**
  - Updated `GPT/gpt.talon` to add:
    - `{user.model} suggestions$: user.model_prompt_recipe_suggestions_gui_open()`
  - This command:
    - Calls the existing `model_prompt_recipe_suggestions_gui_open` action, which:
      - Refreshes `SuggestionGUIState` from `GPTState.last_suggested_recipes`.
      - Closes overlapping GUIs (pattern picker, prompt pattern picker, help).
      - Opens the “Prompt recipe suggestions” window.
- **ADR 008 impact:**
  - Improves everyday ergonomics:
    - After one `model suggest`, you can:
      - Use the suggestion window immediately, or
      - Close it and later say `model suggestions` to revisit the same set without another GPT call.
  - Keeps behaviour aligned with ADR 008’s intent of a small, discoverable surface for browsing and running suggested recipes while relying on the shared cached suggestions.

## 2025-12-03 – Add everyday usage examples to ADR 008 (assistant-authored)

- **Focus area**: Make ADR 008 more practically readable by adding a short “Everyday usage examples” section that shows how `model suggest`, the suggestion window, and `model suggestions` fit together in real workflows.
- **Changes made (docs):**
  - Extended `docs/adr/008-prompt-recipe-suggestion-assistant.md` with an “Everyday usage examples” section that:
    - Describes a basic flow:
      - Select text (or rely on `user.model_default_source`).
      - Say `model suggest` / `model suggest for <subject>`.
      - See 3–5 named recipes inserted as text and mirrored in the suggestion window.
    - Shows how to run a suggested recipe:
      - Click a button in the window.
      - The recipe is parsed into staticPrompt + axes + directional.
      - The prompt executes via the normal `model` pipeline.
      - The window closes on execution.
    - Explains how to reopen the last suggestion set:
      - Say `model suggestions` to reopen the window based on `GPTState.last_suggested_recipes`.
      - Use `close suggestions` to dismiss it.
- **ADR 008 impact:**
  - Improves on-the-page discoverability of the implemented behaviour, so future readers can quickly understand:
    - What `model suggest` does.
    - How the suggestion window behaves.
    - How `model suggestions` reuses cached results without another GPT call.
  - Keeps the ADR aligned with the current implementation, forming a clearer bridge between design and concrete usage.

## 2025-12-03 – Add run-by-index command for suggestions (assistant-authored)

- **Focus area**: Realise the optional “run by index” refinement in ADR 008 by allowing users to execute a specific suggestion by spoken index while the suggestion window is open.
- **Changes made (actions and grammar):**
  - `lib/modelSuggestionGUI.py`:
    - Added `model_prompt_recipe_suggestions_run_index(index: int)` to the `UserActions` class:
      - Refreshes suggestions from `GPTState.last_suggested_recipes`.
      - If there are no suggestions, notifies the user.
      - If the index is out of range, notifies with `No suggestion numbered {index}`.
      - Otherwise, calls `_run_suggestion` with `SuggestionGUIState.suggestions[index - 1]` (1-based indexing).
  - `GPT/gpt-suggestions-gui.talon`:
    - Extended the tag-scoped grammar with:
      - `^run suggestion <number>$: user.model_prompt_recipe_suggestions_run_index(number)`
    - This allows commands like “run suggestion 1” or “run suggestion 2” while the suggestion window is open, using Talon’s built-in `<number>` capture.
- **ADR 008 impact:**
  - Completes the previously “optional” run-by-index refinement for this repo:
    - Users can now:
      - Say `model suggest` to generate recipes and open the window.
      - Say `run suggestion <number>` to execute a specific suggestion without clicking.
  - Keeps behaviour bounded to the suggestion window’s scope (tag-based grammar), avoiding ambiguity with other `model` commands.

## 2025-12-03 – Add unit tests for run-by-index suggestion execution (assistant-authored)

- **Focus area**: Strengthen ADR 008’s guardrails by adding targeted tests for the new `run suggestion <number>` flow.
- **Changes made (tests):**
  - Added `tests/test_model_suggestion_gui.py`:
    - Uses the standard `bootstrap` pattern from this repo.
    - Imports `GPTState` and `SuggestionGUIState` plus `UserActions` from `lib/modelSuggestionGUI`.
    - Replaces `actions.app.notify`, `actions.user.gpt_apply_prompt`, and `actions.user.model_prompt_recipe_suggestions_gui_close` with `MagicMock` instances in `setUp`.
    - `test_run_index_executes_suggestion_and_closes_gui`:
      - Seeds `GPTState.last_suggested_recipes` with two suggestions.
      - Calls `UserActions.model_prompt_recipe_suggestions_run_index(2)`.
      - Asserts that:
        - `actions.user.gpt_apply_prompt` is called once.
        - `actions.user.model_prompt_recipe_suggestions_gui_close` is called once, confirming close-on-execute behaviour.
    - `test_run_index_out_of_range_notifies_and_does_not_run`:
      - Seeds `GPTState.last_suggested_recipes` with a single suggestion.
      - Calls `run_index(0)` and `run_index(3)` (both invalid).
      - Asserts:
        - `actions.app.notify` has been called at least once.
        - `actions.user.gpt_apply_prompt` is never called.
    - `test_run_index_with_no_suggestions_notifies`:
      - Leaves `GPTState.last_suggested_recipes` empty.
      - Calls `run_index(1)`.
      - Asserts:
        - `actions.app.notify` is called once.
        - `actions.user.gpt_apply_prompt` is never called.
- **ADR 008 impact:**
  - Provides direct test coverage for the run-by-index helper, confirming:
    - It respects cached suggestions.
    - It handles out-of-range indices and empty suggestions defensively.
    - It integrates with the close-on-execute contract for the suggestion window.
  - Moves ADR 008 closer to having end-to-end coverage of its core interaction patterns, with remaining test work focused on broader, multi-step flows if needed.

## 2025-12-03 – Mark ADR 008 core behaviour as implemented for this repo (assistant-authored)

- **Focus area**: Reconcile ADR 008’s status with the now-implemented suggestion flow (action, parsing, GUI, run-by-index) and make clear that remaining work is optional polish rather than missing core features.
- **Changes made (docs):**
  - Updated `docs/adr/008-prompt-recipe-suggestion-assistant.md` Status to:
    - “Implemented (core behaviour); optional refinements remain.”
  - Left the detailed “Implemented slices” section intact, now covering:
    - `model suggest` / `model suggest for <user.text>`.
    - Rich, list-backed meta-prompt construction.
    - Parsing and caching suggestions in `GPTState.last_suggested_recipes`.
    - The suggestion GUI with close-on-execute behaviour.
    - `model suggestions` and `run suggestion <number>` voice commands.
  - Left the “Remaining slices” section explicitly scoped to:
    - Higher-level, end-to-end tests for the suggest → GUI → execute path.
- **ADR 008 impact:**
  - Makes it explicit that, for this repo, ADR 008’s core design is realised:
    - Users can discover, inspect, and run suggested prompt recipes via voice and GUI.
  - Clearly separates optional testing/UX refinements from the implemented core, so future loops can target those refinements without questioning whether ADR 008 is “done” functionally.

## 2025-12-03 – Add targeted test for suggestion GUI auto-open (assistant-authored)

- **Focus area**: Add a small, higher-level test to confirm that `gpt_suggest_prompt_recipes` attempts to open the suggestion GUI when suggestions are present, as described in ADR 008’s UX flow.
- **Changes made (tests):**
  - Extended `tests/test_gpt_actions.py` with `test_gpt_suggest_prompt_recipes_opens_suggestion_gui_when_available`:
    - Patches `gpt_module.PromptSession`, `gpt_module.create_model_source`, and `actions.user.model_prompt_recipe_suggestions_gui_open`.
    - Stubs `source.get_text.return_value = "content"` so the action proceeds.
    - Sets `self.pipeline.complete.return_value` to a `PromptResult` whose `text` contains a single, valid `Name: … | Recipe: …` line.
    - Calls `gpt_module.UserActions().gpt_suggest_prompt_recipes("subject")`.
    - Asserts that `actions.user.model_prompt_recipe_suggestions_gui_open` is called exactly once, confirming that:
      - When suggestions are parsed successfully, the helper attempts to open the suggestion window.
      - GUI opening is part of the `model suggest` flow, in addition to inserting plain-text suggestions and caching them in `GPTState.last_suggested_recipes`.
- **ADR 008 impact:**
  - Provides an additional guardrail that the in-repo implementation matches ADR 008’s intended UX:
    - `model suggest` not only generates and caches recipes, but also brings up the suggestion picker when possible.
  - Further reduces the remaining “higher-level tests” slice to broader, multi-step flows if needed; the key auto-open behaviour is now explicitly covered.

## 2025-12-03 – Add GPTState reset tests for suggestion cache (assistant-authored)

- **Focus area**: Ensure that the cached suggestion state behaves well across resets, so future `model suggest` calls do not accidentally reuse stale recipes after a full state clear/reset.
- **Changes made (tests):**
  - Added `tests/test_model_state.py` with `GPTStateSuggestionResetTests`:
    - `test_clear_all_resets_last_suggested_recipes`:
      - Seeds `GPTState.last_suggested_recipes` with a dummy entry.
      - Calls `GPTState.clear_all()`.
      - Asserts that `last_suggested_recipes` is now `[]`.
    - `test_reset_all_resets_last_suggested_recipes`:
      - Seeds `GPTState.last_suggested_recipes` similarly.
      - Calls `GPTState.reset_all()`.
      - Asserts that `last_suggested_recipes` is `[]`.
- **ADR 008 impact:**
  - Confirms the intended behaviour already present in `lib/modelState`:
    - Both `clear_all` and `reset_all` drop any cached prompt recipe suggestions.
  - Reduces the risk that future refactors accidentally leave `last_suggested_recipes` “sticky” across resets, which would confuse the suggestion GUI and `model suggestions` flows.

## 2025-12-03 – Surface `model suggest` in the GPT readme (assistant-authored)

- **Focus area**: Make the prompt recipe suggestion flow discoverable outside ADRs by documenting it alongside other `model` helpers in `GPT/readme.md`.
- **Changes made (docs):**
  - Extended `GPT/readme.md` with a “Prompt recipe suggestions (ADR 008)” subsection under the quick-reference area, describing:
    - `model suggest` / `model suggest for <subject>`:
      - Proposes 3–5 `staticPrompt · completeness · scope · method · style · directional` recipes for the current source.
      - Inserts them as `Name: … | Recipe: …` lines.
      - Caches them and opens the “Prompt recipe suggestions” window.
    - How to use the suggestions window:
      - Click a suggestion to run it and close the window.
      - Say `run suggestion <number>` to execute a specific recipe by index.
      - Say `close suggestions` to dismiss the window.
    - `model suggestions`:
      - Reopens the suggestion window based on the last `model suggest` call without re-running the model.
- **ADR 008 impact:**
  - Exposes ADR 008’s functionality in the primary GPT readme, reducing reliance on ADR prose for everyday usage.
  - Helps users discover `model suggest` and related commands in the same place they learn about patterns, grammar help, and recipe recap.

## 2025-12-03 – Add end-to-end test for suggest → GUI-run path (assistant-authored)

- **Focus area**: Exercise the full data flow from `model suggest` through to executing a suggestion via the GUI helper, in a single test, to complement the unit tests for each piece.
- **Changes made (tests):**
  - Added `tests/test_integration_suggestions.py` with `SuggestionIntegrationTests`:
    - Uses `bootstrap` to load the Talon runtime.
    - In `setUp`, resets `GPTState`, replaces:
      - `actions.user.model_prompt_recipe_suggestions_gui_open` with a `MagicMock` (so GUI opening is inert).
      - `actions.user.gpt_apply_prompt` with a `MagicMock` (so we can assert execution).
      - Patches `gpt_module._prompt_pipeline` with a `MagicMock` pipeline.
    - `test_suggest_then_run_index_executes_recipe`:
      - Arranges the pipeline to return a `PromptResult` whose `.text` is:
        - `Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog`.
      - Patches `gpt_module.create_model_source` and `PromptSession` so:
        - `source.get_text()` returns `"content"`.
        - The session has a `_destination` of `"paste"`.
      - Calls `gpt_module.UserActions().gpt_suggest_prompt_recipes("subject")`:
        - This runs the suggestion logic, populates `GPTState.last_suggested_recipes`, and (in production) would also attempt to open the GUI.
      - Then calls `suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)`:
        - This reads from the cached suggestions, parses the recipe, and executes it via `gpt_apply_prompt`.
      - Asserts that:
        - `actions.user.gpt_apply_prompt.assert_called_once()`.
        - `GPTState.last_recipe` contains both the static prompt token (`describe`) and an axis token (`full`), confirming that the recipe parsing and execution path ran.
- **ADR 008 impact:**
  - Provides a simple end-to-end sanity check that:
    - Suggestions produced by `model suggest` are parsed and cached.
    - The suggestion GUI helper can run one of those cached recipes successfully.
  - Leaves more exhaustive multi-step or UI-level tests as optional, but this test gives confidence that the core suggest → execute path is wired correctly.

