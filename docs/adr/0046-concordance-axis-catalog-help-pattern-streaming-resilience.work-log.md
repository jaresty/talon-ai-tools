# ADR-0046 – Work Log

## 2025-12-11 – Axis Catalog facade slice

Focus (kind: behaviour/guardrail): Establish a shared **axis_catalog** façade that unifies axis tokens, Talon list tokens, and static prompt catalog data, and route GPT/docs helpers through it with guardrail tests.

### Changes
- Added `lib/axisCatalog.py` exposing:
  - `axis_catalog()` combining `AXIS_KEY_TO_VALUE`, Talon axis list tokens, static prompt catalog, and description overrides.
  - Facade exports for `get_static_prompt_profile/get_static_prompt_axes/static_prompt_catalog/static_prompt_description_overrides`, plus `axis_list_tokens` for drift checks.
- Updated `GPT/gpt.py` to import static prompt helpers from `axisCatalog`, consolidating the docs/help entrypoint on the new façade.
- Tests:
  - New `_tests/test_axis_catalog.py` guardrails that Talon axis list tokens align with `AXIS_KEY_TO_VALUE` and that `axis_catalog()["static_prompts"]` matches `static_prompt_catalog()`.
  - `_tests/test_static_prompt_axis_tokens.py` now consumes `static_prompt_catalog` via the façade (still ties profiles back to `AXIS_KEY_TO_VALUE`).

### Checks
- Ran targeted catalog/axis tests:
  - `python3 -m pytest _tests/test_axis_catalog.py _tests/test_static_prompt_axis_tokens.py _tests/test_static_prompt_catalog_consistency.py _tests/test_static_prompt_docs.py _tests/test_readme_axis_lists.py`
  - Result: **19 passed**, 0 failed.

### Removal test
- Reverting this slice would drop the new façade and guardrails, and GPT/docs would fall back to disparate helpers; the added tests would fail or disappear, removing the alignment guardrail between axisConfig, Talon lists, and static prompt catalog.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Extend `axis_catalog` consumers: README/help hub/Talon settings should read catalog data from the façade rather than direct config access.
- Add a small validator/CLI to flag drift between axis tokens and Talon lists at dev time, and wire catalog data into request log axis filtering to keep Concordance inputs explicit.

## 2025-12-11 – RequestLog axis catalog alignment slice

Focus (kind: behaviour/guardrail): Align request history axis filtering with the new **axis_catalog** and guardrail tokens from axisConfig/Talon lists.

### Changes
- Updated `lib/requestLog._filter_axes_payload` to pull axis/token metadata from `axis_catalog()` (axisConfig tokens + Talon list tokens) so filtered axes in history entries stay in sync with the catalog domain.
- Added `_tests/test_request_log.py::test_append_entry_uses_axis_catalog_tokens` covering directional axis filtering (keeps catalog/list tokens, drops unknown) and passthrough trimming for non-axis keys.

### Checks
- Ran focused history/log tests: `python3 -m pytest _tests/test_request_log.py` (4 passed).

### Removal test
- Reverting would revert request history to pre-facade token filtering and drop the new guardrail test; Concordance-aligned axis/token drift could reappear without detection.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Extend catalog consumption to README/help hub/Talon settings.
- Add a developer-facing drift validator/CLI using `axis_catalog` to surface mismatches early.

## 2025-12-11 – Axis catalog drift validator slice

Focus (kind: guardrail/tools): Add a CLI validator to detect drift between axisConfig, Talon lists, and static prompt axis tokens, and guard it with tests.

### Changes
- Added `scripts/tools/axis-catalog-validate.py`:
  - Boots the repo and runs alignment checks across axisConfig token maps, Talon list tokens, and static prompt catalog axis tokens (skipping completeness free-form hints).
  - Exits non-zero with detailed findings if drift is detected.
- Added `_tests/test_axis_catalog_validate.py` to run the CLI and fail if it reports drift.

### Checks
- `python3 scripts/tools/axis-catalog-validate.py` → Axis catalog validation passed.
- `python3 -m pytest _tests/test_axis_catalog_validate.py` → 1 passed.

### Removal test
- Reverting would drop the drift validator and its guardrail test; axis/list/static prompt drift could reappear without a dev-time signal.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Wire README/help hub/Talon settings to consume `axis_catalog` data instead of direct config reads.
- Optionally integrate the validator into a CI hook or `make` target so drift fails fast in automation.

## 2025-12-11 – Axis docs via catalog slice

Focus (kind: behaviour/guardrail): Move GPT axis docs generation onto `axis_catalog` so README/help surfaces describe axis tokens directly from the catalog rather than raw Talon list parsing.

