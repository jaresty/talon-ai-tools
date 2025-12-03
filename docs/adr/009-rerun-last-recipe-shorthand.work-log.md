# 009 – Rerun-Last-Recipe Shorthand – Work-log

This work-log tracks concrete changes made in this repo under ADR 009.

## 2025-12-04 – Initial `model again` wiring and state shaping (assistant-authored)

- **Focus area**: Implement a first, end-to-end slice of the `model again` shorthand that can rerun the last recipe with optional positional overrides, and shape `GPTState` so future loops can build additional ergonomics on top of it.
- **Changes made (state):**
  - Extended `lib/modelState.GPTState` with structured last-recipe fields:
    - `last_static_prompt`, `last_completeness`, `last_scope`, `last_method`, `last_style`, all stored as short tokens.
    - Kept `last_recipe` as the human-readable `staticPrompt · [axes…]` string and `last_directional` as the short directional token.
    - Ensured all of these fields are cleared in both `clear_all` and `reset_all`.
  - Updated all code paths that set `last_recipe` to also keep the structured fields in sync:
    - `lib/talonSettings.modelPrompt` now:
      - Computes short tokens for each effective axis via `_axis_recipe_token`.
      - Writes both the joined `last_recipe` string and the individual `last_*` fields.
      - Normalises the stored directional lens through `_axis_recipe_token("directional", …)`.
    - `lib/modelPatternGUI._run_pattern`, `lib/modelSuggestionGUI._run_suggestion`, and `lib/modelPromptPatternGUI._run_pattern` now:
      - Set `last_recipe` from the token-based recipe they execute.
      - Populate `last_static_prompt` and the per-axis `last_*` fields with the corresponding short tokens.
      - Update `last_directional` with the directional lens token (or `""`).
- **Changes made (actions and grammar):**
  - Added a new `user` action in `GPT/gpt.py`:
    - `gpt_rerun_last_recipe(static_prompt: str, completeness: str, scope: str, method: str, style: str, directional: str) -> None` that:
      - Validates that a last recipe exists; otherwise notifies: `"GPT: No last recipe available to rerun"`.
      - Reads base tokens from `GPTState.last_static_prompt` / `last_*` / `last_directional`.
      - Applies any non-empty overrides passed from Talon (static prompt and up to one value per axis/lens).
      - Builds a lightweight `Match` object with:
        - `staticPrompt` set to the resulting static prompt token.
        - `completenessModifier` / `scopeModifier` / `methodModifier` / `styleModifier` / `directionalModifier` set by mapping tokens through the same axis maps used by pattern/suggestion GUIs (`_axis_value` + `COMPLETENESS_MAP` / `SCOPE_MAP` / `METHOD_MAP` / `STYLE_MAP` / `DIRECTIONAL_MAP`).
      - Calls `modelPrompt(match)` to construct the Task/Constraints text and update recap state.
      - Builds an `ApplyPromptConfiguration` with:
        - `please_prompt` from `modelPrompt(match)`.
        - `model_source=create_model_source(user.model_default_source)`.
        - `model_destination=create_model_destination(user.model_default_destination)`.
      - Executes the rerun through `actions.user.gpt_apply_prompt(config)`.
  - Wired new grammar in `GPT/gpt.talon`:
    - `^{user.model} again$: user.gpt_rerun_last_recipe("", "", "", "", "", "")` for an exact rerun.
    - `^{user.model} again {user.staticPrompt} [{user.completenessModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.styleModifier}] [{user.directionalModifier}]$`:
      - Allows overriding the static prompt and any subset of axes/lens in positional order.
    - `^{user.model} again [{user.completenessModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.styleModifier}] [{user.directionalModifier}]$`:
      - Allows reusing the last static prompt while overriding any subset of axes/lens.
    - In both “with modifiers” rules, optional captures use `value or ""` when calling `gpt_rerun_last_recipe`, so omitted segments simply fall back to the last stored tokens.
- **Changes made (quick help / recap alignment):**
  - Left `gpt_show_last_recipe` behaviour aligned with ADR 006/009:
    - It still shows `Last recipe: <tokens> · <directional>` when a directional lens is present, reading the lens from `GPTState.last_directional`.
- **ADR 009 impact:**
  - Delivers the core behaviour described in ADR 009:
    - `model again` reruns the last recipe without requiring the user to restate it.
    - `model again <tokens…>` lets the user tweak one or more axes/directional (and optionally the static prompt) in a single, positional utterance.
  - Keeps all recipe semantics flowing through the existing `modelPrompt` + `gpt_apply_prompt` pipeline and axis maps, so system prompts, constraints text, and last-recipe recap remain consistent with other entrypoints (spoken grammar, patterns, and suggestions).
  - Sets up structured last-recipe state in `GPTState` that future loops can reuse (for example, richer quick help, status snapshots, or additional rerun variants) without re-parsing the recap string.

