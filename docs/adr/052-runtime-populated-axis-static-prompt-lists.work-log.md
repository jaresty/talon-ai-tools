# 2025-03-09 – Loop 1 (kind: behaviour)
- Focus: ADR 052 – catalog-driven axis/static prompt lists and runtime Talon seeding.
- Changes:
  - Seeded axis/static prompt Talon lists from the Python catalog with a safe ctx guard so grammar vocab reflects `axisConfig`/`staticPromptConfig` without editing list files (`lib/talonSettings.py`).
  - Made catalog helpers fall back to SSOT tokens when Talon list files are absent, keeping overrides optional (`lib/axisCatalog.py`, `lib/staticPromptConfig.py`).
  - Updated axis/static prompt guardrail tests to consume catalog tokens instead of list files, aligning drift checks with the new SSOT (`_tests/test_form_channel_lists.py`, `_tests/test_axis_registry_drift.py`, `_tests/test_axis_overlap_alignment.py`, `_tests/test_static_prompt_docs.py`, `_tests/test_axis_mapping.py`, `_tests/test_model_pattern_gui.py`).
- Tests: `python3 -m pytest _tests/test_axis_mapping.py _tests/test_axis_registry_drift.py _tests/test_static_prompt_docs.py _tests/test_form_channel_lists.py _tests/test_axis_overlap_alignment.py _tests/test_model_pattern_gui.py::ModelPatternGUITests::test_all_pattern_static_prompts_exist_in_config_and_list` (pass).
- Removal test: Reverting would drop runtime list seeding and catalog fallbacks, making axis/static prompt vocab depend on list files again and failing the updated guardrail tests above.

# 2025-03-09 – Loop 2 (kind: behaviour)
- Focus: ADR 052 – document catalog-as-SSOT for static prompts/axes.
- Changes: Updated `GPT/readme.md` to state that static prompt/axis vocab is sourced from the Python catalog and populated into Talon lists at runtime, clarifying the generated/optional nature of `staticPrompt.talon-list`.
- Tests: Not run (doc-only change).
- Removal test: Reverting would reinstate the old wording implying list files are the source of truth.

# 2025-03-09 – Loop 3 (kind: behaviour)
- Focus: ADR 052 – help surfaces respect catalog-sourced vocab (including unprofiled prompts/axis overrides).
- Changes:
  - Help domain now builds its search index from the catalog’s static prompt tokens (profiled + talon_list_tokens) and axis list tokens when available, falling back to file reads only when the catalog is absent (`lib/helpDomain.py`).
- Tests: `python3 -m pytest _tests/test_help_domain.py` (pass).
- Removal test: Reverting would make help rely on list-file parsing again and ignore catalog-provided vocab/overrides.

# 2025-03-09 – Loop 4 (kind: guardrail/tests)
- Focus: ADR 052 – ensure static prompt catalog still exposes vocab when Talon list files are absent.
- Changes:
  - Added guardrail test asserting `static_prompt_catalog` falls back to config tokens if `staticPrompt.talon-list` is missing (`_tests/test_static_prompt_docs.py`).
- Tests: `python3 -m pytest _tests/test_static_prompt_docs.py` (pass).
- Removal test: Reverting would drop the fallback guardrail, letting missing list files hide static prompt tokens from docs/catalog.

# 2025-03-09 – Loop 5 (kind: guardrail/tests)
- Focus: ADR 052 – ensure axis catalog falls back to SSOT tokens when axis list files are absent.
- Changes: Added guardrail verifying `axis_catalog` still surfaces axis tokens (matching `axisConfig`) when the lists directory is empty (`_tests/test_axis_registry_drift.py`).
- Tests: `python3 -m pytest _tests/test_axis_registry_drift.py` (pass).
- Removal test: Reverting would drop the fallback guardrail and allow missing/empty list files to hide axis vocab in the catalog.

# 2025-03-09 – Loop 6 (kind: guardrail/tests)
- Focus: ADR 052 – confirm help index prefers catalog vocab over missing lists.
- Changes: Added a help-domain test that ensures catalog-provided static prompts and axis tokens are used even when list files are empty (`_tests/test_help_domain.py`).
- Tests: `python3 -m pytest _tests/test_help_domain.py` (pass).
- Removal test: Reverting would let help indexing fall back to empty list reads and miss catalog vocab.

# 2025-03-09 – Loop 7 (kind: guardrail/tests)
- Focus: ADR 052 – ensure axis list tokens merge list overrides with SSOT.
- Changes:
  - `axis_catalog.axis_list_tokens` now merges list tokens with SSOT tokens so partial list files can’t drop catalog vocab (`lib/axisCatalog.py`).
  - Added guardrail verifying axis catalog tokens include SSOT entries even when list files are partial (`_tests/test_axis_registry_drift.py`).
- Tests: `python3 -m pytest _tests/test_axis_registry_drift.py` (pass).
- Removal test: Reverting would allow partial list files to hide SSOT tokens and break the guardrail test.

# 2025-03-09 – Loop 8 (kind: guardrail/tests)
- Focus: ADR 052 – prevent partial static prompt lists from hiding catalog vocab.
- Changes:
  - `static_prompt_catalog` now merges list tokens with config tokens so partial list files do not drop SSOT entries (`lib/staticPromptConfig.py`).
  - Added guardrail ensuring catalog talon_list_tokens include config tokens even when the list file is partial (`_tests/test_static_prompt_docs.py`).
- Tests: `python3 -m pytest _tests/test_static_prompt_docs.py` (pass).
- Removal test: Reverting would let partial staticPrompt list files hide profiled prompts and would fail the guardrail test.

# 2025-03-09 – Loop 9 (kind: behaviour)
- Focus: ADR 052 – generate Talon list files from the catalog.
- Changes:
  - Added `scripts/tools/generate_talon_lists.py` to emit axis/static prompt Talon lists from the catalog SSOT.
  - Added CLI guardrail test to ensure the generator writes expected tokens for completeness/static prompts (`_tests/test_generate_talon_lists.py`).
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py` (pass).
- Removal test: Reverting would drop the generator and its guardrail, losing the ability to regenerate list files from the catalog.

# 2025-03-09 – Loop 10 (kind: behaviour)
- Focus: ADR 052 – expose a make target for catalog-driven list generation.
- Changes: Added `talon-lists` Makefile target to regenerate Talon list files from the catalog (`Makefile`).
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py` (pass) — generator still green.
- Removal test: Reverting would remove the make shortcut for regenerating list files from the SSOT.

