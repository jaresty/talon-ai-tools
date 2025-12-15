# ADR-0011 – Concordance Static Prompt and Axis Mapping Domain Boundaries

Status: Accepted  
Date: 2025-12-03  
Owners: Talon AI tools maintainers

---

## Summary (For New Contributors)

This ADR defines and governs two closely related domains:

- The **static prompt domain** (`lib/staticPromptConfig.py`, `GPT/lists/staticPrompt.talon-list`, related GUIs/docs) that owns static prompts, their descriptions, and axis profiles.
- The **axis mapping and model prompt domain** (`lib/talonSettings.py` and related tests) that maps spoken modifiers and defaults into short axis tokens and `modelPrompt` behaviour.

Its goals are to:

- Make these domains explicit and easier to reason about.
- Keep their contracts and tests aligned so Concordance scores fall through genuine structural and behavioural improvements, not by weakening guardrails.

Related ADRs:

- `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md` – earlier, broader Concordance/churn ADR that first identified these domains as hotspots and motivated this focused boundary ADR.

## Context

Over the last 90 days, the statement-level churn × complexity × coordination heatmap for this repo (scope: `lib/`, `GPT/`, `copilot/`, `tests/`) surfaced a small set of consistently hot areas:

- **Static prompt config and lists**
  - `lib/staticPromptConfig.py::StaticPromptProfile` (Class) – very high score driven by high churn and high coordination.
  - `lib/staticPromptConfig.py::get_static_prompt_axes`, `get_static_prompt_profile`.
  - `GPT/lists/staticPrompt.talon-list` – frequent edits with high coordination.
- **Model GUIs and pattern wiring**
  - `lib/modelPatternGUI.py::_axis_value`, `Match`.
  - `lib/modelPromptPatternGUI.py::prompt_pattern_gui`, `Match`.
  - `lib/modelHelpGUI.py::model_help_gui`.
- **Talon settings and axis mapping**
  - `lib/talonSettings.py::_read_axis_value_to_key_map`, `_axis_recipe_token`, `_read_axis_default_from_list`.
  - `lib/talonSettings.py::modelPrompt`, `pleasePrompt`.
- **GPT orchestration and docs**
  - `GPT/gpt.py::_build_static_prompt_docs`, `get_static_prompt_axes`.
  - `GPT/gpt.py::Match`, `gpt_suggest_prompt_recipes_with_source`, `gpt_rerun_last_recipe`.
  - `GPT/readme.md`, `GPT/gpt.talon`, `GPT/gpt-patterns-gui.talon`.
- **High-churn tests**
  - `tests/test_integration_suggestions.py::test_suggest_then_again_merges_overrides`.
  - `tests/test_gpt_actions.py::test_gpt_rerun_last_recipe_applies_overrides_on_last_tokens`.
  - `tests/test_model_pattern_gui.py::test_all_pattern_static_prompts_exist_in_config_and_list`.
  - `tests/test_talon_settings_model_prompt.py::test_model_prompt_updates_last_recipe_with_spoken_modifiers`, `test_clear_all_resets_last_recipe_and_response`.

From these nodes, two main hotspot clusters emerge:

- **Static prompt config and lists + GPT orchestration + tests**
  - End-to-end static prompt axis/profile definition, docs, Talon/GPT commands, and integration tests.
  - Coordination cuts across `lib/staticPromptConfig.py`, `GPT/gpt.py`, `GPT/lists/staticPrompt.talon-list`, and multiple tests.
- **Axis mapping, Talon settings, and model GUIs + tests**
  - Axis/value mapping from spoken Talon phrases into GPT model prompt patterns and recipes.
  - Coordination spans `lib/talonSettings.py`, the model GUIs under `lib/model*GUI.py`, GPT orchestration, and tests.

### Concordance view: visibility, scope, volatility

Applying the Concordance framing:

- **Visibility**
  - The contracts between static prompt config (`staticPromptConfig`), GPT helpers (`_build_static_prompt_docs`, `get_static_prompt_axes`), GUI/pattern modules, and Talon lists are mostly implicit.
  - Domain responsibilities such as “who owns the truth for static prompt axes and profiles” and “who owns axis-to-token mapping” are not named or centralized; callers infer implicit data shapes instead.
  - Tests encode many of the real contracts (what must line up, what tokens are expected), but these contracts are not clearly exposed in the code surface.
- **Scope**
  - Small changes to static prompt definitions, axes, or axis mappings routinely fan out across:
    - Config modules (`staticPromptConfig`, `talonSettings`).
    - Talon lists and command grammars (`GPT/lists/*.talon-list`, `GPT/gpt.talon`).
    - GUI wiring (`modelPatternGUI`, `modelPromptPatternGUI`, `modelHelpGUI`).
    - Integration tests and helper tests.
  - The implicit orchestration in `GPT/gpt.py` also widens the blast radius, as it directly reaches into multiple domains.
- **Volatility**
  - High churn on `StaticPromptProfile`, static prompt axes functions, axis mapping helpers, and their tests indicates:
    - Evolving domain understanding for static prompts and axis mapping.
    - Frequent small fixes to keep config, Talon lists, GUIs, and tests in sync.
  - Churn is not limited to leaf helpers; it affects orchestrators and tests, raising coordination cost.

### Hidden domains / “tunes”

From the above, two hidden domains are apparent:

1. **Static prompt tune and Concordance domain**
   - **Members (illustrative):**
     - `lib/staticPromptConfig.py::StaticPromptProfile`, `get_static_prompt_axes`, `get_static_prompt_profile`.
     - `GPT/gpt.py::_build_static_prompt_docs`, `get_static_prompt_axes`.
     - `GPT/lists/staticPrompt.talon-list`.
     - Integration tests that assert static prompt / profile coherence (for example, `test_all_pattern_static_prompts_exist_in_config_and_list`) and static prompt–related integration paths.
   - **Visibility pattern:** the static prompt “tune” (axes, profiles, docs, and Concordance-facing expectations) is split across config, GPT helpers, lists, and tests without a single named domain home.
   - **Scope pattern:** edits to axes or profiles propagate across multiple modules and tests; the system behaves like one domain but is implemented as several ad-hoc ones.
   - **Volatility pattern:** sustained churn at both structural (“who owns axes and profiles”) and surface (“update specific axis or prompt text”) levels.

2. **Axis mapping and Talon model prompt domain**
   - **Members (illustrative):**
     - `lib/talonSettings.py::_read_axis_value_to_key_map`, `_axis_recipe_token`, `_read_axis_default_from_list`, `modelPrompt`, `pleasePrompt`.
     - `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`, `lib/modelHelpGUI.py` (especially axis-related helpers and `Match` classes).
     - `GPT/gpt.py` functions that interpret or propagate axis and recipe tokens.
     - Tests in `tests/test_model_pattern_gui.py`, `tests/test_talon_settings_model_prompt.py`, and related integration tests.
   - **Visibility pattern:** the mapping from spoken phrases to underlying recipe tokens and prompt patterns is realized through a combination of Talon settings, GUI wiring, and GPT orchestration. The resulting contracts are only partially visible in any one module.
   - **Scope pattern:** when axis mapping or `modelPrompt` behavior changes, GUIs, GPT commands, and tests all move together.
   - **Volatility pattern:** repeated edits to axis mapping helpers, `modelPrompt`, GUI matchers, and their tests indicate that this domain is still being actively tuned.

In both domains, Concordance currently reports high, sustained scores because visibility is low (implicit contracts), scope is wide (changes fan out), and volatility is high (frequent edits across coupled files).

---

## Problem

The current structure around static prompts and axis mapping exhibits:

- **Implicit domain boundaries**
  - Static prompt axes, profiles, and docs are scattered across config, GPT helpers, Talon lists, and tests.
  - Axis mapping from spoken commands to recipe tokens is spread across Talon settings, GUI modules, GPT orchestration, and tests.
- **High coordination cost**
  - Seemingly local edits (for example, changing an axis default, adding a profile, adjusting mapping semantics) require touching multiple modules and several tests.
  - Orchestration logic in `GPT/gpt.py` and Talon settings reaches across these domains, amplifying blast radius.