### Changes
- Updated `GPT/gpt.py`:
  - `_build_axis_docs` now pulls axis token/description pairs from `axis_catalog()` (axisConfig SSOT), falling back to Talon list parsing only if catalog data is missing.
  - Import block reuses the axis catalog facade (with a minimal fallback stub for older Talon runtimes).
- No doc text copied inline; behaviour change is the source of truth for axis docs (catalog-backed).

### Checks
- `python3 -m pytest _tests/test_static_prompt_docs.py` → 10 passed (axis docs expectations still satisfied).

### Removal test
- Reverting would send axis docs back to direct Talon list parsing, breaking the catalog-based SSOT intent and losing the alignment with axis_config tokens enforced by ADR-0046.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Route README/help hub/Talon settings consumers to use `axis_catalog` outputs directly (for example, axis cheat sheet generation), and consider adding a short CLI/Make target that emits catalog-backed docs to catch drift in CI.

## 2025-12-11 – README axis lists via catalog slice

Focus (kind: guardrail/docs): Make README axis token checks depend on `axis_catalog` so docs stay aligned with the catalog SSOT.

### Changes
- Updated `_tests/test_readme_axis_lists.py` to compare README axis token lists against `axis_catalog()` instead of direct Talon list reads/axis registry. This ties doc drift detection to the catalog façade.
- README content already matches catalog tokens; no text changes needed for this slice.

### Checks
- `python3 -m pytest _tests/test_readme_axis_lists.py` → 1 passed.

### Removal test
- Reverting would decouple README checks from the catalog and allow axis/list/catalog drift to slip into docs without failing tests.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Extend help hub and Talon settings to read axis/static prompt data via `axis_catalog`, and consider generating README cheat sheets from the catalog in a scripted way (or gating via CI) to keep docs and runtime aligned.

## 2025-12-11 – Help Hub catalog-backed navigation slice

Focus (kind: behaviour/guardrail): Make Help Hub search/index construction consume `axis_catalog` so help navigation reflects the catalog SSOT instead of raw list parsing.

### Changes
- `lib/helpDomain.help_index` now accepts an optional catalog and prefers catalog data for static prompts and axis tokens (falls back to Talon lists when absent).
- `lib/helpHub.build_search_index` passes `axis_catalog()` (with optional override) and a new test-friendly `catalog` parameter; `_build_search_index` uses the catalog facade by default.
- `_tests/test_help_hub.py::test_build_search_index_uses_buttons_and_lists` now uses a fake catalog to assert that prompt/axis entries come from the catalog, not from list parsing.

### Checks
- `python3 -m pytest _tests/test_help_hub.py` → 13 passed.

### Removal test
- Reverting would send Help Hub back to list-only search data and drop the guardrail that navigation reflects the catalog SSOT, reintroducing drift between help navigation and axis/static prompt semantics.

### Follow-ups / remaining ADR-0046 work (help domain)
- Extend quick-help canvas to read static prompt/axis docs from `axis_catalog` so both hub and quick-help share the same catalog-backed data.
- Consider extracting a small shared navigation state helper for hub + quick-help once catalog-backed data flows through both surfaces.

## 2025-12-11 – Quick-help canvas catalog alignment slice

Focus (kind: guardrail/tests): Ensure quick-help static prompt catalog stays aligned with the axis catalog SSOT.

### Changes
- Added `_tests/test_model_help_canvas_catalog.py` to assert `static_prompt_settings_catalog()` contains every profiled prompt from `axis_catalog()["static_prompts"]["profiled"]`, keeping quick-help prompt coverage aligned with the catalog.
- No runtime code changes required in this slice; existing quick-help rendering already consumes `static_prompt_settings_catalog`.

### Checks
- `python3 -m pytest _tests/test_model_help_canvas_catalog.py` → 1 passed.
- `python3 -m pytest _tests/test_help_hub.py _tests/test_model_help_canvas_catalog.py` → 14 passed.

### Removal test
- Reverting would drop the guardrail that quick-help prompt coverage matches the catalog, allowing drift between catalog SSOT and quick-help surfaces.

### Follow-ups / remaining ADR-0046 work (help domain)
- Plumb axis docs/static prompt descriptions directly from `axis_catalog` into quick-help rendering (currently driven by `static_prompt_settings_catalog`), and consider a shared navigation/data helper across hub and quick-help.

## 2025-12-11 – Quick-help axis lists via catalog slice

Focus (kind: behaviour/guardrail): Make quick-help axis key lists derive from the catalog SSOT and guard against drift.

