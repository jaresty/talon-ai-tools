# 006 – Pattern Picker and Recipe Recap for Prompt Grammar Discoverability

- Status: Accepted  
- Date: 2025-12-02  
- Context: `talon-ai-tools` GPT integration (`model` commands)

## Context

The GPT integration exposes a rich, orthogonal prompt grammar (static prompts, directional modifiers, completeness/scope/method/form/channel axes, and system-level defaults). This enables very fine-grained control but is hard to remember and discover in day-to-day use, especially in a voice-driven workflow.

The current surfaces (Talon voice grammar plus static docs) have these issues:

- Users must recall many token names and combinations under time pressure.
- “Power features” (axes, profiles, and less-common static prompts) are underused because there’s no quick way to *recognize* them at the moment of need.
- Existing GUI (confirmation window) focuses on output handling, not on teaching or surfacing the grammar.

For definitions and rationale behind the core modifier axes (completeness, scope, method, form/channel split from the former style axis), see ADR 005:

- `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`
- For static prompt and axis mapping domain boundaries (including how `modelPrompt` and settings/GUIs interact with the axes), see ADR 0011:
  - `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md`

We want a solution that:

- Favors recognition over recall for common workflows.
- Reinforces the grammar passively over time, so heavy users can internalize it.
- Stays low-friction for fast, repeated use in real tasks (debugging, refactoring, writing).

## Decision

We will adopt a layered, GUI-centric discoverability approach centered on a small pattern/preset picker and passive recipe recap, with deeper help available on demand:

1. **Pattern / preset picker as the primary surface**
   - Provide a compact `imgui` GUI (“pattern picker”) opened via a short voice command (`model patterns`).
   - The GUI presents a curated set of high-value “recipes” (per domain, e.g. coding vs writing), each as a button showing:
     - A human-readable pattern name (e.g. “Debug bug”, “Fix locally”, “Summarize selection”, “Product framing”).
     - The underlying grammar recipe (static prompt + axes + directional lens; for example, `debug · full · narrow · rigor · rog` in the original design, or `describe · full · narrow · debugging · rog` in this repo after ADR 012) and the corresponding spoken grammar line.
   - In the initial implementation:
     - Clicking a button executes the corresponding recipe via the same model pipeline used by spoken `model` commands, using the current default source/destination, and dismisses the pattern picker.
     - The GUI also renders the recipe and a one-line description under each button, making it a visual quick reference before you trigger it.
   - Over time, we may extend pattern buttons to directly execute a configured recipe via the existing prompt pipeline, but clipboard copy remains the low-risk baseline.

2. **Recipe recap in the confirmation GUI for passive reinforcement**
   - Extend the existing confirmation GUI (`modelConfirmationGUI`) to display the effective “prompt recipe” used for the last request, e.g.:
     - `Recipe: fix · full · narrow · steps`
  - The recap is derived from the same resolved axis values applied to `GPTState.system_prompt` (static prompt plus effective completeness/scope/method/form/channel).
   - This line appears consistently but unobtrusively, reinforcing axis names and values every time the model is used.
  - The underlying axis semantics (from the Talon lists) are expressed both in the system prompt contract and as explicit `Constraints:` lines in the user prompt; this duplication is intentional to make the grammar visible in logs and confirmation views without relying solely on system metadata. Style is split into form/channel.
   - Over time, users naturally learn and reuse combinations they see often, even without opening help.

3. **Global “what can I say?” help modal for exploration**
   - Add a separate help GUI (for example, `modelHelpGUI`) opened with `model help` that:
     - Briefly explains each axis (goal, directional lens, completeness, scope, method, form/channel).
     - Lists a small, opinionated subset of values per axis (3–5 each) with short descriptions.
     - Shows example recipes grouped by task (coding, writing, product, reflection).
   - Axis-scoped variants like `model help completeness` or `model help scope` open the same GUI filtered to one axis.
   - This is optimized for exploration and learning, not for every-day use.

4. **Optional guided “builder” for rare, complex prompts**
   - Optionally, provide a multi-step “prompt builder” command (for example, `model build`) that walks the user through Goal → Completeness → Scope → Method → Style via GUI steps.
   - This is explicitly treated as an advanced/onboarding tool for unusual prompts, not the default path.

5. **Keep the pattern set curated and domain-specific**
   - Patterns will be grouped and constrained (for example, “Coding patterns” vs “Writing patterns”) with a strong bias toward a small set of high-leverage recipes:
     - Examples: “Fix bug”, “Explain flow”, “Debug deeply”, “Summarize gist”, “Product framing”, “Retro”.
   - We will periodically refine these based on actual usage and friction, rather than mirroring the full static prompt set.