## 2025-12-04 – Tests for `gpt_rerun_last_recipe` behaviour (assistant-authored)

- **Focus area**: Add targeted tests around the new `gpt_rerun_last_recipe` action to ensure it behaves safely when no last recipe is available, and that it correctly applies overrides on top of the stored last-recipe tokens when state is present.
- **Changes made (tests):**
  - Extended `tests/test_gpt_actions.py` in the `GPTActionPromptSessionTests` suite with:
    - `test_gpt_rerun_last_recipe_without_state_notifies_and_returns`:
      - Calls `GPTState.reset_all()` to ensure no last recipe is stored.
      - Patches `gpt_module.notify`, `actions.user.gpt_apply_prompt`, and `gpt_module.modelPrompt`.
      - Invokes `gpt_module.UserActions.gpt_rerun_last_recipe("", "", "", "", "", "")`.
      - Asserts:
        - `notify` is called once to report the lack of a last recipe.
        - Neither `gpt_apply_prompt` nor `modelPrompt` is called, so no prompt is executed when state is missing.
    - `test_gpt_rerun_last_recipe_applies_overrides_on_last_tokens`:
      - Seeds `GPTState` with a known token-based last recipe:
        - `last_recipe = "describe · full · relations · cluster · bullets"`.
        - `last_static_prompt = "describe"`, plus per-axis tokens and `last_directional = "fog"`.
      - Patches:
        - `gpt_module._axis_value_from_token` to echo its token argument (so tests can assert exact tokens).
        - `gpt_module.modelPrompt` to return a sentinel string `"PROMPT"`.
        - `gpt_module.create_model_source` / `create_model_destination` to return MagicMocks for source/destination.
        - `actions.user.gpt_apply_prompt` to observe the configuration passed in.
      - Calls `gpt_module.UserActions.gpt_rerun_last_recipe("todo", "gist", "", "", "", "rog")` to:
        - Override static prompt, completeness, and directional lens.
        - Reuse the last scope/method/style tokens.
      - Asserts that:
        - `_axis_value_from_token` is called with all expected tokens: `gist`, `relations`, `cluster`, `bullets`, `rog`.
        - `modelPrompt` receives a match object with:
          - `staticPrompt == "todo"`.
          - `completenessModifier == "gist"`.
          - `scopeModifier == "relations"`.
          - `methodModifier == "cluster"`.
          - `styleModifier == "bullets"`.
          - `directionalModifier == "rog"`.
        - `actions.user.gpt_apply_prompt` is called once with an `ApplyPromptConfiguration` whose:
          - `please_prompt` is `"PROMPT"`.
          - `model_source` and `model_destination` are exactly the mocks returned by `create_model_source` / `create_model_destination`.
- **ADR 009 impact:**
  - Confirms that `gpt_rerun_last_recipe` respects the guardrail of “no last recipe, no rerun”.
  - Validates that the action merges overrides with stored last-recipe tokens in the way ADR 009 describes, and that it executes through the same `modelPrompt` / `gpt_apply_prompt` path as other entrypoints.
  - Provides a test harness that will catch regressions if the rerun shorthand, last-recipe state, or axis mapping logic are modified in future loops.

## 2025-12-04 – ADR 009 reconciliation and everyday usage docs (assistant-authored)

