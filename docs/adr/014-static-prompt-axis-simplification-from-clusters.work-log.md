# 014 – Static Prompt Axis Simplification from Clustered Behaviours – Work-log

## 2025-12-04 – Initial loop: ADR authoring and intent clarification

- Created `014-static-prompt-axis-simplification-from-clusters.md` describing:
  - How remaining static prompts implicitly encode completeness/scope/method/style clusters.
  - New candidate axis tokens (`framework`, `path`, `system`, `actions`, `ladder`, `contextualise`) derived from those clusters.
  - A plan to encode static prompt behaviour via axis profiles and retire axis-shaped prompts in favour of recipes.
- Updated the ADR to:
  - Clarify that axis-shaped static prompts will be **retired**, not merely de-emphasised, once their behaviour is expressed via axis tokens and recipes.
  - Commit to tracking removals in this work-log rather than deferring them to a separate ADR.
- No code or list changes yet; this loop focused on defining intent and concrete next steps for implementation.

## 2025-12-04 – Loop: Introduce axis tokens and wire initial static prompts

- Added new axis modifiers based on clustered behaviours:
  - `GPT/lists/completenessModifier.talon-list`: `framework`, `path`.
  - `GPT/lists/scopeModifier.talon-list`: `system`, `actions`.
  - `GPT/lists/methodModifier.talon-list`: `ladder`, `contextualise`.
- Updated `lib/staticPromptConfig.py` to use the new tokens for representative prompts:
  - `system`: now uses `completeness=framework`, `scope=system`, `method=systems`, `style=plain`.
  - `effects`: now uses `scope=dynamics` (keeping `completeness=full`, `method=steps`, `style=plain`).
  - `problem`: now uses `method=ladder` instead of `steps`.
  - `todo`: now uses `scope=actions` instead of `focus`.
  - `bridge`: now uses `completeness=path` instead of `full`.
- Loosened and updated tests to reflect the new axis profile for `todo`:
  - `tests/test_static_prompt_config.py`: still asserts that `todo` has a full axis profile but now checks individual fields and expects `scope="actions"`.
  - `tests/test_talon_settings_model_prompt.py`: `last_recipe` expectation updated to `"todo · gist · actions · steps · checklist"`, and `GPTState.last_scope` now expected to be `"actions"`.
- This loop lands the first behavioural slice of ADR 014: axis tokens exist in the lists, are exercised by live static prompt profiles, and are covered by unit tests via `todo`’s profile. Further loops can extend usage to additional prompts and add GUI recipes that surface these axis combinations.

## 2025-12-04 – Loop: Retire first axis-shaped static prompts

- Retired the most clearly axis-shaped static prompts from the spoken/static surface by removing them from `GPT/lists/staticPrompt.talon-list`:
  - `group` (now intended as “any semantic prompt + method=cluster” via recipes).
  - `sort` (now intended as “any semantic prompt + method=prioritize” via recipes).
  - `problem` (now intended as “describe + method=ladder + scope=focus” via recipes).
- Removed the corresponding static prompt profiles from `lib/staticPromptConfig.py` so they no longer appear in static prompt help generated from `STATIC_PROMPT_CONFIG`.
- No tests referenced these static prompts directly, so behaviour remains green; future loops will add explicit pattern recipes to surface these behaviours via axes instead of static prompts.

## 2025-12-04 – Loop: Add axis-based recipes for retired prompts

- Updated the main model pattern GUI to expose axis-based replacements for the retired static prompts:
  - `lib/modelPatternGUI.py`:
    - Adjusted the existing “Extract todos” pattern to use the new `actions` scope in its recipe (`todo · gist · actions · steps · checklist · ong`).
    - Added “Cluster items” (`describe · full · narrow · cluster · plain · fog`) to cover the old `group` behaviour.
    - Added “Rank items” (`describe · full · narrow · prioritize · plain · fog`) to cover the old `sort` behaviour.
    - Added “Abstraction ladder” (`describe · full · focus · ladder · plain · rog`) to cover the old `problem` behaviour.
