# 007 – Static Prompt Consolidation for Axis-Based Grammar – Work-log

This work-log tracks concrete changes made in this repo under ADR 007.

## 2025-12-02 – Initial ADR and classification (assistant-authored)

- Added ADR 007 (`docs/adr/007-static-prompt-consolidation.md`) describing:
  - Demotion candidates among static prompts that largely encode style/completeness/tone (`simple`, `short`, `clear`, `style`, `silly`, `announce`).
  - Consolidation targets among relational and planning prompts (`relation`, `dependency`, `cochange`, `interact`, `dependent`, `independent`, `parallel`, and the `todo`/`how to`/`incremental`/`bridge` cluster).
  - Rationale for preserving domain-heavy and format-heavy prompts as static prompts.
- No behavioural changes yet; this loop only introduces the ADR and an initial classification for future refactors.

## 2025-12-02 – Add new axis values for consolidation (assistant-authored)

- **Focus area**: Implement the new axis values proposed in ADR 007 so they are available for future consolidation work.
- **Changes made:**
  - Added new `methodModifier` entries in `GPT/lists/methodModifier.talon-list`:
    - `filter`: extract only items matching a named criterion.
    - `prioritize`: assess and order items by importance/impact to the audience.
    - `cluster`: group similar items into labeled categories and describe each cluster.
  - Added new `styleModifier` entry in `GPT/lists/styleModifier.talon-list`:
    - `checklist`: present the answer as an actionable checklist of imperative tasks.
  - Updated ADR 005 (`docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`) to:
    - Mention `filter`, `prioritize`, and `cluster` as examples for the method axis.
    - Mention `checklist` as an example for the style axis.
    - Expand example `model_default_method` and `model_default_style` values accordingly.
- **ADR 007 impact:**
  - Satisfies the “new axis values” part of ADR 007’s decision section.
  - Prepares the ground for future loops that will:
    - Demote axis-shaped static prompts,
    - Consolidate relational and planning prompts into recipes using these new axes.

## 2025-12-02 – Consolidate axis-shaped static prompts (assistant-authored)

- **Focus area**: Apply ADR 007’s consolidation to static prompts that mainly encode style/completeness/tone rather than semantic goals.
- **Changes made (static prompts):**
  - Removed axis-shaped prompts from `GPT/lists/staticPrompt.talon-list`:
    - `announce`, `simple`, `short`, `clear`, `silly`, `style`.
  - Simplified `STATIC_PROMPT_CONFIG` in `lib/staticPromptConfig.py`:
    - Removed profiles for `simple`, `short`, and `clear`, leaving `fix` as the primary “local edit” static prompt in this cluster.
- **Changes made (docs and examples):**
  - Updated `GPT/readme.md` to:
    - Drop example lines using `model simple …` and `model short …`.
    - Update the description of per-prompt defaults to reference `fix`, `todo`, and `diagram` instead of `fix`, `simple`, `short`, `todo`, `diagram`.
  - Updated ADR 005 (`docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`) to:
    - Remove references to `simple` as a profiled static prompt in the decision and status sections.
    - Adjust the example list of `styleModifier` values to include `checklist` and keep the static prompt notes accurate.
- **Rationale and relation to ADR 007:**
  - This loop takes the first concrete consolidation step by removing the most clearly axis-shaped prompts and aligning documentation with the new axis-first grammar.
  - It intentionally does not yet touch the relational/planning clusters, which will be addressed in later loops once more recipes are in place.

## 2025-12-02 – Planning cluster: tighten TODO/plan prompts (assistant-authored)

- **Focus area**: Apply ADR 007 to the planning-style static prompts, moving formatting into axes and trimming overlapping prompts.
- **Changes made (static prompts and profiles):**
  - Updated `todo` in `lib/staticPromptConfig.py` to use:
    - `style: "checklist"` instead of `"bullets"`, so TODO-like formatting is expressed via the style axis.
  - Removed `how to` and `incremental` from `GPT/lists/staticPrompt.talon-list`, eliminating overlapping “quick plan”/“incremental” statics in favour of:
    - `todo` + `bridge` as the primary planning static prompts,
    - Future axis-driven patterns for “quick how-to” and “incremental next step”.
- **Docs impact:**
  - No additional ADR 005 changes were required beyond the earlier axis and profile updates; the decision text there already covers `todo`/`diagram` as examples.
- **ADR 007 impact:**
  - Advances the consolidation of the planning cluster by:
    - Concentrating TODO behaviour into a single semantic static prompt (`todo`) with an explicit checklist style.
    - Removing closely related prompts that mainly differed in implied method/style, which now live more naturally in the axis space and pattern recipes.
  - Note: an earlier version of this entry anticipated removing `how to` and `incremental`; this loop completes that work concretely.