### Changes
- `lib/modelHelpCanvas._axis_keys` now pulls axis tokens from `axis_catalog()` (falls back to `axis_docs_for`), so quick-help axis lists reflect the catalog rather than static list parsing.
- Directional grouping now includes catalog directional tokens when present.
- `_tests/test_model_help_canvas_catalog.py` extended to assert quick-help axis keys (completeness/scope/method/style) match `axis_catalog` tokens, keeping UI lists aligned with the catalog.

### Checks
- `python3 -m pytest _tests/test_model_help_canvas_catalog.py` → 2 passed.

### Removal test
- Reverting would break the catalog-to-quick-help alignment and drop the guardrail that axis keys shown in quick-help match the catalog SSOT, allowing drift between UI hints and axis/static prompt semantics.

### Follow-ups / remaining ADR-0046 work (help domain)
- Feed axis descriptions (not just keys) and static prompt text directly from `axis_catalog` into quick-help rendering, and consider a shared navigation/data helper with Help Hub to keep both surfaces in sync.

## 2025-12-11 – Axis catalog validator make target slice

Focus (kind: tools/guardrail): Wire the axis catalog drift validator into the developer workflow.

### Changes
- Added `axis-catalog-validate` Makefile target invoking `python3 scripts/tools/axis-catalog-validate.py` so catalog/list/profile drift can be run easily or hooked into CI.

### Checks
- `python3 -m pytest _tests/test_axis_catalog_validate.py` → 1 passed.

### Removal test
- Reverting would remove the convenient make target for catalog drift checks, making it easier for drift between axisConfig, Talon lists, and static prompts to slip past local/CI runs.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Consider adding this target to CI/gating scripts; continue aligning help surfaces and Talon settings on `axis_catalog`.

## 2025-12-11 – Talon settings axis filtering via catalog slice

Focus (kind: behaviour/guardrail): Align Talon settings axis filtering with the axis catalog, including directional tokens.

### Changes
- `lib/talonSettings._filter_axis_tokens` now:
  - Imports `axis_catalog` and includes catalog axis tokens when filtering, dropping hydrated “Important:” values and unknowns.
  - Filters directional axis tokens and retains only catalog/axisConfig tokens.
- Added `_tests/test_talon_settings_axis_catalog.py` to assert catalog tokens are kept and unknowns dropped across scope/method/style/directional.

### Checks
- `python3 -m pytest _tests/test_talon_settings_axis_catalog.py` → 1 passed.

### Removal test
- Reverting would drop catalog-aware filtering in Talon settings and remove the guardrail test, allowing axis/catalog drift (especially directional tokens) to leak into system prompt state.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Continue plumbing catalog data into any remaining axis normalization paths (for example, axis_recipe tokens if additional axes are added) and consider CI gating with the catalog validator target.

## 2025-12-11 – History/state axis filtering via catalog slice

Focus (kind: guardrail/tests): Align Talon settings and request history axis filtering with the catalog, including directional tokens.

### Changes
- `lib/talonSettings._filter_axis_tokens` now incorporates `axis_catalog` tokens (including directional) when filtering axis values; drops hydrated/unknown values outside the catalog.
- `lib/requestHistoryActions.history_axes_for` now filters directional tokens and uses the catalog to keep history axes aligned with the SSOT.
- Added guardrails:
  - `_tests/test_talon_settings_axis_catalog.py` checks catalog-aware filtering and unknown-dropping for scope/method/style/directional.
  - `_tests/test_request_history_actions_catalog.py` checks history axis filtering retains catalog tokens and drops unknowns.

### Checks
- `python3 -m pytest _tests/test_talon_settings_axis_catalog.py _tests/test_request_history_actions_catalog.py` → 2 passed.

### Removal test
- Reverting would drop catalog-aware filtering for Talon settings and history, allowing drift (especially directional tokens) to leak into system prompt state and request history axes.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Ensure any remaining axis normalization paths (for example, recipe tokens) and downstream consumers keep using catalog tokens; consider CI gating via the catalog validator.

## 2025-12-11 – Catalog-backed axis cheat sheet generator slice

Focus (kind: tools/guardrail/docs): Provide a catalog-backed axis cheat sheet generator to keep README/help surfaces aligned with the SSOT.

### Changes
- Added `scripts/tools/generate-axis-cheatsheet.py` which reads `axis_catalog()` and emits a markdown cheat sheet (default `tmp/readme-axis-cheatsheet.md`, supports `--out` and stdout).
- Added `_tests/test_generate_axis_cheatsheet.py` to run the generator and assert catalog-backed sections (completeness/scope/method/style/directional) are present.