- Extended the prompt-specific pattern GUI presets so these behaviours can also be applied around any static prompt:
  - `lib/modelPromptPatternGUI.py`:
    - Added presets for “Abstraction ladder”, “Cluster items”, and “Rank items” with the same axis profiles (full/narrow/focus + `ladder`/`cluster`/`prioritize`).
- Kept existing tests green and updated expectations where needed:
  - `tests/test_prompt_pattern_gui.py`: kept the first preset as “Quick gist” and left its expected `last_recipe` (`todo · gist · focus · plain`) intact, while the new presets are covered indirectly via shared pattern execution logic.
- This loop completes the first end-to-end slice for ADR 014 where:
  - Axis tokens exist and are wired to static prompt profiles.
  - The most obviously axis-shaped static prompts (`group`, `sort`, `problem`) are retired.
  - Equivalent behaviours are available via axis-based recipes in both the main pattern GUI and the prompt-specific pattern GUI.

## 2025-12-04 – Loop: Wire contextual axis tokens into profiles and tests

- Extended `lib/staticPromptConfig.py` so more static prompts use the clustered axis tokens introduced by ADR 014:
  - `context`: now has an explicit axis profile – `completeness=gist`, `method=contextualise`, `style=plain`, `scope=focus` – matching its “add context only” semantics.
  - Confirmed earlier changes for:
    - `system` → `completeness=framework`, `scope=system`, `method=systems`, `style=plain`.
    - `effects` → `scope=dynamics` (second- and third-order effects).
    - `bridge` → `completeness=path` (explicit transition path).
- Tightened tests to validate use of the new axis tokens:
  - `tests/test_static_prompt_config.py`:
    - Added `test_static_prompt_axes_include_clustered_tokens`, which spot-checks:
      - `system` uses `framework`/`system`/`systems`.
      - `bridge` uses `path` completeness.
      - `effects` uses `dynamics` scope.
      - `context` uses `contextualise` method.
- This loop increases confidence that ADR 014’s new axis values are not just present in the lists, but actually drive behaviour of key static prompts and are guarded by tests.

## 2025-12-04 – Loop: Align README axis documentation with new tokens

- Updated the axis cheat sheet in `GPT/readme.md` so it reflects the expanded axis vocabularies introduced by ADR 014:
  - Completeness now lists `framework` and `path` alongside `skim`, `gist`, `full`, `max`, `minimal`, `deep`.
  - Scope now lists `dynamics`, `interfaces`, `system`, and `actions` alongside `narrow`, `focus`, `bound`, `edges`, `relations`.
  - Method now lists `ladder` and `contextualise` alongside existing values.
- This keeps the user-facing README in sync with the actual Talon lists under `GPT/lists` and with the clustered axis tokens now used in `STATIC_PROMPT_CONFIG` and tests.

## 2025-12-04 – Loop: Status reconciliation and ADR closure

- Marked ADR 014 as **Accepted** now that:
  - New axis tokens (`framework`, `path`, `system`, `actions`, `ladder`, `contextualise`) are defined in the modifier lists.
  - Key static prompts (`system`, `todo`, `bridge`, `effects`, `context`) use these tokens in `STATIC_PROMPT_CONFIG`.
  - The most clearly axis-shaped static prompts (`group`, `sort`, `problem`) are retired and replaced with axis-based patterns.
  - Tests and GUIs exercise the new axis semantics.
- Added a “Current Status (this repo)” section to ADR 014 summarising:
  - The axis vocabularies in use.
  - Which static prompt profiles are wired to the new tokens.
  - Which prompts were retired and how their behaviours are exposed via patterns.
  - The presence of tests and README updates that guard and document the new behaviour.
- With this loop, there is no substantial remaining in-repo work for ADR 014; future adjustments around static prompts will either:
  - Reuse the same axis vocabulary and recipes established here, or
  - Be governed by new ADRs if they introduce qualitatively new behaviours.