# 2025-03-09 – Loop 11 (kind: behaviour)
- Focus: ADR 052 – document the catalog-driven list regeneration workflow.
- Changes: Updated `CONTRIBUTING.md` to instruct contributors to run `make talon-lists` after axis/static prompt edits so Talon lists stay aligned with the catalog.
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py` (pass) — generator unchanged.
- Removal test: Reverting would drop guidance on regenerating lists, increasing drift risk when contributors edit axes/static prompts.

# 2025-03-09 – Loop 12 (kind: behaviour)
- Focus: ADR 052 – regenerate Talon lists from catalog SSOT.
- Changes: Ran `python3 scripts/tools/generate_talon_lists.py --out-dir GPT/lists` to refresh axis/static prompt `.talon-list` files from the catalog.
- Tests: Not run (generation-only sync).
- Removal test: Reverting would restore stale list files and drift from the catalog.

# 2025-03-09 – Loop 13 (kind: guardrail/tests)
- Focus: ADR 052 – ensure generated lists match committed lists.
- Changes: Added parity test to assert that running `generate_talon_lists.py` reproduces the committed `GPT/lists/*.talon-list` files (`_tests/test_generate_talon_lists.py`).
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py` (pass).
- Removal test: Reverting would drop the guardrail, letting committed lists drift from the catalog or generator output.

# 2025-03-09 – Loop 14 (kind: guardrail/tests)
- Focus: ADR 052 – detect drift between catalog-generated lists and committed lists via CLI.
- Changes:
  - `scripts/tools/axis-catalog-validate.py` now compares committed Talon lists against generator output to flag missing/extra tokens.
  - `axis-catalog-validate` guardrail tests still pass (`_tests/test_axis_catalog_validate.py`).
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would remove the generator parity check from the CLI, allowing list drift to go unnoticed outside the dedicated unit test.

# 2025-03-09 – Loop 15 (kind: behaviour)
- Focus: ADR 052 – include list generation guardrail in axis guardrail target.
- Changes:
  - Added `_tests/test_generate_talon_lists.py` to the `axis-guardrails-test` Makefile target so list generation parity runs with other axis guardrails (`Makefile`).
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would stop the axis guardrail target from exercising list generation parity, reducing drift detection.

# 2025-03-09 – Loop 16 (kind: behaviour)
- Focus: ADR 052 – surface catalog-driven list regeneration in developer docs.
- Changes: Added a note in `readme.md` (Development section) pointing to `make talon-lists` for regenerating Talon lists from the catalog.
- Tests: Not run (doc-only change).
- Removal test: Reverting would drop the dev hint and make catalog/list regeneration less discoverable.

# 2025-03-09 – Loop 17 (kind: behaviour)
- Focus: ADR 052 – reinforce catalog-driven list regeneration in GPT docs.
- Changes: Added a maintainer note to `GPT/readme.md` directing contributors to run `make talon-lists` after axis/static prompt changes so tracked Talon lists stay in sync.
- Tests: Not run (doc-only change).
- Removal test: Reverting would remove the GPT-specific hint, making regeneration less discoverable for GPT area contributors.

# 2025-03-09 – Loop 18 (kind: behaviour)
- Focus: ADR 052 – clarify file-backed user-extensible lists in contributor docs.
- Changes: Updated `CONTRIBUTING.md` to note that catalog-driven list regeneration should not overwrite user-extensible lists (customPrompt, modelDestination, persona/intent lists), which remain file-backed.
- Tests: Not run (doc-only change).
- Removal test: Reverting would drop contributor guidance about which lists remain user-editable vs catalog-generated.

# 2025-03-09 – Loop 19 (kind: behaviour)
- Focus: ADR 052 – surface guardrail targets in developer docs.
- Changes: Updated the root `readme.md` (Development section) to mention `make axis-guardrails-test` alongside `axis-guardrails`/`talon-lists`.
- Tests: Not run (doc-only change).
- Removal test: Reverting would hide the full guardrail target from the quickstart dev docs.

# 2025-03-09 – Loop 20 (kind: behaviour/guardrail)
- Focus: ADR 052 – add drift-only check mode to Talon list generator.
- Changes:
  - Added `--check` to `scripts/tools/generate_talon_lists.py` to compare catalog output against an existing lists directory without overwriting files.
  - Added guardrail tests covering check-mode pass/fail scenarios (`_tests/test_generate_talon_lists.py`).
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py` (pass).
- Removal test: Reverting would drop the check-only guardrail, reducing drift detection outside the CLI.

# 2025-03-09 – Loop 21 (kind: behaviour)
- Focus: ADR 052 – add a drift-only make target for Talon lists.
- Changes: Added `talon-lists-check` Makefile target (uses generator `--check`) and documented it in `readme.md` alongside other guardrail targets.
- Tests: Not run (wiring/doc change); generator tests already cover `--check`.
- Removal test: Reverting would remove the make shortcut for drift-only checks, making catalog/list drift harder to spot.

# 2025-03-09 – Loop 22 (kind: behaviour)
- Focus: ADR 052 – fold list-drift check into the axis guardrail target.
- Changes: Updated `axis-guardrails` Make target to run `talon-lists-check` alongside catalog validation and cheat sheet generation (`Makefile`).
- Tests: `python3 scripts/tools/axis-catalog-validate.py` (pass).
- Removal test: Reverting would drop the list-drift check from the main guardrail target, reducing coverage when running guardrails.

# 2025-03-09 – Loop 23 (kind: guardrail/tests)
- Focus: ADR 052 – allow axis-catalog-validate to target custom list dirs.
- Changes:
  - Added `--lists-dir` arg to `scripts/tools/axis-catalog-validate.py` to validate arbitrary Talon list directories.
  - Added a drift-detection test invoking the CLI with a temporary lists directory (`_tests/test_axis_catalog_validate.py`).
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would remove CLI coverage for drifted custom list dirs and drop the new guardrail test.

# 2025-03-09 – Loop 24 (kind: behaviour)
- Focus: ADR 052 – document custom list-dir validation and update CLI help.
- Changes:
  - Updated axis-catalog-validate docstring to mention `--lists-dir` usage.
  - Added a note to the root `readme.md` (Development section) about using `axis-catalog-validate --lists-dir` for ad-hoc Talon list validation.
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would drop the doc/help note about validating alternate lists, reducing discoverability of the guardrail.

# 2025-03-09 – Loop 25 (kind: behaviour)
- Focus: ADR 052 – add CI-friendly guardrail target and docs.
- Changes:
  - Added `axis-guardrails-ci` Make target (catalog validation + list drift check) for faster guardrails.
  - Documented the CI target alongside existing guardrail commands in `readme.md`.
- Tests: Not run (wiring/doc change); guardrail scripts already exercised in earlier loops.
- Removal test: Reverting would drop the CI-friendly guardrail entry point and its mention in docs.

# 2025-03-09 – Loop 26 (kind: behaviour)
- Focus: ADR 052 – mention guardrail targets in contributor docs.
- Changes: Updated `CONTRIBUTING.md` to direct maintainers to `axis-guardrails-ci` / `axis-guardrails-test` after axis/static prompt changes.
- Tests: Not run (doc-only change).
- Removal test: Reverting would remove contributor-facing guidance on which guardrail targets to run.

# 2025-03-09 – Loop 27 (kind: behaviour)
- Focus: ADR 052 – improve axis-catalog-validate usability.
- Changes:
  - Added `--verbose` flag to `scripts/tools/axis-catalog-validate.py` to print a short summary on success.
  - Ran the validator in verbose mode to confirm behaviour.
- Tests: `python3 scripts/tools/axis-catalog-validate.py --verbose` (pass).
- Removal test: Reverting would drop the verbose summary option and its usage confirmation.

# 2025-03-09 – Loop 29 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail for the validator's verbose mode.
- Changes: Added a test ensuring `axis-catalog-validate --verbose` prints a summary (`_tests/test_axis_catalog_validate.py`).
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would drop the verbose-output guardrail and could mask silent failures in verbose mode.

# 2025-03-09 – Loop 30 (kind: behaviour)
- Focus: ADR 052 – make guardrail target output verbose validation by default.
- Changes: Updated `axis-catalog-validate` Make target to run with `--verbose` for clearer guardrail logs (`Makefile`).
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would reduce guardrail visibility when running the Make target.

# 2025-03-09 – Loop 31 (kind: behaviour)
- Focus: ADR 052 – capture guardrail/ops usage in the ADR doc.
- Changes: Added an Ops/guardrails section to ADR 052 summarising `make talon-lists`, `talon-lists-check`, `axis-guardrails(-ci/-test)`, and the ad-hoc validator usage.
- Tests: Not run (doc-only change).
- Removal test: Reverting would remove the in-ADR pointer to the guardrail workflow.

# 2025-03-09 – Loop 28 (kind: guardrail/tests)
- Focus: ADR 052 – mark guardrail targets as phony to avoid stale builds.
- Changes: Added `.PHONY` declarations for guardrail/list targets in `Makefile` to ensure they always run (`axis-guardrails`, `axis-guardrails-ci`, `axis-guardrails-test`, `talon-lists`, `talon-lists-check`, etc.).
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would allow Make to skip guardrail/list targets based on stale timestamps.

# 2025-03-09 – Loop 32 (kind: behaviour)
- Focus: ADR 052 – add CI guardrail convenience target.
- Changes: Added `ci-guardrails` Make target to run the CI-friendly guardrails plus key axis/list parity tests (`Makefile`).
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would remove the convenience target for running CI guardrails locally.

# 2025-03-09 – Loop 33 (kind: behaviour)
- Focus: ADR 052 – document CI guardrail target in developer docs.
- Changes: Updated `readme.md` (Development section) to mention `ci-guardrails` alongside other guardrail commands.
- Tests: Not run (doc-only change).
- Removal test: Reverting would remove the CI guardrail pointer from the dev docs.

# 2025-03-09 – Loop 34 (kind: behaviour)
- Focus: ADR 052 – add a simple guardrails alias.
- Changes: Added `guardrails` Make target as an alias to the CI guardrail flow and documented it in the Development section of the root README.
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py _tests/test_axis_catalog_validate.py` (pass) to confirm guardrail scripts remain green.
- Removal test: Reverting would drop the alias and its doc mention, making the guardrail entry point slightly less discoverable.

# 2025-03-09 – Loop 34 (kind: guardrail/tests)
- Focus: ADR 052 – keep guardrail targets always-run.
- Changes: Added `ci-guardrails` to the Makefile `.PHONY` list so the target never skips due to stale timestamps.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would allow `ci-guardrails` to be skipped by `make` when timestamps mislead it.

# 2025-03-09 – Loop 35 (kind: behaviour)
- Focus: ADR 052 – surface guardrails alias in contributor docs.
- Changes: Updated `CONTRIBUTING.md` to mention the `guardrails` Make target as a one-command way to run CI guardrails and parity checks.
- Tests: Not run (doc-only change).
- Removal test: Reverting would drop the contributor-facing hint for the guardrails alias.

# 2025-03-09 – Loop 36 (kind: behaviour)
- Focus: ADR 052 – add a Makefile help target for guardrails.
- Changes: Added `help` target to Makefile to list guardrail-related commands and ensured it’s phony.
- Tests: Not run (Makefile-only change); guardrail tests already cover underlying scripts.
- Removal test: Reverting would remove the guardrail quick-reference from the Makefile.

# 2025-03-09 – Loop 37 (kind: behaviour)
- Focus: ADR 052 – note the Makefile help in dev docs.
- Changes: Updated `readme.md` (Development section) to mention `make help` lists guardrail targets.
- Tests: Not run (doc-only change).
- Removal test: Reverting would drop the guardrail help pointer from the README.

# 2025-03-09 – Loop 38 (kind: behaviour)
- Focus: ADR 052 – encourage guardrail runs before PRs.
- Changes: Updated the root `readme.md` (Development section) to recommend running `make guardrails` (or the full `axis-guardrails-test`) before PRs to catch catalog/list drift.
- Tests: Not run (doc-only change).
- Removal test: Reverting would remove the PR guardrail reminder from dev docs.

# 2025-03-09 – Loop 39 (kind: behaviour)
- Focus: ADR 052 – add a CI-friendly guardrail runner script.
- Changes: Added `scripts/tools/run_guardrails_ci.sh` to run the guardrail target (`make guardrails`) as a single CI step.
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py _tests/test_axis_catalog_validate.py` (pass) to ensure guardrail scripts remain green.
- Removal test: Reverting would drop the CI helper script, requiring manual command wiring in pipelines.

# 2025-03-09 – Loop 41 (kind: guardrail/tests)
- Focus: ADR 052 – ensure the CI guardrail script is exercised.
- Changes: Added `_tests/test_run_guardrails_ci.py` to execute `scripts/tools/run_guardrails_ci.sh` and assert catalog validation output.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop coverage for the CI helper script and allow it to drift silently.

# 2025-03-09 – Loop 42 (kind: guardrail/tests)
- Focus: ADR 052 – allow CI guardrail script to target fast guardrails.
- Changes:
  - `run_guardrails_ci.sh` now honors `GUARDRAILS_TARGET` (default `guardrails`) so CI/tests can run the lighter `axis-guardrails-ci` target.
  - Updated `_tests/test_run_guardrails_ci.py` to set `GUARDRAILS_TARGET` for faster validation in tests.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would remove the flexibility/coverage for the CI helper and could reintroduce slow guardrail runs in tests.

# 2025-03-09 – Loop 44 (kind: behaviour/tests)
- Focus: ADR 052 – support arg override for the CI guardrail script.
- Changes:
  - `run_guardrails_ci.sh` now accepts an optional target argument (in addition to `GUARDRAILS_TARGET` env) and uses it as the guardrail target.
  - Updated `_tests/test_run_guardrails_ci.py` to pass the target argument instead of env.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop the arg-based override and its guardrail coverage.

# 2025-03-09 – Loop 40 (kind: behaviour)
- Focus: ADR 052 – surface CI guardrail script in dev docs.
- Changes: Updated `readme.md` to mention `scripts/tools/run_guardrails_ci.sh` as the CI entry point for guardrails.
- Tests: Not run (doc-only change).
- Removal test: Reverting would hide the CI guardrail script from dev docs.

# 2025-03-09 – Loop 43 (kind: behaviour/tests)
- Focus: ADR 052 – surface CI helper in Makefile help and simplify CI target override.
- Changes:
  - `run_guardrails_ci.sh` now accepts an optional target argument (in addition to env) for selecting guardrail tiers.
  - Added the CI helper to the Makefile help output for discoverability.
  - Updated `_tests/test_run_guardrails_ci.py` to pass the target arg.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop the helper reference and the arg-based override coverage.

# 2025-03-09 – Loop 46 (kind: guardrail/tests)
- Focus: ADR 052 – ensure full guardrail target exercises CI helper.
- Changes: Added `_tests/test_run_guardrails_ci.py` to the `axis-guardrails-test` Make target so the full guardrail suite covers the CI helper script.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_generate_talon_lists.py _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop CI helper coverage from the full guardrail target.

# 2025-03-09 – Loop 47 (kind: behaviour)
- Focus: ADR 052 – document CI guardrail entrypoint for contributors.
- Changes: Added a note to `CONTRIBUTING.md` describing `scripts/tools/run_guardrails_ci.sh` as the CI entrypoint for guardrails (supports target override).
- Tests: Not run (doc-only change).
- Removal test: Reverting would hide the CI guardrail script from contributor guidance.

# 2025-03-09 – Loop 48 (kind: behaviour)
- Focus: ADR 052 – clarify CI guardrail usage in dev docs.
- Changes: Updated `readme.md` to mention the optional target argument for `run_guardrails_ci.sh` (default `guardrails`, pass `axis-guardrails-ci` for the fast tier).
- Tests: Not run (doc-only change).
- Removal test: Reverting would remove the target-arg hint from dev docs.

# 2025-03-09 – Loop 50 (kind: guardrail/tests)
- Focus: ADR 052 – ensure guardrail targets stay discoverable via Make help.
- Changes: Added `_tests/test_make_help_guardrails.py` to assert `make help` lists guardrail targets and the CI helper reference.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop the discoverability guardrail for the Make help output.

# 2025-03-09 – Loop 51 (kind: guardrail/tests)
- Focus: ADR 052 – include Make help guardrail in full guardrail target.
- Changes: Added `_tests/test_make_help_guardrails.py` to `axis-guardrails-test` so the full guardrail suite covers Make help discoverability.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop the Make help guardrail from the full guardrail target.

# 2025-03-09 – Loop 52 (kind: guardrail/tests)
- Focus: ADR 052 – include Make help guardrail in CI guardrails.
- Changes: Added `_tests/test_make_help_guardrails.py` to `ci-guardrails` so the CI guardrail target also covers Make help discoverability.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py _tests/test_run_guardrails_ci.py _tests/test_generate_talon_lists.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would drop the Make help guardrail from the CI target.

# 2025-03-09 – Loop 49 (kind: behaviour)
- Focus: ADR 052 – add CI guardrail snippet to dev docs.
- Changes: Added a short CI example to `readme.md` showing how to invoke `run_guardrails_ci.sh axis-guardrails-ci`.
- Tests: Not run (doc-only change).
- Removal test: Reverting would remove the CI usage hint for the guardrail helper.

# 2025-03-09 – Loop 53 (kind: guardrail/tests)
- Focus: ADR 052 – surface usage/help for the CI guardrail helper.
- Changes:
  - `run_guardrails_ci.sh` now supports `-h/--help` with usage examples and exits before running Make.
  - Added `_tests/test_run_guardrails_ci.py::test_run_guardrails_ci_help` to guardrail the help text.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would hide the helper usage guidance and drop the guardrail covering it.

# 2025-03-09 – Loop 54 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail the env-based target override for the CI helper.
- Changes: Added `_tests/test_run_guardrails_ci.py::test_run_guardrails_ci_env_override` to ensure `GUARDRAILS_TARGET` drives the Make target when no arg is given.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring env overrides stay functional.

# 2025-03-09 – Loop 55 (kind: guardrail/tests)
- Focus: ADR 052 – make the CI guardrail helper output the selected target for clarity.
- Changes:
  - `run_guardrails_ci.sh` now echoes the resolved target before running Make.
  - Updated `_tests/test_run_guardrails_ci.py` to assert the target echo for both arg and env override paths.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would remove the target echo and its guardrail, reducing observability in CI logs.

# 2025-03-09 – Loop 56 (kind: guardrail/tests)
- Focus: ADR 052 – ensure CI helper fails loudly for invalid targets.
- Changes: Added `_tests/test_run_guardrails_ci.py::test_run_guardrails_ci_invalid_target` to assert non-zero exit, target echo, and a missing-target hint from make.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop coverage for the failure path, risking silent CI misconfigurations.

# 2025-03-09 – Loop 57 (kind: guardrail/tests)
- Focus: ADR 052 – keep guardrail helper discoverable and documented with the new help flag.
- Changes:
  - `make help` entry for `run_guardrails_ci.sh` now advertises `--help`.
  - Guardrail test `_tests/test_make_help_guardrails.py` updated to assert the `--help` hint.
  - `readme.md` guardrail section updated to mention `run_guardrails_ci.sh --help` and the `--help|target` usage.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would hide the `--help` discoverability and drop the guardrail that ensures it stays visible.

# 2025-03-09 – Loop 58 (kind: guardrail/tests)
- Focus: ADR 052 – cover `talon-lists-check` discoverability in `make help`.
- Changes: `_tests/test_make_help_guardrails.py` now asserts `talon-lists-check` appears in the help output (guardrail for list drift check discoverability).
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring the drift-only list check stays visible in `make help`.

# 2025-03-09 – Loop 59 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail discoverability of CI and full guardrail targets.
- Changes: `_tests/test_make_help_guardrails.py` now asserts `ci-guardrails` and `guardrails` appear in `make help` output alongside other guardrail entries.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop coverage ensuring the consolidated guardrail targets stay visible in help.

# 2025-03-09 – Loop 60 (kind: behaviour/docs)
- Focus: ADR 052 – simplify and update guardrail documentation for SSOT lists.
- Changes:
  - Deduplicated and refreshed the guardrail guidance in `readme.md` (single consolidated bullet with current targets and `run_guardrails_ci.sh --help` hint).
  - Updated `CONTRIBUTING.md` guardrail section to list the current targets (`axis-guardrails`, `axis-guardrails-ci`, `axis-guardrails-test`, `ci-guardrails`, `guardrails`) plus `talon-lists`/`talon-lists-check` and helper usage `[--help|target]`.
- Tests: Not run (docs-only change).
- Removal test: Reverting would restore duplicated/outdated guardrail guidance, reducing clarity on SSOT list workflows and CI entrypoints.

# 2025-03-09 – Loop 61 (kind: behaviour)
- Focus: ADR 052 – align ADR text with catalog-only axis/static lists and catalog-first guardrails.
- Changes: Updated `docs/adr/052-runtime-populated-axis-static-prompt-lists.md` implementation/ops/follow-ups to state no tracked axis/static .talon-lists, catalog validation defaults to `--skip-list-files`, list checks are opt-in with `--no-skip-list-files --lists-dir`, and generator use is optional for local exports/drift checks.
- Tests: Not run (ADR text-only change).
- Removal test: Reverting would reintroduce instructions implying tracked list files or mandatory list validation, conflicting with the catalog-only implementation and guardrail defaults.

# 2025-03-09 – Loop 62 (kind: behaviour)
- Focus: ADR 052 – keep generated Talon lists untracked and clarify optional helper usage.
- Changes:
  - Added `GPT/lists/*.talon-list` to `.gitignore` so optional local exports from `generate_talon_lists.py` stay untracked.
  - Updated `Makefile` help text to describe `talon-lists`/`talon-lists-check` as optional, untracked local helpers (catalog SSOT).
- Tests: Not run (config/help-only change).
- Removal test: Reverting would allow generated axis/static prompt list files to appear as untracked/accidental commits and would mislead users that talon-lists targets manage tracked artefacts.

# 2025-03-09 – Loop 63 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail that generated Talon lists stay untracked.
- Changes:
  - Added `_tests/test_gitignore_talon_lists.py` to assert `.gitignore` ignores `GPT/lists/*.talon-list`.
  - Wired the new guardrail into `axis-guardrails-test` and `ci-guardrails` targets in `Makefile`.
- Tests: `python3 -m pytest _tests/test_gitignore_talon_lists.py` (pass).
- Removal test: Reverting would drop the .gitignore guardrail and stop guardrail suites from catching accidental reintroduction/tracking of generated axis/static prompt list files.

# 2025-03-09 – Loop 64 (kind: behaviour)
- Focus: ADR 052 – align contributor guidance with catalog-only, untracked axis/static lists.
- Changes: Updated `CONTRIBUTING.md` to state axis/static prompt .talon-lists are untracked and only generated ad hoc for local debugging (`make talon-lists`/`talon-lists-check`), removing instructions to regenerate tracked files.
- Tests: Not run (doc-only change).
- Removal test: Reverting would reintroduce guidance to regenerate tracked axis/static prompt list files, contradicting the catalog-only SSOT and risking accidental commits of generated lists.

# 2025-03-09 – Loop 65 (kind: behaviour)
- Focus: ADR 052 – align guardrail help text with catalog-only validation.
- Changes: Updated `Makefile` help entry for `axis-catalog-validate` to describe catalog validation with list checks opt-in (`--lists-dir/--no-skip-list-files`), removing the implication of tracked Talon lists.
- Tests: Not run (Makefile help-only change).
- Removal test: Reverting would reintroduce misleading help suggesting validation depends on tracked list files, conflicting with the catalog-only SSOT and default `--skip-list-files` behaviour.

# 2025-03-09 – Loop 66 (kind: guardrail/tests)
- Focus: ADR 052 – lock README to the “untracked axis/static Talon lists” contract.
- Changes: Added a guardrail assertion in `_tests/test_readme_guardrails_docs.py` that README explicitly states axis/static prompt Talon lists are untracked (catalog-only, optional local generation).
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would allow README to drift back to implying tracked Talon list files, conflicting with the catalog-only SSOT and other guardrails.

# 2025-03-09 – Loop 67 (kind: guardrail/tests)
- Focus: ADR 052 – enforce GPT README aligns with catalog-only, untracked lists.
- Changes:
  - Added `_tests/test_gpt_readme_axis_lists.py` to assert GPT README mentions the catalog SSOT, notes axis/static Talon lists are “no longer tracked,” and references the optional `make talon-lists` helper.
  - Included the new guardrail in `axis-guardrails-test` and `ci-guardrails` targets (`Makefile`).
- Tests: `python3 -m pytest _tests/test_gpt_readme_axis_lists.py _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop coverage that GPT README reflects the catalog-only contract and could let docs imply tracked axis/static list files again.

# 2025-03-09 – Loop 68 (kind: guardrail/tests)
- Focus: ADR 052 – document CLI defaults for catalog-only validation.
- Changes:
  - Added `_tests/test_axis_catalog_validate_help.py` to guardrail `axis-catalog-validate --help` output, ensuring it mentions catalog-only defaults (`--lists-dir` default none, `--skip-list-files`/`--no-skip-list-files`).
  - Included the new guardrail in `axis-guardrails-test` and `ci-guardrails` (`Makefile`).
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_help.py` (pass).
- Removal test: Reverting would drop coverage of the CLI help text and could let `axis-catalog-validate` drift away from the catalog-only/defaults contract without detection.

# 2025-03-09 – Loop 69 (kind: guardrail/tests)
- Focus: ADR 052 – keep GPT README aligned with catalog-only guardrails and helpers.
- Changes:
  - Updated `GPT/readme.md` help blurb to mention catalog-only validation (`--skip-list-files` default), opting into list checks (`--lists-dir … --no-skip-list-files`), and the optional `talon-lists-check` helper alongside `make talon-lists`.
  - Expanded `_tests/test_gpt_readme_axis_lists.py` to assert the README mentions `talon-lists-check` and the skip/no-skip flags.
- Tests: `python3 -m pytest _tests/test_gpt_readme_axis_lists.py` (pass).
- Removal test: Reverting would let the GPT README omit the catalog-only validation defaults and drift-check helper, weakening the documentation guardrails for the catalog-as-SSOT contract.

# 2025-03-09 – Loop 70 (kind: guardrail/tests)
- Focus: ADR 052 – make guardrail help explicitly mention skip/no-skip list checks.
- Changes: Updated `_tests/test_make_help_guardrails.py` to assert `make help`’s axis-catalog-validate entry mentions skip/no-skip list checks for catalog-only validation.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring `make help` surfaces the skip/no-skip behavior, risking confusion about catalog-only defaults.

# 2025-03-09 – Loop 71 (kind: behaviour)
- Focus: ADR 052 – clarify catalog-only defaults in the validator help text.
- Changes: Updated `scripts/tools/axis-catalog-validate.py` docstring/usage to state list-file validation is opt-in (catalog-only default) and reran the help guardrail.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_help.py` (pass).
- Removal test: Reverting would make the validator usage text imply list-file validation is mandatory, diverging from the catalog-only flow and its help guardrail.

# 2025-03-09 – Loop 72 (kind: guardrail/tests)
- Focus: ADR 052 – ensure guardrail targets never depend on tracked GPT/lists.
- Changes: Strengthened `_tests/test_make_guardrail_skip_list_files.py` to scan axis guardrail target lines for any `GPT/lists` references (while allowing optional `talon-lists` helpers elsewhere), preventing reintroduction of tracked list dependencies in guardrails.
- Tests: `python3 -m pytest _tests/test_make_guardrail_skip_list_files.py` (pass).
- Removal test: Reverting would drop the guardrail that axis guardrail targets stay independent of tracked GPT/lists paths, risking a regression back to file-backed list assumptions.

# 2025-03-09 – Loop 73 (kind: guardrail/tests)
- Focus: ADR 052 – enforce contributor docs reflect untracked axis/static lists.
- Changes: Updated `_tests/test_contributing_guardrails_docs.py` to assert `CONTRIBUTING.md` explicitly states axis/static prompt Talon lists are untracked.
- Tests: `python3 -m pytest _tests/test_contributing_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring contributor docs keep the catalog-only/untracked axis list contract visible.

# 2025-03-09 – Loop 74 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail default validator behavior stays catalog-only.
- Changes:
  - Added `_tests/test_axis_catalog_validate_defaults.py` to assert the default `axis-catalog-validate --verbose` run reports `lists_dir=<skipped>` / `lists_validation=skipped` (catalog-only).
  - Added the test to `axis-guardrails-test` and `ci-guardrails` targets in `Makefile`.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_defaults.py` (pass).
- Removal test: Reverting would drop coverage ensuring the validator defaults remain catalog-only, risking accidental reintroduction of on-disk list validation by default.

# 2025-03-09 – Loop 75 (kind: guardrail/tests)
- Focus: ADR 052 – keep Make help messaging aligned with optional/untracked Talon lists.
- Changes: Tightened `_tests/test_make_help_guardrails.py` to assert `make help` includes the “optional” wording for `talon-lists` and `talon-lists-check`, reinforcing that axis/static Talon lists are untracked helpers.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop coverage of the optional/untracked messaging, risking confusion about the status of generated Talon lists in guardrail help.

# 2025-03-09 – Loop 76 (kind: guardrail/tests)
- Focus: ADR 052 – keep README guardrail guidance explicit about optional, untracked Talon list helpers.
- Changes: Updated `readme.md` guardrail blurb to call out `talon-lists`/`talon-lists-check` as optional/untracked helpers; reran README guardrail test.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would weaken the README’s catalog-only messaging by implying Talon lists are tracked/mandatory instead of optional helpers.

# 2025-03-09 – Loop 77 (kind: guardrail/tests)
- Focus: ADR 052 – keep guardrail targets independent of talon-lists generation.
- Changes:
  - Added `_tests/test_guardrail_targets_no_talon_lists.py` to assert guardrail targets (`axis-guardrails*`, `ci-guardrails`) do not depend on `talon-lists`.
  - Wired the new guardrail into `axis-guardrails-test` and `ci-guardrails` in `Makefile`.
- Tests: `python3 -m pytest _tests/test_guardrail_targets_no_talon_lists.py _tests/test_make_guardrail_skip_list_files.py` (pass).
- Removal test: Reverting would drop coverage preventing guardrail targets from regressing to tracked list generation, undermining the catalog-only contract.

# 2025-03-09 – Loop 78 (kind: guardrail/tests)
- Focus: ADR 052 – surface catalog-only guardrail defaults in the CI helper.
- Changes:
  - Updated `scripts/tools/run_guardrails_ci.sh` usage text to note catalog-only defaults (no talon-lists generation).
  - Extended `_tests/test_run_guardrails_ci.py` help guardrail to assert the catalog-only note is present.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop the catalog-only note from the CI helper and its guardrail, risking confusion about whether guardrails generate Talon lists by default.

# 2025-03-09 – Loop 79 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail the CI helper’s default target to stay on catalog-only guardrails.
- Changes:
  - Added `_tests/test_run_guardrails_ci_default_target.py` to assert `run_guardrails_ci.sh` defaults to the `guardrails` target when no arg/env is set.
  - Included the new test in `axis-guardrails-test` and `ci-guardrails` targets (`Makefile`).
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci_default_target.py _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop coverage ensuring the CI helper continues to default to the guardrails target, risking silent changes to its default behavior.

# 2025-03-09 – Loop 80 (kind: guardrail/tests)
- Focus: ADR 052 – keep CI helper help text highlighting the fast catalog-only target.
- Changes: Extended `_tests/test_run_guardrails_ci.py` help assertion to require the `axis-guardrails-ci` example remains in the helper usage output.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop coverage ensuring the CI helper continues to advertise the fast catalog-only target in its help text, risking discoverability drift.

# 2025-03-09 – Loop 81 (kind: guardrail/tests)
- Focus: ADR 052 – clarify list-check enforcement requires an explicit lists_dir.
- Changes:
  - Updated `scripts/tools/axis-catalog-validate.py` to fail fast when `--no-skip-list-files` is used without `--lists-dir`, surfacing a clear error instead of an attribute error.
  - Added a guardrail test in `_tests/test_axis_catalog_validate_lists_dir.py` to cover the missing `--lists-dir` error path.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would reintroduce a crashy code path when forcing list checks without a lists directory and drop the guardrail for that failure mode.

# 2025-03-09 – Loop 82 (kind: guardrail/tests)
- Focus: ADR 052 – clarify contributor guidance for enforced list checks.
- Changes: Updated `CONTRIBUTING.md` to state that `--no-skip-list-files` must be paired with `--lists-dir` when validating Talon list files.
- Tests: `python3 -m pytest _tests/test_contributing_guardrails_docs.py` (pass).
- Removal test: Reverting would remove explicit contributor guidance on pairing `--no-skip-list-files` with `--lists-dir`, increasing the risk of misusing list validation in catalog-only environments.

# 2025-03-09 – Loop 83 (kind: guardrail/tests)
- Focus: ADR 052 – ensure README spells out the `--lists-dir` requirement when enforcing list checks.
- Changes: Updated `readme.md` guardrail blurb to say `--no-skip-list-files` must be paired with `--lists-dir` when validating Talon list files; reran README guardrail test.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the README note about pairing `--no-skip-list-files` with `--lists-dir`, weakening guidance for ad-hoc list validation.

# 2025-03-09 – Loop 84 (kind: guardrail/tests)
- Focus: ADR 052 – ensure GPT README explains lists-dir requirement when enforcing list checks.
- Changes:
  - Updated `GPT/readme.md` to state that `--no-skip-list-files` must be paired with `--lists-dir` when validating Talon list files.
  - Extended `_tests/test_gpt_readme_axis_lists.py` to guardrail the lists-dir mention.
- Tests: `python3 -m pytest _tests/test_gpt_readme_axis_lists.py` (pass).
- Removal test: Reverting would let GPT README omit the lists-dir requirement for enforced list checks, weakening documentation alignment with the catalog-only guardrails.

# 2025-03-09 – Loop 85 (kind: guardrail/tests)
- Focus: ADR 052 – make validator help explicit about lists-dir requirement when enforcing list checks.
- Changes:
  - Updated `scripts/tools/axis-catalog-validate.py` usage/help to state `--no-skip-list-files` requires `--lists-dir`.
  - Extended `_tests/test_axis_catalog_validate_help.py` to guardrail the lists-dir requirement in `--help` output.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_help.py` (pass).
- Removal test: Reverting would drop the clear help text and guardrail about pairing `--no-skip-list-files` with `--lists-dir`, risking misuse of enforced list checks in catalog-only environments.

# 2025-03-09 – Loop 86 (kind: behaviour)
- Focus: ADR 052 – document lists-dir requirement when enforcing list checks.
- Changes: Updated ADR 052 (Ops/guardrails) to state explicitly that `--no-skip-list-files` requires `--lists-dir` when validating Talon lists; catalog-only remains the default.
- Tests: Not run (ADR text-only change; guardrails already cover this behaviour in CLI/tests/docs).
- Removal test: Reverting would make the ADR omit the lists-dir requirement for enforced list checks, diverging from the implemented guardrails and validator behaviour.

# 2025-03-09 – Loop 87 (kind: behaviour)
- Focus: ADR 052 – surface lists-dir requirement in guardrail help.
- Changes: Updated `Makefile` help entry for `axis-catalog-validate` to state that enforcing list checks (`--no-skip-list-files`) requires `--lists-dir`; reran guardrail help test.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop the lists-dir requirement from Make help, weakening guidance for running list checks in catalog-only environments.

# 2025-03-09 – Loop 61 (kind: guardrail/tests)
- Focus: ADR 052 – ensure CI helper help text documents env/default target.
- Changes: `_tests/test_run_guardrails_ci.py::test_run_guardrails_ci_help` now asserts the help output mentions `GUARDRAILS_TARGET`, guarding against losing the env/default hint.
- Tests: `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop the guardrail for documenting env/default target selection in the helper usage.

# 2025-03-09 – Loop 62 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail README discoverability of guardrail entrypoints.
- Changes:
  - Added `_tests/test_readme_guardrails_docs.py` to assert README mentions key guardrail targets and the `run_guardrails_ci.sh` helper.
  - Included the new doc guardrail test in `axis-guardrails-test` and `ci-guardrails` Make targets.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py _tests/test_make_help_guardrails.py _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring README surfaces guardrail/CI entrypoints, risking discoverability drift.

# 2025-03-09 – Loop 63 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail CONTRIBUTING guardrail docs.
- Changes:
  - Added `_tests/test_contributing_guardrails_docs.py` to assert `CONTRIBUTING.md` mentions guardrail targets, list commands, and the CI helper.
  - Wired the new doc guardrail into `axis-guardrails-test` and `ci-guardrails` Make targets.
- Tests: `python3 -m pytest _tests/test_contributing_guardrails_docs.py _tests/test_readme_guardrails_docs.py _tests/test_make_help_guardrails.py _tests/test_run_guardrails_ci.py` (pass).
- Removal test: Reverting would drop coverage that keeps CONTRIBUTING guardrail guidance aligned and discoverable.

# 2025-03-09 – Loop 64 (kind: guardrail/tests)
- Focus: ADR 052 – ensure README guardrail docs mention CI guardrail target.
- Changes: `_tests/test_readme_guardrails_docs.py` now asserts `ci-guardrails` appears in the README guardrail section.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the guardrail that keeps the README aligned with the CI guardrail entrypoint.

# 2025-03-09 – Loop 65 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail README mention of the guardrails alias target.
- Changes: `_tests/test_readme_guardrails_docs.py` now asserts the README mentions the `guardrails` alias in the guardrail section.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop coverage that keeps the README aligned with the guardrails alias entrypoint.

# 2025-03-09 – Loop 66 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail README helper usage flags.
- Changes: `_tests/test_readme_guardrails_docs.py` now asserts the README documents `run_guardrails_ci.sh` usage flags (`[--help|target]`) to keep helper guidance intact.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop coverage ensuring the README keeps the helper usage flags visible.

# 2025-03-09 – Loop 67 (kind: guardrail/tests)
- Focus: ADR 052 – keep Make help listing core guardrail primitives.
- Changes:
  - `make help` now surfaces `axis-catalog-validate` and `axis-cheatsheet`.
  - `_tests/test_make_help_guardrails.py` asserts both appear alongside other guardrail targets.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would hide the catalog validation/cheatsheet targets from help and drop the guardrail ensuring their discoverability.

# 2025-03-09 – Loop 68 (kind: guardrail/tests)
- Focus: ADR 052 – ensure README mentions guardrail primitives.
- Changes:
  - Updated `readme.md` guardrail section to mention `axis-catalog-validate` and `axis-cheatsheet` as individual primitives.
  - `_tests/test_readme_guardrails_docs.py` now asserts those primitives appear in the README guardrail section.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the guardrail keeping the README aligned with the guardrail primitives, reducing discoverability of the catalog/cheat sheet commands.

# 2025-03-09 – Loop 69 (kind: guardrail/tests)
- Focus: ADR 052 – keep CONTRIBUTING guardrail guidance aligned with primitives.
- Changes:
  - `CONTRIBUTING.md` guardrail section now lists `axis-catalog-validate` and `axis-cheatsheet` as individual primitives.
  - `_tests/test_contributing_guardrails_docs.py` asserts both primitives appear alongside other guardrail targets.
- Tests: `python3 -m pytest _tests/test_contributing_guardrails_docs.py _tests/test_readme_guardrails_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop coverage keeping CONTRIBUTING aligned with the guardrail primitives and drift towards stale guidance.

# 2025-03-09 – Loop 70 (kind: guardrail/tests)
- Focus: ADR 052 – document guardrails env override in README.
- Changes:
  - README guardrail section now mentions `GUARDRAILS_TARGET` as the env override for the CI helper.
  - `_tests/test_readme_guardrails_docs.py` asserts the README includes `GUARDRAILS_TARGET` to keep the helper docs accurate.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring the README documents the env override for the guardrail helper.

# 2025-03-09 – Loop 71 (kind: guardrail/tests)
- Focus: ADR 052 – keep CONTRIBUTING guardrail helper usage flags documented.
- Changes: `_tests/test_contributing_guardrails_docs.py` now asserts CONTRIBUTING mentions the helper flags `[--help|target]` and `GUARDRAILS_TARGET`.
- Tests: `python3 -m pytest _tests/test_contributing_guardrails_docs.py` (pass).
- Removal test: Reverting would drop coverage ensuring CONTRIBUTING keeps the helper usage flags visible.

# 2025-03-09 – Loop 72 (kind: guardrail/tests)
- Focus: ADR 052 – ensure Make help continues to surface the env override hint.
- Changes: `_tests/test_make_help_guardrails.py` now asserts `GUARDRAILS_TARGET` appears in `make help` output alongside the guardrail helper entry.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring the Make help continues to hint at the env override for guardrails.

# 2025-03-09 – Loop 73 (kind: guardrail/tests)
- Focus: ADR 052 – keep the README’s CI example guarded.
- Changes: `_tests/test_readme_guardrails_docs.py` now asserts the README retains the CI guardrails example snippet invoking `run_guardrails_ci.sh axis-guardrails-ci`.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop coverage for the CI example, risking loss of the documented entrypoint.

# 2025-03-09 – Loop 74 (kind: guardrail/tests)
- Focus: ADR 052 – ensure README documents ad-hoc lists-dir validation.
- Changes: `_tests/test_readme_guardrails_docs.py` now asserts the README mentions `axis-catalog-validate.py --lists-dir` to keep the ad-hoc validation guidance guarded.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring the README continues to document ad-hoc list validation via `--lists-dir`.

# 2025-03-09 – Loop 75 (kind: guardrail/tests)
- Focus: ADR 052 – ensure CONTRIBUTING documents ad-hoc lists-dir validation.
- Changes:
  - Updated `CONTRIBUTING.md` guardrail section to mention `axis-catalog-validate.py --lists-dir` for ad-hoc list validation.
  - `_tests/test_contributing_guardrails_docs.py` now asserts the ad-hoc validation guidance remains present.
- Tests: `python3 -m pytest _tests/test_contributing_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring CONTRIBUTING continues to document ad-hoc list validation.

# 2025-03-09 – Loop 76 (kind: guardrail/tests)
- Focus: ADR 052 – keep README referencing `make help` for guardrail targets.
- Changes: `_tests/test_readme_guardrails_docs.py` now asserts the README mentions `make help` as the guardrail target index.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop coverage ensuring the README continues to point readers to `make help` for guardrail discovery.

# 2025-03-09 – Loop 77 (kind: guardrail/tests)
- Focus: ADR 052 – prevent duplication of the README guardrail overview.
- Changes: `_tests/test_readme_guardrails_docs.py` now asserts the README contains exactly one `Axis catalog guardrails:` entry to guard against accidental duplication.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the guardrail preventing duplicate guardrail overview text in the README.

# 2025-03-09 – Loop 78 (kind: guardrail/tests)
- Focus: ADR 052 – ensure axis-catalog-validate honors custom lists dirs (pass/fail).
- Changes:
  - Added `_tests/test_axis_catalog_validate_lists_dir.py` to assert the validator passes against generated lists and fails with drift when pointing at a custom `--lists-dir`.
  - Included the new test in `axis-guardrails-test` and `ci-guardrails` targets.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop coverage ensuring the validator’s `--lists-dir` flag works for both clean and drifted directories.

# 2025-03-09 – Loop 79 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail verbose summary output for axis-catalog-validate.
- Changes: `_tests/test_axis_catalog_validate_lists_dir.py` now includes a `--verbose` run that asserts the success summary includes counts and lists_dir.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop coverage ensuring the verbose flag continues to emit the expected summary.

# 2025-03-09 – Loop 80 (kind: guardrail/tests)
- Focus: ADR 052 – ensure axis-catalog-validate fails when lists dir is missing.
- Changes: `_tests/test_axis_catalog_validate_lists_dir.py` now asserts a missing/empty `--lists-dir` causes a non-zero exit and surfaces list drift messaging.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop coverage ensuring the validator fails loudly when lists are absent.

# 2025-03-09 – Loop 81 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail CLI help for axis-catalog-validate flags.
- Changes: `_tests/test_axis_catalog_validate_lists_dir.py` now asserts `--help` surfaces `--lists-dir` and `--verbose`.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop coverage ensuring CLI help continues to advertise the key flags.

# 2025-03-09 – Loop 82 (kind: behaviour/tests)
- Focus: ADR 052 – improve validation feedback for missing/invalid lists_dir.
- Changes:
  - `scripts/tools/axis-catalog-validate.py` now emits explicit errors when `--lists-dir` is missing or not a directory, hinting to pass `--lists-dir` correctly.
  - Updated `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_missing_lists_dir_fails` to assert the new messaging.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop clearer feedback for invalid `--lists-dir` usage and its guardrail.

# 2025-03-09 – Loop 83 (kind: behaviour/tests)
- Focus: ADR 052 – make axis-catalog-validate failure output deterministic and counted.
- Changes:
  - `axis-catalog-validate` now reports the error count and sorts drift messages for deterministic output.
  - Updated drift tests in `_tests/test_axis_catalog_validate.py` and `_tests/test_axis_catalog_validate_lists_dir.py` to assert the counted failure banner.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would drop deterministic, counted failure output and its guardrails.

# 2025-03-09 – Loop 84 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail deterministic ordering of catalog validation errors.
- Changes:
  - Added a sorted-output assertion to `_tests/test_axis_catalog_validate_lists_dir.py` to ensure drift messages remain sorted/deterministic.
  - Drift scenario forces both missing and extra tokens to exercise multiple error lines.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop coverage that keeps axis-catalog-validate failure output stable and sorted.

# 2025-03-09 – Loop 85 (kind: behaviour/tests)
- Focus: ADR 052 – explicit error when Talon list files are missing.
- Changes:
  - `axis-catalog-validate` now emits an explicit drift error when a list file is absent in `--lists-dir`.
  - Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_missing_list_files_reported` to assert the missing-file messaging (non-zero exit, file name, lists_dir hint).
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop the explicit missing-file feedback and its guardrail.

# 2025-03-09 – Loop 86 (kind: behaviour/tests)
- Focus: ADR 052 – guard against non-directory lists_dir and crashy failures.
- Changes:
  - `axis-catalog-validate` now pre-validates `--lists-dir` before loading the catalog, emitting counted/sorted errors for missing/not-a-directory cases.
  - Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_lists_dir_not_directory_fails` to assert the new error path without raising uncaught exceptions.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would reintroduce a crash on non-directory `--lists-dir` and drop the guardrail covering it.

# 2025-03-09 – Loop 87 (kind: status/docs)
- Focus: ADR 052 – align decision with “no tracked axis/static prompt lists”.
- Changes: Updated ADR 052 to state we do not keep axis/static prompt .talon-lists on disk (catalog-only runtime population; only user-extensible lists stay file-backed); Ops/Consequences adjusted accordingly.
- Tests: Not run (docs-only change).
- Removal test: Reverting would reintroduce guidance implying tracked axis/static prompt lists are required.

# 2025-03-09 – Loop 88 (kind: behaviour/docs)
- Focus: ADR 052 – shift guardrails to catalog-only (no on-disk list requirement).
- Changes:
  - `axis-catalog-validate` gains `--skip-list-files`; Make targets now run with `--skip-list-files` so guardrails no longer require tracked list files.
  - Updated guardrail docs in README/CONTRIBUTING to note catalog-only guardrails and optional Talon list helpers.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would reintroduce list-file dependencies into guardrails, conflicting with ADR 052’s catalog-only direction.

# 2025-03-09 – Loop 89 (kind: behaviour/tests)
- Focus: ADR 052 – guardrail catalog-only mode when lists are absent.
- Changes:
  - `axis-catalog-validate` help/docs mention `--skip-list-files`.
  - Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_skip_list_files_allows_missing_dir` to ensure `--skip-list-files` succeeds even when `--lists-dir` is absent.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would drop coverage that the catalog-only validation path remains usable without on-disk lists.

# 2025-03-09 – Loop 90 (kind: guardrail/tests)
- Focus: ADR 052 – document catalog-only validation flag in guardrail docs.
- Changes:
  - README/CONTRIBUTING guardrail sections now mention `--skip-list-files` for catalog-only validation.
  - Guardrail doc tests updated to assert the flag is present.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py` (pass).
- Removal test: Reverting would drop coverage that keeps the catalog-only validation flag documented in user guides.

# 2025-03-09 – Loop 91 (kind: behaviour/tests)
- Focus: ADR 052 – align Make help with catalog-only guardrails.
- Changes: Updated Make help text to reflect that axis guardrails skip on-disk list files; validated via `_tests/test_make_help_guardrails.py`.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would reintroduce stale help text implying list drift checks are required for axis guardrails.

# 2025-03-09 – Loop 92 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail that Make guardrails remain catalog-only.
- Changes:
  - Added `_tests/test_make_guardrail_skip_list_files.py` to assert Makefile guardrail targets include `--skip-list-files` for catalog-only validation.
  - Wired the new test into `axis-guardrails-test` and `ci-guardrails`.
- Tests: `python3 -m pytest _tests/test_make_guardrail_skip_list_files.py` (pass).
- Removal test: Reverting would drop coverage ensuring Make guardrail targets stay aligned with the catalog-only contract (no on-disk list dependency).

# 2025-03-09 – Loop 93 (kind: guardrail/tests)
- Focus: ADR 052 – ensure axis-catalog-validate help advertises catalog-only flag.
- Changes: Updated `_tests/test_axis_catalog_validate_lists_dir.py` to assert `--skip-list-files` appears in CLI help output.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop the guardrail that keeps the catalog-only flag visible in CLI help.

# 2025-03-09 – Loop 94 (kind: behaviour/tests)
- Focus: ADR 052 – remove on-disk axis/static prompt lists and align guardrails.
- Changes:
  - Removed tracked axis/static prompt Talon list files from `GPT/lists`.
  - `axis-catalog-validate` now defaults to `--skip-list-files` (with `--no-skip-list-files` to opt in).
  - Guardrail tests updated: Make guardrail targets stay catalog-only (`_tests/test_make_guardrail_skip_list_files.py`), generator parity tests now self-check without repo lists, and CLI help includes the skip flag.
- Tests: `python3 -m pytest _tests/test_generate_talon_lists.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_validate.py _tests/test_make_guardrail_skip_list_files.py` (pass).
- Removal test: Reverting would restore reliance on tracked list artefacts, breaking the catalog-only contract and guardrails.

# 2025-03-09 – Loop 95 (kind: behaviour/tests)
- Focus: ADR 052 – document and guard the catalog-only defaults and opt-in flag.
- Changes:
  - `axis-catalog-validate` help/docs now call out the default `--skip-list-files` and `--no-skip-list-files` opt-in.
  - README/CONTRIBUTING guardrail sections updated to mention `--no-skip-list-files`.
  - Guardrail doc tests updated; Make guardrail skip-list test remains in place.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_make_help_guardrails.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_validate.py _tests/test_generate_talon_lists.py` (pass).
- Removal test: Reverting would drop documentation and guardrails for the catalog-only default and opt-in list validation flag.

# 2025-03-09 – Loop 96 (kind: behaviour/tests)
- Focus: ADR 052 – clarify catalog-only verbose output and flag enforcement for list validation.
- Changes:
  - `axis-catalog-validate` verbose summary now reports `lists_validation=<skipped|validated@path>`.
  - Adjusted list-validation tests to opt in with `--no-skip-list-files` and ensure failure paths are enforced when requested; added robustness for missing list files during drift checks.
  - Documentation updated to mention `--no-skip-list-files` in guardrail sections.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_validate.py _tests/test_generate_talon_lists.py _tests/test_readme_guardrails_docs.py _tests/test_contributing_guardrails_docs.py _tests/test_make_guardrail_skip_list_files.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop the explicit verbose indicator and weaken guardrails around opting into list-file validation.

# 2025-03-09 – Loop 97 (kind: guardrail/tests)
- Focus: ADR 052 – ensure no tracked axis/static prompt list artefacts remain.
- Changes:
  - Added `_tests/test_no_tracked_axis_lists.py` to assert axis/static prompt .talon-lists are absent on disk.
  - Guardrail targets now include the test so catalog-only contract is enforced.
- Tests: `python3 -m pytest _tests/test_no_tracked_axis_lists.py _tests/test_make_guardrail_skip_list_files.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would drop the guardrail preventing reintroduction of tracked axis/static prompt list files.

# 2025-03-09 – Loop 98 (kind: behaviour/docs)
- Focus: ADR 052 – align GPT README with catalog-only lists.
- Changes: Updated `GPT/readme.md` to note axis/static prompt .talon-lists are not tracked and are generated ad hoc with `make talon-lists`.
- Tests: `python3 -m pytest _tests/test_readme_axis_lists.py` (pass).
- Removal test: Reverting would reintroduce stale guidance implying tracked axis/static prompt lists exist.

# 2025-03-09 – Loop 99 (kind: behaviour/docs)
- Focus: ADR 052 – document catalog-only defaults in validator CLI.
- Changes: Updated `scripts/tools/axis-catalog-validate.py` docstring/usage to state the catalog-only default, `--no-skip-list-files` opt-in, and catalog-only environments.
- Tests: Not run (docstring-only).
- Removal test: Reverting would hide the catalog-only default/opt-in guidance from the validator CLI docs.

# 2025-03-09 – Loop 100 (kind: behaviour/tests)
- Focus: ADR 052 – ensure catalog-only axis tokens skip on-disk lists.
- Changes:
  - `axis_list_tokens` now returns SSOT tokens when `lists_dir` is `None` (avoids touching on-disk lists in catalog-only mode).
  - Added `_tests/test_axis_catalog_skip_lists.py` to guard the catalog-only path; included in guardrail targets.
- Tests: `python3 -m pytest _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would reintroduce on-disk list dependence when `lists_dir` is omitted and drop the guardrail covering it.

# 2025-03-09 – Loop 101 (kind: guardrail/tests)
- Focus: ADR 052 – keep catalog-only verbose indicator and guardrail suite intact.
- Changes:
  - Axis catalog validator verbose output now shows `lists_dir=<skipped>` alongside `lists_validation=skipped`.
  - Updated verbose test to assert the skipped indicator.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop the explicit skipped indicator in verbose mode and its guardrail.

# 2025-03-09 – Loop 102 (kind: guardrail/tests)
- Focus: ADR 052 – guardrail static prompt catalog in catalog-only mode.
- Changes:
  - Added `_tests/test_static_prompt_catalog_skip_lists.py` to assert static prompt SSOT tokens are present even when Talon list files are absent.
  - Included the new test in guardrail targets.
- Tests: `python3 -m pytest _tests/test_static_prompt_catalog_skip_lists.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop coverage ensuring static prompt catalog stays intact without on-disk lists.

# 2025-03-09 – Loop 103 (kind: guardrail/tests)
- Focus: ADR 052 – ensure help index uses catalog tokens without list files.
- Changes:
  - Added `_tests/test_help_index_catalog_only.py` to assert help index entries are populated from the catalog when list files are absent.
  - Guardrail targets updated to include the new test.
- Tests: `python3 -m pytest _tests/test_help_index_catalog_only.py _tests/test_axis_catalog_skip_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop coverage ensuring help/index surfaces remain catalog-driven in list-free environments.

# 2025-03-09 – Loop 104 (kind: behaviour/docs)
- Focus: ADR 052 – clarify static prompt catalog SSOT and list-optional stance.
- Changes: Updated `lib/staticPromptConfig.py` comments/docstring to state static prompt lists are optional/auxiliary and merged with SSOT tokens when present.
- Tests: `python3 -m pytest _tests/test_static_prompt_catalog_skip_lists.py` (pass).
- Removal test: Reverting would weaken documentation on the catalog-only contract for static prompts.

# 2025-03-09 – Loop 105 (kind: behaviour/docs)
- Focus: ADR 052 – clarify axis catalog SSOT vs optional lists.
- Changes: Updated `lib/axisCatalog.py` comments/docstring to state axis lists are optional/auxiliary and SSOT when absent.
- Tests: Not run (doc-only).
- Removal test: Reverting would make axis catalog docs imply tracked lists are required.

# 2025-03-09 – Loop 106 (kind: guardrail/tests)
- Focus: ADR 052 – ensure catalog-only path ignores falsy lists_dir.
- Changes:
  - `axis_list_tokens` now skips on-disk list reads when `lists_dir` is falsy (not just None).
  - Added `_tests/test_axis_catalog_skip_lists.py::test_axis_list_tokens_catalog_only_when_lists_dir_empty` to guard the empty/falsy path.
- Tests: `python3 -m pytest _tests/test_axis_catalog_skip_lists.py` (pass).
- Removal test: Reverting would reintroduce an on-disk read when a falsy lists_dir is passed and drop the guardrail covering it.

# 2025-03-09 – Loop 107 (kind: guardrail/tests)
- Focus: ADR 052 – strengthen catalog-only static prompt guarantees.
- Changes: `_tests/test_static_prompt_catalog_skip_lists.py` now asserts talon_list_tokens include all SSOT names and unprofiled_tokens is empty when the list file is absent.
- Tests: `python3 -m pytest _tests/test_static_prompt_catalog_skip_lists.py` (pass).
- Removal test: Reverting would weaken the guardrail ensuring static prompt catalog stays aligned with SSOT when lists are absent.

# 2025-03-09 – Loop 108 (kind: behaviour/tests)
- Focus: ADR 052 – ensure help index stays catalog-only without list files.
- Changes:
  - `help_index` no longer falls back to list reads when a catalog is provided.
  - Added `_tests/test_help_index_catalog_only.py` to assert help index entries come from the catalog and do not require on-disk lists.
- Tests: `python3 -m pytest _tests/test_help_index_catalog_only.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would reintroduce on-disk list dependence for help index and drop the guardrail covering catalog-only mode.

# 2025-03-09 – Loop 109 (kind: behaviour/docs)
- Focus: ADR 052 – reinforce doc guidance that axis/static lists are untracked.
- Changes: Updated `readme.md` guardrail section to explicitly state axis/static prompt .talon-lists are not tracked and are only generated ad hoc if needed.
- Tests: Not run (docs-only change).
- Removal test: Reverting would weaken the catalog-only guidance in the main README.

# 2025-03-09 – Loop 110 (kind: behaviour/tests)
- Focus: ADR 052 – ensure Talon runtime lists are populated from catalog without on-disk lists.
- Changes:
  - `_set_ctx_list` now initialises `ctx.lists` to a dict if missing (catalog-only environments).
  - Added `_tests/test_talon_settings_catalog_lists.py` to assert runtime lists populate from the catalog (staticPrompt and axis modifiers) and include known tokens.
  - Guardrail targets include the new test.
- Tests: `python3 -m pytest _tests/test_talon_settings_catalog_lists.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_help_index_catalog_only.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_axis_catalog_skip_lists.py` (pass).
- Removal test: Reverting would drop catalog-populated runtime lists in environments without pre-seeded `ctx.lists` and remove the guardrail covering it.

# 2025-03-09 – Loop 111 (kind: behaviour/tests)
- Focus: ADR 052 – avoid touching legacy style lists when lists_dir is absent.
- Changes: Axis catalog skips the legacy style list probe unless a lists_dir is provided, keeping catalog-only mode side-effect free.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would reintroduce unnecessary filesystem touches for legacy style lists when running catalog-only.

# 2025-03-09 – Loop 112 (kind: behaviour/tests)
- Focus: ADR 052 – ensure static prompt catalog skips list reads in catalog-only mode.
- Changes:
  - `static_prompt_catalog` now treats falsy `static_prompt_list_path` as “skip list reads” while merging SSOT tokens.
  - `axis_catalog` passes a falsy path when list files are absent, keeping catalog-only mode pure.
- Tests: `python3 -m pytest _tests/test_static_prompt_catalog_skip_lists.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would reintroduce unnecessary list file reads when running catalog-only, and drop the guardrails covering it.

# 2025-03-09 – Loop 113 (kind: guardrail/tests)
- Focus: ADR 052 – keep help index and runtime lists fully catalog-driven.
- Changes:
  - `help_index` comment clarifies catalog is the SSOT; list reads are fallback only.
  - Added `_tests/test_help_index_catalog_only.py` (guardrail: catalog tokens used without list files).
  - Added `_tests/test_talon_settings_catalog_lists.py` to ensure runtime ctx lists populate from catalog even without pre-seeded Talon lists; guardrail targets updated.
- Tests: `python3 -m pytest _tests/test_talon_settings_catalog_lists.py _tests/test_help_index_catalog_only.py _tests/test_axis_catalog_skip_lists.py _tests/test_static_prompt_catalog_skip_lists.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would weaken catalog-only guarantees for help/index and runtime list population, and drop the guardrails covering them.

# 2025-03-09 – Loop 114 (kind: guardrail/tests)
- Focus: ADR 052 – guard partial list merges back into SSOT tokens.
- Changes:
  - Added `_tests/test_axis_catalog_merge_lists.py` to assert axis list tokens merge partial list files with SSOT tokens (list token + all SSOT tokens are present).
  - Guardrail targets updated to include the new test.
- Tests: `python3 -m pytest _tests/test_axis_catalog_merge_lists.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop coverage ensuring partial list files cannot hide SSOT tokens.

# 2025-03-09 – Loop 115 (kind: guardrail/tests)
- Focus: ADR 052 – guard partial static prompt list merges back into SSOT tokens.
- Changes:
  - Added `_tests/test_static_prompt_catalog_merge_lists.py` to assert static prompt list tokens merge list entries with all SSOT tokens.
  - Guardrail targets updated to include the new test.
- Tests: `python3 -m pytest _tests/test_static_prompt_catalog_merge_lists.py _tests/test_axis_catalog_merge_lists.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would drop coverage ensuring static prompt list files cannot hide SSOT tokens.

# 2025-03-09 – Loop 116 (kind: guardrail/tests)
- Focus: ADR 052 – ensure default validator skips missing lists dir.
- Changes: Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_default_skips_missing_dir` to guard that the default skip-list-files path passes even when the lists dir is absent.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_validate.py` (pass).
- Removal test: Reverting would drop coverage ensuring the default catalog-only path tolerates missing list dirs.

# 2025-03-09 – Loop 117 (kind: behaviour/tests)
- Focus: ADR 052 – ensure runtime Talon lists merge partial list tokens with SSOT.
- Changes:
  - `_axis_tokens` in `talonSettings` now merges catalog axis tokens with any list tokens to avoid losing SSOT values when list tokens are partial.
  - Added `_tests/test_talon_settings_catalog_lists.py::test_runtime_lists_merge_axis_tokens_from_catalog` to guard the merge behaviour.
- Tests: `python3 -m pytest _tests/test_talon_settings_catalog_lists.py _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py _tests/test_axis_catalog_skip_lists.py _tests/test_axis_catalog_merge_lists.py` (pass).
- Removal test: Reverting would allow partial list tokens to drop SSOT axis values in runtime Talon lists and remove the guardrail covering it.

# 2025-03-09 – Loop 118 (kind: behaviour/tests)
- Focus: ADR 052 – make validator default lists_dir optional (catalog-only default).
- Changes: `axis-catalog-validate` now defaults `--lists-dir` to None (catalog-only unless explicitly set); behavior unchanged because list checks are skipped by default.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would reintroduce a default GPT/lists path, weakening the catalog-only default stance.

# 2025-03-09 – Loop 88 (kind: guardrail/tests)
- Focus: ADR 052 – make verbose validator output acknowledge skipped lists_dir args.
- Changes:
  - Updated `scripts/tools/axis-catalog-validate.py` verbose summary to include `lists_dir_arg=<path>` when list checks are skipped but a `--lists-dir` arg is supplied.
  - Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_verbose_summary_with_lists_dir_skipped` to guardrail that behavior.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_verbose_summary_with_lists_dir_skipped` (pass).
- Removal test: Reverting would drop the explicit acknowledgement of skipped lists_dir args in verbose output and the guardrail ensuring catalog-only runs remain transparent when users pass a lists_dir.

# 2025-03-09 – Loop 89 (kind: guardrail/tests)
- Focus: ADR 052 – surface when lists_dir is provided but list checks are skipped.
- Changes:
  - `axis-catalog-validate` now emits a note when `--lists-dir` is provided while list checks are skipped, keeping catalog-only runs explicit.
  - Extended `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_verbose_summary_with_lists_dir_skipped` to assert the note is present.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_verbose_summary_with_lists_dir_skipped` (pass).
- Removal test: Reverting would hide the user hint that list validation was skipped despite a provided lists_dir and drop the guardrail covering it.

# 2025-03-09 – Loop 90 (kind: guardrail/tests)
- Focus: ADR 052 – make catalog-only runs explicit even when lists_dir is provided without verbose.
- Changes:
  - `axis-catalog-validate` note now includes `lists_dir=<skipped>` and `lists_validation=skipped` when list checks are skipped but `--lists-dir` is supplied.
  - Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_default_with_lists_dir_skipped_reports_note` to assert the note appears in default (non-verbose) output.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (pass).
- Removal test: Reverting would stop surfacing the skip note in default runs with lists_dir and drop the guardrail ensuring catalog-only behavior remains visible.

# 2025-03-09 – Loop 91 (kind: guardrail/tests)
- Focus: ADR 052 – ensure make help mentions lists-dir when enforcing list checks.
- Changes:
  - Updated `_tests/test_make_help_guardrails.py` to assert `make help` output includes `lists-dir`, keeping the enforcement requirement discoverable.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would allow `make help` to omit the lists-dir mention, weakening guidance for enforced list checks.

# 2025-03-09 – Loop 92 (kind: guardrail/tests)
- Focus: ADR 052 – keep default validator output minimal when catalog-only.
- Changes:
  - Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_default_without_lists_dir_stays_minimal` to ensure the default `axis-catalog-validate` run (no lists_dir) emits only the success line (no lists_dir/lists_validation or note).
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_default_without_lists_dir_stays_minimal` (pass).
- Removal test: Reverting would allow extra lists_dir/list_validation chatter in default catalog-only runs and drop the guardrail keeping output minimal.

# 2025-03-09 – Loop 93 (kind: guardrail/tests)
- Focus: ADR 052 – ensure enforced list checks report validated lists_dir in verbose output.
- Changes:
  - Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_verbose_with_lists_dir_enforced_reports_validated` to assert verbose output uses validated lists_dir and omits skip notes when `--no-skip-list-files` is set.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_verbose_with_lists_dir_enforced_reports_validated` (pass).
- Removal test: Reverting would drop coverage that enforced list validation reports the correct lists_dir state and could let skip-note behavior leak into enforced runs.

# 2025-03-09 – Loop 94 (kind: guardrail/tests)
- Focus: ADR 052 – report validated lists_dir in non-verbose enforced runs.
- Changes:
  - `axis-catalog-validate` now prints `lists_dir=<dir> lists_validation=validated@<dir>` in non-verbose mode when `--no-skip-list-files` is set.
  - Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_nonverbose_with_lists_dir_enforced_reports_validated` to guard this output.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_nonverbose_with_lists_dir_enforced_reports_validated` (pass).
- Removal test: Reverting would drop the non-verbose reporting of enforced list validation and the guardrail ensuring enforced runs remain observable.

# 2025-03-09 – Loop 95 (kind: guardrail/tests)
- Focus: ADR 052 – ensure enforced list checks fail clearly on empty lists dirs.
- Changes:
  - Added `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_nonverbose_with_empty_lists_dir_reports_missing_files` to assert enforcing list checks against an empty lists dir fails and reports missing list files.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_nonverbose_with_empty_lists_dir_reports_missing_files` (pass).
- Removal test: Reverting would drop coverage that enforced list validation fails on empty directories and reports missing files, potentially masking misconfigured list-check runs.

# 2025-03-09 – Loop 96 (kind: guardrail/tests)
- Focus: ADR 052 – keep README examples aligned with enforced list checks.
- Changes: Updated the README guardrail blurb to include an explicit example command for enforcing list checks with `--lists-dir` and reran the README guardrail test.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would remove the explicit enforced-check example from the README and drop its guardrail coverage.

# 2025-03-09 – Loop 97 (kind: guardrail/tests)
- Focus: ADR 052 – ensure GPT README carries the enforced list check example.
- Changes:
  - Added an explicit enforced list-check command to `GPT/readme.md`.
  - Extended `_tests/test_gpt_readme_axis_lists.py` to assert the example is present.
- Tests: `python3 -m pytest _tests/test_gpt_readme_axis_lists.py` (pass).
- Removal test: Reverting would drop the enforced-check example from the GPT README and the guardrail ensuring it stays documented.

# 2025-03-09 – Loop 98 (kind: guardrail/tests)
- Focus: ADR 052 – ensure root README carries the enforced list check example.
- Changes: Extended `_tests/test_readme_guardrails_docs.py` to assert the README includes an explicit enforced list-check command (`python3 scripts/tools/axis-catalog-validate.py --lists-dir /path/to/lists --no-skip-list-files`).
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring the README documents the enforced list-check command, weakening guidance for ad-hoc validation when enabling list checks.

# 2025-03-09 – Loop 100 (kind: guardrail/tests)
- Focus: ADR 052 – make enforced list validation output include counts.
- Changes:
  - Updated `axis-catalog-validate` to print `Axes=` and `static_prompts=` in non-verbose mode when enforcing list checks.
  - Extended `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_nonverbose_with_lists_dir_enforced_reports_validated` to assert counts are present.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_nonverbose_with_lists_dir_enforced_reports_validated` (pass).
- Removal test: Reverting would drop the counts from enforced validation output and the guardrail ensuring enforced runs remain observable beyond list paths.

# 2025-03-09 – Loop 101 (kind: guardrail/tests)
- Focus: ADR 052 – hint regeneration when list files are missing/drifted.
- Changes:
  - `axis-catalog-validate` now includes `generate_talon_lists.py` hints in list-drift errors (missing dir/file, missing/extra tokens).
  - Extended `_tests/test_axis_catalog_validate_lists_dir.py::test_validate_missing_list_files_reported` to assert the hint is present for missing files.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_missing_list_files_reported` (pass).
- Removal test: Reverting would drop regeneration hints from list-drift errors and the guardrail ensuring users see how to fix missing/extra list files.

# 2025-03-09 – Loop 99 (kind: behaviour/docs)
- Focus: ADR 052 – add an explicit enforced list check example to the ADR itself.
- Changes: Updated `docs/adr/052-runtime-populated-axis-static-prompt-lists.md` Ops/guardrails to include a concrete `--lists-dir … --no-skip-list-files` example.
- Tests: Not run (ADR text-only change; guardrails already cover the enforced example in README/GPT docs).
- Removal test: Reverting would drop the explicit example from the ADR, reducing alignment between the ADR and documented guardrail usage.

# 2025-03-09 – Loop 102 (kind: behaviour/docs)
- Focus: ADR 052 – add regeneration hint for enforced list checks to README.
- Changes: Updated `readme.md` guardrail blurb to suggest regenerating local list files with `make talon-lists`/`generate_talon_lists.py` before running enforced list checks.
- Tests: Not run (doc-only change; enforced checks remain guardrailed elsewhere).
- Removal test: Reverting would remove the regeneration hint from README, making enforced list check remediation less discoverable.

# 2025-03-09 – Loop 103 (kind: guardrail/tests)
- Focus: ADR 052 – ensure GPT README carries regeneration hint for enforced checks.
- Changes:
  - Added regeneration hint (`make talon-lists` / `generate_talon_lists.py --out-dir <dir>`) to `GPT/readme.md` for enforced list checks.
  - Extended `_tests/test_gpt_readme_axis_lists.py` to assert the regeneration hint is present.
- Tests: `python3 -m pytest _tests/test_gpt_readme_axis_lists.py` (pass).
- Removal test: Reverting would drop the regeneration hint from GPT README and the guardrail ensuring enforced check remediation stays documented.

# 2025-03-09 – Loop 104 (kind: guardrail/tests)
- Focus: ADR 052 – ensure root README mentions regenerating list files before enforced checks.
- Changes:
  - Updated `readme.md` guardrail blurb to mention `generate_talon_lists.py` alongside `make talon-lists` for regenerating local list files before enforced list checks.
  - Extended `_tests/test_readme_guardrails_docs.py` to assert the regeneration hint is present.
- Tests: `python3 -m pytest _tests/test_readme_guardrails_docs.py` (pass).
- Removal test: Reverting would drop the regeneration hint from the README and the guardrail ensuring enforced-check remediation stays visible.

# 2025-03-09 – Loop 105 (kind: guardrail/tests)
- Focus: ADR 052 – keep make help explicit that talon-lists outputs are untracked.
- Changes: Updated `_tests/test_make_help_guardrails.py` to assert `make help` mentions the talon-lists outputs are untracked.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring the make help output continues to remind users that talon-lists outputs are untracked.

# 2025-03-09 – Loop 106 (kind: guardrail/tests)
- Focus: ADR 052 – add regeneration hint to axis-catalog-validate help.
- Changes:
  - Updated `scripts/tools/axis-catalog-validate.py` help text (`--lists-dir`/usage) to mention regenerating Talon lists via `generate_talon_lists.py`.
  - Extended `_tests/test_axis_catalog_validate_help.py` to assert the regeneration hint appears in `--help`.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_help.py` (pass).
- Removal test: Reverting would remove the regeneration hint from validator help and drop the guardrail ensuring it stays discoverable.

# 2025-03-09 – Loop 107 (kind: guardrail/tests)
- Focus: ADR 052 – include regeneration hints in enforced list-check errors.
- Changes:
  - Added regeneration hints to `axis-catalog-validate` enforced list-check errors (missing lists_dir/not a dir) to point to `generate_talon_lists.py`.
  - Extended `_tests/test_axis_catalog_validate_lists_dir.py` to assert the regeneration hint appears for missing/non-directory lists_dir errors.
- Tests: `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_missing_lists_dir_fails _tests/test_axis_catalog_validate_lists_dir.py::AxisCatalogValidateListsDirTests::test_validate_lists_dir_not_directory_fails` (pass).
- Removal test: Reverting would drop regeneration guidance from enforced list-check failures and the guardrail ensuring it stays present.

# 2025-03-09 – Loop 108 (kind: status/adversarial)
- Focus: ADR 052 – adversarial check for remaining in-repo work.
- Changes: Reviewed ADR 052 and its guardrail suite; no unchecked tasks or in-repo follow-ups remain beyond the catalog-only, untracked runtime list implementation and documented guardrails. Status remains Accepted.
- Tests: Not run (status-only adversarial check).
- Removal test: Reverting would remove the recorded adversarial confirmation and could reopen ambiguity about ADR completion despite no remaining in-repo tasks.

# 2025-03-09 – Loop 109 (kind: behaviour/docs)
- Focus: Clarify ADR loop helper on minimal slices and risk ordering.
- Changes: Updated `docs/adr/adr-loop-execute-helper.md` to (a) remind that minimal, high-signal slices are preferred (including deletions when they satisfy the goal) without forcing deletions, and (b) note that higher-risk/central slices should not be deferred just to do “safe” work first when they are the most meaningful slice.
- Tests: Not run (doc-only change).
- Removal test: Reverting would drop the clarifications on minimal slices and risk ordering from the loop helper.

# 2025-03-09 – Loop 107 (kind: guardrail/tests)
- Focus: ADR 052 – keep make help guardrail asserting untracked talon-lists wording.
- Changes: Strengthened `_tests/test_make_help_guardrails.py` to assert `make help` explicitly mentions talon-lists outputs are untracked.
- Tests: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: Reverting would drop the guardrail ensuring make help continues to remind users that talon-lists outputs are untracked.