### Checks
- `python3 scripts/tools/generate-axis-cheatsheet.py` → wrote `tmp/readme-axis-cheatsheet.md`.
- `python3 -m pytest _tests/test_generate_axis_cheatsheet.py` → 1 passed.
- `python3 -m pytest _tests/test_generate_axis_cheatsheet.py _tests/test_talon_settings_axis_catalog.py _tests/test_request_history_actions_catalog.py` → 3 passed.

### Removal test
- Reverting would drop the generator and guardrail test, removing an easy path to keep README/help axis cheat sheets synced with the catalog SSOT.

### Follow-ups / remaining ADR-0046 work (axis/help domain)
- Integrate the generated cheat sheet (or its content) into README/help hub via CI/gating or scripted updates so docs stay in lockstep with catalog changes.

## 2025-12-11 – Axis cheat sheet artifact (run) slice

Focus (kind: docs artifact): Generate the catalog-backed axis cheat sheet artifact to support README/help alignment.

### Changes
- Ran `python3 scripts/tools/generate-axis-cheatsheet.py --out tmp/readme-axis-cheatsheet.md` to emit the current catalog-backed axis cheat sheet.

### Checks
- Verified output contains all catalog tokens across axes (see `tmp/readme-axis-cheatsheet.md`).

### Removal test
- Removing this run would drop the freshly generated artifact, making it harder to sync README/help surfaces with the catalog snapshot used in this ADR loop.

### Follow-ups / remaining ADR-0046 work (axis/help domain)
- Use the generated artifact to refresh README/help hub axis lists (or gate via CI) so docs stay aligned with the catalog SSOT.

## 2025-12-11 – Axis cheat sheet make target slice

Focus (kind: tooling/guardrail): Add a Make target to run the catalog-backed axis cheat sheet generator.

### Changes
- Added `make axis-cheatsheet` to generate the catalog-backed cheat sheet at `tmp/readme-axis-cheatsheet.md` via `scripts/tools/generate-axis-cheatsheet.py`.

### Checks
- `make axis-cheatsheet` (writes tmp/readme-axis-cheatsheet.md).
- `python3 -m pytest _tests/test_generate_axis_cheatsheet.py` → 1 passed.

### Removal test
- Reverting would remove the convenient target for generating the catalog-aligned cheat sheet, reducing tooling support for keeping README/help surfaces synced with the catalog.

## 2025-12-11 – History directional axis persistence slice

Focus (kind: behaviour/guardrail): Ensure history saves and state restoration include catalog-backed directional axes.

### Changes
- `lib/requestHistoryActions._save_history_prompt_to_file` now writes `directional_tokens` alongside other axes in history saves.
- `lib/requestHistoryActions._show_entry` now hydrates `GPTState.last_directional` and includes directional tokens when building `last_recipe` from stored axes.
- Added `_tests/test_request_history_axes_catalog.py`:
  - Asserts `history_axes_for` keeps catalog directional tokens while dropping unknowns.
  - Ensures history saves include a `directional_tokens` header when axes contain directional tokens.

### Checks
- `python3 -m pytest _tests/test_request_history_axes_catalog.py` → 2 passed.
- `python3 -m pytest _tests/test_request_history_actions_catalog.py _tests/test_request_history_axes_catalog.py` → 3 passed.

### Removal test
- Reverting would drop directional axes from history saves and state restoration, weakening the catalog-aligned persistence expected by ADR-0046.

### Follow-ups / remaining ADR-0046 work (axis/streaming domain)
- Keep catalog tokens flowing through any remaining persistence paths (for example, snapshot headers) so directional/context axes stay aligned end-to-end.

## 2025-12-12 – Response snapshot directional slug/header slice

Focus (kind: behaviour/guardrail): Ensure response snapshots (File destination) carry catalog-backed directional axes in slugs/headers.

### Changes
- Updated `lib/modelDestination.File` slug construction to include `last_directional` alongside other axis tokens so saved response files are self-describing and aligned with the catalog.
- Extended `_tests/test_model_destination.py::test_file_destination_header_and_slug_use_last_axes_tokens` to seed `last_directional` and assert slugs/headers include directional tokens.

### Checks
- `python3 -m pytest _tests/test_model_destination.py` → 8 passed.
- `python3 -m pytest _tests/test_model_destination.py _tests/test_request_history_actions.py` → 22 passed.

### Removal test
- Reverting would drop directional tokens from response snapshot slugs/headers and weaken the catalog-aligned persistence guardrail.