- **Focus area**: Bring ADR 009 fully in line with the implemented `model again` grammar and `gpt_rerun_last_recipe` signature, and add concrete usage examples so future readers can see how the shorthand behaves in practice.
- **Changes made (ADR text):**
  - Updated `docs/adr/009-rerun-last-recipe-shorthand.md`:
    - Status:
      - Marked ADR 009 as “Accepted” to reflect that the core behaviour and guardrails are now implemented and covered by tests in this repo.
    - Grammar section:
      - Replaced the earlier conceptual capture-based design with the **actual Talon rules** from `GPT/gpt.talon`:
        - `^{user.model} again$` → exact rerun.
        - `^{user.model} again {user.staticPrompt} […]` → override static prompt plus optional axes/directional.
        - `^{user.model} again […]` → reuse last static prompt and override any subset of axes/directional.
      - Clarified that:
        - Each axis capture appears at most once in the relevant rule, so Talon enforces “one value per axis”.
        - All segments after `again` are optional and passed as `""` when omitted.
    - Stored state section:
      - Switched from a “could do either” description to documenting the **implemented approach**:
        - Explicit `GPTState` fields: `last_static_prompt`, `last_completeness`, `last_scope`, `last_method`, `last_style`, `last_directional`, all short tokens.
    - Rerun action section:
      - Updated the signature to match the implementation:
        - `user.gpt_rerun_last_recipe(static_prompt, completeness, scope, method, style, directional)`.
      - Described the override semantics in terms of these six positional arguments rather than a conceptual override object.
    - Consequences / planned slices:
      - Noted that state maintenance now covers `last_recipe`, `last_directional`, and the structured `last_*` fields.
      - Updated the “planned slices” to reflect the implemented action, grammar, and tests, and to frame quick help / README updates as optional polish.
  - Added an “Everyday usage examples” section that:
    - Shows how to:
      - Rerun exactly with `model again`.
      - Tweak a couple of axes (for example, `model again gist fog`).
      - Change static prompt plus some axes (for example, `model again todo gist fog`).
      - Swap method/style and directional (for example, `model again steps tight rog`).
    - Makes explicit which parts of the last recipe are preserved vs. overridden in each example.
- **ADR 009 impact:**
  - ADR 009 now accurately documents:
    - The exact grammar and action signature used in this repo.
    - The structured last-recipe state that powers `model again`.
  - The new examples give a quick mental model for how to iterate on recipes with minimal speech, aligning the design with how the feature actually behaves in Talon.

## 2025-12-04 – Tests for structured last-recipe state (assistant-authored)

- **Focus area**: Strengthen guardrails around the structured last-recipe fields introduced for `model again` by asserting they are kept in sync with `modelPrompt` and are fully cleared by `clear_all`.
- **Changes made (tests):**
  - Updated `tests/test_talon_settings_model_prompt.py` in the `ModelPromptModifiersTests` suite to cover the new `GPTState` fields:
    - Extended `test_clear_all_resets_last_recipe_and_response` to assert that after `GPTState.clear_all()`:
      - `last_directional`, `last_static_prompt`, `last_completeness`, `last_scope`, `last_method`, and `last_style` are all reset to `""` alongside `last_recipe` and `last_response`.
    - Extended `test_model_prompt_updates_last_recipe_with_spoken_modifiers` to assert that, after a `modelPrompt` call with explicit axis modifiers:
      - `GPTState.last_static_prompt == "fix"`.
      - `GPTState.last_completeness == "skim"`.
      - `GPTState.last_scope == "narrow"`.
      - `GPTState.last_method == "steps"`.
      - `GPTState.last_style == "plain"`.
      - `GPTState.last_directional == "DIR"` (since the sentinel “DIR” is not in the directional list, it remains as-is).
    - Extended `test_model_prompt_updates_last_recipe_with_profile_axes` to assert that, when axes come from the `todo` profile:
      - `GPTState.last_static_prompt == "todo"`.
      - `GPTState.last_completeness == "gist"`.
      - `GPTState.last_scope == "focus"`.
      - `GPTState.last_method == "steps"`.
      - `GPTState.last_style == "checklist"`.
      - `GPTState.last_directional == "DIR"`.
- **ADR 009 impact:**
  - Confirms that the structured `last_*` fields stay in lockstep with the token-based `last_recipe` string for both spoken-modifier and profile-driven cases, as required for `model again` to behave predictably.
  - Ensures `clear_all` leaves no stale structured state behind, so rerun helpers and quick help never see mismatched or partially reset recipe data.

## 2025-12-04 – Surface `model again` in GPT README (assistant-authored)

- **Focus area**: Expose the `model again` shorthand from ADR 009 in the primary GPT README so users discover it alongside `model last recipe`, quick help, patterns, and suggestions.
- **Changes made (docs):**
  - Updated `GPT/readme.md` to add a “Rerun last recipe shorthand (ADR 009)” subsection under the in-Talon helpers:
    - Describes:
      - `model last recipe` as a recap helper (static prompt + axes + directional lens).
      - `model again` as an exact rerun of the last recipe.
      - `model again [<staticPrompt>] [axis tokens…]` as a way to:
        - Override static prompt, completeness, scope, method, style, and/or directional lens while reusing the rest of the last recipe.
    - Includes concrete examples:
      - `model again gist fog` → change completeness and lens only.
      - `model again todo gist fog` → change static prompt + completeness (and lens) while reusing last scope/method/style.
      - `model again steps tight rog` → change method/style/lens while reusing last static prompt/completeness/scope.
