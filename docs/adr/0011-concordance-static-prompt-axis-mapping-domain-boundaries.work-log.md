# ADR-0011 Work-log – Concordance Static Prompt and Axis Mapping Domain Boundaries

## 2025-12-03 – Loop 1 – Status snapshot and overlap with ADR-010

Focus area:

- Reconcile ADR-0011’s refactor plan with the current code and existing ADR-010 work, and capture a clear starting status for static prompt and axis mapping domains.

Changes in this loop:

- Confirmed that much of ADR-0011’s “Refactor Plan” for static prompts and axis mapping has already landed in this repo as part of ADR-010:
  - **Static prompt domain façade**
    - `lib/staticPromptConfig.py` exposes `get_static_prompt_profile` and `get_static_prompt_axes` as the primary API over `STATIC_PROMPT_CONFIG`, matching the façade described in ADR-0011.
    - `GPT/gpt.py::_build_static_prompt_docs` builds documentation using `STATIC_PROMPT_CONFIG`, `get_static_prompt_profile`, and `get_static_prompt_axes`, rather than reaching into the raw config structure independently.
    - `tests/test_static_prompt_config.py` and `tests/test_static_prompt_docs.py` provide characterization tests over:
      - Profile lookup and axis extraction for prompts like `"todo"` and `"describe"`.
      - Coherence between `STATIC_PROMPT_CONFIG`, `GPT/lists/staticPrompt.talon-list`, and static prompt documentation output.
  - **Axis mapping and model prompt domain**
    - `lib/talonSettings.py` defines `_axis_recipe_token` and related `_READ_AXIS_*` helpers as a reusable mapping surface for completeness/scope/method/style/directional axes.
    - `tests/test_axis_mapping.py` characterizes:
      - Value→key mapping from Talon list entries (including malformed lines and missing files).
      - `_axis_recipe_token` behaviour for known/unknown axes.
      - `_read_axis_default_from_list` semantics for present vs missing defaults.
    - `tests/test_talon_settings_model_prompt.py` and `tests/test_model_pattern_gui.py` exercise:
      - How spoken modifiers, static prompt profiles, and defaults combine inside `modelPrompt`.
      - How pattern GUIs rely on static prompt tokens and profiles.
- Established that ADR-0011 primarily:
  - Codifies these domain boundaries and Concordance expectations explicitly.
  - Adds emphasis on visibility/scope/volatility and Concordance outcomes, rather than introducing an entirely new refactor plan from scratch.

Impact on ADR-0011 objectives:

- Narrows the **remaining in-repo scope** (`B_a`) for ADR-0011 by:
  - Treating the existing static prompt façade, axis mapping helpers, and associated tests as already satisfying the early phases of its Refactor Plan.
  - Identifying ADR-0011’s primary incremental role as:
    - Making domain boundaries and Concordance goals explicit (already done in the ADR text).
    - Guiding any **further** consolidation or guardrails, rather than re-implementing what ADR-010 already delivered.
- Improves **evidence (`C_a`)** by confirming that:
  - High-churn hotspots called out in ADR-0011 (staticPromptConfig, talonSettings axis mapping, GPT static prompt docs) already have focused, behavior-level tests.
  - Future structural changes in these areas can lean on those tests without needing a new round of broad characterization.

Follow-ups (not completed in this loop):

- For static prompt domain:
  - Decide whether ADR-0011 needs any **additional** invariants or runtime checks in `staticPromptConfig` (for example, sanity checks that every profiled prompt appears in the Talon list), beyond what tests already enforce indirectly.
  - If so, add them in a tests-first slice that reuses `tests/test_static_prompt_config.py` and `tests/test_static_prompt_docs.py` as guardrails.
- For axis mapping and model prompt:
  - Review `lib/talonSettings.py` and GUIs (`modelHelpGUI`, `modelPromptPatternGUI`) for any remaining direct accesses to raw config structures that could be further aligned with the existing façade-style helpers.
  - If meaningful drift is found, plan a small follow-up loop to migrate those callers, using the existing tests (`test_axis_mapping.py`, `test_talon_settings_model_prompt.py`, GUI tests) for safety.
- For Concordance status:
  - In a later loop, run a focused Concordance/heatmap snapshot after any new slices land for ADR-0011 and record in this work-log whether hotspot scores and coordination patterns have measurably improved.

---

## 2025-12-03 – Loop 2 – Static prompt invariants and guardrails status

Focus area:

- Clarify which static prompt invariants ADR-0011 calls for are already enforced by tests, and mark those tasks as effectively satisfied for this repo.

Changes in this loop:

- Reviewed existing guardrail tests around static prompts:
  - `tests/test_static_prompt_docs.py::test_all_profiled_prompts_have_static_prompt_token`:
    - Reads `STATIC_PROMPT_CONFIG.keys()` from `lib/staticPromptConfig.py`.
    - Parses `GPT/lists/staticPrompt.talon-list`.
    - Asserts that every profiled prompt key has a corresponding token in the Talon list, matching ADR-0011’s goal of keeping profiles and list entries in sync.
  - `tests/test_model_pattern_gui.py::test_all_pattern_static_prompts_exist_in_config_and_list`:
    - Ensures that every static prompt referenced by pattern recipes:
      - Appears in `STATIC_PROMPT_CONFIG`, and
      - Has a token in `staticPrompt.talon-list`.
    - Guards against drift between pattern usage, config, and Talon lists.
  - `tests/test_static_prompt_config.py`:
    - Characterises `get_static_prompt_profile` and `get_static_prompt_axes` behaviour for:
      - Known profiled prompts (for example, `"todo"`).
      - Description-only prompts (for example, `"describe"`).
      - Unknown prompts (returning `None`/`{}` as appropriate).
- Cross-checked these tests against ADR-0011’s “Refactor Plan” expectations for the static prompt domain:
  - The ADR calls for:
    - Invariants such as “all profiled prompts appear in the Talon list.”
    - Alignment between static prompt usage in patterns, config, and docs.
    - Characterised behaviour for `get_static_prompt_profile` / `get_static_prompt_axes`.
  - The current tests already implement these guardrails and characterisations without needing additional coverage in this loop.

Impact on ADR-0011 objectives:

- Effectively retires the “add new tests for static prompt invariants” part of ADR-0011’s static prompt Refactor Plan for this repo, as those tests already exist and are active:
  - Alignment between `STATIC_PROMPT_CONFIG` and `staticPrompt.talon-list` is guarded.
  - Alignment between pattern static prompts, config, and list tokens is guarded.
  - Static prompt façade helpers have basic behaviour and edge-case coverage.
- Tightens the ADR’s scope by:
  - Treating further changes in this area as **refactor or invariant-tightening work** driven by these existing tests, rather than a fresh characterization effort.

Follow-ups (not completed in this loop):

- When running the full test suite is practical, ensure the above tests are part of the gating set for any changes that:
  - Add or remove static prompts from `STATIC_PROMPT_CONFIG`.
  - Modify `GPT/lists/staticPrompt.talon-list` structure or entries.
  - Change how patterns reference static prompts.
- If future tuning reveals additional meaningful invariants (for example, constraints on axis combinations per profile), add them as focused tests in `tests/test_static_prompt_config.py` or `tests/test_static_prompt_docs.py`, keeping them behaviour-level and aligned with ADR-0011’s Concordance goals.

---

## 2025-12-03 – Loop 3 – Directional axis mapping characterization

Focus area:

- Extend axis mapping characterization to directional modifiers so ADR-0011’s axis mapping domain is covered across more than just completeness.

Changes in this loop:

- Added a new test to `tests/test_axis_mapping.py`:
  - `test_directional_axis_recipe_token_uses_value_to_key_map`:
    - Parses the first real entry from `GPT/lists/directionalModifier.talon-list`.
    - Asserts that `_axis_recipe_token("directional", <description>)` maps the long description back to the short key using the underlying value→key map.
    - Asserts that `_axis_recipe_token("directional", <key>)` returns the key unchanged.
- Ran the focused test module:
  - `python -m unittest tests.test_axis_mapping -q`
  - All tests passed, confirming that the new directional characterization aligns with existing behaviour.

Impact on ADR-0011 objectives:

- Strengthens branch-level coverage for the axis mapping façade described in ADR-0011 by:
  - Extending explicit characterization beyond completeness to a second axis family (directional).
  - Making it safer to refactor or tune directional modifier semantics while preserving Concordance guardrails.
- Improves evidence (`C_a`) that `_axis_recipe_token` behaves correctly across different axis maps, not just for completeness.

Follow-ups (not completed in this loop):

- Optionally mirror this pattern for other axes (scope, method, style) if future churn or Concordance hotspots suggest they need similar focused coverage.
- Use `tests/test_axis_mapping.py` as a primary guardrail for any changes that:
  - Adjust axis list entries or descriptions in `GPT/lists/*Modifier.talon-list`.
  - Modify `_axis_recipe_token` or `_read_axis_value_to_key_map` implementations.

---

## 2025-12-03 – Loop 4 – ADR-0011 status and cross-ADR relationship

Focus area:

- Align ADR-0011’s text with the current repo reality and neighbouring ADRs, making its governance and incremental scope explicit.

Changes in this loop:

- Updated `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` by adding a **“Current Status and Relationship to Other ADRs”** section that:
  - Notes that many of the refactor steps ADR-0011 describes are already implemented via ADR-005, ADR-006, ADR-007, and ADR-010:
    - `lib/staticPromptConfig.py` façade helpers (`get_static_prompt_profile`, `get_static_prompt_axes`) and their consumers (`modelPrompt`, GUIs, GPT docs).
    - Axis mapping helpers in `lib/talonSettings.py` and their characterization tests.
  - Clarifies that ADR-0011 primarily:
    - Codifies static prompt and axis mapping boundaries and Concordance goals.
    - Acts as a coordination/guidance ADR on how to evolve these domains safely.
    - Leaves only incremental, evidence-driven work (for example, tightening invariants) as in-repo scope.