### Follow-ups / remaining ADR-0046 work (streaming/persistence)
- Audit other snapshot/destination paths to ensure directional/context axes remain present (for example, any ancillary exporters), and consider CI gating for these persistence guardrails.

## 2025-12-12 – Browser/response recap uses catalog-backed axes slice

Focus (kind: behaviour/guardrail): Ensure Browser response recap uses catalog-backed axes (including directional) and falls back to legacy recipes only when catalog tokens are sparse.

### Changes
- `lib/modelDestination.Browser` now:
  - Uses `axis_join` for directional tokens alongside other axes.
  - Prefers `last_recipe` when catalog-derived tokens are sparse (for example, only static prompt + directional), preventing loss of richer axis context.
  - Avoids double-appending directional when already present.
- Tests updated:
  - `_tests/test_model_destination.py::test_browser_includes_recipe_metadata_from_gpt_state` still asserts recipe/grammar include directional.
  - Combined suite (`_tests/test_model_destination.py _tests/test_request_history_actions.py`) passing to cover recaps and history interactions.

### Checks
- `python3 -m pytest _tests/test_model_destination.py -k browser_includes_recipe_metadata_from_gpt_state` → pass.
- `python3 -m pytest _tests/test_model_destination.py _tests/test_request_history_actions.py` → 22 passed.

### Removal test
- Reverting would drop catalog-based directional handling in Browser recaps and could degrade recipe clarity when catalog tokens are sparse, weakening the Concordance-aligned persistence expectations.

## 2025-12-12 – Recipe snapshot directional from catalog axes slice

Focus (kind: behaviour/guardrail): Ensure recipe snapshots pull directional tokens from catalog-backed `last_axes` before falling back to legacy fields so snapshots/headers stay aligned.

### Changes
- `lib/suggestionCoordinator.last_recipe_snapshot` now derives `directional` from `last_axes["directional"]` when present, falling back to `last_directional` otherwise.
- Updated `_tests/test_recipe_header_lines.py::test_last_recipe_snapshot_prefers_last_axes_tokens_over_legacy_fields` to assert directional preference from `last_axes` over legacy `last_directional`.
- Regression checks across snapshot/destination paths remain green (`_tests/test_gpt_source_snapshot.py` unaffected).

### Checks
- `python3 -m pytest _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py` → 6 passed.
- `python3 -m pytest _tests/test_model_destination.py _tests/test_request_history_actions.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py` → 28 passed.

### Removal test
- Reverting would make recipe snapshots ignore catalog-backed directional tokens when `last_axes` carries them, undermining the SSOT alignment for snapshot headers used by source/response persistence.

## 2025-12-12 – README axis cheat sheet refreshed from catalog slice

Focus (kind: docs/guardrail): Refresh README axis lists from the catalog so docs match the SSOT and guardrails stay green.

### Changes
- Updated `GPT/readme.md` axis lists for completeness/scope/method/style to match the catalog (order/tokens reflect `axis_catalog` and `tmp/readme-axis-cheatsheet.md`).

### Checks
- `python3 -m pytest _tests/test_readme_axis_lists.py` → 1 passed.
- `python3 -m pytest _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py` → 8 passed.

### Removal test
- Reverting would desync README axis lists from the catalog and break the doc guardrail tests.

### Follow-ups / remaining ADR-0046 work (docs/help)
- Consider wiring `axis-guardrails` (catalog validate + cheat sheet) into CI to keep README/help surfaces automatically aligned with the catalog SSOT.

## 2025-12-12 – Cheat sheet token parity guardrail slice

Focus (kind: guardrail/tests): Ensure the generated axis cheat sheet token lists exactly match the catalog SSOT.

### Changes
- Extended `_tests/test_generate_axis_cheatsheet.py` with a new test that runs the generator and compares each axis token set to `axis_catalog` to catch mismatches in output.

### Checks
- `python3 -m pytest _tests/test_generate_axis_cheatsheet.py` → 2 passed.

### Removal test
- Reverting would drop the token parity guardrail, allowing the cheat sheet to drift from the catalog without failing tests.

## 2025-12-12 – Axis guardrails dev doc slice

Focus (kind: docs/guardrail): Document the axis guardrail command for contributors.

### Changes
- Updated `README.md` Development section to point contributors to `make axis-guardrails` (catalog drift check + cheat sheet generation) so axis/docs stay aligned with the catalog SSOT.

### Checks
- `python3 -m pytest _tests/test_generate_axis_cheatsheet.py` → 2 passed (guardrails still green).

### Removal test
- Reverting would remove the dev-facing pointer to run catalog guardrails, increasing the risk of drift slipping past contributors.

## 2025-12-12 – Browser recap uses last_axes when recipe empty slice