- **ADR 009 impact:**
  - Brings the user-facing README in line with ADR 009 and the implemented grammar, so `model again` is discoverable without reading the ADR itself.
  - Helps users understand how to iterate on successful recipes quickly using the shorthand, reinforcing the “positional, token-based tweaks” design goal from ADR 009.

## 2025-12-04 – Quick help hint for `model again` (assistant-authored)

- **Focus area**: Make the `model again` shorthand discoverable directly from the quick-help UI that already shows the last recipe and an exact `model …` line.
- **Changes made (quick help GUI):**
  - Updated `lib/modelHelpGUI.py` in the `model_help_gui` renderer:
    - In the `elif GPTState.last_recipe:` branch, after:
      - `Last recipe: <tokens>` and
      - `Say: model …` lines,
      added a hint:
      - `Tip: Say 'model again' to rerun this recipe, or add axis tokens (for example, 'model again gist fog') to tweak it.`
- **ADR 009 impact:**
  - Connects the last-recipe recap surface from ADR 006 with the new rerun shorthand from ADR 009:
    - When a user sees a successful recipe in quick help, they are now explicitly prompted that they can say `model again` or `model again …` to repeat or adapt it.
  - Further reduces recall burden by surfacing the shorthand exactly where users are already inspecting recipes and grammar, without requiring them to consult ADRs or the README.

## 2025-12-04 – ADR 009 status snapshot (assistant-authored)

- **Focus area**: Reconcile ADR 009’s status and “Status and future work” section with the implementation and tests that now exist in this repo, and add a concise “Current status” snapshot for future loops.
- **Changes made (ADR text):**
  - Updated `docs/adr/009-rerun-last-recipe-shorthand.md`:
    - Marked the ADR as **Accepted** in the “Status and future work” section, reflecting that:
      - `model again` and `gpt_rerun_last_recipe` are implemented.
      - Structured last-recipe state and tests are in place.
    - Adjusted the “Quick help integration and docs” slice to note that:
      - Quick help mentions `model again`.
      - `GPT/readme.md` includes `model again` examples.
    - Added a “Current status in this repo” subsection that summarises:
      - What is completed and in use (state, grammar, action, tests, README and quick-help integration).
      - What remains optional/deferred (multi-recipe history, additional voice shortcuts built on the same state).
- **ADR 009 impact:**
  - Provides a clear, in-document snapshot of ADR 009’s implementation state for this repo, so future contributors do not need to infer status from scattered tests and work-log entries.
  - Confirms that remaining ideas (like history or extra shorthands) are explicitly out-of-scope for this ADR and would require new decisions, avoiding scope creep.

## 2025-12-04 – Tests for `gpt_show_last_recipe` recap behaviour (assistant-authored)

- **Focus area**: Add explicit tests around `gpt_show_last_recipe` so that the last-recipe recap notifications stay aligned with ADR 006/009, including the directional lens when present.
- **Changes made (tests):**
  - Extended `tests/test_gpt_actions.py` in `GPTActionPromptSessionTests` with three tests:
    - `test_gpt_show_last_recipe_without_state_notifies_and_returns`:
      - Calls `GPTState.reset_all()` to ensure there is no last recipe.
      - Patches `gpt_module.notify` and `actions.app.notify`.
      - Invokes `gpt_module.UserActions().gpt_show_last_recipe()`.
      - Asserts:
        - `notify` is called once (with the “no last recipe available” message).
        - `actions.app.notify` is **not** called (no recap is shown when there is no recipe).
    - `test_gpt_show_last_recipe_includes_directional_when_present`:
      - Seeds `GPTState.last_recipe` with:
        - `"describe · full · relations · cluster · bullets"`.
      - Sets `GPTState.last_directional = "fog"`.
      - Patches `actions.app.notify` and calls `gpt_show_last_recipe`.
      - Asserts that the notification is:
        - `"Last recipe: describe · full · relations · cluster · bullets · fog"`.
    - `test_gpt_show_last_recipe_omits_directional_when_absent`:
      - Seeds `GPTState.last_recipe` as above but leaves `last_directional = ""`.
      - Patches `actions.app.notify` and calls `gpt_show_last_recipe`.
      - Asserts that the notification is:
        - `"Last recipe: describe · full · relations · cluster · bullets"`.
- **ADR 009 impact:**
  - Confirms that `gpt_show_last_recipe`:
    - Respects the “no last recipe” guardrail.
    - Produces recap text that exactly matches the grammar line shown in quick help (including directional lens when set), as described in ADR 006 and ADR 009.
  - Provides a safety net for future refactors to `gpt_show_last_recipe` or the last-recipe state to ensure the recap experience remains consistent with the rerun shorthand (`model again`) and quick-help displays.