Impact on ADR-0011 objectives:

- Reduces ambiguity about what remains to do for this ADR in this repo:
  - Prevents future loops from redundantly re-implementing work already covered by ADR-005/006/007/010.
  - Makes it clear that ADR-0011 governs how we continue to apply and extend the existing façades/tests, rather than introducing a separate, parallel refactor track.
- Improves cross-ADR Concordance by explicitly anchoring ADR-0011 to earlier ADRs that established the static prompt and axis mapping behaviour.

Follow-ups (not completed in this loop):

- When ADR-0011’s remaining in-repo tasks are close to exhausted (for example, after any targeted invariant or façade refinements), consider a future loop that:
  - Summarises remaining `B_a` and `C_a` for ADR-0011.
  - Proposes whether to move its `Status` from `Proposed` toward a more terminal state for this repo, backed by a green test and Concordance snapshot.

---

## 2025-12-03 – Loop 5 – Scope/method/style axis mapping characterization

Focus area:

- Extend ADR-0011’s axis mapping characterization beyond completeness and directional axes to cover scope, method, and style mappings.

Changes in this loop:

- Updated `tests/test_axis_mapping.py` to add:
  - A small helper `_assert_axis_round_trip(filename, axis)` that:
    - Reads the first real `key: description` entry from the given Talon list in `GPT/lists`.
    - Asserts that `_axis_recipe_token(axis, <description>)` maps the description back to the short key.
    - Asserts that `_axis_recipe_token(axis, <key>)` returns the key unchanged.
  - Three new tests:
    - `test_scope_axis_recipe_token_uses_value_to_key_map`.
    - `test_method_axis_recipe_token_uses_value_to_key_map`.
    - `test_style_axis_recipe_token_uses_value_to_key_map`.
    - Each uses `_assert_axis_round_trip` against the corresponding `*Modifier.talon-list`.
- Ran the focused tests:
  - `python -m unittest tests.test_axis_mapping -q`
  - All 11 tests passed.

Impact on ADR-0011 objectives:

- Completes the initial characterization of `_axis_recipe_token` across all axis families (completeness, scope, method, style, directional) using real Talon list data.
- Further strengthens evidence (`C_a`) for the axis mapping façade so future refactors or tuning can be driven by Concordance signals without risking silent drift in recipe tokens.

Follow-ups (not completed in this loop):

- Treat `tests/test_axis_mapping.py` as the primary guardrail for any changes to:
  - Axis modifier lists (`GPT/lists/*Modifier.talon-list`).
  - `_read_axis_value_to_key_map`, `_read_axis_default_from_list`, or `_axis_recipe_token`.
- In a future loop, consider a short “Current status” summary in ADR-0011 that explicitly calls out axis mapping characterization as effectively satisfied for this repo, pending Concordance-driven refinements.

---

## 2025-12-03 – Loop 6 – Axis mapping façade helper in talonSettings

Focus area:

- Introduce an explicit internal façade over axis value→key maps in `lib/talonSettings.py`, without changing `_axis_recipe_token`’s behaviour.

Changes in this loop:

- Updated `lib/talonSettings.py` to:
  - Add a consolidated `_AXIS_VALUE_TO_KEY_MAPS` dict that holds the per-axis value→key maps for:
    - `completeness`, `scope`, `method`, `style`, and `directional`.
  - Add `_axis_value_to_key_map_for(axis: str) -> dict[str, str]`:
    - Returns the value→key map for a given axis, or `{}` when the axis is unknown.
  - Refactor `_axis_recipe_token` to:
    - Use `_axis_value_to_key_map_for(axis)` instead of an inline axis→map dict literal.
    - Preserve its existing behaviour when `raw_value` is empty or when the axis has no map.
- Ran focused tests:
  - `python -m unittest tests.test_axis_mapping tests.test_talon_settings_model_prompt -q`
  - All 23 tests passed, confirming that the façade refactor preserved observable behaviour.

Impact on ADR-0011 objectives:

- Creates an explicit, reusable axis mapping surface inside `talonSettings`, aligning with ADR-0011’s intent to have a clear axis mapping domain façade:
  - Future callers (or refactors) can depend on `_axis_value_to_key_map_for` rather than duplicating axis→map wiring.
  - `_axis_recipe_token` now clearly delegates to a single, named mapping surface.
- Keeps scope bounded to `talonSettings` for this loop, paving the way for later GUIs/orchestrators to reuse the same façade if Concordance and churn data justify it.

Follow-ups (not completed in this loop):

- In a future loop, consider:
  - Using `_axis_value_to_key_map_for` from other modules that need access to the same mapping semantics, instead of re-reading Talon list files.
  - Documenting this façade briefly in ADR-0011 (or leaving it implicit if it remains an internal detail) once we see whether additional callers adopt it.