## 2025-12-02 – Filter-style cluster: move behaviour into the method axis (assistant-authored)

- **Focus area**: Align the “filter-style” prompts (pain, questions, relevance, misunderstandings, risks) and related patterns with the new `filter` method axis from ADR 007.
- **Changes made (axis/pattern machinery):**
  - Extended `METHOD_TOKENS` and `STYLE_TOKENS` in `lib/modelPatternGUI.py` so the pattern picker understands:
    - `filter`, `prioritize`, and `cluster` as method tokens.
    - `checklist` as a style token.
  - Updated the “Pain points” pattern in `lib/modelPatternGUI.py` to use the new method axis:
    - Recipe changed from `pain · gist · focus · bullets · fog` to `pain · gist · focus · filter · bullets · fog`.
- **Changes made (static prompts):**
  - Updated the filter-style static prompts in `lib/staticPromptConfig.py` to include `method: "filter"`:
    - `pain`, `question`, `relevant`, `misunderstood`, `risky` now all carry `completeness: "gist"`, `method: "filter"`, `style: "bullets"`, `scope: "focus"`.
  - This makes their “X-only list” behaviour explicit and reusable at the axis level.
- **Docs impact:**
  - Updated ADR 005 (`docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`) “Current Status” section so:
    - The `methodModifier` example list includes `filter`, `prioritize`, and `cluster`.
    - The per-static-prompt profile examples reflect the updated `todo` profile (now using `style: "checklist"`).
- **ADR 007 impact:**
  - Concretely moves the filter-style cluster toward axis-based semantics:
    - The prompts remain as semantic lenses (`pain`, `question`, etc.), but the filtering behaviour is now encoded via `method=filter`.
    - The pattern picker can now use the new method/style axis values in recipes without special-casing them.

## 2025-12-02 – Relational cluster: adopt relational scope (assistant-authored)

- **Focus area**: Apply ADR 007’s relational-scope design to the family of prompts that talk about how elements relate (dependencies, co-change, interaction, dependence/independence, parallelisation).
- **Changes made (static prompt profiles):**
  - Updated `relation` in `lib/staticPromptConfig.py` to set:
    - `scope: "relations"`, so it explicitly constrains discussion to relationships between elements.
  - Updated the main relationship-style prompts in `lib/staticPromptConfig.py` to also use `scope: "relations"`:
    - `dependency`, `cochange`, `interact`, `dependent`, `independent`, `parallel`.
  - These prompts already had descriptions focused on relationships; the new scope makes that territory explicit in the axis model and system prompt.
- **Docs impact:**
  - ADR 005 already described `relations` as a relational scope flavour in the constraint-dominance section, so no additional wording changes were needed for this slice.
- **ADR 007 impact:**
  - Moves the relational cluster closer to the ADR’s intent by:
    - Encoding “only talk about relationships and interaction patterns among these parts” via the scope axis instead of relying solely on prose descriptions.
    - Preparing the ground for future consolidation (for example, reducing the number of narrowly different relational prompts and expressing more nuance via axes and patterns).

## 2025-12-02 – Axis-based simplification patterns and TODO alignment (assistant-authored)

- **Focus area**: Replace removed simplification-style static prompts (`simple`, `short`) with axis-driven patterns, and align the TODO pattern with the new checklist style.
- **Changes made (patterns):**
  - Updated the “Extract todos” coding pattern in `lib/modelPatternGUI.py`:
    - Recipe changed from `todo · gist · focus · steps · bullets · ong` to `todo · gist · focus · steps · checklist · ong` to match the `todo` profile (`style: "checklist"`).
  - Added two new writing patterns in `lib/modelPatternGUI.py` that embody the former `simple`/`short` behaviours via axes:
    - `Simplify locally`:
      - Description: rewrite selected text in a simpler way, short but complete.
      - Recipe: `describe · gist · narrow · plain · fog`.
    - `Tighten summary`:
      - Description: shorten text while preserving core meaning.
      - Recipe: `describe · gist · focus · tight · fog`.
- **ADR 007 impact:**
  - Delivers concrete, GUI-surfaced replacements for the removed `simple` and `short` static prompts without reintroducing them as first-class keys.
  - Ensures TODO behaviour in both profiles and patterns is routed through the `checklist` style axis, reinforcing the axis-first grammar in everyday usage.

## 2025-12-02 – Help surfaces and README: align with new axes (assistant-authored)

