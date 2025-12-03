# 009 – Rerun-Last-Recipe Shorthand (`model again`)

- Status: Accepted  
- Date: 2025-12-04  
- Context: `talon-ai-tools` GPT integration (`model` commands)
- See also:
  - `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`
  - `docs/adr/006-pattern-picker-and-recap.md`
  - `docs/adr/008-prompt-recipe-suggestion-assistant.md`
  - Work-log: `docs/adr/009-rerun-last-recipe-shorthand.work-log.md`

## Context

Previous ADRs establish:

- An **orthogonal model grammar** (ADR 005/007):
  - Static prompts (`staticPrompt` list).
  - Contract-style axes: completeness, scope, method, style.
  - Directional lenses (`directionalModifier` list).
- **Recipe recap and quick help** (ADR 006):
  - `GPTState.last_recipe` as a concise, token-based summary:
    - `staticPrompt · [completeness] · [scope] · [method] · [style]`
  - A separate directional lens token associated with the last recipe.
  - Quick help (`model quick help`, `model show grammar`) that:
    - Shows `Last recipe: …`.
    - Shows an exact `model …` grammar line you can repeat or adapt.
- **Patterns and suggestions** (ADR 006/008):
  - Pattern pickers and prompt-specific pattern menus.
  - A prompt recipe suggestion assistant that proposes full recipes.

This ADR describes how the rerun shorthand is implemented **in this repo’s Talon integration**; other environments that reuse similar ideas may need their own, context-specific ADRs.

Today, if you run a successful recipe and want to **tweak it slightly** you have to:

- Remember and restate the *entire* static prompt and axis combination, or
- Navigate a pattern / suggestion GUI and find a nearby recipe, then run that.

There is no small, voice-first **“rerun last recipe but change X and Y”** shorthand that:

- Starts from the last successful recipe (`staticPrompt + axes + directional`).
- Lets you override one or more components (for example, scope + directional).
- Reuses the existing grammar lists and semantics instead of introducing new axis names.

## Problem

We want a way to say:

> “Do **that same thing again**, but with a different **lens** / **scope** / **completeness** / **style** (or static prompt).”

Concretely:

- Users often iterate: they like a static prompt and overall framing, but want to:
  - Tighten / loosen completeness.
  - Zoom in or out (scope).
  - Switch method (e.g. `steps` → `diagnose`).
  - Switch style (e.g. `bullets` → `plain`).
  - Change the directional lens (`fog` → `rog`).
- The existing surfaces (patterns, pattern menus, suggestions) help discover recipes, but:
  - They still require selecting **another complete recipe**.
  - They do not provide a compact way to say “same, but with tweaks.”

We want a **positional, token-based rerun shorthand** that:

- Reuses the same short tokens as the main `model` grammar.
- Allows multiple substitutions in one utterance.
- Relies on Talon’s capture and list machinery for parsing, rather than custom token classification.

## Decision

We will add a **rerun-last-recipe shorthand** centered on a new `model again` family of commands:

- `model again`  
  Rerun the last recipe exactly (same static prompt, axes, and directional lens).

- `model again [<staticPrompt>] [axis tokens…]`  
  Rerun the last recipe, but override any subset of:
  - Static prompt.
  - Completeness.
  - Scope.
  - Method.
  - Style.
  - Directional lens.

In short:  
`model again [<staticPrompt>] [axis tokens…]` = **last recipe** ⊕ **your spoken overrides** (per axis).

### At-a-glance behaviour

- `model again` – reruns the last recipe exactly (same static prompt, axes, and directional lens) using the same source/destination model as other `model` commands.
- `model again <tokens…>` – reruns the last recipe but applies any spoken static prompt / axis / lens tokens as overrides on top of the stored recipe, one axis at a time.

Axis tokens are **positional and token-based**, not named:

- They are drawn from the existing Talon lists:
  - `completenessModifier`, `scopeModifier`, `methodModifier`, `styleModifier`, `directionalModifier`.
- Talon’s capture rules do the heavy lifting:
  - Recognising which spoken word belongs to which list.
  - Applying the ordering we already use for `modelPrompt`.

At a high level:

1. `model again` with no extra tokens:
   - Reconstructs the previous recipe from `GPTState` and re-runs it.
2. `model again …` with any mix of staticPrompt + axis tokens:
   - Starts from the previous recipe.
   - Applies the capture-provided overrides (only for axes that were spoken).
   - Runs the resulting recipe via the existing `modelPrompt` / `gpt_apply_prompt` path.
3. The resulting run updates:
   - `GPTState.last_recipe` (static prompt + axes, token-based).
   - The stored directional lens token.
   - Quick help / last-recipe recap as today.

