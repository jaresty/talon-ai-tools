# 026 – Axis Multiplicity for Scope, Method, and Style

- Status: Accepted  
- Date: 2025-12-07  
- Context: `talon-ai-tools` GPT `model` commands (axes: completeness, scope, method, style; static prompts; patterns)  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 012 – Retire Special‑Purpose Static Prompts into Style/Method Axes  
  - 013 – Static Prompt Axis Refinement and Streamlining  
  - 016 – Directional and Axis Decomposition  
  - 018 – Axis Modifier Decomposition Into Pure Elements  

---

## Summary (for users)

We will keep **completeness** as a **single-choice axis** (one value at a time), but allow **scope**, **method**, and **style** to hold **multiple values simultaneously** (tags) for a single `model` invocation and for stored recipes/patterns.

- Completeness remains a scalar like `gist`, `outline`, `full`, `deep`, etc.  
- Scope/method/style become **sets of tags** that can combine orthogonal behaviours:
  - Example: `model describe jira story rog`  
    - Completeness: `full` (implicit default)  
    - Scope: `actions`  
    - Method: `structure`, `flow`  
    - Style: `jira`, `story`
- The UI and modelPrompt plumbing will be updated to:
  - Treat completeness as a radio/select (one-of).  
  - Treat scope/method/style as multi-select checkboxes / tag lists.  
  - Normalise and validate combinations (for example, prevent contradictory style pairs where we explicitly define them as incompatible).

This is a behavioural change in how axes are represented and combined, but it preserves the existing spoken surface and short tokens. It enables richer, more accurate combinations without multiplying static prompts or patterns.

---

## Context

Existing ADRs already define:

- Axes and their roles (`completeness`, `scope`, `method`, `style`) – ADR-005.  
- Migration of many special-purpose static prompts into style/method axes – ADR-012/013.  
- Decomposition of overloaded modifiers into “pure” axis values – ADR-018.

Today, all four axes are effectively treated as **single-valued** in the core model prompt and GUIs:

- `modelPrompt` and related helpers in `lib/talonSettings.py` assume one value per axis.
- Static prompt profiles in `lib/staticPromptConfig.py` generally set a single value per axis.
- GUIs (`lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`) render axis choices as single-select (or behave as if they are).

However, many real use cases involve **orthogonal combinations** on scope/method/style, where “exactly one” is unnatural:

- **Style**: `jira` + `story` (or `jira` + `bug`), `slack` + `bullets`, `adr` + `table`.  
- **Method**: `structure` + `flow`, `debugging` + `compare`, `experimental` + `mapping`.  
- **Scope**: `edges` + `actions`, `relations` + `dynamics`.

Pushing these combinations into:

- Single composite style/method/scope tokens, or  
- A combinatorial explosion of patterns / static prompts  

would increase churn and complexity in config and tests, undermining the goals from ADR-010/011/018.

---

## Decision

We adopt the following model:

1. **Completeness is single-valued**

   - At any time, a recipe / invocation has **exactly one** completeness value:
     - Example set: `default`, `gist`, `outline`, `full`, `deep`, `sweep`, etc.
   - Rationale:
     - Completeness encodes a single global coverage/effort promise; multiple simultaneous coverage promises (for example, “gist + deep”) are semantically contradictory and better expressed via patterns, goals, or follow-on prompts rather than as stacked axis values.
     - ADR-005/018 already treat completeness as a scalar “how much” knob; this ADR preserves that contract so profiles, patterns, and Concordance attribution stay simple.
   - GUI representation:
     - Radio buttons / segmented control / single-select dropdown.
   - Model representation:
     - `axes["completeness"]` is always a scalar string (or `None` for “use default”).

2. **Scope, method, and style are multi-valued tag sets**

   - Each of `scope`, `method`, and `style` can hold **zero or more** values:
     - Example:
       ```python
       axes = {
           "completeness": "full",
           "scope": ["actions", "edges"],
           "method": ["structure", "flow"],
           "style": ["jira", "story"],
       }
       ```
   - Semantics:
     - Sets are **idempotent** (no duplicates).  
     - For values that do **not** conflict (see below), behaviour is **order-insensitive**: `{jira, story}` is equivalent to `{story, jira}`.  
     - Each value is individually meaningful and should be “pure” per ADR-018; their combination describes how to reason and what shape to output, not a new opaque mode.
   - Representation:
     - Internally and when serialised, axis lists are stored in a **canonical, stable order** (for example, sorted by token id) after normalisation so that equivalent sets have a consistent representation for caching, Concordance, and replay.