- **Refactor risk and friction**
  - Because contracts live in many places and are poorly named, refactors that should be local feel risky, and tests must be carefully curated to avoid regressions.
  - High Concordance scores reflect actual coordination pain rather than noisy signals.

We want to reduce Concordance scores for these hotspots over time by:

- **Increasing visibility** of domain contracts and orchestration boundaries.
- **Narrowing scope** so changes to axes, profiles, and axis mappings are local and predictable.
- **Reducing volatility** through better factoring, alignment with existing patterns, and stronger behavioral tests—without weakening Concordance guardrails or hiding signals.

---

## Current Status and Relationship to Other ADRs

As of the initial adoption of ADR-0011:

- Many of the refactor steps it describes are already in place through earlier work, especially ADR-005, ADR-006, ADR-007, and ADR-010:
  - `lib/staticPromptConfig.py` already provides `get_static_prompt_profile` and `get_static_prompt_axes` and is consumed by:
    - `lib/talonSettings.py::modelPrompt` for profile descriptions and axis defaults.
    - GUI modules (for example, `modelHelpGUI`, `modelPromptPatternGUI`) when available.
    - Static prompt docs builders in `GPT/gpt.py`.
  - Axis mapping helpers in `lib/talonSettings.py` (`_read_axis_value_to_key_map`, `_axis_recipe_token`, `_read_axis_default_from_list`) already form a reusable mapping surface for completeness, scope, method, style, and directional axes.
  - Tests such as `tests/test_static_prompt_config.py`, `tests/test_static_prompt_docs.py`, `tests/test_axis_mapping.py`, and `tests/test_talon_settings_model_prompt.py` already characterize key behaviours and invariants for these domains.
- ADR-0011 therefore:
  - Primarily codifies the inferred domain boundaries and Concordance goals for static prompts and axis mapping.
  - Serves as a coordination and governance ADR ensuring future changes respect these boundaries and reuse the existing façades and tests.
  - Leaves only incremental work in this repo (for example, tightening or extending invariants when justified by churn or Concordance signals, and using the existing tests as guardrails).

---

## Execution Status (This Repo)

For this repository as of 2025-12-03:

- Static prompt and axis mapping façades described by this ADR are implemented and actively used by `modelPrompt`, GUIs, and GPT docs.
- Focused, branch-level tests exercise the core behaviours and invariants for these domains.
- A Concordance baseline for these hotspots has been captured and wired into the ADR’s follow-up tasks.
- Remaining work is incremental and Concordance-driven rather than foundational; see `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.work-log.md` for per-loop history and any new slices.

---

## Key Files and Tests (This Repo)

When working under this ADR, these are the primary artefacts to inspect first:

- **Static prompt domain (code)**
  - `lib/staticPromptConfig.py`
  - `GPT/lists/staticPrompt.talon-list`
  - Static prompt-related sections of `GPT/gpt.py`
- **Axis mapping and modelPrompt domain (code)**
  - `lib/talonSettings.py`
- **Core tests**
  - `tests/test_static_prompt_config.py`
  - `tests/test_static_prompt_docs.py`
  - `tests/test_axis_mapping.py`
  - `tests/test_talon_settings_model_prompt.py`

---

## Out of Scope (This Repo)

This ADR does **not** directly govern:

- The detailed behaviour and layout of model GUIs (`lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`, `lib/modelHelpGUI.py`) beyond their use of static prompts and axis mappings; see ADR-006/ADR-007 for GUI/pattern decisions.
- Non-static prompt GPT behaviours and tools outside `modelPrompt` and its axis/static-prompt coordinates.
- Broader Concordance and churn work not specific to static prompts or axis mappings; ADR-010 remains the umbrella ADR for those concerns.

When working in those areas, treat ADR-0011 as a constraint only where static prompts or axis mappings are involved; otherwise follow the relevant ADRs for those domains.

---

## Decision

We will introduce and align around two explicit domains and their boundaries:

1. **Static prompt domain façade**
   - Create an explicit static prompt domain façade responsible for:
     - Owning the source of truth for static prompt axes and profiles.
     - Providing a clear API for retrieving axes and profiles for both Talon lists and GPT orchestration.
     - Capturing Concordance-facing contracts (for example, which axes must exist, how profiles compose, and what invariant relationships tests enforce).
   - Existing modules (`staticPromptConfig`, `GPT/gpt.py`, `GPT/lists/staticPrompt.talon-list`) will consume this façade instead of re-encoding their own partial views of axes and profiles.

2. **Axis mapping and model prompt domain façade**
   - Extract axis/value mapping and recipe token logic from `lib/talonSettings.py` and GUI helpers into a dedicated axis mapping domain, with:
     - A clear mapping from spoken forms to internal axis values and recipe tokens.
     - Configurable, testable contracts that can be reused across Talon settings, GUIs, and GPT orchestration.
   - `modelPrompt` and GUI `Match` classes will treat this domain as their primary dependency for axis and token semantics rather than duplicating logic.

Across both domains, we will:

- **Align with existing patterns** in this repo (for example, existing domain modules under `lib/`, current GUI orchestrator patterns, existing GPT CLI entrypoints) instead of inventing novel frameworks.
- **Drive refactors through behavior-first tests**, ensuring that:
  - Behavior is characterized before structural changes.
  - Existing integration tests remain the primary guardrails where they already provide good coverage.
- **Target Concordance outcomes explicitly**:
  - We expect sustained Concordance scores for the affected hotspots to decline as visibility increases, scope narrows, and volatility is better absorbed by the new domain homes.
  - We will not relax Concordance checks, reduce coverage, or otherwise game scores; reductions must arise from genuine structural and behavioral improvements.

---

## Tests-First Principle

We restate and adopt the following tests-first refactor principle for this work:

> At each step, we will first analyze existing tests to ensure that the behavior we intend to change is well covered. Where coverage is insufficient, we will add focused characterization tests capturing current behavior (including relevant branches and error paths), and then proceed with the refactor guarded by those tests. Where coverage is already strong and branch-focused for the paths we are changing, we will rely on and, if needed, extend those existing tests rather than adding redundant characterization tests.

Concretely:

- Behavior-changing refactors must not proceed without **adequate** characterization tests for the behavior being changed.
- When existing tests already provide good behavioral and branch coverage for the relevant paths, we will **reuse and extend** those tests instead of adding near-duplicates.
- Tests will favor behavioral/contract-level assertions over internal implementation details, and suites should stay reasonably fast and focused.
- We will avoid tests whose sole intent is to assert incidental static text (for example, boilerplate documentation wording) unless that text itself encodes a behavior-level contract.

---

## Refactor Plan

### 1. Static prompt domain façade

**Original draft idea**

- Centralize static prompt axes and profiles in a dedicated domain module/facade (for example, `lib/staticPromptDomain.py`), and have `staticPromptConfig`, `GPT/gpt.py` helpers, and `GPT/lists/staticPrompt.talon-list` consume it.

**Similar existing behavior and patterns**

- `lib/staticPromptConfig.py` already acts as a de facto domain home for static prompt profiles and axes.
- `GPT/gpt.py::_build_static_prompt_docs` and `get_static_prompt_axes` know how to turn static prompt structures into documentation and UI data.
- Tests like `tests/test_model_pattern_gui.py::test_all_pattern_static_prompts_exist_in_config_and_list` already encode key invariants between config and Talon lists.

**Revised recommendation**

- Evolve `lib/staticPromptConfig.py` into an explicit **static prompt domain façade** rather than creating a separate module:
  - Clarify and document its public API (for example, `get_static_prompt_axes`, `get_static_prompt_profile`, and any additional query helpers).
  - Make the invariants currently enforced in tests (such as “all static prompts in pattern GUIs exist in config and lists”) explicit in code-level contracts and, where practical, runtime checks.
  - Ensure `GPT/gpt.py` and `GPT/lists/staticPrompt.talon-list` rely on this façade for axes/profiles instead of duplicating or recomputing views.
