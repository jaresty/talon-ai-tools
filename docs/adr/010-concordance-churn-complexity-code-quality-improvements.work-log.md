# ADR-010 Work-log – Concordance Churn × Complexity Code Quality Improvements

## 2025-12-03 – Loop 1 – Axis value→key mapping characterization

Focus area:

- `lib/talonSettings.py::_read_axis_value_to_key_map`
- Related last_recipe tokenisation via `_axis_recipe_token`.

Changes in this loop:

- Confirmed that `_read_axis_value_to_key_map`:
  - Builds a mapping from both the short key and the full description text back to the short key.
  - Ignores comments, header lines, bare `-` sentinels, and lines without a `:` separator.
  - Returns an empty mapping when the backing Talon list file is missing.
- Left the implementation behaviourally unchanged, but:
  - Identified the absence of direct unit tests around this mapping function.
  - Chose to address this gap in a follow-up loop that will:
    - Add focused tests for `_read_axis_value_to_key_map` and `_axis_recipe_token`.
    - Use a minimal fixture Talon list file to exercise typical and edge cases (keys only, key+description, malformed lines, missing file).

Impact on ADR-010 objectives:

- Clarified the expected behaviour and edge cases for one of the key hotspots called out in ADR-010.
- Prepared a concrete, tests-first slice for the next loop to reduce risk around axis mapping churn without yet changing runtime behaviour.

Follow-ups (not completed in this loop):

- Add targeted tests for `_read_axis_value_to_key_map` and `_axis_recipe_token` that:
  - Cover mapping from short keys and long descriptions back to short keys.
  - Exercise handling of malformed lines and missing files.
- Consider small refactors (once tests are in place) to:
  - Share axis parsing/mapping behaviour with any future static-prompt domain APIs, keeping mapping logic in a single, well-tested place.

---

## 2025-12-03 – Loop 2 – Tests for axis value→key mapping and recipe tokens

Focus area:

- `lib/talonSettings.py::_read_axis_value_to_key_map`
- `lib/talonSettings.py::_axis_recipe_token`

Changes in this loop:

- Added a dedicated Talon list fixture for tests at `GPT/lists/testsAxisMapping.talon-list` containing:
  - Two well-formed `key: description` entries.
  - Comment, header, dash, and malformed lines to exercise filtering.
- Added `tests/test_axis_mapping.py` with focused tests that:
  - Verify `_read_axis_value_to_key_map("testsAxisMapping.talon-list")`:
    - Maps both the short keys and their long descriptions back to the short key.
    - Ignores comments, list headers, bare `-` lines, and lines without a colon.
    - Returns exactly four mappings (two keys + two descriptions).
  - Confirm `_read_axis_value_to_key_map` returns an empty dict for a missing file.
  - Exercise `_axis_recipe_token` against real configuration by:
    - Parsing one entry from `GPT/lists/completenessModifier.talon-list`.
    - Asserting the long description maps back to the short key for the `completeness` axis.
    - Asserting the short key maps idempotently to itself.
    - Verifying that an unknown axis leaves the value unchanged.

Impact on ADR-010 objectives:

- Strengthens tests around a churn-heavy hotspot identified in ADR-010 without changing runtime behaviour.
- Provides explicit, branch-focused coverage for axis value→key mapping and recipe tokenisation, reducing refactor risk for future changes in this area.

Validation:

- Attempted to run `pytest tests/test_axis_mapping.py -q`, but `pytest` is not available in this environment. The tests are structured to run under the existing unittest-based harness (via `bootstrap`) when executed in a fully configured environment.

Follow-ups (not completed in this loop):

- When a full test runner is available, run the new tests and adjust as needed.
- Use these tests as a safety net for any subsequent refactors that:
  - Share mapping logic with a future static-prompt domain API.
  - Change how last_recipe tokens are derived from axis descriptions.

---

## 2025-12-03 – Loop 3 – Static prompt domain helpers and characterization tests

Focus area:

- `lib/staticPromptConfig.py` – introduce a minimal domain API around static prompt profiles and axes.

Changes in this loop:

- Added small, explicit helpers in `lib/staticPromptConfig.py`:
  - `get_static_prompt_profile(name: str) -> StaticPromptProfile | None` – single entrypoint for looking up profile metadata instead of reaching into `STATIC_PROMPT_CONFIG` directly.
  - `get_static_prompt_axes(name: str) -> dict[str, str]` – returns a `{axis -> value}` mapping for the configured subset of `completeness`, `scope`, `method`, and `style`, or `{}` for unknown/description-only prompts.
- Added characterization tests in `tests/test_static_prompt_config.py` to cover the new domain API:
  - `get_static_prompt_profile("todo")` returns a profile with the expected description and completeness.
  - `get_static_prompt_profile("nonexistent")` returns `None`.
  - `get_static_prompt_axes("todo")` returns the full axis set defined in the configuration (completeness/method/style/scope).
  - `get_static_prompt_axes("describe")` (a description-only profile) returns `{}`.
  - `get_static_prompt_axes("nonexistent")` returns `{}`.

Impact on ADR-010 objectives:

- Establishes a clear, reusable domain surface for static prompt profiles and axes that later refactors (GUI, settings, docs) can consume, aligning with ADR-010’s Phase 2 “Introduce explicit domain APIs”.
- Provides direct tests for this domain API so future changes to profile/axis behaviour can be made safely without relying solely on higher-level tests.

Validation:

- New tests are structured for the existing unittest + bootstrap harness and can be run (in a fully configured environment) via:
  - `python -m unittest tests.test_static_prompt_config`

Follow-ups (not completed in this loop):

- Incrementally migrate callers (e.g. GUI and settings code) to use `get_static_prompt_profile` / `get_static_prompt_axes` instead of reading `STATIC_PROMPT_CONFIG` directly, guided by the existing characterization tests.

---

## 2025-12-03 – Loop 4 – Migrate modelPrompt to the static prompt domain API

Focus area:

- `lib/talonSettings.py::modelPrompt` – use the new static prompt domain helpers instead of reaching into `STATIC_PROMPT_CONFIG` directly.

Changes in this loop:

- Updated `modelPrompt` in `lib/talonSettings.py` to:
  - Use `get_static_prompt_profile(static_prompt)` to obtain the profile and its `description` (for the Task line) instead of calling `STATIC_PROMPT_CONFIG.get` directly.
  - Use `get_static_prompt_axes(static_prompt)` to obtain profile axis defaults and drive:
    - Effective axis resolution (spoken > profile > defaults) for completeness/scope/method/style.
    - The Constraints block when no spoken modifiers are present.
- Left the higher-level behaviour unchanged (spoken modifiers still win over profile axes, and defaults still apply when neither spoken nor profile values are present), but now the logic is expressed in terms of the domain API.

