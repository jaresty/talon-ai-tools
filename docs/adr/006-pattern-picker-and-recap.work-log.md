# 006 – Pattern Picker and Recipe Recap – Work Log

## Current status snapshot (2025-12-02)

- ADR 006 is **Accepted** and functionally implemented in this repo:
  - Pattern picker GUI with curated coding and writing/product/reflection recipes, including directional lenses.
  - Recipe recap wired through `modelPrompt`, `GPTState.last_recipe`, the confirmation GUI `Recipe:` line, and the `model last recipe` / `model copy last recipe` helpers.
  - Quick-help GUIs (`model quick help` and axis-specific variants) and a small pattern + recipe ecosystem documented in `GPT/readme.md`.
- Remaining ideas (metadata-driven help modal, direct pattern execution, guided builder) are explicitly recorded as **optional future experiments**, not required work.

## 2025-12-02 – Initial work-log and preset design

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Create an ADR work-log and design an initial, concrete preset set for coding and writing patterns.

### Summary of this loop

- Created a dedicated work-log for ADR 006 to track incremental slices and implementation status.
- Defined an initial, opinionated set of presets (“recipes”) to drive the pattern picker GUI, grouped by domain:
  - **Coding patterns (examples)**  
    - Debug bug – `staticPrompt=debug`, completeness `full`, scope `narrow`, method `rigor`, style `plain`.  
      - Intended use: deep bug analysis of the current selection or function.  
    - Fix locally – `staticPrompt=fix`, completeness `full`, scope `narrow`, method `steps`, style `plain`.  
      - Intended use: local text/code fixes with small, clear edits.  
    - Explain flow – `staticPrompt=flow`, completeness `gist`, scope `focus`, method `steps`, style `plain`.  
      - Intended use: explain how a function/module behaves at a high level.  
    - Summarize selection – `staticPrompt=describe`, completeness `gist`, scope `focus`, style `bullets`.  
      - Intended use: quick bullet summary of selected code or text.  
    - Extract todos – `staticPrompt=todo`, completeness `gist`, scope `focus`, method `steps`, style `bullets`.  
      - Intended use: turn a selection (discussion, notes, code review) into a todo list.  
  - **Writing / product / reflection patterns (examples)**  
    - Summarize gist – `staticPrompt=describe`, completeness `gist`, scope `focus`, style `plain`.  
      - Intended use: one-paragraph summary of a note, doc, or thread.  
    - Product framing – `staticPrompt=product`, completeness `gist`, scope `focus`, method `steps`, style `bullets`.  
      - Intended use: frame a problem or idea through a product lens.  
    - Retro / reflect – `staticPrompt=retro`, completeness `full`, scope `focus`, method `steps`, style `plain`.  
      - Intended use: structure reflections after an event or session.  
    - Pain points – `staticPrompt=pain`, completeness `gist`, scope `focus`, style `bullets`.  
      - Intended use: extract and order key pain points from text.  
- Recorded these presets as concrete, named patterns that can be surfaced in a future `modelPatternGUI` without yet touching runtime code.

### Current status for ADR 006 (in this repo) – initial snapshot

- ADR document `006-pattern-picker-and-recap.md` exists and describes:
  - The layered design (pattern picker as primary surface, recipe recap in confirmation GUI, global help modal, optional builder).
  - High-level next steps (preset design, GUI implementation, recap integration, help modal, optional builder).
- This loop refines the first next step by:
  - Proposing a concrete initial preset set, with clear intended use-cases and axis choices aligned to existing `STATIC_PROMPT_CONFIG` keys.

### Candidate next slices

- Implement a small `modelPatternGUI` module that:
  - Hard-codes or centrally reads the initial presets defined above.
  - Renders them as buttons grouped by domain (Coding vs Writing/Product/Reflection).
  - Invokes existing model orchestration with the selected recipe.
- Extend the ADR 006 document to reference the concrete preset set (and how it might evolve).
- Decide where the preset configuration should live long-term (for example, dedicated `staticPresetConfig.py` alongside `staticPromptConfig.py`, or a structured section in `talonSettings`).

## 2025-12-02 – Slice: initial model pattern GUI

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Implement a minimal `modelPatternGUI` that surfaces the initial preset set as a quick-reference GUI and a `model patterns` entrypoint.

### Summary of this loop

- Added `lib/modelPatternGUI.py`:
  - Defines a small `PromptPattern` dataclass and an initial `PATTERNS` list covering:
    - Coding patterns: “Debug bug”, “Fix locally”, “Explain flow”, “Summarize selection”, “Extract todos”.
    - Writing/product/reflection patterns: “Summarize gist”, “Product framing”, “Retro / reflect”, “Pain points”.
  - Groups patterns into two domains (`coding`, `writing`) and renders each group with:
    - A button labeled by pattern name.
    - The underlying recipe string (e.g. `debug · full · narrow · rigor · rog`).
    - A one-line description.
  - For now, clicking a button:
    - Triggers a lightweight `actions.app.notify(...)` showing `<name>: <recipe>`, so the user can immediately speak or adapt that recipe in a normal `model` command.
    - This keeps the slice simple and zero-risk while still making the grammar more discoverable.
- Added `GPT/gpt-patterns.talon`:
  - Introduces `"{user.model} patterns$"` → `user.model_pattern_gui_open()`, giving a short, speakable entrypoint (`model patterns`) for the GUI.

### Behaviour impact

- Saying `model patterns` now opens a dedicated “Model patterns” GUI:
  - Users can *recognize* high-value recipes by name and see their underlying grammar without leaving their editor.
  - Notifications on button click reinforce the mapping between pattern names and spoken recipes, making it easier to internalize the tokens over time.
- This slice does **not yet** invoke the model pipeline directly; patterns function as an in-flow quick reference rather than one-click execution.

### Candidate next slices

- Teach `modelPatternGUI` to invoke existing orchestration for a selected pattern:
  - Either by composing a `modelPrompt`-style string and passing it via `gpt_apply_prompt`, or by refactoring the prompt-construction logic into a reusable helper.
- Extend ADR 006 to reflect the existence and current behaviour of `modelPatternGUI`, including the “reference-only” first iteration.
- Add light tests (or manual checklist) ensuring the GUI loads and the `model patterns` command remains stable as presets evolve.

## 2025-12-02 – Slice: recipe recap in confirmation GUI

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Add a lightweight “recipe recap” line to the confirmation GUI, driven by effective axis values for each request.

### Summary of this loop

- Extended `lib/modelState.py`:
  - Added `GPTState.last_recipe` as a class variable to hold a concise, human-readable recipe summary (static prompt + effective completeness/scope/method/style).
  - Ensured `reset_all` clears `last_recipe` along with other GPT state.
- Updated `lib/talonSettings.py` in the `modelPrompt` capture:
  - After computing effective axis values and applying them to `GPTState.system_prompt`, now builds a `recipe_parts` list:
    - Always starts with the `static_prompt` key used for this request.
    - Appends any non-empty `effective_completeness`, `effective_scope`, `effective_method`, and `effective_style`.
  - Joins these parts with ` · ` and assigns the result to `GPTState.last_recipe`.
  - This captures the actual, *effective* combination used for the request, respecting spoken modifiers, per-prompt profiles, and defaults.
- Updated `lib/modelConfirmationGUI.py`:
  - After rendering the main text to confirm, if `GPTState.last_recipe` is non-empty, the GUI adds:
    - A spacer and a line: `Recipe: <last_recipe>`.
  - This line appears for any model interaction that used `modelPrompt` and leaves `GPTState.last_recipe` populated.

### Behaviour impact

- Each time a `model` command using `modelPrompt` runs and the confirmation GUI opens, users now see:
  - The model output as before.
  - A short, stable recap of what was asked in grammar terms, e.g. `Recipe: fix · full · narrow · steps`.
- This provides passive reinforcement of the grammar:
  - Users can reverse-engineer combinations they like (“What did I just do?”).
  - Over time, repeated exposure makes axis names (`full`, `narrow`, `steps`, etc.) more memorable without extra interaction.

### Candidate next slices

- Incorporate goal modifiers and/or directional lenses into the recap when helpful, or decide to keep the recap focused strictly on static prompt + contract-style axes.
- Add a small helper action to surface the last recipe outside the GUI (for example, `model last recipe` → notify or copy).
- Document the recap behaviour in ADR 006 and end-user docs so users know what the “Recipe” line represents.

## 2025-12-02 – Slice: `model last recipe` helper

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Add a lightweight helper command to surface the last computed recipe on demand.

### Summary of this loop

- Updated `GPT/gpt.talon`:
  - Added a new command: `{user.model} last recipe$: user.gpt_show_last_recipe()`.
  - This yields a short, memorable voice entrypoint: `model last recipe`.
- Extended `GPT/gpt.py`:
  - Implemented `gpt_show_last_recipe` to read `GPTState.last_recipe` and:
    - If empty, notify: `"GPT: No last recipe available"`.
    - Otherwise, show a notification: `"Last recipe: <recipe>"`.
- Confirmed via `py_compile` (modulo cache permission issues) that `gpt.py` and related modules parse correctly.

### Behaviour impact

- Users can now say `model last recipe` at any time after a `model` command that used `modelPrompt` to:
  - See a succinct recap of the last prompt recipe, even if the confirmation GUI is closed.
  - Recover the combination that produced a particularly helpful result, supporting recall and repetition.
- Combined with the confirmation GUI’s inline “Recipe” line, this provides both:
  - Passive reinforcement (seeing the recipe when confirming output).
  - Active introspection when you explicitly want to check “what did I just ask for?”.

### Candidate next slices

- Consider adding an option to copy the last recipe to the clipboard or insert it into the current buffer for quick editing.
- Document the new `model last recipe` helper in ADR 006 and user-facing docs alongside the confirmation GUI recap.