- Keep orchestration logic (for example, command behavior) in `GPT/gpt.py`, but route all static prompt domain concerns through the façade.

**Tests-first refactor plan (static prompt domain)**

- **Existing tests to rely on:**
  - `tests/test_model_pattern_gui.py::test_all_pattern_static_prompts_exist_in_config_and_list`.
  - Integration tests that exercise static prompt behavior (for example, suggestions and recipe prompts that depend on static prompts).
- **New characterization tests (where needed):**
  - Focused tests for `get_static_prompt_axes` and `get_static_prompt_profile` covering:
    - Happy paths (common profiles and axes used in GUIs and GPT).
    - Edge cases (missing axes, invalid profiles, backward-compatible changes).
  - Tests that ensure static prompt façade APIs remain backward compatible across refactors (for example, shape of returned structures).
- **Refactor steps:**
  - Step 1: Strengthen and extend characterization tests around static prompt invariants without changing code behavior.
  - Step 2: Refactor `staticPromptConfig` to expose a clearer public API, while all callers continue to pass tests.
  - Step 3: Update `GPT/gpt.py` static prompt helpers and `GPT/lists/staticPrompt.talon-list` usage to rely on the clarified façade.
  - Step 4: Optionally introduce small runtime assertions in the façade to catch misalignment early, guarded by tests.

### 2. Axis mapping and model prompt domain façade

**Original draft idea**

- Extract axis/value mapping and recipe token logic from `lib/talonSettings.py` and GUI modules into a dedicated axis mapping domain (for example, `lib/axisMapping.py`) and have `modelPrompt`, GUIs, and GPT orchestration rely on it.

**Similar existing behavior and patterns**

- `lib/talonSettings.py::_read_axis_value_to_key_map`, `_axis_recipe_token`, `modelPrompt`, and `pleasePrompt` already form a de facto axis mapping and model prompt orchestrator.
- GUI modules like `lib/modelPatternGUI.py` and `lib/modelPromptPatternGUI.py` already encapsulate pattern matching and axis selection for the model UI.
- Tests in `tests/test_model_pattern_gui.py` and `tests/test_talon_settings_model_prompt.py` already define behavior for spoken modifiers, last recipe behavior, and clearing/reset semantics.

**Revised recommendation**

- Introduce an explicit **axis mapping façade** that can be composed with `talonSettings` and GUIs:
  - The façade may live as a dedicated helper module (for example, `lib/axisMapping.py`) or as a clearly separated section within `lib/talonSettings.py`, depending on what better matches existing patterns.
  - Clearly define its inputs (spoken modifiers, axis names/values, context) and outputs (internal axis values, recipe tokens, mapping metadata).
  - Ensure GUI modules and `modelPrompt` call through the façade rather than duplicating ad-hoc mapping logic.
- Keep Talon-specific and GUI-specific wiring (Talon lists, UI widgets) in their existing homes, using the façade strictly for mapping semantics.

**Tests-first refactor plan (axis mapping domain)**

- **Existing tests to rely on:**
  - `tests/test_talon_settings_model_prompt.py`:
    - `test_model_prompt_updates_last_recipe_with_spoken_modifiers`.
    - `test_clear_all_resets_last_recipe_and_response`.
  - `tests/test_model_pattern_gui.py` for axis-related GUI behavior and contracts.
  - Integration tests around GPT actions that involve axis modifiers (for example, `tests/test_gpt_actions.py::test_gpt_rerun_last_recipe_applies_overrides_on_last_tokens`).
- **New characterization tests (where needed):**
  - Focused tests for axis mapping helpers capturing:
    - Mapping from specific spoken forms to internal axis values and recipe tokens.
    - Error handling and fallbacks (for example, unknown modifiers, conflicting modifiers).
  - Behavior-level tests confirming that the combination of GUI + Talon settings + GPT orchestration yields the expected prompts and recipes for key scenarios.