---

## 2025-12-03 – Loop 7 – Reconcile ADR-0011 Salient Tasks with repo state

Focus area:

- Update ADR-0011’s “Salient Tasks” section so it accurately reflects what is already implemented and what remains in-repo.

Changes in this loop:

- Edited the **Salient Tasks** section of `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to:
  - Mark static prompt tasks that are already satisfied in this repo as such, pointing to ADR-0011 work-log Loops 1–2 and existing helpers/tests:
    - Characterisation tests for static prompt invariants.
    - The `staticPromptConfig` façade API and its use by GPT docs and Talon settings.
  - Mark axis mapping tasks that are already satisfied or partially satisfied:
    - Branch-level coverage for axis mapping and `modelPrompt` is satisfied by `tests/test_axis_mapping.py` and `tests/test_talon_settings_model_prompt.py`.
    - The axis mapping façade is partially satisfied via `_axis_value_to_key_map_for` and the consolidated maps in `lib/talonSettings.py`.
  - Refine the “migrate GUIs and GPT orchestration to consume the façade” task to an evaluation step:
    - Make it clear that further adoption should be driven by Concordance hotspots and real duplication, not by a blanket requirement.

Impact on ADR-0011 objectives:

- Brings the ADR’s task list into alignment with the actual code and tests, reducing ambiguity about what remains:
  - Prevents future loops from redoing already-completed characterization and façade work.
  - Focuses remaining effort on incremental, evidence-driven refinements and Concordance follow-up.
- Improves readability for future maintainers by clearly distinguishing between completed, partially satisfied, and still-open tasks.

Follow-ups (not completed in this loop):

- Once additional Concordance/heatmap runs have been performed after these slices, consider a dedicated status loop to:
  - Summarise remaining `B_a` for ADR-0011.
  - Decide whether to adjust its `Status` or further narrow its in-repo scope.

---

## 2025-12-03 – Loop 8 – Concordance hotspot snapshot for ADR-0011 domains

Focus area:

- Re-run the churn × complexity heatmap for ADR-0011-related files and capture a Concordance-oriented snapshot, using it to validate that our work is focused on genuine hotspots.

Changes in this loop:

- Re-ran the churn tools:
  - `python scripts/tools/churn-git-log-stat.py`
  - `python scripts/tools/line-churn-heatmap.py`
  - Confirmed output at:
    - `tmp/churn-scan/git-log-stat.txt`
    - `tmp/churn-scan/line-hotspots.json`
- Extracted node-level hotspots for ADR-0011 focus files:
  - `lib/staticPromptConfig.py`
  - `lib/talonSettings.py`
  - `tests/test_axis_mapping.py`
  - `tests/test_static_prompt_config.py`
- Observed (sorted by score):
  - `lib/staticPromptConfig.py::StaticPromptProfile` remains the top hotspot in this set (high churn and coordination).
  - `lib/talonSettings.py::_read_axis_value_to_key_map`, `modelPrompt`, `_axis_recipe_token`, and `_axis_value_to_key_map_for` all appear with high coordination and non-trivial churn.
  - Newly strengthened test nodes (`tests/test_axis_mapping.py::*`, `tests/test_static_prompt_config.py::*`) now show up as coordinated churn alongside their corresponding implementation hotspots.

Impact on ADR-0011 objectives:

- Confirms that:
  - ADR-0011’s chosen focus areas (static prompt config, axis mapping, and their tests) still align with the highest Concordance hotspots in this domain.
  - Recent loops have **increased evidence (`C_a`)** around these hotspots by adding/strengthening tests, without reducing visibility or artificially suppressing churn.
- Provides a concrete snapshot that future loops can compare against when deciding whether to:
  - Further narrow scope (for example, by extracting sub-domains), or
  - Declare certain objectives effectively satisfied for this repo.

Follow-ups (not completed in this loop):

- In a later status loop, compare this snapshot with a future one after any additional refactors land, to check whether:
  - Scores for static prompt and axis mapping nodes fall due to better factoring and test coverage.
  - Test nodes remain present as healthy coordination hubs, rather than disappearing from the heatmap.

---

## 2025-12-03 – Loop 9 – Wire Concordance snapshot into ADR-0011 tasks

Focus area:

- Update ADR-0011’s Concordance follow-up tasks so they explicitly reference the new baseline snapshot captured in Loop 8.

Changes in this loop:

- Edited the **Concordance follow-up** bullets in `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to:
  - Note that an initial churn × complexity baseline for ADR-0011 domains was captured on 2025-12-03 (see this work-log, Loop 8).
  - Clarify that future runs of `scripts/tools/line-churn-heatmap.py` should be compared against this baseline when deciding whether structural/test changes are genuinely lowering Concordance scores.

Impact on ADR-0011 objectives:

- Tightens the link between ADR-0011’s high-level Concordance intent and the concrete tooling already in use:
  - Makes it clear that Concordance follow-up is about **trend over time** relative to a specific snapshot, rather than ad-hoc one-off scans.
  - Helps future loops avoid re-running scans without anchoring them to an explicit baseline and ADR goals.

Follow-ups (not completed in this loop):

- After additional refactor/test slices land, run another targeted Concordance loop that:
  - Re-runs the heatmap.
  - Compares key hotspot scores to the 2025-12-03 baseline.
  - Records any meaningful improvements or regressions in this work-log before making changes to ADR-0011’s status.

---

## 2025-12-03 – Loop 10 – Current status snapshot for ADR-0011

Focus area:

- Summarise ADR-0011’s in-repo state (`B_a` and `C_a`) so future loops know what is effectively done vs. still open.

Changes in this loop:

- Reviewed ADR-0011 and its work-log to classify tasks:
  - **Static prompt domain (largely satisfied in this repo):**
    - Domain façade: `lib/staticPromptConfig.py` exposes `get_static_prompt_profile` and `get_static_prompt_axes`, and is consumed by `modelPrompt`, GUIs, and GPT docs.
    - Tests: `tests/test_static_prompt_config.py`, `tests/test_static_prompt_docs.py`, and pattern/GUI tests cover profile/axes behaviour and config↔list↔pattern alignment.
  - **Axis mapping and model prompt domain (largely satisfied with room for incremental refinement):**
    - Mapping surface: `_read_axis_value_to_key_map`, `_read_axis_default_from_list`, `_axis_recipe_token`, and `_axis_value_to_key_map_for` in `lib/talonSettings.py`.
    - Tests: `tests/test_axis_mapping.py` and `tests/test_talon_settings_model_prompt.py` characterise all axis families (completeness/scope/method/style/directional), mapping behaviour, and key `modelPrompt` flows.
  - **Concordance follow-up:**
    - Baseline: a churn × complexity snapshot for ADR-0011 domains was captured on 2025-12-03 (Loop 8).
    - ADR text and tasks now explicitly reference this baseline and describe how to use future snapshots.

Current snapshot of `B_a` (remaining in-repo objectives):

- There is no standing refactor backlog for ADR-0011 in this repo.
- Future work under this ADR is reactive:
  - When new static prompts or axis behaviours are introduced, they should follow the existing façades and tests described in the ADR (see Maintainer Usage Guidance and Quick Checklist).
  - When Concordance snapshots, incidents, or tests reveal new problems in these domains, future loops should plan and execute targeted slices based on the **Future Revisit Triggers** and guidance captured here.

Current snapshot of `C_a` (evidence/guardrails):

- Strong, branch-focused tests are now in place around:
  - Static prompt profiles/axes, config↔list↔pattern alignment, and static prompt docs.
  - Axis mappings and `modelPrompt` behaviour for all axis families.
- The ADR and work-log explicitly tie these tests and tools to Concordance goals, reducing the risk that future changes weaken guardrails to “improve” scores.

Follow-ups (not completed in this loop):

- After one or two more substantial slices (if needed), run a dedicated status loop to:
  - Decide whether ADR-0011’s status should move beyond “Proposed” for this repo.
  - Base that decision on: green tests, a follow-up Concordance snapshot, and a clear, small set of remaining in-repo tasks (if any).

---

## 2025-12-03 – Loop 11 – Gating test run for ADR-0011 domains

Focus area:

- Run the key static prompt and axis mapping test modules together as a light gating check for ADR-0011’s domains.

Changes in this loop:

- Executed the most relevant test modules for ADR-0011:
  - `python -m unittest tests.test_static_prompt_config tests.test_static_prompt_docs tests.test_axis_mapping tests.test_talon_settings_model_prompt -q`
  - Result: 32 tests, all passing.

Impact on ADR-0011 objectives:

- Confirms that, at this point in time:
  - Static prompt façade helpers and invariants (config ↔ list ↔ patterns ↔ docs) are green.
  - Axis mapping helpers and `modelPrompt` behaviour (including all axis families) are green.
- Provides a lightweight gating snapshot that can be referenced when considering any change to ADR-0011’s status or remaining scope.

Follow-ups (not completed in this loop):

- When a future follow-up Concordance snapshot is available, combine it with a similar targeted test run to support a status decision for ADR-0011 in this repo.

---

## 2025-12-03 – Loop 12 – Mark ADR-0011 as Accepted for this repo

Focus area:

- Update ADR-0011’s status now that its core refactor/test objectives are in place and a baseline Concordance snapshot plus gating tests have been run.

Changes in this loop:

- Updated `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md`:
  - Changed `Status: Proposed` → `Status: Accepted` while keeping the date and owners unchanged.
- Relied on prior loops as justification:
  - Static prompt and axis mapping façades and tests are implemented and green (Loops 1–7, 11).
  - A Concordance baseline for these domains has been captured (Loop 8) and wired into the ADR’s follow-up tasks (Loop 9).