Impact on ADR-010 objectives:

- Advances Phase 2 by moving a key settings entrypoint (`modelPrompt`) away from direct access to `STATIC_PROMPT_CONFIG` and onto the domain helpers, while keeping behaviour stable.
- Makes it easier to evolve static prompt profiles/axes in one place without having to update consumers that previously depended on the raw configuration structure.

Validation:

- Ran the focused tests for this area:
  - `python -m unittest tests.test_talon_settings_model_prompt tests.test_static_prompt_config tests.test_axis_mapping`
  - All tests passed, confirming that the refactor preserved existing behaviour and that the domain helpers remain correctly characterized.

Follow-ups (not completed in this loop):

- Migrate GUI callers (`modelHelpGUI`, `modelPromptPatternGUI`) to use `get_static_prompt_profile` / `get_static_prompt_axes` rather than reading `STATIC_PROMPT_CONFIG` directly, using the same tests-first approach.

---

## 2025-12-03 – Loop 5 – Migrate modelHelpGUI to the static prompt domain API

Focus area:

- `lib/modelHelpGUI.py::model_help_gui` – align the help GUI with the static prompt domain helpers.

Changes in this loop:

- Updated `model_help_gui` so that, when a specific static prompt is in focus:
  - It uses `get_static_prompt_profile(sp)` and `get_static_prompt_axes(sp)` instead of reading `STATIC_PROMPT_CONFIG` directly.
  - Profile defaults for completeness/scope/method/style are drawn from the same domain API used by `modelPrompt`, ensuring a single source of truth for axis defaults.
- Left the visible output structure unchanged (still showing “Profile defaults:” and one line per axis where applicable).

Impact on ADR-010 objectives:

- Brings the help GUI into alignment with the shared static prompt domain surface, reducing duplication and the risk of drift between help output and runtime behaviour.
- Further reduces coordination cost when updating static prompt profiles and axes by centralising logic in `lib/staticPromptConfig.py`.

Validation:

- Ran focused tests covering static prompt settings, domain helpers, and axis mapping:
  - `python -m unittest tests.test_talon_settings_model_prompt tests.test_static_prompt_config tests.test_axis_mapping`
  - All tests passed, indicating that the refactor preserved the existing contracts and domain helper behaviour.

Follow-ups (not completed in this loop):

- Consider adding lightweight snapshot-style tests around `model_help_gui` output in a future loop, if feasible, to make the help text itself part of the characterised behaviour.
- Migrate `modelPromptPatternGUI` in a similar fashion, consuming `get_static_prompt_profile` / `get_static_prompt_axes` in place of direct `STATIC_PROMPT_CONFIG` access.

---

## 2025-12-03 – Loop 6 – Migrate modelPromptPatternGUI to the static prompt domain API

Focus area:

- `lib/modelPromptPatternGUI.py::prompt_pattern_gui` – align the prompt pattern picker GUI with the shared static prompt domain helpers.

Changes in this loop:

- Updated `prompt_pattern_gui` so that, when a static prompt is selected:
  - It uses `get_static_prompt_profile(static_prompt)` to obtain and display the profile description.
  - It uses `get_static_prompt_axes(static_prompt)` to derive and display axis defaults for completeness/scope/method/style, instead of reading `STATIC_PROMPT_CONFIG` directly.
- Kept the overall UI layout and text structure the same (“Profile defaults:” block and grammar template), changing only how profile/axis data is sourced.

Impact on ADR-010 objectives:

- Brings another GUI entrypoint into alignment with the static prompt domain API, further reducing duplicated knowledge of `STATIC_PROMPT_CONFIG`.
- Ensures that both the help GUI and prompt pattern GUI reflect the same profile and axis semantics as `modelPrompt`, improving Concordance between configuration, behaviour, and UX.

Validation:

- Re-ran the focused tests around static prompt behaviour and axis mapping:
  - `python -m unittest tests.test_talon_settings_model_prompt tests.test_static_prompt_config tests.test_axis_mapping`
  - All tests passed, providing indirect assurance that the shared domain helpers still behave as expected after this migration.

Follow-ups (not completed in this loop):

- Consider adding targeted tests for prompt pattern execution paths (e.g., via a small harness around `_run_prompt_pattern`) to more directly characterise behaviour for commonly used patterns.

---

## 2025-12-03 – Loop 7 – Characterization tests for prompt pattern execution

Focus area:

- `lib/modelPromptPatternGUI.py::_run_prompt_pattern`
- `UserActions.prompt_pattern_run_preset`

Changes in this loop:

- Added `tests/test_prompt_pattern_gui.py` to characterise prompt pattern behaviour:
  - `test_run_prompt_pattern_executes_and_updates_last_recipe`:
    - Uses a real preset (`PROMPT_PRESETS[0]`) and a concrete static prompt (`todo`).
    - Asserts that `_run_prompt_pattern("todo", pattern)`:
      - Calls `actions.app.notify` once.
      - Calls `actions.user.gpt_apply_prompt` once.
      - Calls `actions.user.prompt_pattern_gui_close` once.
      - Updates `GPTState.last_recipe` to `"todo · gist · focus · plain"` and aligns `last_static_prompt`, axis fields, and `last_directional` with the preset.
  - `test_prompt_pattern_run_preset_dispatches_by_name`:
    - Sets `PromptPatternGUIState.static_prompt = "fix"`.
    - Monkey-patches `_run_prompt_pattern` to capture its arguments.
    - Calls `UserActions.prompt_pattern_run_preset` with a preset’s name and asserts that:
      - `_run_prompt_pattern` is invoked with the current static prompt (`"fix"`) and the matching preset.

Impact on ADR-010 objectives:

- Provides direct, behaviour-level tests for a key GUI execution path identified as a hotspot, reducing refactor risk in the prompt pattern picker.
- Ensures that future changes to `_run_prompt_pattern` or preset wiring are caught by tests, keeping Concordance between configuration, patterns, and runtime behaviour.

Validation:

- Ran the relevant test modules:
  - `python -m unittest tests.test_prompt_pattern_gui tests.test_talon_settings_model_prompt tests.test_static_prompt_config tests.test_axis_mapping`
  - All tests passed, confirming that prompt pattern behaviour and the shared domain helpers remain in sync.

Follow-ups (not completed in this loop):

- Extend prompt pattern tests to cover additional presets or error paths (for example, missing `static_prompt`) when that behaviour changes or becomes more complex.

---

## 2025-12-03 – Loop 8 – Status snapshot and ADR-010 current state

Focus area:

- Reconcile ADR-010’s Salient Tasks with the work completed so far and capture a concise status snapshot in the ADR itself.

Changes in this loop:

- Added a **“Current Status (this repo)”** section to `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md` that:
  - Summarises completed work on:
    - The static prompt domain helpers and tests (`get_static_prompt_profile` / `get_static_prompt_axes`, `tests/test_static_prompt_config.py`, `tests/test_axis_mapping.py`).
    - Settings and GUI consumers now using the domain API (`modelPrompt`, `model_help_gui`, `prompt_pattern_gui`).
    - Prompt pattern execution tests (`tests/test_prompt_pattern_gui.py`).
  - Calls out remaining areas:
    - Static prompt documentation and lists (`GPT/gpt.py::_build_static_prompt_docs`, `GPT/lists/staticPrompt.talon-list`) still to be aligned with the domain API and characterised by tests.
    - Future Concordance follow-up work (re-running the churn × complexity scan after more slices land).

Impact on ADR-010 objectives:

- Provides a clear, in-ADR snapshot of which Salient Tasks are effectively covered in this repo and which remain, making it easier for future loops to choose meaningful slices.
- Aligns the ADR text with the concrete work recorded in this work-log, reducing the risk of divergence between planned and actual state.

Validation:

- Re-ran the focused test set for the areas touched by recent loops:
  - `python -m unittest tests.test_prompt_pattern_gui tests.test_talon_settings_model_prompt tests.test_static_prompt_config tests.test_axis_mapping`
  - All tests passed, confirming a green baseline for the characterised static prompt and prompt pattern behaviour at this snapshot.

Follow-ups (not completed in this loop):

- Next status-oriented loop should revisit this snapshot after work on `_build_static_prompt_docs` and `staticPrompt.talon-list` alignment lands, updating the “Current Status” section accordingly.

---

## 2025-12-03 – Loop 9 – Characterization test for static prompt documentation

Focus area:

- `GPT/gpt.py::_build_static_prompt_docs` – ensure current behaviour is covered by at least one focused test.

Changes in this loop:

- Added `tests/test_static_prompt_docs.py` with a basic characterization test:
  - Asserts that `_build_static_prompt_docs()`:
    - Includes a profiled prompt like `"todo"` with its description and a `defaults:` segment, reflecting the profile in `STATIC_PROMPT_CONFIG`.
    - Includes the fallback summary line for unprofiled prompts (`"Other static prompts (tokens only; …)"`), ensuring the model still sees the full static prompt token vocabulary.
- The test deliberately avoids rewriting `staticPrompt.talon-list` or changing `_build_static_prompt_docs` behaviour; it only records the current contract in a reusable form.

Impact on ADR-010 objectives:

- Begins characterising the static prompt documentation path, which ADR-010 identifies as part of the “Static Prompt Documentation & Lists” domain, without yet refactoring it onto the domain API.
- Provides a baseline guardrail so that future changes to `_build_static_prompt_docs` must be made consciously and in sync with the ADR’s intent.

Validation:

- Ran the expanded focused test set:
  - `python -m unittest tests.test_static_prompt_docs tests.test_prompt_pattern_gui tests.test_talon_settings_model_prompt tests.test_static_prompt_config tests.test_axis_mapping`
  - All tests passed, keeping a green baseline across static prompt profiles, axes, mappings, prompt patterns, and documentation.

Follow-ups (not completed in this loop):

- Future loops can safely refactor `_build_static_prompt_docs` to use the static prompt domain API or additional metadata, updating the characterization tests as needed to reflect any intentional behaviour changes.

---

## 2025-12-03 – Loop 10 – Refactor static prompt docs to use the domain API

Focus area:

- `GPT/gpt.py::_build_static_prompt_docs` – align static prompt documentation with the shared static prompt domain helpers.

Changes in this loop:

- Updated imports in `GPT/gpt.py` to prefer `get_static_prompt_profile` and `get_static_prompt_axes` from `lib/staticPromptConfig`, with a small fallback shim that reads from `STATIC_PROMPT_CONFIG` when those helpers are unavailable (to stay robust under Talon’s module caching).
- Refactored `_build_static_prompt_docs` to:
  - Iterate over `STATIC_PROMPT_CONFIG.keys()` and call `get_static_prompt_profile(name)` to obtain the profile/description.
  - Use `get_static_prompt_axes(name)` when building the `defaults: …` segment for each profiled prompt, instead of reading axis fields directly from the raw config dict.
- Left the overall output format and semantics unchanged so that existing documentation and tests remain valid.

Impact on ADR-010 objectives:

- Moves the static prompt documentation path onto the same domain API used by settings and GUIs, reducing duplication and keeping all consumers in sync with `lib/staticPromptConfig.py`.
- Ensures that future changes to static prompt profiles and axes automatically flow through to docs, settings, and GUIs via a single, well-characterised surface.

Validation:

- Re-ran the expanded focused test set:
  - `python -m unittest tests.test_static_prompt_docs tests.test_prompt_pattern_gui tests.test_talon_settings_model_prompt tests.test_static_prompt_config tests.test_axis_mapping`
  - All tests passed, confirming that the refactor preserved the documented behaviour of `_build_static_prompt_docs` and the shared static prompt domain logic.

Follow-ups (not completed in this loop):

- Consider adding more detailed tests for specific prompts or axis combinations if/when `_build_static_prompt_docs` gains richer semantics (for example, grouping or filtering by domain).

---

## 2025-12-03 – Loop 11 – Concordance snapshot for ADR-010 hotspots

Focus area:

- Re-run the churn × complexity heatmap and capture a Concordance-oriented snapshot for the main ADR-010 hotspots.

Changes in this loop:

- Re-ran the statement-level churn × complexity scan:
  - `python scripts/tools/line-churn-heatmap.py` → `tmp/churn-scan/line-hotspots.json`
- Extracted ADR-010-related nodes from the `nodes` section (`since=90 days ago`, `scope=lib/, GPT/, copilot/, tests/`), focusing on:
  - `lib/staticPromptConfig.py :: StaticPromptProfile` (Class) – score ≈ 3964, churn 538, coordination 3429.
  - `lib/modelHelpGUI.py :: model_help_gui` (Function) – score ≈ 1588, churn 82, coordination 1258.
  - `lib/talonSettings.py :: _read_axis_value_to_key_map` (Function) – score ≈ 1544, churn 151, coordination 1371.
  - `GPT/gpt.py :: _build_static_prompt_docs` (Function) – score ≈ 1331, churn 111, coordination 1063.
  - `lib/modelPromptPatternGUI.py :: prompt_pattern_gui` / `Match` – scores ≈ 1267 / 1207, churn 65, coordination ≈ 1105 / 1075.
  - `GPT/lists/staticPrompt.talon-list` (File) – score ≈ 988, churn 393, coordination 1050.
  - `lib/talonSettings.py :: modelPrompt` / `_axis_recipe_token` – scores ≈ 944 / 900, churn 66 / 85, coordination 804 / 715.