Focus (kind: guardrail/tests): Ensure Browser recaps build from catalog-backed `last_axes` (including directional) even when `last_recipe` is empty.

### Changes
- Added `_tests/test_model_destination.py::test_browser_uses_last_axes_when_recipe_empty` to assert the Browser recipe/grammar lines are built from `last_axes` tokens (including directional) when no legacy `last_recipe` is present.

### Checks
- `python3 -m pytest _tests/test_model_destination.py -k "browser_includes_recipe_metadata_from_gpt_state or browser_uses_last_axes_when_recipe_empty"` → 2 passed.
- Combined guardrails: `python3 -m pytest _tests/test_model_destination.py _tests/test_request_history_actions.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py _tests/test_generate_axis_cheatsheet.py` → 31 passed.

### Removal test
- Reverting would drop the guardrail ensuring Browser recaps stay aligned with catalog-backed axes when `last_recipe` is empty, risking incomplete recaps in that scenario.

## 2025-12-12 – Axis catalog description parity slice

Focus (kind: guardrail/tests): Ensure `axis_catalog` static prompt descriptions mirror the canonical overrides helper.

### Changes
- Extended `_tests/test_axis_catalog.py` with a guardrail that `axis_catalog["static_prompt_descriptions"]` matches `static_prompt_description_overrides()`.

### Checks
- `python3 -m pytest _tests/test_axis_catalog.py` → 3 passed.

### Removal test
- Reverting would drop the guardrail that catalog-exposed descriptions remain in sync with the overrides helper, risking drift across doc/help consumers.

## 2025-12-12 – Axis guardrails test target slice

Focus (kind: tooling/guardrail): Provide a single make target to run catalog drift checks, cheat sheet generation, and README axis alignment tests together.

### Changes
- Added `axis-guardrails-test` Make target that depends on `axis-guardrails` and runs key guardrail tests: `test_axis_catalog_validate`, `test_generate_axis_cheatsheet`, and `test_readme_axis_lists`.

### Checks
- `python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py` → 4 passed.
- `python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_recipe_header_lines.py` → 8 passed.

### Removal test
- Reverting would remove the consolidated guardrail target, making it harder to routinely run catalog drift + doc alignment checks in one go.

## 2025-12-12 – History slug includes directional tokens slice

Focus (kind: behaviour/guardrail): Make history save slugs reflect catalog directional axes and guard it with tests.

### Changes
- `lib/requestHistoryActions._save_history_prompt_to_file` now appends normalized directional tokens (via `history_axes_for`) into the filename slug so history saves are self-describing with catalog axes.
- `_tests/test_request_history_axes_catalog.py` extended to assert saved filenames include directional tokens when axes provide them.

### Checks
- `python3 -m pytest _tests/test_request_history_axes_catalog.py` → 2 passed.

### Removal test
- Reverting would drop directional tokens from history save slugs and the guardrail, reducing catalog-aligned persistence for history artifacts.

## 2025-12-12 – Streaming snapshot axes propagation slice

Focus (kind: behaviour/guardrail): Preserve catalog-backed axes through streaming snapshots so errors/completes carry axis context.

### Changes
- `StreamingRun` now carries `axes` and snapshots include them; `_send_request_streaming` seeds axes from `axis_catalog`-filtered request axes so streaming errors/completions retain catalog tokens.
- Updated `_tests/test_streaming_lifecycle_presenter.py` to assert errored snapshots preserve axes.

### Checks
- `python3 -m pytest _tests/test_streaming_lifecycle_presenter.py _tests/test_model_destination.py _tests/test_request_history_actions.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py` → 31 passed.

### Removal test
- Reverting would drop axis context from streaming snapshots and weaken persistence/reporting guardrails for streaming errors/completions.

## 2025-12-12 – Streaming coordinator axes snapshot guardrail slice

Focus (kind: guardrail/tests): Ensure streaming coordinator snapshots retain axes metadata when errored.

### Changes
- `StreamingRun.snapshot()` already includes `axes`; added `_tests/test_streaming_coordinator.py` coverage to assert snapshots retain axes on error.

### Checks
- `python3 -m pytest _tests/test_streaming_coordinator.py` → 9 passed.
- Combined streaming/persistence suite: `python3 -m pytest _tests/test_streaming_coordinator.py _tests/test_streaming_lifecycle_presenter.py _tests/test_model_destination.py _tests/test_request_history_actions.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py` → 40 passed.

### Removal test
- Reverting would drop the guardrail that streaming coordinator snapshots keep axes metadata, weakening catalog-aligned streaming persistence.