3. **Explicit incompatibility / conflict rules**

   - We will introduce a **central incompatibility table** for axis values:
     - Per-axis “cannot co-exist” sets (for example, if we define both `tweet` and `longform` as style tokens on the same axis).
     - Stored alongside axis vocabularies in the axis-mapping domain (`lib/talonSettings.py` or a closely-related helper module), with guardrail tests in `tests/test_talon_settings_model_prompt.py` (and friends) that fail fast when vocab or incompatibilities drift.
   - Behaviour on conflict (**last-wins, layer-aware**):
     - Axis values are accumulated in a deterministic **layer order**:
       1. Static prompt profile defaults.  
       2. Pattern defaults.  
       3. User overrides (spoken modifiers and GUI selections).  
     - Within each axis, normalisation processes values in that order and, for each new value:
       - Removes any existing values on the same axis that are marked as incompatible with the new value.
       - Adds the new value if not already present.
     - This yields a **last-wins semantics within and across layers**:
       - Later pattern defaults override incompatible profile defaults.  
       - User choices override both pattern and profile defaults where there is an explicit conflict.
   - Surface behaviour:
     - In this repo, incompatibilities are enforced centrally in the axis normaliser; GUIs do not currently emit a dedicated per-conflict hint beyond showing the resulting active tags.
     - Spoken/Talon paths remain non-interactive but inherit the same deterministic normalisation; tests assert the resulting axis sets for representative combinations, including incompatibility cases.
     - Future GUI work (out of scope for ADR-0026 in `talon-ai-tools`) may choose to add a **non-modal hint** when an incompatible value is dropped, but that is not required for this ADR to be considered implemented here.
   - Default assumption:
     - Most style/method/scope tokens remain compatible; incompatibilities are **opt-in**, not general.

4. **Normalised internal representation and interfaces**

   - `modelPrompt` and downstream helpers will treat axis values as:

     ```python
     class AxisValues(TypedDict):
         completeness: str | None          # scalar
         scope: list[str]                  # may be empty
         method: list[str]                 # may be empty
         style: list[str]                  # may be empty
         # (plus any future axes, e.g. directional, tone, audience)
     ```

   - Public-facing behaviour:
     - Spoken commands and Talon lists remain grammar-shaped but now support **multi-tag modifiers** on scope, method, and style:
       - You can say, for example, `model describe jira story rog` or `model describe narrow focus actions rog`, and each recognised scope/method/style modifier is added to the corresponding axis set (subject to incompatibility rules).
       - The `model` grammar will be extended so that `scopeModifier`, `methodModifier`, and `styleModifier` can appear zero or more times per invocation; completeness remains single-valued.
     - The axis token mapping and `modelPrompt` construction accumulate multiple values for scope/method/style instead of overwriting, using the last-wins, layer-aware semantics for conflicts.

---

## Details

### Representation and mapping

- **Talon lists** (unchanged in structure):
  - `GPT/lists/completenessModifier.talon-list`
  - `GPT/lists/scopeModifier.talon-list`
  - `GPT/lists/methodModifier.talon-list`
  - `GPT/lists/styleModifier.talon-list`
  - These lists remain the single source of truth for spoken modifier tokens; multi-tag via speech is achieved by **repeating** these modifiers in the `model` grammar, not by introducing separate “plural” lists.