- **Focus area**: Ensure the primary human-facing grammar surfaces (`model quick help` GUI and `GPT/readme.md`) reflect the consolidated axis vocabularies from ADR 005/007.
- **Changes made (README):**
  - Updated the modifier-axes section in `GPT/readme.md` so that:
    - Scope now lists `narrow`, `focus`, `bound`, `edges`, `relations`.
    - Method lists `steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`.
    - Style lists `plain`, `tight`, `bullets`, `table`, `code`, `checklist`, with `cards` still documented as an additional style.
  - Updated the TODO example to use the checklist style:
    - From `model todo gist bullets rog` to `model todo gist checklist rog`.
- **Changes made (help GUI):**
  - Updated fallback axis lists in `lib/modelHelpGUI.py`:
    - Scope fallback now includes `edges` and `relations`.
    - Method fallback now includes `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`.
    - Style fallback now includes `checklist`.
  - These fallbacks are only used when the Talon lists cannot be read, but they now stay in sync with the canonical axis vocabularies.
- **ADR 007 impact:**
  - Brings the visible grammar help and README in line with the consolidated axis design and new values introduced earlier, so users learn and reuse the intended axis set rather than the pre-consolidation subset.

## 2025-12-02 – Relational and risk patterns using new axes (assistant-authored)

- **Focus area**: Add small, high-leverage patterns that exercise the new relational scope (`relations`) and filter-style method semantics in everyday workflows.
- **Changes made (pattern picker):**
  - Extended `SCOPE_TOKENS` in `lib/modelPatternGUI.py` to include `relations` so pattern recipes can use the relational scope token.
  - Added a new coding pattern:
    - `Map dependencies`:
      - Description: list and explain key dependencies and what they depend on.
      - Recipe: `dependency · gist · relations · steps · fog`.
      - Uses the `dependency` static prompt, `relations` scope, and a stepwise method to bias toward a structured dependency overview.
  - Added a new writing/reflection pattern:
    - `Risk scan`:
      - Description: list and briefly explain key risks.
      - Recipe: `risky · gist · focus · filter · bullets · fog`.
      - Reuses the `risky` static prompt plus `method=filter` and bullet style to produce concise risk lists.
  - **ADR 007 impact:**
    - Exercises ADR 007’s consolidated axis design in concrete, discoverable presets:
      - `Map dependencies` demonstrates how relational scope can be combined with an existing relational static prompt and a planning-style method.
      - `Risk scan` demonstrates how filter-style semantics move into the method axis and pattern recipes instead of needing more static prompts.

## 2025-12-02 – Tests aligned with consolidated planning axes (assistant-authored)

- **Focus area**: Bring tests in line with the updated `todo` profile (now using `style: "checklist"`) so ADR 007’s changes are covered by the existing test suite.
- **Changes made (tests):**
  - Updated `tests/test_talon_settings_model_prompt.py`:
    - `test_model_prompt_uses_profiles_for_system_axes_when_unset` now expects:
      - `GPTState.system_prompt.style == "checklist"` for `staticPrompt="todo"`, matching the profile in `STATIC_PROMPT_CONFIG`.
    - `test_model_prompt_updates_last_recipe_with_profile_axes` now expects:
      - `GPTState.last_recipe == "todo · gist · focus · steps · checklist"`.
- **ADR 007 impact:**
  - Confirms that the consolidation of the planning cluster (particularly the move from bullets to checklist style for TODOs) is enforced and guarded by tests, reducing the risk of regressions back to the old profile.

## 2025-12-02 – Tests for filter-style and relational profiles (assistant-authored)

- **Focus area**: Add unit tests that cover the new axis-based profiles introduced by ADR 007 for filter-style and relational prompts.
- **Changes made (tests):**
  - Extended `tests/test_talon_settings_model_prompt.py` with:
    - `test_model_prompt_uses_profiles_for_filter_style_prompts`:
      - Uses `staticPrompt="pain"` with no spoken modifiers.
      - Asserts that `GPTState.system_prompt` reflects the profile from `STATIC_PROMPT_CONFIG`:
        - `completeness == "gist"`, `scope == "focus"`, `method == "filter"`, `style == "bullets"`.
    - `test_model_prompt_uses_relations_scope_for_dependency_prompts`:
      - Uses `staticPrompt="dependency"` with no spoken modifiers.
      - Asserts that `GPTState.system_prompt.scope == "relations"`.
- **ADR 007 impact:**
  - Strengthens guardrails around the consolidated axis semantics by:
    - Ensuring filter-style prompts (`pain`, etc.) actually drive `method=filter` and related axes as intended.
    - Ensuring relational prompts (`dependency` and peers) use the relational scope in the effective axes, matching ADR 007’s relational-scope design.