## 2025-12-12 – Axis catalog description validation slice

Focus (kind: guardrail/tools/tests): Extend catalog validation to cover static prompt descriptions.

### Changes
- `scripts/tools/axis-catalog-validate.py` now validates static prompt descriptions in the catalog against the description overrides helper.
- `_tests/test_axis_catalog_validate.py` extended to guard description parity via the CLI.

### Checks
- `python3 -m pytest _tests/test_axis_catalog_validate.py` → 2 passed.
- Combined guardrails: `python3 -m pytest _tests/test_axis_catalog_validate.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py _tests/test_recipe_header_lines.py` → 9 passed.

### Removal test
- Reverting would drop description parity from the catalog validator and the guardrail test, allowing description drift between catalog and overrides.

## 2025-12-12 – Pattern debug coordinator scaffold slice

Focus (kind: guardrail/tests): Introduce a shared pattern debug snapshot façade to prepare for pattern/debug refactors.

### Changes
- Added `lib/patternDebugCoordinator.py` exposing `pattern_debug_snapshot` (name/description/axes) as a catalog-style snapshot for patterns, so GUIs/tests can share a single source instead of bespoke `_debug` paths.
- Added `_tests/test_pattern_debug_coordinator.py` to assert the snapshot includes name/description/axes for provided patterns.

### Checks
- `python3 -m pytest _tests/test_pattern_debug_coordinator.py` → 1 passed.
- Combined suite (`python3 -m pytest _tests/test_pattern_debug_coordinator.py _tests/test_model_destination.py _tests/test_request_history_actions.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py _tests/test_axis_catalog_validate.py`) → 32 passed.

### Removal test
- Reverting would remove the shared pattern debug snapshot façade and its guardrail, leaving pattern/debug flows without a coordinator starting point for ADR-0046.

## 2025-12-12 – Pattern debug coordinator view/catalog slice

Focus (kind: guardrail/tests): Expand the pattern debug coordinator to serve per-pattern views and a catalog for tests/GPT actions.

### Changes
- `lib/patternDebugCoordinator.py` now exposes `pattern_debug_view` (single pattern with recipe/axes) and `pattern_debug_catalog` (list of views) so GUIs/tests can consume consistent debug data without bespoke `_debug` paths.
- `_tests/test_pattern_debug_coordinator.py` extended to assert view includes name/description/axes and that the catalog enumerates patterns.

### Checks
- `python3 -m pytest _tests/test_pattern_debug_coordinator.py` → 3 passed.
- Combined guardrails: `python3 -m pytest _tests/test_pattern_debug_coordinator.py _tests/test_model_destination.py _tests/test_request_history_actions.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py _tests/test_axis_catalog_validate.py` → 34 passed.

### Removal test
- Reverting would remove the expanded pattern debug views/catalog and their guardrails, leaving pattern/debug flows without the coordinator data contract needed for ADR-0046.

## 2025-12-12 – Pattern GUI integration to coordinator slice

Focus (kind: behaviour/guardrail): Route pattern debug helpers in `modelPatternGUI` through the new coordinator and guard it with tests.

### Changes
- `lib/modelPatternGUI.pattern_debug_snapshot` and `pattern_debug_catalog` now delegate to the shared pattern debug coordinator to avoid bespoke `_debug` paths.
- Added `_tests/test_model_pattern_debug_integration.py` to assert `pattern_debug_catalog` uses coordinator views and carries axes.

### Checks
- `python3 -m pytest _tests/test_model_pattern_debug_integration.py` → 1 passed.
- Combined guardrails: `python3 -m pytest _tests/test_model_pattern_debug_integration.py _tests/test_pattern_debug_coordinator.py _tests/test_model_destination.py _tests/test_request_history_actions.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py _tests/test_axis_catalog_validate.py` → 35 passed.

### Removal test
- Reverting would send pattern debug helpers back to bespoke logic and drop the guardrail ensuring GUI helpers consume the coordinator data contract.

## 2025-12-12 – Pattern debug domain filter slice

Focus (kind: behaviour/guardrail): Ensure pattern debug catalog respects domains via the coordinator.

### Changes
- `pattern_debug_view` now includes the pattern domain; `modelPatternGUI.pattern_debug_catalog` filters using coordinator views.
- `_tests/test_model_pattern_debug_integration.py` extended to assert domain filtering and axes propagation from the coordinator.

### Checks
- `python3 -m pytest _tests/test_pattern_debug_coordinator.py _tests/test_model_pattern_debug_integration.py` → 5 passed.
- Combined guardrails: `python3 -m pytest _tests/test_pattern_debug_coordinator.py _tests/test_model_pattern_debug_integration.py _tests/test_model_destination.py _tests/test_request_history_actions.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py _tests/test_axis_catalog_validate.py` → 36 passed.