## Consequences

- **Positive**
  - Day-to-day use becomes recognition-based: users can get sophisticated behavior by picking a familiar pattern instead of recalling the full grammar.
  - The system passively teaches itself: recurring exposure to recipes in the confirmation GUI makes axis names and semantics more memorable.
  - High-power but low-frequency features become explorable via `model help` and, optionally, the builder, without cluttering the core command surface.
  - Changes to the grammar (new static prompts, new axis values) can be rolled out incrementally via updated presets and help text.

- **Negative / trade-offs**
  - The preset list introduces a new configuration surface that must be curated and maintained; if it grows too large, it becomes another discoverability problem.
  - Implementing multiple GUIs (pattern picker + help, and optionally builder) increases UI complexity and test surface area.
  - Some users may over-rely on presets and never learn the raw grammar, slightly reducing maximal flexibility in voice-only workflows.

## Alternatives Considered

1. **Global help modal as the primary tool**
   - A single, comprehensive `model help` GUI enumerating all axes and options.
   - Rejected as the primary solution because it relies on users remembering to open help and then scanning dense text, which is slow and rarely used under pressure. It is retained as a secondary, exploratory surface.
   - In this repo, the existing HTML `model help` page still serves as the exhaustive reference for prompts and axes; ADR 006 complements it with in-Talon helpers (`model quick help`, pattern pickers, and recap) for faster, in-flow usage.

2. **Static markdown cheat sheet only**
   - A `docs/grammar-quickref.md` opened via a command.
   - Rejected as insufficient because it lives outside the main flow (requires switching to editor/browser) and does not provide repeated, in-context reinforcement.

3. **Prompt builder wizard as the main entry point**
   - A multi-step GUI that constructs every prompt via guided choices.
   - Rejected as primary due to interaction cost: too many steps for quick, repeated coding/writing tasks. Kept as an optional advanced tool for rare or complex prompts.

4. **Do nothing (rely on existing grammar and docs)**
   - Rejected because it demonstrably leads to underuse of the more expressive axes and static prompts, and places a high cognitive load on recall.

## Current Status and Remaining Work

As of 2025-12-02 in this repo:

- A first version of the pattern picker exists:
  - Implemented as `lib/modelPatternGUI.py` with a curated set of coding and writing/product/reflection patterns.
  - Exposed via the `model patterns` voice command (`GPT/gpt-patterns.talon`), with domain-specific variants:
    - `model coding patterns`
    - `model writing patterns`
  - Clicking a pattern runs the corresponding recipe immediately (re-using `modelPrompt` semantics for axes and defaults) and closes the GUI; the recipe and a single “Say: model …” grammar line remain visible up to the moment you trigger it, keeping the menu compact while still teaching the grammar tokens.
- Recipe recap is wired into the confirmation GUI:
  - `lib/talonSettings.py` computes a concise `staticPrompt + axes` recipe for each `modelPrompt` request.
  - `lib/modelState.py` stores this as `GPTState.last_recipe`, and `lib/modelConfirmationGUI.py` renders it as a `Recipe:` line beneath the model output.
- A lightweight introspection helper exists:
  - `model last recipe` (`GPT/gpt.talon` + `GPT/gpt.py`) shows the last computed recipe in a notification, even if the confirmation GUI is closed.
- Quick help GUI variants are available:
  - `model quick help` opens the full grammar quick reference.
  - `model quick help completeness` / `scope` / `method` / `form` / `channel` open focused views on individual axes.
  - `model show grammar` opens the quick reference with the last recipe and a speakable `model …` line.
  - `model quick help <staticPrompt>` opens the quick reference anchored on a specific static prompt, showing any profile defaults and a grammar skeleton.
  - `model pattern menu <staticPrompt>` opens a prompt-focused pattern picker that:
    - Shows the prompt’s description and any profile defaults.
    - Lists a small, generic set of axis-driven mini-patterns (for example, “Quick gist”, “Deep narrow rigor”, “Bulleted summary”) expressed as concrete recipes for that prompt.
    - Lets you trigger these patterns by clicking or by saying preset names such as `quick gist` while the picker is open.

For this repo, these helpers and UIs fully realise ADR 006’s core goals. The ideas below are **optional future experiments**, not required work to consider this ADR complete here:

The following ideas remain as **optional future experiments**:

1. Global, richer metadata-driven help modal:
   - A more comprehensive `imgui` help GUI that brings together static prompts, axes, and example recipes in one place, building on the existing `model quick help` GUI and the HTML `model help` page.
2. Guided builder:
   - A multi-step builder for unusual prompts (Goal → Completeness → Scope → Method → Style), scoped to advanced users and only pursued if real workflows clearly benefit from it.