- **Axis reading / mapping** (`lib/talonSettings.py`):
  - Today, helpers like `_read_axis_value_to_key_map`, `_axis_recipe_token`, and `modelPrompt` effectively assume one value per axis.
  - After this ADR:
    - Completeness path:
      - Stays scalar: when multiple completeness modifiers are spoken (or implied), the **last completeness token wins**, and we drop the rest as redundant.
    - Scope/method/style paths:
      - Accumulate tokens into per-axis lists.
      - Normalise:
        - Apply incompatibility rules (per-axis) using the last-wins, layer-aware semantics above.
        - Deduplicate values after conflict resolution.
        - Canonicalise order (for example, by stable token id) before serialisation or downstream use so equivalent sets have identical representations.
      - Expose axis arrays to:
        - `modelPrompt` construction.
        - GUI and pattern helpers.
        - Tests.

- **Static prompt profiles** (`lib/staticPromptConfig.py`):
  - Profiles will be updated to use list-valued axes for `scope`, `method`, and `style`:
    - For example, instead of:
      ```python
      axes = {"scope": "actions", "method": "structure", "style": "jira"}
      ```
      use:
      ```python
      axes = {"scope": ["actions"], "method": ["structure"], "style": ["jira"]}
      ```
    - Profiles that conceptually baked in combinations (for example, an ADR profile) can now express them directly as sets:
      ```python
      axes = {"scope": ["bound"], "method": ["structure", "analysis"], "style": ["adr"]}
      ```

- **Patterns and recipes** (`lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`):
  - Pattern definitions can now:
    - Pin multi-axis combinations directly (for example, `style=["slack", "bullets"]`).
    - Compose with user overrides in a set-aware way:
      - Pattern defaults are treated as a baseline; user changes (via GUI or spoken modifiers) are applied in the final layer and can both **add** new tags and **displace** incompatible default tags.
      - Conflicts are resolved via the central incompatibility rules and last-wins semantics so that “what you just said/selected” is the final authority.

### Vocabulary and axis discipline

- Axis vocabularies remain constrained by ADR-018’s “pure element” requirement:
  - New `scope`, `method`, and `style` values must describe a single, coherent behaviour along that axis (territory, reasoning pattern, or surface/container), not an implicit composite of multiple axis values.
  - When we discover a need for a recurring composite behaviour, we prefer:
    - A **pattern or profile** that pins multiple existing axis values, rather than
    - Introducing a new overloaded token that quietly re-encodes that combination.
- For style specifically:
  - We acknowledge that some tokens are “heavy containers” (for example, `adr`, `bug`, `jira`, `story`) but still require them to focus on **output container/genre**, not on embedding completeness or method guarantees.
  - If we later introduce a dedicated “genre/artifact” axis, multi-valued style sets should remain straightforward to factor into the new axis because tokens will already be cleanly described.
  - To avoid “axis soup”, each axis defines explicit **soft caps** for how many tags may be active at once, and these are now implemented and tested in this repo:
    - Scope: at most **2** active tags.
    - Method: at most **3** active tags.
    - Style: at most **3** active tags.
    Attempts to exceed these caps are handled by the central normaliser with deterministic, last-wins truncation and are surfaced consistently across speech, GUIs, and suggestions rather than being silently ignored.

### GUI behaviour

- **Axis widgets** (`lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`, `lib/modelHelpGUI.py`):
  - Completeness:
    - Single-select (radio / segmented / dropdown).
  - Scope/method/style:
    - Multi-select (checkboxes or tag chips).
    - Show currently active tags.
    - Provide a clear way to:
      - Add/remove individual tags.
      - Reset the axis to default (empty set or profile default).

- **Display and docs** (`GPT/gpt.py`, `GPT/readme.md`, model help GUIs):
  - Help text will describe:
    - Completeness: “pick one”.
    - Scope/method/style: “you can pick multiple; they stack unless explicitly incompatible”.
  - Example recipes will be updated to show realistic combinations:
    - “Jira story” → `style: jira + story`, `scope: actions`, `method: structure`.

### Validation and guardrails

We will:

- Introduce or extend tests under `tests/` to assert:

  - Single-valued completeness:
    - Multiple completeness tokens result in a deterministic final value.
  - Multi-valued scope/method/style:
    - Multiple tokens per axis are preserved as sets (after normalisation).
    - For **compatible** values, order of spoken modifiers does not affect the final set.
    - For **explicitly incompatible** values, last-wins behaviour is honoured and tested across profile, pattern, and user layers.
  - Incompatibility handling:
    - Explicitly-defined conflicting pairs/groups are resolved in a predictable way.
  - Static prompt & pattern alignment:
    - Profiles and patterns that declare multiple axis values behave as expected in GUI and `modelPrompt`.