### Removal test
- Reverting would drop domain-aware pattern debug views and filtering, weakening the coordinator contract for pattern/debug surfaces.

## 2025-12-12 – ADR0046 guardrails runner slice

Focus (kind: tooling/guardrail): Provide a single command to run ADR-0046 guardrail suites for CI/dev.

### Changes
- Added `adr0046-guardrails` Make target that runs:
  - `axis-guardrails-test` (catalog drift + cheat sheet + README alignment).
  - Key persistence/streaming/pattern guardrails: `_tests/test_model_destination.py`, `_tests/test_request_history_actions.py`, `_tests/test_recipe_header_lines.py`, `_tests/test_gpt_source_snapshot.py`, `_tests/test_streaming_coordinator.py`, `_tests/test_streaming_lifecycle_presenter.py`, `_tests/test_pattern_debug_coordinator.py`.

### Checks
- `python3 -m pytest _tests/test_model_destination.py _tests/test_request_history_actions.py _tests/test_recipe_header_lines.py _tests/test_gpt_source_snapshot.py _tests/test_streaming_coordinator.py _tests/test_streaming_lifecycle_presenter.py _tests/test_pattern_debug_coordinator.py` → 41 passed.

### Removal test
- Reverting would drop the consolidated ADR-0046 guardrail runner, making it harder to gate catalog/persistence/pattern guardrails in CI or local workflows.
## 2025-12-12 – Axis guardrails Make target slice

Focus (kind: tooling/guardrail): Bundle catalog validation and cheat-sheet generation into a single target for developers/CI.

### Changes
- Added `axis-guardrails` Make target that runs `axis-catalog-validate` and `axis-cheatsheet` (catalog drift check + catalog-backed cheat sheet generation).

### Checks
- Not rerun in this slice (wires existing targets together); prior slices already validated both commands.

### Removal test
- Reverting would drop the convenience target, making it easier to skip running both catalog guardrails together in local/CI workflows.

## 2025-12-12 – ADR closure slice

Focus (kind: status): Mark ADR-0046 accepted after all behavioural slices landed and guardrails passed.

### Changes
- Updated ADR status to `Accepted` in `docs/adr/0046-concordance-axis-catalog-help-pattern-streaming-resilience.md`.

### Checks
- Full suite: `python3 -m pytest` → 415 passed.

### Removal test
- Reverting would leave the ADR in Proposed state despite completed work and passing guardrails.

## 2025-12-12 – Pattern debug catalog CLI + axes parsing slice

Focus (kind: tools/behaviour/guardrail): Emit the pattern debug catalog via CLI and enrich coordinator views/snapshots with catalog-parsed axes (including directional) and GPT state.

### Changes
- Added `scripts/tools/pattern-debug-catalog.py` CLI to dump the pattern debug catalog as JSON.
- Pattern debug coordinator now parses recipes using the axis catalog, surfaces `static_prompt`/domain/directional axes, and carries `last_axes` when available; `modelPatternGUI.pattern_debug_snapshot/catalog` consume the richer views.
- Tests updated:
  - `_tests/test_pattern_debug_catalog_cli.py` (CLI emits JSON).
  - `_tests/test_pattern_debug_coordinator.py` (axes parsing + domain filter).
  - `_tests/test_model_pattern_debug_integration.py` (catalog views still expose per-pattern axes).
  - `_tests/test_gpt_actions.py::test_history_then_rerun_keeps_last_axes_token_only` now accounts for directional axes in history state.
- `talonSettings._filter_axis_tokens` accepts an `allow_unknown` flag so live prompts can keep short custom tokens while guardrails still drop non-catalog values.

### Checks
- Targeted guardrails: `python3 -m pytest _tests/test_pattern_debug_catalog_cli.py _tests/test_pattern_debug_coordinator.py _tests/test_model_pattern_debug_integration.py _tests/test_gpt_actions.py::GPTActionPromptSessionTests::test_history_then_rerun_keeps_last_axes_token_only _tests/test_talon_settings_axis_catalog.py _tests/test_talon_settings_model_prompt.py::ModelPromptModifiersTests::test_scope_method_style_modifiers_appended_in_order` → all passed.
- Full suite: `python3 -m pytest` → **415 passed**.

### Removal test
- Reverting would drop the CLI and the enriched coordinator axes/domain/state fields, and the guardrail tests would fail, breaking ADR-0046 coverage for pattern debugging and catalog alignment.