## 2025-12-04 – Cross-link ADR 009 from GPT README (assistant-authored)

- **Focus area**: Make it easier for users and contributors to discover ADR 009 from the main GPT README alongside the other core ADRs.
- **Changes made (docs):**
  - Updated the ADR list in `GPT/readme.md` to include:
    - `docs/adr/009-rerun-last-recipe-shorthand.md` alongside ADR 005 and ADR 006, with wording adjusted to “modifier axes, defaults, helpers, and rerun shorthand”.
- **ADR 009 impact:**
  - Ensures ADR 009 is discoverable from the central GPT README, just like ADR 005 and ADR 006, so readers looking for implementation details or rationale behind `model again` can find the design quickly.
  - Completes a small documentation loop by cross-linking the ADR from both README and the feature surfaces it describes (quick help and commands).

## 2025-12-04 – Clarify ADR 009’s interaction with ADR 006 and ADR 008 (assistant-authored)

- **Focus area**: Make ADR 009’s relationship to the pattern/recap helpers (ADR 006) and the prompt recipe suggestion assistant (ADR 008) explicit, so readers understand how `model again` composes with those features.
- **Changes made (ADR text):**
  - Updated `docs/adr/009-rerun-last-recipe-shorthand.md` with a new “Interaction with other ADRs” subsection that:
    - Describes ADR 006 interaction:
      - `model again` reuses the same `last_recipe` and directional lens state introduced for recap, and appears alongside `model last recipe` / `model show grammar` in quick help.
      - Pattern pickers and prompt-specific pattern menus remain the primary *discovery* surfaces; `model again` provides fast iteration *after* running a pattern.
    - Describes ADR 008 interaction:
      - Running a suggested recipe updates `last_recipe` / `last_directional` and the structured tokens.
      - `model again` can then tweak that suggestion without reopening the suggestion GUI or re-calling the model for suggestions.
      - Keeps responsibilities clear:
        - `model suggest` → choose recipes.
        - `model again` → iterate on the last chosen recipe.
- **ADR 009 impact:**
  - Clarifies how `model again` is intended to layer on top of existing discovery and recap tools rather than replace them.
  - Provides future readers a succinct mental model of the interplay between ADR 006, ADR 008, and ADR 009 when reasoning about changes in this area.

## 2025-12-04 – Integration test for suggest → run → again flow (assistant-authored)

- **Focus area**: Add a higher-level test that exercises the flow from prompt suggestions into execution and then into the `model again` shorthand, to validate that the shared last-recipe state works as intended across ADR 008 and ADR 009.
- **Changes made (tests):**
  - Extended `tests/test_integration_suggestions.py` in `SuggestionIntegrationTests` with:
    - `test_suggest_then_again_merges_overrides`:
      - Uses the same suggestion text as the existing integration test:
        - `"Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog"`.
      - First calls `gpt_suggest_prompt_recipes("subject")` with patched `create_model_source` and `PromptSession` to:
        - Populate `GPTState.last_suggested_recipes`.
      - Calls `model_prompt_recipe_suggestions_run_index(1)` to:
        - Execute the first suggested recipe via the suggestion GUI helper.
        - Seed `GPTState`’s structured last-recipe fields from that run.
      - Records the current `actions.user.gpt_apply_prompt` call count.
      - Then, with:
        - `gpt_module._axis_value_from_token` patched to echo tokens.
        - `gpt_module.modelPrompt` patched to return `"PROMPT-AGAIN"`.
        - `gpt_module.create_model_source` / `create_model_destination` patched to return new mocks for the rerun.
        calls:
        - `gpt_module.UserActions.gpt_rerun_last_recipe("", "gist", "", "", "", "rog")` to:
          - Keep static prompt/scope/method/style from the last recipe.
          - Override completeness to `gist` and directional to `rog`.
      - Asserts that:
        - `actions.user.gpt_apply_prompt` is called one additional time with a config whose:
          - `please_prompt == "PROMPT-AGAIN"`.
          - `model_source` / `model_destination` are exactly the rerun mocks.
        - `GPTState.last_completeness == "gist"` and `GPTState.last_directional == "rog"` after the rerun.
- **ADR 009 impact:**
  - Provides an end-to-end test that spans ADR 008 (suggestions) and ADR 009 (rerun shorthand), confirming:
    - Running a suggestion populates the last-recipe state used by `model again`.
    - `gpt_rerun_last_recipe` correctly merges overrides on top of a suggestion-derived recipe and executes through the normal pipeline.
  - Strengthens confidence that `model again` behaves correctly in realistic flows, not just in isolated unit tests.