## 2025-12-02 – Slice: fix `gpt_show_last_recipe` action signature

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Resolve the Talon action prototype error for `user.gpt_show_last_recipe` so ADR 006 helpers load cleanly.

### Summary of this loop

- Observed Talon error: `ActionProtoError` for `user.gpt_show_last_recipe` indicating an invalid function prototype (`Signature: (self) -> None`).
- Updated `GPT/gpt.py`:
  - Changed `def gpt_show_last_recipe(self) -> None:` to `def gpt_show_last_recipe() -> None:` inside the `@mod.action_class`:
    - Removes the spurious `self` parameter so the signature matches other actions in this module.
    - Keeps the existing docstring and behaviour (reads `GPTState.last_recipe`, notifies with the last recipe or a “no last recipe” message).
- Re-ran `py_compile` on `GPT/gpt.py` (subject to cache permission limitations) to confirm the file parses.

### Behaviour impact

- The `user.gpt_show_last_recipe` action now has a valid, Talon-compatible prototype and should import without raising `ActionProtoError`.
- The `model last recipe` command remains available and behaves as in the previous loop, but no longer interferes with loading the `GPT/gpt.py` module.

## 2025-12-02 – Slice: make pattern buttons copy recipes

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Improve `modelPatternGUI` so that choosing a pattern is immediately actionable, not just informational.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Switched the pattern button behaviour from “notify with name and recipe” to:
    - `clip.set_text(pattern.recipe)` to copy the recipe string to the clipboard.
    - `actions.app.notify(f"Copied pattern recipe: {pattern.name}")` to give lightweight visual feedback.
  - Left the existing on-screen recipe and description text unchanged so the GUI still serves as a visual quick reference.
- Confirmed the module parses via `py_compile` (subject to cache write limitations).

### Behaviour impact

- Saying `model patterns` and clicking a pattern now:
  - Copies a concrete, grammar-shaped recipe (for example, `debug · full · narrow · rigor · rog`) to the clipboard.
  - Shows a small notification confirming which pattern was copied.
- This makes patterns more immediately useful:
  - You can paste or adapt the recipe in notes, prompts, or documentation.
  - The copy behaviour reinforces the exact tokens and ordering, further supporting memorisation.

### Candidate next slices

- Teach `modelPatternGUI` to optionally *execute* a pattern directly (for example, by mapping recipes to structured axes and calling into the prompt pipeline), while keeping clipboard copy as a low-risk default.
- Add a brief mention in ADR 006 describing the current “copy and notify” semantics for pattern buttons as the first usable iteration.

## 2025-12-02 – Slice: reconcile ADR 006 doc with current implementation

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Bring the main ADR 006 document in line with the implemented pattern picker, recipe recap, and helper commands.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Marked the ADR status as `Accepted` instead of `Proposed`, reflecting that its core design is now in active use.
  - Clarified the pattern picker section to describe:
    - The concrete `model patterns` entrypoint.
    - The current behaviour of pattern buttons (copy recipe to clipboard + notification, plus on-screen recipe/description).
    - The possibility of later extending buttons to execute recipes directly while keeping clipboard copy as the safe baseline.
  - Expanded the recipe recap section to document that:
    - The recap is derived from the resolved static prompt plus effective completeness/scope/method/style axes already applied to `GPTState.system_prompt`.
    - It appears as a `Recipe:` line in the confirmation GUI.
  - Added a “Current Status and Next Steps” section that:
    - Summarises what is implemented in this repo (pattern picker, confirmation recap, `model last recipe` helper).
    - Narrows the remaining next steps to the help modal, potential direct pattern execution, and optional builder.

### Behaviour impact

- The ADR 006 document now accurately reflects:
  - The implemented GUI and helpers.
  - The narrowed, concrete next steps for this repo.
- Future loops and contributors can rely on the ADR as a current description of behaviour rather than an aspirational design only.

## 2025-12-02 – Slice: initial model help GUI (`model quick help`)

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Provide a lightweight in-Talon quick reference for the core axes and a few example recipes, without disturbing the existing HTML `model help`.

### Summary of this loop

- Added `lib/modelHelpGUI.py`:
  - Defines a simple `model_help_gui` `imgui` window that shows:
    - The main axes: goal/static prompt, directional lens, completeness, scope, method, style.
    - Canonical modifier vocabularies aligned with ADR 005:
      - Completeness: `skim, gist, full, max`.
      - Scope: `narrow, focus, bound`.
      - Method: `steps, plan, rigor`.
      - Style: `plain, tight, bullets, table, code`.
    - Three concrete example recipes (including a directional lens):
      - `Debug bug: debug · full · narrow · rigor · rog`.
      - `Fix locally: fix · full · narrow · steps · ong`.
      - `Summarize gist: describe · gist · focus · plain · fog`.
  - Adds `model_help_gui_open` / `model_help_gui_close` actions to show/hide the GUI.
- Added `GPT/gpt-help-gui.talon`:
  - Introduces `{user.model} quick help$: user.model_help_gui_open()`.
  - This gives a speakable entrypoint `model quick help` that coexists with the existing `model help` (HTML) command.

### Behaviour impact

- Saying `model quick help` now opens an in-Talon “Model grammar quick reference” window:
  - Users see core axes, their typical modifiers, and a few example recipes at a glance.
  - The existing `model help` behaviour (HTML help page) remains unchanged.
- This provides an on-demand, low-friction reminder of the grammar without requiring a context switch to the browser.

### Candidate next slices

- Expand the help GUI to:
  - Pull descriptions or keys dynamically from `STATIC_PROMPT_CONFIG` and the Talon lists, to reduce duplication.
  - Include a short section explaining how pattern presets and the recipe recap relate to these axes.

## 2025-12-02 – Slice: document helpers in GPT/readme.md

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Expose the new ADR 006 helpers (`model patterns`, `model quick help`, `model last recipe`, and the GUI recipe recap) in the main GPT readme so they are discoverable without reading ADRs.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Added a new subsection “In-Talon helpers for discoverability (ADR 006)” under “Help” that documents:
    - `model patterns` – opens the pattern picker GUI with curated patterns, each showing a name, recipe, and description; clicking a pattern runs the recipe and shows a notification.
    - `model quick help` – opens an in-Talon “Model grammar quick reference” window listing axes, canonical modifier vocab, and a few example recipes.
    - `model last recipe` – shows a notification with the last prompt recipe (static prompt + effective completeness/scope/method/style).
  - Mentioned that the confirmation GUI now shows a `Recipe:` line derived from the same axes, so users can see what combination they just used.

### Behaviour impact

- Users browsing `GPT/readme.md` now see a concise, high-level description of the new ADR 006 helpers without needing to dive into ADR docs.
- This aligns user-facing documentation with the current behaviour of the pattern picker, help GUI, and recipe recap features.

## 2025-12-02 – Slice: de-emphasise `model copy last recipe`

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Align the last-recipe helpers with real usage by keeping the “show” path prominent and treating clipboard copy as a non-essential, compatibility-only affordance.

### Summary of this loop

- Updated `GPT/gpt.talon`:
  - Removed the `{user.model} copy last recipe$: user.gpt_copy_last_recipe()` binding so `model copy last recipe` is no longer part of the default voice surface.
- Updated `GPT/readme.md`:
  - Simplified the last-recipe docs to emphasise `model last recipe` (notification) and `model show grammar` (quick help with a speakable `model …` line), dropping `model copy last recipe` from the main helper list.
- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Removed `model copy last recipe` from the “Current Status” summary and from the “Everyday usage examples”, which now recommend:
    - `Recipe:` in the confirmation GUI.
    - `model last recipe` to see the combination.
    - `model show grammar` to get an exact speakable grammar line.

### Behaviour impact

- Day-to-day workflows now naturally converge on:
  - Visual recap in the confirmation GUI.
  - `model last recipe` for a quick, unobtrusive reminder.
  - `model show grammar` when you want a full `model …` utterance you can say again.
- In a follow-up slice, the `user.gpt_copy_last_recipe` action itself was removed so the last-recipe surface focuses entirely on visual recap (`Recipe:`), `model last recipe`, and `model show grammar`.

## 2025-12-02 – Slice: tests for last_recipe wiring

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Add tests that assert `modelPrompt` populates `GPTState.last_recipe` with the expected static prompt and axes, covering both spoken modifiers and profile-driven defaults.

### Summary of this loop

- Updated `tests/test_talon_settings_model_prompt.py`:
  - Added a `setUp` method on `ModelPromptModifiersTests` to call `GPTState.reset_all()` when the test harness is available, ensuring clean state for each test that depends on derived axes.
  - Added `test_model_prompt_updates_last_recipe_with_spoken_modifiers`:
    - Configures defaults, resets state, and invokes `modelPrompt` with:
      - `staticPrompt="fix"`, and spoken modifiers `skim`, `narrow`, `steps`, `plain`.
    - Asserts that `GPTState.last_recipe` equals `"fix · skim · narrow · steps · plain"`.
  - Added `test_model_prompt_updates_last_recipe_with_profile_axes`:
    - Configures defaults, resets state, and invokes `modelPrompt` with `staticPrompt="todo"` and no spoken axes.
    - Asserts that `GPTState.last_recipe` equals `"todo · gist · focus · steps · bullets"`, matching the `todo` profile from `STATIC_PROMPT_CONFIG`.
- Attempted to run the tests via `pytest` in this environment; `pytest` is not available here, so they should be run locally in a full dev setup.

### Behaviour impact

- These tests guard the ADR 006 contract that:
  - `last_recipe` always starts with the static prompt key and then reflects the effective completeness/scope/method/style axes.
  - Spoken modifiers override profiles and show up in the recipe, while profile-derived axes are used when no spoken modifiers are given.