- **Refactor steps:**
  - Step 1: Confirm that existing tests cover main branches (true/false, error paths, early returns) in axis mapping helpers and `modelPrompt`. Add missing characterization tests where gaps are found.
  - Step 2: Introduce the axis mapping façade with minimal internal redirects from existing helpers (for example, have `_axis_recipe_token` delegate to a new façade function) while keeping tests green.
  - Step 3: Migrate GUIs and orchestrators to consume the façade directly, guided by existing tests.
  - Step 4: Simplify or inline duplicated mapping logic that is now redundant, ensuring tests continue to pass.

### 3. Concordance alignment

For both domains, we will:

- Track which hotspots and tests are in scope for each refactor slice.
- After landing significant slices (for example, façade introduction and major caller migrations), re-run the churn × complexity heatmap and Concordance scores to confirm:
  - Improved visibility (contracts easier to find and reason about).
  - Narrower scope (fewer files and tests touched for domain-local changes).
  - Reduced volatility or better-absorbed volatility in a single domain home.

---

## Consequences

### Positive outcomes

- **Lower coordination cost**
  - Static prompt and axis mapping behavior becomes easier to change safely, with clearer domain homes and contracts.
  - Localized changes are less likely to require cross-cutting edits to GUIs, Talon lists, and tests.
- **Improved Concordance scores**
  - Reduced sustained scores for the in-scope hotspots as structure and tests improve.
  - Scores become more interpretable, signaling genuine coordination issues rather than structural ambiguity.
- **Safer evolution of static prompts and axis mapping**
  - Tests-first characterization and clearer façades reduce the risk of regressions when tuning prompts or mapping semantics.

### Risks and mitigations

- **Risk: façade complexity or over-abstraction**
  - Mitigation: align façades with existing patterns and start with minimal, behavior-driven interfaces.
- **Risk: refactor churn temporarily increases volatility**
  - Mitigation: phase refactors, keep slices small, and ensure tests lead each change.
- **Risk: tests become brittle if tied too closely to internals**
  - Mitigation: focus tests on behavior-level contracts and only expose internal details that represent stable domain concepts.

---

## Maintainer Usage Guidance

When changing or extending behaviour in these domains:

- **Adding or updating static prompts**
  - Add or adjust profiles in `lib/staticPromptConfig.py` using `StaticPromptProfile` (description and optional axes).
  - Ensure `GPT/lists/staticPrompt.talon-list` contains a corresponding token for each profiled prompt key.
  - If patterns or GUIs start to use a new static prompt, confirm it appears in:
    - `STATIC_PROMPT_CONFIG`,
    - `staticPrompt.talon-list`, and
    - static-prompt docs via `_build_static_prompt_docs`.
- **Adding or updating axis modifiers**
  - Edit the relevant `GPT/lists/*Modifier.talon-list` file (completeness/scope/method/style/directional).
  - Rely on `_read_axis_value_to_key_map` and `_axis_value_to_key_map_for` for value→key mappings inside `talonSettings` rather than re-parsing list files elsewhere.
  - Keep new behaviour covered by `tests/test_axis_mapping.py` and `tests/test_talon_settings_model_prompt.py`; extend those tests when adding new axis values or branches.
- **Refactors touching these domains**
  - Treat `tests/test_static_prompt_config.py`, `tests/test_static_prompt_docs.py`, `tests/test_axis_mapping.py`, and `tests/test_talon_settings_model_prompt.py` as the minimum gating set.
  - When changes are large enough to plausibly affect churn or coordination, rerun the churn × complexity heatmap and compare against the 2025-12-03 baseline before updating ADR status or scope.

### Quick Checklist (Before Merging Changes)

For any PR that touches static prompts, axis modifiers, or `modelPrompt`:

- [ ] Updated or added `StaticPromptProfile` entries in `lib/staticPromptConfig.py` where appropriate.
- [ ] Kept `GPT/lists/staticPrompt.talon-list` and static prompt docs in sync with new/changed profiles.
- [ ] Used `_axis_value_to_key_map_for` / `_read_axis_value_to_key_map` instead of introducing new ad-hoc mappings.
- [ ] Extended or re-ran the gating tests:
  - `tests/test_static_prompt_config.py`
  - `tests/test_static_prompt_docs.py`
  - `tests/test_axis_mapping.py`
  - `tests/test_talon_settings_model_prompt.py`