## 2025-12-04 – Align README description of `model last recipe` with ADR 009 (assistant-authored)

- **Focus area**: Ensure the GPT README’s description of `model last recipe` matches the behaviour specified by ADR 006/009 and implemented in `gpt_show_last_recipe` (which now includes the directional lens).
- **Changes made (docs):**
  - Updated `GPT/readme.md` so the earlier recap bullet under “In-Talon helpers for discoverability” reads:
    - `model last recipe` – shows the last prompt recipe **(static prompt plus effective completeness/scope/method/style and directional lens)** in a notification, even if the confirmation GUI is closed.
  - This matches the later ADR 009 section in the README, which already mentioned the directional lens explicitly.
- **ADR 009 impact:**
  - Keeps the user-facing description of `model last recipe` consistent across the README and with the actual recap behaviour (including directional).
  - Avoids confusion by ensuring both recap and rerun (`model again`) surfaces are documented as working over the full `staticPrompt + axes + directional` recipe, as intended in ADR 009.

## 2025-12-04 – Clarify no-last-recipe guardrail in ADR 009 (assistant-authored)

- **Focus area**: Make the no-last-recipe guardrail for `model again` explicit in ADR 009 so the user-facing failure mode matches the implementation and tests.
- **Changes made (ADR text):**
  - Updated the “Rerun action” section in `docs/adr/009-rerun-last-recipe-shorthand.md` to spell out that:
    - When there is no stored last recipe/directional token, this repo’s implementation of `gpt_rerun_last_recipe`:
      - Calls `notify("GPT: No last recipe available to rerun")`.
      - Returns without sending any model request.
- **ADR 009 impact:**
  - Aligns the written design with the behaviour already validated by `test_gpt_rerun_last_recipe_without_state_notifies_and_returns`.
  - Makes the guardrail behaviour clear to future readers so they understand what `model again` does when invoked before any recipe has been run.

## 2025-12-04 – Clarify source/destination semantics for `model again` (assistant-authored)

- **Focus area**: Make explicit in ADR 009 that `model again` uses the same source/destination selection model as other `model` commands, rather than introducing any special handling.
- **Changes made (ADR text):**
  - Updated the “Rerun action” section in `docs/adr/009-rerun-last-recipe-shorthand.md` to state that:
    - `gpt_rerun_last_recipe` builds its `ApplyPromptConfiguration` with:
      - `model_source` derived from `user.model_default_source` via `create_model_source`, exactly like other `model` flows.
      - `model_destination` derived from `user.model_default_destination` via `create_model_destination`.
- **ADR 009 impact:**
  - Clarifies that `model again`:
    - Reuses the same source (selection/clipboard/etc.) and destination (paste/above/below/browser, etc.) semantics as other `model` commands.
    - Only changes the **recipe** (static prompt + axes + directional), not where text is read from or where results go.
  - Reduces potential confusion for readers who might otherwise suspect `model again` had its own source/destination logic separate from the rest of the pipeline.

## 2025-12-04 – Add `model again` to quick-reference recap list (assistant-authored)

- **Focus area**: Make the `model again` shorthand visible in the GPT README’s quick-reference recap list alongside `model last recipe` and the confirmation GUI `Recipe:` line.
- **Changes made (docs):**
  - Updated the “Quick reference (ADR 006 commands)” section in `GPT/readme.md` so the Recap bullets now include:
    - `model last recipe`
    - `model again` / `model again …`
    - Confirmation GUI `Recipe:` line
- **ADR 009 impact:**
  - Ensures the rerun shorthand appears in the same condensed reference block as other recap helpers, improving discoverability for users skimming the quick-reference section.
  - Keeps the README’s quick-reference aligned with the detailed `Rerun last recipe shorthand (ADR 009)` subsection and the ADR itself.

## 2025-12-04 – Add cross-ADR “See also” links to ADR 009 (assistant-authored)

- **Focus area**: Make it clearer, from the top of ADR 009, which other ADRs it builds on.
- **Changes made (ADR text):**
  - Added a small “See also” list under the header of `docs/adr/009-rerun-last-recipe-shorthand.md` that links to:
    - ADR 005 (orthogonal prompt modifiers and defaults).
    - ADR 006 (pattern picker and recap).
    - ADR 008 (prompt recipe suggestion assistant).
- **ADR 009 impact:**
  - Gives readers immediate pointers to the related ADRs that define the axis grammar, recap helpers, and suggestion machinery that `model again` builds on.
  - Complements the existing “Interaction with other ADRs” section with a lightweight navigational aid at the top of the document.