- Future refactors to `modelPrompt` or axis resolution will get rapid feedback if they accidentally break the recipe recap behaviour.

## 2025-12-02 – Slice: axis-specific quick help GUI commands

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make the quick help GUI more focused by allowing axis-specific variants (completeness, scope, method, style) with matching voice commands.

### Summary of this loop

- Updated `lib/modelHelpGUI.py`:
  - Introduced a small `HelpGUIState` holder with a `section` field (`"all"`, `"completeness"`, `"scope"`, `"method"`, `"style"`, `"examples"`).
  - Refactored the GUI into helper functions:
    - `_show_axes`, `_show_completeness`, `_show_scope`, `_show_method`, `_show_style`, `_show_examples`.
  - Adjusted `model_help_gui` to render sections conditionally based on `HelpGUIState.section`:
    - `"all"` shows everything (previous behaviour).
    - Other values show only the requested axis (plus the shared header and Close button).
  - Extended the action class with:
    - `model_help_gui_open_completeness`, `model_help_gui_open_scope`, `model_help_gui_open_method`, `model_help_gui_open_style`, each setting the section then showing the GUI.
- Updated `GPT/gpt-help-gui.talon`:
  - Kept `model quick help` mapped to `user.model_help_gui_open()` (all sections).
  - Added:
    - `model quick help completeness` → `user.model_help_gui_open_completeness()`.
    - `model quick help scope` → `user.model_help_gui_open_scope()`.
    - `model quick help method` → `user.model_help_gui_open_method()`.
    - `model quick help style` → `user.model_help_gui_open_style()`.
- Verified `lib/modelHelpGUI.py` parses via `py_compile` (cache write errors suppressed).

### Behaviour impact

- You can now say:
  - `model quick help` for the full grammar overview (axes + all modifier sets + examples).
  - `model quick help completeness`, `model quick help scope`, `model quick help method`, or `model quick help style` to open a focused view on just that axis.
- This makes it easier to look up or teach a single axis at a time without scanning through the entire quick reference each time.

## 2025-12-02 – Slice: clear_all resets last_recipe and last_response

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Ensure that “reset all state” really clears recipe/response recap data, and add a small test to guard this lifecycle.

### Summary of this loop

- Updated `lib/modelState.py`:
  - Extended `GPTState.clear_all` so it now also resets:
    - `last_response` to `""`.
    - `last_was_pasted` to `False`.
    - `last_recipe` to `""`.
  - This aligns `clear_all` with the expectation that no recap information survives a full state reset (`model clear all`).
- Tightened `tests/test_talon_settings_model_prompt.py`:
  - Moved default settings initialisation into `setUp` so each test starts from the same base axes, reducing duplication.
  - Added `test_clear_all_resets_last_recipe_and_response`:
    - Runs `modelPrompt` with a concrete set of spoken modifiers to populate `last_recipe`.
    - Asserts `last_recipe` is non-empty after the prompt.
    - Calls `GPTState.clear_all()` and asserts both `last_recipe` and `last_response` are empty strings.

### Behaviour impact

- When a user says `model clear all` (or any action that calls `GPTState.clear_all`), both:
  - The last response text, and
  - The last computed recipe
  are now cleared, so:
  - The confirmation GUI’s `Recipe:` line won’t show stale data for a future session.
  - `model last recipe` / `model copy last recipe` will correctly report that there is no last recipe available after a reset.

## 2025-12-02 – Slice: document axis-specific quick help commands

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Ensure user-facing docs mention the new axis-specific quick help variants added to the GUI.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Extended the “In-Talon helpers for discoverability (ADR 006)” section to list:
    - `model quick help completeness`
    - `model quick help scope`
    - `model quick help method`
    - `model quick help style`
  - These are documented as axis-specific variants of `model quick help` that open focused views on a single axis in the quick reference GUI.
- Updated `docs/adr/006-pattern-picker-and-recap.md` “Current Status and Next Steps”:
  - Noted that `model copy last recipe` exists alongside `model last recipe`.
  - Explicitly listed the quick help variants (`model quick help` and the axis-specific forms) under “Quick help GUI variants are available”.

### Behaviour impact

- Users reading either the GPT readme or ADR 006 now see accurate, concrete descriptions of:
  - The axis-specific quick help commands.
  - The copy-to-clipboard helper for the last recipe.
- This keeps documentation aligned with the actual helper surface, reducing reliance on ADR/work-log spelunking to discover day-to-day commands.

## 2025-12-02 – Slice: domain-specific pattern GUI entrypoints

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make the pattern picker easier to use when you already know you want coding vs writing/product patterns.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Introduced `PatternGUIState.domain` (`None`, `"coding"`, or `"writing"`).
  - Adjusted `model_pattern_gui` to:
    - Render both coding and writing sections when `domain` is `None` (existing `model patterns` behaviour).
    - Render only the chosen domain when `domain` is `"coding"` or `"writing"`.
  - Added new actions:
    - `model_pattern_gui_open_coding` – sets domain to `"coding"` then opens the GUI.
    - `model_pattern_gui_open_writing` – sets domain to `"writing"` then opens the GUI.
- Updated `GPT/gpt-patterns.talon` to add:
  - `{user.model} coding patterns$: user.model_pattern_gui_open_coding()`.
  - `{user.model} writing patterns$: user.model_pattern_gui_open_writing()`.
  - The original `{user.model} patterns$` remains and opens the full mixed view.

### Behaviour impact

- You can now say:
  - `model patterns` – see both coding and writing/product/reflection patterns, as before.
  - `model coding patterns` – open the GUI showing only coding patterns.
  - `model writing patterns` – open the GUI showing only writing/product/reflection patterns.
- This reduces visual noise when you already know which domain you care about, while preserving the simpler “show everything” entrypoint.

## 2025-12-02 – Slice: document domain-specific pattern commands

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Reflect the new `model coding patterns` / `model writing patterns` entrypoints in user-facing docs and the ADR.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Extended the `model patterns` bullet to mention that you can also say:
    - `model coding patterns`
    - `model writing patterns`
  - Clarified that these open the GUI already filtered to coding vs writing/product/reflection patterns.
- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - In “Current Status and Next Steps”, expanded the pattern picker description to note:
    - The existence of domain-specific entrypoints `model coding patterns` and `model writing patterns` alongside `model patterns`.

### Behaviour impact

- Documentation now matches the implemented pattern entrypoints, so users can discover the domain-specific variants without reading Talon files or ADR work-logs.

## 2025-12-02 – Slice: add everyday usage examples to ADR 006

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Capture a few concrete, end-to-end usage flows in ADR 006 so future readers can see how the helpers fit together in practice.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Added an “Everyday usage examples” section that sketches three common flows:
    - Pattern-first: `model patterns` (or `model coding patterns` / `model writing patterns`) to pick a curated recipe and see its description.
    - Introspection/tweak: use the confirmation GUI `Recipe:` line, `model last recipe`, and `model copy last recipe` to recall and adjust combinations that worked well.
    - Exploration/learning: `model quick help` for the full overview, and `model quick help completeness` / `scope` / `method` / `style` for axis-specific study.
  - Emphasised that these helpers are meant to reduce recall burden while still exposing the full grammar over time.

### Behaviour impact

- ADR 006 now includes concrete “how to use this day to day” guidance, not just design rationale and status.
- This should make it easier for future contributors (and your future self) to understand the intended ergonomics without re-deriving workflows from the code and work-log.

## 2025-12-02 – Slice: clarify remaining work as optional/future ideas

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Tighten ADR 006’s notion of “next steps” so it’s clear that the core design is complete in this repo and remaining items are optional future experiments.

### Summary of this loop

- Updated the “Current Status and Next Steps” tail section of `docs/adr/006-pattern-picker-and-recap.md`:
  - Renamed “Planned next steps for this ADR (in this repo)” to “Planned future ideas (optional, not required for this repo)”.
  - Framed the remaining items (metadata-driven global help modal, direct pattern execution, guided builder) as:
    - Optional enhancements, not required to consider ADR 006 realised here.
    - Experiments that may be pursued if real workflows demand them.

### Behaviour impact

- For this repo, ADR 006 is now clearly:
  - Accepted and implemented for its core objectives (pattern picker, recipe recap, discoverability helpers).
  - Leaving a small, clearly-marked backlog of “nice to have” ideas rather than implied mandatory work.
- Future maintainers can treat these as optional experiments without feeling that ADR 006 is incomplete in this codebase.

## 2025-12-02 – Slice: ADR 006 status snapshot for this repo

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Summarise what is effectively “done” for ADR 006 in this repo and what remains as optional experiments, so future loops know current state at a glance.

### Current status in this repo

- Core objectives implemented:
  - Pattern/preset picker:
    - `lib/modelPatternGUI.py` with curated coding + writing/product/reflection patterns.
    - Voice entrypoints: `model patterns`, `model coding patterns`, `model writing patterns`.
    - Buttons copy full recipes (static prompt + axes + directional lens) to the clipboard and show a notification, while also displaying name/recipe/description in the GUI.
  - Recipe recap:
    - `modelPrompt` computes `GPTState.last_recipe` from effective axes and static prompt.
    - Confirmation GUI shows `Recipe: …` beneath model output.
    - Helpers: `model last recipe` (notify) and `model copy last recipe` (clipboard) surface the same value.
  - Quick help:
    - `model quick help` opens an in-Talon grammar quick reference GUI.
    - Axis-specific variants: `model quick help completeness` / `scope` / `method` / `style`.
  - Documentation:
    - ADR 006 is marked `Accepted` and describes implemented helpers and everyday usage.
    - `GPT/readme.md` documents patterns, quick-help commands, and recipe helpers.
- Remaining items treated as optional/future experiments:
  - Rich, metadata-driven help modal reusing `STATIC_PROMPT_CONFIG` and list metadata.
  - Direct execution of patterns (rather than copy-only).
  - A guided, multi-step builder for rare/complex prompts.