- Update existing tests that currently assume one value per axis:
  - `tests/test_talon_settings_model_prompt.py`
  - `tests/test_model_pattern_gui.py`
  - Any concordance/axis-mapping tests that depend on scalar axis values.
  - Add at least one **end-to-end multi-tag regression path** that exercises:
    - Speech-driven modifiers with multiple scope/method/style tags.
    - Pattern and prompt-pattern execution with multi-tag axes.
    - `model suggest` proposing multi-tag combinations.
    - `model again` re-running a suggested multi-tag recipe and preserving the same canonical axis sets in `GPTState.last_*` and `last_recipe`.

- Add explicit *robustness* guardrails informed by adversarial analysis:
  - UX feedback on caps and incompatibilities:
    - At least one user-facing surface (for example, a GUI or quick-help recap) must make it clear when axis tags were dropped due to soft caps or incompatibility resolution, rather than relying solely on implicit inference from the remaining tags.
  - Negative and fuzz-style tests:
    - Add tests that cover:
      - Over-cap axis inputs from speech and suggestions (for example, more than two scope tags or more than three style tags), asserting the final sets and recaps match the documented caps and canonicalisation rules.
      - Recipes containing unknown or partially-known axis tokens, asserting they fail safely and predictably (for example, unknown tokens are ignored without breaking known ones, and behaviour remains deterministic).
  - Container-style incompatibility process:
    - When new “container-like” style tokens are introduced (for example, output surfaces such as `tweet`, `email`, `presenterm`, `shellscript`), ADR authors must make an explicit decision about their incompatibilities in `_AXIS_INCOMPATIBILITIES`, or document them as intentionally compatible; add a small guardrail test to catch container styles added without such a decision.
  - External contract for `GPTState.last_*`:
    - Document that `GPTState.last_scope`, `last_method`, and `last_style` are serialised multi-token sets (space-separated short tokens) and that external consumers must treat them as sets, not scalars, so integrations do not accidentally regress as axis multiplicity evolves.

---

## Consequences and migration

### Positive consequences

- **Expressiveness without combinatorial explosion**:
  - Axis combinations like `jira` + `story`, `slack` + `bullets`, `debugging` + `compare` are first-class and composable.
  - Fewer special-case static prompts and composite tokens are needed.

- **Clearer semantics**:
  - Completeness is explicitly scalar.
  - Scope/method/style behave like tags, matching how users already think and speak.

- **More precise profiles and patterns**:
  - Static prompt profiles and recipes can pin multiple axis values where that’s the natural domain shape.

### Negative / neutral consequences

- **Broader code changes**:
  - `lib/talonSettings.py::modelPrompt` and related helpers must be updated to handle list-valued axes.
  - Static prompt config, GUIs, and tests need refactors to normalise and reason about sets.

- **Potential compatibility edges**:
  - Anything that serializes or persists axis values (for example, last recipe state in `modelPrompt`) must:
    - Read both old (scalar) and new (list) representations.
    - Normalise into the new internal shape.

### Migration strategy

- **Internal representation first**:
  - Introduce a shared `AxisValues` representation (scalar completeness; list scope/method/style) and central normalisation helpers in the axis mapping domain (`lib/talonSettings.py` and/or a sibling helper).
  - Update `GPTSystemPrompt` (`lib/modelTypes.py`) and `GPTState` (`lib/modelState.py`) to:
    - Store scope/method/style internally as normalised lists.
    - Provide helpers to read/write them in both list form and a backwards-compatible, serialised string form for recaps and persistence.
  - Keep the visible system prompt schema stable initially (flatten lists to readable strings) so callers outside this repo do not need to change at the same time.

