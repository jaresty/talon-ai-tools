# ADR-010 – Concordance Churn × Complexity Code Quality Improvements

Status: Accepted  
Date: 2025-12-03  
Owners: Talon AI tools maintainers

---

_Work-log_: see `docs/adr/010-concordance-churn-complexity-code-quality-improvements.work-log.md` for per-loop slices and current execution history in this repo.

Related helpers in this repo:

- `docs/adr/adr-loop-execute-helper.md` – generic helper for running ADR execution loops.
- `docs/adr/churn-concordance-adr-helper.md` – helper for churn × complexity + Concordance ADRs.

## Context

Over the last 90 days, a statement‑level churn × complexity heatmap was run over the core Talon AI tools and tests (`lib/`, `GPT/`, `copilot/`, `tests/`) using:

- `scripts/tools/churn-git-log-stat.py` → `tmp/churn-scan/git-log-stat.txt`
- `scripts/tools/line-churn-heatmap.py` → `tmp/churn-scan/line-hotspots.json`

The top node‑level hotspots by `score = churn × complexity × coordination_weight` include:

- `lib/staticPromptConfig.py :: StaticPromptProfile` – high churn and coordination in the central static‑prompt configuration domain.
- `lib/modelPatternGUI.py :: _axis_value` and `Match` – complex GUI pattern‑picking logic with frequent, coordinated edits.
- `lib/modelPromptPatternGUI.py :: Match` and `prompt_pattern_gui` – prompt‑pattern GUI orchestration with significant coordinated churn.
- `lib/talonSettings.py :: _read_axis_value_to_key_map` – settings axis parsing and mapping logic that changes alongside prompt configuration and GUI code.
- `lib/modelHelpGUI.py :: model_help_gui` – help/guide UI that tracks prompt configuration and model options.
- `GPT/gpt.py :: _build_static_prompt_docs` – static‑prompt documentation generation that depends on configuration and list definitions.
- `GPT/lists/staticPrompt.talon-list` and related GPT list files – frequently‑edited static prompt definitions with broad downstream impact.
- `GPT/readme.md` – documentation that changes in tandem with configuration, lists, and GUI behaviour.

These hotspots form several related clusters:

1. **Static Prompt Configuration & Persistence**
   - `lib/staticPromptConfig.py :: StaticPromptProfile`
   - `lib/talonSettings.py :: _read_axis_value_to_key_map`
   - `GPT/lists/staticPrompt.talon-list`
   - Relevant tests under `tests/` touching prompt configuration and settings.

2. **Pattern & Prompt GUI Orchestrators**
   - `lib/modelPatternGUI.py :: _axis_value`, `Match`
   - `lib/modelPromptPatternGUI.py :: Match`, `prompt_pattern_gui`
   - `lib/modelHelpGUI.py :: model_help_gui`

3. **Static Prompt Documentation & UX**
   - `GPT/gpt.py :: _build_static_prompt_docs`
   - `GPT/readme.md` sections describing static prompts and usage.
   - `GPT/lists/staticPrompt.talon-list` as the underlying source of truth.

Each cluster shows high churn in logic that couples configuration, GUI orchestration, and user‑facing descriptions, often changing together across multiple files and modules.

Applying the Concordance framing:

- **Visibility** – Contracts between static prompt configuration (`staticPromptConfig` / `talonSettings`), GUI orchestrators (`modelPatternGUI`, `modelPromptPatternGUI`, `modelHelpGUI`), and user‑visible docs (`GPT/gpt.py`, `GPT/readme.md`, `GPT/lists/*`) are partly implicit. The same concepts (axes, profiles, patterns) appear in many places without a single, explicit contract surface.
- **Scope** – Changes to axes or static prompt definitions can require coordinated edits across core Python modules, Talon lists, tests, and docs. The blast radius for concept‑level changes is wide.
- **Volatility** – These areas evolve frequently as new models, prompts, and workflows are added, leading to sustained churn in the same hotspots.

Together, these patterns point to a few “hidden domains” or “tunes”:

- A **Static Prompt Profile & Axes domain** that owns how profiles, axes, and mappings are defined and persisted.
- A **Prompt & Pattern GUI Orchestration domain** that owns GUI behaviour for selecting, viewing, and applying profiles and patterns.
- A **Static Prompt Documentation & Lists domain** that turns configuration and behaviour into user‑facing lists and help text.

This ADR focuses on improving code quality by making these domains more explicit, tightening their contracts, and reducing the coordination cost between them, so that Concordance scores decrease over time because the system is genuinely easier and safer to change.

---

## Problem

Current churn × complexity patterns show that:

- Conceptually related behaviours (e.g. “static prompt profile axis mapping”) are implemented and updated across multiple modules and list files without a single, clear boundary.
- GUI orchestrators for prompt/pattern selection have grown complex and entangled with configuration details, leading to:
  - High branch complexity in functions like `_axis_value`, `Match`, `prompt_pattern_gui`, and `model_help_gui`.
  - Frequent, coordinated edits when configuration or UX expectations change.
- User‑facing documentation and Talon lists (`GPT/gpt.py`, `GPT/readme.md`, `GPT/lists/staticPrompt.talon-list`) must be kept in sync with the underlying configuration and GUI logic, but the dependency paths are not always explicit or test‑guarded.

This creates several risks:

- **High coordination cost** – Small conceptual changes (e.g. adding a new axis or profile) require many edits across files, increasing the chance of mistakes.
- **Fragile behaviour** – Implicit contracts between configuration, GUI components, and docs are easy to break without detection, especially when tests focus on happy paths or incidental text rather than branch‑level behaviour.
- **Refactor risk** – The same hotspots appear repeatedly in churn scans, indicating that future changes will continue to touch these complex, poorly bounded areas unless we clarify their domains and contracts.

We want to:

- Reduce sustained Concordance scores for these hotspots by improving structure and tests, not by weakening checks or ignoring signals.
- Make common changes (adding/modifying static prompts, axes, profiles, and related GUI behaviour) safer, more local, and easier to reason about.

---

## Decision

For the in‑scope hotspots around static prompt configuration, GUI orchestration, and documentation, we adopt the following structural and code‑quality decisions:

1. **Clarify the Static Prompt Profile & Axes domain**
   - Treat `lib/staticPromptConfig.py` and the related portions of `lib/talonSettings.py` as the primary home for the “Static Prompt Profile & Axes” domain.
   - Define and expose a small, explicit API for:
     - Listing available profiles and axes.
     - Reading and writing axis→key mappings.
     - Validating configuration (e.g. missing axes, invalid keys).
   - Avoid duplicating concept‑level knowledge (e.g. axis names, valid values) in GUI and documentation layers; instead, consume this API.

2. **Separate GUI orchestration from configuration details**
   - Refactor GUI modules (`lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`, `lib/modelHelpGUI.py`) towards:
     - Thin orchestrators that primarily:
       - Call the static prompt profile/axes API.
       - Translate domain data into GUI widgets and events.
     - Reduced direct parsing or re‑interpretation of configuration structures.
   - Where possible, move non‑GUI logic (e.g. axis mapping interpretation, profile selection rules) into the configuration/domain layer and test it there.

3. **Make documentation and Talon lists consume explicit contracts**
   - Treat `GPT/gpt.py::_build_static_prompt_docs` and `GPT/lists/staticPrompt.talon-list` as consumers of the static prompt profile/axes domain, not independent sources of truth.
   - Where feasible, drive static‑prompt documentation and lists from the same API or data structures used by the GUI and settings layers.

4. **Concordance‑aligned outcome**
   - For these hotspots, the intended long‑term effect of this ADR is to **reduce sustained Concordance scores** by:
     - Increasing visibility of contracts between configuration, GUI, and documentation.
     - Narrowing the scope of changes (more localised edits for concept‑level changes).
     - Reducing volatility in core orchestration paths by separating concerns and strengthening tests.
   - We explicitly do **not** change how Concordance or churn analysis is measured; improvements must come from better structure, guardrails, and tests, not from relaxing checks.

---

## Tests‑First Principle

We reaffirm a tests‑first approach for refactors and code‑quality improvements in these hotspots:

> Before changing behaviour, we will first analyze existing tests to ensure that the behaviour we intend to change is well covered. Where coverage is insufficient, we will add focused characterization tests capturing current behaviour (including relevant branches and error paths), and then proceed with the refactor guarded by those tests. Where coverage is already strong and branch‑focused for the paths we are changing, we will rely on and, if needed, extend those existing tests rather than adding redundant characterization tests.

In this ADR’s scope, this means:

- For functions like `_read_axis_value_to_key_map`, `_axis_value`, `Match`, `prompt_pattern_gui`, and `model_help_gui`, we will:
  - Identify existing tests in `tests/` that cover:
    - True/false paths, error handling, and early‑return branches.
    - Typical and edge‑case configurations (e.g. missing axes, unknown keys).
  - Add or extend tests where current coverage does not exercise the branches we plan to touch.
- For documentation and list consumers (`_build_static_prompt_docs`, `GPT/lists/staticPrompt.talon-list`):
  - Prefer tests that assert behavioural contracts (e.g. “a new profile appears in generated docs and lists with the correct axes”) over brittle checks against exact static text.

Behaviour‑changing refactors in these areas must not proceed without adequate tests for the behaviour being changed.

---

## Refactor Plan

This refactor plan is deliberately incremental and Concordance‑aligned.

### Phase 1 – Characterize current behaviour

- **Static Prompt Profile & Axes**
  - Catalogue key entrypoints and data structures in:
    - `lib/staticPromptConfig.py` (e.g. `StaticPromptProfile` and related helpers).
    - `lib/talonSettings.py` (e.g. `_read_axis_value_to_key_map` and axis mappings).
  - Add or refine tests in `tests/` to cover:
    - Loading and persisting profiles.
    - Parsing axis→key mappings, including invalid/missing values.
    - Interactions between settings and static prompt configuration.

- **Pattern & Prompt GUI Orchestrators**
  - Identify the main user flows in:
    - `lib/modelPatternGUI.py` (`_axis_value`, `Match`).
    - `lib/modelPromptPatternGUI.py` (`Match`, `prompt_pattern_gui`).
    - `lib/modelHelpGUI.py` (`model_help_gui`).
  - Ensure tests (or new tests) cover:
    - Selection and display of profiles/patterns for typical and edge cases.
    - Error paths and early returns (e.g. missing configuration, invalid axis).

- **Static Prompt Documentation & Lists**
  - Characterize how `_build_static_prompt_docs` and `GPT/lists/staticPrompt.talon-list` derive their content from configuration and settings.
  - Add tests that check behaviour such as:
    - When a new profile/axis is added, generated docs and lists reflect it.
    - Behaviour when configuration is incomplete or inconsistent.

### Phase 2 – Introduce explicit domain APIs

- Extract and formalize a small domain API around static prompt profiles and axes:
  - Functions or classes in `lib/staticPromptConfig.py` that:
    - Expose a stable representation of profiles, axes, and mappings.
    - Perform validation and normalization.
  - Thin wrappers in `lib/talonSettings.py` that:
    - Map settings storage to/from the domain API.
  - Keep branchy/complex logic here and covered by tests.

### Phase 3 – Simplify GUI orchestrators

- Refactor GUI modules to use the domain API rather than parsing configuration directly:
  - Update `_axis_value`, `Match`, `prompt_pattern_gui`, and `model_help_gui` to:
    - Request domain data via the new API.
    - Focus on GUI concerns (layout, events, user interaction).
  - Remove duplicate or divergent interpretations of axis/profile concepts from GUI code where feasible.
  - Extend tests to verify that:
    - GUIs behave correctly for typical, edge, and error cases.
    - Changes to the domain layer are reflected in the GUI with minimal local changes.

### Phase 4 – Align documentation and lists with the domain API

- Update `_build_static_prompt_docs` and related logic to:
  - Build documentation from the same domain API used by GUI and settings.
  - Make dependencies on profiles/axes explicit.
- Where practical, generate or validate `GPT/lists/staticPrompt.talon-list` content against the domain data:
  - At minimum, add tests or checks that detect mismatches between configuration and lists.

At each phase, ensure we maintain or improve test coverage before landing structural changes.

---

## Consequences

Positive outcomes:

- **Reduced coordination cost** – Concept‑level changes (e.g. new axis, updated profile) become more localised, primarily touching the domain API and a small number of consumers.
- **Improved Concordance** – As visibility, scope, and volatility are improved for these hotspots, sustained Concordance scores should decrease because:
  - Contracts between configuration, GUI, and docs are clearer and better tested.
  - Refactors in one area are less likely to require widespread, risky edits.
- **Safer refactors** – Tests‑first characterization and explicit domain APIs reduce the risk of regressions in frequently‑edited modules.

Risks and mitigations:

- **Short‑term churn increase** – Initial refactors may temporarily increase churn in already hot files.
  - Mitigation: Keep changes incremental and test‑guarded; prefer small, behaviourally‑neutral extractions.
- **Over‑abstraction** – Introducing a domain API that is too complex could harm clarity.
  - Mitigation: Keep the domain surface minimal and driven by real use cases (config, GUI, docs).

Expected Concordance‑score effects:

- For hotspots in `lib/staticPromptConfig.py`, `lib/talonSettings.py`, `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`, `lib/modelHelpGUI.py`, `GPT/gpt.py`, and `GPT/lists/staticPrompt.talon-list`, we expect:
  - Lower sustained Concordance scores once:
    - The domain API is in place.
    - GUI orchestrators are simplified to consumers of that API.
    - Documentation and lists are validated against the same source of truth.
  - Any reductions must come from these genuine improvements, not from reducing coverage or loosening checks.

---

## Salient Tasks

- **Static Prompt Profile & Axes**
  - Add or refine tests around `StaticPromptProfile` and `_read_axis_value_to_key_map` to cover branch cases and error paths. *(In this repo, see `tests/test_static_prompt_config.py` and `tests/test_axis_mapping.py`.)*
  - Extract and document a minimal domain API for profiles and axes in `lib/staticPromptConfig.py`. *(Implemented here as `get_static_prompt_profile` / `get_static_prompt_axes`, with tests in `tests/test_static_prompt_config.py`.)*
  - Update `lib/talonSettings.py` to consume the domain API instead of duplicating parsing logic where possible. *(Implemented here for `modelPrompt`.)*

- **Pattern & Prompt GUI Orchestrators**
  - Characterize and test key branches in `_axis_value`, `Match`, `prompt_pattern_gui`, and `model_help_gui`. *(In this repo, see `tests/test_model_pattern_gui.py`, `tests/test_prompt_pattern_gui.py`, and `tests/test_model_help_gui.py`.)*
  - Refactor GUI modules to rely on the domain API for configuration concepts, keeping GUI code focused on presentation and interaction. *(In this repo, `model_help_gui`, `prompt_pattern_gui`, and `modelPrompt` now consume the static prompt domain helpers.)*

- **Static Prompt Documentation & Lists**
  - Add tests that ensure `_build_static_prompt_docs` reflects configuration accurately (including new/changed profiles and axes). *(In this repo, see `tests/test_static_prompt_docs.py`.)*
  - Add checks or tests that detect mismatches between configuration and `GPT/lists/staticPrompt.talon-list`. *(In this repo, see the guardrails in `tests/test_static_prompt_docs.py` and `tests/test_model_pattern_gui.py`.)*

- **Concordance Follow‑up**
  - Re‑run `scripts/tools/line-churn-heatmap.py` after landing key phases and compare the hotspots and scores for the affected nodes.
  - Use subsequent ADR loops/work‑logs to record progress and adjust the refactor plan as needed.

---

## Current Status (this repo)

As of 2025‑12‑03, for this repo:

- **Static Prompt Profile & Axes**
  - Domain helpers `get_static_prompt_profile` / `get_static_prompt_axes` are implemented in `lib/staticPromptConfig.py` and covered by tests in `tests/test_static_prompt_config.py`.
  - Axis defaults, value→key mapping, and recipe tokenisation are characterised by `tests/test_axis_mapping.py`, including behaviour for missing files, long descriptions, and default lookups from the Talon lists.
  - `lib/talonSettings.py::modelPrompt` now consumes the domain helpers for profile descriptions and axis defaults instead of reading `STATIC_PROMPT_CONFIG` directly.