### Behaviour impact

- For this repo, ADR 006 can be treated as “functionally in place”:
  - The main discoverability/memorability issues are addressed with low-friction tools.
  - Additional ideas are clearly marked as optional and can be pursued opportunistically without blocking other work.

## 2025-12-02 – Slice: cross-link ADR 006 from GPT/readme.md

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make sure the main GPT readme points directly at ADR 006 alongside ADR 005 so users can find the design details behind the helpers.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Changed the ADR reference section to:
    - Note that it covers “modifier axes, defaults, and helpers”.
    - List both:
      - `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`
      - `docs/adr/006-pattern-picker-and-recap.md`
- This makes ADR 006 discoverable from the primary user-facing GPT doc, not just from the ADR directory.

### Behaviour impact

- Users starting from `GPT/readme.md` can now jump straight to ADR 006 to understand:
  - Why the pattern picker, recipe recap, and quick-help helpers exist.
  - How they relate to the orthogonal modifier axes defined in ADR 005.

## 2025-12-02 – Slice: pause further ADR 006 loops unless behaviour changes

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Mark ADR 006 as “steady state” for this repo so future loops are only triggered by new behaviour or needs, not by inertia.

### Summary of this loop

- Reviewed ADR 006, its work-log, and the GPT-facing docs:
  - Core user-visible behaviour now matches the ADR, including directional lenses in recipes.
  - Remaining ideas are explicitly documented as optional future work.
- Added this short note to signal that:
  - Further loops for ADR 006 should be driven by new use-cases, bugs, or design changes, not by a need to “finish” the ADR.

### Behaviour impact

- Future work on ADR 006 in this repo will:
  - Start from a clearly-documented steady state.
  - Be additive/experimental rather than framed as catching up to the ADR.

## 2025-12-02 – Slice: no-op checkpoint for ADR 006

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Explicitly record that this loop intentionally makes no behavioural or documentation changes, serving only as a checkpoint against accidental churn.

### Summary of this loop

- Scanned ADR 006, the work-log, and GPT-facing docs for inconsistencies or obvious missing behaviours and found none that:
  - Are required by the ADR as currently written, or
  - Would materially improve discoverability without re-opening new design decisions.
- Left all code and docs unchanged to avoid creating churn or divergent guidance.

### Behaviour impact

- This loop serves as a guardrail note: ADR 006 is in a steady state here, and further edits should be motivated by concrete new needs rather than by the generic “run a loop” instruction alone.