- **Static prompt profiles and patterns**:
  - Allow `STATIC_PROMPT_CONFIG` profiles to specify either a single token or a small list per axis (for scope/method/style), and have `get_static_prompt_axes` return list-valued axes.
  - In `lib/modelPatternGUI.py` and `lib/modelPromptPatternGUI.py`, parse pattern recipes into axis token sets and feed them through the same normalisation helpers, rather than hard-coding one token per axis.

- **modelPrompt and GPTState**:
  - Refactor `modelPrompt` in `lib/talonSettings.py` to:
    - Build `AxisValues` from profile defaults, pattern-derived axes (when present), and spoken/user overrides.
    - Apply the incompatibility table and last-wins, layer-aware semantics when resolving final axis sets.
  - Update `GPTState.last_*` fields to represent scope/method/style as canonicalised sets (internally lists, externally rendered strings), and ensure `last_recipe` is derived from the same canonical representation.
  - Ensure `gpt again` / rerun paths (`GPT/gpt.py`) construct axis sets from `GPTState.last_*` instead of assuming singular tokens.
  - Define and document a **canonical serialisation format** for `GPTState.last_scope`, `last_method`, and `last_style` (for example, space-separated short tokens in canonical order with no extra punctuation), and ensure all writers and readers of these fields use that format so equivalent axis sets always round-trip identically.

- **Grammar and multi-tag via speech**:
  - Update the `model` grammar in the Talon `.talon` files and `lib/talonSettings.py` captures so that:
    - `completenessModifier` remains single-valued.
    - `scopeModifier`, `methodModifier`, and `styleModifier` can each appear multiple times (for example, via `[...] <user.scopeModifier>+ [...]`-style rules).
  - Ensure the capture-to-axis plumbing:
    - Aggregates all recognised modifiers per axis into the `user_axes` layer (lists).
    - Feeds them through the same normalisation helpers as GUI- and pattern-driven axes.

- **GUIs and help surfaces**:
  - Update model pattern and prompt pattern GUIs to:
    - Display profile and pattern defaults as potentially multi-valued per axis (for example, `Style: jira story`).
    - Use the central normalisers when executing patterns so that GUI-launched prompts and spoken prompts follow the same rules.
  - Update quick-help canvases (`lib/modelHelpCanvas.py` and friends) so axis documentation and examples explicitly mention multi-tag scope/method/style.
  - Ensure suggestion-related surfaces and actions (for example, `model suggest`, `lib/modelSuggestionGUI.py`, and any underlying suggestion helpers):
    - Read and write axis values via the shared normalisation helpers so that suggested recipes and “apply suggestion” flows can use and recap multi-tag scope/method/style consistently.
    - Update their **own prompts to the model** so that suggestion generation is aware of and can propose multi-tag combinations on scope/method/style (for example, suggesting `jira + story` or `structure + flow` together where appropriate), rather than treating each axis as strictly single-valued.

- **Tests and compatibility**:
  - Extend existing tests (especially `test_talon_settings_model_prompt.py`, `test_model_pattern_gui.py`, `test_prompt_pattern_gui.py`, `test_static_prompt_config.py`, `test_model_types_system_prompt.py`, and `test_axis_mapping.py`) to:
    - Assert canonicalisation and last-wins semantics for multi-valued axes.
    - Guard backwards compatibility for existing single-valued behaviours and stored `last_*` shapes during the migration window.
  - Add a small number of explicit multi-tag recipes and profiles to serve as fixtures for long-term regression tests.

- **Documentation and ADR alignment**:
  - Update `GPT/readme.md`, GUI help, and axis docs to:
    - Clarify the scalar vs multi-tag distinction (completeness vs scope/method/style).
    - Provide concrete examples of recommended combinations and how conflicts are resolved.
  - Cross-link this ADR from earlier axis-related ADRs (005/012/013/018) to make the new semantics discoverable for contributors.

---

## Open questions

- **Future axes**:
  - If we later introduce additional axes (for example, `length`, `genre` as separate from `style`), do we:
    - Keep this scalar-vs-set convention (completeness-like vs tag-like), or  
    - Revisit where container/genre tokens live?

This ADR is **Accepted** and fully implemented in `talon-ai-tools` (see the accompanying work-log for evidence); any remaining questions above are explicitly future-looking and do not block the current axis multiplicity design.
