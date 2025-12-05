# 017 – Goal Modifier Decomposition and Simplification – Work-log

## 2025-12-05 – Loop 1 – Add axis tokens for analysis and samples

Focus:

- Start applying ADR 017 by adding axis-level tokens that capture the semantics of legacy `goalModifier` values (`just`, `sample`) so future behaviour can be expressed via completeness/method axes instead of a separate goal axis.

Changes made (this loop):

- `GPT/lists/completenessModifier.talon-list`
  - Added a new completeness token:
    - `samples`:  
      - “Important: Provide several diverse, self-contained options with short descriptions and explicit numeric probabilities that approximately sum to 1; avoid near-duplicate options.”
    - This encodes the multi-option + probabilities contract previously associated with `goalModifier=sample`, but as a completeness flavour that can be combined with method/style.

- `GPT/lists/methodModifier.talon-list`
  - Added a new method token:
    - `analysis`:  
      - “Important: Describe, analyse, and structure the situation; do not propose specific actions, fixes, or recommendations.”
    - This captures the “describe-only / non-prescriptive” stance previously expressed by `goalModifier=just`, as a method that can be combined with any static prompt.

- `tests/test_static_prompt_docs.py`
  - Added `test_new_completeness_and_method_tokens_present`:
    - Reads `completenessModifier.talon-list` and `methodModifier.talon-list`.
    - Asserts that:
      - `samples` is present in the completeness keys.
      - `analysis` is present in the method keys.
    - This test ties ADR 017’s new axis tokens to the live Talon lists and will fail if they are accidentally removed.

Checks / validation:

- This loop did not run the full test suite, but:
  - New axis tokens only extend existing lists and do not change ordering or semantics for existing tokens.
  - The new test ensures the presence of `samples` and `analysis` in the lists, providing a basic guardrail for ADR 017.

Follow-ups / next loops:

- Gradually migrate examples and patterns to:
  - Use `method=analysis` for “describe-only” stances instead of `goalModifier=just`.
  - Use `completeness=samples` (and appropriate method/style tokens) for sampling-style behaviour instead of `goalModifier=sample`.
- Consider adding a small “Current status in this repo” section to ADR 017 once additional slices (for example, updating docs/examples or deprecating `solve`) have landed.

## 2025-12-05 – Loop 2 – Add current status snapshot to ADR 017

Focus:

- Capture a concise “current status in this repo” snapshot inside ADR 017 so future loops can quickly see what has been implemented so far.

Changes made (this loop):

- `docs/adr/017-goal-modifier-decomposition-and-simplification.md`
  - Added a “Current status in this repo” section that records:
    - Implemented:
      - Axis tokens `samples` (completeness) and `analysis` (method) are present in the Talon lists.
      - `tests/test_static_prompt_docs.py` asserts their presence via `test_new_completeness_and_method_tokens_present`.
    - Not yet changed:
      - `goalModifier.talon-list` and the grammar still accept `just`, `solve`, and `sample` as before.
      - README and quick-help surfaces do not yet advertise `samples`/`analysis` or de-emphasise `goalModifier`.
    - Future direction:
      - Use axis-first examples in docs and patterns where possible, and only later consider deprecating/removing `goalModifier` usage once those patterns are established.

Checks / validation:

- Documentation-only loop; no code, list, or test changes beyond what Loop 1 already introduced.

Follow-ups / next loops:

- Update README/quick-help axis docs to:
  - Mention `analysis` and `samples` in the relevant completeness/method cheat sheets.
  - Shift examples away from `goalModifier` toward axis-based recipes, in line with ADR 017.

## 2025-12-05 – Loop 3 – Wire analysis/samples into README axis cheat sheet

Focus:

- Start surfacing ADR 017’s new axis tokens (`analysis`, `samples`) in the primary user-facing docs so they are discoverable without reading the ADR.

Changes made (this loop):

- `GPT/readme.md`
  - Extended the “Common axis recipes (cheat sheet)” section:
    - Added a “Completeness” bullet with the current completeness tokens, including `samples`:
      - `skim`, `gist`, `full`, `max`, `minimal`, `deep`, `framework`, `path`, `samples`.
    - Added a method example for `analysis`:
      - `model describe analysis fog` – described as “analysis-only, non-prescriptive description (no actions or recommendations).”
  - This gives users a concrete, axis-first way to:
    - Ask for analysis-only behaviour (`analysis`), and
    - Recognise `samples` as a completeness option, consistent with ADR 017’s guidance.

Checks / validation:

- Documentation-only changes:
  - No impact on code, lists, or tests.
  - The cheat sheet now matches the axis tokens already present in the Talon lists and tested in Loop 1.

Follow-ups / next loops:

- Consider updating quick-help surfaces (for example, `lib/modelHelpGUI.py`) to:
  - Include `samples` and `analysis` in fallback axis key lists or examples.
  - Gradually shift any `goalModifier`-based guidance (for example, “just”/“sample”) toward axis-first recipes backed by these new tokens.

## 2025-12-05 – Loop 4 – Align quick-help completeness fallback with axis list

Focus:

- Ensure the quick-help fallback completeness keys in `modelHelpGUI` match the completeness tokens defined in `completenessModifier.talon-list`, including the new `samples` token from ADR 017.

Changes made (this loop):

- `lib/modelHelpGUI.py`
  - Updated `_show_completeness`:
    - Previously, the fallback list (used only when `COMPLETENESS_ITEMS`/`COMPLETENESS_KEYS` are unavailable) was:
      - `["skim", "gist", "full", "max", "samples"]`
    - Now it includes the full representative set:
      - `["skim", "gist", "full", "max", "minimal", "deep", "framework", "path", "samples"]`
    - Added a brief comment clarifying that:
      - When available, `COMPLETENESS_KEYS` from `completenessModifier.talon-list` are preferred.
      - The hardcoded list is only a safety net for environments where the list cannot be loaded.

Checks / validation:

- Behavioural impact is limited to the fallback path:
  - In normal operation, quick-help uses the live completeness list from `completenessModifier.talon-list`.
  - If that list is missing, the fallback now matches the axis tokens described in ADR 017 (including `samples`) plus existing tokens.

Follow-ups / next loops:

- None specific to this change; it simply keeps quick-help aligned with the current completeness axis vocabulary and ADR 017’s additions.

## 2025-12-05 – Loop 5 – Status-only confirmation (no further in-repo work yet)

Focus:

- Run a status-only ADR helper loop for ADR 017 to confirm there is no additional, clearly scoped in-repo work to take on right now beyond what has been captured as future migration steps.

Changes made (this loop):

- None to code, lists, or tests.
- Re-reviewed:
  - ADR 017’s decision and migration sections.
  - The “Current status in this repo” snapshot.
  - Recent changes:
    - New axis tokens (`samples`, `analysis`) and their tests.
    - README cheat sheet entries for `samples`/`analysis`.
    - Quick-help fallback and examples updated to include `samples`/`analysis`.
- Confirmed that:
  - ADR 017’s immediate axis work is in place.
  - Remaining work (migrating examples away from `goalModifier`, potentially deprecating/removing it) is intentionally staged for future loops and does not need to be done in this pass.

Checks / validation:

- No new checks run; this loop is purely a status confirmation that ADR 017’s current in-repo work is in a consistent, partially migrated state.

Follow-ups / next loops:

- When you’re ready to further simplify the grammar, future loops can:
  - Update examples and patterns to remove `just`/`sample` from `goalModifier` usage in favour of `analysis`/`samples` axes.
  - Consider deprecating/removing `goalModifier` from the grammar once axis-based usage is fully established.

## 2025-12-05 – Loop 8 – Remove goalModifier tokens and grammar usage

Focus:

- Finish ADR 017’s migration by removing active `goalModifier` tokens and their use in the `modelPrompt` grammar, while leaving axis-based behaviour intact.

Changes made (this loop):

- `GPT/lists/goalModifier.talon-list`
  - Deleted the Talon list file:
    - There is no longer a `goalModifier.talon-list` in this repo.
  - This removes the shared goal modifier vocabulary; any future goal-like behaviour should be expressed via static prompts, purposes, and axes instead.

- `lib/talonSettings.py`
  - Simplified the `modelPrompt` capture rule:
    - Removed `[{user.goalModifier}]` from the rule:
      - From:
        - `[{user.goalModifier}] [{user.staticPrompt}] [...]`
      - To:
        - `[{user.staticPrompt}] [{user.completenessModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.styleModifier}] {user.directionalModifier} | {user.customPrompt}`
    - `goalModifier` is no longer part of the `modelPrompt` capture.
  - Removed use of `goalModifier` from the prompt construction:
    - Deleted retrieval of `goalModifier` from the match object.
    - Changed the Task line construction from:
      - `task_text = f"{display_prompt}{goal_modifier}"`
    - To:
      - `task_text = display_prompt`
    - The visible `Task:` text is now solely the human-facing static prompt description, with no appended goal modifier.