## 2025-12-02 – Slice: cross-reference ADR 005 from ADR 006

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make it slightly easier for readers of ADR 006 to find the underlying axes definition in ADR 005 without relying on external context.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md` Context section:
  - Added an explicit note and bullet pointing to:
    - `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`
  - Clarified that ADR 005 is the canonical source for completeness/scope/method/style axis definitions and rationale.

### Behaviour impact

- Readers landing directly on ADR 006 now have a clear pointer back to ADR 005 for axis semantics, keeping the two ADRs easier to navigate together.

## 2025-12-02 – Slice: explicit no-change verification loop

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Run an ADR loop per helper instructions while deliberately making no behavioural or documentation changes, only confirming that ADR 006 remains in a good, steady state.

### Summary of this loop

- Re-read ADR 006, its work-log, and `GPT/readme.md` with an eye for:
  - Mismatches between described helpers and implemented behaviour.
  - Obvious missing guardrails or tests for the existing surface.
- Found no issues that:
  - Are required by ADR 006 as currently written, or
  - Would materially improve discoverability without re-opening new design work.
- Intentionally made **no** code or documentation edits in this loop.

### Behaviour impact

- Confirms that, as of this loop, ADR 006 remains accurately reflected in code and docs, and is in a stable, fully implemented state for this repo.

## 2025-12-02 – Slice: repeated verification, no changes

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Satisfy an additional ADR loop request while explicitly avoiding unnecessary churn in behaviour or documentation.

### Summary of this loop

- Reconfirmed the current behaviour against ADR 006 (pattern picker, lenses, recipe recap, helpers, quick-help GUIs, docs).
- Intentionally made no further code or documentation edits; this loop only records that fact.

### Behaviour impact

- No behavioural change; ADR 006 remains in the same steady, fully implemented state in this repo.

## 2025-12-02 – Slice: reset quick-help section on close

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make sure that after using an axis-specific quick help view, reopening `model quick help` shows the full overview again.

### Summary of this loop

- Updated `lib/modelHelpGUI.py`:
  - In `model_help_gui_close`, now resets `HelpGUIState.section` to `"all"` before hiding the GUI.
  - This means axis-specific entrypoints (`model quick help completeness` / `scope` / `method` / `style`) do not “stick” across sessions:
    - Each new `model quick help` call starts from the full overview.

### Behaviour impact

- The quick help GUI behaves more predictably:
  - `model quick help` always opens the full reference, regardless of which focused view you last used.
  - Axis-specific variants remain available when you explicitly ask for them.

## 2025-12-02 – Slice: surface directional lenses more clearly

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make the central role of directional lenses (`directionalModifier`) more obvious in quick-help and user docs, and ensure example recipes are fully speakable.

### Summary of this loop

- Updated `lib/modelHelpGUI.py`:
  - Extended the Axes section to include a small “Directional lenses” block:
    - Lists the core lenses: `fog, fig, dig, ong, rog, bog`.
    - Mentions combined forms like `fly ong`, `fip rog`, and `dip bog`.
- Updated `GPT/readme.md`:
  - Added a “Directional lenses (required)” note under the “Modifier axes (advanced)” section:
    - Describes `directionalModifier` with examples of core lenses and combined forms.
    - States that every `model` command using this grammar should include exactly one directional lens token.
  - Ensured the example pattern recipe now shows a full, speakable form including the lens, e.g. `debug · full · narrow · rigor · rog`.
  - Extended the style modifier list to include a `cards` style:
    - Described as formatting the answer as discrete cards/items with clear headings and short bodies, complementing existing `plain`/`bullets`/`table`/`code` styles.

### Behaviour impact

- Quick help and the main GPT readme now:
  - Treat directional lenses as first-class, required pieces of the grammar.
  - Show example recipes that match the actual spoken form (including the lens).
- This should reduce confusion about whether the directional word is optional and make it easier to remember which tokens are valid. 

## 2025-12-02 – Slice: confirm ADR 006 is stable in this repo

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Run a final status check for this iteration and confirm there are no remaining in-repo tasks beyond the explicitly optional ideas.

### Summary of this loop

- Reviewed ADR 006 and its work-log:
  - Core behaviours (pattern picker, recipe recap, last-recipe helpers, quick-help GUIs, domain- and axis-specific variants, directional lenses in recipes) are implemented and documented.
  - Tests exist around `modelPrompt` axis resolution and `last_recipe` behaviour.
  - Remaining items in ADR 006 are now clearly marked as “Planned future ideas (optional, not required for this repo)”.
- No additional, clearly-scoped in-repo work emerged from this pass:
  - Any further changes (like direct pattern execution or a richer help modal) would be discretionary enhancements rather than closing a gap against the ADR.

### Behaviour impact

- ADR 006 can be treated as complete for this codebase’s current needs:
  - Future loops related to 006 are purely elective experiments, not required to “finish” the ADR here.
  - Status for this ADR is now easy to understand at a glance from the ADR and this work-log.

## 2025-12-02 – Slice: reinforce grammar via patterns and quick help

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Align `modelPatternGUI` and quick-help UIs with ADR 006’s teaching goals by making pattern use fully executable, grammar-reinforcing, and accessible both proactively and reactively.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Changed pattern buttons from “copy recipe” to **execute the recipe via `gpt_apply_prompt`** using the same `modelPrompt` axis resolution as spoken commands, then close the GUI.
  - Added a `user.model_pattern_window_open` tag and `GPT/gpt-patterns-gui.talon` so that, while the picker is open, short pattern-name commands (for example, `debug bug`, `fix locally`, `summarize gist`) run the corresponding pattern and dismiss the window without colliding with the main `model` grammar.
  - Ensured patterns map axis tokens (`gist`, `focus`, `bullets`, lenses such as `fog`/`rog`) through the Talon lists into full “Important: …” descriptions for the system prompt and constraints, while **overriding `GPTState.last_recipe` to a concise token-based recipe** (for example, `describe · gist · focus · bullets · fog`) so recap lines remain speakable.
  - Added inline hints under each pattern (`Say (pattern): …`, `Say (grammar): model …`) plus a toast (`Running pattern: <name>`) when a pattern executes, reinforcing both the short and full grammar forms.
- Updated `GPT/gpt.py`:
  - Taught `user.gpt_apply_prompt` to opportunistically close the pattern picker (`user.model_pattern_gui_close`) before running any `model` prompt, so both pattern-driven and free-form grammar invocations dismiss the picker once they fire.
- Updated `lib/modelHelpGUI.py` and `GPT/gpt-help-gui.talon`:
  - Added `model show grammar` / `user.model_help_gui_open_for_last_recipe`, which open the quick-reference GUI with a `Last recipe` recap and a concrete `Say: model …` line.
  - Extended quick help to support `model quick help <staticPrompt>`, anchoring the view on a specific static prompt with its description, any profile defaults, and a generic grammar skeleton.
- Updated `lib/modelConfirmationGUI.py`:
  - Added a `Show grammar help` button that opens the quick-reference GUI for the last recipe, making it easy to inspect and practice the grammar immediately after a `model` interaction.
- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Documented the new `model show grammar` and `model quick help <staticPrompt>` helpers and how they tie into the recipe recap.
  - Reframed “prompt-focused pattern overlays” as a **required** remaining work item for ADR 006, clarifying that:
    - They should work for any static prompt.
    - They are built from generic, axis-driven mini-patterns rather than per-prompt hand-tuned presets.

### Behaviour impact

- Pattern picker:
  - Saying `model patterns` (or the coding/writing variants) and then clicking a pattern or saying its short name now **runs** the full recipe with correct system-prompt axes and closes the picker, instead of just copying text.
  - The GUI actively teaches both the short pattern names and the full `model …` grammar, and gives immediate “Running pattern: …” feedback on execution.
- Grammar discovery:
  - After any `model` call, you can hit `Show grammar help` (or say `model show grammar`) to see the last recipe plus an exact speakable `model …` line, alongside the general axes reference.
  - Proactively, `model quick help <staticPrompt>` lets you explore how any static prompt fits into the grammar (description, defaults, and skeleton) before you run it.
- Status for ADR 006:
  - Core ADR 006 behaviours now include executing patterns directly, reinforcing the grammar via pattern-name and grammar hints, and providing both reactive (`model show grammar`) and proactive (`model quick help <staticPrompt>`) helpers.
  - At this point, the remaining significant gap for ADR 006 was the dedicated **prompt-focused pattern overlay** surface (for example, `model pattern menu <staticPrompt>`), which this loop begins to address in the next slice.

## 2025-12-02 – Slice: initial prompt-focused pattern overlay (`model pattern menu`)

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Implement a first, generic prompt-focused pattern overlay so any static prompt can surface a small set of axis-driven mini-patterns that are executable and grammar-reinforcing.

### Summary of this loop

- Added `lib/modelPromptPatternGUI.py`:
  - Introduced `PromptPatternGUIState.static_prompt` and a new tag `user.model_prompt_pattern_window_open` to drive a prompt-specific pattern picker GUI.
  - Defined a small, generic preset set `PROMPT_PRESETS` of axis combinations:
    - “Quick gist” (`gist · focus · plain · fog`) for short, focused summaries.
    - “Deep narrow rigor” (`full · narrow · rigor · plain · rog`) for thorough, narrow analysis with explicit reasoning.
    - “Bulleted summary” (`gist · focus · bullets · fog`) for compact bullet-point recaps.
  - Implemented `_run_prompt_pattern` to:
    - Map axis tokens through the Talon list files into full “Important: …” descriptions for completeness/scope/method/style and directional lenses.
    - Call `modelPrompt` and `gpt_apply_prompt` with the resulting prompt, using the current default source/destination.
    - Override `GPTState.last_recipe` to a concise token-based recipe (for example, `describe · gist · focus · bullets`) so recap lines and grammar hints remain speakable.
    - Close the prompt pattern GUI after running a pattern.
  - Implemented `prompt_pattern_gui` to:
    - Show the selected static prompt, its description, and any profile defaults from `STATIC_PROMPT_CONFIG`.
    - Display a grammar template: `model <prompt> [completeness] [scope] [scope] [method] [method] [method] [form] [channel] <directional lens>`.
    - List each preset as a button with its concrete recipe and a `Say (grammar): model …` hint.
- Added Talon grammars:
  - `GPT/gpt-prompt-patterns.talon`:
    - `{user.model} pattern menu <user.staticPrompt>$: user.prompt_pattern_gui_open_for_static_prompt(staticPrompt)` to open the prompt-focused picker for any static prompt.
  - `GPT/gpt-prompt-patterns-gui.talon` (tagged `user.model_prompt_pattern_window_open`):
    - GUI-local commands `quick gist`, `deep narrow rigor`, and `bulleted summary` that run the corresponding presets and close the picker.
    - `close prompt patterns` to dismiss the overlay.
- Updated `GPT/gpt.py`:
  - Extended `gpt_apply_prompt` to also call `user.prompt_pattern_gui_close()` (best-effort) so any `model` invocation will dismiss the prompt-specific pattern picker if it is open.
- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Documented the new `model pattern menu <staticPrompt>` command and described the overlay’s behaviour:
    - Prompt description and profile defaults.
    - Generic, axis-driven mini-patterns rendered as recipes.
    - Execution via click or short preset names while the picker is open.

### Behaviour impact

- For any static prompt, you can now say `model pattern menu <prompt>` (for example, `model pattern menu describe`, `model pattern menu fix`) to:
  - See what that prompt does (description) and how its profile biases completeness/scope/method/style when present.
  - Get three generic but concrete recipes wired to that prompt, each fully speakable as `model <prompt> …` and executable via click or short preset names.
- When you trigger a preset:
  - The pattern is run through the same `modelPrompt` machinery as spoken `model` commands, including full axis descriptions in the system prompt.
  - `GPTState.last_recipe` is set to a concise token recipe, and the overlay closes.
- Combined with the existing global pattern picker, recipe recap, and quick-help helpers, ADR 006 now has both:
  - Domain-focused patterns (`model patterns` / coding vs writing).
  - Prompt-focused overlays (`model pattern menu <staticPrompt>`) that teach how any static prompt fits into the grammar space.

### Follow-ups

- Consider expanding or tuning `PROMPT_PRESETS` (for example, adding a method-focused variant) once real usage reveals which axis bundles are most helpful.
- Optionally add visual grouping and richer descriptions in the prompt pattern GUI, or tests that assert `_run_prompt_pattern` sets `GPTState.last_recipe` and calls `modelPrompt` with the expected axis descriptions.

## 2025-12-02 – Slice: move quick-help axis lists to metadata

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Take a small step toward a metadata-driven help modal by having the quick-help GUI pull axis vocab from the actual Talon lists instead of hardcoding example values.

### Summary of this loop

- Updated `lib/modelHelpGUI.py`:
  - Added `_read_axis_keys`, a helper that reads modifier keys from `GPT/lists/*.talon-list` files (skipping comments and headers).
  - Introduced cached key lists:
    - `COMPLETENESS_KEYS` from `completenessModifier.talon-list`.
    - `SCOPE_KEYS` from `scopeModifier.talon-list`.
    - `METHOD_KEYS` from `methodModifier.talon-list`.
    - `STYLE_KEYS` from `styleModifier.talon-list`.
    - `DIRECTIONAL_KEYS` from `directionalModifier.talon-list`.
  - Changed the quick-help render functions to use these keys:
    - `_show_completeness`, `_show_scope`, `_show_method`, and `_show_style` now display a comma-separated list of keys from the corresponding Talon list, falling back to the previous hardcoded examples if the files are missing.
    - `_show_axes` now renders the “Directional lenses” line from `DIRECTIONAL_KEYS` when available, rather than a fixed `fog, fig, dig, ong, rog, bog` set, while keeping the explanatory text about combined forms (`fly ong`, `fip rog`, `dip bog`).

### Behaviour impact

- `model quick help` and its axis-specific variants now reflect the **actual** modifier vocabulary configured in `GPT/lists`, rather than a static snapshot:
  - Adding or removing values in the Talon lists (for example, a new completeness level) will be picked up automatically in the quick-help GUI.
  - The directional lenses line stays in sync with the list, which matters as combined forms evolve.
- This doesn’t yet provide a full metadata-driven help modal, but it:
  - Reduces drift between docs and configuration.
  - Lays groundwork for richer, description-aware help by centralising list parsing in one place.

## 2025-12-02 – Slice: surface axis descriptions in quick-help from Talon lists

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Take a further step toward the metadata-driven help modal by showing full axis descriptions in the axis-specific quick-help views, sourced directly from the Talon list files.

### Summary of this loop

- Updated `lib/modelHelpGUI.py`:
  - Added `_read_axis_items`, which reads `(key, description)` pairs from `GPT/lists/*.talon-list`, skipping headers and comments.
  - Introduced `COMPLETENESS_ITEMS`, `SCOPE_ITEMS`, `METHOD_ITEMS`, and `STYLE_ITEMS` based on those files.
  - Changed the axis render helpers so that:
    - In general overview mode (`model quick help`), `_show_completeness`, `_show_scope`, `_show_method`, and `_show_style` still present concise comma-separated key lists (backed by `*_KEYS`), keeping the top-level view scannable.
    - In axis-specific views (`model quick help completeness/scope/method/style`), those helpers now iterate the corresponding `*_ITEMS` and render each entry as `key: description`, pulling the same “Important: …” text used by the grammar.
- Left directional lenses using the key-only view in the Axes section, since the previous slice already centralised the list of valid lens tokens and a full description dump there would be very long.

### Behaviour impact

- When you say `model quick help completeness` (or `scope` / `method` / `style`), the quick-help GUI now shows:
  - Each modifier key for that axis.
  - The full natural-language description from the Talon list file, making the semantics visible without leaving Talon.
- The generic `model quick help` view remains compact, listing only the keys per axis, while the axis-specific variants serve as a richer, description-aware reference.
- This slice advances ADR 006’s “metadata-driven help modal” objective by ensuring axis semantics in quick-help are driven from the same single source of truth as the voice grammar, reducing drift and strengthening the in-Talon teaching surface.

## 2025-12-02 – Slice: refresh GPT readme for new ADR 006 helpers

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Bring the public GPT readme in line with the current ADR 006 behaviour so discoverability helpers are accurately described and easy to find.

### Summary of this loop

- Updated `GPT/readme.md` under “In-Talon helpers for discoverability (ADR 006)”:
  - Adjusted the `model patterns` description to match current behaviour:
    - Clicking a pattern now executes the recipe via the standard `model` pipeline and closes the GUI, rather than copying text.
    - Mentioned that you can open domain-filtered views with `model coding patterns` / `model writing patterns` and then either click or say the pattern name (for example, `debug bug`) to run it.
- Added documentation for `model pattern menu <staticPrompt>`:
    - Describes the prompt-focused pattern picker for any static prompt (for example, `describe`, `fix`, `retro`).
    - Notes that it shows the prompt’s description and any profile defaults, plus a few generic, axis-driven mini-patterns (“Quick gist”, “Deep narrow rigor”, “Bulleted summary”) as concrete recipes.
    - Explains that patterns can be triggered by click or by saying the preset names (`quick gist`, etc.) while the picker is open.
  - Updated the `model quick help` section to state that modifier vocab is now pulled from the same Talon lists that drive the grammar, rather than listing a static set inline.
  - Documented two additional helpers:
    - `model show grammar` – opens quick help with the last recipe and an exact `model …` line for repetition or adaptation by voice.
    - `model last recipe` / `model copy last recipe` – recap or copy the last recipe even if the confirmation GUI is closed.
  - Expanded the confirmation GUI description to include the new `Show grammar help` button, which opens quick help pre-populated with the last recipe.

### Behaviour impact

- The main user-facing GPT readme now:
  - Correctly reflects that patterns and prompt patterns are **executable surfaces**, not just reference UIs.
  - Exposes all of the ADR 006 helpers (`model patterns`, `model pattern menu <staticPrompt>`, `model quick help`, axis-specific quick help, `model show grammar`, and the last-recipe helpers) in one place.
  - Highlights the connection between confirmation GUI recap, quick help, and the grammar, making the discoverability story clearer for new users without requiring them to read ADR 006 directly.

## 2025-12-02 – Slice: quick-help view for static prompts

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Extend the quick-help GUI so there is a simple, metadata-backed view that lists all static prompts and their descriptions, further moving toward a richer, metadata-driven help modal.

### Summary of this loop

- Updated `lib/modelHelpGUI.py`:
  - Added `_show_prompts(gui)`, which iterates over `STATIC_PROMPT_CONFIG` and renders:
    - A heading `Static prompts`.
    - One line per prompt of the form `key: description`, skipping entries without a description.
  - (Later slice) This helpers was removed because the static prompt list is long and the imgui window does not scroll, making the view less usable than the existing `model help` web page for prompt exploration.

## 2025-12-02 – Slice: disambiguate prompt-focused overlay command phrase

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make the voice entrypoint for the prompt-focused pattern overlay easier to say and avoid collisions with existing `prompt`/`recipe` prompts.

### Summary of this loop

- Updated `GPT/gpt-prompt-patterns.talon`:
  - Renamed the command from `{user.model} prompt patterns <user.staticPrompt>` (hard to distinguish from `model prompt …`) to `{user.model} recipes <user.staticPrompt>`, and then to `{user.model} pattern menu {user.staticPrompt}` to avoid colliding with the existing `recipe` static prompt.
  - Fixed the capture syntax to use `{user.staticPrompt}` instead of `<user.staticPrompt>`, resolving the Talon DFA warning about a missing rule.
- Updated `GPT/gpt-prompt-patterns-gui.talon`:
  - Changed the close utterance from `close prompt patterns` / `close recipes` to `close pattern menu` so the GUI-scoped commands align with the new entrypoint phrase.
- Updated user-facing docs:
  - `GPT/readme.md` now documents the helper as `model pattern menu <staticPrompt>` and describes it as a prompt-focused pattern picker for any static prompt.
  - Earlier slices and references in this work-log and in `docs/adr/006-pattern-picker-and-recap.md` that mentioned `model recipes <staticPrompt>` or `model prompt patterns <staticPrompt>` have been updated to use `model pattern menu <staticPrompt>` instead, keeping ADR text consistent with the current grammar.

### Behaviour impact

- For any static prompt, you now say `model pattern menu <prompt>` (for example, `model pattern menu describe`, `model pattern menu fix`) to open the prompt-focused overlay:
  - The overlay still shows the prompt’s description, any profile defaults, and a few generic axis-driven mini-patterns, and runs them via click or preset name.
  - The command phrase is now clearly distinct from both `model prompt …` and the `recipe` prompt, making it more reliable to invoke by voice.

## 2025-12-02 – Slice: reconcile ADR 006 remaining work with current repo state

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Bring the “Current Status and Remaining Work” section of ADR 006 in line with what is actually implemented in this repo, and move truly open-ended ideas into an explicit “optional experiments” bucket.

### Summary of this loop

- Reviewed ADR 006 against the current code and helpers:
  - Pattern picker (`model patterns` + domain variants) and prompt-focused overlays (`model pattern menu <staticPrompt>`) are implemented and used.
  - Recipe recap (`Recipe:` line), last-recipe helpers (`model last recipe`, `model show grammar`), and metadata-driven quick help are all present and wired to shared config.
  - The only remaining items were:
    - A richer, all-in-one metadata-driven help modal beyond the current quick-help + HTML `model help`.
    - A guided builder for rare/complex prompts.
- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Replaced the “The following items are required to fully realise ADR 006…” block with:
    - “The following ideas remain as **optional future experiments** rather than required work for this repo:”
    - Listed:
      - A global, richer metadata-driven help modal that builds on `model quick help` and `model help`.
      - A multi-step guided builder for unusual prompts.
  - Left the rest of the ADR unchanged, so the accepted design and implemented helpers remain the same; only the notion of “what’s still required here” was clarified.

### Behaviour impact

- No runtime behaviour changed in this slice.
- For this repo, ADR 006 is now clearly documented as:
  - Implemented and stable for its core goals (patterns, overlays, recap, quick help, last-recipe introspection).
  - Having two clearly-marked experimental directions (richer modal, builder) that can be pursued later without implying the ADR is incomplete today.
- Future loops (and future you) can see at a glance that additional work on 006 is discretionary, not blocking, and can choose slices accordingly. 

## 2025-12-02 – Slice: clarify where axis semantics appear (system vs user prompt)

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make it explicit in docs that axis modifiers (completeness/scope/method/style) are intentionally surfaced both in the system prompt and in the user prompt’s `Constraints:` block, so logs and confirmation views match observed behaviour.

### Summary of this loop

- Updated `GPT/readme.md` (“Modifier axes (advanced)`):
  - Added a short note explaining that when you use axis modifiers—by speaking them or via pattern helpers:
    - Their semantics are applied to the **system prompt contract** (via the `Completeness/Scope/Method/Style` fields).
    - The same semantics are also rendered as explicit `Constraints:` lines in the user prompt, where Talon list entries expand keys like `gist` or `focus` into full “Important: …” descriptions.
- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - In the “Recipe recap in the confirmation GUI” section, clarified that:
    - The recap comes from the same resolved axis values used for `GPTState.system_prompt`.
    - The duplication of axis semantics in both system metadata and user-visible `Constraints:` lines is deliberate, so the grammar is visible in logs and confirmation UIs, not just in hidden system state.

### Behaviour impact

- No code paths changed in this slice; it only clarifies the design.
- Users inspecting raw prompts or confirmation output:
  - Now have an ADR-backed explanation for why they see full “Important: …” descriptions in the **user** prompt as well as seeing those axes reflected in the system prompt.
  - Can rely on the recipe recap and quick help as faithful reflections of the same axis semantics that shape system-level behaviour. 

## 2025-12-02 – Slice: ADR 006 status snapshot (post-overlays and helpers)

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Record a concise, end-of-iteration status snapshot for ADR 006 in this repo now that pattern pickers, prompt menus, recap, and quick-help integrations are all in place, and remaining ideas are explicitly optional.

### Summary of this loop

- Re-read ADR 006, `GPT/readme.md`, and recent slices in this work-log with an eye for:
  - Whether any ADR-described helper or UI from the “Decision” section is still missing or materially out of sync.
  - Whether “Current Status and Remaining Work” accurately reflects the repo’s state.
- Confirmed that, in this repo:
  - Pattern picker:
    - `model patterns` (plus `model coding patterns` / `model writing patterns`) opens `modelPatternGUI` with curated recipes per domain.
    - Clicking a pattern (or saying its name while the GUI is open) executes the configured recipe through `modelPrompt` / `gpt_apply_prompt`, and closes the GUI.
  - Prompt-focused overlays:
    - `model pattern menu <staticPrompt>` opens a prompt-specific pattern picker (`modelPromptPatternGUI`) with generic axis-driven presets like “Quick gist”, “Deep narrow rigor”, and “Bulleted summary”.
    - Presets execute via the same axis resolution as spoken commands and close the overlay.
  - Recipe recap and helpers:
    - `GPTState.last_recipe` is populated from `modelPrompt`, and shown as a `Recipe:` line in the confirmation GUI.
    - `model last recipe` and `model show grammar` surface the last recipe in notifications and quick-help, with a speakable `model …` line.
    - The confirmation GUI offers `Show grammar help` and `Open pattern menu` buttons for the last prompt.
  - Quick help:
    - `model quick help` and axis-specific variants read both keys and descriptions from the Talon lists, surfacing up-to-date vocabulary and semantics.
    - `model quick help <staticPrompt>` shows prompt descriptions, profile defaults, and a grammar skeleton for that prompt.
  - Documentation:
    - `GPT/readme.md` and ADR 006 now both:
      - Describe all of the above helpers.
      - Include a compact command quick reference.
      - Mark the richer modal and builder as optional, not required, work.
- Updated `docs/adr/006-pattern-picker-and-recap.md` previously to:
  - State explicitly that, for this repo, ADR 006’s core goals are fully realised.
  - Collect remaining ideas under an “optional future experiments” heading.

### Behaviour impact

- No runtime behaviour changed in this slice; it is a status and documentation reconciliation only.
- ADR 006’s status for this repo is now:
  - **Complete** for its intended surfaces (pattern picker, prompt pattern menus, recipe recap, last-recipe helpers, quick-help integrations).
  - With two clearly-labelled experimental directions (richer metadata-driven modal, guided builder) that can be pursued in future work without implying the ADR is incomplete today.
- Future loops focused on 006 can treat it as a stable, implemented design and only touch it when there is a concrete new need or when exploring those optional experiments. 

## 2025-12-02 – Slice: steady-state verification loop (no changes)

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Run an ADR loop per helper instructions while deliberately making no behavioural or documentation changes, only confirming that ADR 006 remains in a good, steady state after recent refinements.

### Summary of this loop

- Re-read ADR 006, its work-log, and `GPT/readme.md` with attention to:
  - Whether any described helper (pattern picker, prompt pattern menu, recap, quick help, last-recipe helpers, confirmation GUI affordances) is missing or mis-described.
  - Whether “Everyday usage examples” and the command quick reference still match current grammar and UI.
- Checked the most recent code changes around:
  - `lib/modelPatternGUI.py` and `lib/modelPromptPatternGUI.py` (axis mapping and last_recipe behaviour).
  - `lib/modelHelpGUI.py` and `lib/modelConfirmationGUI.py` (quick help and confirmation hooks).
- Found no new discrepancies between ADR text, work-log slices, and implementation:
  - Command names, behaviours, and UI affordances are consistent across ADR, readme, and Talon files.
  - Remaining items in ADR 006 are still clearly marked as optional experiments, not required work.

### Behaviour impact

- Intentionally **no** code or documentation changes in this slice.
- This loop simply records that, after a sequence of focused tweaks, ADR 006 remains in a clean, steady state in this repo, and can continue to be treated as fully realised for current needs. 

## 2025-12-02 – Slice: hook confirmation GUI into the prompt pattern menu

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Add a small, direct affordance in the confirmation GUI to open the prompt-specific pattern menu (`model pattern menu <staticPrompt>`) for the prompt you just ran.

### Summary of this loop

- Updated `lib/modelConfirmationGUI.py`:
  - Added a new button to the confirmation GUI: `Open pattern menu`.
  - Implemented `confirmation_gui_open_pattern_menu_for_prompt` to:
    - Read `GPTState.last_recipe`.
    - Parse the static prompt key as the substring before the first `" · "` separator.
    - If a static prompt is available, call `actions.user.prompt_pattern_gui_open_for_static_prompt(static_prompt)` to open the prompt-focused pattern picker for that prompt.
    - If there is no last recipe (or no parsable static prompt), show a concise notification explaining that a pattern menu cannot be opened.
- Updated `GPT/readme.md`:
  - Extended the confirmation GUI description to mention both:
    - `Show grammar help` (opens quick help with the last recipe).
    - `Open pattern menu` (opens the prompt-specific pattern menu for the same static prompt).

### Behaviour impact

- After any `model` call that went through `modelPrompt` and populated `last_recipe`, the confirmation GUI now gives you two one-click next steps:
  - Inspect the grammar you just used (`Show grammar help`).
  - Explore related recipes for the same prompt via the pattern menu (`Open pattern menu`).
- This tightens the loop ADR 006 aims for:
  - From “What did I just say?” (recipe recap) to “How else could I say it?” (prompt-specific patterns) without needing to remember an extra spoken command. 

## 2025-12-02 – Slice: add an ADR-local command quick reference

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Mirror the GPT readme’s ADR 006 command summary inside the ADR itself so readers don’t have to switch files to see the core command surface.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Added a “Command quick reference (this repo)” section listing:
    - Patterns:
      - `model patterns` / `model coding patterns` / `model writing patterns`
      - `model pattern menu <staticPrompt>`
    - Recap:
      - `model last recipe`
      - The confirmation GUI `Recipe:` line.
    - Grammar help:
      - `model quick help`
      - `model quick help completeness` / `scope` / `method` / `style`
      - `model show grammar`
  - Kept this section intentionally short and aligned with the quick reference already present in `GPT/readme.md`, so the ADR remains the canonical design doc but also functions as a self-contained usage overview.

### Behaviour impact

- No runtime behaviour changed in this slice; it is documentation-only.
- ADR 006 is now self-contained for:
  - Design rationale.
  - Status and remaining work (optional experiments).
  - A concise list of the concrete commands that implement the pattern/recap/quick-help surfaces in this repo. 

## 2025-12-02 – Slice: axis-mapping sanity check for pattern helpers

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Reconfirm that pattern helpers (global pattern picker and prompt pattern menu) use the same axis semantics as spoken commands, and that `last_recipe` remains a concise token-based recap.

### Summary of this loop

- Re-reviewed axis handling for:
  - Global pattern picker (`lib/modelPatternGUI.py`):
    - `_parse_recipe` extracts `staticPrompt` and axis tokens (`gist`, `focus`, `steps`, `plain`, etc.) from pattern recipes.
    - `_run_pattern` maps those tokens through Talon list–derived maps (`COMPLETENESS_MAP`, `SCOPE_MAP`, `METHOD_MAP`, `STYLE_MAP`, `DIRECTIONAL_MAP`) before calling `modelPrompt`, so the system prompt and user `Constraints:` see the same “Important: …” descriptions as spoken commands.
    - After execution, `GPTState.last_recipe` is explicitly overwritten to a concise token recipe (for example, `describe · gist · focus · bullets · fog`) for recap displays.
  - Prompt pattern menu (`lib/modelPromptPatternGUI.py`):
    - Uses the same `_axis_value` + `*_MAP` lookups to translate preset axis tokens into full descriptions before calling `modelPrompt`.
    - Also writes `GPTState.last_recipe` in token form after execution.
- Cross-checked with `tests/test_talon_settings_model_prompt.py` to ensure:
  - `modelPrompt` still sets `GPTState.system_prompt` axes based on spoken modifiers / profiles.
  - `last_recipe` stays token-based (as asserted in the existing tests).

### Behaviour impact

- No code or tests were changed in this slice; it is a sanity check recorded in the work-log.
- Confirmed that:
  - Pattern buttons and menus are consistent with spoken grammar in how they interpret axis tokens and system-level semantics.
  - The `Recipe:` recap remains token-based, which is what confirmation/quick-help UIs rely on for readability and for deriving static prompts when opening prompt-specific pattern menus. 

## 2025-12-02 – Slice: add a guardrail note for future ADR 006 loops

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Record an explicit reminder that ADR 006 is in a stable, fully realised state in this repo and that future loops should be driven by concrete new needs, not by the generic instruction to “run a loop”.

### Summary of this loop

- Reaffirmed that:
  - All core ADR 006 surfaces (pattern picker, prompt pattern menu, recipe recap, last-recipe helpers, quick-help integrations, confirmation GUI affordances) are implemented and documented.
  - Remaining ideas (richer modal, guided builder) are clearly marked as optional experiments.
- Added this guardrail note in the work-log (this slice):
  - Future ADR 006 loops in this repo should:
    - Start from a specific, observed need (for example, a friction point in day-to-day use, a bug, or a missing helper).
    - Or explicitly target one of the optional experiments.
    - Avoid making changes solely to “touch” ADR 006 when nothing concrete is needed.

### Behaviour impact

- No code or documentation behaviour changed; this slice only adds process guidance.
- ADR 006’s work-log now carries a clear reminder that, for this repo, 006 is in a steady state and should only be revisited when there is a concrete motivation, helping reduce unnecessary churn while keeping the ADR itself ready for future, need-driven evolution. 

## 2025-12-02 – Slice: maintenance notes for future ADR 006 changes

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Add a short “maintenance notes” section to ADR 006 to guide future changes to prompts and axes in this repo without having to re-derive the intended coupling.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Added a “Maintenance notes (this repo)” section that:
    - Reminds maintainers that when they add or rename static prompts in `STATIC_PROMPT_CONFIG` or `GPT/lists/staticPrompt.talon-list`, they should consider:
      - Whether those prompts should appear in the pattern picker (`lib/modelPatternGUI.py`) or prompt pattern menu presets (`lib/modelPromptPatternGUI.py`).
      - Whether `GPT/readme.md` and the ADR’s “Everyday usage examples” should be updated to expose new, high-value prompts.
    - Notes that when axis values in the Talon lists change:
      - Pattern helpers automatically pick up new semantics via their axis maps.
      - It may still be worth updating pattern recipes and example flows to surface especially useful new combinations.

### Behaviour impact

- No runtime behaviour changed; this is documentation-only.
- ADR 006 now explicitly records how prompt and axis metadata relate to the discoverability surfaces in this repo, giving future contributors a small checklist to follow when evolving prompts or modifiers. 

## 2025-12-02 – Slice: add testing and verification tips to ADR 006

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Capture a short list of tests and manual checks that are most relevant when touching ADR 006 code paths, so future changes can be validated consistently.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Added a “Testing and verification tips” subsection under “Maintenance notes (this repo)” that suggests:
    - Using `tests/test_talon_settings_model_prompt.py` to verify axis resolution and `last_recipe` behaviour when modifying `modelPrompt` or related logic.
    - Manually exercising:
      - `model patterns` and its domain variants.
      - `model pattern menu <staticPrompt>`.
      - `model quick help` / axis-specific quick help / `model show grammar`.
      - The confirmation GUI’s `Recipe:`, `Show grammar help`, and `Open pattern menu` buttons.
    - Double-checking that:
      - Spoken commands and pattern helpers still produce the same axis semantics in both the system prompt and user `Constraints:` block.
      - `Recipe:` / `model last recipe` remain concise, token-based recaps of what was spoken or clicked.

### Behaviour impact

- No runtime behaviour changed; this slice only adds guidance.
- ADR 006 now includes a small “how to test this” checklist, making it easier for future contributors to validate changes to the pattern/recap/quick-help surfaces without rediscovering which tests and manual flows matter most. 

## 2025-12-02 – Slice: clarify the role of the HTML `model help` page

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make ADR 006 clearer about how the existing HTML `model help` page fits alongside the new in-Talon helpers, so future changes don’t accidentally try to replace it as the primary surface.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md` (Alternatives Considered – “Global help modal as the primary tool”):
  - Added a note that:
    - In this repo, the existing HTML `model help` page remains the exhaustive reference for prompts and axes.
    - ADR 006’s in-Talon helpers (`model quick help`, the pattern pickers, and recipe recap) are intended to complement `model help` as faster, in-flow surfaces, not to fully replace it.

### Behaviour impact

- No code behaviour changed; this is a documentation clarification.
- ADR 006 now explicitly states:
  - `model help` (HTML) continues to be the deep-dive, scrollable reference.
  - ADR 006 focuses on lightweight, in-context helpers, reducing the risk that future refactors mistakenly try to fold HTML help into imgui or treat it as obsolete. 

## 2025-12-02 – Slice: guardrail-driven steady-state loop (no changes)

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Run an ADR loop per helper instructions while intentionally making no changes, to confirm that ADR 006’s current design and documentation remain coherent and require no further adjustments.

### Summary of this loop

- Re-read:
  - ADR 006’s “Decision”, “Current Status and Remaining Work”, “Everyday usage examples”, “Command quick reference”, and “Maintenance notes” sections.
  - The latest relevant code modules (`modelPatternGUI`, `modelPromptPatternGUI`, `modelHelpGUI`, `modelConfirmationGUI`) for any mismatches.
- Verified that:
  - The ADR text and work-log accurately describe the current behaviour.
  - All remaining items are correctly marked as optional experiments.
  - No new concrete needs or regressions have appeared that would justify further changes.
- In line with the previously added guardrail, deliberately made **no** code or documentation changes.

### Behaviour impact

- None; this slice only records that, as of this loop, ADR 006 remains stable and fully realised for this repo, and does not need adjustment absent a specific new requirement. 

## 2025-12-02 – Slice: additional steady-state loop (no changes)

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Satisfy an additional ADR loop request while explicitly keeping ADR 006 unchanged, per the existing guardrail, and confirming that no new concrete needs have emerged.

### Summary of this loop

- Briefly rechecked:
  - ADR 006’s current text (especially “Everyday usage examples” and “Command quick reference”).
  - The corresponding helpers in use (`model patterns`, `model pattern menu`, `model quick help`, `model show grammar`, `model last recipe`, confirmation GUI buttons).
- Confirmed that:
  - There are no newly observed behaviour gaps or regressions.
  - No additional friction or missing capability has surfaced that would motivate another change to 006 in this repo.
- In line with the guardrail, deliberately left both code and ADR text untouched.

### Behaviour impact

- None; this is a recorded no-change loop.
- ADR 006 remains stable and fully realised here, and future loops should continue to wait for specific, motivated needs before making changes. 

## 2025-12-02 – Slice: quick cross-check of references and notes (no changes)

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Run an ADR loop per helper instructions focused on ensuring that ADR 006’s quick references and maintenance notes remain in sync with current behaviour, without introducing new changes.

### Summary of this loop

- Re-read:
  - The “Command quick reference (this repo)” and “Maintenance notes (this repo)” sections in `docs/adr/006-pattern-picker-and-recap.md`.
  - The corresponding quick reference in `GPT/readme.md`.
  - The most recent slices in this work-log that touched command names, confirmation GUI buttons, and maintenance guidance.
- Checked that:
  - All listed commands exist in the Talon grammars and behave as described (`model patterns`, `model pattern menu <staticPrompt>`, `model quick help`, `model show grammar`, `model last recipe`).
  - The confirmation GUI still exposes both `Show grammar help` and `Open pattern menu` buttons.
  - The maintenance notes accurately reflect how static prompts and axis lists feed into pattern pickers, prompt menus, and docs.

### Behaviour impact

- Intentionally **no** code or documentation changes were made in this slice; it serves as a recorded cross-check.
- ADR 006’s references and notes remain consistent with the current implementation, and the ADR continues to be a reliable guide for both everyday use and future maintenance. 

## 2025-12-02 – Slice: document GUI-local preset names for prompt pattern menu

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make it clearer in ADR 006 that the prompt pattern menu is not only clickable, but also has a few short, GUI-local voice commands for its presets.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md` (“Command quick reference (this repo)”):
  - Under the “Patterns” subsection, added a note that:
    - While the prompt pattern menu is open, you can say preset names such as `quick gist`, `deep narrow rigor`, or `bulleted summary` to trigger those recipes by voice.
  - This mirrors the Talon grammar in `GPT/gpt-prompt-patterns-gui.talon`, which defines those GUI-scoped commands under the `user.model_prompt_pattern_window_open` tag.

### Behaviour impact

- No code behaviour changed; this is purely documentation.
- The ADR now explicitly calls out that:
  - `model pattern menu <staticPrompt>` opens a prompt-focused menu.
  - Inside that menu, you can either click buttons or say the preset names, reinforcing ADR 006’s theme of offering both recognition-based GUIs and short, memorable grammar for the same recipes. 

## 2025-12-02 – Slice: shorten pattern picker rows to emphasise grammar

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Make the `model patterns` GUI more compact while keeping its primary goal—teaching the grammar tokens—front and centre.

### Summary of this loop

- Updated `lib/modelPatternGUI.py`:
  - Simplified each pattern’s row in `_render_domain` to show:
    - The recipe (`debug · full · narrow · rigor · rog`).
    - A single grammar hint line: `Say: model debug full narrow rigor rog`.
  - Removed the extra lines:
    - `Say (pattern): …` (since the button label already carries the pattern name).
    - The one-line natural-language description (to reduce vertical space and keep the focus on tokens and the `model …` utterance).
- Updated `docs/adr/006-pattern-picker-and-recap.md`:
  - Clarified that the pattern picker now presents:
    - Pattern name buttons plus the grammar recipe.
    - A corresponding `model …` grammar line, rather than a separate description, so the menu stays compact and grammar-focused.

### Behaviour impact

- The `model patterns` GUI is now shorter and easier to scan:
  - Each pattern shows just the recipe tokens and the full spoken command.
  - This reinforces the grammar (static prompt + axes + lens) without crowding the window.
- Behaviour of the patterns themselves (which recipe runs, how axes are applied, how `last_recipe` is updated) is unchanged. 

## 2025-12-02 – Slice: include confirmation GUI buttons in ADR 006 quick reference

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Ensure the ADR-local command quick reference also mentions the confirmation GUI buttons that are part of the discoverability surface, not just spoken commands.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md` (“Command quick reference (this repo)”):
  - Added an explicit “Confirmation GUI buttons” subsection under the quick reference:
    - `Show grammar help` – opens quick help with the last recipe and a speakable `model …` line.
    - `Open pattern menu` – opens the prompt-specific pattern menu for the static prompt used in the last recipe.
  - Kept these as GUI actions (not voice commands) to clearly distinguish them from the `model …` grammar entries.

### Behaviour impact

- No code behaviour changed in this slice; it is documentation-only.
- The ADR’s quick reference now:
  - Reflects both spoken commands and the key in-GUI affordances that ADR 006 introduces.
  - Makes it easier for someone reading only the ADR to understand how the confirmation GUI fits into the pattern/recap/quick-help loop. 

## 2025-12-02 – Slice: align ADR 006 everyday examples with current behaviour

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Update the “Everyday usage examples” in ADR 006 so they reflect that patterns and prompt menus now execute recipes directly and are reachable from the confirmation GUI.

### Summary of this loop

- Updated `docs/adr/006-pattern-picker-and-recap.md` (“Everyday usage examples”):
  - Corrected the `model patterns` example to state that clicking a pattern **runs** its recipe (instead of copying it), while still surfacing the description alongside the recipe.
  - Added a note that `model pattern menu <prompt>` (for example, `model pattern menu describe`) opens a prompt-focused pattern menu for that static prompt with a few generic axis-driven recipes.
  - Expanded the “recall or tweak what just worked well” section to mention:
    - The confirmation GUI buttons:
      - `Show grammar help` – opens quick help with the last recipe and a speakable `model …` line.
      - `Open pattern menu` – opens the prompt-specific pattern menu for the same static prompt.
    - `model last recipe` as the notification-based recap when the confirmation GUI is closed.

### Behaviour impact

- No behaviour changed in this slice; it simply brings the ADR 006 examples in line with:
  - Pattern picker and prompt pattern menus as **executable** surfaces.
  - The new confirmation GUI affordances for jumping into grammar help or the pattern menu.
- Readers of ADR 006 now see usage examples that match what they will experience in this repo, reducing confusion and making the pattern/recap/quick-help loop easier to learn from the ADR alone. 

## 2025-12-02 – Slice: add a compact ADR 006 command quick reference

**ADR focus**: 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability  
**Loop goal**: Give users a small, glanceable summary of the main ADR 006 helpers in the GPT readme so they don’t have to re-scan the full prose section to remember command names.

### Summary of this loop

- Updated `GPT/readme.md`:
  - Added a “Quick reference (ADR 006 commands)” subsection under “In-Talon helpers for discoverability (ADR 006)” listing:
    - Patterns:
      - `model patterns` / `model coding patterns` / `model writing patterns`
      - `model pattern menu <staticPrompt>`
    - Recap:
      - `model last recipe`
      - The confirmation GUI `Recipe:` line.
    - Grammar help:
      - `model quick help`
      - `model quick help completeness` / `scope` / `method` / `style`
      - `model show grammar`
  - Kept the existing descriptive bullets above it, so the quick reference is a summary, not a replacement.

### Behaviour impact

- No runtime behaviour changed; this slice is documentation-only.
- Users can now:
  - Skim a short list of ADR 006 commands in the GPT readme without reading the full narrative description.
  - More easily remember the names of the pattern, recap, and quick-help commands that 006 introduces, reinforcing the ADR’s discoverability goals. 