## 2025-12-04 – Clarify repo-local scope of ADR 009 (assistant-authored)

- **Focus area**: Make it explicit that ADR 009’s design is scoped to this Talon integration, and similar patterns elsewhere should use repo-appropriate ADRs.
- **Changes made (ADR text):**
  - Added a short note in the Context section of `docs/adr/009-rerun-last-recipe-shorthand.md` stating that:
    - ADR 009 describes how the rerun shorthand is implemented in this repo’s Talon integration.
    - Other environments that borrow the idea may need their own, context-specific ADRs.
- **ADR 009 impact:**
  - Reduces the risk of readers over-generalising this ADR beyond its intended scope.
  - Encourages other codebases to capture their own rerun designs rather than assuming this repo’s choices are universally applicable.

## 2025-12-04 – Add safety considerations for `model again` usage (assistant-authored)

- **Focus area**: Highlight practical safety considerations when using `model again`, especially in destinations that modify text directly.
- **Changes made (ADR text):**
  - Added a “Safety considerations” subsection to `docs/adr/009-rerun-last-recipe-shorthand.md` noting that:
    - `model again` uses the same source and destination model as other `model` commands (selection vs. clipboard, paste vs. browser, etc.).
    - In destructive destinations (for example, pasting fixes directly into an editor), users should:
      - Confirm that the active source (selection or clipboard) is what they expect.
      - Confirm that the active destination window is the one they intend to modify.
- **ADR 009 impact:**
  - Makes the operational risk profile of `model again` explicit, particularly when re-running prompts that change code or documents in place.
  - Encourages slightly more deliberate usage without adding new guardrails to the implementation.

## 2025-12-04 – Loop closure note for ADR 009 (assistant-authored)

- **Focus area**: Record that ADR 009’s in-repo objectives are complete and that further work should proceed via new ADRs or concrete bugfixes.
- **Changes made (docs):**
  - Added this “Loop closure” entry to the work-log to state explicitly:
    - Behaviour, UX surfaces, validation, and documentation described by ADR 009 are all implemented in this repo.
    - Any new features in this space (for example, recipe history or additional shorthands) should be proposed as separate ADRs.
    - Future edits to ADR 009 should be limited to regression fixes or clarifications where implementation and ADR drift out of sync.
- **ADR 009 impact:**
  - Provides a clear stopping point for ADR 009 loops in this repo.
  - Signals to future contributors that, absent regressions or new ADRs, ADR 009 should now be treated as reference documentation rather than an active design space.




## 2025-12-04 – Document validation strategy for ADR 009 (assistant-authored)

- **Focus area**: Capture, in ADR 009 itself, which tests in this repo exercise the `model again` behaviour and its supporting state, so future maintainers can quickly see how the design is validated.
- **Changes made (ADR text):**
  - Added a “Validation and tests in this repo” subsection to `docs/adr/009-rerun-last-recipe-shorthand.md` that lists:
    - `tests/test_talon_settings_model_prompt.py` as covering:
      - Population of `GPTState.last_recipe` and structured `last_*` fields via `modelPrompt`.
      - Reset behaviour via `clear_all`.
    - `tests/test_gpt_actions.py` as covering:
      - Guardrails and override semantics for `gpt_rerun_last_recipe`.
      - Recap behaviour for `gpt_show_last_recipe`, including directional lenses.
    - `tests/test_integration_suggestions.py` as covering:
      - Suggestion execution updating last-recipe state.
      - The suggest → run → again path (`test_suggest_then_again_merges_overrides`), confirming that `model again` can tweak suggestion-derived recipes and that structured state is updated accordingly.
- **ADR 009 impact:**
  - Makes the connection between ADR 009 and its test coverage explicit, simplifying future changes and reviews in this area.
  - Helps ensure that modifications to `modelPrompt`, suggestions, or `model again` are evaluated against the right set of tests.

## 2025-12-04 – Cross-reference ADR 009 from ADR 006 and ADR 008 (assistant-authored)

- **Focus area**: Make the relationship between ADR 009 and the earlier ADRs (pattern/recap and suggestions) discoverable directly from those ADRs.
- **Changes made (docs):**
  - `docs/adr/006-pattern-picker-and-recap.md`:
    - In the “For future changes in this repo” section, added a note that:
      - Recap helpers (`model last recipe`, `model show grammar`) and the rerun shorthand from ADR 009 (`model again`) both depend on the shared `last_recipe` + directional state.
  - `docs/adr/008-prompt-recipe-suggestion-assistant.md`:
    - In the “Alternatives considered → Rely solely on pattern pickers and prompt menus (ADR 006)” section, extended the Cons to mention:
      - Pattern pickers alone do not provide a shorthand for iterating on the last recipe; ADR 009’s `model again` rerun shorthand fills that gap.