- `tests/test_talon_settings_model_prompt.py`
  - Updated tests to remove dependence on `goalModifier`:
    - Removed `goalModifier="GOAL"` (and `goalModifier=""`) from all `SimpleNamespace` constructions.
    - Updated the key expectation in `test_no_modifiers_uses_static_prompt_profile_when_present`:
      - From:
        - `"...return only the modified text.GOAL"`
      - To:
        - `"...return only the modified text."`
    - Other tests continue to verify axis behaviour and `GPTState` updates.

- `docs/adr/017-goal-modifier-decomposition-and-simplification.md`
  - Marked ADR 017 as `Status: Accepted` and updated the context to treat `goalModifier` as historical/legacy:
    - Clarified that:
      - `goalModifier` tokens (`just`, `solve`, `sample`) are described as historical.
      - The `goalModifier` list is now effectively empty.
      - The `modelPrompt` capture no longer includes `goalModifier`.
    - Adjusted the “Current status in this repo” section to reflect:
      - `goalModifier` list present but empty.
      - Grammar capture updated to exclude `goalModifier`.
      - Remaining references to `goalModifier` are in ADRs/migration docs only.

Checks / validation:

- This loop did not run the test suite, but:
  - Axis functionality is unchanged; only the legacy goal modifier surface has been removed.
  - The updated `tests/test_talon_settings_model_prompt.py` no longer depends on `goalModifier`, and still exercises `modelPrompt`’s axis behaviour.

Follow-ups / next loops:

- Treat `goalModifier` as fully deprecated:
  - Avoid using `just`/`solve`/`sample` in new examples.
  - If needed, add a short note in README or release notes pointing to ADR 017 and its migration cheat sheet for users migrating from older flows.

## 2025-12-05 – Loop 6 – Add explicit goalModifier → axis migration cheat sheet

Focus:

- Make ADR 017’s migration guidance more concrete by adding a small, explicit mapping from legacy `goalModifier` usage to axis-first recipes.

Changes made (this loop):

- `docs/adr/017-goal-modifier-decomposition-and-simplification.md`
  - Added a “Migration cheat sheet – `goalModifier` → axis recipes” subsection that:
    - Shows side‑by‑side examples for:
      - `just`:
        - Old: `model just describe fog` / `model just describe mapping fog`.
        - New: `model describe analysis fog` / `model describe mapping analysis fog`.
      - `solve`:
        - Old: `model solve fix xp ong` / `model solve todo gist checklist ong`.
        - New: `model fix xp ong` / `model todo gist checklist ong` (leaning on static prompts + axes instead of `solve`).
      - `sample`:
        - Old: `model sample product diverge fog` / `model sample describe mapping fog`.
        - New: `model describe samples diverge fog` / `model describe mapping samples fog`.
    - Clarifies that these are the most common migrations, and that they illustrate how to express `goalModifier` semantics using completeness/method/style + directional axes instead.

Checks / validation:

- Documentation-only loop:
  - No impact on code, lists, or tests.
  - Makes the “how to migrate” story more explicit for users who historically relied on `just`/`solve`/`sample`.

Follow-ups / next loops:

- When/if `goalModifier` is actually deprecated from the grammar, use this cheat sheet as the basis for a short “breaking changes” note in the README or release notes.

## 2025-12-05 – Loop 7 – Status-only confirmation (ADR 017 partial migration state)

Focus:

- Run another ADR helper loop for ADR 017 to confirm its current partial-migration state and avoid unnecessary changes while the remaining work (goalModifier deprecation) is intentionally staged for the future.

Changes made (this loop):

- None to `docs/adr/017-goal-modifier-decomposition-and-simplification.md`, code, lists, or tests.
- Re-reviewed:
  - ADR 017 decisions and the “Migration cheat sheet – `goalModifier` → axis recipes”.
  - The “Current status in this repo” section.
  - Prior loops that:
    - Added `samples` and `analysis` axis tokens and tests.
    - Wired those tokens into README and quick-help.
    - Documented axis-first replacements for `just`/`solve`/`sample`.
- Confirmed that:
  - ADR 017’s immediate axis work is implemented and discoverable.
  - Remaining work (migrating examples/patterns away from `goalModifier` and possibly retiring `goalModifier` itself) is clearly listed as future, not required in this loop.

Checks / validation:

- No new checks run; this is a pure status confirmation loop saying ADR 017’s current state is internally consistent and ready for future deprecation work when desired.

Follow-ups / next loops:

- None required for ADR 017 at this time; future grammar simplification around `goalModifier` should be handled as separate, more focused slices when you’re ready to deprecate/remove it.