This keeps the rerun shorthand:

- **Positional** (no new “set scope to …” syntax).
- **Token-based** (reuses the same short keys users see in recipes and quick help).
- **Grounded in Talon’s lists and captures** (no manual token classification logic).

## Rationale

- **Leverages existing axis semantics**  
  The shorthand mirrors the existing `model` grammar, rather than inventing a new configuration language. Users only need to know the same tokens they already see in:
  - Recipe recaps.
  - Pattern menus.
  - Quick help.

- **Recognition over recall, even for iteration**  
  Quick help already surfaces the last recipe as an exact `model …` line. This ADR adds a lighter alternative:
  - You can say `model again` to retry the same configuration.
  - Or `model again <few tokens>` to nudge axes or lens without reconstructing the full line.

- **Multiple substitutions in one go**  
  Because the grammar accepts a mix of axis tokens, you can say:
  - `model again gist bound steps fog`  
    and override completeness, scope, method, and directional in a single utterance.

- **Keeps parsing in Talon, not Python**  
  We rely on:
  - The uniqueness of entries in the Talon lists.
  - Talon’s ability to bind spoken tokens to specific captures (`completenessModifier`, `scopeModifier`, etc.).
  The Python side only merges **already-classified** overrides with the stored last recipe.

- **Minimal new surface area**  
  This ADR adds:
  - A small new capture / helper for the `again` form.
  - A `gpt_rerun_last_recipe`-style action that merges overrides with stored state and calls into the existing pipeline.

## Design

### Grammar

We introduce a new `again`-family grammar that hangs off the existing `model` tag.

The key constraint is that we want to **avoid** allowing multiple modifiers for the same axis in a single utterance, and we prefer Talon’s grammar to enforce that rather than rejecting duplicates later in Python. To do this, we mirror the main `modelPrompt` ordering and expose each axis at most once in the rules, relying on optional segments.

Implemented `.talon` bindings (from `GPT/gpt.talon`):

- Rerun exactly:

  - `^{user.model} again$: user.gpt_rerun_last_recipe("", "", "", "", "", "")`

- Rerun with static prompt and optional overrides:

  - `^{user.model} again {user.staticPrompt} [{user.completenessModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.styleModifier}] [{user.directionalModifier}]$:`
    - Calls:
      - `user.gpt_rerun_last_recipe(staticPrompt or "", completenessModifier or "", scopeModifier or "", methodModifier or "", styleModifier or "", directionalModifier or "")`

- Rerun with overrides only (reusing last static prompt):

  - `^{user.model} again [{user.completenessModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.styleModifier}] [{user.directionalModifier}]$:`
    - Calls:
      - `user.gpt_rerun_last_recipe("", completenessModifier or "", scopeModifier or "", methodModifier or "", styleModifier or "", directionalModifier or "")`

Properties:

- Each axis capture (`completenessModifier`, `scopeModifier`, etc.) appears **at most once** in the relevant rule, so Talon itself prevents multiple values for the same axis in a single `again` command.
- All segments after `again` are optional:
  - Saying only `model again` passes six empty strings to the action (meaning “no overrides; use all last values”).
  - Saying `model again gist fog` sets only the completeness and directional arguments; the rest are empty strings.
  - Saying `model again todo gist fog` sets the static prompt to `todo`, overrides completeness to `gist`, and directional to `fog`, leaving other axes unchanged.

On the Python side, the rerun helper receives:

- A static prompt override (possibly `""`).
- Up to one override string per axis (`""` when omitted).

It then merges these with the stored last-recipe state as described in the next section.

### Stored “last recipe” state

The rerun shorthand builds on the state already used by quick help and recap:

- `GPTState.last_recipe`:
  - A concise string: `staticPrompt · [completeness] · [scope] · [method] · [style]`.
  - Tokens are short keys from the Talon lists (not long descriptions).
- A separate directional token associated with the last recipe:
  - Stored as another short key (for example, `fog`).

To rerun with changes, we need a **structured view** of the last recipe:

- Base fields (derived from the last run’s configuration):
  - `base_static_prompt`
  - `base_completeness`
  - `base_scope`
  - `base_method`
  - `base_style`
  - `base_directional`

In this repo we use the **first approach** and store explicit fields on `GPTState`:

- `last_static_prompt`
- `last_completeness`
- `last_scope`
- `last_method`
- `last_style`
- `last_directional`

All of these are short tokens from the Talon lists (for example, `gist`, `focus`, `steps`, `plain`, `fog`), so shorthand grammars can reuse them directly.