Impact on ADR-0011 objectives:

- Signals that, for this repo:
  - ADR-0011’s main structural and test-related decisions are in effect.
  - Remaining work is incremental and guided by Concordance signals, not foundational refactors.
- Aligns ADR-0011’s status with ADR-010 and others that are already actively governing behaviour in this codebase.

Follow-ups (not completed in this loop):

- Future loops that meaningfully change static prompt or axis mapping behaviour should:
  - Treat ADR-0011 as an active constraint and update its work-log when they refine its domains.
  - Optionally record new Concordance snapshots when changes are large enough to plausibly affect hotspot scores.

---

## 2025-12-03 – Loop 13 – Maintainer usage guidance in ADR-0011

Focus area:

- Add concise maintainer-facing guidance to ADR-0011 on how to use the static prompt and axis-mapping domains when evolving the system.

Changes in this loop:

- Updated `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` with a new **“Maintainer Usage Guidance”** section that:
  - Explains how to add or update static prompts:
    - Edit `StaticPromptProfile` entries in `lib/staticPromptConfig.py`.
    - Keep `GPT/lists/staticPrompt.talon-list` and `_build_static_prompt_docs` in sync.
  - Explains how to add or update axis modifiers:
    - Edit `GPT/lists/*Modifier.talon-list`.
    - Reuse `_read_axis_value_to_key_map` / `_axis_value_to_key_map_for` in `talonSettings` instead of re-parsing lists elsewhere.
    - Extend `tests/test_axis_mapping.py` and `tests/test_talon_settings_model_prompt.py` when adding new values or branches.
  - Recommends a minimal gating set and Concordance workflow for refactors that touch these domains (run the key tests and, when changes are large, compare a fresh heatmap to the 2025-12-03 baseline).

Impact on ADR-0011 objectives:

- Makes ADR-0011 more directly actionable for maintainers by:
  - Turning its domain and Concordance framing into concrete “how to change things safely” instructions.
  - Reducing the risk that future contributors bypass the façades or tests when evolving static prompts or axis mappings.

Follow-ups (not completed in this loop):

- As new patterns or tools emerge (for example, additional Concordance helpers), future loops can extend this guidance section to point at those without changing ADR-0011’s core decisions.

---

## 2025-12-03 – Loop 14 – Execution status section in ADR-0011

Focus area:

- Add an explicit execution-status summary to ADR-0011 so maintainers can quickly see how fully it has been applied in this repo.

Changes in this loop:

- Updated `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to add an **“Execution Status (This Repo)”** section that:
  - States that the static prompt and axis mapping façades are implemented and in active use.
  - Notes that focused tests and a Concordance baseline are in place.
  - Clarifies that remaining work is incremental and Concordance-driven, and points readers to this work-log for loop-by-loop history.

Impact on ADR-0011 objectives:

- Makes it easier for future contributors to:
  - See at a glance that ADR-0011 is Accepted and substantially executed in this repo.
  - Understand that new work should refine or extend existing domains/tests rather than reintroduce parallel patterns.

Follow-ups (not completed in this loop):

- If future, larger refactors significantly change the domains ADR-0011 describes, update this execution-status section and work-log together so they continue to match reality.

---

## 2025-12-03 – Loop 15 – Future revisit triggers for ADR-0011

Focus area:

- Define clear conditions under which maintainers should revisit or extend ADR-0011.

Changes in this loop:

- Updated `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to add a **“Future Revisit Triggers”** section that:
  - Lists concrete triggers, including:
    - New Concordance hotspots around static prompts or axis mapping that fall outside the current domains.
    - Major prompt taxonomy changes (large additions/restructures of static prompts or axis modifiers).
    - New orchestration surfaces coordinating these concerns without using the existing façades.
    - Evidence of test blind spots (regressions or near-misses) in these domains.
  - Describes how to respond when a trigger fires:
    - Start from the ADR-0011 work-log and latest Concordance snapshot.
    - Decide whether to add focused tests/invariants or extend/split domains (possibly via a successor ADR).

Impact on ADR-0011 objectives:

- Clarifies when ADR-0011 should be actively revisited versus treated as background governance, helping avoid unnecessary churn while still keeping an explicit path for evolution.

Follow-ups (not completed in this loop):

- When any trigger is hit in practice, future loops should:
  - Record the event and chosen response in this work-log.
  - Update ADR-0011 or introduce a successor ADR if the domains themselves need to change.

---

## 2025-12-03 – Loop 16 – Quick maintainer checklist in ADR-0011

Focus area:

- Provide a concise, repeatable checklist in ADR-0011 for changes touching static prompts, axis modifiers, or `modelPrompt`.

Changes in this loop:

- Updated `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to add a **“Quick Checklist (Before Merging Changes)”** under Maintainer Usage Guidance:
  - Enumerates pre-merge checks for:
    - Updating `StaticPromptProfile` entries in `lib/staticPromptConfig.py`.
    - Keeping `GPT/lists/staticPrompt.talon-list` and docs aligned with profiles.
    - Reusing `_axis_value_to_key_map_for` / `_read_axis_value_to_key_map` instead of adding ad-hoc mappings.
    - Running/extending the four key gating test modules.
    - Considering a fresh heatmap run versus the 2025-12-03 baseline for larger refactors.

Impact on ADR-0011 objectives:

- Gives maintainers a low-friction way to apply ADR-0011’s guidance during everyday changes, improving the odds that façades, tests, and Concordance checks stay in sync without re-reading the whole ADR each time.

Follow-ups (not completed in this loop):

- As workflows evolve, future loops can refine this checklist (for example, referencing additional tooling or CI checks) while keeping it short and focused.

---

## 2025-12-03 – Loop 17 – Cross-link ADR-0011 from ADR-010

Focus area:

- Make the relationship between ADR-010 (umbrella Concordance improvements) and ADR-0011 (static prompt and axis mapping domains) explicit.

Changes in this loop:

- Updated `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md` to add a small **Related ADRs** section near the top:
  - Links to `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md`.
  - Explains that ADR-0011 narrows in on the static prompt and axis mapping domains identified as hotspots in ADR-010 and codifies their boundaries, façades, and tests.

Impact on ADR-0011 objectives:

- Clarifies that ADR-0011 is a focused companion to ADR-010 rather than a competing or unrelated decision:
  - Helps maintainers discover ADR-0011 when working from the broader Concordance/churn context in ADR-010.
  - Reinforces ADR-0011’s role as the home for static prompt and axis mapping domain boundaries.

Follow-ups (not completed in this loop):

- If future ADRs build on ADR-0011 for other Concordance domains, cross-link them in a similar fashion so the ADR chain remains discoverable from the top-level Concordance work.

---

## 2025-12-03 – Loop 18 – Add newcomer summary to ADR-0011

Focus area:

- Provide a short, newcomer-friendly summary at the top of ADR-0011 so contributors can quickly understand what it governs.

Changes in this loop:

- Updated `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to add a **“Summary (For New Contributors)”** section near the top that:
  - Briefly describes the two domains ADR-0011 governs (static prompts, and axis mapping/modelPrompt).
  - States the high-level goals (make domains explicit, align contracts/tests, and improve Concordance through genuine structural changes).

Impact on ADR-0011 objectives:

- Lowers the activation energy for new contributors to discover and respect ADR-0011 when working on static prompts or axis mappings, without needing to read the full document immediately.

Follow-ups (not completed in this loop):

- If ADR-0011’s scope or domains expand in future, update this summary in tandem so it stays accurate and focused.

---

## 2025-12-03 – Loop 19 – Key files and tests index in ADR-0011

Focus area:

- Add a concise index of the main files and tests governed by ADR-0011.

Changes in this loop:

- Updated `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to include a **“Key Files and Tests (This Repo)”** section listing:
  - Static prompt domain code files (`lib/staticPromptConfig.py`, `GPT/lists/staticPrompt.talon-list`, and the static prompt sections of `GPT/gpt.py`).
  - Axis mapping and `modelPrompt` code (`lib/talonSettings.py`).
  - The four core test modules that serve as guardrails for these domains.

Impact on ADR-0011 objectives:

- Gives maintainers and new contributors a quick starting map of where ADR-0011 applies, reducing the chance of missing an important file or test when making related changes.

Follow-ups (not completed in this loop):

- If new key entrypoints or tests are added for these domains, future loops should update this index so it continues to reflect the real coordination surface.

---

## 2025-12-03 – Loop 20 – Cross-reference ADR-010 from ADR-0011 summary

Focus area:

- Make ADR-0011’s dependency on and relationship to ADR-010 explicit for new contributors.

Changes in this loop:

- Updated the **Summary (For New Contributors)** section of `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to:
  - Add a short “Related ADRs” bullet linking to `docs/adr/010-concordance-churn-complexity-code-quality-improvements.md`.
  - Clarify that ADR-010 is the earlier, broader Concordance/churn ADR that first identified these domains as hotspots and motivated ADR-0011.

Impact on ADR-0011 objectives:

- Helps newcomers orient themselves in the ADR chain:
  - They can start from ADR-0011 for concrete domain boundaries and tests.
  - They can jump to ADR-010 when they need the broader Concordance context and other hotspots.

Follow-ups (not completed in this loop):

- If future Concordance ADRs build further on ADR-0011, consider adding them to this related-ADRs list so the navigation path stays coherent.

---

## 2025-12-03 – Loop 21 – Clarify ADR-0011 out-of-scope areas

Focus area:

- Make explicit which domains and behaviours are *not* governed by ADR-0011 in this repo.

Changes in this loop:

- Updated `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to add an **“Out of Scope (This Repo)”** section that clarifies:
  - GUI layout/behaviour in `modelPatternGUI`, `modelPromptPatternGUI`, and `modelHelpGUI` is out of scope beyond their use of static prompts and axis mappings (governed instead by ADR-006/ADR-007).
  - Non-static-prompt GPT behaviours/tools outside `modelPrompt` are out of scope.
  - Broader Concordance/churn work unrelated to static prompts or axis mappings remains under ADR-010.

Impact on ADR-0011 objectives:

- Tightens ADR-0011’s boundaries by:
  - Reducing ambiguity about where its decisions apply.
  - Helping maintainers avoid over-applying it to unrelated domains.

Follow-ups (not completed in this loop):

- If future ADRs move GUI or broader Concordance responsibilities, update this out-of-scope section to reflect the new domain split.

---

## 2025-12-03 – Loop 22 – Add combined gating test command to ADR-0011

Focus area:

- Make it trivial for maintainers to run the core ADR-0011 gating tests in one shot.

Changes in this loop:

- Updated the **Quick Checklist (Before Merging Changes)** section of `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to include a recommended combined test command:
  - `python -m unittest tests.test_static_prompt_config tests.test_static_prompt_docs tests.test_axis_mapping tests.test_talon_settings_model_prompt -q`

Impact on ADR-0011 objectives:

- Reduces friction for consistently running the key guardrail tests tied to this ADR, making it more likely they are exercised before changes land in these domains.

Follow-ups (not completed in this loop):

- If CI gains a dedicated job or script for these tests, consider updating the ADR to reference that entrypoint alongside or instead of the raw command.

---

## 2025-12-03 – Loop 25 – Ongoing obligations snapshot

Focus area:

- Make explicit, in one place, that ADR-0011’s remaining work in this repo is now expressed as guidance for future changes rather than a standing backlog.

Changes in this loop:

- Synced ADR-0011’s main document and this work-log around remaining objectives:
  - The main ADR summarises current execution status and provides guidance (via Maintainer Usage Guidance, Quick Checklist, and Future Revisit Triggers) for future changes.
  - The `B_a` snapshot in this work-log now states that there is no standing refactor backlog; future work is reactive and should use that guidance when relevant.

Impact on ADR-0011 objectives:

- Clarifies that, as of 2025-12-03:
  - There is no standing, unfulfilled refactor backlog for ADR-0011 in this repo.
  - Future work under ADR-0011 will be driven by new changes, Concordance snapshots, or incidents that hit the revisit triggers, and should follow the ADR’s guidance rather than a fixed backlog.

Follow-ups (not completed in this loop):

- When a future trigger fires (for example, a new hotspot or a significant static-prompt/axis-mapping change), start from the **Ongoing Obligations** and **Future Revisit Triggers** sections plus this work-log to plan the next loop.


---

## 2025-12-03 – Loop 23 – Example change flows in ADR-0011

Focus area:

- Add concrete example workflows to ADR-0011 so maintainers can see how to apply its guidance step by step.

Changes in this loop:

- Updated the **Maintainer Usage Guidance** section of `docs/adr/0011-concordance-static-prompt-axis-mapping-domain-boundaries.md` to include an **“Example Change Flows”** subsection with two worked examples:
  - Adding a new static prompt with an axis profile (profile entry, Talon list token, and running gating tests).
  - Adding a new axis modifier value (updating the relevant `*Modifier.talon-list`, extending `tests/test_axis_mapping.py` where needed, and running gating tests plus an optional churn snapshot).

Impact on ADR-0011 objectives:

- Makes the ADR more operational by showing how its domains, tests, and Concordance tooling fit together in realistic change workflows, rather than only listing principles and checklists.

Follow-ups (not completed in this loop):

- Future loops can add further examples (for example, a small refactor of `modelPrompt`) if new, common workflows emerge that would benefit from a documented path.

---

## 2025-12-03 – Loop 24 – Cross-link ADR-0011 from ADR-006/ADR-007

Focus area:

- Make ADR-0011 more discoverable from neighbouring static-prompt/GUI ADRs (ADR-006 and ADR-007).

Changes in this loop:

- Updated related ADR references:
  - `docs/adr/006-pattern-picker-and-recap.md` now points to ADR-0011 as the home for static prompt and axis-mapping domain boundaries that underpin `modelPrompt`, settings, and GUIs.
  - `docs/adr/007-static-prompt-consolidation.md` now lists ADR-0011 in its Related ADRs list, alongside ADR-005 and ADR-006.

Impact on ADR-0011 objectives:

- Strengthens the ADR chain around static prompts and axis mappings:
  - Contributors reading ADR-006/ADR-007 for GUI/pattern/static-prompt decisions can easily discover ADR-0011 when domain boundaries or mappings are involved.

Follow-ups (not completed in this loop):

- If future ADRs refine static-prompt or axis-mapping behaviour further, ensure they also link back to ADR-0011 so it remains the central domain-boundary reference.