## 2025-12-02 – Status reconciliation and snapshot (assistant-authored)

- **Focus area**: Reconcile ADR 007’s stated intent with the current repo state and mark the ADR as accepted for this repo.
- **Changes made:**
  - Updated ADR 007 (`docs/adr/007-static-prompt-consolidation.md`) to:
    - Change `Status: Proposed` to `Status: Accepted`.
    - Add a “Current Status (this repo)” section summarising:
      - Implemented axis values (`filter`, `prioritize`, `cluster`, `checklist`, `relations`).
      - Static prompt consolidation (removal of axis-shaped prompts; planning prompts centred on `todo` and `bridge`; relational prompts using `scope: "relations"`).
      - Pattern and help updates (new simplification, planning, relational, and risk patterns; help/README aligned with new axes).
      - Tests that now enforce the consolidated behaviour.
- **ADR 007 impact:**
  - Clarifies that, for this repo, ADR 007’s core changes are implemented and in effect.
  - Provides a snapshot so future loops can treat remaining tweaks as incremental refinement rather than open design work.

## 2025-12-02 – Planning-cluster text aligned with implemented state (assistant-authored)

- **Focus area**: Bring ADR 007’s narrative about the planning cluster in line with the now-implemented consolidation (only `todo` and `bridge` remain as planning statics).
- **Changes made:**
  - Updated the “Planning cluster” subsection in ADR 007 (`docs/adr/007-static-prompt-consolidation.md`) to:
    - Describe the cluster as `todo`, `bridge` instead of `todo`, `how to`, `incremental`, `bridge`.
    - Frame “quick how-to” and “incremental next step” as axis/pattern recipes over `todo`/`bridge` rather than future static prompts to be removed.
- **ADR 007 impact:**
  - Removes the lingering implication that `how to` and `incremental` are still present and awaiting consolidation, making the ADR text match the current static prompt surface and pattern design.

## 2025-12-02 – Everyday usage examples added to ADR 007 (assistant-authored)

- **Focus area**: Make ADR 007 more directly actionable by adding concrete “after consolidation” usage examples that tie static prompts, axes, and patterns together.
- **Changes made:**
  - Extended ADR 007 (`docs/adr/007-static-prompt-consolidation.md`) with:
    - A short “Everyday usage after consolidation (this repo)” section that:
      - Shows how to express former `simple`/`short` behaviours via `describe` + axes or the `Simplify locally` / `Tighten summary` patterns.
      - Shows how to use `todo` + `checklist` (and the “Extract todos” pattern) and `bridge` for planning flows.
      - Shows how to use `relations` scope and the `dependency` prompt (or “Map dependencies”) for relationship work.
      - Shows how to use filter-style prompts (`pain`, `question`, `relevant`, `misunderstood`, `risky`) with `method=filter` or via the “Pain points” / “Risk scan” patterns.
    - A brief note in the “Current Status” section that tests now assert the consolidated `todo`, filter-style, and relational profiles.
- **ADR 007 impact:**
  - Gives future readers a concise, usage-oriented snapshot of what “post-consolidation” looks like in day-to-day commands, without needing to infer it from the decision text and work-log alone.

## 2025-12-02 – Help surfaces: reminders for replaced prompts (assistant-authored)

- **Focus area**: Add small, in-context reminders in the help surfaces about how to replace the removed static prompts using axes and patterns.
- **Changes made (GUI quick help):**
  - Extended `_show_examples` in `lib/modelHelpGUI.py` with a short “Replaced prompts” subsection that reminds users:
    - `simple` → use `describe · gist · plain` (or the “Simplify locally” pattern).
    - `short` → use `describe · gist · tight` (or the “Tighten summary” pattern).
    - TODO-style “how to” → use `todo · gist · checklist` (or the “Extract todos” pattern).
- **Changes made (HTML gpt_help):**
  - Added a “Replaced prompts (ADR 007)” section in `GPT/gpt.py`’s `gpt_help()` output that lists:
    - `simple` → `describe` + `gist` + `plain` (or “Simplify locally”).
    - `short` → `describe` + `gist` + `tight` (or “Tighten summary”).
    - `how to` / `incremental` → `todo`/`bridge` with `steps` + `checklist`/`minimal` (or “Extract todos”).
- **ADR 007 impact:**
  - Makes the consolidation more discoverable in everyday use by:
    - Providing lightweight mapping hints directly in the help UIs, without reintroducing old static prompts.
    - Reinforcing the axis-first mental model and the new patterns whenever users reach for help.