- **Pattern & Prompt GUI Orchestrators**
  - `lib/modelHelpGUI.py::model_help_gui` and `lib/modelPromptPatternGUI.py::prompt_pattern_gui` both use the static prompt domain API to display profile descriptions and axis defaults, keeping GUI views aligned with configuration.
  - Prompt pattern execution paths are characterised by `tests/test_prompt_pattern_gui.py`, which exercise `_run_prompt_pattern` and `UserActions.prompt_pattern_run_preset`.

- **Remaining / Future Work**
  - Static prompt documentation and list consumers have initial characterization and domain‑API alignment:
    - `_build_static_prompt_docs` now consumes the static prompt domain helpers and is covered by `tests/test_static_prompt_docs.py`.
    - A guardrail test ensures all profiled prompts in `STATIC_PROMPT_CONFIG` have corresponding tokens in `GPT/lists/staticPrompt.talon-list`.
  - Concordance follow‑up work (re‑running the churn × complexity scan to observe the impact of these refactors) has begun; see recent snapshots in the ADR‑010 work‑log for details.

Overall, for this repo, ADR‑010’s core foundations (domain helpers, GUI refactors, docs/list guardrails, and test coverage) are in place; remaining work is largely opportunistic and driven by future hotspots.

---

## How to Re‑run ADR‑010 Checks (this repo)

- **Churn × complexity heatmap**
  - `python scripts/tools/churn-git-log-stat.py`
  - `python scripts/tools/line-churn-heatmap.py`
  - Inspect `tmp/churn-scan/line-hotspots.json` (especially nodes for `lib/staticPromptConfig.py`, `lib/talonSettings.py`, `lib/modelHelpGUI.py`, `lib/modelPromptPatternGUI.py`, `GPT/gpt.py`, and `GPT/lists/staticPrompt.talon-list`).
  - Or run the Makefile helper:
    - `make churn-scan`
  - To print a focused ADR‑010 hotspot summary:
     - `make adr010-status`

- **Static prompt domain & axes tests**
  - `python -m unittest tests.test_static_prompt_config tests.test_axis_mapping`

- **GUI and prompt pattern behaviour**
  - `python -m unittest tests.test_prompt_pattern_gui tests.test_talon_settings_model_prompt`

- **Static prompt docs and list alignment**
  - `python -m unittest tests.test_static_prompt_docs`

- **Full test sweep (this repo)**
  - `make test`

- **Focused ADR‑010 checks**
  - `make adr010-check`

These commands exercise the main guardrails and hotspots that ADR‑010 governs in this repo.

---

## Example ADR‑010 Workflow (this repo)

- Run a fresh churn × complexity scan:
  - `make churn-scan`
- Inspect ADR‑010 hotspots:
  - `make adr010-status`
- Run focused ADR‑010 tests:
  - `make adr010-check`

---

## Hotspot ↔ Tests Map (this repo)

- `lib/staticPromptConfig.py::StaticPromptProfile` and domain helpers:
  - `tests/test_static_prompt_config.py`
  - `tests/test_axis_mapping.py`
- `lib/talonSettings.py::_read_axis_value_to_key_map`, `_read_axis_default_from_list`, `_axis_recipe_token`, `modelPrompt`:
  - `tests/test_axis_mapping.py`
  - `tests/test_talon_settings_model_prompt.py`
- `lib/modelPatternGUI.py::_axis_value`, `_parse_recipe`, `_run_pattern`, `model_pattern_gui`:
  - `tests/test_model_pattern_gui.py`
- `lib/modelPromptPatternGUI.py::_axis_value`, `_run_prompt_pattern`, `prompt_pattern_gui`:
  - `tests/test_prompt_pattern_gui.py`
- `lib/modelHelpGUI.py::model_help_gui` and related actions:
  - `tests/test_model_help_gui.py`
- `GPT/gpt.py::_build_static_prompt_docs`, `_build_axis_docs`:
  - `tests/test_static_prompt_docs.py`
- `GPT/lists/staticPrompt.talon-list` and `STATIC_PROMPT_CONFIG` alignment:
  - `tests/test_static_prompt_docs.py`
  - `tests/test_model_pattern_gui.py`