### Rerun action

We introduce a new user action:

- `user.gpt_rerun_last_recipe(static_prompt: str, completeness: str, scope: str, method: str, style: str, directional: str) -> None`

Behaviour:

1. **Guardrail: no last recipe**  
   - If there is no stored last recipe (or directional token), notify the user and do nothing:
     - In this repo, `gpt_rerun_last_recipe` calls:
       - `notify("GPT: No last recipe available to rerun")`
       - and returns without executing any prompt.

2. **Base configuration from last recipe**  
   - Read the base fields from `GPTState`:
     - Static prompt, axes, directional lens.

3. **Apply overrides from the Talon rule**  
   - For each positional argument:
     - If `static_prompt` is non-empty, replace `base_static_prompt`.
     - If `completeness` / `scope` / `method` / `style` / `directional` is non-empty, replace the corresponding base field with that short token.
   - At this stage we have a full, explicit recipe:
     - `staticPrompt`, `completeness`, `scope`, `method`, `style`, `directional`.

4. **Build a match object and prompt text**  
   - Construct a lightweight `Match` object mirroring the attributes that `modelPrompt` expects:
     - `staticPrompt`
     - `completenessModifier` (if set)
     - `scopeModifier` (if set)
     - `methodModifier` (if set)
     - `styleModifier` (if set)
     - `directionalModifier` (if set)
   - Call `modelPrompt(match)` to produce the full task/constraints text.

5. **Run through the existing `model` pipeline**  
   - Construct an `ApplyPromptConfiguration` with:
     - `please_prompt` from `modelPrompt(match)`.
     - `model_source` derived from `user.model_default_source` (same as other `model` commands; for example, selection vs. clipboard), via `create_model_source`.
     - `additional_model_source` (if any) left as in the default flow.
     - `model_destination` from `user.model_default_destination`, via `create_model_destination`.
   - Call `gpt_apply_prompt(configuration)` to execute the request.

6. **Update recap state**  
   - After execution, update:
     - `GPTState.last_recipe` to the new staticPrompt + axes tokens.
     - The last directional lens token.
   - Quick help and the confirmation GUI continue to show the updated recipe and grammar line.

### Examples

Assume the previous run left:

- `staticPrompt = describe`  
- `completeness = full`  
- `scope = relations`  
- `method = cluster`  
- `style = bullets`  
- `directional = fog`

so that:

- `GPTState.last_recipe == "describe · full · relations · cluster · bullets"`  
- Last directional lens token is `fog`.

Examples:

- `model again`  
  - No overrides.
  - Reconstructs the same configuration and runs:
    - `describe · full · relations · cluster · bullets · fog`.

- `model again fog`  
  - Capture yields `directionalModifier = fog`.
  - Only `directional` is overridden; other axes remain unchanged.

- `model again tight fog`  
  - Capture yields `styleModifier = tight`, `directionalModifier = fog`.
  - New recipe:
    - `describe · full · relations · cluster · tight · fog`.

- `model again steps tight rog`  
  - Capture yields `methodModifier = steps`, `styleModifier = tight`, `directionalModifier = rog`.
  - New recipe:
    - `describe · full · relations · steps · tight · rog`.

- `model again gist bound fog`  
  - Capture yields `completenessModifier = gist`, `scopeModifier = bound`, `directionalModifier = fog`.
  - New recipe:
    - `describe · gist · bound · cluster · bullets · fog`.

- `model again todo gist fog`  
  - Capture yields `staticPrompt = todo`, `completenessModifier = gist`, `directionalModifier = fog`.
  - New recipe:
    - `todo · gist · relations · cluster · bullets · fog`.

In each case:

- The user does not have to specify axes they are not changing.
- The grammar stays aligned with quick help and patterns.

## Consequences

### Benefits

- **Fast iteration on successful recipes**  
  Users can:
  - Rerun the last recipe exactly with `model again`.
  - Tweak axes or directional in-place without rebuilding the whole command.

- **Consistency with existing grammar**  
  The shorthand only uses:
  - Existing lists (`staticPrompt`, axis modifiers, directional modifiers).
  - Existing semantics (what each axis means).
  Quick help, pattern menus, and suggestions all keep seeing the same vocabulary.

- **Low implementation and cognitive overhead**  
  - Talon does the heavy lifting on parsing and classification.
  - Python merges structured overrides with stored state.
  - No custom tokenization or axis-detection logic is required in this repo.

### Risks / Trade-offs

- **State dependence**  
  - `model again` is only meaningful if a sensible `last_recipe` exists.
  - We must ensure `last_recipe`, the directional token, and the structured fields are kept accurate:
    - Cleared on `clear_all`.
    - Updated on pattern runs, suggestion runs, and general `modelPrompt` runs.