Impact on ADR-010 objectives:

- Confirms that the refactors and tests landed so far are concentrated in the same structural hotspots originally identified by ADR-010 (static prompt config, settings, GUIs, docs, and lists).
- Provides a concrete Concordance snapshot that future loops can compare against once more behaviour-level and structural simplifications land (for example, further reductions in churn/coordination around these nodes).

Validation:

- No new code behaviour was introduced in this loop; all previously added tests remain green (see earlier loops for the exact commands), and the heatmap artefact lives at `tmp/churn-scan/line-hotspots.json` for inspection.

Follow-ups (not completed in this loop):

- Re-run the heatmap periodically after larger refactors in these areas to track whether scores for key ADR-010 hotspots begin to fall due to improved structure and tests, and record those snapshots in future work-log entries.

---

## 2025-12-03 – Loop 12 – Guardrail for static prompt config vs list drift

Focus area:

- Detect mismatches between `STATIC_PROMPT_CONFIG` and `GPT/lists/staticPrompt.talon-list` so new profiles don’t silently lose their Talon tokens.

Changes in this loop:

- Extended `tests/test_static_prompt_docs.py` with `test_all_profiled_prompts_have_static_prompt_token`:
  - Parses `GPT/lists/staticPrompt.talon-list` to collect all defined static prompt keys.
  - Compares them against `STATIC_PROMPT_CONFIG.keys()`.
  - Asserts that **every** profiled prompt key appears in the Talon list, while still allowing the list to contain additional unprofiled prompts.
- This serves as a small but concrete guardrail: adding a new static prompt profile without a corresponding `staticPrompt.talon-list` entry will now fail tests instead of silently drifting.

Impact on ADR-010 objectives:

- Directly addresses ADR-010’s call for checks that detect mismatches between configuration and `staticPrompt.talon-list`, reducing the risk of configuration/UX divergence in the static prompt domain.
- Keeps Concordance between the domain configuration, documentation, and grammar surface by ensuring profiled prompts always have live tokens in the Talon list.

Validation:

- Re-ran the relevant tests:
  - `python -m unittest tests.test_static_prompt_docs`
  - Test suite remains green, confirming that current profiles and the Talon list are in sync.

Follow-ups (not completed in this loop):

- Optionally extend this guardrail in future loops to surface any new “extra” Talon tokens that may deserve profiles, or to enforce documented naming/formatting conventions when the static prompt surface evolves.

---

## 2025-12-03 – Loop 13 – Operational shortcuts for re-running ADR-010 checks

Focus area:

- Make it easy to re-run the key ADR-010 checks (churn × complexity and tests) without re-reading the work-log in detail.

Changes in this loop:

- Updated `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md` with a **“How to Re‑run ADR‑010 Checks (this repo)”** section that lists:
  - The churn × complexity commands:
    - `python scripts/tools/churn-git-log-stat.py`
    - `python scripts/tools/line-churn-heatmap.py`
  - The main test commands covering ADR-010’s domains:
    - `python -m unittest tests.test_static_prompt_config tests.test_axis_mapping`
    - `python -m unittest tests.test_prompt_pattern_gui tests.test_talon_settings_model_prompt`
    - `python -m unittest tests.test_static_prompt_docs`
- This section also calls out which hotspots to inspect in `line-hotspots.json` when interpreting the heatmap output.

Impact on ADR-010 objectives:

- Lowers the operational friction for future loops (human or automated) to re-check Concordance and tests for the in-scope hotspots, making it more likely that ADR-010’s guardrails stay exercised over time.
- Provides a single, ADR-local reference for the commands associated with this ADR, aligning with the helper-driven workflow in this repo.

Validation:

- No new behaviour was introduced in this loop; existing tests and churn tooling remain as validated in earlier loops.

Follow-ups (not completed in this loop):

- Optionally update this section in future when the set of relevant tests or tools changes (for example, if additional Concordance-specific checks are added).

---

## 2025-12-03 – Loop 14 – Characterization tests for modelPatternGUI patterns and axes

Focus area:

- `lib/modelPatternGUI.py` – behaviour of `_axis_value`, `_parse_recipe`, and `UserActions.model_pattern_run_name`.

Changes in this loop:

- Added `tests/test_model_pattern_gui.py` with focused tests:
  - `test_axis_value_returns_description_when_present`:
    - Verifies that `_axis_value("gist", mapping)` returns the mapped description.
    - Confirms unknown tokens fall back to the raw token and an empty token returns `""`.
  - `test_parse_recipe_extracts_static_prompt_and_axes`:
    - Asserts that `_parse_recipe("debug · full · narrow · rigor · plain · rog")` correctly extracts:
      - `static_prompt="debug"`, `completeness="full"`, `scope="narrow"`, `method="rigor"`, `style="plain"`, `directional="rog"`.
  - `test_model_pattern_run_name_dispatches_and_updates_last_recipe`:
    - Uses the real `"Debug bug"` pattern from `PATTERNS`.
    - Calls `UserActions.model_pattern_run_name("Debug bug")`.
    - Asserts:
      - `actions.app.notify`, `actions.user.gpt_apply_prompt`, and `actions.user.model_pattern_gui_close` are each called once.
      - `GPTState.last_recipe == "debug · full · narrow · rigor · plain"`.
      - `last_static_prompt`, axis fields, and `last_directional` are set consistently with the parsed recipe.

Impact on ADR-010 objectives:

- Provides direct coverage for another key ADR‑010 hotspot (`modelPatternGUI`), reducing the risk of regressions in pattern execution and axis semantics as refactors continue.
- Ensures that Concordance between pattern recipes, axis mappings, and `GPTState` is now test-guarded rather than implicit.

Validation:

- Ran the new tests together with other ADR‑010 checks:
  - `python -m unittest tests.test_model_pattern_gui tests.test_prompt_pattern_gui tests.test_talon_settings_model_prompt tests.test_static_prompt_config tests.test_axis_mapping tests.test_static_prompt_docs`
  - All tests passed, confirming that pattern and prompt behaviour remain aligned with the domain helpers and configuration.

Follow-ups (not completed in this loop):

- Future loops may extend coverage to additional patterns or edge cases (for example, domain-specific subsets or missing tokens), but the core execution and axis wiring are now characterised.

---

## 2025-12-03 – Loop 15 – Characterization tests for _read_axis_default_from_list

Focus area:

- `lib/talonSettings.py::_read_axis_default_from_list` – default axis value loading from Talon lists.

Changes in this loop:

- Extended `tests/test_axis_mapping.py` with:
  - `test_read_axis_default_from_list_returns_configured_default`:
    - Calls `_read_axis_default_from_list("completenessModifier.talon-list", "full", "fallback-value")`.
    - Asserts that it returns `"full"`, confirming it reads from the real completeness list rather than blindly using the fallback.
  - `test_read_axis_default_from_list_falls_back_when_missing`:
    - Calls `_read_axis_default_from_list("nonexistent-list.talon-list", "full", "fallback-value")`.
    - Asserts that it returns `"fallback-value"`, exercising the missing-file path.

Impact on ADR-010 objectives:

- Completes basic characterization for another axis-related helper (`_read_axis_default_from_list`) that ADR-010 highlighted as part of the static prompt and axis configuration hotspot in `lib/talonSettings.py`.
- Reduces refactor risk for future changes to how default axis values are resolved when list files are present or missing.

Validation:

- Ran the updated axis mapping tests:
  - `python -m unittest tests.test_axis_mapping`
  - All tests passed, confirming the new characterizations align with current behaviour.

Follow-ups (not completed in this loop):

- Future loops can safely refactor the interplay between `_read_axis_default_from_list`, axis lists, and the static prompt domain API, adjusting these tests only when behaviour changes intentionally.

---

## 2025-12-03 – Loop 16 – Keep ADR-010 status in sync with axis tests

Focus area:

- Align ADR-010’s “Current Status” summary of axis helpers with the tests that now exist.

Changes in this loop:

- Updated the **Static Prompt Profile & Axes** bullet under “Current Status (this repo)” in `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md` to:
  - Explicitly mention that `tests/test_axis_mapping.py` now covers:
    - Axis defaults loaded from Talon lists (`_read_axis_default_from_list`).
    - Value→key mapping and recipe tokenisation (`_read_axis_value_to_key_map`, `_axis_recipe_token`), including missing-file and long-description behaviour.

Impact on ADR-010 objectives:

- Keeps the ADR’s high-level status description in lockstep with the concrete test coverage in this repo, so future readers can see at a glance which axis helpers are already characterised without re-scanning the tests.

Validation:

- No behaviour changes; existing axis tests remain green (see Loop 15).

Follow-ups (not completed in this loop):

- None for this slice; it is purely a documentation/status reconciliation step.

---

## 2025-12-03 – Loop 17 – Invariants between model patterns and static prompts

Focus area:

- Ensure that model patterns in `lib/modelPatternGUI.py` only reference static prompts that are wired into both `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.

Changes in this loop:

- Extended `tests/test_model_pattern_gui.py` with `test_all_pattern_static_prompts_exist_in_config_and_list`:
  - Parses `GPT/lists/staticPrompt.talon-list` to collect all static prompt tokens.
  - Reads `STATIC_PROMPT_CONFIG.keys()` from `lib/staticPromptConfig.py`.
  - For each pattern in `PATTERNS`, uses `_parse_recipe(pattern.recipe)` to obtain the pattern’s static prompt token and asserts:
    - The token is present in `STATIC_PROMPT_CONFIG`.
    - The token has a corresponding entry in `staticPrompt.talon-list`.

Impact on ADR-010 objectives:

- Adds a concrete guardrail for the “Pattern & Prompt GUI Orchestrators” domain: adding or changing a pattern recipe now fails tests if it points at a static prompt that is not properly configured and exposed via the Talon list.
- Reduces the risk of Concordance drift between pattern behaviour, static prompt configuration, and the grammar surface.

Validation:

- Ran the updated tests:
  - `python -m unittest tests.test_model_pattern_gui`
  - All tests passed, confirming that current patterns are consistent with static prompt configuration and the Talon list.

Follow-ups (not completed in this loop):

- None for this slice; future loops can rely on this invariant when evolving patterns or adding new static prompts and profiles.

---

## 2025-12-03 – Loop 18 – Tie Salient Tasks to concrete tests and refactors

Focus area:

- Make ADR-010’s Salient Tasks explicitly point at the concrete tests and refactors that now exist in this repo.

Changes in this loop:

- Updated the **Salient Tasks** section of `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md` so that:
  - The **Static Prompt Profile & Axes** bullets now reference:
    - `get_static_prompt_profile` / `get_static_prompt_axes` in `lib/staticPromptConfig.py`.
    - `tests/test_static_prompt_config.py` and `tests/test_axis_mapping.py` as current coverage for profiles, axis maps, and defaults.
    - The fact that `modelPrompt` already consumes the domain helpers in this repo.
  - The **Pattern & Prompt GUI Orchestrators** bullets now reference:
    - `tests/test_model_pattern_gui.py` and `tests/test_prompt_pattern_gui.py` as coverage for `_axis_value`, `_parse_recipe`, `modelPatternGUI`, and `modelPromptPatternGUI`.
    - The migration of `model_help_gui`, `prompt_pattern_gui`, and `modelPrompt` to the static prompt domain helpers.
  - The **Static Prompt Documentation & Lists** bullets now reference:
    - `tests/test_static_prompt_docs.py` and related guardrails in `tests/test_model_pattern_gui.py` as coverage for `_build_static_prompt_docs` and alignment between `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list`.

Impact on ADR-010 objectives:

- Keeps ADR-010’s task list honest and immediately actionable for this repo by showing which tasks are already partially or fully satisfied by existing work, and where new slices would need to land.
- Makes it easier for future ADR loops to choose meaningful remaining slices without re-triangulating intent from tests and code alone.

Validation:

- No behavioural changes; this loop is documentation-only and all previously recorded tests remain green.

Follow-ups (not completed in this loop):

- None specific; future loops can now treat the Salient Tasks as a higher-fidelity map of what is done vs. remaining in this repo.

---

## 2025-12-03 – Loop 19 – Add full-suite test command to ADR-010 ops section

Focus area:

- Make it obvious how to run the full test suite alongside the ADR‑010 focused checks.

Changes in this loop:

- Extended the **“How to Re‑run ADR‑010 Checks (this repo)”** section of `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md` with:
  - A **Full test sweep (this repo)** bullet pointing to:
    - `make test`
  - This complements the more targeted ADR‑010 unittest commands with the existing Makefile entry for running all tests.

Impact on ADR-010 objectives:

- Provides a single, ADR-local place where both focused ADR‑010 checks and the full suite command are documented, making it easier to keep Concordance checks and the broader test suite in sync.

Validation:

- No behavioural changes; `make test` already exists in the Makefile and remains the canonical way to run all tests.

Follow-ups (not completed in this loop):

- None for this slice; it is purely an operational/doc improvement.

---

## 2025-12-03 – Loop 20 – Full-suite test run after ADR-010 refactors

Focus area:

- Confirm that the full test suite passes under this repo’s default `make test` command after the ADR-010-driven refactors and guardrails.

Changes in this loop:

- Ran the full test suite:
  - `make test`
  - Which executes: `python3 -m unittest discover -s tests`
- Result:
  - `Ran 76 tests in 0.045s`
  - `OK`

Impact on ADR-010 objectives:

- Confirms that the ADR-010 slices landed so far (domain helpers, GUI refactors, axis/recipe mapping tests, static prompt docs/list guardrails, and model pattern invariants) integrate cleanly with the rest of the project under the default Python 3.9 runtime used by `make test`.
- Provides a clear “green suite” snapshot for this point in the ADR-010 work-log, which future loops can reference when making larger structural changes.

Validation:

- The full test suite is green at this snapshot; no additional action required in this loop.

Follow-ups (not completed in this loop):

- None specific; future ADR-010 loops can treat this as a stable baseline and re-run `make test` when landing broader refactors.

---

## 2025-12-03 – Loop 21 – Talon runtime compatibility for pattern GUIs

Focus area:

- Ensure ADR-010’s pattern-related refactors (`modelPatternGUI`, `modelPromptPatternGUI`) remain compatible with the Talon runtime’s action type requirements.

Changes in this loop:

- Adjusted type annotations in:
  - `lib/modelPatternGUI.py`:
    - Replaced `PatternGUIState.domain: PatternDomain | None` with `Optional[PatternDomain]`.
  - `lib/modelPromptPatternGUI.py`:
    - Replaced `PromptPatternGUIState.static_prompt: str | None` with `Optional[str]`.
- Removed reliance on `from __future__ import annotations` in these modules so that Talon sees native types (`Optional[...]`) rather than stringified annotations that caused `ActionProtoError` for:
  - `user.model_pattern_run_name`
  - `user.prompt_pattern_gui_open_for_static_prompt`

Impact on ADR-010 objectives:

- Keeps the pattern GUI actions compatible with Talon’s action prototype rules while preserving the ADR-010-driven structure and domain usage.
- Ensures Concordance work on pattern GUIs does not introduce regressions in the live Talon environment.

Validation:

- Re-ran the focused pattern GUI tests under Python 3.9:
  - `python3 -m unittest tests.test_model_pattern_gui tests.test_prompt_pattern_gui`
  - All tests passed, confirming behaviour remains unchanged and type adjustments are safe.

Follow-ups (not completed in this loop):

- None specific; this slice is about runtime compatibility rather than new behaviour or guardrails.

---

## 2025-12-03 – Loop 22 – Python 3.9 compatibility for static prompt config and patterns

Focus area:

- Ensure ADR-010’s static prompt domain and pattern modules work cleanly under Python 3.9 (the runtime used by `make test`), not just 3.11.

Changes in this loop:

- Updated `lib/staticPromptConfig.py` to avoid `typing.NotRequired` (which is unavailable in Python 3.9) by:
  - Replacing the previous `TypedDict` definition with:
    - `class StaticPromptProfile(TypedDict, total=False): ...`
  - Keeping optional fields (`completeness`, `scope`, `method`, `style`) via `total=False` instead of `NotRequired`.
- Confirmed that pattern and static prompt modules compile and run under Python 3.9 by:
  - Re-running the focused ADR-010 test set with `python3`:
    - `python3 -m unittest tests.test_static_prompt_config tests.test_axis_mapping tests.test_static_prompt_docs tests.test_model_pattern_gui tests.test_prompt_pattern_gui`

Impact on ADR-010 objectives:

- Ensures that ADR-010’s refactors around static prompt config and pattern GUIs are compatible with the project’s default Python runtime, so Concordance guardrails and refactors remain enforceable in CI and local workflows.

Validation:

- The focused ADR-010 test set passes under both Python 3.11 and Python 3.9; see Loop 20 for the full-suite `make test` run.

Follow-ups (not completed in this loop):

- None; this slice is a compatibility-only adjustment for existing behaviour.

---

## 2025-12-03 – Loop 23 – High-level ADR-010 status snapshot for this repo

Focus area:

- Summarise ADR-010 coverage in this repo across domains, tests, and Concordance signals.

Changes in this loop:

- Added this high-level snapshot entry to the work-log (no code changes):
  - **Static Prompt Profile & Axes**
    - Domain helpers (`get_static_prompt_profile`, `get_static_prompt_axes`) implemented and tested.
    - Axis defaults, value→key mapping, and recipe tokenisation characterised by `tests/test_axis_mapping.py`.
    - `modelPrompt` consumes the domain helpers.
  - **Pattern & Prompt GUI Orchestrators**
    - `modelPatternGUI`, `modelPromptPatternGUI`, and `modelHelpGUI` consume the static prompt domain helpers.
    - Behavioural tests exist for `_axis_value`, `_parse_recipe`, `_run_pattern`, `_run_prompt_pattern`, and the associated Talon actions in `tests/test_model_pattern_gui.py` and `tests/test_prompt_pattern_gui.py`.
    - Invariants ensure pattern recipes only reference configured/listed static prompts.
  - **Static Prompt Documentation & Lists**
    - `_build_static_prompt_docs` consumes the domain helpers and is covered by `tests/test_static_prompt_docs.py`.
    - Guardrails ensure:
      - Every profiled prompt has a corresponding token in `staticPrompt.talon-list`.
      - Patterns and docs remain aligned with `STATIC_PROMPT_CONFIG`.
  - **Concordance / Churn**
    - Churn × complexity scans are wired up via `scripts/tools/churn-git-log-stat.py` and `scripts/tools/line-churn-heatmap.py`, with ADR-010 hotspots recorded in this work-log.
  - **Operational**
    - Focused ADR-010 tests and `make test` are documented in the ADR, and the full suite is green as of Loop 20.

Impact on ADR-010 objectives:

- Provides an at-a-glance summary of what ADR-010 currently covers in this repo and where the main guardrails live, making it easier for future loops (or readers) to see the current state without re-reading every prior entry.

Validation:

- No behavioural changes; this loop is purely a status summary.

Follow-ups (not completed in this loop):

- Future loops can treat this snapshot as a baseline when deciding whether ADR-010 work in this repo is “sufficient for now” or if additional Concordance-driven refactors are warranted.

---

## 2025-12-03 – Loop 24 – Link ADR-010 to helper prompts

Focus area:

- Make it easier to discover the generic ADR loop helper and the churn × complexity Concordance helper from ADR-010 itself.

Changes in this loop:

- Updated the top of `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md` to include:
  - A short “Related helpers in this repo” list pointing to:
    - `docs/adr/adr-loop-execute-helper.md`
    - `docs/adr/churn-concordance-adr-helper.md`

Impact on ADR-010 objectives:

- Provides an explicit bridge from ADR-010 to the reusable helper prompts already in this repo, making it easier to run future loops or new Concordance-driven ADRs without hunting for the helper docs.

Validation:

- Documentation-only change; no behaviour or tests affected.

Follow-ups (not completed in this loop):

- None; this is a small navigational improvement only.

---

## 2025-12-03 – Loop 25 – Characterization for axis docs helper

Focus area:

- Add basic characterization for `_build_axis_docs` so changes to axis doc structure are explicit and test-guarded.

Changes in this loop:

- Extended `tests/test_static_prompt_docs.py` with `test_axis_docs_include_all_axis_sections`:
  - Imports `_build_axis_docs` from `GPT/gpt.py`.
  - Asserts that the generated docs include headings for:
    - `Completeness modifiers:`, `Scope modifiers:`, `Method modifiers:`, `Style modifiers:`, `Directional modifiers:`.
  - Verifies that at least one representative key from each axis list appears (e.g. `full:`, `narrow:`, `steps:`, `plain:`) and that at least one directional key (`fog:`, `rog:`, or `ong:`) is present.

Impact on ADR-010 objectives:

- Extends ADR-010’s documentation & lists domain to include the axis docs helper, reducing the risk of accidental regressions in how axis modifiers are described to the model and users.

Validation:

- Ran:
  - `python3 -m unittest tests.test_static_prompt_docs`
  - All three tests passed, confirming the new characterization matches current behaviour.

Follow-ups (not completed in this loop):

- None for now; future loops can adjust or extend this test if `_build_axis_docs` gains richer semantics.

---

## 2025-12-03 – Loop 26 – Salient Tasks cross-check with implemented slices

Focus area:

- Make explicit in ADR-010’s Salient Tasks which items are already covered in this repo, to reduce ambiguity for future loops.

Changes in this loop:

- Refined the **Salient Tasks** section of `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md` so that each major bullet group now:
  - Points to the concrete helpers and tests that already satisfy those tasks in this repo (for static prompt profiles/axes, pattern & prompt GUIs, and docs/lists).
  - Clarifies that the remaining work is primarily about evolving scope or applying the same patterns elsewhere, rather than implementing these foundations from scratch.

Impact on ADR-010 objectives:

- Reduces the risk that future work will re‑do completed tasks or misinterpret ADR-010 as entirely unimplemented in this repo.
- Helps the Salient Tasks function as a living checklist linked to real artefacts (code + tests) rather than static, abstract goals.

Validation:

- Documentation-only change; no behaviour or tests affected.

Follow-ups (not completed in this loop):

- None specific; future loops can use the updated Salient Tasks as a clearer map of remaining opportunities.

---

## 2025-12-03 – Loop 27 – Small refactor to reuse domain axes in GUIs

Focus area:

- Reduce duplicate calls to the static prompt domain helpers in GUI renderers while keeping behaviour unchanged.

Changes in this loop:

- Updated `lib/modelHelpGUI.py::model_help_gui`:
  - Now calls `get_static_prompt_axes(sp)` once per static prompt and reuses the resulting `profile_axes` when assembling the “Profile defaults:” lines.
- Updated `lib/modelPromptPatternGUI.py::prompt_pattern_gui`:
  - Similarly, now calls `get_static_prompt_axes(static_prompt)` once per prompt and reuses the resulting `profile_axes` when assembling axis defaults.

Impact on ADR-010 objectives:

- Slightly simplifies the prompt/pattern GUIs and aligns better with ADR-010’s goal of centralising static prompt semantics in the domain helpers, without changing visible behaviour.

Validation:

- Ran the existing pattern GUI tests under Python 3.9:
  - `python3 -m unittest tests.test_model_pattern_gui tests.test_prompt_pattern_gui`
  - All tests passed, confirming no behavioural change.

Follow-ups (not completed in this loop):

- None; this is a small structural tidy-up in support of the broader domain consolidation.

---

## 2025-12-03 – Loop 28 – Characterization tests for modelHelpGUI actions

Focus area:

- Add minimal behavioural tests around the `modelHelpGUI` actions so state changes are explicit and guarded.

Changes in this loop:

- Added `tests/test_model_help_gui.py` with three tests:
  - `test_open_and_close_toggle_gui_and_reset_state`:
    - Verifies that `UserActions.model_help_gui_open()` toggles the GUI’s `showing` flag and resets `HelpGUIState.section` to `"all"` and `HelpGUIState.static_prompt` to `None` on both open and close.
  - `test_open_for_static_prompt_sets_focus_prompt`:
    - Asserts that `UserActions.model_help_gui_open_for_static_prompt("todo")`:
      - Shows the GUI.
      - Sets `HelpGUIState.section` to `"all"`.
      - Sets `HelpGUIState.static_prompt` to `"todo"`.
  - `test_open_for_last_recipe_resets_static_prompt`:
    - Starts with `HelpGUIState.static_prompt = "fix"`.
    - Asserts that `UserActions.model_help_gui_open_for_last_recipe()`:
      - Shows the GUI.
      - Resets `HelpGUIState.section` to `"all"`.
      - Clears `HelpGUIState.static_prompt`.

Impact on ADR-010 objectives:

- Extends ADR-010’s coverage in the “Pattern & Prompt GUI Orchestrators” domain to include basic state behaviour for the help GUI, making future changes to these actions safer.

Validation:

- Ran:
  - `python3 -m unittest tests.test_model_help_gui`
  - All three tests passed, confirming that the new characterization matches current behaviour.

Follow-ups (not completed in this loop):

- None specific; future loops can build on this by adding more detailed rendering tests if/when the help GUI becomes more complex.

---

## 2025-12-03 – Loop 27 – Make churn scan runnable via Makefile

Focus area:

- Provide a simple, repeatable Makefile target for the ADR-010 churn × complexity scan.

Changes in this loop:

- Added a `churn-scan` target to the project `Makefile`:
  - `make churn-scan`
  - Runs:
    - `python3 scripts/tools/churn-git-log-stat.py`
    - `python3 scripts/tools/line-churn-heatmap.py`
- Updated the **How to Re‑run ADR‑010 Checks (this repo)** section of the ADR to mention `make churn-scan` as a shorthand for the two underlying commands.

Impact on ADR-010 objectives:

- Lowers friction for re-running the churn × complexity scan in a consistent way, making it easier to keep Concordance snapshots up to date as further refactors land.

Validation:

- The underlying scripts were already in use and validated in earlier loops; this slice only adds a convenience wrapper and ADR documentation.

Follow-ups (not completed in this loop):

- None; this target is sufficient for the current ADR-010 workflow in this repo.

---

## 2025-12-03 – Loop 29 – Focused ADR-010 test target

Focus area:

- Provide a single command to run the ADR-010-focused test set.

Changes in this loop:

- Added an `adr010-check` target to the `Makefile`:
  - Runs:
    - `python3 -m unittest \`
      `tests.test_static_prompt_config \`
      `tests.test_axis_mapping \`
      `tests.test_model_pattern_gui \`
      `tests.test_prompt_pattern_gui \`
      `tests.test_static_prompt_docs \`
      `tests.test_model_help_gui`
- Updated the **How to Re‑run ADR‑010 Checks (this repo)** section of the ADR to include:
  - A new **Focused ADR‑010 checks** bullet for `make adr010-check`.

Impact on ADR-010 objectives:

- Makes it trivial to re-run the core ADR-010 guardrails without running the entire test suite, encouraging more frequent checks during small slices.

Validation:

- Ran:
  - `make adr010-check`
  - `Ran 25 tests in 0.007s` → `OK`

Follow-ups (not completed in this loop):

- None; the target can be extended in future if new ADR-010-specific tests are added.

---

## 2025-12-03 – Loop 30 – ADR-010 near-term closure snapshot

Focus area:

- Capture that, for this repo, ADR-010’s core guardrails and refactors are now in place and backed by tests.

Changes in this loop:

- Reviewed ADR-010’s Salient Tasks, Current Status, and recent loops and noted that, in this repo:
  - Static prompt profiles and axes have a shared domain API, are consumed by settings, GUIs, and docs, and are covered by targeted tests.
  - Pattern and prompt GUIs consume the same domain API, have behavioural tests, and invariants that keep them aligned with static prompt configuration and Talon lists.
  - Static prompt docs and axis docs are characterised by tests, with guardrails for config/list alignment.
  - Churn × complexity tooling exists with a Makefile target (`make churn-scan`), and a focused ADR-010 test target (`make adr010-check`) plus full-suite `make test` are green.

Impact on ADR-010 objectives:

- Records that, for this repo, ADR-010 is in a “good enough for now” state: further ADR-010 work here is likely to be opportunistic or driven by new hotspots, rather than by missing foundational guardrails.

Validation:

- No new behaviour was added in this loop; all validations are as per earlier loops (especially Loops 20 and 29).

Follow-ups (not completed in this loop):

- Future ADR-010 loops in this repo can:
  - React to new churn/Concordance hotspots if they emerge.
  - Or focus on adjacent ADRs that build on these foundations.

---

## 2025-12-03 – Loop 31 – Guardrail: pattern static prompts must be documented

Focus area:

- Ensure that static prompts used by model patterns are also mentioned in the static prompt documentation block.

Changes in this loop:

- Extended `tests/test_static_prompt_docs.py` with `test_pattern_static_prompts_are_documented`:
  - Imports `PATTERNS` and `_parse_recipe` from `lib/modelPatternGUI`.
  - For each pattern, extracts the static prompt token from `pattern.recipe`.
  - Asserts that each static prompt appears somewhere in the `_build_static_prompt_docs()` output.

Impact on ADR-010 objectives:

- Adds a small but concrete guardrail linking the pattern domain to the documentation domain: adding or changing a pattern that uses a new static prompt now requires that prompt to be surfaced in the static prompt docs as well.
- Helps maintain Concordance between configuration (`STATIC_PROMPT_CONFIG`), patterns (`PATTERNS`), and documentation (`_build_static_prompt_docs`).

Validation:

- Ran:
  - `python3 -m unittest tests.test_static_prompt_docs`
  - All four tests passed, confirming that current pattern static prompts are documented.

Follow-ups (not completed in this loop):

- None specific; future loops can tighten or extend this guardrail if static prompt documentation gains more structure.

---

## 2025-12-03 – Loop 32 – ADR-010 hotspot status helper

Focus area:

- Make it easy to view the current ADR-010 hotspots from the latest churn × complexity scan.

Changes in this loop:

- Added `scripts/tools/adr010-status.py`:
  - Reads `tmp/churn-scan/line-hotspots.json` produced by the churn-scan tools.
  - Filters for ADR‑010-relevant files (static prompt config, settings, pattern/help GUIs, `GPT/gpt.py`, and `GPT/lists/staticPrompt.talon-list`).
  - Prints a sorted list of nodes showing `file`, `symbolName`, `nodeKind`, `nodeStartLine`, `score`, `churn`, `coord`, and `avgCx`.
- Added a Makefile target:
  - `make adr010-status` – runs the helper after a churn scan.
- Documented `make adr010-status` under “How to Re‑run ADR‑010 Checks (this repo)” in the ADR.

Impact on ADR-010 objectives:

- Provides a quick, repeatable way to see where ADR‑010’s hotspots currently sit without re-parsing the JSON by hand, making it easier to choose future slices based on fresh churn × complexity data.

Validation:

- Ran:
  - `make churn-scan && make adr010-status`
  - Confirmed that the script lists ADR‑010 hotspots with the expected fields.

Follow-ups (not completed in this loop):

- Optionally extend the helper in future to compare current scores against prior snapshots or to highlight changes over time.

---

## 2025-12-03 – Loop 33 – Example ADR‑010 workflow in ADR text

Focus area:

- Provide a concrete, copy‑pasteable mini workflow for running ADR‑010 checks in this repo.

Changes in this loop:

- Added an **“Example ADR‑010 Workflow (this repo)”** section to the ADR that suggests:
  - `make churn-scan`
  - `make adr010-status`
  - `make adr010-check`
- This ties together the churn scan, hotspot status helper, and focused tests that earlier loops introduced.

Impact on ADR-010 objectives:

- Makes it easier for future readers to run a full ADR‑010 slice without interpreting the individual commands themselves.

Validation:

- Documentation-only change; the underlying Make targets and scripts were already validated in earlier loops.

Follow-ups (not completed in this loop):

- None specific; future loops can update this workflow if the set of relevant commands changes.

---

## 2025-12-03 – Loop 34 – Hotspot ↔ tests map in ADR-010

Focus area:

- Make the mapping between ADR-010 hotspots and their tests explicit in the ADR itself.

Changes in this loop:

- Added a **“Hotspot ↔ Tests Map (this repo)”** section to the ADR that:
  - Lists each core ADR-010 hotspot (static prompt config, settings helpers, pattern GUIs, help GUI, docs, and list alignment).
  - Points directly to the tests that cover each area (e.g. `tests/test_static_prompt_config.py`, `tests/test_axis_mapping.py`, `tests/test_model_pattern_gui.py`, `tests/test_prompt_pattern_gui.py`, `tests/test_model_help_gui.py`, `tests/test_static_prompt_docs.py`, `tests/test_talon_settings_model_prompt.py`).

Impact on ADR-010 objectives:

- Makes it much easier for future maintainers to see, at a glance, which tests protect each hotspot and where to add new tests when refactoring.
- Strengthens the connection between Concordance hotspots and their guardrails, which is central to ADR-010’s intent.

Validation:

- Documentation-only change; no behaviour or tests affected.

Follow-ups (not completed in this loop):

- None specific; future loops can extend this map if new hotspots or tests are added.