- [ ] (For larger refactors) Considered re-running `scripts/tools/line-churn-heatmap.py` and comparing against the 2025-12-03 baseline for these domains.

Recommended combined test command:

```bash
python -m unittest \
  tests.test_static_prompt_config \
  tests.test_static_prompt_docs \
  tests.test_axis_mapping \
  tests.test_talon_settings_model_prompt \
  -q
```

### Example Change Flows

- **Adding a new static prompt with an axis profile**
  - Add a `StaticPromptProfile` entry in `lib/staticPromptConfig.py` with description and any axis defaults.
  - Add the token to `GPT/lists/staticPrompt.talon-list`.
  - Run the combined gating tests; fix any failures in static-prompt docs or pattern tests.
- **Adding a new axis modifier value**
  - Add the new `key: description` line to the appropriate `GPT/lists/*Modifier.talon-list`.
  - Verify that `_read_axis_value_to_key_map` / `_axis_value_to_key_map_for` handle it correctly by extending `tests/test_axis_mapping.py` where needed.
  - Run the combined gating tests and, if behaviour changes are significant, consider a fresh churn × complexity snapshot.

---

## Future Revisit Triggers

Revisit or extend this ADR when any of the following occur:

- **New Concordance hotspots** emerge around static prompts or axis mapping that are not well explained by the current domains (for example, new high-churn nodes outside `staticPromptConfig`/`talonSettings` but clearly related to these concerns).
- **Major prompt taxonomy changes** (for example, a large expansion or restructuring of static prompts or axis modifiers) that significantly alter coordination patterns, list structures, or profile semantics.
- **New orchestration surfaces** (for example, additional GUIs, CLIs, or tools) begin to coordinate static prompts or axis mappings without going through the existing façades.
- **Evidence of test blind spots** appears (for example, real regressions or near-misses) indicating that current characterization is insufficient for new behaviours.

When one of these triggers fires:

- Start from this ADR’s work-log and the latest Concordance snapshot.
- Decide whether to:
  - Add focused tests/invariants within the existing domains, or
  - Extend/split domains and update this ADR (or a successor ADR) accordingly.

---

## Salient Tasks

- **Static prompt domain**
  - Strengthen characterization tests around static prompt invariants (config ↔ lists ↔ GUIs). *(Satisfied in this repo as of 2025-12-03; see ADR-0011 work-log Loops 1–2.)*
  - Clarify and document `staticPromptConfig` public API for axes and profiles. *(Satisfied by existing helpers and tests; further changes should extend, not replace, the current façade.)*
  - Update `GPT/gpt.py` static prompt helpers and `GPT/lists/staticPrompt.talon-list` to use the clarified façade API. *(In place: current helpers and guardrails already consume `staticPromptConfig` rather than raw config.)*
  - Add targeted runtime checks or logging for key invariants where useful.
- **Axis mapping and model prompt domain**
  - Confirm branch-level coverage for axis mapping and `modelPrompt` in existing tests; fill gaps with focused tests. *(Satisfied by `tests/test_axis_mapping.py` and `tests/test_talon_settings_model_prompt.py` as of 2025-12-03.)*
  - Introduce an axis mapping façade aligned with existing `talonSettings` and GUI patterns. *(Partially satisfied via `_axis_value_to_key_map_for` and related maps in `lib/talonSettings.py`; future callers should reuse this surface instead of duplicating mappings.)*
  - Evaluate where, if at all, GUIs and GPT orchestration should consume the façade in addition to their existing list-driven mappings, based on Concordance hotspots and duplication rather than by default.
  - Simplify or remove redundant mapping logic once the façade is fully adopted.
- **Concordance follow-up**
  - Re-run `scripts/tools/line-churn-heatmap.py` after major slices land and review updated hotspots. *(Initial baseline snapshot captured on 2025-12-03; see ADR-0011 work-log Loop 8 for details.)*
  - Adjust subsequent refactor slices or tests based on observed Concordance score changes relative to that baseline to ensure sustained improvement rather than local optimizations.