- **Axis list evolution**  
  - If axis vocabularies change, the rerun shorthand inherits those changes.
  - This is both a benefit (always up to date) and a dependency (tests should confirm `model again` still behaves as expected).

### Safety considerations

- `model again` always uses the same source and destination model as other `model` commands:
  - If your default source is the clipboard, it will rerun against the current clipboard; if it is selection-based, it will rerun against the current selection.
  - If your default destination pastes into the active editor, `model again` will paste there as well.
- When using `model again` in destructive destinations (for example, applying fixes directly in an editor), double-check:
  - That the active selection / clipboard matches what you expect.
  - That the destination is the window you intend to modify.

## Alternatives considered

- **Named-parameter rerun grammar**

  For example:

  - `model again completeness gist scope bound directional fog`

  Pros:

  - More explicit and self-describing.

  Cons:

  - Verbose.
  - Diverges from the concise, token-based feel of the existing grammar.

- **Freeform “but …” clause**

  For example:

  - `model again but scope bound and fog`

  Pros:

  - Reads more like natural language.

  Cons:

  - Harder to parse reliably.
  - Would require more custom tokenization and pattern matching.

- **Rely on pattern menus and suggestions only**

  Pros:

  - No new commands.
  - Users can still find nearby recipes via GUI.

  Cons:

  - Slower than a direct voice rerun for simple tweaks.
  - Requires switching modality (voice → pointer) more often.

## Status and future work

- **Status**: Accepted; implemented and in active use in this repo.
  
- **Planned / implemented slices in this repo**:

  1. **State shaping**
     - Ensure `GPTState` stores structured last-axis values alongside `last_recipe` and the directional token.
     - Add or extend tests that assert last-recipe state after `modelPrompt` / pattern / suggestion runs.

  2. **Grammar**
     - Add `model again` bindings that:
       - Reuse the existing staticPrompt and modifier lists.
       - Pass at most one override per axis into `gpt_rerun_last_recipe`, with empty strings for omitted parts.

  3. **Rerun action and tests**
     - Implement `user.gpt_rerun_last_recipe(static_prompt, completeness, scope, method, style, directional)`.
     - Add tests that:
       - Seed `GPTState` with a known last recipe.
       - Call the action with different override combinations.
       - Assert that `modelPrompt` and the prompt pipeline are invoked with the expected static prompt and axis values.

  4. **Quick help integration and docs (optional polish)**
     - Mention `model again` in:
       - Quick help UI (implemented).
       - `GPT/readme.md` usage examples (implemented).

### Interaction with other ADRs

- **ADR 006 – Pattern picker and recap**
  - `model again` builds directly on the recap state introduced in ADR 006:
    - It uses the same `last_recipe` token string and the associated directional lens.
    - It appears alongside `model last recipe` and `model show grammar` in the quick-help UI, and is hinted from there.
  - Patterns and prompt-specific pattern menus:
    - Continue to be the primary way to *discover* good recipes.
    - After running a pattern, `model again` provides a fast way to iterate on that recipe.

- **ADR 008 – Prompt recipe suggestion assistant**
  - The suggestion assistant proposes concrete recipes based on subject + content and runs them via the normal `model` pipeline.
  - When you run a suggestion:
    - It updates the same `last_recipe` / `last_directional` and structured tokens that `model again` depends on.
    - You can then say `model again` (or `model again …`) to tweak a suggested recipe without re-opening the suggestion GUI or calling the model again for suggestions.
  - This keeps:
    - `model suggest` focused on *choosing* recipes.
    - `model again` focused on *iterating* on the last chosen recipe.

### Choosing between patterns, suggestions, and `model again`

In everyday usage, the three helpers play complementary roles:

- Use **patterns / prompt pattern menus** (ADR 006) when:
  - You want a small, curated set of well-known recipes for common tasks.
  - You are exploring what kinds of recipes exist for a static prompt (`model pattern menu <staticPrompt>`).
- Use **suggestions** (ADR 008) when:
  - You have a specific subject or text and want GPT to propose several candidate recipes tailored to it (`model suggest` / `model suggest for …`).
  - You are not sure which static prompt or axis combination to start from.
- Use **`model again`** (ADR 009) when:
  - You already ran a recipe (from speech, a pattern, or a suggestion) and liked the general shape.
  - You want to rerun it exactly, or tweak one or more axes/lens (and optionally the static prompt) without rebuilding the whole grammar line or reopening a GUI.

## Everyday usage examples