## Everyday usage examples

These helpers are designed to make the grammar easy to reach in common workflows:

- When you want a strong starting point without remembering axes:
  - Say `model patterns` and click a pattern that matches your task (for example, “Debug bug” or “Summarize gist”) to run its recipe and see its description.
  - If you already know you’re in code vs prose, use `model coding patterns` or `model writing patterns` to narrow the list.
  - For a specific prompt, say `model pattern menu <prompt>` (for example, `model pattern menu describe`) to open a prompt-focused pattern menu with a few generic axis-driven recipes for that prompt.
- When you need to recall or tweak what just worked well:
  - Look at the `Recipe:` line in the confirmation GUI after a `model` call.
  - Use the confirmation GUI buttons:
    - `Show grammar help` to open quick help with the last recipe and a speakable `model …` line you can repeat or adapt.
    - `Open pattern menu` to open the prompt-specific pattern menu for the same static prompt you just used.
  - Say `model last recipe` to see the last combination in a notification when the confirmation GUI is closed.
- When you’re exploring or teaching yourself the grammar:
  - Say `model quick help` for a full overview of axes and example recipes.
  - Use `model quick help completeness` / `scope` / `method` / `form` / `channel` to drill into a single axis.

### Putting it together: one simple flow

As a concrete end-to-end flow that exercises ADR 006 helpers:

1. Say `model patterns` and choose a pattern (for example, “Debug bug”) to run a curated recipe.
2. Review the result in the confirmation GUI, checking the `Recipe:` line to see which static prompt and axes were used.
3. If you like the combination but want to explore nearby options:
   - Click `Show grammar help` to see the full prompt text and a speakable `model …` line, or
   - Click `Open pattern menu` to open `model pattern menu <staticPrompt>` for the same prompt and try neighbouring recipes.

## Command quick reference (this repo)

> **Regenerate before editing**: Axis and static prompt vocab referenced here comes from the AxisSnapshot façade. Run `make readme-axis-refresh` (and, when needed, `python3 scripts/tools/generate-axis-cheatsheet.py`) before updating these lists so they stay aligned with `lib/axisCatalog.py` and the shared helpers.

For convenience, the main ADR 006-related commands in this repo are:

- Patterns:
  - `model patterns` / `model coding patterns` / `model writing patterns`
  - `model pattern menu <staticPrompt>`
  - While the pattern menu is open, you can also say preset names such as `quick gist`, `deep narrow rigor`, or `bulleted summary` to trigger those recipes by voice.
- Recap:
  - `model last recipe`
  - Confirmation GUI: `Recipe:` line
- Confirmation GUI buttons:
  - `Show grammar help` – open quick help with the last recipe and a speakable `model …` line.
  - `Open pattern menu` – open the prompt-specific pattern menu for the static prompt used in the last recipe.
- Grammar help:
  - `model quick help`
  - `model quick help completeness` / `scope` / `method` / `form` / `channel`
  - `model show grammar`

## Maintenance notes (this repo)

For future changes in this repo:

- If you add or rename static prompts in `STATIC_PROMPT_CONFIG` or `GPT/lists/staticPrompt.talon-list`, also consider:
  - Whether they deserve entries in the pattern picker (`lib/modelPatternGUI.py`) or prompt pattern menu presets (`lib/modelPromptPatternGUI.py`).
  - Whether `GPT/readme.md` and the ADR’s “Everyday usage examples” should mention them.
- If you add or change axis values in the Talon lists (completeness/scope/method/form/channel/directional):
  - Pattern helpers (`model patterns` and `model pattern menu …`) will automatically pick up the new semantics via their axis maps.
  - You may still want to update pattern recipes and example flows to showcase particularly useful new combinations.
  - Remember that recap helpers (`model last recipe`, `model show grammar`) and the rerun shorthand from ADR 009 (`model again`) also depend on the same `last_recipe` + directional state.

### Testing and verification tips

When making changes related to ADR 006 in this repo:

- Prefer the focused tests in `tests/test_talon_settings_model_prompt.py` to check axis resolution and `last_recipe` behaviour.
- Manually exercise:
  - `model patterns` / `model coding patterns` / `model writing patterns`
  - `model pattern menu <staticPrompt>`
  - `model quick help` and `model show grammar`
  - The confirmation GUI (`Recipe:`, `Show grammar help`, `Open pattern menu`)
- When in doubt, check that:
  - Spoken commands and pattern helpers produce the same axis semantics in both the system prompt and `Constraints:` block.
  - `Recipe:` / `model last recipe` still show concise, token-based recipes that match what you spoke or clicked.