- **ADR 009 impact:**
  - Ensures readers of ADR 006 and ADR 008 can easily discover ADR 009 when thinking about recap or iteration flows.
  - Reinforces the separation of concerns:
    - ADR 006 → discovery via patterns and recap.
    - ADR 008 → selection via suggestions.
    - ADR 009 → iteration via `model again`.

## 2025-12-04 – “When to use what” guidance for ADR 009 (assistant-authored)

- **Focus area**: Provide a concise, in-ADR guide to when to reach for patterns, suggestions, or `model again`, tying together ADR 006, ADR 008, and ADR 009 in practical terms.
- **Changes made (ADR text):**
  - Added a “Choosing between patterns, suggestions, and `model again`” subsection to `docs/adr/009-rerun-last-recipe-shorthand.md` that:
    - Recommends:
      - Patterns / prompt pattern menus (ADR 006) for curated, predesigned recipes and exploring the space for a given static prompt.
      - Suggestions (ADR 008) when you have content + subject and want GPT to propose suitable recipes.
      - `model again` (ADR 009) once you already have a successful recipe and want to rerun or tweak it without rebuilding the entire grammar line.
- **ADR 009 impact:**
  - Gives readers a quick decision aid for which helper to use in different situations, instead of having to infer this from three separate ADRs.
  - Reinforces ADR 009’s role as an iteration tool rather than another discovery surface.

## 2025-12-04 – Add a one-line mental model for `model again` (assistant-authored)

- **Focus area**: Provide a compact, memorable summary of the `model again` shorthand directly in ADR 009’s Decision section.
- **Changes made (ADR text):**
  - Added a short “In short:” line under the Decision bullets in `docs/adr/009-rerun-last-recipe-shorthand.md`:
    - `model again [<staticPrompt>] [axis tokens…] = last recipe ⊕ your spoken overrides (per axis).`
- **ADR 009 impact:**
  - Gives readers a quick mental model of the shorthand without reading the full design:
    - Start from the last recipe, then apply whatever axes/static-prompt overrides you speak.
  - Reinforces the positional, per-axis override semantics in a single, easy-to-remember line.

## 2025-12-04 – Mark ADR 009’s core objectives as complete in this repo (assistant-authored)

- **Focus area**: Explicitly state in ADR 009 that, for this repo, its core behavioural and UX objectives are now complete and further work should go through new ADRs.
- **Changes made (ADR text):**
  - Extended the “Status and future work” section in `docs/adr/009-rerun-last-recipe-shorthand.md` with a short paragraph noting that:
    - `model again` is implemented, wired through the existing pipeline, tested, and surfaced in primary help surfaces.
    - The ADR’s core objectives are considered complete for this repo.
    - Future changes in this area (multi-recipe history, additional shorthands, etc.) should be treated as follow-on ADRs rather than silent extensions.
- **ADR 009 impact:**
  - Clarifies that `B_a` for ADR 009 in this repo is effectively exhausted; what remains are optional, out-of-scope enhancements.
  - Helps future contributors decide when they should draft a new ADR instead of quietly expanding the scope of this one.

### Current loop guidance for ADR 009

For future ADR loops in this repo:

- Treat ADR 009 as **complete** unless:
  - You are explicitly working on a new ADR that builds on its state or grammar, or
  - You discover a regression in `model again` / recap behaviour that needs fixing.
- When in doubt, prefer:
  - Updating or adding **new** ADRs for multi-recipe history or additional shorthands, and
  - Using ADR 009 primarily as a reference for how `model again` is expected to behave.

## 2025-12-04 – Add an at-a-glance behaviour summary to ADR 009 (assistant-authored)

- **Focus area**: Make ADR 009 easier to skim by adding a short “At-a-glance behaviour” summary near the Decision section.
- **Changes made (ADR text):**
  - Added an “At-a-glance behaviour” subsection to `docs/adr/009-rerun-last-recipe-shorthand.md` that:
    - Summarises:
      - `model again` as “rerun the last recipe exactly, using the same source/destination”.
      - `model again <tokens…>` as “rerun last recipe plus per-axis overrides based on spoken tokens”.
- **ADR 009 impact:**
  - Improves readability for future readers who want a quick reminder of what `model again` does without re-reading the full Decision and Design sections.
  - Reinforces the shorthand mental model already captured elsewhere in the ADR.