Once ADR 009 is implemented in this repo and Talon has loaded the grammar, typical flows look like:

- **Rerun the last recipe exactly**
  - Say: `model again`
  - Behaviour:
    - Reads the last stored recipe (static prompt + axes + directional) from `GPTState`.
    - Rebuilds the same configuration and runs it via `modelPrompt` / `gpt_apply_prompt`.
    - Updates `last_recipe` / `last_directional` as usual so quick help and recap stay in sync.

- **Tweak completeness and lens only**
  - Assume the last recipe tokens are: `describe · full · relations · cluster · bullets` with directional `fog`.
  - Say: `model again gist fog`
  - Behaviour:
    - Keeps `staticPrompt=describe`, `scope=relations`, `method=cluster`, `style=bullets`.
    - Overrides `completeness` to `gist` and directional lens to `fog`.

- **Change static prompt and completeness, keep the rest**
  - Same starting recipe as above.
  - Say: `model again todo gist fog`
  - Behaviour:
    - Sets `staticPrompt=todo`.
    - Overrides `completeness` to `gist` and directional to `fog`.
    - Reuses the last `scope`, `method`, and `style` tokens.

- **Swap method and style, change directional**
  - Say: `model again steps tight rog`
  - Behaviour:
    - Keeps the last `staticPrompt`, `completeness`, and `scope`.
    - Overrides:
      - `method=steps`
      - `style=tight`
      - `directional=rog`
    - Runs the new recipe and updates recap state so quick help and `model last recipe` reflect the new combination.

## Current status in this repo

- **Completed and in use:**
  - Structured last-recipe state on `GPTState`:
    - `last_recipe` (token string) and `last_directional` (short lens token).
    - Per-field tokens: `last_static_prompt`, `last_completeness`, `last_scope`, `last_method`, `last_style`.
    - All of these are written by:
      - `modelPrompt` (spoken grammar).
      - Pattern picker (`model patterns`).
      - Prompt pattern menu.
      - Prompt recipe suggestions (`model suggest` → suggestion GUI).
    - All are cleared by `clear_all` / `reset_all`.
  - Rerun action and grammar:
    - `user.gpt_rerun_last_recipe(static_prompt, completeness, scope, method, style, directional)` implemented in `GPT/gpt.py`.
    - `model again` / `model again …` grammar wired in `GPT/gpt.talon`.
    - Targeted tests in `tests/test_gpt_actions.py` and `tests/test_talon_settings_model_prompt.py` validate:
      - Guardrails when no last recipe exists.
      - Correct merging of overrides with stored tokens.
      - Consistency between `modelPrompt` and the structured last-recipe fields.
  - UX integration:
    - GPT README documents `model again` with examples.
    - Quick help (`model quick help` / `model show grammar`) shows:
      - The last recipe and an exact `model …` line.
      - A hint that you can say `model again` or `model again …` to rerun or tweak the recipe.

- **Still optional / deferred:**
  - Any richer analytics or history around multiple past recipes beyond the single `last_recipe` + `model again` shorthand.
  - Additional voice shortcuts that build on the same state (for example, domain-specific aliases) are out of scope for this ADR and can be treated as separate design decisions.

In this repo, the core objectives of ADR 009 are considered **complete**: `model again` is implemented, wired through the existing pipeline, covered by tests, and surfaced in the main help surfaces. Future changes in this area (for example, multi-recipe history or new shorthands) should be treated as follow-on ADRs rather than silent extensions of this one.

### Validation and tests in this repo

This repo includes targeted tests that exercise `model again` and its supporting state:

- `tests/test_talon_settings_model_prompt.py`:
  - Verifies that `modelPrompt` populates `GPTState.last_recipe` and the structured `last_*` fields for both spoken-modifier and profile-driven cases.
  - Asserts that `clear_all` resets `last_recipe`, `last_directional`, and all structured fields.
- `tests/test_gpt_actions.py`:
  - `test_gpt_rerun_last_recipe_without_state_notifies_and_returns` checks the no-last-recipe guardrail.
  - `test_gpt_rerun_last_recipe_applies_overrides_on_last_tokens` validates merge semantics and wiring through `modelPrompt` / `gpt_apply_prompt`.
  - `test_gpt_show_last_recipe_*` tests last-recipe recap notifications, including directional when present.
- `tests/test_integration_suggestions.py`:
  - `test_suggest_then_run_index_executes_recipe` verifies suggestion execution and last-recipe updates.
  - `test_suggest_then_again_merges_overrides` covers the suggest → run → again integration path, ensuring that `model again` can tweak a suggestion-derived recipe and that structured state reflects the overrides.
